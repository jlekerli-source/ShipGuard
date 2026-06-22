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
  "status": "review",
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
grep -q '"missingReceiptPriority": \[\]' "$tmp_dir/inspect/shipguard-inspect.json"
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
if data["proofReceipts"]["fullAudit"]["status"] != "review":
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

python3 - <<'PY' "$tmp_dir/value/tool-value-gauntlet.json" "$tmp_dir/value/tool-value-gauntlet-stable.json"
import json
import sys

source, target = sys.argv[1:3]
data = json.load(open(source, encoding="utf-8"))
data["stablePublicationPriority"] = {
    "status": "review",
    "surface": "v4 Stable Release Publication",
    "nextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-out> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable",
    "blockedBy": [
        "public GitHub release metadata and release notes",
        "downloaded release assets",
        "post-release consumer proof",
    ],
    "whyItMatters": "Stable v4 should not be claimed until public release assets and consumer proof pass together.",
}
json.dump(data, open(target, "w", encoding="utf-8"), indent=2, sort_keys=True)
PY

mkdir -p "$tmp_dir/value-stable"
mv "$tmp_dir/value/tool-value-gauntlet-stable.json" "$tmp_dir/value-stable/tool-value-gauntlet.json"

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/stable-priority" \
  --value-gauntlet "$tmp_dir/value-stable" \
  --full-audit "$tmp_dir/full" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/stable-priority/shipguard-inspect.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
next_action = data.get("nextAction") or {}
result = data.get("resultUX") or {}
priority = data["proofReceipts"]["valueGauntlet"].get("stablePublicationPriority") or {}
expected = priority.get("nextCommand")
if next_action.get("source") != "value-gauntlet.stablePublicationPriority":
    raise SystemExit(f"stable-publication priority should drive nextAction: {next_action!r}")
if not expected or next_action.get("command") != expected:
    raise SystemExit(f"stable-publication command should survive inspect: {next_action!r} {priority!r}")
if result.get("nextCommand") != expected:
    raise SystemExit(f"resultUX should mirror stable-publication command: {result!r}")
if "public GitHub release metadata" not in next_action.get("reason", ""):
    raise SystemExit(f"stable-publication blockers should be in reason: {next_action!r}")
PY

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
missing = data.get("missingReceiptPriority") or []
ids = [item.get("id") for item in missing]
expected = ["value-gauntlet", "full-audit", "release-assets"]
if ids != expected:
    raise SystemExit(f"missing receipts should stay prioritized {expected}: {missing!r}")
if missing[0].get("nextCommand") != next_action.get("command"):
    raise SystemExit(f"first missing receipt should mirror next action: {missing!r} {next_action!r}")
PY

grep -q 'value-gauntlet.missing' "$tmp_dir/missing-inputs/shipguard-inspect.md"
grep -q './bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet' "$tmp_dir/missing-inputs/shipguard-inspect.md"
grep -q 'Missing Receipt Priority' "$tmp_dir/missing-inputs/shipguard-inspect.md"

python3 - <<'PY' "$tmp_dir/value/tool-value-gauntlet.json" "$tmp_dir/value/tool-value-gauntlet-prose.json"
import json
import sys

source, target = sys.argv[1:3]
data = json.load(open(source, encoding="utf-8"))
answer = data["lowestValueSurfaceProbe"]["answer"]
answer["identifier"] = "shipguard v4-product-release-stabilization"
answer["recommendation"] = "Stabilize the v4 product release with adoption, rollback, and release proof."
answer["proofGuidance"] = "Run value-gauntlet plus focused v4 product-release fixtures that prove install, rollback, and release consumption."
json.dump(data, open(target, "w", encoding="utf-8"), indent=2, sort_keys=True)
PY

mkdir -p "$tmp_dir/value-prose"
mv "$tmp_dir/value/tool-value-gauntlet-prose.json" "$tmp_dir/value-prose/tool-value-gauntlet.json"

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/prose-guidance" \
  --value-gauntlet "$tmp_dir/value-prose" \
  --full-audit "$tmp_dir/full" \
  --release-assets "$tmp_dir/release" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/prose-guidance/shipguard-inspect.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
next_action = data.get("nextAction") or {}
result = data.get("resultUX") or {}
expected = "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet"
if next_action.get("command") != expected:
    raise SystemExit(f"prose proof guidance should fall back to executable command: {next_action!r}")
if result.get("nextCommand") != expected:
    raise SystemExit(f"resultUX nextCommand should stay executable: {result!r}")
if "Run value-gauntlet plus focused v4 product-release fixtures" not in next_action.get("reason", ""):
    raise SystemExit(f"prose proof guidance should remain in reason: {next_action!r}")
PY

mkdir -p "$tmp_dir/full-unsafe"
cat > "$tmp_dir/full-unsafe/shipguard-full-audit.json" <<'JSON'
{
  "tool": "shipguard full-audit",
  "status": "review",
  "profile": "release",
  "planOnly": false,
  "stageStatusSummary": {
    "review": 1
  },
  "stages": [
    {
      "stageId": "bad stage; echo nope",
      "title": "Bad stage id",
      "status": "review",
      "errorSummary": "Synthetic malformed stage id."
    }
  ]
}
JSON

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/unsafe-stage" \
  --value-gauntlet "$tmp_dir/value" \
  --full-audit "$tmp_dir/full-unsafe" \
  --release-assets "$tmp_dir/release" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/unsafe-stage/shipguard-inspect.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
next_action = data.get("nextAction") or {}
result = data.get("resultUX") or {}
expected = "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --shipguard-eval --shareable"
if next_action.get("source") != "full-audit.failedStages":
    raise SystemExit(f"unsafe stage should still be a failed-stage action: {next_action!r}")
if next_action.get("command") != expected:
    raise SystemExit(f"unsafe stage id should fall back to executable full-audit command: {next_action!r}")
if "--stage bad stage" in next_action.get("command", ""):
    raise SystemExit(f"unsafe stage id leaked into command: {next_action!r}")
if result.get("nextCommand") != expected:
    raise SystemExit(f"resultUX should mirror safe fallback command: {result!r}")
PY

echo "inspect tests passed"
