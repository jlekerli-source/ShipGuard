#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard arena sign --help >/dev/null
./bin/shipguard arena verify --help >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard arena sign \
    --fixture fixtures/external-arena-pack \
    --out "$tmp_dir/PACK.json" \
    --pack-name "external-pack" \
    --signer "ShipGuard Fixtures" \
    --signer-url "https://github.com/jlekerli-source/ShipGuard" >/dev/null

test -f "$tmp_dir/PACK.json"
grep -q '"schema_version" : "1.0"' "$tmp_dir/PACK.json"
grep -q '"signature_type" : "sha256-content-digest"' "$tmp_dir/PACK.json"
grep -q '"pack_name" : "external-pack"' "$tmp_dir/PACK.json"
grep -q '"signer" : "ShipGuard Fixtures"' "$tmp_dir/PACK.json"
grep -q '"signer_url" : "https://github.com/jlekerli-source/ShipGuard"' "$tmp_dir/PACK.json"
grep -q '"identity_digest" : "[a-f0-9]\{64\}"' "$tmp_dir/PACK.json"
grep -q '"case_count" : 2' "$tmp_dir/PACK.json"
grep -q '"path" : "imported-clean/run.md"' "$tmp_dir/PACK.json"

./bin/shipguard arena verify \
  --fixture fixtures/external-arena-pack \
  --manifest "$tmp_dir/PACK.json" >/dev/null

cp -R fixtures/external-arena-pack "$tmp_dir/tampered-pack"
printf '\ntampered\n' >> "$tmp_dir/tampered-pack/imported-clean/run.md"
if ./bin/shipguard arena verify \
  --fixture "$tmp_dir/tampered-pack" \
  --manifest "$tmp_dir/PACK.json" >/dev/null 2>&1; then
  echo "expected tampered fixture pack to fail verification" >&2
  exit 1
fi

cp -R fixtures/external-arena-pack "$tmp_dir/extra-file-pack"
printf 'hidden extra file\n' > "$tmp_dir/extra-file-pack/imported-clean/notes.txt"
if ./bin/shipguard arena verify \
  --fixture "$tmp_dir/extra-file-pack" \
  --manifest "$tmp_dir/PACK.json" >/dev/null 2>&1; then
  echo "expected fixture pack with an unsupported case file to fail verification" >&2
  exit 1
fi

if ./bin/shipguard arena sign \
  --fixture "$tmp_dir/extra-file-pack" \
  --out "$tmp_dir/extra-file.json" >/dev/null 2>&1; then
  echo "expected fixture pack with an unsupported case file to fail signing" >&2
  exit 1
fi

if ./bin/shipguard arena sign \
  --fixture "$tmp_dir/missing-pack" \
  --out "$tmp_dir/missing.json" >/dev/null 2>&1; then
  echo "expected signing missing pack to fail" >&2
  exit 1
fi

printf '{"schema_version":"1.0","signature_type":"wrong"}\n' > "$tmp_dir/bad-manifest.json"
if ./bin/shipguard arena verify \
  --fixture fixtures/external-arena-pack \
  --manifest "$tmp_dir/bad-manifest.json" >/dev/null 2>&1; then
  echo "expected bad manifest to fail verification" >&2
  exit 1
fi

cp "$tmp_dir/PACK.json" "$tmp_dir/tampered-identity.json"
perl -0pi -e 's/ShipGuard Fixtures/Other Maintainer Fixtures/' "$tmp_dir/tampered-identity.json"
if ./bin/shipguard arena verify \
  --fixture fixtures/external-arena-pack \
  --manifest "$tmp_dir/tampered-identity.json" >/dev/null 2>&1; then
  echo "expected tampered identity metadata to fail verification" >&2
  exit 1
fi

if ./bin/shipguard arena sign \
  --fixture fixtures/external-arena-pack \
  --out "$tmp_dir/unsafe-signer.json" \
  --signer "maintainer@example.com" >/dev/null 2>&1; then
  echo "expected unsafe signer identity to fail signing" >&2
  exit 1
fi

if ./bin/shipguard arena sign \
  --fixture fixtures/external-arena-pack \
  --out "$tmp_dir/insecure-signer-url.json" \
  --signer "ShipGuard Fixtures" \
  --signer-url "http://example.com/pack" >/dev/null 2>&1; then
  echo "expected insecure signer URL to fail signing" >&2
  exit 1
fi

echo "arena sign tests passed"
