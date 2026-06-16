#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/release-evidence-negative-index/action.yml"
workflow="examples/workflows/release-evidence-negative-index.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Audit Codex maintainer release evidence negative fixtures' "$action"
grep -q 'release-evidence negative-index' "$action"
grep -q 'fixture:' "$action"
grep -q 'fixture="$root/fixtures/release-evidence/negative"' "$action"
grep -q 'index-html=' "$action"
grep -q 'index.html' "$action"
grep -q 'negative-fixture-index.json' "$action"
grep -q 'negative-fixture-index.md' "$action"
grep -q 'badge.json' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'artifact-name:' "$action"
grep -q 'codex-maintainer-release-evidence-negative-index' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-evidence-negative-index@v3.26.0' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"
grep -q 'artifact-name: codex-maintainer-release-evidence-negative-index' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence negative-index \
    --fixture fixtures/release-evidence/negative \
    --out "$tmp_dir/negative-index" \
    --title "Release Evidence Negative Index Action Test" >/dev/null

test -f "$tmp_dir/negative-index/negative-fixture-index.json"
test -f "$tmp_dir/negative-index/negative-fixture-index.md"
test -f "$tmp_dir/negative-index/index.html"
test -f "$tmp_dir/negative-index/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"case_count" : 4' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"expected_blocked_count" : 4' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"message" : "pass 4/4"' "$tmp_dir/negative-index/badge.json"
grep -q 'Release Evidence Negative Index Action Test' "$tmp_dir/negative-index/index.html"
grep -q 'Machine-readable index' "$tmp_dir/negative-index/index.html"

echo "release evidence negative index action tests passed"
