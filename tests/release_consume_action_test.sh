#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-consume/action.yml"
workflow="examples/workflows/release-consume-verify.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Verify Codex maintainer release proof' "$action"
grep -q 'release-tag:' "$action"
grep -q 'download-assets:' "$action"
grep -q 'mode:' "$action"
grep -q 'gh release download' "$action"
grep -q 'release-consume verify' "$action"
grep -q 'asset-digests.json' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'status="pass"' "$action"
grep -q 'mode must be fail or warn' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.30.0' "$workflow"
grep -q 'release-tag:' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

version="$(sed -n '1p' VERSION)"
bundle="$tmp_dir/release-proof-bundle"
CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-proof build \
    --out "$bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" \
    --notes "release consume action test" >/dev/null

assets="$tmp_dir/assets"
mkdir -p "$assets"
cp "$bundle/codex-maintainer-v$version.tar.gz" "$assets/"
cp "$bundle/proof/release-manifest.json" "$assets/"
cp "$bundle/proof/proof-ledger.md" "$assets/"
cp "$bundle/index/release-index.json" "$assets/"
cp "$bundle/replay/replay-report.json" "$assets/"
cp "$bundle/attestation/attestation.json" "$assets/"
cp "$bundle/attestation/attestation-badge.json" "$assets/"

./bin/codex-maintainer release-consume verify \
  --dir "$assets" \
  --out "$tmp_dir/consumer-proof" \
  --version "$version" >/dev/null

grep -q '"status": "pass"' "$tmp_dir/consumer-proof/consumer-report.json"
grep -q '"asset_digest_matrix": "asset-digests.json"' "$tmp_dir/consumer-proof/consumer-report.json"
grep -q "| codex-maintainer-v$version.tar.gz | release tarball | true | present |" "$tmp_dir/consumer-proof/asset-digests.md"
grep -q '"name": "attestation-badge.json"' "$tmp_dir/consumer-proof/asset-digests.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/consumer-proof/attestation/attestation-badge.json"

echo "release consume action tests passed"
