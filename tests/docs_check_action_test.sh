#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/docs-check/action.yml"
workflow="examples/workflows/docs-check.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Check Codex maintainer docs links' "$action"
grep -q 'path:' "$action"
grep -q 'docs-check' "$action"
grep -q 'docs-check.json' "$action"
grep -q 'docs-check.md' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'status="failed"' "$action"
grep -q 'exit_code="$check_exit"' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'codex-maintainer-docs-check' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/docs-check@v3.39.0' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"
grep -q 'artifact-name: codex-maintainer-docs-check' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

./bin/codex-maintainer docs-check . --out "$tmp_dir/docs-check" >/dev/null

grep -q '"status" : "pass"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"broken_count" : 0' "$tmp_dir/docs-check/docs-check.json"
grep -q '# Docs Check' "$tmp_dir/docs-check/docs-check.md"

echo "docs check action tests passed"
