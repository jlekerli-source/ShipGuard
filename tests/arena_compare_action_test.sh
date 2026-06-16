#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/arena-compare/action.yml"
workflow="examples/workflows/arena-compare.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Compare Codex maintainer Arena results' "$action"
grep -q 'left-results:' "$action"
grep -q 'right-results:' "$action"
grep -q 'arena compare' "$action"
grep -q 'arena-compare.json' "$action"
grep -q 'arena-compare.md' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'status="failed"' "$action"
grep -q 'exit_code="$compare_exit"' "$action"
grep -q 'exit "$exit_code"' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'codex-maintainer-arena-compare' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/arena-compare@v3.30.0' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"
grep -q 'artifact-name: codex-maintainer-arena-compare' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

mkdir -p "$tmp_dir/eight-case-fixture"
for case_id in \
  backend-webhook-idempotency \
  cli-dangerous-clean \
  dangerous-maintainer \
  failing-validation \
  good-maintainer \
  no-diff-implementation \
  review-only \
  weak-maintainer; do
  cp -R "fixtures/arena/$case_id" "$tmp_dir/eight-case-fixture/$case_id"
done

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena run \
    --fixture "$tmp_dir/eight-case-fixture" \
    --out "$tmp_dir/old-arena" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena run \
    --fixture fixtures/arena \
    --out "$tmp_dir/current-arena" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena compare \
    --left "$tmp_dir/old-arena/results.json" \
    --right "$tmp_dir/current-arena/results.json" \
    --out "$tmp_dir/compare" \
    --title "Arena Compare Action Test" >/dev/null

grep -q '"status" : "improved"' "$tmp_dir/compare/arena-compare.json"
grep -q 'Arena Compare Action Test' "$tmp_dir/compare/arena-compare.md"

echo "arena compare action tests passed"
