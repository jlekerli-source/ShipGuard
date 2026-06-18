#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard value-gauntlet --help >/dev/null
./bin/shipguard value-gauntlet \
  --path . \
  --out "$tmp_dir/gauntlet" >/dev/null

test -f "$tmp_dir/gauntlet/tool-value-gauntlet.json"
test -f "$tmp_dir/gauntlet/tool-value-gauntlet.md"
python3 -m json.tool "$tmp_dir/gauntlet/tool-value-gauntlet.json" >/dev/null

grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"surface": "ShipGuard Tool Value Gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"intent": "shipguard-product-qa"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"shipguardOnly": true' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"commandCount": 54' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"pluginCount": 1' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"actions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"skills":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"plugins":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"lowestValueSurfaceProbe":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"runtimeOutputProbe":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"runtimeOutputNegativeFixtures":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"runtimeCommandFamilyCoverage":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"skillPluginRuntimeReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"workflowChainReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"scenarioMatrixReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"scenarioFailureReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"scenarioRemediationReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"adoptionReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"targetOnboardingReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"multiProfileOnboardingReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"profileNativeFirstAuditReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"priorityActions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard score"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard value-gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "alarm-testing"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/alarm-testing/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "notification-permissions"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/notification-permissions/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "release-checklist"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/release-checklist/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "bug-triage"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/bug-triage/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "ui-polish"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/ui-polish/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"

grep -q '# ShipGuard Tool Value Gauntlet' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Priority Actions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Lowest-Value Surface Probe' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Commands' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Skills' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Plugins' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Actions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Docs' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Runtime Output Probe' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Runtime Output Negative Fixtures' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Runtime Command-Family Coverage' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Skill/Plugin Runtime Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Workflow Chain Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Scenario Matrix Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Scenario Failure Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Scenario Remediation Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Fresh-User Adoption Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Target Onboarding Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Multi-Profile Onboarding Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Profile-Native First-Audit Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Report Quality Questions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'profile-native fix-plan receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}
runtime = data.get("runtimeOutputProbe") or {}
negative = data.get("runtimeOutputNegativeFixtures") or {}
command_family = data.get("runtimeCommandFamilyCoverage") or {}
receipts = data.get("skillPluginRuntimeReceipts") or {}
workflow_chain = data.get("workflowChainReceipts") or {}
scenario_matrix = data.get("scenarioMatrixReceipts") or {}
scenario_failure = data.get("scenarioFailureReceipts") or {}
scenario_remediation = data.get("scenarioRemediationReceipts") or {}
adoption = data.get("adoptionReceipts") or {}
target_onboarding = data.get("targetOnboardingReceipts") or {}
multi_profile = data.get("multiProfileOnboardingReceipts") or {}
profile_native = data.get("profileNativeFirstAuditReceipts") or {}
if probe.get("question") != "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?":
    raise SystemExit(f"unexpected probe question: {probe!r}")
for key in ("surfaceType", "identifier", "name", "baseScore", "depthScore", "depthChecks", "recommendation", "proofGuidance", "reason"):
    if key not in answer:
        raise SystemExit(f"probe answer missing {key}: {answer!r}")
if answer.get("surfaceType") != "cross-cutting" or answer.get("identifier") != "shipguard value-gauntlet profile-native-fix-plan-receipts":
    raise SystemExit(f"passing profile-native first-audit receipts should escalate to profile-native fix-plan receipts: {answer!r}")
if "runtimeProfileNativeFixPlanReceipts" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"profile-native fix-plan receipt gap should be explicit: {answer!r}")
for retired_signal in ("runtimeSkillPluginReceipts", "runtimeWorkflowChainReceipts", "runtimeScenarioMatrixReceipts", "runtimeScenarioFailureReceipts", "runtimeScenarioRemediationReceipts", "runtimeAdoptionReceipts", "runtimeTargetOnboardingReceipts", "runtimeMultiProfileOnboardingReceipts", "runtimeProfileNativeFirstAuditReceipts"):
    if retired_signal in answer.get("missingDepthSignals", []):
        raise SystemExit(f"{retired_signal} should no longer be missing after fixture proof: {answer!r}")
if not isinstance(probe.get("rankedSurfaces"), list) or not probe["rankedSurfaces"]:
    raise SystemExit("lowest-value surface probe should rank surfaces")
if runtime.get("status") != "pass":
    raise SystemExit(f"runtime output probe should pass on representative commands: {runtime!r}")
if runtime.get("averageScore") != 100:
    raise SystemExit(f"runtime output probe should score complete machine-readable output: {runtime!r}")
command_ids = {item.get("id") for item in runtime.get("commands") or []}
expected_ids = {"brand-deck", "ios-doctor-demo", "ios-design-demo", "report-quality-fixture"}
if command_ids != expected_ids:
    raise SystemExit(f"unexpected runtime command set: {command_ids!r}")
for item in runtime.get("commands") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"runtime command should pass without missing checks: {item!r}")
if negative.get("status") != "pass":
    raise SystemExit(f"negative runtime fixture probe should pass: {negative!r}")
if negative.get("fixtureCount") != 2 or negative.get("passedFixtureCount") != 2:
    raise SystemExit(f"expected two negative runtime fixtures to reject bad reports: {negative!r}")
case_ids = {item.get("id") for item in negative.get("cases") or []}
if case_ids != {"decorative-empty-report", "boundaryless-design-report"}:
    raise SystemExit(f"unexpected negative fixture cases: {case_ids!r}")
for item in negative.get("cases") or []:
    if item.get("status") == "pass" or item.get("fixturePassed") is not True:
        raise SystemExit(f"negative fixture should fail report scoring but pass fixture expectation: {item!r}")
if command_family.get("status") != "pass":
    raise SystemExit(f"runtime command-family coverage should pass: {command_family!r}")
if command_family.get("commandCount") != 54 or command_family.get("passedCommandCount") != 54:
    raise SystemExit(f"expected all public command help paths to pass: {command_family!r}")
for item in command_family.get("commands") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"command help path should pass without missing checks: {item!r}")
if receipts.get("status") != "pass":
    raise SystemExit(f"skill/plugin runtime receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 3 or receipts.get("passedReceiptCount") != 3 or receipts.get("commandCount") != 5:
    raise SystemExit(f"expected three receipt fixtures and five receipt commands: {receipts!r}")
receipt_ids = {item.get("id") for item in receipts.get("receipts") or []}
expected_receipts = {"ios-shipguard-design-audit", "starter-ui-polish-plan", "plugin-cache-status"}
if receipt_ids != expected_receipts:
    raise SystemExit(f"unexpected skill/plugin receipt fixtures: {receipt_ids!r}")
for item in receipts.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"skill/plugin receipt should pass without missing checks: {item!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"receipt command should pass without missing checks: {command!r}")
if workflow_chain.get("status") != "pass":
    raise SystemExit(f"workflow-chain receipts should pass: {workflow_chain!r}")
if workflow_chain.get("receiptCount") != 1 or workflow_chain.get("passedReceiptCount") != 1 or workflow_chain.get("commandCount") != 5:
    raise SystemExit(f"expected one workflow-chain receipt and five commands: {workflow_chain!r}")
workflow_ids = {item.get("id") for item in workflow_chain.get("receipts") or []}
if workflow_ids != {"report-quality-to-spec-and-next-goal"}:
    raise SystemExit(f"unexpected workflow-chain receipt fixtures: {workflow_ids!r}")
for item in workflow_chain.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"workflow-chain receipt should pass without missing checks: {item!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"workflow-chain command should pass without missing checks: {command!r}")
if scenario_matrix.get("status") != "pass":
    raise SystemExit(f"scenario-matrix receipts should pass: {scenario_matrix!r}")
if scenario_matrix.get("receiptCount") != 1 or scenario_matrix.get("passedReceiptCount") != 1 or scenario_matrix.get("commandCount") != 15:
    raise SystemExit(f"expected one scenario-matrix receipt and fifteen commands: {scenario_matrix!r}")
scenario_ids = {item.get("id") for item in scenario_matrix.get("receipts") or []}
if scenario_ids != {"full-public-maintainer-loop"}:
    raise SystemExit(f"unexpected scenario-matrix receipt fixtures: {scenario_ids!r}")
for item in scenario_matrix.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"scenario-matrix receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "ios-doctor",
        "ios-inventory",
        "ios-ui-plan",
        "ios-design-eval",
        "design-report-quality",
        "docs-check",
        "transcript-redact",
        "transcript-verify",
        "ci-gate",
        "ci-summary",
        "codex-plugin-status",
        "release-manifest",
        "release-manifest-verify",
        "release-index",
        "release-replay",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected scenario-matrix command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"scenario-matrix command should pass without missing checks: {command!r}")
if scenario_failure.get("status") != "pass":
    raise SystemExit(f"scenario-failure receipts should pass: {scenario_failure!r}")
if scenario_failure.get("receiptCount") != 1 or scenario_failure.get("passedReceiptCount") != 1 or scenario_failure.get("commandCount") != 5:
    raise SystemExit(f"expected one scenario-failure receipt and five commands: {scenario_failure!r}")
failure_ids = {item.get("id") for item in scenario_failure.get("receipts") or []}
if failure_ids != {"bad-evidence-blocks"}:
    raise SystemExit(f"unexpected scenario-failure receipt fixtures: {failure_ids!r}")
for item in scenario_failure.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"scenario-failure receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "unsafe-transcript-blocked",
        "broken-docs-blocked",
        "stale-plugin-cache-blocked",
        "incomplete-release-manifest",
        "incomplete-release-replay-blocked",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected scenario-failure command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"scenario-failure command should pass without missing checks: {command!r}")
    expected_nonzero = {
        "unsafe-transcript-blocked",
        "broken-docs-blocked",
        "stale-plugin-cache-blocked",
        "incomplete-release-replay-blocked",
    }
    for command in item.get("commands") or []:
        if command.get("id") in expected_nonzero and command.get("exitCode") == 0:
            raise SystemExit(f"failure-path command should prove nonzero blocking: {command!r}")
if scenario_remediation.get("status") != "pass":
    raise SystemExit(f"scenario-remediation receipts should pass: {scenario_remediation!r}")
if scenario_remediation.get("receiptCount") != 1 or scenario_remediation.get("passedReceiptCount") != 1 or scenario_remediation.get("commandCount") != 12:
    raise SystemExit(f"expected one scenario-remediation receipt and twelve commands: {scenario_remediation!r}")
if scenario_remediation.get("remediationPairCount") != 4 or scenario_remediation.get("passedRemediationPairCount") != 4:
    raise SystemExit(f"expected four passing remediation pairs: {scenario_remediation!r}")
remediation_ids = {item.get("id") for item in scenario_remediation.get("receipts") or []}
if remediation_ids != {"blocked-to-repaired-loop"}:
    raise SystemExit(f"unexpected scenario-remediation receipt fixtures: {remediation_ids!r}")
for item in scenario_remediation.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"scenario-remediation receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "unsafe-transcript-blocked",
        "transcript-redact-repair",
        "transcript-verify-clean",
        "broken-docs-blocked",
        "repair-docs-link-and-rerun",
        "stale-plugin-cache-blocked",
        "fresh-plugin-cache-pass",
        "incomplete-release-manifest",
        "incomplete-release-replay-blocked",
        "complete-release-manifest",
        "complete-release-index",
        "complete-release-replay",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected scenario-remediation command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"scenario-remediation command should pass without missing checks: {command!r}")
    expected_nonzero = {
        "unsafe-transcript-blocked",
        "broken-docs-blocked",
        "stale-plugin-cache-blocked",
        "incomplete-release-replay-blocked",
    }
    for command in item.get("commands") or []:
        if command.get("id") in expected_nonzero and command.get("exitCode") == 0:
            raise SystemExit(f"remediation blocked command should prove nonzero blocking: {command!r}")
    pair_ids = {pair.get("id") for pair in item.get("remediationPairs") or []}
    expected_pairs = {
        "privacy-redaction-remediation",
        "docs-link-remediation",
        "plugin-cache-remediation",
        "release-proof-remediation",
    }
    if pair_ids != expected_pairs:
        raise SystemExit(f"unexpected remediation pair set: {pair_ids!r}")
    for pair in item.get("remediationPairs") or []:
        if pair.get("status") != "pass" or pair.get("missing"):
            raise SystemExit(f"remediation pair should pass without missing checks: {pair!r}")
if adoption.get("status") != "pass":
    raise SystemExit(f"adoption receipts should pass: {adoption!r}")
if adoption.get("receiptCount") != 1 or adoption.get("passedReceiptCount") != 1 or adoption.get("commandCount") != 6:
    raise SystemExit(f"expected one adoption receipt and six commands: {adoption!r}")
adoption_ids = {item.get("id") for item in adoption.get("receipts") or []}
if adoption_ids != {"fresh-package-first-audit"}:
    raise SystemExit(f"unexpected adoption receipt fixtures: {adoption_ids!r}")
for item in adoption.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"adoption receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "package-from-fresh-copy",
        "install-to-temp-prefix",
        "installed-version",
        "fresh-plugin-cache-status",
        "first-useful-audit",
        "next-command-handoff",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected adoption command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"adoption command should pass without missing checks: {command!r}")
    if any("stdout" in command or "stderr" in command for command in item.get("commands") or []):
        raise SystemExit(f"adoption commands should not store raw stdout/stderr in the public report: {item!r}")
if target_onboarding.get("status") != "pass":
    raise SystemExit(f"target-onboarding receipts should pass: {target_onboarding!r}")
if target_onboarding.get("receiptCount") != 1 or target_onboarding.get("passedReceiptCount") != 1 or target_onboarding.get("commandCount") != 6:
    raise SystemExit(f"expected one target-onboarding receipt and six commands: {target_onboarding!r}")
target_onboarding_ids = {item.get("id") for item in target_onboarding.get("receipts") or []}
if target_onboarding_ids != {"fresh-ios-target-first-plan"}:
    raise SystemExit(f"unexpected target-onboarding receipt fixtures: {target_onboarding_ids!r}")
for item in target_onboarding.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"target-onboarding receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "init-ios-starter",
        "starter-doctor",
        "toolkit-validate",
        "ios-doctor-target",
        "ios-inventory-target",
        "first-scoped-plan",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected target-onboarding command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"target-onboarding command should pass without missing checks: {command!r}")
if multi_profile.get("status") != "pass":
    raise SystemExit(f"multi-profile onboarding receipts should pass: {multi_profile!r}")
if multi_profile.get("receiptCount") != 1 or multi_profile.get("passedReceiptCount") != 1 or multi_profile.get("commandCount") != 9:
    raise SystemExit(f"expected one multi-profile onboarding receipt and nine commands: {multi_profile!r}")
multi_profile_ids = {item.get("id") for item in multi_profile.get("receipts") or []}
if multi_profile_ids != {"all-starter-profiles-init-doctor"}:
    raise SystemExit(f"unexpected multi-profile onboarding receipt fixtures: {multi_profile_ids!r}")
for item in multi_profile.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"multi-profile onboarding receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "init-ios-starter",
        "doctor-ios-starter",
        "init-web-starter",
        "doctor-web-starter",
        "init-backend-starter",
        "doctor-backend-starter",
        "init-cli-starter",
        "doctor-cli-starter",
        "toolkit-validate",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected multi-profile onboarding command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"multi-profile onboarding command should pass without missing checks: {command!r}")
if profile_native.get("status") != "pass":
    raise SystemExit(f"profile-native first-audit receipts should pass: {profile_native!r}")
if profile_native.get("receiptCount") != 1 or profile_native.get("passedReceiptCount") != 1 or profile_native.get("commandCount") != 7:
    raise SystemExit(f"expected one profile-native first-audit receipt and seven commands: {profile_native!r}")
profile_native_ids = {item.get("id") for item in profile_native.get("receipts") or []}
if profile_native_ids != {"web-backend-cli-first-audits"}:
    raise SystemExit(f"unexpected profile-native first-audit receipt fixtures: {profile_native_ids!r}")
for item in profile_native.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"profile-native first-audit receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "init-web-starter",
        "web-first-audit",
        "init-backend-starter",
        "backend-first-audit",
        "init-cli-starter",
        "cli-first-audit",
        "profile-report-quality",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected profile-native first-audit command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"profile-native first-audit command should pass without missing checks: {command!r}")
if "Which ShipGuard command" in data.get("reportQualityQuestions", []):
    raise SystemExit("the answered lowest-value question should not remain a report-quality question")
retired_phrases = (
    "execute representative commands and compare actual output",
    "decorative but low-value reports so output scoring cannot become ceremonial",
    "command-family matrix so every major ShipGuard surface gets executed over time",
    "skill/plugin runtime receipt fixtures so Codex guidance is tested through realistic invoked workflows",
    "workflow chain receipts so report-quality questions become spec-workflow tasks",
    "scenario-matrix receipts that execute complete public developer journeys",
    "scenario-failure receipts that prove complete public developer journeys reject missing proof",
    "scenario-remediation receipts that pair each blocked developer journey",
    "adoption receipts that prove a fresh user can install",
    "target-onboarding receipts that prove a fresh app repo",
    "multi-profile onboarding receipts that prove",
    "profile-native first-audit receipts so web, backend, and CLI targets",
)
if any(any(phrase in question for phrase in retired_phrases) for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"runtime-output, negative-fixture, command-family, skill/plugin receipt, workflow-chain, scenario-matrix, scenario-failure, scenario-remediation, adoption, target-onboarding, and multi-profile onboarding questions should be retired after implementation: {data.get('reportQualityQuestions')!r}")
if not any("profile-native fix-plan receipts" in question for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"expected profile-native fix-plan quality question: {data.get('reportQualityQuestions')!r}")
PY

json_stdout="$(./bin/shipguard value-gauntlet --path . --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
grep -q '"tool": "shipguard value-gauntlet"' <<<"$json_stdout"

markdown_stdout="$(./bin/shipguard value-gauntlet --path . --markdown)"
grep -q '# ShipGuard Tool Value Gauntlet' <<<"$markdown_stdout"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/gauntlet" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null
grep -q '"tool": "shipguard ios report-quality"' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/quality/ios-report-quality.json"
grep -q 'ShipGuard Tool Value Gauntlet' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'profile-native fix-plan receipts' "$tmp_dir/quality/ios-report-quality.md"

echo "tool value gauntlet tests passed"
