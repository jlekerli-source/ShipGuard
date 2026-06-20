#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

install_prefix="$tmp_dir/install"
install_output="$(PREFIX="$install_prefix" ./scripts/install.sh)"
printf '%s\n' "$install_output" | grep -q "installed shipguard to $install_prefix/bin/shipguard"
printf '%s\n' "$install_output" | grep -q "installed toolkit files to $install_prefix/lib/shipguard"
printf '%s\n' "$install_output" | grep -q '# ShipGuard Install Receipt'
printf '%s\n' "$install_output" | grep -q 'Status: pass'
printf '%s\n' "$install_output" | grep -q "PATH hint: export PATH=\"$install_prefix/bin:"
printf '%s\n' "$install_output" | grep -q "Next action: run \"$install_prefix/bin/shipguard\" validate"
printf '%s\n' "$install_output" | grep -q -- "- \"$install_prefix/bin/shipguard\" prepare"
printf '%s\n' "$install_output" | grep -q -- "- \"$install_prefix/bin/shipguard\" verify"

test "$("$install_prefix/bin/shipguard" version)" = "$(./bin/shipguard version)"
"$install_prefix/bin/shipguard" doctor --help >/dev/null
"$install_prefix/bin/shipguard" validate >/dev/null

"$install_prefix/bin/shipguard" init ios "$tmp_dir/ios-app" >/dev/null
doctor_output="$("$install_prefix/bin/shipguard" doctor ios "$tmp_dir/ios-app")"
printf '%s\n' "$doctor_output" | grep -q '# ShipGuard RepoVitals'
printf '%s\n' "$doctor_output" | grep -q 'Profile: ios'
printf '%s\n' "$doctor_output" | grep -q 'Status: pass'
printf '%s\n' "$doctor_output" | grep -q 'Required files: 10/10'
printf '%s\n' "$doctor_output" | grep -q 'doctor passed for ios'

set +e
missing_output="$("$install_prefix/bin/shipguard" doctor web "$tmp_dir/missing-web" 2>&1)"
missing_status=$?
set -e
if [[ "$missing_status" -eq 0 ]]; then
  echo "expected doctor to fail for missing target workflow files" >&2
  exit 1
fi
printf '%s\n' "$missing_output" | grep -q 'Status: missing'
printf '%s\n' "$missing_output" | grep -q 'Required files: 0/10'
printf '%s\n' "$missing_output" | grep -q 'Next action: run shipguard init web'

"$install_prefix/bin/shipguard" prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/task" \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable >/dev/null
"$install_prefix/bin/shipguard" verify \
  --task "$tmp_dir/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out "$tmp_dir/verdict" >"$tmp_dir/verify.out"
grep -q 'ShipGuard Proof Report: pass. Validation 1/1 covered; claims 1/1 accepted;' "$tmp_dir/verify.out"
grep -q 'Status: `pass`' "$tmp_dir/verdict/shipguard-verdict.md"
python3 - <<'PY' "$tmp_dir/verdict/shipguard-verdict.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
proof = data.get("proofReport") or {}
assert data.get("status") == "pass", data
assert proof.get("mergeAllowed") is True, proof
assert proof.get("validation", {}).get("label") == "1/1 covered", proof
assert proof.get("claims", {}).get("label") == "1/1 accepted", proof
PY

echo "install doctor tests passed"
