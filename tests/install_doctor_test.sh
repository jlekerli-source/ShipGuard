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

echo "install doctor tests passed"
