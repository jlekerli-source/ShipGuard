#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/demo-ios-ai"
cp -R fixtures/demo-ios-repo "$fixture"
cat > "$fixture/Sources/DemoShipGuardApp/DemoAI.swift" <<'SWIFT'
import CoreML
import FoundationModels
import SwiftUI

struct DemoAI {
    func summarize(_ text: String) async throws -> String {
        let session = LanguageModelSession(model: SystemLanguageModel.default)
        _ = MLModel.self
        let endpoint = URL(string: "https://api.openai.com/v1/responses")!
        return "\(session) \(endpoint) \(text)"
    }
}
SWIFT
touch "$fixture/Sources/DemoShipGuardApp/DemoClassifier.mlmodel"

./bin/shipguard ios ai-readiness --help >/dev/null
./bin/shipguard ios ai-readiness \
  --path "$fixture" \
  --out "$tmp_dir/ai-readiness" >/dev/null

test -f "$tmp_dir/ai-readiness/ios-ai-readiness.md"
test -f "$tmp_dir/ai-readiness/ios-ai-readiness.json"

python3 -m json.tool "$tmp_dir/ai-readiness/ios-ai-readiness.json" >/dev/null
grep -q '# iOS AI Readiness Audit' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'On-Device Versus Cloud Decision Matrix' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'Foundation Models' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'Core ML' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'OpenAI API' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'server-side API key handling' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q 'DemoAI.swift' "$tmp_dir/ai-readiness/ios-ai-readiness.md"
grep -q '"tool": "shipguard ios ai-readiness"' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"foundationModels":' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"openAIAPI":' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"ruleId": "openai-api-cloud-privacy-gate"' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"ruleId": "foundation-models-availability-gate"' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"ruleId": "core-ml-performance-gate"' "$tmp_dir/ai-readiness/ios-ai-readiness.json"
grep -q '"option": "No AI"' "$tmp_dir/ai-readiness/ios-ai-readiness.json"

json_stdout="$(./bin/shipguard ios ai-readiness --path "$fixture" --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios ai-readiness"'

echo "ios ai readiness tests passed"
