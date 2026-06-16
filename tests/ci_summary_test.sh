#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ci-summary --help >/dev/null

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/gate" \
  --mode warn >/dev/null

test -f "$tmp_dir/gate/summary.md"
grep -q '# Codex Maintainer Gate' "$tmp_dir/gate/summary.md"
grep -q '| Status | blocked |' "$tmp_dir/gate/summary.md"
grep -q '| Score | 1/12 |' "$tmp_dir/gate/summary.md"
grep -q -- '- sarif: `sarif/results.sarif`' "$tmp_dir/gate/summary.md"

./bin/codex-maintainer ci-summary \
  --gate "$tmp_dir/gate/gate.json" \
  --out "$tmp_dir/manual-summary.md" >/dev/null

grep -q '| High-risk findings | 3 |' "$tmp_dir/manual-summary.md"

if ./bin/codex-maintainer ci-summary --gate "$tmp_dir/missing.json" --out "$tmp_dir/missing.md" >/dev/null 2>&1; then
  echo "expected missing gate to fail" >&2
  exit 1
fi

grep -q 'Append CI gate step summary' actions/ci-gate/action.yml
grep -q 'GITHUB_STEP_SUMMARY' actions/ci-gate/action.yml

echo "ci summary tests passed"
