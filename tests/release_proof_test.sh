#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"

./bin/shipguard release-proof build --help >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" \
    --notes "release proof test" >/dev/null

test -f "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz"
test -f "$tmp_dir/proof-bundle/proof/release-manifest.json"
test -f "$tmp_dir/proof-bundle/proof/proof-ledger.md"
test -f "$tmp_dir/proof-bundle/index/release-index.json"
test -f "$tmp_dir/proof-bundle/index/release-index.md"
test -f "$tmp_dir/proof-bundle/replay/replay-report.json"
test -f "$tmp_dir/proof-bundle/replay/replay-report.md"
test -f "$tmp_dir/proof-bundle/attestation/attestation.json"
test -f "$tmp_dir/proof-bundle/attestation/attestation.md"
test -f "$tmp_dir/proof-bundle/attestation/attestation-badge.json"

grep -q "\"version\" : \"$version\"" "$tmp_dir/proof-bundle/proof/release-manifest.json"
grep -q '"status": "pass"' "$tmp_dir/proof-bundle/replay/replay-report.json"
grep -q '"status" : "pass"' "$tmp_dir/proof-bundle/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/proof-bundle/attestation/attestation-badge.json"

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle-without-optional-links" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --notes "release proof optional links test" >/dev/null

test -f "$tmp_dir/proof-bundle-without-optional-links/shipguard-v$version.tar.gz"
test -f "$tmp_dir/proof-bundle-without-optional-links/proof/release-manifest.json"
grep -q '"ci_run_url" : "https://github.com/example/repo/actions/runs/123"' "$tmp_dir/proof-bundle-without-optional-links/proof/release-manifest.json"
grep -q '"issue_url" : ""' "$tmp_dir/proof-bundle-without-optional-links/proof/release-manifest.json"
grep -q '"status": "pass"' "$tmp_dir/proof-bundle-without-optional-links/replay/replay-report.json"

if ./bin/shipguard release-proof build \
  --out "$tmp_dir/missing-release-url" >/dev/null 2>&1; then
  echo "expected release-proof build without release-url to fail" >&2
  exit 1
fi

if ./bin/shipguard release-proof build \
  --out "$tmp_dir/bad-release-url" \
  --release-url "https://example.com/releases/tag/v$version" >/dev/null 2>&1; then
  echo "expected release-proof build with non-GitHub release-url to fail" >&2
  exit 1
fi

echo "release proof tests passed"
