#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"
tarball="$(./scripts/package_release.sh)"
tarball_name="$(basename "$tarball")"

./bin/codex-maintainer release-replay verify --help >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-manifest \
    --tarball "$tarball" \
    --out "$tmp_dir/proof" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-index build \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --out "$tmp_dir/index" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-replay verify \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --tarball "$tarball" \
    --index "$tmp_dir/index/release-index.json" \
    --ledger "$tmp_dir/proof/proof-ledger.md" \
    --out "$tmp_dir/replay" >/dev/null

test -f "$tmp_dir/replay/replay-report.json"
test -f "$tmp_dir/replay/replay-report.md"
grep -q '"status": "pass"' "$tmp_dir/replay/replay-report.json"
grep -q "\"version\": \"$version\"" "$tmp_dir/replay/replay-report.json"
grep -q '"name": "artifact sha256"' "$tmp_dir/replay/replay-report.json"
grep -q '"name": "release index replay"' "$tmp_dir/replay/replay-report.json"
grep -q '"name": "proof ledger replay"' "$tmp_dir/replay/replay-report.json"
grep -q '# Release Replay Report' "$tmp_dir/replay/replay-report.md"
grep -q '| artifact sha256 | pass |' "$tmp_dir/replay/replay-report.md"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-replay verify \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --tarball "$tarball" \
    --out "$tmp_dir/replay-without-optional" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/replay-without-optional/replay-report.json"
grep -q '"skipped": 2' "$tmp_dir/replay-without-optional/replay-report.json"

tamper_dir="$tmp_dir/tamper"
mkdir -p "$tamper_dir"
cp "$tarball" "$tamper_dir/$tarball_name"
printf 'tampered' >> "$tamper_dir/$tarball_name"
if ./bin/codex-maintainer release-replay verify \
  --manifest "$tmp_dir/proof/release-manifest.json" \
  --tarball "$tamper_dir/$tarball_name" \
  --index "$tmp_dir/index/release-index.json" \
  --ledger "$tmp_dir/proof/proof-ledger.md" \
  --out "$tmp_dir/tampered-replay" >/dev/null 2>&1; then
  echo "expected tampered tarball replay to fail" >&2
  exit 1
fi
grep -q '"status": "blocked"' "$tmp_dir/tampered-replay/replay-report.json"
grep -q '"name": "artifact sha256"' "$tmp_dir/tampered-replay/replay-report.json"

echo "release replay tests passed"
