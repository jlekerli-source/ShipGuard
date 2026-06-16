#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-evidence-verify/action.yml"
workflow="examples/workflows/release-evidence-consume.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Verify Codex maintainer release evidence' "$action"
grep -q 'release-evidence verify' "$action"
grep -q 'require-diff:' "$action"
grep -q 'require-index:' "$action"
grep -q 'download-artifact:' "$action"
grep -q 'source-artifact-name:' "$action"
grep -q 'actions/download-artifact@v4' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'require-diff must be auto, true, or false' "$action"
grep -q 'require-index must be auto, true, or false' "$action"
grep -q 'download-artifact must be true or false' "$action"
grep -q 'evidence-verify.json' "$action"
grep -q 'badge.json' "$action"
grep -q 'actions/upload-artifact@v4' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.37.0' "$workflow"
grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-evidence-verify@v3.37.0' "$workflow"
grep -q 'default: v3.22.0' "$workflow"
grep -q 'default: v3.37.0' "$workflow"
grep -q 'download-artifact: true' "$workflow"
grep -q 'source-artifact-name: codex-maintainer-release-evidence' "$workflow"
grep -q 'require-diff: true' "$workflow"
grep -q 'require-index: true' "$workflow"

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
    --commit "6666666666666666666666666666666666666666" \
    --ci-run-url "https://github.com/example/repo/actions/runs/666" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/6" \
    --notes "release evidence verify action test" >/dev/null

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

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence bundle \
    --assets "$assets" \
    --left "$bundle" \
    --out "$tmp_dir/action-evidence" \
    --version "$version" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence verify \
    --dir "$tmp_dir/action-evidence" \
    --out "$tmp_dir/action-evidence-verify" \
    --require-diff true \
    --require-index true >/dev/null

grep -q '"status" : "pass"' "$tmp_dir/action-evidence-verify/evidence-verify.json"
grep -q '"bundle_present" : true' "$tmp_dir/action-evidence-verify/evidence-verify.json"

echo "release evidence verify action tests passed"
