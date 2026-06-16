#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer arena compare --help >/dev/null

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
    --title "Arena Compare Test" >/dev/null

test -f "$tmp_dir/compare/arena-compare.json"
test -f "$tmp_dir/compare/arena-compare.md"
grep -q '"schema_version" : "0.1"' "$tmp_dir/compare/arena-compare.json"
grep -q '"status" : "improved"' "$tmp_dir/compare/arena-compare.json"
grep -q '"case_count_delta" : 1' "$tmp_dir/compare/arena-compare.json"
grep -q '"average_total_delta" : 0.42' "$tmp_dir/compare/arena-compare.json"
grep -q '"high_risk_finding_delta" : 0' "$tmp_dir/compare/arena-compare.json"
grep -q '"added_cases" : 1' "$tmp_dir/compare/arena-compare.json"
grep -q '"removed_cases" : 0' "$tmp_dir/compare/arena-compare.json"
grep -q '"id" : "frontend-async-state-regression"' "$tmp_dir/compare/arena-compare.json"
grep -q '"status" : "added"' "$tmp_dir/compare/arena-compare.json"
grep -q '| Status | improved |' "$tmp_dir/compare/arena-compare.md"
grep -q '| Average score delta | +0.42 |' "$tmp_dir/compare/arena-compare.md"
grep -q '| frontend-async-state-regression | added | - | 10 | - | - | 0 | - |' "$tmp_dir/compare/arena-compare.md"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena compare \
    --left "$tmp_dir/current-arena/results.json" \
    --right "$tmp_dir/old-arena/results.json" \
    --out "$tmp_dir/reverse-compare" >/dev/null

grep -q '"status" : "regressed"' "$tmp_dir/reverse-compare/arena-compare.json"
grep -q '"case_count_delta" : -1' "$tmp_dir/reverse-compare/arena-compare.json"
grep -q '"average_total_delta" : -0.42' "$tmp_dir/reverse-compare/arena-compare.json"
grep -q '"removed_cases" : 1' "$tmp_dir/reverse-compare/arena-compare.json"
grep -q '| frontend-async-state-regression | removed | 10 | - | - | 0 | - | - |' "$tmp_dir/reverse-compare/arena-compare.md"

if ./bin/codex-maintainer arena compare \
  --left "$tmp_dir/missing.json" \
  --right "$tmp_dir/current-arena/results.json" \
  --out "$tmp_dir/missing-compare" >/dev/null 2>&1; then
  echo "expected missing left results to fail" >&2
  exit 1
fi

echo "arena compare tests passed"
