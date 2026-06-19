#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"
export SHIPGUARD_CLI="$repo_root/bin/shipguard"

plugin_version="$(python3 - <<'PY'
import json
with open("plugins/ios-shipguard/.codex-plugin/plugin.json", "r", encoding="utf-8") as handle:
    print(json.load(handle)["version"])
PY
)"
cache_dir="$tmp_dir/codex-cache"
plugin_cache="$cache_dir/shipguard/ios-shipguard/$plugin_version"
mkdir -p "$(dirname "$plugin_cache")"
cp -R plugins/ios-shipguard "$plugin_cache"

./bin/shipguard codex marketplace-readiness \
  --path . \
  --out "$tmp_dir/readiness" \
  --cache "$cache_dir" \
  --strict \
  --shareable >/dev/null

test -f "$tmp_dir/readiness/codex-marketplace-readiness.json"
test -f "$tmp_dir/readiness/codex-marketplace-readiness.md"

python3 - "$tmp_dir/readiness/codex-marketplace-readiness.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)

if data.get("tool") != "shipguard codex marketplace-readiness":
    raise SystemExit(f"wrong tool: {data.get('tool')!r}")
if data.get("surface") != "ShipGuard MarketplaceDeck":
    raise SystemExit(f"wrong surface: {data.get('surface')!r}")
if data.get("status") != "pass":
    raise SystemExit(f"expected pass: {data.get('status')!r} findings={data.get('findings')!r}")
if data.get("path") != "<shipguard-repo>":
    raise SystemExit(f"shareable path was not redacted: {data.get('path')!r}")
summary = data.get("summary") or {}
if summary.get("requiredFailureCount") != 0 or summary.get("passedCheckCount") != summary.get("checkCount"):
    raise SystemExit(f"unexpected summary: {summary!r}")
for key in ["resultUX", "pluginMetadata", "marketplaceSource", "publicAssets", "installProof", "statusProof", "submissionPacket", "scopeBoundary"]:
    if key not in data:
        raise SystemExit(f"missing key: {key}")
if data["resultUX"].get("status") != "pass":
    raise SystemExit(f"resultUX not pass: {data['resultUX']!r}")
if data["marketplaceSource"].get("id") != "shipguard":
    raise SystemExit(f"wrong marketplace source: {data['marketplaceSource']!r}")
if data["marketplaceSource"].get("pluginPath") != "./plugins/ios-shipguard":
    raise SystemExit(f"wrong plugin path: {data['marketplaceSource']!r}")
if data["statusProof"].get("overallStatus") != "pass":
    raise SystemExit(f"status proof did not pass: {data['statusProof']!r}")
packet = data["submissionPacket"]
if "codex plugin marketplace add ." not in packet.get("installCommands", []):
    raise SystemExit(f"install commands incomplete: {packet.get('installCommands')!r}")
if not any("codex marketplace-readiness" in command for command in packet.get("proofCommands", [])):
    raise SystemExit(f"proof commands incomplete: {packet.get('proofCommands')!r}")
if "Do not fabricate screenshots" not in packet.get("screenshotPolicy", ""):
    raise SystemExit(f"screenshot policy too weak: {packet.get('screenshotPolicy')!r}")
if "model selection happens outside ShipGuard" not in packet.get("modelChoiceBoundary", ""):
    raise SystemExit(f"model boundary missing: {packet.get('modelChoiceBoundary')!r}")
if not data["scopeBoundary"].get("shipguardOnly") or data["scopeBoundary"].get("mutatesPluginCache"):
    raise SystemExit(f"scope boundary wrong: {data['scopeBoundary']!r}")
PY

grep -q '# ShipGuard Codex Marketplace Readiness' "$tmp_dir/readiness/codex-marketplace-readiness.md"
grep -q '## Result' "$tmp_dir/readiness/codex-marketplace-readiness.md"
grep -q '## Submission Packet' "$tmp_dir/readiness/codex-marketplace-readiness.md"
grep -q '## Public Assets' "$tmp_dir/readiness/codex-marketplace-readiness.md"
grep -q 'codex plugin add ios-shipguard@shipguard' "$tmp_dir/readiness/codex-marketplace-readiness.md"
grep -q 'Do not fabricate screenshots' "$tmp_dir/readiness/codex-marketplace-readiness.md"
if grep -q "$repo_root" "$tmp_dir/readiness/codex-marketplace-readiness.md"; then
  echo "shareable marketplace readiness report leaked repo path" >&2
  exit 1
fi
if grep -q "$HOME" "$tmp_dir/readiness/codex-marketplace-readiness.md"; then
  echo "shareable marketplace readiness report leaked home path" >&2
  exit 1
fi

if ./bin/shipguard codex marketplace-readiness \
  --path . \
  --out "$tmp_dir/missing-cache" \
  --cache "$tmp_dir/missing-cache-root" \
  --strict >/dev/null 2>&1; then
  echo "expected strict marketplace readiness to fail with missing Codex cache proof" >&2
  exit 1
fi

echo "codex marketplace readiness tests passed"
