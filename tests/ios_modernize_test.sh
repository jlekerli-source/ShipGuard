#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ios modernize --help >/dev/null
./bin/codex-maintainer ios modernize \
  --focus swift \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/modernize" >/dev/null

test -f "$tmp_dir/modernize/ios-modernize.md"
test -f "$tmp_dir/modernize/ios-modernize.json"

python3 -m json.tool "$tmp_dir/modernize/ios-modernize.json" >/dev/null
grep -q '# iOS Swift Modernization Audit' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'Swift Concurrency' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'Accessibility And Localization' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'Availability And Fallbacks' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'Liquid Glass-specific styling' "$tmp_dir/modernize/ios-modernize.md"
grep -q 'DemoPermissions.swift' "$tmp_dir/modernize/ios-modernize.md"
grep -q '"tool": "codex-maintainer ios modernize"' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"focus": "swift"' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"ruleId": "swiftui-accessibility-copy"' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"ruleId": "swiftui-availability-fallbacks"' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"ruleId": "swift-concurrency-async-proof"' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"swiftVersions":' "$tmp_dir/modernize/ios-modernize.json"
grep -q '"6.0"' "$tmp_dir/modernize/ios-modernize.json"

json_stdout="$(./bin/codex-maintainer ios modernize --focus swift --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "codex-maintainer ios modernize"'

echo "ios modernize tests passed"
