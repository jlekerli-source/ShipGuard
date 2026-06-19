#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

mkdir -p "$tmp_dir/fixture/Sources/ReceiptFixtureApp" "$tmp_dir/fixture/Tests/ReceiptFixtureAppTests"
printf 'public struct ReceiptFixtureApp {}\n' > "$tmp_dir/fixture/Sources/ReceiptFixtureApp/App.swift"
printf 'import XCTest\nfinal class ReceiptFixtureAppTests: XCTestCase {}\n' > "$tmp_dir/fixture/Tests/ReceiptFixtureAppTests/AppTests.swift"

./bin/shipguard prepare \
  "Exercise structured evidence receipts" \
  --path "$tmp_dir/fixture" \
  --out "$tmp_dir/prepare" \
  --profile ios \
  --allowed "Sources/**" \
  --validation "swift test" >/dev/null

cat > "$tmp_dir/good.diff" <<'DIFF'
diff --git a/Sources/ReceiptFixtureApp/App.swift b/Sources/ReceiptFixtureApp/App.swift
--- a/Sources/ReceiptFixtureApp/App.swift
+++ b/Sources/ReceiptFixtureApp/App.swift
@@ -1,3 +1,4 @@
+// structured receipt fixture
DIFF

mkdir -p "$tmp_dir/logs"
printf 'swift test passed for structured receipt fixture\n' > "$tmp_dir/logs/swift-test.log"
log_sha="$(shasum -a 256 "$tmp_dir/logs/swift-test.log" | awk '{print $1}')"
log_bytes="$(wc -c < "$tmp_dir/logs/swift-test.log" | tr -d ' ')"

cat > "$tmp_dir/logs/v2-validation-receipt.json" <<JSON
{
  "schemaVersion": "2.0",
  "receiptId": "v2-swift-test",
  "receiptType": "validation",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "environment": "simulator",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$log_sha",
    "bytes": $log_bytes
  },
  "scope": ["DemoShipGuardAppTests"]
}
JSON

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/v2-validation-receipt.json" \
  --claim "Implemented scoped source update." \
  --out "$tmp_dir/verify-v2-pass" >/dev/null

python3 - <<'PY' "$tmp_dir/verify-v2-pass/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "pass"
assert data["validationCoverage"]["status"] == "covered"
schema = data["evidenceReceiptSchema"]
assert schema["schemaVersion"] == "2.0"
assert schema["v2Count"] == 1
assert schema["structuredValidationCount"] == 1
assert schema["invalidCount"] == 0
assert data["evidence"][0]["compatibility"]["status"] == "current"
assert data["diffFirstAnalysis"]["evidenceReceiptSchema"]["v2Count"] == 1
PY

cat > "$tmp_dir/logs/legacy-validation-receipt.json" <<JSON
{
  "receiptId": "legacy-swift-test",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$log_sha",
    "bytes": $log_bytes
  },
  "scope": ["DemoShipGuardAppTests"]
}
JSON

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/legacy-validation-receipt.json" \
  --claim "Implemented scoped source update." \
  --out "$tmp_dir/verify-legacy-pass" >/dev/null

python3 - <<'PY' "$tmp_dir/verify-legacy-pass/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "pass"
assert data["evidenceReceiptSchema"]["legacyCount"] == 1
assert data["evidence"][0]["compatibility"]["status"] == "legacy-compatible"
PY

cat > "$tmp_dir/logs/unsupported-schema-validation-receipt.json" <<JSON
{
  "schemaVersion": "9.0",
  "receiptId": "unsupported-schema-swift-test",
  "receiptType": "validation",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$log_sha",
    "bytes": $log_bytes
  },
  "scope": ["DemoShipGuardAppTests"]
}
JSON

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/unsupported-schema-validation-receipt.json" \
  --claim "Implemented scoped source update." \
  --out "$tmp_dir/verify-unsupported-schema-blocked" >/dev/null
unsupported_status=$?
set -e

if [[ "$unsupported_status" -ne 2 ]]; then
  echo "expected unsupported schema verification to exit 2, got $unsupported_status" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/verify-unsupported-schema-blocked/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
assert data["validationCoverage"]["status"] == "invalid"
assert data["evidenceReceiptSchema"]["unsupportedSchemaCount"] == 1
assert data["validationCoverage"]["invalidReceipts"][0]["reason"] == "unsupported schemaVersion 9.0"
PY

cat > "$tmp_dir/logs/manual-proof-receipt.json" <<JSON
{
  "schemaVersion": "2.0",
  "receiptId": "manual-swift-test-context",
  "receiptType": "manual",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2099-01-01T00:00:00Z",
  "completedAt": "2099-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$log_sha",
    "bytes": $log_bytes
  },
  "scope": ["manual-proof-context"]
}
JSON

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/manual-proof-receipt.json" \
  --claim "Implemented scoped source update." \
  --out "$tmp_dir/verify-manual-review" >/dev/null

python3 - <<'PY' "$tmp_dir/verify-manual-review/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "review"
assert data["validationCoverage"]["status"] == "missing"
assert data["validationCoverage"]["downgradedReceipts"]
assert data["evidenceReceiptSchema"]["downgradedCount"] == 1
assert data["evidence"][0]["kind"] == "structured-proof"
assert data["evidence"][0]["usableForValidation"] is False
PY

cat > "$tmp_dir/logs/stale-v2-validation-receipt.json" <<JSON
{
  "schemaVersion": "2.0",
  "receiptId": "stale-v2-swift-test",
  "receiptType": "validation",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2000-01-01T00:00:00Z",
  "completedAt": "2000-01-01T00:00:10Z",
  "repositoryCommit": "synthetic",
  "artifact": {
    "path": "swift-test.log",
    "sha256": "$log_sha",
    "bytes": $log_bytes
  },
  "scope": ["DemoShipGuardAppTests"]
}
JSON

set +e
./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/logs/stale-v2-validation-receipt.json" \
  --claim "Implemented scoped source update." \
  --out "$tmp_dir/verify-stale-blocked" >/dev/null
stale_status=$?
set -e

if [[ "$stale_status" -ne 2 ]]; then
  echo "expected stale receipt verification to exit 2, got $stale_status" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/verify-stale-blocked/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
assert data["validationCoverage"]["status"] == "invalid"
assert data["evidenceReceiptSchema"]["staleCount"] == 1
assert data["validationCoverage"]["invalidReceipts"][0]["reason"] == "receipt predates task contract"
PY

grep -q 'Evidence Receipt Schema' "$tmp_dir/verify-v2-pass/shipguard-verdict.md"

echo "structured evidence receipt tests passed"
