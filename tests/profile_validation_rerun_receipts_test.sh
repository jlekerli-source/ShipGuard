#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

mkdir -p "$tmp_dir/web-app" "$tmp_dir/web-audit"
cat > "$tmp_dir/web-app/package.json" <<'JSON'
{
  "scripts": {},
  "dependencies": {
    "next": "latest"
  }
}
JSON
cat > "$tmp_dir/web-audit/web-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard web audit",
  "surface": "ShipGuard WebScan",
  "profile": "web",
  "generatedAt": "2026-06-18T00:00:00Z",
  "status": "pass",
  "target": {"root": "<target-repo>", "fileCountScanned": 2},
  "recommendedFirstCommands": ["shipguard web audit --path . --out /tmp/shipguard-web-audit"],
  "recommendedValidation": ["npm run lint"],
  "findings": [],
  "reportQualityQuestions": ["Does ShipGuard web plan prove blocked validation lanes can be repaired and rerun?"]
}
JSON

./bin/shipguard web plan \
  --report "$tmp_dir/web-audit" \
  --out "$tmp_dir/web-plan-blocked" \
  --target "$tmp_dir/web-app" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/web-plan-blocked/web-plan.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("validationReceipts") or {}
rerun = data.get("validationRerunReceipts") or {}
if receipts.get("blockedCount") != 1:
    raise SystemExit(f"expected one blocked validation lane before repair: {receipts!r}")
if rerun.get("pairCount") != 1 or rerun.get("blockedPairCount") != 1:
    raise SystemExit(f"expected one blocked repair/rerun pair: {rerun!r}")
pairs = rerun.get("pairs") or []
if not pairs or pairs[0].get("status") != "blocked_until_repaired":
    raise SystemExit(f"expected blocked_until_repaired pair: {pairs!r}")
if "`lint` script" not in pairs[0].get("smallestRepair", ""):
    raise SystemExit(f"expected smallest repair to name the missing lint script: {pairs[0]!r}")
if "--target <target-repo>" not in pairs[0].get("rerunCommand", ""):
    raise SystemExit(f"expected shareable rerun command with target placeholder: {pairs[0]!r}")
if pairs[0].get("repairAuthorized") is not False or pairs[0].get("rerunAuthorized") is not False:
    raise SystemExit(f"repair/rerun should remain unauthorized read-only guidance: {pairs[0]!r}")
PY

grep -q 'Validation Rerun Receipts' "$tmp_dir/web-plan-blocked/web-plan.md"
grep -q 'blocked_until_repaired' "$tmp_dir/web-plan-blocked/web-plan.md"
grep -q 'Rerun template' "$tmp_dir/web-plan-blocked/web-plan.md"
if grep -q "$tmp_dir" "$tmp_dir/web-plan-blocked/web-plan.json" "$tmp_dir/web-plan-blocked/web-plan.md"; then
  echo "validation rerun receipts leaked local temp path" >&2
  exit 1
fi

cat > "$tmp_dir/web-app/package.json" <<'JSON'
{
  "scripts": {
    "lint": "eslint ."
  },
  "dependencies": {
    "next": "latest"
  }
}
JSON

./bin/shipguard web plan \
  --report "$tmp_dir/web-audit" \
  --out "$tmp_dir/web-plan-rerun" \
  --target "$tmp_dir/web-app" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/web-plan-rerun/web-plan.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
receipts = data.get("validationReceipts") or {}
rerun = data.get("validationRerunReceipts") or {}
if receipts.get("blockedCount") != 0:
    raise SystemExit(f"expected blocked validation lanes to clear after repair: {receipts!r}")
if rerun.get("pairCount") != 0:
    raise SystemExit(f"expected no rerun repair pairs after clean rerun: {rerun!r}")
if data.get("scopeBoundary", {}).get("implementationAuthorized") is not False:
    raise SystemExit("profile plan must stay read-only after rerun")
PY

echo "profile validation rerun receipt tests passed"
