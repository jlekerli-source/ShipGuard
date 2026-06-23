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
grep -q 'Fresh Install Package Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Upgrade Package Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Rollback Package Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Release Proof Consumption' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'GitHub Release Asset Download' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Published Release Asset Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'External Adoption Packet' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'External Adoption Evidence' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Security Review Evidence' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Plugin Refresh Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Blocked Claims' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Scope Boundary' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"

grep -q '"tool": "shipguard v4 release-candidate"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"surface": "ShipGuard V4 Release Candidate Readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"status": "pass"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"productStage": "v4-release-candidate-readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"readinessProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"installProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"freshInstallPackageProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"upgradeProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"upgradePackageProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"uninstallProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"rollbackPackageProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"releaseProofConsumption":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"githubReleaseAssetDownloadProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"publishedReleaseAssetProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"externalAdoptionPacket":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"externalAdoptionEvidenceProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"securityReviewEvidenceProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
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
assert report["releaseReadiness"]["freshInstallPackageProof"] == "not-provided"
assert report["releaseReadiness"]["upgradePackageProof"] == "not-provided"
assert report["releaseReadiness"]["rollbackPackageProof"] == "not-provided"
assert report["releaseReadiness"]["githubReleaseAssetDownloadProof"] == "not-requested"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "not-provided"
assert report["releaseReadiness"]["externalAdoptionEvidenceProof"] == "not-provided"
assert report["releaseReadiness"]["externalAdoptionEvidenceStableGate"] == "not-provided"
assert report["releaseReadiness"]["securityReviewEvidenceProof"] == "not-provided"
assert report["releaseReadiness"]["securityReviewEvidenceStableGate"] == "not-provided"
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
assert report["freshInstallPackageProof"]["status"] == "not-provided"
assert report["freshInstallPackageProof"]["provided"] is False
assert report["freshInstallPackageProof"]["requiredForStableV4"] is True
assert "--package-tarball <release-tarball>" in report["freshInstallPackageProof"]["nextCommand"]
assert "--package-tarball <release-tarball>" in report["resultUX"]["nextCommand"]
assert report["upgradePackageProof"]["status"] == "not-provided"
assert report["upgradePackageProof"]["provided"] is False
assert report["upgradePackageProof"]["requiredForStableV4"] is True
assert "--upgrade-from-tarball <previous-release-tarball>" in report["upgradePackageProof"]["nextCommand"]
assert report["rollbackPackageProof"]["status"] == "not-provided"
assert report["rollbackPackageProof"]["provided"] is False
assert report["rollbackPackageProof"]["requiredForStableV4"] is True
assert report["publishedReleaseAssetProof"]["status"] == "not-provided"
assert report["publishedReleaseAssetProof"]["provided"] is False
assert report["publishedReleaseAssetProof"]["requiredForStableV4"] is True
assert "--release-assets <downloaded-assets-dir>" in report["publishedReleaseAssetProof"]["nextCommand"]
assert report["githubReleaseAssetDownloadProof"]["status"] == "not-requested"
assert report["githubReleaseAssetDownloadProof"]["requested"] is False
assert "--download-release-assets" in report["githubReleaseAssetDownloadProof"]["nextCommand"]
assert report["externalAdoptionEvidenceProof"]["status"] == "not-provided"
assert report["externalAdoptionEvidenceProof"]["provided"] is False
assert report["externalAdoptionEvidenceProof"]["requiredForStableV4"] is True
assert "--external-adoption-evidence <evidence-json-or-dir>" in report["externalAdoptionEvidenceProof"]["nextCommand"]
assert report["securityReviewEvidenceProof"]["status"] == "not-provided"
assert report["securityReviewEvidenceProof"]["provided"] is False
assert report["securityReviewEvidenceProof"]["requiredForStableV4"] is True
assert "--security-review-evidence <evidence-json-or-dir>" in report["securityReviewEvidenceProof"]["nextCommand"]
assert "codex status --strict" in " ".join(report["pluginRefreshProof"]["commands"])
assert "external developer" in report["externalAdoptionPacket"]["supportBoundary"]
assert any("stable v4 product release" in claim.lower() for claim in report["blockedClaims"])
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["scopeBoundary"]["targetAppsReadOnly"] is True
assert report["scopeBoundary"]["privateAppsUsed"] is False
assert report["scopeBoundary"]["doesNotPublishRelease"] is True
assert "fresh-install receipt" in report["resultUX"]["priorityAction"].lower()
PY

version="$(sed -n '1p' VERSION)"
mkdir -p "$tmp_dir/adoption"
cat > "$tmp_dir/adoption/synthetic-adoption.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "external-user-install",
  "evidenceClass": "public-fixture",
  "actorRelationship": "independent",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "consentToShare": true,
  "fixtureSynthetic": true,
  "actor": "synthetic external reviewer fixture",
  "source": "public ShipGuard fixture",
  "commands": [
    "shipguard version",
    "shipguard v4 release-candidate --path . --out /tmp/fixture --shipguard-eval --shareable"
  ],
  "artifacts": [
    "consumer-report.json",
    "v4-release-candidate.json"
  ],
  "outcome": "Synthetic fixture proves the adoption evidence schema without claiming real adoption.",
  "nonClaims": [
    "This fixture is not real external adoption.",
    "This fixture does not claim stable v4 or marketplace acceptance."
  ]
}
JSON
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/synthetic-adoption" \
  --external-adoption-evidence "$tmp_dir/adoption" \
  --shipguard-eval \
  --shareable
python3 - "$tmp_dir/synthetic-adoption/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
proof = report["externalAdoptionEvidenceProof"]
attachment = proof["adoptionGateAttachment"]
assert report["status"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceProof"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceStableGate"] == "review"
assert proof["status"] == "pass"
assert proof["stableV4GateStatus"] == "review"
assert proof["evidenceInputs"] == ["<external-adoption-evidence>"]
assert proof["evidenceRecordCount"] == 1
assert proof["validRecordCount"] == 1
assert proof["stableV4EligibleEvidenceCount"] == 0
assert proof["records"][0]["path"] == "<external-adoption-evidence>/synthetic-adoption.json"
assert proof["records"][0]["stableV4Eligible"] is False
assert "none of the records are stable-v4 eligible" in proof["summary"]
assert attachment["status"] == "pass"
assert attachment["stableV4GateStatus"] == "review"
assert attachment["stableV4EligibleEvidenceCount"] == 0
assert attachment["stableV4IneligibleEvidenceCount"] == 1
assert attachment["firstStableV4IneligibleRecord"]["path"] == "<external-adoption-evidence>/synthetic-adoption.json"
assert "not stable-v4 eligible" in attachment["firstStableV4IneligibleRecord"]["reason"]
assert attachment["firstStableV4IneligibleRecord"]["fixtureSynthetic"] is True
assert "public-external" in attachment["acceptedEvidenceClasses"]
assert "private-redacted-external" in attachment["acceptedEvidenceClasses"]
assert "actorRelationship" in attachment["requiredFields"]
assert attachment["proofBoundary"]["fixtureSyntheticProofCounts"] is False
assert attachment["proofBoundary"]["githubDownloadCountsAsAdoption"] is False
PY
if grep -R -F -q "$tmp_dir/adoption" "$tmp_dir/synthetic-adoption"; then
  echo "shareable v4 release-candidate output must redact adoption evidence paths" >&2
  exit 1
fi

mkdir -p "$tmp_dir/stable-adoption"
cat > "$tmp_dir/stable-adoption/external-adoption.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "external-user-install",
  "evidenceClass": "public-external",
  "actorRelationship": "independent",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "consentToShare": true,
  "actor": "redacted independent reviewer",
  "source": "public redacted evidence packet",
  "commands": [
    "shipguard version",
    "shipguard v4 release-candidate --path . --out /tmp/redacted --shipguard-eval --shareable"
  ],
  "artifacts": [
    "redacted-consumer-report.json",
    "redacted-v4-release-candidate.json"
  ],
  "outcome": "Redacted independent evidence packet reports that the external install and LaunchKey run completed.",
  "nonClaims": [
    "This evidence does not claim marketplace acceptance.",
    "This evidence does not validate private apps or physical-device iOS behavior."
  ]
}
JSON
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/stable-adoption-report" \
  --external-adoption-evidence "$tmp_dir/stable-adoption/external-adoption.json" \
  --shipguard-eval \
  --shareable
grep -q 'Adoption Gate Attachment' "$tmp_dir/stable-adoption-report/v4-release-candidate.md"
python3 - "$tmp_dir/stable-adoption-report/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
proof = report["externalAdoptionEvidenceProof"]
attachment = proof["adoptionGateAttachment"]
assert report["releaseReadiness"]["externalAdoptionEvidenceProof"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceStableGate"] == "pass"
assert proof["stableV4GateStatus"] == "pass"
assert proof["stableV4EligibleEvidenceCount"] == 1
assert proof["records"][0]["stableV4Eligible"] is True
assert attachment["stableV4GateStatus"] == "pass"
assert attachment["stableV4EligibleEvidenceCount"] == 1
assert attachment["stableV4IneligibleEvidenceCount"] == 0
assert attachment["firstStableV4IneligibleRecord"] == {}
assert attachment["invalidRecordCount"] == 0
assert attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
PY

mkdir -p "$tmp_dir/security"
cat > "$tmp_dir/security/synthetic-security.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "final-security-review",
  "evidenceClass": "public-fixture",
  "reviewerRelationship": "maintainer-security-review",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "consentToShare": true,
  "fixtureSynthetic": true,
  "reviewer": "synthetic security reviewer fixture",
  "source": "public ShipGuard fixture",
  "scope": [
    "cli",
    "plugin",
    "github-actions",
    "release-proof",
    "package-install",
    "redaction-privacy"
  ],
  "methodology": [
    "threat model review",
    "release proof trust-boundary review",
    "redaction/privacy review"
  ],
  "commands": [
    "shipguard validate",
    "shipguard v4 release-candidate --path . --out /tmp/fixture --shipguard-eval --shareable"
  ],
  "artifacts": [
    "security-review.md",
    "threat-model.md",
    "v4-release-candidate.json"
  ],
  "findingsSummary": {
    "criticalOpen": 0,
    "highOpen": 0,
    "mediumOpen": 0
  },
  "outcome": "Synthetic fixture proves the security review evidence schema without claiming real security review.",
  "nonClaims": [
    "This fixture is not a real security review.",
    "This fixture does not claim third-party certification or stable v4."
  ]
}
JSON
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/synthetic-security" \
  --security-review-evidence "$tmp_dir/security" \
  --shipguard-eval \
  --shareable
python3 - "$tmp_dir/synthetic-security/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
proof = report["securityReviewEvidenceProof"]
attachment = proof["securityReviewGateAttachment"]
assert report["status"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceProof"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceStableGate"] == "review"
assert proof["status"] == "pass"
assert proof["stableV4GateStatus"] == "review"
assert proof["evidenceInputs"] == ["<security-review-evidence>"]
assert proof["evidenceRecordCount"] == 1
assert proof["validRecordCount"] == 1
assert proof["stableV4EligibleEvidenceCount"] == 0
assert proof["records"][0]["path"] == "<security-review-evidence>/synthetic-security.json"
assert proof["records"][0]["stableV4Eligible"] is False
assert "none of the records are stable-v4 eligible" in proof["summary"]
assert attachment["status"] == "pass"
assert attachment["stableV4GateStatus"] == "review"
assert attachment["stableV4EligibleEvidenceCount"] == 0
assert "public-security-review" in attachment["acceptedEvidenceClasses"]
assert "private-redacted-security-review" in attachment["acceptedEvidenceClasses"]
assert "maintainer-security-review" in attachment["acceptedReviewerRelationships"]
assert "redaction-privacy" in attachment["requiredScope"]
assert "findingsSummary" in attachment["requiredFields"]
assert attachment["proofBoundary"]["fixtureSyntheticProofCounts"] is False
assert attachment["proofBoundary"]["criticalHighOpenMustBeZero"] is True
PY
if grep -R -F -q "$tmp_dir/security" "$tmp_dir/synthetic-security"; then
  echo "shareable v4 release-candidate output must redact security review evidence paths" >&2
  exit 1
fi

mkdir -p "$tmp_dir/stable-security"
cat > "$tmp_dir/stable-security/security-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "final-security-review",
  "evidenceClass": "private-redacted-security-review",
  "reviewerRelationship": "maintainer-security-review",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "shareableSummaryOnly": true,
  "reviewer": "redacted security reviewer",
  "source": "redacted final security review packet",
  "scope": [
    "cli",
    "plugin",
    "github-actions",
    "release-proof",
    "package-install",
    "redaction-privacy"
  ],
  "methodology": [
    "threat model review",
    "release artifact trust-boundary review",
    "local plugin boundary review",
    "redaction/privacy review"
  ],
  "commands": [
    "shipguard validate",
    "shipguard codex marketplace-readiness --path . --out /tmp/redacted --strict --shareable",
    "shipguard v4 release-candidate --path . --out /tmp/redacted --shipguard-eval --shareable"
  ],
  "artifacts": [
    "redacted-security-review.md",
    "redacted-threat-model.md",
    "redacted-marketplace-readiness.json",
    "redacted-v4-release-candidate.json"
  ],
  "findingsSummary": {
    "criticalOpen": 0,
    "highOpen": 0,
    "mediumOpen": 1
  },
  "outcome": "Redacted final security review packet reports no open critical or high findings for stable-v4 gating surfaces.",
  "nonClaims": [
    "This evidence does not claim third-party certification.",
    "This evidence does not validate private apps or physical-device iOS behavior."
  ]
}
JSON
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/stable-security-report" \
  --security-review-evidence "$tmp_dir/stable-security/security-review.json" \
  --shipguard-eval \
  --shareable
grep -q 'Security Review Gate Attachment' "$tmp_dir/stable-security-report/v4-release-candidate.md"
python3 - "$tmp_dir/stable-security-report/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
proof = report["securityReviewEvidenceProof"]
attachment = proof["securityReviewGateAttachment"]
assert report["releaseReadiness"]["securityReviewEvidenceProof"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceStableGate"] == "pass"
assert proof["stableV4GateStatus"] == "pass"
assert proof["stableV4EligibleEvidenceCount"] == 1
assert proof["records"][0]["stableV4Eligible"] is True
assert proof["records"][0]["criticalOpen"] == 0
assert proof["records"][0]["highOpen"] == 0
assert attachment["stableV4GateStatus"] == "pass"
assert attachment["stableV4EligibleEvidenceCount"] == 1
assert attachment["invalidRecordCount"] == 0
assert attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
PY
SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit 0123456789abcdef \
    --ci-run-url "https://github.com/jlekerli-source/ShipGuard/actions/runs/123" \
    --release-url "https://github.com/jlekerli-source/ShipGuard/releases/tag/v$version" \
    --issue-url "https://github.com/jlekerli-source/ShipGuard/issues/99" >/dev/null

mkdir -p "$tmp_dir/downloaded"
cp "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/release-manifest.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/index/release-index.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/proof-ledger.md" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/replay/replay-report.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation-badge.json" "$tmp_dir/downloaded/"

old_version="0.0.0"
mkdir -p "$tmp_dir/old-package-work"
tar -xzf "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" -C "$tmp_dir/old-package-work"
printf '%s\n' "$old_version" > "$tmp_dir/old-package-work/shipguard-v$version/VERSION"
(cd "$tmp_dir/old-package-work" && COPYFILE_DISABLE=1 tar -czf "$tmp_dir/shipguard-v$old_version.tar.gz" "shipguard-v$version")

SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard v4 release-candidate \
    --path . \
    --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
    --upgrade-from-tarball "$tmp_dir/shipguard-v$old_version.tar.gz" \
    --fresh-install-prefix "$tmp_dir/fresh-prefix" \
    --fresh-install-work-dir "$tmp_dir/fresh-work" \
    --upgrade-prefix "$tmp_dir/upgrade-prefix" \
    --upgrade-work-dir "$tmp_dir/upgrade-work" \
    --rollback-prefix "$tmp_dir/rollback-prefix" \
    --rollback-work-dir "$tmp_dir/rollback-work" \
    --out "$tmp_dir/with-assets" \
    --release-assets "$tmp_dir/downloaded" \
    --release-version "$version" \
    --release-consume-out "$tmp_dir/with-assets-consume" \
    --external-adoption-evidence "$tmp_dir/stable-adoption/external-adoption.json" \
    --shipguard-eval \
    --shareable

test -f "$tmp_dir/with-assets/v4-release-candidate.json"
test -f "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Fresh Install Proof Attachment' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Fresh Install Receipt Handoff' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Upgrade Proof Attachment' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Upgrade Receipt Handoff' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Rollback Proof Attachment' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Rollback Receipt Handoff' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Release Asset Proof Attachment' "$tmp_dir/with-assets/v4-release-candidate.md"
grep -q 'Release Asset Receipt Handoff' "$tmp_dir/with-assets/v4-release-candidate.md"
test -f "$tmp_dir/with-assets-consume/consumer-report.json"
test -f "$tmp_dir/with-assets-consume/asset-digests.json"
test -x "$tmp_dir/fresh-prefix/bin/shipguard"
test -x "$tmp_dir/upgrade-prefix/bin/shipguard"
test ! -e "$tmp_dir/rollback-prefix/bin/shipguard"
test ! -e "$tmp_dir/rollback-prefix/bin/codex-maintainer"
test ! -e "$tmp_dir/rollback-prefix/lib/shipguard"

python3 - "$tmp_dir/with-assets/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
fresh = report["freshInstallPackageProof"]
fresh_attachment = fresh["freshInstallProofAttachment"]
fresh_handoff = fresh_attachment["receiptHandoff"]
upgrade = report["upgradePackageProof"]
upgrade_attachment = upgrade["upgradeProofAttachment"]
upgrade_handoff = upgrade_attachment["receiptHandoff"]
rollback = report["rollbackPackageProof"]
rollback_attachment = rollback["rollbackProofAttachment"]
rollback_handoff = rollback_attachment["receiptHandoff"]
proof = report["publishedReleaseAssetProof"]
attachment = proof["releaseAssetProofAttachment"]
release_asset_handoff = attachment["receiptHandoff"]
adoption = report["externalAdoptionEvidenceProof"]
security = report["securityReviewEvidenceProof"]
assert report["status"] == "pass"
assert report["releaseReadiness"]["freshInstallPackageProof"] == "pass"
assert report["releaseReadiness"]["upgradePackageProof"] == "pass"
assert report["releaseReadiness"]["rollbackPackageProof"] == "pass"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceProof"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceStableGate"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceProof"] == "not-provided"
assert report["releaseReadiness"]["securityReviewEvidenceStableGate"] == "not-provided"
assert fresh["status"] == "pass"
assert fresh["provided"] is True
assert fresh["installedVersion"] == report["version"]
assert fresh["installedLegacyVersion"] == report["version"]
assert fresh["forbiddenInstalledPathCount"] == 0
assert fresh["packageTarball"] == "<package-tarball>"
assert fresh["installPrefix"] == "<fresh-install-prefix>"
assert fresh["workDir"] == "<fresh-install-work-dir>"
assert fresh["packageRoot"] == "<fresh-install-package-root>"
assert fresh["installedRoot"] == "<fresh-install-root>"
assert fresh["versionResult"]["exitCode"] == 0
assert fresh["legacyVersionResult"]["exitCode"] == 0
assert fresh["validateResult"]["exitCode"] == 0
assert fresh_attachment["status"] == "pass"
assert fresh_attachment["packageTarball"] == "<package-tarball>"
assert fresh_attachment["installPrefix"] == "<fresh-install-prefix>"
assert fresh_attachment["workDir"] == "<fresh-install-work-dir>"
assert fresh_attachment["packageRoot"] == "<fresh-install-package-root>"
assert fresh_attachment["installedRoot"] == "<fresh-install-root>"
assert fresh_attachment["installedVersion"] == report["version"]
assert fresh_attachment["installedLegacyVersion"] == report["version"]
assert fresh_attachment["versionExitCode"] == 0
assert fresh_attachment["legacyVersionExitCode"] == 0
assert fresh_attachment["validateExitCode"] == 0
assert fresh_attachment["forbiddenInstalledPathCount"] == 0
assert fresh_attachment["missingProofArtifacts"] == []
assert fresh_attachment["proofBoundary"]["shipguardValidateRequired"] is True
assert fresh_attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
assert fresh_handoff["receipt"] == "freshInstallPackageProof"
assert fresh_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert fresh_handoff["packageTarball"] == "<package-tarball>"
assert fresh_handoff["installPrefix"] == "<fresh-install-prefix>"
assert fresh_handoff["installedRoot"] == "<fresh-install-root>"
assert "shipguard-validate" in fresh_handoff["proofArtifacts"]
assert fresh_handoff["missingProofArtifacts"] == []
assert "--release-candidate-report <v4-release-candidate-json-or-dir>" in fresh_handoff["stablePublicationCommand"]
assert fresh_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert fresh_handoff["proofBoundary"]["installPrefixAloneCountsAsStableV4Proof"] is False
assert fresh_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert upgrade["status"] == "pass"
assert upgrade["provided"] is True
assert upgrade["previousPackageVersion"] == "0.0.0"
assert upgrade["previousInstalledVersion"] == "0.0.0"
assert upgrade["previousInstalledLegacyVersion"] == "0.0.0"
assert upgrade["upgradedVersion"] == report["version"]
assert upgrade["upgradedLegacyVersion"] == report["version"]
assert upgrade["forbiddenInstalledPathCount"] == 0
assert upgrade["previousTarball"] == "<previous-package-tarball>"
assert upgrade["candidateTarball"] == "<package-tarball>"
assert upgrade["upgradePrefix"] == "<upgrade-prefix>"
assert upgrade["workDir"] == "<upgrade-work-dir>"
assert upgrade["previousPackageRoot"] == "<previous-package-root>"
assert upgrade["candidatePackageRoot"] == "<candidate-package-root>"
assert upgrade["installedRoot"] == "<upgrade-installed-root>"
assert upgrade["previousVersionResult"]["exitCode"] == 0
assert upgrade["upgradedVersionResult"]["exitCode"] == 0
assert upgrade["upgradedLegacyVersionResult"]["exitCode"] == 0
assert upgrade["validateResult"]["exitCode"] == 0
assert upgrade_attachment["status"] == "pass"
assert upgrade_attachment["previousTarball"] == "<previous-package-tarball>"
assert upgrade_attachment["candidateTarball"] == "<package-tarball>"
assert upgrade_attachment["upgradePrefix"] == "<upgrade-prefix>"
assert upgrade_attachment["workDir"] == "<upgrade-work-dir>"
assert upgrade_attachment["previousPackageVersion"] == "0.0.0"
assert upgrade_attachment["upgradedVersion"] == report["version"]
assert upgrade_attachment["upgradedLegacyVersion"] == report["version"]
assert upgrade_attachment["validateExitCode"] == 0
assert upgrade_attachment["forbiddenInstalledPathCount"] == 0
assert upgrade_attachment["missingProofArtifacts"] == []
assert upgrade_attachment["proofBoundary"]["samePrefixUpgradeRequiredForStableV4"] is True
assert upgrade_attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
assert upgrade_handoff["receipt"] == "upgradePackageProof"
assert upgrade_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert upgrade_handoff["previousTarball"] == "<previous-package-tarball>"
assert upgrade_handoff["candidateTarball"] == "<package-tarball>"
assert upgrade_handoff["upgradePrefix"] == "<upgrade-prefix>"
assert upgrade_handoff["installedRoot"] == "<upgrade-installed-root>"
assert "shipguard-validate" in upgrade_handoff["proofArtifacts"]
assert upgrade_handoff["missingProofArtifacts"] == []
assert "--release-candidate-report <v4-release-candidate-json-or-dir>" in upgrade_handoff["stablePublicationCommand"]
assert upgrade_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert upgrade_handoff["proofBoundary"]["upgradePrefixAloneCountsAsStableV4Proof"] is False
assert upgrade_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert rollback["status"] == "pass"
assert rollback["provided"] is True
assert rollback["installedVersion"] == report["version"]
assert rollback["removedPathCount"] == 3
assert rollback["remainingPathCount"] == 0
assert rollback["packageTarball"] == "<package-tarball>"
assert rollback["rollbackPrefix"] == "<rollback-prefix>"
assert rollback["workDir"] == "<rollback-work-dir>"
assert rollback["packageRoot"] == "<rollback-package-root>"
assert rollback["installedRoot"] == "<rollback-installed-root>"
assert rollback_attachment["status"] == "pass"
assert rollback_attachment["packageTarball"] == "<package-tarball>"
assert rollback_attachment["rollbackPrefix"] == "<rollback-prefix>"
assert rollback_attachment["workDir"] == "<rollback-work-dir>"
assert rollback_attachment["installedVersion"] == report["version"]
assert rollback_attachment["versionExitCode"] == 0
assert rollback_attachment["removedPathCount"] == 3
assert rollback_attachment["remainingPathCount"] == 0
assert rollback_attachment["missingProofArtifacts"] == []
assert rollback_attachment["proofBoundary"]["rollbackCleanupRequiredForStableV4"] is True
assert rollback_attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
assert rollback_handoff["receipt"] == "rollbackPackageProof"
assert rollback_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert rollback_handoff["packageTarball"] == "<package-tarball>"
assert rollback_handoff["rollbackPrefix"] == "<rollback-prefix>"
assert rollback_handoff["installedRoot"] == "<rollback-installed-root>"
assert "removed-package-paths" in rollback_handoff["proofArtifacts"]
assert rollback_handoff["missingProofArtifacts"] == []
assert "--release-candidate-report <v4-release-candidate-json-or-dir>" in rollback_handoff["stablePublicationCommand"]
assert rollback_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert rollback_handoff["proofBoundary"]["rollbackPrefixAloneCountsAsStableV4Proof"] is False
assert rollback_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert proof["status"] == "pass"
assert proof["provided"] is True
assert proof["downloadSource"] == "supplied-directory"
assert proof["downloadProofStatus"] == "not-requested"
assert proof["consumerReportStatus"] == "pass"
assert proof["replayStatus"] == "pass"
assert proof["attestationStatus"] == "pass"
assert proof["consumerReportPath"] == "<release-consume-out>/consumer-report.json"
assert proof["assetDigestMatrixPath"] == "<release-consume-out>/asset-digests.json"
assert proof["assetsDir"] == "<release-assets>"
assert proof["consumeOut"] == "<release-consume-out>"
assert attachment["status"] == "pass"
assert attachment["downloadSource"] == "supplied-directory"
assert attachment["consumerReportPath"] == "<release-consume-out>/consumer-report.json"
assert attachment["assetDigestMatrixPath"] == "<release-consume-out>/asset-digests.json"
assert attachment["missingProofArtifacts"] == []
assert attachment["proofBoundary"]["releaseConsumeVerificationRequired"] is True
assert attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
assert attachment["proofBoundary"]["fixtureProofCountsAsStableV4PublicationProof"] is False
assert release_asset_handoff["receipt"] == "publishedReleaseAssetProof"
assert release_asset_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert release_asset_handoff["assetsDir"] == "<release-assets>"
assert release_asset_handoff["consumeOut"] == "<release-consume-out>"
assert release_asset_handoff["consumerReportPath"] == "<release-consume-out>/consumer-report.json"
assert release_asset_handoff["assetDigestMatrixPath"] == "<release-consume-out>/asset-digests.json"
assert "release-consume-verification" in release_asset_handoff["proofArtifacts"]
assert release_asset_handoff["missingProofArtifacts"] == []
assert "--release-candidate-report <v4-release-candidate-json-or-dir>" in release_asset_handoff["stablePublicationCommand"]
assert release_asset_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert release_asset_handoff["proofBoundary"]["releaseAssetsDirectoryAloneCountsAsStableV4Proof"] is False
assert release_asset_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert adoption["status"] == "pass"
assert adoption["stableV4GateStatus"] == "pass"
assert adoption["evidenceInputs"][0].startswith("<external-adoption-evidence>")
assert security["status"] == "not-provided"
assert "--security-review-evidence <evidence-json-or-dir>" in report["resultUX"]["nextCommand"]
questions = report["reportQualityQuestions"]
assert not any("fresh user install, upgrade, uninstall" in question for question in questions)
assert questions[0] == "Which final security review evidence can be attached without leaking private data, hiding critical/high findings, or claiming stable v4 too early?"
PY

SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard v4 release-candidate \
    --path . \
    --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
    --upgrade-from-tarball "$tmp_dir/shipguard-v$old_version.tar.gz" \
    --fresh-install-prefix "$tmp_dir/fresh-security-prefix" \
    --fresh-install-work-dir "$tmp_dir/fresh-security-work" \
    --upgrade-prefix "$tmp_dir/upgrade-security-prefix" \
    --upgrade-work-dir "$tmp_dir/upgrade-security-work" \
    --rollback-prefix "$tmp_dir/rollback-security-prefix" \
    --rollback-work-dir "$tmp_dir/rollback-security-work" \
    --out "$tmp_dir/with-assets-and-security" \
    --release-assets "$tmp_dir/downloaded" \
    --release-version "$version" \
    --release-consume-out "$tmp_dir/with-assets-and-security-consume" \
    --external-adoption-evidence "$tmp_dir/stable-adoption/external-adoption.json" \
    --security-review-evidence "$tmp_dir/stable-security/security-review.json" \
    --shipguard-eval \
    --shareable
python3 - "$tmp_dir/with-assets-and-security/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "pass"
assert report["releaseReadiness"]["freshInstallPackageProof"] == "pass"
assert report["releaseReadiness"]["upgradePackageProof"] == "pass"
assert report["releaseReadiness"]["rollbackPackageProof"] == "pass"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "pass"
assert report["releaseReadiness"]["externalAdoptionEvidenceStableGate"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceProof"] == "pass"
assert report["releaseReadiness"]["securityReviewEvidenceStableGate"] == "pass"
assert report["securityReviewEvidenceProof"]["stableV4EligibleEvidenceCount"] == 1
assert report["securityReviewEvidenceProof"]["securityReviewGateAttachment"]["stableV4GateStatus"] == "pass"
assert "--profile release" in report["resultUX"]["nextCommand"]
assert "--release-url <release-url>" in report["resultUX"]["nextCommand"]
assert "final stable-v4 release proof packet" in report["resultUX"]["priorityAction"]
PY

api_root="$tmp_dir/github-api"
release_endpoint_file="$api_root/repos/jlekerli-source/ShipGuard/releases/tags/v$version"
mkdir -p "$(dirname "$release_endpoint_file")"
python3 - "$release_endpoint_file" "$version" "$tmp_dir/downloaded" <<'PY'
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
version = sys.argv[2]
downloaded = Path(sys.argv[3])
asset_names = [
    f"shipguard-v{version}.tar.gz",
    "release-manifest.json",
    "release-index.json",
    "proof-ledger.md",
    "replay-report.json",
    "attestation.json",
    "attestation-badge.json",
]
target.write_text(
    json.dumps(
        {
            "tag_name": f"v{version}",
            "html_url": f"https://github.com/jlekerli-source/ShipGuard/releases/tag/v{version}",
            "assets": [
                {
                    "name": name,
                    "browser_download_url": (downloaded / name).as_uri(),
                }
                for name in asset_names
            ],
        }
    ),
    encoding="utf-8",
)
PY

SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard v4 release-candidate \
    --path . \
    --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
    --upgrade-from-tarball "$tmp_dir/shipguard-v$old_version.tar.gz" \
    --fresh-install-prefix "$tmp_dir/native-fresh-prefix" \
    --fresh-install-work-dir "$tmp_dir/native-fresh-work" \
    --upgrade-prefix "$tmp_dir/native-upgrade-prefix" \
    --upgrade-work-dir "$tmp_dir/native-upgrade-work" \
    --rollback-prefix "$tmp_dir/native-rollback-prefix" \
    --rollback-work-dir "$tmp_dir/native-rollback-work" \
    --out "$tmp_dir/native-assets" \
    --download-release-assets \
    --github-release-repo jlekerli-source/ShipGuard \
    --github-api-url "file://$api_root" \
    --release-version "$version" \
    --shipguard-eval \
    --shareable

test -f "$tmp_dir/native-assets/v4-release-candidate.json"
test -f "$tmp_dir/native-assets/v4-release-candidate.md"
test -f "$tmp_dir/native-assets/downloaded-release-assets/release-manifest.json"
test -f "$tmp_dir/native-assets/release-consume/consumer-report.json"
grep -q 'Download Proof Attachment' "$tmp_dir/native-assets/v4-release-candidate.md"
grep -q 'Download Receipt Handoff' "$tmp_dir/native-assets/v4-release-candidate.md"

SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard v4 release-candidate \
    --path . \
    --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
    --upgrade-from-tarball "$tmp_dir/shipguard-v$old_version.tar.gz" \
    --fresh-install-prefix "$tmp_dir/native-fresh-prefix-rerun" \
    --fresh-install-work-dir "$tmp_dir/native-fresh-work-rerun" \
    --upgrade-prefix "$tmp_dir/native-upgrade-prefix-rerun" \
    --upgrade-work-dir "$tmp_dir/native-upgrade-work-rerun" \
    --rollback-prefix "$tmp_dir/native-rollback-prefix-rerun" \
    --rollback-work-dir "$tmp_dir/native-rollback-work-rerun" \
    --out "$tmp_dir/native-assets" \
    --download-release-assets \
    --github-release-repo jlekerli-source/ShipGuard \
    --github-api-url "file://$api_root" \
    --release-version "$version" \
    --shipguard-eval \
    --shareable

grep -q '"githubReleaseAssetDownloadProof": "pass"' "$tmp_dir/native-assets/v4-release-candidate.json"

python3 - "$tmp_dir/native-assets/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
download = report["githubReleaseAssetDownloadProof"]
download_attachment = download["downloadProofAttachment"]
download_handoff = download_attachment["receiptHandoff"]
proof = report["publishedReleaseAssetProof"]
attachment = proof["releaseAssetProofAttachment"]
release_asset_handoff = attachment["receiptHandoff"]
assert report["status"] == "pass"
assert report["releaseReadiness"]["githubReleaseAssetDownloadProof"] == "pass"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "pass"
assert download["status"] == "pass"
assert download["requested"] is True
assert download["repo"] == "jlekerli-source/ShipGuard"
assert download["downloadDir"] == "<downloaded-release-assets>"
assert download["apiUrl"] == "<github-api-url>"
assert download["releaseEndpoint"] == "<github-release-endpoint>"
assert download["assetCount"] == 7
assert all(asset["path"].startswith("<downloaded-release-assets>/") for asset in download["downloadedAssets"])
assert all(asset["source"].startswith("<github-asset-url>/") for asset in download["downloadedAssets"])
assert download_attachment["status"] == "pass"
assert download_attachment["repo"] == "jlekerli-source/ShipGuard"
assert download_attachment["tag"] == f"v{report['version']}"
assert download_attachment["downloadDir"] == "<downloaded-release-assets>"
assert download_attachment["apiUrl"] == "<github-api-url>"
assert download_attachment["releaseEndpoint"] == "<github-release-endpoint>"
assert download_attachment["assetCount"] == 7
assert len(download_attachment["downloadedAssetNames"]) == 7
assert len(download_attachment["downloadedAssetDigests"]) == 7
assert download_attachment["proofBoundary"]["releaseConsumeStillRequiredForStableV4"] is True
assert download_attachment["proofBoundary"]["sourceOnlyProofCounts"] is False
assert download_handoff["receipt"] == "githubReleaseAssetDownloadProof"
assert download_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert download_handoff["repo"] == "jlekerli-source/ShipGuard"
assert download_handoff["tag"] == f"v{report['version']}"
assert download_handoff["downloadDir"] == "<downloaded-release-assets>"
assert download_handoff["releaseEndpoint"] == "<github-release-endpoint>"
assert "downloaded-asset-sha256" in download_handoff["proofArtifacts"]
assert download_handoff["missingProofArtifacts"] == []
assert "--release-candidate-report <v4-release-candidate-json>" in download_handoff["stablePublicationCommand"]
assert "--github-release-repo jlekerli-source/ShipGuard" in download_handoff["stablePublicationCommand"]
assert f"--release-version {report['version']}" in download_handoff["stablePublicationCommand"]
assert "--release-assets <downloaded-release-assets>" in download_handoff["stablePublicationCommand"]
assert "--external-adoption-evidence <adoption-evidence-json-or-dir>" in download_handoff["stablePublicationCommand"]
assert "--security-review-evidence <security-review-json-or-dir>" in download_handoff["stablePublicationCommand"]
assert "--download-release-assets" not in download_handoff["stablePublicationCommand"]
assert download_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert download_handoff["proofBoundary"]["downloadDirectoryAloneCountsAsStableV4Proof"] is False
assert download_handoff["proofBoundary"]["releaseConsumeStillRequiredForStableV4"] is True
assert download_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert proof["status"] == "pass"
assert proof["downloadSource"] == "github-release-assets"
assert proof["downloadProofStatus"] == "pass"
assert proof["assetsDir"] == "<downloaded-release-assets>"
assert proof["consumerReportStatus"] == "pass"
assert proof["replayStatus"] == "pass"
assert proof["attestationStatus"] == "pass"
assert attachment["status"] == "pass"
assert attachment["downloadSource"] == "github-release-assets"
assert attachment["consumerReportPath"] == "<release-consume-out>/consumer-report.json"
assert attachment["assetDigestMatrixPath"] == "<release-consume-out>/asset-digests.json"
assert attachment["missingProofArtifacts"] == []
assert release_asset_handoff["receipt"] == "publishedReleaseAssetProof"
assert release_asset_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert release_asset_handoff["assetsDir"] == "<downloaded-release-assets>"
assert release_asset_handoff["consumeOut"] == "<release-consume-out>"
assert "release-consume-verification" in release_asset_handoff["proofArtifacts"]
assert release_asset_handoff["missingProofArtifacts"] == []
assert release_asset_handoff["proofBoundary"]["releaseAssetsDirectoryAloneCountsAsStableV4Proof"] is False
PY

if grep -R -F -q "$api_root" "$tmp_dir/native-assets"; then
  echo "shareable v4 release-candidate output must redact local GitHub API fixture paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/native-assets/downloaded-release-assets" "$tmp_dir/native-assets/v4-release-candidate.json" "$tmp_dir/native-assets/v4-release-candidate.md"; then
  echo "shareable v4 release-candidate output must redact native download directory paths" >&2
  exit 1
fi

if grep -R -F -q "$tmp_dir/downloaded" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact release asset paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/with-assets-consume" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact release-consume paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/fresh-prefix" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact fresh install prefix paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/fresh-work" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact fresh install work paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/upgrade-prefix" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact upgrade prefix paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/upgrade-work" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact upgrade work paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/rollback-prefix" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact rollback prefix paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/rollback-work" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact rollback work paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/shipguard-v$old_version.tar.gz" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact previous package tarball paths" >&2
  exit 1
fi

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-tarball" \
  --package-tarball "$tmp_dir/does-not-exist.tar.gz" \
  --json >/dev/null 2>&1; then
  echo "expected missing package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-tarball/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-tarball/v4-release-candidate.json"
grep -q '"freshInstallPackageProof": "blocked"' "$tmp_dir/missing-tarball/v4-release-candidate.json"

mkdir -p "$tmp_dir/unsafe-package/shipguard-v$version/scripts"
printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp_dir/unsafe-package/shipguard-v$version/scripts/install.sh"
ln -s /tmp "$tmp_dir/unsafe-package/shipguard-v$version/unsafe-link"
(cd "$tmp_dir/unsafe-package" && COPYFILE_DISABLE=1 tar -czf "$tmp_dir/unsafe-package.tar.gz" "shipguard-v$version")
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/unsafe-tarball" \
  --package-tarball "$tmp_dir/unsafe-package.tar.gz" \
  --json >/dev/null 2>&1; then
  echo "expected unsafe package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/unsafe-tarball/v4-release-candidate.json"
grep -q '"freshInstallPackageProof": "blocked"' "$tmp_dir/unsafe-tarball/v4-release-candidate.json"
grep -q 'unsafe tarball member is a link or device' "$tmp_dir/unsafe-tarball/v4-release-candidate.json"

mkdir -p "$tmp_dir/appledouble-package/shipguard-v$version/scripts"
printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp_dir/appledouble-package/shipguard-v$version/scripts/install.sh"
printf 'sidecar metadata\n' > "$tmp_dir/appledouble-package/shipguard-v$version/scripts/._install.sh"
(cd "$tmp_dir/appledouble-package" && COPYFILE_DISABLE=1 tar -czf "$tmp_dir/appledouble-package.tar.gz" "shipguard-v$version")
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/appledouble-tarball" \
  --package-tarball "$tmp_dir/appledouble-package.tar.gz" \
  --shipguard-eval \
  --json >/dev/null 2>&1; then
  echo "expected AppleDouble package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/appledouble-tarball/v4-release-candidate.json"
grep -q '"freshInstallPackageProof": "blocked"' "$tmp_dir/appledouble-tarball/v4-release-candidate.json"
grep -q '"blockingProof":' "$tmp_dir/appledouble-tarball/v4-release-candidate.json"
grep -q '"receipt": "freshInstallPackageProof"' "$tmp_dir/appledouble-tarball/v4-release-candidate.json"
grep -q 'unsafe tarball member is generated metadata/cache' "$tmp_dir/appledouble-tarball/v4-release-candidate.json"
grep -q 'Rebuild the release package with ./scripts/package_release.sh' "$tmp_dir/appledouble-tarball/v4-release-candidate.json"

mkdir -p "$tmp_dir/appledouble-previous/shipguard-v$old_version/scripts" "$tmp_dir/appledouble-previous/shipguard-v$old_version/bin"
printf '%s\n' "$old_version" > "$tmp_dir/appledouble-previous/shipguard-v$old_version/VERSION"
printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp_dir/appledouble-previous/shipguard-v$old_version/scripts/install.sh"
printf '#!/usr/bin/env bash\nprintf "%s\\n" "0.0.0"\n' > "$tmp_dir/appledouble-previous/shipguard-v$old_version/bin/shipguard"
printf 'sidecar metadata\n' > "$tmp_dir/appledouble-previous/shipguard-v$old_version/scripts/._install.sh"
mkdir -p "$tmp_dir/appledouble-previous-package"
(cd "$tmp_dir/appledouble-previous" && COPYFILE_DISABLE=1 tar -czf "$tmp_dir/appledouble-previous-package/shipguard-v$old_version.tar.gz" "shipguard-v$old_version")
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/appledouble-previous-upgrade" \
  --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
  --upgrade-from-tarball "$tmp_dir/appledouble-previous-package/shipguard-v$old_version.tar.gz" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected AppleDouble previous package to fail upgrade proof" >&2
  exit 1
fi
test -f "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json"
test -f "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.md"
grep -q '"upgradePackageProof": "blocked"' "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json"
grep -q '"packageHygieneEvidence":' "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json"
grep -q 'appledouble-sidecar' "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json"
grep -q 'shipguard release-package hygiene' "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json"
grep -q 'Package hygiene status' "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.md"
python3 - "$tmp_dir/appledouble-previous-upgrade/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
proof = report["upgradePackageProof"]
hygiene = proof["packageHygieneEvidence"]
blocking = report["blockingProof"]
assert proof["status"] == "blocked"
assert proof["previousExtractStatus"] == "blocked"
assert hygiene["status"] == "blocked"
assert hygiene["blockedFindingCount"] >= 1
assert hygiene["firstFinding"]["ruleId"] == "appledouble-sidecar"
assert blocking["receipt"] == "upgradePackageProof"
assert "appledouble-sidecar" in blocking["failureEvidence"]
assert "release-package hygiene" in blocking["nextCommand"]
assert "<previous-package-tarball>" in blocking["nextCommand"]
assert "<package-tarball>" in blocking["nextCommand"]
PY

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-upgrade-tarball" \
  --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
  --upgrade-from-tarball "$tmp_dir/missing-previous.tar.gz" \
  --json >/dev/null 2>&1; then
  echo "expected missing previous package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-upgrade-tarball/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-upgrade-tarball/v4-release-candidate.json"
grep -q '"upgradePackageProof": "blocked"' "$tmp_dir/missing-upgrade-tarball/v4-release-candidate.json"
python3 - "$tmp_dir/missing-upgrade-tarball/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["readinessProof"]["upgrade"]["status"] == "blocked"
assert report["upgradeProof"]["status"] == "blocked"
assert "./scripts/package_release.sh" in report["blockingProof"]["nextCommand"]
assert "./tests/package_release_test.sh" in report["blockingProof"]["nextCommand"]
assert "./tests/v4_release_candidate_test.sh" in report["blockingProof"]["nextCommand"]
PY

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-assets" \
  --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
  --release-assets "$tmp_dir/does-not-exist" \
  --release-version "$version" \
  --json >/dev/null 2>&1; then
  echo "expected missing release assets to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-assets/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-assets/v4-release-candidate.json"
grep -q '"publishedReleaseAssetProof": "blocked"' "$tmp_dir/missing-assets/v4-release-candidate.json"
python3 - "$tmp_dir/missing-assets/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["readinessProof"]["releaseProofConsumption"]["status"] == "blocked"
assert report["releaseProofConsumption"]["status"] == "blocked"
attachment = report["publishedReleaseAssetProof"]["releaseAssetProofAttachment"]
assert attachment["status"] == "blocked"
assert attachment["missingProofArtifacts"] == ["consumer-report.json", "asset-digests.json"]
assert attachment["proofBoundary"]["downloadedOrSuppliedReleaseAssetsRequired"] is True
PY

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-adoption-evidence" \
  --external-adoption-evidence "$tmp_dir/does-not-exist-adoption" \
  --json >/dev/null 2>&1; then
  echo "expected missing external adoption evidence to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-adoption-evidence/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-adoption-evidence/v4-release-candidate.json"
grep -q '"externalAdoptionEvidenceProof": "blocked"' "$tmp_dir/missing-adoption-evidence/v4-release-candidate.json"
grep -q '"receipt": "externalAdoptionEvidenceProof"' "$tmp_dir/missing-adoption-evidence/v4-release-candidate.json"

mkdir -p "$tmp_dir/bad-adoption"
cat > "$tmp_dir/bad-adoption/bad.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "external-user-install",
  "evidenceClass": "public-external",
  "actorRelationship": "maintainer",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": false,
  "commands": [
    "echo no shipguard proof"
  ],
  "artifacts": [],
  "outcome": "bad fixture",
  "nonClaims": []
}
JSON
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/bad-adoption-report" \
  --external-adoption-evidence "$tmp_dir/bad-adoption" \
  --json >/dev/null 2>&1; then
  echo "expected invalid external adoption evidence to fail release-candidate proof" >&2
  exit 1
fi
grep -q '"externalAdoptionEvidenceProof": "blocked"' "$tmp_dir/bad-adoption-report/v4-release-candidate.json"
grep -q 'privateDataRedacted must be true' "$tmp_dir/bad-adoption-report/v4-release-candidate.json"

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-security-evidence" \
  --security-review-evidence "$tmp_dir/does-not-exist-security" \
  --json >/dev/null 2>&1; then
  echo "expected missing security review evidence to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-security-evidence/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-security-evidence/v4-release-candidate.json"
grep -q '"securityReviewEvidenceProof": "blocked"' "$tmp_dir/missing-security-evidence/v4-release-candidate.json"
grep -q '"receipt": "securityReviewEvidenceProof"' "$tmp_dir/missing-security-evidence/v4-release-candidate.json"

mkdir -p "$tmp_dir/bad-security"
cat > "$tmp_dir/bad-security/bad.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "final-security-review",
  "evidenceClass": "public-security-review",
  "reviewerRelationship": "maintainer-security-review",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "scope": [
    "cli",
    "plugin"
  ],
  "methodology": [
    "thin review"
  ],
  "commands": [
    "echo no shipguard proof"
  ],
  "artifacts": [],
  "findingsSummary": {
    "criticalOpen": 0,
    "highOpen": 1
  },
  "outcome": "bad fixture",
  "nonClaims": []
}
JSON
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/bad-security-report" \
  --security-review-evidence "$tmp_dir/bad-security" \
  --json >/dev/null 2>&1; then
  echo "expected invalid security review evidence to fail release-candidate proof" >&2
  exit 1
fi
grep -q '"securityReviewEvidenceProof": "blocked"' "$tmp_dir/bad-security-report/v4-release-candidate.json"
grep -q 'highOpen must be 0' "$tmp_dir/bad-security-report/v4-release-candidate.json"

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/native-missing-repo" \
  --download-release-assets \
  --release-version "$version" \
  --shareable >/dev/null 2>&1; then
  echo "expected native GitHub asset download without repo to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/native-missing-repo/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/native-missing-repo/v4-release-candidate.json"
grep -q '"githubReleaseAssetDownloadProof": "blocked"' "$tmp_dir/native-missing-repo/v4-release-candidate.json"
grep -q '"receipt": "githubReleaseAssetDownloadProof"' "$tmp_dir/native-missing-repo/v4-release-candidate.json"
grep -q 'missing --github-release-repo' "$tmp_dir/native-missing-repo/v4-release-candidate.json"
grep -q 'Download Blocking Proof' "$tmp_dir/native-missing-repo/v4-release-candidate.md"
grep -q 'Download Blocking Receipt Handoff' "$tmp_dir/native-missing-repo/v4-release-candidate.md"
python3 - "$tmp_dir/native-missing-repo/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
download = report["githubReleaseAssetDownloadProof"]
blocking = download["downloadBlockingProof"]
blocking_handoff = blocking["receiptHandoff"]
assert download["status"] == "blocked"
assert blocking["status"] == "blocked"
assert blocking["repo"] == ""
assert blocking["tag"] == f"v{report['version']}"
assert blocking["downloadDir"] == "<downloaded-release-assets>"
assert blocking["error"] == "missing --github-release-repo <owner/repo>"
assert "--download-release-assets" in blocking["nextCommand"]
assert blocking["proofBoundary"]["githubReleaseRepoRequired"] is True
assert blocking["proofBoundary"]["sourceOnlyProofCounts"] is False
assert blocking_handoff["receipt"] == "githubReleaseAssetDownloadProof"
assert blocking_handoff["candidateReportPath"] == "<v4-release-candidate-json>"
assert blocking_handoff["downloadDir"] == "<downloaded-release-assets>"
assert blocking_handoff["failureEvidence"] == "missing --github-release-repo <owner/repo>"
assert "download-error" in blocking_handoff["proofArtifacts"]
assert blocking_handoff["missingProofArtifacts"] == []
assert "--download-release-assets" in blocking_handoff["repairCommand"]
assert "--release-candidate-report <v4-release-candidate-json>" in blocking_handoff["stablePublicationCommand"]
assert "--github-release-repo <owner/repo>" in blocking_handoff["stablePublicationCommand"]
assert f"--release-version {report['version']}" in blocking_handoff["stablePublicationCommand"]
assert "--download-release-assets" in blocking_handoff["stablePublicationCommand"]
assert "--external-adoption-evidence <adoption-evidence-json-or-dir>" in blocking_handoff["stablePublicationCommand"]
assert "--security-review-evidence <security-review-json-or-dir>" in blocking_handoff["stablePublicationCommand"]
assert "--release-assets" not in blocking_handoff["stablePublicationCommand"]
assert blocking_handoff["proofBoundary"]["attachCandidateReportToStablePublication"] is True
assert blocking_handoff["proofBoundary"]["blockedDownloadCountsAsStableV4Proof"] is False
assert blocking_handoff["proofBoundary"]["releaseConsumeStillRequiredForStableV4"] is True
assert blocking_handoff["proofBoundary"]["sourceOnlyProofCounts"] is False
assert report["blockingProof"]["receipt"] == "githubReleaseAssetDownloadProof"
assert report["resultUX"]["blockingProof"]["receipt"] == "githubReleaseAssetDownloadProof"
PY

echo "v4 release-candidate test passed"
