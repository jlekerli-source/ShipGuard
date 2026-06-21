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
grep -q '"modeBiasReview":' "$tmp_dir/review/lean-review.json"
grep -q '"selectedMode": "full"' "$tmp_dir/review/lean-review.json"
grep -q '"selectedTopActionMatchesBias": true' "$tmp_dir/review/lean-review.json"
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
if data.get("modeBiasReview", {}).get("selectedFirstActionBias") != "proof-ladder":
    raise SystemExit("full Lean Review should record proof-ladder mode bias")
precision = data.get("precisionReview") or {}
delete_rules = {item.get("ruleId") for item in precision.get("deleteList") or []}
if "speculative-future-hook-diff" not in delete_rules:
    raise SystemExit(f"speculative future hooks should be delete candidates: {delete_rules!r}")
mode_bias = data.get("modeBiasReview") or {}
if mode_bias.get("expectedFirstSource") != "deleteList":
    raise SystemExit(f"full mode should start from deleteList: {mode_bias!r}")
top_actions = precision.get("topActions") or []
if top_actions and top_actions[0].get("ruleId") != (precision.get("deleteList") or [{}])[0].get("ruleId"):
    raise SystemExit(f"full mode top action should match deleteList first action: {top_actions[:1]!r}")
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
grep -q '## Mode Bias Review' "$tmp_dir/review/lean-review.md"
grep -q 'suggestion-first' "$tmp_dir/review/lean-review.md"
grep -q 'delete-first' "$tmp_dir/review/lean-review.md"
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
if data.get("leanMode", {}).get("firstActionBias") != "suggestion-first":
    raise SystemExit("lite mode should use suggestion-first bias")
mode_bias = data.get("modeBiasReview") or {}
if mode_bias.get("expectedFirstSource") != "simplifyFirst":
    raise SystemExit(f"lite mode should start from simplifyFirst: {mode_bias!r}")
precision = data.get("precisionReview") or {}
simplify = precision.get("simplifyFirst") or []
top_actions = precision.get("topActions") or []
if simplify and top_actions and top_actions[0].get("ruleId") != simplify[0].get("ruleId"):
    raise SystemExit(f"lite mode should start with simplify suggestions: {top_actions[:1]!r} vs {simplify[:1]!r}")
PY

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff fixtures/lean-audit-demo/diffs/overbuilt-widget.diff \
  --out "$tmp_dir/review-ultra" \
  --mode ultra \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/review-ultra/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("leanMode", {}).get("mode") != "ultra":
    raise SystemExit("lean review should record ultra mode")
if data.get("leanMode", {}).get("firstActionBias") != "delete-first":
    raise SystemExit("ultra mode should use delete-first bias")
mode_bias = data.get("modeBiasReview") or {}
if mode_bias.get("expectedFirstSource") != "deleteList":
    raise SystemExit(f"ultra mode should start from deleteList when deletes exist: {mode_bias!r}")
precision = data.get("precisionReview") or {}
delete = precision.get("deleteList") or []
top_actions = precision.get("topActions") or []
if delete and top_actions and top_actions[0].get("ruleId") != delete[0].get("ruleId"):
    raise SystemExit(f"ultra mode should start with delete candidates: {top_actions[:1]!r} vs {delete[:1]!r}")
if not (mode_bias.get("summary") or {}).get("selectedTopActionMatchesBias"):
    raise SystemExit(f"ultra mode should prove selected top-action match: {mode_bias!r}")
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

cat > "$tmp_dir/hardware-host-boundary.diff" <<'DIFF'
diff --git a/src/plugin_host_adapter.js b/src/plugin_host_adapter.js
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/plugin_host_adapter.js
@@ -0,0 +1,3 @@
+export function handlePluginRequest(request) {
+  return pluginHost.handle(request)
+}
diff --git a/src/sensor_sampler.py b/src/sensor_sampler.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/src/sensor_sampler.py
@@ -0,0 +1,3 @@
+def sample_sensor(adc):
+    raw = adc.read(0)
+    return raw
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/hardware-host-boundary.diff" \
  --out "$tmp_dir/hardware-host-boundary-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "host-adapter-boundary-diff"' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q '"ruleId": "hardware-calibration-missing-diff"' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q '"hardwareHostBoundaryReview":' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q '"hostAdapterBoundaryFindings": 1' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q '"hardwareCalibrationFindings": 1' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q '"falseLessCodePressureBlocked": 2' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
grep -q 'Hardware And Host Boundary Review' "$tmp_dir/hardware-host-boundary-review/lean-review.md"
grep -q 'Hardware Calibration Proof' "$tmp_dir/hardware-host-boundary-review/lean-review.md"
grep -q 'Host Adapter Boundaries' "$tmp_dir/hardware-host-boundary-review/lean-review.md"
python3 - <<'PY' "$tmp_dir/hardware-host-boundary-review/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
decisions = {row["file"]: row for row in data["currentDiffDecisionMap"]["decisions"]}
host = decisions["src/plugin_host_adapter.js"]
sensor = decisions["src/sensor_sampler.py"]
if host["decision"] != "keep" or host["ruleIds"] != ["host-adapter-boundary-diff"]:
    raise SystemExit(f"host adapter should be a keep boundary: {host!r}")
if sensor["decision"] != "proof-blocked" or sensor["ruleIds"] != ["hardware-calibration-missing-diff"]:
    raise SystemExit(f"sensor code should be proof-blocked: {sensor!r}")
rules = {item["ruleId"] for item in data["findings"]}
if "thin-wrapper-diff-review" in rules:
    raise SystemExit(f"host adapter must not be treated as a delete-wrapper finding: {rules!r}")
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/hardware-host-boundary-review" \
  --out "$tmp_dir/hardware-host-boundary-quality" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/hardware-host-boundary-quality/ios-report-quality.json"
if grep -q 'lean-review-hardware-host-boundary' "$tmp_dir/hardware-host-boundary-quality/ios-report-quality.json"; then
  echo "report-quality should accept complete hardware/host boundary review packets" >&2
  exit 1
fi

cat > "$tmp_dir/hardware-wrapper.diff" <<'DIFF'
diff --git a/src/sensor_wrapper.js b/src/sensor_wrapper.js
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/sensor_wrapper.js
@@ -0,0 +1,3 @@
+export function sampleSensor(adc) {
+  return adc.read(channel)
+}
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/hardware-wrapper.diff" \
  --out "$tmp_dir/hardware-wrapper-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "hardware-calibration-missing-diff"' "$tmp_dir/hardware-wrapper-review/lean-review.json"
grep -q '"ruleId": "thin-wrapper-diff-review"' "$tmp_dir/hardware-wrapper-review/lean-review.json"
python3 - <<'PY' "$tmp_dir/hardware-wrapper-review/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
decision = data["currentDiffDecisionMap"]["decisions"][0]
if decision["decision"] != "proof-blocked":
    raise SystemExit(f"hardware wrapper should be proof-blocked before delete pressure: {decision!r}")
for expected in ("hardware-calibration-missing-diff", "thin-wrapper-diff-review"):
    if expected not in decision["ruleIds"]:
        raise SystemExit(f"hardware wrapper decision should preserve {expected}: {decision!r}")
PY

cat > "$tmp_dir/python-host-adapter.diff" <<'DIFF'
diff --git a/src/plugin_host_adapter.py b/src/plugin_host_adapter.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/plugin_host_adapter.py
@@ -0,0 +1,2 @@
+def handle_plugin_request(request):
+    return plugin_host.handle(request)
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/python-host-adapter.diff" \
  --out "$tmp_dir/python-host-adapter-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "host-adapter-boundary-diff"' "$tmp_dir/python-host-adapter-review/lean-review.json"
python3 - <<'PY' "$tmp_dir/python-host-adapter-review/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
decision = data["currentDiffDecisionMap"]["decisions"][0]
if decision["decision"] != "keep" or decision["ruleIds"] != ["host-adapter-boundary-diff"]:
    raise SystemExit(f"Python host adapter should be a keep boundary: {decision!r}")
rules = {item["ruleId"] for item in data["findings"]}
if "thin-wrapper-diff-review" in rules:
    raise SystemExit(f"Python host adapter must not be treated as a delete-wrapper finding: {rules!r}")
PY

cat > "$tmp_dir/safety-boundary.diff" <<'DIFF'
diff --git a/src/permission_gate.py b/src/permission_gate.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/permission_gate.py
@@ -0,0 +1,5 @@
+def can_delete_account(user, request):
+    if not user.has_permission("delete_account"):
+        return "blocked"
+    audit_security_event("delete-account-request", request.id)
+    return "allowed"
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/safety-boundary.diff" \
  --out "$tmp_dir/safety-boundary-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "do-not-cut-safety-diff-without-proof"' "$tmp_dir/safety-boundary-review/lean-review.json"
grep -q '"safetyBoundaryReview":' "$tmp_dir/safety-boundary-review/lean-review.json"
grep -q '"safetyBoundaryFindings": 1' "$tmp_dir/safety-boundary-review/lean-review.json"
grep -q 'Safety Boundary Review' "$tmp_dir/safety-boundary-review/lean-review.md"
grep -q 'Keep With Proof Boundaries' "$tmp_dir/safety-boundary-review/lean-review.md"
python3 - <<'PY' "$tmp_dir/safety-boundary-review/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
decision = data["currentDiffDecisionMap"]["decisions"][0]
if decision["decision"] != "keep":
    raise SystemExit(f"safety boundary should be kept before deletion pressure: {decision!r}")
if "do-not-cut-safety-diff-without-proof" not in decision.get("ruleIds", []):
    raise SystemExit(f"safety boundary decision should keep the safety rule visible: {decision!r}")
review = data.get("safetyBoundaryReview") or {}
summary = review.get("summary") or {}
if summary.get("falseDeletionPressureBlocked") != 1 or summary.get("keepSafetyBoundaryFiles") != 1:
    raise SystemExit(f"safety boundary summary should count blocked deletion pressure: {summary!r}")
rows = review.get("safetyBoundaryFindings") or []
if not rows or rows[0].get("line") is None or ":" not in rows[0].get("location", ""):
    raise SystemExit(f"safety boundary row should point at the first matched added line: {rows!r}")
if not rows[0].get("evidence") or rows[0].get("evidence") == "diff touches security/validation/accessibility/data-loss terms":
    raise SystemExit(f"safety boundary row should include the matched diff evidence: {rows!r}")
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/safety-boundary-review" \
  --out "$tmp_dir/safety-boundary-quality" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/safety-boundary-quality/ios-report-quality.json"
if grep -q 'lean-review-safety-boundary' "$tmp_dir/safety-boundary-quality/ios-report-quality.json"; then
  echo "report-quality should accept complete safety-boundary review packets" >&2
  exit 1
fi

cat > "$tmp_dir/safety-fixture-report.diff" <<'DIFF'
diff --git a/fixtures/ios-report-quality/safety-demo/fixture-report.json b/fixtures/ios-report-quality/safety-demo/fixture-report.json
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/fixtures/ios-report-quality/safety-demo/fixture-report.json
@@ -0,0 +1,6 @@
+{
+  "question": "Does the report keep permission and delete safety boundaries visible?",
+  "policy": "Do not delete validation or security rows without proof.",
+  "status": "pass"
+}
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/safety-fixture-report.diff" \
  --out "$tmp_dir/safety-fixture-report-review" \
  --shipguard-eval \
  --shareable >/dev/null

if grep -q '"ruleId": "do-not-cut-safety-diff-without-proof"' "$tmp_dir/safety-fixture-report-review/lean-review.json"; then
  echo "Lean Review should not treat public fixture report prose as product safety-boundary code" >&2
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
grep -q '"runnableCheckReview":' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"duplicateCeremonyAvoided": 1' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"proofSignalMatching":' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"matchedSameDiffProofFiles": 1' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"missingProofFiles": 0' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q '"unmatchedProofSignalCount": 0' "$tmp_dir/same-diff-proof-review/lean-review.json"
grep -q 'Proof Signal Calibration' "$tmp_dir/same-diff-proof-review/lean-review.md"
grep -q 'Runnable Check Review' "$tmp_dir/same-diff-proof-review/lean-review.md"
grep -q 'Proof Signal Matching' "$tmp_dir/same-diff-proof-review/lean-review.md"
grep -q 'tests/test_proof_target.py:4' "$tmp_dir/same-diff-proof-review/lean-review.md"
if grep -q '"ruleId": "one-runnable-check-missing-diff"' "$tmp_dir/same-diff-proof-review/lean-review.json"; then
  echo "Lean Review should calibrate same-diff test evidence instead of reporting a missing runnable check" >&2
  exit 1
fi

cat > "$tmp_dir/unrelated-proof.diff" <<'DIFF'
diff --git a/src/order_router.py b/src/order_router.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/src/order_router.py
@@ -0,0 +1,5 @@
+def route_order(order):
+    if order.priority > 5:
+        return "priority"
+    return "normal"
diff --git a/tests/test_profile_badge.py b/tests/test_profile_badge.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/tests/test_profile_badge.py
@@ -0,0 +1,4 @@
+from src.profile_badge import badge_text
+
+def test_badge_text():
+    assert badge_text("new") == "New"
DIFF

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff "$tmp_dir/unrelated-proof.diff" \
  --out "$tmp_dir/unrelated-proof-review" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"ruleId": "one-runnable-check-missing-diff"' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"sameDiffProofStatus": "present"' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"codeFindingsCoveredBySameDiffProof": 0' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"missingRunnableCheckFindings": 1' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"matchedSameDiffProofFiles": 0' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"missingProofFiles": 1' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"unmatchedProofSignalCount": 1' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q '"duplicateCeremonyAvoided": 0' "$tmp_dir/unrelated-proof-review/lean-review.json"
grep -q 'Proof Signal Matching' "$tmp_dir/unrelated-proof-review/lean-review.md"
grep -q 'Unmatched Proof Signals' "$tmp_dir/unrelated-proof-review/lean-review.md"
grep -q 'tests/test_profile_badge.py:4' "$tmp_dir/unrelated-proof-review/lean-review.md"
if grep -q '"ruleId": "one-runnable-check-signal-present-diff"' "$tmp_dir/unrelated-proof-review/lean-review.json"; then
  echo "Lean Review should not count unrelated changed tests as same-diff proof for another file" >&2
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
