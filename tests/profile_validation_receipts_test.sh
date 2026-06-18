#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard init web "$tmp_dir/web-app" >/dev/null
mkdir -p "$tmp_dir/web-app/src" "$tmp_dir/web-app/tests"
cat > "$tmp_dir/web-app/package.json" <<'JSON'
{
  "scripts": {
    "lint": "eslint .",
    "test": "vitest",
    "build": "next build",
    "e2e": "playwright test"
  },
  "dependencies": {
    "next": "latest",
    "playwright": "latest"
  }
}
JSON
printf 'export const checkoutRisk = true\n' > "$tmp_dir/web-app/src/App.tsx"

./bin/shipguard web audit \
  --path "$tmp_dir/web-app" \
  --out "$tmp_dir/web-audit" \
  --shipguard-eval \
  --shareable >/dev/null

./bin/shipguard web plan \
  --report "$tmp_dir/web-audit" \
  --out "$tmp_dir/web-plan-no-target" \
  --shipguard-eval \
  --shareable >/dev/null

./bin/shipguard web plan \
  --report "$tmp_dir/web-audit" \
  --out "$tmp_dir/web-plan-target" \
  --target "$tmp_dir/web-app" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/web-plan-no-target/web-plan.json" "$tmp_dir/web-plan-target/web-plan.json"
import json
import sys

no_target = json.load(open(sys.argv[1], encoding="utf-8"))
with_target = json.load(open(sys.argv[2], encoding="utf-8"))

receipts = no_target["validationReceipts"]
if receipts["checked"] is not False:
    raise SystemExit("missing-target plan should not mark validation receipts checked")
if receipts["notCheckedCount"] < 1:
    raise SystemExit("missing-target plan should classify commands as not_checked")
if receipts["runnableCount"] != 0:
    raise SystemExit("missing-target plan must not claim runnable validation")

target_receipts = with_target["validationReceipts"]
if target_receipts["checked"] is not True:
    raise SystemExit("target-backed plan should mark validation receipts checked")
if target_receipts["target"] != "<target-repo>":
    raise SystemExit("shareable target path should be redacted")
if target_receipts["runnableCount"] < 5:
    raise SystemExit(f"expected web target commands to be classified runnable: {target_receipts!r}")
statuses = {item["command"]: item["status"] for item in target_receipts["receipts"]}
for command in ("npm run lint", "npm test", "npm run build", "npx playwright test"):
    if statuses.get(command) != "runnable":
        raise SystemExit(f"{command} should be runnable: {statuses!r}")
if any(item.get("executed") for item in target_receipts["receipts"]):
    raise SystemExit("validation receipts should classify availability without executing target commands")
if any(item.get("runAuthorized") for item in target_receipts["receipts"]):
    raise SystemExit("validation receipts must not authorize command execution")
PY

if grep -q "$tmp_dir" "$tmp_dir/web-plan-target/web-plan.json" "$tmp_dir/web-plan-target/web-plan.md"; then
  echo "validation receipts leaked local temp path" >&2
  exit 1
fi

grep -q 'Validation Receipts' "$tmp_dir/web-plan-target/web-plan.md"
grep -q 'read-only command availability classification' "$tmp_dir/web-plan-target/web-plan.md"
grep -q 'runnable' "$tmp_dir/web-plan-target/web-plan.md"

echo "profile validation receipt tests passed"
