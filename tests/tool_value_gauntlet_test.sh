#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard value-gauntlet --help >/dev/null
./bin/shipguard value-gauntlet \
  --path . \
  --out "$tmp_dir/gauntlet" >/dev/null

test -f "$tmp_dir/gauntlet/tool-value-gauntlet.json"
test -f "$tmp_dir/gauntlet/tool-value-gauntlet.md"
python3 -m json.tool "$tmp_dir/gauntlet/tool-value-gauntlet.json" >/dev/null

grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"surface": "ShipGuard Tool Value Gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"intent": "shipguard-product-qa"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"shipguardOnly": true' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"commandCount": 51' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"pluginCount": 1' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"actions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"skills":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"plugins":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"lowestValueSurfaceProbe":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"priorityActions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard score"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"command": "shipguard value-gauntlet"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "alarm-testing"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/alarm-testing/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "notification-permissions"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/notification-permissions/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "release-checklist"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/release-checklist/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "bug-triage"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/bug-triage/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"name": "ui-polish"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"path": ".agents/skills/ui-polish/SKILL.md"' "$tmp_dir/gauntlet/tool-value-gauntlet.json"

grep -q '# ShipGuard Tool Value Gauntlet' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Priority Actions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Lowest-Value Surface Probe' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Commands' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Skills' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Plugins' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Actions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Docs' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Report Quality Questions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'representative commands and compare actual output' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}
if probe.get("question") != "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?":
    raise SystemExit(f"unexpected probe question: {probe!r}")
for key in ("surfaceType", "identifier", "name", "baseScore", "depthScore", "depthChecks", "recommendation", "proofGuidance", "reason"):
    if key not in answer:
        raise SystemExit(f"probe answer missing {key}: {answer!r}")
if answer.get("surfaceType") != "cross-cutting" or answer.get("identifier") != "shipguard value-gauntlet runtime-output-probe":
    raise SystemExit(f"all-green static coverage should escalate to runtime output probing: {answer!r}")
if "runtimeOutputProbe" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"runtime output probe gap should be explicit: {answer!r}")
if not isinstance(probe.get("rankedSurfaces"), list) or not probe["rankedSurfaces"]:
    raise SystemExit("lowest-value surface probe should rank surfaces")
if "Which ShipGuard command" in data.get("reportQualityQuestions", []):
    raise SystemExit("the answered lowest-value question should not remain a report-quality question")
if not any("representative commands" in question for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"expected next command-execution quality question: {data.get('reportQualityQuestions')!r}")
PY

json_stdout="$(./bin/shipguard value-gauntlet --path . --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard value-gauntlet"'

markdown_stdout="$(./bin/shipguard value-gauntlet --path . --markdown)"
printf '%s\n' "$markdown_stdout" | grep -q '# ShipGuard Tool Value Gauntlet'

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/gauntlet" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null
grep -q '"tool": "shipguard ios report-quality"' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/quality/ios-report-quality.json"
grep -q 'ShipGuard Tool Value Gauntlet' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'representative commands and compare actual output' "$tmp_dir/quality/ios-report-quality.md"

echo "tool value gauntlet tests passed"
