#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out "$tmp_dir/doctor" >/dev/null
./bin/shipguard ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor "$tmp_dir/doctor/ios-doctor.json" \
  --out "$tmp_dir/inventory" >/dev/null

grep -q '## Target Risk Map' "$tmp_dir/inventory/ios-inventory.md"
grep -q '## Permission And Entitlement Review' "$tmp_dir/inventory/ios-inventory.md"
grep -q '## Unmapped Surfaces' "$tmp_dir/inventory/ios-inventory.md"
grep -q '## Modernization Opportunities' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'DemoShipGuardAppTests' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'Swift Concurrency' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'StoreKit `DemoProducts.storekit`' "$tmp_dir/inventory/ios-inventory.md"
grep -q 'privacy `PrivacyInfo.xcprivacy`' "$tmp_dir/inventory/ios-inventory.md"

python3 - "$tmp_dir/inventory/ios-inventory.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
assert report["schema_version"] == 2
assert report["doctor"]["source"].endswith("ios-doctor.json")
assert report["counts"]["targets"] == 3
assert report["counts"]["unmapped_surfaces"] == 0

targets = {target["id"]: target for target in report["targets"]}
app_targets = [target for target in targets.values() if target["kind"] == "app"]
test_targets = [target for target in targets.values() if target["kind"] == "test"]
package_targets = [target for target in targets.values() if target["kind"] == "package-target"]
assert len(app_targets) == 1
assert len(test_targets) == 1
assert len(package_targets) == 1

app = app_targets[0]
assert app["bundle_identifiers"] == ["dev.codexmaintainer.demo"]
assert app["deployment_targets"] == ["17.0"]
assert app["swift_versions"] == ["6.0"]
assert app["info_plists"] == ["Sources/DemoShipGuardApp/Info.plist"]
assert app["entitlements"] == ["Sources/DemoShipGuardApp/DemoShipGuardApp.entitlements"]
assert app["storekit_configs"] == ["DemoProducts.storekit"]
assert app["privacy_manifests"] == ["PrivacyInfo.xcprivacy"]
assert app["risk_counts"]["high"] == 1

location = next(surface for surface in report["surfaces"] if surface["surface"] == "Location")
assert location["status"] == "needs-user-answer"
assert location["risk"] == "high"
assert {owner["kind"] for owner in location["owners"]} == {"app", "package-target"}
assert any(owner["status"] == "single-app-target" for owner in location["owners"])

storekit = next(surface for surface in report["surfaces"] if surface["surface"] == "StoreKit")
assert storekit["status"] == "present"
assert any(item["file"] == "DemoProducts.storekit" for item in storekit["project_files"])
assert any(owner["kind"] == "app" and owner["status"] == "owned" for owner in storekit["owners"])

concurrency = next(surface for surface in report["surfaces"] if surface["surface"] == "Swift Concurrency")
assert any(owner["kind"] == "test" for owner in concurrency["owners"])
assert test_targets[0]["risk_counts"]["review"] == 1
PY

multi_target="$tmp_dir/multi-target"
mkdir -p "$multi_target/DemoMulti.xcodeproj" "$multi_target/App" "$multi_target/DemoAppTests"
cat >"$multi_target/DemoMulti.xcodeproj/project.pbxproj" <<'PBX'
// !$*UTF8*$!
{
  objects = {

/* Begin PBXNativeTarget section */
    A00000000000000000000001 /* DemoApp */ = {
      isa = PBXNativeTarget;
      buildConfigurationList = A00000000000000000000011 /* Build configuration list for PBXNativeTarget "DemoApp" */;
      name = DemoApp;
      productName = DemoApp;
      productType = "com.apple.product-type.application";
    };
    A00000000000000000000002 /* DemoAppTests */ = {
      isa = PBXNativeTarget;
      buildConfigurationList = A00000000000000000000012 /* Build configuration list for PBXNativeTarget "DemoAppTests" */;
      name = DemoAppTests;
      productName = DemoAppTests;
      productType = "com.apple.product-type.bundle.unit-test";
    };
/* End PBXNativeTarget section */

/* Begin XCConfigurationList section */
    A00000000000000000000011 /* Build configuration list for PBXNativeTarget "DemoApp" */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
        A00000000000000000000021 /* Debug */,
        A00000000000000000000022 /* Release */,
      );
    };
    A00000000000000000000012 /* Build configuration list for PBXNativeTarget "DemoAppTests" */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
        A00000000000000000000031 /* Debug */,
      );
    };
/* End XCConfigurationList section */

/* Begin XCBuildConfiguration section */
    A00000000000000000000021 /* Debug */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        CODE_SIGN_ENTITLEMENTS = App/App.entitlements;
        INFOPLIST_FILE = App/Info.plist;
        IPHONEOS_DEPLOYMENT_TARGET = 17.0;
        PRODUCT_BUNDLE_IDENTIFIER = dev.codexmaintainer.multi;
        SWIFT_VERSION = 6.0;
      };
      name = Debug;
    };
    A00000000000000000000022 /* Release */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        CODE_SIGN_ENTITLEMENTS = App/App.entitlements;
        INFOPLIST_FILE = App/Info.plist;
        IPHONEOS_DEPLOYMENT_TARGET = 17.0;
        PRODUCT_BUNDLE_IDENTIFIER = dev.codexmaintainer.multi;
        SWIFT_VERSION = 6.0;
      };
      name = Release;
    };
    A00000000000000000000031 /* Debug */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
        INFOPLIST_FILE = DemoAppTests/Info.plist;
        PRODUCT_BUNDLE_IDENTIFIER = dev.codexmaintainer.multi.tests;
        SWIFT_VERSION = 6.0;
      };
      name = Debug;
    };
/* End XCBuildConfiguration section */

  };
}
PBX
cat >"$multi_target/App/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>NSCameraUsageDescription</key><string>Camera proof.</string></dict></plist>
PLIST
cat >"$multi_target/App/App.entitlements" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>aps-environment</key><string>development</string></dict></plist>
PLIST
cat >"$multi_target/DemoAppTests/NotificationTests.swift" <<'SWIFT'
import UserNotifications

final class NotificationTests {
    func testNotificationReference() {
        _ = UNUserNotificationCenter.current()
    }
}
SWIFT

./bin/shipguard ios doctor --path "$multi_target" --out "$tmp_dir/multi-doctor" >/dev/null
./bin/shipguard ios inventory \
  --path "$multi_target" \
  --doctor "$tmp_dir/multi-doctor/ios-doctor.json" \
  --out "$tmp_dir/multi-inventory" >/dev/null

python3 - "$tmp_dir/multi-doctor/ios-doctor.json" "$tmp_dir/multi-inventory/ios-inventory.json" <<'PY'
import json
import sys
from pathlib import Path

doctor = json.loads(Path(sys.argv[1]).read_text())
inventory = json.loads(Path(sys.argv[2]).read_text())

targets = doctor["xcode_projects"][0]["target_details"]
app = next(target for target in targets if target["name"] == "DemoApp")
tests = next(target for target in targets if target["name"] == "DemoAppTests")
assert app["kind"] == "app"
assert app["info_plists"] == ["App/Info.plist"]
assert app["entitlements"] == ["App/App.entitlements"]
assert app["bundle_identifiers"] == ["dev.codexmaintainer.multi"]
assert tests["kind"] == "test"

notifications = next(surface for surface in inventory["surfaces"] if surface["surface"] == "Notifications")
assert notifications["owner_status"] == "unmapped"
assert notifications["owners"] == []
assert notifications["risk"] == "unmapped"
PY

custom_package="$tmp_dir/custom-package"
mkdir -p "$custom_package/CustomSpec"
cat >"$custom_package/Package.swift" <<'SWIFT'
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "CustomPackage",
    platforms: [.iOS(.v17)],
    targets: [
        .testTarget(name: "BehaviorSpec", path: "CustomSpec")
    ]
)
SWIFT
cat >"$custom_package/CustomSpec/BehaviorSpec.swift" <<'SWIFT'
final class BehaviorSpec {
    func verifiesAsyncMapping() async {
        await Task.yield()
    }
}
SWIFT

./bin/shipguard ios inventory --path "$custom_package" --out "$tmp_dir/custom-inventory" >/dev/null
python3 - "$tmp_dir/custom-inventory/ios-inventory.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
concurrency = next(surface for surface in report["surfaces"] if surface["surface"] == "Swift Concurrency")
assert any(owner["name"] == "BehaviorSpec" and owner["kind"] == "test" for owner in concurrency["owners"])
target = next(target for target in report["targets"] if target["name"] == "BehaviorSpec")
assert target["source_roots"] == ["CustomSpec"]
PY

echo "ios target risk map tests passed"
