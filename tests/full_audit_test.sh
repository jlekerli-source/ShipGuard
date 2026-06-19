#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard full-audit --help >/dev/null

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/plan" \
  --profile release \
  --plan-only \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/plan/shipguard-full-audit.json"
test -f "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '"tool": "shipguard full-audit"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"status": "pass"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"resultUX":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"proofSource":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"nextCommand":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"planned": 14' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"stageId": "release-proof"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"doesNotPush": true' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q 'ShipGuard Full Audit' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '## Result' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Proof source:' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Slow Lanes' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'v3.127.0 Codex Marketplace Readiness' "$tmp_dir/plan/shipguard-full-audit.md"
if grep -q "$repo_root" "$tmp_dir/plan/shipguard-full-audit.json" "$tmp_dir/plan/shipguard-full-audit.md"; then
  echo "shareable full-audit output leaked local repo path" >&2
  exit 1
fi

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/mini" \
  --stage version \
  --stage py-compile \
  --stage docs-check \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/mini/shipguard-full-audit.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
if data["status"] != "pass":
    raise SystemExit(data)
if data["stageStatusSummary"] != {"pass": 3}:
    raise SystemExit(data["stageStatusSummary"])
if data["efficiency"]["executedStages"] != 3:
    raise SystemExit(data["efficiency"])
if data["scopeBoundary"]["targetAppsReadOnly"] is not True:
    raise SystemExit(data["scopeBoundary"])
stage_ids = [stage["stageId"] for stage in data["stages"]]
if stage_ids != ["version", "py-compile", "docs-check"]:
    raise SystemExit(stage_ids)
if any(stage["durationSeconds"] < 0 for stage in data["stages"]):
    raise SystemExit(data["stages"])
if not data["reportQualityQuestions"]:
    raise SystemExit("missing report quality questions")
if not data.get("resultUX", {}).get("verdict", "").startswith("PASS:"):
    raise SystemExit(data.get("resultUX"))
PY

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/mini" \
  --stage version \
  --stage py-compile \
  --stage docs-check \
  --resume \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/mini/shipguard-full-audit.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
statuses = {stage["status"] for stage in data["stages"]}
if statuses != {"skipped"}:
    raise SystemExit(data["stages"])
if data["stageStatusSummary"] != {"skipped": 3}:
    raise SystemExit(data["stageStatusSummary"])
if not all(stage.get("skippedReason") == "resume reused prior passing receipt" for stage in data["stages"]):
    raise SystemExit(data["stages"])
PY

json_stdout="$(./bin/shipguard full-audit --path . --out "$tmp_dir/json" --stage version --plan-only --json)"
grep -q '"tool": "shipguard full-audit"' <<<"$json_stdout"
markdown_stdout="$(./bin/shipguard full-audit --path . --out "$tmp_dir/md" --stage version --plan-only --markdown)"
grep -q '# ShipGuard Full Audit' <<<"$markdown_stdout"

echo "full audit tests passed"
