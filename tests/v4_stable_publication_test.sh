#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

version="$(sed -n '1p' VERSION)"
release_commit="$(git rev-parse HEAD)"

./bin/shipguard v4 stable-publication --help >/dev/null

cat > "$tmp_dir/candidate-pass.json" <<JSON
{
  "schemaVersion": 1,
  "tool": "shipguard v4 release-candidate",
  "status": "pass",
  "releaseReadiness": {
    "releaseClaim": "candidate-ready",
    "stableV4Release": false,
    "freshInstallPackageProof": "pass",
    "upgradePackageProof": "pass",
    "rollbackPackageProof": "pass"
  }
}
JSON

cat > "$tmp_dir/candidate-incomplete.json" <<JSON
{
  "schemaVersion": 1,
  "tool": "shipguard v4 release-candidate",
  "status": "pass",
  "releaseReadiness": {
    "releaseClaim": "candidate-ready",
    "stableV4Release": false,
    "freshInstallPackageProof": "not-provided",
    "upgradePackageProof": "not-provided",
    "rollbackPackageProof": "not-provided"
  }
}
JSON

cat > "$tmp_dir/candidate-hygiene-blocked.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard v4 release-candidate",
  "status": "review",
  "releaseReadiness": {
    "releaseClaim": "not-ready",
    "stableV4Release": false,
    "freshInstallPackageProof": "pass",
    "upgradePackageProof": "blocked",
    "rollbackPackageProof": "pass"
  },
  "upgradePackageProof": {
    "status": "blocked",
    "provided": true,
    "requested": true,
    "requiredForStableV4": true,
    "summary": "Previous release package tarball could not be safely extracted.",
    "packageHygieneEvidence": {
      "status": "blocked",
      "tool": "shipguard release-package hygiene",
      "readOnly": true,
      "blockedFindingCount": 782,
      "reviewFindingCount": 0,
      "affectedVersions": ["3.130.0"],
      "safeTarballs": ["shipguard-v3.131.0.tar.gz"],
      "tarballsScanned": 2,
      "nextCommand": "./bin/shipguard release-package hygiene --path . --tarball <previous-package-tarball> --tarball <package-tarball> --out /tmp/shipguard-package-hygiene --shareable",
      "firstFinding": {
        "severity": "blocked",
        "ruleId": "appledouble-sidecar",
        "tarball": "shipguard-v3.130.0.tar.gz",
        "version": "3.130.0",
        "member": "._shipguard-v3.130.0",
        "evidence": "AppleDouble generated metadata sidecar",
        "recommendation": "Rebuild the release package with metadata-disabled packaging, then rerun package release proof and this hygiene report.",
        "proofGuidance": "Run ./scripts/package_release.sh, ./tests/package_release_test.sh, and shipguard release-package hygiene against the rebuilt tarball."
      }
    }
  },
  "blockingProof": {
    "receipt": "upgradePackageProof",
    "status": "blocked",
    "summary": "Supplied previous/candidate package pair failed same-prefix upgrade validation.",
    "failure": "Previous release package tarball could not be safely extracted.",
    "failureEvidence": "appledouble-sidecar in shipguard-v3.130.0.tar.gz: ._shipguard-v3.130.0 (AppleDouble generated metadata sidecar); 782 blocked finding(s)",
    "nextAction": "Rebuild the package pair, verify package release tests, then rerun LaunchKey with --upgrade-from-tarball against the previous release tarball.",
    "nextCommand": "./bin/shipguard release-package hygiene --path . --tarball <previous-package-tarball> --tarball <package-tarball> --out /tmp/shipguard-package-hygiene --shareable",
    "proofSource": "same-prefix package upgrade receipt"
  },
  "resultUX": {
    "status": "review",
    "nextCommand": "./bin/shipguard release-package hygiene --path . --tarball <previous-package-tarball> --tarball <package-tarball> --out /tmp/shipguard-package-hygiene --shareable",
    "blockingProof": {
      "receipt": "upgradePackageProof",
      "status": "blocked",
      "summary": "Supplied previous/candidate package pair failed same-prefix upgrade validation.",
      "failureEvidence": "appledouble-sidecar in shipguard-v3.130.0.tar.gz: ._shipguard-v3.130.0 (AppleDouble generated metadata sidecar); 782 blocked finding(s)",
      "nextCommand": "./bin/shipguard release-package hygiene --path . --tarball <previous-package-tarball> --tarball <package-tarball> --out /tmp/shipguard-package-hygiene --shareable"
    }
  }
}
JSON

mkdir -p "$tmp_dir/evidence/stable-adoption" "$tmp_dir/evidence/stable-security"
cat > "$tmp_dir/evidence/stable-adoption/external-adoption.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "shipguard-external-adoption",
  "evidenceClass": "public-external",
  "actorRelationship": "independent",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "commands": [
    "shipguard version",
    "shipguard validate"
  ],
  "artifacts": [
    "public release assets",
    "consumer-report.json"
  ],
  "outcome": "Independent public fixture user installed and validated ShipGuard from release assets.",
  "nonClaims": [
    "Does not prove OpenAI marketplace acceptance.",
    "Does not include private app validation."
  ],
  "consentToShare": true
}
JSON
cat > "$tmp_dir/evidence/stable-security/security-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "evidenceType": "shipguard-security-review",
  "evidenceClass": "public-security-review",
  "reviewerRelationship": "independent",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "pass",
  "privateDataRedacted": true,
  "scope": {
    "areas": [
      "cli",
      "plugin",
      "github-actions",
      "release-proof",
      "package-install",
      "redaction-privacy"
    ]
  },
  "methodology": [
    "reviewed release proof commands",
    "reviewed package install and redaction boundaries"
  ],
  "commands": [
    "shipguard validate",
    "shipguard codex status --strict"
  ],
  "artifacts": [
    "release proof bundle",
    "plugin status report"
  ],
  "findingsSummary": {
    "criticalOpen": 0,
    "highOpen": 0,
    "mediumOpen": 0,
    "lowOpen": 0
  },
  "nonClaims": [
    "Does not prove marketplace acceptance.",
    "Does not review private target app code."
  ],
  "shareableSummaryOnly": true
}
JSON

mkdir -p "$tmp_dir/evidence/stale-adoption" "$tmp_dir/evidence/stale-security"
cp "$tmp_dir/evidence/stable-adoption/external-adoption.json" "$tmp_dir/evidence/stale-adoption/external-adoption.json"
cp "$tmp_dir/evidence/stable-security/security-review.json" "$tmp_dir/evidence/stale-security/security-review.json"
python3 - "$tmp_dir/evidence/stale-adoption/external-adoption.json" "$tmp_dir/evidence/stale-security/security-review.json" <<'PY'
import json
import sys
from pathlib import Path

for raw in sys.argv[1:]:
    path = Path(raw)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["generatedAt"] = "2026-06-19T00:00:00Z"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "$release_commit" \
    --ci-run-url "https://github.com/jlekerli-source/ShipGuard/actions/runs/123" \
    --release-url "https://github.com/jlekerli-source/ShipGuard/releases/tag/v$version" \
    --notes "stable v4 publication release proof test" >/dev/null

mkdir -p "$tmp_dir/downloaded"
cp "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/release-manifest.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/index/release-index.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/proof-ledger.md" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/replay/replay-report.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation-badge.json" "$tmp_dir/downloaded/"

api_root="$tmp_dir/github-api"
release_endpoint_file="$api_root/repos/jlekerli-source/ShipGuard/releases/tags/v$version"
latest_release_file="$api_root/repos/jlekerli-source/ShipGuard/releases/latest"
tag_ref_file="$api_root/repos/jlekerli-source/ShipGuard/git/ref/tags/v$version"
mkdir -p "$(dirname "$release_endpoint_file")" "$(dirname "$latest_release_file")" "$(dirname "$tag_ref_file")"
python3 - "$release_endpoint_file" "$latest_release_file" "$tag_ref_file" "$version" "$tmp_dir/downloaded" "$release_commit" <<'PY'
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
latest = Path(sys.argv[2])
tag_ref = Path(sys.argv[3])
version = sys.argv[4]
downloaded = Path(sys.argv[5])
release_commit = sys.argv[6]
asset_names = [
    f"shipguard-v{version}.tar.gz",
    "release-manifest.json",
    "release-index.json",
    "proof-ledger.md",
    "replay-report.json",
    "attestation.json",
    "attestation-badge.json",
]
payload = {
    "tag_name": f"v{version}",
    "html_url": f"https://github.com/jlekerli-source/ShipGuard/releases/tag/v{version}",
    "published_at": "2026-06-20T00:00:00Z",
    "target_commitish": release_commit,
    "body": "ShipGuard stable v4 publication proof. Includes stable-v4 publication boundaries, release proof, downloaded release asset verification, post-release consumer proof, independent adoption evidence, final security review evidence, and blocked claims/non-claims for marketplace acceptance and private app validation.",
    "assets": [
        {
            "name": name,
            "browser_download_url": (downloaded / name).as_uri()
        }
        for name in asset_names
    ],
}
target.write_text(json.dumps(payload), encoding="utf-8")
latest.write_text(json.dumps(payload), encoding="utf-8")
tag_ref.write_text(
    json.dumps(
        {
            "ref": f"refs/tags/v{version}",
            "object": {
                "type": "commit",
                "sha": release_commit,
            },
        }
    ),
    encoding="utf-8",
)
PY

metadata_blocked_api_root="$tmp_dir/metadata-blocked-github-api"
mkdir -p "$metadata_blocked_api_root"
if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/metadata-blocked" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$metadata_blocked_api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-pass.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/metadata-blocked-consume" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected missing GitHub release metadata to block stable publication" >&2
  exit 1
fi
test -f "$tmp_dir/metadata-blocked/v4-stable-publication.json"
test -f "$tmp_dir/metadata-blocked/v4-stable-publication.md"
python3 - "$tmp_dir/metadata-blocked/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
assert report["stableV4Release"] is False
metadata = report["githubReleaseMetadataProof"]
assert metadata["status"] == "blocked"
assert metadata["repo"] == "jlekerli-source/ShipGuard"
assert metadata["repoInference"]["source"] == "explicit-argument"
assert metadata["tag"].startswith("v")
assert metadata["releaseEndpoint"].endswith(f"/repos/jlekerli-source/ShipGuard/releases/tags/{metadata['tag']}")
assert metadata["requiredAssets"]
assert metadata["summary"] == "GitHub release metadata could not be loaded."
packet = report["stablePublicationEvidencePacket"]
assert packet["status"] == "review"
assert packet["firstBlockingGate"]["id"] == "github-release-metadata"
assert packet["firstBlockingGate"]["receipt"] == "githubReleaseMetadataProof"
assert packet["firstBlockingGate"]["status"] == "blocked"
assert "github-release-metadata" in packet["missingEvidenceIds"]
closure = report["stablePublicationClosureChecklist"]
assert closure["status"] == "review"
assert closure["firstBlocker"]["id"] == "github-release-metadata"
assert closure["items"][0]["id"] == "github-release-metadata"
assert closure["items"][0]["isFirstBlockingGate"] is True
item = closure["items"][0]
kit = item["releaseMetadataClosureKit"]
assert kit["status"] == "blocked"
assert kit["repo"] == "jlekerli-source/ShipGuard"
assert kit["tag"] == metadata["tag"]
assert kit["releaseEndpoint"] == metadata["releaseEndpoint"]
assert kit["requiredAssets"] == metadata["requiredAssets"]
assert isinstance(kit["metadataAssetNames"], list)
assert isinstance(kit["metadataMissingAssets"], list)
assert kit["releaseState"]["isDraft"] is False
assert kit["releaseState"]["isPrerelease"] is False
assert "sha256" in kit["releaseNotesSummary"]
assert "missingTopicIds" in kit["releaseNotesSummary"]
assert kit["currentMetadataDiagnostics"]["status"] == metadata["status"]
assert kit["currentMetadataDiagnostics"]["error"]
assert len(kit["repairCriteria"]) >= 4
assert len(kit["passCriteria"]) >= 5
assert len(kit["failCriteria"]) >= 6
assert "stable-publication" in kit["metadataRerunCommand"]
boundary = kit["metadataProofBoundary"]
assert boundary["publicGitHubReleaseMetadataRequired"] is True
assert boundary["ownerRepoSyntaxRequired"] is True
assert boundary["draftOrPrereleaseCountsAsStablePublicationProof"] is False
assert boundary["sourceOnlyProofCountsAsReleaseMetadataProof"] is False
assert boundary["fixtureApiProofCountsAsStableV4PublicationProof"] is False
assert boundary["releaseAssetsStillRequireDownloadedOrSuppliedProof"] is True
assert item["nextCommand"] == item["metadataRerunCommand"] == kit["metadataRerunCommand"]
PY
grep -q 'GitHub Release Metadata Closure Kit' "$tmp_dir/metadata-blocked/v4-stable-publication.md"
grep -q 'Public GitHub release metadata required: `True`' "$tmp_dir/metadata-blocked/v4-stable-publication.md"
grep -q 'Draft or prerelease counts as stable-publication proof: `False`' "$tmp_dir/metadata-blocked/v4-stable-publication.md"
grep -q 'Source-only proof counts as release metadata proof: `False`' "$tmp_dir/metadata-blocked/v4-stable-publication.md"
grep -q 'Fixture API proof counts as stable-v4 publication proof: `False`' "$tmp_dir/metadata-blocked/v4-stable-publication.md"
grep -q 'Rerun release metadata proof' "$tmp_dir/metadata-blocked/v4-stable-publication.md"

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/blocked" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-incomplete.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/blocked-consume" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected incomplete LaunchKey packet to block stable publication" >&2
  exit 1
fi
test -f "$tmp_dir/blocked/v4-stable-publication.json"
grep -q '"stableV4Release": false' "$tmp_dir/blocked/v4-stable-publication.json"
grep -q '"releaseCandidatePacketProof":' "$tmp_dir/blocked/v4-stable-publication.json"
grep -q '"status": "review"' "$tmp_dir/blocked/v4-stable-publication.json"
python3 - "$tmp_dir/blocked/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
packet = report["stablePublicationEvidencePacket"]
assert packet["status"] == "review"
assert packet["stableV4Release"] is False
assert packet["requiredEvidenceCount"] == 10
assert packet["passedEvidenceCount"] < 10
assert "launchkey-candidate-packet" in packet["missingEvidenceIds"]
assert "release-version-coherence" not in packet["missingEvidenceIds"]
assert "release-asset-coherence" not in packet["missingEvidenceIds"]
assert packet["firstBlockingGate"]["receipt"] == "releaseCandidatePacketProof"
assert packet["firstBlockingGate"]["nextCommand"].startswith("./bin/shipguard v4 release-candidate")
closure = report["stablePublicationClosureChecklist"]
assert closure["status"] == "review"
assert closure["stableV4Release"] is False
assert closure["blockerCount"] == len(packet["missingEvidenceIds"])
assert closure["blockedEvidenceIds"] == packet["missingEvidenceIds"]
assert closure["noHiddenLowerOrderBlockers"] is True
assert [item["id"] for item in closure["items"]] == packet["missingEvidenceIds"]
assert closure["items"][0]["isFirstBlockingGate"] is True
assert all(item["nextCommand"] for item in closure["items"])
assert all(item["proofBoundary"] for item in closure["items"])
launchkey_item = closure["items"][0]
assert launchkey_item["id"] == "launchkey-candidate-packet"
launchkey_kit = launchkey_item["launchKeyCandidateClosureKit"]
assert "candidate-incomplete.json" in launchkey_kit["candidateReportPath"]
assert launchkey_kit["nestedBlockingReceipt"] == "freshInstallPackageProof"
assert launchkey_kit["nestedBlockingStatus"] == "not-provided"
assert "release-candidate" in launchkey_kit["nestedRerunCommand"]
assert "stable-publication" in launchkey_kit["stablePublicationRerunCommand"]
assert launchkey_kit["fixtureCandidateBoundary"]["fixtureCandidateProofCountsAsStableV4PublicationProof"] is False
required_receipts = {area["receipt"] for area in launchkey_kit["requiredLaunchKeyProofAreas"]}
assert {
    "freshInstallPackageProof",
    "upgradePackageProof",
    "rollbackPackageProof",
    "githubReleaseAssetDownloadProof",
    "publishedReleaseAssetProof",
    "externalAdoptionEvidenceStableGate",
    "securityReviewEvidenceStableGate",
} <= required_receipts
assert len(launchkey_kit["repairCriteria"]) >= 3
assert len(launchkey_kit["passCriteria"]) >= 5
assert len(launchkey_kit["failCriteria"]) >= 5
templates = report["stablePublicationEvidenceTemplates"]
assert templates["draftOnly"] is True
assert templates["templateDirectory"] == "templates/stable-publication"
assert {
    "independent-adoption-evidence",
    "final-security-review-evidence",
} <= set(templates["templateIds"])
by_id = {item["id"]: item for item in templates["templates"]}
assert by_id["independent-adoption-evidence"]["exists"] is True
assert by_id["final-security-review-evidence"]["exists"] is True
starter = report["stablePublicationEvidenceStarterKit"]
assert starter["schemaVersion"] == 2
assert starter["draftOnly"] is True
assert starter["directory"] == "stable-publication-evidence-kit"
assert starter["releaseVersion"] == report["releaseVersion"]
related = {item["id"]: item for item in starter["relatedAuthoringKits"]}
assert related["release-notes-authoring-kit"]["directory"] == "stable-publication-release-notes"
assert related["release-notes-authoring-kit"]["status"] == report["stablePublicationReleaseNotesAuthoringKit"]["status"]
assert {
    "stable-publication-evidence-kit/README.md",
    "stable-publication-evidence-kit/stable-publication-checklist.json",
    "stable-publication-evidence-kit/external-adoption-evidence.json",
    "stable-publication-evidence-kit/security-review-evidence.json",
} <= {item["path"] for item in starter["files"]}
assert "stable-publication-evidence-kit/external-adoption-evidence.json" in starter["nextCommandTemplate"]
relay = report["stablePublicationLaunchRelayDrafts"]
assert relay["draftOnly"] is True
assert relay["directory"] == "stable-publication-launch-relay"
assert relay["approvalRequired"] is True
assert relay["publicPostingAllowed"] is False
assert relay["postingPolicy"]["requiresExplicitApproval"] is True
assert relay["postingPolicy"]["computerUseMayPost"] is False
assert {
    "stable-publication-launch-relay/README.md",
    "stable-publication-launch-relay/launch-relay-checklist.json",
    "stable-publication-launch-relay/product-hunt-draft.md",
    "stable-publication-launch-relay/reddit-r-shipguard-draft.md",
    "stable-publication-launch-relay/x-thread-draft.md",
    "stable-publication-launch-relay/hacker-news-draft.md",
} <= {item["path"] for item in relay["files"]}
required_by_id = {item["id"]: item for item in packet["requiredEvidence"]}
assert required_by_id["independent-adoption-evidence"]["templatePath"] == "templates/stable-publication/external-adoption-evidence.template.json"
assert required_by_id["final-security-review-evidence"]["templatePath"] == "templates/stable-publication/security-review-evidence.template.json"
PY
test -f "$tmp_dir/blocked/stable-publication-evidence-kit/README.md"
test -f "$tmp_dir/blocked/stable-publication-evidence-kit/stable-publication-checklist.json"
test -f "$tmp_dir/blocked/stable-publication-evidence-kit/external-adoption-evidence.json"
test -f "$tmp_dir/blocked/stable-publication-evidence-kit/security-review-evidence.json"
grep -q '"draftOnly": true' "$tmp_dir/blocked/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q "\"releaseVersion\": \"$version\"" "$tmp_dir/blocked/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q '"relatedAuthoringKits":' "$tmp_dir/blocked/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q 'Stable Publication Evidence Kit' "$tmp_dir/blocked/stable-publication-evidence-kit/README.md"
grep -q "Release version: \`$version\`" "$tmp_dir/blocked/stable-publication-evidence-kit/README.md"
grep -q 'Release notes kit: `stable-publication-release-notes`' "$tmp_dir/blocked/stable-publication-evidence-kit/README.md"
grep -q '"closureChecklist":' "$tmp_dir/blocked/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q 'Closure Checklist' "$tmp_dir/blocked/v4-stable-publication.md"
grep -q 'LaunchKey Candidate Closure Kit' "$tmp_dir/blocked/v4-stable-publication.md"
grep -q 'candidate-incomplete.json' "$tmp_dir/blocked/v4-stable-publication.md"
grep -q 'Fixture candidate proof counts as stable-v4 publication proof: `False`' "$tmp_dir/blocked/v4-stable-publication.md"
grep -q 'final-security-review-evidence' "$tmp_dir/blocked/v4-stable-publication.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/README.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/product-hunt-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/reddit-r-shipguard-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/x-thread-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/hacker-news-draft.md"
grep -q '"publicPostingAllowed": false' "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
grep -q '"computerUseMayPost": false' "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
grep -q 'Stable Publication Launch Relay' "$tmp_dir/blocked/stable-publication-launch-relay/README.md"

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/evidence-blocked" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-pass.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/evidence-blocked-consume" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected missing adoption/security evidence to block stable publication" >&2
  exit 1
fi
python3 - "$tmp_dir/evidence-blocked/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
packet = report["stablePublicationEvidencePacket"]
assert packet["missingEvidenceIds"] == [
    "independent-adoption-evidence",
    "final-security-review-evidence",
]
required_by_id = {item["id"]: item for item in packet["requiredEvidence"]}
assert required_by_id["independent-adoption-evidence"]["evidenceDiagnostics"]["stableV4GateStatus"] == "not-provided"
assert required_by_id["final-security-review-evidence"]["evidenceDiagnostics"]["stableV4GateStatus"] == "not-provided"
public_evidence = report["publicEvidenceClosureProof"]
assert public_evidence["status"] == "review"
assert public_evidence["missingOrBlockingEvidenceIds"] == [
    "independent-adoption-evidence",
    "final-security-review-evidence",
]
assert public_evidence["publicEvidenceBoundary"]["githubDownloadCountsCountAsAdoptionEvidence"] is False
assert public_evidence["publicEvidenceBoundary"]["doesNotClaimMarketplaceAcceptance"] is True
assert any("stable-publication" in command for command in public_evidence["copyReadyCommands"])
final_claim = report["finalStableV4ClaimPacket"]
assert final_claim["status"] == "blocked"
assert final_claim["claimDecision"] == "blocked"
assert final_claim["stableV4Release"] is False
assert "Do not claim ShipGuard" in final_claim["copyReadyClaim"]
delta_summary = final_claim["publicReleaseDeltaSummary"]
assert delta_summary["unpublishedLocalDelta"] is False
assert delta_summary["stableV4ClaimCoversSelectedPublicRelease"] is False
assert delta_summary["stableV4ClaimCoversLocalCheckout"] is False
assert delta_summary["unpublishedLocalCodeCountsAsReleased"] is False
assert final_claim["missingEvidenceIds"] == packet["missingEvidenceIds"]
assert final_claim["firstBlockingGate"]["id"] == "independent-adoption-evidence"
assert final_claim["publicEvidenceClosureStatus"] == "review"
assert any("ShipGuard v4 is stable" in claim for claim in final_claim["blockedClaims"])
assert len(final_claim["evidenceSummary"]) == packet["requiredEvidenceCount"]
assert final_claim["claimBoundary"]["sourceOnlyProofCountsAsStableV4"] is False
assert final_claim["claimBoundary"]["fixtureProofCountsAsStableV4"] is False
assert final_claim["claimBoundary"]["githubDownloadCountsCountAsAdoptionEvidence"] is False
assert final_claim["claimBoundary"]["marketplaceAcceptanceClaimed"] is False
assert final_claim["approvalBoundary"]["publicPostingRequiresExplicitApproval"] is True
assert final_claim["approvalBoundary"]["computerUseMayPost"] is False
closure = report["stablePublicationClosureChecklist"]
items = closure["items"]
assert [item["id"] for item in items] == packet["missingEvidenceIds"]
expected = {
    "independent-adoption-evidence": {
        "starterPath": "stable-publication-evidence-kit/external-adoption-evidence.json",
        "templatePath": "templates/stable-publication/external-adoption-evidence.template.json",
        "classes": {"public-external", "private-redacted-external"},
        "requiredFields": {"actorRelationship", "privateDataRedacted", "commands", "artifacts", "outcome", "nonClaims"},
    },
    "final-security-review-evidence": {
        "starterPath": "stable-publication-evidence-kit/security-review-evidence.json",
        "templatePath": "templates/stable-publication/security-review-evidence.template.json",
        "classes": {"public-security-review", "private-redacted-security-review"},
        "requiredFields": {"scope", "methodology", "findingsSummary", "privateDataRedacted", "nonClaims"},
    },
}
for item in items:
    spec = expected[item["id"]]
    kit = item["evidenceClosureKit"]
    assert item["starterKitPath"] == spec["starterPath"]
    assert item["templatePath"] == spec["templatePath"]
    assert kit["starterPath"] == spec["starterPath"]
    assert kit["templatePath"] == spec["templatePath"]
    assert set(kit["acceptedEvidenceClasses"]) == spec["classes"]
    assert spec["requiredFields"] <= set(kit["requiredFields"])
    assert kit["redactionBoundary"]["privateDataRedactedMustBeTrue"] is True
    assert kit["privacyBoundary"]
    assert len(kit["passCriteria"]) >= 3
    assert len(kit["failCriteria"]) >= 3
    assert "stable-publication" in kit["rerunCommand"]
    assert kit["currentEvidenceDiagnostics"]["stableV4GateStatus"] == "not-provided"
    assert item["nextCommand"] == item["rerunCommand"] == kit["rerunCommand"]
security_kit = expected["final-security-review-evidence"]
security_item = next(item for item in items if item["id"] == "final-security-review-evidence")
assert set(security_item["evidenceClosureKit"]["requiredScope"]) == {
    "cli",
    "plugin",
    "github-actions",
    "release-proof",
    "package-install",
    "redaction-privacy",
}
PY
grep -q 'Evidence Closure Kit: `independent-adoption-evidence`' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Evidence Closure Kit: `final-security-review-evidence`' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Public Evidence Closure' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Final Stable V4 Claim Packet' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Claim decision: `blocked`' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'ShipGuard v4 is stable.' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'GitHub download counts count as adoption evidence: `False`' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Pass criteria:' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'Fail criteria:' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'stable-publication-evidence-kit/external-adoption-evidence.json' "$tmp_dir/evidence-blocked/v4-stable-publication.md"
grep -q 'stable-publication-evidence-kit/security-review-evidence.json' "$tmp_dir/evidence-blocked/v4-stable-publication.md"

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/consumer-blocked" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-pass.json" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected missing post-release consumer proof to block stable publication" >&2
  exit 1
fi
python3 - "$tmp_dir/consumer-blocked/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
packet = report["stablePublicationEvidencePacket"]
assert packet["missingEvidenceIds"] == [
    "downloaded-release-assets",
    "post-release-consumer-proof",
    "public-release-freshness",
    "release-version-coherence",
    "release-asset-coherence",
]
assert packet["firstBlockingGate"]["receipt"] == "publishedReleaseAssetProof"
required_by_id = {item["id"]: item for item in packet["requiredEvidence"]}
asset_required = required_by_id["downloaded-release-assets"]
asset_diagnostics = asset_required["releaseAssetDiagnostics"]
assert asset_diagnostics["status"] == "not-provided"
assert asset_diagnostics["downloadProofStatus"] == "not-provided"
assert asset_diagnostics["localAssetNames"] == []
consumer_required = required_by_id["post-release-consumer-proof"]
diagnostics = consumer_required["postReleaseConsumerDiagnostics"]
assert diagnostics["status"] == "not-provided"
assert diagnostics["consumerReportStatus"] == "not-provided"
assert set(diagnostics["missingProofArtifacts"]) == {"consumer-report.json", "asset-digests.json"}
assert diagnostics["consumerDigestFreshness"]["status"] == "not-provided"
assert "asset-digests.json missing" in diagnostics["consumerDigestFreshness"]["problems"]
freshness_required = required_by_id["public-release-freshness"]
freshness_diagnostics = freshness_required["releaseFreshnessDiagnostics"]
assert freshness_diagnostics["status"] == "not-provided"
assert any("release-manifest.json" in problem for problem in freshness_diagnostics["problems"])
version_required = required_by_id["release-version-coherence"]
version_diagnostics = version_required["releaseVersionCoherenceDiagnostics"]
assert version_diagnostics["status"] == "review"
assert version_diagnostics["comparisons"]["packageVersionMatchesRequested"] is False
assert version_diagnostics["comparisons"]["consumerReportVersionMatchesRequested"] is False
asset_coherence_required = required_by_id["release-asset-coherence"]
asset_coherence_diagnostics = asset_coherence_required["releaseAssetCoherenceDiagnostics"]
assert asset_coherence_diagnostics["status"] == "review"
assert asset_coherence_diagnostics["comparisons"]["localAssetsCoverRequired"] is False
assert asset_coherence_diagnostics["comparisons"]["digestAssetsCoverRequired"] is False
assert asset_coherence_diagnostics["missingLocalAssetNames"]
assert asset_coherence_diagnostics["missingDigestAssetNames"]
closure = report["stablePublicationClosureChecklist"]
assert [item["id"] for item in closure["items"]] == packet["missingEvidenceIds"]
asset_item = closure["items"][0]
assert asset_item["id"] == "downloaded-release-assets"
assert asset_item["receipt"] == "publishedReleaseAssetProof"
assert asset_item["isFirstBlockingGate"] is True
asset_kit = asset_item["releaseAssetClosureKit"]
assert asset_kit["status"] == "not-provided"
assert asset_kit["downloadProofStatus"] == "not-provided"
assert asset_kit["requiredAssets"]
assert set(asset_kit["missingLocalAssets"]) == set(asset_kit["requiredAssets"])
assert asset_kit["releaseAssetProofBoundary"]["downloadedOrSuppliedAssetsRequired"] is True
assert asset_kit["releaseAssetProofBoundary"]["githubMetadataOnlyCountsAsReleaseAssetProof"] is False
assert asset_kit["releaseAssetProofBoundary"]["sourceOnlyProofCountsAsReleaseAssetProof"] is False
assert asset_kit["releaseAssetProofBoundary"]["fixtureProofCountsAsStableV4PublicationProof"] is False
assert "--download-release-assets" in asset_kit["downloadAssetsRerunCommand"]
assert "stable-publication" in asset_kit["stablePublicationRerunCommand"]
assert len(asset_kit["repairCriteria"]) >= 3
assert len(asset_kit["passCriteria"]) >= 3
assert len(asset_kit["failCriteria"]) >= 3
assert asset_kit["currentReleaseAssetDiagnostics"]["status"] == "not-provided"
assert asset_item["nextCommand"] == asset_item["downloadAssetsRerunCommand"] == asset_kit["downloadAssetsRerunCommand"]
consumer_item = closure["items"][1]
assert consumer_item["id"] == "post-release-consumer-proof"
assert consumer_item["receipt"] == "postReleaseConsumerProof"
assert consumer_item["isFirstBlockingGate"] is False
kit = consumer_item["postReleaseConsumerClosureKit"]
assert kit["status"] == "not-provided"
assert kit["consumerReportStatus"] == "not-provided"
assert kit["consumerReportPath"] == ""
assert kit["assetDigestMatrixPath"] == ""
assert set(kit["missingProofArtifacts"]) == {"consumer-report.json", "asset-digests.json"}
assert kit["consumerDigestFreshness"]["status"] == "not-provided"
assert "asset-digests.json missing" in kit["consumerDigestFreshness"]["problems"]
assert kit["consumerProofBoundary"]["releaseConsumeRequired"] is True
assert kit["consumerProofBoundary"]["assetDigestMatrixMustCoverRequiredAssets"] is True
assert kit["consumerProofBoundary"]["releaseTarballDigestMustMatchConsumerArtifact"] is True
assert kit["consumerProofBoundary"]["sourceOnlyProofCountsAsConsumerProof"] is False
assert kit["consumerProofBoundary"]["fixtureProofCountsAsStableV4PublicationProof"] is False
assert "release-consume verify" in kit["releaseConsumeRerunCommand"]
assert "stable-publication" in kit["stablePublicationRerunCommand"]
assert len(kit["repairCriteria"]) >= 3
assert len(kit["passCriteria"]) >= 4
assert len(kit["failCriteria"]) >= 4
assert kit["currentConsumerDiagnostics"]["status"] == "not-provided"
assert consumer_item["nextCommand"] == consumer_item["releaseConsumeRerunCommand"] == kit["releaseConsumeRerunCommand"]
freshness_item = closure["items"][2]
assert freshness_item["id"] == "public-release-freshness"
freshness_kit = freshness_item["releaseFreshnessClosureKit"]
assert freshness_kit["status"] == "not-provided"
assert freshness_kit["freshnessProofBoundary"]["releaseManifestRequired"] is True
assert freshness_kit["freshnessProofBoundary"]["sourceOnlyProofCountsAsFreshnessProof"] is False
assert "stable-publication" in freshness_kit["freshnessRerunCommand"]
PY
grep -q 'Release Asset Closure Kit' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'GitHub metadata only counts as release-asset proof: `False`' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Rerun release asset proof' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Post-Release Consumer Closure Kit' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'consumer-report.json, asset-digests.json' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Digest freshness status: `not-provided`' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Asset digest matrix must cover required assets: `True`' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Source-only proof counts as consumer proof: `False`' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Rerun release-consume proof' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'release-consume verify' "$tmp_dir/consumer-blocked/v4-stable-publication.md"
grep -q 'Public Release Freshness Closure Kit' "$tmp_dir/consumer-blocked/v4-stable-publication.md"

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/hygiene-blocked" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-hygiene-blocked.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/hygiene-blocked-consume" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected LaunchKey hygiene blocker to block stable publication" >&2
  exit 1
fi
python3 - "$tmp_dir/hygiene-blocked/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
candidate = report["releaseCandidatePacketProof"]
assert candidate["status"] == "review"
assert candidate["nextCommand"].startswith("./bin/shipguard release-package hygiene")
blocker = candidate["launchKeyBlockingProof"]
assert blocker["receipt"] == "upgradePackageProof"
assert blocker["status"] == "blocked"
assert "appledouble-sidecar" in blocker["failureEvidence"]
assert "release-package hygiene" in blocker["nextCommand"]
hygiene = blocker["packageHygieneEvidence"]
assert hygiene["status"] == "blocked"
assert hygiene["blockedFindingCount"] == 782
assert hygiene["firstFinding"]["ruleId"] == "appledouble-sidecar"
packet = report["stablePublicationEvidencePacket"]
assert packet["firstBlockingGate"]["receipt"] == "releaseCandidatePacketProof"
assert packet["firstBlockingGate"]["nextCommand"].startswith("./bin/shipguard release-package hygiene")
assert "appledouble-sidecar" in packet["firstBlockingGate"]["failureEvidence"]
closure = report["stablePublicationClosureChecklist"]
expected_missing = [item["id"] for item in packet["requiredEvidence"] if item["status"] != "pass"]
assert [item["id"] for item in closure["items"]] == expected_missing
assert closure["blockedEvidenceIds"] == expected_missing
assert closure["blockerCount"] == len(expected_missing)
assert closure["items"][0]["id"] == "launchkey-candidate-packet"
assert closure["items"][0]["receipt"] == "releaseCandidatePacketProof"
assert closure["items"][0]["blockingProof"]["receipt"] == "upgradePackageProof"
assert "appledouble-sidecar" in closure["items"][0]["failureEvidence"]
assert "release-package hygiene" in closure["items"][0]["nextCommand"]
launchkey_kit = closure["items"][0]["launchKeyCandidateClosureKit"]
assert "candidate-hygiene-blocked.json" in launchkey_kit["candidateReportPath"]
assert launchkey_kit["nestedBlockingReceipt"] == "upgradePackageProof"
assert launchkey_kit["nestedBlockingProof"]["receipt"] == "upgradePackageProof"
assert "release-package hygiene" in launchkey_kit["nestedRerunCommand"]
assert "stable-publication" in launchkey_kit["stablePublicationRerunCommand"]
assert launchkey_kit["packageHygieneDiagnostics"]["blockedFindingCount"] == 782
assert launchkey_kit["packageHygieneDiagnostics"]["firstFinding"]["member"] == "._shipguard-v3.130.0"
assert launchkey_kit["fixtureCandidateBoundary"]["fixtureCandidateProofCountsAsStableV4PublicationProof"] is False
required_by_id = {item["id"]: item for item in packet["requiredEvidence"]}
candidate_item = required_by_id["launchkey-candidate-packet"]
assert candidate_item["blockingProof"]["receipt"] == "upgradePackageProof"
assert candidate_item["blockingProof"]["packageHygieneEvidence"]["firstFinding"]["member"] == "._shipguard-v3.130.0"
assert candidate_item["launchKeyCandidateDiagnostics"]["nestedBlockingReceipt"] == "upgradePackageProof"
PY
grep -q 'LaunchKey Candidate Blocker' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"
grep -q 'LaunchKey Candidate Closure Kit' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"
grep -q 'Closure Checklist' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"
grep -q 'appledouble-sidecar' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"
grep -q 'release-package hygiene' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"
grep -q 'Rerun the full stable-publication gate after LaunchKey passes' "$tmp_dir/hygiene-blocked/v4-stable-publication.md"

python3 - "$release_endpoint_file" "$version" "$tmp_dir/downloaded" "$release_commit" <<'PY'
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
version = sys.argv[2]
downloaded = Path(sys.argv[3])
release_commit = sys.argv[4]
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
            "published_at": "2026-06-20T00:00:00Z",
            "target_commitish": release_commit,
            "body": "ShipGuard stable v4 release proof is ready.",
            "assets": [
                {
                    "name": name,
                    "browser_download_url": (downloaded / name).as_uri()
                }
                for name in asset_names
            ]
        }
    ),
    encoding="utf-8",
)
PY

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/weak-notes" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-pass.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/weak-notes-consume" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected weak release notes to block stable publication" >&2
  exit 1
fi
python3 - "$tmp_dir/weak-notes/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
assert report["stableV4Release"] is False
assert report["releaseNotesProof"]["status"] == "review"
assert report["stablePublicationEvidencePacket"]["firstBlockingGate"]["receipt"] == "releaseNotesProof"
closure = report["stablePublicationClosureChecklist"]
assert closure["items"][0]["id"] == "release-notes"
assert closure["items"][0]["receipt"] == "releaseNotesProof"
assert len(closure["items"]) == 1
missing = set(report["releaseNotesProof"]["missingTopicIds"])
assert {
    "downloaded-release-assets",
    "post-release-consumer-proof",
    "independent-adoption-evidence",
    "final-security-review-evidence",
    "non-claims-boundary",
} <= missing
release_notes_item = closure["items"][0]
assert set(release_notes_item["missingTopicIds"]) == missing
assert {
    "stable-publication-release-notes/README.md",
    "stable-publication-release-notes/release-notes-checklist.json",
    "stable-publication-release-notes/draft-release-notes.md",
} <= set(release_notes_item["authoringKitPaths"])
assert release_notes_item["releaseNotesAuthoringKit"]["draftOnly"] is True
assert release_notes_item["releaseNotesAuthoringKit"]["directory"] == "stable-publication-release-notes"
assert release_notes_item["releaseNotesAuthoringKit"]["checklistPath"] == "stable-publication-release-notes/release-notes-checklist.json"
edit_boundary = release_notes_item["publicGitHubReleaseEditBoundary"]
assert edit_boundary["requiresPublicReleaseEdit"] is True
assert edit_boundary["shipguardDoesNotEditRelease"] is True
assert edit_boundary["authoringKitIsDraftOnly"] is True
assert edit_boundary["stableV4ClaimAllowed"] is False
assert "stable-publication" in release_notes_item["rerunCommand"]
assert "--github-release-repo jlekerli-source/ShipGuard" in release_notes_item["rerunCommand"]
assert f"--release-version {report['releaseVersion']}" in release_notes_item["rerunCommand"]
assert len(report["releaseNotesProof"]["topicMatrix"]) == 7
notes_kit = report["stablePublicationReleaseNotesAuthoringKit"]
assert notes_kit["schemaVersion"] == 2
assert notes_kit["draftOnly"] is True
assert notes_kit["directory"] == "stable-publication-release-notes"
assert notes_kit["releaseTag"] == f"v{report['releaseVersion']}"
assert notes_kit["releaseUrl"].endswith(f"/releases/tag/v{report['releaseVersion']}")
assert notes_kit["publicReleaseEditCommand"] == (
    f"gh release edit v{report['releaseVersion']} --repo jlekerli-source/ShipGuard "
    "--notes-file stable-publication-release-notes/draft-release-notes.md"
)
assert report["stablePublicationEvidencePacket"]["firstBlockingGate"]["nextCommand"] == notes_kit["publicReleaseEditCommand"]
assert report["resultUX"]["nextCommand"] == notes_kit["publicReleaseEditCommand"]
assert report["resultUX"]["proofSource"] == "release notes"
assert report["resultUX"]["nextActionSummary"] == "Work the Closure Checklist in order; first complete release notes before claiming stable-v4 publication."
assert "stablePublicationClosureChecklist" not in report["resultUX"]["nextActionSummary"]
assert "releaseNotesProof" not in report["resultUX"]["nextActionSummary"]
assert "releaseNotesProof" not in report["resultUX"]["proofSource"]
assert release_notes_item["nextCommand"] == notes_kit["publicReleaseEditCommand"]
assert release_notes_item["rerunCommand"] != release_notes_item["nextCommand"]
visibility_actions = {item["id"]: item for item in report["releaseVisibilityHandoff"]["requiredActions"]}
assert visibility_actions["update-release-notes"]["required"] is True
assert visibility_actions["update-release-notes"]["nextCommand"] == notes_kit["publicReleaseEditCommand"]
assert visibility_actions["publish-new-github-release"]["nextCommand"] == "not-needed"
assert visibility_actions["update-release-assets"]["nextCommand"] == "not-needed"
assert visibility_actions["keep-current-public-release-unchanged"]["nextCommand"] == "blocked-by-required-actions"
assert set(notes_kit["missingTopicIds"]) == missing
assert {
    "stable-publication-release-notes/README.md",
    "stable-publication-release-notes/release-notes-checklist.json",
    "stable-publication-release-notes/draft-release-notes.md",
} <= {item["path"] for item in notes_kit["files"]}
relay = report["stablePublicationLaunchRelayDrafts"]
assert relay["draftOnly"] is True
assert relay["approvalRequired"] is True
assert relay["publicPostingAllowed"] is False
assert relay["postingPolicy"]["computerUseMayPost"] is False
PY
grep -q 'Release Notes Proof' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'Release Notes Authoring Kit' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'Release Notes Closure Kit' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'update-release-notes.*gh release edit' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'post-release-consumer-proof' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'Public release edit required: `True`' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'gh release edit' "$tmp_dir/weak-notes/v4-stable-publication.md"
grep -q 'stable-publication-release-notes/draft-release-notes.md' "$tmp_dir/weak-notes/v4-stable-publication.md"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/README.md"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/release-notes-checklist.json"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/draft-release-notes.md"
grep -q 'Post-release consumer proof' "$tmp_dir/weak-notes/stable-publication-release-notes/draft-release-notes.md"
grep -q 'gh release edit' "$tmp_dir/weak-notes/stable-publication-release-notes/README.md"
grep -q 'gh release edit' "$tmp_dir/weak-notes/stable-publication-release-notes/draft-release-notes.md"
grep -q '"draftOnly": true' "$tmp_dir/weak-notes/stable-publication-release-notes/release-notes-checklist.json"

python3 - "$release_endpoint_file" "$version" "$tmp_dir/downloaded" "$release_commit" <<'PY'
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
version = sys.argv[2]
downloaded = Path(sys.argv[3])
release_commit = sys.argv[4]
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
            "published_at": "2026-06-20T00:00:00Z",
            "target_commitish": release_commit,
            "body": "ShipGuard stable v4 publication proof. Includes stable-v4 publication boundaries, release proof, downloaded release asset verification, post-release consumer proof, independent adoption evidence, final security review evidence, and blocked claims/non-claims for marketplace acceptance and private app validation.",
            "assets": [
                {
                    "name": name,
                    "browser_download_url": (downloaded / name).as_uri()
                }
                for name in asset_names
            ]
        }
    ),
    encoding="utf-8",
)
PY

python3 - "$tag_ref_file" "$version" <<'PY'
import json
import sys
from pathlib import Path

version = sys.argv[2]
Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "ref": f"refs/tags/v{version}",
            "object": {
                "type": "commit",
                "sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            },
        }
    ),
    encoding="utf-8",
)
PY

if ./bin/shipguard v4 stable-publication \
  --path . \
  --out "$tmp_dir/stale-freshness" \
  --github-release-repo jlekerli-source/ShipGuard \
  --github-api-url "file://$api_root" \
  --release-version "$version" \
  --release-candidate-report "$tmp_dir/candidate-pass.json" \
  --release-assets "$tmp_dir/downloaded" \
  --release-consume-out "$tmp_dir/stale-freshness-consume" \
  --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
  --security-review-evidence "$tmp_dir/evidence/stable-security" \
  --shipguard-eval \
  --shareable >/dev/null 2>&1; then
  echo "expected stale public tag target to block stable publication freshness" >&2
  exit 1
fi
python3 - "$tmp_dir/stale-freshness/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
assert report["stableV4Release"] is False
freshness = report["publicReleaseFreshnessProof"]
assert freshness["status"] == "review"
assert freshness["tagTargetSha"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
assert freshness["comparisons"]["tagTargetMatchesManifestCommit"] is False
assert "public-release-freshness" in report["stablePublicationEvidencePacket"]["missingEvidenceIds"]
delta = report["publicReleaseDeltaProof"]
assert delta["status"] == "review"
assert delta["latestGitHubReleaseStatus"] == "pass"
assert delta["latestGitHubReleaseVersion"] == report["releaseVersion"].removeprefix("v")
assert delta["selectedGitHubReleaseTag"] == f"v{report['releaseVersion']}"
assert delta["latestGitHubReleaseTag"] == f"v{report['releaseVersion']}"
assert delta["comparisons"]["selectedReleaseMatchesLatestGitHubRelease"] is True
assert delta["comparisons"]["publicTagTargetMatchesReleaseManifestCommit"] is False
assert delta["comparisons"]["localMainMatchesSelectedPublicReleaseCommit"] is True
assert delta["releaseDeltaBoundary"]["unpublishedLocalCodeCountsAsReleased"] is False
visibility = report["releaseVisibilityHandoff"]
assert visibility["status"] == "review"
assert visibility["primaryDecision"] == "publish-new-github-release"
assert visibility["unpublishedLocalDelta"] is False
assert visibility["currentPublicReleaseCanBeAnnounced"] is False
assert visibility["visibilityBoundary"]["unpublishedLocalCodeCountsAsReleased"] is False
actions = {item["id"]: item for item in visibility["requiredActions"]}
assert actions["publish-new-github-release"]["required"] is True
assert actions["attach-launchkey-candidate-proof"]["required"] is False
assert actions["keep-current-public-release-unchanged"]["status"] == "blocked"
assert actions["keep-current-public-release-unchanged"]["nextCommand"] == "blocked-by-required-actions"
assert report["stablePublicationEvidencePacket"]["firstBlockingGate"]["receipt"] == "publicReleaseFreshnessProof"
closure = report["stablePublicationClosureChecklist"]
assert closure["items"][0]["id"] == "public-release-freshness"
kit = closure["items"][0]["releaseFreshnessClosureKit"]
assert kit["tagTargetSha"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
assert kit["manifestCommit"]
assert kit["comparisons"]["tagTargetMatchesManifestCommit"] is False
assert kit["freshnessProofBoundary"]["releaseManifestCommitMustMatchPublicTagTarget"] is True
assert kit["freshnessProofBoundary"]["sourceOnlyProofCountsAsFreshnessProof"] is False
assert "stable-publication" in kit["freshnessRerunCommand"]
assert len(kit["repairCriteria"]) >= 3
assert len(kit["passCriteria"]) >= 5
assert len(kit["failCriteria"]) >= 5
PY
grep -q 'Public Release Freshness Closure Kit' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'Public Release Delta' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'Release Visibility Handoff' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'Primary decision: `publish-new-github-release`' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'publicTagTargetMatchesReleaseManifestCommit' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'tagTargetMatchesManifestCommit' "$tmp_dir/stale-freshness/v4-stable-publication.md"
grep -q 'Source-only proof counts as freshness proof: `False`' "$tmp_dir/stale-freshness/v4-stable-publication.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/stale-freshness" \
  --out "$tmp_dir/stale-freshness-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stale-freshness-quality/ios-report-quality.json"

python3 - "$tag_ref_file" "$version" "$release_commit" <<'PY'
import json
import sys
from pathlib import Path

tag_ref = Path(sys.argv[1])
version = sys.argv[2]
release_commit = sys.argv[3]
tag_ref.write_text(
    json.dumps(
        {
            "ref": f"refs/tags/v{version}",
            "object": {
                "type": "commit",
                "sha": release_commit,
            },
        }
    ),
    encoding="utf-8",
)
PY

if SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard v4 stable-publication \
    --path . \
    --out "$tmp_dir/stale-external-evidence" \
    --github-api-url "file://$api_root" \
    --release-version "v$version" \
    --release-candidate-report "$tmp_dir/candidate-pass.json" \
    --download-release-assets \
    --download-release-assets-dir "$tmp_dir/stale-external-downloaded" \
    --release-consume-out "$tmp_dir/stale-external-consume" \
    --external-adoption-evidence "$tmp_dir/evidence/stale-adoption" \
    --security-review-evidence "$tmp_dir/evidence/stale-security" \
    --shipguard-eval \
    --shareable >/dev/null 2>&1; then
  echo "expected stale adoption/security evidence to block stable publication" >&2
  exit 1
fi
python3 - "$tmp_dir/stale-external-evidence/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "review"
assert report["stableV4Release"] is False
adoption = report["externalAdoptionEvidenceProof"]
security = report["securityReviewEvidenceProof"]
assert adoption["stableV4GateStatus"] == "review"
assert security["stableV4GateStatus"] == "review"
assert adoption["evidencePacketFreshness"]["status"] == "review"
assert security["evidencePacketFreshness"]["status"] == "review"
assert adoption["evidencePacketFreshness"]["staleStableRecordCount"] == 1
assert security["evidencePacketFreshness"]["staleStableRecordCount"] == 1
assert report["stablePublicationEvidencePacket"]["firstBlockingGate"]["id"] == "independent-adoption-evidence"
closure = report["stablePublicationClosureChecklist"]
assert "independent-adoption-evidence" in closure["blockedEvidenceIds"]
assert "final-security-review-evidence" in closure["blockedEvidenceIds"]
PY
grep -q 'External Evidence Freshness' "$tmp_dir/stale-external-evidence/v4-stable-publication.md"
grep -q 'External adoption freshness: `review`' "$tmp_dir/stale-external-evidence/v4-stable-publication.md"
grep -q 'Security review freshness: `review`' "$tmp_dir/stale-external-evidence/v4-stable-publication.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/stale-external-evidence" \
  --out "$tmp_dir/stale-external-evidence-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stale-external-evidence-quality/ios-report-quality.json"

SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard v4 stable-publication \
    --path . \
    --out "$tmp_dir/pass" \
    --github-api-url "file://$api_root" \
    --release-version "v$version" \
    --release-candidate-report "$tmp_dir/candidate-pass.json" \
    --download-release-assets \
    --download-release-assets-dir "$tmp_dir/pass-downloaded" \
    --release-consume-out "$tmp_dir/pass-consume" \
    --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
    --security-review-evidence "$tmp_dir/evidence/stable-security" \
    --shipguard-eval \
    --shareable >/dev/null

default_rerun_out="$tmp_dir/pass-default-rerun"
SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard v4 stable-publication \
    --path . \
    --out "$default_rerun_out" \
    --github-api-url "file://$api_root" \
    --release-version "v$version" \
    --release-candidate-report "$tmp_dir/candidate-pass.json" \
    --download-release-assets \
    --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
    --security-review-evidence "$tmp_dir/evidence/stable-security" \
    --shipguard-eval \
    --shareable >/dev/null
printf 'stale' > "$default_rerun_out/downloaded-release-assets/stale.txt"
SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard v4 stable-publication \
    --path . \
    --out "$default_rerun_out" \
    --github-api-url "file://$api_root" \
    --release-version "v$version" \
    --release-candidate-report "$tmp_dir/candidate-pass.json" \
    --download-release-assets \
    --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
    --security-review-evidence "$tmp_dir/evidence/stable-security" \
    --shipguard-eval \
    --shareable >/dev/null
test ! -e "$default_rerun_out/downloaded-release-assets/stale.txt"
python3 - "$default_rerun_out/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "pass"
assert report["githubReleaseAssetDownloadProof"]["status"] == "pass"
assert report["publishedReleaseAssetProof"]["status"] == "pass"
assert report["postReleaseConsumerProof"]["status"] == "pass"
PY
custom_download_dir="$tmp_dir/custom-download-protected"
mkdir -p "$custom_download_dir"
printf 'keep' > "$custom_download_dir/keep.txt"
if SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard v4 stable-publication \
    --path . \
    --out "$tmp_dir/custom-download-protected-run" \
    --github-api-url "file://$api_root" \
    --release-version "v$version" \
    --release-candidate-report "$tmp_dir/candidate-pass.json" \
    --download-release-assets \
    --download-release-assets-dir "$custom_download_dir" \
    --external-adoption-evidence "$tmp_dir/evidence/stable-adoption" \
    --security-review-evidence "$tmp_dir/evidence/stable-security" \
    --shipguard-eval \
    --shareable >/dev/null 2>&1; then
  echo "custom download destinations must still reject non-empty directories" >&2
  exit 1
fi
test -f "$custom_download_dir/keep.txt"

test -f "$tmp_dir/pass/v4-stable-publication.json"
test -f "$tmp_dir/pass/v4-stable-publication.md"
test -f "$tmp_dir/pass-consume/consumer-report.json"
python3 - "$tmp_dir/pass/v4-stable-publication.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["tool"] == "shipguard v4 stable-publication"
assert report["surface"] == "ShipGuard V4 Stable Publication Proof"
assert report["status"] == "pass"
assert report["stableV4Release"] is True
assert report["githubReleaseRepoInference"]["used"] is True
assert report["githubReleaseRepoInference"]["repo"] == "jlekerli-source/ShipGuard"
assert report["githubReleaseMetadataProof"]["status"] == "pass"
assert report["githubReleaseMetadataProof"]["repoInference"]["used"] is True
assert report["releaseNotesProof"]["status"] == "pass"
assert report["releaseNotesProof"]["missingTopicIds"] == []
assert len(report["releaseNotesProof"]["topicMatrix"]) == 7
assert report["releaseNotesProof"]["releaseNotesSha256"]
assert report["stablePublicationReleaseNotesAuthoringKit"]["draftOnly"] is True
assert report["stablePublicationReleaseNotesAuthoringKit"]["missingTopicIds"] == []
assert report["releaseCandidatePacketProof"]["status"] == "pass"
assert report["githubReleaseAssetDownloadProof"]["status"] == "pass"
assert report["publishedReleaseAssetProof"]["status"] == "pass"
assert report["postReleaseConsumerProof"]["status"] == "pass"
digest = report["postReleaseConsumerProof"]["consumerDigestFreshness"]
assert digest["status"] == "pass"
assert digest["releaseTarballDigestMatchesConsumerArtifact"] is True
assert digest["missingRequiredAssetNames"] == []
assert digest["missingSha256AssetNames"] == []
assert f"shipguard-v{report['releaseVersion'].removeprefix('v')}.tar.gz" in digest["requiredAssetNames"]
assert report["publicReleaseFreshnessProof"]["status"] == "pass"
assert report["publicReleaseFreshnessProof"]["comparisons"]["tagTargetMatchesManifestCommit"] is True
version_coherence = report["releaseVersionCoherenceProof"]
assert version_coherence["status"] == "pass"
assert version_coherence["comparisons"]["sourceVersionMatchesRequested"] is True
assert version_coherence["comparisons"]["metadataReturnedTagMatchesRequested"] is True
assert version_coherence["comparisons"]["manifestVersionMatchesRequested"] is True
assert version_coherence["comparisons"]["packageVersionMatchesRequested"] is True
assert version_coherence["comparisons"]["consumerReportVersionMatchesRequested"] is True
assert version_coherence["expectedTarballName"] == f"shipguard-v{report['releaseVersion'].removeprefix('v')}.tar.gz"
asset_coherence = report["releaseAssetCoherenceProof"]
assert asset_coherence["status"] == "pass"
assert asset_coherence["comparisons"]["localAssetsCoverRequired"] is True
assert asset_coherence["comparisons"]["digestAssetsCoverRequired"] is True
assert asset_coherence["comparisons"]["expectedTarballInLocalAssets"] is True
assert asset_coherence["comparisons"]["manifestArtifactShaMatchesDigestTarball"] is True
assert asset_coherence["comparisons"]["consumerArtifactShaMatchesDigestTarball"] is True
assert asset_coherence["missingLocalAssetNames"] == []
assert asset_coherence["missingDigestAssetNames"] == []
assert asset_coherence["missingSha256AssetNames"] == []
assert report["externalAdoptionEvidenceProof"]["stableV4GateStatus"] == "pass"
assert report["securityReviewEvidenceProof"]["stableV4GateStatus"] == "pass"
adoption_freshness = report["externalAdoptionEvidenceProof"]["evidencePacketFreshness"]
security_freshness = report["securityReviewEvidenceProof"]["evidencePacketFreshness"]
assert adoption_freshness["status"] == "pass"
assert security_freshness["status"] == "pass"
assert adoption_freshness["referenceTimestamp"] == "2026-06-20T00:00:00Z"
assert security_freshness["referenceTimestamp"] == "2026-06-20T00:00:00Z"
assert adoption_freshness["freshStableRecordCount"] == 1
assert security_freshness["freshStableRecordCount"] == 1
assert adoption_freshness["staleStableRecordCount"] == 0
assert security_freshness["staleStableRecordCount"] == 0
assert adoption_freshness["freshnessBoundary"]["generatedAtMustBeNoEarlierThanReleaseManifest"] is True
assert adoption_freshness["freshnessBoundary"]["sourceOnlyProofRefreshesExternalEvidence"] is False
public_evidence = report["publicEvidenceClosureProof"]
assert public_evidence["status"] == "pass"
assert public_evidence["missingOrBlockingEvidenceIds"] == []
assert {row["id"] for row in public_evidence["evidenceRows"]} == {
    "independent-adoption-evidence",
    "final-security-review-evidence",
}
assert all(row["freshnessStatus"] == "pass" for row in public_evidence["evidenceRows"])
assert public_evidence["publicEvidenceBoundary"]["fixtureEvidenceCountsAsStableV4Evidence"] is False
assert public_evidence["publicEvidenceBoundary"]["doesNotPostOrSubmitExternally"] is True
delta = report["publicReleaseDeltaProof"]
assert delta["status"] == "pass"
assert delta["sourceVersion"] == report["version"]
assert delta["releaseVersion"] == report["releaseVersion"]
assert delta["latestGitHubReleaseVersion"] == report["releaseVersion"].removeprefix("v")
assert delta["packageVersion"] == report["releaseVersion"].removeprefix("v")
assert delta["unpublishedLocalDelta"] is False
assert delta["stableV4ClaimCoversSelectedPublicRelease"] is True
assert delta["stableV4ClaimCoversLocalCheckout"] is True
assert delta["comparisons"]["selectedReleaseMatchesLatestGitHubRelease"] is True
assert delta["comparisons"]["localHeadMatchesSelectedPublicReleaseCommit"] is True
assert delta["comparisons"]["localMainMatchesSelectedPublicReleaseCommit"] is True
assert delta["comparisons"]["releaseVersionCoherencePassed"] is True
assert delta["comparisons"]["releaseAssetCoherencePassed"] is True
assert delta["releaseDeltaBoundary"]["localHeadIsNotPublicReleaseProof"] is True
assert delta["releaseDeltaBoundary"]["localMainIsNotPublicReleaseProof"] is True
assert delta["releaseDeltaBoundary"]["unpublishedLocalCodeCountsAsReleased"] is False
visibility = report["releaseVisibilityHandoff"]
assert visibility["status"] == "pass"
assert visibility["primaryDecision"] == "announce-current-public-release"
assert visibility["currentPublicReleaseCanBeAnnounced"] is True
assert visibility["localMainCanBeAnnounced"] is True
assert visibility["visibilityBoundary"]["latestPublicGitHubReleaseIsPublicationTruth"] is True
assert visibility["visibilityBoundary"]["localMainIsNotPublicationProof"] is True
actions = {item["id"]: item for item in visibility["requiredActions"]}
assert {
    "publish-new-github-release",
    "update-release-notes",
    "attach-launchkey-candidate-proof",
    "update-release-assets",
    "attach-adoption-security-evidence",
    "keep-current-public-release-unchanged",
} <= set(actions)
assert actions["publish-new-github-release"]["required"] is False
assert actions["publish-new-github-release"]["nextCommand"] == "not-needed"
assert actions["attach-launchkey-candidate-proof"]["required"] is False
assert actions["attach-launchkey-candidate-proof"]["nextCommand"] == "not-needed"
assert actions["update-release-assets"]["nextCommand"] == "not-needed"
assert actions["attach-adoption-security-evidence"]["nextCommand"] == "not-needed"
assert actions["keep-current-public-release-unchanged"]["required"] is True
assert actions["keep-current-public-release-unchanged"]["nextCommand"] != "blocked-by-required-actions"
final_claim = report["finalStableV4ClaimPacket"]
assert final_claim["status"] == "allowed"
assert final_claim["claimDecision"] == "allowed"
assert final_claim["stableV4Release"] is True
assert "has passed stable-v4 publication proof" in final_claim["copyReadyClaim"]
delta_summary = final_claim["publicReleaseDeltaSummary"]
assert delta_summary["status"] == "pass"
assert delta_summary["unpublishedLocalDelta"] is False
assert delta_summary["stableV4ClaimCoversSelectedPublicRelease"] is True
assert delta_summary["stableV4ClaimCoversLocalCheckout"] is True
assert delta_summary["unpublishedLocalCodeCountsAsReleased"] is False
assert final_claim["missingEvidenceIds"] == []
assert final_claim["firstBlockingGate"] is None
assert final_claim["publicEvidenceClosureStatus"] == "pass"
assert len(final_claim["evidenceSummary"]) == 10
assert all(item["status"] == "pass" for item in final_claim["evidenceSummary"])
assert final_claim["claimBoundary"]["allRequiredEvidenceMustPass"] is True
assert final_claim["claimBoundary"]["sourceOnlyProofCountsAsStableV4"] is False
assert final_claim["claimBoundary"]["fixtureProofCountsAsStableV4"] is False
assert final_claim["claimBoundary"]["marketplaceAcceptanceClaimed"] is False
assert final_claim["claimBoundary"]["externalPostingClaimed"] is False
assert final_claim["approvalBoundary"]["publicPostingRequiresExplicitApproval"] is True
assert final_claim["approvalBoundary"]["computerUseMayPost"] is False
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["shipguardEval"]["mode"] == "ShipGuard product QA"
assert "value-gauntlet" in report["resultUX"]["nextCommand"]
packet = report["stablePublicationEvidencePacket"]
assert packet["status"] == "pass"
assert packet["stableV4Release"] is True
assert packet["requiredEvidenceCount"] == 10
assert packet["passedEvidenceCount"] == 10
assert packet["missingEvidenceIds"] == []
assert packet["firstBlockingGate"] is None
closure = report["stablePublicationClosureChecklist"]
assert closure["status"] == "pass"
assert closure["blockerCount"] == 0
assert closure["blockedEvidenceIds"] == []
assert closure["items"] == []
assert closure["firstBlocker"] is None
ids = {item["id"] for item in packet["requiredEvidence"]}
assert {
    "github-release-metadata",
    "release-notes",
    "launchkey-candidate-packet",
    "downloaded-release-assets",
    "post-release-consumer-proof",
    "public-release-freshness",
    "release-version-coherence",
    "release-asset-coherence",
    "independent-adoption-evidence",
    "final-security-review-evidence",
} <= ids
assert all(item["requiredForStableV4"] and item["realEvidenceRequired"] for item in packet["requiredEvidence"])
templates = report["stablePublicationEvidenceTemplates"]
assert templates["draftOnly"] is True
assert len(templates["templates"]) == 2
starter = report["stablePublicationEvidenceStarterKit"]
assert starter["schemaVersion"] == 2
assert starter["draftOnly"] is True
assert starter["directory"] == "stable-publication-evidence-kit"
assert starter["releaseVersion"] == report["releaseVersion"]
related = {item["id"]: item for item in starter["relatedAuthoringKits"]}
assert related["release-notes-authoring-kit"]["directory"] == "stable-publication-release-notes"
assert "stable-publication-evidence-kit/security-review-evidence.json" in starter["nextCommandTemplate"]
relay = report["stablePublicationLaunchRelayDrafts"]
assert relay["draftOnly"] is True
assert relay["directory"] == "stable-publication-launch-relay"
assert relay["status"] == "ready-to-stage"
assert relay["approvalRequired"] is True
assert relay["publicPostingAllowed"] is False
assert relay["postingPolicy"]["requiresExplicitApproval"] is True
assert relay["postingPolicy"]["computerUseMayPost"] is False
assert {item["id"] for item in relay["channels"]} == {"product-hunt", "reddit-r-shipguard", "x-thread", "hacker-news"}
required_by_id = {item["id"]: item for item in packet["requiredEvidence"]}
assert "templateCommand" in required_by_id["independent-adoption-evidence"]
assert "templateCommand" in required_by_id["final-security-review-evidence"]
PY

grep -q '# ShipGuard V4 Stable Publication Proof' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Stable Publication Gates' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Evidence Packet' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Closure Checklist' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Remaining blockers: `0`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release Notes Proof' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release Notes Authoring Kit' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Launch Relay Drafts' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Public posting allowed: `False`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'External Evidence Freshness' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Public Evidence Closure' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Public Release Delta' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Unpublished local code counts as released: `False`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release Visibility Handoff' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Primary decision: `announce-current-public-release`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'keep-current-public-release-unchanged' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Final Stable V4 Claim Packet' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Claim decision: `allowed`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'has passed stable-v4 publication proof' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Final claim public-release delta' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Unpublished local delta: `False`' "$tmp_dir/pass/v4-stable-publication.md"
python3 - "$tmp_dir/pass/v4-stable-publication.md" <<'PY'
from pathlib import Path
import sys

markdown = Path(sys.argv[1]).read_text(encoding="utf-8")
section = markdown.split("## Final Stable V4 Claim Packet", 1)[1].split("\n## ", 1)[0]
table = section.index("| Evidence | Status |")
row = section.index("| `github-release-metadata` |", table)
delta = section.index("Final claim public-release delta:", row)
assert table < row < delta
PY
grep -q 'Release Version Coherence' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release Asset Coherence' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release version coherence: `pass`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release asset coherence: `pass`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Public evidence closure: `pass`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'External adoption freshness: `pass`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Security review freshness: `pass`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'independent-adoption-evidence' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Evidence Templates' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Evidence Starter Kit' "$tmp_dir/pass/v4-stable-publication.md"
grep -Eq 'Release version: `v?3\.131\.0`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'stable-publication-release-notes' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Stable v4 release claim allowed: `True`' "$tmp_dir/pass/v4-stable-publication.md"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/README.md"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q '"relatedAuthoringKits":' "$tmp_dir/pass/stable-publication-evidence-kit/stable-publication-checklist.json"
grep -q 'Release notes kit: `stable-publication-release-notes`' "$tmp_dir/pass/stable-publication-evidence-kit/README.md"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/external-adoption-evidence.json"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/security-review-evidence.json"
test -f "$tmp_dir/pass/stable-publication-release-notes/README.md"
test -f "$tmp_dir/pass/stable-publication-release-notes/release-notes-checklist.json"
test -f "$tmp_dir/pass/stable-publication-release-notes/draft-release-notes.md"
test -f "$tmp_dir/pass/stable-publication-launch-relay/README.md"
test -f "$tmp_dir/pass/stable-publication-launch-relay/launch-relay-checklist.json"
test -f "$tmp_dir/pass/stable-publication-launch-relay/product-hunt-draft.md"
test -f "$tmp_dir/pass/stable-publication-launch-relay/reddit-r-shipguard-draft.md"
test -f "$tmp_dir/pass/stable-publication-launch-relay/x-thread-draft.md"
test -f "$tmp_dir/pass/stable-publication-launch-relay/hacker-news-draft.md"

python3 - <<'PY'
from scripts.v4_stable_publication import build_release_visibility_handoff

delta = {
    "status": "review",
    "releaseVersion": "3.131.0",
    "latestGitHubReleaseVersion": "3.131.0",
    "selectedGitHubReleaseTag": "v3.131.0",
    "latestGitHubReleaseTag": "v3.131.0",
    "unpublishedLocalDelta": True,
    "stableV4ClaimCoversSelectedPublicRelease": True,
    "stableV4ClaimCoversLocalCheckout": False,
    "comparisons": {
        "selectedReleaseMatchesLatestGitHubRelease": True,
        "publicTagTargetMatchesReleaseManifestCommit": True,
        "packageAssetsVersionMatchesRequestedRelease": True,
    },
}
handoff = build_release_visibility_handoff(
    release_version="3.131.0",
    stable_v4_release=True,
    release_notes_proof={"status": "pass", "summary": "Release notes passed."},
    release_notes_authoring_kit={"publicReleaseEditCommand": "gh release edit v3.131.0 --repo example/shipguard --notes-file stable-publication-release-notes/draft-release-notes.md"},
    release_candidate_packet_proof={"status": "pass", "summary": "Candidate proof passed."},
    published_asset_proof={"status": "pass"},
    public_evidence_closure_proof={"status": "pass", "summary": "Public evidence passed."},
    public_release_delta_proof=delta,
    release_asset_coherence_proof={"status": "pass"},
    final_claim_packet={"nextCommand": "next"},
    rerun_command="rerun",
)
actions = {item["id"]: item for item in handoff["requiredActions"]}
assert handoff["primaryDecision"] == "announce-current-public-release"
assert handoff["currentPublicReleaseCanBeAnnounced"] is True
assert handoff["localMainCanBeAnnounced"] is False
assert actions["publish-new-github-release"]["required"] is False
assert actions["keep-current-public-release-unchanged"]["required"] is True
PY
grep -q '"publicPostingAllowed": false' "$tmp_dir/pass/stable-publication-launch-relay/launch-relay-checklist.json"
grep -q 'Draft only until explicit approval' "$tmp_dir/pass/stable-publication-launch-relay/x-thread-draft.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/pass" \
  --out "$tmp_dir/pass-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/pass-quality/ios-report-quality.json"
grep -q 'stable-publication proof is the current release proof source' "$tmp_dir/pass-quality/ios-report-quality.json"

if grep -R -F -q "$tmp_dir" "$tmp_dir/pass/v4-stable-publication.json" "$tmp_dir/pass/v4-stable-publication.md"; then
  echo "shareable stable-publication output must redact local tmp paths" >&2
  exit 1
fi

echo "v4 stable publication tests passed"
