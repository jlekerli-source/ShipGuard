#!/usr/bin/env python3
"""Generate the ShipGuard v4 stable-publication proof report."""

from __future__ import annotations

import argparse
import json
import os
import re
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
        "version": release_version,
        "tag": release_tag,
        "apiUrl": args.github_api_url.rstrip("/"),
        "requiredAssets": sorted(REQUIRED_RELEASE_ASSETS | {f"shipguard-v{normalize_version(release_version)}.tar.gz"}),
        "nextCommand": stable_publication_command(args, placeholders=True),
    }
    if not args.github_release_repo:
        proof["status"] = "not-provided"
        proof["summary"] = "No GitHub release repository was supplied."
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
            "releaseNotesPreview": launchkey.short_output(body, 700),
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


def build_release_notes_proof(metadata_proof: dict[str, Any]) -> dict[str, Any]:
    body = str(metadata_proof.get("releaseNotesPreview") or "")
    normalized = re_normalized(body)
    stable_terms = ("stable-v4" in normalized or "stable v4" in normalized) and (
        "release proof" in normalized or "publication" in normalized or "stable release" in normalized
    )
    pass_status = metadata_proof.get("status") == "pass" and stable_terms
    return {
        "status": "pass" if pass_status else "review",
        "requiredForStableV4": True,
        "summary": (
            "Release notes explicitly describe stable-v4 publication proof."
            if pass_status
            else "Release notes do not yet explicitly describe stable-v4 publication proof."
        ),
        "releaseNotesLength": metadata_proof.get("releaseNotesLength", 0),
        "requiredLanguage": "Mention stable-v4 publication plus release proof or stable-release proof boundaries.",
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


def build_stable_publication_evidence_packet(
    *,
    gates: list[tuple[str, dict[str, Any], str]],
    blocked: tuple[str, dict[str, Any], str] | None,
    release_version: str,
    stable_v4_release: bool,
) -> dict[str, Any]:
    required_evidence: list[dict[str, Any]] = []
    for receipt, proof, command in gates:
        status = str(proof.get("status") or "not-provided")
        required_evidence.append(
            {
                "id": evidence_id_for_receipt(receipt),
                "receipt": receipt,
                "status": status,
                "provided": bool(proof.get("provided", status == "pass")),
                "requiredForStableV4": True,
                "realEvidenceRequired": True,
                "summary": proof.get("summary") or f"{receipt} status is {status}.",
                "nextCommand": command,
            }
        )

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
    evidence_packet = build_stable_publication_evidence_packet(
        gates=gates,
        blocked=blocked,
        release_version=release_version,
        stable_v4_release=stable_v4_release,
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
        "productStage": "v4-stable-publication-proof",
        "stableV4Release": stable_v4_release,
        "stablePublicationEvidencePacket": evidence_packet,
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
        ],
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "privateAppsUsed": False,
            "doesNotEditTargetApps": True,
            "doesNotPublishRelease": True,
            "shareable": bool(args.shareable),
        },
        "reportQualityQuestions": [
            "Can ShipGuard prove stable-v4 publication from real release metadata, release notes, downloaded assets, external adoption evidence, security evidence, and post-release consumer proof?",
            "Does the stable-publication report block every stable-v4 claim until independent adoption and final security evidence are attached?",
            "Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?",
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
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
