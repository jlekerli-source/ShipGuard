#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

assert_contains() {
  local file="$1"
  local pattern="$2"
  if ! grep -q "$pattern" "$file"; then
    echo "expected $file to contain: $pattern" >&2
    exit 1
  fi
}

assert_not_contains() {
  local file="$1"
  local pattern="$2"
  if grep -q "$pattern" "$file"; then
    echo "expected $file to not contain: $pattern" >&2
    exit 1
  fi
}

good_out="$tmp_dir/good"
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out "$good_out" >/dev/null

assert_contains "$good_out/report.md" 'No autopsy findings.'
assert_contains "$good_out/report.json" '"total": 11'
assert_contains "$good_out/report.json" '"verdict": "usable maintainer-quality run"'
assert_not_contains "$good_out/report.json" '"severity": "high"'
assert_not_contains "$good_out/report.json" 'validation_claim_without_tests'

weak_out="$tmp_dir/weak"
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/weak-run/run.md \
  --task fixtures/autopsy/weak-run/task.md \
  --diff fixtures/autopsy/weak-run/diff.patch \
  --out "$weak_out" >/dev/null

assert_contains "$weak_out/report.json" '"total": 3'
assert_contains "$weak_out/report.json" '"verdict": "do not merge until high-risk findings are resolved"'
assert_contains "$weak_out/report.json" 'missing_score_category'
assert_contains "$weak_out/report.json" 'no_test_log'
assert_contains "$weak_out/report.json" 'validation_claim_without_tests'

dangerous_out="$tmp_dir/dangerous"
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out "$dangerous_out" >/dev/null

assert_contains "$dangerous_out/report.json" '"total": 1'
assert_contains "$dangerous_out/report.json" '"verdict": "do not merge until high-risk findings are resolved"'
assert_contains "$dangerous_out/report.json" 'validation_claim_without_tests'
assert_contains "$dangerous_out/report.json" 'high_assurance_claim'
assert_contains "$dangerous_out/report.json" 'scope_creep_signal'
assert_contains "$dangerous_out/report.json" 'protected_area_touch'
assert_contains "$dangerous_out/report.md" 'Changed files from diff: 4'

echo "autopsy tests passed"
