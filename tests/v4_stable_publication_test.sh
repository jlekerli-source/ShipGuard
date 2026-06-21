#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

version="$(sed -n '1p' VERSION)"

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

SHIPGUARD_GENERATED_AT="2026-06-20T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
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
            "published_at": "2026-06-20T00:00:00Z",
            "target_commitish": "0123456789abcdef0123456789abcdef01234567",
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
assert packet["requiredEvidenceCount"] == 7
assert packet["passedEvidenceCount"] < 7
assert "launchkey-candidate-packet" in packet["missingEvidenceIds"]
assert packet["firstBlockingGate"]["receipt"] == "releaseCandidatePacketProof"
assert packet["firstBlockingGate"]["nextCommand"].startswith("./bin/shipguard v4 release-candidate")
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
assert starter["draftOnly"] is True
assert starter["directory"] == "stable-publication-evidence-kit"
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
grep -q 'Stable Publication Evidence Kit' "$tmp_dir/blocked/stable-publication-evidence-kit/README.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/README.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/product-hunt-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/reddit-r-shipguard-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/x-thread-draft.md"
test -f "$tmp_dir/blocked/stable-publication-launch-relay/hacker-news-draft.md"
grep -q '"publicPostingAllowed": false' "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
grep -q '"computerUseMayPost": false' "$tmp_dir/blocked/stable-publication-launch-relay/launch-relay-checklist.json"
grep -q 'Stable Publication Launch Relay' "$tmp_dir/blocked/stable-publication-launch-relay/README.md"

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
            "published_at": "2026-06-20T00:00:00Z",
            "target_commitish": "0123456789abcdef0123456789abcdef01234567",
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
missing = set(report["releaseNotesProof"]["missingTopicIds"])
assert {
    "downloaded-release-assets",
    "post-release-consumer-proof",
    "independent-adoption-evidence",
    "final-security-review-evidence",
    "non-claims-boundary",
} <= missing
assert len(report["releaseNotesProof"]["topicMatrix"]) == 7
notes_kit = report["stablePublicationReleaseNotesAuthoringKit"]
assert notes_kit["draftOnly"] is True
assert notes_kit["directory"] == "stable-publication-release-notes"
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
grep -q 'post-release-consumer-proof' "$tmp_dir/weak-notes/v4-stable-publication.md"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/README.md"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/release-notes-checklist.json"
test -f "$tmp_dir/weak-notes/stable-publication-release-notes/draft-release-notes.md"
grep -q 'Post-release consumer proof' "$tmp_dir/weak-notes/stable-publication-release-notes/draft-release-notes.md"
grep -q '"draftOnly": true' "$tmp_dir/weak-notes/stable-publication-release-notes/release-notes-checklist.json"

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
            "published_at": "2026-06-20T00:00:00Z",
            "target_commitish": "0123456789abcdef0123456789abcdef01234567",
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
assert report["externalAdoptionEvidenceProof"]["stableV4GateStatus"] == "pass"
assert report["securityReviewEvidenceProof"]["stableV4GateStatus"] == "pass"
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["shipguardEval"]["mode"] == "ShipGuard product QA"
assert "value-gauntlet" in report["resultUX"]["nextCommand"]
packet = report["stablePublicationEvidencePacket"]
assert packet["status"] == "pass"
assert packet["stableV4Release"] is True
assert packet["requiredEvidenceCount"] == 7
assert packet["passedEvidenceCount"] == 7
assert packet["missingEvidenceIds"] == []
assert packet["firstBlockingGate"] is None
ids = {item["id"] for item in packet["requiredEvidence"]}
assert {
    "github-release-metadata",
    "release-notes",
    "launchkey-candidate-packet",
    "downloaded-release-assets",
    "post-release-consumer-proof",
    "independent-adoption-evidence",
    "final-security-review-evidence",
} <= ids
assert all(item["requiredForStableV4"] and item["realEvidenceRequired"] for item in packet["requiredEvidence"])
templates = report["stablePublicationEvidenceTemplates"]
assert templates["draftOnly"] is True
assert len(templates["templates"]) == 2
starter = report["stablePublicationEvidenceStarterKit"]
assert starter["draftOnly"] is True
assert starter["directory"] == "stable-publication-evidence-kit"
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
grep -q 'Release Notes Proof' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Release Notes Authoring Kit' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Launch Relay Drafts' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Public posting allowed: `False`' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'independent-adoption-evidence' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Evidence Templates' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Evidence Starter Kit' "$tmp_dir/pass/v4-stable-publication.md"
grep -q 'Stable v4 release claim allowed: `True`' "$tmp_dir/pass/v4-stable-publication.md"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/README.md"
test -f "$tmp_dir/pass/stable-publication-evidence-kit/stable-publication-checklist.json"
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
