#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer self-audit --help >/dev/null
CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer self-audit --out "$tmp_dir/audit" >/dev/null

test -f "$tmp_dir/audit/self-audit.md"
test -f "$tmp_dir/audit/self-audit.json"
grep -q '"status": "pass"' "$tmp_dir/audit/self-audit.json"
grep -q '"commands_checked": 9' "$tmp_dir/audit/self-audit.json"
grep -q '"artifacts_checked": 7' "$tmp_dir/audit/self-audit.json"
grep -q '| codex-maintainer ci-gate --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer sarif --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer next-goal --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| examples/demo-reports/leaderboard.json | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/next-goal.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/sarif.md | pass |' "$tmp_dir/audit/self-audit.md"

echo "self audit tests passed"
