#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard value-gauntlet \
  --path . \
  --out "$tmp_dir/gauntlet" >/dev/null

test -f "$tmp_dir/gauntlet/tool-value-gauntlet.json"
test -f "$tmp_dir/gauntlet/tool-value-gauntlet.md"

grep -q '"taskContractReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"domainPackSDKReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"configurationBaselineReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"structuredEvidenceReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"conciseVerdictResultUXReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Task-Contract Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Domain Pack SDK' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Configuration Baseline Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Structured Evidence Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Concise Verdict Result UX Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"

python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("taskContractReceipts") or {}
domain_pack_sdk = data.get("domainPackSDKReceipts") or {}
configuration_baseline = data.get("configurationBaselineReceipts") or {}
structured_evidence = data.get("structuredEvidenceReceipts") or {}
concise_result_ux = data.get("conciseVerdictResultUXReceipts") or {}
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}

if receipts.get("status") != "pass":
    raise SystemExit(f"task-contract receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 1 or receipts.get("passedReceiptCount") != 1:
    raise SystemExit(f"expected one passing task-contract receipt: {receipts!r}")
if receipts.get("commandCount") != 5:
    raise SystemExit(f"expected five task-contract commands: {receipts!r}")

receipt = (receipts.get("receipts") or [{}])[0]
if receipt.get("id") != "prepare-verify-proof-gate":
    raise SystemExit(f"unexpected task-contract receipt id: {receipt!r}")
if receipt.get("status") != "pass" or receipt.get("missing"):
    raise SystemExit(f"task-contract receipt should pass with no missing checks: {receipt!r}")

command_ids = {command.get("id") for command in receipt.get("commands") or []}
expected_commands = {
    "prepare-ios-notification-task",
    "verify-scoped-diff-pass",
    "verify-generic-permission-receipt-review",
    "verify-invalid-receipt-blocked",
    "verify-protected-diff-blocked",
}
if command_ids != expected_commands:
    raise SystemExit(f"unexpected task-contract command set: {command_ids!r}")
for command in receipt.get("commands") or []:
    if command.get("status") != "pass" or command.get("missing"):
        raise SystemExit(f"task-contract command should pass without missing checks: {command!r}")

if domain_pack_sdk.get("status") != "pass":
    raise SystemExit(f"Domain Pack SDK receipts should pass: {domain_pack_sdk!r}")
if domain_pack_sdk.get("receiptCount") != 1 or domain_pack_sdk.get("passedReceiptCount") != 1 or domain_pack_sdk.get("commandCount") != 3:
    raise SystemExit(f"expected one Domain Pack SDK receipt and three commands: {domain_pack_sdk!r}")

if configuration_baseline.get("status") != "pass":
    raise SystemExit(f"configuration baseline receipts should pass: {configuration_baseline!r}")
if configuration_baseline.get("receiptCount") != 1 or configuration_baseline.get("passedReceiptCount") != 1 or configuration_baseline.get("commandCount") != 6:
    raise SystemExit(f"expected one configuration baseline receipt and six commands: {configuration_baseline!r}")

if structured_evidence.get("status") != "pass":
    raise SystemExit(f"structured evidence receipts should pass: {structured_evidence!r}")
if structured_evidence.get("receiptCount") != 1 or structured_evidence.get("passedReceiptCount") != 1 or structured_evidence.get("commandCount") != 6:
    raise SystemExit(f"expected one structured evidence receipt and six commands: {structured_evidence!r}")

if concise_result_ux.get("status") != "pass":
    raise SystemExit(f"concise result UX receipts should pass: {concise_result_ux!r}")
if answer.get("identifier") != "shipguard codex-marketplace-readiness":
    raise SystemExit(f"passing concise result UX receipts should escalate to marketplace readiness: {answer!r}")
if "runtimeProofGatedTaskContract" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"proof-gated task contract should no longer be missing: {answer!r}")
if "runtimeDiffFirstVerification" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"diff-first verification should no longer be missing: {answer!r}")
if "runtimeIOSNotificationPermissionWorkflow" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"notification permission workflow should no longer be missing: {answer!r}")
if "runtimeExternalPilotVerdictBench" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"PilotBench should no longer be missing: {answer!r}")
if "runtimeDomainPackSDK" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Domain Pack SDK should no longer be missing: {answer!r}")
if "runtimeConfigurationBaselineSuppressions" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"configuration baseline/suppression should no longer be missing: {answer!r}")
if "runtimeStructuredEvidenceReceiptsV2" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"structured evidence receipts v2 should no longer be missing: {answer!r}")
if "runtimeCodexNativeTaskTraceAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Codex-native task trace adapter should no longer be missing: {answer!r}")
if "runtimeXcodeBuildMCPEvidenceAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"XcodeBuildMCP evidence adapter should no longer be missing: {answer!r}")
if "runtimeExpoMCPAndEASAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Expo MCP and EAS adapter should no longer be missing: {answer!r}")
if "runtimeUniversalAgentPackagingAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"universal agent packaging should no longer be missing: {answer!r}")
if "runtimeFullAuditOrchestrator" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"full-audit orchestrator should no longer be missing: {answer!r}")
if "runtimeUnifiedInspectExperience" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"unified inspect should no longer be missing: {answer!r}")
if "runtimeConciseVerdictResultUX" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"concise verdict UX should no longer be missing: {answer!r}")
if "runtimeCodexMarketplaceReadiness" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"marketplace readiness gap should be explicit: {answer!r}")
PY

echo "task contract receipt tests passed"
