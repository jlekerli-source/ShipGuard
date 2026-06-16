#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer policy show >/dev/null
./bin/codex-maintainer policy init "$tmp_dir/policy.conf" >/dev/null
test -f "$tmp_dir/policy.conf"
grep -q '^max_changed_files=3$' "$tmp_dir/policy.conf"

if ./bin/codex-maintainer policy init "$tmp_dir/policy.conf" >/dev/null 2>&1; then
  echo "expected policy init to reject existing file without --force" >&2
  exit 1
fi

./bin/codex-maintainer policy init "$tmp_dir/policy.conf" --force >/dev/null

./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/weak-run/run.md \
  --task fixtures/autopsy/weak-run/task.md \
  --diff fixtures/autopsy/weak-run/diff.patch \
  --policy fixtures/policy/strict.conf \
  --out "$tmp_dir/policy-autopsy" >/dev/null

grep -q '"policy": "fixtures/policy/strict.conf"' "$tmp_dir/policy-autopsy/report.json"
grep -q '"max_changed_files": 0' "$tmp_dir/policy-autopsy/report.json"
grep -q 'scope_creep_signal' "$tmp_dir/policy-autopsy/report.json"
grep -q 'protected_area_touch' "$tmp_dir/policy-autopsy/report.json"
grep -q 'limit 0' "$tmp_dir/policy-autopsy/report.json"

echo "policy tests passed"
