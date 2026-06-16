#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

state="$tmp_dir/goals.json"
next_goal="$tmp_dir/NEXT_SHIPGUARD_GOAL.md"
evidence="$tmp_dir/proof.md"

printf '# Proof\n\n- command passed\n' > "$evidence"

./bin/codex-maintainer ios goals --help >/dev/null
./bin/codex-maintainer ios goals init --state "$state" --out "$next_goal" >/dev/null

test -f "$state"
test -f "$next_goal"
grep -q '"current_index": 0' "$state"
grep -q '"id": "shipguard-ios-doctor"' "$state"
grep -q '# iOS Shipguard Goal: Implement iOS Doctor' "$next_goal"
grep -q '/goal Implement shipguard-ios-doctor' "$next_goal"

./bin/codex-maintainer ios goals status --state "$state" --out "$tmp_dir/status.md" >/dev/null
grep -q 'Completed: 0/13' "$tmp_dir/status.md"
grep -q 'Current goal: `shipguard-ios-doctor`' "$tmp_dir/status.md"

./bin/codex-maintainer ios goals emit \
  --goal shipguard-ios-preview-bridge \
  --out "$tmp_dir/preview-goal.md" >/dev/null
grep -q '# iOS Shipguard Goal: Preview iOS App In Codex' "$tmp_dir/preview-goal.md"
grep -q '/goal Implement shipguard-ios-preview-bridge' "$tmp_dir/preview-goal.md"
grep -q './tests/ios_preview_test.sh' "$tmp_dir/preview-goal.md"

./bin/codex-maintainer ios goals emit \
  --goal shipguard-devspace-mcp \
  --out "$tmp_dir/devspace-goal.md" >/dev/null
grep -q '# iOS Shipguard Goal: Bridge Shipguard Preview To ChatGPT' "$tmp_dir/devspace-goal.md"
grep -q '/goal Implement shipguard-devspace-mcp' "$tmp_dir/devspace-goal.md"
grep -q './tests/shipguard_devspace_mcp_test.sh' "$tmp_dir/devspace-goal.md"

./bin/codex-maintainer ios goals emit \
  --goal shipguard-codex-handoff-supervisor \
  --out "$tmp_dir/supervisor-goal.md" >/dev/null
grep -q '# iOS Shipguard Goal: Supervise Codex Handoffs' "$tmp_dir/supervisor-goal.md"
grep -q '/goal Implement shipguard-codex-handoff-supervisor' "$tmp_dir/supervisor-goal.md"
grep -q './tests/ios_codex_handoff_test.sh' "$tmp_dir/supervisor-goal.md"

if ./bin/codex-maintainer ios goals complete \
  --state "$state" \
  --goal shipguard-guided-plan \
  --evidence "$evidence" >/dev/null 2>&1; then
  echo "expected completing a non-current goal to fail" >&2
  exit 1
fi

./bin/codex-maintainer ios goals complete \
  --state "$state" \
  --goal shipguard-ios-doctor \
  --evidence "$evidence" \
  --notes "focused test proof" \
  --out "$next_goal" >/dev/null

grep -q '"current_index": 1' "$state"
grep -q '"status": "completed"' "$state"
grep -q '"evidence": "'"$evidence"'"' "$state"
grep -q '# iOS Shipguard Goal: Map Target Risk Surfaces' "$next_goal"
grep -q '/goal Implement shipguard-target-risk-map' "$next_goal"

./bin/codex-maintainer ios goals next --state "$state" --out "$tmp_dir/current.md" >/dev/null
grep -q 'Goal id: `shipguard-target-risk-map`' "$tmp_dir/current.md"

echo "ios goal loop tests passed"
