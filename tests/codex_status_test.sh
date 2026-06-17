#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

cache_dir="$tmp_dir/cache/ringly-codex-workflows/ios-shipguard/0.2.0+codex.test"
mkdir -p "$cache_dir/.codex-plugin" "$cache_dir/skills/ios-shipguard/agents"

cat > "$cache_dir/.codex-plugin/plugin.json" <<'JSON'
{
  "name": "ios-shipguard",
  "version": "0.2.0+codex.test",
  "repository": "https://github.com/jlekerli-source/ringly-codex-workflows",
  "homepage": "https://github.com/jlekerli-source/ringly-codex-workflows",
  "interface": {
    "displayName": "iOS Shipguard"
  }
}
JSON

cat > "$cache_dir/skills/ios-shipguard/SKILL.md" <<'EOF_SKILL'
---
name: ios-shipguard
description: Test skill
---

Run ./bin/codex-maintainer ios inventory before edits.
EOF_SKILL

cat > "$cache_dir/skills/ios-shipguard/agents/openai.yaml" <<'YAML'
interface:
  display_name: "iOS Shipguard"
YAML

status_output="$(./bin/shipguard codex status --cache "$tmp_dir/cache")"
printf '%s\n' "$status_output" | grep -q '# ShipGuard Codex Status'
printf '%s\n' "$status_output" | grep -q 'Overall status: stale'
printf '%s\n' "$status_output" | grep -q 'Local marketplace id: shipguard'
printf '%s\n' "$status_output" | grep -q 'stale_metadata'
printf '%s\n' "$status_output" | grep -q 'stale_skill_text'

if ./bin/shipguard codex status --cache "$tmp_dir/cache" --strict >/dev/null 2>&1; then
  echo "expected strict stale Codex status to fail" >&2
  exit 1
fi

empty_output="$(./bin/shipguard codex status --cache "$tmp_dir/empty-cache")"
printf '%s\n' "$empty_output" | grep -q 'Overall status: missing'
printf '%s\n' "$empty_output" | grep -q 'missing_install'

fresh_cache="$tmp_dir/fresh-cache/shipguard/ios-shipguard/$(python3 - <<'PY'
import json
with open("plugins/ios-shipguard/.codex-plugin/plugin.json", "r", encoding="utf-8") as handle:
    print(json.load(handle)["version"])
PY
)"
mkdir -p "$(dirname "$fresh_cache")"
cp -R plugins/ios-shipguard "$fresh_cache"

fresh_output="$(./bin/shipguard codex status --cache "$tmp_dir/fresh-cache" --strict)"
printf '%s\n' "$fresh_output" | grep -q 'Overall status: pass'
printf '%s\n' "$fresh_output" | grep -q 'Tracked plugin source: present'
printf '%s\n' "$fresh_output" | grep -q 'Local marketplace plugin path: ./plugins/ios-shipguard'
printf '%s\n' "$fresh_output" | grep -q 'iOS ShipGuard'

echo "codex status tests passed"
