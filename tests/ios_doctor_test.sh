#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios doctor --help >/dev/null
./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out "$tmp_dir/doctor" >/dev/null

test -f "$tmp_dir/doctor/ios-doctor.md"
test -f "$tmp_dir/doctor/ios-doctor.json"

python3 -m json.tool "$tmp_dir/doctor/ios-doctor.json" >/dev/null
grep -q '# iOS Doctor' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'DemoShipGuardApp.xcodeproj' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'DemoShipGuardApp.xcworkspace' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'DemoShipGuardApp.xctestplan' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'DemoProducts.storekit' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'PrivacyInfo.xcprivacy' "$tmp_dir/doctor/ios-doctor.md"
grep -q '`17.0`' "$tmp_dir/doctor/ios-doctor.md"
grep -q '`6.0`' "$tmp_dir/doctor/ios-doctor.md"
grep -q 'Use XcodeBuildMCP session defaults' "$tmp_dir/doctor/ios-doctor.md"

grep -q '"tool": "shipguard ios doctor"' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"xcode_projects": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"xcode_workspaces": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"swift_packages": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"storekit_configs": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"privacy_manifests": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"swift_versions":' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"6.0"' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"target_details":' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"kind": "app"' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"DemoShipGuardAppTests"' "$tmp_dir/doctor/ios-doctor.json"

json_stdout="$(./bin/shipguard ios doctor --path fixtures/demo-ios-repo --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios doctor"'

echo "ios doctor tests passed"
