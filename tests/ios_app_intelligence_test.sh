#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ios app-intelligence --help >/dev/null
./bin/codex-maintainer ios app-intelligence \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/app-intelligence" >/dev/null

test -f "$tmp_dir/app-intelligence/ios-app-intelligence.md"
test -f "$tmp_dir/app-intelligence/ios-app-intelligence.json"

python3 -m json.tool "$tmp_dir/app-intelligence/ios-app-intelligence.json" >/dev/null
grep -q '# iOS App Intelligence Audit' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'DemoAlarmIntent' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'System Surface Opportunity Matrix' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Shortcuts' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Apple Intelligence' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'AppShortcutsProvider' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'No AppEntity' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q 'Privacy Review' "$tmp_dir/app-intelligence/ios-app-intelligence.md"
grep -q '"tool": "codex-maintainer ios app-intelligence"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"intentCount": 1' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"entityCount": 0' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"surface": "Shortcuts"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"status": "partial"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"ruleId": "app-intent-missing-shortcuts-provider"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"ruleId": "app-intent-missing-entity-surface"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"
grep -q '"DemoAlarmIntent"' "$tmp_dir/app-intelligence/ios-app-intelligence.json"

json_stdout="$(./bin/codex-maintainer ios app-intelligence --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "codex-maintainer ios app-intelligence"'

echo "ios app intelligence tests passed"
