#!/usr/bin/env python3
"""Generate a local Shipguard threat model for Codex iOS workflows."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-threat-model: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Shipguard for Codex threat model for plugin, preview, Devspace, report, and release surfaces."
    )
    parser.add_argument("--path", default=".", help="Repository root to inspect")
    parser.add_argument("--out", required=True, help="Output directory for ios-threat-model.md and ios-threat-model.json")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def evidence(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in paths:
        path = root / item
        rows.append({"path": item, "present": path.exists()})
    return rows


def present_paths(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row["path"]) for row in rows if row.get("present")]


def all_present(rows: list[dict[str, Any]]) -> bool:
    return all(row.get("present") for row in rows)


def boundary(
    boundary_id: str,
    name: str,
    source: str,
    destination: str,
    trust_change: str,
    attacker_inputs: list[str],
    controls: list[str],
    evidence_paths: list[str],
) -> dict[str, Any]:
    return {
        "id": boundary_id,
        "name": name,
        "source": source,
        "destination": destination,
        "trustChange": trust_change,
        "attackerControlledInputs": attacker_inputs,
        "existingControls": controls,
        "evidence": evidence_paths,
    }


def threat(
    threat_id: str,
    title: str,
    priority: str,
    likelihood: str,
    impact: str,
    affected_assets: list[str],
    abuse_path: str,
    existing_controls: list[str],
    recommended_controls: list[str],
    evidence_paths: list[str],
) -> dict[str, Any]:
    return {
        "id": threat_id,
        "title": title,
        "priority": priority,
        "likelihood": likelihood,
        "impact": impact,
        "affectedAssets": affected_assets,
        "abusePath": abuse_path,
        "existingControls": existing_controls,
        "recommendedControls": recommended_controls,
        "evidence": evidence_paths,
    }


def build_report(root: Path) -> dict[str, Any]:
    if not root.exists() or not root.is_dir():
        fail(f"repository root not found: {root}")
    root = root.resolve()

    key_paths = evidence(
        root,
        [
            "AGENTS.md",
            "bin/codex-maintainer",
            "plugins/ios-shipguard/.codex-plugin/plugin.json",
            "plugins/ios-shipguard/.mcp.json",
            "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md",
            "scripts/ios_preview.py",
            "scripts/shipguard_devspace_mcp.py",
            "scripts/ios_codex_handoff.py",
            "scripts/ios_redaction.py",
            "scripts/package_release.sh",
            "tests/package_release_test.sh",
            "scripts/self_audit.sh",
            "scripts/validate_workflow_bundle.sh",
            "docs/shipguard-devspace.md",
            "docs/ios-preview.md",
            "docs/ios-shipguard.md",
            "evals/ios_shipguard_cases.jsonl",
        ],
    )

    assets = [
        {
            "id": "local-ios-project",
            "name": "Local iOS project and simulator state",
            "whyItMatters": "Shipguard reads app topology, permissions, screenshots, preview events, and handoff prompts from developer machines.",
            "evidence": present_paths(evidence(root, ["scripts/ios_doctor.py", "scripts/ios_inventory.py", "scripts/ios_preview.py"])),
        },
        {
            "id": "credentials-and-identifiers",
            "name": "Credentials, Apple identifiers, tokens, local paths, and account names",
            "whyItMatters": "Reports can contain team IDs, bundle IDs, App Store Connect identifiers, bearer tokens, and user-local filesystem paths.",
            "evidence": present_paths(evidence(root, ["scripts/ios_redaction.py", "docs/shipguard-devspace.md"])),
        },
        {
            "id": "codex-handoff-prompts",
            "name": "Codex handoff prompts and app-server request plans",
            "whyItMatters": "Prompt files can trigger local Codex workflows and must not hide automatic execution or leaked secrets.",
            "evidence": present_paths(evidence(root, ["scripts/ios_codex_handoff.py", "scripts/shipguard_devspace_mcp.py"])),
        },
        {
            "id": "release-artifacts",
            "name": "Release tarballs, package manifests, release proof, and GitHub Actions artifacts",
            "whyItMatters": "Published assets need reproducible package contents and tamper-evident proof.",
            "evidence": present_paths(evidence(root, ["scripts/package_release.sh", "tests/package_release_test.sh", "actions/release-proof/action.yml"])),
        },
    ]

    boundaries = [
        boundary(
            "preview-browser-to-local-server",
            "Codex browser preview to local loopback server",
            "Codex in-app browser or local browser",
            "scripts/ios_preview.py",
            "Browser events become local JSONL handoff evidence, not simulator input.",
            ["click coordinates", "right-click action labels", "free-form notes"],
            [
                "loopback bind by default",
                "bounded JSON event bodies",
                "raw coordinates are visual intent only",
                "semantic XcodeBuildMCP elementRef proof required before real simulator taps",
            ],
            ["scripts/ios_preview.py", "docs/ios-preview.md", "tests/ios_preview_test.sh"],
        ),
        boundary(
            "devspace-mcp-to-preview",
            "ChatGPT Apps / MCP host to Shipguard Devspace",
            "MCP client, ChatGPT Developer Mode, or Codex plugin sidecar",
            "scripts/shipguard_devspace_mcp.py",
            "Tool calls can start preview, read screenshots, record events, and prepare handoff prompts.",
            ["MCP JSON-RPC requests", "preview event payloads", "handoff note text", "optional fixture paths"],
            [
                "loopback-only HTTP mode",
                "optional bearer auth for tunneled Developer Mode",
                "screenshot view-token containment",
                "path scope in bearer-auth mode",
                "no arbitrary shell tool",
                "no automatic Codex app-server execution",
            ],
            ["scripts/shipguard_devspace_mcp.py", "docs/shipguard-devspace.md", "tests/shipguard_devspace_mcp_test.sh"],
        ),
        boundary(
            "reports-to-public-evidence",
            "Local reports to prompts, public issues, benchmark notes, or release evidence",
            "Local generated reports",
            "Humans, Codex prompts, CI artifacts, or public repositories",
            "Private local state can leave the developer machine if report sharing is not gated.",
            ["report files", "preview logs", "handoff prompts", "local paths", "tokens", "team IDs", "bundle IDs"],
            [
                "ios redact command",
                "redaction report with remaining risk count",
                "screenshot sharing remains manual",
                "package tests grep for local paths and token-looking strings",
            ],
            ["scripts/ios_redaction.py", "tests/ios_redaction_test.sh", "tests/package_release_test.sh"],
        ),
        boundary(
            "release-package-to-consumer",
            "Source checkout to release package consumer",
            "Maintainer release process",
            "Release tarball, GitHub Action artifacts, and downstream verifier",
            "Consumers rely on packaged scripts, tests, plugin files, and proof ledgers rather than README claims alone.",
            ["release asset contents", "workflow inputs", "downloaded artifacts"],
            [
                "package release test",
                "self-audit required artifact list",
                "release manifest and replay verification",
                "negative evidence fixtures",
            ],
            ["scripts/package_release.sh", "tests/package_release_test.sh", "scripts/self_audit.sh", "fixtures/release-evidence/negative/README.md"],
        ),
    ]

    threats = [
        threat(
            "raw-coordinate-tap-confusion",
            "Visual preview coordinates are mistaken for safe simulator proof",
            "high",
            "medium",
            "high",
            ["local-ios-project", "codex-handoff-prompts"],
            "A user clicks a visual preview and an agent treats raw browser coordinates as a real simulator target, causing the wrong UI action or source edit.",
            ["preview handoff marks raw coordinate taps as not proof", "target-match ranks semantic UI candidates without tapping"],
            ["Keep no-raw-coordinate language in plugin guidance and evals", "Require simulator UI snapshot or elementRef proof before tapping"],
            ["scripts/ios_preview.py", "scripts/ios_target_match.py", "evals/ios_shipguard_cases.jsonl"],
        ),
        threat(
            "devspace-token-or-path-leak",
            "Devspace exposes screenshot tokens, local paths, or bearer credentials to model-visible content",
            "high",
            "medium",
            "high",
            ["credentials-and-identifiers", "local-ios-project"],
            "A tunneled MCP session returns tokenized screenshot URLs or path details where the model or public logs can retain them.",
            ["widget-only screenshot token metadata", "bearer auth mode", "path-scope controls", "redaction command"],
            ["Keep token URLs out of structuredContent", "Run ios redact before publishing Devspace reports", "Avoid adding OCR without a redaction pass"],
            ["scripts/shipguard_devspace_mcp.py", "docs/shipguard-devspace.md", "scripts/ios_redaction.py"],
        ),
        threat(
            "automatic-codex-execution",
            "Prepared handoff becomes unintended Codex execution",
            "high",
            "low",
            "high",
            ["codex-handoff-prompts", "local-ios-project"],
            "A connector or prompt starts Codex app-server execution without explicit local approval.",
            ["codex_prepare_handoff prepares artifacts only", "ios codex-handoff requires --execute for execution", "plugin guidance calls out trusted local approval"],
            ["Keep execution flags explicit and covered by tests", "Record transcript paths for any execution mode"],
            ["scripts/ios_codex_handoff.py", "scripts/shipguard_devspace_mcp.py", "tests/ios_codex_handoff_test.sh"],
        ),
        threat(
            "report-sensitive-data-disclosure",
            "Generated reports leak app identifiers, accounts, tokens, or private local paths",
            "medium",
            "medium",
            "medium",
            ["credentials-and-identifiers", "release-artifacts"],
            "Reports from inventory, AI readiness, preview, or release proof are pasted into public issues or benchmark notes without redaction.",
            ["ios redact covers common iOS secrets", "package release test rejects local paths and token-looking strings"],
            ["Treat screenshots as local-only unless explicitly approved", "Keep private-term support in redaction workflows"],
            ["scripts/ios_redaction.py", "tests/ios_redaction_test.sh", "tests/package_release_test.sh"],
        ),
        threat(
            "release-package-drift",
            "Release package omits plugin, tests, evals, or guardrails needed by consumers",
            "medium",
            "medium",
            "medium",
            ["release-artifacts"],
            "A tarball ships without the latest Shipguard script, test, plugin metadata, or evidence fixture, leaving consumers with stale guardrails.",
            ["validate workflow bundle", "self-audit artifact list", "package release test"],
            ["Update package and self-audit manifests with every new command", "Run package release test before release claims"],
            ["scripts/validate_workflow_bundle.sh", "scripts/self_audit.sh", "tests/package_release_test.sh"],
        ),
    ]

    severity = {
        "critical": [
            "Pre-auth remote command execution or arbitrary shell exposed from Devspace or plugin MCP.",
            "Automatic Codex execution from a remote/tunneled tool without explicit local approval and transcript evidence.",
        ],
        "high": [
            "Credential, bearer token, screenshot token, team ID, or private local-path disclosure into model-visible or public artifacts.",
            "Raw preview coordinates converted into real simulator actions without semantic target proof for a sensitive flow.",
        ],
        "medium": [
            "Report redaction misses a private identifier that remains in a public benchmark or issue artifact.",
            "Release packages drift from source manifests or omit a guardrail test, plugin file, or eval case.",
        ],
        "low": [
            "Docs or generated handoff text are stale but do not change command behavior or leak private data.",
            "Fixture-only eval wording is imprecise without affecting proof boundaries.",
        ],
    }

    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "codex-maintainer ios threat-model",
        "generatedAt": utc_now(),
        "project": "Shipguard for Codex",
        "root": ".",
        "status": "pass" if all_present(key_paths) else "partial",
        "summary": {
            "purpose": "Local-first guardrails for iOS Codex workflows, preview handoffs, report sharing, and release proof.",
            "primarySurfaces": [
                "codex-maintainer iOS CLI commands",
                "ios-shipguard Codex plugin and skill",
                "local preview bridge",
                "Shipguard Devspace MCP/App bridge",
                "generated reports and release proof artifacts",
            ],
            "keyEvidenceCount": len(present_paths(key_paths)),
            "missingEvidence": [str(row["path"]) for row in key_paths if not row.get("present")],
        },
        "assets": assets,
        "trustBoundaries": boundaries,
        "attackerControlledInputs": sorted(
            {
                item
                for boundary_item in boundaries
                for item in boundary_item["attackerControlledInputs"]
            }
        ),
        "existingControls": sorted(
            {
                item
                for boundary_item in boundaries
                for item in boundary_item["existingControls"]
            }
        ),
        "threats": threats,
        "severityCalibration": severity,
        "assumptions": [
            "Shipguard remains local-first and does not expose a production hosted Devspace by default.",
            "Codex app-server execution is a trusted local action and must remain opt-in.",
            "Screenshots can contain private app/user data and are not public-safe by default.",
            "The actual GitHub repository slug and CLI package name may remain stable even if the public brand changes.",
        ],
        "keyEvidence": key_paths,
    }
    return report


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Shipguard for Codex Threat Model",
        "",
        "## Overview",
        "",
        report["summary"]["purpose"],
        "",
        f"- Status: `{report['status']}`",
        f"- Primary surfaces: {', '.join(report['summary']['primarySurfaces'])}",
        f"- Evidence files present: {report['summary']['keyEvidenceCount']}",
        "",
        "## Threat Model, Trust Boundaries, and Assumptions",
        "",
        "Assets:",
    ]
    for asset in report["assets"]:
        evidence_text = ", ".join(asset["evidence"]) or "no local evidence file found"
        lines.append(f"- **{asset['name']}**: {asset['whyItMatters']} Evidence: `{evidence_text}`.")
    lines.extend(["", "Trust boundaries:", ""])
    for item in report["trustBoundaries"]:
        controls = "; ".join(item["existingControls"])
        inputs = "; ".join(item["attackerControlledInputs"])
        evidence_text = ", ".join(item["evidence"])
        lines.append(f"- **{item['name']}**: {item['source']} -> {item['destination']}. {item['trustChange']}")
        lines.append(f"  Inputs: {inputs}.")
        lines.append(f"  Existing controls: {controls}.")
        lines.append(f"  Evidence: `{evidence_text}`.")
    lines.extend(["", "Assumptions:", ""])
    for assumption in report["assumptions"]:
        lines.append(f"- {assumption}")

    lines.extend(["", "## Attack Surface, Mitigations, and Attacker Stories", ""])
    for item in report["threats"]:
        lines.append(f"### {item['title']}")
        lines.append("")
        lines.append(f"- Priority: `{item['priority']}`")
        lines.append(f"- Likelihood: `{item['likelihood']}`")
        lines.append(f"- Impact: `{item['impact']}`")
        lines.append(f"- Abuse path: {item['abusePath']}")
        lines.append(f"- Affected assets: {', '.join(item['affectedAssets'])}")
        lines.append(f"- Existing controls: {'; '.join(item['existingControls'])}")
        lines.append(f"- Recommended controls: {'; '.join(item['recommendedControls'])}")
        lines.append(f"- Evidence: `{', '.join(item['evidence'])}`")
        lines.append("")

    lines.extend(["## Severity Calibration (Critical, High, Medium, Low)", ""])
    for level in ["critical", "high", "medium", "low"]:
        lines.append(f"### {level.title()}")
        lines.append("")
        for item in report["severityCalibration"][level]:
            lines.append(f"- {item}")
        lines.append("")
    if report["summary"]["missingEvidence"]:
        lines.append("## Missing Evidence")
        lines.append("")
        for item in report["summary"]["missingEvidence"]:
            lines.append(f"- `{item}`")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(Path(args.path))
    markdown = markdown_report(report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ios-threat-model.json"
    md_path = out_dir / "ios-threat-model.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    print(f"wrote: {json_path}")
    print(f"wrote: {md_path}")
    print(f"status: {report['status']}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)


if __name__ == "__main__":
    main()
