#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"

./bin/shipguard release-consume verify --help >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit 0123456789abcdef \
    --ci-run-url "https://github.com/jlekerli-source/ShipGuard/actions/runs/123" \
    --release-url "https://github.com/jlekerli-source/ShipGuard/releases/tag/v$version" \
    --issue-url "https://github.com/jlekerli-source/ShipGuard/issues/99" >/dev/null

mkdir -p "$tmp_dir/downloaded"
cp "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/release-manifest.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/index/release-index.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/proof-ledger.md" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/replay/replay-report.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation-badge.json" "$tmp_dir/downloaded/"

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-consume verify \
    --dir "$tmp_dir/downloaded" \
    --out "$tmp_dir/consumer" \
    --version "$version" >/dev/null

test -f "$tmp_dir/consumer/sha256.txt"
test -f "$tmp_dir/consumer/replay/replay-report.json"
test -f "$tmp_dir/consumer/attestation/attestation.json"
test -f "$tmp_dir/consumer/attestation/attestation-badge.json"
test -f "$tmp_dir/consumer/consumer-report.json"
test -f "$tmp_dir/consumer/consumer-report.md"
test -f "$tmp_dir/consumer/asset-digests.json"
test -f "$tmp_dir/consumer/asset-digests.md"

grep -q "$(perl -MJSON::PP -e 'open my $fh, "<", $ARGV[0] or die $!; local $/; print decode_json(<$fh>)->{artifact}->{sha256}' "$tmp_dir/downloaded/release-manifest.json")" "$tmp_dir/consumer/sha256.txt"
grep -q '"status": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q "\"version\": \"$version\"" "$tmp_dir/consumer/consumer-report.json"
grep -q '"replay_status": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"replay_blocked": 0' "$tmp_dir/consumer/consumer-report.json"
grep -q '"attestation_status": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"attestation_blocked": 0' "$tmp_dir/consumer/consumer-report.json"
grep -q '"badge_message": "pass v'"$version"'"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"replay_report": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"attestation": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"attestation_badge": "pass"' "$tmp_dir/consumer/consumer-report.json"
grep -q '"blocked": 0' "$tmp_dir/consumer/consumer-report.json"
grep -q '"asset_digest_matrix": "asset-digests.json"' "$tmp_dir/consumer/consumer-report.json"
grep -q '# Release Proof Consumer Report' "$tmp_dir/consumer/consumer-report.md"
grep -q 'Replay blocked checks: 0' "$tmp_dir/consumer/consumer-report.md"
grep -q 'Published badge crosscheck: pass' "$tmp_dir/consumer/consumer-report.md"
grep -q 'Asset digest matrix: `asset-digests.json`' "$tmp_dir/consumer/consumer-report.md"
grep -q '# Release Asset Digest Matrix' "$tmp_dir/consumer/asset-digests.md"
grep -q "| shipguard-v$version.tar.gz | release tarball | true | present |" "$tmp_dir/consumer/asset-digests.md"
grep -q '| attestation-badge.json | published attestation badge | false | present |' "$tmp_dir/consumer/asset-digests.md"
grep -q "\"name\": \"shipguard-v$version.tar.gz\"" "$tmp_dir/consumer/asset-digests.json"
grep -q '"role": "release tarball"' "$tmp_dir/consumer/asset-digests.json"
grep -q '"status": "present"' "$tmp_dir/consumer/asset-digests.json"
grep -q '"sha256":' "$tmp_dir/consumer/asset-digests.json"

cp -R "$tmp_dir/downloaded" "$tmp_dir/tampered"
printf '{ "schemaVersion": 1, "label": "release proof", "message": "pass v0.0.0", "color": "brightgreen" }\n' > "$tmp_dir/tampered/attestation-badge.json"
if ./bin/shipguard release-consume verify \
  --dir "$tmp_dir/tampered" \
  --out "$tmp_dir/tampered-consumer" \
  --version "$version" >/dev/null 2>&1; then
  echo "expected tampered published badge to fail" >&2
  exit 1
fi

if ./bin/shipguard release-consume verify \
  --dir "$tmp_dir/downloaded" \
  --out "$tmp_dir/wrong-version" \
  --version 0.0.0 >/dev/null 2>&1; then
  echo "expected wrong version to fail" >&2
  exit 1
fi

if ./bin/shipguard release-consume verify \
  --dir "$tmp_dir/missing-assets" \
  --out "$tmp_dir/missing-out" >/dev/null 2>&1; then
  echo "expected missing asset dir to fail" >&2
  exit 1
fi

echo "release consume tests passed"
