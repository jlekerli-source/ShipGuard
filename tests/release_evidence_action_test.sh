#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"
action="actions/release-evidence/action.yml"
workflow="examples/workflows/release-evidence-export.yml"
bundle_workflow="examples/workflows/release-evidence-bundle.yml"

test -f "$action"
test -f "$workflow"
test -f "$bundle_workflow"

grep -q 'name: Export ShipGuard release evidence' "$action"
grep -q 'run:' "$action"
grep -q 'repo:' "$action"
grep -q 'release-tag:' "$action"
grep -q 'previous-tag:' "$action"
grep -q 'download-assets:' "$action"
grep -q 'assets-dir:' "$action"
grep -q 'left-assets-dir:' "$action"
grep -q 'version:' "$action"
grep -q 'consume-dir:' "$action"
grep -q 'diff-dir:' "$action"
grep -q 'include-diff:' "$action"
grep -q 'build-index:' "$action"
grep -q 'extra-index-sites:' "$action"
grep -q 'release-evidence site' "$action"
grep -q 'release-evidence index' "$action"
grep -q 'release-evidence bundle' "$action"
grep -q 'gh release download "$release_tag"' "$action"
grep -q 'gh release download "$previous_tag"' "$action"
grep -q 'left_assets_dir="$out-previous-assets"' "$action"
grep -q 'run must be reports or bundle' "$action"
grep -q 'download-assets must be true or false' "$action"
grep -q 'download-assets is only supported when run is bundle' "$action"
grep -q 'include-diff must be auto, true, or false' "$action"
grep -q 'build-index must be true or false' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'evidence-json=' "$action"
grep -q 'evidence-index-json=' "$action"
grep -q 'bundle=' "$action"

grep -q "jlekerli-source/ShipGuard/actions/release-consume@v$version" "$workflow"
grep -q "jlekerli-source/ShipGuard/actions/release-diff@v$version" "$workflow"
grep -q "jlekerli-source/ShipGuard/actions/release-evidence@v$version" "$workflow"
grep -q 'previous-tag:' "$workflow"
grep -q 'release-tag:' "$workflow"
grep -q 'default: v3.22.0' "$workflow"
grep -q "default: v$version" "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'include-diff: auto' "$workflow"
grep -q 'build-index: true' "$workflow"
grep -q 'mode: fail' "$workflow"

grep -q "jlekerli-source/ShipGuard/actions/release-evidence@v$version" "$bundle_workflow"
grep -q 'run: bundle' "$bundle_workflow"
grep -q 'download-assets: true' "$bundle_workflow"
grep -q 'previous-tag:' "$bundle_workflow"
grep -q 'release-tag:' "$bundle_workflow"
grep -q 'default: v3.22.0' "$bundle_workflow"
grep -q "default: v$version" "$bundle_workflow"
grep -q 'contents: read' "$bundle_workflow"
grep -q 'mode: fail' "$bundle_workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow" "$bundle_workflow"
fi

bundle="$tmp_dir/release-proof-bundle"

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-proof build \
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
cp "$bundle/shipguard-v$version.tar.gz" "$assets/"
cp "$bundle/proof/release-manifest.json" "$assets/"
cp "$bundle/proof/proof-ledger.md" "$assets/"
cp "$bundle/index/release-index.json" "$assets/"
cp "$bundle/index/release-index.md" "$assets/"
cp "$bundle/replay/replay-report.json" "$assets/"
cp "$bundle/replay/replay-report.md" "$assets/"
cp "$bundle/attestation/attestation.json" "$assets/"
cp "$bundle/attestation/attestation.md" "$assets/"
cp "$bundle/attestation/attestation-badge.json" "$assets/"

./bin/shipguard release-consume verify \
  --dir "$assets" \
  --out "$tmp_dir/consumer-proof" \
  --version "$version" >/dev/null

./bin/shipguard release-diff compare \
  --left "$bundle" \
  --right "$assets" \
  --out "$tmp_dir/release-diff" >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-evidence site \
    --consume "$tmp_dir/consumer-proof" \
    --diff "$tmp_dir/release-diff" \
    --out "$tmp_dir/evidence/site" \
    --title "Release Evidence Action Test" >/dev/null

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-evidence index \
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

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-evidence bundle \
    --assets "$assets" \
    --left "$bundle" \
    --out "$tmp_dir/evidence-bundle" \
    --version "$version" \
    --title "Release Evidence Action Bundle Test" \
    --index-title "Release Evidence Action Bundle Index Test" >/dev/null

test -f "$tmp_dir/evidence-bundle/bundle.json"
test -f "$tmp_dir/evidence-bundle/site/index.html"
test -f "$tmp_dir/evidence-bundle/index/evidence-index.json"
grep -q '"diff_included": true' "$tmp_dir/evidence-bundle/bundle.json"
grep -q 'Release Evidence Action Bundle Test' "$tmp_dir/evidence-bundle/site/index.html"

echo "release evidence action tests passed"
