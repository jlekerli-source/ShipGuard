#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/demo-ios-design"
cp -R fixtures/demo-ios-repo "$fixture"
cat > "$fixture/Sources/DemoShipGuardApp/DemoDesignSurface.swift" <<'SWIFT'
import SwiftUI

struct DemoDesignSurface: View {
    @State private var expanded = false

    var body: some View {
        NavigationStack {
            VStack {
                Text("Focus Mode")
                Button("Start Game") {
                    withAnimation(.spring(response: 0.45, dampingFraction: 0.7).repeatForever()) {
                        expanded.toggle()
                    }
                }
                RoundedRectangle(cornerRadius: 24)
                    .fill(.blue.gradient)
                    .shadow(color: .blue.opacity(0.35), radius: 18)
                    .blur(radius: expanded ? 4 : 0)
            }
            .navigationTitle("Dashboard")
        }
    }
}
SWIFT
mkdir -p "$fixture/release-artifacts/noisy-proof"
cat > "$fixture/release-artifacts/noisy-proof/GeneratedDesignNoise.swift" <<'SWIFT'
import SwiftUI

struct GeneratedDesignNoise: View {
    var body: some View {
        Text("This generated proof file should not affect app-type or design findings")
            .onAppear {
                withAnimation(.linear.repeatForever()) {}
            }
    }
}
SWIFT

preview_out="$tmp_dir/preview"
mkdir -p "$preview_out"
cat > "$preview_out/session.json" <<'JSON'
{
  "captureMode": "fixture",
  "previewUrl": "http://127.0.0.1:8765"
}
JSON
cat > "$preview_out/handoff.json" <<'JSON'
{
  "targetResolution": {
    "status": "needs-element-ref"
  }
}
JSON
cat > "$preview_out/preview-events.jsonl" <<'JSONL'
{"type":"visual-fix","source":"preview-context-menu","note":"Make this screen calmer"}
JSONL
printf 'fixture image bytes\n' > "$preview_out/last-screenshot.png"

./bin/shipguard ios design --help >/dev/null
./bin/shipguard ios design \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/design" >/dev/null
./bin/shipguard ios design \
  --path "$fixture" \
  --out "$tmp_dir/game-design" \
  --app-type game \
  --preview-out "$preview_out" \
  --icon-brief \
  --shipguard-eval >/dev/null

test -f "$tmp_dir/design/ios-design.md"
test -f "$tmp_dir/design/ios-design.json"
test -f "$tmp_dir/game-design/ios-design.md"
test -f "$tmp_dir/game-design/ios-design.json"
test -f "$tmp_dir/game-design/app-icon-imagegen-brief.md"

python3 -m json.tool "$tmp_dir/design/ios-design.json" >/dev/null
python3 -m json.tool "$tmp_dir/game-design/ios-design.json" >/dev/null
grep -q '# iOS Design QA Audit' "$tmp_dir/design/ios-design.md"
grep -q 'Design DNA' "$tmp_dir/design/ios-design.md"
grep -q 'Motion Blueprint' "$tmp_dir/design/ios-design.md"
grep -q 'Haptics Blueprint' "$tmp_dir/design/ios-design.md"
grep -q 'Preview And Devspace' "$tmp_dir/design/ios-design.md"
grep -q 'shipguard ios preview' "$tmp_dir/design/ios-design.md"
grep -q 'shipguard ios devspace' "$tmp_dir/design/ios-design.md"
grep -q '"tool": "shipguard ios design"' "$tmp_dir/design/ios-design.json"
grep -q '"intent": "app-development"' "$tmp_dir/design/ios-design.json"
grep -q '"value": "utility"' "$tmp_dir/design/ios-design.json"
grep -q '"ruleId": "preview-proof-not-provided"' "$tmp_dir/design/ios-design.json"
grep -q '"ruleId": "motion-reduced-motion-gate"' "$tmp_dir/design/ios-design.json"

grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/game-design/ios-design.json"
grep -q '"shipguardOnly": true' "$tmp_dir/game-design/ios-design.json"
grep -q '"value": "game"' "$tmp_dir/game-design/ios-design.json"
grep -q '"override": "game"' "$tmp_dir/game-design/ios-design.json"
grep -q '"status": "provided"' "$tmp_dir/game-design/ios-design.json"
grep -q '"eventCount": 1' "$tmp_dir/game-design/ios-design.json"
grep -q '"scanScope"' "$tmp_dir/game-design/ios-design.json"
grep -q '"release-artifacts"' "$tmp_dir/game-design/ios-design.json"
grep -q 'Scan-scope exclusions' "$tmp_dir/game-design/ios-design.md"
grep -q 'release-artifacts' "$tmp_dir/game-design/ios-design.md"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/game-design/ios-design.md"
grep -q 'Report Quality Questions' "$tmp_dir/game-design/ios-design.md"
grep -q 'App Icon ImageGen Brief' "$tmp_dir/game-design/ios-design.md"
grep -q 'ChatGPT ImageGen' "$tmp_dir/game-design/app-icon-imagegen-brief.md"
grep -q 'ShipGuard does not create CSS or SVG icon art' "$tmp_dir/game-design/app-icon-imagegen-brief.md"
if find "$tmp_dir/game-design" \( -name '*.svg' -o -name '*.css' \) | grep -q .; then
  echo "ios design should not create CSS or SVG icon art" >&2
  exit 1
fi

json_stdout="$(./bin/shipguard ios design --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios design"'
eval_json_stdout="$(./bin/shipguard ios design --path fixtures/demo-ios-repo --shipguard-eval --json)"
printf '%s\n' "$eval_json_stdout" | grep -q '"intent": "shipguard-evaluation"'

echo "ios design tests passed"
