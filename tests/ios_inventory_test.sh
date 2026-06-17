#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios inventory --help >/dev/null
./bin/shipguard ios inventory --path fixtures/demo-ios-repo --out "$tmp_dir/inventory" >/dev/null

test -f "$tmp_dir/inventory/ios-inventory.md"
test -f "$tmp_dir/inventory/ios-inventory.json"

python3 -m json.tool "$tmp_dir/inventory/ios-inventory.json" >/dev/null
grep -q '# iOS Permission And Runtime Inventory' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Target Risk Map' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Notifications' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Location | needs-user-answer' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'DemoShipGuardAppTests' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Modernization Opportunities' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Codex Workflow Prompts' "$tmp_dir/inventory/ios-inventory.md"
grep -q '"targets": 3' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"owner_status": "owned"' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"surface": "Location"' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"status": "needs-user-answer"' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"surface": "StoreKit"' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"surface": "App Intents"' "$tmp_dir/inventory/ios-inventory.json"
grep -q '"surface": "Swift Concurrency"' "$tmp_dir/inventory/ios-inventory.json"

json_stdout="$(./bin/shipguard ios inventory --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios inventory"'

echo "ios inventory tests passed"
