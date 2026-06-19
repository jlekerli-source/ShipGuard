#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

mkdir -p "$tmp_dir/fixture/Sources/AgentTraceFixture" "$tmp_dir/diffs" "$tmp_dir/logs" "$tmp_dir/xcodebuildmcp" "$tmp_dir/expo-eas" "$tmp_dir/non-codex"
printf 'public struct AgentTraceFixture {}\n' > "$tmp_dir/fixture/Sources/AgentTraceFixture/App.swift"
printf 'diff --git a/Sources/AgentTraceFixture/App.swift b/Sources/AgentTraceFixture/App.swift\n--- a/Sources/AgentTraceFixture/App.swift\n+++ b/Sources/AgentTraceFixture/App.swift\n@@ -1 +1,2 @@\n public struct AgentTraceFixture {}\n+// trace adapter fixture\n' > "$tmp_dir/diffs/good.diff"
printf 'swift test passed for agent trace fixture\n' > "$tmp_dir/logs/swift-test.log"
cat > "$tmp_dir/logs/v2-validation-receipt.json" <<'JSON'
{
  "schemaVersion": "2.0",
  "receiptId": "v2-agent-trace-swift-test",
  "receiptType": "validation",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "environment": "local-cli",
  "artifact": {"path": "swift-test.log"},
  "scope": ["agent-trace-fixture"]
}
JSON

./bin/shipguard prepare \
  "Exercise Codex-native agent trace adapter" \
  --path "$tmp_dir/fixture" \
  --out "$tmp_dir/prepare" \
  --profile ios \
  --allowed "Sources/**" \
  --validation "swift test" >/dev/null

cat > "$tmp_dir/trace.json" <<JSON
{
  "adapter": "codex",
  "threadId": "synthetic-codex-thread",
  "taskId": "TASK-TRACE-001",
  "agentBudget": {"workersRequested": 3, "maxWorkers": 5, "recursiveSpawning": false},
  "events": [
    {"type": "prompt", "role": "user", "text": "Implement v3.120 agent adapter kernel."},
    {"type": "tool_call", "tool": "functions.exec_command", "command": "./bin/shipguard prepare ..."},
    {"type": "receipt", "receiptId": "v2-agent-trace-swift-test", "path": "$tmp_dir/logs/v2-validation-receipt.json"},
    {"type": "verdict", "status": "pass", "path": "$tmp_dir/verify/shipguard-verdict.json"},
    {"type": "next_action", "text": "Generate NEXT_GOAL for v3.121."}
  ]
}
JSON
cat > "$tmp_dir/non-codex/claude-trace.json" <<JSON
{
  "adapter": "claude",
  "threadId": "synthetic-claude-thread",
  "taskId": "TASK-TRACE-CLAUDE",
  "agentBudget": {"workersRequested": 2, "maxWorkers": 5, "recursiveSpawning": false},
  "events": [
    {"type": "message", "role": "user", "text": "Review this ShipGuard report."},
    {"type": "tool_use", "tool": "claude-code", "command": "python -m pytest"},
    {"type": "receipt", "receiptId": "v2-agent-trace-swift-test", "path": "$tmp_dir/logs/v2-validation-receipt.json"},
    {"type": "verdict", "status": "pass"},
    {"type": "handoff", "nextAction": "Run ShipGuard package proof."}
  ]
}
JSON
cat > "$tmp_dir/non-codex/gemini-trace.json" <<JSON
{
  "adapter": "gemini",
  "threadId": "synthetic-gemini-thread",
  "taskId": "TASK-TRACE-GEMINI",
  "agentBudget": {"workersRequested": 2, "maxWorkers": 5, "recursiveSpawning": false},
  "events": [
    {"type": "prompt", "role": "user", "text": "Gemini CLI should emit ShipGuard receipts."},
    {"type": "function_call", "tool": "gemini-cli", "command": "shipguard agent trace"},
    {"type": "receipt", "receiptId": "v2-agent-trace-swift-test", "path": "$tmp_dir/logs/v2-validation-receipt.json"},
    {"type": "verdict", "status": "pass"},
    {"type": "next_action", "text": "Continue to NEXT_GOAL."}
  ]
}
JSON
cat > "$tmp_dir/non-codex/cursor-trace.json" <<JSON
{
  "adapter": "cursor",
  "threadId": "synthetic-cursor-thread",
  "taskId": "TASK-TRACE-CURSOR",
  "agentBudget": {"workersRequested": 2, "maxWorkers": 5, "recursiveSpawning": false},
  "events": [
    {"type": "prompt", "role": "user", "text": "Cursor Composer should preserve proof."},
    {"type": "tool_call", "tool": "cursor-agent", "command": "apply_patch"},
    {"type": "receipt", "receiptId": "v2-agent-trace-swift-test", "path": "$tmp_dir/logs/v2-validation-receipt.json"},
    {"type": "verdict", "status": "pass"},
    {"type": "next_action", "text": "Run report-quality."}
  ]
}
JSON
cat > "$tmp_dir/non-codex/mcp-trace.json" <<JSON
{
  "adapter": "mcp",
  "threadId": "synthetic-mcp-thread",
  "taskId": "TASK-TRACE-MCP",
  "agentBudget": {"workersRequested": 2, "maxWorkers": 5, "recursiveSpawning": false},
  "events": [
    {"type": "prompt", "role": "user", "text": "Generic MCP should call ShipGuard."},
    {"type": "tools/call", "tool": "mcp__generic__run", "command": "shipguard verify"},
    {"type": "receipt", "receiptId": "v2-agent-trace-swift-test", "path": "$tmp_dir/logs/v2-validation-receipt.json"},
    {"type": "verdict", "status": "pass"},
    {"type": "next_action", "text": "Publish release proof."}
  ]
}
JSON
cat > "$tmp_dir/xcodebuildmcp/session-build.log" <<'EOF'
session_show_defaults
session_set_defaults with workspace=DemoShipGuardApp.xcworkspace, scheme=DemoShipGuardApp, simulator=iPhone 15
build_run_sim
** BUILD SUCCEEDED **
Launching DemoShipGuardApp
EOF
cat > "$tmp_dir/xcodebuildmcp/describe-ui.json" <<'EOF'
{"tool":"snapshot_ui","elements":[{"elementRef":"button.start","label":"Start"}]}
EOF
printf 'png proof\n' > "$tmp_dir/xcodebuildmcp/screenshot.png"
cat > "$tmp_dir/xcodebuildmcp/runtime.log" <<'EOF'
start_sim_log_cap
runtime log contains focused os_log output
stop_sim_log_cap
EOF
cat > "$tmp_dir/xcodebuildmcp/profile.trace" <<'EOF'
xctrace record --template 'Animation Hitches'
Time Profiler and Animation Hitches summaries preserved.
EOF
cat > "$tmp_dir/expo-eas/app.json" <<'EOF'
{"expo":{"name":"ShipGuardExpoFixture","slug":"shipguard-expo-fixture","sdkVersion":"54.0.0","runtimeVersion":"1.0.0"}}
EOF
cat > "$tmp_dir/expo-eas/eas-build.log" <<'EOF'
expo mcp routed the task into EAS.
expo prebuild completed with config plugin sync.
eas build --platform ios --profile production
Build ID: 12345678-abcd
Build URL: https://expo.dev/accounts/example/projects/shipguard/builds/12345678
Artifact URL: https://expo.dev/artifacts/builds/shipguard.ipa
sha256: 0123456789abcdef
credentials redacted
EOF
cat > "$tmp_dir/expo-eas/eas-update.json" <<'EOF'
{"command":"eas update","channel":"production","branch":"main","runtimeVersion":"1.0.0","updateGroup":"synthetic-update-group","artifact":{"sha256":"0123456789abcdef"}}
EOF
cat > "$tmp_dir/expo-eas/runtime.log" <<'EOF'
simulator launch succeeded for Expo dev client native runtime log
EOF

./bin/shipguard agent trace \
  --trace "$tmp_dir/trace.json" \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/diffs/good.diff" \
  --evidence "$tmp_dir/logs/v2-validation-receipt.json" \
  --xcodebuildmcp-evidence "$tmp_dir/xcodebuildmcp" \
  --expo-eas-evidence "$tmp_dir/expo-eas" \
  --run-verify \
  --out "$tmp_dir/agent-trace" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/agent-trace/agent-trace.json"
test -f "$tmp_dir/agent-trace/agent-trace.md"
test -f "$tmp_dir/agent-trace/agent-trace-receipt.json"
python3 -m json.tool "$tmp_dir/agent-trace/agent-trace.json" >/dev/null
python3 -m json.tool "$tmp_dir/agent-trace/agent-trace-receipt.json" >/dev/null

python3 - <<'PY' "$tmp_dir/agent-trace/agent-trace.json" "$tmp_dir/agent-trace/agent-trace-receipt.json" "$tmp_dir"
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
receipt = json.load(open(sys.argv[2], encoding="utf-8"))
tmp_dir = sys.argv[3]
if report["status"] != "pass":
    raise SystemExit(report)
if report["adapter"]["type"] != "codex":
    raise SystemExit(report["adapter"])
summary = report["traceSummary"]
for key in ("promptCount", "toolCallCount", "receiptCount", "verdictCount", "nextActionCount"):
    if summary.get(key) != 1:
        raise SystemExit(f"unexpected {key}: {summary}")
if report["agentBudget"]["status"] != "pass" or report["agentBudget"]["workerCount"] != 3:
    raise SystemExit(report["agentBudget"])
summary = report["xcodeBuildMCPEvidence"]["summary"]
for key in ("sessionDefaultsProof", "buildRunProof", "uiSnapshotProof", "screenshotProof", "logProof", "profilerProof"):
    if summary.get(key) is not True:
        raise SystemExit(f"missing XcodeBuildMCP proof {key}: {summary}")
if report["traceSummary"]["xcodeBuildMCPEvidenceCount"] < 5:
    raise SystemExit(report["traceSummary"])
if not report["taskTrace"]["xcodeBuildMCPEvidenceTimeline"]:
    raise SystemExit(report["taskTrace"])
expo_summary = report["expoEASAssuranceEvidence"]["summary"]
for key in ("expoMCPProof", "expoProjectProof", "prebuildProof", "easBuildProof", "easUpdateProof", "nativeRuntimeProof", "artifactIntegrityProof", "credentialBoundaryProof"):
    if expo_summary.get(key) is not True:
        raise SystemExit(f"missing Expo/EAS proof {key}: {expo_summary}")
if report["traceSummary"]["expoEASAssuranceEvidenceCount"] < 8:
    raise SystemExit(report["traceSummary"])
if not report["taskTrace"]["expoEASAssuranceEvidenceTimeline"]:
    raise SystemExit(report["taskTrace"])
if report["verifyHandoff"]["status"] != "pass" or report["verifyHandoff"]["verdictStatus"] != "pass":
    raise SystemExit(report["verifyHandoff"])
if report["receiptHandoff"]["schema"]["v2Count"] != 1:
    raise SystemExit(report["receiptHandoff"]["schema"])
if report["scopeBoundary"]["shipguardOnly"] is not True or report["scopeBoundary"]["targetAppsReadOnly"] is not True:
    raise SystemExit(report["scopeBoundary"])
if receipt["receiptType"] != "runtime" or receipt["artifact"]["path"] != "agent-trace.json":
    raise SystemExit(receipt)
if receipt["requirementId"] != "expo-eas-assurance-adapter" or "xcodebuildmcp-evidence" not in receipt["scope"] or "expo-eas-evidence" not in receipt["scope"]:
    raise SystemExit(receipt)
serialized = json.dumps(report, sort_keys=True)
if tmp_dir in serialized:
    raise SystemExit("shareable report leaked temporary path")
PY

grep -q '# ShipGuard Agent Trace' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'Agent Budget' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'Verify Handoff' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'XcodeBuildMCP Evidence' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'Build/run proof' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'Expo/EAS Assurance Evidence' "$tmp_dir/agent-trace/agent-trace.md"
grep -q 'EAS build proof' "$tmp_dir/agent-trace/agent-trace.md"

./bin/shipguard agent trace \
  --trace "$tmp_dir/trace.json" \
  --out "$tmp_dir/agent-trace-overbudget" \
  --budget-workers 6 \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/agent-trace-overbudget/agent-trace.json"
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report["status"] != "blocked":
    raise SystemExit(report)
if report["agentBudget"]["status"] != "blocked":
    raise SystemExit(report["agentBudget"])
rule_ids = {finding["ruleId"] for finding in report["findings"]}
if "agent-budget-worker-count" not in rule_ids:
    raise SystemExit(rule_ids)
PY

./bin/shipguard codex trace \
  --trace "$tmp_dir/trace.json" \
  --expo-eas-evidence "$tmp_dir/expo-eas" \
  --out "$tmp_dir/codex-trace" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/codex-trace/agent-trace.json"
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report["tool"] != "shipguard codex trace":
    raise SystemExit(report["tool"])
if report["adapter"]["type"] != "codex":
    raise SystemExit(report["adapter"])
if report["expoEASAssuranceEvidence"]["status"] != "pass":
    raise SystemExit(report["expoEASAssuranceEvidence"])
PY

for adapter in claude gemini cursor mcp; do
  ./bin/shipguard agent trace \
    --trace "$tmp_dir/non-codex/$adapter-trace.json" \
    --adapter "$adapter" \
    --evidence "$tmp_dir/logs/v2-validation-receipt.json" \
    --out "$tmp_dir/non-codex/$adapter-out" \
    --shipguard-eval \
    --shareable >/dev/null

  python3 - <<'PY' "$tmp_dir/non-codex/$adapter-out/agent-trace.json" "$tmp_dir/non-codex/$adapter-out/agent-trace-receipt.json" "$tmp_dir" "$adapter"
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
receipt = json.load(open(sys.argv[2], encoding="utf-8"))
tmp_dir = sys.argv[3]
adapter = sys.argv[4]
if report["status"] != "pass":
    raise SystemExit(report)
if report["adapter"]["type"] != adapter or report["adapter"]["confidence"] != "override":
    raise SystemExit(report["adapter"])
packaging = report["adapterPackaging"]
if packaging["status"] != "pass" or packaging["currentAdapter"] != adapter:
    raise SystemExit(packaging)
for required in ("codex", "claude", "gemini", "cursor", "mcp", "generic"):
    if required not in packaging["supportedAdapters"]:
        raise SystemExit(packaging)
if "agent-neutral-packaging" not in receipt.get("scope", []):
    raise SystemExit(receipt)
if receipt.get("requirementId") != "universal-agent-packaging-adapter":
    raise SystemExit(receipt)
if "v3.124.0 Efficient Unleash The Beast Full-Audit Orchestrator" not in report["slashPlan"]:
    raise SystemExit(report["slashPlan"])
serialized = json.dumps(report, sort_keys=True)
if tmp_dir in serialized:
    raise SystemExit("shareable non-Codex report leaked temporary path")
PY

  grep -q 'Agent Packaging' "$tmp_dir/non-codex/$adapter-out/agent-trace.md"
  grep -q "$adapter" "$tmp_dir/non-codex/$adapter-out/agent-trace.md"
done

./bin/shipguard agent trace \
  --trace "$tmp_dir/non-codex/claude-trace.json" \
  --out "$tmp_dir/non-codex/claude-auto" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/non-codex/claude-auto/agent-trace.json"
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report["adapter"]["type"] != "claude" or report["adapter"]["confidence"] != "metadata":
    raise SystemExit(report["adapter"])
if report["adapterPackaging"]["currentAdapter"] != "claude":
    raise SystemExit(report["adapterPackaging"])
PY

echo "agent trace tests passed"
