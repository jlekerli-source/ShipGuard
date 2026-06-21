#!/usr/bin/env python3
"""Generate the ShipGuard v4 stable-publication proof report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import v4_release_candidate as launchkey
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import v4_release_candidate as launchkey
    from shipguard_result import build_result_ux, render_result_markdown


SURFACE = "ShipGuard V4 Stable Publication Proof"
TOOL = "shipguard v4 stable-publication"
SCHEMA_VERSION = 1
REQUIRED_RELEASE_ASSETS = {
    "release-manifest.json",
    "release-index.json",
    "proof-ledger.md",
    "replay-report.json",
    "attestation.json",
    "attestation-badge.json",
}
RELEASE_NOTES_TOPIC_RULES = [
    {
        "id": "stable-v4-claim",
        "title": "Stable v4 release claim",
        "terms": ("stable-v4", "stable v4"),
        "summary": "Names the stable-v4 release claim explicitly.",
    },
    {
        "id": "publication-proof-boundary",
        "title": "Publication proof boundary",
        "terms": ("publication proof", "release proof", "stable-publication", "stable publication"),
        "summary": "Explains that stable publication depends on proof, not intent.",
    },
    {
        "id": "downloaded-release-assets",
        "title": "Downloaded release assets",
        "terms": ("downloaded release asset", "release asset", "release assets"),
        "summary": "Mentions downloaded release assets or asset verification.",
    },
    {
        "id": "post-release-consumer-proof",
        "title": "Post-release consumer proof",
        "terms": ("post-release consumer", "consumer proof", "release-consume", "release consume"),
        "summary": "Mentions post-release consumer verification.",
    },
    {
        "id": "independent-adoption-evidence",
        "title": "Independent adoption evidence",
        "terms": ("independent adoption", "external adoption", "adoption evidence"),
        "summary": "Mentions independent or external adoption evidence.",
    },
    {
        "id": "final-security-review-evidence",
        "title": "Final security review evidence",
        "terms": ("final security", "security review", "security evidence"),
        "summary": "Mentions final security review evidence.",
    },
    {
        "id": "non-claims-boundary",
        "title": "Non-claims boundary",
        "terms": ("non-claim", "nonclaim", "does not claim", "blocked claim", "blocked claims"),
        "summary": "States what the release notes do not prove or claim.",
    },
]

STABLE_PUBLICATION_TEMPLATE_DIR = "templates/stable-publication"
STABLE_PUBLICATION_TEMPLATE_SPECS = [
    {
        "id": "independent-adoption-evidence",
        "title": "Independent adoption evidence",
        "path": f"{STABLE_PUBLICATION_TEMPLATE_DIR}/external-adoption-evidence.template.json",
        "targetFile": "<evidence-dir>/external-adoption-evidence.json",
        "commandFlag": "--external-adoption-evidence",
        "evidenceType": "shipguard-external-adoption",
        "acceptedEvidenceClasses": ["public-external", "private-redacted-external"],
        "requiredFields": [
            "schemaVersion",
            "evidenceType",
            "evidenceClass",
            "actorRelationship",
            "generatedAt",
            "status",
            "privateDataRedacted",
            "commands",
            "artifacts",
            "outcome",
            "nonClaims",
        ],
        "stableRequirement": "Real independent public or private-redacted external adoption evidence; unchanged template records are draft-only and must not pass.",
    },
    {
        "id": "final-security-review-evidence",
        "title": "Final security review evidence",
        "path": f"{STABLE_PUBLICATION_TEMPLATE_DIR}/security-review-evidence.template.json",
        "targetFile": "<evidence-dir>/security-review-evidence.json",
        "commandFlag": "--security-review-evidence",
        "evidenceType": "shipguard-security-review",
        "acceptedEvidenceClasses": ["public-security-review", "private-redacted-security-review"],
        "requiredFields": [
            "schemaVersion",
            "evidenceType",
            "evidenceClass",
            "reviewerRelationship",
            "generatedAt",
            "status",
            "privateDataRedacted",
            "scope",
            "methodology",
            "commands",
            "artifacts",
            "findingsSummary",
            "nonClaims",
        ],
        "stableRequirement": "Real final review evidence covering CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings.",
    },
]
STARTER_KIT_DIRNAME = "stable-publication-evidence-kit"
RELEASE_NOTES_KIT_DIRNAME = "stable-publication-release-notes"
LAUNCH_RELAY_DIRNAME = "stable-publication-launch-relay"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def normalize_version(version: str) -> str:
    return version.removeprefix("v")


def github_repo_from_remote_url(remote_url: str) -> str:
    value = str(remote_url or "").strip()
    if not value:
        return ""
    patterns = [
        r"^git@github\.com:(?P<repo>[^/]+/[^/]+?)(?:\.git)?$",
        r"^https://github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return match.group("repo")
    return ""


def infer_github_release_repo(root: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", "-C", root.as_posix(), "config", "--get", "remote.origin.url"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return {"status": "not-detected", "source": "git-remote-origin", "repo": "", "remoteUrl": ""}
    remote_url = completed.stdout.strip()
    repo = github_repo_from_remote_url(remote_url)
    return {
        "status": "detected" if repo else "not-detected",
        "source": "git-remote-origin",
        "repo": repo,
        "remoteUrl": remote_url,
    }


def normalize_args(args: argparse.Namespace, root: Path) -> argparse.Namespace:
    normalized = argparse.Namespace(**vars(args))
    normalized.githubReleaseRepoInference = {
        "used": False,
        "status": "not-needed" if normalized.github_release_repo else "not-detected",
        "source": "explicit-argument" if normalized.github_release_repo else "git-remote-origin",
        "repo": normalized.github_release_repo or "",
    }
    if normalized.github_release_repo:
        return normalized
    inference = infer_github_release_repo(root)
    normalized.githubReleaseRepoInference = {
        **inference,
        "used": bool(inference.get("repo")),
    }
    if inference.get("repo"):
        normalized.github_release_repo = str(inference["repo"])
    return normalized


def stable_publication_command(args: argparse.Namespace, *, placeholders: bool = False) -> str:
    release_version = args.release_version or "<version>"
    repo = args.github_release_repo or "<owner/repo>"
    command = [
        "./bin/shipguard",
        "v4",
        "stable-publication",
        "--path",
        ".",
        "--out",
        "/tmp/shipguard-v4-stable-publication",
        "--github-release-repo",
        repo if not placeholders else "<owner/repo>",
        "--release-version",
        release_version if not placeholders else "<version>",
        "--release-candidate-report",
        "<v4-release-candidate-json-or-dir>" if placeholders else args.release_candidate_report or "<v4-release-candidate-json-or-dir>",
        "--download-release-assets",
        "--external-adoption-evidence",
        "<evidence-json-or-dir>",
        "--security-review-evidence",
        "<evidence-json-or-dir>",
        "--shipguard-eval",
        "--shareable",
    ]
    return " ".join(command)


def resolve_release_candidate_report(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    if path.is_dir():
        return path / "v4-release-candidate.json"
    return path


def build_release_candidate_packet_proof(args: argparse.Namespace) -> dict[str, Any]:
    path = resolve_release_candidate_report(args.release_candidate_report)
    if path is None:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No LaunchKey release-candidate report was supplied; stable publication needs prior package install, upgrade, and rollback proof.",
            "nextCommand": (
                "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> "
                "--package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> "
                "--download-release-assets --github-release-repo <owner/repo> --release-version <version> "
                "--external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> "
                "--shipguard-eval --shareable"
            ),
        }
    report = load_json(path)
    release_readiness = report.get("releaseReadiness") if isinstance(report.get("releaseReadiness"), dict) else {}
    required_statuses = {
        "freshInstallPackageProof": release_readiness.get("freshInstallPackageProof"),
        "upgradePackageProof": release_readiness.get("upgradePackageProof"),
        "rollbackPackageProof": release_readiness.get("rollbackPackageProof"),
    }
    missing = [key for key, value in required_statuses.items() if value != "pass"]
    tool_ok = report.get("tool") == "shipguard v4 release-candidate"
    status_ok = report.get("status") == "pass"
    claim_ok = release_readiness.get("releaseClaim") == "candidate-ready" and release_readiness.get("stableV4Release") is False
    proof = {
        "status": "pass" if tool_ok and status_ok and claim_ok and not missing else "review",
        "provided": True,
        "requiredForStableV4": True,
        "reportPath": path.as_posix(),
        "tool": report.get("tool"),
        "reportStatus": report.get("status"),
        "releaseClaim": release_readiness.get("releaseClaim"),
        "stableV4ReleaseClaimed": release_readiness.get("stableV4Release"),
        "requiredStatuses": required_statuses,
        "missingPackageProof": missing,
        "summary": "LaunchKey package install, upgrade, and rollback proof passed.",
        "nextCommand": "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable",
    }
    if not report:
        proof["status"] = "blocked"
        proof["summary"] = "LaunchKey release-candidate report could not be loaded."
        proof["error"] = "missing or invalid v4-release-candidate JSON"
    elif not tool_ok:
        proof["summary"] = "Supplied report is not a LaunchKey release-candidate report."
    elif not status_ok:
        proof["summary"] = "LaunchKey report has not passed."
    elif not claim_ok:
        proof["summary"] = "LaunchKey report does not prove candidate readiness without a stable-v4 claim."
    elif missing:
        proof["summary"] = "LaunchKey report is missing package install, upgrade, or rollback proof required for stable publication."
    return proof


def build_github_release_metadata_proof(args: argparse.Namespace, version: str) -> dict[str, Any]:
    release_version = args.release_version or version
    release_tag = launchkey.normalize_release_tag(release_version)
    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": bool(args.github_release_repo),
        "requiredForStableV4": True,
        "repo": args.github_release_repo or "",
        "repoInference": getattr(args, "githubReleaseRepoInference", {}),
        "version": release_version,
        "tag": release_tag,
        "apiUrl": args.github_api_url.rstrip("/"),
        "requiredAssets": sorted(REQUIRED_RELEASE_ASSETS | {f"shipguard-v{normalize_version(release_version)}.tar.gz"}),
        "nextCommand": stable_publication_command(args, placeholders=True),
    }
    if not args.github_release_repo:
        proof["status"] = "not-provided"
        proof["summary"] = "No GitHub release repository was supplied or detected from git remote origin."
        return proof
    if "/" not in args.github_release_repo:
        proof["summary"] = "GitHub release repository must use owner/repo syntax."
        proof["error"] = f"invalid --github-release-repo value: {args.github_release_repo}"
        return proof

    token = os.environ.get(args.github_token_env or "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "shipguard-stable-publication",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    endpoint = launchkey.join_api_url(args.github_api_url, f"/repos/{args.github_release_repo}/releases/tags/{release_tag}")
    proof["releaseEndpoint"] = endpoint
    try:
        release = launchkey.request_json(endpoint, headers)
    except (RuntimeError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        proof["summary"] = "GitHub release metadata could not be loaded."
        proof["error"] = launchkey.short_output(str(exc), 500)
        return proof

    assets = release.get("assets") if isinstance(release.get("assets"), list) else []
    asset_names = sorted(str(asset.get("name") or "") for asset in assets if isinstance(asset, dict))
    required_assets = set(proof["requiredAssets"])
    missing_assets = sorted(required_assets - set(asset_names))
    body = str(release.get("body") or "")
    release_notes_analysis = analyze_release_notes(body)
    proof.update(
        {
            "status": "pass" if not missing_assets else "review",
            "provided": True,
            "summary": "GitHub release metadata was loaded and required release assets are present.",
            "releaseUrl": release.get("html_url") or release.get("url") or "",
            "publishedAt": release.get("published_at") or release.get("publishedAt") or "",
            "targetCommitish": release.get("target_commitish") or release.get("targetCommitish") or "",
            "assetCount": len(asset_names),
            "assetNames": asset_names,
            "missingAssets": missing_assets,
            "releaseNotesLength": len(body.strip()),
            "releaseNotesLineCount": release_notes_analysis["lineCount"],
            "releaseNotesSha256": release_notes_analysis["sha256"],
            "releaseNotesPreview": launchkey.short_output(body, 700),
            "releaseNotesTopicMatrix": release_notes_analysis["topicMatrix"],
            "releaseNotesMissingTopicIds": release_notes_analysis["missingTopicIds"],
            "isDraft": bool(release.get("draft") or release.get("isDraft")),
            "isPrerelease": bool(release.get("prerelease") or release.get("isPrerelease")),
        }
    )
    if missing_assets:
        proof["summary"] = "GitHub release metadata loaded, but required stable-publication assets are missing."
    if proof["isDraft"] or proof["isPrerelease"]:
        proof["status"] = "review"
        proof["summary"] = "GitHub release exists but is draft or prerelease."
    return proof


def analyze_release_notes(body: str) -> dict[str, Any]:
    text = str(body or "").strip()
    normalized = re_normalized(text)
    topic_matrix: list[dict[str, Any]] = []
    for rule in RELEASE_NOTES_TOPIC_RULES:
        matched_terms = [term for term in rule["terms"] if term in normalized]
        topic_matrix.append(
            {
                "id": rule["id"],
                "title": rule["title"],
                "status": "pass" if matched_terms else "missing",
                "matchedTerms": matched_terms,
                "summary": rule["summary"],
            }
        )
    missing_topic_ids = [item["id"] for item in topic_matrix if item["status"] != "pass"]
    return {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else "",
        "lineCount": len(text.splitlines()) if text else 0,
        "topicMatrix": topic_matrix,
        "missingTopicIds": missing_topic_ids,
    }


def build_release_notes_proof(metadata_proof: dict[str, Any]) -> dict[str, Any]:
    topic_matrix = metadata_proof.get("releaseNotesTopicMatrix")
    if not isinstance(topic_matrix, list):
        topic_matrix = analyze_release_notes(str(metadata_proof.get("releaseNotesPreview") or ""))["topicMatrix"]
    missing_topic_ids = [str(item.get("id")) for item in topic_matrix if isinstance(item, dict) and item.get("status") != "pass"]
    pass_status = metadata_proof.get("status") == "pass" and not missing_topic_ids
    return {
        "status": "pass" if pass_status else "review",
        "requiredForStableV4": True,
        "summary": (
            "Release notes explicitly describe stable-v4 publication proof."
            if pass_status
            else "Release notes do not yet explicitly describe stable-v4 publication proof."
        ),
        "releaseNotesLength": metadata_proof.get("releaseNotesLength", 0),
        "releaseNotesLineCount": metadata_proof.get("releaseNotesLineCount", 0),
        "releaseNotesSha256": metadata_proof.get("releaseNotesSha256", ""),
        "topicMatrix": topic_matrix,
        "missingTopicIds": missing_topic_ids,
        "requiredLanguage": "Mention stable-v4 publication proof, downloaded release assets, post-release consumer proof, independent adoption evidence, final security review evidence, and non-claim boundaries.",
    }


def re_normalized(value: str) -> str:
    return " ".join(str(value).lower().split())


def build_post_release_consumer_proof(published_release_asset_proof: dict[str, Any]) -> dict[str, Any]:
    passed = published_release_asset_proof.get("status") == "pass"
    return {
        "status": "pass" if passed else published_release_asset_proof.get("status", "not-provided"),
        "requiredForStableV4": True,
        "summary": (
            "Downloaded release assets passed post-release consumer verification."
            if passed
            else "Post-release consumer proof needs downloaded assets to pass release-consume verification."
        ),
        "consumerReportStatus": published_release_asset_proof.get("consumerReportStatus"),
        "replayStatus": published_release_asset_proof.get("replayStatus"),
        "attestationStatus": published_release_asset_proof.get("attestationStatus"),
        "assetDigestMatrixPath": published_release_asset_proof.get("assetDigestMatrixPath"),
        "consumerReportPath": published_release_asset_proof.get("consumerReportPath"),
    }


def first_blocking_gate(gates: list[tuple[str, dict[str, Any], str]]) -> tuple[str, dict[str, Any], str] | None:
    for receipt, proof, command in gates:
        if proof.get("status") == "pass":
            continue
        return receipt, proof, command
    return None


def evidence_id_for_receipt(receipt: str) -> str:
    mapping = {
        "githubReleaseMetadataProof": "github-release-metadata",
        "releaseNotesProof": "release-notes",
        "releaseCandidatePacketProof": "launchkey-candidate-packet",
        "publishedReleaseAssetProof": "downloaded-release-assets",
        "postReleaseConsumerProof": "post-release-consumer-proof",
        "externalAdoptionEvidenceStableGate": "independent-adoption-evidence",
        "securityReviewEvidenceStableGate": "final-security-review-evidence",
    }
    return mapping.get(receipt, re.sub(r"[^a-z0-9]+", "-", receipt.lower()).strip("-"))


def build_stable_publication_evidence_templates(root: Path) -> dict[str, Any]:
    templates: list[dict[str, Any]] = []
    full_validate_command = (
        "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
        "--github-release-repo <owner/repo> --release-version <version> "
        "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
        "--external-adoption-evidence <adoption-evidence-json-or-dir> "
        "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
    )
    for spec in STABLE_PUBLICATION_TEMPLATE_SPECS:
        relative_path = str(spec["path"])
        target_file = str(spec["targetFile"])
        templates.append(
            {
                **spec,
                "exists": (root / relative_path).is_file(),
                "copyCommand": f"cp {relative_path} {target_file}",
                "attachArgument": f"{spec['commandFlag']} {target_file}",
                "validateCommand": full_validate_command,
            }
        )
    return {
        "schemaVersion": 1,
        "templateDirectory": STABLE_PUBLICATION_TEMPLATE_DIR,
        "templates": templates,
        "templateIds": [str(item["id"]) for item in templates],
        "draftOnly": True,
        "instructions": [
            "Copy a template into a private evidence directory, replace placeholder text with real reviewed evidence, and keep private app details redacted.",
            "Do not use unchanged templates as proof. They intentionally default to draft/privateDataRedacted=false so stable-publication blocks fake evidence.",
            "Pass the completed JSON file or directory to --external-adoption-evidence or --security-review-evidence.",
        ],
    }


def build_stable_publication_evidence_starter_kit_manifest() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "draftOnly": True,
        "directory": STARTER_KIT_DIRNAME,
        "files": [
            {
                "id": "checklist",
                "path": f"{STARTER_KIT_DIRNAME}/README.md",
                "purpose": "Human checklist for collecting the real stable-v4 publication packet.",
            },
            {
                "id": "stable-publication-checklist",
                "path": f"{STARTER_KIT_DIRNAME}/stable-publication-checklist.json",
                "purpose": "Machine-readable draft checklist with the seven required stable-publication gates.",
            },
            {
                "id": "independent-adoption-evidence",
                "path": f"{STARTER_KIT_DIRNAME}/external-adoption-evidence.json",
                "sourceTemplate": "templates/stable-publication/external-adoption-evidence.template.json",
                "attachArgument": f"--external-adoption-evidence {STARTER_KIT_DIRNAME}/external-adoption-evidence.json",
                "purpose": "Draft-only independent adoption evidence record. Fill with real external evidence before use.",
            },
            {
                "id": "final-security-review-evidence",
                "path": f"{STARTER_KIT_DIRNAME}/security-review-evidence.json",
                "sourceTemplate": "templates/stable-publication/security-review-evidence.template.json",
                "attachArgument": f"--security-review-evidence {STARTER_KIT_DIRNAME}/security-review-evidence.json",
                "purpose": "Draft-only final security-review evidence record. Fill with real review evidence before use.",
            },
        ],
        "instructions": [
            "These files are generated as a starter kit only; unchanged starter-kit JSON must not pass stable-publication.",
            "Replace placeholder values with real reviewed evidence, keep private paths and private app details redacted, then pass the completed files back to v4 stable-publication.",
            "Use the report's firstBlockingGate and this checklist together; do not claim stable v4 until v4 stable-publication returns pass.",
        ],
        "nextCommandTemplate": (
            "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
            "--github-release-repo <owner/repo> --release-version <version> "
            "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
            f"--external-adoption-evidence {STARTER_KIT_DIRNAME}/external-adoption-evidence.json "
            f"--security-review-evidence {STARTER_KIT_DIRNAME}/security-review-evidence.json "
            "--shipguard-eval --shareable"
        ),
    }


def build_stable_publication_release_notes_authoring_kit(
    *,
    release_version: str,
    release_notes_proof: dict[str, Any],
) -> dict[str, Any]:
    missing_topic_ids = release_notes_proof.get("missingTopicIds")
    if not isinstance(missing_topic_ids, list):
        missing_topic_ids = []
    topic_matrix = release_notes_proof.get("topicMatrix")
    if not isinstance(topic_matrix, list):
        topic_matrix = []
    return {
        "schemaVersion": 1,
        "draftOnly": True,
        "directory": RELEASE_NOTES_KIT_DIRNAME,
        "releaseVersion": release_version,
        "status": "pass" if release_notes_proof.get("status") == "pass" else "review",
        "missingTopicIds": missing_topic_ids,
        "topicMatrix": topic_matrix,
        "files": [
            {
                "id": "checklist",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/release-notes-checklist.json",
                "purpose": "Machine-readable checklist for the stable-publication release-notes topics.",
            },
            {
                "id": "draft-release-notes",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/draft-release-notes.md",
                "purpose": "Draft-only release notes section that includes every required stable-publication proof topic.",
            },
            {
                "id": "copy-brief",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/README.md",
                "purpose": "Human instructions for adapting the draft into the public GitHub release body.",
            },
        ],
        "instructions": [
            "Use this as a release-notes authoring aid only; it is not proof that a GitHub release was published.",
            "Replace placeholders with the real release version, asset list, adoption summary, security review summary, and non-claims before publishing.",
            "Run stable-publication again against the public GitHub release metadata after editing the release notes.",
        ],
        "nextCommandTemplate": (
            "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
            "--github-release-repo <owner/repo> --release-version <version> "
            "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
            "--external-adoption-evidence <adoption-evidence-json-or-dir> "
            "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
        ),
    }


def build_stable_publication_launch_relay_drafts(
    *,
    release_version: str,
    stable_v4_release: bool,
    evidence_packet: dict[str, Any],
) -> dict[str, Any]:
    status = "ready-to-stage" if stable_v4_release else "blocked-until-stable-publication-pass"
    return {
        "schemaVersion": 1,
        "draftOnly": True,
        "directory": LAUNCH_RELAY_DIRNAME,
        "releaseVersion": release_version,
        "status": status,
        "approvalRequired": True,
        "publicPostingAllowed": False,
        "postingPolicy": {
            "requiresExplicitApproval": True,
            "publicPostingAllowed": False,
            "computerUseMayStageDrafts": True,
            "computerUseMayPost": False,
            "approvalText": (
                "Public posting, publishing, submission, or account-visible external actions require explicit human "
                "approval for that exact launch run."
            ),
            "prohibitedActions": [
                "submit Product Hunt launch",
                "post to r/ShipGuard or any subreddit",
                "publish X posts or threads",
                "submit to Hacker News",
                "change account-visible public settings",
            ],
            "allowedActions": [
                "write local draft copy",
                "prepare screenshots or asset checklists",
                "stage browser fields only after explicit approval for that exact launch run",
            ],
        },
        "channels": [
            {
                "id": "product-hunt",
                "name": "Product Hunt",
                "draftPath": f"{LAUNCH_RELAY_DIRNAME}/product-hunt-draft.md",
                "approvalGate": "explicit-human-approval-required",
            },
            {
                "id": "reddit-r-shipguard",
                "name": "r/ShipGuard",
                "draftPath": f"{LAUNCH_RELAY_DIRNAME}/reddit-r-shipguard-draft.md",
                "approvalGate": "explicit-human-approval-required",
            },
            {
                "id": "x-thread",
                "name": "X thread",
                "draftPath": f"{LAUNCH_RELAY_DIRNAME}/x-thread-draft.md",
                "approvalGate": "explicit-human-approval-required",
            },
            {
                "id": "hacker-news",
                "name": "Hacker News",
                "draftPath": f"{LAUNCH_RELAY_DIRNAME}/hacker-news-draft.md",
                "approvalGate": "explicit-human-approval-required",
            },
        ],
        "files": [
            {
                "id": "readme",
                "path": f"{LAUNCH_RELAY_DIRNAME}/README.md",
                "purpose": "Human launch-relay guardrails and approval boundary.",
            },
            {
                "id": "checklist",
                "path": f"{LAUNCH_RELAY_DIRNAME}/launch-relay-checklist.json",
                "purpose": "Machine-readable draft-only launch checklist and posting policy.",
            },
            {
                "id": "product-hunt-draft",
                "path": f"{LAUNCH_RELAY_DIRNAME}/product-hunt-draft.md",
                "purpose": "Draft Product Hunt launch copy; not submitted by ShipGuard.",
            },
            {
                "id": "reddit-r-shipguard-draft",
                "path": f"{LAUNCH_RELAY_DIRNAME}/reddit-r-shipguard-draft.md",
                "purpose": "Draft subreddit announcement; not posted by ShipGuard.",
            },
            {
                "id": "x-thread-draft",
                "path": f"{LAUNCH_RELAY_DIRNAME}/x-thread-draft.md",
                "purpose": "Draft X thread; not posted by ShipGuard.",
            },
            {
                "id": "hacker-news-draft",
                "path": f"{LAUNCH_RELAY_DIRNAME}/hacker-news-draft.md",
                "purpose": "Draft Hacker News submission notes; not submitted by ShipGuard.",
            },
        ],
        "proofSource": "stablePublicationEvidencePacket",
        "proofStatus": evidence_packet.get("status"),
        "stableV4Release": stable_v4_release,
        "requiredBeforePosting": [
            "stablePublicationEvidencePacket.status == pass",
            "stableV4Release == true",
            "public release notes reviewed",
            "independent adoption and final security evidence attached",
            "explicit human approval for the exact launch run",
        ],
        "nonClaims": [
            "This packet does not publish, submit, post, or schedule anything.",
            "This packet does not authorize computer-use to perform account-visible actions.",
            "Draft copy must not claim adoption, security review, marketplace acceptance, or performance numbers beyond attached evidence.",
        ],
        "nextCommandTemplate": (
            "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
            "--github-release-repo <owner/repo> --release-version <version> "
            "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
            "--external-adoption-evidence <adoption-evidence-json-or-dir> "
            "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
        ),
    }


def build_stable_publication_evidence_packet(
    *,
    gates: list[tuple[str, dict[str, Any], str]],
    blocked: tuple[str, dict[str, Any], str] | None,
    release_version: str,
    stable_v4_release: bool,
    evidence_templates: dict[str, Any],
) -> dict[str, Any]:
    templates_by_id = {
        str(item.get("id")): item
        for item in evidence_templates.get("templates", [])
        if isinstance(item, dict)
    }
    required_evidence: list[dict[str, Any]] = []
    for receipt, proof, command in gates:
        status = str(proof.get("status") or "not-provided")
        evidence_id = evidence_id_for_receipt(receipt)
        item = {
            "id": evidence_id,
            "receipt": receipt,
            "status": status,
            "provided": bool(proof.get("provided", status == "pass")),
            "requiredForStableV4": True,
            "realEvidenceRequired": True,
            "summary": proof.get("summary") or f"{receipt} status is {status}.",
            "nextCommand": command,
        }
        template = templates_by_id.get(evidence_id)
        if template:
            item.update(
                {
                    "templateId": template.get("id"),
                    "templatePath": template.get("path"),
                    "templateCommand": template.get("copyCommand"),
                }
            )
        required_evidence.append(item)

    missing = [item for item in required_evidence if item.get("status") != "pass"]
    first_blocking = None
    if blocked:
        receipt, proof, command = blocked
        first_blocking = {
            "id": evidence_id_for_receipt(receipt),
            "receipt": receipt,
            "status": proof.get("status"),
            "summary": proof.get("summary") or f"{receipt} has not passed.",
            "nextCommand": command,
        }

    return {
        "schemaVersion": 1,
        "releaseVersion": release_version,
        "status": "pass" if not missing else "review",
        "stableV4Release": stable_v4_release,
        "requiredEvidence": required_evidence,
        "requiredEvidenceCount": len(required_evidence),
        "passedEvidenceCount": len(required_evidence) - len(missing),
        "missingEvidenceIds": [str(item.get("id")) for item in missing],
        "firstBlockingGate": first_blocking,
        "proofOrder": [
            "Run LaunchKey release-candidate proof with package install, upgrade, rollback, release assets, adoption, and security receipts.",
            "Publish the GitHub release with stable-v4 release notes and required release-proof assets.",
            "Run stable-publication against the published release metadata, downloaded assets, independent adoption evidence, and final security review evidence.",
            "Use a passing stable-publication report as the only local permission to claim ShipGuard v4 is stable.",
        ],
        "nonClaims": [
            "This packet does not publish a GitHub release.",
            "This packet does not prove OpenAI marketplace acceptance.",
            "Fixture adoption or fixture security records prove tooling only; they do not prove real stable-v4 publication.",
            "GitHub release metadata and download counts are not independent adoption evidence.",
        ],
    }


def write_stable_publication_evidence_starter_kit(
    out_dir: Path,
    *,
    report: dict[str, Any],
    root: Path,
) -> None:
    starter_kit = report.get("stablePublicationEvidenceStarterKit")
    if not isinstance(starter_kit, dict):
        return
    kit_dir = out_dir / STARTER_KIT_DIRNAME
    kit_dir.mkdir(parents=True, exist_ok=True)

    for spec in STABLE_PUBLICATION_TEMPLATE_SPECS:
        source = root / str(spec["path"])
        if not source.is_file():
            continue
        if spec["id"] == "independent-adoption-evidence":
            target = kit_dir / "external-adoption-evidence.json"
        elif spec["id"] == "final-security-review-evidence":
            target = kit_dir / "security-review-evidence.json"
        else:
            continue
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    packet = report.get("stablePublicationEvidencePacket") if isinstance(report.get("stablePublicationEvidencePacket"), dict) else {}
    checklist = {
        "schemaVersion": 1,
        "draftOnly": True,
        "status": packet.get("status", report.get("status")),
        "stableV4Release": False,
        "firstBlockingGate": packet.get("firstBlockingGate"),
        "requiredEvidence": packet.get("requiredEvidence", []),
        "missingEvidenceIds": packet.get("missingEvidenceIds", []),
        "blockedClaims": report.get("blockedClaims", []),
        "nextCommandTemplate": starter_kit.get("nextCommandTemplate"),
    }
    (kit_dir / "stable-publication-checklist.json").write_text(
        json.dumps(checklist, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    readme_lines = [
        "# Stable Publication Evidence Kit",
        "",
        "This directory is a draft-only starter kit for `shipguard v4 stable-publication`.",
        "It helps collect the real evidence packet; it is not evidence by itself.",
        "",
        "## Files",
        "",
        "- `stable-publication-checklist.json`: the current seven-gate checklist and first blocker.",
        "- `external-adoption-evidence.json`: starter record for independent adoption evidence.",
        "- `security-review-evidence.json`: starter record for final security-review evidence.",
        "",
        "## Rules",
        "",
        "- Do not use unchanged starter-kit JSON as stable-v4 proof.",
        "- Redact private app names, private paths, screenshots, account data, and token-like strings before sharing.",
        "- Stable v4 is only claimable when `shipguard v4 stable-publication` returns `pass`.",
        "",
        "## Next Command",
        "",
        "```bash",
        str(starter_kit.get("nextCommandTemplate") or ""),
        "```",
        "",
    ]
    (kit_dir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")


def write_stable_publication_release_notes_authoring_kit(
    out_dir: Path,
    *,
    report: dict[str, Any],
) -> None:
    kit = report.get("stablePublicationReleaseNotesAuthoringKit")
    if not isinstance(kit, dict):
        return
    kit_dir = out_dir / RELEASE_NOTES_KIT_DIRNAME
    kit_dir.mkdir(parents=True, exist_ok=True)

    release_notes_proof = report.get("releaseNotesProof") if isinstance(report.get("releaseNotesProof"), dict) else {}
    topic_matrix = kit.get("topicMatrix") if isinstance(kit.get("topicMatrix"), list) else []
    missing_topic_ids = kit.get("missingTopicIds") if isinstance(kit.get("missingTopicIds"), list) else []
    checklist = {
        "schemaVersion": 1,
        "draftOnly": True,
        "status": kit.get("status"),
        "releaseVersion": kit.get("releaseVersion"),
        "missingTopicIds": missing_topic_ids,
        "topicMatrix": topic_matrix,
        "requiredLanguage": release_notes_proof.get("requiredLanguage"),
        "nextCommandTemplate": kit.get("nextCommandTemplate"),
    }
    (kit_dir / "release-notes-checklist.json").write_text(
        json.dumps(checklist, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    release_version = str(kit.get("releaseVersion") or report.get("releaseVersion") or "<version>")
    draft_lines = [
        f"# ShipGuard {release_version}",
        "",
        "ShipGuard stable v4 publication is ready only when the stable-publication proof packet passes.",
        "",
        "## Stable Publication Proof",
        "",
        "- Stable-v4 claim: this release is a stable-v4 publication candidate until `shipguard v4 stable-publication` returns `pass` against the public GitHub release.",
        "- Publication proof boundary: stable status depends on release proof, not intent, local fixtures, or unpublished assets.",
        "- Downloaded release assets: verify the published tarball, release manifest, release index, proof ledger, replay report, attestation, and attestation badge from the GitHub release assets.",
        "- Post-release consumer proof: run `shipguard release-consume verify` against the downloaded release assets and keep the consumer report with the publication packet.",
        "- Independent adoption evidence: attach real independent public or private-redacted external adoption evidence; GitHub downloads do not count as adoption.",
        "- Final security review evidence: attach final security-review evidence covering CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy.",
        "- Non-claims: this release note does not claim OpenAI marketplace acceptance, private app validation, or external adoption beyond the attached evidence.",
        "",
        "## Proof Commands",
        "",
        "```bash",
        str(kit.get("nextCommandTemplate") or ""),
        "```",
        "",
    ]
    if missing_topic_ids:
        draft_lines.extend(
            [
                "## Current Missing Topics",
                "",
                ", ".join(str(item) for item in missing_topic_ids),
                "",
            ]
        )
    (kit_dir / "draft-release-notes.md").write_text("\n".join(draft_lines), encoding="utf-8")

    readme_lines = [
        "# Stable Publication Release Notes Kit",
        "",
        "This directory is a draft-only authoring aid for the public GitHub release body.",
        "It does not publish the release and does not prove stable v4 by itself.",
        "",
        "## Files",
        "",
        "- `release-notes-checklist.json`: machine-readable topic matrix and missing topic list.",
        "- `draft-release-notes.md`: copy-ready draft section that includes every required stable-publication topic.",
        "",
        "## Rules",
        "",
        "- Replace placeholders with real public release facts before publishing.",
        "- Keep private app names, paths, screenshots, accounts, and token-like strings out of public notes.",
        "- Re-run `shipguard v4 stable-publication` against the public GitHub release after editing the release notes.",
        "",
        "## Next Command",
        "",
        "```bash",
        str(kit.get("nextCommandTemplate") or ""),
        "```",
        "",
    ]
    (kit_dir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")


def write_stable_publication_launch_relay_drafts(
    out_dir: Path,
    *,
    report: dict[str, Any],
) -> None:
    relay = report.get("stablePublicationLaunchRelayDrafts")
    if not isinstance(relay, dict):
        return
    relay_dir = out_dir / LAUNCH_RELAY_DIRNAME
    relay_dir.mkdir(parents=True, exist_ok=True)

    status = str(relay.get("status") or "blocked-until-stable-publication-pass")
    release_version = str(relay.get("releaseVersion") or report.get("releaseVersion") or "<version>")
    posting_policy = relay.get("postingPolicy") if isinstance(relay.get("postingPolicy"), dict) else {}
    approval_text = str(posting_policy.get("approvalText") or "Explicit human approval is required before posting.")
    checklist = {
        "schemaVersion": 1,
        "draftOnly": True,
        "releaseVersion": release_version,
        "status": status,
        "stableV4Release": bool(relay.get("stableV4Release")),
        "approvalRequired": True,
        "publicPostingAllowed": False,
        "postingPolicy": posting_policy,
        "channels": relay.get("channels") or [],
        "requiredBeforePosting": relay.get("requiredBeforePosting") or [],
        "nonClaims": relay.get("nonClaims") or [],
        "nextCommandTemplate": relay.get("nextCommandTemplate"),
    }
    (relay_dir / "launch-relay-checklist.json").write_text(
        json.dumps(checklist, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    guard_lines = [
        f"Release: {release_version}",
        f"Launch-relay status: {status}",
        "",
        "Approval boundary: draft only. Do not publish, submit, post, schedule, or perform account-visible external actions without explicit human approval for this exact launch run.",
        f"Approval text: {approval_text}",
        "",
        "Evidence boundary: only claim facts backed by the stable-publication report, release notes, downloaded release assets, independent adoption evidence, and final security-review evidence.",
    ]
    common_intro = "\n".join(guard_lines)

    readme_lines = [
        "# Stable Publication Launch Relay",
        "",
        "This directory contains draft-only launch copy for verified major ShipGuard milestones.",
        "It is a relay packet, not a posting tool.",
        "",
        "## Guardrails",
        "",
        "- Public posting, publishing, submission, scheduling, or account-visible external actions require explicit human approval for the exact launch run.",
        "- Computer-use may help stage drafts only after that explicit approval; it must not post by default.",
        "- Keep private app names, local paths, screenshots, account data, tokens, adoption claims, and security claims out of public copy unless they are covered by the stable-publication evidence packet.",
        "- If the stable-publication report is not `pass`, treat every draft below as blocked context only.",
        "",
        "## Files",
        "",
        "- `launch-relay-checklist.json`: machine-readable approval boundary and channel list.",
        "- `product-hunt-draft.md`: draft Product Hunt copy.",
        "- `reddit-r-shipguard-draft.md`: draft r/ShipGuard post.",
        "- `x-thread-draft.md`: draft X thread.",
        "- `hacker-news-draft.md`: draft Hacker News submission notes.",
        "",
        "## Next Command",
        "",
        "```bash",
        str(relay.get("nextCommandTemplate") or ""),
        "```",
        "",
    ]
    (relay_dir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")

    drafts = {
        "product-hunt-draft.md": [
            "# Product Hunt Draft",
            "",
            common_intro,
            "",
            "## Tagline",
            "",
            "Local-first proof reports for AI-assisted development.",
            "",
            "## Launch Copy",
            "",
            "ShipGuard helps developers use coding agents without accepting vague `done` or `tested` claims. It scopes a task, checks evidence, rejects unsupported claims, and returns a reviewable verdict with the next exact action.",
            "",
            "## Proof To Mention",
            "",
            "- Stable-publication report status",
            "- Downloaded release asset verification",
            "- Post-release consumer proof",
            "- Independent adoption and final security review evidence, if attached",
            "",
            "## Do Not Claim",
            "",
            "- OpenAI marketplace acceptance",
            "- Private app validation",
            "- External adoption beyond attached evidence",
            "- Performance, security, or install numbers not in the proof packet",
            "",
        ],
        "reddit-r-shipguard-draft.md": [
            "# r/ShipGuard Draft",
            "",
            common_intro,
            "",
            "I am preparing a ShipGuard milestone announcement. ShipGuard is an open-source, local-first proof layer for AI-assisted development: prepare the task, verify the diff/evidence/claims, and keep the next action reviewable.",
            "",
            "The release should only be posted after the stable-publication report passes and the exact launch run is approved.",
            "",
            "Useful proof to attach: release notes, release proof, consumer verification, adoption evidence, security review evidence, and the stable-publication report.",
            "",
        ],
        "x-thread-draft.md": [
            "# X Thread Draft",
            "",
            common_intro,
            "",
            "1. ShipGuard is a local-first proof layer for AI-assisted development.",
            "",
            "2. The core loop is simple: prepare the task, collect proof, verify the diff and claims, then return pass/review/blocked with one next action.",
            "",
            "3. The milestone should be announced only after stable-publication proof passes: release metadata, release notes, downloaded assets, consumer proof, independent adoption, and security review.",
            "",
            "4. Draft only until explicit approval for this exact launch run.",
            "",
        ],
        "hacker-news-draft.md": [
            "# Hacker News Draft",
            "",
            common_intro,
            "",
            "## Title Draft",
            "",
            "Show HN: ShipGuard, local-first proof reports for AI-assisted coding agents",
            "",
            "## Comment Draft",
            "",
            "ShipGuard is an open-source CLI/plugin workflow that turns AI coding work into scoped task contracts and evidence-backed verification reports. It is local-first and focuses on whether a maintainer can review the change honestly: what changed, what proof exists, which claims are unsupported, and what the next action is.",
            "",
            "Post only after the stable-publication proof packet passes and the exact HN submission is approved.",
            "",
        ],
    }
    for name, lines in drafts.items():
        (relay_dir / name).write_text("\n".join(lines), encoding="utf-8")


def redact_report(report: dict[str, Any], args: argparse.Namespace, root: Path) -> dict[str, Any]:
    home = Path.home().resolve()
    replacements = {
        root.as_posix(): "<repo>",
        home.as_posix(): "<home>",
    }
    for raw in [
        args.out,
        args.release_assets,
        args.release_consume_out,
        args.download_release_assets_dir,
        args.release_candidate_report,
        *(args.external_adoption_evidence or []),
        *(args.security_review_evidence or []),
    ]:
        if raw:
            resolved = Path(raw).expanduser().resolve()
            replacements[resolved.as_posix()] = f"<{Path(str(raw)).name or 'path'}>"
            if resolved.parent != resolved:
                replacements[resolved.parent.as_posix()] = "<stable-publication-work>"
    if args.github_api_url.startswith("file://"):
        replacements[args.github_api_url] = "<github-api-url>"
    scrubbed = launchkey.scrub_value(report, replacements)

    def scrub_runtime_paths(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: scrub_runtime_paths(child) for key, child in value.items()}
        if isinstance(value, list):
            return [scrub_runtime_paths(child) for child in value]
        if isinstance(value, str):
            text = re.sub(r"file:///(?:private/)?var/folders/[^\"'\s]+?/T/tmp\.[A-Za-z0-9._-]+", "file://<stable-publication-work>", value)
            text = re.sub(r"/(?:private/)?var/folders/[^\"'\s]+?/T/tmp\.[A-Za-z0-9._-]+", "<stable-publication-work>", text)
            text = re.sub(r"/private/tmp/[^\"'\s]+", "<stable-publication-work>", text)
            return text
        return value

    return scrub_runtime_paths(scrubbed)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    args = normalize_args(args, root)
    version = read_text(root / "VERSION").strip() or "unknown"
    release_version = args.release_version or version
    out_dir = Path(args.out).expanduser().resolve()
    consumer_args = argparse.Namespace(**vars(args))
    if consumer_args.release_version:
        consumer_args.release_version = normalize_version(consumer_args.release_version)

    metadata_proof = build_github_release_metadata_proof(args, version)
    release_notes_proof = build_release_notes_proof(metadata_proof)
    release_candidate_packet_proof = build_release_candidate_packet_proof(args)
    github_download_proof = launchkey.build_github_release_asset_download_proof(args, version)
    published_asset_proof = launchkey.build_published_release_asset_proof(consumer_args, root, version, github_download_proof)
    post_release_consumer_proof = build_post_release_consumer_proof(published_asset_proof)
    adoption_proof = launchkey.build_external_adoption_evidence_proof(args)
    security_proof = launchkey.build_security_review_evidence_proof(args)
    adoption_gate_proof = {
        **adoption_proof,
        "status": adoption_proof.get("stableV4GateStatus") or adoption_proof.get("status"),
    }
    security_gate_proof = {
        **security_proof,
        "status": security_proof.get("stableV4GateStatus") or security_proof.get("status"),
    }

    gates = [
        ("githubReleaseMetadataProof", metadata_proof, stable_publication_command(args, placeholders=True)),
        ("releaseNotesProof", release_notes_proof, stable_publication_command(args, placeholders=True)),
        ("releaseCandidatePacketProof", release_candidate_packet_proof, release_candidate_packet_proof.get("nextCommand", "")),
        ("publishedReleaseAssetProof", published_asset_proof, published_asset_proof.get("nextCommand", "")),
        ("postReleaseConsumerProof", post_release_consumer_proof, published_asset_proof.get("consumeCommand", "")),
        ("externalAdoptionEvidenceStableGate", adoption_gate_proof, adoption_proof.get("nextCommand", "")),
        ("securityReviewEvidenceStableGate", security_gate_proof, security_proof.get("nextCommand", "")),
    ]
    blocked = first_blocking_gate(gates)
    status = "pass" if blocked is None else "review"
    stable_v4_release = status == "pass"
    evidence_templates = build_stable_publication_evidence_templates(root)
    evidence_starter_kit = build_stable_publication_evidence_starter_kit_manifest()
    release_notes_authoring_kit = build_stable_publication_release_notes_authoring_kit(
        release_version=release_version,
        release_notes_proof=release_notes_proof,
    )
    evidence_packet = build_stable_publication_evidence_packet(
        gates=gates,
        blocked=blocked,
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_templates=evidence_templates,
    )
    launch_relay_drafts = build_stable_publication_launch_relay_drafts(
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_packet=evidence_packet,
    )

    if blocked:
        receipt, proof, next_command = blocked
        summary = str(proof.get("summary") or f"{receipt} has not passed.")
        priority_action = f"Complete `{receipt}` before claiming stable-v4 publication."
        proof_source = receipt
    else:
        next_command = "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet"
        summary = "Stable-v4 publication proof passed every local stable-publication gate."
        priority_action = "Use the stable-publication report as release proof input, then move the next ShipGuard roadmap goal forward."
        proof_source = "release metadata, release notes, LaunchKey report, release-consume, adoption evidence, and security evidence"

    result_ux = build_result_ux(
        status=status,
        summary=summary,
        proof_source=proof_source,
        why_it_matters="Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.",
        next_command=next_command or stable_publication_command(args, placeholders=True),
        next_action_summary=priority_action,
    )
    result_ux["priorityAction"] = priority_action

    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "tool": TOOL,
        "surface": SURFACE,
        "status": status,
        "version": version,
        "releaseVersion": release_version,
        "repo": root.as_posix(),
        "githubReleaseRepoInference": getattr(args, "githubReleaseRepoInference", {}),
        "productStage": "v4-stable-publication-proof",
        "stableV4Release": stable_v4_release,
        "stablePublicationEvidencePacket": evidence_packet,
        "stablePublicationEvidenceTemplates": evidence_templates,
        "stablePublicationEvidenceStarterKit": evidence_starter_kit,
        "stablePublicationReleaseNotesAuthoringKit": release_notes_authoring_kit,
        "stablePublicationLaunchRelayDrafts": launch_relay_drafts,
        "githubReleaseMetadataProof": metadata_proof,
        "releaseNotesProof": release_notes_proof,
        "releaseCandidatePacketProof": release_candidate_packet_proof,
        "githubReleaseAssetDownloadProof": github_download_proof,
        "publishedReleaseAssetProof": published_asset_proof,
        "postReleaseConsumerProof": post_release_consumer_proof,
        "externalAdoptionEvidenceProof": adoption_proof,
        "securityReviewEvidenceProof": security_proof,
        "stablePublicationGates": [
            {"receipt": receipt, "status": proof.get("status"), "nextCommand": command}
            for receipt, proof, command in gates
        ],
        "blockedClaims": [
            "Do not claim stable v4 until this report status is pass.",
            "Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.",
            "Do not treat GitHub release download counts as independent adoption evidence.",
            "Do not include private app paths, screenshots, identifiers, or token-like text in shareable proof.",
            "Do not publish, submit, post, schedule, or perform account-visible external launch actions without explicit human approval for that exact launch run.",
        ],
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "privateAppsUsed": False,
            "doesNotEditTargetApps": True,
            "doesNotPublishRelease": True,
            "doesNotPostExternally": True,
            "shareable": bool(args.shareable),
        },
        "reportQualityQuestions": [
            "Can ShipGuard prove stable-v4 publication from real release metadata, release notes, downloaded assets, external adoption evidence, security evidence, and post-release consumer proof?",
            "Does the stable-publication report block every stable-v4 claim until independent adoption and final security evidence are attached?",
            "Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?",
            "Does the stable-publication report provide draft-only evidence templates for independent adoption and final security review without manufacturing proof?",
            "Does the stable-publication report write a draft-only evidence starter kit so maintainers can collect the packet without reverse-engineering JSON shapes?",
            "Does the stable-publication report prepare guarded launch relay drafts without posting, submitting, or bypassing explicit human approval?",
        ],
        "resultUX": result_ux,
    }
    if args.shipguard_eval:
        report["shipguardEval"] = {
            "mode": "ShipGuard product QA",
            "allowedInput": "ShipGuard source tree, public release metadata, downloaded release assets, and redacted evidence records",
            "forbiddenOutput": "Private target-app edits, fake adoption, synthetic stable-v4 evidence claims, or OpenAI marketplace acceptance claims",
            "nextImprovement": priority_action,
        }
    if args.shareable:
        report = redact_report(report, args, root)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard V4 Stable Publication Proof",
        "",
    ]
    lines.extend(render_result_markdown(report.get("resultUX", {})))
    lines.extend(
        [
            "",
            "## Stable Publication Gates",
            "",
            "| Gate | Status |",
            "| --- | --- |",
        ]
    )
    for item in report.get("stablePublicationGates", []):
        lines.append(f"| `{item.get('receipt')}` | `{item.get('status')}` |")
    packet = report.get("stablePublicationEvidencePacket") if isinstance(report.get("stablePublicationEvidencePacket"), dict) else {}
    if packet:
        lines.extend(
            [
                "",
                "## Evidence Packet",
                "",
                f"- Packet status: `{packet.get('status')}`",
                f"- Required evidence passed: `{packet.get('passedEvidenceCount')}/{packet.get('requiredEvidenceCount')}`",
                f"- First blocking gate: `{(packet.get('firstBlockingGate') or {}).get('receipt') or 'none'}`",
                "",
                "| Evidence | Status |",
                "| --- | --- |",
            ]
        )
        for item in packet.get("requiredEvidence", []):
            if isinstance(item, dict):
                lines.append(f"| `{item.get('id')}` | `{item.get('status')}` |")
    release_notes = report.get("releaseNotesProof") if isinstance(report.get("releaseNotesProof"), dict) else {}
    topic_matrix = release_notes.get("topicMatrix") if isinstance(release_notes.get("topicMatrix"), list) else []
    if topic_matrix:
        lines.extend(
            [
                "",
                "## Release Notes Proof",
                "",
                f"- Notes digest: `{release_notes.get('releaseNotesSha256') or 'not-available'}`",
                f"- Missing topics: `{', '.join(release_notes.get('missingTopicIds') or []) or 'none'}`",
                "",
                "| Topic | Status | Matched terms |",
                "| --- | --- | --- |",
            ]
        )
        for item in topic_matrix:
            if isinstance(item, dict):
                terms = ", ".join(str(term) for term in item.get("matchedTerms", [])) or "none"
                lines.append(f"| `{item.get('id')}` | `{item.get('status')}` | {terms} |")
    release_notes_kit = report.get("stablePublicationReleaseNotesAuthoringKit") if isinstance(report.get("stablePublicationReleaseNotesAuthoringKit"), dict) else {}
    if release_notes_kit:
        lines.extend(
            [
                "",
                "## Release Notes Authoring Kit",
                "",
                f"- Directory: `{release_notes_kit.get('directory')}`",
                f"- Draft-only: `{release_notes_kit.get('draftOnly')}`",
                f"- Missing topics: `{', '.join(release_notes_kit.get('missingTopicIds') or []) or 'none'}`",
                "",
                "| File | Purpose |",
                "| --- | --- |",
            ]
        )
        for item in release_notes_kit.get("files", []):
            if isinstance(item, dict):
                lines.append(f"| `{item.get('path')}` | {item.get('purpose')} |")
        lines.extend(["", "Next command template:", "", "```bash", str(release_notes_kit.get("nextCommandTemplate") or ""), "```"])
    templates = report.get("stablePublicationEvidenceTemplates") if isinstance(report.get("stablePublicationEvidenceTemplates"), dict) else {}
    if templates:
        lines.extend(
            [
                "",
                "## Evidence Templates",
                "",
                f"- Draft-only templates: `{templates.get('draftOnly')}`",
                "",
                "| Template | Exists | Copy command |",
                "| --- | --- | --- |",
            ]
        )
        for item in templates.get("templates", []):
            if isinstance(item, dict):
                lines.append(
                    f"| `{item.get('id')}` | `{item.get('exists')}` | `{item.get('copyCommand')}` |"
                )
    starter_kit = report.get("stablePublicationEvidenceStarterKit") if isinstance(report.get("stablePublicationEvidenceStarterKit"), dict) else {}
    if starter_kit:
        lines.extend(
            [
                "",
                "## Evidence Starter Kit",
                "",
                f"- Directory: `{starter_kit.get('directory')}`",
                f"- Draft-only: `{starter_kit.get('draftOnly')}`",
                "",
                "| File | Purpose |",
                "| --- | --- |",
            ]
        )
        for item in starter_kit.get("files", []):
            if isinstance(item, dict):
                lines.append(f"| `{item.get('path')}` | {item.get('purpose')} |")
        lines.extend(["", "Next command template:", "", "```bash", str(starter_kit.get("nextCommandTemplate") or ""), "```"])
    launch_relay = report.get("stablePublicationLaunchRelayDrafts") if isinstance(report.get("stablePublicationLaunchRelayDrafts"), dict) else {}
    if launch_relay:
        posting_policy = launch_relay.get("postingPolicy") if isinstance(launch_relay.get("postingPolicy"), dict) else {}
        lines.extend(
            [
                "",
                "## Launch Relay Drafts",
                "",
                f"- Directory: `{launch_relay.get('directory')}`",
                f"- Draft-only: `{launch_relay.get('draftOnly')}`",
                f"- Approval required: `{launch_relay.get('approvalRequired')}`",
                f"- Public posting allowed: `{launch_relay.get('publicPostingAllowed')}`",
                f"- Computer-use may post: `{posting_policy.get('computerUseMayPost')}`",
                f"- Status: `{launch_relay.get('status')}`",
                "",
                "| File | Purpose |",
                "| --- | --- |",
            ]
        )
        for item in launch_relay.get("files", []):
            if isinstance(item, dict):
                lines.append(f"| `{item.get('path')}` | {item.get('purpose')} |")
        lines.extend(
            [
                "",
                "Approval boundary:",
                "",
                str(posting_policy.get("approvalText") or "Explicit human approval is required before posting."),
            ]
        )
    lines.extend(
        [
            "",
            "## Proof Summary",
            "",
            f"- GitHub release metadata: `{report.get('githubReleaseMetadataProof', {}).get('status')}`",
            f"- Release notes: `{report.get('releaseNotesProof', {}).get('status')}`",
            f"- LaunchKey package packet: `{report.get('releaseCandidatePacketProof', {}).get('status')}`",
            f"- Release assets: `{report.get('publishedReleaseAssetProof', {}).get('status')}`",
            f"- Post-release consumer proof: `{report.get('postReleaseConsumerProof', {}).get('status')}`",
            f"- External adoption stable gate: `{report.get('externalAdoptionEvidenceProof', {}).get('stableV4GateStatus')}`",
            f"- Security review stable gate: `{report.get('securityReviewEvidenceProof', {}).get('stableV4GateStatus')}`",
            f"- Stable v4 release claim allowed: `{report.get('stableV4Release')}`",
            "",
            "## Blocked Claims",
            "",
        ]
    )
    for claim in report.get("blockedClaims", []):
        lines.append(f"- {claim}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report.get("reportQualityQuestions", []):
        lines.append(f"- {question}")
    lines.extend(["", "## Scope Boundary", ""])
    for key, value in sorted((report.get("scopeBoundary") or {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ShipGuard v4 stable-publication proof reports.")
    parser.add_argument("--path", default=".", help="ShipGuard repository path. Defaults to current directory.")
    parser.add_argument("--out", required=True, help="Output directory for v4-stable-publication reports.")
    parser.add_argument("--github-release-repo", help="GitHub repository in owner/repo form.")
    parser.add_argument("--release-version", help="Release version/tag to verify. Defaults to VERSION.")
    parser.add_argument("--release-candidate-report", help="LaunchKey v4-release-candidate JSON file or output directory.")
    parser.add_argument("--release-assets", help="Optional downloaded release assets directory to verify with release-consume.")
    parser.add_argument("--release-consume-out", help="Output directory for embedded release-consume proof. Defaults under --out.")
    parser.add_argument("--download-release-assets", action="store_true", help="Download GitHub release assets before running release-consume.")
    parser.add_argument("--download-release-assets-dir", help="Optional destination for downloaded GitHub release assets. Defaults under --out.")
    parser.add_argument("--github-api-url", default="https://api.github.com", help="GitHub API base URL. Defaults to https://api.github.com.")
    parser.add_argument("--github-token-env", default="GITHUB_TOKEN", help="Environment variable containing an optional GitHub API token.")
    parser.add_argument("--external-adoption-evidence", action="append", help="External adoption evidence JSON file or directory. May be passed multiple times.")
    parser.add_argument("--security-review-evidence", action="append", help="Final security review evidence JSON file or directory. May be passed multiple times.")
    parser.add_argument("--shipguard-eval", action="store_true", help="Include ShipGuard-only product QA boundaries.")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths for shareable output.")
    parser.add_argument("--json", action="store_true", help="Write only JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Write only Markdown output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    write_json = args.json or not args.markdown
    write_markdown = args.markdown or not args.json
    if write_json:
        (out_dir / "v4-stable-publication.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_markdown:
        (out_dir / "v4-stable-publication.md").write_text(render_markdown(report), encoding="utf-8")
    write_stable_publication_evidence_starter_kit(out_dir, report=report, root=Path(args.path).expanduser().resolve())
    write_stable_publication_release_notes_authoring_kit(out_dir, report=report)
    write_stable_publication_launch_relay_drafts(out_dir, report=report)
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
