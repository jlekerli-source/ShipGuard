#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

workflow=".github/workflows/autopsy-artifact.yml"
[[ -f "$workflow" ]] || {
  echo "missing autopsy artifact workflow" >&2
  exit 1
}

grep -q 'actions/upload-artifact@v4' "$workflow"
grep -q 'artifacts/autopsy-' "$workflow"
grep -q './bin/codex-maintainer autopsy' "$workflow"

./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out "$tmp_dir/artifacts/autopsy-good-run" >/dev/null

test -f "$tmp_dir/artifacts/autopsy-good-run/report.md"
test -f "$tmp_dir/artifacts/autopsy-good-run/report.json"
grep -q '"total": 11' "$tmp_dir/artifacts/autopsy-good-run/report.json"

echo "action artifact tests passed"
