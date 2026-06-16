#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/good-gate" \
  --mode warn >/dev/null

test -f "$tmp_dir/good-gate/autopsy/report.json"
test -f "$tmp_dir/good-gate/sarif/results.sarif"
test -f "$tmp_dir/good-gate/review/comment.md"
test -f "$tmp_dir/good-gate/review/badge.json"
test -f "$tmp_dir/good-gate/summary.md"
test -f "$tmp_dir/good-gate/gate.json"
grep -q '"status": "pass"' "$tmp_dir/good-gate/gate.json"
grep -q '"score": 11' "$tmp_dir/good-gate/gate.json"
grep -q '"sarif": "sarif/results.sarif"' "$tmp_dir/good-gate/gate.json"
grep -q '"summary": "summary.md"' "$tmp_dir/good-gate/gate.json"
grep -q '"version" : "2.1.0"' "$tmp_dir/good-gate/sarif/results.sarif"
grep -q '| Status | pass |' "$tmp_dir/good-gate/summary.md"

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/dangerous-gate" \
  --mode warn >/dev/null

grep -q '"status": "blocked"' "$tmp_dir/dangerous-gate/gate.json"
grep -q '"high_risk_findings": 3' "$tmp_dir/dangerous-gate/gate.json"
grep -q '| Status | blocked |' "$tmp_dir/dangerous-gate/review/comment.md"
grep -q '| Status | blocked |' "$tmp_dir/dangerous-gate/summary.md"
grep -q '"ruleId" : "validation_claim_without_tests"' "$tmp_dir/dangerous-gate/sarif/results.sarif"

if ./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/dangerous-fail-gate" \
  --mode fail >/dev/null 2>&1; then
  echo "expected dangerous gate to fail in fail mode" >&2
  exit 1
fi

grep -q 'actions/upload-artifact@v4' actions/ci-gate/action.yml

echo "ci gate tests passed"
