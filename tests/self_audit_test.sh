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
grep -q '"commands_checked": 15' "$tmp_dir/audit/self-audit.json"
grep -q '"artifacts_checked": 16' "$tmp_dir/audit/self-audit.json"
grep -q '| codex-maintainer ci-gate --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer arena import --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer arena sign --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer arena verify --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer ci-summary --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer check-run --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer check-run post --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer sarif --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| codex-maintainer next-goal --help | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| examples/demo-reports/leaderboard.json | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/next-goal.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/sarif.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/ci-summary.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/check-run.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| docs/template-profiles.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| templates/web/AGENTS.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| templates/backend/AGENTS.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| templates/cli/AGENTS.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| fixtures/external-arena-pack/imported-clean/run.md | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| scripts/arena_sign.sh | pass |' "$tmp_dir/audit/self-audit.md"
grep -q '| scripts/arena_verify.sh | pass |' "$tmp_dir/audit/self-audit.md"

echo "self audit tests passed"
