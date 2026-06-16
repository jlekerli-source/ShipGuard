#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena run \
  --fixture fixtures/arena \
  --out "$tmp_dir/arena" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer leaderboard build \
  --arena-results "$tmp_dir/arena/results.json" \
  --out "$tmp_dir/leaderboard.json" >/dev/null

grep -q '"schema_version": "1.0"' "$tmp_dir/leaderboard.json"
grep -q '"benchmark": "Public AI Maintainer Reliability Benchmark"' "$tmp_dir/leaderboard.json"
grep -q '"generated_at": "2026-06-16T00:00:00Z"' "$tmp_dir/leaderboard.json"
grep -q '"id": "codex-maintainer-fixture-baseline"' "$tmp_dir/leaderboard.json"
grep -q '"average_total": 7.00' "$tmp_dir/leaderboard.json"
grep -q '"high_risk_finding_count": 8' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "backend-webhook-idempotency"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "cli-dangerous-clean"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "docs-release-proof-drift"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "frontend-async-state-regression"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "good-maintainer"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "dangerous-maintainer"' "$tmp_dir/leaderboard.json"
grep -q '"task_id": "failing-validation"' "$tmp_dir/leaderboard.json"

./scripts/build_demo_reports.sh "$tmp_dir/demo" >/dev/null
test -f "$tmp_dir/demo/README.md"
test -f "$tmp_dir/demo/arena/results.json"
test -f "$tmp_dir/demo/arena/index.md"
test -f "$tmp_dir/demo/arena/runs/good-maintainer/report.json"
test -f "$tmp_dir/demo/arena/runs/backend-webhook-idempotency/report.json"
test -f "$tmp_dir/demo/arena/runs/cli-dangerous-clean/report.json"
test -f "$tmp_dir/demo/leaderboard.json"
grep -q '"schema_version": "1.0"' "$tmp_dir/demo/leaderboard.json"

test -f examples/demo-reports/README.md
test -f examples/demo-reports/arena/results.json
test -f examples/demo-reports/leaderboard.json
test -f examples/demo-reports/transcripts/corpus.json
test -f examples/demo-reports/transcripts/index.md
grep -q '"case_count": 4' examples/demo-reports/transcripts/corpus.json

echo "leaderboard tests passed"
