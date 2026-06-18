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

grep -q '"trustHardeningReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q 'Trust-Hardening Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'external pilot verdict bench' "$tmp_dir/gauntlet/tool-value-gauntlet.md"

python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("trustHardeningReceipts") or {}
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}

if receipts.get("status") != "pass":
    raise SystemExit(f"trust-hardening receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 1 or receipts.get("passedReceiptCount") != 1:
    raise SystemExit(f"expected one passing trust receipt: {receipts!r}")
if receipts.get("commandCount") != 4:
    raise SystemExit(f"expected four trust-hardening commands: {receipts!r}")

receipt = (receipts.get("receipts") or [{}])[0]
if receipt.get("id") != "action-devspace-archive-release-provenance":
    raise SystemExit(f"unexpected trust receipt id: {receipt!r}")
if receipt.get("status") != "pass" or receipt.get("missing"):
    raise SystemExit(f"trust receipt should pass with no missing checks: {receipt!r}")

trust_checks = receipt.get("trustChecks") or {}
action_check = trust_checks.get("actionRunInputInterpolation") or {}
if action_check.get("status") != "pass" or action_check.get("violationCount") != 0:
    raise SystemExit(f"action input interpolation should have zero shell-block violations: {action_check!r}")
if action_check.get("checkedPathCount") != 12:
    raise SystemExit(f"expected all composite action shell blocks to be scanned: {action_check!r}")

archive_check = trust_checks.get("unsafeArchiveExtraction") or {}
if archive_check.get("status") != "pass":
    raise SystemExit(f"unsafe archive extraction should be rejected: {archive_check!r}")

command_ids = {command.get("id") for command in receipt.get("commands") or []}
expected_commands = {
    "devspace-token-in-url-blocked",
    "release-proof-bad-host-blocked",
    "release-proof-tag-mismatch-blocked",
    "release-manifest-provenance-output",
}
if command_ids != expected_commands:
    raise SystemExit(f"unexpected trust command set: {command_ids!r}")
for command in receipt.get("commands") or []:
    if command.get("status") != "pass" or command.get("missing"):
        raise SystemExit(f"trust command should pass without missing checks: {command!r}")

if answer.get("identifier") != "shipguard external-pilot-verdict-bench":
    raise SystemExit(f"passing trust, task-contract, and notification workflow receipts should escalate to external pilot verdict bench: {answer!r}")
if "runtimeTrustHardeningReceipts" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"trust-hardening should no longer be missing: {answer!r}")
if "runtimeProofGatedTaskContract" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"proof-gated task contract should no longer be missing: {answer!r}")
if "runtimeDiffFirstVerification" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"diff-first verification should no longer be missing: {answer!r}")
if "runtimeIOSNotificationPermissionWorkflow" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"notification permission workflow should no longer be missing: {answer!r}")
if "runtimeExternalPilotVerdictBench" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"external pilot verdict bench gap should be explicit: {answer!r}")
PY

echo "trust hardening receipt tests passed"
