#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

mkdir -p "$tmp_dir/web-app" "$tmp_dir/web-audit"
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
  "reportQualityQuestions": ["Does ShipGuard web plan produce a copy-ready proof handoff only after validation blockers clear?"]
}
JSON

cat > "$tmp_dir/web-app/package.json" <<'JSON'
{
  "scripts": {},
  "dependencies": {
    "next": "latest"
  }
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
handoff = data.get("proofHandoff") or {}
if handoff.get("copyReady") is not False:
    raise SystemExit(f"blocked plan should not be copy-ready: {handoff!r}")
if handoff.get("status") != "blocked_until_validation_ready":
    raise SystemExit(f"blocked plan should explain proof handoff blocker: {handoff!r}")
if not handoff.get("blockers"):
    raise SystemExit(f"blocked plan should include blocker text: {handoff!r}")
if handoff.get("scopeBoundary", {}).get("implementationAuthorized") is not False:
    raise SystemExit("proof handoff must not authorize target implementation")
if handoff.get("scopeBoundary", {}).get("validationExecutionAuthorized") is not False:
    raise SystemExit("proof handoff must not authorize validation execution")
markdown = handoff.get("handoffMarkdown") or ""
if "Copy-ready: false" not in markdown or "Do not share this as completion proof yet" not in markdown:
    raise SystemExit(f"blocked handoff markdown is not explicit enough: {markdown!r}")
PY

grep -q 'Proof Handoff Packet' "$tmp_dir/web-plan-blocked/web-plan.md"
grep -q 'Copy-ready: false' "$tmp_dir/web-plan-blocked/web-plan.md"

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
  --out "$tmp_dir/web-plan-ready" \
  --target "$tmp_dir/web-app" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/web-plan-ready/web-plan.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
handoff = data.get("proofHandoff") or {}
if handoff.get("copyReady") is not True:
    raise SystemExit(f"repaired plan should be copy-ready: {handoff!r}")
if handoff.get("status") != "copy_ready":
    raise SystemExit(f"repaired plan should have copy_ready status: {handoff!r}")
if handoff.get("blockers"):
    raise SystemExit(f"copy-ready handoff should have no blockers: {handoff!r}")
status = handoff.get("validationStatus") or {}
if status.get("blockedCount") != 0 or status.get("notCheckedCount") != 0 or status.get("runnableCount") < 1:
    raise SystemExit(f"copy-ready validation status should be clean and target-backed: {status!r}")
commands = handoff.get("commandsToCapture") or []
if not any(item.get("command") == "npm run lint" and item.get("receiptStatus") == "runnable" for item in commands):
    raise SystemExit(f"copy-ready handoff should name runnable validation command: {commands!r}")
markdown = handoff.get("handoffMarkdown") or ""
for phrase in ("# ShipGuard WebForge Proof Handoff", "Copy-ready: true", "npm run lint", "Attach this packet"):
    if phrase not in markdown:
        raise SystemExit(f"copy-ready handoff markdown missing {phrase!r}: {markdown!r}")
if "/tmp/" in markdown or ("/" + "Users/") in markdown:
    raise SystemExit(f"shareable handoff leaked local path: {markdown!r}")
PY

grep -q 'Proof Handoff Packet' "$tmp_dir/web-plan-ready/web-plan.md"
grep -q 'Copy-ready: true' "$tmp_dir/web-plan-ready/web-plan.md"
grep -q 'npm run lint' "$tmp_dir/web-plan-ready/web-plan.md"
if grep -q "$tmp_dir" "$tmp_dir/web-plan-ready/web-plan.json" "$tmp_dir/web-plan-ready/web-plan.md"; then
  echo "proof handoff leaked local temp path" >&2
  exit 1
fi

echo "profile proof handoff receipt tests passed"
