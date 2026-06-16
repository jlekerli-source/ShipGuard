#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ios threat-model --help >/dev/null
./bin/codex-maintainer ios threat-model --path . --out "$tmp_dir/threat-model" >/dev/null

test -f "$tmp_dir/threat-model/ios-threat-model.json"
test -f "$tmp_dir/threat-model/ios-threat-model.md"
grep -q '"tool": "codex-maintainer ios threat-model"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"project": "Shipguard for Codex"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"status": "pass"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"id": "devspace-mcp-to-preview"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"id": "reports-to-public-evidence"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"raw-coordinate-tap-confusion"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '"devspace-token-or-path-leak"' "$tmp_dir/threat-model/ios-threat-model.json"
grep -q '# Shipguard for Codex Threat Model' "$tmp_dir/threat-model/ios-threat-model.md"
grep -q 'Codex app-server execution is a trusted local action' "$tmp_dir/threat-model/ios-threat-model.md"
grep -q 'Severity Calibration' "$tmp_dir/threat-model/ios-threat-model.md"
grep -q 'raw coordinates are visual intent only' "$tmp_dir/threat-model/ios-threat-model.md"

json_stdout="$(./bin/codex-maintainer ios threat-model --path . --out "$tmp_dir/threat-model-json" --json)"
printf '%s\n' "$json_stdout" | grep -q '"status": "pass"'

markdown_stdout="$(./bin/codex-maintainer ios threat-model --path . --out "$tmp_dir/threat-model-markdown" --markdown)"
printf '%s\n' "$markdown_stdout" | grep -q '# Shipguard for Codex Threat Model'

echo "ios threat model tests passed"
