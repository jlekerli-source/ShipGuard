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
grep -q '"schemaVersion": 1' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"generatedAt":' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"project": "<target-repo>"' "$tmp_dir/doctor/ios-doctor.json"
grep -q '"pathRedacted": true' "$tmp_dir/doctor/ios-doctor.json"
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

mkdir -p "$tmp_dir/package-only"
cat > "$tmp_dir/package-only/Package.swift" <<'SWIFT'
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "PackageOnlyFixture",
    platforms: [.iOS(.v17)],
    products: [.library(name: "PackageOnlyFixture", targets: ["PackageOnlyFixture"])],
    targets: [.target(name: "PackageOnlyFixture")]
)
SWIFT

./bin/shipguard ios doctor --path "$tmp_dir/package-only" --out "$tmp_dir/package-only-doctor" >/dev/null
python3 - "$tmp_dir/package-only-doctor/ios-doctor.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["schemaVersion"] == 1
assert report["schema_version"] == 1
assert report["generatedAt"].endswith("Z")
assert report["project"] == "<target-repo>"
assert report["target"]["pathRedacted"] is True
assert report["findings"], "expected package-only fixture findings"
for finding in report["findings"]:
    assert finding["ruleId"]
    assert finding["code"] == finding["ruleId"]
    assert finding["evidence"]
    assert finding["recommendation"]
    assert finding["proofGuidance"]
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/package-only-doctor" \
  --out "$tmp_dir/package-only-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-only-quality/ios-report-quality.json"
local_path_pattern="/""Users/"
if grep -q "$local_path_pattern" "$tmp_dir/package-only-doctor/ios-doctor.json" "$tmp_dir/package-only-doctor/ios-doctor.md"; then
  echo "ios doctor leaked an absolute local path" >&2
  exit 1
fi

echo "ios doctor tests passed"
