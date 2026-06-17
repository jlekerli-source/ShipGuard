#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios app-intelligence --help >/dev/null
./bin/shipguard ios app-intelligence \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/app-intelligence" >/dev/null
./bin/shipguard ios app-intelligence \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/eval-app-intelligence" \
  --shipguard-eval >/dev/null

cap_fixture="$tmp_dir/cap-fixture"
mkdir -p "$cap_fixture/Sources/CapApp"
{
  printf 'import AppIntents\n\n'
  for index in $(seq 1 45); do
    printf 'struct BulkIntent%02d: AppIntent {\n' "$index"
    printf '  static var title: LocalizedStringResource = "Bulk %02d"\n' "$index"
    printf '  func perform() async throws -> some IntentResult { .result() }\n'
    printf '}\n\n'
  done
} > "$cap_fixture/Sources/CapApp/BulkIntents.swift"

./bin/shipguard ios app-intelligence \
  --path "$cap_fixture" \
  --out "$tmp_dir/cap-app-intelligence" >/dev/null

test -f "$tmp_dir/app-intelligence/ios-app-intelligence.md"
test -f "$tmp_dir/app-intelligence/ios-app-intelligence.json"
test -f "$tmp_dir/eval-app-intelligence/ios-app-intelligence.md"
test -f "$tmp_dir/eval-app-intelligence/ios-app-intelligence.json"
test -f "$tmp_dir/cap-app-intelligence/ios-app-intelligence.md"
test -f "$tmp_dir/cap-app-intelligence/ios-app-intelligence.json"

python3 -m json.tool "$tmp_dir/app-intelligence/ios-app-intelligence.json" >/dev/null
grep -q '# iOS App Intelligence Audit' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'DemoAlarmIntent' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'System Surface Opportunity Matrix' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Shortcuts' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Apple Intelligence' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'AppShortcutsProvider' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'No AppEntity' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Privacy Review' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q '"tool": "shipguard ios app-intelligence"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"intent": "app-development"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"intentCount": 1' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"entityCount": 0' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"surface": "Shortcuts"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"status": "partial"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"ruleId": "app-intent-missing-shortcuts-provider"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"ruleId": "app-intent-missing-entity-surface"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"proofGuidance":' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q 'Proof Guidance' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q '"DemoAlarmIntent"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/eval-app-intelligence/ios-app-intelligence.json"
grep -q '"shipguardOnly": true' "$tmp_dir/eval-app-intelligence/ios-app-intelligence.json"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/eval-app-intelligence/ios-app-intelligence.md"
grep -q 'Report Quality Questions' "$tmp_dir/eval-app-intelligence/ios-app-intelligence.md"
grep -q 'more type(s) hidden from Markdown' "$tmp_dir/cap-app-intelligence/ios-app-intelligence.md"
grep -q 'more candidate action(s) hidden from Markdown' "$tmp_dir/cap-app-intelligence/ios-app-intelligence.md"
grep -q '"BulkIntent45"' "$tmp_dir/cap-app-intelligence/ios-app-intelligence.json"
grep -q '"intentCount": 45' "$tmp_dir/cap-app-intelligence/ios-app-intelligence.json"

json_stdout="$(./bin/shipguard ios app-intelligence --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios app-intelligence"'
eval_json_stdout="$(./bin/shipguard ios app-intelligence --path fixtures/demo-ios-repo --shipguard-eval --json)"
printf '%s\n' "$eval_json_stdout" | grep -q '"intent": "shipguard-evaluation"'

echo "ios app intelligence tests passed"
