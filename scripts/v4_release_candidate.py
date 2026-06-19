#!/usr/bin/env python3
"""Generate the ShipGuard v4 release-candidate readiness report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown


SURFACE = "ShipGuard V4 Release Candidate Readiness"
TOOL = "shipguard v4 release-candidate"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def contains_all(text: str, phrases: list[str]) -> bool:
    lower = text.lower()
    return all(phrase.lower() in lower for phrase in phrases)


def scrub_value(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: scrub_value(child, replacements) for key, child in value.items()}
    if isinstance(value, list):
        return [scrub_value(child, replacements) for child in value]
    if isinstance(value, str):
        result = value
        for source, replacement in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            result = result.replace(source, replacement)
        return result
    return value


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    title: str,
    passed: bool,
    evidence: list[str],
    recommendation: str,
    required: bool = True,
) -> None:
    checks.append(
        {
            "id": check_id,
            "title": title,
            "status": "pass" if passed else "review",
            "required": required,
            "evidence": evidence,
            "recommendation": recommendation,
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def short_output(value: str, limit: int = 1200) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def build_published_release_asset_proof(args: argparse.Namespace, root: Path, version: str) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--release-assets <downloaded-assets-dir> --release-version <version> --shipguard-eval --shareable"
    )
    consume_command_template = (
        "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> "
        "--out <consume-dir> --version <version>"
    )
    if not args.release_assets:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No downloaded release assets were supplied; stable v4 proof still needs consumer-side release asset verification.",
            "nextCommand": command_template,
            "consumeCommand": consume_command_template,
        }

    assets_dir = Path(args.release_assets).expanduser().resolve()
    consume_out = (
        Path(args.release_consume_out).expanduser().resolve()
        if args.release_consume_out
        else Path(args.out).expanduser().resolve() / "release-consume"
    )
    release_version = args.release_version or version
    command = [
        str(root / "bin" / "shipguard"),
        "release-consume",
        "verify",
        "--dir",
        str(assets_dir),
        "--out",
        str(consume_out),
        "--version",
        release_version,
    ]

    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "assetsDir": assets_dir.as_posix(),
        "consumeOut": consume_out.as_posix(),
        "version": release_version,
        "command": " ".join(command),
        "commandTemplate": consume_command_template,
        "nextCommand": "./tests/v4_release_candidate_test.sh",
        "consumerReport": "consumer-report.json",
        "assetDigestMatrix": "asset-digests.json",
    }
    if not assets_dir.exists():
        proof["summary"] = "Downloaded release assets directory was not found."
        proof["error"] = f"release assets directory not found: {assets_dir}"
        return proof
    if not (root / "bin" / "shipguard").exists():
        proof["summary"] = "ShipGuard CLI was not found in the inspected checkout."
        proof["error"] = "bin/shipguard not found"
        return proof

    try:
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        proof["summary"] = "Consumer-side release asset verification timed out."
        proof["exitCode"] = "timeout"
        proof["stdout"] = short_output(exc.stdout or "")
        proof["stderr"] = short_output(exc.stderr or "")
        return proof

    consumer_report = load_json(consume_out / "consumer-report.json")
    digest_report = load_json(consume_out / "asset-digests.json")
    consumer_status = consumer_report.get("status")
    consumer_summary = consumer_report.get("summary") if isinstance(consumer_report.get("summary"), dict) else {}
    published_summary = consumer_report.get("published") if isinstance(consumer_report.get("published"), dict) else {}
    proof.update(
        {
            "exitCode": completed.returncode,
            "stdout": short_output(completed.stdout),
            "stderr": short_output(completed.stderr),
            "consumerReportStatus": consumer_status or "missing",
            "consumerReportPath": (consume_out / "consumer-report.json").as_posix(),
            "assetDigestMatrixPath": (consume_out / "asset-digests.json").as_posix(),
            "artifactSha256": consumer_report.get("artifact_sha256") or consumer_report.get("artifact", {}).get("sha256"),
            "replayStatus": consumer_report.get("replay_status") or consumer_summary.get("replay_status"),
            "attestationStatus": consumer_report.get("attestation_status") or consumer_summary.get("attestation_status"),
            "publishedReplayCrosscheck": consumer_report.get("published_assets", {}).get("replay_report") or published_summary.get("replay_report"),
            "publishedAttestationCrosscheck": consumer_report.get("published_assets", {}).get("attestation") or published_summary.get("attestation"),
            "publishedBadgeCrosscheck": consumer_report.get("published_assets", {}).get("attestation_badge") or published_summary.get("attestation_badge"),
            "assetCount": len(digest_report.get("assets", [])) if isinstance(digest_report.get("assets"), list) else None,
        }
    )
    if completed.returncode == 0 and consumer_status == "pass":
        proof["status"] = "pass"
        proof["summary"] = "Supplied downloaded release assets passed consumer-side verification."
    else:
        proof["summary"] = "Supplied downloaded release assets did not pass consumer-side verification."
    return proof


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    home = Path.home().resolve()

    version = read_text(root / "VERSION").strip() or "unknown"
    bin_text = read_text(root / "bin" / "shipguard")
    cli_text = read_text(root / "docs" / "cli.md")
    matrix_text = read_text(root / "docs" / "command-matrix.md")
    rc_doc_text = read_text(root / "docs" / "v4-release-candidate.md")
    schema_doc_text = read_text(root / "docs" / "v4-schema-freeze.md")
    release_consume_doc_text = read_text(root / "docs" / "release-consume.md")
    release_proof_doc_text = read_text(root / "docs" / "release-proof.md")
    install_text = read_text(root / "scripts" / "install.sh")
    package_text = read_text(root / "scripts" / "package_release.sh")
    package_test_text = read_text(root / "tests" / "package_release_test.sh")
    gauntlet_text = read_text(root / "scripts" / "tool_value_gauntlet.py")
    report_quality_text = read_text(root / "scripts" / "ios_report_quality.py")
    self_audit_text = read_text(root / "scripts" / "self_audit.sh")
    plugin_text = read_text(root / "plugins" / "ios-shipguard" / "skills" / "ios-shipguard" / "SKILL.md")
    changelog_text = read_text(root / "CHANGELOG.md")

    published_release_asset_proof = build_published_release_asset_proof(args, root, version)

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "release-candidate-command-routed",
        "CLI route is public",
        "release-candidate" in bin_text and TOOL in cli_text,
        ["bin/shipguard", "docs/cli.md"],
        "Route `shipguard v4 release-candidate` through the public CLI and CLI docs.",
    )
    add_check(
        checks,
        "release-candidate-contract-documented",
        "Release-candidate contract is documented",
        contains_all(
            rc_doc_text,
            [
                "fresh install",
                "upgrade",
                "uninstall",
                "release proof consumption",
                "external adoption packet",
                "plugin refresh proof",
            ],
        ),
        ["docs/v4-release-candidate.md"],
        "Document the install, upgrade, uninstall, release-consume, adoption, and plugin-refresh proof contract.",
    )
    add_check(
        checks,
        "fresh-install-proof-present",
        "Fresh install proof path is present",
        contains_all(install_text + package_test_text, ["install", "prefix"])
        and "adoptionReceipts" in gauntlet_text
        and "fresh-user adoption" in gauntlet_text,
        ["scripts/install.sh", "tests/package_release_test.sh", "scripts/tool_value_gauntlet.py"],
        "Keep a runnable fresh-package install proof so a new user can validate ShipGuard without maintainer context.",
    )
    add_check(
        checks,
        "upgrade-proof-present",
        "Upgrade proof path is present",
        "upgrade" in rc_doc_text.lower() and contains_all(package_test_text, ["package_name", "install.sh", "version"]),
        ["docs/v4-release-candidate.md", "tests/package_release_test.sh"],
        "Make the release candidate report point at concrete upgrade verification instead of only saying upgrades are supported.",
    )
    add_check(
        checks,
        "uninstall-proof-present",
        "Uninstall proof path is present",
        "uninstall" in rc_doc_text.lower() and ("rm -rf" in rc_doc_text or "remove" in rc_doc_text.lower()),
        ["docs/v4-release-candidate.md"],
        "Keep uninstall proof explicit so ShipGuard does not leave hidden state as an adoption blocker.",
    )
    add_check(
        checks,
        "release-proof-consumption-present",
        "Release proof consumption is present",
        "release-consume verify" in release_consume_doc_text and "release-proof build" in release_proof_doc_text,
        ["docs/release-consume.md", "docs/release-proof.md"],
        "Require consumer-side release proof verification before treating a release candidate as shippable.",
    )
    add_check(
        checks,
        "external-adoption-packet-present",
        "External adoption packet is present",
        contains_all(rc_doc_text, ["external adoption packet", "first command", "support boundary", "proof bundle"]),
        ["docs/v4-release-candidate.md"],
        "Give external users one packet with first command, proof bundle, support boundary, and non-claims.",
    )
    add_check(
        checks,
        "final-schema-docs-present",
        "Final schema docs are present",
        contains_all(schema_doc_text, ["compatibility policy", "migration checks", "deprecation policy"]),
        ["docs/v4-schema-freeze.md"],
        "Keep the schema freeze docs linked from release-candidate readiness so v4 does not drift after the freeze.",
    )
    add_check(
        checks,
        "plugin-refresh-proof-present",
        "Plugin refresh proof is present",
        "codex status --strict" in rc_doc_text.lower() and "codex status --strict" in plugin_text.lower(),
        ["docs/v4-release-candidate.md", "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md"],
        "Make plugin refresh proof visible in the release-candidate path, including the installed Codex plugin check.",
    )
    add_check(
        checks,
        "release-candidate-gauntlet-receipts-present",
        "Value gauntlet has release-candidate receipts",
        "v4ReleaseCandidateReadinessReceipts" in gauntlet_text and "runtimeV4ReleaseCandidateReadiness" in gauntlet_text,
        ["scripts/tool_value_gauntlet.py"],
        "Add a runtime receipt family so release-candidate readiness is measured by command proof.",
    )
    add_check(
        checks,
        "release-candidate-report-quality-present",
        "Report-quality accepts release-candidate reports",
        TOOL in report_quality_text,
        ["scripts/ios_report_quality.py"],
        "Allow report-quality to score the v4 release-candidate readiness report as a root ShipGuard report.",
    )
    add_check(
        checks,
        "release-candidate-self-audit-package-present",
        "Self-audit and package proof include the surface",
        "v4 release-candidate --help" in self_audit_text
        and "tests/v4_release_candidate_test.sh" in package_test_text
        and "scripts/v4_release_candidate.py" in package_test_text,
        ["scripts/self_audit.sh", "tests/package_release_test.sh"],
        "Include the command, script, docs, test, and receipt fixture in self-audit and package proof.",
    )
    add_check(
        checks,
        "release-candidate-command-matrix-present",
        "Command matrix exposes the release-candidate surface",
        "v4 release-candidate" in matrix_text,
        ["docs/command-matrix.md"],
        "Add release-candidate readiness to the command matrix so the v4 path is discoverable.",
    )
    add_check(
        checks,
        "release-candidate-changelog-present",
        "Changelog records the readiness gate",
        contains_all(changelog_text, ["v3.131", "release-candidate", "install"]),
        ["CHANGELOG.md"],
        "Record the release-candidate readiness gate in the changelog.",
    )
    if published_release_asset_proof["provided"]:
        add_check(
            checks,
            "published-release-assets-consumed",
            "Supplied release assets pass consumer proof",
            published_release_asset_proof["status"] == "pass",
            ["release-consume verify", "consumer-report.json", "asset-digests.json"],
            "Run consumer-side release proof against downloaded assets before using release-candidate readiness as stable-v4 evidence.",
        )

    required_checks = [check for check in checks if check["required"]]
    failed_required = [check for check in required_checks if check["status"] != "pass"]
    status = "pass" if not failed_required else "review"

    readiness_proof = {
        "freshInstall": {
            "status": "pass" if any(check["id"] == "fresh-install-proof-present" and check["status"] == "pass" for check in checks) else "review",
            "commands": [
                "./scripts/package_release.sh",
                "tar -tzf <release-tarball>",
                "<package>/scripts/install.sh --prefix <tmp-prefix>",
                "<tmp-prefix>/bin/shipguard validate <package>",
            ],
        },
        "upgrade": {
            "status": "pass" if any(check["id"] == "upgrade-proof-present" and check["status"] == "pass" for check in checks) else "review",
            "commands": [
                "shipguard version",
                "./scripts/install.sh --prefix <existing-prefix>",
                "<existing-prefix>/bin/shipguard version",
            ],
        },
        "uninstall": {
            "status": "pass" if any(check["id"] == "uninstall-proof-present" and check["status"] == "pass" for check in checks) else "review",
            "commands": [
                "rm -rf <tmp-prefix>",
                "test ! -e <tmp-prefix>/bin/shipguard",
            ],
        },
        "releaseProofConsumption": {
            "status": "pass" if any(check["id"] == "release-proof-consumption-present" and check["status"] == "pass" for check in checks) else "review",
            "commands": [
                "./bin/shipguard release-proof build --out <proof-dir> --release-url <url> --version <version> --tag <tag> --commit <sha> --ci-run-url <url>",
                "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>",
            ],
        },
        "externalAdoptionPacket": {
            "status": "pass" if any(check["id"] == "external-adoption-packet-present" and check["status"] == "pass" for check in checks) else "review",
            "artifacts": ["README.md", "docs/v4-release-candidate.md", "docs/cli.md", "release proof bundle"],
        },
        "finalSchemaDocs": {
            "status": "pass" if any(check["id"] == "final-schema-docs-present" and check["status"] == "pass" for check in checks) else "review",
            "artifacts": ["docs/v4-schema-freeze.md", "docs/compatibility.md"],
        },
        "pluginRefreshProof": {
            "status": "pass" if any(check["id"] == "plugin-refresh-proof-present" and check["status"] == "pass" for check in checks) else "review",
            "commands": [
                "codex plugin marketplace add .",
                "codex plugin add ios-shipguard@shipguard",
                "./bin/shipguard codex status --strict",
            ],
        },
    }
    release_readiness = {
        "currentVersion": version,
        "targetVersion": "4.0.0",
        "productStage": "v4-release-candidate-readiness",
        "releaseClaim": "candidate-ready" if status == "pass" else "not-ready",
        "stableV4Release": False,
        "publishedReleaseAssetProof": published_release_asset_proof["status"],
        "publishedReleaseAssetsRequiredForStableV4": True,
        "requiredProofCommands": [
            "git diff --check",
            "./tests/v4_release_candidate_test.sh",
            "./tests/tool_value_gauntlet_test.sh",
            "./bin/shipguard validate",
            "./bin/shipguard docs-check . --out /tmp/shipguard-docs-check",
            "./tests/self_audit_test.sh",
            "./tests/cli_smoke_test.sh",
            "./tests/package_release_test.sh",
            "codex plugin marketplace add .",
            "codex plugin add ios-shipguard@shipguard",
            "./bin/shipguard codex status --strict",
            "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>",
        ],
    }
    external_adoption_packet = {
        "firstCommand": "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --shipguard-eval --shareable",
        "supportBoundary": "ShipGuard gives an external developer local proof and report-quality checks; it does not run private app remediation unless explicitly asked.",
        "proofBundle": ["release manifest", "release index", "release replay", "release consume report", "self-audit report"],
        "nonClaims": [
            "No OpenAI marketplace acceptance is claimed.",
            "No third-party adoption is claimed by this local readiness report.",
            "No private app validation is part of this ShipGuard product QA run.",
        ],
    }
    blocked_claims = [
        "This proves release-candidate readiness, not a stable v4 product release.",
        "Marketplace acceptance, broad external adoption, and third-party security review remain outside this local report.",
        "Private Ringly or Ilmify app validation is not part of this report.",
        "Physical-device iOS proof is not implied by package, docs, or local fixture proof.",
    ]
    scope_boundary = {
        "shipguardOnly": True,
        "targetAppsReadOnly": True,
        "privateAppsUsed": False,
        "doesNotEditTargetApps": True,
        "doesNotPush": True,
        "doesNotPublishRelease": True,
        "shareable": bool(args.shareable),
    }
    report_quality_questions = [
        "Can a fresh user install, upgrade, uninstall, and validate ShipGuard from the release package without maintainer context?",
        "Can a consumer download release assets and independently verify the manifest, tarball SHA-256, replay, and attestation?",
        "Does the adoption packet tell an external developer the first command, proof bundle, support boundary, and non-claims?",
        "What stable v4 product release proof remains after release-candidate readiness passes?",
    ]
    if status == "pass" and published_release_asset_proof["status"] == "not-provided":
        priority_action = (
            "Attach downloaded release assets to the v4 product release candidate before any stable v4 claim; "
            "external adoption evidence, final security review, package proof, rollback proof, and release proof consumption still remain stabilization gates."
        )
        next_command = published_release_asset_proof["nextCommand"]
        summary = (
            "ShipGuard has release-candidate readiness proof, but no downloaded release assets were supplied for consumer-side stable-v4 proof."
        )
        proof_source = "v4 release-candidate checks plus documented release-consume boundary; published asset proof not supplied"
    elif status == "pass":
        priority_action = (
            "Use the passing release-asset consumer receipt as one v4 stabilization input, then finish external adoption evidence, final security review, package proof, and rollback proof."
        )
        next_command = "./tests/v4_release_candidate_test.sh"
        summary = "ShipGuard has release-candidate readiness proof and supplied release assets passed consumer-side verification."
        proof_source = "v4 release-candidate checks plus release-consume consumer-report and asset digest matrix"
    else:
        priority_action = "Complete the missing release-candidate readiness checks before calling v4 candidate-ready."
        next_command = "./tests/v4_release_candidate_test.sh"
        summary = "ShipGuard v4 release-candidate readiness still has missing proof."
        proof_source = "v4 release-candidate checks, value-gauntlet receipts, docs, package proof hooks, and release-consume boundaries"
    result_ux = build_result_ux(
        status=status,
        summary=summary,
        proof_source=proof_source,
        why_it_matters="This removes manual interpretation from the v4 gate: a release candidate must be installable, consumable, and externally understandable.",
        next_command=next_command,
        next_action_summary=priority_action,
    )
    result_ux["priorityAction"] = priority_action

    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "tool": TOOL,
        "surface": SURFACE,
        "version": version,
        "repo": root.as_posix(),
        "status": status,
        "productStage": "v4-release-candidate-readiness",
        "checks": checks,
        "readinessProof": readiness_proof,
        "installProof": readiness_proof["freshInstall"],
        "upgradeProof": readiness_proof["upgrade"],
        "uninstallProof": readiness_proof["uninstall"],
        "releaseProofConsumption": readiness_proof["releaseProofConsumption"],
        "publishedReleaseAssetProof": published_release_asset_proof,
        "externalAdoptionPacket": external_adoption_packet,
        "finalSchemaDocs": readiness_proof["finalSchemaDocs"],
        "pluginRefreshProof": readiness_proof["pluginRefreshProof"],
        "releaseReadiness": release_readiness,
        "blockedClaims": blocked_claims,
        "scopeBoundary": scope_boundary,
        "reportQualityQuestions": report_quality_questions,
        "resultUX": result_ux,
    }
    if args.shipguard_eval:
        report["shipguardEval"] = {
            "mode": "ShipGuard product QA",
            "allowedInput": "ShipGuard source tree and public fixtures",
            "forbiddenOutput": "Private target-app edits, unproven stable-v4 release claims, or marketplace acceptance claims",
            "nextImprovement": priority_action,
        }
    if args.shareable:
        replacements = {
            root.as_posix(): "<repo>",
            home.as_posix(): "<home>",
        }
        if published_release_asset_proof.get("assetsDir"):
            replacements[str(published_release_asset_proof["assetsDir"])] = "<release-assets>"
        if published_release_asset_proof.get("consumeOut"):
            replacements[str(published_release_asset_proof["consumeOut"])] = "<release-consume-out>"
        report = scrub_value(report, replacements)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ShipGuard V4 Release Candidate Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Product stage: `{report['productStage']}`",
        f"- Release claim: `{report['releaseReadiness']['releaseClaim']}`",
        f"- Stable v4 release: `{report['releaseReadiness']['stableV4Release']}`",
        f"- Version inspected: `{report['version']}`",
        "",
        *render_result_markdown(report["resultUX"]),
        "## Readiness Proof",
        "",
    ]
    for key, proof in report["readinessProof"].items():
        title = key[0].upper() + key[1:]
        lines.append(f"- {title}: `{proof.get('status')}`")
    lines.extend(["", "## Fresh Install", ""])
    for command in report["installProof"].get("commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Upgrade", ""])
    for command in report["upgradeProof"].get("commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Uninstall", ""])
    for command in report["uninstallProof"].get("commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Release Proof Consumption", ""])
    for command in report["releaseProofConsumption"].get("commands", []):
        lines.append(f"- `{command}`")
    proof = report["publishedReleaseAssetProof"]
    lines.extend(["", "## Published Release Asset Proof", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Version: `{proof.get('version')}`")
        lines.append(f"- Consumer report status: `{proof.get('consumerReportStatus')}`")
        lines.append(f"- Replay status: `{proof.get('replayStatus')}`")
        lines.append(f"- Attestation status: `{proof.get('attestationStatus')}`")
        if proof.get("artifactSha256"):
            lines.append(f"- Artifact SHA-256: `{proof.get('artifactSha256')}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## External Adoption Packet", ""])
    packet = report["externalAdoptionPacket"]
    lines.append(f"- First command: `{packet['firstCommand']}`")
    lines.append(f"- Support boundary: {packet['supportBoundary']}")
    lines.append(f"- Proof bundle: {', '.join(packet['proofBundle'])}")
    for claim in packet["nonClaims"]:
        lines.append(f"- {claim}")
    lines.extend(["", "## Plugin Refresh Proof", ""])
    for command in report["pluginRefreshProof"].get("commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Release Readiness", ""])
    for command in report["releaseReadiness"]["requiredProofCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Blocked Claims", ""])
    for claim in report["blockedClaims"]:
        lines.append(f"- {claim}")
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        marker = "pass" if check["status"] == "pass" else "review"
        lines.append(f"- `{marker}` {check['title']}: {check['recommendation']}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    if "shipguardEval" in report:
        lines.extend(
            [
                "",
                "## Scope Boundary",
                "",
                "- This is ShipGuard product QA, not a target-app remediation task.",
                "- Release-candidate readiness can pass while stable v4 product release remains blocked.",
                "- Shareable reports must not include private app source, local paths, screenshots, or tokens.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ShipGuard v4 release-candidate readiness reports.")
    parser.add_argument("--path", default=".", help="ShipGuard repository path. Defaults to current directory.")
    parser.add_argument("--out", required=True, help="Output directory for v4-release-candidate reports.")
    parser.add_argument("--release-assets", help="Optional downloaded release assets directory to verify with release-consume.")
    parser.add_argument("--release-version", help="Version to use when verifying --release-assets. Defaults to VERSION.")
    parser.add_argument("--release-consume-out", help="Output directory for embedded release-consume proof. Defaults under --out.")
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
        (out_dir / "v4-release-candidate.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_markdown:
        (out_dir / "v4-release-candidate.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
