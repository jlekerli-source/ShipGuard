#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ios plan --help >/dev/null
./bin/codex-maintainer ios doctor --path fixtures/demo-ios-repo --out "$tmp_dir/doctor" >/dev/null
./bin/codex-maintainer ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor "$tmp_dir/doctor/ios-doctor.json" \
  --out "$tmp_dir/inventory" >/dev/null

./bin/codex-maintainer ios plan \
  --mode permission-audit \
  --inventory "$tmp_dir/inventory/ios-inventory.json" \
  --out "$tmp_dir/plan/ios-plan.md" >/dev/null

test -f "$tmp_dir/plan/ios-plan.md"
test -f "$tmp_dir/plan/ios-plan.json"
grep -q '"tool": "codex-maintainer ios plan"' "$tmp_dir/plan/ios-plan.json"
grep -q '"mode": "permission-audit"' "$tmp_dir/plan/ios-plan.json"
grep -q '"status": "needs-user-answer"' "$tmp_dir/plan/ios-plan.json"
grep -q 'What user-visible feature justifies location access' "$tmp_dir/plan/ios-plan.md"
grep -q 'Sources/DemoCodexMaintainerApp/DemoPermissions.swift' "$tmp_dir/plan/ios-plan.md"
grep -q 'source-plus-simulator' "$tmp_dir/plan/ios-plan.md"
grep -q 'Do not claim release, purchase, device, App Store, or preview proof without the required evidence.' "$tmp_dir/plan/ios-plan.md"
if grep -q 'Tests/DemoCodexMaintainerAppTests' "$tmp_dir/plan/ios-plan.md"; then
  echo "permission plan should not route to the test target owner files" >&2
  exit 1
fi

json_stdout="$(./bin/codex-maintainer ios plan \
  --inventory "$tmp_dir/inventory/ios-inventory.json" \
  --out "$tmp_dir/auto-plan" \
  --json)"
printf '%s\n' "$json_stdout" | grep -q '"mode": "permission-audit"'
test -f "$tmp_dir/auto-plan/ios-plan.md"
test -f "$tmp_dir/auto-plan/ios-plan.json"

echo "ios plan tests passed"
