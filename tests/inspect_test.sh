#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard inspect --help >/dev/null

mkdir -p "$tmp_dir/value" "$tmp_dir/full" "$tmp_dir/release/proof" "$tmp_dir/release/attestation"

cat > "$tmp_dir/value/tool-value-gauntlet.json" <<'JSON'
{
  "tool": "shipguard value-gauntlet",
  "surface": "ShipGuard Tool Value Gauntlet",
  "status": "pass",
  "summary": {
    "averageScore": 100,
    "commandCount": 63
  },
  "lowestValueSurfaceProbe": {
    "answer": {
      "identifier": "shipguard unified-inspect-experience",
      "name": "Unified inspect experience",
      "surfaceType": "cross-cutting",
      "depthScore": 80,
      "missingDepthSignals": ["runtimeUnifiedInspectExperience"],
      "recommendation": "Add one concise inspect command that summarizes proof state and next action.",
      "proofGuidance": "./tests/inspect_test.sh",
      "reason": "ShipGuard proof state is split across reports."
    }
  },
  "reportQualityQuestions": [
    "Should ShipGuard add a unified inspect experience?"
  ]
}
JSON

cat > "$tmp_dir/full/shipguard-full-audit.json" <<'JSON'
{
  "tool": "shipguard full-audit",
  "status": "pass",
  "profile": "release",
  "planOnly": true,
  "stageStatusSummary": {
    "planned": 14
  },
  "slowLaneSummary": {
    "slowDefaultStageCount": 5
  },
  "efficiency": {
    "executedStages": 0,
    "plannedStages": 14
  },
  "scopeBoundary": {
    "targetAppsReadOnly": true,
    "doesNotPush": true,
    "doesNotPublishRelease": true
  },
  "stages": [],
  "reportQualityQuestions": [
    "Can the release plan be inspected from one surface?"
  ]
}
JSON

cat > "$tmp_dir/release/proof/release-manifest.json" <<'JSON'
{
  "schema_version": "1.0",
  "version": "3.125.0",
  "tag": "v3.125.0",
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "artifact": {
    "name": "shipguard-v3.125.0.tar.gz",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "proofs": {
    "release_url": "https://github.com/jlekerli-source/ShipGuard/releases/tag/v3.125.0",
    "ci_run_url": "https://github.com/jlekerli-source/ShipGuard/actions/runs/1"
  }
}
JSON

cat > "$tmp_dir/release/attestation/attestation-badge.json" <<'JSON'
{
  "status": "pass"
}
JSON

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/inspect" \
  --value-gauntlet "$tmp_dir/value" \
  --full-audit "$tmp_dir/full" \
  --release-assets "$tmp_dir/release" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/inspect/shipguard-inspect.json"
test -f "$tmp_dir/inspect/shipguard-inspect.md"
python3 -m json.tool "$tmp_dir/inspect/shipguard-inspect.json" >/dev/null

grep -q '"tool": "shipguard inspect"' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"surface": "ShipGuard InspectDeck"' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"repoState":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"proofReceipts":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"pluginState":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"releaseState":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"underlyingEvidence":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"resultUX":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"proofSource":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"nextCommand":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"nextAction":' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"source": "value-gauntlet.lowestValueSurfaceProbe.answer"' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"shipguardOnly": true' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"doesNotPush": true' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/inspect/shipguard-inspect.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/inspect/shipguard-inspect.json"

grep -q '# ShipGuard InspectDeck' "$tmp_dir/inspect/shipguard-inspect.md"
grep -q '## Result' "$tmp_dir/inspect/shipguard-inspect.md"
grep -q 'Proof source:' "$tmp_dir/inspect/shipguard-inspect.md"
grep -q 'Next Action' "$tmp_dir/inspect/shipguard-inspect.md"
grep -q 'Underlying Evidence' "$tmp_dir/inspect/shipguard-inspect.md"
grep -q 'Scope Boundary' "$tmp_dir/inspect/shipguard-inspect.md"

python3 - <<'PY' "$tmp_dir/inspect/shipguard-inspect.json" "$repo_root"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
repo_root = sys.argv[2]
if repo_root in json.dumps(data):
    raise SystemExit("shareable inspect output leaked repo root")
if data["proofReceipts"]["valueGauntlet"]["lowestValueSurface"]["identifier"] != "shipguard unified-inspect-experience":
    raise SystemExit(data["proofReceipts"]["valueGauntlet"])
if data["proofReceipts"]["fullAudit"]["stageStatusSummary"].get("planned") != 14:
    raise SystemExit(data["proofReceipts"]["fullAudit"])
if data["releaseState"]["version"] != "3.125.0":
    raise SystemExit(data["releaseState"])
if data["nextAction"]["command"] != "./tests/inspect_test.sh":
    raise SystemExit(data["nextAction"])
if not data.get("resultUX", {}).get("verdict"):
    raise SystemExit(data.get("resultUX"))
if not data["pluginState"].get("checked"):
    raise SystemExit(data["pluginState"])
PY

json_stdout="$(./bin/shipguard inspect --path . --out "$tmp_dir/json" --value-gauntlet "$tmp_dir/value" --full-audit "$tmp_dir/full" --release-assets "$tmp_dir/release" --json)"
grep -q '"tool": "shipguard inspect"' <<<"$json_stdout"
markdown_stdout="$(./bin/shipguard inspect --path . --out "$tmp_dir/md" --value-gauntlet "$tmp_dir/value" --full-audit "$tmp_dir/full" --release-assets "$tmp_dir/release" --markdown)"
grep -q '# ShipGuard InspectDeck' <<<"$markdown_stdout"

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/missing-inputs" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/missing-inputs/shipguard-inspect.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("status") != "review":
    raise SystemExit(f"missing-input inspect should be review: {data.get('status')!r}")
next_action = data.get("nextAction") or {}
if next_action.get("source") != "value-gauntlet.missing":
    raise SystemExit(f"missing-input inspect should prioritize value-gauntlet receipt first: {next_action!r}")
if next_action.get("command") != "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet":
    raise SystemExit(f"missing-input inspect command should be executable: {next_action!r}")
result = data.get("resultUX") or {}
if result.get("proofSource") != "value-gauntlet.missing":
    raise SystemExit(f"resultUX should expose missing value-gauntlet proof source: {result!r}")
if result.get("nextCommand") != next_action.get("command"):
    raise SystemExit(f"resultUX next command should mirror nextAction: {result!r} {next_action!r}")
PY

grep -q 'value-gauntlet.missing' "$tmp_dir/missing-inputs/shipguard-inspect.md"
grep -q './bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet' "$tmp_dir/missing-inputs/shipguard-inspect.md"

echo "inspect tests passed"
