#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios devspace-check --help >/dev/null

preview_out="fixtures/ios-devspace/complete-preview"

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
grep -q '"handoffQualityStatus": "pass"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"eventCount": 1' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"status": "source-edit-target"' "$tmp_dir/check/ios-devspace-check.json"
grep -q '"safetyMarkdownPresent": true' "$tmp_dir/check/ios-devspace-check.json"
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

unsafe_preview="$tmp_dir/unsafe-preview"
mkdir -p "$unsafe_preview"
printf '{"tool":"shipguard ios preview","previewUrl":"http://127.0.0.1:8765"}\n' > "$unsafe_preview/session.json"
printf '{"type":"tap-request","action":"tap","source":"preview","note":"Tap Settings"}\n' > "$unsafe_preview/preview-events.jsonl"
cat > "$unsafe_preview/handoff.json" <<'JSON'
{
  "latestEvent": {
    "action": "tap",
    "source": "preview",
    "type": "tap-request"
  },
  "prompt": "Tap the Settings button from the preview coordinates.",
  "targetResolution": {
    "rawCoordinateTapAllowed": true,
    "status": "needs-semantic-target",
    "xcodeBuildMCP": {
      "elementRefRequiredBeforeTouch": false,
      "nextTool": "tap"
    }
  }
}
JSON
printf '# Handoff\n\nRaw coordinate tap allowed: `true`\n' > "$unsafe_preview/handoff.md"
./bin/shipguard ios devspace-check \
  --path . \
  --preview-out "$unsafe_preview" \
  --out "$tmp_dir/unsafe-preview-report" >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/unsafe-preview-report/ios-devspace-check.json"
grep -q '"handoffQualityStatus": "blocked"' "$tmp_dir/unsafe-preview-report/ios-devspace-check.json"
grep -q '"ruleId": "preview-handoff-raw-coordinate-tap-enabled"' "$tmp_dir/unsafe-preview-report/ios-devspace-check.json"
grep -q '"ruleId": "preview-handoff-element-ref-not-required"' "$tmp_dir/unsafe-preview-report/ios-devspace-check.json"

echo "ios devspace-check tests passed"
