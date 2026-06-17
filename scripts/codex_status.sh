#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
shipguard codex status

Usage:
  shipguard codex status [--cache <codex-plugin-cache-dir>] [--strict]

Checks the local Codex plugin cache for ShipGuard-related plugin installs and
reports whether the installed metadata appears current with this checkout.

Options:
  --cache <dir>  Override the Codex plugin cache path.
  --strict       Exit non-zero when the install is missing or stale.
USAGE
}

fail() {
  echo "codex-status: $*" >&2
  exit 1
}

json_field() {
  local file="$1"
  local field="$2"
  python3 - "$file" "$field" <<'PY'
import json
import sys

path, dotted = sys.argv[1], sys.argv[2]
try:
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
except Exception:
    sys.exit(0)

for part in dotted.split("."):
    if isinstance(value, dict):
        value = value.get(part, "")
    else:
        value = ""
        break

if isinstance(value, list):
    print(", ".join(str(item) for item in value))
elif isinstance(value, dict):
    print(json.dumps(value, sort_keys=True))
elif value is not None:
    print(value)
PY
}

table_cell() {
  printf '%s' "$1" | perl -pe 's/\|/\\|/g'
}

cache_dir="${CODEX_PLUGIN_CACHE:-$HOME/.codex/plugins/cache}"
strict="false"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --cache)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--cache requires a value"
      cache_dir="$2"
      shift 2
      ;;
    --strict)
      strict="true"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

toolkit_version="$(sed -n '1p' "$tool_root/VERSION")"
source_plugin_json="$tool_root/plugins/ios-shipguard/.codex-plugin/plugin.json"
marketplace_json="$tool_root/.agents/plugins/marketplace.json"
source_status="missing"
source_version=""
source_repository=""
marketplace_status="missing"
marketplace_name=""
marketplace_plugin_name=""
marketplace_plugin_path=""

if [[ -f "$source_plugin_json" ]]; then
  source_status="present"
  source_version="$(json_field "$source_plugin_json" "version")"
  source_repository="$(json_field "$source_plugin_json" "repository")"
fi

if [[ -f "$marketplace_json" ]]; then
  marketplace_status="present"
  marketplace_name="$(json_field "$marketplace_json" "name")"
  marketplace_plugin_name="$(python3 - "$marketplace_json" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        marketplace = json.load(handle)
except Exception:
    sys.exit(0)

for plugin in marketplace.get("plugins", []):
    if plugin.get("name") == "ios-shipguard":
        print(plugin.get("name", ""))
        break
PY
)"
  marketplace_plugin_path="$(python3 - "$marketplace_json" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        marketplace = json.load(handle)
except Exception:
    sys.exit(0)

for plugin in marketplace.get("plugins", []):
    if plugin.get("name") == "ios-shipguard":
        print(plugin.get("source", {}).get("path", ""))
        break
PY
)"
fi

plugin_jsons=()
plugin_count=0
while IFS= read -r plugin_json; do
  plugin_jsons+=("$plugin_json")
  plugin_count=$((plugin_count + 1))
done < <(
  if [[ -d "$cache_dir" ]]; then
    find "$cache_dir" -path '*/ios-shipguard/*/.codex-plugin/plugin.json' -type f 2>/dev/null | sort
  fi
)

status="pass"
findings=()
finding_count=0

add_finding() {
  findings+=("$1")
  finding_count=$((finding_count + 1))
}

if [[ "$source_status" != "present" ]]; then
  status="stale"
  add_finding "missing_source: tracked plugin source is absent at plugins/ios-shipguard/.codex-plugin/plugin.json, so the expected Codex install cannot be rebuilt or verified from source."
fi

if [[ "$marketplace_status" != "present" ]]; then
  status="stale"
  add_finding "missing_marketplace: local plugin marketplace is absent at .agents/plugins/marketplace.json, so the plugin cannot be installed from this checkout through the marketplace flow."
elif [[ "$marketplace_name" != "shipguard" || "$marketplace_plugin_name" != "ios-shipguard" || "$marketplace_plugin_path" != "./plugins/ios-shipguard" ]]; then
  status="stale"
  add_finding "stale_marketplace: local plugin marketplace should expose ios-shipguard@shipguard from ./plugins/ios-shipguard."
fi

if [[ "$plugin_count" -eq 0 ]]; then
  status="missing"
  add_finding "missing_install: no ios-shipguard plugin install was found under the Codex plugin cache."
fi

plugin_rows=()
plugin_row_count=0
plugin_index=0
while [[ "$plugin_index" -lt "$plugin_count" ]]; do
  plugin_json="${plugin_jsons[$plugin_index]}"
  plugin_index=$((plugin_index + 1))
  plugin_root="$(cd "$(dirname "$plugin_json")/.." && pwd)"
  skill_file="$plugin_root/skills/ios-shipguard/SKILL.md"
  agent_file="$plugin_root/skills/ios-shipguard/agents/openai.yaml"
  name="$(json_field "$plugin_json" "name")"
  version="$(json_field "$plugin_json" "version")"
  repository="$(json_field "$plugin_json" "repository")"
  homepage="$(json_field "$plugin_json" "homepage")"
  display_name="$(json_field "$plugin_json" "interface.displayName")"
  row_status="pass"

  if [[ "$repository" == *"ringly-codex-workflows"* || "$homepage" == *"ringly-codex-workflows"* ]]; then
    row_status="stale"
    status="stale"
    add_finding "stale_metadata: installed plugin metadata still references ringly-codex-workflows at $plugin_root."
  fi
  if [[ "$display_name" == *"Shipguard"* ]]; then
    row_status="stale"
    status="stale"
    add_finding "stale_display_name: installed plugin display name uses old Shipguard casing at $plugin_root."
  fi
  if [[ -f "$skill_file" ]] && grep -q 'codex-maintainer' "$skill_file"; then
    row_status="stale"
    status="stale"
    add_finding "stale_skill_text: installed skill guidance still prefers codex-maintainer instead of shipguard at $skill_file."
  fi
  if [[ -f "$agent_file" ]] && grep -q 'Shipguard' "$agent_file"; then
    row_status="stale"
    status="stale"
    add_finding "stale_agent_metadata: installed agent metadata uses old Shipguard casing at $agent_file."
  fi
  if [[ -n "$source_version" && "$version" != "$source_version" ]]; then
    row_status="stale"
    status="stale"
    add_finding "version_mismatch: installed plugin version $version does not match tracked source plugin version $source_version at $plugin_root."
  fi

  plugin_rows+=("| $(table_cell "${version:-unknown}") | $(table_cell "${name:-unknown}") | $(table_cell "${repository:-unknown}") | $(table_cell "${display_name:-unknown}") | $(table_cell "$plugin_root") | $row_status |")
  plugin_row_count=$((plugin_row_count + 1))
done

{
  echo "# ShipGuard Codex Status"
  echo
  echo "- Toolkit version: $toolkit_version"
  if [[ "$source_status" == "present" ]]; then
    echo "- Tracked plugin source: present"
    echo "- Tracked plugin version: ${source_version:-unknown}"
    echo "- Tracked plugin repository: ${source_repository:-unknown}"
  else
    echo "- Tracked plugin source: missing"
  fi
  if [[ "$marketplace_status" == "present" ]]; then
    echo "- Local marketplace: present"
    echo "- Local marketplace id: ${marketplace_name:-unknown}"
    echo "- Local marketplace plugin: ${marketplace_plugin_name:-unknown}"
    echo "- Local marketplace plugin path: ${marketplace_plugin_path:-unknown}"
  else
    echo "- Local marketplace: missing"
  fi
  echo "- Codex plugin cache: $cache_dir"
  echo "- Installed ios-shipguard plugins: $plugin_count"
  echo "- Overall status: $status"
  echo
  echo "## Installed Plugins"
  echo
  echo "| Version | Name | Repository | Display name | Path | Status |"
  echo "| --- | --- | --- | --- | --- | --- |"
  if [[ "$plugin_row_count" -gt 0 ]]; then
    plugin_row_index=0
    while [[ "$plugin_row_index" -lt "$plugin_row_count" ]]; do
      printf '%s\n' "${plugin_rows[$plugin_row_index]}"
      plugin_row_index=$((plugin_row_index + 1))
    done
  else
    echo "| none | none | none | none | none | missing |"
  fi
  echo
  echo "## Findings"
  echo
  if [[ "$finding_count" -gt 0 ]]; then
    finding_index=0
    while [[ "$finding_index" -lt "$finding_count" ]]; do
      printf '%s\n' "${findings[$finding_index]}"
      finding_index=$((finding_index + 1))
    done | awk '!seen[$0]++ { print "- " $0 }'
  else
    echo "- none"
  fi
}

if [[ "$strict" == "true" && "$status" != "pass" ]]; then
  exit 1
fi
