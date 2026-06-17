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
printf '%s\n' "$status_output" | grep -q 'missing_source'
printf '%s\n' "$status_output" | grep -q 'stale_metadata'
printf '%s\n' "$status_output" | grep -q 'stale_skill_text'

if ./bin/shipguard codex status --cache "$tmp_dir/cache" --strict >/dev/null 2>&1; then
  echo "expected strict stale Codex status to fail" >&2
  exit 1
fi

empty_output="$(./bin/shipguard codex status --cache "$tmp_dir/empty-cache")"
printf '%s\n' "$empty_output" | grep -q 'Overall status: missing'
printf '%s\n' "$empty_output" | grep -q 'missing_install'

echo "codex status tests passed"
