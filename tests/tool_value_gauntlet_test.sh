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
grep -q '"runtimeOutputProbe":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"runtimeOutputNegativeFixtures":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"runtimeCommandFamilyCoverage":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
grep -q '"skillPluginRuntimeReceipts":' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
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
grep -q 'Runtime Output Probe' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Runtime Output Negative Fixtures' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Runtime Command-Family Coverage' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Skill/Plugin Runtime Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'Report Quality Questions' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
grep -q 'workflow chain receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"
python3 - <<'PY' "$tmp_dir/gauntlet/tool-value-gauntlet.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
probe = data.get("lowestValueSurfaceProbe") or {}
answer = probe.get("answer") or {}
runtime = data.get("runtimeOutputProbe") or {}
negative = data.get("runtimeOutputNegativeFixtures") or {}
command_family = data.get("runtimeCommandFamilyCoverage") or {}
receipts = data.get("skillPluginRuntimeReceipts") or {}
if probe.get("question") != "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?":
    raise SystemExit(f"unexpected probe question: {probe!r}")
for key in ("surfaceType", "identifier", "name", "baseScore", "depthScore", "depthChecks", "recommendation", "proofGuidance", "reason"):
    if key not in answer:
        raise SystemExit(f"probe answer missing {key}: {answer!r}")
if answer.get("surfaceType") != "cross-cutting" or answer.get("identifier") != "shipguard value-gauntlet workflow-chain-receipts":
    raise SystemExit(f"passing skill/plugin receipts should escalate to workflow-chain receipts: {answer!r}")
if "runtimeWorkflowChainReceipts" not in answer.get("missingDepthSignals", []):
    raise SystemExit(f"workflow-chain receipt gap should be explicit: {answer!r}")
if "runtimeSkillPluginReceipts" in answer.get("missingDepthSignals", []):
    raise SystemExit(f"skill/plugin receipts should no longer be missing after fixture proof: {answer!r}")
if not isinstance(probe.get("rankedSurfaces"), list) or not probe["rankedSurfaces"]:
    raise SystemExit("lowest-value surface probe should rank surfaces")
if runtime.get("status") != "pass":
    raise SystemExit(f"runtime output probe should pass on representative commands: {runtime!r}")
if runtime.get("averageScore") != 100:
    raise SystemExit(f"runtime output probe should score complete machine-readable output: {runtime!r}")
command_ids = {item.get("id") for item in runtime.get("commands") or []}
expected_ids = {"brand-deck", "ios-doctor-demo", "ios-design-demo", "report-quality-fixture"}
if command_ids != expected_ids:
    raise SystemExit(f"unexpected runtime command set: {command_ids!r}")
for item in runtime.get("commands") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"runtime command should pass without missing checks: {item!r}")
if negative.get("status") != "pass":
    raise SystemExit(f"negative runtime fixture probe should pass: {negative!r}")
if negative.get("fixtureCount") != 2 or negative.get("passedFixtureCount") != 2:
    raise SystemExit(f"expected two negative runtime fixtures to reject bad reports: {negative!r}")
case_ids = {item.get("id") for item in negative.get("cases") or []}
if case_ids != {"decorative-empty-report", "boundaryless-design-report"}:
    raise SystemExit(f"unexpected negative fixture cases: {case_ids!r}")
for item in negative.get("cases") or []:
    if item.get("status") == "pass" or item.get("fixturePassed") is not True:
        raise SystemExit(f"negative fixture should fail report scoring but pass fixture expectation: {item!r}")
if command_family.get("status") != "pass":
    raise SystemExit(f"runtime command-family coverage should pass: {command_family!r}")
if command_family.get("commandCount") != 51 or command_family.get("passedCommandCount") != 51:
    raise SystemExit(f"expected all public command help paths to pass: {command_family!r}")
for item in command_family.get("commands") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"command help path should pass without missing checks: {item!r}")
if receipts.get("status") != "pass":
    raise SystemExit(f"skill/plugin runtime receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 3 or receipts.get("passedReceiptCount") != 3 or receipts.get("commandCount") != 5:
    raise SystemExit(f"expected three receipt fixtures and five receipt commands: {receipts!r}")
receipt_ids = {item.get("id") for item in receipts.get("receipts") or []}
expected_receipts = {"ios-shipguard-design-audit", "starter-ui-polish-plan", "plugin-cache-status"}
if receipt_ids != expected_receipts:
    raise SystemExit(f"unexpected skill/plugin receipt fixtures: {receipt_ids!r}")
for item in receipts.get("receipts") or []:
    if item.get("status") != "pass" or item.get("missing"):
        raise SystemExit(f"skill/plugin receipt should pass without missing checks: {item!r}")
    for command in item.get("commands") or []:
        if command.get("status") != "pass" or command.get("missing"):
            raise SystemExit(f"receipt command should pass without missing checks: {command!r}")
if "Which ShipGuard command" in data.get("reportQualityQuestions", []):
    raise SystemExit("the answered lowest-value question should not remain a report-quality question")
retired_phrases = (
    "execute representative commands and compare actual output",
    "decorative but low-value reports so output scoring cannot become ceremonial",
    "command-family matrix so every major ShipGuard surface gets executed over time",
    "skill/plugin runtime receipt fixtures so Codex guidance is tested through realistic invoked workflows",
)
if any(any(phrase in question for phrase in retired_phrases) for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"runtime-output, negative-fixture, command-family, and skill/plugin receipt questions should be retired after implementation: {data.get('reportQualityQuestions')!r}")
if not any("workflow chain receipts" in question for question in data.get("reportQualityQuestions", [])):
    raise SystemExit(f"expected workflow-chain receipt quality question: {data.get('reportQualityQuestions')!r}")
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
grep -q 'workflow chain receipts' "$tmp_dir/quality/ios-report-quality.md"

echo "tool value gauntlet tests passed"
