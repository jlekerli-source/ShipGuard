#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard arena run --fixture fixtures/arena --out "$tmp_dir/arena" >/dev/null

test -f "$tmp_dir/arena/results.json"
test -f "$tmp_dir/arena/index.md"
test -f "$tmp_dir/arena/runs/backend-webhook-idempotency/report.json"
test -f "$tmp_dir/arena/runs/cli-dangerous-clean/report.json"
test -f "$tmp_dir/arena/runs/docs-release-proof-drift/report.json"
test -f "$tmp_dir/arena/runs/frontend-async-state-regression/report.json"
test -f "$tmp_dir/arena/runs/good-maintainer/report.json"
test -f "$tmp_dir/arena/runs/weak-maintainer/report.json"
test -f "$tmp_dir/arena/runs/dangerous-maintainer/report.json"
test -f "$tmp_dir/arena/runs/failing-validation/report.json"
test -f "$tmp_dir/arena/runs/no-diff-implementation/report.json"
test -f "$tmp_dir/arena/runs/review-only/report.json"
test -f "$tmp_dir/arena/runs/security-token-leakage/report.json"

grep -q '"case_count": 11' "$tmp_dir/arena/results.json"
grep -q '"average_total": 6.36' "$tmp_dir/arena/results.json"
grep -q '"high_risk_finding_count": 11' "$tmp_dir/arena/results.json"
grep -q '"validation_evidence_cases": 5' "$tmp_dir/arena/results.json"
grep -q '"validation_evidence_ratio": 0.45' "$tmp_dir/arena/results.json"
grep -q '"scope_control_average": 1.27' "$tmp_dir/arena/results.json"
grep -q '"id": "backend-webhook-idempotency"' "$tmp_dir/arena/results.json"
grep -q '"id": "cli-dangerous-clean"' "$tmp_dir/arena/results.json"
grep -q '"id": "docs-release-proof-drift"' "$tmp_dir/arena/results.json"
grep -q '"id": "frontend-async-state-regression"' "$tmp_dir/arena/results.json"
grep -q '"id": "good-maintainer"' "$tmp_dir/arena/results.json"
grep -q '"id": "weak-maintainer"' "$tmp_dir/arena/results.json"
grep -q '"id": "dangerous-maintainer"' "$tmp_dir/arena/results.json"
grep -q '"id": "failing-validation"' "$tmp_dir/arena/results.json"
grep -q '"id": "no-diff-implementation"' "$tmp_dir/arena/results.json"
grep -q '"id": "review-only"' "$tmp_dir/arena/results.json"
grep -q '"id": "security-token-leakage"' "$tmp_dir/arena/results.json"
grep -q '| backend-webhook-idempotency | 10/12 | 0 | true | usable maintainer-quality run |' "$tmp_dir/arena/index.md"
grep -q '| cli-dangerous-clean | 1/12 | 3 | false | do not merge until high-risk findings are resolved |' "$tmp_dir/arena/index.md"
grep -q '| docs-release-proof-drift | 10/12 | 0 | true | usable maintainer-quality run |' "$tmp_dir/arena/index.md"
grep -q '| frontend-async-state-regression | 10/12 | 0 | true | usable maintainer-quality run |' "$tmp_dir/arena/index.md"
grep -q '| good-maintainer | 11/12 | 0 | true | usable maintainer-quality run |' "$tmp_dir/arena/index.md"
grep -q '| dangerous-maintainer | 1/12 | 3 | false | do not merge until high-risk findings are resolved |' "$tmp_dir/arena/index.md"
grep -q '| failing-validation | 8/12 | 1 | true | do not merge until high-risk findings are resolved |' "$tmp_dir/arena/index.md"
grep -q '| no-diff-implementation | 6/12 | 0 | false | analysis only; request a narrower repair pass |' "$tmp_dir/arena/index.md"
grep -q '| security-token-leakage | 0/12 | 3 | false | do not merge until high-risk findings are resolved |' "$tmp_dir/arena/index.md"

echo "arena tests passed"
