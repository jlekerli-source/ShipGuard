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
grep -q '"scanScope"' "$tmp_dir/performance/ios-performance.json"
grep -q '"release-artifacts"' "$tmp_dir/performance/ios-performance.json"
grep -q 'Scan Scope' "$tmp_dir/performance/ios-performance.md"
grep -q 'release-artifacts' "$tmp_dir/performance/ios-performance.md"
if grep -q 'GeneratedPerformanceNoise.swift' "$tmp_dir/performance/ios-performance.json"; then
  echo "ios performance should skip generated proof artifacts" >&2
  exit 1
fi
grep -q 'physical-device smoothness' "$tmp_dir/performance/ios-performance.md"
grep -q 'Animation Hitches' "$tmp_dir/performance/ios-performance.md"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/eval-performance/ios-performance.json"
grep -q '"shipguardOnly": true' "$tmp_dir/eval-performance/ios-performance.json"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/eval-performance/ios-performance.md"
grep -q 'Do not edit the scanned app' "$tmp_dir/eval-performance/ios-performance.md"
grep -q 'Report Quality Questions' "$tmp_dir/eval-performance/ios-performance.md"
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
