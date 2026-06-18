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
grep -q 'Task-Contract Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'external pilot verdict bench' "$tmp_dir/gauntlet/tool-value-gauntlet.md"

python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("taskContractReceipts") or {}
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

if answer.get("identifier") != "shipguard external-pilot-verdict-bench":
    raise SystemExit(f"passing notification workflow receipts should escalate to external pilot verdict bench: {answer!r}")
if "runtimeProofGatedTaskContract" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"proof-gated task contract should no longer be missing: {answer!r}")
if "runtimeDiffFirstVerification" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"diff-first verification should no longer be missing: {answer!r}")
if "runtimeIOSNotificationPermissionWorkflow" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"notification permission workflow should no longer be missing: {answer!r}")
if "runtimeExternalPilotVerdictBench" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"external pilot verdict bench gap should be explicit: {answer!r}")
PY

echo "task contract receipt tests passed"
