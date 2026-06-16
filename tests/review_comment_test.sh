#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

good_autopsy="$tmp_dir/good-autopsy"
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out "$good_autopsy" >/dev/null

./bin/codex-maintainer review-comment \
  --report "$good_autopsy/report.json" \
  --out "$tmp_dir/good-comment.md" \
  --badge "$tmp_dir/good-badge.json" \
  --artifact-dir "$tmp_dir/good-bundle" \
  --mode warn >/dev/null

grep -q '| Status | pass |' "$tmp_dir/good-comment.md"
grep -q '"message": "pass 11/12"' "$tmp_dir/good-badge.json"
grep -q '"color": "brightgreen"' "$tmp_dir/good-badge.json"
test -f "$tmp_dir/good-bundle/report.json"
test -f "$tmp_dir/good-bundle/report.md"
test -f "$tmp_dir/good-bundle/comment.md"
test -f "$tmp_dir/good-bundle/badge.json"

dangerous_autopsy="$tmp_dir/dangerous-autopsy"
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out "$dangerous_autopsy" >/dev/null

./bin/codex-maintainer review-comment \
  --report "$dangerous_autopsy/report.json" \
  --out "$tmp_dir/dangerous-comment.md" \
  --badge "$tmp_dir/dangerous-badge.json" \
  --artifact-dir "$tmp_dir/dangerous-bundle" \
  --mode warn >/dev/null

grep -q '| Status | blocked |' "$tmp_dir/dangerous-comment.md"
grep -q '| High-risk findings | 3 |' "$tmp_dir/dangerous-comment.md"
grep -q '"message": "blocked 1/12"' "$tmp_dir/dangerous-badge.json"
grep -q '"color": "red"' "$tmp_dir/dangerous-badge.json"
test -f "$tmp_dir/dangerous-bundle/report.json"
test -f "$tmp_dir/dangerous-bundle/report.md"
test -f "$tmp_dir/dangerous-bundle/comment.md"
test -f "$tmp_dir/dangerous-bundle/badge.json"

if ./bin/codex-maintainer review-comment \
  --report "$dangerous_autopsy/report.json" \
  --out "$tmp_dir/dangerous-fail-comment.md" \
  --mode fail >/dev/null 2>&1; then
  echo "expected dangerous report to fail in fail mode" >&2
  exit 1
fi

echo "review comment tests passed"
