#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard prepare \
  "Exercise synthetic domain-pack-sdk fixture" \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/prepare" \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/prepare/shipguard-task.json"
test -f "$tmp_dir/prepare/shipguard-task.md"
grep -q 'Domain Pack SDK' "$tmp_dir/prepare/shipguard-task.md"
grep -q 'Domain Pack Workflow' "$tmp_dir/prepare/shipguard-task.md"

python3 - <<'PY' "$tmp_dir/prepare/shipguard-task.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
sdk = data["domainPackSDK"]
registered = {item["id"]: item for item in sdk["registeredPacks"]}
assert sdk["sdkVersion"] == "1"
assert sdk["activePack"] == "synthetic-domain-pack-sdk-fixture"
assert registered["ios-notification-permission-workflow"]["resultField"] == "notificationPermissionWorkflow"
assert registered["synthetic-domain-pack-sdk-fixture"]["resultField"] == "syntheticDomainPackWorkflow"
assert data["domainRiskPack"]["id"] == "synthetic-domain-pack-sdk-fixture"
assert data["domainRiskPack"]["validationReceiptRequirements"][0]["id"] == "synthetic-domain-pack-validation"
assert data["nextAction"]["resolves"] == ["synthetic-domain-pack-validation"]
assert data["scopeBoundary"]["shipguardOnly"] is True
PY

mkdir -p "$tmp_dir/diffs" "$tmp_dir/logs"
cat > "$tmp_dir/diffs/good.diff" <<'DIFF'
diff --git a/Sources/DemoShipGuardApp/DemoPermissions.swift b/Sources/DemoShipGuardApp/DemoPermissions.swift
--- a/Sources/DemoShipGuardApp/DemoPermissions.swift
+++ b/Sources/DemoShipGuardApp/DemoPermissions.swift
@@ -1,3 +1,4 @@
+// synthetic sdk proof fixture
DIFF

printf 'swift test passed for synthetic domain pack sdk fixture\n' > "$tmp_dir/logs/swift-test.log"
cat > "$tmp_dir/logs/generic-swift-test-receipt.json" <<JSON
{
  "receiptId": "synthetic-domain-pack-sdk-generic",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {"path": "swift-test.log"},
  "scope": ["generic-tests"]
}
JSON

cat > "$tmp_dir/logs/swift-test-receipt.json" <<JSON
{
  "receiptId": "synthetic-domain-pack-sdk",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {"path": "swift-test.log"},
  "scope": ["synthetic-domain-proof", "domain-pack-sdk"]
}
JSON

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/diffs/good.diff" \
  --evidence "$tmp_dir/logs/generic-swift-test-receipt.json" \
  --claim "Synthetic Domain Pack SDK fixture is wired." \
  --out "$tmp_dir/verify-review" >/dev/null

python3 - <<'PY' "$tmp_dir/verify-review/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "review"
assert data["notificationPermissionWorkflow"] is None
workflow = data["syntheticDomainPackWorkflow"]
assert workflow["status"] == "review"
assert workflow["reviewRequired"] is True
assert workflow["proofLanes"][0]["status"] == "missing"
assert data["nextAction"]["resolves"] == ["synthetic-domain-pack-validation"]
assert data["domainPackSDK"]["evaluatedPacks"] == ["synthetic-domain-pack-sdk-fixture"]
PY

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/diffs/good.diff" \
  --evidence "$tmp_dir/logs/swift-test-receipt.json" \
  --claim "Synthetic Domain Pack SDK fixture is wired." \
  --out "$tmp_dir/verify-pass" >/dev/null

grep -q 'Status: pass' "$tmp_dir/verify-pass/shipguard-verdict.md"
grep -q 'Domain Pack Workflow: synthetic-domain-pack-sdk-fixture' "$tmp_dir/verify-pass/shipguard-verdict.md"

python3 - <<'PY' "$tmp_dir/verify-pass/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "pass"
assert data["notificationPermissionWorkflow"] is None
workflow = data["syntheticDomainPackWorkflow"]
assert workflow["id"] == "synthetic-domain-pack-sdk-fixture"
assert workflow["status"] == "pass"
assert workflow["reviewRequired"] is False
assert workflow["proofLanes"][0]["status"] == "proven"
assert data["domainWorkflows"]["syntheticDomainPackWorkflow"]["status"] == "pass"
assert data["diffFirstAnalysis"]["domainWorkflows"]["syntheticDomainPackWorkflow"]["status"] == "pass"
assert data["domainPackSDK"]["activePack"] == "synthetic-domain-pack-sdk-fixture"
assert data["domainPackSDK"]["evaluatedPacks"] == ["synthetic-domain-pack-sdk-fixture"]
assert data["nextAction"]["priority"] == 7
PY

echo "domain pack SDK tests passed"
