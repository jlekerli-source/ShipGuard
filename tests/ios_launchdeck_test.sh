#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/demo-ios-launchdeck"
cp -R fixtures/demo-ios-repo "$fixture"
mkdir -p "$fixture/release-artifacts/noisy-build-proof"
printf 'generated proof should be skipped\n' > "$fixture/release-artifacts/noisy-build-proof/Build.log"

./bin/shipguard ios launchdeck --help >/dev/null
./bin/shipguard ios launchdeck \
  --path "$fixture" \
  --out "$tmp_dir/launchdeck" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/launchdeck/ios-launchdeck.md"
test -f "$tmp_dir/launchdeck/ios-launchdeck.json"

python3 -m json.tool "$tmp_dir/launchdeck/ios-launchdeck.json" >/dev/null
grep -q '# ShipGuard LaunchDeck' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'LaunchDeck Console' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Harbor Check' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Glass Deck' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Hot-Swap Dock' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Trace Radar' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'XcodeBuildMCP Build/Run' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Simulator Browser' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'SwiftUI Preview Hot Reload' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Performance Profiling' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Execution Receipts' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'serve-sim' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'swiftui-preview-browser.mjs' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Animation Hitches' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Report Quality Questions' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'Scan Scope' "$tmp_dir/launchdeck/ios-launchdeck.md"
grep -q 'release-artifacts' "$tmp_dir/launchdeck/ios-launchdeck.md"

grep -q '"tool": "shipguard ios launchdeck"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"mode": "shareable"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"surface": "ShipGuard LaunchDeck"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"codename": "launchdeck"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"integration": "native-shipguard-launch-control"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"Harbor Check"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"xcodeBuildMCP"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"simulatorBrowser"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"swiftUIPreviewHotReload"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"performanceProfiling"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"scheme": "<private-app>"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"workspacePath": "<private-app>.xcworkspace"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"projectPath": "<private-app>.xcodeproj"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"preferredXcodeSelector": "workspace"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"recommendedWorkflow": "xcodebuildmcp-build-run"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"executionReceipts"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"receiptQuality"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"status": "not-provided"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"status": "not-assessed"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q 'launchdeck-execution-receipts-not-provided' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"shipguardOnly": true' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"scanScope"' "$tmp_dir/launchdeck/ios-launchdeck.json"
grep -q '"release-artifacts"' "$tmp_dir/launchdeck/ios-launchdeck.json"

if grep -R -F -q "$tmp_dir" "$tmp_dir/launchdeck"; then
  echo "shareable ios launchdeck output must not include local absolute fixture paths" >&2
  exit 1
fi
if grep -R -q 'DemoShipGuardApp' "$tmp_dir/launchdeck"; then
  echo "shareable ios launchdeck output must redact target identifiers" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/launchdeck" \
  --out "$tmp_dir/launchdeck-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/launchdeck-quality/ios-report-quality.json"
if grep -q 'local-path-shareability-warning' "$tmp_dir/launchdeck-quality/ios-report-quality.json"; then
  echo "shareable ios launchdeck output should not trigger local-path shareability warnings" >&2
  exit 1
fi

json_stdout="$(./bin/shipguard ios launchdeck --path fixtures/demo-ios-repo --workflow preview --shareable --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios launchdeck"'
printf '%s\n' "$json_stdout" | grep -q '"requestedWorkflow": "preview"'
printf '%s\n' "$json_stdout" | grep -q '"recommendedWorkflow": "swiftui-preview-hot-reload"'

receipt_dir="$tmp_dir/good-receipts"
mkdir -p "$receipt_dir"
cat > "$receipt_dir/build.log" <<'EOF'
session_show_defaults
session_set_defaults with workspace=DemoShipGuardApp.xcworkspace, scheme=DemoShipGuardApp, simulator=Booted
build_run_sim
** BUILD SUCCEEDED **
Launching DemoShipGuardApp
EOF
cat > "$receipt_dir/describe-ui.json" <<'EOF'
{"elements":[{"elementRef":"button.start","label":"Start"}]}
EOF
cat > "$receipt_dir/serve-sim.log" <<'EOF'
npx --yes serve-sim@latest ABCD-1234
preview URL http://127.0.0.1:8765
EOF
cat > "$receipt_dir/preview.log" <<'EOF'
node swiftui-preview-browser.mjs Package.swift --package-target DemoShipGuardApp --device ABCD-1234
hot reloaded package preview DemoPreview in pid 123
EOF
cat > "$receipt_dir/trace.log" <<'EOF'
xctrace record --template 'Animation Hitches'
Time Profiler and Animation Hitches summaries preserved.
EOF
printf 'png proof\n' > "$receipt_dir/screenshot.png"

./bin/shipguard ios launchdeck \
  --path "$fixture" \
  --workflow performance \
  --receipt "$receipt_dir" \
  --out "$tmp_dir/launchdeck-receipts" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"status": "provided"' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"receiptQuality"' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"status": "pass"' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"buildRunProof": true' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"performanceProof": true' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"simulatorBrowserProof": true' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"swiftuiPreviewProof": true' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q '"uiProof": true' "$tmp_dir/launchdeck-receipts/ios-launchdeck.json"
grep -q 'Execution Receipts' "$tmp_dir/launchdeck-receipts/ios-launchdeck.md"
grep -q 'build_run_sim' "$tmp_dir/launchdeck-receipts/ios-launchdeck.md"
grep -q 'Animation Hitches' "$tmp_dir/launchdeck-receipts/ios-launchdeck.md"
grep -q 'serve-sim' "$tmp_dir/launchdeck-receipts/ios-launchdeck.md"
if grep -R -F -q "$tmp_dir" "$tmp_dir/launchdeck-receipts"; then
  echo "shareable receipt output must not include local absolute receipt paths" >&2
  exit 1
fi
if grep -R -q 'DemoShipGuardApp' "$tmp_dir/launchdeck-receipts"; then
  echo "shareable receipt output must redact target identifiers" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/launchdeck-receipts" \
  --out "$tmp_dir/launchdeck-receipts-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/launchdeck-receipts-quality/ios-report-quality.json"

weak_receipt_dir="$tmp_dir/weak-receipts"
mkdir -p "$weak_receipt_dir"
printf 'notes only, no execution proof\n' > "$weak_receipt_dir/notes.txt"
./bin/shipguard ios launchdeck \
  --path "$fixture" \
  --workflow performance \
  --receipt "$weak_receipt_dir" \
  --out "$tmp_dir/launchdeck-weak-receipts" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/launchdeck-weak-receipts/ios-launchdeck.json"
grep -q 'launchdeck-build-run-receipt-missing' "$tmp_dir/launchdeck-weak-receipts/ios-launchdeck.json"
grep -q 'launchdeck-performance-receipt-missing' "$tmp_dir/launchdeck-weak-receipts/ios-launchdeck.json"
grep -q 'Collect the missing execution receipts' "$tmp_dir/launchdeck-weak-receipts/ios-launchdeck.md"

echo "ios launchdeck tests passed"
