#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/demo-ios-performance"
cp -R fixtures/demo-ios-repo "$fixture"
mkdir -p "$fixture/release-artifacts/noisy-proof"
cat > "$fixture/release-artifacts/noisy-proof/GeneratedPerformanceNoise.swift" <<'SWIFT'
import SwiftUI

struct GeneratedPerformanceNoise: View {
    var body: some View {
        TimelineView(.periodic(from: .now, by: 0.01)) { _ in
            Text("Generated proof noise")
        }
    }
}
SWIFT
cat > "$fixture/Sources/DemoShipGuardApp/RepeatedPerformanceFindings.swift" <<'SWIFT'
import SwiftUI
import UserNotifications

struct RepeatedPerformanceFindings: View {
    var body: some View {
        VStack {
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("A") }
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("B") }
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("C") }
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("D") }
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("E") }
            TimelineView(.periodic(from: .now, by: 0.01)) { _ in Text("F") }
        }
    }
}

@MainActor
final class RepeatedNotificationCleanup {
    func cleanup() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["a"])
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["b"])
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["c"])
    }
}
SWIFT

./bin/shipguard ios performance --help >/dev/null
./bin/shipguard ios performance \
  --path "$fixture" \
  --out "$tmp_dir/performance" >/dev/null
./bin/shipguard ios performance \
  --path "$fixture" \
  --out "$tmp_dir/eval-performance" \
  --shipguard-eval >/dev/null
./bin/shipguard ios performance \
  --path "$fixture" \
  --out "$tmp_dir/shareable-performance" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/performance/ios-performance.json"
test -f "$tmp_dir/performance/ios-performance.md"
test -f "$tmp_dir/eval-performance/ios-performance.json"
test -f "$tmp_dir/eval-performance/ios-performance.md"
test -f "$tmp_dir/shareable-performance/ios-performance.json"
test -f "$tmp_dir/shareable-performance/ios-performance.md"
grep -q '"tool": "shipguard ios performance"' "$tmp_dir/performance/ios-performance.json"
grep -q '"status": "blocked"' "$tmp_dir/performance/ios-performance.json"
grep -q '"intent": "app-development"' "$tmp_dir/performance/ios-performance.json"
grep -q '"ruleId": "swiftui-periodic-timeline"' "$tmp_dir/performance/ios-performance.json"
grep -q '"ruleId": "notification-removal-ui-stall"' "$tmp_dir/performance/ios-performance.json"
grep -q '"ruleId": "formatter-created-in-view"' "$tmp_dir/performance/ios-performance.json"
grep -q '"severityReason":' "$tmp_dir/performance/ios-performance.json"
grep -q '"localProof":' "$tmp_dir/performance/ios-performance.json"
grep -q '"manualProof":' "$tmp_dir/performance/ios-performance.json"
grep -q '"impact":' "$tmp_dir/performance/ios-performance.json"
grep -q '"groupedActionPlan":' "$tmp_dir/performance/ios-performance.json"
grep -q '"evidencePromotion":' "$tmp_dir/performance/ios-performance.json"
grep -q '"promotionStatus": "missing-runtime-proof"' "$tmp_dir/performance/ios-performance.json"
grep -q '"expectedArtifact":' "$tmp_dir/performance/ios-performance.json"
grep -q '"successCondition":' "$tmp_dir/performance/ios-performance.json"
grep -q '"failureMeaning":' "$tmp_dir/performance/ios-performance.json"
grep -q '"scanScope"' "$tmp_dir/performance/ios-performance.json"
grep -q '"release-artifacts"' "$tmp_dir/performance/ios-performance.json"
grep -q 'Scan Scope' "$tmp_dir/performance/ios-performance.md"
grep -q 'release-artifacts' "$tmp_dir/performance/ios-performance.md"
grep -q 'Evidence Promotion Contract' "$tmp_dir/performance/ios-performance.md"
grep -q 'Expected artifact' "$tmp_dir/performance/ios-performance.md"
grep -q 'Success condition' "$tmp_dir/performance/ios-performance.md"
grep -q 'Failure meaning' "$tmp_dir/performance/ios-performance.md"
grep -q 'Why severity' "$tmp_dir/performance/ios-performance.md"
grep -q 'Why it matters' "$tmp_dir/performance/ios-performance.md"
grep -q 'Grouped Next Actions' "$tmp_dir/performance/ios-performance.md"
grep -q 'First experiment' "$tmp_dir/performance/ios-performance.md"
grep -q 'Validation route' "$tmp_dir/performance/ios-performance.md"
grep -q 'Stop condition' "$tmp_dir/performance/ios-performance.md"
grep -q 'Proof Boundaries' "$tmp_dir/performance/ios-performance.md"
grep -q 'Codex local proof' "$tmp_dir/performance/ios-performance.md"
grep -q 'Manual/device proof' "$tmp_dir/performance/ios-performance.md"
if grep -q 'GeneratedPerformanceNoise.swift' "$tmp_dir/performance/ios-performance.json"; then
  echo "ios performance should skip generated proof artifacts" >&2
  exit 1
fi
python3 - <<'PY' "$tmp_dir/performance/ios-performance.json" "$tmp_dir/performance/ios-performance.md"
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
groups = {item["ruleId"]: item for item in report["groupedActionPlan"]}
promotion = report.get("evidencePromotion") or {}
next_action = promotion.get("nextAction") or {}
if promotion.get("sourceEvidence") != "source heuristic":
    raise SystemExit(f"unexpected evidence promotion source: {promotion!r}")
if promotion.get("promotionStatus") != "missing-runtime-proof":
    raise SystemExit(f"unexpected evidence promotion status: {promotion!r}")
if not promotion.get("firstCandidateRule"):
    raise SystemExit(f"missing first candidate rule: {promotion!r}")
for field in ("owner", "expectedArtifact", "successCondition", "failureMeaning"):
    if not next_action.get(field):
        raise SystemExit(f"next action missing {field}: {next_action!r}")
if not (next_action.get("command") or next_action.get("manualProof")):
    raise SystemExit(f"next action needs command or manual proof: {next_action!r}")
for rule_id in ("swiftui-periodic-timeline", "notification-removal-ui-stall"):
    if groups.get(rule_id, {}).get("count", 0) <= 3:
        raise SystemExit(f"expected repeated group for {rule_id}: {groups.get(rule_id)}")
    for field in ("firstLocations", "severityReason", "whyThisGroupMatters", "firstExperiment", "validationRoute", "stopCondition", "recommendedFirstMove", "localProof", "manualProof", "proofGuidance"):
        if not groups[rule_id].get(field):
            raise SystemExit(f"group {rule_id} missing {field}: {groups[rule_id]}")

markdown = Path(sys.argv[2]).read_text(encoding="utf-8")
top = markdown.split("## Top Findings", 1)[1].split("## Proof Boundaries", 1)[0]
if top.count("`swiftui-periodic-timeline`") > 3:
    raise SystemExit("top findings should cap repeated timeline rows after grouped actions")
PY
grep -q 'physical-device smoothness' "$tmp_dir/performance/ios-performance.md"
grep -q 'Animation Hitches' "$tmp_dir/performance/ios-performance.md"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/eval-performance/ios-performance.json"
grep -q '"shipguardOnly": true' "$tmp_dir/eval-performance/ios-performance.json"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/eval-performance/ios-performance.md"
grep -q 'Do not edit the scanned app' "$tmp_dir/eval-performance/ios-performance.md"
grep -q 'Report Quality Questions' "$tmp_dir/eval-performance/ios-performance.md"
grep -q 'Did report wording keep target-app remediation separate from ShipGuard product QA next steps?' "$tmp_dir/eval-performance/ios-performance.json"
grep -q 'Which grouped performance observation should become a public fixture or eval case before changing scanner heuristics again?' "$tmp_dir/eval-performance/ios-performance.json"
if grep -q 'Did grouped first experiments name a clear validation route and stop condition before broader refactors?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied stop-condition gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Did grouped next actions name the smallest first experiment before broad refactors?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied first-experiment gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Did proof guidance name what Codex can verify locally and what remains device/manual proof?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied proof-boundary gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Did high severity reasons cite concrete thresholds, actor context, or source signals rather than broad suspicion?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied high-severity gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Were high findings justified by evidence instead of broad suspicion?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied high-evidence gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Did grouped next actions make repeated rules scannable without hiding full JSON evidence?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied grouping-action gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Were repeated rules grouped enough to stay scannable?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied grouping gate as the first actionability question" >&2
  exit 1
fi
if grep -q 'Did the report explain why each finding matters without requiring private app context?' "$tmp_dir/eval-performance/ios-performance.json"; then
  echo "ios performance should not keep a satisfied explanation gate as the first actionability question" >&2
  exit 1
fi
grep -q '"mode": "shareable"' "$tmp_dir/shareable-performance/ios-performance.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/shareable-performance/ios-performance.json"
grep -q '"project": "."' "$tmp_dir/shareable-performance/ios-performance.json"
grep -q 'Shareability mode: `shareable`' "$tmp_dir/shareable-performance/ios-performance.md"
if grep -R -F -q "$tmp_dir" "$tmp_dir/shareable-performance"; then
  echo "ios performance --shareable should not leak local temp paths" >&2
  exit 1
fi
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/shareable-performance" \
  --out "$tmp_dir/shareable-performance-quality" \
  --shareable >/dev/null
if grep -q 'local-path-shareability-warning' "$tmp_dir/shareable-performance-quality/ios-report-quality.json"; then
  echo "shareable ios performance should not trigger report-quality local-path warning" >&2
  exit 1
fi

json_stdout="$(./bin/shipguard ios performance --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios performance"'
eval_json_stdout="$(./bin/shipguard ios performance --path fixtures/demo-ios-repo --shipguard-eval --json)"
printf '%s\n' "$eval_json_stdout" | grep -q '"intent": "shipguard-evaluation"'

echo "ios performance tests passed"
