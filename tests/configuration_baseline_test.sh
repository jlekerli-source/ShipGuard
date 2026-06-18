#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture_repo="$tmp_dir/baseline-app"
mkdir -p "$fixture_repo/Sources/BaselineApp" "$fixture_repo/Tests/BaselineAppTests" "$fixture_repo/.github/workflows"
printf 'public struct BaselineApp {}\n' > "$fixture_repo/Sources/BaselineApp/App.swift"
printf 'import XCTest\nfinal class BaselineAppTests: XCTestCase {}\n' > "$fixture_repo/Tests/BaselineAppTests/AppTests.swift"
printf 'name: release\n' > "$fixture_repo/.github/workflows/release.yml"
printf 'name: deploy\n' > "$fixture_repo/.github/workflows/deploy.yml"

fingerprint_release="$(
  PYTHONPATH="$repo_root/scripts" python3 - <<'PY'
from shipguard_baseline import finding_fingerprint
print(finding_fingerprint("task-contract.protected-boundary", ".github/workflows/release.yml"))
PY
)"

write_baseline() {
  local expires_at="$1"
  local owner="${2:-release-owner}"
  cat > "$fixture_repo/.shipguard.yml" <<'YAML'
baseline:
  path: .shipguard-baseline.json
suppressions:
  requireOwner: true
  requireReason: true
  requireExpiresAt: true
  requireProofBoundary: true
YAML
  cat > "$fixture_repo/.shipguard-baseline.json" <<JSON
{
  "schemaVersion": "1.0",
  "suppressions": [
    {
      "id": "accepted-release-workflow-touch",
      "ruleId": "task-contract.protected-boundary",
      "fingerprint": "$fingerprint_release",
      "owner": "$owner",
      "reason": "Synthetic fixture accepts this exact release workflow touch.",
      "expiresAt": "$expires_at",
      "proofBoundary": "Only .github/workflows/release.yml is accepted; other workflow files remain regressions."
    }
  ]
}
JSON
}

prepare_task() {
  local out="$1"
  ./bin/shipguard prepare \
    "Exercise configuration baseline suppressions" \
    --path "$fixture_repo" \
    --out "$out" \
    --profile ios \
    --allowed "Sources/**" \
    --allowed "Tests/**" \
    --allowed ".github/workflows/**" \
    --forbidden ".github/workflows/**" \
    --validation "swift test" >/dev/null
}

mkdir -p "$tmp_dir/logs"
printf 'swift test passed for baseline fixture\n' > "$tmp_dir/logs/swift-test.log"
swift_log_sha="$(shasum -a 256 "$tmp_dir/logs/swift-test.log" | awk '{print $1}')"
swift_log_bytes="$(wc -c < "$tmp_dir/logs/swift-test.log" | tr -d ' ')"
cat > "$tmp_dir/logs/swift-test-receipt.json" <<JSON
{
  "receiptId": "baseline-swift-test",
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
  "scope": ["BaselineAppTests"]
}
JSON

cat > "$tmp_dir/release-only.diff" <<'DIFF'
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -1 +1,2 @@
 name: release
+# accepted baseline fixture
DIFF

cat > "$tmp_dir/release-and-deploy.diff" <<'DIFF'
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -1 +1,2 @@
 name: release
+# accepted baseline fixture
diff --git a/.github/workflows/deploy.yml b/.github/workflows/deploy.yml
--- a/.github/workflows/deploy.yml
+++ b/.github/workflows/deploy.yml
@@ -1 +1,2 @@
 name: deploy
+# unsuppressed regression fixture
DIFF

write_baseline "2099-01-01"
prepare_task "$tmp_dir/prepare-active"

python3 - <<'PY' "$tmp_dir/prepare-active/shipguard-task.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
config = data["configurationPolicy"]
assert config["status"] == "configured"
assert config["baseline"]["present"] is True
assert config["baseline"]["suppressionCount"] == 1
assert config["policy"]["requireOwner"] is True
PY

./bin/shipguard verify \
  --task "$tmp_dir/prepare-active/shipguard-task.json" \
  --diff "$tmp_dir/release-only.diff" \
  --evidence "$tmp_dir/logs/swift-test-receipt.json" \
  --claim "Scoped release workflow touch is covered by accepted risk." \
  --out "$tmp_dir/verify-active" >/dev/null

grep -q 'Status: pass' "$tmp_dir/verify-active/shipguard-verdict.md"
grep -q 'Configuration Baseline' "$tmp_dir/verify-active/shipguard-verdict.md"
grep -q 'accepted-release-workflow-touch' "$tmp_dir/verify-active/shipguard-verdict.json"
python3 - <<'PY' "$tmp_dir/verify-active/shipguard-verdict.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
baseline = data["configurationBaseline"]
assert data["status"] == "pass"
assert data["scopeChecks"]["rawForbiddenTouched"] == [".github/workflows/release.yml"]
assert data["scopeChecks"]["forbiddenTouched"] == []
assert baseline["status"] == "pass"
assert baseline["acceptedFindingCount"] == 1
assert baseline["unsuppressedFindingCount"] == 0
accepted = baseline["acceptedFindings"][0]
assert accepted["ruleId"] == "task-contract.protected-boundary"
assert accepted["suppression"]["owner"] == "release-owner"
assert accepted["suppression"]["proofBoundary"].startswith("Only .github/workflows/release.yml")
assert data["diffFirstAnalysis"]["configurationBaseline"]["acceptedFindingCount"] == 1
PY

write_baseline "2000-01-01"
prepare_task "$tmp_dir/prepare-expired"

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare-expired/shipguard-task.json" \
  --diff "$tmp_dir/release-only.diff" \
  --evidence "$tmp_dir/logs/swift-test-receipt.json" \
  --claim "Expired accepted risk should not pass." \
  --out "$tmp_dir/verify-expired" >/dev/null
expired_status=$?
set -e
if [[ "$expired_status" -ne 2 ]]; then
  echo "expected expired suppression to block, got $expired_status" >&2
  exit 1
fi
python3 - <<'PY' "$tmp_dir/verify-expired/shipguard-verdict.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
baseline = data["configurationBaseline"]
assert data["status"] == "blocked"
assert data["scopeChecks"]["forbiddenTouched"] == [".github/workflows/release.yml"]
assert baseline["status"] == "blocked"
assert baseline["acceptedFindingCount"] == 0
assert baseline["unsuppressedFindings"][0]["baselineStatus"] == "expired"
assert baseline["expiredSuppressions"][0]["id"] == "accepted-release-workflow-touch"
PY

write_baseline "2099-01-01"
prepare_task "$tmp_dir/prepare-regression"

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare-regression/shipguard-task.json" \
  --diff "$tmp_dir/release-and-deploy.diff" \
  --evidence "$tmp_dir/logs/swift-test-receipt.json" \
  --claim "Only one workflow change is accepted." \
  --out "$tmp_dir/verify-regression" >/dev/null
regression_status=$?
set -e
if [[ "$regression_status" -ne 2 ]]; then
  echo "expected unsuppressed new workflow touch to block, got $regression_status" >&2
  exit 1
fi
python3 - <<'PY' "$tmp_dir/verify-regression/shipguard-verdict.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
baseline = data["configurationBaseline"]
assert data["status"] == "blocked"
assert data["scopeChecks"]["rawForbiddenTouched"] == [".github/workflows/deploy.yml", ".github/workflows/release.yml"]
assert data["scopeChecks"]["forbiddenTouched"] == [".github/workflows/deploy.yml"]
assert baseline["acceptedFindingCount"] == 1
assert baseline["unsuppressedFindingCount"] == 1
assert baseline["unsuppressedFindings"][0]["subject"] == ".github/workflows/deploy.yml"
assert baseline["unsuppressedFindings"][0]["baselineStatus"] == "new"
assert baseline["regressionBehavior"]["newFindingsBlock"] is True
PY

echo "configuration baseline tests passed"
