#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

./bin/shipguard v4 release-candidate --help >/dev/null
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/v4-release-candidate" \
  --shipguard-eval \
  --shareable
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/json-only" \
  --json
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/markdown-only" \
  --markdown

test -f "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
test -f "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
test -f "$tmp_dir/json-only/v4-release-candidate.json"
test ! -f "$tmp_dir/json-only/v4-release-candidate.md"
test -f "$tmp_dir/markdown-only/v4-release-candidate.md"
test ! -f "$tmp_dir/markdown-only/v4-release-candidate.json"

python3 -m json.tool "$tmp_dir/v4-release-candidate/v4-release-candidate.json" >/dev/null

grep -q '# ShipGuard V4 Release Candidate Readiness' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q '## Result' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Readiness Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Fresh Install' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Release Proof Consumption' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'External Adoption Packet' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Plugin Refresh Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Blocked Claims' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Scope Boundary' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"

grep -q '"tool": "shipguard v4 release-candidate"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"surface": "ShipGuard V4 Release Candidate Readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"status": "pass"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"productStage": "v4-release-candidate-readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"readinessProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"installProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"upgradeProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"uninstallProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"releaseProofConsumption":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"externalAdoptionPacket":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"pluginRefreshProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"releaseClaim": "candidate-ready"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"stableV4Release": false' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"shipguardOnly": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"privateAppsUsed": false' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"mode": "ShipGuard product QA"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"

if grep -R -F -q "$repo_root" "$tmp_dir/v4-release-candidate"; then
  echo "shareable v4 release-candidate output must not include the local repo path" >&2
  exit 1
fi

python3 - "$tmp_dir/v4-release-candidate/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["tool"] == "shipguard v4 release-candidate"
assert report["surface"] == "ShipGuard V4 Release Candidate Readiness"
assert report["status"] == "pass"
assert report["productStage"] == "v4-release-candidate-readiness"
assert report["releaseReadiness"]["releaseClaim"] == "candidate-ready"
assert report["releaseReadiness"]["stableV4Release"] is False
for key in [
    "freshInstall",
    "upgrade",
    "uninstall",
    "releaseProofConsumption",
    "externalAdoptionPacket",
    "finalSchemaDocs",
    "pluginRefreshProof",
]:
    assert report["readinessProof"][key]["status"] == "pass"
assert "release-consume verify" in " ".join(report["releaseProofConsumption"]["commands"])
assert "codex status --strict" in " ".join(report["pluginRefreshProof"]["commands"])
assert "external developer" in report["externalAdoptionPacket"]["supportBoundary"]
assert any("stable v4 product release" in claim.lower() for claim in report["blockedClaims"])
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["scopeBoundary"]["targetAppsReadOnly"] is True
assert report["scopeBoundary"]["privateAppsUsed"] is False
assert report["scopeBoundary"]["doesNotPublishRelease"] is True
assert "product release" in report["resultUX"]["priorityAction"].lower()
PY

echo "v4 release-candidate test passed"
