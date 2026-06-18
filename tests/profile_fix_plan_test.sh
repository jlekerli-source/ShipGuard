#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard web plan --help >/dev/null
./bin/shipguard backend plan --help >/dev/null
./bin/shipguard cli plan --help >/dev/null

./bin/shipguard init web "$tmp_dir/web-app" >/dev/null
mkdir -p "$tmp_dir/web-app/src/components" "$tmp_dir/web-app/tests"
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
    "stripe": "latest"
  }
}
JSON
printf 'export const authPaymentSurface = true\n' > "$tmp_dir/web-app/src/components/AuthPanel.tsx"

./bin/shipguard web audit \
  --path "$tmp_dir/web-app" \
  --out "$tmp_dir/web-audit" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard web plan \
  --report "$tmp_dir/web-audit" \
  --out "$tmp_dir/web-plan" \
  --shipguard-eval \
  --shareable >/dev/null
test -f "$tmp_dir/web-plan/web-plan.json"
test -f "$tmp_dir/web-plan/web-plan.md"
grep -q '"tool": "shipguard web plan"' "$tmp_dir/web-plan/web-plan.json"
grep -q '"surface": "ShipGuard WebForge"' "$tmp_dir/web-plan/web-plan.json"
grep -q '"profile": "web"' "$tmp_dir/web-plan/web-plan.json"
grep -q '"shipguardOnly": true' "$tmp_dir/web-plan/web-plan.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/web-plan/web-plan.json"
grep -q '"implementationAuthorized": false' "$tmp_dir/web-plan/web-plan.json"
grep -q '"fixPlan":' "$tmp_dir/web-plan/web-plan.json"
grep -q '"validationCommands":' "$tmp_dir/web-plan/web-plan.json"
grep -q 'ShipGuard WebForge' "$tmp_dir/web-plan/web-plan.md"
grep -q 'Scoped Fix Plan' "$tmp_dir/web-plan/web-plan.md"
grep -q 'Validation Commands' "$tmp_dir/web-plan/web-plan.md"
grep -q 'Stop Conditions' "$tmp_dir/web-plan/web-plan.md"
grep -q 'Report Quality Questions' "$tmp_dir/web-plan/web-plan.md"
if grep -q "$tmp_dir" "$tmp_dir/web-plan/web-plan.json" "$tmp_dir/web-plan/web-plan.md"; then
  echo "web plan leaked local temp path" >&2
  exit 1
fi

./bin/shipguard init backend "$tmp_dir/backend-app" >/dev/null
mkdir -p "$tmp_dir/backend-app/app/routes" "$tmp_dir/backend-app/tests"
cat > "$tmp_dir/backend-app/pyproject.toml" <<'TOML'
[project]
name = "demo-service"

[tool.pytest.ini_options]
testpaths = ["tests"]
TOML
printf 'def auth_webhook_queue_handler():\n    return "ok"\n' > "$tmp_dir/backend-app/app/routes/webhook.py"

./bin/shipguard backend audit \
  --path "$tmp_dir/backend-app" \
  --out "$tmp_dir/backend-audit" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard backend plan \
  --report "$tmp_dir/backend-audit" \
  --out "$tmp_dir/backend-plan" \
  --shipguard-eval \
  --shareable >/dev/null
test -f "$tmp_dir/backend-plan/backend-plan.json"
test -f "$tmp_dir/backend-plan/backend-plan.md"
grep -q '"tool": "shipguard backend plan"' "$tmp_dir/backend-plan/backend-plan.json"
grep -q '"surface": "ShipGuard ServiceForge"' "$tmp_dir/backend-plan/backend-plan.json"
grep -q '"profile": "backend"' "$tmp_dir/backend-plan/backend-plan.json"
grep -q 'ShipGuard ServiceForge' "$tmp_dir/backend-plan/backend-plan.md"
grep -q 'Scoped Fix Plan' "$tmp_dir/backend-plan/backend-plan.md"
if grep -q "$tmp_dir" "$tmp_dir/backend-plan/backend-plan.json" "$tmp_dir/backend-plan/backend-plan.md"; then
  echo "backend plan leaked local temp path" >&2
  exit 1
fi

./bin/shipguard init cli "$tmp_dir/cli-tool" >/dev/null
mkdir -p "$tmp_dir/cli-tool/bin" "$tmp_dir/cli-tool/tests"
cat > "$tmp_dir/cli-tool/package.json" <<'JSON'
{
  "bin": {
    "demo-cli": "bin/demo-cli.js"
  },
  "scripts": {
    "test": "node tests/demo.test.js",
    "lint": "shellcheck scripts/*.sh"
  },
  "dependencies": {
    "commander": "latest"
  }
}
JSON
printf '#!/usr/bin/env node\nconsole.log("stdout stderr exit code token redaction")\n' > "$tmp_dir/cli-tool/bin/demo-cli.js"

./bin/shipguard cli audit \
  --path "$tmp_dir/cli-tool" \
  --out "$tmp_dir/cli-audit" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard cli plan \
  --report "$tmp_dir/cli-audit" \
  --out "$tmp_dir/cli-plan" \
  --shipguard-eval \
  --shareable >/dev/null
test -f "$tmp_dir/cli-plan/cli-plan.json"
test -f "$tmp_dir/cli-plan/cli-plan.md"
grep -q '"tool": "shipguard cli plan"' "$tmp_dir/cli-plan/cli-plan.json"
grep -q '"surface": "ShipGuard CommandForge"' "$tmp_dir/cli-plan/cli-plan.json"
grep -q '"profile": "cli"' "$tmp_dir/cli-plan/cli-plan.json"
grep -q 'ShipGuard CommandForge' "$tmp_dir/cli-plan/cli-plan.md"
grep -q 'Scoped Fix Plan' "$tmp_dir/cli-plan/cli-plan.md"
if grep -q "$tmp_dir" "$tmp_dir/cli-plan/cli-plan.json" "$tmp_dir/cli-plan/cli-plan.md"; then
  echo "cli plan leaked local temp path" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/web-plan/web-plan.json" "$tmp_dir/backend-plan/backend-plan.json" "$tmp_dir/cli-plan/cli-plan.json"
import json
import sys

for path in sys.argv[1:]:
    data = json.load(open(path, encoding="utf-8"))
    if not data.get("fixPlan", {}).get("tasks"):
        raise SystemExit(f"missing fixPlan.tasks in {path}")
    if not data.get("validationCommands"):
        raise SystemExit(f"missing validationCommands in {path}")
    if not data.get("stopConditions"):
        raise SystemExit(f"missing stopConditions in {path}")
    if not data.get("reportQualityQuestions"):
        raise SystemExit(f"missing reportQualityQuestions in {path}")
    if data.get("scopeBoundary", {}).get("implementationAuthorized") is not False:
        raise SystemExit(f"implementationAuthorized should stay false in {path}")
PY

json_stdout="$(./bin/shipguard web plan --report "$tmp_dir/web-audit/web-audit.json" --out "$tmp_dir/web-json" --shipguard-eval --shareable --json)"
printf '%s\n' "$json_stdout" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read().split("\nwrote:", 1)[0])["tool"])' | grep -q 'shipguard web plan'

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/web-plan" \
  --reports "$tmp_dir/backend-plan" \
  --reports "$tmp_dir/cli-plan" \
  --out "$tmp_dir/profile-plan-quality" \
  --shareable >/dev/null
grep -q '"tool": "shipguard ios report-quality"' "$tmp_dir/profile-plan-quality/ios-report-quality.json"
grep -q 'ShipGuard WebForge' "$tmp_dir/profile-plan-quality/ios-report-quality.md"
grep -q 'ShipGuard ServiceForge' "$tmp_dir/profile-plan-quality/ios-report-quality.md"
grep -q 'ShipGuard CommandForge' "$tmp_dir/profile-plan-quality/ios-report-quality.md"

echo "profile fix-plan tests passed"
