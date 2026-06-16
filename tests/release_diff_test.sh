#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-diff compare --help >/dev/null

current_version="$(sed -n '1p' VERSION)"
left_version="0.1.0"
left_assets="$tmp_dir/left-assets"
right_assets="$tmp_dir/right-assets"
mkdir -p "$left_assets" "$right_assets"

packaged_tarball="$(./scripts/package_release.sh)"
left_tarball="$left_assets/codex-maintainer-v$left_version.tar.gz"
right_tarball="$right_assets/$(basename "$packaged_tarball")"
cp "$packaged_tarball" "$left_tarball"
cp "$packaged_tarball" "$right_tarball"
printf 'synthetic left release delta\n' >> "$left_tarball"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-manifest \
    --tarball "$left_tarball" \
    --out "$left_assets" \
    --version "$left_version" \
    --tag "v$left_version" \
    --commit "1111111111111111111111111111111111111111" \
    --ci-run-url "https://github.com/example/repo/actions/runs/111" \
    --release-url "https://github.com/example/repo/releases/tag/v$left_version" \
    --issue-url "https://github.com/example/repo/issues/1" \
    --notes "left release diff test" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-manifest \
    --tarball "$right_tarball" \
    --out "$right_assets" \
    --version "$current_version" \
    --tag "v$current_version" \
    --commit "2222222222222222222222222222222222222222" \
    --ci-run-url "https://github.com/example/repo/actions/runs/222" \
    --release-url "https://github.com/example/repo/releases/tag/v$current_version" \
    --issue-url "https://github.com/example/repo/issues/2" \
    --notes "right release diff test" >/dev/null

./bin/codex-maintainer release-index build \
  --manifest "$left_assets/release-manifest.json" \
  --out "$left_assets" >/dev/null
./bin/codex-maintainer release-index build \
  --manifest "$right_assets/release-manifest.json" \
  --out "$right_assets" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-diff compare \
    --left "$left_assets" \
    --right "$right_assets" \
    --out "$tmp_dir/release-diff" >/dev/null

test -f "$tmp_dir/release-diff/release-diff.json"
test -f "$tmp_dir/release-diff/release-diff.md"
grep -q '"status" : "pass"' "$tmp_dir/release-diff/release-diff.json"
grep -q '"version" : "0.1.0"' "$tmp_dir/release-diff/release-diff.json"
grep -q '"version" : "'"$current_version"'"' "$tmp_dir/release-diff/release-diff.json"
grep -q '"artifact_changed" : true' "$tmp_dir/release-diff/release-diff.json"
grep -q '"asset_count" : 10' "$tmp_dir/release-diff/release-diff.json"
grep -q '"role" : "release tarball"' "$tmp_dir/release-diff/release-diff.json"
grep -q '# Release Diff Audit' "$tmp_dir/release-diff/release-diff.md"
grep -q '| release tarball | true | changed |' "$tmp_dir/release-diff/release-diff.md"
grep -q '| proof ledger | true | changed |' "$tmp_dir/release-diff/release-diff.md"

if ./bin/codex-maintainer release-diff compare \
  --left "$tmp_dir/missing" \
  --right "$right_assets" \
  --out "$tmp_dir/should-not-exist" >/dev/null 2>&1; then
  echo "expected missing left directory to fail" >&2
  exit 1
fi

echo "release diff tests passed"
