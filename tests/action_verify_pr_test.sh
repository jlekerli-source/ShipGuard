#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

python3 -m py_compile scripts/action_verify_pr.py
./bin/shipguard action verify-pr --help >/dev/null

set +e
./bin/shipguard action verify-pr \
  --path . \
  --workflow examples/workflows/verify-pr.yml \
  --out "$tmp_dir/starter" \
  --shipguard-eval \
  --shareable >"$tmp_dir/starter.out"
starter_status=$?
set -e

if [[ "$starter_status" -ne 1 ]]; then
  echo "expected starter workflow to return review exit 1 before validation command is configured, got $starter_status" >&2
  exit 1
fi

grep -q '"status": "review"' "$tmp_dir/starter/action-verify-pr.json"
grep -q '"ruleId": "validation-command-placeholder"' "$tmp_dir/starter/action-verify-pr.json"
grep -q 'Runtime proof required: True' "$tmp_dir/starter/action-verify-pr.md"
grep -q 'read-only workflow text inspection; no target validation command executed' "$tmp_dir/starter/action-verify-pr.md"

./bin/shipguard action verify-pr \
  --path . \
  --workflow fixtures/action-verify-pr/configured.yml \
  --out "$tmp_dir/configured" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/configured/action-verify-pr.json"
grep -q '"placeholderValidationCommand": false' "$tmp_dir/configured/action-verify-pr.json"
grep -q 'gh run download <run-id> --name shipguard-verdict --dir /tmp/shipguard-verdict-artifact' "$tmp_dir/configured/action-verify-pr.md"
grep -q 'open a tiny PR, then download and inspect the uploaded shipguard-verdict artifact' "$tmp_dir/configured/action-verify-pr.md"

set +e
./bin/shipguard action verify-pr \
  --path . \
  --workflow fixtures/action-verify-pr/broken.yml \
  --out "$tmp_dir/broken" \
  --shareable >"$tmp_dir/broken.out"
broken_status=$?
set -e

if [[ "$broken_status" -ne 1 ]]; then
  echo "expected broken workflow to return blocked exit 1, got $broken_status" >&2
  exit 1
fi

grep -q '"status": "blocked"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "shipguard-install-step"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "verify-step"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "proof-artifact-upload"' "$tmp_dir/broken/action-verify-pr.json"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/configured/action-verify-pr.json" \
  --out "$tmp_dir/report-quality" \
  --shareable \
  --strict >/dev/null

grep -q '"status": "pass"' "$tmp_dir/report-quality/ios-report-quality.json"

echo "action verify-pr tests passed"
