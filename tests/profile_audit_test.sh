#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard web audit --help >/dev/null
./bin/shipguard backend audit --help >/dev/null
./bin/shipguard cli audit --help >/dev/null

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
printf 'export const auth = true\n' > "$tmp_dir/web-app/src/components/AuthPanel.tsx"

./bin/shipguard web audit \
  --path "$tmp_dir/web-app" \
  --out "$tmp_dir/web-audit" \
  --shipguard-eval \
  --shareable >/dev/null
test -f "$tmp_dir/web-audit/web-audit.json"
test -f "$tmp_dir/web-audit/web-audit.md"
grep -q '"tool": "shipguard web audit"' "$tmp_dir/web-audit/web-audit.json"
grep -q '"surface": "ShipGuard WebScan"' "$tmp_dir/web-audit/web-audit.json"
grep -q '"profile": "web"' "$tmp_dir/web-audit/web-audit.json"
grep -q '"root": "<target-repo>"' "$tmp_dir/web-audit/web-audit.json"
grep -q '"shipguardOnly": true' "$tmp_dir/web-audit/web-audit.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/web-audit/web-audit.json"
grep -q 'ShipGuard WebScan' "$tmp_dir/web-audit/web-audit.md"
grep -q 'Recommended First Commands' "$tmp_dir/web-audit/web-audit.md"
grep -q 'shipguard web audit --path .' "$tmp_dir/web-audit/web-audit.md"
grep -q 'Scan Transparency' "$tmp_dir/web-audit/web-audit.md"
grep -q 'target-config' "$tmp_dir/web-audit/web-audit.md"

./bin/shipguard init web "$tmp_dir/starter-only-web" >/dev/null
./bin/shipguard web audit \
  --path "$tmp_dir/starter-only-web" \
  --out "$tmp_dir/starter-only-web-audit" \
  --shipguard-eval \
  --shareable >/dev/null
python3 - "$tmp_dir/starter-only-web-audit/web-audit.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
scan = data.get("scan") or {}
signals = data.get("signals") or {}
if data.get("profileFiles", {}).get("presentCount", 0) < 5:
    raise SystemExit(f"starter profile files should still be tracked: {data.get('profileFiles')!r}")
if scan.get("excludedShipGuardFileCount", 0) < 6:
    raise SystemExit(f"starter-generated files should be excluded from target signals: {scan!r}")
if any(signals.get(group) for group in ("framework", "source", "validation", "risk")):
    raise SystemExit(f"starter-only repo must not get target signals from ShipGuard templates: {signals!r}")
if data.get("target", {}).get("fileCountScanned") != 0:
    raise SystemExit(f"starter-only repo should have zero target signal files: {data.get('target')!r}")
if not any(item.get("ruleId") == "no-validation-signals" for item in data.get("findings", [])):
    raise SystemExit(f"starter-only audit should require real validation evidence: {data.get('findings')!r}")
PY

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
test -f "$tmp_dir/backend-audit/backend-audit.json"
test -f "$tmp_dir/backend-audit/backend-audit.md"
grep -q '"tool": "shipguard backend audit"' "$tmp_dir/backend-audit/backend-audit.json"
grep -q '"surface": "ShipGuard ServiceRadar"' "$tmp_dir/backend-audit/backend-audit.json"
grep -q '"profile": "backend"' "$tmp_dir/backend-audit/backend-audit.json"
grep -q 'ShipGuard ServiceRadar' "$tmp_dir/backend-audit/backend-audit.md"
grep -q 'shipguard backend audit --path .' "$tmp_dir/backend-audit/backend-audit.md"

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
printf '#!/usr/bin/env node\nconsole.log("stdout exit code token redaction")\n' > "$tmp_dir/cli-tool/bin/demo-cli.js"

./bin/shipguard cli audit \
  --path "$tmp_dir/cli-tool" \
  --out "$tmp_dir/cli-audit" \
  --shipguard-eval \
  --shareable >/dev/null
test -f "$tmp_dir/cli-audit/cli-audit.json"
test -f "$tmp_dir/cli-audit/cli-audit.md"
grep -q '"tool": "shipguard cli audit"' "$tmp_dir/cli-audit/cli-audit.json"
grep -q '"surface": "ShipGuard CommandLens"' "$tmp_dir/cli-audit/cli-audit.json"
grep -q '"profile": "cli"' "$tmp_dir/cli-audit/cli-audit.json"
grep -q 'ShipGuard CommandLens' "$tmp_dir/cli-audit/cli-audit.md"
grep -q 'shipguard cli audit --path .' "$tmp_dir/cli-audit/cli-audit.md"

json_stdout="$(./bin/shipguard web audit --path "$tmp_dir/web-app" --out "$tmp_dir/web-json" --shareable --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
grep -q '"tool": "shipguard web audit"' <<<"$json_stdout"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/web-audit" \
  --reports "$tmp_dir/backend-audit" \
  --reports "$tmp_dir/cli-audit" \
  --out "$tmp_dir/profile-quality" \
  --shareable >/dev/null
grep -q '"tool": "shipguard ios report-quality"' "$tmp_dir/profile-quality/ios-report-quality.json"
grep -q 'ShipGuard WebScan' "$tmp_dir/profile-quality/ios-report-quality.md"
grep -q 'ShipGuard ServiceRadar' "$tmp_dir/profile-quality/ios-report-quality.md"
grep -q 'ShipGuard CommandLens' "$tmp_dir/profile-quality/ios-report-quality.md"

echo "profile audit tests passed"
