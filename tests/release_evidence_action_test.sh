#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-evidence/action.yml"
workflow="examples/workflows/release-evidence-export.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Export Codex maintainer release evidence' "$action"
grep -q 'consume-dir:' "$action"
grep -q 'diff-dir:' "$action"
grep -q 'include-diff:' "$action"
grep -q 'build-index:' "$action"
grep -q 'extra-index-sites:' "$action"
grep -q 'release-evidence site' "$action"
grep -q 'release-evidence index' "$action"
grep -q 'include-diff must be auto, true, or false' "$action"
grep -q 'build-index must be true or false' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'evidence-json=' "$action"
grep -q 'evidence-index-json=' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.19.0' "$workflow"
grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-diff@v3.19.0' "$workflow"
grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.19.0' "$workflow"
grep -q 'previous-tag:' "$workflow"
grep -q 'release-tag:' "$workflow"
grep -q 'default: v3.18.0' "$workflow"
grep -q 'default: v3.19.0' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'include-diff: auto' "$workflow"
grep -q 'build-index: true' "$workflow"
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
    --commit "4444444444444444444444444444444444444444" \
    --ci-run-url "https://github.com/example/repo/actions/runs/444" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/4" \
    --notes "release evidence action test" >/dev/null

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
    --out "$tmp_dir/evidence/site" \
    --title "Release Evidence Action Test" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence index \
    --site "$tmp_dir/evidence/site" \
    --out "$tmp_dir/evidence/index" \
    --title "Release Evidence Action Index Test" >/dev/null

test -f "$tmp_dir/evidence/site/index.html"
test -f "$tmp_dir/evidence/site/evidence.json"
test -f "$tmp_dir/evidence/site/README.md"
test -f "$tmp_dir/evidence/site/sources/consumer-report.json"
test -f "$tmp_dir/evidence/site/sources/asset-digests.json"
test -f "$tmp_dir/evidence/site/sources/release-diff.json"
test -f "$tmp_dir/evidence/index/index.html"
test -f "$tmp_dir/evidence/index/evidence-index.json"

grep -q '"status" : "pass"' "$tmp_dir/evidence/site/evidence.json"
grep -q '"release_diff" : {' "$tmp_dir/evidence/site/evidence.json"
grep -q 'Release Evidence Action Test' "$tmp_dir/evidence/site/index.html"
grep -q '"site_count" : 1' "$tmp_dir/evidence/index/evidence-index.json"
grep -q 'Release Evidence Action Index Test' "$tmp_dir/evidence/index/index.html"

echo "release evidence action tests passed"
