#!/usr/bin/env python3
"""Generate the ShipGuard v4 preview stabilization report."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown


SURFACE = "ShipGuard V4 Preview"
TOOL = "shipguard v4 preview"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def scrub_value(value: Any, root: Path, home: Path) -> Any:
    if isinstance(value, dict):
        return {key: scrub_value(child, root, home) for key, child in value.items()}
    if isinstance(value, list):
        return [scrub_value(child, root, home) for child in value]
    if isinstance(value, str):
        result = value.replace(root.as_posix(), "<repo>")
        result = result.replace(home.as_posix(), "<home>")
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


def contains_all(text: str, phrases: list[str]) -> bool:
    lower = text.lower()
    return all(phrase.lower() in lower for phrase in phrases)


def file_has_all(root: Path, relative_path: str, phrases: list[str]) -> bool:
    return contains_all(read_text(root / relative_path), phrases)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    home = Path.home().resolve()

    version = read_text(root / "VERSION").strip() or "unknown"
    bin_text = read_text(root / "bin" / "shipguard")
    cli_text = read_text(root / "docs" / "cli.md")
    matrix_text = read_text(root / "docs" / "command-matrix.md")
    preview_doc_text = read_text(root / "docs" / "v4-preview.md")
    roadmap_text = read_text(root / "ROADMAP.md")
    security_text = read_text(root / "docs" / "security-threat-model.md")
    privacy_text = read_text(root / "docs" / "privacy.md")
    receipts_text = read_text(root / "scripts" / "shipguard_receipts.py")
    release_consume_text = read_text(root / "scripts" / "release_consume.sh")
    release_proof_text = read_text(root / "scripts" / "release_proof.sh")
    gauntlet_text = read_text(root / "scripts" / "tool_value_gauntlet.py")

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "v4-preview-command-routed",
        "CLI route is public and documented",
        "cmd_v4" in bin_text and "v4 preview" in bin_text and "shipguard v4 preview" in cli_text,
        ["bin/shipguard", "docs/cli.md"],
        "Wire the v4 preview route through the public CLI and command docs.",
    )
    add_check(
        checks,
        "v4-preview-contract-documented",
        "Preview contract names the stabilization contract",
        contains_all(
            preview_doc_text,
            [
                "schema freeze",
                "security review",
                "migration plan",
                "deprecation policy",
                "release readiness",
            ],
        ),
        ["docs/v4-preview.md"],
        "Document the v4 preview contract before claiming product readiness.",
    )
    add_check(
        checks,
        "receipt-v2-contract-present",
        "Structured evidence receipts remain the proof spine",
        "schemaVersion" in receipts_text and "receipt" in receipts_text.lower(),
        ["scripts/shipguard_receipts.py"],
        "Keep v4 tied to structured, machine-readable evidence receipts.",
    )
    add_check(
        checks,
        "release-proof-consumer-present",
        "Release proof can be consumed independently",
        bool(release_consume_text.strip()) and bool(release_proof_text.strip()),
        ["scripts/release_proof.sh", "scripts/release_consume.sh"],
        "Keep release proof generation and consumer verification available for v4.",
    )
    add_check(
        checks,
        "security-boundary-present",
        "Trust boundary docs exist for preview review",
        bool(security_text.strip()) and bool(privacy_text.strip()),
        ["docs/security-threat-model.md", "docs/privacy.md"],
        "Keep security and privacy boundaries explicit before widening adapters.",
    )
    add_check(
        checks,
        "value-gauntlet-v4-probe-present",
        "Value gauntlet can score v4 stabilization",
        "runtimeV4PreviewStabilization" in gauntlet_text
        and "v4PreviewStabilizationReceipts" in gauntlet_text,
        ["scripts/tool_value_gauntlet.py"],
        "Add a runtime receipt family so v4 preview quality is measured, not asserted.",
    )
    add_check(
        checks,
        "migration-roadmap-present",
        "Roadmap has an upgrade path from v3 preview to v4",
        "v4" in roadmap_text.lower() and "migration" in (roadmap_text + preview_doc_text).lower(),
        ["ROADMAP.md", "docs/v4-preview.md"],
        "Keep the migration plan visible before freezing v4 schemas.",
    )
    add_check(
        checks,
        "command-matrix-present",
        "Command matrix exposes the preview surface",
        "v4 preview" in matrix_text,
        ["docs/command-matrix.md"],
        "Add the command to the matrix so users can discover the preview contract.",
    )

    required_checks = [check for check in checks if check["required"]]
    failed_required = [check for check in required_checks if check["status"] != "pass"]
    status = "pass" if not failed_required else "review"

    stable_contract = {
        "stage": "preview-stabilization",
        "frontDoorCommands": [
            "shipguard init",
            "shipguard inspect",
            "shipguard prepare",
            "shipguard verify",
            "shipguard doctor",
            "shipguard full-audit",
            "shipguard value-gauntlet",
            "shipguard v4 preview",
        ],
        "thinAdapters": [
            "Codex plugin and skill routing",
            "XcodeBuildMCP evidence adapter",
            "Expo and EAS assurance adapter",
            "Generic MCP and agent trace adapters",
        ],
        "scopeBoundaries": [
            "ShipGuard reports can recommend proof, but must not claim proof without artifacts.",
            "Private app checkouts may inform product QA only through redacted public fixtures.",
            "Interactive model choice stays in the host agent; ShipGuard records the evidence contract.",
        ],
    }
    schema_freeze = {
        "status": "preview-stabilized" if status == "pass" else "review",
        "frozenForPreview": status == "pass",
        "frozenForV4Release": False,
        "schemas": [
            {
                "name": "structured evidence receipt",
                "owner": "scripts/shipguard_receipts.py",
                "previewRequirement": "schemaVersion, surface, proof, scope boundary, and result UX fields remain machine-readable.",
            },
            {
                "name": "agent adapter trace",
                "owner": "scripts/agent_adapter_kernel.py",
                "previewRequirement": "adapter identity, task intent, evidence artifacts, and blocked claims are preserved.",
            },
            {
                "name": "value gauntlet report",
                "owner": "scripts/tool_value_gauntlet.py",
                "previewRequirement": "lowest-value probe, command coverage, and receipt-family pass/fail state remain stable.",
            },
            {
                "name": "release proof bundle",
                "owner": "scripts/release_proof.sh",
                "previewRequirement": "consumer install proof and package manifest can be verified after publishing.",
            },
        ],
    }
    security_review = {
        "status": "preview-ready" if status == "pass" else "review",
        "requiredGates": [
            "No secrets, tokens, local private paths, or target-app source are emitted in shareable reports.",
            "Release proof can be consumed by a fresh checkout before a release is called ready.",
            "Adapter reports separate local proof, manual proof, and blocked proof.",
            "Codex plugin status passes strict installation checks after plugin refresh.",
        ],
        "blockedSecurityClaims": [
            "No formal third-party security audit is claimed.",
            "No sandbox escape, mobile device security, or App Store compliance guarantee is claimed.",
        ],
    }
    migration_plan = {
        "target": "ShipGuard v4",
        "steps": [
            "Stabilize preview command output and receipt families.",
            "Freeze v4 schema names, compatibility policy, and migration fixtures.",
            "Publish adapter compatibility notes for Codex, XcodeBuildMCP, Expo, EAS, and generic MCP users.",
            "Keep v3-compatible command aliases until the deprecation window closes.",
            "Require release proof consumption before announcing v4 as a product release.",
        ],
    }
    deprecation_policy = {
        "status": "preview-policy",
        "rules": [
            "No existing public command is removed during v4 preview stabilization.",
            "Breaking schema changes require a migration note, fixture update, and changelog entry.",
            "Deprecated fields keep compatibility shims for at least two minor releases unless they leak secrets or create unsafe behavior.",
            "Machine-readable reports must prefer additive fields over renamed fields.",
        ],
    }
    release_readiness = {
        "currentVersion": version,
        "targetVersion": "4.0.0",
        "releaseClaim": "not-released",
        "requiredProofCommands": [
            "git diff --check",
            "./tests/v4_preview_test.sh",
            "./tests/tool_value_gauntlet_test.sh",
            "./bin/shipguard validate",
            "./bin/shipguard docs-check . --out /tmp/shipguard-docs-check",
            "./tests/self_audit_test.sh",
            "./tests/cli_smoke_test.sh",
            "./tests/package_release_test.sh",
            "./bin/shipguard codex status --strict",
        ],
        "nonClaims": [
            "This report does not publish v4.",
            "This report does not certify marketplace acceptance.",
            "This report does not verify private target apps.",
        ],
    }
    blocked_claims = [
        "ShipGuard v4 is not released until package proof, install proof, and release notes are verified.",
        "External adoption is not proven by local fixtures.",
        "Agent-neutral adapter support is preview-level until each adapter has consumer proof.",
        "Security readiness is bounded by documented checks unless an external audit exists.",
    ]
    report_quality_questions = [
        "Are all v4 preview claims backed by runnable ShipGuard commands instead of roadmap prose?",
        "Can a solo developer understand what is stable, what is preview-only, and what remains blocked?",
        "Does the report give a concrete next proof step rather than a broad product wish?",
        "Are private-app observations excluded from public artifacts unless converted into redacted fixtures?",
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
    priority_action = (
        "Freeze v4 schemas with compatibility fixtures and migration checks."
        if status == "pass"
        else "Complete the missing v4 preview stabilization checks before freezing schemas."
    )
    result_ux = build_result_ux(
        status=status,
        summary=(
            "ShipGuard has a runnable v4 preview stabilization contract."
            if status == "pass"
            else "ShipGuard v4 preview needs stabilization work before schema freeze."
        ),
        proof_source="v4 preview checks plus repository docs and proof scripts",
        why_it_matters="This prevents roadmap language from becoming an unproven v4 release claim.",
        next_command="./tests/v4_preview_test.sh",
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
        "productStage": "v4-preview-stabilization",
        "checks": checks,
        "stableContract": stable_contract,
        "schemaFreeze": schema_freeze,
        "securityReview": security_review,
        "migrationPlan": migration_plan,
        "deprecationPolicy": deprecation_policy,
        "releaseReadiness": release_readiness,
        "blockedClaims": blocked_claims,
        "scopeBoundary": scope_boundary,
        "reportQualityQuestions": report_quality_questions,
        "resultUX": result_ux,
    }
    if args.shipguard_eval:
        report["shipguardEval"] = {
            "mode": "ShipGuard product QA",
            "allowedInput": "ShipGuard source tree and redacted public fixtures",
            "forbiddenOutput": "Private target-app edits or unproven release claims",
            "nextImprovement": priority_action,
        }
    if args.shareable:
        report = scrub_value(report, root, home)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ShipGuard V4 Preview",
        "",
        f"- Status: `{report['status']}`",
        f"- Product stage: `{report['productStage']}`",
        f"- Release claim: `{report['releaseReadiness']['releaseClaim']}`",
        f"- Version inspected: `{report['version']}`",
        "",
        *render_result_markdown(report["resultUX"]),
        "## Stable Contract",
        "",
    ]
    for command in report["stableContract"]["frontDoorCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Schema Freeze", ""])
    schema = report["schemaFreeze"]
    lines.append(f"- Frozen for preview: `{schema['frozenForPreview']}`")
    lines.append(f"- Frozen for v4 release: `{schema['frozenForV4Release']}`")
    for item in schema["schemas"]:
        lines.append(f"- {item['name']}: {item['previewRequirement']}")
    lines.extend(["", "## Security Review", ""])
    for gate in report["securityReview"]["requiredGates"]:
        lines.append(f"- {gate}")
    lines.extend(["", "## Migration Plan", ""])
    for step in report["migrationPlan"]["steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Deprecation Policy", ""])
    for rule in report["deprecationPolicy"]["rules"]:
        lines.append(f"- {rule}")
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
                "- Private apps are read-only inputs only when explicitly used for product QA.",
                "- Shareable reports must not include private app source, local paths, screenshots, or tokens.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ShipGuard v4 preview stabilization reports.")
    parser.add_argument("--path", default=".", help="ShipGuard repository path. Defaults to current directory.")
    parser.add_argument("--out", required=True, help="Output directory for v4-preview reports.")
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
        (out_dir / "v4-preview.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_markdown:
        (out_dir / "v4-preview.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
