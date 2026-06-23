#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard prepare --help >/dev/null
./bin/shipguard verify --help >/dev/null

./bin/shipguard prepare \
  "Add provisional notification onboarding flow" \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/prepare" \
  --profile ios \
  --forbidden ".github/workflows/**" \
  --validation "swift test" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/prepare/shipguard-task.json"
test -f "$tmp_dir/prepare/shipguard-task.md"
grep -q '# ShipGuard Task Contract' "$tmp_dir/prepare/shipguard-task.md"
grep -q 'ShipGuard Product-QA Boundary' "$tmp_dir/prepare/shipguard-task.md"
grep -q 'Quickstart Replay' "$tmp_dir/prepare/shipguard-task.md"
grep -q 'shipguard verify --task <task-dir>/shipguard-task.json' "$tmp_dir/prepare/shipguard-task.md"
local_path_pattern="/""Users/"
if grep -q "$local_path_pattern" "$tmp_dir/prepare/shipguard-task.md" "$tmp_dir/prepare/shipguard-task.json"; then
  echo "shareable task contract leaked a local path" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/prepare/shipguard-task.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["tool"] == "shipguard prepare"
assert data["surface"] == "ShipGuard Task Contract"
assert data["projectSnapshot"]["profile"] == "ios"
assert data["projectSnapshot"]["root"] == "<target-repo>"
assert data["projectSnapshot"]["scanScope"]["mode"] == "bounded"
assert isinstance(data["projectSnapshot"]["scanScope"]["skippedDirs"], list)
assert data["verdict"]["status"] == "prepared"
assert data["riskClassification"]["level"] in {"high", "critical"}
assert data["scopeBoundary"]["shipguardOnly"] is True
assert data["scopeBoundary"]["targetAppsReadOnly"] is True
assert data["authorizedFiles"]
assert ".github/workflows/**" in data["protectedBoundaries"]
assert data["validationContract"]["required"][0]["command"] == "swift test"
replay = data["quickstartReplay"]
assert replay["phase"] == "prepare"
assert "shipguard verify" in replay["firstUsefulVerdictCommand"]
assert "<validation-receipt.json>" in replay["proofInputs"]
assert {"goal", "riskClassification", "authorizedFiles", "protectedBoundaries", "validationContract", "agentClaims", "verdict", "nextAction"} <= set(replay["connects"])
pack = data["domainRiskPack"]
assert pack["id"] == "ios-notification-permission-workflow"
assert pack["status"] == "active"
assert pack["validationReceiptRequirements"][0]["id"] == "permission-state-validation"
assert "permission-state" in pack["validationReceiptRequirements"][0]["requiredReceiptScope"]
assert pack["scopeRecommendations"]["reviewOnly"]
assert pack["scopeRecommendations"]["forbiddenUnlessExplicit"]
assert data["nextAction"]["command"]
PY

external_repo="$tmp_dir/PrivateAppRepo"
mkdir -p "$external_repo/PrivateApp" "$external_repo/PrivateAppTests" "$external_repo/PrivateApp.xcodeproj/xcshareddata/xcschemes"
printf 'import SwiftUI\nstruct PrivateView {}\n' > "$external_repo/PrivateApp/PrivateView.swift"
printf 'import UserNotifications\nlet center = UNUserNotificationCenter.current()\n' > "$external_repo/PrivateApp/PrivateAppPermissionView.swift"
printf 'import XCTest\nfinal class PrivateAppTests: XCTestCase {}\n' > "$external_repo/PrivateAppTests/PrivateAppTests.swift"
printf '<?xml version="1.0" encoding="UTF-8"?><Scheme LastUpgradeVersion="1500" version="1.7"></Scheme>\n' > "$external_repo/PrivateApp.xcodeproj/xcshareddata/xcschemes/PrivateApp.xcscheme"

./bin/shipguard prepare \
  "Add provisional notification onboarding flow" \
  --path "$external_repo" \
  --out "$tmp_dir/private-prepare-shareable" \
  --profile ios \
  --shipguard-eval \
  --shareable >/dev/null

if grep -R -q 'PrivateApp' "$tmp_dir/private-prepare-shareable"; then
  echo "shareable external task contract leaked target names" >&2
  exit 1
fi
python3 - <<'PY' "$tmp_dir/private-prepare-shareable/shipguard-task.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["authorizedFiles"] == ["<ios-source-target>/**", "<ios-test-target>/**"]
assert data["validationContract"]["required"][0]["command"] == "xcodebuild test -scheme <ios-scheme>"
assert data["validationContract"]["required"][0]["requirementId"] == "ios-scheme-tests"
assert data["shareableRedactions"]["targetNames"] is True
PY

mkdir -p "$tmp_dir/logs"

cat > "$tmp_dir/good.diff" <<'DIFF'
diff --git a/Sources/DemoShipGuardApp/DemoPermissions.swift b/Sources/DemoShipGuardApp/DemoPermissions.swift
--- a/Sources/DemoShipGuardApp/DemoPermissions.swift
+++ b/Sources/DemoShipGuardApp/DemoPermissions.swift
@@ -1,3 +1,4 @@
+// scoped proof fixture
DIFF
printf 'swift test passed for DemoPermissionsTests\n' > "$tmp_dir/logs/swift-test.log"
swift_log_sha="$(shasum -a 256 "$tmp_dir/logs/swift-test.log" | awk '{print $1}')"
swift_log_bytes="$(wc -c < "$tmp_dir/logs/swift-test.log" | tr -d ' ')"
cat > "$tmp_dir/logs/swift-test-receipt.json" <<JSON
{
  "receiptId": "validation-unit-tests",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "environment": "simulator",
  "proofType": "ios-permission-simulator-reset",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$swift_log_sha",
    "bytes": $swift_log_bytes
  },
  "scope": ["DemoPermissionsTests", "permission-state", "denied-state", "not-determined-state", "simulator-permission-reset"]
}
JSON

cat > "$tmp_dir/logs/generic-swift-test-receipt.json" <<JSON
{
  "receiptId": "validation-unit-tests-generic",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$swift_log_sha",
    "bytes": $swift_log_bytes
  },
  "scope": ["DemoPermissionsTests"]
}
JSON

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/swift-test.log" \
  --claim "Implemented scoped notification onboarding source update." \
  --out "$tmp_dir/verify-plain-log" >/dev/null

grep -q 'Status: review' "$tmp_dir/verify-plain-log/shipguard-verdict.md"
python3 - <<'PY' "$tmp_dir/verify-plain-log/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "review"
assert data["validationCoverage"]["status"] == "missing"
assert data["evidence"][0]["kind"] == "artifact-only"
assert data["evidence"][0]["usableForValidation"] is False
PY

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/generic-swift-test-receipt.json" \
  --claim "Implemented scoped notification onboarding source update." \
  --out "$tmp_dir/verify-generic-permission-receipt" >/dev/null

grep -q 'Status: review' "$tmp_dir/verify-generic-permission-receipt/shipguard-verdict.md"
grep -q 'permission-state-validation: missing' "$tmp_dir/verify-generic-permission-receipt/shipguard-verdict.md"
python3 - <<'PY' "$tmp_dir/verify-generic-permission-receipt/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "review"
assert data["validationCoverage"]["status"] == "covered"
workflow = data["notificationPermissionWorkflow"]
assert workflow["reviewRequired"] is True
lane_status = {item["id"]: item["status"] for item in workflow["proofLanes"]}
assert lane_status["permission-state-validation"] == "missing"
assert data["nextAction"]["priority"] == 4
assert data["nextAction"]["resolves"] == ["permission-state-validation"]
PY

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/swift-test-receipt.json" \
  --claim "Implemented scoped notification onboarding source update." \
  --reviewer-disposition accepted \
  --reviewer-note "Maintainer accepted this proof packet." \
  --out "$tmp_dir/verify-pass" >/dev/null

test -f "$tmp_dir/verify-pass/shipguard-verdict.json"
test -f "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Status: pass' "$tmp_dir/verify-pass/shipguard-verdict.md"

python3 - <<'PY' "$tmp_dir/verify-pass/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["tool"] == "shipguard verify"
assert data["status"] == "pass"
proof = data["proofReport"]
assert proof["status"] == "pass"
assert proof["validation"]["label"] == "1/1 covered"
assert proof["claims"]["label"] == "1/1 accepted"
assert proof["mergeAllowed"] is True
replay = data["quickstartReplay"]
assert replay["phase"] == "verify"
assert replay["status"] == "pass"
assert "shipguard verify" in replay["replayCommand"]
assert "ShipGuard Proof Report: pass" in replay["fastVerdict"]
assert "shipguard-verdict.json" in replay["reviewPacket"]
assert "shipguard-verdict.md" in replay["reviewPacket"]
assert data["changedFiles"] == ["Sources/DemoShipGuardApp/DemoPermissions.swift"]
assert data["scopeChecks"]["outOfScope"] == []
assert data["scopeChecks"]["forbiddenTouched"] == []
assert data["evidence"][0]["present"] is True
assert data["evidence"][0]["sha256"]
assert data["evidence"][0]["kind"] == "structured-validation"
assert data["evidence"][0]["artifact"]["digestMatches"] is True
assert data["claimChecks"]["rejectedClaims"] == []
analysis = data["diffFirstAnalysis"]
assert analysis["mergeVerdict"]["allowedToMerge"] is True
assert analysis["changedFileCount"] == 1
assert analysis["changedFiles"][0]["behaviorCategories"] == ["permission", "privacy"]
assert analysis["changedFiles"][0]["behaviorCategoryEvidence"]
assert analysis["validationCoverage"]["status"] == "covered"
assert analysis["validationCoverage"]["coveredCommands"][0]["command"] == "swift test"
assert analysis["claimDecisions"][0]["status"] == "accepted"
assert analysis["evidenceCoverage"][0]["status"] == "proven"
workflow = data["notificationPermissionWorkflow"]
assert workflow["id"] == "ios-notification-permission-workflow"
assert workflow["status"] == "local-pass-manual-device-proof-required"
assert workflow["reviewRequired"] is False
lane_status = {item["id"]: item["status"] for item in workflow["proofLanes"]}
assert lane_status["permission-state-validation"] == "proven"
assert lane_status["denied-state-recovery"] == "proven"
assert lane_status["simulator-permission-reset"] == "proven"
assert lane_status["physical-device-prompt"] == "manual-required"
assert analysis["notificationPermissionWorkflow"]["status"] == workflow["status"]
learning = data["diffLearningHandoff"]
assert learning["status"] == "pass"
assert learning["primaryLesson"].startswith("This exact diff matched")
assert learning["changedFileSignals"][0]["path"] == "Sources/DemoShipGuardApp/DemoPermissions.swift"
assert learning["learningSignals"] == ["scope-evidence-claim-match"]
recurrence = learning["recurringSignalTuning"]
summary = learning["reviewerDispositionSummary"]
disposition = learning["reviewerDispositionReceipt"]
assert summary["status"] == "present"
assert summary["disposition"] == "accepted"
assert summary["trackedSignalCount"] == 0
assert summary["nextStep"] == disposition["recommendedFollowUp"]
assert "Do not tune" in summary["guard"]
assert disposition["status"] == "present"
assert disposition["disposition"] == "accepted"
assert disposition["note"] == "Maintainer accepted this proof packet."
assert disposition["repairHint"] is None
assert disposition["trackedSignals"] == []
assert disposition["recommendedFollowUp"].startswith("Keep this verdict as positive")
assert "not adoption evidence" in disposition["proofBoundary"]
assert recurrence["shouldTrackLocally"] is False
assert recurrence["signalKeys"] == []
assert recurrence["reviewerDispositionReceipt"] == disposition
assert recurrence["doNotTuneFromSingleVerdict"] is True
assert "two or more reviewed verify verdicts" in recurrence["recurrenceRule"]
assert "does not prove a false positive" in recurrence["proofBoundary"]
assert learning["nextTuningAction"]["expectedArtifact"] == "review-ready proof packet"
assert "not persistent project memory" in learning["proofBoundary"]
assert analysis["learningHandoff"] == learning
assert data["nextAction"]["expectedArtifact"] == "review-ready proof packet"
assert data["nextAction"]["priority"] == 7
PY
grep -q '## Proof Report' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Status: `pass`' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Validation: `1/1 covered`' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Merge allowed: True' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Behavior Categories' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Diff Learning Handoff' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'scope-evidence-claim-match' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Reviewer disposition summary: `accepted` / `present` / 0 tracked signal(s)' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Reviewer disposition: `accepted`' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Reviewer follow-up: Keep this verdict as positive local outcome evidence' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Reviewer note: Maintainer accepted this proof packet.' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Track recurring signals: `False`' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Recurring signal keys: `none`' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Validation Coverage' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Claim Decisions' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Quickstart Replay' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'iOS Notification Permission Workflow' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'simulator-permission-reset: proven' "$tmp_dir/verify-pass/shipguard-verdict.md"

cat > "$tmp_dir/protected.diff" <<'DIFF'
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -1,3 +1,4 @@
+name: unsafe-release-change
DIFF

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/protected.diff" \
  --claim "Notification flow is fully verified." \
  --out "$tmp_dir/verify-blocked" >/dev/null
blocked_status=$?
set -e

if [[ "$blocked_status" -ne 2 ]]; then
  echo "expected protected diff verification to exit 2, got $blocked_status" >&2
  exit 1
fi

test -f "$tmp_dir/verify-blocked/shipguard-verdict.json"
grep -q 'Status: blocked' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'Protected boundary touched' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'fully verified' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'Unsupported Claim Replay' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'Revise the completion claim or attach the missing structured evidence receipts' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'not product proof' "$tmp_dir/verify-blocked/shipguard-verdict.md"
grep -q 'not a merge' "$tmp_dir/verify-blocked/shipguard-verdict.md"

python3 - <<'PY' "$tmp_dir/verify-blocked/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
assert ".github/workflows/release.yml" in data["scopeChecks"]["outOfScope"]
assert ".github/workflows/release.yml" in data["scopeChecks"]["forbiddenTouched"]
assert "fully verified" in data["claimChecks"]["rejectedClaims"]
analysis = data["diffFirstAnalysis"]
assert analysis["mergeVerdict"]["allowedToMerge"] is False
assert analysis["protectedBoundaryCrossings"]["forbiddenTouched"] == [".github/workflows/release.yml"]
assert analysis["changedFiles"][0]["behaviorCategories"] == ["release-workflow"]
assert analysis["validationCoverage"]["status"] == "missing"
assert analysis["claimDecisions"][0]["status"] == "rejected"
learning = data["diffLearningHandoff"]
assert learning["status"] == "blocked"
assert learning["primaryLesson"].startswith("This exact diff exposed")
assert "protected-boundary-crossing" in learning["learningSignals"]
assert "out-of-scope-diff" in learning["learningSignals"]
assert "missing-validation-coverage" in learning["learningSignals"]
assert "unsupported-completion-claim" in learning["learningSignals"]
assert learning["changedFileSignals"][0]["forbidden"] is True
recurrence = learning["recurringSignalTuning"]
summary = learning["reviewerDispositionSummary"]
disposition = learning["reviewerDispositionReceipt"]
assert summary["status"] == "missing"
assert summary["disposition"] == "not-recorded"
assert summary["trackedSignalCount"] == 4
assert summary["nextStep"] == disposition["recommendedFollowUp"]
assert disposition["status"] == "missing"
assert disposition["disposition"] == "not-recorded"
assert disposition["recommendedFollowUp"].startswith("Ask the reviewer")
repair = disposition["repairHint"]
assert repair["command"].startswith("shipguard verify --task <task.json>")
assert "--reviewer-disposition accepted" in repair["command"]
assert repair["acceptedValues"] == ["accepted", "dismissed", "follow-up", "unknown"]
assert "local reviewer outcome" in repair["boundary"]
assert disposition["trackedSignals"] == [
    "protected-boundary-crossing",
    "out-of-scope-diff",
    "missing-validation-coverage",
    "unsupported-completion-claim",
]
assert recurrence["shouldTrackLocally"] is True
assert recurrence["signalKeys"] == [
    "protected-boundary-crossing",
    "out-of-scope-diff",
    "missing-validation-coverage",
    "unsupported-completion-claim",
]
assert "reviewerDisposition" in recurrence["localMetricCandidates"]
assert recurrence["reviewerDispositionReceipt"] == disposition
assert recurrence["doNotTuneFromSingleVerdict"] is True
assert "not persistent project memory" in learning["proofBoundary"]
assert analysis["learningHandoff"] == learning
assert data["nextAction"]["owner"] == "developer"
assert "Update the task contract scope" in data["nextAction"]["command"]
assert data["nextAction"]["priority"] == 1
replay = data["unsupportedClaimReplay"]
assert replay["status"] == "blocked"
assert replay["unsupportedPhrases"] == ["fully verified"]
assert replay["unsupportedClaimCount"] == 1
assert replay["unsupportedClaims"][0]["status"] == "rejected"
assert replay["rejectedClaimCount"] == 1
assert replay["rejectedClaims"][0]["claim"] == "Notification flow is fully verified."
assert replay["manualProofClaimCount"] == 0
assert replay["manualProofClaims"] == []
assert "shipguard verify" in replay["replayCommand"]
assert "--claim" in replay["replayCommand"]
assert replay["nextAction"]["resolves"] == ["unsupported-completion-claim"]
assert "Revise the completion claim" in replay["nextAction"]["command"]
assert replay["nextAction"]["priority"] == 6
assert any("not product proof" in item for item in replay["nonClaims"])
assert any("not a merge" in item for item in replay["nonClaims"])
assert "does not prove" in replay["proofBoundary"]
assert "structured proof" in replay["proofBoundary"]
PY
grep -q 'Reviewer repair hint: `shipguard verify --task <task.json> --diff <change.diff> --evidence <validation-receipt.json> --reviewer-disposition accepted --out <verdict-dir>`' "$tmp_dir/verify-blocked/shipguard-verdict.md"

printf 'all tests passed, but command failed\n' > "$tmp_dir/logs/failing-swift-test.log"
failing_log_sha="$(shasum -a 256 "$tmp_dir/logs/failing-swift-test.log" | awk '{print $1}')"
failing_log_bytes="$(wc -c < "$tmp_dir/logs/failing-swift-test.log" | tr -d ' ')"
cat > "$tmp_dir/logs/failing-swift-test-receipt.json" <<JSON
{
  "receiptId": "validation-unit-tests-failed",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 1,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "failing-swift-test.log",
    "sha256": "$failing_log_sha",
    "bytes": $failing_log_bytes
  },
  "scope": ["DemoPermissionsTests"]
}
JSON

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/failing-swift-test-receipt.json" \
  --claim "Implemented scoped notification onboarding source update." \
  --out "$tmp_dir/verify-invalid-receipt" >/dev/null
invalid_status=$?
set -e

if [[ "$invalid_status" -ne 2 ]]; then
  echo "expected invalid receipt verification to exit 2, got $invalid_status" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/verify-invalid-receipt/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
assert data["validationCoverage"]["status"] == "invalid"
assert data["validationCoverage"]["invalidReceipts"]
assert data["nextAction"]["priority"] == 3
assert data["nextAction"]["resolves"] == ["swift-test"]
PY

echo "task contract tests passed"
