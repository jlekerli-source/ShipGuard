#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios devspace-check --help >/dev/null

preview_out="$tmp_dir/preview"
mkdir -p "$preview_out"
printf '{"tool":"shipguard ios preview","status":"running"}\n' > "$preview_out/session.json"
printf '# Handoff\n\nUse semantic targets before simulator input.\n' > "$preview_out/handoff.md"
printf '{"source":"preview","action":"tap-request"}\n' > "$preview_out/preview-events.jsonl"

./bin/shipguard ios devspace-check \
  --path . \
  --preview-out "$preview_out" \
  --public-url "https://shipguard-devspace.example.test/mcp" \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN \
  --out "$tmp_dir/check" >/dev/null

test -f "$tmp_dir/check/ios-devspace-check.json"
test -f "$tmp_dir/check/ios-devspace-check.md"
python3 -m json.tool "$tmp_dir/check/ios-devspace-check.json" >/dev/null
grep -q '"tool": "shipguard ios devspace-check"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"status": "pass"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"ruleId": "devspace-loopback-default"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"ruleId": "devspace-bearer-auth-supported"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"ruleId": "devspace-widget-contract"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"ruleId": "devspace-codex-handoff-not-auto-executed"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"status": "complete"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '# iOS Devspace Connector Readiness' "$tmp_dir/check/ios-devspace-check.md"
grep -q 'local MCP bridge with conservative safety defaults' "$tmp_dir/check/ios-devspace-check.md"

json_stdout="$(./bin/shipguard ios devspace-check --path . --json)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios devspace-check"'
printf '%s\n' "$json_stdout" | grep -q '"ruleId": "preview-evidence-not-provided"'

if ./bin/shipguard ios devspace-check \
  --path . \
  --public-url "https://shipguard-devspace.example.test/mcp?token=super-secret-token-value" \
  --strict >/dev/null 2>&1; then
  echo "strict devspace-check should fail when public URL carries a token and no bearer env" >&2
  exit 1
fi

./bin/shipguard ios devspace-check \
  --path . \
  --public-url "https://shipguard-devspace.example.test/mcp?token=super-secret-token-value" \
  --out "$tmp_dir/unsafe" >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/unsafe/ios-devspace-check.json"
grep -q '"ruleId": "public-devspace-token-in-url"' "$tmp_dir/unsafe/ios-devspace-check.json"
grep -q '"ruleId": "public-devspace-missing-bearer-env"' "$tmp_dir/unsafe/ios-devspace-check.json"
if grep -R -q 'super-secret-token-value' "$tmp_dir/unsafe"; then
  echo "devspace-check output must not echo URL token values" >&2
  exit 1
fi

incomplete_preview="$tmp_dir/incomplete-preview"
mkdir -p "$incomplete_preview"
printf '{"tool":"shipguard ios preview"}\n' > "$incomplete_preview/session.json"
./bin/shipguard ios devspace-check \
  --path . \
  --preview-out "$incomplete_preview" \
  --out "$tmp_dir/incomplete" >/dev/null
grep -q '"status": "review"' "$tmp_dir/incomplete/ios-devspace-check.json"
grep -q '"ruleId": "preview-evidence-incomplete"' "$tmp_dir/incomplete/ios-devspace-check.json"

echo "ios devspace-check tests passed"
