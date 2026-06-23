#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/task" \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable >/dev/null

./bin/shipguard verify \
  --task "$tmp_dir/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out "$tmp_dir/pass" >"$tmp_dir/pass.out"

grep -q '## Proof Report' "$tmp_dir/pass/shipguard-verdict.md"
grep -q '## Quickstart Replay' "$tmp_dir/pass/shipguard-verdict.md"
grep -q 'Status: `pass`' "$tmp_dir/pass/shipguard-verdict.md"
grep -q 'Validation: `1/1 covered`' "$tmp_dir/pass/shipguard-verdict.md"
grep -q 'Claims checked: `1/1 accepted`' "$tmp_dir/pass/shipguard-verdict.md"
grep -q 'Release evidence: `not-applicable`' "$tmp_dir/pass/shipguard-verdict.md"
grep -q 'ShipGuard Proof Report: pass. Validation 1/1 covered; claims 1/1 accepted;' "$tmp_dir/pass.out"

python3 - "$tmp_dir/pass/shipguard-verdict.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
proof = data["proofReport"]
assert proof["title"] == "ShipGuard Proof Report"
assert proof["status"] == "pass"
assert proof["validation"]["label"] == "1/1 covered"
assert proof["claims"]["label"] == "1/1 accepted"
assert proof["riskFiles"]["protectedCount"] == 0
assert proof["riskFiles"]["outOfScopeCount"] == 0
assert proof["releaseEvidence"] == "not-applicable"
assert proof["mergeAllowed"] is True
assert "ShipGuard Proof Report: pass" in proof["copyReadyText"]
replay = data["quickstartReplay"]
assert replay["phase"] == "verify"
assert replay["status"] == "pass"
assert "shipguard verify" in replay["replayCommand"]
assert "ShipGuard Proof Report: pass" in replay["fastVerdict"]
assert "shipguard-verdict.json" in replay["reviewPacket"]
assert "shipguard-verdict.md" in replay["reviewPacket"]
PY

./bin/shipguard verify \
  --task "$tmp_dir/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test.log \
  --claim "Implemented scoped notification permission copy." \
  --out "$tmp_dir/review" >"$tmp_dir/review.out"

grep -q 'Status: `review`' "$tmp_dir/review/shipguard-verdict.md"
grep -q 'Quickstart Replay' "$tmp_dir/review/shipguard-verdict.md"
grep -q 'Validation: `0/1 covered`' "$tmp_dir/review/shipguard-verdict.md"
grep -q 'ShipGuard Proof Report: review. Validation 0/1 covered; claims 1/1 accepted;' "$tmp_dir/review.out"

set +e
./bin/shipguard verify \
  --task "$tmp_dir/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/protected-workflow.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Notification permission copy is fully verified." \
  --out "$tmp_dir/blocked" >"$tmp_dir/blocked.out"
blocked_status=$?
set -e

if [[ "$blocked_status" -ne 2 ]]; then
  echo "expected protected workflow quickstart diff to exit 2, got $blocked_status" >&2
  exit 1
fi

grep -q 'Status: `blocked`' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'Quickstart Replay' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'Unsupported Claim Replay' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'Revise the completion claim, or capture the required manual/physical-device proof receipt' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'not product proof' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'not a merge' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'Risk files: `1 risk file(s): 1 protected, 1 out of scope, 0 deleted test(s)`' "$tmp_dir/blocked/shipguard-verdict.md"
grep -q 'ShipGuard Proof Report: blocked. Validation 1/1 covered; claims 0/1 accepted;' "$tmp_dir/blocked.out"
python3 - "$tmp_dir/blocked/shipguard-verdict.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "blocked"
replay = data["unsupportedClaimReplay"]
assert replay["status"] == "review"
assert replay["unsupportedPhrases"] == ["fully verified"]
assert replay["unsupportedClaimCount"] == 1
assert replay["unsupportedClaims"][0]["status"] == "needs-manual-proof"
assert replay["manualProofClaimCount"] == 1
assert replay["manualProofClaims"][0]["claim"] == "Notification permission copy is fully verified."
assert replay["rejectedClaimCount"] == 0
assert replay["rejectedClaims"] == []
assert "shipguard verify" in replay["replayCommand"]
assert "--claim" in replay["replayCommand"]
assert "Notification permission copy is fully verified." in replay["replayCommand"]
assert replay["nextAction"]["resolves"] == ["unsupported-completion-claim", "manual-device-proof"]
assert "Revise the completion claim" in replay["nextAction"]["command"]
assert any("not product proof" in item for item in replay["nonClaims"])
assert any("not a merge" in item for item in replay["nonClaims"])
assert "does not prove" in replay["proofBoundary"]
assert "structured proof" in replay["proofBoundary"]
assert "manual/device proof" in replay["proofBoundary"]
PY
grep -q 'SHIPGUARD_VALIDATION_COMMAND: replace-with-your-test-command' examples/workflows/verify-pr.yml
grep -q 'Set SHIPGUARD_VALIDATION_COMMAND to your real test command' examples/workflows/verify-pr.yml
grep -q -- '--validation "$SHIPGUARD_VALIDATION_COMMAND"' examples/workflows/verify-pr.yml
grep -q 'bash -lc "$SHIPGUARD_VALIDATION_COMMAND"' examples/workflows/verify-pr.yml
grep -q 'command = sys.argv\[5\]' examples/workflows/verify-pr.yml
grep -q 'Inspect public demo outputs' docs/index.md
grep -q 'Verify-First Quickstart' docs/demo-reports.md
grep -q 'pass, review, and blocked demo path' docs/demo-reports.md
grep -q 'ShipGuard Proof Report: pass' examples/demo-reports/README.md
grep -q 'docs/verify-first-quickstart.md' examples/demo-reports/README.md

placeholder_count="$(grep -c 'replace-with-your-test-command' examples/workflows/verify-pr.yml)"
if [[ "$placeholder_count" -ne 2 ]]; then
  echo "expected workflow placeholder only in env default and guard, got $placeholder_count occurrences" >&2
  exit 1
fi

echo "verify-first quickstart tests passed"
