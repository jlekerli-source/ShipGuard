#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios prove --help >/dev/null
./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out "$tmp_dir/doctor" >/dev/null
./bin/shipguard ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor "$tmp_dir/doctor/ios-doctor.json" \
  --out "$tmp_dir/inventory" >/dev/null

./bin/shipguard ios plan \
  --mode permission-audit \
  --inventory "$tmp_dir/inventory/ios-inventory.json" \
  --out "$tmp_dir/permission-plan.md" >/dev/null

./bin/shipguard ios prove \
  --plan "$tmp_dir/permission-plan.json" \
  --out "$tmp_dir/permission-proof" >/dev/null

test -f "$tmp_dir/permission-proof/ios-proof.json"
test -f "$tmp_dir/permission-proof/ios-proof.md"
grep -q '"tool": "shipguard ios prove"' "$tmp_dir/permission-proof/ios-proof.json"
grep -q '"status": "blocked-manual"' "$tmp_dir/permission-proof/ios-proof.json"
grep -q 'blocked questions' "$tmp_dir/permission-proof/ios-proof.md"
grep -q 'simulator permission-state walkthrough' "$tmp_dir/permission-proof/ios-proof.md"

./bin/shipguard ios plan \
  --mode release-proof \
  --inventory "$tmp_dir/inventory/ios-inventory.json" \
  --out "$tmp_dir/release-plan" >/dev/null
./bin/shipguard ios prove \
  --plan "$tmp_dir/release-plan/ios-plan.json" \
  --out "$tmp_dir/release-proof" >/dev/null

grep -q '"planMode": "release-proof"' "$tmp_dir/release-proof/ios-proof.json"
grep -q 'App Store Connect' "$tmp_dir/release-proof/ios-proof.md"
grep -q 'Do not claim App Store, TestFlight, purchase, physical-device, or release proof without named evidence.' "$tmp_dir/release-proof/ios-proof.md"

json_stdout="$(./bin/shipguard ios prove --plan "$tmp_dir/release-plan/ios-plan.json" --out "$tmp_dir/release-proof-json" --json)"
printf '%s\n' "$json_stdout" | grep -q '"status": "blocked-manual"'

echo "ios prove tests passed"
