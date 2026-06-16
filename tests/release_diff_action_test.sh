#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-diff/action.yml"
workflow="examples/workflows/release-diff-compare.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Compare Codex maintainer release proof' "$action"
grep -q 'left-tag:' "$action"
grep -q 'right-tag:' "$action"
grep -q 'download-assets:' "$action"
grep -q 'mode:' "$action"
grep -q 'gh release download "$left_tag"' "$action"
grep -q 'gh release download "$right_tag"' "$action"
grep -q 'release-diff compare' "$action"
grep -q 'release-diff.json' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'status="pass"' "$action"
grep -q 'mode must be fail or warn' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-diff@v3.24.0' "$workflow"
grep -q 'left-tag:' "$workflow"
grep -q 'right-tag:' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

"$repo_root/tests/release_diff_test.sh" >/dev/null

echo "release diff action tests passed"
