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
grep -q '"commandCount": 61' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
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
grep -q '"profileNativeFixPlanReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"profileNativeValidationReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"profileNativeValidationRerunReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"profileNativeProofHandoffReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"commandFamilyRuntimeOutputReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"trustHardeningReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"taskContractReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"externalPilotVerdictBenchReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"domainPackSDKReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"configurationBaselineReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"structuredEvidenceReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"agentAdapterReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"xcodeBuildMCPEvidenceReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"priorityActions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard score"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard prepare"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard verify"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
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
grep -q 'Profile-Native Fix-Plan Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Profile-Native Validation Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Profile-Native Validation Rerun Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Profile-Native Proof Handoff Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Command-Family Runtime Output Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Trust-Hardening Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Task-Contract Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'ShipGuard PilotBench Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Domain Pack SDK Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Configuration Baseline Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Structured Evidence Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Agent Adapter Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'XcodeBuildMCP Evidence Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Report Quality Questions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'ShipGuard PilotBench' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
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
profile_fix = data.get("profileNativeFixPlanReceipts") or {}
profile_validation = data.get("profileNativeValidationReceipts") or {}
profile_validation_rerun = data.get("profileNativeValidationRerunReceipts") or {}
profile_proof_handoff = data.get("profileNativeProofHandoffReceipts") or {}
command_family_output = data.get("commandFamilyRuntimeOutputReceipts") or {}
trust_hardening = data.get("trustHardeningReceipts") or {}
task_contract = data.get("taskContractReceipts") or {}
pilot_bench = data.get("externalPilotVerdictBenchReceipts") or {}
domain_pack_sdk = data.get("domainPackSDKReceipts") or {}
configuration_baseline = data.get("configurationBaselineReceipts") or {}
structured_evidence = data.get("structuredEvidenceReceipts") or {}
agent_adapter = data.get("agentAdapterReceipts") or {}
xcode_receipts = data.get("xcodeBuildMCPEvidenceReceipts") or {}
if probe.get("question") != "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?":
    raise SystemExit(f"unexpected probe question: {probe!r}")
for key in ("surfaceType", "identifier", "name", "baseScore", "depthScore", "depthChecks", "recommendation", "proofGuidance", "reason"):
    if key not in answer:
        raise SystemExit(f"probe answer missing {key}: {answer!r}")
if answer.get("surfaceType") != "cross-cutting" or answer.get("identifier") != "shipguard expo-mcp-eas-assurance-adapter":
    raise SystemExit(f"passing XcodeBuildMCP receipts should escalate to Expo MCP and EAS assurance adapter: {answer!r}")
if "runtimeDiffFirstVerification" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"diff-first verification should no longer be missing: {answer!r}")
if "runtimeIOSNotificationPermissionWorkflow" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"notification permission workflow should no longer be missing: {answer!r}")
if "runtimeStructuredEvidenceReceiptsV2" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"structured evidence receipts v2 should no longer be missing: {answer!r}")
if "runtimeCodexNativeTaskTraceAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Codex-native task trace adapter should no longer be missing: {answer!r}")
if "runtimeXcodeBuildMCPEvidenceAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"XcodeBuildMCP evidence adapter should no longer be missing: {answer!r}")
if "runtimeExpoMCPAndEASAdapter" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Expo MCP and EAS adapter gap should be explicit: {answer!r}")
for retired_signal in ("runtimeSkillPluginReceipts", "runtimeWorkflowChainReceipts", "runtimeScenarioMatrixReceipts", "runtimeScenarioFailureReceipts", "runtimeScenarioRemediationReceipts", "runtimeAdoptionReceipts", "runtimeTargetOnboardingReceipts", "runtimeMultiProfileOnboardingReceipts", "runtimeProfileNativeFirstAuditReceipts", "runtimeProfileNativeFixPlanReceipts", "runtimeProfileNativeValidationReceipts", "runtimeProfileNativeValidationRerunReceipts", "runtimeProfileNativeProofHandoffReceipts", "runtimeCommandFamilyOutputReceipts", "runtimeTrustHardeningReceipts", "runtimeProofGatedTaskContract", "runtimeIOSNotificationPermissionWorkflow", "runtimeExternalPilotVerdictBench", "runtimeDomainPackSDK", "runtimeConfigurationBaselineSuppressions", "runtimeStructuredEvidenceReceiptsV2", "runtimeCodexNativeTaskTraceAdapter", "runtimeXcodeBuildMCPEvidenceAdapter"):
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
if command_family.get("commandCount") != 61 or command_family.get("passedCommandCount") != 61:
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
if profile_fix.get("status") != "pass":
    raise SystemExit(f"profile-native fix-plan receipts should pass: {profile_fix!r}")
if profile_fix.get("receiptCount") != 1 or profile_fix.get("passedReceiptCount") != 1 or profile_fix.get("commandCount") != 10:
    raise SystemExit(f"expected one profile-native fix-plan receipt and ten commands: {profile_fix!r}")
profile_fix_ids = {item.get("id") for item in profile_fix.get("receipts") or []}
if profile_fix_ids != {"web-backend-cli-fix-plans"}:
    raise SystemExit(f"unexpected profile-native fix-plan receipt fixtures: {profile_fix_ids!r}")
for item in profile_fix.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"profile-native fix-plan receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "init-web-starter",
        "web-first-audit",
        "web-fix-plan",
        "init-backend-starter",
        "backend-first-audit",
        "backend-fix-plan",
        "init-cli-starter",
        "cli-first-audit",
        "cli-fix-plan",
        "profile-fix-plan-quality",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected profile-native fix-plan command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"profile-native fix-plan command should pass without missing checks: {command!r}")
if profile_validation.get("status") != "pass":
    raise SystemExit(f"profile-native validation receipts should pass: {profile_validation!r}")
if profile_validation.get("receiptCount") != 1 or profile_validation.get("passedReceiptCount") != 1 or profile_validation.get("commandCount") != 4:
    raise SystemExit(f"expected one profile-native validation receipt and four commands: {profile_validation!r}")
profile_validation_ids = {item.get("id") for item in profile_validation.get("receipts") or []}
if profile_validation_ids != {"web-backend-cli-validation-receipts"}:
    raise SystemExit(f"unexpected profile-native validation receipt fixtures: {profile_validation_ids!r}")
for item in profile_validation.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"profile-native validation receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "web-validation-plan",
        "backend-validation-plan",
        "cli-validation-plan",
        "profile-validation-quality",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected profile-native validation command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"profile-native validation command should pass without missing checks: {command!r}")
if profile_validation_rerun.get("status") != "pass":
    raise SystemExit(f"profile-native validation rerun receipts should pass: {profile_validation_rerun!r}")
if profile_validation_rerun.get("receiptCount") != 1 or profile_validation_rerun.get("passedReceiptCount") != 1 or profile_validation_rerun.get("commandCount") != 9:
    raise SystemExit(f"expected one profile-native validation rerun receipt and nine commands: {profile_validation_rerun!r}")
if profile_validation_rerun.get("remediationPairCount") != 3 or profile_validation_rerun.get("passedRemediationPairCount") != 3:
    raise SystemExit(f"expected three passing profile-native validation rerun pairs: {profile_validation_rerun!r}")
profile_validation_rerun_ids = {item.get("id") for item in profile_validation_rerun.get("receipts") or []}
if profile_validation_rerun_ids != {"web-backend-cli-validation-rerun-receipts"}:
    raise SystemExit(f"unexpected profile-native validation rerun receipt fixtures: {profile_validation_rerun_ids!r}")
for item in profile_validation_rerun.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"profile-native validation rerun receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "web-blocked-lint-plan",
        "web-repair-lint-script",
        "web-rerun-lint-plan",
        "backend-blocked-lint-plan",
        "backend-repair-lint-signal",
        "backend-rerun-lint-plan",
        "cli-blocked-help-plan",
        "cli-repair-bin-entry",
        "cli-rerun-help-plan",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected profile-native validation rerun command set: {command_ids!r}")
    pair_ids = {pair.get("id") for pair in item.get("remediationPairs") or []}
    expected_pairs = {"web-lint-smallest-repair", "backend-lint-smallest-repair", "cli-help-smallest-repair"}
    if pair_ids != expected_pairs:
        raise SystemExit(f"unexpected profile-native validation rerun pairs: {pair_ids!r}")
    for pair in item.get("remediationPairs") or []:
        if pair.get("status") != "pass":
            raise SystemExit(f"profile-native validation rerun pair should pass: {pair!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"profile-native validation rerun command should pass without missing checks: {command!r}")
if profile_proof_handoff.get("status") != "pass":
    raise SystemExit(f"profile-native proof handoff receipts should pass: {profile_proof_handoff!r}")
if profile_proof_handoff.get("receiptCount") != 1 or profile_proof_handoff.get("passedReceiptCount") != 1 or profile_proof_handoff.get("commandCount") != 3:
    raise SystemExit(f"expected one profile-native proof handoff receipt and three commands: {profile_proof_handoff!r}")
profile_proof_handoff_ids = {item.get("id") for item in profile_proof_handoff.get("receipts") or []}
if profile_proof_handoff_ids != {"web-backend-cli-proof-handoffs"}:
    raise SystemExit(f"unexpected profile-native proof handoff receipt fixtures: {profile_proof_handoff_ids!r}")
for item in profile_proof_handoff.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"profile-native proof handoff receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "web-copy-ready-proof-handoff",
        "backend-copy-ready-proof-handoff",
        "cli-copy-ready-proof-handoff",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected profile-native proof handoff command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"profile-native proof handoff command should pass without missing checks: {command!r}")
if command_family_output.get("status") != "pass":
    raise SystemExit(f"command-family runtime-output receipts should pass: {command_family_output!r}")
if command_family_output.get("receiptCount") != 1 or command_family_output.get("passedReceiptCount") != 1 or command_family_output.get("commandCount") != 7:
    raise SystemExit(f"expected one command-family runtime-output receipt and seven commands: {command_family_output!r}")
command_family_output_ids = {item.get("id") for item in command_family_output.get("receipts") or []}
if command_family_output_ids != {"major-family-report-outputs"}:
    raise SystemExit(f"unexpected command-family runtime-output receipt fixtures: {command_family_output_ids!r}")
for item in command_family_output.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"command-family runtime-output receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "brand-output",
        "ios-doctor-output",
        "ios-design-output",
        "web-audit-output",
        "web-plan-output",
        "docs-check-output",
        "release-manifest-output",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected command-family runtime-output command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"command-family runtime-output command should pass without missing checks: {command!r}")
if trust_hardening.get("status") != "pass":
    raise SystemExit(f"trust-hardening receipts should pass: {trust_hardening!r}")
if trust_hardening.get("receiptCount") != 1 or trust_hardening.get("passedReceiptCount") != 1 or trust_hardening.get("commandCount") != 4:
    raise SystemExit(f"expected one trust-hardening receipt and four commands: {trust_hardening!r}")
trust_hardening_ids = {item.get("id") for item in trust_hardening.get("receipts") or []}
if trust_hardening_ids != {"action-devspace-archive-release-provenance"}:
    raise SystemExit(f"unexpected trust-hardening receipt fixtures: {trust_hardening_ids!r}")
for item in trust_hardening.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"trust-hardening receipt should pass without missing checks: {item!r}")
    trust_checks = item.get("trustChecks") or {}
    action_check = trust_checks.get("actionRunInputInterpolation") or {}
    if action_check.get("status") != "pass" or action_check.get("violationCount") != 0:
        raise SystemExit(f"action input interpolation should have no shell-block violations: {action_check!r}")
    archive_check = trust_checks.get("unsafeArchiveExtraction") or {}
    if archive_check.get("status") != "pass":
        raise SystemExit(f"unsafe archive extraction should be rejected: {archive_check!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "devspace-token-in-url-blocked",
        "release-proof-bad-host-blocked",
        "release-proof-tag-mismatch-blocked",
        "release-manifest-provenance-output",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected trust-hardening command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"trust-hardening command should pass without missing checks: {command!r}")
if task_contract.get("status") != "pass":
    raise SystemExit(f"task-contract receipts should pass: {task_contract!r}")
if task_contract.get("receiptCount") != 1 or task_contract.get("passedReceiptCount") != 1 or task_contract.get("commandCount") != 5:
    raise SystemExit(f"expected one task-contract receipt and five commands: {task_contract!r}")
task_contract_ids = {item.get("id") for item in task_contract.get("receipts") or []}
if task_contract_ids != {"prepare-verify-proof-gate"}:
    raise SystemExit(f"unexpected task-contract receipt fixtures: {task_contract_ids!r}")
for item in task_contract.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"task-contract receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-ios-notification-task",
        "verify-scoped-diff-pass",
        "verify-generic-permission-receipt-review",
        "verify-invalid-receipt-blocked",
        "verify-protected-diff-blocked",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected task-contract command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"task-contract command should pass without missing checks: {command!r}")
if pilot_bench.get("status") != "pass":
    raise SystemExit(f"PilotBench receipts should pass: {pilot_bench!r}")
if pilot_bench.get("receiptCount") != 1 or pilot_bench.get("passedReceiptCount") != 1 or pilot_bench.get("commandCount") != 1:
    raise SystemExit(f"expected one PilotBench receipt and one command: {pilot_bench!r}")
pilot_receipt_ids = {item.get("id") for item in pilot_bench.get("receipts") or []}
if pilot_receipt_ids != {"public-verdict-traces"}:
    raise SystemExit(f"unexpected PilotBench receipt fixtures: {pilot_receipt_ids!r}")
for item in pilot_bench.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"PilotBench receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    if command_ids != {"pilot-bench-public-traces"}:
        raise SystemExit(f"unexpected PilotBench command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"PilotBench command should pass without missing checks: {command!r}")
if domain_pack_sdk.get("status") != "pass":
    raise SystemExit(f"Domain Pack SDK receipts should pass: {domain_pack_sdk!r}")
if domain_pack_sdk.get("receiptCount") != 1 or domain_pack_sdk.get("passedReceiptCount") != 1 or domain_pack_sdk.get("commandCount") != 3:
    raise SystemExit(f"expected one Domain Pack SDK receipt and three commands: {domain_pack_sdk!r}")
domain_pack_receipt_ids = {item.get("id") for item in domain_pack_sdk.get("receipts") or []}
if domain_pack_receipt_ids != {"synthetic-pack-extension"}:
    raise SystemExit(f"unexpected Domain Pack SDK receipt fixtures: {domain_pack_receipt_ids!r}")
for item in domain_pack_sdk.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"Domain Pack SDK receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-synthetic-domain-pack",
        "verify-synthetic-pack-review",
        "verify-synthetic-pack-pass",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected Domain Pack SDK command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"Domain Pack SDK command should pass without missing checks: {command!r}")
if configuration_baseline.get("status") != "pass":
    raise SystemExit(f"configuration baseline receipts should pass: {configuration_baseline!r}")
if configuration_baseline.get("receiptCount") != 1 or configuration_baseline.get("passedReceiptCount") != 1 or configuration_baseline.get("commandCount") != 6:
    raise SystemExit(f"expected one configuration baseline receipt and six commands: {configuration_baseline!r}")
configuration_baseline_receipt_ids = {item.get("id") for item in configuration_baseline.get("receipts") or []}
if configuration_baseline_receipt_ids != {"accepted-expired-regression"}:
    raise SystemExit(f"unexpected configuration baseline receipt fixtures: {configuration_baseline_receipt_ids!r}")
for item in configuration_baseline.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"configuration baseline receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-baseline-active",
        "verify-baseline-accepted-pass",
        "prepare-baseline-expired",
        "verify-baseline-expired-blocked",
        "prepare-baseline-regression",
        "verify-baseline-regression-blocked",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected configuration baseline command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"configuration baseline command should pass without missing checks: {command!r}")
if structured_evidence.get("status") != "pass":
    raise SystemExit(f"structured evidence receipts should pass: {structured_evidence!r}")
if structured_evidence.get("receiptCount") != 1 or structured_evidence.get("passedReceiptCount") != 1 or structured_evidence.get("commandCount") != 6:
    raise SystemExit(f"expected one structured evidence receipt and six commands: {structured_evidence!r}")
structured_evidence_receipt_ids = {item.get("id") for item in structured_evidence.get("receipts") or []}
if structured_evidence_receipt_ids != {"v2-compatibility-freshness-downgrade"}:
    raise SystemExit(f"unexpected structured evidence receipt fixtures: {structured_evidence_receipt_ids!r}")
for item in structured_evidence.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"structured evidence receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-structured-receipt-task",
        "verify-v2-validation-receipt-pass",
        "verify-legacy-validation-receipt-pass",
        "verify-unsupported-schema-receipt-blocked",
        "verify-manual-receipt-downgraded-review",
        "verify-stale-v2-receipt-blocked",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected structured evidence command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"structured evidence command should pass without missing checks: {command!r}")
if agent_adapter.get("status") != "pass":
    raise SystemExit(f"agent adapter receipts should pass: {agent_adapter!r}")
if agent_adapter.get("receiptCount") != 1 or agent_adapter.get("passedReceiptCount") != 1 or agent_adapter.get("commandCount") != 4:
    raise SystemExit(f"expected one agent adapter receipt and four commands: {agent_adapter!r}")
agent_adapter_receipt_ids = {item.get("id") for item in agent_adapter.get("receipts") or []}
if agent_adapter_receipt_ids != {"codex-task-trace-adapter"}:
    raise SystemExit(f"unexpected agent adapter receipt fixtures: {agent_adapter_receipt_ids!r}")
for item in agent_adapter.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"agent adapter receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-agent-trace-task",
        "agent-trace-run-verify-pass",
        "agent-trace-overbudget-blocked",
        "codex-trace-alias-pass",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected agent adapter command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"agent adapter command should pass without missing checks: {command!r}")
if xcode_receipts.get("status") != "pass":
    raise SystemExit(f"XcodeBuildMCP evidence receipts should pass: {xcode_receipts!r}")
if xcode_receipts.get("receiptCount") != 1 or xcode_receipts.get("passedReceiptCount") != 1 or xcode_receipts.get("commandCount") != 3:
    raise SystemExit(f"expected one XcodeBuildMCP evidence receipt and three commands: {xcode_receipts!r}")
xcode_receipt_ids = {item.get("id") for item in xcode_receipts.get("receipts") or []}
if xcode_receipt_ids != {"simulator-build-ui-profiler-adapter"}:
    raise SystemExit(f"unexpected XcodeBuildMCP evidence receipt fixtures: {xcode_receipt_ids!r}")
for item in xcode_receipts.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"XcodeBuildMCP evidence receipt should pass without missing checks: {item!r}")
    command_ids = {command.get("id") for command in item.get("commands") or []}
    expected_commands = {
        "prepare-xcodebuildmcp-trace-task",
        "agent-trace-xcodebuildmcp-proof-pass",
        "codex-trace-xcodebuildmcp-proof-pass",
    }
    if command_ids != expected_commands:
        raise SystemExit(f"unexpected XcodeBuildMCP evidence command set: {command_ids!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"XcodeBuildMCP evidence command should pass without missing checks: {command!r}")
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
    "profile-native fix-plan receipts so web, backend, and CLI first audits",
    "profile-native validation receipts so web, backend, and CLI fix plans",
    "profile-native validation rerun receipts so repaired web, backend, and CLI plans",
    "profile-native proof handoff receipts so repaired web, backend, and CLI plans",
    "command-family runtime-output receipts so every major public family",
    "trust-hardening receipts for GitHub Action input interpolation",
    "proof-gated task contract",
    "external pilot verdict bench",
    "Domain Pack SDK",
    "configuration baselines and suppressions",
    "structured evidence receipts v2",
    "Codex-native task and trace adapter",
    "XcodeBuildMCP evidence adapter",
)
if any(any(phrase in question for phrase in retired_phrases) for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"answered runtime receipt questions should be retired after implementation: {data.get('reportQualityQuestions')!r}")
if not any("Expo MCP and EAS assurance adapter" in question for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"expected Expo MCP and EAS adapter quality question: {data.get('reportQualityQuestions')!r}")
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
grep -q 'Expo MCP and EAS assurance adapter' "$tmp_dir/quality/ios-report-quality.md"

echo "tool value gauntlet tests passed"
