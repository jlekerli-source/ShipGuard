#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard lean audit --help >/dev/null
./bin/shipguard lean review --help >/dev/null
./bin/shipguard lean debt --help >/dev/null
./bin/shipguard lean gain --help >/dev/null
python3 -m py_compile scripts/lean_audit.py scripts/lean_review.py scripts/lean_debt.py scripts/lean_gain.py

./bin/shipguard lean audit \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/lean" \
  --mode full \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/lean/lean-audit.json"
test -f "$tmp_dir/lean/lean-audit.md"
grep -q '"tool": "shipguard lean audit"' "$tmp_dir/lean/lean-audit.json"
grep -q '"surface": "ShipGuard Lean Deck"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "native-date-input"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "native-color-input"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "dependency-date-helper-review"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "do-not-cut-safety-logic-without-proof"' "$tmp_dir/lean/lean-audit.json"
grep -q '"precisionReview":' "$tmp_dir/lean/lean-audit.json"
grep -q '"leanMode":' "$tmp_dir/lean/lean-audit.json"
grep -q '"firstActionBias": "proof-ladder"' "$tmp_dir/lean/lean-audit.json"
grep -q '"leanDebtLedger":' "$tmp_dir/lean/lean-audit.json"
grep -q '"behaviorGates":' "$tmp_dir/lean/lean-audit.json"
grep -q '"nativeOpportunityCatalog":' "$tmp_dir/lean/lean-audit.json"
grep -q '"marker": "shipguard-lean"' "$tmp_dir/lean/lean-audit.json"
grep -q '"hasUpgradeTrigger": true' "$tmp_dir/lean/lean-audit.json"
grep -q '"deleteList":' "$tmp_dir/lean/lean-audit.json"
grep -q '"simplifyFirst":' "$tmp_dir/lean/lean-audit.json"
grep -q '"keepList":' "$tmp_dir/lean/lean-audit.json"
grep -q '"blockedByProof":' "$tmp_dir/lean/lean-audit.json"
grep -q '"actionGroups":' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "thin-wrapper-review"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "thin-adapter-boundary"' "$tmp_dir/lean/lean-audit.json"
grep -q '"scopeBoundary"' "$tmp_dir/lean/lean-audit.json"
grep -q '"reportQualityQuestions"' "$tmp_dir/lean/lean-audit.json"
grep -q '"scanScope":' "$tmp_dir/lean/lean-audit.json"
grep -q 'Ponytail' "$tmp_dir/lean/lean-audit.md"
grep -q '## Lean Mode' "$tmp_dir/lean/lean-audit.md"
grep -q '## Behavior Gates' "$tmp_dir/lean/lean-audit.md"
grep -q '## Native Opportunity Catalog' "$tmp_dir/lean/lean-audit.md"
grep -q '## Precision Review' "$tmp_dir/lean/lean-audit.md"
grep -q 'Grouped Action Plan' "$tmp_dir/lean/lean-audit.md"
grep -q '## Lean Debt Ledger' "$tmp_dir/lean/lean-audit.md"
grep -q 'replace when fixture needs multi-call-site proof' "$tmp_dir/lean/lean-audit.md"
grep -q 'Keep Without More Proof' "$tmp_dir/lean/lean-audit.md"
grep -q 'Do not cut trust-boundary validation without proof' "$tmp_dir/lean/lean-audit.md"
if grep -q '/Users/' "$tmp_dir/lean/lean-audit.json"; then
  echo "shareable lean audit leaked an absolute user path" >&2
  exit 1
fi

clean_repo="$tmp_dir/clean-lean-repo"
mkdir -p "$clean_repo/Sources"
cat > "$clean_repo/Sources/Tiny.py" <<'PY'
def add(left, right):
    return left + right
PY

./bin/shipguard lean audit \
  --path "$clean_repo" \
  --out "$tmp_dir/clean-lean" \
  --mode ultra \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/clean-lean/lean-audit.json"
grep -q '"cleanStateAction":' "$tmp_dir/clean-lean/lean-audit.json"
grep -q '"kind": "pass-state-next-probe"' "$tmp_dir/clean-lean/lean-audit.json"
grep -q '"evidenceCommand":' "$tmp_dir/clean-lean/lean-audit.json"
grep -q '"nextCommand":' "$tmp_dir/clean-lean/lean-audit.json"
grep -q 'Clean State Action' "$tmp_dir/clean-lean/lean-audit.md"
grep -q 'Do not force a delete/simplify pass' "$tmp_dir/clean-lean/lean-audit.md"
if grep -q 'Start with the first delete action group' "$tmp_dir/clean-lean/lean-audit.md"; then
  echo "clean pass-state Lean Audit should not tell maintainers to start with a missing delete group" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/clean-lean" \
  --out "$tmp_dir/clean-lean-quality" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/clean-lean-quality/ios-report-quality.json"
if grep -q 'lean-clean-state-action' "$tmp_dir/clean-lean-quality/ios-report-quality.json"; then
  echo "report-quality should accept clean pass-state Lean Audit handoffs" >&2
  exit 1
fi

./bin/shipguard lean audit \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/lean-ultra" \
  --mode ultra \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/lean-ultra/lean-audit.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("leanMode", {}).get("mode") != "ultra":
    raise SystemExit("lean audit should record ultra mode")
precision = data.get("precisionReview") or {}
delete_list = precision.get("deleteList") or []
top_actions = precision.get("topActions") or []
if delete_list and top_actions and top_actions[0].get("ruleId") != delete_list[0].get("ruleId"):
    raise SystemExit(f"ultra mode should start with delete candidates: {top_actions[:1]!r} vs {delete_list[:1]!r}")
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null

grep -q 'shipguard lean audit' "$tmp_dir/quality/ios-report-quality.json"

./bin/shipguard lean audit \
  --path . \
  --out "$tmp_dir/repo-lean" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"fixtures"' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '"leanDebtLedger":' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '"behaviorGates":' "$tmp_dir/repo-lean/lean-audit.json"
if grep -q 'fixtures/lean-audit-demo' "$tmp_dir/repo-lean/lean-audit.json"; then
  echo "repo-level lean audit should not let public fixtures dominate findings" >&2
  exit 1
fi
if grep -q '"ruleId": "native-date-input"' "$tmp_dir/repo-lean/lean-audit.json"; then
  echo "repo-level lean audit should not treat prose such as 'moments' as a date picker dependency" >&2
  exit 1
fi
if grep -q '"ruleId": "large-legacy-file-review"' "$tmp_dir/repo-lean/lean-audit.json"; then
  echo "repo-level lean audit should not treat incidental legacy/compatibility strings or API names as large-file debt markers" >&2
  exit 1
fi

false_marker_repo="$tmp_dir/large-false-marker-repo"
mkdir -p "$false_marker_repo/scripts"
{
  echo 'LEGACY_LABEL = "Legacy SiriKit"'
  echo 'COMPATIBILITY_LABEL = "compatibility route"'
  echo 'def screenshot_path():'
  echo '    return tempfile.NamedTemporaryFile(prefix="shipguard-screenshot-", delete=False)'
  for index in $(seq 1 705); do
    echo "value_${index} = ${index}"
  done
} > "$false_marker_repo/scripts/FalseMarkers.py"

./bin/shipguard lean audit \
  --path "$false_marker_repo" \
  --out "$tmp_dir/false-marker-lean" \
  --shipguard-eval \
  --shareable >/dev/null

if grep -q '"ruleId": "large-legacy-file-review"' "$tmp_dir/false-marker-lean/lean-audit.json"; then
  echo "Lean Deck should ignore incidental legacy/compatibility strings and temp-file API names as large-file markers" >&2
  exit 1
fi

large_repo="$tmp_dir/large-legacy-repo"
mkdir -p "$large_repo/scripts"
for name in LargeOne.py LargeTwo.py; do
  {
    echo "# TODO remove compatibility branch after callers are migrated"
    for index in $(seq 1 705); do
      echo "value_${index} = ${index}"
    done
  } > "$large_repo/scripts/$name"
done

./bin/shipguard lean audit \
  --path "$large_repo" \
  --out "$tmp_dir/large-lean" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"actionGroups":' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"ruleId": "large-legacy-file-review"' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"leanEvidence":' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"markerPolicy":' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"firstMarkerLines":' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"evidenceCount": 2' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"firstExperiment": "Open the first marker line' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"validationRoute": "Run call-site search for each marker line' "$tmp_dir/large-lean/lean-audit.json"
grep -q '"stopCondition": "Stop if search or focused tests show the code is still active product behavior."' "$tmp_dir/large-lean/lean-audit.json"
grep -q 'Grouped Action Plan' "$tmp_dir/large-lean/lean-audit.md"
grep -q 'Individual Starting Points' "$tmp_dir/large-lean/lean-audit.md"
grep -q '## Lean Evidence Packets' "$tmp_dir/large-lean/lean-audit.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/large-lean" \
  --out "$tmp_dir/large-lean-quality" \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/large-lean-quality/ios-report-quality.json"
if grep -q 'lean-action-groups-missing' "$tmp_dir/large-lean-quality/ios-report-quality.json"; then
  echo "report-quality should accept grouped Lean action plans" >&2
  exit 1
fi

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff fixtures/lean-audit-demo/diffs/overbuilt-widget.diff \
  --out "$tmp_dir/review" \
  --mode full \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/review/lean-review.json"
test -f "$tmp_dir/review/lean-review.md"
grep -q '"tool": "shipguard lean review"' "$tmp_dir/review/lean-review.json"
grep -q '"surface": "ShipGuard Lean Review"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "native-date-input-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "dependency-small-helper-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "thin-wrapper-diff-review"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "deferred-shortcut-without-trigger"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "one-runnable-check-missing-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "hardware-calibration-missing-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "speculative-future-hook-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"reviewLines":' "$tmp_dir/review/lean-review.json"
grep -q '"leanMode":' "$tmp_dir/review/lean-review.json"
grep -q '"firstActionBias": "proof-ladder"' "$tmp_dir/review/lean-review.json"
grep -q '"behaviorGates":' "$tmp_dir/review/lean-review.json"
grep -q '"proofSignalCalibration":' "$tmp_dir/review/lean-review.json"
grep -q '"sameDiffProofStatus": "missing"' "$tmp_dir/review/lean-review.json"
grep -q '"missingRunnableCheckFindings":' "$tmp_dir/review/lean-review.json"
grep -q '"precisionReview":' "$tmp_dir/review/lean-review.json"
grep -q '"actionGroups":' "$tmp_dir/review/lean-review.json"
python3 - <<'PY' "$tmp_dir/review/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
precision = data.get("precisionReview") or {}
delete_rules = {item.get("ruleId") for item in precision.get("deleteList") or []}
if "speculative-future-hook-diff" not in delete_rules:
    raise SystemExit(f"speculative future hooks should be delete candidates: {delete_rules!r}")
groups = precision.get("actionGroups") or []
matching = [
    group
    for group in groups
    if group.get("ruleId") == "speculative-future-hook-diff" and group.get("decision") == "delete"
]
if not matching:
    raise SystemExit(f"expected a delete action group for speculative future hooks: {groups!r}")
PY
grep -q 'ShipGuard Lean Review' "$tmp_dir/review/lean-review.md"
grep -q '## Lean Mode' "$tmp_dir/review/lean-review.md"
grep -q 'Diff Review' "$tmp_dir/review/lean-review.md"
grep -q 'Behavior Gates' "$tmp_dir/review/lean-review.md"
grep -q 'Proof Signal Calibration' "$tmp_dir/review/lean-review.md"
grep -q 'Grouped Action Plan' "$tmp_dir/review/lean-review.md"
grep -q 'delete | `speculative-future-hook-diff`' "$tmp_dir/review/lean-review.md"
grep -q 'Individual Starting Points' "$tmp_dir/review/lean-review.md"
if grep -q '/Users/' "$tmp_dir/review/lean-review.json"; then
  echo "shareable lean review leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff fixtures/lean-audit-demo/diffs/overbuilt-widget.diff \
  --out "$tmp_dir/review-lite" \
  --mode lite \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/review-lite/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("leanMode", {}).get("mode") != "lite":
    raise SystemExit("lean review should record lite mode")
precision = data.get("precisionReview") or {}
simplify = precision.get("simplifyFirst") or []
top_actions = precision.get("topActions") or []
if simplify and top_actions and top_actions[0].get("ruleId") != simplify[0].get("ruleId"):
    raise SystemExit(f"lite mode should start with simplify suggestions: {top_actions[:1]!r} vs {simplify[:1]!r}")
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/review" \
  --out "$tmp_dir/review-quality" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/review-quality/ios-report-quality.json"
if grep -q 'lean-action-groups-markdown-missing' "$tmp_dir/review-quality/ios-report-quality.json"; then
  echo "report-quality should accept Lean Review Markdown grouped action plans" >&2
  exit 1
fi

cat > "$tmp_dir/empty.diff" <<'DIFF'
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/empty.diff" \
  --out "$tmp_dir/clean-review" \
  --mode ultra \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/clean-review/lean-review.json"
grep -q '"cleanStateAction":' "$tmp_dir/clean-review/lean-review.json"
grep -q '"kind": "pass-state-next-probe"' "$tmp_dir/clean-review/lean-review.json"
grep -q '"evidenceCommand":' "$tmp_dir/clean-review/lean-review.json"
grep -q '"nextCommand":' "$tmp_dir/clean-review/lean-review.json"
grep -q 'Clean State Action' "$tmp_dir/clean-review/lean-review.md"
grep -q 'Do not force a delete/simplify pass' "$tmp_dir/clean-review/lean-review.md"
if grep -q 'Start with precisionReview.topActions\[0\]' "$tmp_dir/clean-review/lean-review.md"; then
  echo "clean pass-state Lean Review should not point to a missing top action" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/clean-review" \
  --out "$tmp_dir/clean-review-quality" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/clean-review-quality/ios-report-quality.json"
if grep -q 'lean-clean-state-action' "$tmp_dir/clean-review-quality/ios-report-quality.json"; then
  echo "report-quality should accept clean pass-state Lean Review handoffs" >&2
  exit 1
fi

cat > "$tmp_dir/detector-command.diff" <<'DIFF'
diff --git a/tools/lean_commands.py b/tools/lean_commands.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/tools/lean_commands.py
@@ -0,0 +1,3 @@
+LEAN_MARKERS = ("TODO", "FIXME", "temporary", "future-proof", "placeholder", "for later")
+def lean_marker_command(path):
+    return f'rg -n "TODO|FIXME|temporary|future-proof|placeholder|for later" {path}'
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/detector-command.diff" \
  --out "$tmp_dir/detector-review" \
  --shipguard-eval \
  --shareable >/dev/null

if grep -q '"ruleId": "speculative-future-hook-diff"' "$tmp_dir/detector-review/lean-review.json"; then
  echo "Lean Review should not flag a diagnostic rg command as speculative code" >&2
  exit 1
fi

cat > "$tmp_dir/prose-token.diff" <<'DIFF'
diff --git a/tools/profile_text.py b/tools/profile_text.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/tools/profile_text.py
@@ -0,0 +1,2 @@
+MODE_GUIDANCE = "lite mode preserves implementation momentum"
+BOUNDARY_GUIDANCE = "Keep hardware boundaries visible in profile guidance"
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/prose-token.diff" \
  --out "$tmp_dir/prose-token-review" \
  --shipguard-eval \
  --shareable >/dev/null

if grep -q '"ruleId": "native-date-input-diff"' "$tmp_dir/prose-token-review/lean-review.json"; then
  echo "Lean Review should not treat prose token 'momentum' as the moment date dependency" >&2
  exit 1
fi
if grep -q '"ruleId": "hardware-calibration-missing-diff"' "$tmp_dir/prose-token-review/lean-review.json"; then
  echo "Lean Review should not treat generic profile guidance mentioning hardware as hardware implementation code" >&2
  exit 1
fi

cat > "$tmp_dir/same-diff-proof.diff" <<'DIFF'
diff --git a/src/proof_target.py b/src/proof_target.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/proof_target.py
@@ -0,0 +1,5 @@
+def classify(value):
+    if value > 0:
+        return "positive"
+    return "other"
diff --git a/tests/test_proof_target.py b/tests/test_proof_target.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/tests/test_proof_target.py
@@ -0,0 +1,4 @@
+from src.proof_target import classify
+
+def test_classify_positive():
+    assert classify(1) == "positive"
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/same-diff-proof.diff" \
  --out "$tmp_dir/same-diff-proof-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "one-runnable-check-signal-present-diff"' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"sameDiffProofStatus": "present"' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"codeFindingsCoveredBySameDiffProof": 1' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"sameDiffProofSignalCount": 1' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q 'Proof Signal Calibration' "$tmp_dir/same-diff-proof-review/lean-review.md"
grep -q 'tests/test_proof_target.py:1' "$tmp_dir/same-diff-proof-review/lean-review.md"
if grep -q '"ruleId": "one-runnable-check-missing-diff"' "$tmp_dir/same-diff-proof-review/lean-review.json"; then
  echo "Lean Review should calibrate same-diff test evidence instead of reporting a missing runnable check" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/same-diff-proof-review" \
  --out "$tmp_dir/same-diff-proof-quality" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/same-diff-proof-quality/ios-report-quality.json"

./bin/shipguard lean debt \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/debt" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/debt/lean-debt.json"
test -f "$tmp_dir/debt/lean-debt.md"
grep -q '"tool": "shipguard lean debt"' "$tmp_dir/debt/lean-debt.json"
grep -q '"surface": "ShipGuard Lean Debt"' "$tmp_dir/debt/lean-debt.json"
grep -q '"marker": "shipguard-lean"' "$tmp_dir/debt/lean-debt.json"
grep -q '"status": "tracked"' "$tmp_dir/debt/lean-debt.json"
grep -q 'ShipGuard Lean Debt' "$tmp_dir/debt/lean-debt.md"
if grep -q '/Users/' "$tmp_dir/debt/lean-debt.json"; then
  echo "shareable lean debt leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard lean gain \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/gain" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/gain/lean-gain.json"
test -f "$tmp_dir/gain/lean-gain.md"
grep -q '"tool": "shipguard lean gain"' "$tmp_dir/gain/lean-gain.json"
grep -q '"surface": "ShipGuard Lean Gain"' "$tmp_dir/gain/lean-gain.json"
grep -q '"perRepoSavingsClaim": "not-computed"' "$tmp_dir/gain/lean-gain.json"
grep -q '"benchmarkScoreboard":' "$tmp_dir/gain/lean-gain.json"
grep -q 'Honesty Boundary' "$tmp_dir/gain/lean-gain.md"
if grep -q '/Users/' "$tmp_dir/gain/lean-gain.json"; then
  echo "shareable lean gain leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean" \
  --reports "$tmp_dir/review" \
  --reports "$tmp_dir/debt" \
  --reports "$tmp_dir/gain" \
  --out "$tmp_dir/lean-family-quality" \
  --shareable >/dev/null

grep -q 'shipguard lean audit' "$tmp_dir/lean-family-quality/ios-report-quality.json"
grep -q 'shipguard lean review' "$tmp_dir/lean-family-quality/ios-report-quality.json"
grep -q 'shipguard lean debt' "$tmp_dir/lean-family-quality/ios-report-quality.json"
grep -q 'shipguard lean gain' "$tmp_dir/lean-family-quality/ios-report-quality.json"

echo "lean audit tests passed"
