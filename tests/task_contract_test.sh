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
assert data["verdict"]["status"] == "prepared"
assert data["riskClassification"]["level"] in {"high", "critical"}
assert data["scopeBoundary"]["shipguardOnly"] is True
assert data["scopeBoundary"]["targetAppsReadOnly"] is True
assert data["authorizedFiles"]
assert ".github/workflows/**" in data["protectedBoundaries"]
assert data["validationContract"]["required"][0]["command"] == "swift test"
assert data["nextAction"]["command"]
PY

cat > "$tmp_dir/good.diff" <<'DIFF'
diff --git a/Sources/DemoShipGuardApp/DemoPermissions.swift b/Sources/DemoShipGuardApp/DemoPermissions.swift
--- a/Sources/DemoShipGuardApp/DemoPermissions.swift
+++ b/Sources/DemoShipGuardApp/DemoPermissions.swift
@@ -1,3 +1,4 @@
+// scoped proof fixture
DIFF
printf 'swift test passed for DemoPermissionsTests\n' > "$tmp_dir/swift-test.log"

./bin/shipguard verify \
  --task "$tmp_dir/prepare/shipguard-task.json" \
  --diff "$tmp_dir/good.diff" \
  --evidence "$tmp_dir/swift-test.log" \
  --claim "Implemented scoped notification onboarding source update." \
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
assert data["changedFiles"] == ["Sources/DemoShipGuardApp/DemoPermissions.swift"]
assert data["scopeChecks"]["outOfScope"] == []
assert data["scopeChecks"]["forbiddenTouched"] == []
assert data["evidence"][0]["present"] is True
assert data["claimChecks"]["rejectedClaims"] == []
assert data["nextAction"]["expectedArtifact"] == "review-ready proof packet"
PY

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

python3 - <<'PY' "$tmp_dir/verify-blocked/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
assert ".github/workflows/release.yml" in data["scopeChecks"]["outOfScope"]
assert ".github/workflows/release.yml" in data["scopeChecks"]["forbiddenTouched"]
assert "fully verified" in data["claimChecks"]["rejectedClaims"]
assert data["nextAction"]["owner"] == "developer"
assert "Update the task contract scope" in data["nextAction"]["command"]
PY

echo "task contract tests passed"
