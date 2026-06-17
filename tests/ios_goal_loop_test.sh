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

./bin/shipguard ios goals --help >/dev/null
./bin/shipguard ios goals init --state "$state" --out "$next_goal" >/dev/null

test -f "$state"
test -f "$next_goal"
grep -q '"current_index": 0' "$state"
grep -q '"id": "shipguard-ios-doctor"' "$state"
grep -q '# iOS ShipGuard Goal: Implement iOS Doctor' "$next_goal"
grep -q '/goal Implement shipguard-ios-doctor' "$next_goal"

./bin/shipguard ios goals status --state "$state" --out "$tmp_dir/status.md" >/dev/null
grep -q 'Completed: 0/13' "$tmp_dir/status.md"
grep -q 'Current goal: `shipguard-ios-doctor`' "$tmp_dir/status.md"

./bin/shipguard ios goals emit \
  --goal shipguard-guided-plan \
  --out "$tmp_dir/guided-plan-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Generate Codex-Ready iOS Plans' "$tmp_dir/guided-plan-goal.md"
grep -q '/goal Implement shipguard-guided-plan' "$tmp_dir/guided-plan-goal.md"
grep -q 'ios plan' "$tmp_dir/guided-plan-goal.md"
grep -q './tests/ios_plan_test.sh' "$tmp_dir/guided-plan-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-proof-router \
  --out "$tmp_dir/proof-router-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Route iOS Proof' "$tmp_dir/proof-router-goal.md"
grep -q '/goal Implement shipguard-proof-router' "$tmp_dir/proof-router-goal.md"
grep -q 'ios prove' "$tmp_dir/proof-router-goal.md"
grep -q './tests/ios_prove_test.sh' "$tmp_dir/proof-router-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-ios-preview-bridge \
  --out "$tmp_dir/preview-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Preview iOS App In Codex' "$tmp_dir/preview-goal.md"
grep -q '/goal Implement shipguard-ios-preview-bridge' "$tmp_dir/preview-goal.md"
grep -q 'right-click context-menu' "$tmp_dir/preview-goal.md"
grep -q 'handoff.md' "$tmp_dir/preview-goal.md"
grep -q './tests/ios_preview_test.sh' "$tmp_dir/preview-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-devspace-mcp \
  --out "$tmp_dir/devspace-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Bridge ShipGuard Preview To ChatGPT' "$tmp_dir/devspace-goal.md"
grep -q '/goal Implement shipguard-devspace-mcp' "$tmp_dir/devspace-goal.md"
grep -q 'shipguard-preview-v2.html' "$tmp_dir/devspace-goal.md"
grep -q 'production-readiness reporting' "$tmp_dir/devspace-goal.md"
grep -q 'Markdown handoff' "$tmp_dir/devspace-goal.md"
grep -q 'target resolution' "$tmp_dir/devspace-goal.md"
grep -q './tests/ios_target_match_test.sh' "$tmp_dir/devspace-goal.md"
grep -q './tests/shipguard_devspace_mcp_test.sh' "$tmp_dir/devspace-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-codex-handoff-supervisor \
  --out "$tmp_dir/supervisor-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Supervise Codex Handoffs' "$tmp_dir/supervisor-goal.md"
grep -q '/goal Implement shipguard-codex-handoff-supervisor' "$tmp_dir/supervisor-goal.md"
grep -q './tests/ios_codex_handoff_test.sh' "$tmp_dir/supervisor-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-app-intelligence-audit \
  --out "$tmp_dir/app-intelligence-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Audit App Intelligence Surfaces' "$tmp_dir/app-intelligence-goal.md"
grep -q '/goal Implement shipguard-app-intelligence-audit' "$tmp_dir/app-intelligence-goal.md"
grep -q 'ios app-intelligence' "$tmp_dir/app-intelligence-goal.md"
grep -q './tests/ios_app_intelligence_test.sh' "$tmp_dir/app-intelligence-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-ai-capability-audit \
  --out "$tmp_dir/ai-readiness-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Audit AI Capability Choices' "$tmp_dir/ai-readiness-goal.md"
grep -q '/goal Implement shipguard-ai-capability-audit' "$tmp_dir/ai-readiness-goal.md"
grep -q 'ios ai-readiness' "$tmp_dir/ai-readiness-goal.md"
grep -q './tests/ios_ai_readiness_test.sh' "$tmp_dir/ai-readiness-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-privacy-security-redaction \
  --out "$tmp_dir/redaction-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Harden Privacy And Security Reports' "$tmp_dir/redaction-goal.md"
grep -q '/goal Implement shipguard-privacy-security-redaction' "$tmp_dir/redaction-goal.md"
grep -q 'ios redact' "$tmp_dir/redaction-goal.md"
grep -q './tests/ios_redaction_test.sh' "$tmp_dir/redaction-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-evals \
  --out "$tmp_dir/evals-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Evaluate ShipGuard Behavior' "$tmp_dir/evals-goal.md"
grep -q '/goal Implement shipguard-evals' "$tmp_dir/evals-goal.md"
grep -q 'ios eval' "$tmp_dir/evals-goal.md"
grep -q './tests/ios_shipguard_eval_test.sh' "$tmp_dir/evals-goal.md"

./bin/shipguard ios goals emit \
  --goal shipguard-plugin-polish \
  --out "$tmp_dir/plugin-polish-goal.md" >/dev/null
grep -q '# iOS ShipGuard Goal: Polish Plugin Packaging' "$tmp_dir/plugin-polish-goal.md"
grep -q '/goal Implement shipguard-plugin-polish' "$tmp_dir/plugin-polish-goal.md"
grep -q 'ios demo' "$tmp_dir/plugin-polish-goal.md"
grep -q './tests/ios_shipguard_demo_test.sh' "$tmp_dir/plugin-polish-goal.md"

if ./bin/shipguard ios goals complete \
  --state "$state" \
  --goal shipguard-guided-plan \
  --evidence "$evidence" >/dev/null 2>&1; then
  echo "expected completing a non-current goal to fail" >&2
  exit 1
fi

./bin/shipguard ios goals complete \
  --state "$state" \
  --goal shipguard-ios-doctor \
  --evidence "$evidence" \
  --notes "focused test proof" \
  --out "$next_goal" >/dev/null

grep -q '"current_index": 1' "$state"
grep -q '"status": "completed"' "$state"
grep -q '"evidence": "'"$evidence"'"' "$state"
grep -q '# iOS ShipGuard Goal: Map Target Risk Surfaces' "$next_goal"
grep -q '/goal Implement shipguard-target-risk-map' "$next_goal"

./bin/shipguard ios goals next --state "$state" --out "$tmp_dir/current.md" >/dev/null
grep -q 'Goal id: `shipguard-target-risk-map`' "$tmp_dir/current.md"

echo "ios goal loop tests passed"
