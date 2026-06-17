#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-proof/action.yml"
test -f "$action"
grep -q 'name: Build ShipGuard release proof' "$action"
grep -q 'release-url:' "$action"
grep -q 'required: true' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'release-manifest' "$action"
grep -q 'release-index build' "$action"
grep -q 'release-replay verify' "$action"
grep -q 'release-attest build' "$action"
grep -q 'attestation-badge.json' "$action"

version="$(sed -n '1p' VERSION)"
out="$tmp_dir/release-proof-action"
tarball="$(./scripts/package_release.sh)"
release_tarball="$out/$(basename "$tarball")"
mkdir -p "$out"
cp "$tarball" "$release_tarball"

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-manifest \
    --tarball "$release_tarball" \
    --out "$out/proof" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" \
    --notes "action test" >/dev/null

./bin/shipguard release-manifest verify \
  --manifest "$out/proof/release-manifest.json" \
  --tarball "$release_tarball" \
  --version "$version" \
  --tag "v$version" >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-index build \
    --manifest "$out/proof/release-manifest.json" \
    --out "$out/index" >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-replay verify \
    --manifest "$out/proof/release-manifest.json" \
    --tarball "$release_tarball" \
    --index "$out/index/release-index.json" \
    --ledger "$out/proof/proof-ledger.md" \
    --out "$out/replay" >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-attest build \
    --manifest "$out/proof/release-manifest.json" \
    --replay "$out/replay/replay-report.json" \
    --out "$out/attestation" >/dev/null

test -f "$out/$(basename "$tarball")"
test -f "$out/proof/release-manifest.json"
test -f "$out/proof/proof-ledger.md"
test -f "$out/index/release-index.json"
test -f "$out/replay/replay-report.json"
test -f "$out/attestation/attestation.json"
test -f "$out/attestation/attestation-badge.json"
grep -q '"status": "pass"' "$out/replay/replay-report.json"
grep -q '"status" : "pass"' "$out/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$out/attestation/attestation-badge.json"

echo "release proof action tests passed"
