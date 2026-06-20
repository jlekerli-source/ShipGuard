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

grep -q '"commandFamilyRuntimeOutputReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Command-Family Runtime Output Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q '"trustHardeningReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Trust-Hardening Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q '"domainPackSDKReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Domain Pack SDK Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q '"conciseVerdictResultUXReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Concise Verdict Result UX Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"

python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("commandFamilyRuntimeOutputReceipts") or {}
trust_receipts = data.get("trustHardeningReceipts") or {}
domain_pack_sdk = data.get("domainPackSDKReceipts") or {}
concise_result_ux = data.get("conciseVerdictResultUXReceipts") or {}
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}

if receipts.get("status") != "pass":
    raise SystemExit(f"command-family runtime-output receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 1 or receipts.get("passedReceiptCount") != 1:
    raise SystemExit(f"expected one passing receipt: {receipts!r}")
if receipts.get("commandCount") != 8:
    raise SystemExit(f"expected eight report-producing commands in the receipt: {receipts!r}")
receipt_ids = {item.get("id") for item in receipts.get("receipts") or []}
if receipt_ids != {"major-family-report-outputs"}:
    raise SystemExit(f"unexpected receipt ids: {receipt_ids!r}")

receipt = (receipts.get("receipts") or [{}])[0]
if receipt.get("status") != "pass" or receipt.get("missing"):
    raise SystemExit(f"receipt should pass with no missing checks: {receipt!r}")
command_ids = {command.get("id") for command in receipt.get("commands") or []}
expected_commands = {
    "brand-output",
    "ios-doctor-output",
    "ios-design-output",
    "web-audit-output",
    "web-plan-output",
    "docs-check-output",
    "action-verify-pr-output",
    "release-manifest-output",
}
if command_ids != expected_commands:
    raise SystemExit(f"unexpected command set: {command_ids!r}")
for command in receipt.get("commands") or []:
    if command.get("status") != "pass" or command.get("missing"):
        raise SystemExit(f"receipt command should pass without missing checks: {command!r}")

if trust_receipts.get("status") != "pass":
    raise SystemExit(f"trust-hardening receipts should also pass in the full gauntlet: {trust_receipts!r}")
if domain_pack_sdk.get("status") != "pass":
    raise SystemExit(f"Domain Pack SDK receipts should also pass in the full gauntlet: {domain_pack_sdk!r}")
if concise_result_ux.get("status") != "pass":
    raise SystemExit(f"concise result UX receipts should also pass in the full gauntlet: {concise_result_ux!r}")
if answer.get("identifier") != "shipguard v4-stable-release-publication":
    raise SystemExit(f"passing v4 product-release stabilization receipts should escalate to stable v4 publication: {answer!r}")
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
    raise SystemExit(f"configuration baseline/suppression receipts should no longer be missing: {answer!r}")
if "runtimeStructuredEvidenceReceiptsV2" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"structured evidence receipts v2 should no longer be missing: {answer!r}")
if "runtimeCodexNativeTaskTraceAdapter" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"Codex-native task/trace adapter should no longer be missing: {answer!r}")
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
if "runtimeExternalBenchmarkV2" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"external benchmark v2 should no longer be missing: {answer!r}")
if "runtimeV4SchemaFreeze" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"v4 schema freeze should no longer be missing: {answer!r}")
if "runtimeV4ReleaseCandidateReadiness" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"v4 release-candidate readiness should no longer be missing: {answer!r}")
if "runtimeV4StableReleasePublication" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"stable v4 publication gap should be explicit: {answer!r}")
if "runtimeCommandFamilyOutputReceipts" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"command-family output receipts should no longer be missing: {answer!r}")
if "runtimeTrustHardeningReceipts" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"trust-hardening receipts should no longer be missing: {answer!r}")
PY

echo "command-family runtime-output receipt tests passed"
