#!/usr/bin/env python3
"""Generate the ShipGuard v4 schema-freeze contract report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown


SURFACE = "ShipGuard V4 Schema Freeze"
TOOL = "shipguard v4 schema-freeze"
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


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    home = Path.home().resolve()

    version = read_text(root / "VERSION").strip() or "unknown"
    bin_text = read_text(root / "bin" / "shipguard")
    cli_text = read_text(root / "docs" / "cli.md")
    matrix_text = read_text(root / "docs" / "command-matrix.md")
    freeze_doc_text = read_text(root / "docs" / "v4-schema-freeze.md")
    preview_doc_text = read_text(root / "docs" / "v4-preview.md")
    gauntlet_text = read_text(root / "scripts" / "tool_value_gauntlet.py")
    report_quality_text = read_text(root / "scripts" / "ios_report_quality.py")
    self_audit_text = read_text(root / "scripts" / "self_audit.sh")
    package_test_text = read_text(root / "tests" / "package_release_test.sh")
    changelog_text = read_text(root / "CHANGELOG.md")

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "schema-freeze-command-routed",
        "CLI route is public",
        "schema-freeze" in bin_text and TOOL in cli_text,
        ["bin/shipguard", "docs/cli.md"],
        "Route `shipguard v4 schema-freeze` through the public CLI and CLI docs.",
    )
    add_check(
        checks,
        "schema-freeze-contract-documented",
        "Schema-freeze contract is documented",
        contains_all(
            freeze_doc_text,
            [
                "compatibility policy",
                "compatibility fixtures",
                "migration checks",
                "changelog policy",
                "blocked claims",
            ],
        ),
        ["docs/v4-schema-freeze.md"],
        "Document the frozen schema contract, migration checks, and non-claims before treating the contract as frozen.",
    )
    add_check(
        checks,
        "schema-freeze-gauntlet-receipts-present",
        "Value gauntlet has schema-freeze receipts",
        "v4SchemaFreezeReceipts" in gauntlet_text and "runtimeV4SchemaFreeze" in gauntlet_text,
        ["scripts/tool_value_gauntlet.py"],
        "Add a runtime receipt family so schema freeze is measured by command proof.",
    )
    add_check(
        checks,
        "schema-freeze-report-quality-present",
        "Report-quality accepts schema-freeze reports",
        TOOL in report_quality_text,
        ["scripts/ios_report_quality.py"],
        "Allow report-quality to score the v4 schema-freeze report as a root ShipGuard report.",
    )
    add_check(
        checks,
        "schema-freeze-self-audit-package-present",
        "Self-audit and package proof include the surface",
        "v4 schema-freeze --help" in self_audit_text
        and "tests/v4_schema_freeze_test.sh" in package_test_text
        and "scripts/v4_schema_freeze.py" in package_test_text,
        ["scripts/self_audit.sh", "tests/package_release_test.sh"],
        "Include the command, script, docs, test, and receipt fixture in self-audit and package proof.",
    )
    add_check(
        checks,
        "schema-freeze-command-matrix-present",
        "Command matrix exposes the schema-freeze surface",
        "v4 schema-freeze" in matrix_text,
        ["docs/command-matrix.md"],
        "Add schema-freeze to the command matrix so the v4 path is discoverable.",
    )
    add_check(
        checks,
        "schema-freeze-changelog-policy-present",
        "Changelog records schema policy",
        contains_all(changelog_text, ["v3.130", "schema-freeze", "compatibility"]),
        ["CHANGELOG.md"],
        "Record the schema-freeze contract and compatibility policy in the changelog.",
    )
    add_check(
        checks,
        "v4-preview-boundary-retained",
        "Preview remains separate from product release",
        ("not publish v4" in preview_doc_text.lower() or "does not publish v4" in preview_doc_text.lower())
        and "not-released" in preview_doc_text,
        ["docs/v4-preview.md"],
        "Keep preview stabilization separate from stable v4 release claims.",
    )

    required_checks = [check for check in checks if check["required"]]
    failed_required = [check for check in required_checks if check["status"] != "pass"]
    status = "pass" if not failed_required else "review"

    schema_registry = [
        {
            "name": "structured evidence receipt",
            "owner": "scripts/shipguard_receipts.py",
            "schemaVersion": "v2-compatible",
            "compatibility": "Additive fields allowed; renamed or removed fields require migration notes and fixtures.",
        },
        {
            "name": "agent adapter trace",
            "owner": "scripts/agent_adapter_kernel.py",
            "schemaVersion": "v1",
            "compatibility": "Adapter identity, task intent, evidence artifacts, blocked claims, and result UX stay stable.",
        },
        {
            "name": "tool value gauntlet report",
            "owner": "scripts/tool_value_gauntlet.py",
            "schemaVersion": "v1",
            "compatibility": "Receipt-family status, lowest-value answer, depth signals, and result UX remain machine-readable.",
        },
        {
            "name": "v4 preview and schema-freeze reports",
            "owner": "scripts/v4_preview.py, scripts/v4_schema_freeze.py",
            "schemaVersion": "v1",
            "compatibility": "Product stage, release claim, blocked claims, report-quality questions, and scope boundary stay explicit.",
        },
    ]
    compatibility_policy = {
        "status": "frozen" if status == "pass" else "review",
        "frozenForV4Release": status == "pass",
        "releaseClaim": "not-released",
        "rules": [
            "Prefer additive JSON fields over renames or removals.",
            "Breaking field changes require a compatibility fixture, changelog note, migration guidance, and report-quality coverage.",
            "Deprecated fields keep a two-minor-release compatibility window unless they leak secrets or create unsafe claims.",
            "Shareable reports must preserve redaction behavior for local paths, private app data, screenshots, URLs, and tokens.",
        ],
    }
    compatibility_fixtures = [
        {
            "id": "v4-schema-freeze-contract-pass",
            "path": "fixtures/tool-value-gauntlet/v4-schema-freeze-receipts/schema-contract/receipt.json",
            "proves": "The schema-freeze report emits required JSON/Markdown fields and keeps v4 product release claims blocked.",
        },
        {
            "id": "v4-schema-freeze-report-quality-pass",
            "path": "fixtures/tool-value-gauntlet/v4-schema-freeze-receipts/schema-contract/receipt.json",
            "proves": "Report-quality can score the schema-freeze report and preserve actionability questions.",
        },
        {
            "id": "v4-schema-freeze-docs-check-pass",
            "path": "fixtures/tool-value-gauntlet/v4-schema-freeze-receipts/schema-contract/receipt.json",
            "proves": "Docs remain link-valid after adding the schema-freeze contract.",
        },
    ]
    migration_checks = [
        "Run `shipguard v4 preview` first to prove the preview contract is stabilized.",
        "Run `shipguard v4 schema-freeze` to prove compatibility rules, fixtures, migration notes, and blocked claims.",
        "Run `shipguard value-gauntlet` and confirm `runtimeV4SchemaFreeze` is no longer missing.",
        "Run package proof and consumer install proof before any stable v4 product claim.",
    ]
    changelog_policy = {
        "requiredFor": ["new public command", "schema field rename", "schema field removal", "compatibility downgrade", "release-claim change"],
        "format": "Every schema-affecting entry names the command, affected schema, compatibility behavior, and required migration proof.",
    }
    deprecation_policy = {
        "status": "frozen",
        "rules": [
            "Deprecated fields remain readable for at least two minor releases.",
            "Removal requires package proof, report-quality proof, and a migration note.",
            "Unsafe fields that leak secrets or private app data can be removed immediately with a security note.",
        ],
    }
    release_readiness = {
        "currentVersion": version,
        "targetVersion": "4.0.0",
        "productStage": "v4-schema-freeze",
        "releaseClaim": "not-released",
        "frozenForV4Release": status == "pass",
        "requiredProofCommands": [
            "git diff --check",
            "./tests/v4_schema_freeze_test.sh",
            "./tests/v4_preview_test.sh",
            "./tests/tool_value_gauntlet_test.sh",
            "./bin/shipguard validate",
            "./bin/shipguard docs-check . --out /tmp/shipguard-docs-check",
            "./tests/self_audit_test.sh",
            "./tests/cli_smoke_test.sh",
            "./tests/package_release_test.sh",
            "./bin/shipguard codex status --strict",
        ],
    }
    blocked_claims = [
        "This freezes the local v4 schema contract; it does not release ShipGuard v4 as a product.",
        "External adoption, marketplace acceptance, and third-party audit are not proven by this report.",
        "Private Ringly or Ilmify app validation is not part of this report.",
        "Physical-device proof is not implied by local schema fixtures.",
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
        "Can value-gauntlet prove the v4 schema freeze with runtime receipts rather than roadmap language?",
        "Does the schema-freeze report clearly separate frozen schema contract from unreleased v4 product status?",
        "Are compatibility, migration, changelog, and deprecation rules visible in both JSON and Markdown?",
        "What release-candidate readiness proof is still missing before v4 can be called stable?",
    ]
    priority_action = (
        "Prove v4 release-candidate readiness with install, upgrade, uninstall, release-proof, and adoption packet checks."
        if status == "pass"
        else "Complete the missing schema-freeze checks before claiming the v4 schema contract is frozen."
    )
    result_ux = build_result_ux(
        status=status,
        summary=(
            "ShipGuard has a frozen v4 schema contract with compatibility proof hooks."
            if status == "pass"
            else "ShipGuard v4 schema freeze needs more proof before it can be treated as frozen."
        ),
        proof_source="v4 schema-freeze checks plus value-gauntlet receipts, docs, and package proof hooks",
        why_it_matters="This stops v4 from becoming a brand label without a stable machine-readable contract.",
        next_command="./tests/v4_schema_freeze_test.sh",
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
        "productStage": "v4-schema-freeze",
        "checks": checks,
        "schemaRegistry": schema_registry,
        "schemaFreeze": compatibility_policy,
        "compatibilityPolicy": compatibility_policy,
        "compatibilityFixtures": compatibility_fixtures,
        "migrationChecks": migration_checks,
        "changelogPolicy": changelog_policy,
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
            "allowedInput": "ShipGuard source tree and public fixtures",
            "forbiddenOutput": "Private target-app edits or unproven stable-v4 release claims",
            "nextImprovement": priority_action,
        }
    if args.shareable:
        report = scrub_value(report, root, home)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ShipGuard V4 Schema Freeze",
        "",
        f"- Status: `{report['status']}`",
        f"- Product stage: `{report['productStage']}`",
        f"- Release claim: `{report['releaseReadiness']['releaseClaim']}`",
        f"- Frozen for v4 release: `{report['releaseReadiness']['frozenForV4Release']}`",
        f"- Version inspected: `{report['version']}`",
        "",
        *render_result_markdown(report["resultUX"]),
        "## Schema Registry",
        "",
    ]
    for schema in report["schemaRegistry"]:
        lines.append(f"- {schema['name']}: {schema['compatibility']}")
    lines.extend(["", "## Compatibility Policy", ""])
    for rule in report["compatibilityPolicy"]["rules"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Compatibility Fixtures", ""])
    for fixture in report["compatibilityFixtures"]:
        lines.append(f"- `{fixture['id']}`: {fixture['proves']}")
    lines.extend(["", "## Migration Checks", ""])
    for check in report["migrationChecks"]:
        lines.append(f"- {check}")
    lines.extend(["", "## Changelog Policy", ""])
    lines.append(f"- {report['changelogPolicy']['format']}")
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
                "- The v4 schema contract can freeze while the v4 product release remains blocked.",
                "- Shareable reports must not include private app source, local paths, screenshots, or tokens.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ShipGuard v4 schema-freeze reports.")
    parser.add_argument("--path", default=".", help="ShipGuard repository path. Defaults to current directory.")
    parser.add_argument("--out", required=True, help="Output directory for v4-schema-freeze reports.")
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
        (out_dir / "v4-schema-freeze.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_markdown:
        (out_dir / "v4-schema-freeze.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
