#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-evidence site --help >/dev/null

version="$(sed -n '1p' VERSION)"
bundle="$tmp_dir/release-proof-bundle"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-proof build \
    --out "$bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "3333333333333333333333333333333333333333" \
    --ci-run-url "https://github.com/example/repo/actions/runs/333" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/3" \
    --notes "release evidence site test" >/dev/null

assets="$tmp_dir/assets"
mkdir -p "$assets"
cp "$bundle/codex-maintainer-v$version.tar.gz" "$assets/"
cp "$bundle/proof/release-manifest.json" "$assets/"
cp "$bundle/proof/proof-ledger.md" "$assets/"
cp "$bundle/index/release-index.json" "$assets/"
cp "$bundle/index/release-index.md" "$assets/"
cp "$bundle/replay/replay-report.json" "$assets/"
cp "$bundle/replay/replay-report.md" "$assets/"
cp "$bundle/attestation/attestation.json" "$assets/"
cp "$bundle/attestation/attestation.md" "$assets/"
cp "$bundle/attestation/attestation-badge.json" "$assets/"

./bin/codex-maintainer release-consume verify \
  --dir "$assets" \
  --out "$tmp_dir/consumer-proof" \
  --version "$version" >/dev/null

./bin/codex-maintainer release-diff compare \
  --left "$bundle" \
  --right "$assets" \
  --out "$tmp_dir/release-diff" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence site \
    --consume "$tmp_dir/consumer-proof" \
    --diff "$tmp_dir/release-diff" \
    --out "$tmp_dir/site" \
    --title "Release Evidence Test" >/dev/null

test -f "$tmp_dir/site/index.html"
test -f "$tmp_dir/site/evidence.json"
test -f "$tmp_dir/site/README.md"
test -f "$tmp_dir/site/sources/consumer-report.json"
test -f "$tmp_dir/site/sources/asset-digests.json"
test -f "$tmp_dir/site/sources/release-diff.json"

grep -q '<!doctype html>' "$tmp_dir/site/index.html"
grep -q 'Release Evidence Test' "$tmp_dir/site/index.html"
grep -q 'Asset Digest Matrix' "$tmp_dir/site/index.html"
grep -q 'Release Diff' "$tmp_dir/site/index.html"
grep -q 'sources/consumer-report.json' "$tmp_dir/site/index.html"
grep -q 'sources/release-diff.json' "$tmp_dir/site/index.html"
grep -q "codex-maintainer-v$version.tar.gz" "$tmp_dir/site/index.html"
grep -q '"status" : "pass"' "$tmp_dir/site/evidence.json"
grep -q '"title" : "Release Evidence Test"' "$tmp_dir/site/evidence.json"
grep -q '"consumer_report" : "sources/consumer-report.json"' "$tmp_dir/site/evidence.json"
grep -q '"asset_digests" : "sources/asset-digests.json"' "$tmp_dir/site/evidence.json"
grep -q '"release_diff" : "sources/release-diff.json"' "$tmp_dir/site/evidence.json"
grep -q '"required_missing" : 0' "$tmp_dir/site/evidence.json"
grep -q '# Release Evidence Test' "$tmp_dir/site/README.md"
grep -q 'Release diff: pass' "$tmp_dir/site/README.md"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence site \
    --consume "$tmp_dir/consumer-proof" \
    --out "$tmp_dir/site-no-diff" >/dev/null

test -f "$tmp_dir/site-no-diff/index.html"
grep -q '"present" : false' "$tmp_dir/site-no-diff/evidence.json"

if ./bin/codex-maintainer release-evidence site \
  --consume "$tmp_dir/missing" \
  --out "$tmp_dir/should-not-exist" >/dev/null 2>&1; then
  echo "expected missing consumer proof directory to fail" >&2
  exit 1
fi

echo "release evidence tests passed"
