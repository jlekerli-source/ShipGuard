#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/large-ios-source"
cp -R fixtures/demo-ios-repo "$fixture"

python3 - <<'PY' "$fixture/Sources/DemoShipGuardApp/LargeGeneratedLessonView.swift"
from pathlib import Path
import sys

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
body = [
    "import SwiftUI\n",
    "\n",
    "struct LargeGeneratedLessonView: View {\n",
    "    var body: some View {\n",
    "        TimelineView(.periodic(from: .now, by: 0.01)) { _ in\n",
    "            Text(\"Large lesson\")\n",
    "        }\n",
    "    }\n",
    "}\n",
    "\n",
]
body.extend([f"// generated curriculum paragraph {index}\n" for index in range(5000)])
path.write_text("".join(body), encoding="utf-8")
PY
cat > "$fixture/Sources/DemoShipGuardApp/SmallPerformanceSignal.swift" <<'SWIFT'
import SwiftUI

struct SmallPerformanceSignal: View {
    var body: some View {
        TimelineView(.periodic(from: .now, by: 0.01)) { _ in
            Text("Small signal")
        }
    }
}
SWIFT

export SHIPGUARD_IOS_SCAN_MAX_TEXT_BYTES=16384

./bin/shipguard ios doctor --path "$fixture" --out "$tmp_dir/doctor" >/dev/null
./bin/shipguard ios performance --path "$fixture" --out "$tmp_dir/performance" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios design --path "$fixture" --out "$tmp_dir/design" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios modernize --focus swift --path "$fixture" --out "$tmp_dir/modernize" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios launchdeck --path "$fixture" --out "$tmp_dir/launchdeck" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios app-intelligence --path "$fixture" --out "$tmp_dir/app-intelligence" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios ai-readiness --path "$fixture" --out "$tmp_dir/ai-readiness" --shipguard-eval --shareable >/dev/null

python3 - <<'PY' \
  "$tmp_dir/doctor/ios-doctor.json" \
  "$tmp_dir/performance/ios-performance.json" \
  "$tmp_dir/design/ios-design.json" \
  "$tmp_dir/modernize/ios-modernize.json" \
  "$tmp_dir/launchdeck/ios-launchdeck.json" \
  "$tmp_dir/app-intelligence/ios-app-intelligence.json" \
  "$tmp_dir/ai-readiness/ios-ai-readiness.json"
import json
import sys
from pathlib import Path

for raw in sys.argv[1:]:
    path = Path(raw)
    report = json.loads(path.read_text(encoding="utf-8"))
    scope = report.get("scanScope") or report.get("sourceSummary", {}).get("scanScope") or {}
    preview_scope = report.get("previewSignals", {}).get("scanScope") or {}
    if "textBytesPerFileLimit" not in scope and preview_scope:
        scope = preview_scope
    if scope.get("textBytesPerFileLimit") != 16384:
        raise SystemExit(f"{path.name} did not record the scan byte limit: {scope!r}")
    if scope.get("largeTextReadMode") != "omit-large-files":
        raise SystemExit(f"{path.name} did not record default large-file mode: {scope!r}")
    if scope.get("omittedLargeTextFileCount", 0) < 1:
        raise SystemExit(f"{path.name} did not record omitted large text files: {scope!r}")
    if not any("LargeGeneratedLessonView.swift" in item for item in scope.get("omittedLargeTextFiles", [])):
        raise SystemExit(f"{path.name} did not name the omitted large source file: {scope!r}")

performance = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if performance["metrics"].get("omittedLargeSwiftFiles", 0) < 1:
    raise SystemExit("performance metrics did not expose omittedLargeSwiftFiles")
if not any(item.get("ruleId") == "swiftui-periodic-timeline" for item in performance.get("findings", [])):
    raise SystemExit("bounded performance scan should still catch normal-sized source findings")

modernize = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
if modernize["summary"].get("omittedLargeSwiftFiles", 0) < 1:
    raise SystemExit("modernize summary did not expose omittedLargeSwiftFiles")

launchdeck = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
if launchdeck["previewSignals"].get("omittedLargeSwiftFiles", 0) < 1:
    raise SystemExit("launchdeck previewSignals did not expose omittedLargeSwiftFiles")

app_intelligence = json.loads(Path(sys.argv[6]).read_text(encoding="utf-8"))
if app_intelligence["summary"].get("omittedLargeSwiftFiles", 0) < 1:
    raise SystemExit("app-intelligence summary did not expose omittedLargeSwiftFiles")

ai_readiness = json.loads(Path(sys.argv[7]).read_text(encoding="utf-8"))
if ai_readiness["summary"].get("omittedLargeSourceFiles", 0) < 1:
    raise SystemExit("ai-readiness summary did not expose omittedLargeSourceFiles")
PY

python3 - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import ios_scan_scope  # noqa: E402

original_open = Path.open


def synthetic_timeout(self, *args, **kwargs):
    raise TimeoutError("synthetic read timeout")


Path.open = synthetic_timeout
try:
    result = ios_scan_scope.read_text_limited(Path("SyntheticSlowFile.swift"))
finally:
    Path.open = original_open

if not result.omitted or not result.timed_out:
    raise SystemExit(f"TimeoutError should be reported as an omitted timed-out text read: {result!r}")
PY

grep -q 'Truncated Swift files:' "$tmp_dir/performance/ios-performance.md"
grep -q 'large Swift files omitted:' "$tmp_dir/performance/ios-performance.md"
grep -q 'Large text files omitted from source scoring:' "$tmp_dir/design/ios-design.md"
grep -q 'Truncated Swift files:' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'large Swift files omitted:' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'Preview Swift files sampled:' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'large Swift files omitted:' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Truncated Swift files:' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'large Swift files omitted:' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Truncated source files:' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'large source files omitted:' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'Text files sampled:' "$tmp_dir/doctor/ios-doctor.md"

echo "ios scan-scope budget tests passed"
