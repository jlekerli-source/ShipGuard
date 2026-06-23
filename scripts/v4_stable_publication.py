#!/usr/bin/env python3
"""Generate the ShipGuard v4 stable-publication proof report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import shlex
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
STARTER_KIT_DIRNAME = "stable-publication-evidence-kit"
RELEASE_NOTES_KIT_DIRNAME = "stable-publication-release-notes"
LAUNCH_RELAY_DIRNAME = "stable-publication-launch-relay"
STABLE_PUBLICATION_TEMPLATE_SPECS = [
    {
        "id": "independent-adoption-evidence",
        "title": "Independent adoption evidence",
        "path": f"{STABLE_PUBLICATION_TEMPLATE_DIR}/external-adoption-evidence.template.json",
        "starterPath": f"{STARTER_KIT_DIRNAME}/external-adoption-evidence.json",
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
        "redactionBoundary": {
            "privateDataRedactedMustBeTrue": True,
            "forbiddenContent": [
                "private app source",
                "private app identifiers",
                "local absolute paths",
                "screenshots with private data",
                "tokens or account identifiers",
            ],
        },
        "privacyBoundary": {
            "consentToShareOrSummaryOnlyRequired": True,
            "privateAppDetailsForbiddenInShareableProof": True,
            "githubDownloadsDoNotCountAsAdoption": True,
            "maintainerOnlyRunsDoNotCountAsIndependentAdoption": True,
        },
        "passCriteria": [
            "At least one JSON record has status=pass.",
            "evidenceType is shipguard-external-adoption.",
            "evidenceClass is public-external or private-redacted-external.",
            "actorRelationship is independent.",
            "privateDataRedacted is true.",
            "commands, artifacts, outcome, and nonClaims are present.",
            "fixtureSynthetic is not true.",
            "The record is public-shareable or summary-shareable with consent/privacy reviewed.",
        ],
        "failCriteria": [
            "The unchanged template or generated starter file is submitted as evidence.",
            "status is not pass.",
            "privateDataRedacted is not true.",
            "actorRelationship is not independent.",
            "fixtureSynthetic is true.",
            "Evidence relies only on GitHub downloads or maintainer-only runs.",
            "The record contains local paths, private app identifiers, screenshots with private data, tokens, or account data.",
        ],
    },
    {
        "id": "final-security-review-evidence",
        "title": "Final security review evidence",
        "path": f"{STABLE_PUBLICATION_TEMPLATE_DIR}/security-review-evidence.template.json",
        "starterPath": f"{STARTER_KIT_DIRNAME}/security-review-evidence.json",
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
        "requiredScope": [
            "cli",
            "plugin",
            "github-actions",
            "release-proof",
            "package-install",
            "redaction-privacy",
        ],
        "redactionBoundary": {
            "privateDataRedactedMustBeTrue": True,
            "forbiddenContent": [
                "private app source",
                "private app identifiers",
                "local absolute paths",
                "screenshots with private data",
                "tokens or account identifiers",
            ],
        },
        "privacyBoundary": {
            "privateAppReviewRequiresSeparateAuthorization": True,
            "privateAppDetailsForbiddenInShareableProof": True,
            "zeroRiskClaimsForbidden": True,
            "criticalAndHighFindingsMustBeExplicit": True,
        },
        "passCriteria": [
            "At least one JSON record has status=pass.",
            "evidenceType is shipguard-security-review.",
            "evidenceClass is public-security-review or private-redacted-security-review.",
            "privateDataRedacted is true.",
            "scope covers cli, plugin, github-actions, release-proof, package-install, and redaction-privacy.",
            "methodology, commands, artifacts, findingsSummary, and nonClaims are present.",
            "findingsSummary.criticalOpen is 0 and findingsSummary.highOpen is 0.",
            "fixtureSynthetic is not true.",
        ],
        "failCriteria": [
            "The unchanged template or generated starter file is submitted as evidence.",
            "status is not pass.",
            "privateDataRedacted is not true.",
            "required security scope is missing.",
            "findingsSummary.criticalOpen or findingsSummary.highOpen is not 0.",
            "fixtureSynthetic is true.",
            "The record claims zero risk instead of reporting scope, findings, and residual risk.",
            "The record contains local paths, private app identifiers, screenshots with private data, tokens, or account data.",
        ],
    },
]

LAUNCHKEY_REQUIRED_PROOF_AREAS = [
    {
        "id": "fresh-install-package-proof",
        "receipt": "freshInstallPackageProof",
        "title": "Fresh package install",
        "requiredForCandidateClosure": True,
        "stablePublicationGate": "launchkey-candidate-packet",
        "requirement": "A release tarball installs into a clean prefix, reports the expected version through both CLI aliases, runs validation, and leaves no generated/cache/VCS/package sidecar files in the installed tree.",
    },
    {
        "id": "same-prefix-upgrade-proof",
        "receipt": "upgradePackageProof",
        "title": "Same-prefix upgrade",
        "requiredForCandidateClosure": True,
        "stablePublicationGate": "launchkey-candidate-packet",
        "requirement": "A previous release package installs first, the candidate package upgrades the same prefix, both aliases report the candidate version, validation passes, and the upgraded tree is clean.",
    },
    {
        "id": "rollback-cleanup-proof",
        "receipt": "rollbackPackageProof",
        "title": "Rollback cleanup",
        "requiredForCandidateClosure": True,
        "stablePublicationGate": "launchkey-candidate-packet",
        "requirement": "A temporary candidate install can be removed without leaving ShipGuard package state behind.",
    },
    {
        "id": "github-release-asset-download-proof",
        "receipt": "githubReleaseAssetDownloadProof",
        "title": "GitHub release asset download",
        "requiredForCandidateClosure": False,
        "stablePublicationGate": "downloaded-release-assets",
        "requirement": "LaunchKey may download public GitHub release assets for candidate readiness, but stable-publication verifies downloaded or supplied release assets again.",
    },
    {
        "id": "post-release-consumer-proof",
        "receipt": "publishedReleaseAssetProof",
        "title": "Release-consume proof",
        "requiredForCandidateClosure": False,
        "stablePublicationGate": "post-release-consumer-proof",
        "requirement": "Downloaded or supplied release assets can be consumed by release-consume verification; stable-publication still owns the final consumer gate.",
    },
    {
        "id": "external-adoption-evidence-proof",
        "receipt": "externalAdoptionEvidenceStableGate",
        "title": "Independent adoption evidence",
        "requiredForCandidateClosure": False,
        "stablePublicationGate": "independent-adoption-evidence",
        "requirement": "LaunchKey can validate adoption-evidence structure, but real independent adoption for stable v4 is proven by the stable-publication adoption gate.",
    },
    {
        "id": "security-review-evidence-proof",
        "receipt": "securityReviewEvidenceStableGate",
        "title": "Final security review evidence",
        "requiredForCandidateClosure": False,
        "stablePublicationGate": "final-security-review-evidence",
        "requirement": "LaunchKey can validate security-evidence structure and scope, but final stable-v4 security proof is proven by the stable-publication security gate.",
    },
]

LAUNCHKEY_CANDIDATE_REPAIR_CRITERIA = [
    "Use the supplied candidate report path to inspect the LaunchKey JSON, but fix the failing LaunchKey input or package lineage instead of editing the stable-publication report.",
    "If package hygiene diagnostics are present, rebuild the affected tarball without AppleDouble, cache, VCS, bytecode, or unsafe archive members, then rerun `shipguard release-package hygiene`.",
    "Rerun `shipguard v4 release-candidate` with the rebuilt candidate package, previous release package for same-prefix upgrade proof, rollback proof, release assets when needed, and redacted evidence inputs.",
    "After the LaunchKey candidate report passes, rerun `shipguard v4 stable-publication` with the same publication inputs so later release notes, release assets, adoption, and security gates remain visible.",
]

LAUNCHKEY_CANDIDATE_PASS_CRITERIA = [
    "The supplied report is from `shipguard v4 release-candidate`.",
    "The supplied report status is `pass`.",
    "releaseReadiness.releaseClaim is `candidate-ready`.",
    "releaseReadiness.stableV4Release is `false`.",
    "freshInstallPackageProof, upgradePackageProof, and rollbackPackageProof all pass.",
    "No nested blockingProof remains.",
    "No package-hygiene blocker remains for the candidate or previous release tarball.",
]

LAUNCHKEY_CANDIDATE_FAIL_CRITERIA = [
    "The LaunchKey report is missing, unreadable, or from the wrong tool.",
    "The LaunchKey report status is not `pass`.",
    "The LaunchKey report claims stable v4 instead of candidate readiness.",
    "Fresh install, same-prefix upgrade, or rollback cleanup proof is missing or not passing.",
    "A nested blocking receipt still points at package, release-asset, adoption, security, or consumer proof failure.",
    "Package hygiene diagnostics report unsafe archive members such as AppleDouble sidecars, `.DS_Store`, `__MACOSX`, bytecode, cache, VCS data, unsafe links/devices, or path traversal.",
    "Fixture candidate proof is used as stable-v4 publication proof.",
]

GITHUB_RELEASE_METADATA_REPAIR_CRITERIA = [
    "Pass `--github-release-repo <owner/repo>` explicitly when the origin remote is missing, private, mirrored, or not the publication repository.",
    "Confirm `--release-version <version>` resolves to the exact public GitHub release tag ShipGuard should validate.",
    "If the release is missing, create it manually with the generated `gh release create` command after the release tarball and proof assets exist.",
    "Publish or update the GitHub release so it is not draft-only or prerelease-only and includes every required stable-publication asset.",
    "After repairing the repository, tag, release state, or asset list, rerun `shipguard v4 stable-publication` so release notes, downloaded assets, consumer proof, adoption, and security gates remain visible.",
]

GITHUB_RELEASE_METADATA_PASS_CRITERIA = [
    "The GitHub release repository is explicit or successfully inferred from `origin`.",
    "The release tag exists in the selected repository.",
    "The returned GitHub release tag name matches the requested release tag.",
    "The release is not draft-only and not prerelease-only.",
    "Every required stable-publication asset is present in GitHub release metadata.",
    "The release URL, target commitish, asset names, and release-note digest are recorded for downstream proof.",
]

GITHUB_RELEASE_METADATA_FAIL_CRITERIA = [
    "No GitHub release repository is supplied or inferred.",
    "`--github-release-repo` is not in `owner/repo` form.",
    "The selected API endpoint cannot load the requested release tag.",
    "The returned GitHub release tag name disagrees with the requested release tag.",
    "The release is draft or prerelease when stable-v4 publication proof is requested.",
    "GitHub metadata is missing one or more required release assets.",
    "A source checkout, local package build, fixture API, or generated report is treated as public release metadata proof.",
]

PUBLIC_RELEASE_FRESHNESS_REPAIR_CRITERIA = [
    "Publish the release from the exact commit recorded in `release-manifest.json`, then ensure the GitHub tag points at that same commit.",
    "If release assets were rebuilt, rebuild and re-upload the full release proof packet so `release-manifest.json`, the tarball, replay, attestation, and badge all describe the same commit and tag.",
    "If `target_commitish` is a branch name, make sure ShipGuard can resolve the public GitHub tag ref so the branch name is not treated as commit proof.",
    "Rerun `shipguard v4 stable-publication` with downloaded or supplied release assets after repairing the tag, release metadata, manifest, or uploaded assets.",
]

PUBLIC_RELEASE_FRESHNESS_PASS_CRITERIA = [
    "GitHub release metadata loads for the selected owner/repo and tag.",
    "The public GitHub tag target resolves to a commit SHA.",
    "`release-manifest.json` exists in the downloaded or supplied release assets.",
    "The release manifest version and tag match the requested release.",
    "The release manifest commit matches the public GitHub tag target.",
    "If GitHub release `target_commitish` is a SHA, it also matches the release manifest commit.",
    "The release manifest was generated no later than the public release publication timestamp.",
]

PUBLIC_RELEASE_FRESHNESS_FAIL_CRITERIA = [
    "The public GitHub tag target cannot be resolved.",
    "`release-manifest.json` is missing from the downloaded or supplied release assets.",
    "The release manifest tag, version, or commit disagrees with the public GitHub release metadata.",
    "The public GitHub tag points at a different commit than the release manifest.",
    "The release metadata `target_commitish` is a SHA and disagrees with the release manifest commit.",
    "The release manifest appears newer than the public release publication timestamp, which means the public metadata/assets may be stale or replaced.",
    "Source checkout state, fixture API responses, local package builds, or draft release notes are treated as freshness proof.",
]

RELEASE_VERSION_COHERENCE_REPAIR_CRITERIA = [
    "Use one release version across VERSION, `--release-version`, the public GitHub release tag, release-manifest.json, and release-consume verification.",
    "Rebuild and re-upload the release packet if the manifest or tarball belongs to a different version than the public GitHub release.",
    "Rerun `shipguard v4 stable-publication` after repairing the version, tag, manifest, package, or GitHub release metadata.",
]

RELEASE_VERSION_COHERENCE_PASS_CRITERIA = [
    "VERSION matches the requested release version.",
    "The public GitHub release tag and returned metadata tag name match the requested release.",
    "release-manifest.json version and tag match the requested release.",
    "release-consume verification reports the requested release version.",
    "The versioned tarball name matches the requested release version.",
]

RELEASE_VERSION_COHERENCE_FAIL_CRITERIA = [
    "VERSION disagrees with `--release-version`.",
    "GitHub release metadata returns a different tag name than the requested tag.",
    "release-manifest.json version or tag disagrees with the requested release.",
    "release-consume verifies a different package version.",
    "The release asset packet exposes a tarball for a different version.",
]

RELEASE_ASSET_COHERENCE_REPAIR_CRITERIA = [
    "Download or supply the exact public release asset packet for the requested tag.",
    "Make sure GitHub metadata, the downloaded/supplied directory, `release-manifest.json`, and `asset-digests.json` all list every required release asset.",
    "Rebuild and re-upload the release packet when the manifest tarball name or SHA-256 disagrees with the consumer digest matrix.",
    "Rerun `shipguard v4 stable-publication` after repairing the uploaded assets or supplied downloaded asset directory.",
]

RELEASE_ASSET_COHERENCE_PASS_CRITERIA = [
    "Every required GitHub release asset is present in metadata, local downloaded/supplied assets, and `asset-digests.json`.",
    "The expected versioned ShipGuard tarball is present in metadata, local assets, and digest rows.",
    "The release manifest artifact name and digest tarball row name match the expected versioned tarball.",
    "The release manifest artifact SHA-256, digest tarball SHA-256, and consumer artifact SHA-256 agree.",
]

RELEASE_ASSET_COHERENCE_FAIL_CRITERIA = [
    "The downloaded/supplied asset directory is missing required assets.",
    "`asset-digests.json` omits required assets or SHA-256 values for present assets.",
    "The release manifest artifact name or digest tarball row points at a different version.",
    "The manifest artifact SHA-256, digest tarball SHA-256, or consumer artifact SHA-256 disagrees.",
    "Source-only files, fixture assets, or metadata-only asset names are treated as proof.",
]

RELEASE_ASSET_REPAIR_CRITERIA = [
    "Use `shipguard v4 stable-publication --download-release-assets` to download the public GitHub release assets, or pass the already downloaded asset directory with `--release-assets`.",
    "Confirm the downloaded or supplied directory contains every required release asset listed by the GitHub release metadata, including the versioned ShipGuard tarball.",
    "Do not edit source files, fixture outputs, or generated report JSON to close this gate; repair the public release assets or the supplied downloaded asset directory.",
    "After the assets are present, rerun `shipguard v4 stable-publication` so the downloaded-release-assets gate and the downstream post-release consumer gate are evaluated together.",
]

RELEASE_ASSET_PASS_CRITERIA = [
    "GitHub release metadata for the requested tag exists and is not draft-only or prerelease-only.",
    "Every required stable-publication asset is present in the public GitHub release metadata.",
    "The assets are downloaded by stable-publication or supplied through `--release-assets` from the exact published release packet.",
    "The stable-publication report records `publishedReleaseAssetProof.status = pass`; source checkout files, local build output, and fixture assets do not count.",
]

RELEASE_ASSET_FAIL_CRITERIA = [
    "No downloaded or supplied release-assets directory is available.",
    "The release metadata is missing one or more required assets.",
    "The downloaded or supplied directory does not contain every required release asset.",
    "GitHub release asset download fails or points at a draft, prerelease, wrong tag, wrong repository, or wrong version.",
    "Source-only package tests, LaunchKey fixtures, generated report directories, or local package builds are treated as published release assets.",
]

POST_RELEASE_CONSUMER_REPAIR_CRITERIA = [
    "Download the published release assets with `shipguard v4 stable-publication --download-release-assets` or supply the exact downloaded asset directory with `--release-assets`.",
    "Run `shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>` and keep both `consumer-report.json` and `asset-digests.json` with the stable-publication packet.",
    "Repair missing or mismatched release assets, replay proof, attestation proof, badge proof, manifest, index, ledger, or tarball digest before rerunning stable-publication.",
    "After `release-consume verify` passes, rerun `shipguard v4 stable-publication` with the same release metadata, LaunchKey, adoption, and security inputs so later gates remain visible.",
]

POST_RELEASE_CONSUMER_PASS_CRITERIA = [
    "`shipguard release-consume verify` exits 0.",
    "`consumer-report.json` exists and reports `status = pass`.",
    "`asset-digests.json` exists and lists the downloaded release assets with SHA-256 and byte counts.",
    "Replay and attestation status are `pass` or explicitly verified as matching published assets.",
    "The stable-publication report records `postReleaseConsumerProof.status = pass` from the consumed release assets, not from source-only or fixture proof.",
]

POST_RELEASE_CONSUMER_FAIL_CRITERIA = [
    "No downloaded or supplied release-assets directory is available.",
    "`release-consume verify` times out, exits non-zero, or cannot run from the current checkout.",
    "`consumer-report.json` is missing, malformed, or reports a non-pass status.",
    "`asset-digests.json` is missing, incomplete, or shows missing required release assets.",
    "Replay, attestation, published crosscheck, version, or tarball SHA-256 proof is blocked or mismatched.",
    "Source checkout tests, package fixtures, or draft release notes are treated as post-release consumer proof.",
]


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


def requested_tarball_name(version: str) -> str:
    return f"shipguard-v{normalize_version(version)}.tar.gz"


def is_sha_like(value: object) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", str(value or "").strip()))


def sha_matches(left: object, right: object) -> bool:
    left_value = str(left or "").strip().lower()
    right_value = str(right or "").strip().lower()
    if not left_value or not right_value or not is_sha_like(left_value) or not is_sha_like(right_value):
        return False
    if len(left_value) == len(right_value):
        return left_value == right_value
    shorter, longer = sorted((left_value, right_value), key=len)
    return longer.startswith(shorter)


def parse_utc_datetime(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def git_rev_parse(root: Path, revision: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", root.as_posix(), "rev-parse", "--verify", revision],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


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


def refresh_generated_download_destination(args: argparse.Namespace, out_dir: Path) -> None:
    if not args.download_release_assets or args.download_release_assets_dir or args.release_assets:
        return
    download_dir = out_dir / "downloaded-release-assets"
    # ponytail: only this default path is ShipGuard-owned; custom asset dirs stay protected.
    if download_dir.is_dir():
        shutil.rmtree(download_dir)


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


def stable_publication_rerun_command(args: argparse.Namespace) -> str:
    command = [
        "./bin/shipguard",
        "v4",
        "stable-publication",
        "--path",
        ".",
        "--out",
        "/tmp/shipguard-v4-stable-publication",
        "--github-release-repo",
        args.github_release_repo or "<owner/repo>",
        "--release-version",
        args.release_version or "<version>",
        "--release-candidate-report",
        args.release_candidate_report or "<v4-release-candidate-json-or-dir>",
    ]
    if args.release_assets:
        command.extend(["--release-assets", args.release_assets])
    else:
        command.append("--download-release-assets")
    adoption_inputs = list(args.external_adoption_evidence or []) or ["<adoption-evidence-json-or-dir>"]
    for value in adoption_inputs:
        command.extend(["--external-adoption-evidence", value])
    security_inputs = list(args.security_review_evidence or []) or ["<security-review-json-or-dir>"]
    for value in security_inputs:
        command.extend(["--security-review-evidence", value])
    command.extend(["--shipguard-eval", "--shareable"])
    return " ".join(shlex.quote(str(part)) for part in command)


def public_release_notes_edit_command(*, repo: str, tag: str, notes_file: str | Path | None = None) -> str:
    repo = repo or "<owner/repo>"
    tag = tag or "<tag>"
    notes_path = str(notes_file or f"{RELEASE_NOTES_KIT_DIRNAME}/draft-release-notes.md")
    return " ".join(
        shlex.quote(str(part))
        for part in (
            "gh",
            "release",
            "edit",
            tag,
            "--repo",
            repo,
            "--notes-file",
            notes_path,
        )
    )


def resolve_release_candidate_report(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    if path.is_dir():
        return path / "v4-release-candidate.json"
    return path


def compact_package_hygiene_evidence(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    keys = [
        "status",
        "tool",
        "readOnly",
        "blockedFindingCount",
        "reviewFindingCount",
        "affectedVersions",
        "safeTarballs",
        "tarballsScanned",
        "firstFinding",
        "nextCommand",
    ]
    compact = {key: value[key] for key in keys if key in value}
    return compact or None


def extract_launchkey_blocking_proof(report: dict[str, Any]) -> dict[str, Any] | None:
    raw_blocker = report.get("blockingProof")
    result_ux = report.get("resultUX") if isinstance(report.get("resultUX"), dict) else {}
    if not isinstance(raw_blocker, dict):
        raw_blocker = result_ux.get("blockingProof")

    if isinstance(raw_blocker, dict):
        blocker = {
            key: raw_blocker[key]
            for key in (
                "receipt",
                "status",
                "summary",
                "failure",
                "failureEvidence",
                "nextAction",
                "nextCommand",
                "proofSource",
            )
            if key in raw_blocker
        }
        receipt = str(blocker.get("receipt") or "")
        receipt_proof = report.get(receipt) if receipt else None
        hygiene = compact_package_hygiene_evidence(
            receipt_proof.get("packageHygieneEvidence") if isinstance(receipt_proof, dict) else None
        )
        if hygiene:
            blocker["packageHygieneEvidence"] = hygiene
            if hygiene.get("nextCommand") and not blocker.get("nextCommand"):
                blocker["nextCommand"] = hygiene["nextCommand"]
            first_finding = hygiene.get("firstFinding") if isinstance(hygiene.get("firstFinding"), dict) else {}
            if first_finding and not blocker.get("failureEvidence"):
                blocker["failureEvidence"] = (
                    f"{first_finding.get('ruleId')} in {first_finding.get('tarball')}: "
                    f"{first_finding.get('member')} ({first_finding.get('evidence')}); "
                    f"{hygiene.get('blockedFindingCount')} blocked finding(s)"
                )
        if result_ux.get("nextCommand") and not blocker.get("nextCommand"):
            blocker["nextCommand"] = result_ux["nextCommand"]
        return blocker or None

    release_readiness = report.get("releaseReadiness") if isinstance(report.get("releaseReadiness"), dict) else {}
    for receipt in (
        "freshInstallPackageProof",
        "upgradePackageProof",
        "rollbackPackageProof",
        "githubReleaseAssetDownloadProof",
        "publishedReleaseAssetProof",
        "externalAdoptionEvidenceProof",
        "securityReviewEvidenceProof",
    ):
        proof = report.get(receipt)
        if not isinstance(proof, dict):
            proof = {}
        status = str(proof.get("status") or release_readiness.get(receipt) or "")
        if not status or status in {"pass", "not-provided", "not-requested"}:
            continue
        blocker = {
            "receipt": receipt,
            "status": status,
            "summary": proof.get("summary") or f"{receipt} did not pass in the LaunchKey report.",
            "failure": proof.get("error") or proof.get("summary") or "",
            "failureEvidence": proof.get("extractEvidence") or proof.get("previousExtractEvidence") or proof.get("candidateExtractEvidence") or proof.get("error") or "",
            "nextCommand": proof.get("nextCommand") or result_ux.get("nextCommand") or "",
            "proofSource": receipt,
        }
        hygiene = compact_package_hygiene_evidence(proof.get("packageHygieneEvidence"))
        if hygiene:
            blocker["packageHygieneEvidence"] = hygiene
            if hygiene.get("nextCommand"):
                blocker["nextCommand"] = hygiene["nextCommand"]
            first_finding = hygiene.get("firstFinding") if isinstance(hygiene.get("firstFinding"), dict) else {}
            if first_finding and not blocker["failureEvidence"]:
                blocker["failureEvidence"] = (
                    f"{first_finding.get('ruleId')} in {first_finding.get('tarball')}: "
                    f"{first_finding.get('member')} ({first_finding.get('evidence')}); "
                    f"{hygiene.get('blockedFindingCount')} blocked finding(s)"
                )
        return {key: value for key, value in blocker.items() if value not in ("", None)}
    return None


def add_launchkey_blocker_to_evidence_item(item: dict[str, Any], proof: dict[str, Any]) -> None:
    blocker = proof.get("launchKeyBlockingProof")
    if isinstance(blocker, dict):
        item["blockingProof"] = blocker
        if blocker.get("failureEvidence"):
            item["failureEvidence"] = blocker["failureEvidence"]
        if blocker.get("nextCommand"):
            item["nextCommand"] = blocker["nextCommand"]


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
    launchkey_blocker = extract_launchkey_blocking_proof(report) if report else None
    release_readiness = report.get("releaseReadiness") if isinstance(report.get("releaseReadiness"), dict) else {}
    candidate_readiness_statuses = {
        str(area["receipt"]): release_readiness.get(str(area["receipt"]), "not-reported")
        for area in LAUNCHKEY_REQUIRED_PROOF_AREAS
    }
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
        "candidateReadinessStatuses": candidate_readiness_statuses,
        "missingPackageProof": missing,
        "summary": "LaunchKey package install, upgrade, and rollback proof passed.",
        "nextCommand": "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable",
    }
    if launchkey_blocker:
        proof["launchKeyBlockingProof"] = launchkey_blocker
        if launchkey_blocker.get("failureEvidence"):
            proof["failureEvidence"] = launchkey_blocker["failureEvidence"]
        if launchkey_blocker.get("packageHygieneEvidence"):
            proof["packageHygieneEvidence"] = launchkey_blocker["packageHygieneEvidence"]
        if launchkey_blocker.get("nextCommand"):
            proof["nextCommand"] = launchkey_blocker["nextCommand"]
    if not report:
        proof["status"] = "blocked"
        proof["summary"] = "LaunchKey release-candidate report could not be loaded."
        proof["error"] = "missing or invalid v4-release-candidate JSON"
    elif not tool_ok:
        proof["summary"] = "Supplied report is not a LaunchKey release-candidate report."
    elif not status_ok:
        if launchkey_blocker:
            proof["summary"] = (
                f"LaunchKey report has not passed because "
                f"{launchkey_blocker.get('receipt') or 'a required receipt'} is "
                f"{launchkey_blocker.get('status') or 'not pass'}."
            )
        else:
            proof["summary"] = "LaunchKey report has not passed."
    elif not claim_ok:
        proof["summary"] = "LaunchKey report does not prove candidate readiness without a stable-v4 claim."
    elif missing:
        proof["summary"] = "LaunchKey report is missing package install, upgrade, or rollback proof required for stable publication."
    return proof


def build_github_tag_target_proof(args: argparse.Namespace, release_tag: str) -> dict[str, Any]:
    proof: dict[str, Any] = {
        "status": "not-provided",
        "repo": args.github_release_repo or "",
        "tag": release_tag,
        "tagRefEndpoint": "",
        "tagObjectSha": "",
        "tagObjectType": "",
        "tagTargetSha": "",
        "tagTargetType": "",
        "summary": "GitHub tag target proof was not requested because no repository was selected.",
    }
    if not args.github_release_repo or "/" not in args.github_release_repo:
        return proof

    token = os.environ.get(args.github_token_env or "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "shipguard-stable-publication",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    ref_endpoint = launchkey.join_api_url(args.github_api_url, f"/repos/{args.github_release_repo}/git/ref/tags/{release_tag}")
    proof["tagRefEndpoint"] = ref_endpoint
    try:
        ref_payload = launchkey.request_json(ref_endpoint, headers)
    except (RuntimeError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        proof.update(
            {
                "status": "blocked",
                "summary": "GitHub tag target could not be loaded.",
                "error": launchkey.short_output(str(exc), 500),
            }
        )
        return proof

    ref_object = ref_payload.get("object") if isinstance(ref_payload.get("object"), dict) else {}
    object_sha = str(ref_object.get("sha") or "")
    object_type = str(ref_object.get("type") or "")
    proof.update(
        {
            "status": "blocked",
            "tagObjectSha": object_sha,
            "tagObjectType": object_type,
            "tagTargetSha": object_sha if object_type == "commit" else "",
            "tagTargetType": object_type if object_type == "commit" else "",
            "summary": "GitHub tag ref loaded but did not resolve to a commit target.",
        }
    )
    if object_type == "commit" and object_sha:
        proof["status"] = "pass"
        proof["summary"] = "GitHub tag target resolves to a commit."
        return proof

    if object_type != "tag" or not object_sha:
        return proof

    tag_endpoint = launchkey.join_api_url(args.github_api_url, f"/repos/{args.github_release_repo}/git/tags/{object_sha}")
    proof["annotatedTagEndpoint"] = tag_endpoint
    try:
        tag_payload = launchkey.request_json(tag_endpoint, headers)
    except (RuntimeError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        proof.update(
            {
                "status": "blocked",
                "summary": "Annotated GitHub tag object could not be loaded.",
                "error": launchkey.short_output(str(exc), 500),
            }
        )
        return proof

    tag_object = tag_payload.get("object") if isinstance(tag_payload.get("object"), dict) else {}
    target_sha = str(tag_object.get("sha") or "")
    target_type = str(tag_object.get("type") or "")
    proof.update(
        {
            "tagTargetSha": target_sha,
            "tagTargetType": target_type,
        }
    )
    if target_type == "commit" and target_sha:
        proof["status"] = "pass"
        proof["summary"] = "Annotated GitHub tag resolves to a commit."
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
        "metadataTagName": "",
        "apiUrl": args.github_api_url.rstrip("/"),
        "requiredAssets": sorted(REQUIRED_RELEASE_ASSETS | {requested_tarball_name(release_version)}),
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

    tag_target_proof = build_github_tag_target_proof(args, release_tag)
    assets = release.get("assets") if isinstance(release.get("assets"), list) else []
    asset_names = sorted(str(asset.get("name") or "") for asset in assets if isinstance(asset, dict))
    required_assets = set(proof["requiredAssets"])
    missing_assets = sorted(required_assets - set(asset_names))
    body = str(release.get("body") or "")
    release_notes_analysis = analyze_release_notes(body)
    metadata_tag_name = str(release.get("tag_name") or release.get("tagName") or "")
    proof.update(
        {
            "status": "pass" if not missing_assets and metadata_tag_name == release_tag else "review",
            "provided": True,
            "summary": "GitHub release metadata was loaded and required release assets are present.",
            "releaseUrl": release.get("html_url") or release.get("url") or "",
            "metadataTagName": metadata_tag_name,
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
            "githubTagTargetProof": tag_target_proof,
            "tagRefEndpoint": tag_target_proof.get("tagRefEndpoint") or "",
            "tagObjectSha": tag_target_proof.get("tagObjectSha") or "",
            "tagObjectType": tag_target_proof.get("tagObjectType") or "",
            "tagTargetSha": tag_target_proof.get("tagTargetSha") or "",
            "tagTargetType": tag_target_proof.get("tagTargetType") or "",
        }
    )
    if missing_assets:
        proof["summary"] = "GitHub release metadata loaded, but required stable-publication assets are missing."
    if metadata_tag_name != release_tag:
        proof["summary"] = "GitHub release metadata loaded, but returned release tag does not match the requested tag."
    if proof["isDraft"] or proof["isPrerelease"]:
        proof["status"] = "review"
        proof["summary"] = "GitHub release exists but is draft or prerelease."
    return proof


def build_github_latest_release_proof(args: argparse.Namespace) -> dict[str, Any]:
    proof: dict[str, Any] = {
        "status": "not-provided",
        "provided": bool(args.github_release_repo),
        "repo": args.github_release_repo or "",
        "tag": "",
        "version": "",
        "releaseUrl": "",
        "publishedAt": "",
        "targetCommitish": "",
        "tagTargetSha": "",
        "tagTargetProofStatus": "not-provided",
        "summary": "Latest GitHub release metadata was not requested because no repository was selected.",
    }
    if not args.github_release_repo or "/" not in args.github_release_repo:
        return proof

    token = os.environ.get(args.github_token_env or "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "shipguard-stable-publication",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    endpoint = launchkey.join_api_url(args.github_api_url, f"/repos/{args.github_release_repo}/releases/latest")
    proof["releaseEndpoint"] = endpoint
    try:
        release = launchkey.request_json(endpoint, headers)
    except (RuntimeError, OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        proof.update(
            {
                "status": "blocked",
                "summary": "Latest GitHub release metadata could not be loaded.",
                "error": launchkey.short_output(str(exc), 500),
            }
        )
        return proof

    tag = str(release.get("tag_name") or release.get("tagName") or "")
    tag_target_proof = build_github_tag_target_proof(args, tag) if tag else {}
    proof.update(
        {
            "status": "pass" if tag else "review",
            "provided": True,
            "summary": "Latest GitHub release metadata loaded." if tag else "Latest GitHub release metadata has no tag.",
            "tag": tag,
            "version": normalize_version(tag),
            "releaseUrl": release.get("html_url") or release.get("url") or "",
            "publishedAt": release.get("published_at") or release.get("publishedAt") or "",
            "targetCommitish": release.get("target_commitish") or release.get("targetCommitish") or "",
            "isDraft": bool(release.get("draft") or release.get("isDraft")),
            "isPrerelease": bool(release.get("prerelease") or release.get("isPrerelease")),
            "tagTargetSha": tag_target_proof.get("tagTargetSha") or "",
            "tagTargetProofStatus": tag_target_proof.get("status") or "not-provided",
        }
    )
    if proof.get("isDraft") or proof.get("isPrerelease"):
        proof["status"] = "review"
        proof["summary"] = "Latest GitHub release is draft or prerelease."
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


def build_consumer_digest_freshness(proof: dict[str, Any]) -> dict[str, Any]:
    path_raw = str(proof.get("assetDigestMatrixPath") or "")
    artifact_sha = str(proof.get("artifactSha256") or "")
    summary: dict[str, Any] = {
        "status": "not-provided",
        "assetDigestMatrixPath": path_raw,
        "schemaVersion": "",
        "totalAssetRows": 0,
        "requiredAssetNames": [],
        "presentRequiredAssetNames": [],
        "missingRequiredAssetNames": [],
        "missingSha256AssetNames": [],
        "releaseTarballName": "",
        "releaseTarballStatus": "not-provided",
        "releaseTarballSha256": "",
        "artifactSha256": artifact_sha,
        "releaseTarballDigestMatchesConsumerArtifact": None,
        "problems": [],
    }
    problems: list[str] = summary["problems"]
    if not path_raw:
        problems.append("asset-digests.json missing")
        return summary
    matrix = load_json(Path(path_raw))
    assets = matrix.get("assets") if isinstance(matrix.get("assets"), list) else []
    summary["schemaVersion"] = matrix.get("schema_version") or matrix.get("schemaVersion") or ""
    summary["totalAssetRows"] = len(assets)
    if not assets:
        summary["status"] = "review"
        problems.append("asset digest matrix has no assets")
        return summary

    required_rows = [row for row in assets if isinstance(row, dict) and row.get("required") is True]
    present_required = [row for row in required_rows if row.get("status") == "present"]
    missing_required = [str(row.get("name") or "") for row in required_rows if row.get("status") != "present"]
    missing_sha = [
        str(row.get("name") or "")
        for row in assets
        if isinstance(row, dict) and row.get("status") == "present" and not row.get("sha256")
    ]
    tarball_row = next(
        (
            row
            for row in assets
            if isinstance(row, dict)
            and (row.get("role") == "release tarball" or str(row.get("name") or "").endswith(".tar.gz"))
        ),
        {},
    )
    tarball_sha = str(tarball_row.get("sha256") or "") if isinstance(tarball_row, dict) else ""
    summary.update(
        {
            "requiredAssetNames": [str(row.get("name") or "") for row in required_rows],
            "presentRequiredAssetNames": [str(row.get("name") or "") for row in present_required],
            "missingRequiredAssetNames": [name for name in missing_required if name],
            "missingSha256AssetNames": [name for name in missing_sha if name],
            "releaseTarballName": str(tarball_row.get("name") or "") if isinstance(tarball_row, dict) else "",
            "releaseTarballStatus": str(tarball_row.get("status") or "not-provided") if isinstance(tarball_row, dict) else "not-provided",
            "releaseTarballSha256": tarball_sha,
        }
    )
    if not required_rows:
        problems.append("asset digest matrix has no required asset rows")
    if summary["missingRequiredAssetNames"]:
        problems.append("required release assets are missing from the digest matrix")
    if summary["missingSha256AssetNames"]:
        problems.append("present release assets are missing SHA-256 values")
    if not tarball_row:
        problems.append("release tarball row missing from asset digest matrix")
    if artifact_sha and tarball_sha:
        matches = artifact_sha == tarball_sha
        summary["releaseTarballDigestMatchesConsumerArtifact"] = matches
        if not matches:
            problems.append("release tarball digest does not match consumer artifact SHA-256")
    elif artifact_sha or tarball_sha:
        problems.append("release tarball digest cannot be compared with consumer artifact SHA-256")
    summary["status"] = "review" if problems else "pass"
    return summary


def build_post_release_consumer_proof(published_release_asset_proof: dict[str, Any]) -> dict[str, Any]:
    passed = published_release_asset_proof.get("status") == "pass"
    proof = {
        "status": "pass" if passed else published_release_asset_proof.get("status", "not-provided"),
        "provided": published_release_asset_proof.get("provided") is True,
        "requiredForStableV4": True,
        "summary": (
            "Downloaded release assets passed post-release consumer verification."
            if passed
            else "Post-release consumer proof needs downloaded assets to pass release-consume verification."
        ),
        "downloadSource": published_release_asset_proof.get("downloadSource"),
        "downloadProofStatus": published_release_asset_proof.get("downloadProofStatus"),
        "version": published_release_asset_proof.get("version"),
        "assetsDir": published_release_asset_proof.get("assetsDir"),
        "consumeOut": published_release_asset_proof.get("consumeOut"),
        "command": published_release_asset_proof.get("command"),
        "consumeCommand": published_release_asset_proof.get("consumeCommand"),
        "commandTemplate": published_release_asset_proof.get("commandTemplate"),
        "exitCode": published_release_asset_proof.get("exitCode"),
        "error": published_release_asset_proof.get("error"),
        "stdout": published_release_asset_proof.get("stdout"),
        "stderr": published_release_asset_proof.get("stderr"),
        "consumerReportStatus": published_release_asset_proof.get("consumerReportStatus"),
        "replayStatus": published_release_asset_proof.get("replayStatus"),
        "attestationStatus": published_release_asset_proof.get("attestationStatus"),
        "assetDigestMatrixPath": published_release_asset_proof.get("assetDigestMatrixPath"),
        "consumerReportPath": published_release_asset_proof.get("consumerReportPath"),
        "artifactSha256": published_release_asset_proof.get("artifactSha256"),
        "publishedReplayCrosscheck": published_release_asset_proof.get("publishedReplayCrosscheck"),
        "publishedAttestationCrosscheck": published_release_asset_proof.get("publishedAttestationCrosscheck"),
        "publishedBadgeCrosscheck": published_release_asset_proof.get("publishedBadgeCrosscheck"),
        "assetCount": published_release_asset_proof.get("assetCount"),
    }
    missing_artifacts: list[str] = []
    if not proof.get("consumerReportPath"):
        missing_artifacts.append("consumer-report.json")
    if not proof.get("assetDigestMatrixPath"):
        missing_artifacts.append("asset-digests.json")
    if missing_artifacts:
        proof["missingProofArtifacts"] = missing_artifacts
    digest_freshness = build_consumer_digest_freshness(proof)
    proof["consumerDigestFreshness"] = digest_freshness
    if passed and digest_freshness.get("status") != "pass":
        proof["status"] = "review"
        proof["summary"] = "Downloaded release assets passed release-consume, but digest freshness needs review."
        proof["consumerDigestFreshnessProblems"] = digest_freshness.get("problems") if isinstance(digest_freshness.get("problems"), list) else []
    return proof


def build_public_release_freshness_proof(
    *,
    root: Path,
    release_version: str,
    metadata_proof: dict[str, Any],
    published_asset_proof: dict[str, Any],
) -> dict[str, Any]:
    release_tag = str(metadata_proof.get("tag") or launchkey.normalize_release_tag(release_version))
    assets_dir_raw = str(published_asset_proof.get("assetsDir") or "")
    manifest_path = Path(assets_dir_raw).expanduser().resolve() / "release-manifest.json" if assets_dir_raw else None
    tag_target_proof = metadata_proof.get("githubTagTargetProof") if isinstance(metadata_proof.get("githubTagTargetProof"), dict) else {}
    target_commitish = str(metadata_proof.get("targetCommitish") or "")
    local_head = git_rev_parse(root, "HEAD")
    local_tag_commit = git_rev_parse(root, f"{release_tag}^{{commit}}") if release_tag else ""
    proof: dict[str, Any] = {
        "status": "not-provided",
        "provided": False,
        "requiredForStableV4": True,
        "summary": "Public release freshness needs GitHub metadata plus downloaded or supplied release assets.",
        "releaseVersion": release_version,
        "releaseTag": release_tag,
        "metadataStatus": metadata_proof.get("status"),
        "publishedReleaseAssetStatus": published_asset_proof.get("status"),
        "releaseUrl": metadata_proof.get("releaseUrl") or "",
        "publishedAt": metadata_proof.get("publishedAt") or "",
        "releaseTargetCommitish": target_commitish,
        "tagRefEndpoint": tag_target_proof.get("tagRefEndpoint") or metadata_proof.get("tagRefEndpoint") or "",
        "tagObjectSha": tag_target_proof.get("tagObjectSha") or metadata_proof.get("tagObjectSha") or "",
        "tagObjectType": tag_target_proof.get("tagObjectType") or metadata_proof.get("tagObjectType") or "",
        "tagTargetSha": tag_target_proof.get("tagTargetSha") or metadata_proof.get("tagTargetSha") or "",
        "tagTargetType": tag_target_proof.get("tagTargetType") or metadata_proof.get("tagTargetType") or "",
        "tagTargetProofStatus": tag_target_proof.get("status") or "not-provided",
        "assetsDir": assets_dir_raw,
        "releaseManifestPath": manifest_path.as_posix() if manifest_path else "",
        "manifestVersion": "",
        "manifestTag": "",
        "manifestCommit": "",
        "manifestGeneratedAt": "",
        "artifactName": "",
        "artifactSha256": "",
        "localHeadCommit": local_head,
        "localTagCommit": local_tag_commit,
        "comparisons": {},
        "problems": [],
        "nextCommand": stable_publication_command(
            argparse.Namespace(
                github_release_repo=metadata_proof.get("repo") or "<owner/repo>",
                release_version=release_version,
                release_candidate_report="<v4-release-candidate-json-or-dir>",
                release_assets=None,
                external_adoption_evidence=[],
                security_review_evidence=[],
            ),
            placeholders=True,
        ),
    }

    problems: list[str] = []
    if metadata_proof.get("status") != "pass":
        problems.append("GitHub release metadata must pass before freshness can pass.")
    if published_asset_proof.get("status") != "pass":
        problems.append("Downloaded or supplied release assets must pass release-consume before freshness can pass.")
    if not manifest_path or not manifest_path.is_file():
        problems.append("Downloaded or supplied release assets are missing release-manifest.json.")
        proof["problems"] = problems
        proof["summary"] = "Public release freshness could not find release-manifest.json in the release assets."
        return proof

    manifest = load_json(manifest_path)
    artifact = manifest.get("artifact") if isinstance(manifest.get("artifact"), dict) else {}
    manifest_version = str(manifest.get("version") or "")
    manifest_tag = str(manifest.get("tag") or "")
    manifest_commit = str(manifest.get("commit") or "")
    manifest_generated_at = str(manifest.get("generated_at") or manifest.get("generatedAt") or "")
    proof.update(
        {
            "provided": True,
            "manifestVersion": manifest_version,
            "manifestTag": manifest_tag,
            "manifestCommit": manifest_commit,
            "manifestGeneratedAt": manifest_generated_at,
            "artifactName": artifact.get("name") or "",
            "artifactSha256": artifact.get("sha256") or "",
        }
    )

    tag_target_sha = str(proof.get("tagTargetSha") or "")
    target_commitish_is_sha = is_sha_like(target_commitish)
    comparisons = {
        "manifestVersionMatchesRequested": normalize_version(manifest_version) == normalize_version(release_version),
        "manifestTagMatchesMetadataTag": manifest_tag == release_tag,
        "tagTargetMatchesManifestCommit": sha_matches(tag_target_sha, manifest_commit),
        "releaseTargetCommitishIsSha": target_commitish_is_sha,
        "releaseTargetCommitishMatchesManifestCommit": (
            sha_matches(target_commitish, manifest_commit) if target_commitish_is_sha else None
        ),
        "localHeadMatchesManifestCommit": sha_matches(local_head, manifest_commit) if local_head else None,
        "localTagMatchesManifestCommit": sha_matches(local_tag_commit, manifest_commit) if local_tag_commit else None,
        "manifestGeneratedNoLaterThanPublishedAt": None,
    }
    published_at = parse_utc_datetime(proof.get("publishedAt"))
    manifest_generated = parse_utc_datetime(manifest_generated_at)
    if published_at and manifest_generated:
        comparisons["manifestGeneratedNoLaterThanPublishedAt"] = manifest_generated <= published_at

    if not comparisons["manifestVersionMatchesRequested"]:
        problems.append("release-manifest.json version does not match the requested release version.")
    if not comparisons["manifestTagMatchesMetadataTag"]:
        problems.append("release-manifest.json tag does not match the public GitHub release tag.")
    if tag_target_proof.get("status") != "pass":
        problems.append("Public GitHub tag target did not resolve to a commit.")
    if not comparisons["tagTargetMatchesManifestCommit"]:
        problems.append("Public GitHub tag target does not match release-manifest.json commit.")
    if target_commitish_is_sha and not comparisons["releaseTargetCommitishMatchesManifestCommit"]:
        problems.append("GitHub release target_commitish SHA does not match release-manifest.json commit.")
    if comparisons["manifestGeneratedNoLaterThanPublishedAt"] is False:
        problems.append("release-manifest.json was generated after the public release publication timestamp.")
    if not manifest_commit or manifest_commit == "unknown":
        problems.append("release-manifest.json does not record a concrete commit SHA.")

    proof["comparisons"] = comparisons
    proof["problems"] = problems
    proof["status"] = "pass" if not problems else "review"
    proof["summary"] = (
        "Public release metadata, tag target, release manifest, and asset proof are fresh and consistent."
        if not problems
        else "Public release freshness has mismatched or incomplete tag, manifest, metadata, or asset proof."
    )
    return proof


def build_release_version_coherence_proof(
    *,
    source_version: str,
    release_version: str,
    metadata_proof: dict[str, Any],
    published_asset_proof: dict[str, Any],
    public_release_freshness_proof: dict[str, Any],
) -> dict[str, Any]:
    requested = normalize_version(release_version)
    expected_tag = launchkey.normalize_release_tag(release_version)
    expected_tarball = requested_tarball_name(release_version)
    consumer_report_path = str(published_asset_proof.get("consumerReportPath") or "")
    consumer_report = load_json(Path(consumer_report_path)) if consumer_report_path else {}
    digest = (
        public_release_freshness_proof.get("artifactName")
        or published_asset_proof.get("artifactName")
        or ""
    )
    required_assets = set(str(value) for value in metadata_proof.get("requiredAssets", []) if value)
    metadata_assets = set(str(value) for value in metadata_proof.get("assetNames", []) if value)
    digest_assets = set()
    matrix_path = str(published_asset_proof.get("assetDigestMatrixPath") or "")
    if matrix_path:
        matrix = load_json(Path(matrix_path))
        rows = matrix.get("assets") if isinstance(matrix.get("assets"), list) else []
        digest_assets = {str(row.get("name") or "") for row in rows if isinstance(row, dict)}

    comparisons = {
        "sourceVersionMatchesRequested": normalize_version(source_version) == requested,
        "metadataVersionMatchesRequested": normalize_version(str(metadata_proof.get("version") or "")) == requested,
        "metadataTagMatchesRequested": str(metadata_proof.get("tag") or "") == expected_tag,
        "metadataReturnedTagMatchesRequested": str(metadata_proof.get("metadataTagName") or "") == expected_tag,
        "manifestVersionMatchesRequested": normalize_version(str(public_release_freshness_proof.get("manifestVersion") or "")) == requested,
        "manifestTagMatchesRequested": str(public_release_freshness_proof.get("manifestTag") or "") == expected_tag,
        "packageVersionMatchesRequested": normalize_version(str(published_asset_proof.get("version") or "")) == requested,
        "consumerReportVersionMatchesRequested": normalize_version(str(consumer_report.get("version") or "")) == requested,
        "manifestArtifactNameMatchesRequestedTarball": str(digest or "") == expected_tarball,
        "metadataRequiredAssetsContainRequestedTarball": expected_tarball in required_assets,
        "metadataAssetsContainRequestedTarball": expected_tarball in metadata_assets,
        "consumerDigestAssetsContainRequestedTarball": expected_tarball in digest_assets,
    }
    labels = {
        "sourceVersionMatchesRequested": "VERSION does not match the requested release version.",
        "metadataVersionMatchesRequested": "GitHub metadata proof version does not match the requested release version.",
        "metadataTagMatchesRequested": "GitHub metadata proof tag does not match the requested release tag.",
        "metadataReturnedTagMatchesRequested": "GitHub returned tag_name does not match the requested release tag.",
        "manifestVersionMatchesRequested": "release-manifest.json version does not match the requested release version.",
        "manifestTagMatchesRequested": "release-manifest.json tag does not match the requested release tag.",
        "packageVersionMatchesRequested": "Release-consume package version does not match the requested release version.",
        "consumerReportVersionMatchesRequested": "consumer-report.json version does not match the requested release version.",
        "manifestArtifactNameMatchesRequestedTarball": "release-manifest.json artifact name does not match the requested versioned tarball.",
        "metadataRequiredAssetsContainRequestedTarball": "GitHub metadata required asset list does not include the requested versioned tarball.",
        "metadataAssetsContainRequestedTarball": "GitHub release metadata asset list does not include the requested versioned tarball.",
        "consumerDigestAssetsContainRequestedTarball": "asset-digests.json does not include the requested versioned tarball.",
    }
    problems = [labels[key] for key, passed in comparisons.items() if passed is not True]
    if metadata_proof.get("status") != "pass":
        problems.append("GitHub release metadata must pass before version coherence can pass.")
    if published_asset_proof.get("status") != "pass":
        problems.append("Release-consume package proof must pass before version coherence can pass.")
    if public_release_freshness_proof.get("status") != "pass":
        problems.append("Public release freshness must pass before version coherence can pass.")

    return {
        "schemaVersion": 1,
        "status": "pass" if not problems else "review",
        "provided": True,
        "requiredForStableV4": True,
        "summary": (
            "VERSION, GitHub release metadata, release manifest, package proof, and consumer digest all name the same release version."
            if not problems
            else "Release version metadata is mismatched or incomplete."
        ),
        "sourceVersion": source_version,
        "releaseVersion": release_version,
        "normalizedReleaseVersion": requested,
        "expectedTag": expected_tag,
        "metadataTagName": metadata_proof.get("metadataTagName") or "",
        "manifestVersion": public_release_freshness_proof.get("manifestVersion") or "",
        "manifestTag": public_release_freshness_proof.get("manifestTag") or "",
        "packageVersion": published_asset_proof.get("version") or "",
        "consumerReportVersion": consumer_report.get("version") or "",
        "expectedTarballName": expected_tarball,
        "manifestArtifactName": digest,
        "comparisons": comparisons,
        "problems": problems,
        "repairCriteria": RELEASE_VERSION_COHERENCE_REPAIR_CRITERIA,
        "passCriteria": RELEASE_VERSION_COHERENCE_PASS_CRITERIA,
        "failCriteria": RELEASE_VERSION_COHERENCE_FAIL_CRITERIA,
        "nextCommand": stable_publication_command(
            argparse.Namespace(
                github_release_repo=metadata_proof.get("repo") or "<owner/repo>",
                release_version=release_version,
                release_candidate_report="<v4-release-candidate-json-or-dir>",
                release_assets=None,
                external_adoption_evidence=[],
                security_review_evidence=[],
            ),
            placeholders=True,
        ),
        "versionCoherenceBoundary": {
            "versionMustMatchAcrossSourceMetadataManifestPackageAndConsumerProof": True,
            "githubMetadataReturnedTagNameMustMatchRequestedTag": True,
            "sourceOnlyProofCountsAsVersionCoherenceProof": False,
            "fixtureApiProofCountsAsStableV4PublicationProof": False,
        },
    }


def digest_rows_from_matrix(path_raw: object) -> list[dict[str, Any]]:
    if not path_raw:
        return []
    matrix = load_json(Path(str(path_raw)))
    rows = matrix.get("assets") if isinstance(matrix.get("assets"), list) else []
    return [row for row in rows if isinstance(row, dict)]


def build_release_asset_coherence_proof(
    *,
    release_version: str,
    metadata_proof: dict[str, Any],
    published_asset_proof: dict[str, Any],
    post_release_consumer_proof: dict[str, Any],
    public_release_freshness_proof: dict[str, Any],
    release_version_coherence_proof: dict[str, Any],
) -> dict[str, Any]:
    expected_tarball = requested_tarball_name(release_version)
    required_assets = sorted(str(value) for value in metadata_proof.get("requiredAssets", []) if value)
    metadata_assets = sorted(str(value) for value in metadata_proof.get("assetNames", []) if value)
    local_assets = asset_names_from_dir(published_asset_proof.get("assetsDir") or "")
    digest_rows = digest_rows_from_matrix(post_release_consumer_proof.get("assetDigestMatrixPath") or published_asset_proof.get("assetDigestMatrixPath"))
    digest_assets = sorted(str(row.get("name") or "") for row in digest_rows if row.get("name"))
    missing_sha = sorted(
        str(row.get("name") or "")
        for row in digest_rows
        if row.get("status") == "present" and row.get("name") and not row.get("sha256")
    )
    digest_by_name = {str(row.get("name") or ""): str(row.get("sha256") or "") for row in digest_rows if row.get("name")}
    digest_freshness = (
        post_release_consumer_proof.get("consumerDigestFreshness")
        if isinstance(post_release_consumer_proof.get("consumerDigestFreshness"), dict)
        else {}
    )
    manifest_artifact_name = str(public_release_freshness_proof.get("artifactName") or "")
    manifest_artifact_sha = str(public_release_freshness_proof.get("artifactSha256") or "")
    digest_tarball_name = str(digest_freshness.get("releaseTarballName") or "")
    digest_tarball_sha = str(digest_freshness.get("releaseTarballSha256") or digest_by_name.get(expected_tarball) or "")
    consumer_artifact_sha = str(post_release_consumer_proof.get("artifactSha256") or published_asset_proof.get("artifactSha256") or "")
    required_set = set(required_assets)

    comparisons = {
        "metadataAssetsCoverRequired": bool(required_set) and required_set.issubset(set(metadata_assets)),
        "localAssetsCoverRequired": bool(required_set) and required_set.issubset(set(local_assets)),
        "digestAssetsCoverRequired": bool(required_set) and required_set.issubset(set(digest_assets)),
        "expectedTarballInRequiredAssets": expected_tarball in required_set,
        "expectedTarballInMetadataAssets": expected_tarball in set(metadata_assets),
        "expectedTarballInLocalAssets": expected_tarball in set(local_assets),
        "expectedTarballInDigestAssets": expected_tarball in set(digest_assets),
        "manifestArtifactNameMatchesExpectedTarball": manifest_artifact_name == expected_tarball,
        "digestTarballNameMatchesExpectedTarball": digest_tarball_name == expected_tarball,
        "allPresentDigestRowsHaveSha256": not missing_sha,
        "manifestArtifactShaMatchesDigestTarball": bool(manifest_artifact_sha and digest_tarball_sha and manifest_artifact_sha == digest_tarball_sha),
        "consumerArtifactShaMatchesDigestTarball": digest_freshness.get("releaseTarballDigestMatchesConsumerArtifact") is True,
    }
    labels = {
        "metadataAssetsCoverRequired": "GitHub release metadata does not list every required stable-publication asset.",
        "localAssetsCoverRequired": "Downloaded or supplied release assets do not contain every required stable-publication asset.",
        "digestAssetsCoverRequired": "asset-digests.json does not list every required stable-publication asset.",
        "expectedTarballInRequiredAssets": "Required assets do not include the expected versioned ShipGuard tarball.",
        "expectedTarballInMetadataAssets": "GitHub release metadata does not include the expected versioned ShipGuard tarball.",
        "expectedTarballInLocalAssets": "Downloaded or supplied release assets do not include the expected versioned ShipGuard tarball.",
        "expectedTarballInDigestAssets": "asset-digests.json does not include the expected versioned ShipGuard tarball.",
        "manifestArtifactNameMatchesExpectedTarball": "release-manifest.json artifact name does not match the expected versioned tarball.",
        "digestTarballNameMatchesExpectedTarball": "asset-digests.json tarball row does not match the expected versioned tarball.",
        "allPresentDigestRowsHaveSha256": "One or more present release assets lack SHA-256 values in asset-digests.json.",
        "manifestArtifactShaMatchesDigestTarball": "release-manifest.json artifact SHA-256 does not match the digest tarball SHA-256.",
        "consumerArtifactShaMatchesDigestTarball": "consumer-report artifact SHA-256 does not match the digest tarball SHA-256.",
    }
    problems = [labels[key] for key, passed in comparisons.items() if passed is not True]
    if published_asset_proof.get("status") != "pass":
        problems.append("Downloaded or supplied release assets must pass before asset coherence can pass.")
    if post_release_consumer_proof.get("status") != "pass":
        problems.append("Post-release consumer proof must pass before asset coherence can pass.")
    if public_release_freshness_proof.get("status") != "pass":
        problems.append("Public release freshness must pass before asset coherence can pass.")
    if release_version_coherence_proof.get("status") != "pass":
        problems.append("Release version coherence must pass before asset coherence can pass.")

    return {
        "schemaVersion": 1,
        "status": "pass" if not problems else "review",
        "provided": True,
        "requiredForStableV4": True,
        "summary": (
            "Release asset names and SHA-256 values match across metadata, downloaded assets, manifest, digest matrix, and consumer proof."
            if not problems
            else "Release asset names or SHA-256 values are mismatched or incomplete."
        ),
        "releaseVersion": release_version,
        "expectedTarballName": expected_tarball,
        "requiredAssetNames": required_assets,
        "metadataAssetNames": metadata_assets,
        "localAssetNames": local_assets,
        "digestAssetNames": digest_assets,
        "missingLocalAssetNames": sorted(required_set - set(local_assets)),
        "missingDigestAssetNames": sorted(required_set - set(digest_assets)),
        "missingSha256AssetNames": missing_sha,
        "manifestArtifactName": manifest_artifact_name,
        "manifestArtifactSha256": manifest_artifact_sha,
        "digestTarballName": digest_tarball_name,
        "digestTarballSha256": digest_tarball_sha,
        "consumerArtifactSha256": consumer_artifact_sha,
        "comparisons": comparisons,
        "problems": problems,
        "repairCriteria": RELEASE_ASSET_COHERENCE_REPAIR_CRITERIA,
        "passCriteria": RELEASE_ASSET_COHERENCE_PASS_CRITERIA,
        "failCriteria": RELEASE_ASSET_COHERENCE_FAIL_CRITERIA,
        "nextCommand": stable_publication_command(
            argparse.Namespace(
                github_release_repo=metadata_proof.get("repo") or "<owner/repo>",
                release_version=release_version,
                release_candidate_report="<v4-release-candidate-json-or-dir>",
                release_assets=None,
                external_adoption_evidence=[],
                security_review_evidence=[],
            ),
            placeholders=True,
        ),
        "assetCoherenceBoundary": {
            "downloadedOrSuppliedAssetsRequired": True,
            "assetDigestMatrixRequired": True,
            "manifestArtifactMustMatchDigestTarball": True,
            "sourceOnlyProofCountsAsAssetCoherenceProof": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
            "metadataOnlyProofCountsAsAssetCoherenceProof": False,
        },
    }


def build_public_release_delta_proof(
    *,
    root: Path,
    source_version: str,
    release_version: str,
    metadata_proof: dict[str, Any],
    latest_release_proof: dict[str, Any],
    published_asset_proof: dict[str, Any],
    public_release_freshness_proof: dict[str, Any],
    release_version_coherence_proof: dict[str, Any],
    release_asset_coherence_proof: dict[str, Any],
    stable_v4_release: bool,
    rerun_command: str,
) -> dict[str, Any]:
    local_head = git_rev_parse(root, "HEAD")
    local_main = git_rev_parse(root, "main^{commit}") or local_head
    selected_tag = str(metadata_proof.get("tag") or launchkey.normalize_release_tag(release_version))
    latest_tag = str(latest_release_proof.get("tag") or "")
    manifest_commit = str(public_release_freshness_proof.get("manifestCommit") or "")
    selected_release_commit = str(public_release_freshness_proof.get("tagTargetSha") or "")
    package_version = str(published_asset_proof.get("version") or "")
    freshness_comparisons = (
        public_release_freshness_proof.get("comparisons")
        if isinstance(public_release_freshness_proof.get("comparisons"), dict)
        else {}
    )
    comparisons = {
        "sourceVersionMatchesRequestedRelease": normalize_version(source_version) == normalize_version(release_version),
        "selectedReleaseMatchesLatestGitHubRelease": latest_release_proof.get("status") == "pass" and latest_tag == selected_tag,
        "releaseManifestVersionMatchesRequestedRelease": normalize_version(str(public_release_freshness_proof.get("manifestVersion") or "")) == normalize_version(release_version),
        "packageAssetsVersionMatchesRequestedRelease": normalize_version(package_version) == normalize_version(release_version),
        "publicTagTargetMatchesReleaseManifestCommit": freshness_comparisons.get("tagTargetMatchesManifestCommit") is True,
        "releaseAssetCoherencePassed": release_asset_coherence_proof.get("status") == "pass",
        "releaseVersionCoherencePassed": release_version_coherence_proof.get("status") == "pass",
        "localHeadMatchesSelectedPublicReleaseCommit": sha_matches(local_head, manifest_commit) if local_head and manifest_commit else None,
        "localMainMatchesSelectedPublicReleaseCommit": sha_matches(local_main, manifest_commit) if local_main and manifest_commit else None,
    }
    stable_claim_covers_public_release = (
        stable_v4_release
        and comparisons["selectedReleaseMatchesLatestGitHubRelease"] is True
        and comparisons["releaseVersionCoherencePassed"] is True
        and comparisons["releaseAssetCoherencePassed"] is True
    )
    stable_claim_covers_local_checkout = (
        stable_claim_covers_public_release
        and comparisons["localHeadMatchesSelectedPublicReleaseCommit"] is True
        and comparisons["localMainMatchesSelectedPublicReleaseCommit"] is True
    )
    problems: list[str] = []
    labels = {
        "sourceVersionMatchesRequestedRelease": "VERSION does not match the requested publication version.",
        "selectedReleaseMatchesLatestGitHubRelease": "The selected publication tag is not the latest public GitHub release.",
        "releaseManifestVersionMatchesRequestedRelease": "release-manifest.json does not match the selected publication version.",
        "packageAssetsVersionMatchesRequestedRelease": "Downloaded or supplied package assets do not match the selected publication version.",
        "publicTagTargetMatchesReleaseManifestCommit": "The public tag target does not match the release manifest commit.",
        "releaseAssetCoherencePassed": "Release asset coherence has not passed.",
        "releaseVersionCoherencePassed": "Release version coherence has not passed.",
    }
    for key, label in labels.items():
        if comparisons.get(key) is not True:
            problems.append(label)
    if comparisons["localHeadMatchesSelectedPublicReleaseCommit"] is False:
        problems.append("Local HEAD contains code that is not the selected public release.")
    if comparisons["localMainMatchesSelectedPublicReleaseCommit"] is False:
        problems.append("Local main contains code that is not the selected public release.")
    unpublished_delta = (
        comparisons["localHeadMatchesSelectedPublicReleaseCommit"] is False
        or comparisons["localMainMatchesSelectedPublicReleaseCommit"] is False
    )
    return {
        "schemaVersion": 1,
        "status": "pass" if not problems else "review",
        "releaseVersion": release_version,
        "sourceVersion": source_version,
        "latestGitHubReleaseVersion": latest_release_proof.get("version") or "",
        "selectedGitHubReleaseTag": selected_tag,
        "latestGitHubReleaseTag": latest_tag,
        "latestGitHubReleaseStatus": latest_release_proof.get("status") or "not-provided",
        "latestGitHubReleaseUrl": latest_release_proof.get("releaseUrl") or "",
        "packageVersion": package_version,
        "localHeadCommit": local_head,
        "localMainCommit": local_main,
        "selectedPublicReleaseCommit": selected_release_commit,
        "releaseManifestCommit": manifest_commit,
        "stableV4Release": stable_v4_release,
        "stableV4ClaimCoversSelectedPublicRelease": stable_claim_covers_public_release,
        "stableV4ClaimCoversLocalCheckout": stable_claim_covers_local_checkout,
        "unpublishedLocalDelta": unpublished_delta,
        "summary": (
            "Local source, latest GitHub release, release manifest, package assets, and stable-v4 claim context are aligned."
            if not problems
            else "Local source, latest GitHub release, package assets, or claim context are out of sync."
        ),
        "comparisons": comparisons,
        "problems": problems,
        "nextCommand": rerun_command,
        "releaseDeltaBoundary": {
            "latestPublicGitHubReleaseIsPublicationSource": True,
            "localHeadIsNotPublicReleaseProof": True,
            "localMainIsNotPublicReleaseProof": True,
            "unpublishedLocalCodeCountsAsReleased": False,
            "downloadedOrSuppliedAssetsAreRequiredForPackageTruth": True,
            "stableV4ClaimCoversSelectedReleaseOnly": True,
        },
    }


def build_release_visibility_handoff(
    *,
    release_version: str,
    stable_v4_release: bool,
    release_notes_proof: dict[str, Any],
    release_notes_authoring_kit: dict[str, Any],
    release_candidate_packet_proof: dict[str, Any],
    published_asset_proof: dict[str, Any],
    public_evidence_closure_proof: dict[str, Any],
    public_release_delta_proof: dict[str, Any],
    release_asset_coherence_proof: dict[str, Any],
    final_claim_packet: dict[str, Any],
    rerun_command: str,
    release_create_command: str = "",
    release_asset_repair_command: str = "",
) -> dict[str, Any]:
    comparisons = (
        public_release_delta_proof.get("comparisons")
        if isinstance(public_release_delta_proof.get("comparisons"), dict)
        else {}
    )
    unpublished_delta = public_release_delta_proof.get("unpublishedLocalDelta") is True
    publication_mismatch = any(
        comparisons.get(key) is not True
        for key in (
            "selectedReleaseMatchesLatestGitHubRelease",
            "publicTagTargetMatchesReleaseManifestCommit",
        )
    )
    needs_release = publication_mismatch
    needs_notes = release_notes_proof.get("status") != "pass"
    needs_candidate = release_candidate_packet_proof.get("status") != "pass"
    needs_assets = (
        published_asset_proof.get("status") != "pass"
        or release_asset_coherence_proof.get("status") != "pass"
        or comparisons.get("packageAssetsVersionMatchesRequestedRelease") is not True
    )
    needs_evidence = public_evidence_closure_proof.get("status") != "pass"

    if stable_v4_release:
        primary = "announce-current-public-release"
    elif needs_release:
        primary = "publish-new-github-release"
    elif needs_notes:
        primary = "update-release-notes"
    elif needs_candidate:
        primary = "attach-launchkey-candidate-proof"
    elif needs_assets:
        primary = "update-release-assets"
    elif needs_evidence:
        primary = "attach-adoption-security-evidence"
    else:
        primary = "keep-current-public-release-in-review"

    release_notes_edit_command = str(
        release_notes_authoring_kit.get("publicReleaseEditCommand")
        or release_notes_proof.get("nextCommand")
        or rerun_command
    )
    release_create_command = str(
        release_create_command
        or "gh release create <tag> dist/shipguard-v<version>.tar.gz --notes-file <release-notes.md>"
    )
    actions = [
        {
            "id": "publish-new-github-release",
            "required": needs_release,
            "status": "review" if needs_release else "pass",
            "reason": (
                "The selected release is not the latest public release or its tag target does not match the release manifest commit."
                if needs_release
                else "Selected public release, latest release, tag target, and manifest are aligned; local source deltas are reported separately."
            ),
            "nextCommand": release_create_command if needs_release else "not-needed",
        },
        {
            "id": "update-release-notes",
            "required": needs_notes,
            "status": "review" if needs_notes else "pass",
            "reason": release_notes_proof.get("summary") or "Release notes proof status decides this action.",
            "nextCommand": release_notes_edit_command if needs_notes else "not-needed",
        },
        {
            "id": "attach-launchkey-candidate-proof",
            "required": needs_candidate,
            "status": "review" if needs_candidate else "pass",
            "reason": release_candidate_packet_proof.get("summary") or "LaunchKey candidate packet proof status decides this action.",
            "nextCommand": str(release_candidate_packet_proof.get("nextCommand") or rerun_command) if needs_candidate else "not-needed",
        },
        {
            "id": "update-release-assets",
            "required": needs_assets,
            "status": "review" if needs_assets else "pass",
            "reason": (
                "Downloaded or supplied release assets, package version, or SHA-256 coherence still needs repair."
                if needs_assets
                else "Release assets and digest coherence passed."
            ),
            "nextCommand": str(release_asset_repair_command or published_asset_proof.get("nextCommand") or rerun_command) if needs_assets else "not-needed",
        },
        {
            "id": "attach-adoption-security-evidence",
            "required": needs_evidence,
            "status": "review" if needs_evidence else "pass",
            "reason": public_evidence_closure_proof.get("summary") or "Adoption/security evidence closure status decides this action.",
            "nextCommand": str(public_evidence_closure_proof.get("rerunCommand") or rerun_command) if needs_evidence else "not-needed",
        },
        {
            "id": "keep-current-public-release-unchanged",
            "required": not any([needs_release, needs_notes, needs_candidate, needs_assets, needs_evidence]),
            "status": "pass" if not any([needs_release, needs_notes, needs_candidate, needs_assets, needs_evidence]) else "blocked",
            "reason": (
                "The current public release can remain the announcement target."
                if not any([needs_release, needs_notes, needs_candidate, needs_assets, needs_evidence])
                else "Do not treat the current public release as covering missing release, notes, candidate, asset, adoption, or security proof."
            ),
            "nextCommand": str(final_claim_packet.get("nextCommand") or rerun_command)
            if not any([needs_release, needs_notes, needs_candidate, needs_assets, needs_evidence])
            else "blocked-by-required-actions",
        },
    ]
    return {
        "schemaVersion": 1,
        "releaseVersion": release_version,
        "status": "pass" if stable_v4_release else "review",
        "primaryDecision": primary,
        "summary": (
            f"ShipGuard {release_version} can be announced from the current public release."
            if stable_v4_release
            else f"ShipGuard {release_version} is not ready for stable-v4 announcement; next action: {primary}."
        ),
        "latestGitHubReleaseVersion": public_release_delta_proof.get("latestGitHubReleaseVersion") or "",
        "selectedGitHubReleaseTag": public_release_delta_proof.get("selectedGitHubReleaseTag") or "",
        "latestGitHubReleaseTag": public_release_delta_proof.get("latestGitHubReleaseTag") or "",
        "unpublishedLocalDelta": unpublished_delta,
        "stableV4Release": stable_v4_release,
        "currentPublicReleaseCanBeAnnounced": stable_v4_release and public_release_delta_proof.get("stableV4ClaimCoversSelectedPublicRelease") is True,
        "localMainCanBeAnnounced": stable_v4_release and public_release_delta_proof.get("stableV4ClaimCoversLocalCheckout") is True,
        "requiredActions": actions,
        "nextCommand": str(final_claim_packet.get("nextCommand") or rerun_command),
        "visibilityBoundary": {
            "doesNotPublishRelease": True,
            "doesNotEditGitHubRelease": True,
            "doesNotPostExternally": True,
            "latestPublicGitHubReleaseIsPublicationTruth": True,
            "localHeadIsNotPublicationProof": True,
            "localMainIsNotPublicationProof": True,
            "unpublishedLocalCodeCountsAsReleased": False,
        },
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
        "publicReleaseFreshnessProof": "public-release-freshness",
        "releaseVersionCoherenceProof": "release-version-coherence",
        "releaseAssetCoherenceProof": "release-asset-coherence",
        "externalAdoptionEvidenceStableGate": "independent-adoption-evidence",
        "securityReviewEvidenceStableGate": "final-security-review-evidence",
    }
    return mapping.get(receipt, re.sub(r"[^a-z0-9]+", "-", receipt.lower()).strip("-"))


def evidence_label_for_receipt(receipt: str) -> str:
    mapping = {
        "githubReleaseMetadataProof": "GitHub release metadata",
        "releaseNotesProof": "release notes",
        "releaseCandidatePacketProof": "LaunchKey candidate proof",
        "publishedReleaseAssetProof": "downloaded release assets",
        "postReleaseConsumerProof": "post-release consumer proof",
        "publicReleaseFreshnessProof": "public release freshness",
        "releaseVersionCoherenceProof": "release version coherence",
        "releaseAssetCoherenceProof": "release asset coherence",
        "externalAdoptionEvidenceStableGate": "independent adoption evidence",
        "securityReviewEvidenceStableGate": "final security-review evidence",
    }
    return mapping.get(receipt, evidence_id_for_receipt(receipt).replace("-", " "))


def proof_boundary_for_evidence_id(evidence_id: str) -> str:
    mapping = {
        "github-release-metadata": "Public GitHub release metadata must exist for the requested tag and must not be draft-only or prerelease-only proof.",
        "release-notes": "Public release notes must describe the stable-v4 proof packet, downloaded assets, consumer proof, adoption evidence, security review, and non-claims.",
        "launchkey-candidate-packet": "LaunchKey candidate proof must pass before stable publication; package install, upgrade, rollback, release-asset, adoption, and security receipts cannot be inferred.",
        "downloaded-release-assets": "Release assets must be downloaded or supplied and verified from the publication packet, not assumed from source state.",
        "post-release-consumer-proof": "Post-release consumer proof must come from release-consume verification of the downloaded or supplied assets.",
        "public-release-freshness": "Public release freshness must prove the GitHub tag target, release manifest commit, release metadata, and downloaded/supplied assets all describe the same release.",
        "release-version-coherence": "VERSION, requested release version, public tag, release manifest, package proof, and consumer proof must all name the same release.",
        "release-asset-coherence": "Release asset names and SHA-256 values must match across GitHub metadata, downloaded/supplied assets, release manifest, digest matrix, and consumer proof.",
        "independent-adoption-evidence": "Independent adoption evidence must be real public or private-redacted evidence; GitHub download counts and maintainer-only runs do not count.",
        "final-security-review-evidence": "Final security review evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings.",
    }
    return mapping.get(evidence_id, "This stable-v4 evidence input must pass from real reviewed proof before stable publication can be claimed.")


def evidence_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {
        "status": proof.get("status"),
        "stableV4GateStatus": proof.get("stableV4GateStatus") or proof.get("status"),
        "provided": proof.get("provided") is True,
        "summary": proof.get("summary") or "",
        "error": proof.get("error") or "",
        "evidenceInputs": proof.get("evidenceInputs") if isinstance(proof.get("evidenceInputs"), list) else [],
        "collectionErrors": proof.get("collectionErrors") if isinstance(proof.get("collectionErrors"), list) else [],
        "recordCount": proof.get("evidenceRecordCount"),
        "validRecordCount": proof.get("validRecordCount"),
        "invalidRecordCount": proof.get("invalidRecordCount"),
        "stableV4EligibleEvidenceCount": proof.get("stableV4EligibleEvidenceCount"),
    }
    if isinstance(proof.get("evidencePacketFreshness"), dict):
        diagnostics["evidencePacketFreshness"] = proof.get("evidencePacketFreshness")
    if isinstance(proof.get("requiredScope"), list):
        diagnostics["requiredScope"] = proof.get("requiredScope")
    records = proof.get("records") if isinstance(proof.get("records"), list) else []
    if records:
        first = records[0] if isinstance(records[0], dict) else {}
        diagnostics["firstRecord"] = {
            "path": first.get("path"),
            "status": first.get("status"),
            "stableV4Eligible": first.get("stableV4Eligible") is True,
            "missingFields": first.get("missingFields") if isinstance(first.get("missingFields"), list) else [],
            "errors": first.get("errors") if isinstance(first.get("errors"), list) else [],
            "missingStableScope": first.get("missingStableScope") if isinstance(first.get("missingStableScope"), list) else [],
            "stableV4Reason": first.get("stableV4Reason") or "",
        }
    return diagnostics


def build_external_evidence_freshness(
    proof: dict[str, Any],
    *,
    evidence_id: str,
    metadata_proof: dict[str, Any],
    release_freshness_proof: dict[str, Any],
) -> dict[str, Any]:
    reference = (
        release_freshness_proof.get("manifestGeneratedAt")
        or metadata_proof.get("publishedAt")
        or ""
    )
    reference_at = parse_utc_datetime(reference)
    records = proof.get("records") if isinstance(proof.get("records"), list) else []
    stable_records = [record for record in records if isinstance(record, dict) and record.get("stableV4Eligible")]
    rows: list[dict[str, Any]] = []
    problems: list[str] = []

    for record in stable_records:
        generated = str(record.get("generatedAt") or "")
        generated_at = parse_utc_datetime(generated)
        fresh = bool(reference_at and generated_at and generated_at >= reference_at)
        rows.append(
            {
                "path": record.get("path") or "",
                "generatedAt": generated,
                "generatedAtValid": generated_at is not None,
                "noEarlierThanReleaseManifest": fresh,
            }
        )
        if generated_at is None:
            problems.append(f"{evidence_id} record has an invalid generatedAt timestamp.")
        elif reference_at and generated_at < reference_at:
            problems.append(f"{evidence_id} record predates the release manifest timestamp.")

    if not records:
        status = "not-provided"
        problems.append(f"{evidence_id} has no evidence records.")
    elif (proof.get("stableV4GateStatus") or proof.get("status")) != "pass":
        status = str(proof.get("stableV4GateStatus") or proof.get("status") or "review")
        problems.append(f"{evidence_id} stable-v4 gate must pass before freshness can pass.")
    elif not reference_at:
        status = "review"
        problems.append("release manifest or public release timestamp is missing or invalid.")
    elif not stable_records:
        status = "review"
        problems.append(f"{evidence_id} has no stable-v4 eligible records to freshness-check.")
    else:
        status = "pass" if not problems else "review"

    return {
        "schemaVersion": 1,
        "evidenceId": evidence_id,
        "status": status,
        "referenceTimestamp": reference,
        "referenceSource": "release-manifest.generatedAt" if release_freshness_proof.get("manifestGeneratedAt") else "github-release.publishedAt",
        "stableRecordCount": len(stable_records),
        "freshStableRecordCount": sum(1 for row in rows if row.get("noEarlierThanReleaseManifest") is True),
        "staleStableRecordCount": sum(1 for row in rows if row.get("noEarlierThanReleaseManifest") is False),
        "records": rows,
        "problems": problems,
        "freshnessBoundary": {
            "generatedAtMustBeNoEarlierThanReleaseManifest": True,
            "sourceOnlyProofRefreshesExternalEvidence": False,
            "fixtureProofRefreshesExternalEvidence": False,
            "localPackageProofRefreshesExternalEvidence": False,
        },
    }


def attach_external_evidence_freshness(
    proof: dict[str, Any],
    *,
    evidence_id: str,
    metadata_proof: dict[str, Any],
    release_freshness_proof: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(proof)
    freshness = build_external_evidence_freshness(
        proof,
        evidence_id=evidence_id,
        metadata_proof=metadata_proof,
        release_freshness_proof=release_freshness_proof,
    )
    updated["evidencePacketFreshness"] = freshness
    if proof.get("stableV4GateStatus") == "pass" and freshness.get("status") != "pass":
        updated["stableV4GateStatus"] = "review"
        updated["summary"] = f"{proof.get('summary', '').rstrip()} Evidence freshness must pass for this release."
        if freshness.get("problems"):
            updated["freshnessError"] = freshness["problems"][0]
    return updated


def build_public_evidence_closure_proof(
    *,
    release_version: str,
    adoption_proof: dict[str, Any],
    security_proof: dict[str, Any],
    evidence_templates: dict[str, Any],
    evidence_starter_kit: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    templates = {
        str(item.get("id")): item
        for item in evidence_templates.get("templates", [])
        if isinstance(item, dict)
    }
    starter_files = {
        "independent-adoption-evidence": "stable-publication-evidence-kit/external-adoption-evidence.json",
        "final-security-review-evidence": "stable-publication-evidence-kit/security-review-evidence.json",
    }
    proof_pairs = [
        ("independent-adoption-evidence", adoption_proof),
        ("final-security-review-evidence", security_proof),
    ]
    rows: list[dict[str, Any]] = []
    problems: list[str] = []
    for evidence_id, proof in proof_pairs:
        template = templates.get(evidence_id, {})
        freshness = proof.get("evidencePacketFreshness") if isinstance(proof.get("evidencePacketFreshness"), dict) else {}
        gate_status = str(proof.get("stableV4GateStatus") or proof.get("status") or "not-provided")
        freshness_status = str(freshness.get("status") or "not-provided")
        row = {
            "id": evidence_id,
            "status": "pass" if gate_status == "pass" and freshness_status == "pass" else "review",
            "provided": proof.get("provided") is True,
            "stableV4GateStatus": gate_status,
            "freshnessStatus": freshness_status,
            "stableV4EligibleEvidenceCount": proof.get("stableV4EligibleEvidenceCount") or 0,
            "freshStableRecordCount": freshness.get("freshStableRecordCount") or 0,
            "staleStableRecordCount": freshness.get("staleStableRecordCount") or 0,
            "starterPath": starter_files[evidence_id],
            "templatePath": template.get("path") or "",
            "copyCommand": template.get("copyCommand") or "",
            "attachArgument": (
                "--external-adoption-evidence"
                if evidence_id == "independent-adoption-evidence"
                else "--security-review-evidence"
            ),
            "copyReadyNextCommand": rerun_command,
        }
        if row["status"] != "pass":
            problems.append(f"{evidence_id} needs passing real evidence and freshness proof.")
        rows.append(row)

    return {
        "schemaVersion": 1,
        "releaseVersion": release_version,
        "status": "pass" if not problems else "review",
        "requiredForStableV4": True,
        "summary": (
            "Independent adoption and final security-review evidence are present, fresh for this release, and claim-bounded."
            if not problems
            else "Independent adoption or final security-review evidence still needs real, fresh, claim-bounded proof."
        ),
        "evidenceRows": rows,
        "missingOrBlockingEvidenceIds": [row["id"] for row in rows if row["status"] != "pass"],
        "starterKitDirectory": evidence_starter_kit.get("directory") or "stable-publication-evidence-kit",
        "rerunCommand": rerun_command,
        "copyReadyCommands": [
            row["copyCommand"]
            for row in rows
            if row.get("copyCommand")
        ] + [rerun_command],
        "problems": problems,
        "publicEvidenceBoundary": {
            "realExternalAdoptionEvidenceRequired": True,
            "finalSecurityReviewEvidenceRequired": True,
            "generatedAtMustBeNoEarlierThanReleaseManifest": True,
            "privateEvidenceMustBeRedacted": True,
            "githubDownloadCountsCountAsAdoptionEvidence": False,
            "fixtureEvidenceCountsAsStableV4Evidence": False,
            "sourceOnlyProofCountsAsPublicEvidence": False,
            "doesNotClaimMarketplaceAcceptance": True,
            "doesNotPostOrSubmitExternally": True,
        },
        "nonClaims": [
            "GitHub stars, forks, or download counts are not independent adoption evidence.",
            "Fixture adoption or security records prove the tool path only.",
            "Security-review evidence does not imply marketplace acceptance.",
            "Private app evidence must stay redacted before shareable publication proof.",
        ],
    }


def build_final_stable_v4_claim_packet(
    *,
    release_version: str,
    stable_v4_release: bool,
    evidence_packet: dict[str, Any],
    public_evidence_closure_proof: dict[str, Any],
    launch_relay_drafts: dict[str, Any],
    public_release_delta_proof: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    required = evidence_packet.get("requiredEvidence") if isinstance(evidence_packet.get("requiredEvidence"), list) else []
    first_blocker = evidence_packet.get("firstBlockingGate") if isinstance(evidence_packet.get("firstBlockingGate"), dict) else {}
    missing_ids = evidence_packet.get("missingEvidenceIds") if isinstance(evidence_packet.get("missingEvidenceIds"), list) else []
    passed = int(evidence_packet.get("passedEvidenceCount") or 0)
    total = int(evidence_packet.get("requiredEvidenceCount") or len(required))
    first_blocker_id = str(first_blocker.get("id") or first_blocker.get("receipt") or "none")
    first_blocker_next_command = str(first_blocker.get("nextCommand") or "").strip()
    next_command = (
        first_blocker_next_command
        if first_blocker_next_command and first_blocker_next_command not in {"not-needed", "blocked-by-required-actions"}
        else rerun_command
    )
    claim_status = "allowed" if stable_v4_release else "blocked"
    delta_boundary = public_release_delta_proof.get("releaseDeltaBoundary") if isinstance(public_release_delta_proof.get("releaseDeltaBoundary"), dict) else {}
    public_delta_summary = {
        "status": public_release_delta_proof.get("status") or "not-provided",
        "selectedGitHubReleaseTag": public_release_delta_proof.get("selectedGitHubReleaseTag") or "",
        "selectedPublicReleaseCommit": public_release_delta_proof.get("selectedPublicReleaseCommit") or "",
        "localHeadCommit": public_release_delta_proof.get("localHeadCommit") or "",
        "localMainCommit": public_release_delta_proof.get("localMainCommit") or "",
        "unpublishedLocalDelta": public_release_delta_proof.get("unpublishedLocalDelta") is True,
        "stableV4ClaimCoversSelectedPublicRelease": public_release_delta_proof.get("stableV4ClaimCoversSelectedPublicRelease") is True,
        "stableV4ClaimCoversLocalCheckout": public_release_delta_proof.get("stableV4ClaimCoversLocalCheckout") is True,
        "unpublishedLocalCodeCountsAsReleased": delta_boundary.get("unpublishedLocalCodeCountsAsReleased") is True,
        "localHeadIsNotPublicReleaseProof": delta_boundary.get("localHeadIsNotPublicReleaseProof") is True,
        "localMainIsNotPublicReleaseProof": delta_boundary.get("localMainIsNotPublicReleaseProof") is True,
        "problems": public_release_delta_proof.get("problems") if isinstance(public_release_delta_proof.get("problems"), list) else [],
    }
    local_delta_note = (
        " Local checkout has unpublished changes; do not describe local main as released until a new public release passes."
        if public_delta_summary["unpublishedLocalDelta"]
        else ""
    )
    copy_ready_claim = (
        f"ShipGuard {release_version} has passed stable-v4 publication proof: public release metadata, release notes, "
        "downloaded release assets, post-release consumer proof, independent adoption evidence, and final security review all passed."
        f"{local_delta_note}"
        if stable_v4_release
        else f"Do not claim ShipGuard {release_version} as stable v4 yet. Stable-publication is {passed}/{total}; first blocker: {first_blocker_id}.{local_delta_note}"
    )
    claim_publication_readiness = {
        "status": "pass" if stable_v4_release else "blocked",
        "stableV4ClaimMayBePublished": stable_v4_release,
        "firstBlockingGateId": "none" if stable_v4_release else first_blocker_id,
        "requiredEvidencePassed": passed,
        "requiredEvidenceTotal": total,
        "nextCommand": "" if stable_v4_release else next_command,
        "explicitHumanApprovalRequiredForPosting": True,
        "computerUseMayPost": False,
    }
    return {
        "schemaVersion": 1,
        "releaseVersion": release_version,
        "status": claim_status,
        "stableV4Release": stable_v4_release,
        "claimDecision": claim_status,
        "claimPublicationReadiness": claim_publication_readiness,
        "copyReadyClaim": copy_ready_claim,
        "allowedClaims": (
            [
                "Stable-v4 publication proof passed.",
                "The attached report is the local proof source for the stable-v4 claim.",
                "Release metadata, release notes, downloaded assets, consumer proof, adoption evidence, and security evidence passed.",
            ]
            if stable_v4_release
            else []
        ),
        "blockedClaims": [
            claim
            for claim in [
                "ShipGuard v4 is stable." if not stable_v4_release else "",
                "OpenAI marketplace acceptance is proven.",
                "Public launch posts were published or submitted.",
                "GitHub stars, forks, or downloads prove independent adoption.",
                "Fixture, source-only, or local package proof proves stable-v4 publication.",
                "Private app evidence can be shared without redaction.",
            ]
            if claim
        ],
        "evidenceSummary": [
            {
                "id": str(item.get("id") or ""),
                "status": str(item.get("status") or "not-provided"),
                "requiredForStableV4": item.get("requiredForStableV4") is True,
                "nextCommand": str(item.get("nextCommand") or ""),
            }
            for item in required
            if isinstance(item, dict)
        ],
        "missingEvidenceIds": missing_ids,
        "firstBlockingGate": first_blocker or None,
        "publicEvidenceClosureStatus": public_evidence_closure_proof.get("status") or "not-provided",
        "publicReleaseDeltaSummary": public_delta_summary,
        "nextCommand": next_command,
        "approvalBoundary": {
            "publicPostingRequiresExplicitApproval": True,
            "computerUseMayPost": False,
            "launchRelayStatus": launch_relay_drafts.get("status") or "not-provided",
        },
        "claimBoundary": {
            "stablePublicationReportRequired": True,
            "allRequiredEvidenceMustPass": True,
            "sourceOnlyProofCountsAsStableV4": False,
            "fixtureProofCountsAsStableV4": False,
            "githubDownloadCountsCountAsAdoptionEvidence": False,
            "marketplaceAcceptanceClaimed": False,
            "externalPostingClaimed": False,
        },
    }


def launchkey_candidate_proof_areas_for_closure(proof: dict[str, Any]) -> list[dict[str, Any]]:
    statuses = proof.get("candidateReadinessStatuses")
    if not isinstance(statuses, dict):
        statuses = proof.get("requiredStatuses") if isinstance(proof.get("requiredStatuses"), dict) else {}
    areas: list[dict[str, Any]] = []
    for spec in LAUNCHKEY_REQUIRED_PROOF_AREAS:
        receipt = str(spec["receipt"])
        status = str(statuses.get(receipt) or "not-reported")
        areas.append(
            {
                **spec,
                "status": status,
                "passed": status == "pass",
                "missingOrBlocking": status not in {"pass", "not-requested"},
            }
        )
    return areas


def package_hygiene_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    hygiene = proof.get("packageHygieneEvidence")
    if not isinstance(hygiene, dict):
        blocker = proof.get("launchKeyBlockingProof") if isinstance(proof.get("launchKeyBlockingProof"), dict) else {}
        hygiene = blocker.get("packageHygieneEvidence")
    if not isinstance(hygiene, dict):
        return {}
    first_finding = hygiene.get("firstFinding") if isinstance(hygiene.get("firstFinding"), dict) else {}
    return {
        "status": hygiene.get("status"),
        "tool": hygiene.get("tool"),
        "readOnly": hygiene.get("readOnly") is True,
        "blockedFindingCount": hygiene.get("blockedFindingCount"),
        "reviewFindingCount": hygiene.get("reviewFindingCount"),
        "affectedVersions": hygiene.get("affectedVersions") if isinstance(hygiene.get("affectedVersions"), list) else [],
        "safeTarballs": hygiene.get("safeTarballs") if isinstance(hygiene.get("safeTarballs"), list) else [],
        "tarballsScanned": hygiene.get("tarballsScanned"),
        "firstFinding": first_finding,
        "nextCommand": hygiene.get("nextCommand") or "",
    }


def launchkey_candidate_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    blocker = proof.get("launchKeyBlockingProof") if isinstance(proof.get("launchKeyBlockingProof"), dict) else {}
    required_statuses = proof.get("requiredStatuses") if isinstance(proof.get("requiredStatuses"), dict) else {}
    missing_package = proof.get("missingPackageProof") if isinstance(proof.get("missingPackageProof"), list) else []
    nested_receipt = str(blocker.get("receipt") or (missing_package[0] if missing_package else ""))
    if not nested_receipt and proof.get("status") != "pass":
        nested_receipt = "releaseCandidatePacketProof"
    nested_status = str(blocker.get("status") or required_statuses.get(nested_receipt) or proof.get("status") or "")
    nested_summary = str(
        blocker.get("summary")
        or blocker.get("failure")
        or proof.get("summary")
        or (f"{nested_receipt} is {nested_status}." if nested_receipt else "")
    )
    package_hygiene = package_hygiene_diagnostics_for_closure(proof)
    nested_blocking_proof = dict(blocker) if blocker else {}
    if nested_receipt and not nested_blocking_proof:
        nested_blocking_proof = {
            "receipt": nested_receipt,
            "status": nested_status,
            "summary": nested_summary,
            "proofSource": "releaseReadiness",
        }
    return {
        "status": proof.get("status"),
        "provided": proof.get("provided") is True,
        "reportPath": proof.get("reportPath") or "",
        "tool": proof.get("tool") or "",
        "reportStatus": proof.get("reportStatus") or "",
        "releaseClaim": proof.get("releaseClaim") or "",
        "stableV4ReleaseClaimed": proof.get("stableV4ReleaseClaimed"),
        "requiredStatuses": required_statuses,
        "candidateReadinessStatuses": proof.get("candidateReadinessStatuses") if isinstance(proof.get("candidateReadinessStatuses"), dict) else {},
        "missingPackageProof": missing_package,
        "summary": proof.get("summary") or "",
        "error": proof.get("error") or "",
        "nestedBlockingReceipt": nested_receipt,
        "nestedBlockingStatus": nested_status,
        "nestedBlockingSummary": nested_summary,
        "nestedBlockingProof": nested_blocking_proof,
        "requiredLaunchKeyProofAreas": launchkey_candidate_proof_areas_for_closure(proof),
        "packageHygieneDiagnostics": package_hygiene,
        "nestedRerunCommand": str(blocker.get("nextCommand") or package_hygiene.get("nextCommand") or proof.get("nextCommand") or ""),
    }


def github_release_metadata_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": proof.get("status"),
        "provided": proof.get("provided") is True,
        "summary": proof.get("summary") or "",
        "error": proof.get("error") or "",
        "repo": proof.get("repo") or "",
        "repoInference": proof.get("repoInference") if isinstance(proof.get("repoInference"), dict) else {},
        "version": proof.get("version") or "",
        "tag": proof.get("tag") or "",
        "metadataTagName": proof.get("metadataTagName") or "",
        "apiUrl": proof.get("apiUrl") or "",
        "releaseEndpoint": proof.get("releaseEndpoint") or "",
        "releaseUrl": proof.get("releaseUrl") or "",
        "publishedAt": proof.get("publishedAt") or "",
        "targetCommitish": proof.get("targetCommitish") or "",
        "githubTagTargetProof": proof.get("githubTagTargetProof") if isinstance(proof.get("githubTagTargetProof"), dict) else {},
        "tagRefEndpoint": proof.get("tagRefEndpoint") or "",
        "tagObjectSha": proof.get("tagObjectSha") or "",
        "tagObjectType": proof.get("tagObjectType") or "",
        "tagTargetSha": proof.get("tagTargetSha") or "",
        "tagTargetType": proof.get("tagTargetType") or "",
        "assetCount": proof.get("assetCount"),
        "assetNames": proof.get("assetNames") if isinstance(proof.get("assetNames"), list) else [],
        "missingAssets": proof.get("missingAssets") if isinstance(proof.get("missingAssets"), list) else [],
        "requiredAssets": proof.get("requiredAssets") if isinstance(proof.get("requiredAssets"), list) else [],
        "releaseNotesLength": proof.get("releaseNotesLength", 0),
        "releaseNotesLineCount": proof.get("releaseNotesLineCount", 0),
        "releaseNotesSha256": proof.get("releaseNotesSha256") or "",
        "releaseNotesMissingTopicIds": proof.get("releaseNotesMissingTopicIds") if isinstance(proof.get("releaseNotesMissingTopicIds"), list) else [],
        "isDraft": proof.get("isDraft") is True,
        "isPrerelease": proof.get("isPrerelease") is True,
        "nextCommand": proof.get("nextCommand") or "",
    }


def build_github_release_metadata_closure_kit(
    *,
    item: dict[str, Any],
    rerun_command: str,
    notes_file: str | Path | None = None,
    assets_dir: str | Path | None = None,
) -> dict[str, Any]:
    diagnostics = (
        item.get("githubReleaseMetadataDiagnostics")
        if isinstance(item.get("githubReleaseMetadataDiagnostics"), dict)
        else {}
    )
    metadata_rerun = rerun_command or diagnostics.get("nextCommand") or item.get("nextCommand") or (
        "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
        "--github-release-repo <owner/repo> --release-version <version> "
        "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
        "--external-adoption-evidence <adoption-evidence-json-or-dir> "
        "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
    )
    if "stable-publication" not in metadata_rerun:
        metadata_rerun = (
            "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
            "--github-release-repo <owner/repo> --release-version <version> "
            "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
            "--external-adoption-evidence <adoption-evidence-json-or-dir> "
            "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
        )
    release_create = github_release_create_handoff(diagnostics, notes_file=notes_file, assets_dir=assets_dir)
    post_handoff_proof = public_release_post_handoff_proof(
        manual_action="create-github-release",
        repo=str(release_create["inputs"].get("repo") or diagnostics.get("repo") or "<owner/repo>"),
        tag=str(release_create["inputs"].get("tag") or diagnostics.get("tag") or "v<version>"),
        rerun_command=metadata_rerun,
    )
    return {
        "schemaVersion": 1,
        "title": "GitHub release metadata closure kit",
        "status": diagnostics.get("status") or item.get("status") or "not-provided",
        "summary": diagnostics.get("summary") or item.get("summary") or "",
        "repo": diagnostics.get("repo") or "",
        "repoInference": diagnostics.get("repoInference") if isinstance(diagnostics.get("repoInference"), dict) else {},
        "version": diagnostics.get("version") or "",
        "tag": diagnostics.get("tag") or "",
        "metadataTagName": diagnostics.get("metadataTagName") or "",
        "apiUrl": diagnostics.get("apiUrl") or "",
        "releaseEndpoint": diagnostics.get("releaseEndpoint") or "",
        "releaseUrl": diagnostics.get("releaseUrl") or "",
        "publishedAt": diagnostics.get("publishedAt") or "",
        "targetCommitish": diagnostics.get("targetCommitish") or "",
        "tagRefEndpoint": diagnostics.get("tagRefEndpoint") or "",
        "tagObjectSha": diagnostics.get("tagObjectSha") or "",
        "tagObjectType": diagnostics.get("tagObjectType") or "",
        "tagTargetSha": diagnostics.get("tagTargetSha") or "",
        "tagTargetType": diagnostics.get("tagTargetType") or "",
        "requiredAssets": diagnostics.get("requiredAssets") if isinstance(diagnostics.get("requiredAssets"), list) else [],
        "metadataAssetNames": diagnostics.get("assetNames") if isinstance(diagnostics.get("assetNames"), list) else [],
        "metadataMissingAssets": diagnostics.get("missingAssets") if isinstance(diagnostics.get("missingAssets"), list) else [],
        "releaseState": {
            "isDraft": diagnostics.get("isDraft") is True,
            "isPrerelease": diagnostics.get("isPrerelease") is True,
        },
        "releaseNotesSummary": {
            "length": diagnostics.get("releaseNotesLength", 0),
            "lineCount": diagnostics.get("releaseNotesLineCount", 0),
            "sha256": diagnostics.get("releaseNotesSha256") or "",
            "missingTopicIds": diagnostics.get("releaseNotesMissingTopicIds") if isinstance(diagnostics.get("releaseNotesMissingTopicIds"), list) else [],
        },
        "currentMetadataDiagnostics": diagnostics,
        "repairCriteria": GITHUB_RELEASE_METADATA_REPAIR_CRITERIA,
        "passCriteria": GITHUB_RELEASE_METADATA_PASS_CRITERIA,
        "failCriteria": GITHUB_RELEASE_METADATA_FAIL_CRITERIA,
        "metadataRerunCommand": metadata_rerun,
        "releaseCreateCommand": release_create["command"],
        "releaseCreateInputs": release_create["inputs"],
        "releaseCreateCommandBoundary": release_create["boundary"],
        "postHandoffProof": post_handoff_proof,
        "metadataProofBoundary": {
            "publicGitHubReleaseMetadataRequired": True,
            "ownerRepoSyntaxRequired": True,
            "draftOrPrereleaseCountsAsStablePublicationProof": False,
            "sourceOnlyProofCountsAsReleaseMetadataProof": False,
            "fixtureApiProofCountsAsStableV4PublicationProof": False,
            "releaseAssetsStillRequireDownloadedOrSuppliedProof": True,
            "explanation": "The github-release-metadata gate is satisfied only by public release metadata for the selected owner/repo and tag. Source checkout state, local packages, fixture APIs, and generated reports can test ShipGuard routing but do not prove stable-v4 publication.",
        },
    }


def github_release_create_handoff(
    diagnostics: dict[str, Any],
    notes_file: str | Path | None = None,
    assets_dir: str | Path | None = None,
) -> dict[str, Any]:
    repo = str(diagnostics.get("repo") or "<owner/repo>")
    tag = str(diagnostics.get("tag") or "")
    version = str(diagnostics.get("version") or "").strip()
    if not tag:
        tag = f"v{version}" if version else "v<version>"
    if not version and tag.startswith("v") and "<" not in tag:
        version = tag[1:]
    required_assets = diagnostics.get("requiredAssets")
    if not isinstance(required_assets, list) or not required_assets:
        tarball = requested_tarball_name(version or "<version>")
        required_assets = sorted(REQUIRED_RELEASE_ASSETS | {tarball})
    assets_dir_raw = str(assets_dir or "").strip()
    assets_dir_path = Path(assets_dir_raw).expanduser() if assets_dir_raw and "<" not in assets_dir_raw else None
    asset_args = []
    for asset in required_assets:
        name = str(asset)
        if not name:
            continue
        concrete_asset = assets_dir_path / name if assets_dir_path else None
        if concrete_asset and concrete_asset.is_file():
            asset_args.append(concrete_asset.as_posix())
            continue
        if name.startswith("shipguard-v") and name.endswith(".tar.gz"):
            asset_args.append(f"dist/{name}")
        else:
            asset_args.append(f"<release-proof-assets-dir>/{name}")
    notes_file = str(notes_file or "<stable-publication-report-dir>/stable-publication-release-notes/draft-release-notes.md")
    title = f"ShipGuard {tag}"
    command_parts = [
        "gh",
        "release",
        "create",
        tag,
        "--repo",
        repo,
        "--title",
        title,
        "--notes-file",
        notes_file,
        *asset_args,
    ]
    return {
        "command": " ".join(shlex.quote(part) for part in command_parts),
        "inputs": {
            "repo": repo,
            "tag": tag,
            "title": title,
            "notesFile": notes_file,
            "assetsDir": assets_dir_raw,
            "requiredAssets": required_assets,
            "assetArguments": asset_args,
        },
        "boundary": {
            "manualApprovalRequired": True,
            "shipguardPublishesGitHubRelease": False,
            "requiresPassingPackageProof": True,
            "requiresReleaseProofAssets": True,
            "sourceOnlyProofCountsAsPublishedRelease": False,
            "fixtureApiProofCountsAsPublishedRelease": False,
            "explanation": "ShipGuard can prepare the release-create command, but it does not publish GitHub releases. Run the command manually only after the release tarball and proof assets exist.",
        },
    }


def github_release_upload_handoff(
    diagnostics: dict[str, Any],
    assets_dir: str | Path | None = None,
) -> dict[str, Any]:
    repo = str(diagnostics.get("repo") or "<owner/repo>")
    tag = str(diagnostics.get("tag") or "")
    version = str(diagnostics.get("version") or "").strip()
    if not tag:
        tag = f"v{version}" if version else "v<version>"
    if not version and tag.startswith("v") and "<" not in tag:
        version = tag[1:]
    required_assets = diagnostics.get("requiredAssets")
    if not isinstance(required_assets, list) or not required_assets:
        required_assets = sorted(REQUIRED_RELEASE_ASSETS | {requested_tarball_name(version or "<version>")})

    assets_dir_raw = str(assets_dir or "").strip()
    assets_dir_path = Path(assets_dir_raw).expanduser() if assets_dir_raw and "<" not in assets_dir_raw else None
    asset_args = []
    concrete_count = 0
    for asset in required_assets:
        name = str(asset)
        if not name:
            continue
        concrete_asset = assets_dir_path / name if assets_dir_path else None
        if concrete_asset and concrete_asset.is_file():
            asset_args.append(concrete_asset.as_posix())
            concrete_count += 1
        else:
            asset_args.append(f"<release-proof-assets-dir>/{name}")

    command_parts = ["gh", "release", "upload", tag, "--repo", repo, "--clobber", *asset_args]
    return {
        "command": " ".join(shlex.quote(part) for part in command_parts),
        "inputs": {
            "repo": repo,
            "tag": tag,
            "assetsDir": assets_dir_raw,
            "requiredAssets": required_assets,
            "assetArguments": asset_args,
            "concreteAssetCount": concrete_count,
        },
        "boundary": {
            "manualApprovalRequired": True,
            "shipguardUploadsGitHubAssets": False,
            "requiresReleaseProofAssets": True,
            "usesClobber": True,
            "sourceOnlyProofCountsAsPublishedRelease": False,
            "fixtureApiProofCountsAsPublishedRelease": False,
            "explanation": "ShipGuard prepares the release-asset upload command, but it does not upload or replace GitHub release assets.",
        },
    }


def public_release_post_handoff_proof(
    *,
    manual_action: str,
    repo: str,
    tag: str,
    rerun_command: str,
) -> dict[str, Any]:
    release_view_command = " ".join(
        shlex.quote(part)
        for part in [
            "gh",
            "release",
            "view",
            tag or "v<version>",
            "--repo",
            repo or "<owner/repo>",
            "--json",
            "tagName,isDraft,isPrerelease,targetCommitish,publishedAt,assets,url",
        ]
    )
    proof_commands = [release_view_command]
    if rerun_command:
        proof_commands.append(rerun_command)
    return {
        "schemaVersion": 1,
        "manualAction": manual_action,
        "releaseViewCommand": release_view_command,
        "stablePublicationRerunCommand": rerun_command,
        "proofCommands": proof_commands,
        "successCriteria": [
            "The GitHub release exists for the requested tag.",
            "The release is not a draft or prerelease.",
            "Required release-proof assets are visible on the public release.",
            "A fresh stable-publication run moves past this manual handoff gate or passes.",
        ],
        "nonClaims": [
            "The manual GitHub action does not prove stable v4 by itself.",
            "GitHub release metadata still does not prove independent adoption or final security review.",
        ],
    }


def asset_names_from_dir(raw_path: object) -> list[str]:
    if not raw_path:
        return []
    path = Path(str(raw_path)).expanduser()
    try:
        if not path.is_dir():
            return []
        return sorted(child.name for child in path.iterdir() if child.is_file())
    except OSError:
        return []


def release_asset_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    assets_dir = proof.get("assetsDir") or ""
    local_asset_names = asset_names_from_dir(assets_dir)
    return {
        "status": proof.get("status"),
        "provided": proof.get("provided") is True,
        "summary": proof.get("summary") or "",
        "error": proof.get("error") or "",
        "downloadSource": proof.get("downloadSource") or "",
        "downloadProofStatus": proof.get("downloadProofStatus") or "not-provided",
        "version": proof.get("version") or "",
        "assetsDir": assets_dir,
        "consumeOut": proof.get("consumeOut") or "",
        "command": proof.get("command") or "",
        "commandTemplate": proof.get("commandTemplate") or "",
        "nextCommand": proof.get("nextCommand") or "",
        "consumeCommand": proof.get("consumeCommand") or "",
        "exitCode": proof.get("exitCode"),
        "consumerReportStatus": proof.get("consumerReportStatus") or "not-provided",
        "consumerReportPath": proof.get("consumerReportPath") or "",
        "assetDigestMatrixPath": proof.get("assetDigestMatrixPath") or "",
        "assetCount": proof.get("assetCount"),
        "artifactSha256": proof.get("artifactSha256") or "",
        "localAssetNames": local_asset_names,
        "localAssetCount": len(local_asset_names),
    }


def build_release_asset_closure_kit(
    *,
    item: dict[str, Any],
    metadata_proof: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    diagnostics = (
        item.get("releaseAssetDiagnostics")
        if isinstance(item.get("releaseAssetDiagnostics"), dict)
        else {}
    )
    required_assets = metadata_proof.get("requiredAssets") if isinstance(metadata_proof.get("requiredAssets"), list) else []
    metadata_asset_names = metadata_proof.get("assetNames") if isinstance(metadata_proof.get("assetNames"), list) else []
    metadata_missing_assets = metadata_proof.get("missingAssets") if isinstance(metadata_proof.get("missingAssets"), list) else []
    local_asset_names = diagnostics.get("localAssetNames") if isinstance(diagnostics.get("localAssetNames"), list) else []
    if required_assets:
        missing_local_assets = sorted(set(str(name) for name in required_assets) - set(str(name) for name in local_asset_names))
    else:
        missing_local_assets = []
    stable_rerun = rerun_command or item.get("nextCommand") or stable_publication_command(
        argparse.Namespace(
            github_release_repo="<owner/repo>",
            release_version="<version>",
            release_candidate_report="<v4-release-candidate-json-or-dir>",
            release_assets=None,
            external_adoption_evidence=[],
            security_review_evidence=[],
        ),
        placeholders=True,
    )
    download_command = stable_rerun
    if "--download-release-assets" not in download_command and "--release-assets" not in download_command:
        download_command = (
            "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
            "--github-release-repo <owner/repo> --release-version <version> "
            "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
            "--external-adoption-evidence <adoption-evidence-json-or-dir> "
            "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
        )
    upload_handoff = github_release_upload_handoff(metadata_proof, assets_dir=diagnostics.get("assetsDir") or "")
    upload_inputs = upload_handoff["inputs"]
    upload_ready = bool(upload_inputs.get("concreteAssetCount")) and upload_inputs.get("concreteAssetCount") == len(upload_inputs.get("requiredAssets", []))
    post_handoff_proof = public_release_post_handoff_proof(
        manual_action="upload-release-assets",
        repo=str(upload_inputs.get("repo") or metadata_proof.get("repo") or "<owner/repo>"),
        tag=str(upload_inputs.get("tag") or metadata_proof.get("tag") or "v<version>"),
        rerun_command=stable_rerun,
    )
    return {
        "schemaVersion": 1,
        "title": "Release asset proof closure kit",
        "status": diagnostics.get("status") or item.get("status") or "not-provided",
        "summary": diagnostics.get("summary") or item.get("summary") or "",
        "version": diagnostics.get("version") or metadata_proof.get("version") or "",
        "downloadSource": diagnostics.get("downloadSource") or "not-provided",
        "downloadProofStatus": diagnostics.get("downloadProofStatus") or "not-provided",
        "assetsDir": diagnostics.get("assetsDir") or "",
        "consumeOut": diagnostics.get("consumeOut") or "",
        "requiredAssets": required_assets,
        "metadataAssetNames": metadata_asset_names,
        "metadataMissingAssets": metadata_missing_assets,
        "localAssetNames": local_asset_names,
        "missingLocalAssets": missing_local_assets,
        "consumerReportStatus": diagnostics.get("consumerReportStatus") or "not-provided",
        "consumerReportPath": diagnostics.get("consumerReportPath") or "",
        "assetDigestMatrixPath": diagnostics.get("assetDigestMatrixPath") or "",
        "currentReleaseAssetDiagnostics": diagnostics,
        "repairCriteria": RELEASE_ASSET_REPAIR_CRITERIA,
        "passCriteria": RELEASE_ASSET_PASS_CRITERIA,
        "failCriteria": RELEASE_ASSET_FAIL_CRITERIA,
        "downloadAssetsRerunCommand": download_command,
        "releaseAssetUploadCommand": upload_handoff["command"],
        "releaseAssetUploadInputs": upload_inputs,
        "releaseAssetUploadCommandReady": upload_ready,
        "releaseAssetUploadCommandBoundary": upload_handoff["boundary"],
        "postHandoffProof": post_handoff_proof,
        "stablePublicationRerunCommand": stable_rerun,
        "releaseAssetProofBoundary": {
            "downloadedOrSuppliedAssetsRequired": True,
            "githubMetadataOnlyCountsAsReleaseAssetProof": False,
            "sourceOnlyProofCountsAsReleaseAssetProof": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
            "releaseConsumeStillRequiredForConsumerProof": True,
            "explanation": "The downloaded-release-assets gate is satisfied only by the actual published release assets downloaded or supplied to stable-publication. GitHub metadata, source checkout state, local package builds, and fixture assets do not satisfy this gate.",
        },
    }


def build_launchkey_candidate_closure_kit(
    *,
    item: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    diagnostics = (
        item.get("launchKeyCandidateDiagnostics")
        if isinstance(item.get("launchKeyCandidateDiagnostics"), dict)
        else {}
    )
    nested_rerun = str(diagnostics.get("nestedRerunCommand") or item.get("nextCommand") or "")
    return {
        "schemaVersion": 1,
        "title": "LaunchKey candidate packet closure kit",
        "candidateReportPath": diagnostics.get("reportPath") or "",
        "suppliedCandidateReportPath": diagnostics.get("reportPath") or "",
        "nestedBlockingReceipt": diagnostics.get("nestedBlockingReceipt") or "",
        "nestedBlockingStatus": diagnostics.get("nestedBlockingStatus") or "",
        "nestedBlockingSummary": diagnostics.get("nestedBlockingSummary") or "",
        "nestedBlockingProof": diagnostics.get("nestedBlockingProof") if isinstance(diagnostics.get("nestedBlockingProof"), dict) else {},
        "requiredLaunchKeyProofAreas": diagnostics.get("requiredLaunchKeyProofAreas") if isinstance(diagnostics.get("requiredLaunchKeyProofAreas"), list) else [],
        "packageHygieneDiagnostics": diagnostics.get("packageHygieneDiagnostics") if isinstance(diagnostics.get("packageHygieneDiagnostics"), dict) else {},
        "currentCandidateDiagnostics": diagnostics,
        "repairCriteria": LAUNCHKEY_CANDIDATE_REPAIR_CRITERIA,
        "passCriteria": LAUNCHKEY_CANDIDATE_PASS_CRITERIA,
        "failCriteria": LAUNCHKEY_CANDIDATE_FAIL_CRITERIA,
        "nestedRerunCommand": nested_rerun,
        "stablePublicationRerunCommand": rerun_command,
        "fixtureCandidateBoundary": {
            "fixtureCandidateProofAllowedForToolingTests": True,
            "fixtureCandidateProofCountsAsStableV4PublicationProof": False,
            "stablePublicationRequiresRealPublishedReleaseProof": True,
            "doNotPromoteFixtureLaunchKeyProofToStableV4": True,
            "explanation": "LaunchKey fixture reports can test ShipGuard routing. Stable-v4 publication still requires the public release metadata, release notes, downloaded release assets, post-release consumer proof, independent adoption evidence, and final security-review evidence to pass in stable-publication.",
        },
    }


def post_release_consumer_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    missing_artifacts = proof.get("missingProofArtifacts") if isinstance(proof.get("missingProofArtifacts"), list) else []
    return {
        "status": proof.get("status"),
        "provided": proof.get("provided") is True,
        "summary": proof.get("summary") or "",
        "downloadSource": proof.get("downloadSource") or "",
        "downloadProofStatus": proof.get("downloadProofStatus") or "",
        "version": proof.get("version") or "",
        "assetsDir": proof.get("assetsDir") or "",
        "consumeOut": proof.get("consumeOut") or "",
        "command": proof.get("command") or "",
        "consumeCommand": proof.get("consumeCommand") or "",
        "commandTemplate": proof.get("commandTemplate") or "",
        "exitCode": proof.get("exitCode"),
        "error": proof.get("error") or "",
        "stdout": proof.get("stdout") or "",
        "stderr": proof.get("stderr") or "",
        "consumerReportStatus": proof.get("consumerReportStatus") or "not-provided",
        "consumerReportPath": proof.get("consumerReportPath") or "",
        "assetDigestMatrixPath": proof.get("assetDigestMatrixPath") or "",
        "missingProofArtifacts": missing_artifacts,
        "replayStatus": proof.get("replayStatus") or "not-provided",
        "attestationStatus": proof.get("attestationStatus") or "not-provided",
        "artifactSha256": proof.get("artifactSha256") or "",
        "publishedReplayCrosscheck": proof.get("publishedReplayCrosscheck") or "not-provided",
        "publishedAttestationCrosscheck": proof.get("publishedAttestationCrosscheck") or "not-provided",
        "publishedBadgeCrosscheck": proof.get("publishedBadgeCrosscheck") or "not-provided",
        "assetCount": proof.get("assetCount"),
        "consumerDigestFreshness": proof.get("consumerDigestFreshness") if isinstance(proof.get("consumerDigestFreshness"), dict) else {},
        "consumerDigestFreshnessProblems": proof.get("consumerDigestFreshnessProblems") if isinstance(proof.get("consumerDigestFreshnessProblems"), list) else [],
    }


def release_freshness_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": proof.get("status"),
        "provided": proof.get("provided") is True,
        "summary": proof.get("summary") or "",
        "releaseVersion": proof.get("releaseVersion") or "",
        "releaseTag": proof.get("releaseTag") or "",
        "releaseUrl": proof.get("releaseUrl") or "",
        "publishedAt": proof.get("publishedAt") or "",
        "releaseTargetCommitish": proof.get("releaseTargetCommitish") or "",
        "tagRefEndpoint": proof.get("tagRefEndpoint") or "",
        "tagObjectSha": proof.get("tagObjectSha") or "",
        "tagObjectType": proof.get("tagObjectType") or "",
        "tagTargetSha": proof.get("tagTargetSha") or "",
        "tagTargetType": proof.get("tagTargetType") or "",
        "tagTargetProofStatus": proof.get("tagTargetProofStatus") or "not-provided",
        "assetsDir": proof.get("assetsDir") or "",
        "releaseManifestPath": proof.get("releaseManifestPath") or "",
        "manifestVersion": proof.get("manifestVersion") or "",
        "manifestTag": proof.get("manifestTag") or "",
        "manifestCommit": proof.get("manifestCommit") or "",
        "manifestGeneratedAt": proof.get("manifestGeneratedAt") or "",
        "artifactName": proof.get("artifactName") or "",
        "artifactSha256": proof.get("artifactSha256") or "",
        "localHeadCommit": proof.get("localHeadCommit") or "",
        "localTagCommit": proof.get("localTagCommit") or "",
        "comparisons": proof.get("comparisons") if isinstance(proof.get("comparisons"), dict) else {},
        "problems": proof.get("problems") if isinstance(proof.get("problems"), list) else [],
        "nextCommand": proof.get("nextCommand") or "",
    }


def release_version_coherence_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": proof.get("status"),
        "summary": proof.get("summary") or "",
        "sourceVersion": proof.get("sourceVersion") or "",
        "releaseVersion": proof.get("releaseVersion") or "",
        "normalizedReleaseVersion": proof.get("normalizedReleaseVersion") or "",
        "expectedTag": proof.get("expectedTag") or "",
        "metadataTagName": proof.get("metadataTagName") or "",
        "manifestVersion": proof.get("manifestVersion") or "",
        "manifestTag": proof.get("manifestTag") or "",
        "packageVersion": proof.get("packageVersion") or "",
        "consumerReportVersion": proof.get("consumerReportVersion") or "",
        "expectedTarballName": proof.get("expectedTarballName") or "",
        "manifestArtifactName": proof.get("manifestArtifactName") or "",
        "comparisons": proof.get("comparisons") if isinstance(proof.get("comparisons"), dict) else {},
        "problems": proof.get("problems") if isinstance(proof.get("problems"), list) else [],
        "nextCommand": proof.get("nextCommand") or "",
    }


def release_asset_coherence_diagnostics_for_closure(proof: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": proof.get("status"),
        "summary": proof.get("summary") or "",
        "releaseVersion": proof.get("releaseVersion") or "",
        "expectedTarballName": proof.get("expectedTarballName") or "",
        "requiredAssetNames": proof.get("requiredAssetNames") if isinstance(proof.get("requiredAssetNames"), list) else [],
        "metadataAssetNames": proof.get("metadataAssetNames") if isinstance(proof.get("metadataAssetNames"), list) else [],
        "localAssetNames": proof.get("localAssetNames") if isinstance(proof.get("localAssetNames"), list) else [],
        "digestAssetNames": proof.get("digestAssetNames") if isinstance(proof.get("digestAssetNames"), list) else [],
        "missingLocalAssetNames": proof.get("missingLocalAssetNames") if isinstance(proof.get("missingLocalAssetNames"), list) else [],
        "missingDigestAssetNames": proof.get("missingDigestAssetNames") if isinstance(proof.get("missingDigestAssetNames"), list) else [],
        "missingSha256AssetNames": proof.get("missingSha256AssetNames") if isinstance(proof.get("missingSha256AssetNames"), list) else [],
        "manifestArtifactName": proof.get("manifestArtifactName") or "",
        "manifestArtifactSha256": proof.get("manifestArtifactSha256") or "",
        "digestTarballName": proof.get("digestTarballName") or "",
        "digestTarballSha256": proof.get("digestTarballSha256") or "",
        "consumerArtifactSha256": proof.get("consumerArtifactSha256") or "",
        "comparisons": proof.get("comparisons") if isinstance(proof.get("comparisons"), dict) else {},
        "problems": proof.get("problems") if isinstance(proof.get("problems"), list) else [],
        "nextCommand": proof.get("nextCommand") or "",
    }


def build_public_release_freshness_closure_kit(
    *,
    item: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    diagnostics = (
        item.get("releaseFreshnessDiagnostics")
        if isinstance(item.get("releaseFreshnessDiagnostics"), dict)
        else {}
    )
    freshness_rerun = rerun_command or diagnostics.get("nextCommand") or item.get("nextCommand") or (
        "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
        "--github-release-repo <owner/repo> --release-version <version> "
        "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
        "--external-adoption-evidence <adoption-evidence-json-or-dir> "
        "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
    )
    return {
        "schemaVersion": 1,
        "title": "Public release freshness closure kit",
        "status": diagnostics.get("status") or item.get("status") or "not-provided",
        "summary": diagnostics.get("summary") or item.get("summary") or "",
        "releaseVersion": diagnostics.get("releaseVersion") or "",
        "releaseTag": diagnostics.get("releaseTag") or "",
        "releaseUrl": diagnostics.get("releaseUrl") or "",
        "publishedAt": diagnostics.get("publishedAt") or "",
        "releaseTargetCommitish": diagnostics.get("releaseTargetCommitish") or "",
        "tagRefEndpoint": diagnostics.get("tagRefEndpoint") or "",
        "tagObjectSha": diagnostics.get("tagObjectSha") or "",
        "tagObjectType": diagnostics.get("tagObjectType") or "",
        "tagTargetSha": diagnostics.get("tagTargetSha") or "",
        "tagTargetType": diagnostics.get("tagTargetType") or "",
        "tagTargetProofStatus": diagnostics.get("tagTargetProofStatus") or "not-provided",
        "assetsDir": diagnostics.get("assetsDir") or "",
        "releaseManifestPath": diagnostics.get("releaseManifestPath") or "",
        "manifestVersion": diagnostics.get("manifestVersion") or "",
        "manifestTag": diagnostics.get("manifestTag") or "",
        "manifestCommit": diagnostics.get("manifestCommit") or "",
        "manifestGeneratedAt": diagnostics.get("manifestGeneratedAt") or "",
        "artifactName": diagnostics.get("artifactName") or "",
        "artifactSha256": diagnostics.get("artifactSha256") or "",
        "localHeadCommit": diagnostics.get("localHeadCommit") or "",
        "localTagCommit": diagnostics.get("localTagCommit") or "",
        "comparisons": diagnostics.get("comparisons") if isinstance(diagnostics.get("comparisons"), dict) else {},
        "problems": diagnostics.get("problems") if isinstance(diagnostics.get("problems"), list) else [],
        "currentFreshnessDiagnostics": diagnostics,
        "repairCriteria": PUBLIC_RELEASE_FRESHNESS_REPAIR_CRITERIA,
        "passCriteria": PUBLIC_RELEASE_FRESHNESS_PASS_CRITERIA,
        "failCriteria": PUBLIC_RELEASE_FRESHNESS_FAIL_CRITERIA,
        "freshnessRerunCommand": freshness_rerun,
        "freshnessProofBoundary": {
            "publicGitHubTagTargetRequired": True,
            "releaseManifestRequired": True,
            "releaseManifestCommitMustMatchPublicTagTarget": True,
            "targetCommitishBranchNameRequiresTagTargetProof": True,
            "sourceOnlyProofCountsAsFreshnessProof": False,
            "fixtureApiProofCountsAsStableV4PublicationProof": False,
            "localHeadMayBeAheadOfPublishedRelease": True,
            "explanation": "Freshness is satisfied by coherence between the public GitHub release/tag metadata and the downloaded or supplied release manifest. Local source state is context only; source checkout tests, fixture APIs, and local package builds do not prove a published release is fresh.",
        },
    }


def build_post_release_consumer_closure_kit(
    *,
    item: dict[str, Any],
    rerun_command: str,
) -> dict[str, Any]:
    diagnostics = (
        item.get("postReleaseConsumerDiagnostics")
        if isinstance(item.get("postReleaseConsumerDiagnostics"), dict)
        else {}
    )
    release_consume_rerun = (
        str(diagnostics.get("command") or diagnostics.get("consumeCommand") or item.get("nextCommand") or "")
        or "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>"
    )
    return {
        "schemaVersion": 1,
        "title": "Post-release consumer proof closure kit",
        "status": diagnostics.get("status") or item.get("status") or "not-provided",
        "summary": diagnostics.get("summary") or item.get("summary") or "",
        "downloadSource": diagnostics.get("downloadSource") or "",
        "downloadProofStatus": diagnostics.get("downloadProofStatus") or "",
        "version": diagnostics.get("version") or "",
        "assetsDir": diagnostics.get("assetsDir") or "",
        "consumeOut": diagnostics.get("consumeOut") or "",
        "consumerReportStatus": diagnostics.get("consumerReportStatus") or "not-provided",
        "consumerReportPath": diagnostics.get("consumerReportPath") or "",
        "assetDigestMatrixPath": diagnostics.get("assetDigestMatrixPath") or "",
        "missingProofArtifacts": diagnostics.get("missingProofArtifacts") if isinstance(diagnostics.get("missingProofArtifacts"), list) else [],
        "replayStatus": diagnostics.get("replayStatus") or "not-provided",
        "attestationStatus": diagnostics.get("attestationStatus") or "not-provided",
        "artifactSha256": diagnostics.get("artifactSha256") or "",
        "publishedCrosschecks": {
            "replayReport": diagnostics.get("publishedReplayCrosscheck") or "not-provided",
            "attestation": diagnostics.get("publishedAttestationCrosscheck") or "not-provided",
            "attestationBadge": diagnostics.get("publishedBadgeCrosscheck") or "not-provided",
        },
        "assetCount": diagnostics.get("assetCount"),
        "consumerDigestFreshness": diagnostics.get("consumerDigestFreshness") if isinstance(diagnostics.get("consumerDigestFreshness"), dict) else {},
        "consumerDigestFreshnessProblems": diagnostics.get("consumerDigestFreshnessProblems") if isinstance(diagnostics.get("consumerDigestFreshnessProblems"), list) else [],
        "currentConsumerDiagnostics": diagnostics,
        "repairCriteria": POST_RELEASE_CONSUMER_REPAIR_CRITERIA,
        "passCriteria": POST_RELEASE_CONSUMER_PASS_CRITERIA,
        "failCriteria": POST_RELEASE_CONSUMER_FAIL_CRITERIA,
        "releaseConsumeRerunCommand": release_consume_rerun,
        "stablePublicationRerunCommand": rerun_command,
        "consumerProofBoundary": {
            "releaseConsumeRequired": True,
            "downloadedOrSuppliedAssetsRequired": True,
            "assetDigestMatrixMustCoverRequiredAssets": True,
            "releaseTarballDigestMustMatchConsumerArtifact": True,
            "sourceOnlyProofCountsAsConsumerProof": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
            "postReleaseConsumerProofDoesNotProveAdoptionOrSecurity": True,
            "explanation": "Post-release consumer proof is only satisfied by release-consume verification of downloaded or supplied release assets. Source tests, package fixtures, release-note drafts, and GitHub metadata alone are not consumer proof.",
        },
    }


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
        "schemaVersion": 2,
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
                "purpose": "Machine-readable draft checklist with the ten required stable-publication gates.",
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


def attach_release_notes_authoring_kit_to_starter(
    starter_kit: dict[str, Any],
    *,
    release_version: str,
    release_notes_authoring_kit: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(starter_kit)
    related_files = release_notes_authoring_kit.get("files")
    updated["releaseVersion"] = release_version
    updated["relatedAuthoringKits"] = [
        {
            "id": "release-notes-authoring-kit",
            "directory": release_notes_authoring_kit.get("directory") or RELEASE_NOTES_KIT_DIRNAME,
            "status": release_notes_authoring_kit.get("status") or "review",
            "draftOnly": release_notes_authoring_kit.get("draftOnly") is True,
            "missingTopicIds": release_notes_authoring_kit.get("missingTopicIds") if isinstance(release_notes_authoring_kit.get("missingTopicIds"), list) else [],
            "files": related_files if isinstance(related_files, list) else [],
            "nextCommandTemplate": release_notes_authoring_kit.get("nextCommandTemplate") or "",
        }
    ]
    return updated


def build_stable_publication_release_notes_authoring_kit(
    *,
    release_version: str,
    release_notes_proof: dict[str, Any],
    metadata_proof: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    missing_topic_ids = release_notes_proof.get("missingTopicIds")
    if not isinstance(missing_topic_ids, list):
        missing_topic_ids = []
    topic_matrix = release_notes_proof.get("topicMatrix")
    if not isinstance(topic_matrix, list):
        topic_matrix = []
    release_tag = str(metadata_proof.get("tag") or launchkey.normalize_release_tag(release_version))
    release_repo = str(metadata_proof.get("repo") or "<owner/repo>")
    kit_dir = out_dir / RELEASE_NOTES_KIT_DIRNAME
    checklist_path = kit_dir / "release-notes-checklist.json"
    draft_path = kit_dir / "draft-release-notes.md"
    readme_path = kit_dir / "README.md"
    edit_command = public_release_notes_edit_command(
        repo=release_repo,
        tag=release_tag,
        notes_file=draft_path,
    )
    return {
        "schemaVersion": 2,
        "draftOnly": True,
        "directory": RELEASE_NOTES_KIT_DIRNAME,
        "generatedPaths": {
            "checklist": checklist_path.as_posix(),
            "draftReleaseNotes": draft_path.as_posix(),
            "readme": readme_path.as_posix(),
        },
        "releaseVersion": release_version,
        "releaseTag": release_tag,
        "releaseUrl": metadata_proof.get("releaseUrl") or "",
        "status": "pass" if release_notes_proof.get("status") == "pass" else "review",
        "missingTopicIds": missing_topic_ids,
        "topicMatrix": topic_matrix,
        "publicReleaseEditCommand": edit_command,
        "publicGitHubReleaseEditBoundary": {
            "target": "public GitHub release body",
            "releaseUrl": metadata_proof.get("releaseUrl") or "",
            "requiresPublicReleaseEdit": True,
            "shipguardDoesNotEditRelease": True,
            "authoringKitIsDraftOnly": True,
            "stableV4ClaimAllowed": False,
        },
        "files": [
            {
                "id": "checklist",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/release-notes-checklist.json",
                "generatedPath": checklist_path.as_posix(),
                "purpose": "Machine-readable checklist for the stable-publication release-notes topics.",
            },
            {
                "id": "draft-release-notes",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/draft-release-notes.md",
                "generatedPath": draft_path.as_posix(),
                "purpose": "Draft-only release notes section that includes every required stable-publication proof topic.",
            },
            {
                "id": "copy-brief",
                "path": f"{RELEASE_NOTES_KIT_DIRNAME}/README.md",
                "generatedPath": readme_path.as_posix(),
                "purpose": "Human instructions for adapting the draft into the public GitHub release body.",
            },
        ],
        "instructions": [
            "Use this as a release-notes authoring aid only; it is not proof that a GitHub release was published.",
            "Replace placeholders with the real release version, asset list, adoption summary, security review summary, and non-claims before publishing.",
            "Review the generated draft, then run the publicReleaseEditCommand manually to update the public GitHub release body.",
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
        add_launchkey_blocker_to_evidence_item(item, proof)
        template = templates_by_id.get(evidence_id)
        if template:
            item.update(
                {
                    "templateId": template.get("id"),
                    "templatePath": template.get("path"),
                    "templateCommand": template.get("copyCommand"),
                }
            )
        if evidence_id == "github-release-metadata":
            item["githubReleaseMetadataDiagnostics"] = github_release_metadata_diagnostics_for_closure(proof)
        if evidence_id == "launchkey-candidate-packet":
            item["launchKeyCandidateDiagnostics"] = launchkey_candidate_diagnostics_for_closure(proof)
        if evidence_id == "downloaded-release-assets":
            item["releaseAssetDiagnostics"] = release_asset_diagnostics_for_closure(proof)
        if evidence_id == "post-release-consumer-proof":
            item["postReleaseConsumerDiagnostics"] = post_release_consumer_diagnostics_for_closure(proof)
        if evidence_id == "public-release-freshness":
            item["releaseFreshnessDiagnostics"] = release_freshness_diagnostics_for_closure(proof)
        if evidence_id == "release-version-coherence":
            item["releaseVersionCoherenceDiagnostics"] = release_version_coherence_diagnostics_for_closure(proof)
        if evidence_id == "release-asset-coherence":
            item["releaseAssetCoherenceDiagnostics"] = release_asset_coherence_diagnostics_for_closure(proof)
        if evidence_id in {"independent-adoption-evidence", "final-security-review-evidence"}:
            item["evidenceDiagnostics"] = evidence_diagnostics_for_closure(proof)
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
        add_launchkey_blocker_to_evidence_item(first_blocking, proof)

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
            "Confirm the VERSION file, requested release version, GitHub tag, release manifest, package proof, and consumer report name the same release.",
            "Confirm required release assets and SHA-256 values match across metadata, downloaded assets, release manifest, digest matrix, and consumer proof.",
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


def build_stable_publication_closure_checklist(
    *,
    evidence_packet: dict[str, Any],
    release_version: str,
    stable_v4_release: bool,
    evidence_templates: dict[str, Any] | None = None,
    evidence_starter_kit: dict[str, Any] | None = None,
    release_notes_proof: dict[str, Any] | None = None,
    release_notes_authoring_kit: dict[str, Any] | None = None,
    metadata_proof: dict[str, Any] | None = None,
    release_assets_dir: str | Path | None = None,
    rerun_command: str = "",
) -> dict[str, Any]:
    required = evidence_packet.get("requiredEvidence") if isinstance(evidence_packet.get("requiredEvidence"), list) else []
    first_blocking = evidence_packet.get("firstBlockingGate") if isinstance(evidence_packet.get("firstBlockingGate"), dict) else {}
    evidence_templates = evidence_templates if isinstance(evidence_templates, dict) else {}
    evidence_starter_kit = evidence_starter_kit if isinstance(evidence_starter_kit, dict) else {}
    release_notes_proof = release_notes_proof if isinstance(release_notes_proof, dict) else {}
    release_notes_authoring_kit = release_notes_authoring_kit if isinstance(release_notes_authoring_kit, dict) else {}
    metadata_proof = metadata_proof if isinstance(metadata_proof, dict) else {}
    templates_by_id = {
        str(template.get("id")): template
        for template in evidence_templates.get("templates", [])
        if isinstance(template, dict)
    }
    starter_files_by_id = {
        str(file_item.get("id")): file_item
        for file_item in evidence_starter_kit.get("files", [])
        if isinstance(file_item, dict)
    }
    items: list[dict[str, Any]] = []

    for index, item in enumerate(required, start=1):
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "not-provided")
        if status == "pass":
            continue
        evidence_id = str(item.get("id") or evidence_id_for_receipt(str(item.get("receipt") or "")))
        closure_item = {
            "rank": len(items) + 1,
            "dependencyOrder": index,
            "id": evidence_id,
            "receipt": item.get("receipt"),
            "status": status,
            "summary": item.get("summary") or f"{evidence_id} has not passed.",
            "nextCommand": item.get("nextCommand") or first_blocking.get("nextCommand") or "",
            "proofBoundary": proof_boundary_for_evidence_id(evidence_id),
            "blocksStableV4": True,
            "isFirstBlockingGate": evidence_id == first_blocking.get("id"),
        }
        for optional_key in ("templatePath", "templateCommand", "failureEvidence", "blockingProof"):
            if optional_key in item:
                closure_item[optional_key] = item[optional_key]
        if evidence_id == "github-release-metadata":
            generated_paths = release_notes_authoring_kit.get("generatedPaths") if isinstance(release_notes_authoring_kit.get("generatedPaths"), dict) else {}
            metadata_kit = build_github_release_metadata_closure_kit(
                item=item,
                rerun_command=rerun_command
                or (
                    "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
                    "--github-release-repo <owner/repo> --release-version <version> "
                    "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
                    "--external-adoption-evidence <adoption-evidence-json-or-dir> "
                    "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
                ),
                notes_file=generated_paths.get("draftReleaseNotes") or None,
                assets_dir=release_assets_dir,
            )
            closure_item.update(
                {
                    "githubReleaseRepo": metadata_kit.get("repo") or "",
                    "githubReleaseRepoInference": metadata_kit.get("repoInference") if isinstance(metadata_kit.get("repoInference"), dict) else {},
                    "releaseTag": metadata_kit.get("tag") or "",
                    "releaseEndpoint": metadata_kit.get("releaseEndpoint") or "",
                    "releaseUrl": metadata_kit.get("releaseUrl") or "",
                    "targetCommitish": metadata_kit.get("targetCommitish") or "",
                    "tagRefEndpoint": metadata_kit.get("tagRefEndpoint") or "",
                    "tagTargetSha": metadata_kit.get("tagTargetSha") or "",
                    "requiredAssets": metadata_kit.get("requiredAssets") if isinstance(metadata_kit.get("requiredAssets"), list) else [],
                    "metadataAssetNames": metadata_kit.get("metadataAssetNames") if isinstance(metadata_kit.get("metadataAssetNames"), list) else [],
                    "metadataMissingAssets": metadata_kit.get("metadataMissingAssets") if isinstance(metadata_kit.get("metadataMissingAssets"), list) else [],
                    "releaseState": metadata_kit.get("releaseState") if isinstance(metadata_kit.get("releaseState"), dict) else {},
                    "releaseNotesSummary": metadata_kit.get("releaseNotesSummary") if isinstance(metadata_kit.get("releaseNotesSummary"), dict) else {},
                    "metadataRerunCommand": metadata_kit.get("metadataRerunCommand") or item.get("nextCommand") or "",
                    "releaseCreateCommand": metadata_kit.get("releaseCreateCommand") or "",
                    "releaseCreateInputs": metadata_kit.get("releaseCreateInputs") if isinstance(metadata_kit.get("releaseCreateInputs"), dict) else {},
                    "releaseCreateCommandBoundary": metadata_kit.get("releaseCreateCommandBoundary") if isinstance(metadata_kit.get("releaseCreateCommandBoundary"), dict) else {},
                    "postHandoffProof": metadata_kit.get("postHandoffProof") if isinstance(metadata_kit.get("postHandoffProof"), dict) else {},
                    "repairCriteria": metadata_kit.get("repairCriteria") if isinstance(metadata_kit.get("repairCriteria"), list) else [],
                    "passCriteria": metadata_kit.get("passCriteria") if isinstance(metadata_kit.get("passCriteria"), list) else [],
                    "failCriteria": metadata_kit.get("failCriteria") if isinstance(metadata_kit.get("failCriteria"), list) else [],
                    "metadataProofBoundary": metadata_kit.get("metadataProofBoundary") if isinstance(metadata_kit.get("metadataProofBoundary"), dict) else {},
                    "releaseMetadataClosureKit": metadata_kit,
                }
            )
            closure_item["nextCommand"] = closure_item["metadataRerunCommand"]
        if evidence_id == "release-notes":
            kit_files = release_notes_authoring_kit.get("files") if isinstance(release_notes_authoring_kit.get("files"), list) else []
            authoring_paths = [str(file_item.get("path")) for file_item in kit_files if isinstance(file_item, dict) and file_item.get("path")]
            edit_command = str(release_notes_authoring_kit.get("publicReleaseEditCommand") or "")
            closure_item.update(
                {
                    "missingTopicIds": release_notes_proof.get("missingTopicIds") if isinstance(release_notes_proof.get("missingTopicIds"), list) else [],
                    "authoringKitPaths": authoring_paths,
                    "releaseNotesAuthoringKit": {
                        "directory": release_notes_authoring_kit.get("directory"),
                        "draftOnly": release_notes_authoring_kit.get("draftOnly") is True,
                        "readmePath": f"{RELEASE_NOTES_KIT_DIRNAME}/README.md",
                        "checklistPath": f"{RELEASE_NOTES_KIT_DIRNAME}/release-notes-checklist.json",
                        "draftPath": f"{RELEASE_NOTES_KIT_DIRNAME}/draft-release-notes.md",
                        "files": kit_files,
                        "publicReleaseEditCommand": release_notes_authoring_kit.get("publicReleaseEditCommand") or "",
                    },
                    "publicGitHubReleaseEditBoundary": {
                        "target": "public GitHub release body",
                        "releaseUrl": metadata_proof.get("releaseUrl") or "",
                        "requiresPublicReleaseEdit": True,
                        "shipguardDoesNotEditRelease": True,
                        "authoringKitIsDraftOnly": True,
                        "stableV4ClaimAllowed": False,
                        "publicReleaseEditCommand": edit_command,
                        "instruction": "Edit the public GitHub release body with the missing stable-publication topics, then rerun stable-publication against public release metadata.",
                    },
                    "rerunCommand": rerun_command or item.get("nextCommand") or first_blocking.get("nextCommand") or "",
                }
            )
            closure_item["nextCommand"] = edit_command or closure_item["rerunCommand"]
        if evidence_id == "launchkey-candidate-packet":
            candidate_kit = build_launchkey_candidate_closure_kit(
                item=item,
                rerun_command=rerun_command
                or (
                    "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
                    "--github-release-repo <owner/repo> --release-version <version> "
                    "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
                    "--external-adoption-evidence <adoption-evidence-json-or-dir> "
                    "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
                ),
            )
            closure_item.update(
                {
                    "candidateReportPath": candidate_kit.get("candidateReportPath") or "",
                    "suppliedCandidateReportPath": candidate_kit.get("suppliedCandidateReportPath") or "",
                    "nestedBlockingReceipt": candidate_kit.get("nestedBlockingReceipt") or "",
                    "nestedBlockingStatus": candidate_kit.get("nestedBlockingStatus") or "",
                    "nestedBlockingSummary": candidate_kit.get("nestedBlockingSummary") or "",
                    "requiredLaunchKeyProofAreas": candidate_kit.get("requiredLaunchKeyProofAreas") if isinstance(candidate_kit.get("requiredLaunchKeyProofAreas"), list) else [],
                    "packageHygieneDiagnostics": candidate_kit.get("packageHygieneDiagnostics") if isinstance(candidate_kit.get("packageHygieneDiagnostics"), dict) else {},
                    "repairCriteria": candidate_kit.get("repairCriteria") if isinstance(candidate_kit.get("repairCriteria"), list) else [],
                    "passCriteria": candidate_kit.get("passCriteria") if isinstance(candidate_kit.get("passCriteria"), list) else [],
                    "failCriteria": candidate_kit.get("failCriteria") if isinstance(candidate_kit.get("failCriteria"), list) else [],
                    "nestedRerunCommand": candidate_kit.get("nestedRerunCommand") or item.get("nextCommand") or "",
                    "stablePublicationRerunCommand": candidate_kit.get("stablePublicationRerunCommand") or rerun_command,
                    "fixtureCandidateBoundary": candidate_kit.get("fixtureCandidateBoundary") if isinstance(candidate_kit.get("fixtureCandidateBoundary"), dict) else {},
                    "launchKeyCandidateClosureKit": candidate_kit,
                }
            )
            closure_item["nextCommand"] = closure_item["nestedRerunCommand"] or closure_item["stablePublicationRerunCommand"]
        if evidence_id == "downloaded-release-assets":
            asset_kit = build_release_asset_closure_kit(
                item=item,
                metadata_proof=metadata_proof,
                rerun_command=rerun_command
                or (
                    "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
                    "--github-release-repo <owner/repo> --release-version <version> "
                    "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
                    "--external-adoption-evidence <adoption-evidence-json-or-dir> "
                    "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
                ),
            )
            closure_item.update(
                {
                    "assetsDir": asset_kit.get("assetsDir") or "",
                    "requiredAssets": asset_kit.get("requiredAssets") if isinstance(asset_kit.get("requiredAssets"), list) else [],
                    "metadataAssetNames": asset_kit.get("metadataAssetNames") if isinstance(asset_kit.get("metadataAssetNames"), list) else [],
                    "metadataMissingAssets": asset_kit.get("metadataMissingAssets") if isinstance(asset_kit.get("metadataMissingAssets"), list) else [],
                    "localAssetNames": asset_kit.get("localAssetNames") if isinstance(asset_kit.get("localAssetNames"), list) else [],
                    "missingLocalAssets": asset_kit.get("missingLocalAssets") if isinstance(asset_kit.get("missingLocalAssets"), list) else [],
                    "downloadAssetsRerunCommand": asset_kit.get("downloadAssetsRerunCommand") or item.get("nextCommand") or "",
                    "releaseAssetUploadCommand": asset_kit.get("releaseAssetUploadCommand") or "",
                    "releaseAssetUploadCommandReady": asset_kit.get("releaseAssetUploadCommandReady") is True,
                    "releaseAssetUploadCommandBoundary": asset_kit.get("releaseAssetUploadCommandBoundary") if isinstance(asset_kit.get("releaseAssetUploadCommandBoundary"), dict) else {},
                    "postHandoffProof": asset_kit.get("postHandoffProof") if isinstance(asset_kit.get("postHandoffProof"), dict) else {},
                    "stablePublicationRerunCommand": asset_kit.get("stablePublicationRerunCommand") or rerun_command,
                    "repairCriteria": asset_kit.get("repairCriteria") if isinstance(asset_kit.get("repairCriteria"), list) else [],
                    "passCriteria": asset_kit.get("passCriteria") if isinstance(asset_kit.get("passCriteria"), list) else [],
                    "failCriteria": asset_kit.get("failCriteria") if isinstance(asset_kit.get("failCriteria"), list) else [],
                    "releaseAssetProofBoundary": asset_kit.get("releaseAssetProofBoundary") if isinstance(asset_kit.get("releaseAssetProofBoundary"), dict) else {},
                    "releaseAssetClosureKit": asset_kit,
                }
            )
            closure_item["nextCommand"] = closure_item["downloadAssetsRerunCommand"] or closure_item["stablePublicationRerunCommand"]
        if evidence_id == "post-release-consumer-proof":
            consumer_kit = build_post_release_consumer_closure_kit(
                item=item,
                rerun_command=rerun_command
                or (
                    "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
                    "--github-release-repo <owner/repo> --release-version <version> "
                    "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
                    "--external-adoption-evidence <adoption-evidence-json-or-dir> "
                    "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
                ),
            )
            closure_item.update(
                {
                    "consumerReportStatus": consumer_kit.get("consumerReportStatus") or "not-provided",
                    "consumerReportPath": consumer_kit.get("consumerReportPath") or "",
                    "assetDigestMatrixPath": consumer_kit.get("assetDigestMatrixPath") or "",
                    "missingProofArtifacts": consumer_kit.get("missingProofArtifacts") if isinstance(consumer_kit.get("missingProofArtifacts"), list) else [],
                    "releaseConsumeRerunCommand": consumer_kit.get("releaseConsumeRerunCommand") or item.get("nextCommand") or "",
                    "stablePublicationRerunCommand": consumer_kit.get("stablePublicationRerunCommand") or rerun_command,
                    "repairCriteria": consumer_kit.get("repairCriteria") if isinstance(consumer_kit.get("repairCriteria"), list) else [],
                    "passCriteria": consumer_kit.get("passCriteria") if isinstance(consumer_kit.get("passCriteria"), list) else [],
                    "failCriteria": consumer_kit.get("failCriteria") if isinstance(consumer_kit.get("failCriteria"), list) else [],
                    "consumerProofBoundary": consumer_kit.get("consumerProofBoundary") if isinstance(consumer_kit.get("consumerProofBoundary"), dict) else {},
                    "postReleaseConsumerClosureKit": consumer_kit,
                }
            )
            closure_item["nextCommand"] = closure_item["releaseConsumeRerunCommand"] or closure_item["stablePublicationRerunCommand"]
        if evidence_id == "public-release-freshness":
            freshness_kit = build_public_release_freshness_closure_kit(
                item=item,
                rerun_command=rerun_command
                or (
                    "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> "
                    "--github-release-repo <owner/repo> --release-version <version> "
                    "--release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets "
                    "--external-adoption-evidence <adoption-evidence-json-or-dir> "
                    "--security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable"
                ),
            )
            closure_item.update(
                {
                    "releaseTag": freshness_kit.get("releaseTag") or "",
                    "tagTargetSha": freshness_kit.get("tagTargetSha") or "",
                    "releaseTargetCommitish": freshness_kit.get("releaseTargetCommitish") or "",
                    "releaseManifestPath": freshness_kit.get("releaseManifestPath") or "",
                    "manifestCommit": freshness_kit.get("manifestCommit") or "",
                    "manifestGeneratedAt": freshness_kit.get("manifestGeneratedAt") or "",
                    "comparisons": freshness_kit.get("comparisons") if isinstance(freshness_kit.get("comparisons"), dict) else {},
                    "problems": freshness_kit.get("problems") if isinstance(freshness_kit.get("problems"), list) else [],
                    "freshnessRerunCommand": freshness_kit.get("freshnessRerunCommand") or item.get("nextCommand") or "",
                    "repairCriteria": freshness_kit.get("repairCriteria") if isinstance(freshness_kit.get("repairCriteria"), list) else [],
                    "passCriteria": freshness_kit.get("passCriteria") if isinstance(freshness_kit.get("passCriteria"), list) else [],
                    "failCriteria": freshness_kit.get("failCriteria") if isinstance(freshness_kit.get("failCriteria"), list) else [],
                    "freshnessProofBoundary": freshness_kit.get("freshnessProofBoundary") if isinstance(freshness_kit.get("freshnessProofBoundary"), dict) else {},
                    "releaseFreshnessClosureKit": freshness_kit,
                }
            )
            closure_item["nextCommand"] = closure_item["freshnessRerunCommand"]
        if evidence_id == "release-version-coherence":
            diagnostics = (
                item.get("releaseVersionCoherenceDiagnostics")
                if isinstance(item.get("releaseVersionCoherenceDiagnostics"), dict)
                else {}
            )
            closure_item.update(
                {
                    "sourceVersion": diagnostics.get("sourceVersion") or "",
                    "releaseVersion": diagnostics.get("releaseVersion") or "",
                    "expectedTag": diagnostics.get("expectedTag") or "",
                    "metadataTagName": diagnostics.get("metadataTagName") or "",
                    "manifestVersion": diagnostics.get("manifestVersion") or "",
                    "manifestTag": diagnostics.get("manifestTag") or "",
                    "packageVersion": diagnostics.get("packageVersion") or "",
                    "consumerReportVersion": diagnostics.get("consumerReportVersion") or "",
                    "expectedTarballName": diagnostics.get("expectedTarballName") or "",
                    "manifestArtifactName": diagnostics.get("manifestArtifactName") or "",
                    "comparisons": diagnostics.get("comparisons") if isinstance(diagnostics.get("comparisons"), dict) else {},
                    "problems": diagnostics.get("problems") if isinstance(diagnostics.get("problems"), list) else [],
                    "repairCriteria": RELEASE_VERSION_COHERENCE_REPAIR_CRITERIA,
                    "passCriteria": RELEASE_VERSION_COHERENCE_PASS_CRITERIA,
                    "failCriteria": RELEASE_VERSION_COHERENCE_FAIL_CRITERIA,
                    "versionCoherenceRerunCommand": rerun_command or item.get("nextCommand") or first_blocking.get("nextCommand") or "",
                }
            )
            closure_item["nextCommand"] = closure_item["versionCoherenceRerunCommand"]
        if evidence_id == "release-asset-coherence":
            diagnostics = (
                item.get("releaseAssetCoherenceDiagnostics")
                if isinstance(item.get("releaseAssetCoherenceDiagnostics"), dict)
                else {}
            )
            upload_handoff = github_release_upload_handoff(metadata_proof, assets_dir=release_assets_dir)
            upload_inputs = upload_handoff["inputs"]
            upload_ready = bool(upload_inputs.get("concreteAssetCount")) and upload_inputs.get("concreteAssetCount") == len(upload_inputs.get("requiredAssets", []))
            post_handoff_proof = public_release_post_handoff_proof(
                manual_action="upload-release-assets",
                repo=str(upload_inputs.get("repo") or metadata_proof.get("repo") or "<owner/repo>"),
                tag=str(upload_inputs.get("tag") or metadata_proof.get("tag") or "v<version>"),
                rerun_command=rerun_command or item.get("nextCommand") or first_blocking.get("nextCommand") or "",
            )
            closure_item.update(
                {
                    "expectedTarballName": diagnostics.get("expectedTarballName") or "",
                    "requiredAssetNames": diagnostics.get("requiredAssetNames") if isinstance(diagnostics.get("requiredAssetNames"), list) else [],
                    "metadataAssetNames": diagnostics.get("metadataAssetNames") if isinstance(diagnostics.get("metadataAssetNames"), list) else [],
                    "localAssetNames": diagnostics.get("localAssetNames") if isinstance(diagnostics.get("localAssetNames"), list) else [],
                    "digestAssetNames": diagnostics.get("digestAssetNames") if isinstance(diagnostics.get("digestAssetNames"), list) else [],
                    "missingLocalAssetNames": diagnostics.get("missingLocalAssetNames") if isinstance(diagnostics.get("missingLocalAssetNames"), list) else [],
                    "missingDigestAssetNames": diagnostics.get("missingDigestAssetNames") if isinstance(diagnostics.get("missingDigestAssetNames"), list) else [],
                    "missingSha256AssetNames": diagnostics.get("missingSha256AssetNames") if isinstance(diagnostics.get("missingSha256AssetNames"), list) else [],
                    "manifestArtifactName": diagnostics.get("manifestArtifactName") or "",
                    "digestTarballName": diagnostics.get("digestTarballName") or "",
                    "manifestArtifactSha256": diagnostics.get("manifestArtifactSha256") or "",
                    "digestTarballSha256": diagnostics.get("digestTarballSha256") or "",
                    "consumerArtifactSha256": diagnostics.get("consumerArtifactSha256") or "",
                    "comparisons": diagnostics.get("comparisons") if isinstance(diagnostics.get("comparisons"), dict) else {},
                    "problems": diagnostics.get("problems") if isinstance(diagnostics.get("problems"), list) else [],
                    "repairCriteria": RELEASE_ASSET_COHERENCE_REPAIR_CRITERIA,
                    "passCriteria": RELEASE_ASSET_COHERENCE_PASS_CRITERIA,
                    "failCriteria": RELEASE_ASSET_COHERENCE_FAIL_CRITERIA,
                    "releaseAssetUploadCommand": upload_handoff["command"],
                    "releaseAssetUploadCommandReady": upload_ready,
                    "releaseAssetUploadCommandBoundary": upload_handoff["boundary"],
                    "postHandoffProof": post_handoff_proof,
                    "assetCoherenceRerunCommand": rerun_command or item.get("nextCommand") or first_blocking.get("nextCommand") or "",
                }
            )
            closure_item["nextCommand"] = closure_item["releaseAssetUploadCommand"] if upload_ready else closure_item["assetCoherenceRerunCommand"]
        if evidence_id in {"independent-adoption-evidence", "final-security-review-evidence"}:
            template = templates_by_id.get(evidence_id, {})
            starter_file = starter_files_by_id.get(evidence_id, {})
            evidence_diagnostics = item.get("evidenceDiagnostics") if isinstance(item.get("evidenceDiagnostics"), dict) else {}
            closure_rerun_command = rerun_command or item.get("nextCommand") or first_blocking.get("nextCommand") or ""
            closure_item.update(
                {
                    "starterKitPath": starter_file.get("path") or template.get("starterPath") or "",
                    "templatePath": template.get("path") or item.get("templatePath") or "",
                    "templateCommand": template.get("copyCommand") or item.get("templateCommand") or "",
                    "attachArgument": starter_file.get("attachArgument") or "",
                    "acceptedEvidenceClasses": template.get("acceptedEvidenceClasses") if isinstance(template.get("acceptedEvidenceClasses"), list) else [],
                    "requiredFields": template.get("requiredFields") if isinstance(template.get("requiredFields"), list) else [],
                    "requiredScope": template.get("requiredScope") if isinstance(template.get("requiredScope"), list) else [],
                    "stableRequirement": template.get("stableRequirement") or "",
                    "redactionBoundary": template.get("redactionBoundary") if isinstance(template.get("redactionBoundary"), dict) else {},
                    "privacyBoundary": template.get("privacyBoundary") if isinstance(template.get("privacyBoundary"), dict) else {},
                    "passCriteria": template.get("passCriteria") if isinstance(template.get("passCriteria"), list) else [],
                    "failCriteria": template.get("failCriteria") if isinstance(template.get("failCriteria"), list) else [],
                    "currentEvidenceDiagnostics": evidence_diagnostics,
                    "rerunCommand": closure_rerun_command,
                    "evidenceClosureKit": {
                        "evidenceId": evidence_id,
                        "title": template.get("title") or closure_item["summary"],
                        "directory": evidence_starter_kit.get("directory"),
                        "draftOnly": evidence_starter_kit.get("draftOnly") is True,
                        "starterPath": starter_file.get("path") or template.get("starterPath") or "",
                        "templatePath": template.get("path") or item.get("templatePath") or "",
                        "templateCommand": template.get("copyCommand") or item.get("templateCommand") or "",
                        "attachArgument": starter_file.get("attachArgument") or "",
                        "acceptedEvidenceClasses": template.get("acceptedEvidenceClasses") if isinstance(template.get("acceptedEvidenceClasses"), list) else [],
                        "requiredFields": template.get("requiredFields") if isinstance(template.get("requiredFields"), list) else [],
                        "requiredScope": template.get("requiredScope") if isinstance(template.get("requiredScope"), list) else [],
                        "redactionBoundary": template.get("redactionBoundary") if isinstance(template.get("redactionBoundary"), dict) else {},
                        "privacyBoundary": template.get("privacyBoundary") if isinstance(template.get("privacyBoundary"), dict) else {},
                        "passCriteria": template.get("passCriteria") if isinstance(template.get("passCriteria"), list) else [],
                        "failCriteria": template.get("failCriteria") if isinstance(template.get("failCriteria"), list) else [],
                        "currentEvidenceDiagnostics": evidence_diagnostics,
                        "rerunCommand": closure_rerun_command,
                    },
                }
            )
            closure_item["nextCommand"] = closure_item["rerunCommand"]
        items.append(closure_item)

    first_item = items[0] if items else None
    return {
        "schemaVersion": 1,
        "releaseVersion": release_version,
        "status": "pass" if not items else "review",
        "stableV4Release": stable_v4_release,
        "blockerCount": len(items),
        "blockedEvidenceIds": [str(item.get("id")) for item in items],
        "firstBlocker": first_item,
        "items": items,
        "dependencyOrder": [str(item.get("id")) for item in required if isinstance(item, dict)],
        "noHiddenLowerOrderBlockers": True,
        "nextCommand": (
            first_item.get("nextCommand")
            if first_item
            else "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet"
        ),
        "nonClaims": [
            "This checklist does not prove stable v4 by itself.",
            "Every listed item must pass from real publication evidence before stable-v4 claims are allowed.",
            "Do not skip later blockers merely because an earlier gate is still failing.",
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
    closure_checklist = (
        report.get("stablePublicationClosureChecklist")
        if isinstance(report.get("stablePublicationClosureChecklist"), dict)
        else {}
    )
    checklist = {
        "schemaVersion": 1,
        "draftOnly": True,
        "status": packet.get("status", report.get("status")),
        "releaseVersion": report.get("releaseVersion"),
        "stableV4Release": False,
        "firstBlockingGate": packet.get("firstBlockingGate"),
        "closureChecklist": closure_checklist,
        "requiredEvidence": packet.get("requiredEvidence", []),
        "missingEvidenceIds": packet.get("missingEvidenceIds", []),
        "blockedClaims": report.get("blockedClaims", []),
        "relatedAuthoringKits": starter_kit.get("relatedAuthoringKits", []),
        "nextCommandTemplate": starter_kit.get("nextCommandTemplate"),
    }
    (kit_dir / "stable-publication-checklist.json").write_text(
        json.dumps(checklist, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    related_kits = starter_kit.get("relatedAuthoringKits")
    release_notes_kit = next(
        (
            item for item in related_kits
            if isinstance(item, dict) and item.get("id") == "release-notes-authoring-kit"
        ),
        {},
    ) if isinstance(related_kits, list) else {}

    readme_lines = [
        "# Stable Publication Evidence Kit",
        "",
        "This directory is a draft-only starter kit for `shipguard v4 stable-publication`.",
        "It helps collect the real evidence packet; it is not evidence by itself.",
        "",
        f"- Release version: `{report.get('releaseVersion') or 'unknown'}`",
        "",
        "## Files",
        "",
        "- `stable-publication-checklist.json`: the current ten-gate checklist, closure checklist, and first blocker.",
        "- `external-adoption-evidence.json`: starter record for independent adoption evidence.",
        "- `security-review-evidence.json`: starter record for final security-review evidence.",
        "",
        "## Rules",
        "",
        "- Do not use unchanged starter-kit JSON as stable-v4 proof.",
        "- Redact private app names, private paths, screenshots, account data, and token-like strings before sharing.",
        "- Stable v4 is only claimable when `shipguard v4 stable-publication` returns `pass`.",
        "",
    ]
    if release_notes_kit:
        missing_topics = ", ".join(str(item) for item in release_notes_kit.get("missingTopicIds", [])) or "none"
        readme_lines.extend(
            [
                "## Related Authoring Kits",
                "",
                f"- Release notes kit: `{release_notes_kit.get('directory') or RELEASE_NOTES_KIT_DIRNAME}`",
                f"- Release notes status: `{release_notes_kit.get('status') or 'review'}`",
                f"- Missing release-note topics: `{missing_topics}`",
                "",
            ]
        )
    readme_lines.extend(
        [
            "## Next Command",
            "",
            "```bash",
            str(starter_kit.get("nextCommandTemplate") or ""),
            "```",
            "",
        ]
    )
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
    edit_command = str(kit.get("publicReleaseEditCommand") or "")
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
        "## Publish Edited Notes",
        "",
        "Review this draft, then update the public GitHub release body manually:",
        "",
        "```bash",
        edit_command,
        "```",
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
        f"- Release URL: `{kit.get('releaseUrl') or 'not-provided'}`",
        f"- Release tag: `{kit.get('releaseTag') or 'not-provided'}`",
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
        "## Edit Public Release Notes",
        "",
        "Review `draft-release-notes.md`, then run:",
        "",
        "```bash",
        edit_command,
        "```",
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
    refresh_generated_download_destination(args, out_dir)

    metadata_proof = build_github_release_metadata_proof(args, version)
    latest_release_proof = build_github_latest_release_proof(args)
    release_notes_proof = build_release_notes_proof(metadata_proof)
    release_candidate_packet_proof = build_release_candidate_packet_proof(args)
    github_download_proof = launchkey.build_github_release_asset_download_proof(args, version)
    published_asset_proof = launchkey.build_published_release_asset_proof(consumer_args, root, version, github_download_proof)
    post_release_consumer_proof = build_post_release_consumer_proof(published_asset_proof)
    public_release_freshness_proof = build_public_release_freshness_proof(
        root=root,
        release_version=release_version,
        metadata_proof=metadata_proof,
        published_asset_proof=published_asset_proof,
    )
    release_version_coherence_proof = build_release_version_coherence_proof(
        source_version=version,
        release_version=release_version,
        metadata_proof=metadata_proof,
        published_asset_proof=published_asset_proof,
        public_release_freshness_proof=public_release_freshness_proof,
    )
    release_asset_coherence_proof = build_release_asset_coherence_proof(
        release_version=release_version,
        metadata_proof=metadata_proof,
        published_asset_proof=published_asset_proof,
        post_release_consumer_proof=post_release_consumer_proof,
        public_release_freshness_proof=public_release_freshness_proof,
        release_version_coherence_proof=release_version_coherence_proof,
    )
    release_assets_dir = published_asset_proof.get("assetsDir") or args.release_assets or ""
    adoption_proof = attach_external_evidence_freshness(
        launchkey.build_external_adoption_evidence_proof(args),
        evidence_id="independent-adoption-evidence",
        metadata_proof=metadata_proof,
        release_freshness_proof=public_release_freshness_proof,
    )
    security_proof = attach_external_evidence_freshness(
        launchkey.build_security_review_evidence_proof(args),
        evidence_id="final-security-review-evidence",
        metadata_proof=metadata_proof,
        release_freshness_proof=public_release_freshness_proof,
    )
    adoption_gate_proof = {
        **adoption_proof,
        "status": adoption_proof.get("stableV4GateStatus") or adoption_proof.get("status"),
    }
    security_gate_proof = {
        **security_proof,
        "status": security_proof.get("stableV4GateStatus") or security_proof.get("status"),
    }
    release_notes_authoring_kit = build_stable_publication_release_notes_authoring_kit(
        release_version=release_version,
        release_notes_proof=release_notes_proof,
        metadata_proof=metadata_proof,
        out_dir=out_dir,
    )
    release_notes_next_command = str(
        release_notes_authoring_kit.get("publicReleaseEditCommand")
        or stable_publication_command(args, placeholders=True)
    )

    gates = [
        ("githubReleaseMetadataProof", metadata_proof, stable_publication_command(args, placeholders=True)),
        ("releaseNotesProof", release_notes_proof, release_notes_next_command),
        ("releaseCandidatePacketProof", release_candidate_packet_proof, release_candidate_packet_proof.get("nextCommand", "")),
        ("publishedReleaseAssetProof", published_asset_proof, stable_publication_rerun_command(args)),
        ("postReleaseConsumerProof", post_release_consumer_proof, published_asset_proof.get("consumeCommand", "")),
        ("publicReleaseFreshnessProof", public_release_freshness_proof, stable_publication_rerun_command(args)),
        ("releaseVersionCoherenceProof", release_version_coherence_proof, stable_publication_rerun_command(args)),
        ("releaseAssetCoherenceProof", release_asset_coherence_proof, stable_publication_rerun_command(args)),
        ("externalAdoptionEvidenceStableGate", adoption_gate_proof, adoption_proof.get("nextCommand", "")),
        ("securityReviewEvidenceStableGate", security_gate_proof, security_proof.get("nextCommand", "")),
    ]
    blocked = first_blocking_gate(gates)
    status = "pass" if blocked is None else "review"
    stable_v4_release = status == "pass"
    evidence_templates = build_stable_publication_evidence_templates(root)
    evidence_starter_kit = build_stable_publication_evidence_starter_kit_manifest()
    evidence_starter_kit = attach_release_notes_authoring_kit_to_starter(
        evidence_starter_kit,
        release_version=release_version,
        release_notes_authoring_kit=release_notes_authoring_kit,
    )
    public_evidence_closure_proof = build_public_evidence_closure_proof(
        release_version=release_version,
        adoption_proof=adoption_proof,
        security_proof=security_proof,
        evidence_templates=evidence_templates,
        evidence_starter_kit=evidence_starter_kit,
        rerun_command=stable_publication_rerun_command(args),
    )
    evidence_packet = build_stable_publication_evidence_packet(
        gates=gates,
        blocked=blocked,
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_templates=evidence_templates,
    )
    closure_checklist = build_stable_publication_closure_checklist(
        evidence_packet=evidence_packet,
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_templates=evidence_templates,
        evidence_starter_kit=evidence_starter_kit,
        release_notes_proof=release_notes_proof,
        release_notes_authoring_kit=release_notes_authoring_kit,
        metadata_proof=metadata_proof,
        release_assets_dir=release_assets_dir,
        rerun_command=stable_publication_rerun_command(args),
    )
    launch_relay_drafts = build_stable_publication_launch_relay_drafts(
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_packet=evidence_packet,
    )
    public_release_delta_proof = build_public_release_delta_proof(
        root=root,
        source_version=version,
        release_version=release_version,
        metadata_proof=metadata_proof,
        latest_release_proof=latest_release_proof,
        published_asset_proof=published_asset_proof,
        public_release_freshness_proof=public_release_freshness_proof,
        release_version_coherence_proof=release_version_coherence_proof,
        release_asset_coherence_proof=release_asset_coherence_proof,
        stable_v4_release=stable_v4_release,
        rerun_command=stable_publication_rerun_command(args),
    )
    final_claim_packet = build_final_stable_v4_claim_packet(
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        evidence_packet=evidence_packet,
        public_evidence_closure_proof=public_evidence_closure_proof,
        launch_relay_drafts=launch_relay_drafts,
        public_release_delta_proof=public_release_delta_proof,
        rerun_command=stable_publication_rerun_command(args),
    )
    generated_paths = release_notes_authoring_kit.get("generatedPaths") if isinstance(release_notes_authoring_kit.get("generatedPaths"), dict) else {}
    release_create_command = ""
    for item in closure_checklist.get("items", []):
        if isinstance(item, dict) and item.get("id") == "github-release-metadata":
            release_create_command = str(item.get("releaseCreateCommand") or "")
            break
    if not release_create_command:
        release_create_command = github_release_create_handoff(
            metadata_proof,
            notes_file=generated_paths.get("draftReleaseNotes") or None,
            assets_dir=release_assets_dir,
        )["command"]
    release_asset_repair_command = ""
    for item in closure_checklist.get("items", []):
        if not isinstance(item, dict):
            continue
        if item.get("id") in {"downloaded-release-assets", "release-asset-coherence"}:
            release_asset_repair_command = str(item.get("nextCommand") or "")
            break
    release_visibility_handoff = build_release_visibility_handoff(
        release_version=release_version,
        stable_v4_release=stable_v4_release,
        release_notes_proof=release_notes_proof,
        release_notes_authoring_kit=release_notes_authoring_kit,
        release_candidate_packet_proof=release_candidate_packet_proof,
        published_asset_proof=published_asset_proof,
        public_evidence_closure_proof=public_evidence_closure_proof,
        public_release_delta_proof=public_release_delta_proof,
        release_asset_coherence_proof=release_asset_coherence_proof,
        final_claim_packet=final_claim_packet,
        rerun_command=stable_publication_rerun_command(args),
        release_create_command=release_create_command,
        release_asset_repair_command=release_asset_repair_command,
    )

    if blocked:
        receipt, proof, next_command = blocked
        summary = (
            f"{closure_checklist.get('blockerCount')} stable-v4 publication blocker(s) remain; first blocker: "
            f"{proof.get('summary') or f'{receipt} has not passed.'}"
        )
        priority_action = (
            f"Work the Closure Checklist in order; first complete {evidence_label_for_receipt(receipt)} before claiming stable-v4 publication."
        )
        proof_source = evidence_label_for_receipt(receipt)
    else:
        next_command = "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet"
        summary = "Stable-v4 publication proof passed every local stable-publication gate."
        priority_action = "Use the stable-publication report as release proof input, then move the next ShipGuard roadmap goal forward."
        proof_source = "release metadata, release notes, LaunchKey report, release-consume, adoption evidence, and security evidence"

    visibility_primary = str(release_visibility_handoff.get("primaryDecision") or "")
    visibility_actions = (
        release_visibility_handoff.get("requiredActions")
        if isinstance(release_visibility_handoff.get("requiredActions"), list)
        else []
    )
    visibility_action = next(
        (
            item
            for item in visibility_actions
            if isinstance(item, dict)
            and item.get("id") == visibility_primary
            and item.get("required") is True
            and str(item.get("nextCommand") or "") not in {"", "not-needed", "blocked-by-required-actions"}
        ),
        None,
    )
    if blocked and receipt == "githubReleaseMetadataProof" and isinstance(visibility_action, dict):
        next_command = str(visibility_action.get("nextCommand") or next_command)
        priority_action = (
            f"Use the release visibility handoff action `{visibility_primary}` before rerunning stable-publication."
        )

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
        "stablePublicationClosureChecklist": closure_checklist,
        "stablePublicationEvidenceTemplates": evidence_templates,
        "stablePublicationEvidenceStarterKit": evidence_starter_kit,
        "stablePublicationReleaseNotesAuthoringKit": release_notes_authoring_kit,
        "stablePublicationLaunchRelayDrafts": launch_relay_drafts,
        "publicReleaseDeltaProof": public_release_delta_proof,
        "releaseVisibilityHandoff": release_visibility_handoff,
        "finalStableV4ClaimPacket": final_claim_packet,
        "githubReleaseMetadataProof": metadata_proof,
        "githubLatestReleaseProof": latest_release_proof,
        "releaseNotesProof": release_notes_proof,
        "releaseCandidatePacketProof": release_candidate_packet_proof,
        "githubReleaseAssetDownloadProof": github_download_proof,
        "publishedReleaseAssetProof": published_asset_proof,
        "postReleaseConsumerProof": post_release_consumer_proof,
        "publicReleaseFreshnessProof": public_release_freshness_proof,
        "releaseVersionCoherenceProof": release_version_coherence_proof,
        "releaseAssetCoherenceProof": release_asset_coherence_proof,
        "publicEvidenceClosureProof": public_evidence_closure_proof,
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
            "Does the stable-publication closure checklist list every remaining blocker in dependency order with exact next commands instead of hiding lower-order blockers behind only the first failing gate?",
            "Does the stable-publication report provide draft-only evidence templates for independent adoption and final security review without manufacturing proof?",
            "Does the stable-publication report write a draft-only evidence starter kit so maintainers can collect the packet without reverse-engineering JSON shapes?",
            "Does the LaunchKey candidate closure row expose the supplied candidate path, nested receipt, required proof areas, package-hygiene diagnostics, repair/pass criteria, nested rerun, full stable-publication rerun, and fixture-proof boundary?",
            "Does the downloaded release-assets closure row expose required assets, metadata/local missing assets, download source/status, asset directory, repair/pass/fail criteria, download rerun, full stable-publication rerun, and metadata-only/source-only/fixture-proof boundaries?",
            "Does the post-release consumer closure row expose release-consume paths, missing proof artifacts, digest/replay/attestation statuses, repair/pass criteria, release-consume rerun, full stable-publication rerun, and source-only/fixture-proof boundaries?",
            "Does the public release freshness row prove the GitHub tag target, release manifest commit, release metadata target, and publication timestamp describe the same release?",
            "Does the release version coherence row prove VERSION, GitHub metadata, release manifest, package proof, and consumer report all name the same release version?",
            "Does the release asset coherence row prove required asset names and SHA-256 values match across metadata, local assets, manifest, digest matrix, and consumer proof?",
            "Do independent adoption and final security-review evidence records prove generatedAt freshness against the release manifest instead of reusing stale packet evidence?",
            "Does the public evidence closure proof summarize adoption/security gate status, freshness, starter paths, copy-ready commands, and non-claims before stable-v4 publication?",
            "Does the public release delta proof show whether local main, latest GitHub release, package assets, and stable-publication claims are aligned before announcement copy?",
            "Does the release visibility handoff say whether to publish a new GitHub release, update notes/assets, attach adoption/security evidence, or keep the current public release unchanged?",
            "Does the final stable-v4 claim packet give copy-ready allowed wording, blocked wording, evidence status rows, approval boundaries, and non-claims before any launch announcement?",
            "Do independent adoption and final security-review closure rows expose starter paths, required fields, redaction/privacy boundaries, pass/fail criteria, current diagnostics, and exact stable-publication rerun commands?",
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


def append_post_handoff_proof_markdown(lines: list[str], proof: dict[str, Any]) -> None:
    if not isinstance(proof, dict) or not proof:
        return
    proof_commands = proof.get("proofCommands") if isinstance(proof.get("proofCommands"), list) else []
    lines.extend(
        [
            "",
            "Post-handoff proof:",
            "",
            f"- Manual action: `{proof.get('manualAction') or 'not-provided'}`",
            "",
        ]
    )
    for command in proof_commands:
        if command:
            lines.extend(["```bash", str(command), "```", ""])
    criteria = proof.get("successCriteria") if isinstance(proof.get("successCriteria"), list) else []
    if criteria:
        lines.extend(["Success criteria:", ""])
        for criterion in criteria:
            lines.append(f"- {criterion}")
    non_claims = proof.get("nonClaims") if isinstance(proof.get("nonClaims"), list) else []
    if non_claims:
        lines.extend(["", "Non-claims:", ""])
        for claim in non_claims:
            lines.append(f"- {claim}")


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
    public_evidence = (
        report.get("publicEvidenceClosureProof")
        if isinstance(report.get("publicEvidenceClosureProof"), dict)
        else {}
    )
    if public_evidence:
        boundary = (
            public_evidence.get("publicEvidenceBoundary")
            if isinstance(public_evidence.get("publicEvidenceBoundary"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Public Evidence Closure",
                "",
                f"- Status: `{public_evidence.get('status')}`",
                f"- Starter kit: `{public_evidence.get('starterKitDirectory') or 'not-provided'}`",
                f"- Real adoption evidence required: `{boundary.get('realExternalAdoptionEvidenceRequired')}`",
                f"- Final security review required: `{boundary.get('finalSecurityReviewEvidenceRequired')}`",
                f"- GitHub download counts count as adoption evidence: `{boundary.get('githubDownloadCountsCountAsAdoptionEvidence')}`",
                f"- Fixture evidence counts as stable-v4 evidence: `{boundary.get('fixtureEvidenceCountsAsStableV4Evidence')}`",
                f"- Marketplace acceptance claimed: `{not boundary.get('doesNotClaimMarketplaceAcceptance')}`",
                "",
                "| Evidence | Gate | Freshness | Eligible | Fresh | Stale | Starter |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for row in public_evidence.get("evidenceRows", []):
            if isinstance(row, dict):
                lines.append(
                    f"| `{row.get('id')}` | `{row.get('stableV4GateStatus')}` | `{row.get('freshnessStatus')}` | "
                    f"`{row.get('stableV4EligibleEvidenceCount')}` | `{row.get('freshStableRecordCount')}` | "
                    f"`{row.get('staleStableRecordCount')}` | `{row.get('starterPath') or 'not-provided'}` |"
                )
        lines.extend(["", "Copy-ready commands:", ""])
        for command in public_evidence.get("copyReadyCommands", []):
            lines.append(f"- `{command}`")
        lines.extend(["", "Public evidence non-claims:", ""])
        for claim in public_evidence.get("nonClaims", []):
            lines.append(f"- {claim}")
    public_delta = (
        report.get("publicReleaseDeltaProof")
        if isinstance(report.get("publicReleaseDeltaProof"), dict)
        else {}
    )
    if public_delta:
        boundary = (
            public_delta.get("releaseDeltaBoundary")
            if isinstance(public_delta.get("releaseDeltaBoundary"), dict)
            else {}
        )
        comparisons = (
            public_delta.get("comparisons")
            if isinstance(public_delta.get("comparisons"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Public Release Delta",
                "",
                f"- Status: `{public_delta.get('status')}`",
                f"- Source version: `{public_delta.get('sourceVersion')}`",
                f"- Selected release: `{public_delta.get('releaseVersion')}`",
                f"- Latest GitHub release: `{public_delta.get('latestGitHubReleaseVersion') or 'not-provided'}`",
                f"- Package version: `{public_delta.get('packageVersion') or 'not-provided'}`",
                f"- Unpublished local delta: `{public_delta.get('unpublishedLocalDelta')}`",
                f"- Stable-v4 claim covers selected public release: `{public_delta.get('stableV4ClaimCoversSelectedPublicRelease')}`",
                f"- Stable-v4 claim covers local checkout: `{public_delta.get('stableV4ClaimCoversLocalCheckout')}`",
                f"- Unpublished local code counts as released: `{boundary.get('unpublishedLocalCodeCountsAsReleased')}`",
                "",
                "| Comparison | Value |",
                "| --- | --- |",
            ]
        )
        for key, value in comparisons.items():
            lines.append(f"| `{key}` | `{value}` |")
        if public_delta.get("problems"):
            lines.extend(["", "Release delta problems:", ""])
            for problem in public_delta.get("problems", []):
                lines.append(f"- {problem}")
        lines.extend(["", "Next command:", "", "```bash", str(public_delta.get("nextCommand") or ""), "```"])
    visibility = (
        report.get("releaseVisibilityHandoff")
        if isinstance(report.get("releaseVisibilityHandoff"), dict)
        else {}
    )
    if visibility:
        boundary = (
            visibility.get("visibilityBoundary")
            if isinstance(visibility.get("visibilityBoundary"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Release Visibility Handoff",
                "",
                f"- Status: `{visibility.get('status')}`",
                f"- Primary decision: `{visibility.get('primaryDecision')}`",
                f"- Latest GitHub release: `{visibility.get('latestGitHubReleaseVersion') or 'not-provided'}`",
                f"- Selected release tag: `{visibility.get('selectedGitHubReleaseTag') or 'not-provided'}`",
                f"- Unpublished local delta: `{visibility.get('unpublishedLocalDelta')}`",
                f"- Current public release can be announced: `{visibility.get('currentPublicReleaseCanBeAnnounced')}`",
                f"- Local main can be announced: `{visibility.get('localMainCanBeAnnounced')}`",
                f"- Unpublished local code counts as released: `{boundary.get('unpublishedLocalCodeCountsAsReleased')}`",
                "",
                "| Action | Required | Status | Next command |",
                "| --- | ---: | --- | --- |",
            ]
        )
        for action in visibility.get("requiredActions", []):
            if isinstance(action, dict):
                lines.append(
                    f"| `{action.get('id')}` | `{action.get('required')}` | "
                    f"`{action.get('status')}` | `{action.get('nextCommand') or 'not-provided'}` |"
                )
        lines.extend(["", "Next command:", "", "```bash", str(visibility.get("nextCommand") or ""), "```"])
    final_claim = (
        report.get("finalStableV4ClaimPacket")
        if isinstance(report.get("finalStableV4ClaimPacket"), dict)
        else {}
    )
    if final_claim:
        approval = (
            final_claim.get("approvalBoundary")
            if isinstance(final_claim.get("approvalBoundary"), dict)
            else {}
        )
        boundary = (
            final_claim.get("claimBoundary")
            if isinstance(final_claim.get("claimBoundary"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Final Stable V4 Claim Packet",
                "",
                f"- Claim decision: `{final_claim.get('claimDecision')}`",
                f"- Stable v4 release: `{final_claim.get('stableV4Release')}`",
                f"- Public evidence closure: `{final_claim.get('publicEvidenceClosureStatus')}`",
                f"- Claim may be published: `{(final_claim.get('claimPublicationReadiness') or {}).get('stableV4ClaimMayBePublished')}`",
                f"- First publication blocker: `{(final_claim.get('claimPublicationReadiness') or {}).get('firstBlockingGateId')}`",
                f"- Public posting requires explicit approval: `{approval.get('publicPostingRequiresExplicitApproval')}`",
                f"- Computer-use may post: `{approval.get('computerUseMayPost')}`",
                f"- Source-only proof counts as stable v4: `{boundary.get('sourceOnlyProofCountsAsStableV4')}`",
                f"- Fixture proof counts as stable v4: `{boundary.get('fixtureProofCountsAsStableV4')}`",
                f"- GitHub downloads count as adoption evidence: `{boundary.get('githubDownloadCountsCountAsAdoptionEvidence')}`",
                "",
                "Copy-ready claim:",
                "",
                str(final_claim.get("copyReadyClaim") or ""),
                "",
                "| Evidence | Status |",
                "| --- | --- |",
            ]
        )
        for row in final_claim.get("evidenceSummary", []):
            if isinstance(row, dict):
                lines.append(f"| `{row.get('id')}` | `{row.get('status')}` |")
        delta = (
            final_claim.get("publicReleaseDeltaSummary")
            if isinstance(final_claim.get("publicReleaseDeltaSummary"), dict)
            else {}
        )
        if delta:
            lines.extend(
                [
                    "",
                    "Final claim public-release delta:",
                    "",
                    f"- Delta status: `{delta.get('status')}`",
                    f"- Selected public release: `{delta.get('selectedGitHubReleaseTag') or 'not-provided'}`",
                    f"- Unpublished local delta: `{delta.get('unpublishedLocalDelta')}`",
                    f"- Claim covers selected public release: `{delta.get('stableV4ClaimCoversSelectedPublicRelease')}`",
                    f"- Claim covers local checkout: `{delta.get('stableV4ClaimCoversLocalCheckout')}`",
                    f"- Unpublished local code counts as released: `{delta.get('unpublishedLocalCodeCountsAsReleased')}`",
                ]
            )
        lines.extend(["", "Blocked claim wording:", ""])
        for claim in final_claim.get("blockedClaims", []):
            lines.append(f"- {claim}")
        lines.extend(["", "Next command:", "", "```bash", str(final_claim.get("nextCommand") or ""), "```"])
    evidence_freshness_rows = []
    for label, proof_key in (
        ("independent-adoption-evidence", "externalAdoptionEvidenceProof"),
        ("final-security-review-evidence", "securityReviewEvidenceProof"),
    ):
        proof = report.get(proof_key) if isinstance(report.get(proof_key), dict) else {}
        freshness = proof.get("evidencePacketFreshness") if isinstance(proof.get("evidencePacketFreshness"), dict) else {}
        if freshness:
            evidence_freshness_rows.append((label, freshness))
    if evidence_freshness_rows:
        lines.extend(
            [
                "",
                "## External Evidence Freshness",
                "",
                "| Evidence | Status | Reference timestamp | Fresh stable records | Stale stable records |",
                "| --- | --- | --- | ---: | ---: |",
            ]
        )
        for label, freshness in evidence_freshness_rows:
            lines.append(
                f"| `{label}` | `{freshness.get('status')}` | `{freshness.get('referenceTimestamp') or 'not-provided'}` | "
                f"`{freshness.get('freshStableRecordCount')}` | `{freshness.get('staleStableRecordCount')}` |"
            )
        lines.extend(["", "Freshness boundary:", ""])
        for label, freshness in evidence_freshness_rows:
            boundary = freshness.get("freshnessBoundary") if isinstance(freshness.get("freshnessBoundary"), dict) else {}
            problems = freshness.get("problems") if isinstance(freshness.get("problems"), list) else []
            lines.append(f"- `{label}` generatedAt no earlier than release manifest: `{boundary.get('generatedAtMustBeNoEarlierThanReleaseManifest')}`")
            if problems:
                lines.append(f"- `{label}` first problem: {problems[0]}")
            else:
                lines.append(f"- `{label}` first problem: none")
    version_coherence = (
        report.get("releaseVersionCoherenceProof")
        if isinstance(report.get("releaseVersionCoherenceProof"), dict)
        else {}
    )
    if version_coherence:
        comparisons = version_coherence.get("comparisons") if isinstance(version_coherence.get("comparisons"), dict) else {}
        problems = version_coherence.get("problems") if isinstance(version_coherence.get("problems"), list) else []
        boundary = (
            version_coherence.get("versionCoherenceBoundary")
            if isinstance(version_coherence.get("versionCoherenceBoundary"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Release Version Coherence",
                "",
                f"- Status: `{version_coherence.get('status')}`",
                f"- Source VERSION: `{version_coherence.get('sourceVersion') or 'not-provided'}`",
                f"- Release version: `{version_coherence.get('releaseVersion') or 'not-provided'}`",
                f"- Expected tag: `{version_coherence.get('expectedTag') or 'not-provided'}`",
                f"- GitHub returned tag: `{version_coherence.get('metadataTagName') or 'not-provided'}`",
                f"- Manifest version: `{version_coherence.get('manifestVersion') or 'not-provided'}`",
                f"- Package version: `{version_coherence.get('packageVersion') or 'not-provided'}`",
                f"- Consumer report version: `{version_coherence.get('consumerReportVersion') or 'not-provided'}`",
                f"- Expected tarball: `{version_coherence.get('expectedTarballName') or 'not-provided'}`",
                f"- Manifest artifact: `{version_coherence.get('manifestArtifactName') or 'not-provided'}`",
                f"- Source-only proof counts as version coherence proof: `{boundary.get('sourceOnlyProofCountsAsVersionCoherenceProof')}`",
                "",
                "| Version comparison | Status |",
                "| --- | --- |",
            ]
        )
        if comparisons:
            for key, value in comparisons.items():
                lines.append(f"| `{key}` | `{value}` |")
        else:
            lines.append("| `not-provided` | `not-provided` |")
        lines.extend(["", "Version coherence problems:", ""])
        if problems:
            for problem in problems:
                lines.append(f"- {problem}")
        else:
            lines.append("- none")
        asset_coherence = (
            report.get("releaseAssetCoherenceProof")
            if isinstance(report.get("releaseAssetCoherenceProof"), dict)
            else {}
        )
    if asset_coherence:
        comparisons = asset_coherence.get("comparisons") if isinstance(asset_coherence.get("comparisons"), dict) else {}
        problems = asset_coherence.get("problems") if isinstance(asset_coherence.get("problems"), list) else []
        boundary = (
            asset_coherence.get("assetCoherenceBoundary")
            if isinstance(asset_coherence.get("assetCoherenceBoundary"), dict)
            else {}
        )
        lines.extend(
            [
                "",
                "## Release Asset Coherence",
                "",
                f"- Status: `{asset_coherence.get('status')}`",
                f"- Expected tarball: `{asset_coherence.get('expectedTarballName') or 'not-provided'}`",
                f"- Required assets: `{len(asset_coherence.get('requiredAssetNames') or [])}`",
                f"- Local assets: `{len(asset_coherence.get('localAssetNames') or [])}`",
                f"- Digest assets: `{len(asset_coherence.get('digestAssetNames') or [])}`",
                f"- Manifest artifact: `{asset_coherence.get('manifestArtifactName') or 'not-provided'}`",
                f"- Digest tarball: `{asset_coherence.get('digestTarballName') or 'not-provided'}`",
                f"- Manifest artifact SHA-256: `{asset_coherence.get('manifestArtifactSha256') or 'not-provided'}`",
                f"- Digest tarball SHA-256: `{asset_coherence.get('digestTarballSha256') or 'not-provided'}`",
                f"- Consumer artifact SHA-256: `{asset_coherence.get('consumerArtifactSha256') or 'not-provided'}`",
                f"- Source-only proof counts as asset coherence proof: `{boundary.get('sourceOnlyProofCountsAsAssetCoherenceProof')}`",
                "",
                "| Asset comparison | Status |",
                "| --- | --- |",
            ]
        )
        if comparisons:
            for key, value in comparisons.items():
                lines.append(f"| `{key}` | `{value}` |")
        else:
            lines.append("| `not-provided` | `not-provided` |")
        lines.extend(["", "Asset coherence problems:", ""])
        if problems:
            for problem in problems:
                lines.append(f"- {problem}")
        else:
            lines.append("- none")
        closure_items = (
            report.get("stablePublicationClosureChecklist", {}).get("items", [])
            if isinstance(report.get("stablePublicationClosureChecklist"), dict)
            else []
        )
        coherence_closure = next(
            (item for item in closure_items if isinstance(item, dict) and item.get("id") == "release-asset-coherence"),
            None,
        )
        if isinstance(coherence_closure, dict) and coherence_closure.get("releaseAssetUploadCommand"):
            lines.extend(
                [
                    "",
                    "Release asset upload handoff:",
                    "",
                    f"- Command ready: `{coherence_closure.get('releaseAssetUploadCommandReady')}`",
                    "",
                    "```bash",
                    str(coherence_closure.get("releaseAssetUploadCommand") or ""),
                    "```",
                ]
            )
            append_post_handoff_proof_markdown(
                lines,
                coherence_closure.get("postHandoffProof") if isinstance(coherence_closure.get("postHandoffProof"), dict) else {},
            )
    closure_checklist = (
        report.get("stablePublicationClosureChecklist")
        if isinstance(report.get("stablePublicationClosureChecklist"), dict)
        else {}
    )
    if closure_checklist:
        lines.extend(
            [
                "",
                "## Closure Checklist",
                "",
                f"- Checklist status: `{closure_checklist.get('status')}`",
                f"- Remaining blockers: `{closure_checklist.get('blockerCount')}`",
                f"- No hidden lower-order blockers: `{closure_checklist.get('noHiddenLowerOrderBlockers')}`",
                "",
                "| Rank | Evidence | Status | First | Next command | Proof boundary |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        items = closure_checklist.get("items") if isinstance(closure_checklist.get("items"), list) else []
        if items:
            for item in items:
                if isinstance(item, dict):
                    lines.append(
                        f"| `{item.get('rank')}` | `{item.get('id')}` | `{item.get('status')}` | "
                        f"`{item.get('isFirstBlockingGate')}` | `{item.get('nextCommand') or 'not-provided'}` | "
                        f"{item.get('proofBoundary') or ''} |"
                    )
        else:
            lines.append("| `none` | `none` | `pass` | `False` | `not-needed` | Every stable-publication gate passed. |")
        metadata_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "github-release-metadata"),
            None,
        )
        if isinstance(metadata_closure, dict) and isinstance(metadata_closure.get("releaseMetadataClosureKit"), dict):
            kit = metadata_closure["releaseMetadataClosureKit"]
            boundary = kit.get("metadataProofBoundary") if isinstance(kit.get("metadataProofBoundary"), dict) else {}
            create_boundary = kit.get("releaseCreateCommandBoundary") if isinstance(kit.get("releaseCreateCommandBoundary"), dict) else {}
            release_state = kit.get("releaseState") if isinstance(kit.get("releaseState"), dict) else {}
            notes_summary = kit.get("releaseNotesSummary") if isinstance(kit.get("releaseNotesSummary"), dict) else {}
            repo_inference = kit.get("repoInference") if isinstance(kit.get("repoInference"), dict) else {}
            required_assets = kit.get("requiredAssets") if isinstance(kit.get("requiredAssets"), list) else []
            metadata_assets = kit.get("metadataAssetNames") if isinstance(kit.get("metadataAssetNames"), list) else []
            metadata_missing = kit.get("metadataMissingAssets") if isinstance(kit.get("metadataMissingAssets"), list) else []
            lines.extend(
                [
                    "",
                    "### GitHub Release Metadata Closure Kit",
                    "",
                    f"- Status: `{kit.get('status') or metadata_closure.get('status') or 'not-provided'}`",
                    f"- Repository: `{kit.get('repo') or 'not-provided'}`",
                    f"- Repository inference: `{repo_inference.get('status') or 'not-provided'}` from `{repo_inference.get('source') or 'not-provided'}`",
                    f"- Release tag: `{kit.get('tag') or 'not-provided'}`",
                    f"- GitHub returned tag: `{kit.get('metadataTagName') or 'not-provided'}`",
                    f"- API URL: `{kit.get('apiUrl') or 'not-provided'}`",
                    f"- Release endpoint: `{kit.get('releaseEndpoint') or 'not-provided'}`",
                    f"- Release URL: `{kit.get('releaseUrl') or 'not-provided'}`",
                    f"- Target commitish: `{kit.get('targetCommitish') or 'not-provided'}`",
                    f"- Tag ref endpoint: `{kit.get('tagRefEndpoint') or 'not-provided'}`",
                    f"- Tag target SHA: `{kit.get('tagTargetSha') or 'not-provided'}`",
                    f"- Draft release: `{release_state.get('isDraft')}`",
                    f"- Prerelease: `{release_state.get('isPrerelease')}`",
                    f"- Required assets: `{', '.join(str(value) for value in required_assets) or 'not-provided'}`",
                    f"- Metadata assets: `{', '.join(str(value) for value in metadata_assets) or 'none'}`",
                    f"- Metadata missing assets: `{', '.join(str(value) for value in metadata_missing) or 'none'}`",
                    f"- Release notes SHA-256: `{notes_summary.get('sha256') or 'not-provided'}`",
                    f"- Release notes missing topics: `{', '.join(str(value) for value in notes_summary.get('missingTopicIds', []) if value) or 'none'}`",
                    f"- Public GitHub release metadata required: `{boundary.get('publicGitHubReleaseMetadataRequired')}`",
                    f"- Draft or prerelease counts as stable-publication proof: `{boundary.get('draftOrPrereleaseCountsAsStablePublicationProof')}`",
                    f"- Source-only proof counts as release metadata proof: `{boundary.get('sourceOnlyProofCountsAsReleaseMetadataProof')}`",
                    f"- Fixture API proof counts as stable-v4 publication proof: `{boundary.get('fixtureApiProofCountsAsStableV4PublicationProof')}`",
                    f"- Manual approval required to create release: `{create_boundary.get('manualApprovalRequired')}`",
                    f"- ShipGuard publishes GitHub release: `{create_boundary.get('shipguardPublishesGitHubRelease')}`",
                    f"- Release-create requires passing package proof: `{create_boundary.get('requiresPassingPackageProof')}`",
                    f"- Release-create requires proof assets: `{create_boundary.get('requiresReleaseProofAssets')}`",
                ]
            )
            lines.extend(["", "Repair criteria:", ""])
            for criterion in kit.get("repairCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Create missing GitHub release metadata manually:",
                    "",
                    "```bash",
                    str(kit.get("releaseCreateCommand") or ""),
                    "```",
                ]
            )
            append_post_handoff_proof_markdown(
                lines,
                kit.get("postHandoffProof") if isinstance(kit.get("postHandoffProof"), dict) else {},
            )
            lines.extend(
                [
                    "",
                    "Rerun release metadata proof:",
                    "",
                    "```bash",
                    str(kit.get("metadataRerunCommand") or metadata_closure.get("nextCommand") or ""),
                    "```",
                ]
            )
        release_notes_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "release-notes"),
            None,
        )
        if isinstance(release_notes_closure, dict):
            edit_boundary = (
                release_notes_closure.get("publicGitHubReleaseEditBoundary")
                if isinstance(release_notes_closure.get("publicGitHubReleaseEditBoundary"), dict)
                else {}
            )
            authoring_paths = (
                release_notes_closure.get("authoringKitPaths")
                if isinstance(release_notes_closure.get("authoringKitPaths"), list)
                else []
            )
            lines.extend(
                [
                    "",
                    "### Release Notes Closure Kit",
                    "",
                    f"- Missing topics: `{', '.join(release_notes_closure.get('missingTopicIds') or []) or 'none'}`",
                    f"- Public release edit required: `{edit_boundary.get('requiresPublicReleaseEdit')}`",
                    f"- ShipGuard edits public release: `{not bool(edit_boundary.get('shipguardDoesNotEditRelease'))}`",
                    f"- Release URL: `{edit_boundary.get('releaseUrl') or 'not-provided'}`",
                    f"- Public release edit command: `{edit_boundary.get('publicReleaseEditCommand') or 'not-provided'}`",
                    "",
                    "| Authoring file |",
                    "| --- |",
                ]
            )
            if authoring_paths:
                for path in authoring_paths:
                    lines.append(f"| `{path}` |")
            else:
                lines.append("| `not-provided` |")
            lines.extend(
                [
                    "",
                    "Rerun after editing public release notes:",
                    "",
                    "```bash",
                    str(release_notes_closure.get("rerunCommand") or release_notes_closure.get("nextCommand") or ""),
                    "```",
                ]
            )
        launchkey_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "launchkey-candidate-packet"),
            None,
        )
        if isinstance(launchkey_closure, dict) and isinstance(launchkey_closure.get("launchKeyCandidateClosureKit"), dict):
            kit = launchkey_closure["launchKeyCandidateClosureKit"]
            required_areas = kit.get("requiredLaunchKeyProofAreas") if isinstance(kit.get("requiredLaunchKeyProofAreas"), list) else []
            hygiene = kit.get("packageHygieneDiagnostics") if isinstance(kit.get("packageHygieneDiagnostics"), dict) else {}
            first_finding = hygiene.get("firstFinding") if isinstance(hygiene.get("firstFinding"), dict) else {}
            fixture_boundary = kit.get("fixtureCandidateBoundary") if isinstance(kit.get("fixtureCandidateBoundary"), dict) else {}
            lines.extend(
                [
                    "",
                    "### LaunchKey Candidate Closure Kit",
                    "",
                    f"- Candidate report path: `{kit.get('candidateReportPath') or 'not-provided'}`",
                    f"- Nested blocking receipt: `{kit.get('nestedBlockingReceipt') or 'not-provided'}`",
                    f"- Nested blocking status: `{kit.get('nestedBlockingStatus') or 'not-provided'}`",
                    f"- Nested blocking summary: {kit.get('nestedBlockingSummary') or 'not-provided'}",
                    f"- Fixture candidate proof counts as stable-v4 publication proof: `{fixture_boundary.get('fixtureCandidateProofCountsAsStableV4PublicationProof')}`",
                    "",
                    "| LaunchKey proof area | Receipt | Status | Stable-publication gate |",
                    "| --- | --- | --- | --- |",
                ]
            )
            if required_areas:
                for area in required_areas:
                    if isinstance(area, dict):
                        lines.append(
                            f"| {area.get('title') or area.get('id')} | `{area.get('receipt')}` | "
                            f"`{area.get('status')}` | `{area.get('stablePublicationGate')}` |"
                        )
            else:
                lines.append("| not-provided | not-provided | not-provided | not-provided |")
            if hygiene:
                lines.extend(
                    [
                        "",
                        "Package hygiene diagnostics:",
                        "",
                        f"- Status: `{hygiene.get('status') or 'not-provided'}`",
                        f"- Blocked findings: `{hygiene.get('blockedFindingCount')}`",
                        f"- Tarballs scanned: `{hygiene.get('tarballsScanned')}`",
                    ]
                )
                if first_finding:
                    lines.extend(
                        [
                            f"- First hygiene rule: `{first_finding.get('ruleId')}`",
                            f"- First hygiene tarball: `{first_finding.get('tarball')}`",
                            f"- First hygiene member: `{first_finding.get('member')}`",
                        ]
                    )
            lines.extend(["", "Repair criteria:", ""])
            for criterion in kit.get("repairCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Rerun the nested LaunchKey blocker:",
                    "",
                    "```bash",
                    str(kit.get("nestedRerunCommand") or launchkey_closure.get("nextCommand") or ""),
                    "```",
                    "",
                    "Rerun the full stable-publication gate after LaunchKey passes:",
                    "",
                    "```bash",
                    str(kit.get("stablePublicationRerunCommand") or ""),
                    "```",
                ]
            )
        asset_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "downloaded-release-assets"),
            None,
        )
        if isinstance(asset_closure, dict) and isinstance(asset_closure.get("releaseAssetClosureKit"), dict):
            kit = asset_closure["releaseAssetClosureKit"]
            boundary = kit.get("releaseAssetProofBoundary") if isinstance(kit.get("releaseAssetProofBoundary"), dict) else {}
            required_assets = kit.get("requiredAssets") if isinstance(kit.get("requiredAssets"), list) else []
            metadata_missing = kit.get("metadataMissingAssets") if isinstance(kit.get("metadataMissingAssets"), list) else []
            local_assets = kit.get("localAssetNames") if isinstance(kit.get("localAssetNames"), list) else []
            missing_local = kit.get("missingLocalAssets") if isinstance(kit.get("missingLocalAssets"), list) else []
            diagnostics = kit.get("currentReleaseAssetDiagnostics") if isinstance(kit.get("currentReleaseAssetDiagnostics"), dict) else {}
            lines.extend(
                [
                    "",
                    "### Release Asset Closure Kit",
                    "",
                    f"- Status: `{kit.get('status') or asset_closure.get('status') or 'not-provided'}`",
                    f"- Download source: `{kit.get('downloadSource') or 'not-provided'}`",
                    f"- Download proof status: `{kit.get('downloadProofStatus') or 'not-provided'}`",
                    f"- Release version: `{kit.get('version') or 'not-provided'}`",
                    f"- Assets directory: `{kit.get('assetsDir') or 'not-provided'}`",
                    f"- Required assets: `{', '.join(str(value) for value in required_assets) or 'not-provided'}`",
                    f"- Metadata missing assets: `{', '.join(str(value) for value in metadata_missing) or 'none'}`",
                    f"- Local downloaded assets: `{', '.join(str(value) for value in local_assets) or 'none'}`",
                    f"- Missing local assets: `{', '.join(str(value) for value in missing_local) or 'none'}`",
                    f"- Consumer report status: `{kit.get('consumerReportStatus') or 'not-provided'}`",
                    f"- Asset digest matrix path: `{kit.get('assetDigestMatrixPath') or 'not-provided'}`",
                    f"- Exit code: `{diagnostics.get('exitCode') if diagnostics.get('exitCode') is not None else 'not-provided'}`",
                    f"- Error: `{diagnostics.get('error') or 'none'}`",
                    f"- Downloaded or supplied assets required: `{boundary.get('downloadedOrSuppliedAssetsRequired')}`",
                    f"- GitHub metadata only counts as release-asset proof: `{boundary.get('githubMetadataOnlyCountsAsReleaseAssetProof')}`",
                    f"- Source-only proof counts as release-asset proof: `{boundary.get('sourceOnlyProofCountsAsReleaseAssetProof')}`",
                    f"- Fixture proof counts as stable-v4 publication proof: `{boundary.get('fixtureProofCountsAsStableV4PublicationProof')}`",
                    f"- Release asset upload command ready: `{kit.get('releaseAssetUploadCommandReady')}`",
                ]
            )
            lines.extend(["", "Repair criteria:", ""])
            for criterion in kit.get("repairCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Rerun release asset proof:",
                    "",
                    "```bash",
                    str(kit.get("downloadAssetsRerunCommand") or asset_closure.get("nextCommand") or ""),
                    "```",
                    "",
                    "Upload or replace public release assets manually when local release assets are complete:",
                    "",
                    "```bash",
                    str(kit.get("releaseAssetUploadCommand") or ""),
                    "```",
                ]
            )
            append_post_handoff_proof_markdown(
                lines,
                kit.get("postHandoffProof") if isinstance(kit.get("postHandoffProof"), dict) else {},
            )
            lines.extend(
                [
                    "",
                    "Rerun the full stable-publication gate after release assets pass:",
                    "",
                    "```bash",
                    str(kit.get("stablePublicationRerunCommand") or ""),
                    "```",
                ]
            )
        consumer_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "post-release-consumer-proof"),
            None,
        )
        if isinstance(consumer_closure, dict) and isinstance(consumer_closure.get("postReleaseConsumerClosureKit"), dict):
            kit = consumer_closure["postReleaseConsumerClosureKit"]
            boundary = kit.get("consumerProofBoundary") if isinstance(kit.get("consumerProofBoundary"), dict) else {}
            crosschecks = kit.get("publishedCrosschecks") if isinstance(kit.get("publishedCrosschecks"), dict) else {}
            missing_artifacts = kit.get("missingProofArtifacts") if isinstance(kit.get("missingProofArtifacts"), list) else []
            digest = kit.get("consumerDigestFreshness") if isinstance(kit.get("consumerDigestFreshness"), dict) else {}
            diagnostics = kit.get("currentConsumerDiagnostics") if isinstance(kit.get("currentConsumerDiagnostics"), dict) else {}
            lines.extend(
                [
                    "",
                    "### Post-Release Consumer Closure Kit",
                    "",
                    f"- Status: `{kit.get('status') or consumer_closure.get('status') or 'not-provided'}`",
                    f"- Consumer report status: `{kit.get('consumerReportStatus') or 'not-provided'}`",
                    f"- Consumer report path: `{kit.get('consumerReportPath') or 'not-provided'}`",
                    f"- Asset digest matrix path: `{kit.get('assetDigestMatrixPath') or 'not-provided'}`",
                    f"- Missing proof artifacts: `{', '.join(str(value) for value in missing_artifacts) or 'none'}`",
                    f"- Download source: `{kit.get('downloadSource') or 'not-provided'}`",
                    f"- Download proof status: `{kit.get('downloadProofStatus') or 'not-provided'}`",
                    f"- Release version: `{kit.get('version') or 'not-provided'}`",
                    f"- Assets directory: `{kit.get('assetsDir') or 'not-provided'}`",
                    f"- Consume output directory: `{kit.get('consumeOut') or 'not-provided'}`",
                    f"- Exit code: `{diagnostics.get('exitCode') if diagnostics.get('exitCode') is not None else 'not-provided'}`",
                    f"- Error: `{diagnostics.get('error') or 'none'}`",
                    f"- Digest freshness status: `{digest.get('status') or 'not-provided'}`",
                    f"- Required digest assets: `{', '.join(str(value) for value in digest.get('requiredAssetNames', []) if value) or 'not-provided'}`",
                    f"- Missing required digest assets: `{', '.join(str(value) for value in digest.get('missingRequiredAssetNames', []) if value) or 'none'}`",
                    f"- Missing SHA-256 digest assets: `{', '.join(str(value) for value in digest.get('missingSha256AssetNames', []) if value) or 'none'}`",
                    f"- Release tarball digest matches consumer artifact: `{digest.get('releaseTarballDigestMatchesConsumerArtifact')}`",
                    f"- Release-consume required: `{boundary.get('releaseConsumeRequired')}`",
                    f"- Asset digest matrix must cover required assets: `{boundary.get('assetDigestMatrixMustCoverRequiredAssets')}`",
                    f"- Release tarball digest must match consumer artifact: `{boundary.get('releaseTarballDigestMustMatchConsumerArtifact')}`",
                    f"- Source-only proof counts as consumer proof: `{boundary.get('sourceOnlyProofCountsAsConsumerProof')}`",
                    f"- Fixture proof counts as stable-v4 publication proof: `{boundary.get('fixtureProofCountsAsStableV4PublicationProof')}`",
                    "",
                    "| Consumer crosscheck | Status |",
                    "| --- | --- |",
                    f"| Replay | `{kit.get('replayStatus') or 'not-provided'}` |",
                    f"| Attestation | `{kit.get('attestationStatus') or 'not-provided'}` |",
                    f"| Published replay report | `{crosschecks.get('replayReport') or 'not-provided'}` |",
                    f"| Published attestation | `{crosschecks.get('attestation') or 'not-provided'}` |",
                    f"| Published badge | `{crosschecks.get('attestationBadge') or 'not-provided'}` |",
                ]
            )
            lines.extend(["", "Repair criteria:", ""])
            for criterion in kit.get("repairCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Rerun release-consume proof:",
                    "",
                    "```bash",
                    str(kit.get("releaseConsumeRerunCommand") or consumer_closure.get("nextCommand") or ""),
                    "```",
                    "",
                    "Rerun the full stable-publication gate after consumer proof passes:",
                    "",
                    "```bash",
                    str(kit.get("stablePublicationRerunCommand") or ""),
                    "```",
                ]
            )
        freshness_closure = next(
            (item for item in items if isinstance(item, dict) and item.get("id") == "public-release-freshness"),
            None,
        )
        if isinstance(freshness_closure, dict) and isinstance(freshness_closure.get("releaseFreshnessClosureKit"), dict):
            kit = freshness_closure["releaseFreshnessClosureKit"]
            boundary = kit.get("freshnessProofBoundary") if isinstance(kit.get("freshnessProofBoundary"), dict) else {}
            comparisons = kit.get("comparisons") if isinstance(kit.get("comparisons"), dict) else {}
            problems = kit.get("problems") if isinstance(kit.get("problems"), list) else []
            lines.extend(
                [
                    "",
                    "### Public Release Freshness Closure Kit",
                    "",
                    f"- Status: `{kit.get('status') or freshness_closure.get('status') or 'not-provided'}`",
                    f"- Release tag: `{kit.get('releaseTag') or 'not-provided'}`",
                    f"- Release URL: `{kit.get('releaseUrl') or 'not-provided'}`",
                    f"- Published at: `{kit.get('publishedAt') or 'not-provided'}`",
                    f"- Release target commitish: `{kit.get('releaseTargetCommitish') or 'not-provided'}`",
                    f"- Tag target SHA: `{kit.get('tagTargetSha') or 'not-provided'}`",
                    f"- Tag target proof status: `{kit.get('tagTargetProofStatus') or 'not-provided'}`",
                    f"- Release manifest path: `{kit.get('releaseManifestPath') or 'not-provided'}`",
                    f"- Manifest version: `{kit.get('manifestVersion') or 'not-provided'}`",
                    f"- Manifest tag: `{kit.get('manifestTag') or 'not-provided'}`",
                    f"- Manifest commit: `{kit.get('manifestCommit') or 'not-provided'}`",
                    f"- Manifest generated at: `{kit.get('manifestGeneratedAt') or 'not-provided'}`",
                    f"- Artifact: `{kit.get('artifactName') or 'not-provided'}`",
                    f"- Artifact SHA-256: `{kit.get('artifactSha256') or 'not-provided'}`",
                    f"- Public tag target required: `{boundary.get('publicGitHubTagTargetRequired')}`",
                    f"- Release manifest required: `{boundary.get('releaseManifestRequired')}`",
                    f"- Source-only proof counts as freshness proof: `{boundary.get('sourceOnlyProofCountsAsFreshnessProof')}`",
                    f"- Fixture API proof counts as stable-v4 publication proof: `{boundary.get('fixtureApiProofCountsAsStableV4PublicationProof')}`",
                    "",
                    "| Freshness comparison | Status |",
                    "| --- | --- |",
                ]
            )
            if comparisons:
                for key, value in comparisons.items():
                    lines.append(f"| `{key}` | `{value}` |")
            else:
                lines.append("| `not-provided` | `not-provided` |")
            lines.extend(["", "Freshness problems:", ""])
            if problems:
                for problem in problems:
                    lines.append(f"- {problem}")
            else:
                lines.append("- none")
            lines.extend(["", "Repair criteria:", ""])
            for criterion in kit.get("repairCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Rerun public release freshness proof:",
                    "",
                    "```bash",
                    str(kit.get("freshnessRerunCommand") or freshness_closure.get("nextCommand") or ""),
                    "```",
                ]
            )
        evidence_closure_items = [
            item
            for item in items
            if isinstance(item, dict)
            and item.get("id") in {"independent-adoption-evidence", "final-security-review-evidence"}
            and isinstance(item.get("evidenceClosureKit"), dict)
        ]
        for item in evidence_closure_items:
            kit = item.get("evidenceClosureKit") if isinstance(item.get("evidenceClosureKit"), dict) else {}
            diagnostics = (
                kit.get("currentEvidenceDiagnostics")
                if isinstance(kit.get("currentEvidenceDiagnostics"), dict)
                else {}
            )
            first_record = (
                diagnostics.get("firstRecord")
                if isinstance(diagnostics.get("firstRecord"), dict)
                else {}
            )
            required_fields = ", ".join(str(field) for field in kit.get("requiredFields", [])) or "not-provided"
            accepted_classes = ", ".join(str(value) for value in kit.get("acceptedEvidenceClasses", [])) or "not-provided"
            required_scope = ", ".join(str(value) for value in kit.get("requiredScope", [])) or "not-required"
            lines.extend(
                [
                    "",
                    f"### Evidence Closure Kit: `{item.get('id')}`",
                    "",
                    f"- Starter path: `{kit.get('starterPath') or 'not-provided'}`",
                    f"- Template path: `{kit.get('templatePath') or 'not-provided'}`",
                    f"- Attach argument: `{kit.get('attachArgument') or 'not-provided'}`",
                    f"- Accepted evidence classes: `{accepted_classes}`",
                    f"- Required fields: `{required_fields}`",
                    f"- Required scope: `{required_scope}`",
                    f"- Private data redacted required: `{(kit.get('redactionBoundary') or {}).get('privateDataRedactedMustBeTrue')}`",
                    f"- Current gate: `{diagnostics.get('stableV4GateStatus') or diagnostics.get('status') or 'not-provided'}`",
                    f"- Current error: `{diagnostics.get('error') or 'none'}`",
                    f"- Evidence records: `{diagnostics.get('recordCount')}` total, `{diagnostics.get('validRecordCount')}` valid, `{diagnostics.get('stableV4EligibleEvidenceCount')}` stable-v4 eligible",
                ]
            )
            if first_record:
                first_errors = ", ".join(str(value) for value in first_record.get("errors", [])) or "none"
                missing_fields = ", ".join(str(value) for value in first_record.get("missingFields", [])) or "none"
                missing_scope = ", ".join(str(value) for value in first_record.get("missingStableScope", [])) or "none"
                lines.extend(
                    [
                        f"- First record missing fields: `{missing_fields}`",
                        f"- First record errors: `{first_errors}`",
                        f"- First record missing security scope: `{missing_scope}`",
                    ]
                )
            lines.extend(["", "Pass criteria:", ""])
            for criterion in kit.get("passCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(["", "Fail criteria:", ""])
            for criterion in kit.get("failCriteria", []):
                lines.append(f"- {criterion}")
            lines.extend(
                [
                    "",
                    "Rerun after attaching real evidence:",
                    "",
                    "```bash",
                    str(kit.get("rerunCommand") or item.get("nextCommand") or ""),
                    "```",
                ]
            )
    launchkey_blocker = {}
    release_candidate_proof = report.get("releaseCandidatePacketProof")
    if isinstance(release_candidate_proof, dict) and isinstance(release_candidate_proof.get("launchKeyBlockingProof"), dict):
        launchkey_blocker = release_candidate_proof["launchKeyBlockingProof"]
    if launchkey_blocker:
        hygiene = launchkey_blocker.get("packageHygieneEvidence") if isinstance(launchkey_blocker.get("packageHygieneEvidence"), dict) else {}
        first_finding = hygiene.get("firstFinding") if isinstance(hygiene.get("firstFinding"), dict) else {}
        lines.extend(
            [
                "",
                "## LaunchKey Candidate Blocker",
                "",
                f"- Receipt: `{launchkey_blocker.get('receipt')}`",
                f"- Status: `{launchkey_blocker.get('status')}`",
                f"- Summary: {launchkey_blocker.get('summary') or launchkey_blocker.get('failure') or 'LaunchKey candidate proof did not pass.'}",
            ]
        )
        if launchkey_blocker.get("failureEvidence"):
            lines.append(f"- Failure evidence: `{launchkey_blocker.get('failureEvidence')}`")
        if first_finding:
            lines.extend(
                [
                    f"- Hygiene rule: `{first_finding.get('ruleId')}`",
                    f"- Hygiene tarball: `{first_finding.get('tarball')}`",
                    f"- Hygiene member: `{first_finding.get('member')}`",
                    f"- Blocked hygiene findings: `{hygiene.get('blockedFindingCount')}`",
                ]
            )
        if launchkey_blocker.get("nextCommand"):
            lines.extend(["", "Next command:", "", "```bash", str(launchkey_blocker.get("nextCommand") or ""), "```"])
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
                f"- Release URL: `{release_notes_kit.get('releaseUrl') or 'not-provided'}`",
                f"- Public release edit command: `{release_notes_kit.get('publicReleaseEditCommand') or 'not-provided'}`",
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
                f"- Release version: `{starter_kit.get('releaseVersion') or report.get('releaseVersion') or 'unknown'}`",
                "",
                "| File | Purpose |",
                "| --- | --- |",
            ]
        )
        for item in starter_kit.get("files", []):
            if isinstance(item, dict):
                lines.append(f"| `{item.get('path')}` | {item.get('purpose')} |")
        related = starter_kit.get("relatedAuthoringKits")
        if isinstance(related, list) and related:
            lines.extend(["", "| Related kit | Status | Missing topics |", "| --- | --- | --- |"])
            for item in related:
                if isinstance(item, dict):
                    missing = ", ".join(str(topic) for topic in item.get("missingTopicIds", [])) or "none"
                    lines.append(f"| `{item.get('directory')}` | `{item.get('status')}` | {missing} |")
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
            f"- Public release freshness: `{report.get('publicReleaseFreshnessProof', {}).get('status')}`",
            f"- Release version coherence: `{report.get('releaseVersionCoherenceProof', {}).get('status')}`",
            f"- Release asset coherence: `{report.get('releaseAssetCoherenceProof', {}).get('status')}`",
            f"- Public evidence closure: `{report.get('publicEvidenceClosureProof', {}).get('status')}`",
            f"- External adoption stable gate: `{report.get('externalAdoptionEvidenceProof', {}).get('stableV4GateStatus')}`",
            f"- External adoption freshness: `{(report.get('externalAdoptionEvidenceProof', {}).get('evidencePacketFreshness') or {}).get('status')}`",
            f"- Security review stable gate: `{report.get('securityReviewEvidenceProof', {}).get('stableV4GateStatus')}`",
            f"- Security review freshness: `{(report.get('securityReviewEvidenceProof', {}).get('evidencePacketFreshness') or {}).get('status')}`",
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
