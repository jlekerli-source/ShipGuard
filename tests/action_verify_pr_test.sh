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
grep -q 'shipguard action verify-pr --workflow .github/workflows/shipguard-verify-pr.yml --artifact-dir /tmp/shipguard-verdict-artifact' "$tmp_dir/configured/action-verify-pr.md"
grep -q 'open a tiny PR, then download and inspect the uploaded shipguard-verdict artifact' "$tmp_dir/configured/action-verify-pr.md"

./bin/shipguard action verify-pr \
  --path . \
  --workflow fixtures/action-verify-pr/configured.yml \
  --artifact-dir fixtures/action-verify-pr/runtime-artifact \
  --out "$tmp_dir/runtime" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"status": "pass"' "$tmp_dir/runtime/action-verify-pr.json"
grep -q '"runtimeArtifactProvided": true' "$tmp_dir/runtime/action-verify-pr.json"
grep -q '"verdictStatus": "pass"' "$tmp_dir/runtime/action-verify-pr.json"
grep -q '"freshMaintainerFailureGuide":' "$tmp_dir/runtime/action-verify-pr.json"
grep -q '"ruleId": "runtime-verdict-tool"' "$tmp_dir/runtime/action-verify-pr.json"
grep -q 'Runtime Artifact' "$tmp_dir/runtime/action-verify-pr.md"
grep -q 'Fresh Maintainer Failure Guide' "$tmp_dir/runtime/action-verify-pr.md"
grep -q 'shipguard action verify-pr --workflow .github/workflows/shipguard-verify-pr.yml --artifact-dir /tmp/shipguard-verdict-artifact' "$tmp_dir/runtime/action-verify-pr.md"

set +e
./bin/shipguard action verify-pr \
  --path . \
  --workflow fixtures/action-verify-pr/configured.yml \
  --artifact-dir fixtures/action-verify-pr/runtime-broken \
  --out "$tmp_dir/runtime-broken" \
  --shareable >"$tmp_dir/runtime-broken.out"
runtime_broken_status=$?
set -e

if [[ "$runtime_broken_status" -ne 1 ]]; then
  echo "expected broken runtime artifact to return blocked exit 1, got $runtime_broken_status" >&2
  exit 1
fi

grep -q '"status": "blocked"' "$tmp_dir/runtime-broken/action-verify-pr.json"
grep -q '"firstBlockingRuleId": "runtime-verdict-tool"' "$tmp_dir/runtime-broken/action-verify-pr.json"
grep -q '"ruleId": "runtime-verdict-tool"' "$tmp_dir/runtime-broken/action-verify-pr.json"
grep -q '"ruleId": "runtime-proof-report"' "$tmp_dir/runtime-broken/action-verify-pr.json"
grep -q '"ruleId": "runtime-evidence-receipt-schema"' "$tmp_dir/runtime-broken/action-verify-pr.json"
grep -q 'Markdown verdict not found beside JSON: fixtures/action-verify-pr/runtime-broken/shipguard-verdict.md' "$tmp_dir/runtime-broken/action-verify-pr.json"
if grep -R -q '/Users/' "$tmp_dir/runtime-broken"; then
  echo "shareable broken runtime verify-pr report leaked a local absolute path" >&2
  exit 1
fi

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
grep -q '"firstBlockingRuleId": "shipguard-install-step"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "shipguard-install-step"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "verify-step"' "$tmp_dir/broken/action-verify-pr.json"
grep -q '"ruleId": "proof-artifact-upload"' "$tmp_dir/broken/action-verify-pr.json"
grep -q 'Next action: Install ShipGuard before prepare/verify' "$tmp_dir/broken/action-verify-pr.md"
grep -q 'Fresh Maintainer Failure Guide' "$tmp_dir/broken/action-verify-pr.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/configured/action-verify-pr.json" \
  --out "$tmp_dir/report-quality" \
  --shareable \
  --strict >/dev/null

grep -q '"status": "pass"' "$tmp_dir/report-quality/ios-report-quality.json"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/runtime-broken" \
  --reports "$tmp_dir/broken" \
  --out "$tmp_dir/blocker-quality" \
  --shareable \
  --strict >/dev/null

grep -q '"status": "pass"' "$tmp_dir/blocker-quality/ios-report-quality.json"
if grep -q 'local-path-shareability-warning' "$tmp_dir/blocker-quality/ios-report-quality.json"; then
  echo "shareable verify-pr reports should not trigger local path warnings" >&2
  exit 1
fi

cp -R "$tmp_dir/broken" "$tmp_dir/missing-guide"
python3 - <<'PY' "$tmp_dir/missing-guide/action-verify-pr.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.pop("freshMaintainerFailureGuide", None)
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-guide" \
  --out "$tmp_dir/missing-guide-quality" \
  --shareable >/dev/null

grep -q '"ruleId": "verify-pr-failure-guide-missing"' "$tmp_dir/missing-guide-quality/ios-report-quality.json"

echo "action verify-pr tests passed"
