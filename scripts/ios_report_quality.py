#!/usr/bin/env python3
"""Grade ShipGuard reports for usefulness as product-QA artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

import ios_shareable
from shipguard_result import build_result_ux, render_result_markdown


SCHEMA_VERSION = 1
SOURCE_SCANNER_TOOLS = {
    "shipguard ios launchdeck",
    "shipguard ios performance",
    "shipguard ios design",
    "shipguard ios modernize",
    "shipguard ios app-intelligence",
    "shipguard ios ai-readiness",
    "shipguard ios external-audit",
    "shipguard ios spec-workflow",
}
DECLARED_SHAREABILITY_TOOLS = SOURCE_SCANNER_TOOLS | {
    "shipguard ios devspace-check",
}
REPORT_QUALITY_TOOL = "shipguard ios report-quality"
SPEC_WORKFLOW_TOOL = "shipguard ios spec-workflow"
SPEC_WORKFLOW_REQUIRED_ARTIFACTS = {
    "constitution",
    "spec",
    "checklist",
    "integrationDecisions",
    "plan",
    "tasks",
    "analysis",
    "devspaceGuardrails",
    "json",
    "markdown",
}
SPEC_WORKFLOW_ARTIFACT_MARKERS = {
    "analysis": [
        "# Spec Workflow Consistency Analysis",
        "## Coverage Summary",
        "## Constitution Alignment",
        "## Cross-Artifact Checks",
    ],
    "checklist": [
        "# Requirements Quality Checklist",
        "Unit tests for ShipGuard planning requirements",
        "[Completeness]",
    ],
    "integrationDecisions": [
        "# Native Integration Decisions",
        "## Replacement Decisions",
        "## Source-by-Source Evaluation",
        "## Report-Quality Questions Driving This Integration",
    ],
    "constitution": ["# ShipGuard Constitution", "Read-only product QA", "Devspace is a planning bridge"],
    "devspaceGuardrails": [
        "# Devspace Guardrails",
        "ios devspace-check",
        "model selection happens in ChatGPT, not ShipGuard",
        "## Boundary",
    ],
    "markdown": ["# iOS ShipGuard Spec Workflow", "## Slash Plan", "## Slash Goal"],
    "plan": ["# Implementation Plan", "## Phases", "## Validation", "## Analysis Gates"],
    "spec": ["# Feature Spec", "## User Outcomes", "## Acceptance Criteria", "## Clarifying Questions"],
    "tasks": ["# Tasks", "`S001`", "`S006`", "Proof:"],
}
SPEC_WORKFLOW_REQUIRED_VALIDATION_COMMANDS = [
    "git diff --check",
    "./tests/ios_spec_workflow_test.sh",
    "./tests/ios_report_quality_test.sh",
    "./tests/ios_devspace_check_test.sh",
    "./tests/cli_smoke_test.sh",
    "./bin/shipguard validate",
]
SPEC_WORKFLOW_REQUIRED_ANALYSIS_GATES = [
    "Spec includes what and why before implementation details.",
    "Plan maps every risky surface to a proof lane.",
    "Tasks are ordered and independently verifiable.",
    "Integration decisions explain whether external workflow ideas replace, extend, keep, or defer ShipGuard surfaces.",
    "Devspace remains a connector and handoff path, not an execution bypass.",
    "Private-app observations remain ShipGuard product-QA evidence only.",
]
SEVERITY_PRIORITY = {"high": 0, "review": 1, "opportunity": 2}
STATUS_PRIORITY = {"blocked": 0, "review": 1, "pass": 2}
TOOL_NEXT_ACTION_PRIORITY = {
    "shipguard brand": 0,
    "shipguard value-gauntlet": 0,
    "shipguard action verify-pr": 0,
    "shipguard lean audit": 0,
    "shipguard lean review": 0,
    "shipguard lean debt": 0,
    "shipguard lean gain": 0,
    "shipguard full-audit": 0,
    "shipguard inspect": 0,
    "shipguard prepare": 0,
    "shipguard verify": 0,
    "shipguard web audit": 1,
    "shipguard backend audit": 1,
    "shipguard cli audit": 1,
    "shipguard web plan": 2,
    "shipguard backend plan": 2,
    "shipguard cli plan": 2,
    "shipguard v4 preview": 3,
    "shipguard v4 schema-freeze": 3,
    "shipguard v4 release-candidate": 3,
    "shipguard v4 stable-publication": 3,
    "shipguard release-package hygiene": 3,
    "shipguard ios brand": 3,
    "shipguard ios launchdeck": 4,
    "shipguard ios performance": 5,
    "shipguard ios design": 6,
    "shipguard ios modernize": 7,
    "shipguard ios app-intelligence": 8,
    "shipguard ios ai-readiness": 9,
    "shipguard ios external-audit": 10,
    "shipguard ios spec-workflow": 11,
    "shipguard ios devspace-check": 12,
    "shipguard codex marketplace-readiness": 13,
    "shipguard agent trace": 14,
    "shipguard codex trace": 14,
}
ROOT_REPORT_TOOLS = {
    "shipguard brand",
    "shipguard docs-check",
    "shipguard value-gauntlet",
    "shipguard action verify-pr",
    "shipguard lean audit",
    "shipguard lean review",
    "shipguard lean debt",
    "shipguard lean gain",
    "shipguard full-audit",
    "shipguard inspect",
    "shipguard v4 preview",
    "shipguard v4 schema-freeze",
    "shipguard v4 release-candidate",
    "shipguard v4 stable-publication",
    "shipguard release-package hygiene",
    "shipguard codex marketplace-readiness",
    "shipguard agent trace",
    "shipguard codex trace",
    "shipguard prepare",
    "shipguard verify",
    "shipguard pilot-bench",
    "shipguard web audit",
    "shipguard web plan",
    "shipguard backend audit",
    "shipguard backend plan",
    "shipguard cli audit",
    "shipguard cli plan",
}
SPEC_WORKFLOW_PLACEHOLDER_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:TODO|TBD|FIXME)\b")
TOKEN_RISK_PATTERNS = {
    "bearer-token": re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    "query-token": re.compile(
        r"(?i)[?&](?:codexpro_token|shipguard_token|token|access_token|bearer_token)=[A-Za-z0-9._~%+-]{12,}"
    ),
    "secret-assignment": re.compile(
        r"(?i)\b(?:SHIPGUARD_DEVSPACE_TOKEN|OPENAI_API_KEY|CODEXPRO_HTTP_TOKEN|CLOUDFLARE_TOKEN|NGROK_AUTHTOKEN)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{12,}"
    ),
    "known-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b"),
}
LOCAL_PATH_VALUE_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:Users|private/tmp|var/folders)/[^\s`'\"),]+")
COMMAND_SHAPED_RE = re.compile(
    r"^(?:\./|/|shipguard\b|codex\b|git\b|gh\b|xcrun\b|xcodebuild\b|python(?:3)?\b|bash\b|sh\b|make\b|npm\b|swift\b)"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-report-quality: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grade ShipGuard iOS JSON/Markdown reports for actionability, eval boundaries, scan scope, and shareability."
    )
    parser.add_argument(
        "--reports",
        action="append",
        required=True,
        help="Report JSON file or directory containing ShipGuard iOS reports. May be passed multiple times.",
    )
    parser.add_argument("--out", help="Output directory for ios-report-quality.md and ios-report-quality.json")
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute input/report paths from JSON and Markdown before external sharing.",
    )
    parser.add_argument(
        "--write-fixture-candidates",
        help="Write public-safe synthetic fixture starter directories for generated fixtureCandidates.",
    )
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark the report-quality run itself as ShipGuard product-QA output.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when report-quality status is not pass")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


SOURCE_REPORT_SKIP_NAMES = {
    "ios-report-quality.json",
    "fixture-candidate.json",
    "fixture-candidates-index.json",
    "fixture-promotion-manifest.json",
    "stable-publication-external-evidence-fixture-index.json",
}
SOURCE_REPORT_SKIP_DIR_NAMES = {
    "fresh-install-prefix",
    "fresh-install-work",
    "upgrade-prefix",
    "upgrade-work",
    "rollback-prefix",
    "rollback-work",
    "downloaded-release-assets",
    "release-consume",
    "stage-receipts",
    "stable-publication-evidence-kit",
    "stable-publication-launch-relay",
    "stable-publication-release-notes",
}


def is_skipped_report_path(path: Path) -> bool:
    return skipped_report_dir_name(path) is not None


def skipped_report_dir_name(path: Path) -> str | None:
    for parent in path.parents:
        if parent.name in SOURCE_REPORT_SKIP_DIR_NAMES:
            return parent.name
    return None


def report_json_files(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            fail(f"report path not found: {path}")
        if path.is_file():
            if path.name in SOURCE_REPORT_SKIP_NAMES:
                continue
            paths.append(path)
            continue
        for candidate in sorted(path.rglob("*.json")):
            if candidate.name in SOURCE_REPORT_SKIP_NAMES:
                continue
            if is_skipped_report_path(candidate):
                continue
            paths.append(candidate)
    unique = sorted({path for path in paths})
    if not unique:
        fail("no report JSON files found")
    return unique


def skipped_report_json_files(inputs: list[str]) -> list[tuple[Path, str]]:
    skipped: list[tuple[Path, str]] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if not path.exists() or path.is_file():
            continue
        for candidate in sorted(path.rglob("*.json")):
            if candidate.name in SOURCE_REPORT_SKIP_NAMES:
                continue
            skipped_dir = skipped_report_dir_name(candidate)
            if skipped_dir:
                skipped.append((candidate, skipped_dir))
    return sorted(set(skipped), key=lambda item: item[0].as_posix())


def fixture_promotion_manifest_files(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            continue
        if path.is_file():
            if path.name == "fixture-promotion-manifest.json":
                paths.append(path)
            continue
        paths.extend(candidate for candidate in sorted(path.rglob("fixture-promotion-manifest.json")) if not is_skipped_report_path(candidate))
    return sorted({path for path in paths})


def resolved_input_paths(inputs: list[str]) -> list[Path]:
    return [Path(item).expanduser().resolve() for item in inputs]


def path_label(path: Path, *, input_paths: list[Path], shareable: bool, cwd: Path) -> str:
    if not shareable:
        return path.as_posix()
    try:
        relative = path.relative_to(cwd)
        return relative.as_posix() or "."
    except ValueError:
        pass
    for index, root in enumerate(input_paths, start=1):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        suffix = relative.as_posix()
        return f"<report-input-{index}>" if not suffix or suffix == "." else f"<report-input-{index}>/{suffix}"
    return "<local-report-path>"


def paired_markdown(path: Path) -> Path | None:
    candidate = path.with_suffix(".md")
    if candidate.is_file():
        return candidate
    return None


def table_cell(value: object, limit: int = 100) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def find_scan_scope(report: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [
        report.get("scanScope"),
        report.get("sourceSummary", {}).get("scanScope") if isinstance(report.get("sourceSummary"), dict) else None,
        report.get("summary", {}).get("scanScope") if isinstance(report.get("summary"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, dict):
            return candidate
    return None


def has_local_path(text: str) -> bool:
    return bool(re.search(r"(?<![A-Za-z0-9_])/(?:Users|private/tmp|var/folders)/", text))


def token_risk_labels(text: str) -> list[str]:
    return sorted(label for label, pattern in TOKEN_RISK_PATTERNS.items() if pattern.search(text))


def declared_shareability_issues(report: dict[str, Any], *, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    shareability = report.get("shareability")
    if not isinstance(shareability, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="declared-shareability-missing",
            evidence=f"{path_name} has no shareability metadata",
            recommendation="Regenerate the source report with --shareable before report-quality scoring or external planning.",
        )
        return issues

    mode = shareability.get("mode")
    includes_local_paths = shareability.get("localAbsolutePathsIncluded")
    if mode != "shareable" or includes_local_paths is not False:
        add_issue(
            issues,
            severity="review",
            rule_id="declared-shareability-local-mode",
            evidence=f"{path_name} declares shareability mode={mode or 'missing'} localAbsolutePathsIncluded={includes_local_paths!r}",
            recommendation="Regenerate the source report with --shareable so path-safe intent is explicit before sharing or scoring.",
        )
    return issues


def private_identifier_shareability_issues(
    report: dict[str, Any], *, raw_text: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    scope = report.get("scopeBoundary")
    is_product_qa = report.get("intent") == "shipguard-evaluation" or (
        isinstance(scope, dict) and scope.get("shipguardOnly") is True
    )
    if not is_product_qa or is_materialized_fixture_report(report):
        return issues
    shareability = report.get("shareability")
    if not isinstance(shareability, dict) or shareability.get("mode") != "shareable":
        return issues
    hits = ios_shareable.private_identifier_hits(raw_text, report)
    if hits:
        add_issue(
            issues,
            severity="high",
            rule_id="private-identifier-shareability-risk",
            evidence=f"{path_name} contains {len(hits)} private target identifier(s) in shareable ShipGuard-eval output",
            recommendation=(
                "Regenerate the report with the current ShipGuard shareable redaction path, or run "
                "shipguard ios redact with explicit --private-term values before external sharing."
            ),
        )
    return issues


def is_materialized_fixture_report(report: dict[str, Any]) -> bool:
    candidate = report.get("fixtureCandidate")
    if not isinstance(candidate, dict):
        return False
    scope = report.get("scopeBoundary")
    return (
        candidate.get("sourceReportsRedacted") is True
        and isinstance(scope, dict)
        and scope.get("shipguardOnly") is True
        and scope.get("targetAppsReadOnly") is True
    )


def value_gauntlet_probe_answer(report: dict[str, Any]) -> dict[str, Any]:
    probe = report.get("lowestValueSurfaceProbe")
    answer = probe.get("answer") if isinstance(probe, dict) and isinstance(probe.get("answer"), dict) else {}
    return answer if isinstance(answer, dict) else {}


def value_gauntlet_actionability_question(answer: dict[str, Any]) -> str | None:
    if not answer:
        return None
    identifier = str(answer.get("identifier") or "")
    missing = answer.get("missingDepthSignals")
    missing_signals = {str(item) for item in missing} if isinstance(missing, list) else set()
    if identifier == "shipguard v4-stable-release-publication" or "runtimeV4StableReleasePublication" in missing_signals:
        return (
            "Can ShipGuard prove stable-v4 publication with downloaded GitHub release assets, "
            "independent adoption evidence, final security review evidence, release notes, and "
            "post-release consumer proof?"
        )
    if identifier == "shipguard v4-product-release-stabilization" or "runtimeV4ProductReleaseStabilization" in missing_signals:
        return (
            "Should ShipGuard stabilize the v4 product release with external adoption evidence, "
            "final security review, rollback proof, package proof, and release proof consumption?"
        )
    name = str(answer.get("name") or answer.get("title") or identifier or "the current lowest-value ShipGuard surface").strip()
    recommendation = str(answer.get("recommendation") or "").strip()
    if recommendation:
        return f"Can ShipGuard improve {name} by proving this recommendation: {recommendation}"
    return f"Can ShipGuard turn {name} into a concrete fixture-backed improvement instead of leaving it as a vague priority?"


def value_gauntlet_stable_publication_priority_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    answer = value_gauntlet_probe_answer(report)
    missing = answer.get("missingDepthSignals")
    missing_signals = {str(item) for item in missing} if isinstance(missing, list) else set()
    is_stable_gap = answer.get("identifier") == "shipguard v4-stable-release-publication" or "runtimeV4StableReleasePublication" in missing_signals
    if not is_stable_gap:
        return []
    issues: list[dict[str, str]] = []
    priority = report.get("stablePublicationPriority") if isinstance(report.get("stablePublicationPriority"), dict) else {}
    if priority.get("status") != "review" or priority.get("priorityId") != "stable-v4-publication":
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-status-missing",
            evidence=f"{path_name} stablePublicationPriority does not mark stable-v4 publication as review",
            recommendation="Expose stablePublicationPriority.status=review and priorityId=stable-v4-publication when the lowest-value surface is stable publication.",
        )
    if not is_command_shaped(priority.get("nextCommand")) or "shipguard v4 stable-publication" not in str(priority.get("nextCommand") or ""):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-command-missing",
            evidence=f"{path_name} stablePublicationPriority has no copy-ready stable-publication command",
            recommendation="Add a concrete stable-publication command with release assets, adoption evidence, and security evidence placeholders.",
        )
    expected_blockers = {
        "public GitHub release metadata and release notes",
        "downloaded release assets",
        "post-release consumer proof",
        "independent adoption evidence",
        "final security review evidence",
    }
    if set(priority.get("blockedBy") or []) != expected_blockers:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-blockers-missing",
            evidence=f"{path_name} stablePublicationPriority does not list the stable-v4 proof blockers",
            recommendation="List release metadata, assets, consumer proof, adoption evidence, and security review as blockers.",
        )
    packet = priority.get("proofPacket") if isinstance(priority.get("proofPacket"), list) else []
    packet_ids = {str(item.get("id") or "") for item in packet if isinstance(item, dict)}
    expected_packet_ids = {
        "github-release-metadata",
        "release-notes",
        "downloaded-release-assets",
        "post-release-consumer-proof",
        "independent-adoption-evidence",
        "final-security-review-evidence",
    }
    if priority.get("firstBlocker") != "public-github-release-metadata" or packet_ids != expected_packet_ids:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-proof-packet-missing",
            evidence=f"{path_name} stablePublicationPriority does not expose the first blocker and full proof packet",
            recommendation="Add firstBlocker plus proofPacket rows for release metadata, notes, assets, consumer proof, adoption evidence, and security review.",
        )
    boundary = priority.get("proofBoundary") if isinstance(priority.get("proofBoundary"), dict) else {}
    if boundary.get("sourceOnlyCountsAsStableV4Proof") is not False or boundary.get("fixtureProofCountsAsStableV4Proof") is not False:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-nonclaims-missing",
            evidence=f"{path_name} stablePublicationPriority proofBoundary does not block source/fixture overclaims",
            recommendation="Keep source-only and fixture-backed reports from counting as stable-v4 proof.",
        )
    if "Stable Publication Priority" not in markdown or "Proof packet" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-priority-markdown-missing",
            evidence=f"{path_name} Markdown does not show the stable-publication proof packet",
            recommendation="Render Stable Publication Priority, first blocker, proof packet, blockers, and non-claims in Markdown.",
        )
    return issues


def report_questions(report: dict[str, Any], *, report_path: str, tool: str) -> list[dict[str, Any]]:
    questions = report.get("reportQualityQuestions")
    source_questions = questions if isinstance(questions, list) else []
    candidate_questions: list[str] = []
    if tool == "shipguard value-gauntlet":
        current_question = value_gauntlet_actionability_question(value_gauntlet_probe_answer(report))
        if current_question:
            candidate_questions.append(current_question)
    candidate_questions.extend(str(question) for question in source_questions if isinstance(question, str))
    materialized_fixture = is_materialized_fixture_report(report)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for question in candidate_questions[:8]:
        text = question.strip()
        if not text:
            continue
        key = normalized_question_text(text)
        if key in seen:
            continue
        seen.add(key)
        row = {
            "tool": tool,
            "report": report_path,
            "question": text,
        }
        if materialized_fixture:
            row["sourceMaterializedFixture"] = True
        rows.append(row)
    return rows


def add_issue(
    issues: list[dict[str, str]],
    *,
    severity: str,
    rule_id: str,
    evidence: str,
    recommendation: str,
) -> None:
    issues.append(
        {
            "severity": severity,
            "ruleId": rule_id,
            "evidence": evidence,
            "recommendation": recommendation,
        }
    )


def normalized_question_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def stable_publication_launch_relay_question(value: object) -> bool:
    text = normalized_question_text(value)
    return any(
        token in text
        for token in (
            "launch relay",
            "launch copy",
            "launch draft",
            "launch drafts",
            "product hunt",
            "r/shipguard",
            "hacker news",
            "public posting",
            "public post",
            "external launch",
            "computer-use",
        )
    )


def markdown_contains_token(markdown: str, token: object) -> bool:
    text = str(token or "").strip()
    if not text:
        return True
    return text in markdown or text.replace("|", "\\|") in markdown


LEAN_REVIEW_MODE_BIAS_CONTRACT = {
    "lite": {
        "firstActionBias": "suggestion-first",
        "priorityOrder": ["simplifyFirst", "deleteList", "blockedByProof"],
    },
    "full": {
        "firstActionBias": "proof-ladder",
        "priorityOrder": ["deleteList", "simplifyFirst", "blockedByProof"],
    },
    "ultra": {
        "firstActionBias": "delete-first",
        "priorityOrder": ["deleteList", "blockedByProof", "simplifyFirst"],
    },
}


def mode_action_key(action: object) -> tuple[str, str]:
    if not isinstance(action, dict):
        return ("", "")
    return (str(action.get("ruleId") or ""), str(action.get("location") or action.get("firstLocation") or ""))


def first_mode_priority_action(precision: dict[str, Any], priority_order: list[str]) -> tuple[dict[str, Any] | None, str]:
    for source in priority_order:
        rows = precision.get(source)
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            return rows[0], source
    return None, "none"


def list_matches_expected(value: object, expected: list[str]) -> bool:
    return isinstance(value, list) and [str(item) for item in value] == expected


def kebab_case(value: object) -> str:
    spaced = re.sub(r"(?<!^)(?=[A-Z])", "-", str(value or ""))
    return re.sub(r"[^a-z0-9]+", "-", spaced.lower()).strip("-")


def dedupe_question_rows(rows: list[dict[str, Any]], *, annotate_duplicates: bool = False) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = normalized_question_text(row.get("question") or "")
        if not key:
            continue
        if key in seen:
            if annotate_duplicates:
                existing = seen[key]
                existing["duplicateCount"] = int(existing.get("duplicateCount") or 1) + 1
                if row.get("sourceMaterializedFixture"):
                    existing["sourceMaterializedFixture"] = True
                report = str(row.get("report") or "").strip()
                if report and report != existing.get("report"):
                    duplicate_reports = existing.setdefault("duplicateReports", [])
                    if isinstance(duplicate_reports, list) and report not in duplicate_reports and len(duplicate_reports) < 8:
                        duplicate_reports.append(report)
            continue
        copied = dict(row)
        if annotate_duplicates:
            copied["duplicateCount"] = 1
            copied["duplicateReports"] = []
        deduped.append(copied)
        seen[key] = copied
    return deduped


def markdown_section_text(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"(?ims)^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)")
    match = pattern.search(markdown)
    return match.group(1) if match else ""


def spec_workflow_expected_questions(inputs: dict[str, Any], limit: int = 8) -> list[str]:
    raw_questions = inputs.get("actionabilityQuestions")
    if not isinstance(raw_questions, list):
        return []
    questions: list[str] = []
    seen: set[str] = set()
    for item in raw_questions:
        if isinstance(item, dict):
            question = str(item.get("question") or "").strip()
        else:
            question = str(item).strip()
        key = normalized_question_text(question)
        if question and key not in seen:
            questions.append(question)
            seen.add(key)
        if len(questions) >= limit:
            break
    return questions


def spec_workflow_feature_title(report: dict[str, Any]) -> str:
    feature = report.get("feature")
    if isinstance(feature, dict):
        return str(feature.get("title") or "").strip()
    return ""


def spec_workflow_slash_handoff_gaps(report: dict[str, Any]) -> list[str]:
    feature_title = spec_workflow_feature_title(report)
    feature_key = normalized_question_text(feature_title)
    checks = [
        ("slashPlan", "/plan", "plan"),
        ("slashGoal", "/goal", "goal"),
    ]
    gaps: list[str] = []
    for field, prefix, label in checks:
        text = str(report.get(field) or "").strip()
        normalized = normalized_question_text(text)
        if not text:
            gaps.append(f"{field} is missing")
            continue
        if not text.startswith(prefix + " "):
            gaps.append(f"{field} is not a {prefix} command")
        if feature_key and feature_key not in normalized:
            gaps.append(f"{field} does not name the feature")
        if "validate" not in normalized:
            gaps.append(f"{field} does not preserve validation proof guidance")
        if "next" not in normalized or "goal" not in normalized:
            gaps.append(f"{field} does not preserve the next-goal handoff")
        if label == "goal" and "plan" not in normalized:
            gaps.append(f"{field} does not preserve the next slash-plan handoff")
    return gaps


def score_for(issues: list[dict[str, str]]) -> int:
    score = 100
    for issue in issues:
        severity = issue["severity"]
        if severity == "high":
            score -= 25
        elif severity == "review":
            score -= 12
        else:
            score -= 4
    return max(0, score)


def severity_rank(value: object) -> int:
    return SEVERITY_PRIORITY.get(str(value or "").lower(), 9)


def status_rank(value: object) -> int:
    return STATUS_PRIORITY.get(str(value or "").lower(), 9)


def tool_priority(value: object) -> int:
    return TOOL_NEXT_ACTION_PRIORITY.get(str(value or ""), 99)


def is_launchdeck_receipt_question(question: object, tool: object) -> bool:
    question_text = normalized_question_text(question)
    if str(tool or "") != "shipguard ios launchdeck":
        return False
    if any(
        token in question_text
        for token in ("receipt", "missing build/run", "profiler proof", "proof for the selected lane")
    ):
        return True
    return "execution" in question_text and ("quality" in question_text or "proof bundle" in question_text)


def is_notification_scope_question(question: object) -> bool:
    text = normalized_question_text(question)
    return bool(
        "notification permission owner scopes" in text
        or "notification/permission owner scopes" in text
        or "review only lifecycle" in text
        or "review-only lifecycle" in text
        or "forbidden entitlement/project" in text
        or "forbidden entitlement" in text
    )


def is_notification_proof_lane_question(question: object) -> bool:
    text = normalized_question_text(question)
    if not text:
        return False
    proof_lane_tokens = (
        "permission-state" in text
        and "denied-state" in text
        and (
            "generic test log" in text
            or "generic test receipt" in text
            or "generic test receipts" in text
            or "generic receipt" in text
            or "generic validation" in text
            or "scope labels" in text
        )
    )
    return bool(
        proof_lane_tokens
        or "permission-state scope labels instead of accepting generic test receipts" in text
        or is_notification_simulator_device_boundary_question(question)
    )


def is_notification_simulator_device_boundary_question(question: object) -> bool:
    text = normalized_question_text(question)
    if not text:
        return False
    device_prompt = any(
        token in text
        for token in (
            "physical-device",
            "physical device",
            "real-device",
            "real device",
            "manual/device",
            "manual device",
            "device prompt",
            "device receipt",
        )
    )
    prompt_or_release = any(
        token in text
        for token in (
            "prompt proof",
            "permission prompt",
            "prompt receipt",
            "release claim",
            "release proof",
            "release-ready",
            "fully verified",
        )
    )
    return bool(
        (("simulator" in text or "simulator reset" in text or "simctl" in text) and device_prompt and prompt_or_release)
        or (
            "simulator denied-state proof" in text
            and "physical-device prompt proof" in text
        )
    )


def synthetic_notification_domain_risk_pack() -> dict[str, Any]:
    return {
        "id": "ios-notification-permission-workflow",
        "version": "1",
        "status": "active",
        "triggerSignals": [
            "profile:ios",
            "goal:notification",
            "goal:permission",
        ],
        "scopeRecommendations": {
            "authorized": [
                {
                    "pattern": "Sources/SyntheticPermissions/**",
                    "reason": "Synthetic source owner for notification permission copy and copy-only UI.",
                },
                {
                    "pattern": "Tests/SyntheticPermissionsTests/**",
                    "reason": "Synthetic test owner for permission-state validation.",
                },
            ],
            "reviewOnly": [
                {
                    "pattern": "**/Info.plist",
                    "reason": "Permission purpose strings can change review behavior and require human review.",
                },
                {
                    "pattern": "**/*AppDelegate*.swift",
                    "reason": "Notification registration lifecycle changes must be reviewed before editing.",
                },
                {
                    "pattern": "**/*SceneDelegate*.swift",
                    "reason": "Scene lifecycle notification routing must be reviewed before editing.",
                },
            ],
            "forbiddenUnlessExplicit": [
                {
                    "pattern": "**/*.entitlements",
                    "reason": "Entitlement changes are release/signing sensitive and require explicit authorization.",
                },
                {
                    "pattern": "**/project.pbxproj",
                    "reason": "Project graph changes are forbidden unless the task explicitly authorizes Xcode project edits.",
                },
            ],
        },
        "candidateEvidence": {
            "permissionSensitiveFiles": [
                {
                    "path": "Sources/SyntheticPermissions/NotificationPermissionCopy.swift",
                    "signals": [
                        "source references UNUserNotificationCenter",
                        "path references notification permission",
                    ],
                },
                {
                    "path": "Tests/SyntheticPermissionsTests/NotificationPermissionStateTests.swift",
                    "signals": ["test path references permission-state"],
                },
            ],
            "scannedFileLimit": 10000,
            "shareable": True,
        },
        "validationReceiptRequirements": [
            {
                "id": "permission-state-validation",
                "validationId": "swift-test",
                "command": "swift test",
                "requiredReceiptScope": ["permission-state", "denied-state", "not-determined-state"],
                "expectedArtifact": "structured validation receipt with permission-state scope labels",
                "successCondition": "Tests or UI automation cover not-determined, denied, and authorized/provisional states.",
                "failureMeaning": "Permission-state behavior remains a generic test claim, not a permission workflow proof.",
            },
            {
                "id": "simulator-denied-state-recovery",
                "proofType": "ios-permission-simulator-reset",
                "environment": "simulator",
                "expectedArtifact": "simulator screenshot, UI log, or receipt after resetting notification permission state",
                "successCondition": "Denied-state recovery is observed after a simulator permission reset.",
                "failureMeaning": "The denied-state recovery path remains unproven in a runnable local environment.",
            },
            {
                "id": "physical-device-prompt-boundary",
                "proofType": "ios-permission-prompt-physical-device",
                "environment": "physical-device",
                "releaseOnly": True,
                "expectedArtifact": "physical-device prompt receipt or manually reviewed screenshot reference",
                "successCondition": "Real-device prompt timing and wording are observed before release claims.",
                "failureMeaning": "ShipGuard must not treat simulator/source evidence as physical-device prompt proof.",
            },
        ],
        "proofBoundaries": {
            "localAutomation": "Structured validation receipts can prove state handling and regression coverage.",
            "simulator": "Simulator proof can show reset/denied-state recovery, but not final physical-device prompt truth.",
            "physicalDevice": "Physical-device prompt timing, OS-level permission UI, and release claims need manual/device proof.",
        },
        "nextAction": {
            "owner": "developer",
            "command": "swift test",
            "expectedArtifact": "structured receipt with scope labels: permission-state, denied-state, not-determined-state, simulator-permission-reset",
            "successCondition": "ShipGuard verify can distinguish local permission workflow proof from manual device proof.",
            "failureMeaning": "Notification permission work remains generic validation rather than a permission workflow contract.",
        },
        "reportQualityQuestions": [
            "Did prepare identify notification/permission owner scopes, review-only lifecycle/plist surfaces, and forbidden entitlement/project changes?",
            "Did verify require permission-state and denied-state proof instead of treating a generic test log as enough?",
            "Did the verdict separate simulator denied-state proof from physical-device prompt proof before release claims?",
        ],
    }


def synthetic_notification_scope_markdown_lines() -> list[str]:
    return [
        "## iOS Notification Permission Workflow",
        "",
        "- Status: `active`",
        "- Trigger signals: `profile:ios`, `goal:notification`, `goal:permission`",
        "",
        "### Permission-sensitive source signals",
        "",
        "| Path | Signals |",
        "| --- | --- |",
        "| `Sources/SyntheticPermissions/NotificationPermissionCopy.swift` | source references UNUserNotificationCenter; path references notification permission |",
        "| `Tests/SyntheticPermissionsTests/NotificationPermissionStateTests.swift` | test path references permission-state |",
        "",
        "### Scope recommendations",
        "",
        "Authorized candidate:",
        "",
        "| Pattern | Reason |",
        "| --- | --- |",
        "| `Sources/SyntheticPermissions/**` | Synthetic source owner for notification permission copy and copy-only UI. |",
        "| `Tests/SyntheticPermissionsTests/**` | Synthetic test owner for permission-state validation. |",
        "",
        "Review only:",
        "",
        "| Pattern | Reason |",
        "| --- | --- |",
        "| `**/Info.plist` | Permission purpose strings can change review behavior and require human review. |",
        "| `**/*AppDelegate*.swift` | Notification registration lifecycle changes must be reviewed before editing. |",
        "| `**/*SceneDelegate*.swift` | Scene lifecycle notification routing must be reviewed before editing. |",
        "",
        "Forbidden unless explicit:",
        "",
        "| Pattern | Reason |",
        "| --- | --- |",
        "| `**/*.entitlements` | Entitlement changes are release/signing sensitive and require explicit authorization. |",
        "| `**/project.pbxproj` | Project graph changes are forbidden unless the task explicitly authorizes Xcode project edits. |",
        "",
        "### Receipt requirements",
        "",
        "- permission-state-validation: permission-state, denied-state, not-determined-state",
        "  Expected: structured validation receipt with permission-state scope labels",
        "  Success: Tests or UI automation cover not-determined, denied, and authorized/provisional states.",
        "  Failure meaning: Permission-state behavior remains a generic test claim, not a permission workflow proof.",
        "- simulator-denied-state-recovery: ios-permission-simulator-reset",
        "  Expected: simulator screenshot, UI log, or receipt after resetting notification permission state",
        "  Success: Denied-state recovery is observed after a simulator permission reset.",
        "  Failure meaning: The denied-state recovery path remains unproven in a runnable local environment.",
        "- physical-device-prompt-boundary: ios-permission-prompt-physical-device",
        "  Expected: physical-device prompt receipt or manually reviewed screenshot reference",
        "  Success: Real-device prompt timing and wording are observed before release claims.",
        "  Failure meaning: ShipGuard must not treat simulator/source evidence as physical-device prompt proof.",
        "",
        "### Proof boundaries",
        "",
        "- localAutomation: Structured validation receipts can prove state handling and regression coverage.",
        "- simulator: Simulator proof can show reset/denied-state recovery, but not final physical-device prompt truth.",
        "- physicalDevice: Physical-device prompt timing, OS-level permission UI, and release claims need manual/device proof.",
        "",
        "### Next action",
        "",
        "- Command: `swift test`",
        "- Expected artifact: structured receipt with scope labels: permission-state, denied-state, not-determined-state, simulator-permission-reset",
        "- Success: ShipGuard verify can distinguish local permission workflow proof from manual device proof.",
        "- Failure meaning: Notification permission work remains generic validation rather than a permission workflow contract.",
        "",
    ]


def release_stabilization_signal_text(value: object) -> bool:
    text = normalized_question_text(value)
    if not text:
        return False
    if "v4 product release" in text or "stable v4" in text:
        return any(
            token in text
            for token in (
                "external adoption",
                "security review",
                "rollback",
                "package proof",
                "release proof",
                "release asset",
                "fresh install",
                "install proof",
            )
        )
    return False


def launchkey_release_artifact_question(value: object) -> bool:
    text = normalized_question_text(value)
    if not text:
        return False
    return any(
        all(token in text for token in token_group)
        for token_group in (
            ("fresh user", "install", "release package"),
            ("download release assets", "verify"),
            ("release assets", "manifest"),
            ("release assets", "sha-256"),
            ("release proof", "consumption"),
            ("external adoption", "security review"),
        )
    )


def source_priority_signal(report: dict[str, Any]) -> dict[str, Any]:
    tool = str(report.get("tool") or "")
    result_ux = report.get("resultUX") if isinstance(report.get("resultUX"), dict) else {}
    result_text = " ".join(
        str(result_ux.get(field) or "")
        for field in ("nextActionSummary", "verdict", "whyItMatters", "nextCommand")
    )
    questions = report.get("reportQualityQuestions")
    question_text = " ".join(str(item) for item in questions if isinstance(item, str)) if isinstance(questions, list) else ""

    if tool == "shipguard value-gauntlet":
        answer = value_gauntlet_probe_answer(report)
        missing = answer.get("missingDepthSignals")
        missing_text = " ".join(str(item) for item in missing) if isinstance(missing, list) else ""
        combined = " ".join(
            str(value or "")
            for value in (
                answer.get("identifier"),
                answer.get("name"),
                answer.get("title"),
                answer.get("recommendation"),
                missing_text,
                result_text,
                question_text,
            )
        )
        if (
            "runtimeV4StableReleasePublication" in missing_text
            or "v4-stable-release-publication" in normalized_question_text(answer.get("identifier") or "")
            or (
                ("stable-v4" in normalized_question_text(combined) or "stable v4" in normalized_question_text(combined))
                and any(
                    token in normalized_question_text(combined)
                    for token in ("downloaded github release assets", "post-release consumer proof", "final security review")
                )
            )
        ):
            return {
                "kind": "v4-stable-release-publication",
                "priority": -40,
                "reason": "value-gauntlet lowest-value surface is stable-v4 publication",
            }
        if (
            "runtimeV4ProductReleaseStabilization" in missing_text
            or "v4-product-release-stabilization" in normalized_question_text(answer.get("identifier") or "")
            or release_stabilization_signal_text(combined)
        ):
            return {
                "kind": "v4-product-release-stabilization",
                "priority": -35,
                "reason": "value-gauntlet lowest-value surface is v4 product release stabilization",
            }

    if tool == "shipguard v4 release-candidate":
        readiness = report.get("releaseReadiness")
        readiness_text = json.dumps(readiness, sort_keys=True) if isinstance(readiness, dict) else ""
        combined = " ".join((result_text, question_text, readiness_text))
        if "not-provided" in normalized_question_text(combined) or release_stabilization_signal_text(combined):
            return {
                "kind": "launchkey-stable-v4-proof-gap",
                "priority": -30,
                "reason": "LaunchKey release-readiness evidence still has stable-v4 proof gaps",
            }

    if tool == "shipguard v4 stable-publication":
        combined = " ".join((result_text, question_text, json.dumps(report.get("stablePublicationGates") or [], sort_keys=True)))
        if report.get("status") != "pass" or report.get("stableV4Release") is not True:
            return {
                "kind": "stable-publication-proof-gap",
                "priority": -45,
                "reason": "stable-publication report blocks the stable-v4 claim until real publication evidence passes",
            }
        if "stable-publication" in normalized_question_text(combined):
            return {
                "kind": "stable-publication-proof-passed",
                "priority": -25,
                "reason": "stable-publication proof is the current release proof source",
            }

    if release_stabilization_signal_text(f"{result_text} {question_text}"):
        return {
            "kind": "result-ux-release-stabilization",
            "priority": -20,
            "reason": "source report result UX points to v4 release stabilization proof",
        }

    return {"kind": None, "priority": 0, "reason": None}


def source_block_priority(row: dict[str, Any]) -> int:
    return 0 if status_rank(row.get("sourceStatus")) == 0 else 1


def question_focus_priority(row: dict[str, Any]) -> int:
    question = normalized_question_text(row.get("question") or "")
    tool = str(row.get("tool") or "")
    source_status = str(row.get("sourceStatus") or "")
    source_signal_priority = row.get("sourcePriority")
    priority = int(source_signal_priority) if isinstance(source_signal_priority, int) else 0
    if tool == "shipguard ios launchdeck" and source_status != "pass":
        if any(token in question for token in ("missing build/run", "proof for the selected lane", "when receipts")):
            priority = min(priority, -30)
        if is_launchdeck_receipt_question(question, tool):
            priority = min(priority, -20)
    if tool == "shipguard codex marketplace-readiness" and any(
        token in question
        for token in (
            "docs/index",
            "first-time users",
            "command dump",
            "release wall",
            "onboarding",
        )
    ):
        priority = min(priority, -20)
    if release_stabilization_signal_text(question):
        priority = min(priority, -35)
    if launchkey_release_artifact_question(question):
        priority = min(priority, -25)
    if should_create_fixture_candidate(question):
        priority = min(priority, -10)
    return priority


def report_status(issues: list[dict[str, str]]) -> str:
    if any(issue["severity"] == "high" for issue in issues):
        return "blocked"
    if any(issue["severity"] == "review" for issue in issues):
        return "review"
    return "pass"


def finding_quality_issues(report: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return issues
    for index, item in enumerate(findings[:20], start=1):
        if not isinstance(item, dict):
            add_issue(
                issues,
                severity="high",
                rule_id="finding-shape-invalid",
                evidence=f"finding #{index} is not an object",
                recommendation="Emit findings as structured objects with rule id, severity, evidence, recommendation, and proof guidance.",
            )
            continue
        missing = [field for field in ("severity", "ruleId") if not item.get(field)]
        if missing:
            add_issue(
                issues,
                severity="high",
                rule_id="finding-required-fields-missing",
                evidence=f"finding #{index} missing {', '.join(missing)}",
                recommendation="Keep report findings machine-grade so evals and docs can reason about them.",
            )
        if not item.get("evidence"):
            add_issue(
                issues,
                severity="review",
                rule_id="finding-evidence-missing",
                evidence=f"finding #{index} has no evidence field",
                recommendation="Attach concrete source, report, or proof evidence to each finding.",
            )
        if not item.get("recommendation"):
            add_issue(
                issues,
                severity="review",
                rule_id="finding-recommendation-missing",
                evidence=f"finding #{index} has no recommendation field",
                recommendation="Tell the next ShipGuard iteration what to refine in the report or rule.",
            )
        if not (item.get("proof") or item.get("proofGuidance")):
            add_issue(
                issues,
                severity="review",
                rule_id="finding-proof-guidance-missing",
                evidence=f"finding #{index} has no proof or proofGuidance field",
                recommendation="Add proof guidance so a solo developer knows what evidence would confirm the issue.",
            )
    return issues


def is_command_shaped(value: object) -> bool:
    text = " ".join(str(value or "").split())
    if not text or "`" in text:
        return False
    return bool(COMMAND_SHAPED_RE.match(text))


def result_ux_quality_issues(report: dict[str, Any], *, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    result = report.get("resultUX")
    if not isinstance(result, dict):
        return issues
    next_command = str(result.get("nextCommand") or "").strip()
    if not is_command_shaped(next_command):
        add_issue(
            issues,
            severity="review",
            rule_id="result-ux-next-command-not-command",
            evidence=f"{path_name} resultUX.nextCommand is prose or Markdown instead of a command template",
            recommendation="Move human explanation into resultUX.nextActionSummary and keep nextCommand as a runnable ShipGuard, test, or tool command template.",
        )
    if str(report.get("tool") or "") == "shipguard v4 stable-publication":
        result_summary = " ".join(
            str(result.get(field) or "")
            for field in ("nextActionSummary", "priorityAction", "proofSource")
        )
        leaked_tokens = [
            token
            for token in (
                "stablePublicationClosureChecklist",
                "githubReleaseMetadataProof",
                "releaseNotesProof",
                "releaseCandidatePacketProof",
                "publishedReleaseAssetProof",
                "postReleaseConsumerProof",
                "publicReleaseFreshnessProof",
                "releaseVersionCoherenceProof",
                "releaseAssetCoherenceProof",
                "externalAdoptionEvidenceStableGate",
                "securityReviewEvidenceStableGate",
            )
            if token in result_summary
        ]
        if leaked_tokens:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-result-ux-internal-name-leak",
                evidence=f"{path_name} resultUX leaks internal stable-publication field names: {', '.join(leaked_tokens)}",
                recommendation="Use reader-facing labels in resultUX.nextActionSummary, priorityAction, and proofSource while keeping schema field names in structured JSON fields.",
            )
    priority = report.get("priorityAction")
    if isinstance(priority, dict) and "nextCommand" in priority and not is_command_shaped(priority.get("nextCommand")):
        add_issue(
            issues,
            severity="review",
            rule_id="priority-action-next-command-not-command",
            evidence=f"{path_name} priorityAction.nextCommand is prose or Markdown instead of a command template",
            recommendation="Keep priorityAction.nextCommand runnable; put explanation in priorityAction.summary or recommendation.",
        )
    return issues


def verify_pr_report_quality_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard action verify-pr":
        return issues
    guide = report.get("freshMaintainerFailureGuide")
    if not isinstance(guide, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="verify-pr-failure-guide-missing",
            evidence=f"{path_name} has no freshMaintainerFailureGuide",
            recommendation="Emit a blocker-first failure guide so a fresh maintainer sees the first real fix before lower-severity review items.",
        )
        return issues
    if "Fresh Maintainer Failure Guide" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="verify-pr-failure-guide-markdown-missing",
            evidence=f"{path_name} Markdown does not render the fresh maintainer failure guide",
            recommendation="Render the static/runtime phase guide in Markdown so humans do not have to inspect JSON.",
        )
    status = str(report.get("status") or "")
    first_action = guide.get("firstAction") if isinstance(guide.get("firstAction"), dict) else {}
    if status == "blocked" and first_action.get("severity") != "blocked":
        add_issue(
            issues,
            severity="review",
            rule_id="verify-pr-first-action-not-blocker",
            evidence=f"{path_name} is blocked but freshMaintainerFailureGuide.firstAction is not a blocker",
            recommendation="Choose the first blocked finding as the next action before lower-severity review findings.",
        )
    if status == "blocked" and not guide.get("firstBlockingRuleId"):
        add_issue(
            issues,
            severity="review",
            rule_id="verify-pr-first-blocker-missing",
            evidence=f"{path_name} is blocked but freshMaintainerFailureGuide.firstBlockingRuleId is empty",
            recommendation="Record the first blocking rule id so report-quality and humans can verify blocker-first routing.",
        )
    phases = guide.get("phases")
    phase_titles = {str(item.get("title") or "") for item in phases if isinstance(item, dict)} if isinstance(phases, list) else set()
    if not {"Static workflow setup", "Runtime artifact proof"}.issubset(phase_titles):
        add_issue(
            issues,
            severity="review",
            rule_id="verify-pr-failure-guide-phases-missing",
            evidence=f"{path_name} freshMaintainerFailureGuide does not include both static and runtime phases",
            recommendation="Separate static workflow setup from runtime artifact proof so maintainers know which proof lane failed.",
        )
    runtime_artifact = report.get("runtimeArtifact") if isinstance(report.get("runtimeArtifact"), dict) else {}
    if runtime_artifact.get("provided"):
        handoff = report.get("runtimeReviewerHandoff")
        if not isinstance(handoff, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-handoff-missing",
                evidence=f"{path_name} inspected a runtime artifact but has no runtimeReviewerHandoff",
                recommendation="Emit a reviewer handoff with decision, proof-to-attach, reviewer action, and failure meaning.",
            )
            return issues
        if "Runtime Reviewer Handoff" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-handoff-markdown-missing",
                evidence=f"{path_name} Markdown does not render the runtime reviewer handoff",
                recommendation="Render the runtime reviewer handoff in Markdown so PR reviewers do not need to parse JSON.",
            )
        decision = str(handoff.get("decision") or "").strip()
        reviewer_action = str(handoff.get("reviewerAction") or "").strip()
        failure_meaning = str(handoff.get("failureMeaning") or "").strip()
        proof_to_attach = handoff.get("proofToAttach") if isinstance(handoff.get("proofToAttach"), list) else []
        if not decision:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-decision-missing",
                evidence=f"{path_name} runtimeReviewerHandoff.decision is empty",
                recommendation="State whether the runtime artifact means ready-for-maintainer-review, needs review, do-not-merge, or do-not-use-artifact.",
            )
        if not reviewer_action:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-action-missing",
                evidence=f"{path_name} runtimeReviewerHandoff.reviewerAction is empty",
                recommendation="Tell the reviewer exactly what to do next with the downloaded artifact.",
            )
        if not failure_meaning:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-failure-meaning-missing",
                evidence=f"{path_name} runtimeReviewerHandoff.failureMeaning is empty",
                recommendation="Explain what a failed or incomplete artifact means so a green-looking decorative artifact is not trusted.",
            )
        if not proof_to_attach:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-proof-list-missing",
                evidence=f"{path_name} runtimeReviewerHandoff.proofToAttach is empty",
                recommendation="List the exact proof files or receipts a maintainer should attach to the PR review.",
            )
        if str(runtime_artifact.get("status") or "") != "pass" and not decision.startswith("do-not"):
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-invalid-artifact-decision",
                evidence=f"{path_name} runtime artifact is not pass but reviewer decision is {decision!r}",
                recommendation="Route incomplete or invalid runtime artifacts to a do-not-use/do-not-merge reviewer decision.",
            )
        if str(runtime_artifact.get("status") or "") == "pass" and decision in {"", "download-runtime-artifact", "do-not-use-artifact"}:
            add_issue(
                issues,
                severity="review",
                rule_id="verify-pr-runtime-reviewer-pass-decision-too-vague",
                evidence=f"{path_name} runtime artifact passed but reviewer decision is {decision!r}",
                recommendation="Translate a consumable runtime artifact into ready-for-maintainer-review, needs-maintainer-review, or do-not-merge based on verdict status and merge verdict.",
            )
    return issues


def launchkey_release_asset_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("publishedReleaseAssetProof")
    if not isinstance(proof, dict) or not proof.get("provided"):
        return []
    issues: list[dict[str, str]] = []
    attachment = proof.get("releaseAssetProofAttachment")
    if not isinstance(attachment, dict) or not attachment:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-missing",
            evidence=f"{path_name} publishedReleaseAssetProof participated but has no releaseAssetProofAttachment",
            recommendation="Attach a compact releaseAssetProofAttachment with release-consume paths, digest status, next command, missing artifacts, and proof boundary.",
        )
        return issues
    if attachment.get("status") != proof.get("status"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-status-drift",
            evidence=f"{path_name} releaseAssetProofAttachment.status does not mirror publishedReleaseAssetProof.status",
            recommendation="Keep the attachment status aligned with the root release asset proof status.",
        )
    if not attachment.get("consumerReportPath") and "consumer-report.json" not in (attachment.get("missingProofArtifacts") or []):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-consumer-path-missing",
            evidence=f"{path_name} releaseAssetProofAttachment hides consumer-report.json and does not list it as missing",
            recommendation="Expose consumerReportPath when release-consume ran, or list consumer-report.json in missingProofArtifacts.",
        )
    if not attachment.get("assetDigestMatrixPath") and "asset-digests.json" not in (attachment.get("missingProofArtifacts") or []):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-digest-path-missing",
            evidence=f"{path_name} releaseAssetProofAttachment hides asset-digests.json and does not list it as missing",
            recommendation="Expose assetDigestMatrixPath when release-consume ran, or list asset-digests.json in missingProofArtifacts.",
        )
    boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
    if (
        boundary.get("downloadedOrSuppliedReleaseAssetsRequired") is not True
        or boundary.get("releaseConsumeVerificationRequired") is not True
        or boundary.get("assetDigestMatrixRequired") is not True
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-boundary-missing",
            evidence=f"{path_name} releaseAssetProofAttachment weakens the release asset proof boundary",
            recommendation="State that downloaded/supplied assets, release-consume, and asset-digests are required; source-only and fixture proof do not count for stable-v4 publication.",
        )
    if "Release Asset Proof Attachment" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-release-asset-proof-attachment-markdown-missing",
            evidence=f"{path_name} Markdown does not render the release asset proof attachment",
            recommendation="Render the attachment under Published Release Asset Proof so maintainers can find consumer paths and digest status without opening JSON.",
        )
    return issues


def launchkey_fresh_install_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("freshInstallPackageProof")
    if not isinstance(proof, dict) or not proof.get("provided"):
        return []
    issues: list[dict[str, str]] = []
    attachment = proof.get("freshInstallProofAttachment")
    if not isinstance(attachment, dict) or not attachment:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-fresh-install-proof-attachment-missing",
            evidence=f"{path_name} freshInstallPackageProof participated but has no freshInstallProofAttachment",
            recommendation="Attach a compact freshInstallProofAttachment with install paths, version exits, validation exit, forbidden installed paths, next command, and proof boundary.",
        )
        return issues
    if attachment.get("status") != proof.get("status"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-fresh-install-proof-attachment-status-drift",
            evidence=f"{path_name} freshInstallProofAttachment.status does not mirror freshInstallPackageProof.status",
            recommendation="Keep the attachment status aligned with the root fresh install proof status.",
        )
    if attachment.get("validateExitCode") is None and "shipguard-validate" not in (attachment.get("missingProofArtifacts") or []):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-fresh-install-proof-attachment-validate-proof-missing",
            evidence=f"{path_name} freshInstallProofAttachment hides shipguard validate status and does not list it as missing",
            recommendation="Expose validateExitCode when validation ran, or list shipguard-validate in missingProofArtifacts.",
        )
    boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
    if (
        boundary.get("freshInstallRequiredForStableV4") is not True
        or boundary.get("cleanPrefixInstallRequired") is not True
        or boundary.get("shipguardValidateRequired") is not True
        or boundary.get("legacyAliasVersionRequired") is not True
        or boundary.get("generatedCacheVcsPathsForbidden") is not True
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-fresh-install-proof-attachment-boundary-missing",
            evidence=f"{path_name} freshInstallProofAttachment weakens the fresh-install proof boundary",
            recommendation="State that a clean prefix install, version checks, shipguard validate, and clean installed tree are required; source-only and fixture proof do not count for stable-v4 publication.",
        )
    if "Fresh Install Proof Attachment" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-fresh-install-proof-attachment-markdown-missing",
            evidence=f"{path_name} Markdown does not render the fresh install proof attachment",
            recommendation="Render the attachment under Fresh Install Package Proof so maintainers can inspect install and validation proof without opening JSON.",
        )
    return issues


def launchkey_upgrade_rollback_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    configs = [
        {
            "proofKey": "upgradePackageProof",
            "attachmentKey": "upgradeProofAttachment",
            "slug": "upgrade",
            "title": "Upgrade Proof Attachment",
            "exitField": "validateExitCode",
            "missingArtifact": "shipguard-validate",
            "boundary": [
                "samePrefixUpgradeRequiredForStableV4",
                "previousPackageInstallRequired",
                "candidatePackageInstallRequired",
                "versionChecksRequired",
                "shipguardValidateRequired",
                "cleanInstalledTreeRequired",
            ],
        },
        {
            "proofKey": "rollbackPackageProof",
            "attachmentKey": "rollbackProofAttachment",
            "slug": "rollback",
            "title": "Rollback Proof Attachment",
            "exitField": "versionExitCode",
            "missingArtifact": "shipguard-version",
            "boundary": [
                "rollbackCleanupRequiredForStableV4",
                "temporaryPrefixInstallRequired",
                "versionCheckRequired",
                "knownPackageStateRemovalRequired",
            ],
        },
    ]
    issues: list[dict[str, str]] = []
    for config in configs:
        proof = report.get(str(config["proofKey"]))
        if not isinstance(proof, dict) or not proof.get("provided"):
            continue
        attachment = proof.get(str(config["attachmentKey"]))
        slug = str(config["slug"])
        if not isinstance(attachment, dict) or not attachment:
            add_issue(
                issues,
                severity="review",
                rule_id=f"launchkey-{slug}-proof-attachment-missing",
                evidence=f"{path_name} {config['proofKey']} participated but has no {config['attachmentKey']}",
                recommendation=f"Attach a compact {config['attachmentKey']} with paths, version or validation exits, missing artifacts, next command, and proof boundary.",
            )
            continue
        if attachment.get("status") != proof.get("status"):
            add_issue(
                issues,
                severity="review",
                rule_id=f"launchkey-{slug}-proof-attachment-status-drift",
                evidence=f"{path_name} {config['attachmentKey']}.status does not mirror {config['proofKey']}.status",
                recommendation=f"Keep {config['attachmentKey']}.status aligned with the root {config['proofKey']} status.",
            )
        missing_artifacts = attachment.get("missingProofArtifacts") or []
        if attachment.get(str(config["exitField"])) is None and config["missingArtifact"] not in missing_artifacts:
            add_issue(
                issues,
                severity="review",
                rule_id=f"launchkey-{slug}-proof-attachment-exit-proof-missing",
                evidence=f"{path_name} {config['attachmentKey']} hides {config['exitField']} and does not list {config['missingArtifact']} as missing",
                recommendation=f"Expose {config['exitField']} when the proof ran, or list {config['missingArtifact']} in missingProofArtifacts.",
            )
        boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
        if (
            any(boundary.get(key) is not True for key in config["boundary"])
            or boundary.get("sourceOnlyProofCounts") is not False
            or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id=f"launchkey-{slug}-proof-attachment-boundary-missing",
                evidence=f"{path_name} {config['attachmentKey']} weakens the stable-v4 proof boundary",
                recommendation="State the required package proof steps and that source-only or fixture proof does not count for stable-v4 publication.",
            )
        if str(config["title"]) not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id=f"launchkey-{slug}-proof-attachment-markdown-missing",
                evidence=f"{path_name} Markdown does not render {config['title']}",
                recommendation=f"Render {config['title']} so maintainers can inspect package proof without opening JSON.",
            )
    return issues


def launchkey_download_blocking_proof_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("githubReleaseAssetDownloadProof")
    if not isinstance(proof, dict) or not proof.get("requested") or proof.get("status") in {"pass", "not-requested"}:
        return []
    issues: list[dict[str, str]] = []
    blocking = proof.get("downloadBlockingProof")
    if not isinstance(blocking, dict) or not blocking:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-missing",
            evidence=f"{path_name} githubReleaseAssetDownloadProof blocked but has no downloadBlockingProof",
            recommendation="Attach downloadBlockingProof with repo, tag, endpoint, download directory, error, next command, and proof boundary.",
        )
        return issues
    if blocking.get("status") != proof.get("status"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-status-drift",
            evidence=f"{path_name} downloadBlockingProof.status does not mirror githubReleaseAssetDownloadProof.status",
            recommendation="Keep downloadBlockingProof.status aligned with githubReleaseAssetDownloadProof.status.",
        )
    if not blocking.get("error") and not blocking.get("summary"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-error-missing",
            evidence=f"{path_name} downloadBlockingProof hides the download failure reason",
            recommendation="Expose the short download error or summary so maintainers know whether repo, tag, API, destination, or asset metadata blocked the run.",
        )
    if not blocking.get("nextCommand"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-next-command-missing",
            evidence=f"{path_name} downloadBlockingProof has no rerun command",
            recommendation="Expose the LaunchKey rerun command with --download-release-assets and --github-release-repo placeholders.",
        )
    handoff = blocking.get("receiptHandoff") if isinstance(blocking.get("receiptHandoff"), dict) else {}
    if not handoff:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-receipt-handoff-missing",
            evidence=f"{path_name} downloadBlockingProof has no receiptHandoff",
            recommendation="Attach a receiptHandoff that points stable-publication at the candidate report, names the blocking evidence, and keeps the repair command visible.",
        )
    else:
        handoff_boundary = handoff.get("proofBoundary") if isinstance(handoff.get("proofBoundary"), dict) else {}
        if (
            handoff.get("receipt") != "githubReleaseAssetDownloadProof"
            or not handoff.get("candidateReportPath")
            or not handoff.get("repairCommand")
            or not handoff.get("stablePublicationCommand")
            or handoff_boundary.get("attachCandidateReportToStablePublication") is not True
            or handoff_boundary.get("blockedDownloadCountsAsStableV4Proof") is not False
            or handoff_boundary.get("releaseConsumeStillRequiredForStableV4") is not True
            or handoff_boundary.get("sourceOnlyProofCounts") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="launchkey-download-blocking-receipt-handoff-weak",
                evidence=f"{path_name} downloadBlockingProof receiptHandoff is incomplete",
                recommendation="Keep the blocking handoff tied to the candidate report, repair command, stable-publication command, blocked-download non-proof boundary, and release-consume requirement.",
            )
    boundary = blocking.get("proofBoundary") if isinstance(blocking.get("proofBoundary"), dict) else {}
    if (
        boundary.get("githubReleaseRepoRequired") is not True
        or boundary.get("ownerRepoSyntaxRequired") is not True
        or boundary.get("emptyDownloadDestinationRequired") is not True
        or boundary.get("releaseAssetsRequired") is not True
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-boundary-missing",
            evidence=f"{path_name} downloadBlockingProof weakens the GitHub release asset download boundary",
            recommendation="State that repo/tag/API access, empty destination, and real release assets are required; source-only and fixture proof do not count for stable-v4 publication.",
        )
    if "Download Blocking Proof" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-proof-markdown-missing",
            evidence=f"{path_name} Markdown does not render Download Blocking Proof",
            recommendation="Render Download Blocking Proof under GitHub Release Asset Download so maintainers can inspect the download blocker without opening JSON.",
        )
    if handoff and "Download Blocking Receipt Handoff" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-blocking-receipt-handoff-markdown-missing",
            evidence=f"{path_name} Markdown does not render Download Blocking Receipt Handoff",
            recommendation="Render Download Blocking Receipt Handoff so the repair and stable-publication paths are visible without opening JSON.",
        )
    return issues


def launchkey_download_proof_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("githubReleaseAssetDownloadProof")
    if not isinstance(proof, dict) or not proof.get("requested") or proof.get("status") != "pass":
        return []
    issues: list[dict[str, str]] = []
    attachment = proof.get("downloadProofAttachment")
    if not isinstance(attachment, dict) or not attachment:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-missing",
            evidence=f"{path_name} githubReleaseAssetDownloadProof passed but has no downloadProofAttachment",
            recommendation="Attach downloadProofAttachment with repo, tag, endpoint, destination, downloaded asset names, SHA-256 rows, next command, and proof boundary.",
        )
        return issues
    if attachment.get("status") != "pass":
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-status-drift",
            evidence=f"{path_name} downloadProofAttachment.status does not mirror the passing download proof",
            recommendation="Keep downloadProofAttachment.status aligned with githubReleaseAssetDownloadProof.status.",
        )
    if not attachment.get("assetCount") or not attachment.get("downloadedAssetNames"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-assets-missing",
            evidence=f"{path_name} downloadProofAttachment hides downloaded release asset names",
            recommendation="List the downloaded release assets so maintainers can inspect the native download without opening downloadedAssets.",
        )
    if not attachment.get("downloadedAssetDigests"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-digests-missing",
            evidence=f"{path_name} downloadProofAttachment hides downloaded asset SHA-256 rows",
            recommendation="Carry compact downloadedAssetDigests with asset name and SHA-256 values.",
        )
    if not attachment.get("nextCommand"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-next-command-missing",
            evidence=f"{path_name} downloadProofAttachment has no rerun command",
            recommendation="Expose the LaunchKey rerun command with --download-release-assets and --github-release-repo placeholders.",
        )
    handoff = attachment.get("receiptHandoff") if isinstance(attachment.get("receiptHandoff"), dict) else {}
    if not handoff:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-receipt-handoff-missing",
            evidence=f"{path_name} downloadProofAttachment has no receiptHandoff",
            recommendation="Attach a receiptHandoff that points stable-publication at the candidate report, names download proof artifacts, and states that the download directory alone is not stable-v4 proof.",
        )
    else:
        handoff_boundary = handoff.get("proofBoundary") if isinstance(handoff.get("proofBoundary"), dict) else {}
        if (
            handoff.get("receipt") != "githubReleaseAssetDownloadProof"
            or not handoff.get("candidateReportPath")
            or not handoff.get("stablePublicationCommand")
            or handoff_boundary.get("attachCandidateReportToStablePublication") is not True
            or handoff_boundary.get("downloadDirectoryAloneCountsAsStableV4Proof") is not False
            or handoff_boundary.get("releaseConsumeStillRequiredForStableV4") is not True
            or handoff_boundary.get("sourceOnlyProofCounts") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="launchkey-download-proof-receipt-handoff-weak",
                evidence=f"{path_name} downloadProofAttachment receiptHandoff is incomplete",
                recommendation="Keep the download receipt handoff tied to the candidate report, stable-publication command, release-consume requirement, and source-only non-proof boundary.",
            )
    boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
    if (
        boundary.get("githubReleaseRepoRequired") is not True
        or boundary.get("releaseTagRequired") is not True
        or boundary.get("assetDownloadRequired") is not True
        or boundary.get("sha256RecordedForDownloadedAssets") is not True
        or boundary.get("releaseConsumeStillRequiredForStableV4") is not True
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-boundary-missing",
            evidence=f"{path_name} downloadProofAttachment weakens the native download proof boundary",
            recommendation="State that repo/tag/API access, asset download, SHA-256 rows, and later release-consume proof are required; source-only and fixture proof do not count for stable-v4 publication.",
        )
    if "Download Proof Attachment" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-attachment-markdown-missing",
            evidence=f"{path_name} Markdown does not render Download Proof Attachment",
            recommendation="Render Download Proof Attachment under GitHub Release Asset Download so maintainers can inspect the native download proof without opening JSON.",
        )
    if handoff and "Download Receipt Handoff" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-download-proof-receipt-handoff-markdown-missing",
            evidence=f"{path_name} Markdown does not render Download Receipt Handoff",
            recommendation="Render Download Receipt Handoff so stable-publication next steps are visible without opening JSON.",
        )
    return issues


def launchkey_external_adoption_gate_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("externalAdoptionEvidenceProof")
    if not isinstance(proof, dict) or not proof.get("provided"):
        return []
    issues: list[dict[str, str]] = []
    attachment = proof.get("adoptionGateAttachment")
    if not isinstance(attachment, dict) or not attachment:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-missing",
            evidence=f"{path_name} externalAdoptionEvidenceProof was supplied but has no adoptionGateAttachment",
            recommendation="Attach adoptionGateAttachment with record counts, accepted classes, required fields, diagnostics, next command, and proof boundary.",
        )
        return issues
    if attachment.get("stableV4GateStatus") != proof.get("stableV4GateStatus"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-status-drift",
            evidence=f"{path_name} adoptionGateAttachment.stableV4GateStatus does not mirror externalAdoptionEvidenceProof",
            recommendation="Keep adoptionGateAttachment stable-v4 gate status aligned with the adoption evidence proof.",
        )
    accepted_classes = set(str(value) for value in attachment.get("acceptedEvidenceClasses", [])) if isinstance(attachment.get("acceptedEvidenceClasses"), list) else set()
    if not {"public-external", "private-redacted-external"} <= accepted_classes:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-classes-missing",
            evidence=f"{path_name} adoptionGateAttachment does not list accepted stable-v4 adoption evidence classes",
            recommendation="List public-external and private-redacted-external so maintainers know what can pass stable-v4 adoption evidence.",
        )
    required_fields = set(str(value) for value in attachment.get("requiredFields", [])) if isinstance(attachment.get("requiredFields"), list) else set()
    if not {"actorRelationship", "privateDataRedacted", "commands", "artifacts", "nonClaims"} <= required_fields:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-required-fields-missing",
            evidence=f"{path_name} adoptionGateAttachment hides key required adoption fields",
            recommendation="Expose required fields including actorRelationship, privateDataRedacted, commands, artifacts, and nonClaims.",
        )
    if proof.get("status") == "blocked" and not attachment.get("firstInvalidRecord"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-diagnostics-missing",
            evidence=f"{path_name} blocked adoption proof has no firstInvalidRecord diagnostics",
            recommendation="Expose the first invalid adoption record path, missing fields, and errors.",
        )
    boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
    if (
        boundary.get("independentActorRequired") is not True
        or boundary.get("privateDataRedactedRequired") is not True
        or boundary.get("consentOrShareableSummaryRequired") is not True
        or boundary.get("fixtureSyntheticProofCounts") is not False
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("githubDownloadCountsAsAdoption") is not False
        or boundary.get("marketplaceAcceptanceClaimed") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-boundary-missing",
            evidence=f"{path_name} adoptionGateAttachment weakens the adoption evidence proof boundary",
            recommendation="State that independent actors, redaction, consent/shareable summary, and real external evidence are required, while fixture/source/download/marketplace proof does not count.",
        )
    if "Adoption Gate Attachment" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-external-adoption-gate-attachment-markdown-missing",
            evidence=f"{path_name} Markdown does not render Adoption Gate Attachment",
            recommendation="Render Adoption Gate Attachment under External Adoption Evidence so maintainers can inspect the gate without opening JSON.",
        )
    return issues


def launchkey_security_review_gate_attachment_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    if str(report.get("tool") or "") != "shipguard v4 release-candidate":
        return []
    proof = report.get("securityReviewEvidenceProof")
    if not isinstance(proof, dict) or not proof.get("provided"):
        return []
    issues: list[dict[str, str]] = []
    attachment = proof.get("securityReviewGateAttachment")
    if not isinstance(attachment, dict) or not attachment:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-missing",
            evidence=f"{path_name} securityReviewEvidenceProof was supplied but has no securityReviewGateAttachment",
            recommendation="Attach securityReviewGateAttachment with record counts, accepted classes, accepted reviewers, required scope, diagnostics, next command, and proof boundary.",
        )
        return issues
    if attachment.get("stableV4GateStatus") != proof.get("stableV4GateStatus"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-status-drift",
            evidence=f"{path_name} securityReviewGateAttachment.stableV4GateStatus does not mirror securityReviewEvidenceProof",
            recommendation="Keep securityReviewGateAttachment stable-v4 gate status aligned with the security evidence proof.",
        )
    accepted_classes = set(str(value) for value in attachment.get("acceptedEvidenceClasses", [])) if isinstance(attachment.get("acceptedEvidenceClasses"), list) else set()
    if not {"public-security-review", "private-redacted-security-review"} <= accepted_classes:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-classes-missing",
            evidence=f"{path_name} securityReviewGateAttachment does not list accepted stable-v4 security review classes",
            recommendation="List public-security-review and private-redacted-security-review so maintainers know what can pass stable-v4 final security evidence.",
        )
    accepted_reviewers = set(str(value) for value in attachment.get("acceptedReviewerRelationships", [])) if isinstance(attachment.get("acceptedReviewerRelationships"), list) else set()
    if not {"independent", "maintainer-security-review"} <= accepted_reviewers:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-reviewers-missing",
            evidence=f"{path_name} securityReviewGateAttachment does not list accepted reviewer relationships",
            recommendation="List independent and maintainer-security-review so maintainers know which reviewer relationships can pass final security evidence.",
        )
    required_scope = set(str(value) for value in attachment.get("requiredScope", [])) if isinstance(attachment.get("requiredScope"), list) else set()
    expected_scope = {"cli", "plugin", "github-actions", "release-proof", "package-install", "redaction-privacy"}
    if not expected_scope <= required_scope:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-scope-missing",
            evidence=f"{path_name} securityReviewGateAttachment hides required stable-v4 security scope",
            recommendation="Expose CLI, plugin, GitHub Actions, release-proof, package-install, and redaction/privacy scope requirements.",
        )
    required_fields = set(str(value) for value in attachment.get("requiredFields", [])) if isinstance(attachment.get("requiredFields"), list) else set()
    if not {"reviewerRelationship", "scope", "methodology", "findingsSummary", "nonClaims"} <= required_fields:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-required-fields-missing",
            evidence=f"{path_name} securityReviewGateAttachment hides key required security-review fields",
            recommendation="Expose required fields including reviewerRelationship, scope, methodology, findingsSummary, and nonClaims.",
        )
    if proof.get("status") == "blocked" and not attachment.get("firstInvalidRecord"):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-diagnostics-missing",
            evidence=f"{path_name} blocked security-review proof has no firstInvalidRecord diagnostics",
            recommendation="Expose the first invalid security review record path, missing fields, missing scope, and errors.",
        )
    boundary = attachment.get("proofBoundary") if isinstance(attachment.get("proofBoundary"), dict) else {}
    if (
        boundary.get("requiredScopeMustBeCovered") is not True
        or boundary.get("privateDataRedactedRequired") is not True
        or boundary.get("criticalHighOpenMustBeZero") is not True
        or boundary.get("methodologyRequired") is not True
        or boundary.get("consentOrShareableSummaryRequired") is not True
        or boundary.get("fixtureSyntheticProofCounts") is not False
        or boundary.get("sourceOnlyProofCounts") is not False
        or boundary.get("marketplaceAcceptanceClaimed") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-boundary-missing",
            evidence=f"{path_name} securityReviewGateAttachment weakens the final security-review proof boundary",
            recommendation="State that required scope, redaction, methodology, and zero open critical/high findings are required, while fixture/source/marketplace proof does not count.",
        )
    if "Security Review Gate Attachment" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="launchkey-security-review-gate-attachment-markdown-missing",
            evidence=f"{path_name} Markdown does not render Security Review Gate Attachment",
            recommendation="Render Security Review Gate Attachment under Security Review Evidence so maintainers can inspect the gate without opening JSON.",
        )
    return issues


def task_contract_quickstart_replay_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    tool = str(report.get("tool") or "")
    if tool not in {"shipguard prepare", "shipguard verify"}:
        return issues

    replay = report.get("quickstartReplay")
    if not isinstance(replay, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-quickstart-replay-missing",
            evidence=f"{path_name} has no quickstartReplay object",
            recommendation="Emit quickstartReplay so a fresh maintainer can reach or replay the first useful prepare/verify verdict without reading internal docs.",
        )
        return issues

    if "Quickstart Replay" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-quickstart-replay-markdown-missing",
            evidence=f"{path_name} has quickstartReplay JSON but Markdown does not expose it",
            recommendation="Render Quickstart Replay in Markdown beside the proof report so the first-user path is visible without opening JSON.",
        )

    if tool == "shipguard prepare":
        required_fields = ("phase", "taskArtifact", "firstUsefulVerdictCommand", "proofInputs", "successSignal", "connects", "boundary")
        missing = [field for field in required_fields if not replay.get(field)]
        command = str(replay.get("firstUsefulVerdictCommand") or "")
        connects = replay.get("connects") if isinstance(replay.get("connects"), list) else []
        expected_connections = {
            "goal",
            "riskClassification",
            "authorizedFiles",
            "protectedBoundaries",
            "validationContract",
            "agentClaims",
            "verdict",
            "nextAction",
        }
        if missing or "shipguard verify" not in command or not expected_connections <= {str(item) for item in connects}:
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-prepare-replay-incomplete",
                evidence=f"{path_name} prepare quickstartReplay is missing fields or does not connect the durable task object to the first verify command",
                recommendation="For prepare reports, include the verify command template, proof inputs, success signal, boundary, and the goal/risk/scope/proof/claim/verdict connections.",
            )

    if tool == "shipguard verify":
        required_fields = ("phase", "status", "replayCommand", "fastVerdict", "reviewPacket", "nextAction", "successSignal", "boundary")
        missing = [field for field in required_fields if not replay.get(field)]
        packet = replay.get("reviewPacket") if isinstance(replay.get("reviewPacket"), list) else []
        packet_text = " ".join(str(item) for item in packet)
        command = str(replay.get("replayCommand") or "")
        if missing or "shipguard verify" not in command or "shipguard-verdict.json" not in packet_text or "shipguard-verdict.md" not in packet_text:
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-verify-replay-incomplete",
                evidence=f"{path_name} verify quickstartReplay is missing replay command, fast verdict, review packet, or next action",
                recommendation="For verify reports, include the replay command, copy-ready proof report, review packet files, next action, and boundary.",
            )
    return issues


def task_contract_notification_scope_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard prepare":
        return issues

    questions = report.get("reportQualityQuestions") if isinstance(report.get("reportQualityQuestions"), list) else []
    question_text = normalized_question_text(" ".join(str(item) for item in questions))
    pack = report.get("domainRiskPack")
    pack_id = str((pack or {}).get("id") or "") if isinstance(pack, dict) else ""
    scope_required = pack_id == "ios-notification-permission-workflow" or is_notification_scope_question(question_text)
    if not scope_required:
        return issues

    if not isinstance(pack, dict) or pack_id != "ios-notification-permission-workflow":
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-scope-pack-missing",
            evidence=f"{path_name} asks for notification/permission scope specificity but has no ios-notification-permission-workflow domainRiskPack",
            recommendation="Emit domainRiskPack.id=ios-notification-permission-workflow with authorized, review-only, and forbidden scope recommendations.",
        )
        return issues

    scope = pack.get("scopeRecommendations") if isinstance(pack.get("scopeRecommendations"), dict) else {}
    authorized = scope.get("authorized") if isinstance(scope.get("authorized"), list) else []
    review_only = scope.get("reviewOnly") if isinstance(scope.get("reviewOnly"), list) else []
    forbidden = scope.get("forbiddenUnlessExplicit") if isinstance(scope.get("forbiddenUnlessExplicit"), list) else []

    def rows_have_pattern_reason(rows: list[Any]) -> bool:
        return bool(rows) and all(
            isinstance(item, dict) and item.get("pattern") and item.get("reason") for item in rows
        )

    if not rows_have_pattern_reason(authorized):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-authorized-scope-missing",
            evidence=f"{path_name} notification domainRiskPack has no authorized owner scope rows with reasons",
            recommendation="List source/test owner scope patterns with reasons so a maintainer knows what the permission task may touch.",
        )
    review_patterns = {str(item.get("pattern") or "") for item in review_only if isinstance(item, dict)}
    if not rows_have_pattern_reason(review_only) or not {
        "**/Info.plist",
        "**/*AppDelegate*.swift",
        "**/*SceneDelegate*.swift",
    } <= review_patterns:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-review-only-scope-incomplete",
            evidence=f"{path_name} notification domainRiskPack review-only rows are missing plist or lifecycle surfaces",
            recommendation="List Info.plist, AppDelegate, and SceneDelegate as review-only surfaces with reasons.",
        )
    forbidden_patterns = {str(item.get("pattern") or "") for item in forbidden if isinstance(item, dict)}
    if not rows_have_pattern_reason(forbidden) or not {"**/*.entitlements", "**/project.pbxproj"} <= forbidden_patterns:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-forbidden-scope-incomplete",
            evidence=f"{path_name} notification domainRiskPack forbidden rows are missing entitlement or project-file boundaries",
            recommendation="List entitlements and project.pbxproj as forbidden-unless-explicit surfaces with reasons.",
        )
    candidate_evidence = pack.get("candidateEvidence") if isinstance(pack.get("candidateEvidence"), dict) else {}
    sensitive_files = candidate_evidence.get("permissionSensitiveFiles") if isinstance(candidate_evidence.get("permissionSensitiveFiles"), list) else []
    if not sensitive_files:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-source-signals-missing",
            evidence=f"{path_name} notification domainRiskPack has no permission-sensitive source signal rows",
            recommendation="Expose the source/test files or redacted targets that triggered the notification permission workflow.",
        )
    markdown_needles = [
        "iOS Notification Permission Workflow",
        "Authorized candidate",
        "Review only",
        "Forbidden unless explicit",
        "`**/Info.plist`",
        "`**/*AppDelegate*.swift`",
        "`**/*SceneDelegate*.swift`",
        "`**/*.entitlements`",
        "`**/project.pbxproj`",
    ]
    missing_markdown = [needle for needle in markdown_needles if needle not in markdown]
    if missing_markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-scope-markdown-missing",
            evidence=f"{path_name} Markdown does not expose notification scope rows: {', '.join(missing_markdown[:4])}",
            recommendation="Render notification authorized owner scopes, review-only lifecycle/plist surfaces, and forbidden entitlement/project boundaries in Markdown.",
        )
    return issues


def task_contract_unsupported_claim_replay_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard verify":
        return issues
    claim_checks = report.get("claimChecks") if isinstance(report.get("claimChecks"), dict) else {}
    rejected_claims = claim_checks.get("rejectedClaims") if isinstance(claim_checks.get("rejectedClaims"), list) else []
    raw_rejected_claims = claim_checks.get("rawRejectedClaims") if isinstance(claim_checks.get("rawRejectedClaims"), list) else []
    decisions = claim_checks.get("claimDecisions") if isinstance(claim_checks.get("claimDecisions"), list) else []
    manual_proof_claims = [
        item
        for item in decisions
        if isinstance(item, dict) and item.get("status") == "needs-manual-proof"
    ]
    questions = report.get("reportQualityQuestions") if isinstance(report.get("reportQualityQuestions"), list) else []
    question_text = normalized_question_text(" ".join(str(item) for item in questions))
    replay_required = bool(
        rejected_claims
        or raw_rejected_claims
        or manual_proof_claims
        or "unsupported completion claim" in question_text
    )
    if not replay_required:
        return issues

    replay = report.get("unsupportedClaimReplay")
    if not isinstance(replay, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-missing",
            evidence=f"{path_name} rejects unsupported claims but has no unsupportedClaimReplay object",
            recommendation="Emit unsupportedClaimReplay with rejected claims, replay command, next action, proof boundary, and non-claims.",
        )
        return issues

    unsupported_rows = replay.get("unsupportedClaims") if isinstance(replay.get("unsupportedClaims"), list) else []
    rejected_rows = replay.get("rejectedClaims") if isinstance(replay.get("rejectedClaims"), list) else []
    manual_rows = replay.get("manualProofClaims") if isinstance(replay.get("manualProofClaims"), list) else []
    if not unsupported_rows and rejected_rows:
        unsupported_rows = rejected_rows
    expected_status = "blocked" if rejected_rows else "review"
    if replay.get("status") != expected_status:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-status-wrong",
            evidence=f"{path_name} unsupportedClaimReplay status is {replay.get('status')!r}",
            recommendation="Mark rejected-claim replays as blocked and manual-proof-only replays as review so claim status matches the proof gap.",
        )
    if not unsupported_rows or int(replay.get("unsupportedClaimCount") or 0) < 1:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-claims-missing",
            evidence=f"{path_name} unsupportedClaimReplay does not list unsupported claims",
            recommendation="List every unsupported completion claim with status, proof phrase, reason, and resolution.",
        )
    if rejected_rows and int(replay.get("rejectedClaimCount") or 0) < 1:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-rejected-count-missing",
            evidence=f"{path_name} unsupportedClaimReplay lists rejected rows but has no rejected count",
            recommendation="Expose rejectedClaimCount separately from manualProofClaimCount.",
        )
    if manual_proof_claims and not manual_rows:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-manual-claims-missing",
            evidence=f"{path_name} has needs-manual-proof claim decisions but unsupportedClaimReplay has no manualProofClaims",
            recommendation="Expose manualProofClaims separately so manual/device proof gaps are not mislabeled as rejected claims.",
        )
    unsupported_phrases = replay.get("unsupportedPhrases") if isinstance(replay.get("unsupportedPhrases"), list) else []
    if not unsupported_phrases:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-phrases-missing",
            evidence=f"{path_name} unsupportedClaimReplay does not list unsupported proof phrases",
            recommendation="Expose the proof phrases that made the claim unsupported so the developer can narrow the wording.",
        )
    command = str(replay.get("replayCommand") or "")
    if "shipguard verify" not in command or "--claim" not in command:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-command-missing",
            evidence=f"{path_name} unsupportedClaimReplay has no replayable verify command with the claim",
            recommendation="Keep the replay command copy-ready, including task, diff, evidence, and claim arguments.",
        )
    next_action = replay.get("nextAction") if isinstance(replay.get("nextAction"), dict) else {}
    resolves = {str(item) for item in next_action.get("resolves", [])} if isinstance(next_action.get("resolves"), list) else set()
    if (
        "unsupported-completion-claim" not in resolves
        or "Revise the completion claim" not in str(next_action.get("command") or "")
        or not next_action.get("expectedArtifact")
        or not next_action.get("successCondition")
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-next-action-missing",
            evidence=f"{path_name} unsupportedClaimReplay does not give the exact repair action",
            recommendation="Point to revising the claim or attaching structured evidence, with expected artifact and success condition.",
        )
    boundary = normalized_question_text(replay.get("proofBoundary") or "")
    if "does not prove" not in boundary or ("structured proof" not in boundary and "manual/device proof" not in boundary):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-boundary-missing",
            evidence=f"{path_name} unsupportedClaimReplay proof boundary does not block overclaim reuse",
            recommendation="State that replay proves non-acceptance only, not the claimed product behavior.",
        )
    non_claims = " ".join(str(item) for item in replay.get("nonClaims") or [])
    if "not product proof" not in non_claims.lower() or "not a merge" not in non_claims.lower():
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-nonclaims-missing",
            evidence=f"{path_name} unsupportedClaimReplay non-claims are incomplete",
            recommendation="Keep non-claims explicit: replay is not product proof, not merge approval, and not release approval.",
        )
    normalized_markdown = markdown.lower()
    if (
        "Unsupported Claim Replay" not in markdown
        or "Revise the claim" not in markdown
        or "not product proof" not in normalized_markdown
        or "not a merge" not in normalized_markdown
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-unsupported-claim-replay-markdown-missing",
            evidence=f"{path_name} Markdown does not render the unsupported-claim replay repair path",
            recommendation="Render Unsupported Claim Replay in Markdown with the unsupported claim, replay command, next action, proof boundary, and non-claims.",
        )
    return issues


def task_contract_notification_proof_lane_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    tool = str(report.get("tool") or "")
    if tool not in {"shipguard prepare", "shipguard verify"}:
        return issues

    def json_text(value: object) -> str:
        try:
            return normalized_question_text(json.dumps(value, sort_keys=True))
        except TypeError:
            return normalized_question_text(value)

    def physical_device_prompt_receipt_present() -> bool:
        evidence_sources: list[object] = []
        for field in ("evidenceReceipts", "evidence"):
            value = report.get(field)
            if isinstance(value, list):
                evidence_sources.extend(value)
        analysis = report.get("diffFirstAnalysis") if isinstance(report.get("diffFirstAnalysis"), dict) else {}
        value = analysis.get("evidenceReceipts")
        if isinstance(value, list):
            evidence_sources.extend(value)
        schema = report.get("evidenceReceiptSchema") if isinstance(report.get("evidenceReceiptSchema"), dict) else {}
        for field in ("normalizedReceipts", "receipts", "presentReceipts"):
            value = schema.get(field)
            if isinstance(value, list):
                evidence_sources.extend(value)
        evidence_text = json_text(evidence_sources)
        return any(
            token in evidence_text
            for token in (
                "physical-device-prompt",
                "device-permission-prompt",
                "ios-permission-prompt-physical-device",
            )
        ) or (
            ("physical-device" in evidence_text or "real-device" in evidence_text)
            and ("prompt" in evidence_text or "permission" in evidence_text)
        )

    report_questions = report.get("reportQualityQuestions") if isinstance(report.get("reportQualityQuestions"), list) else []
    workflow = report.get("notificationPermissionWorkflow")
    if not isinstance(workflow, dict):
        workflows = report.get("domainWorkflows") if isinstance(report.get("domainWorkflows"), dict) else {}
        workflow = workflows.get("notificationPermissionWorkflow") if isinstance(workflows.get("notificationPermissionWorkflow"), dict) else {}
    pack = report.get("domainRiskPack") if isinstance(report.get("domainRiskPack"), dict) else {}
    if not pack and isinstance(workflow, dict):
        pack = workflow.get("riskPack") if isinstance(workflow.get("riskPack"), dict) else {}
    pack_questions = pack.get("reportQualityQuestions") if isinstance(pack.get("reportQualityQuestions"), list) else []
    workflow_questions = workflow.get("reportQualityQuestions") if isinstance(workflow, dict) and isinstance(workflow.get("reportQualityQuestions"), list) else []
    question_text = normalized_question_text(" ".join(str(item) for item in [*report_questions, *pack_questions, *workflow_questions]))
    simulator_device_boundary_question = is_notification_simulator_device_boundary_question(question_text)
    workflow_active = (
        isinstance(pack, dict)
        and pack.get("id") == "ios-notification-permission-workflow"
        and is_notification_proof_lane_question(question_text)
    ) or (
        isinstance(workflow, dict)
        and workflow.get("id") == "ios-notification-permission-workflow"
        and (is_notification_proof_lane_question(question_text) or bool(workflow.get("proofLanes")))
    )
    if not workflow_active:
        return issues

    if tool == "shipguard prepare":
        if not isinstance(pack, dict) or pack.get("id") != "ios-notification-permission-workflow":
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-pack-missing",
                evidence=f"{path_name} asks for permission-state proof-lane specificity but has no notification domainRiskPack",
                recommendation="Emit ios-notification-permission-workflow validationReceiptRequirements before prepare asks verify proof-lane questions.",
            )
            return issues
        requirements = pack.get("validationReceiptRequirements") if isinstance(pack.get("validationReceiptRequirements"), list) else []
        requirements_text = json_text(requirements)
        if (
            not requirements
            or "permission-state" not in requirements_text
            or "denied-state" not in requirements_text
            or ("structured" not in requirements_text and "scope label" not in requirements_text)
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-requirements-missing",
                evidence=f"{path_name} notification domainRiskPack does not require structured permission-state and denied-state receipt scopes",
                recommendation="List validationReceiptRequirements that require permission-state, denied-state, and not-determined-state scope labels.",
            )
        boundary_text = json_text(pack.get("proofBoundaries"))
        next_action_text = json_text(pack.get("nextAction"))
        if (
            "generic" not in f"{requirements_text} {boundary_text} {next_action_text}"
            or ("not a permission workflow proof" not in requirements_text and "rather than a permission workflow" not in next_action_text)
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-generic-boundary-missing",
                evidence=f"{path_name} notification domainRiskPack does not explain why a generic test log is insufficient",
                recommendation="State that generic validation is not permission workflow proof and point to structured receipt scopes.",
            )
        if (
            "structured" not in next_action_text
            or "permission-state" not in next_action_text
            or "denied-state" not in next_action_text
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-next-action-missing",
                evidence=f"{path_name} nextAction does not ask for structured permission-state and denied-state receipt proof",
                recommendation="Make the next action name the structured receipt artifact and required permission-state/denied-state labels.",
            )
        if simulator_device_boundary_question:
            boundary_bundle = f"{requirements_text} {boundary_text} {next_action_text}"
            if (
                "simulator" not in boundary_bundle
                or "physical-device" not in boundary_bundle
                or "physical-device prompt" not in boundary_bundle
                or ("manual" not in boundary_bundle and "release" not in boundary_bundle)
                or "simulator-permission-reset" not in boundary_bundle
                or (
                    "physical-device-prompt-boundary" not in requirements_text
                    and "ios-permission-prompt-physical-device" not in requirements_text
                )
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="task-contract-notification-simulator-device-boundary-missing",
                    evidence=f"{path_name} notification domainRiskPack does not separate simulator reset proof from physical-device prompt proof",
                    recommendation="Expose simulator denied-state/reset proof separately from physical-device prompt proof, and state that release claims still need manual/device evidence.",
                )
        markdown_text = normalized_question_text(markdown)
        if (
            "ios notification permission workflow" not in markdown_text
            or "receipt requirements" not in markdown_text
            or "permission-state" not in markdown_text
            or "denied-state" not in markdown_text
            or "generic test claim" not in markdown_text
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-markdown-missing",
                evidence=f"{path_name} Markdown does not render the generic-log proof-lane boundary",
                recommendation="Render receipt requirements and failure meanings so a maintainer sees that generic logs are not enough.",
            )
        if simulator_device_boundary_question and (
            "simulator-denied-state-recovery" not in markdown_text
            or "simulator-permission-reset" not in markdown_text
            or "physical-device-prompt-boundary" not in markdown_text
            or "physical-device prompt" not in markdown_text
            or "release claims" not in markdown_text
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-simulator-device-markdown-missing",
                evidence=f"{path_name} Markdown hides the simulator reset versus physical-device prompt boundary",
                recommendation="Render simulator denied-state/reset and physical-device prompt receipt requirements in Markdown, including the release-claim boundary.",
            )
        return issues

    proof_lanes = workflow.get("proofLanes") if isinstance(workflow.get("proofLanes"), list) else []
    lane_text = json_text(proof_lanes)
    permission_lane = next(
        (
            item
            for item in proof_lanes
            if isinstance(item, dict)
            and item.get("id") == "permission-state-validation"
            and "permission-state" in json_text(item.get("requiredReceiptScope"))
            and "denied-state" in json_text(item.get("requiredReceiptScope"))
        ),
        None,
    )
    denied_lane = next(
        (
            item
            for item in proof_lanes
            if isinstance(item, dict)
            and "denied-state" in str(item.get("id") or "")
            and "denied-state" in json_text(item.get("requiredReceiptScope"))
        ),
        None,
    )
    simulator_lane = next(
        (
            item
            for item in proof_lanes
            if isinstance(item, dict)
            and item.get("id") == "simulator-permission-reset"
            and (
                "simulator" in json_text(item.get("proofBoundary"))
                or "simulator-permission-reset" in json_text(item.get("requiredReceiptScope"))
            )
        ),
        None,
    )
    physical_prompt_lane = next(
        (
            item
            for item in proof_lanes
            if isinstance(item, dict)
            and item.get("id") == "physical-device-prompt"
            and "physical-device" in json_text(item)
        ),
        None,
    )
    if not permission_lane or not denied_lane:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-proof-lanes-missing",
            evidence=f"{path_name} verify report does not expose permission-state and denied-state proof lanes",
            recommendation="Emit notificationPermissionWorkflow.proofLanes for permission-state-validation and denied-state-recovery.",
        )
    boundary_active = simulator_device_boundary_question or "physical-device-prompt" in lane_text or "simulator-permission-reset" in lane_text
    if boundary_active and (not simulator_lane or not physical_prompt_lane):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-simulator-device-proof-lanes-missing",
            evidence=f"{path_name} verify report does not expose separate simulator reset and physical-device prompt proof lanes",
            recommendation="Emit simulator-permission-reset and physical-device-prompt proof lanes so local simulator proof cannot be confused with release/device proof.",
        )
    if (
        physical_prompt_lane
        and str(physical_prompt_lane.get("status") or "").lower() in {"pass", "passed", "covered", "proven"}
        and not physical_device_prompt_receipt_present()
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-physical-device-prompt-overclaimed",
            evidence=f"{path_name} marks physical-device prompt proof as locally proven",
            recommendation="Keep physical-device-prompt at manual-required until a real device/manual prompt receipt is attached.",
        )
    schema = report.get("evidenceReceiptSchema") if isinstance(report.get("evidenceReceiptSchema"), dict) else {}
    next_action_text = json_text(workflow.get("nextAction") if isinstance(workflow, dict) else report.get("nextAction"))
    generic_artifact_only = int(schema.get("artifactOnlyCount") or 0) > 0 and int(schema.get("structuredValidationCount") or 0) == 0
    if generic_artifact_only:
        if str(report.get("status") or "") == "pass":
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-generic-log-accepted",
                evidence=f"{path_name} accepted artifact-only evidence as a pass for notification permission proof",
                recommendation="Keep generic logs at review until structured permission-state and denied-state receipt scopes are attached.",
            )
        if (
            "structured" not in next_action_text
            or "permission-state" not in next_action_text
            or "denied-state" not in next_action_text
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-proof-lanes-generic-next-action-missing",
                evidence=f"{path_name} generic-log review does not point to structured permission-state and denied-state receipts",
                recommendation="For artifact-only evidence, nextAction should request structured scope labels instead of another generic log.",
            )
    local_lanes_proven = bool(
        permission_lane
        and denied_lane
        and simulator_lane
        and str(permission_lane.get("status") or "").lower() == "proven"
        and str(denied_lane.get("status") or "").lower() == "proven"
        and str(simulator_lane.get("status") or "").lower() == "proven"
    )
    physical_prompt_receipt_present = physical_device_prompt_receipt_present()
    if boundary_active and physical_prompt_lane and local_lanes_proven and not physical_prompt_receipt_present:
        if (
            "physical-device" not in next_action_text
            or "prompt" not in next_action_text
            or ("release" not in next_action_text and "manual" not in next_action_text)
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="task-contract-notification-simulator-device-next-action-missing",
                evidence=f"{path_name} local simulator proof is complete but nextAction does not name the remaining physical-device prompt proof",
                recommendation="After local permission/simulator lanes are proven, make nextAction point to the physical-device prompt receipt before release claims.",
            )
    if "generic" not in lane_text or "not proven" not in lane_text:
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-proof-lanes-failure-meaning-missing",
            evidence=f"{path_name} proof lanes do not explain that generic receipts leave permission-state proof missing",
            recommendation="Add failureMeaning text that says permission-state coverage is not proven by a generic receipt.",
        )
    markdown_text = normalized_question_text(markdown)
    if (
        "ios notification permission workflow" not in markdown_text
        or "proof lanes" not in markdown_text
        or "permission-state-validation" not in markdown_text
        or "denied-state-recovery" not in markdown_text
        or "required receipt scope" not in markdown_text
        or "generic receipt" not in markdown_text
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-proof-lanes-verify-markdown-missing",
            evidence=f"{path_name} Markdown does not expose permission-state/denied-state proof-lane status and generic receipt boundary",
            recommendation="Render proof lanes, required receipt scopes, and generic-receipt failure meanings in the verify Markdown report.",
        )
    physical_prompt_needs_manual = not (
        physical_prompt_lane
        and str(physical_prompt_lane.get("status") or "").lower() in {"pass", "passed", "covered", "proven"}
        and physical_prompt_receipt_present
    )
    if boundary_active and (
        "simulator-permission-reset" not in markdown_text
        or "physical-device-prompt" not in markdown_text
        or (physical_prompt_needs_manual and "manual-required" not in markdown_text)
        or (physical_prompt_needs_manual and "release claims" not in markdown_text)
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="task-contract-notification-simulator-device-verify-markdown-missing",
            evidence=f"{path_name} Markdown does not expose simulator reset proof separately from physical-device prompt proof",
            recommendation="Render simulator-permission-reset and physical-device-prompt lanes with manual-required status and release-claim failure meaning.",
        )
    return issues


def full_audit_slash_handoff_issues(report: dict[str, Any], *, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard full-audit":
        return issues
    slash_plan = str(report.get("slashPlan") or "").strip()
    slash_goal = str(report.get("slashGoal") or "").strip()
    combined = normalized_question_text(f"{slash_plan} {slash_goal}")
    if not slash_plan.startswith("/plan ") or not slash_goal.startswith("/goal "):
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-slash-handoff-incomplete",
            evidence=f"{path_name} slashPlan or slashGoal is missing a copy-ready slash command",
            recommendation="Regenerate Full Audit so it emits copy-ready /plan and /goal handoff text.",
        )
    source = report.get("slashHandoffSource")
    if not isinstance(source, dict) or source.get("status") != "loaded" or source.get("sourcePath") != "NEXT_GOAL.md":
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-slash-handoff-source-missing",
            evidence=f"{path_name} does not prove slashPlan and slashGoal came from NEXT_GOAL.md",
            recommendation="Load the slash handoff from NEXT_GOAL.md and include slashHandoffSource.status=loaded.",
        )
    else:
        proof = report.get("slashHandoffProof")
        if not isinstance(proof, dict) or not proof:
            add_issue(
                issues,
                severity="review",
                rule_id="full-audit-slash-handoff-proof-missing",
                evidence=f"{path_name} claims a loaded NEXT_GOAL.md slash handoff but has no slashHandoffProof",
                recommendation="Attach slashHandoffProof with selected section, copy-ready plan/goal checks, completion receipt presence, version lineage status, and non-publication boundaries.",
            )
        else:
            boundary = proof.get("proofBoundary") if isinstance(proof.get("proofBoundary"), dict) else {}
            if (
                proof.get("sourcePath") != "NEXT_GOAL.md"
                or proof.get("copyReadyPlan") is not True
                or proof.get("copyReadyGoal") is not True
                or proof.get("staleHardcodedV3132Absent") is not True
                or proof.get("handoffFreshness") not in {"active-handoff", "fresh-following-handoff", "following-without-completion-receipt"}
                or "shipguard next-goal" not in str(proof.get("regenerateCommand") or "")
                or boundary.get("nextGoalFileRequired") is not True
                or boundary.get("fallbackIsReviewOnly") is not True
                or boundary.get("doesNotMarkGoalComplete") is not True
                or boundary.get("doesNotPublishRelease") is not True
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="full-audit-slash-handoff-proof-weak",
                    evidence=f"{path_name} slashHandoffProof does not prove copy-ready NEXT_GOAL.md handoff boundaries",
                    recommendation="Keep slashHandoffProof aligned to NEXT_GOAL.md, copy-ready /plan and /goal text, stale-handoff rejection, and no goal-complete/publication claims.",
                )
    if "v3.132.0 v4 product release stabilization" in combined:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-slash-handoff-stale",
            evidence=f"{path_name} still contains the old v3.132 Full Audit slash handoff",
            recommendation="Replace hardcoded Full Audit slash handoff text with the current NEXT_GOAL.md handoff.",
        )
    return issues


def full_audit_execution_command_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard full-audit":
        return issues
    stages = report.get("stages")
    if not isinstance(stages, list) or not stages:
        return issues
    command_stages = [
        stage
        for stage in stages
        if isinstance(stage, dict) and isinstance(stage.get("command"), list) and stage.get("command")
    ]
    if not command_stages:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-stage-commands-missing-json",
            evidence=f"{path_name} Full Audit stages do not carry structured command arrays",
            recommendation="Include stages[].command so Full Audit reports can render and audit copy-ready execution receipts.",
        )
        return issues
    receipt = report.get("executionCommandReceipt")
    if not isinstance(receipt, dict) or not receipt:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-execution-command-receipt-missing",
            evidence=f"{path_name} Full Audit stages expose commands but no executionCommandReceipt",
            recommendation="Attach executionCommandReceipt with execute/resume commands, stage command rows, empty/manual stage ids, fallback commands, and no-push/no-publish boundaries.",
        )
    else:
        boundary = receipt.get("proofBoundary") if isinstance(receipt.get("proofBoundary"), dict) else {}
        stage_rows = receipt.get("stageCommands")
        empty_ids = receipt.get("emptyStageCommandIds")
        missing_receipt_parts = []
        if "shipguard full-audit" not in str(receipt.get("executeCommand") or ""):
            missing_receipt_parts.append("executeCommand")
        if "shipguard full-audit" not in str(receipt.get("resumeCommand") or ""):
            missing_receipt_parts.append("resumeCommand")
        if not isinstance(stage_rows, list) or len(stage_rows) != len(stages):
            missing_receipt_parts.append("stageCommands")
        if not isinstance(empty_ids, list):
            missing_receipt_parts.append("emptyStageCommandIds")
        if not isinstance(receipt.get("fallbackStageCount"), int):
            missing_receipt_parts.append("fallbackStageCount")
        if not isinstance(receipt.get("manualStageCount"), int):
            missing_receipt_parts.append("manualStageCount")
        for key in ("doesNotExecuteByRendering", "commandsAreLocalRepoScoped", "doesNotPush", "doesNotPublishRelease"):
            if boundary.get(key) is not True:
                missing_receipt_parts.append(f"proofBoundary.{key}")
        if missing_receipt_parts:
            add_issue(
                issues,
                severity="review",
                rule_id="full-audit-execution-command-receipt-incomplete",
                evidence=f"{path_name} executionCommandReceipt missing: {', '.join(missing_receipt_parts)}",
                recommendation="Keep Full Audit execution command receipts copy-ready, stage-aligned, and explicit that rendering commands does not execute, push, or publish.",
            )
        elif isinstance(stage_rows, list):
            row_by_id = {str(row.get("stageId") or ""): row for row in stage_rows if isinstance(row, dict)}
            malformed_rows = []
            for stage in stages:
                stage_id = str(stage.get("stageId") or "")
                row = row_by_id.get(stage_id)
                command = stage.get("command") if isinstance(stage.get("command"), list) else []
                if not isinstance(row, dict):
                    malformed_rows.append(f"{stage_id}: missing row")
                    continue
                if command and (row.get("copyReady") is not True or not str(row.get("commandText") or "").strip()):
                    malformed_rows.append(f"{stage_id}: command not copy-ready")
                if not command and (
                    row.get("copyReady") is not False
                    or not str(row.get("fallbackCommand") or "").strip()
                    or not str(row.get("emptyReason") or "").strip()
                ):
                    malformed_rows.append(f"{stage_id}: empty command lacks fallback")
            if malformed_rows:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="full-audit-execution-command-receipt-rows-incomplete",
                    evidence=f"{path_name} executionCommandReceipt rows incomplete: {', '.join(malformed_rows[:5])}",
                    recommendation="For every stage, mark runnable commands copy-ready and give empty/manual stages a fallback full-audit command plus reason.",
                )
    def command_signature(text: str) -> str:
        return re.sub(r"[`'\"\\]+", "", " ".join(text.split()))

    compact_markdown = command_signature(markdown)
    if "Execution Commands" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-execution-commands-markdown-missing",
            evidence=f"{path_name} Full Audit Markdown does not expose a copy-ready Execution Commands section",
            recommendation="Render an Execution Commands table from stages[].command so a maintainer can run or audit the planned lane from the Markdown report.",
        )
        return issues
    missing_stage_ids: list[str] = []
    for stage in command_stages:
        command_text = command_signature(" ".join(str(part) for part in stage["command"]))
        if command_text and command_text not in compact_markdown:
            missing_stage_ids.append(str(stage.get("stageId") or "unknown"))
    if missing_stage_ids:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-execution-command-missing",
            evidence=f"{path_name} Full Audit Markdown omits stage commands for {', '.join(missing_stage_ids[:5])}",
            recommendation="Render every stages[].command value in the Execution Commands table so package/release receipts are copy-ready.",
        )
    required_receipt_markdown = [
        "Execution Command Receipt",
        "Execute command:",
        "Resume command:",
        "Copy-ready stage commands:",
        "Fallback stage commands:",
        "Manual-required stage commands:",
        "Empty/manual stage commands:",
    ]
    missing_receipt_markdown = [token for token in required_receipt_markdown if token not in markdown]
    if missing_receipt_markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-execution-command-receipt-markdown-missing",
            evidence=f"{path_name} Full Audit Markdown missing execution receipt tokens: {', '.join(missing_receipt_markdown)}",
            recommendation="Render executionCommandReceipt in Markdown so the top execute/resume command and empty-stage fallback are visible without opening JSON.",
        )
    return issues


def full_audit_release_packet_plan_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(report.get("tool") or "") != "shipguard full-audit":
        return issues
    stages = report.get("stages")
    stage_ids = {str(stage.get("stageId") or "") for stage in stages if isinstance(stage, dict)} if isinstance(stages, list) else set()
    release_stage_ids = {"package-release", "plugin-status", "install-refresh", "ci-proof", "release-proof"}
    if not (stage_ids & release_stage_ids):
        return issues
    packet = report.get("releasePacketPlan")
    if not isinstance(packet, dict) or not packet:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-plan-missing",
            evidence=f"{path_name} selects release-packet stages but has no releasePacketPlan",
            recommendation="Add releasePacketPlan with selected stages, required metadata, missing metadata, next command, non-claims, and proof boundaries.",
        )
        return issues
    boundary = packet.get("proofBoundary") if isinstance(packet.get("proofBoundary"), dict) else {}
    if (
        boundary.get("planOnlyCountsAsReleaseProof") is not False
        or boundary.get("sourceOnlyCountsAsStableV4Proof") is not False
        or boundary.get("publishesGitHubRelease") is not False
        or boundary.get("pushesMain") is not False
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-boundary-weak",
            evidence=f"{path_name} releasePacketPlan weakens release/stable-v4 proof boundaries",
            recommendation="State that plan-only/source-only proof does not count, and Full Audit does not push or publish releases.",
        )
    required_metadata = packet.get("requiredMetadata")
    if not isinstance(required_metadata, list) or not {"release_url", "version", "tag", "commit", "ci_run_url"} <= {
        str(item.get("field") or "") for item in required_metadata if isinstance(item, dict)
    }:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-metadata-missing",
            evidence=f"{path_name} releasePacketPlan does not expose all release-proof metadata fields",
            recommendation="List release URL, version, tag, commit, and CI run URL so release-proof placeholders are inspectable in JSON.",
        )
    if not isinstance(packet.get("stagePlan"), list) or not packet.get("stagePlan"):
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-stage-plan-missing",
            evidence=f"{path_name} releasePacketPlan does not summarize selected release-packet stage statuses",
            recommendation="Include stagePlan rows for selected release-packet stages with status and proof boundary.",
        )
    raw_non_claims = packet.get("nonClaims")
    non_claims = " ".join(str(item) for item in raw_non_claims) if isinstance(raw_non_claims, list) else ""
    if "does not publish" not in non_claims or "Plan-only" not in non_claims:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-nonclaims-missing",
            evidence=f"{path_name} releasePacketPlan hides key release-packet non-claims",
            recommendation="Expose that Full Audit does not publish a release and plan-only output is route proof only.",
        )
    if "Release Packet Plan" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="full-audit-release-packet-markdown-missing",
            evidence=f"{path_name} Markdown does not render Release Packet Plan",
            recommendation="Render a Release Packet Plan section so maintainers can see missing metadata and non-claims without opening JSON.",
        )
    return issues


def source_report_findings(
    report: dict[str, Any],
    *,
    path_name: str,
    report_path: str,
    tool: str,
    shareable: bool,
) -> list[dict[str, str]]:
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return []

    private_terms = ios_shareable.collect_private_terms(report)
    rows: list[dict[str, str]] = []
    for index, item in enumerate(findings[:40], start=1):
        if not isinstance(item, dict):
            continue
        rule_id = str(item.get("ruleId") or "").strip()
        if not rule_id:
            rule_id = f"source-finding-{index}"

        def text_value(key: str) -> str:
            value = str(item.get(key) or "").strip()
            return ios_shareable.redact_text(value, private_terms=private_terms) if shareable else value

        rows.append(
            {
                "severity": text_value("severity") or "review",
                "category": text_value("category") or "source-report",
                "ruleId": sanitize_materialized_text(rule_id) if shareable else rule_id,
                "tool": tool or "unknown",
                "report": report_path,
                "sourceStatus": str(report.get("status") or "unknown"),
                "evidence": text_value("evidence"),
                "recommendation": text_value("recommendation"),
                "proofGuidance": text_value("proofGuidance") or text_value("proof"),
                "visibility": (
                    f"{path_name} source finding #{index} is carried through report-quality separately from report-quality issues."
                ),
            }
        )
    return rows


def performance_finding_explanation_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return issues
    for index, item in enumerate(findings[:20], start=1):
        if not isinstance(item, dict):
            continue
        if not (item.get("impact") or item.get("whyItMatters")):
            add_issue(
                issues,
                severity="review",
                rule_id="performance-finding-impact-missing",
                evidence=f"{path_name} finding #{index} has no impact or whyItMatters field",
                recommendation="Explain why each performance finding matters so solo developers can prioritize without private app context.",
            )
    if issues:
        return issues
    impact_markdown_visible = bool(
        "Why it matters" in markdown
        or re.search(r"(?im)^\s*#{1,6}\s+Impact\b", markdown)
        or re.search(r"(?im)\|\s*Impact\s*\|", markdown)
    )
    if not impact_markdown_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-markdown-impact-missing",
            evidence=f"{path_name} has performance findings but Markdown does not surface why they matter",
            recommendation="Show the finding impact in Markdown, not only JSON, so Codex and review readers see the prioritization reason.",
        )
    return issues


def performance_grouping_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return issues
    rule_counts: dict[str, int] = {}
    for item in findings:
        if not isinstance(item, dict):
            continue
        rule_id = str(item.get("ruleId") or "")
        if not rule_id:
            continue
        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
    grouped = report.get("groupedActionPlan")
    if isinstance(grouped, list) and grouped:
        missing_first_experiment = [
            str(item.get("ruleId") or "<unknown>")
            for item in grouped
            if isinstance(item, dict) and not item.get("firstExperiment")
        ]
        missing_validation_route = [
            str(item.get("ruleId") or "<unknown>")
            for item in grouped
            if isinstance(item, dict) and not item.get("validationRoute")
        ]
        missing_stop_condition = [
            str(item.get("ruleId") or "<unknown>")
            for item in grouped
            if isinstance(item, dict) and not item.get("stopCondition")
        ]
        if missing_first_experiment:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-grouped-first-experiment-missing",
                evidence=f"{path_name} groupedActionPlan missing firstExperiment for: {', '.join(missing_first_experiment[:5])}",
                recommendation="Add a tiny reversible firstExperiment to each grouped performance action before broader refactor advice.",
            )
        if missing_validation_route:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-grouped-validation-route-missing",
                evidence=f"{path_name} groupedActionPlan missing validationRoute for: {', '.join(missing_validation_route[:5])}",
                recommendation="Add a concrete validationRoute to each grouped performance action so the first experiment has an exact proof path.",
            )
        if missing_stop_condition:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-grouped-stop-condition-missing",
                evidence=f"{path_name} groupedActionPlan missing stopCondition for: {', '.join(missing_stop_condition[:5])}",
                recommendation="Add an explicit stopCondition to each grouped performance action so broad refactors stay blocked until the first experiment has signal.",
            )
        if "First experiment" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-markdown-first-experiment-missing",
                evidence=f"{path_name} groupedActionPlan includes next actions but Markdown does not show a First experiment column",
                recommendation="Show the smallest first experiment in Markdown so reviewers can start with a narrow proof step.",
            )
        if "Validation route" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-markdown-validation-route-missing",
                evidence=f"{path_name} groupedActionPlan includes validation routes but Markdown does not show a Validation route column",
                recommendation="Show grouped validation routes in Markdown so Codex and reviewers know which proof path to run.",
            )
        if "Stop condition" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-markdown-stop-condition-missing",
                evidence=f"{path_name} groupedActionPlan includes stop conditions but Markdown does not show a Stop condition column",
                recommendation="Show grouped stop conditions in Markdown so broad refactors remain gated by first-experiment evidence.",
            )
    repeated_rules = sorted(rule_id for rule_id, count in rule_counts.items() if count > 3)
    if not repeated_rules:
        return issues

    if not isinstance(grouped, list) or not grouped:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-grouped-action-plan-missing",
            evidence=f"{path_name} has repeated performance rules without groupedActionPlan",
            recommendation="Emit groupedActionPlan so repeated findings become rule-level next actions instead of duplicate rows.",
        )
        return issues

    grouped_ids = {
        str(item.get("ruleId") or "")
        for item in grouped
        if isinstance(item, dict)
    }
    missing_groups = [rule_id for rule_id in repeated_rules if rule_id not in grouped_ids]
    if missing_groups:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-grouped-action-plan-incomplete",
            evidence=f"{path_name} groupedActionPlan missing repeated rules: {', '.join(missing_groups[:5])}",
            recommendation="Include every repeated performance rule in groupedActionPlan with count, first locations, recommendation, and proof guidance.",
        )
    if "Grouped Next Actions" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-markdown-grouping-missing",
            evidence=f"{path_name} has repeated performance rules but Markdown does not show Grouped Next Actions",
            recommendation="Surface grouped next actions in Markdown so reviewers can start from rule groups before reading duplicate findings.",
        )
    return issues


def performance_high_severity_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return issues
    high_findings = [
        (index, item)
        for index, item in enumerate(findings[:20], start=1)
        if isinstance(item, dict) and str(item.get("severity") or "").lower() == "high"
    ]
    if not high_findings:
        return issues
    for index, item in high_findings:
        if not item.get("severityReason"):
            add_issue(
                issues,
                severity="review",
                rule_id="performance-high-severity-reason-missing",
                evidence=f"{path_name} high finding #{index} has no severityReason",
                recommendation="Explain why a performance finding is high severity using an explicit threshold, context, or source signal.",
            )
    if issues:
        return issues
    severity_markdown_visible = bool(
        "Why severity" in markdown
        or "Severity reason" in markdown
        or "Severity evidence" in markdown
    )
    if not severity_markdown_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-markdown-severity-reason-missing",
            evidence=f"{path_name} has high performance findings but Markdown does not surface why severity is high",
            recommendation="Show high-severity justification in Markdown so reviewers can distinguish concrete thresholds from broad suspicion.",
        )
    return issues


def performance_proof_boundary_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    if not isinstance(findings, list) or not findings:
        return issues
    for index, item in enumerate(findings[:20], start=1):
        if not isinstance(item, dict):
            continue
        missing = [field for field in ("localProof", "manualProof") if not item.get(field)]
        if missing:
            add_issue(
                issues,
                severity="review",
                rule_id="performance-proof-boundary-missing",
                evidence=f"{path_name} finding #{index} missing {', '.join(missing)}",
                recommendation="Split performance proof guidance into what Codex can verify locally and what still needs device, account, or manual proof.",
            )
    if issues:
        return issues
    boundary_markdown_visible = bool(
        ("Codex local proof" in markdown or "Local proof" in markdown)
        and "Manual/device proof" in markdown
    )
    if not boundary_markdown_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-markdown-proof-boundary-missing",
            evidence=f"{path_name} has performance findings but Markdown does not separate local proof from manual/device proof",
            recommendation="Show Codex-local proof and manual/device proof separately in Markdown so report readers know what can be verified in the current thread.",
        )
    return issues


def performance_runtime_evidence_boundary_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    boundary = report.get("runtimeEvidenceBoundary")
    if not isinstance(boundary, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-evidence-boundary-missing",
            evidence=f"{path_name} has no runtimeEvidenceBoundary",
            recommendation=(
                "State that source-only performance findings are source heuristics with medium confidence, "
                "missing runtime proof, and no target-app blocking claim."
            ),
        )
        return issues

    evidence = normalized_question_text(boundary.get("evidence") or boundary.get("evidenceType") or "")
    confidence = normalized_question_text(boundary.get("confidence") or "")
    runtime_proof = normalized_question_text(boundary.get("runtimeProof") or "")
    blocking = normalized_question_text(boundary.get("blocking") or "")
    interpretation = normalized_question_text(boundary.get("interpretation") or "")
    promotion_rule = normalized_question_text(boundary.get("promotionRule") or "")
    proof_items = boundary.get("requiredRuntimeProof")
    proof_text = normalized_question_text(" ".join(str(item) for item in proof_items if isinstance(item, str))) if isinstance(proof_items, list) else ""

    if evidence not in {"source heuristic", "source-heuristic", "source heuristics", "source-only heuristic"}:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-evidence-type-invalid",
            evidence=f"{path_name} runtimeEvidenceBoundary evidence={boundary.get('evidence')!r}",
            recommendation="Use evidence='source heuristic' until runtime profiler or device evidence is attached.",
        )
    if confidence != "medium":
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-confidence-invalid",
            evidence=f"{path_name} runtimeEvidenceBoundary confidence={boundary.get('confidence')!r}",
            recommendation="Use confidence='medium' for source-only performance reports unless calibrated runtime evidence changes that claim.",
        )
    if runtime_proof != "missing":
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-proof-invalid",
            evidence=f"{path_name} runtimeEvidenceBoundary runtimeProof={boundary.get('runtimeProof')!r}",
            recommendation="Use runtimeProof='missing' for source-only performance reports before a trace, sample, or device proof is attached.",
        )
    if blocking not in {"no", "false"}:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-blocking-invalid",
            evidence=f"{path_name} runtimeEvidenceBoundary blocking={boundary.get('blocking')!r}",
            recommendation="Use blocking='no' so source-only performance suspicion does not become target-app remediation authority.",
        )
    if not all(token in interpretation for token in ("source", "prove", "cpu", "gpu", "fps")):
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-interpretation-incomplete",
            evidence=f"{path_name} runtimeEvidenceBoundary interpretation does not clearly separate source suspicion from runtime proof",
            recommendation="Explain that the report nominates proof candidates and does not prove CPU/GPU/FPS/runtime problems by itself.",
        )
    if "promote" not in promotion_rule and "promotion" not in promotion_rule:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-promotion-rule-missing",
            evidence=f"{path_name} runtimeEvidenceBoundary has no promotion rule",
            recommendation="State what evidence promotes a source suspicion into a broader performance finding or ShipGuard rule change.",
        )
    if not all(token in proof_text for token in ("simulator", "physical-device")):
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-proof-list-incomplete",
            evidence=f"{path_name} runtimeEvidenceBoundary requiredRuntimeProof does not separate Simulator and physical-device proof",
            recommendation="List local Simulator proof separately from physical-device proof for hardware, thermal, ProMotion, and release claims.",
        )

    if issues:
        return issues
    markdown_boundary_visible = (
        "Runtime Evidence Boundary" in markdown
        and "Evidence: `source heuristic`" in markdown
        and "Runtime proof: `missing`" in markdown
        and "Blocking: `no`" in markdown
    )
    if not markdown_boundary_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-runtime-boundary-markdown-missing",
            evidence=f"{path_name} has runtimeEvidenceBoundary JSON but Markdown does not show the source-heuristic boundary",
            recommendation="Show Evidence, Confidence, Runtime proof, and Blocking in Markdown before report-quality passes.",
        )
    return issues


def performance_evidence_promotion_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    findings = report.get("findings")
    has_findings = isinstance(findings, list) and bool(findings)
    status = normalized_question_text(report.get("status") or "")
    if not has_findings and status == "pass":
        return issues

    promotion = report.get("evidencePromotion")
    if not isinstance(promotion, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="performance-evidence-promotion-contract-missing",
            evidence=f"{path_name} has performance findings without evidencePromotion",
            recommendation="Add evidencePromotion with sourceEvidence, promotionStatus, first candidate rule, proof requirements, and one exact nextAction.",
        )
        return issues

    source_evidence = normalized_question_text(promotion.get("sourceEvidence") or "")
    promotion_status = normalized_question_text(promotion.get("promotionStatus") or "")
    if "source" not in source_evidence or "heuristic" not in source_evidence:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-evidence-promotion-source-missing",
            evidence=f"{path_name} evidencePromotion sourceEvidence={promotion.get('sourceEvidence')!r}",
            recommendation="State that the promotion contract starts from source-heuristic evidence.",
        )
    if not promotion_status:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-evidence-promotion-status-missing",
            evidence=f"{path_name} evidencePromotion has no promotionStatus",
            recommendation="State whether runtime proof is missing, attached, rejected, or not needed.",
        )

    action = promotion.get("nextAction")
    if not isinstance(action, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-missing",
            evidence=f"{path_name} evidencePromotion has no nextAction",
            recommendation="Provide exactly one nextAction with owner, command or manual proof, expected artifact, success condition, and failure meaning.",
        )
        return issues

    owner = normalized_question_text(action.get("owner") or "")
    command = normalized_question_text(action.get("command") or "")
    manual_proof = normalized_question_text(action.get("manualProof") or action.get("manual_proof") or "")
    expected_artifact = normalized_question_text(action.get("expectedArtifact") or action.get("expected_artifact") or "")
    success_condition = normalized_question_text(action.get("successCondition") or action.get("success_condition") or "")
    failure_meaning = normalized_question_text(action.get("failureMeaning") or action.get("failure_meaning") or "")
    if not owner:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-owner-missing",
            evidence=f"{path_name} evidencePromotion.nextAction has no owner",
            recommendation="Name who owns the next proof step, usually developer for local/manual performance evidence.",
        )
    if not command and not manual_proof:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-proof-missing",
            evidence=f"{path_name} evidencePromotion.nextAction has neither command nor manualProof",
            recommendation="Provide either a runnable command or a concrete manual/device proof instruction.",
        )
    if not expected_artifact:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-artifact-missing",
            evidence=f"{path_name} evidencePromotion.nextAction has no expectedArtifact",
            recommendation="Name the artifact a maintainer should attach before promoting the source suspicion.",
        )
    if not success_condition:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-success-missing",
            evidence=f"{path_name} evidencePromotion.nextAction has no successCondition",
            recommendation="Define the condition that proves the source suspicion was promoted by runtime evidence.",
        )
    if not failure_meaning:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-next-action-failure-missing",
            evidence=f"{path_name} evidencePromotion.nextAction has no failureMeaning",
            recommendation="Explain what it means if the next proof action fails or produces no signal.",
        )

    if issues:
        return issues
    markdown_contract_visible = (
        "Evidence Promotion Contract" in markdown
        and "Expected artifact" in markdown
        and "Success condition" in markdown
        and "Failure meaning" in markdown
        and ("Manual proof" in markdown or "Command" in markdown)
    )
    if not markdown_contract_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="performance-markdown-evidence-promotion-missing",
            evidence=f"{path_name} has evidencePromotion JSON but Markdown does not show the exact next-action contract",
            recommendation="Render the evidence promotion contract in Markdown so reviewers see the owner, proof, artifact, success condition, and failure meaning.",
        )
    return issues


def design_app_type_tailoring_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    app_type = report.get("appType")
    app_value = ""
    if isinstance(app_type, dict):
        app_value = normalized_question_text(app_type.get("value") or "")
    if not app_value:
        add_issue(
            issues,
            severity="review",
            rule_id="design-app-type-missing",
            evidence=f"{path_name} has no appType.value",
            recommendation="Emit appType.value so design guidance can be checked against the inferred or overridden app category.",
        )

    tailoring = report.get("designTailoring")
    if not isinstance(tailoring, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-contract-missing",
            evidence=f"{path_name} has no designTailoring contract",
            recommendation="Add designTailoring with tailoredFor, guidanceProfile, sourceSignals, dimensions, and one exact nextAction.",
        )
        return issues

    tailored_for = normalized_question_text(tailoring.get("tailoredFor") or "")
    guidance_profile = normalized_question_text(tailoring.get("guidanceProfile") or "")
    if app_value and tailored_for != app_value:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-app-type-mismatch",
            evidence=f"{path_name} appType.value={app_value!r} but designTailoring.tailoredFor={tailored_for!r}",
            recommendation="Set designTailoring.tailoredFor to the same app type used by motion, haptics, copy, and layout guidance.",
        )
    if not guidance_profile or "universal" in guidance_profile or guidance_profile == "default":
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-profile-generic",
            evidence=f"{path_name} guidanceProfile={tailoring.get('guidanceProfile')!r}",
            recommendation="Name a specific app-type guidance profile such as utility-speed, learning-progress, calm-confidence, transactional-trust, workflow-density, human-relationship, or expressive-delight.",
        )
    if tailoring.get("universalDefaultsRejected") is not True:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-universal-defaults-not-rejected",
            evidence=f"{path_name} universalDefaultsRejected={tailoring.get('universalDefaultsRejected')!r}",
            recommendation="State that universal design defaults were rejected and guidance was weighted by app type.",
        )

    source_signals = tailoring.get("sourceSignals")
    if not isinstance(source_signals, list) or not source_signals:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-source-signals-missing",
            evidence=f"{path_name} designTailoring has no sourceSignals",
            recommendation="Attach the source or metadata signals that justify the selected app type.",
        )

    dimensions = tailoring.get("dimensions")
    required_dimensions = ("motion", "haptics", "visualDensity", "copyTone")
    if not isinstance(dimensions, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-dimensions-missing",
            evidence=f"{path_name} designTailoring has no dimensions object",
            recommendation="Provide motion, haptics, visualDensity, and copyTone tailoring dimensions.",
        )
        dimensions = {}
    for dimension in required_dimensions:
        if not isinstance(dimensions.get(dimension), dict):
            add_issue(
                issues,
                severity="review",
                rule_id=f"design-tailoring-{dimension.lower()}-missing",
                evidence=f"{path_name} designTailoring.dimensions.{dimension} is missing",
                recommendation=f"Add designTailoring.dimensions.{dimension} so app-type guidance is not a single universal paragraph.",
            )

    haptics_dimension = dimensions.get("haptics") if isinstance(dimensions, dict) else None
    haptics_tone = normalized_question_text(
        haptics_dimension.get("tone") if isinstance(haptics_dimension, dict) else ""
    )
    if app_value and app_value != "utility" and haptics_tone == "quiet and utility-focused":
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-haptics-universal-utility-tone",
            evidence=f"{path_name} uses utility haptics tone for appType={app_value}",
            recommendation="Tailor haptic tone to the app category instead of reusing the utility default.",
        )

    action = tailoring.get("nextAction")
    if not isinstance(action, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-missing",
            evidence=f"{path_name} designTailoring has no nextAction",
            recommendation="Provide one exact nextAction with owner, manual proof or command, expected artifact, success condition, and failure meaning.",
        )
        return issues

    owner = normalized_question_text(action.get("owner") or "")
    command = normalized_question_text(action.get("command") or "")
    manual_proof = normalized_question_text(action.get("manualProof") or action.get("manual_proof") or "")
    expected_artifact = normalized_question_text(action.get("expectedArtifact") or action.get("expected_artifact") or "")
    success_condition = normalized_question_text(action.get("successCondition") or action.get("success_condition") or "")
    failure_meaning = normalized_question_text(action.get("failureMeaning") or action.get("failure_meaning") or "")
    if not owner:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-owner-missing",
            evidence=f"{path_name} designTailoring.nextAction has no owner",
            recommendation="Name who owns the next design proof step.",
        )
    if not command and not manual_proof:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-proof-missing",
            evidence=f"{path_name} designTailoring.nextAction has neither command nor manualProof",
            recommendation="Provide either a runnable command or concrete manual preview/design proof instruction.",
        )
    if not expected_artifact:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-artifact-missing",
            evidence=f"{path_name} designTailoring.nextAction has no expectedArtifact",
            recommendation="Name the artifact that proves app-type-tailored guidance was reviewed.",
        )
    if not success_condition:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-success-missing",
            evidence=f"{path_name} designTailoring.nextAction has no successCondition",
            recommendation="Define what proves the design report is app-type tailored.",
        )
    if not failure_meaning:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-next-action-failure-missing",
            evidence=f"{path_name} designTailoring.nextAction has no failureMeaning",
            recommendation="Explain what it means when app-type proof is missing or generic.",
        )

    if issues:
        return issues
    markdown_contract_visible = (
        "Design Tailoring Contract" in markdown
        and "Guidance profile" in markdown
        and "Universal defaults rejected" in markdown
        and "Expected artifact" in markdown
        and "Success condition" in markdown
        and "Failure meaning" in markdown
    )
    if not markdown_contract_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="design-tailoring-markdown-missing",
            evidence=f"{path_name} has designTailoring JSON but Markdown does not show the exact app-type contract",
            recommendation="Render the design tailoring contract in Markdown so reviewers see app type, profile, proof, artifact, success condition, and failure meaning.",
        )
    return issues


def design_principle_vocabulary_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    required = (
        "contrast",
        "hierarchy",
        "alignment",
        "proximity",
        "repetition",
        "balance",
        "white space",
        "unity",
        "motion",
        "haptics",
        "preview proof",
        "app-type fit",
    )
    vocabulary = report.get("professionalDesignPrincipleVocabulary")
    if not isinstance(vocabulary, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-principle-vocabulary-missing",
            evidence=f"{path_name} has no professionalDesignPrincipleVocabulary",
            recommendation="Add explicit professional design vocabulary so design QA uses concrete principles instead of generic make-it-prettier advice.",
        )
        return issues

    principles = vocabulary.get("requiredPrinciples")
    checks = vocabulary.get("checks")
    principle_names = {
        normalized_question_text(item.get("principle") or "")
        for item in checks
        if isinstance(item, dict)
    } if isinstance(checks, list) else set()
    declared = {
        normalized_question_text(item)
        for item in principles
        if isinstance(item, str)
    } if isinstance(principles, list) else set()
    missing = [item for item in required if item not in principle_names or item not in declared]
    if missing:
        add_issue(
            issues,
            severity="review",
            rule_id="design-principle-vocabulary-incomplete",
            evidence=f"{path_name} is missing design principle vocabulary entries: {', '.join(missing)}",
            recommendation="Include contrast, hierarchy, alignment, proximity, repetition, balance, white space, unity, motion, haptics, preview proof, and app-type fit.",
        )
    if not isinstance(checks, list) or any(
        not isinstance(item, dict)
        or not normalized_question_text(item.get("principle") or "")
        or not normalized_question_text(item.get("question") or "")
        for item in checks or []
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="design-principle-vocabulary-questions-missing",
            evidence=f"{path_name} professionalDesignPrincipleVocabulary checks are not review-ready",
            recommendation="Give every principle a concrete review question so the report is actionable.",
        )

    if issues:
        return issues
    markdown_lower = normalized_question_text(markdown)
    markdown_visible = "professional design principle vocabulary" in markdown_lower and all(
        item in markdown_lower for item in required
    )
    if not markdown_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="design-principle-vocabulary-markdown-missing",
            evidence=f"{path_name} has professionalDesignPrincipleVocabulary JSON but Markdown does not show the principle vocabulary",
            recommendation="Render the professional design principles in Markdown so humans see the design QA lens.",
        )
    return issues


def design_coherence_boundary_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if report.get("intent") != "shipguard-evaluation":
        return issues

    boundary = report.get("designCoherenceBoundary")
    if not isinstance(boundary, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-boundary-missing",
            evidence=f"{path_name} has no designCoherenceBoundary contract",
            recommendation=(
                "Add designCoherenceBoundary so ShipGuard product-QA runs separate source inventory, "
                "coherence risks, ShipGuard follow-up work, and target-app authorization."
            ),
        )
        return issues

    source_inventory = boundary.get("sourceInventory")
    if not isinstance(source_inventory, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-source-inventory-missing",
            evidence=f"{path_name} designCoherenceBoundary has no sourceInventory",
            recommendation="Keep source inventory separate from coherence risks and recommendations.",
        )

    coherence_risks = boundary.get("coherenceRisks")
    findings = report.get("findings")
    if not isinstance(coherence_risks, list):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-risks-missing",
            evidence=f"{path_name} designCoherenceBoundary has no coherenceRisks list",
            recommendation="List the coherence risks separately from source inventory and target-app tasks.",
        )
    elif isinstance(findings, list) and findings and not coherence_risks:
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-risks-empty",
            evidence=f"{path_name} has design findings but no designCoherenceBoundary.coherenceRisks entries",
            recommendation="Mirror design coherence findings into coherenceRisks so the report does not collapse into a generic inventory.",
        )

    checks = boundary.get("separationChecks")
    required_checks = (
        "inventoryIsNotRemediation",
        "coherenceRiskIsNotTargetTask",
        "shipguardActionIsPublicFixtureOrRule",
        "appWorkRequiresSeparateAuthorization",
    )
    if not isinstance(checks, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-separation-checks-missing",
            evidence=f"{path_name} designCoherenceBoundary has no separationChecks",
            recommendation="Emit explicit boolean separation checks for inventory, risks, ShipGuard action, and app-work authorization.",
        )
        checks = {}
    for key in required_checks:
        if checks.get(key) is not True:
            add_issue(
                issues,
                severity="review",
                rule_id=f"design-coherence-{kebab_case(key)}-missing",
                evidence=f"{path_name} designCoherenceBoundary.separationChecks.{key} is not true",
                recommendation=f"Set separationChecks.{key}=true when the report keeps this boundary explicit.",
            )

    action = boundary.get("shipguardNextAction")
    if not isinstance(action, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-shipguard-next-action-missing",
            evidence=f"{path_name} designCoherenceBoundary has no shipguardNextAction",
            recommendation="Provide one ShipGuard-owned next action, not a target-app redesign task.",
        )
        action = {}
    action_kind = normalized_question_text(action.get("kind") or "")
    if not action.get("owner"):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-next-action-owner-missing",
            evidence=f"{path_name} designCoherenceBoundary.shipguardNextAction has no owner",
            recommendation="Name the ShipGuard-side owner for the next report-quality improvement.",
        )
    if not action_kind or ("app" in action_kind and "shipguard" not in action_kind):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-next-action-kind-unsafe",
            evidence=f"{path_name} designCoherenceBoundary.shipguardNextAction.kind={action.get('kind')!r}",
            recommendation="Keep the next action in ShipGuard-owned fixture, rule, docs, or report-quality work.",
        )
    for key, rule_id, label in (
        ("expectedArtifact", "design-coherence-next-action-artifact-missing", "expected artifact"),
        ("successCondition", "design-coherence-next-action-success-missing", "success condition"),
        ("failureMeaning", "design-coherence-next-action-failure-missing", "failure meaning"),
    ):
        if not normalized_question_text(action.get(key) or ""):
            add_issue(
                issues,
                severity="review",
                rule_id=rule_id,
                evidence=f"{path_name} designCoherenceBoundary.shipguardNextAction has no {key}",
                recommendation=f"Name the {label} for the ShipGuard-owned coherence-boundary improvement.",
            )

    authorization = boundary.get("appWorkAuthorization")
    if not isinstance(authorization, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-app-work-authorization-missing",
            evidence=f"{path_name} designCoherenceBoundary has no appWorkAuthorization",
            recommendation="Declare whether this product-QA report authorizes target-app design work.",
        )
        authorization = {}
    if authorization.get("status") != "not-authorized-from-this-run":
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-app-work-status-unsafe",
            evidence=f"{path_name} appWorkAuthorization.status={authorization.get('status')!r}",
            recommendation="Use status=not-authorized-from-this-run for ShipGuard product-QA scans against private apps.",
        )
    if authorization.get("requiresExplicitRequest") is not True:
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-explicit-request-missing",
            evidence=f"{path_name} appWorkAuthorization.requiresExplicitRequest is not true",
            recommendation="Require a separate explicit app-work request before converting coherence risks into target-app edits.",
        )
    forbidden = authorization.get("forbiddenActions")
    allowed = authorization.get("allowedShipGuardActions")
    if not isinstance(forbidden, list) or not forbidden:
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-forbidden-actions-missing",
            evidence=f"{path_name} appWorkAuthorization has no forbiddenActions",
            recommendation="List target-app actions that are forbidden from the product-QA run.",
        )
    if not isinstance(allowed, list) or not allowed:
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-allowed-shipguard-actions-missing",
            evidence=f"{path_name} appWorkAuthorization has no allowedShipGuardActions",
            recommendation="List ShipGuard-owned improvements that are allowed from this product-QA run.",
        )

    proof_boundary = boundary.get("proofBoundary")
    if not isinstance(proof_boundary, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-proof-boundary-missing",
            evidence=f"{path_name} designCoherenceBoundary has no proofBoundary",
            recommendation="Split local report-quality proof from manual app-work authorization proof.",
        )
        proof_boundary = {}
    for key, rule_id in (
        ("localProof", "design-coherence-local-proof-missing"),
        ("manualProof", "design-coherence-manual-proof-missing"),
        ("expectedArtifact", "design-coherence-proof-artifact-missing"),
    ):
        if not normalized_question_text(proof_boundary.get(key) or ""):
            add_issue(
                issues,
                severity="review",
                rule_id=rule_id,
                evidence=f"{path_name} designCoherenceBoundary.proofBoundary has no {key}",
                recommendation="State the proof boundary before promoting private-app evidence into public ShipGuard rules.",
            )

    if boundary.get("targetRemediationStatus") != "not-authorized-from-this-run":
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-target-remediation-status-unsafe",
            evidence=f"{path_name} targetRemediationStatus={boundary.get('targetRemediationStatus')!r}",
            recommendation="Keep targetRemediationStatus=not-authorized-from-this-run for ShipGuard product-QA reports.",
        )

    if issues:
        return issues
    markdown_contract_visible = (
        "Design Coherence Boundary" in markdown
        and "ShipGuard next action" in markdown
        and "App work authorization" in markdown
        and "not-authorized-from-this-run" in markdown
        and "Success condition" in markdown
        and "Failure meaning" in markdown
        and "Proof boundary" in markdown
    )
    if not markdown_contract_visible:
        add_issue(
            issues,
            severity="review",
            rule_id="design-coherence-markdown-missing",
            evidence=f"{path_name} has designCoherenceBoundary JSON but Markdown does not show the boundary contract",
            recommendation="Render the coherence boundary in Markdown so readers see the ShipGuard next action and app-work authorization status.",
        )
    return issues


def design_preview_routing_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    questions = report.get("reportQualityQuestions")
    findings = report.get("findings")
    preview_question = (
        isinstance(questions, list)
        and any(
            "preview" in normalized_question_text(item)
            or "devspace" in normalized_question_text(item)
            for item in questions
        )
    )
    preview_finding = (
        isinstance(findings, list)
        and any(isinstance(item, dict) and item.get("ruleId") == "preview-proof-not-provided" for item in findings)
    )
    has_preview_evidence = isinstance(report.get("previewEvidence"), dict)
    if not (preview_question or preview_finding or has_preview_evidence):
        return issues

    preview = report.get("previewEvidence")
    if not isinstance(preview, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="design-preview-evidence-missing",
            evidence=f"{path_name} has preview/devspace guidance but no previewEvidence object",
            recommendation="Emit previewEvidence so report-quality can distinguish missing visual proof from supplied preview receipts.",
        )
        return issues

    status = normalized_question_text(preview.get("status") or "")
    if status not in {"not-provided", "provided", "missing"}:
        add_issue(
            issues,
            severity="review",
            rule_id="design-preview-evidence-status-missing",
            evidence=f"{path_name} previewEvidence.status={preview.get('status')!r}",
            recommendation="Set previewEvidence.status to not-provided, provided, or missing.",
        )

    if status == "not-provided":
        commands = preview.get("recommendedCommands")
        command_text = "\n".join(str(item) for item in commands) if isinstance(commands, list) else ""
        if "shipguard ios preview" not in command_text:
            add_issue(
                issues,
                severity="review",
                rule_id="design-preview-command-missing",
                evidence=f"{path_name} previewEvidence has no shipguard ios preview command",
                recommendation="Recommend `shipguard ios preview --out <preview-out>` when no visual proof is attached.",
            )
        if "shipguard ios devspace" not in command_text or "SHIPGUARD_DEVSPACE_TOKEN" not in command_text:
            add_issue(
                issues,
                severity="review",
                rule_id="design-devspace-command-missing",
                evidence=f"{path_name} previewEvidence has no authenticated shipguard ios devspace command",
                recommendation="Recommend the Devspace bridge with --preview-out and bearer-token env guidance when ChatGPT should plan from the phone widget.",
            )
        markdown_visible = (
            "Preview And Devspace" in markdown
            and "shipguard ios preview" in markdown
            and "shipguard ios devspace" in markdown
            and "model selection happens in ChatGPT" in markdown
        )
        if not markdown_visible:
            add_issue(
                issues,
                severity="review",
                rule_id="design-preview-devspace-markdown-missing",
                evidence=f"{path_name} previewEvidence JSON exists but Markdown does not make preview/devspace routing obvious",
                recommendation="Render a Preview And Devspace section with the preview command, Devspace command, and model-choice boundary.",
            )

    if status == "provided":
        for key in ("path", "sessionFound", "handoffFound", "screenshotFound", "eventCount"):
            if key not in preview:
                add_issue(
                    issues,
                    severity="review",
                    rule_id=f"design-preview-provided-{kebab_case(key)}-missing",
                    evidence=f"{path_name} previewEvidence.status=provided but {key} is missing",
                    recommendation="Expose supplied preview receipt facts so visual claims can be checked without opening local files.",
                )
        markdown_visible = (
            "Preview And Devspace" in markdown
            and "Preview directory" in markdown
            and "Session found" in markdown
            and "Handoff found" in markdown
            and "Screenshot found" in markdown
            and "Event count" in markdown
        )
        if not markdown_visible:
            add_issue(
                issues,
                severity="review",
                rule_id="design-preview-provided-markdown-missing",
                evidence=f"{path_name} has provided previewEvidence but Markdown does not show the receipt facts",
                recommendation="Render preview receipt status in Markdown so reviewers can see session, handoff, screenshot, and event proof at a glance.",
            )

    return issues


def stable_publication_evidence_packet_issues(
    report: dict[str, Any], *, markdown: str, path_name: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    packet = report.get("stablePublicationEvidencePacket")
    if not isinstance(packet, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-packet-missing",
            evidence=f"{path_name} has no stablePublicationEvidencePacket",
            recommendation="Emit one evidence packet that lists every real stable-v4 evidence input, current status, first blocker, next command, and non-claims.",
        )
        return issues

    required = packet.get("requiredEvidence")
    required_rows = required if isinstance(required, list) else []
    synthetic_fixture_report = isinstance(report.get("fixtureCandidate"), dict) or path_name == "fixture-report.json"
    freshness_expected = isinstance(report.get("publicReleaseFreshnessProof"), dict) or not synthetic_fixture_report
    minimum_required_count = 10 if freshness_expected else 7
    if not isinstance(required, list) or len(required) < minimum_required_count:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-required-evidence-incomplete",
            evidence=f"{path_name} evidence packet does not list all required stable-publication evidence gates",
            recommendation="List release metadata, release notes, LaunchKey candidate proof, downloaded assets, consumer proof, public release freshness, release version coherence, release asset coherence, adoption evidence, and security review evidence.",
        )
    else:
        required_ids = {str(item.get("id") or "") for item in required_rows if isinstance(item, dict)}
        expected = {
            "github-release-metadata",
            "release-notes",
            "launchkey-candidate-packet",
            "downloaded-release-assets",
            "post-release-consumer-proof",
            "independent-adoption-evidence",
            "final-security-review-evidence",
        }
        if freshness_expected:
            expected.add("public-release-freshness")
            expected.add("release-version-coherence")
            expected.add("release-asset-coherence")
        missing_ids = sorted(expected - required_ids)
        if missing_ids:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-required-evidence-ids-missing",
                evidence=f"{path_name} evidence packet missing ids: {', '.join(missing_ids)}",
                recommendation="Use stable evidence ids so downstream tools can identify exactly which stable-v4 proof is missing.",
            )
        for item in required_rows:
            if not isinstance(item, dict):
                continue
            if item.get("requiredForStableV4") is not True or item.get("realEvidenceRequired") is not True:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-real-evidence-boundary-missing",
                    evidence=f"{path_name} evidence `{item.get('id')}` does not mark stable-v4 real-evidence requirements",
                    recommendation="Mark each stable-publication evidence input as requiredForStableV4 and realEvidenceRequired.",
                )

    missing_evidence = packet.get("missingEvidenceIds")
    if not isinstance(missing_evidence, list):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-missing-evidence-list-missing",
            evidence=f"{path_name} evidence packet has no missingEvidenceIds list",
            recommendation="Expose missingEvidenceIds so the next stable-v4 action is machine-readable.",
        )

    first_blocking = packet.get("firstBlockingGate")
    stable_release = report.get("stableV4Release") is True
    if stable_release:
        if packet.get("status") != "pass" or missing_evidence:
            add_issue(
                issues,
                severity="high",
                rule_id="stable-publication-packet-contradicts-pass",
                evidence=f"{path_name} claims stableV4Release while the evidence packet is not fully passing",
                recommendation="Only allow stableV4Release when the evidence packet status is pass and missingEvidenceIds is empty.",
            )
        if first_blocking is not None:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-pass-has-first-blocker",
                evidence=f"{path_name} passing evidence packet still includes firstBlockingGate",
                recommendation="Clear firstBlockingGate once every stable-publication evidence input passes.",
            )
    else:
        if not isinstance(first_blocking, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-first-blocker-missing",
                evidence=f"{path_name} blocks stable-v4 but does not identify the first blocking gate",
                recommendation="Set stablePublicationEvidencePacket.firstBlockingGate with receipt, status, summary, and nextCommand.",
            )
        elif not first_blocking.get("nextCommand"):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-first-blocker-command-missing",
                evidence=f"{path_name} first blocking gate has no nextCommand",
                recommendation="Attach the exact next command needed to clear the first stable-publication blocker.",
            )
        else:
            notes_kit_for_first_blocker = (
                report.get("stablePublicationReleaseNotesAuthoringKit")
                if isinstance(report.get("stablePublicationReleaseNotesAuthoringKit"), dict)
                else {}
            )
            if (
                first_blocking.get("id") == "release-notes"
                and int(notes_kit_for_first_blocker.get("schemaVersion") or 1) >= 2
                and first_blocking.get("nextCommand") != notes_kit_for_first_blocker.get("publicReleaseEditCommand")
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-first-blocker-release-notes-command-wrong",
                    evidence=f"{path_name} first blocking release-notes gate does not point at the GitHub release edit command",
                    recommendation="Set firstBlockingGate.nextCommand to stablePublicationReleaseNotesAuthoringKit.publicReleaseEditCommand when release notes are the first blocker.",
                )

    closure = report.get("stablePublicationClosureChecklist")
    if not isinstance(closure, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-closure-checklist-missing",
            evidence=f"{path_name} has no stablePublicationClosureChecklist",
            recommendation="Emit a closure checklist that lists every remaining stable-v4 blocker in dependency order with exact next commands.",
        )
    else:
        closure_items = closure.get("items")
        if not isinstance(closure_items, list):
            closure_items = []
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-closure-checklist-items-missing",
                evidence=f"{path_name} closure checklist has no items list",
                recommendation="List every non-passing stable-publication evidence gate as a closure item.",
            )
        expected_missing = [
            str(item.get("id")) for item in required_rows if isinstance(item, dict) and item.get("status") != "pass"
        ]
        closure_ids = [str(item.get("id")) for item in closure_items if isinstance(item, dict)]
        if stable_release:
            if closure.get("status") != "pass" or int(closure.get("blockerCount") or 0) != 0 or closure_items:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-pass-has-closure-blockers",
                    evidence=f"{path_name} stable-v4 pass still has closure checklist blockers",
                    recommendation="Set closure checklist status to pass with zero items once every stable-publication gate passes.",
                )
        else:
            if closure.get("noHiddenLowerOrderBlockers") is not True:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-closure-no-hidden-blockers-missing",
                    evidence=f"{path_name} closure checklist does not assert noHiddenLowerOrderBlockers",
                    recommendation="Set noHiddenLowerOrderBlockers=true after listing every non-passing gate in dependency order.",
                )
            if closure_ids != expected_missing or int(closure.get("blockerCount") or -1) != len(expected_missing):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-closure-checklist-incomplete",
                    evidence=f"{path_name} closure ids {closure_ids!r} do not match missing evidence ids {expected_missing!r}",
                    recommendation="Mirror every non-passing stablePublicationEvidencePacket.requiredEvidence row into the closure checklist in dependency order.",
                )
            first_blocking_id = first_blocking.get("id") if isinstance(first_blocking, dict) else None
            for index, item in enumerate(closure_items, start=1):
                if not isinstance(item, dict):
                    continue
                if item.get("rank") != index or not isinstance(item.get("dependencyOrder"), int):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="stable-publication-closure-checklist-rank-missing",
                        evidence=f"{path_name} closure item `{item.get('id')}` lacks stable rank/dependencyOrder",
                        recommendation="Give every closure item a rank and dependencyOrder so lower-order blockers remain visible.",
                    )
                if not item.get("nextCommand"):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="stable-publication-closure-checklist-command-missing",
                        evidence=f"{path_name} closure item `{item.get('id')}` has no nextCommand",
                        recommendation="Attach the exact command needed to clear each remaining stable-publication blocker.",
                    )
                if not item.get("proofBoundary"):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="stable-publication-closure-checklist-boundary-missing",
                        evidence=f"{path_name} closure item `{item.get('id')}` has no proofBoundary",
                        recommendation="Explain what real evidence must pass for each closure item before stable-v4 claims are allowed.",
                    )
                if item.get("id") == first_blocking_id and item.get("isFirstBlockingGate") is not True:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="stable-publication-closure-first-blocker-unmarked",
                        evidence=f"{path_name} closure item `{item.get('id')}` is the first blocker but is not marked",
                        recommendation="Set isFirstBlockingGate=true on the closure item that matches firstBlockingGate.",
                    )
                if item.get("id") == "github-release-metadata":
                    source_metadata = (
                        report.get("githubReleaseMetadataProof")
                        if isinstance(report.get("githubReleaseMetadataProof"), dict)
                        else {}
                    )
                    closure_kit = (
                        item.get("releaseMetadataClosureKit")
                        if isinstance(item.get("releaseMetadataClosureKit"), dict)
                        else {}
                    )
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-metadata-closure-kit-missing",
                            evidence=f"{path_name} github-release-metadata closure item has no releaseMetadataClosureKit",
                            recommendation="Attach a release metadata closure kit with repo inference, release tag, API endpoint, release state, asset inventory, release-note digest, repair/pass/fail criteria, rerun command, and metadata-proof boundaries.",
                        )
                    else:
                        if not closure_kit.get("repo") and not isinstance(closure_kit.get("repoInference"), dict):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-repo-missing",
                                evidence=f"{path_name} release metadata closure kit hides the selected repository and inference result",
                                recommendation="Expose the explicit or inferred owner/repo plus repoInference so maintainers know which public release ShipGuard queried.",
                            )
                        if not closure_kit.get("tag"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-tag-missing",
                                evidence=f"{path_name} release metadata closure kit omits the release tag",
                                recommendation="Expose the normalized release tag so wrong-version publication checks are easy to diagnose.",
                            )
                        if not closure_kit.get("releaseEndpoint") and source_metadata.get("provided") is True:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-endpoint-missing",
                                evidence=f"{path_name} release metadata closure kit omits the GitHub release API endpoint",
                                recommendation="Expose the endpoint used for release metadata lookup when a repository was provided or inferred.",
                            )
                        if not isinstance(closure_kit.get("requiredAssets"), list) or not closure_kit.get("requiredAssets"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-required-assets-missing",
                                evidence=f"{path_name} release metadata closure kit omits requiredAssets",
                                recommendation="List the stable-publication assets that GitHub release metadata must expose.",
                            )
                        if not isinstance(closure_kit.get("metadataMissingAssets"), list):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-missing-assets-missing",
                                evidence=f"{path_name} release metadata closure kit omits metadataMissingAssets",
                                recommendation="Expose missing release metadata assets even when the list is empty.",
                            )
                        release_state = (
                            closure_kit.get("releaseState")
                            if isinstance(closure_kit.get("releaseState"), dict)
                            else {}
                        )
                        if "isDraft" not in release_state or "isPrerelease" not in release_state:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-state-missing",
                                evidence=f"{path_name} release metadata closure kit omits draft/prerelease state",
                                recommendation="State whether the GitHub release is draft-only or prerelease-only, because neither can satisfy stable-publication proof.",
                            )
                        notes_summary = (
                            closure_kit.get("releaseNotesSummary")
                            if isinstance(closure_kit.get("releaseNotesSummary"), dict)
                            else {}
                        )
                        if "sha256" not in notes_summary or "missingTopicIds" not in notes_summary:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-notes-summary-missing",
                                evidence=f"{path_name} release metadata closure kit omits release-note digest or missing-topic summary",
                                recommendation="Expose the release-note SHA-256 and missing topic ids from GitHub metadata so notes and metadata can be repaired together.",
                            )
                        diagnostics = (
                            closure_kit.get("currentMetadataDiagnostics")
                            if isinstance(closure_kit.get("currentMetadataDiagnostics"), dict)
                            else {}
                        )
                        if not diagnostics:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-diagnostics-missing",
                                evidence=f"{path_name} release metadata closure kit has no currentMetadataDiagnostics",
                                recommendation="Mirror repository, tag, endpoint, release state, asset inventory, release notes digest, and error text into currentMetadataDiagnostics.",
                            )
                        else:
                            source_status = str(source_metadata.get("status") or "")
                            if source_status and str(diagnostics.get("status") or "") != source_status:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-release-metadata-diagnostics-status-drift",
                                    evidence=f"{path_name} release metadata diagnostics status does not mirror githubReleaseMetadataProof.status",
                                    recommendation="Keep currentMetadataDiagnostics.status aligned with githubReleaseMetadataProof.status.",
                                )
                        if not isinstance(closure_kit.get("repairCriteria"), list) or len(closure_kit.get("repairCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-repair-criteria-missing",
                                evidence=f"{path_name} release metadata closure kit does not list repair criteria",
                                recommendation="Tell maintainers how to repair repo selection, tag selection, draft/prerelease state, required assets, and rerun stable-publication.",
                            )
                        if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 4:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-pass-criteria-missing",
                                evidence=f"{path_name} release metadata closure kit does not list pass criteria",
                                recommendation="List concrete pass criteria for public repo/tag metadata, release state, required assets, release URL, and target commitish proof.",
                            )
                        if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 4:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-fail-criteria-missing",
                                evidence=f"{path_name} release metadata closure kit does not list fail criteria",
                                recommendation="List fail cases such as missing repo inference, invalid owner/repo syntax, missing tag, draft/prerelease release, missing assets, and fixture/source proof misuse.",
                            )
                        if "stable-publication" not in str(closure_kit.get("metadataRerunCommand") or item.get("metadataRerunCommand") or item.get("nextCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-rerun-command-missing",
                                evidence=f"{path_name} release metadata closure kit lacks the stable-publication metadata rerun command",
                                recommendation="Attach the stable-publication command to rerun after the public GitHub release repository, tag, state, or assets are repaired.",
                            )
                        boundary = (
                            closure_kit.get("metadataProofBoundary")
                            if isinstance(closure_kit.get("metadataProofBoundary"), dict)
                            else {}
                        )
                        if (
                            boundary.get("publicGitHubReleaseMetadataRequired") is not True
                            or boundary.get("draftOrPrereleaseCountsAsStablePublicationProof") is not False
                            or boundary.get("sourceOnlyProofCountsAsReleaseMetadataProof") is not False
                            or boundary.get("fixtureApiProofCountsAsStableV4PublicationProof") is not False
                        ):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-boundary-missing",
                                evidence=f"{path_name} release metadata closure kit does not state the public metadata, draft/prerelease, source-only, and fixture-API proof boundaries",
                                recommendation="State that stable-publication requires public GitHub release metadata and that draft/prerelease, source-only, and fixture API proof do not satisfy stable-v4 publication.",
                            )
                        if "GitHub Release Metadata Closure Kit" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-metadata-closure-kit-markdown-missing",
                                evidence=f"{path_name} Markdown does not render the release metadata closure kit",
                                recommendation="Render repo inference, tag, endpoint, release state, asset inventory, release notes digest, criteria, rerun command, and proof boundaries in Markdown.",
                            )
                if item.get("id") == "launchkey-candidate-packet":
                    source_candidate = (
                        report.get("releaseCandidatePacketProof")
                        if isinstance(report.get("releaseCandidatePacketProof"), dict)
                        else {}
                    )
                    closure_kit = (
                        item.get("launchKeyCandidateClosureKit")
                        if isinstance(item.get("launchKeyCandidateClosureKit"), dict)
                        else {}
                    )
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-launchkey-candidate-closure-kit-missing",
                            evidence=f"{path_name} launchkey-candidate-packet closure item has no launchKeyCandidateClosureKit",
                            recommendation="Attach a candidate closure kit with the supplied candidate report path, nested blocking receipt, required LaunchKey proof areas, package-hygiene diagnostics, repair/pass criteria, nested rerun command, full stable-publication rerun command, and fixture-proof boundary.",
                        )
                    else:
                        candidate_was_supplied = (
                            source_candidate.get("provided") is True
                            or bool(source_candidate.get("reportPath"))
                            or bool(closure_kit.get("suppliedCandidateReportPath"))
                        )
                        if candidate_was_supplied and not closure_kit.get("candidateReportPath"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-candidate-report-path-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit omits the supplied candidate report path",
                                recommendation="Expose the supplied candidate report path directly on the closure kit so maintainers know which LaunchKey JSON produced the blocker.",
                            )
                        if not closure_kit.get("nestedBlockingReceipt"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-nested-receipt-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit omits the nested blocking receipt",
                                recommendation="Name the failing LaunchKey receipt, or synthesize it from the first missing package proof when LaunchKey did not emit blockingProof.",
                            )
                        required_areas = (
                            closure_kit.get("requiredLaunchKeyProofAreas")
                            if isinstance(closure_kit.get("requiredLaunchKeyProofAreas"), list)
                            else []
                        )
                        required_receipts = {str(area.get("receipt") or "") for area in required_areas if isinstance(area, dict)}
                        expected_receipts = {
                            "freshInstallPackageProof",
                            "upgradePackageProof",
                            "rollbackPackageProof",
                        }
                        if len(required_areas) < 3 or not expected_receipts <= required_receipts:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-required-proof-areas-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit does not list the package proof areas needed for candidate closure",
                                recommendation="List fresh install, same-prefix upgrade, and rollback cleanup proof areas, plus the adjacent release-asset/adoption/security areas when present.",
                            )
                        source_hygiene = {}
                        source_blocker = (
                            source_candidate.get("launchKeyBlockingProof")
                            if isinstance(source_candidate.get("launchKeyBlockingProof"), dict)
                            else {}
                        )
                        if isinstance(source_blocker.get("packageHygieneEvidence"), dict):
                            source_hygiene = source_blocker["packageHygieneEvidence"]
                        elif isinstance(source_candidate.get("packageHygieneEvidence"), dict):
                            source_hygiene = source_candidate["packageHygieneEvidence"]
                        kit_hygiene = (
                            closure_kit.get("packageHygieneDiagnostics")
                            if isinstance(closure_kit.get("packageHygieneDiagnostics"), dict)
                            else {}
                        )
                        if source_hygiene and not kit_hygiene:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-package-hygiene-diagnostics-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit hides package hygiene diagnostics from the nested blocker",
                                recommendation="Mirror package hygiene status, first finding, blocked count, affected versions, and hygiene rerun command into the candidate closure kit.",
                            )
                        if not isinstance(closure_kit.get("repairCriteria"), list) or len(closure_kit.get("repairCriteria") or []) < 2:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-repair-criteria-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit does not list repair criteria",
                                recommendation="Tell maintainers how to repair package lineage, rerun LaunchKey, and then rerun stable-publication without editing proof reports.",
                            )
                        if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-pass-criteria-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit does not list pass criteria",
                                recommendation="List the concrete LaunchKey statuses that must pass before the candidate blocker is closed.",
                            )
                        if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-fail-criteria-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit does not list fail criteria",
                                recommendation="List common fail cases such as wrong tool, non-passing status, missing package proof, nested blockers, package-hygiene failures, and fixture proof misuse.",
                            )
                        if "release-candidate" not in str(closure_kit.get("nestedRerunCommand") or item.get("nestedRerunCommand") or item.get("nextCommand") or "") and "release-package hygiene" not in str(closure_kit.get("nestedRerunCommand") or item.get("nestedRerunCommand") or item.get("nextCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-nested-rerun-command-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit lacks the nested LaunchKey or package-hygiene rerun command",
                                recommendation="Attach the exact nested rerun command that clears the LaunchKey blocker before stable-publication is rerun.",
                            )
                        if "stable-publication" not in str(closure_kit.get("stablePublicationRerunCommand") or item.get("stablePublicationRerunCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-full-rerun-command-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit lacks the full stable-publication rerun command",
                                recommendation="Attach the full stable-publication command to run after LaunchKey candidate proof passes, preserving later release notes, asset, adoption, and security gates.",
                            )
                        fixture_boundary = (
                            closure_kit.get("fixtureCandidateBoundary")
                            if isinstance(closure_kit.get("fixtureCandidateBoundary"), dict)
                            else {}
                        )
                        if fixture_boundary.get("fixtureCandidateProofCountsAsStableV4PublicationProof") is not False:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-fixture-boundary-missing",
                                evidence=f"{path_name} LaunchKey candidate closure kit does not state that fixture candidate proof is not stable-v4 publication proof",
                                recommendation="Keep fixture LaunchKey reports as tooling tests only; stable-v4 publication must still pass real release metadata, assets, adoption, and security gates.",
                            )
                        if "LaunchKey Candidate Closure Kit" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-launchkey-closure-kit-markdown-missing",
                                evidence=f"{path_name} Markdown does not render the LaunchKey candidate closure kit",
                                recommendation="Render candidate report path, nested receipt, required proof areas, hygiene diagnostics, repair/pass criteria, nested rerun, full stable-publication rerun, and fixture-proof boundary in Markdown.",
                            )
                if item.get("id") == "downloaded-release-assets":
                    source_assets = (
                        report.get("publishedReleaseAssetProof")
                        if isinstance(report.get("publishedReleaseAssetProof"), dict)
                        else {}
                    )
                    closure_kit = (
                        item.get("releaseAssetClosureKit")
                        if isinstance(item.get("releaseAssetClosureKit"), dict)
                        else {}
                    )
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-assets-closure-kit-missing",
                            evidence=f"{path_name} downloaded-release-assets closure item has no releaseAssetClosureKit",
                            recommendation="Attach a release asset closure kit with required assets, metadata/local missing assets, download status/source, asset directory, repair/pass/fail criteria, download rerun, stable-publication rerun, and metadata-only/source-only/fixture-proof boundaries.",
                        )
                    else:
                        if not isinstance(closure_kit.get("requiredAssets"), list) or not closure_kit.get("requiredAssets"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-required-assets-missing",
                                evidence=f"{path_name} release asset closure kit omits requiredAssets",
                                recommendation="Expose the required stable-publication release assets directly on the closure kit.",
                            )
                        if not isinstance(closure_kit.get("metadataMissingAssets"), list):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-metadata-missing-assets-missing",
                                evidence=f"{path_name} release asset closure kit omits metadataMissingAssets",
                                recommendation="Mirror GitHub metadata missing assets so maintainers know whether the public release is incomplete before checking local downloads.",
                            )
                        if not closure_kit.get("assetsDir") and not isinstance(closure_kit.get("missingLocalAssets"), list):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-local-assets-or-missing-list-missing",
                                evidence=f"{path_name} release asset closure kit hides the asset directory and does not list missing local assets",
                                recommendation="Expose assetsDir when assets were supplied/downloaded, or list missingLocalAssets when no local asset packet exists.",
                            )
                        if not closure_kit.get("downloadProofStatus"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-download-status-missing",
                                evidence=f"{path_name} release asset closure kit omits downloadProofStatus",
                                recommendation="Mirror whether GitHub release asset download was pass, blocked, not-requested, or not-provided.",
                            )
                        diagnostics = (
                            closure_kit.get("currentReleaseAssetDiagnostics")
                            if isinstance(closure_kit.get("currentReleaseAssetDiagnostics"), dict)
                            else {}
                        )
                        if not diagnostics:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-diagnostics-missing",
                                evidence=f"{path_name} release asset closure kit has no currentReleaseAssetDiagnostics",
                                recommendation="Mirror downloaded asset status, paths, local asset list, consumer report status, and errors into currentReleaseAssetDiagnostics.",
                            )
                        else:
                            source_status = str(source_assets.get("status") or "")
                            if source_status and str(diagnostics.get("status") or "") != source_status:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-release-assets-diagnostics-status-drift",
                                    evidence=f"{path_name} release asset diagnostics status does not mirror publishedReleaseAssetProof.status",
                                    recommendation="Keep currentReleaseAssetDiagnostics.status aligned with publishedReleaseAssetProof.status.",
                                )
                        if not isinstance(closure_kit.get("repairCriteria"), list) or len(closure_kit.get("repairCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-repair-criteria-missing",
                                evidence=f"{path_name} release asset closure kit does not list repair criteria",
                                recommendation="Tell maintainers to download/supply public release assets, verify every required asset is present, and rerun stable-publication.",
                            )
                        if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-pass-criteria-missing",
                                evidence=f"{path_name} release asset closure kit does not list pass criteria",
                                recommendation="List concrete pass criteria for public release metadata, downloaded/supplied assets, and publishedReleaseAssetProof.status.",
                            )
                        if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-fail-criteria-missing",
                                evidence=f"{path_name} release asset closure kit does not list fail criteria",
                                recommendation="List fail cases such as missing downloaded assets, missing release metadata assets, wrong tag/repo/version, and source-only or fixture proof misuse.",
                            )
                        if "--download-release-assets" not in str(closure_kit.get("downloadAssetsRerunCommand") or item.get("downloadAssetsRerunCommand") or item.get("nextCommand") or "") and "--release-assets" not in str(closure_kit.get("downloadAssetsRerunCommand") or item.get("downloadAssetsRerunCommand") or item.get("nextCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-rerun-command-missing",
                                evidence=f"{path_name} release asset closure kit lacks the download/supplied-assets rerun command",
                                recommendation="Attach a stable-publication command that either downloads release assets or points to the supplied downloaded asset directory.",
                            )
                        if "stable-publication" not in str(closure_kit.get("stablePublicationRerunCommand") or item.get("stablePublicationRerunCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-full-rerun-command-missing",
                                evidence=f"{path_name} release asset closure kit lacks the full stable-publication rerun command",
                                recommendation="Attach the full stable-publication command to run after release assets are available.",
                            )
                        boundary = (
                            closure_kit.get("releaseAssetProofBoundary")
                            if isinstance(closure_kit.get("releaseAssetProofBoundary"), dict)
                            else {}
                        )
                        if (
                            boundary.get("downloadedOrSuppliedAssetsRequired") is not True
                            or boundary.get("githubMetadataOnlyCountsAsReleaseAssetProof") is not False
                            or boundary.get("sourceOnlyProofCountsAsReleaseAssetProof") is not False
                            or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
                        ):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-boundary-missing",
                                evidence=f"{path_name} release asset closure kit does not state the downloaded/supplied-assets, metadata-only, source-only, and fixture-proof boundaries",
                                recommendation="State that only actual downloaded or supplied public release assets satisfy this gate; metadata-only, source-only, and fixture proof do not.",
                            )
                        if "Release Asset Closure Kit" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-assets-closure-kit-markdown-missing",
                                evidence=f"{path_name} Markdown does not render the release asset closure kit",
                                recommendation="Render required assets, metadata/local missing assets, download status/source, paths, repair/pass/fail criteria, rerun commands, and proof boundaries in Markdown.",
                            )
                if item.get("id") == "post-release-consumer-proof":
                    source_consumer = (
                        report.get("postReleaseConsumerProof")
                        if isinstance(report.get("postReleaseConsumerProof"), dict)
                        else {}
                    )
                    closure_kit = (
                        item.get("postReleaseConsumerClosureKit")
                        if isinstance(item.get("postReleaseConsumerClosureKit"), dict)
                        else {}
                    )
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-post-release-consumer-closure-kit-missing",
                            evidence=f"{path_name} post-release-consumer-proof closure item has no postReleaseConsumerClosureKit",
                            recommendation="Attach a post-release consumer closure kit with release-consume paths, missing proof artifacts, digest/replay/attestation statuses, repair/pass criteria, release-consume rerun, stable-publication rerun, and source-only/fixture-proof boundaries.",
                        )
                    else:
                        missing_artifacts = (
                            closure_kit.get("missingProofArtifacts")
                            if isinstance(closure_kit.get("missingProofArtifacts"), list)
                            else []
                        )
                        if not closure_kit.get("consumerReportPath") and "consumer-report.json" not in missing_artifacts:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-report-path-or-missing-artifact-missing",
                                evidence=f"{path_name} post-release consumer closure kit hides the consumer report path and does not list it as missing",
                                recommendation="Expose consumerReportPath when release-consume ran, or list consumer-report.json in missingProofArtifacts when it did not.",
                            )
                        if not closure_kit.get("assetDigestMatrixPath") and "asset-digests.json" not in missing_artifacts:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-digest-path-or-missing-artifact-missing",
                                evidence=f"{path_name} post-release consumer closure kit hides the asset digest matrix path and does not list it as missing",
                                recommendation="Expose assetDigestMatrixPath when release-consume ran, or list asset-digests.json in missingProofArtifacts when it did not.",
                            )
                        if not closure_kit.get("consumerReportStatus"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-status-missing",
                                evidence=f"{path_name} post-release consumer closure kit omits consumerReportStatus",
                                recommendation="Mirror consumerReportStatus so maintainers know whether release-consume produced a pass, blocked, missing, or malformed report.",
                            )
                        digest = (
                            closure_kit.get("consumerDigestFreshness")
                            if isinstance(closure_kit.get("consumerDigestFreshness"), dict)
                            else {}
                        )
                        if not digest:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-digest-freshness-missing",
                                evidence=f"{path_name} post-release consumer closure kit hides the asset digest freshness summary",
                                recommendation="Expose consumerDigestFreshness with required asset rows, missing required assets, missing SHA-256 rows, tarball digest comparison, and problems from asset-digests.json.",
                            )
                        else:
                            if not digest.get("status") or not isinstance(digest.get("requiredAssetNames"), list):
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-post-release-consumer-digest-freshness-status-missing",
                                    evidence=f"{path_name} post-release consumer digest freshness lacks status or requiredAssetNames",
                                    recommendation="Include digest freshness status and requiredAssetNames from asset-digests.json.",
                                )
                            if not isinstance(digest.get("missingRequiredAssetNames"), list) or not isinstance(digest.get("missingSha256AssetNames"), list):
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-post-release-consumer-digest-problems-missing",
                                    evidence=f"{path_name} post-release consumer digest freshness lacks missing asset/SHA-256 lists",
                                    recommendation="List missing required asset names and present assets missing SHA-256 values so release-consume problems are actionable.",
                                )
                            if "releaseTarballDigestMatchesConsumerArtifact" not in digest:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-post-release-consumer-tarball-digest-match-missing",
                                    evidence=f"{path_name} post-release consumer digest freshness does not compare the release tarball digest with the consumer artifact SHA-256",
                                    recommendation="Record releaseTarballDigestMatchesConsumerArtifact as true, false, or null when comparison is impossible.",
                                )
                        crosschecks = (
                            closure_kit.get("publishedCrosschecks")
                            if isinstance(closure_kit.get("publishedCrosschecks"), dict)
                            else {}
                        )
                        if not closure_kit.get("replayStatus") or not closure_kit.get("attestationStatus") or not crosschecks:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-crosschecks-missing",
                                evidence=f"{path_name} post-release consumer closure kit omits replay, attestation, or published crosscheck statuses",
                                recommendation="Expose replayStatus, attestationStatus, and published replay/attestation/badge crosschecks from release-consume.",
                            )
                        diagnostics = (
                            closure_kit.get("currentConsumerDiagnostics")
                            if isinstance(closure_kit.get("currentConsumerDiagnostics"), dict)
                            else {}
                        )
                        if not diagnostics:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-diagnostics-missing",
                                evidence=f"{path_name} post-release consumer closure kit has no currentConsumerDiagnostics",
                                recommendation="Mirror release-consume status, command, paths, exit code, missing artifacts, and errors into currentConsumerDiagnostics.",
                            )
                        else:
                            source_status = str(source_consumer.get("status") or "")
                            if source_status and str(diagnostics.get("status") or "") != source_status:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-post-release-consumer-diagnostics-status-drift",
                                    evidence=f"{path_name} post-release consumer diagnostics status does not mirror postReleaseConsumerProof.status",
                                    recommendation="Keep currentConsumerDiagnostics.status aligned with postReleaseConsumerProof.status.",
                                )
                        if not isinstance(closure_kit.get("repairCriteria"), list) or len(closure_kit.get("repairCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-repair-criteria-missing",
                                evidence=f"{path_name} post-release consumer closure kit does not list repair criteria",
                                recommendation="Tell maintainers to download/supply release assets, rerun release-consume, repair missing assets or digest proof, then rerun stable-publication.",
                            )
                        if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 4:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-pass-criteria-missing",
                                evidence=f"{path_name} post-release consumer closure kit does not list pass criteria",
                                recommendation="List concrete pass criteria for release-consume exit code, consumer report, asset digest matrix, replay/attestation proof, and stable-publication status.",
                            )
                        if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 4:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-fail-criteria-missing",
                                evidence=f"{path_name} post-release consumer closure kit does not list fail criteria",
                                recommendation="List fail cases such as missing assets, non-pass consumer report, missing digest matrix, replay/attestation mismatch, and source-only proof misuse.",
                            )
                        if "release-consume" not in str(closure_kit.get("releaseConsumeRerunCommand") or item.get("releaseConsumeRerunCommand") or item.get("nextCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-rerun-command-missing",
                                evidence=f"{path_name} post-release consumer closure kit lacks the release-consume rerun command",
                                recommendation="Attach the exact release-consume command or a release-consume template when assets were not supplied.",
                            )
                        if "stable-publication" not in str(closure_kit.get("stablePublicationRerunCommand") or item.get("stablePublicationRerunCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-full-rerun-command-missing",
                                evidence=f"{path_name} post-release consumer closure kit lacks the full stable-publication rerun command",
                                recommendation="Attach the full stable-publication command to run after release-consume passes.",
                            )
                        boundary = (
                            closure_kit.get("consumerProofBoundary")
                            if isinstance(closure_kit.get("consumerProofBoundary"), dict)
                            else {}
                        )
                        if (
                            boundary.get("releaseConsumeRequired") is not True
                            or boundary.get("assetDigestMatrixMustCoverRequiredAssets") is not True
                            or boundary.get("releaseTarballDigestMustMatchConsumerArtifact") is not True
                            or boundary.get("sourceOnlyProofCountsAsConsumerProof") is not False
                            or boundary.get("fixtureProofCountsAsStableV4PublicationProof") is not False
                        ):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-boundary-missing",
                                evidence=f"{path_name} post-release consumer closure kit does not state the release-consume/digest/source-only/fixture-proof boundary",
                                recommendation="State that release-consume over downloaded or supplied assets is required, the digest matrix must cover required assets, tarball digest must match the consumer artifact, source-only proof cannot satisfy post-release consumer proof, and fixture proof cannot satisfy stable-v4 publication proof.",
                            )
                        if "Post-Release Consumer Closure Kit" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-closure-kit-markdown-missing",
                                evidence=f"{path_name} Markdown does not render the post-release consumer closure kit",
                                recommendation="Render release-consume paths, missing artifacts, statuses, repair/pass/fail criteria, rerun commands, and proof boundaries in Markdown.",
                            )
                        if "Digest freshness status" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-post-release-consumer-digest-markdown-missing",
                                evidence=f"{path_name} Markdown does not render digest freshness status",
                                recommendation="Render digest freshness status, required asset rows, missing required assets, missing SHA-256 rows, and tarball digest comparison in Markdown.",
                            )
                if item.get("id") == "public-release-freshness":
                    source_freshness = (
                        report.get("publicReleaseFreshnessProof")
                        if isinstance(report.get("publicReleaseFreshnessProof"), dict)
                        else {}
                    )
                    closure_kit = (
                        item.get("releaseFreshnessClosureKit")
                        if isinstance(item.get("releaseFreshnessClosureKit"), dict)
                        else {}
                    )
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-freshness-closure-kit-missing",
                            evidence=f"{path_name} public-release-freshness closure item has no releaseFreshnessClosureKit",
                            recommendation="Attach a freshness closure kit with public tag target, release manifest commit, release target, timestamp comparisons, repair/pass/fail criteria, rerun command, and source/fixture boundaries.",
                        )
                    else:
                        if not closure_kit.get("releaseTag") or not closure_kit.get("tagTargetSha"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-tag-target-missing",
                                evidence=f"{path_name} freshness closure kit omits release tag or public tag target SHA",
                                recommendation="Expose the selected release tag and resolved GitHub tag target SHA so stale tags are visible.",
                            )
                        if not closure_kit.get("releaseManifestPath") or not closure_kit.get("manifestCommit"):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-manifest-missing",
                                evidence=f"{path_name} freshness closure kit omits release manifest path or manifest commit",
                                recommendation="Expose release-manifest.json and its commit so public metadata can be compared to the published asset packet.",
                            )
                        comparisons = (
                            closure_kit.get("comparisons")
                            if isinstance(closure_kit.get("comparisons"), dict)
                            else {}
                        )
                        for comparison_key in (
                            "manifestVersionMatchesRequested",
                            "manifestTagMatchesMetadataTag",
                            "tagTargetMatchesManifestCommit",
                            "manifestGeneratedNoLaterThanPublishedAt",
                        ):
                            if comparison_key not in comparisons:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-release-freshness-comparison-missing",
                                    evidence=f"{path_name} freshness closure kit omits comparison `{comparison_key}`",
                                    recommendation="Render the freshness comparison matrix so maintainers can see whether version, tag, commit, and timestamps agree.",
                                )
                                break
                        diagnostics = (
                            closure_kit.get("currentFreshnessDiagnostics")
                            if isinstance(closure_kit.get("currentFreshnessDiagnostics"), dict)
                            else {}
                        )
                        if not diagnostics:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-diagnostics-missing",
                                evidence=f"{path_name} freshness closure kit has no currentFreshnessDiagnostics",
                                recommendation="Mirror public tag target, release manifest, metadata target, timestamp comparisons, and freshness problems into currentFreshnessDiagnostics.",
                            )
                        else:
                            source_status = str(source_freshness.get("status") or "")
                            if source_status and str(diagnostics.get("status") or "") != source_status:
                                add_issue(
                                    issues,
                                    severity="review",
                                    rule_id="stable-publication-release-freshness-diagnostics-status-drift",
                                    evidence=f"{path_name} freshness diagnostics status does not mirror publicReleaseFreshnessProof.status",
                                    recommendation="Keep currentFreshnessDiagnostics.status aligned with publicReleaseFreshnessProof.status.",
                                )
                        if not isinstance(closure_kit.get("repairCriteria"), list) or len(closure_kit.get("repairCriteria") or []) < 3:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-repair-criteria-missing",
                                evidence=f"{path_name} freshness closure kit does not list repair criteria",
                                recommendation="Tell maintainers how to repair stale tags, stale release assets, manifest commits, and rerun stable-publication.",
                            )
                        if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 5:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-pass-criteria-missing",
                                evidence=f"{path_name} freshness closure kit does not list pass criteria",
                                recommendation="List concrete pass criteria for tag target, release manifest, metadata target, version/tag match, and timestamp freshness.",
                            )
                        if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 5:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-fail-criteria-missing",
                                evidence=f"{path_name} freshness closure kit does not list fail criteria",
                                recommendation="List fail cases such as unresolved tag target, missing manifest, commit mismatch, timestamp inversion, and source-only/fixture proof misuse.",
                            )
                        if "stable-publication" not in str(closure_kit.get("freshnessRerunCommand") or item.get("freshnessRerunCommand") or item.get("nextCommand") or ""):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-rerun-command-missing",
                                evidence=f"{path_name} freshness closure kit lacks the stable-publication rerun command",
                                recommendation="Attach the full stable-publication command to rerun after public release metadata, tag target, or assets are repaired.",
                            )
                        boundary = (
                            closure_kit.get("freshnessProofBoundary")
                            if isinstance(closure_kit.get("freshnessProofBoundary"), dict)
                            else {}
                        )
                        if (
                            boundary.get("publicGitHubTagTargetRequired") is not True
                            or boundary.get("releaseManifestRequired") is not True
                            or boundary.get("releaseManifestCommitMustMatchPublicTagTarget") is not True
                            or boundary.get("sourceOnlyProofCountsAsFreshnessProof") is not False
                            or boundary.get("fixtureApiProofCountsAsStableV4PublicationProof") is not False
                        ):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-boundary-missing",
                                evidence=f"{path_name} freshness closure kit does not state the public tag, manifest, source-only, and fixture-proof boundaries",
                                recommendation="State that public tag target plus release manifest proof is required and source-only or fixture API proof cannot satisfy stable-v4 freshness.",
                            )
                        if "Public Release Freshness Closure Kit" not in markdown:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-freshness-closure-kit-markdown-missing",
                                evidence=f"{path_name} Markdown does not render the public release freshness closure kit",
                                recommendation="Render release tag, tag target, manifest commit, freshness comparisons, problems, criteria, rerun command, and proof boundaries in Markdown.",
                            )
                if item.get("id") == "release-notes":
                    release_notes_proof = report.get("releaseNotesProof") if isinstance(report.get("releaseNotesProof"), dict) else {}
                    proof_missing_topics = release_notes_proof.get("missingTopicIds")
                    item_missing_topics = item.get("missingTopicIds")
                    if isinstance(proof_missing_topics, list) and item_missing_topics != proof_missing_topics:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-missing-topics",
                            evidence=f"{path_name} release-notes closure item does not mirror releaseNotesProof.missingTopicIds",
                            recommendation="Copy releaseNotesProof.missingTopicIds onto the release-notes closure item so maintainers can close the first blocker without opening nested JSON.",
                        )
                    authoring_paths = item.get("authoringKitPaths")
                    expected_note_paths = {
                        "stable-publication-release-notes/README.md",
                        "stable-publication-release-notes/release-notes-checklist.json",
                        "stable-publication-release-notes/draft-release-notes.md",
                    }
                    actual_note_paths = set(str(path) for path in authoring_paths) if isinstance(authoring_paths, list) else set()
                    if not expected_note_paths <= actual_note_paths:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-authoring-paths-missing",
                            evidence=f"{path_name} release-notes closure item does not list every generated authoring-kit path",
                            recommendation="Attach README, checklist, and draft release-notes paths to the release-notes closure item.",
                        )
                    notes_kit_for_closure = (
                        report.get("stablePublicationReleaseNotesAuthoringKit")
                        if isinstance(report.get("stablePublicationReleaseNotesAuthoringKit"), dict)
                        else {}
                    )
                    kit_edit_command = str(notes_kit_for_closure.get("publicReleaseEditCommand") or "")
                    if "gh release edit" in kit_edit_command and "--notes-file" in kit_edit_command:
                        generated_paths = notes_kit_for_closure.get("generatedPaths")
                        generated_values = set(str(value) for value in generated_paths.values()) if isinstance(generated_paths, dict) else set()
                        generated_files = notes_kit_for_closure.get("files")
                        generated_values.update(
                            str(file_item.get("generatedPath"))
                            for file_item in (generated_files if isinstance(generated_files, list) else [])
                            if isinstance(file_item, dict) and file_item.get("generatedPath")
                        )
                        if not all(any(value.endswith(expected) for value in generated_values) for expected in expected_note_paths):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="stable-publication-release-notes-generated-paths-missing",
                                evidence=f"{path_name} release-notes authoring kit exposes an edit command but not generated output paths",
                                recommendation="Expose generatedPaths and per-file generatedPath values for README, checklist, and draft release notes so copy/paste commands can be audited from the report.",
                            )
                    edit_boundary = (
                        item.get("publicGitHubReleaseEditBoundary")
                        if isinstance(item.get("publicGitHubReleaseEditBoundary"), dict)
                        else {}
                    )
                    if edit_boundary.get("requiresPublicReleaseEdit") is not True or edit_boundary.get("shipguardDoesNotEditRelease") is not True:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-edit-boundary-missing",
                            evidence=f"{path_name} release-notes closure item does not expose the public GitHub release edit boundary",
                            recommendation="State that ShipGuard generated a draft-only kit and the maintainer must edit the public GitHub release body before rerunning stable-publication.",
                        )
                    edit_command = str(edit_boundary.get("publicReleaseEditCommand") or "")
                    if int(notes_kit_for_closure.get("schemaVersion") or 1) >= 2 and (
                        not edit_command
                        or item.get("nextCommand") != edit_command
                        or "gh release edit" not in str(item.get("nextCommand") or "")
                    ):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-next-command-missing",
                            evidence=f"{path_name} release-notes closure nextCommand does not point at the GitHub release edit command",
                            recommendation="Set the release-notes closure nextCommand to publicGitHubReleaseEditBoundary.publicReleaseEditCommand, and keep rerunCommand for after the edit.",
                        )
                    if "stable-publication" not in str(item.get("rerunCommand") or ""):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-rerun-command-missing",
                            evidence=f"{path_name} release-notes closure item has no exact stable-publication rerun command",
                            recommendation="Attach the stable-publication rerun command to the release-notes closure item.",
                        )
                    if "Release Notes Closure Kit" not in markdown:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="stable-publication-release-notes-closure-markdown-missing",
                            evidence=f"{path_name} Markdown does not render the release-notes closure kit",
                            recommendation="Render missing topics, authoring-kit paths, public edit boundary, and rerun command in Markdown.",
                        )
                if item.get("id") in {"independent-adoption-evidence", "final-security-review-evidence"}:
                    evidence_id = str(item.get("id"))
                    expected = {
                        "independent-adoption-evidence": {
                            "starterPath": "stable-publication-evidence-kit/external-adoption-evidence.json",
                            "templatePath": "templates/stable-publication/external-adoption-evidence.template.json",
                            "classes": {"public-external", "private-redacted-external"},
                        },
                        "final-security-review-evidence": {
                            "starterPath": "stable-publication-evidence-kit/security-review-evidence.json",
                            "templatePath": "templates/stable-publication/security-review-evidence.template.json",
                            "classes": {"public-security-review", "private-redacted-security-review"},
                        },
                    }[evidence_id]
                    closure_kit = item.get("evidenceClosureKit") if isinstance(item.get("evidenceClosureKit"), dict) else {}
                    if not closure_kit:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` has no evidenceClosureKit",
                            recommendation="Attach a per-blocker closure kit with starter path, template path, required fields, redaction/privacy boundaries, pass/fail criteria, diagnostics, and rerun command.",
                        )
                        continue
                    if closure_kit.get("starterPath") != expected["starterPath"] or closure_kit.get("templatePath") != expected["templatePath"]:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-paths-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not expose the expected starter/template paths",
                            recommendation="Put the generated starter evidence path and repo template path directly on the closure kit.",
                        )
                    accepted_classes = set(str(value) for value in closure_kit.get("acceptedEvidenceClasses", [])) if isinstance(closure_kit.get("acceptedEvidenceClasses"), list) else set()
                    if not expected["classes"] <= accepted_classes:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-classes-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not list the accepted stable-v4 evidence classes",
                            recommendation="List accepted evidenceClass values so maintainers know what record shape can pass the gate.",
                        )
                    if not isinstance(closure_kit.get("requiredFields"), list) or len(closure_kit.get("requiredFields") or []) < 5:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-required-fields-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not list required evidence fields",
                            recommendation="Expose the required JSON fields directly on the closure kit.",
                        )
                    redaction_boundary = closure_kit.get("redactionBoundary") if isinstance(closure_kit.get("redactionBoundary"), dict) else {}
                    privacy_boundary = closure_kit.get("privacyBoundary") if isinstance(closure_kit.get("privacyBoundary"), dict) else {}
                    if redaction_boundary.get("privateDataRedactedMustBeTrue") is not True or not privacy_boundary:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-boundaries-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not expose redaction and privacy boundaries",
                            recommendation="State the redaction/privacy boundary on the closure kit so private paths, app identifiers, screenshots, tokens, and account data cannot leak into shareable proof.",
                        )
                    if not isinstance(closure_kit.get("passCriteria"), list) or len(closure_kit.get("passCriteria") or []) < 3:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-pass-criteria-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not list pass criteria",
                            recommendation="List concrete pass criteria so maintainers know exactly when the evidence can satisfy stable publication.",
                        )
                    if not isinstance(closure_kit.get("failCriteria"), list) or len(closure_kit.get("failCriteria") or []) < 3:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-fail-criteria-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not list fail criteria",
                            recommendation="List common fail cases such as unchanged templates, missing redaction, fixture evidence, and private-data leakage.",
                        )
                    if "stable-publication" not in str(closure_kit.get("rerunCommand") or item.get("rerunCommand") or ""):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-rerun-command-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` has no exact stable-publication rerun command",
                            recommendation="Attach the stable-publication command to rerun after real adoption/security evidence is attached.",
                        )
                    if not isinstance(closure_kit.get("currentEvidenceDiagnostics"), dict):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-diagnostics-missing",
                            evidence=f"{path_name} closure item `{evidence_id}` does not show current evidence diagnostics",
                            recommendation="Mirror the current gate status, record counts, first error, and relevant missing scope/fields into the closure kit.",
                        )
                    if f"Evidence Closure Kit: `{evidence_id}`" not in markdown:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id=f"stable-publication-{evidence_id}-closure-kit-markdown-missing",
                            evidence=f"{path_name} Markdown does not render the `{evidence_id}` closure kit",
                            recommendation="Render starter path, required fields, privacy boundary, pass/fail criteria, diagnostics, and rerun command in Markdown.",
                        )
    if "Closure Checklist" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-closure-checklist-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication closure checklist",
            recommendation="Render the closure checklist in Markdown so maintainers can see every remaining blocker without opening JSON.",
        )

    freshness_proofs = [
        ("independent-adoption-evidence", report.get("externalAdoptionEvidenceProof")),
        ("final-security-review-evidence", report.get("securityReviewEvidenceProof")),
    ]
    freshness_present = False
    for evidence_id, proof in freshness_proofs:
        proof = proof if isinstance(proof, dict) else {}
        freshness = proof.get("evidencePacketFreshness") if isinstance(proof.get("evidencePacketFreshness"), dict) else {}
        if freshness:
            freshness_present = True
        if report.get("stableV4Release") is True and not freshness:
            add_issue(
                issues,
                severity="review",
                rule_id=f"stable-publication-{evidence_id}-freshness-missing",
                evidence=f"{path_name} claims stableV4Release=true but `{evidence_id}` has no evidencePacketFreshness",
                recommendation="Compare adoption/security record generatedAt timestamps against the release manifest timestamp before allowing a stable-v4 claim.",
            )
            continue
        if freshness and report.get("stableV4Release") is True and freshness.get("status") != "pass":
            add_issue(
                issues,
                severity="review",
                rule_id=f"stable-publication-{evidence_id}-freshness-not-pass",
                evidence=f"{path_name} claims stableV4Release=true but `{evidence_id}` freshness is {freshness.get('status')}",
                recommendation="Block stable-v4 claims until external evidence records are generated for the release being published.",
            )
        boundary = freshness.get("freshnessBoundary") if isinstance(freshness.get("freshnessBoundary"), dict) else {}
        if freshness and boundary.get("generatedAtMustBeNoEarlierThanReleaseManifest") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id=f"stable-publication-{evidence_id}-freshness-boundary-missing",
                evidence=f"{path_name} `{evidence_id}` freshness does not expose the generatedAt release-manifest boundary",
                recommendation="State that external evidence generatedAt must be no earlier than the release manifest timestamp and cannot be refreshed by source-only, fixture, or local package proof.",
            )
    if freshness_present and "External Evidence Freshness" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-external-evidence-freshness-markdown-missing",
            evidence=f"{path_name} has external evidence freshness data but Markdown does not render it",
            recommendation="Render external adoption and security-review freshness status in Markdown so stale evidence cannot hide in JSON.",
        )

    version_coherence = (
        report.get("releaseVersionCoherenceProof")
        if isinstance(report.get("releaseVersionCoherenceProof"), dict)
        else {}
    )
    if report.get("stableV4Release") is True and not version_coherence:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-version-coherence-missing",
            evidence=f"{path_name} claims stableV4Release=true but has no releaseVersionCoherenceProof",
            recommendation="Compare VERSION, GitHub release metadata, release-manifest.json, package proof, and consumer report version before allowing stable-v4 claims.",
        )
    if version_coherence:
        comparisons = (
            version_coherence.get("comparisons")
            if isinstance(version_coherence.get("comparisons"), dict)
            else {}
        )
        if report.get("stableV4Release") is True and version_coherence.get("status") != "pass":
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-version-coherence-not-pass",
                evidence=f"{path_name} claims stableV4Release=true but releaseVersionCoherenceProof is {version_coherence.get('status')}",
                recommendation="Block stable-v4 claims until every version/tag/package/manifest comparison passes.",
            )
        for comparison_key in (
            "sourceVersionMatchesRequested",
            "metadataReturnedTagMatchesRequested",
            "manifestVersionMatchesRequested",
            "packageVersionMatchesRequested",
            "consumerReportVersionMatchesRequested",
        ):
            if comparison_key not in comparisons:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-version-coherence-comparison-missing",
                    evidence=f"{path_name} releaseVersionCoherenceProof omits comparison `{comparison_key}`",
                    recommendation="Expose a version coherence matrix covering VERSION, GitHub metadata, release manifest, package proof, and consumer report version.",
                )
                break
        boundary = (
            version_coherence.get("versionCoherenceBoundary")
            if isinstance(version_coherence.get("versionCoherenceBoundary"), dict)
            else {}
        )
        if boundary.get("versionMustMatchAcrossSourceMetadataManifestPackageAndConsumerProof") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-version-coherence-boundary-missing",
                evidence=f"{path_name} releaseVersionCoherenceProof does not expose the stable-v4 version boundary",
                recommendation="State that version metadata must match across source, GitHub metadata, release manifest, package proof, and consumer proof before stable-v4 claims are allowed.",
            )
        if "Release Version Coherence" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-version-coherence-markdown-missing",
                evidence=f"{path_name} has releaseVersionCoherenceProof but Markdown does not render it",
                recommendation="Render the version coherence matrix in Markdown so mismatched versions cannot hide in JSON.",
            )

    asset_coherence = (
        report.get("releaseAssetCoherenceProof")
        if isinstance(report.get("releaseAssetCoherenceProof"), dict)
        else {}
    )
    if report.get("stableV4Release") is True and not asset_coherence:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-asset-coherence-missing",
            evidence=f"{path_name} claims stableV4Release=true but has no releaseAssetCoherenceProof",
            recommendation="Compare required asset names and SHA-256 values across GitHub metadata, downloaded assets, release manifest, asset-digests.json, and consumer proof before allowing stable-v4 claims.",
        )
    if asset_coherence:
        comparisons = (
            asset_coherence.get("comparisons")
            if isinstance(asset_coherence.get("comparisons"), dict)
            else {}
        )
        if report.get("stableV4Release") is True and asset_coherence.get("status") != "pass":
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-asset-coherence-not-pass",
                evidence=f"{path_name} claims stableV4Release=true but releaseAssetCoherenceProof is {asset_coherence.get('status')}",
                recommendation="Block stable-v4 claims until release asset names and SHA-256 values agree across the published packet.",
            )
        for comparison_key in (
            "localAssetsCoverRequired",
            "digestAssetsCoverRequired",
            "expectedTarballInLocalAssets",
            "manifestArtifactShaMatchesDigestTarball",
            "consumerArtifactShaMatchesDigestTarball",
        ):
            if comparison_key not in comparisons:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-asset-coherence-comparison-missing",
                    evidence=f"{path_name} releaseAssetCoherenceProof omits comparison `{comparison_key}`",
                    recommendation="Expose an asset coherence matrix covering required assets, local assets, digest rows, manifest artifact, and consumer artifact SHA-256.",
                )
                break
        boundary = (
            asset_coherence.get("assetCoherenceBoundary")
            if isinstance(asset_coherence.get("assetCoherenceBoundary"), dict)
            else {}
        )
        if (
            boundary.get("downloadedOrSuppliedAssetsRequired") is not True
            or boundary.get("assetDigestMatrixRequired") is not True
            or boundary.get("sourceOnlyProofCountsAsAssetCoherenceProof") is not False
            or boundary.get("metadataOnlyProofCountsAsAssetCoherenceProof") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-asset-coherence-boundary-missing",
                evidence=f"{path_name} releaseAssetCoherenceProof does not expose the stable-v4 asset proof boundary",
                recommendation="State that downloaded or supplied assets plus asset-digests.json are required and that source-only, metadata-only, or fixture proof cannot satisfy asset coherence.",
            )
        if "Release Asset Coherence" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-asset-coherence-markdown-missing",
                evidence=f"{path_name} has releaseAssetCoherenceProof but Markdown does not render it",
                recommendation="Render the asset coherence matrix in Markdown so mismatched release assets cannot hide in JSON.",
            )

    public_evidence = (
        report.get("publicEvidenceClosureProof")
        if isinstance(report.get("publicEvidenceClosureProof"), dict)
        else {}
    )
    if report.get("stableV4Release") is True and not public_evidence:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-public-evidence-closure-missing",
            evidence=f"{path_name} claims stableV4Release=true but has no publicEvidenceClosureProof",
            recommendation="Expose one copy-ready public evidence closure proof for adoption/security status, freshness, starter paths, rerun commands, and non-claims.",
        )
    if public_evidence:
        rows = public_evidence.get("evidenceRows") if isinstance(public_evidence.get("evidenceRows"), list) else []
        row_ids = {str(row.get("id")) for row in rows if isinstance(row, dict)}
        boundary = (
            public_evidence.get("publicEvidenceBoundary")
            if isinstance(public_evidence.get("publicEvidenceBoundary"), dict)
            else {}
        )
        if report.get("stableV4Release") is True and public_evidence.get("status") != "pass":
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-evidence-closure-not-pass",
                evidence=f"{path_name} claims stableV4Release=true but publicEvidenceClosureProof is {public_evidence.get('status')}",
                recommendation="Block stable-v4 claims until adoption and security evidence both pass and are fresh for the release manifest.",
            )
        if {"independent-adoption-evidence", "final-security-review-evidence"} - row_ids:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-evidence-closure-row-missing",
                evidence=f"{path_name} publicEvidenceClosureProof omits adoption or security evidence rows",
                recommendation="Summarize both independent adoption and final security-review evidence in the public closure proof.",
            )
        if (
            boundary.get("realExternalAdoptionEvidenceRequired") is not True
            or boundary.get("finalSecurityReviewEvidenceRequired") is not True
            or boundary.get("githubDownloadCountsCountAsAdoptionEvidence") is not False
            or boundary.get("fixtureEvidenceCountsAsStableV4Evidence") is not False
            or boundary.get("doesNotClaimMarketplaceAcceptance") is not True
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-evidence-closure-boundary-missing",
                evidence=f"{path_name} publicEvidenceClosureProof does not expose adoption/security non-claim boundaries",
                recommendation="State that real adoption and final security evidence are required, and that downloads, fixtures, source-only proof, marketplace acceptance, or posting claims do not count.",
            )
        if int(public_evidence.get("schemaVersion") or 1) >= 2:
            source_matrix = (
                public_evidence.get("sourceClassMatrix")
                if isinstance(public_evidence.get("sourceClassMatrix"), list)
                else []
            )
            matrix_by_id = {str(item.get("id") or ""): item for item in source_matrix if isinstance(item, dict)}
            adoption_matrix = matrix_by_id.get("independent-adoption-evidence") or {}
            security_matrix = matrix_by_id.get("final-security-review-evidence") or {}
            adoption_classes = set(str(value) for value in adoption_matrix.get("acceptedEvidenceClasses", []))
            adoption_relationships = set(str(value) for value in adoption_matrix.get("acceptedRelationships", []))
            adoption_rejections = set(str(value) for value in adoption_matrix.get("rejectedSubstitutes", []))
            security_classes = set(str(value) for value in security_matrix.get("acceptedEvidenceClasses", []))
            security_relationships = set(str(value) for value in security_matrix.get("acceptedRelationships", []))
            security_rejections = set(str(value) for value in security_matrix.get("rejectedSubstitutes", []))
            if not {"public-external", "private-redacted-external"} <= adoption_classes:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-adoption-source-class-matrix-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not list accepted adoption evidence classes",
                    recommendation="Expose public-external and private-redacted-external as the only stable adoption evidence classes.",
                )
            if adoption_matrix.get("requiredRelationshipField") != "actorRelationship" or "independent" not in adoption_relationships:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-adoption-relationship-matrix-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not expose the independent actor relationship requirement",
                    recommendation="Expose actorRelationship=independent so maintainer QA cannot be confused with adoption evidence.",
                )
            if not {"download counts", "maintainer-only private app runs", "fixtureSynthetic records", "stale generatedAt records"} <= adoption_rejections:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-adoption-rejected-substitutes-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not list rejected adoption substitutes",
                    recommendation="List download counts, maintainer-only runs, fixture records, and stale records as non-substitutes for independent adoption.",
                )
            if not {"public-security-review", "private-redacted-security-review"} <= security_classes:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-security-source-class-matrix-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not list accepted security-review evidence classes",
                    recommendation="Expose public-security-review and private-redacted-security-review as the only stable security-review evidence classes.",
                )
            if security_matrix.get("requiredRelationshipField") != "reviewerRelationship" or not {"independent", "maintainer-security-review"} <= security_relationships:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-security-relationship-matrix-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not expose accepted reviewer relationships",
                    recommendation="Expose reviewerRelationship values so security review evidence is not confused with adoption evidence.",
                )
            if not {"fixtureSynthetic records", "stale generatedAt records", "vague self-review notes", "open critical/high findings"} <= security_rejections:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-security-rejected-substitutes-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof does not list rejected security-review substitutes",
                    recommendation="List fixture records, stale records, vague self-review, and open critical/high findings as non-substitutes for final security proof.",
                )
            if source_matrix and "External Evidence Source-Class Matrix" not in markdown:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-source-class-matrix-markdown-missing",
                    evidence=f"{path_name} publicEvidenceClosureProof has sourceClassMatrix data but Markdown does not render it",
                    recommendation="Render accepted classes, relationship fields, rejected substitutes, and pass boundaries in Markdown.",
                )
        if not public_evidence.get("copyReadyCommands"):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-evidence-closure-command-missing",
                evidence=f"{path_name} publicEvidenceClosureProof has no copy-ready commands",
                recommendation="Include template-copy and stable-publication rerun commands so evidence closure is actionable from the report.",
            )
        if "Public Evidence Closure" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-evidence-closure-markdown-missing",
                evidence=f"{path_name} has publicEvidenceClosureProof but Markdown does not render it",
                recommendation="Render the public evidence closure proof in Markdown so adoption/security status and non-claims are visible without opening JSON.",
            )

    public_delta = (
        report.get("publicReleaseDeltaProof")
        if isinstance(report.get("publicReleaseDeltaProof"), dict)
        else {}
    )
    public_delta_expected = (
        report.get("stableV4Release") is True
        or bool(public_evidence)
        or isinstance(report.get("finalStableV4ClaimPacket"), dict)
        or any("public release delta proof" in normalized_question_text(question) for question in report.get("reportQualityQuestions", []))
    )
    if public_delta_expected and not public_delta:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-public-release-delta-missing",
            evidence=f"{path_name} has no publicReleaseDeltaProof",
            recommendation="Expose whether local main, latest GitHub release, package assets, and stable-publication claims are aligned before announcement copy.",
        )
    elif public_delta:
        comparisons = public_delta.get("comparisons") if isinstance(public_delta.get("comparisons"), dict) else {}
        boundary = public_delta.get("releaseDeltaBoundary") if isinstance(public_delta.get("releaseDeltaBoundary"), dict) else {}
        for comparison_key in (
            "selectedReleaseMatchesLatestGitHubRelease",
            "packageAssetsVersionMatchesRequestedRelease",
            "localHeadMatchesSelectedPublicReleaseCommit",
            "localMainMatchesSelectedPublicReleaseCommit",
            "releaseVersionCoherencePassed",
            "releaseAssetCoherencePassed",
        ):
            if comparison_key not in comparisons:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-public-release-delta-comparison-missing",
                    evidence=f"{path_name} publicReleaseDeltaProof omits comparison `{comparison_key}`",
                    recommendation="Expose a compact delta matrix for local source, latest GitHub release, package assets, and release claim scope.",
                )
                break
        if (
            boundary.get("latestPublicGitHubReleaseIsPublicationSource") is not True
            or boundary.get("localHeadIsNotPublicReleaseProof") is not True
            or boundary.get("localMainIsNotPublicReleaseProof") is not True
            or boundary.get("unpublishedLocalCodeCountsAsReleased") is not False
            or boundary.get("downloadedOrSuppliedAssetsAreRequiredForPackageTruth") is not True
            or boundary.get("stableV4ClaimCoversSelectedReleaseOnly") is not True
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-release-delta-boundary-missing",
                evidence=f"{path_name} publicReleaseDeltaProof does not make the unpublished-code/public-release boundary explicit",
                recommendation="State that the latest public GitHub release and downloaded assets are publication truth, while local HEAD/main are not release proof.",
            )
        if report.get("stableV4Release") is True and public_delta.get("stableV4ClaimCoversSelectedPublicRelease") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-release-delta-claim-scope-mismatch",
                evidence=f"{path_name} claims stableV4Release=true but publicReleaseDeltaProof does not cover the selected public release",
                recommendation="Only allow stable-v4 claim wording when the selected public release, latest GitHub release, package assets, version coherence, and asset coherence align.",
            )
        if "Public Release Delta" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-public-release-delta-markdown-missing",
                evidence=f"{path_name} has publicReleaseDeltaProof but Markdown does not render it",
                recommendation="Render the public-release delta in Markdown so unpublished local work cannot be mistaken for released code.",
            )

    visibility = (
        report.get("releaseVisibilityHandoff")
        if isinstance(report.get("releaseVisibilityHandoff"), dict)
        else {}
    )
    visibility_expected = (
        bool(public_delta)
        or report.get("stableV4Release") is True
        or any("release visibility handoff" in normalized_question_text(question) for question in report.get("reportQualityQuestions", []))
    )
    if visibility_expected and not visibility:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-release-visibility-handoff-missing",
            evidence=f"{path_name} has no releaseVisibilityHandoff",
            recommendation="Tell maintainers whether to publish a new GitHub release, update release notes/assets, attach adoption/security evidence, or keep the current public release unchanged.",
        )
    elif visibility:
        boundary = visibility.get("visibilityBoundary") if isinstance(visibility.get("visibilityBoundary"), dict) else {}
        actions = visibility.get("requiredActions") if isinstance(visibility.get("requiredActions"), list) else []
        action_ids = {str(action.get("id")) for action in actions if isinstance(action, dict)}
        required_ids = {
            "publish-new-github-release",
            "update-release-notes",
            "attach-launchkey-candidate-proof",
            "update-release-assets",
            "attach-adoption-security-evidence",
            "keep-current-public-release-unchanged",
        }
        if not visibility.get("primaryDecision") or not required_ids.issubset(action_ids):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-action-missing",
                evidence=f"{path_name} releaseVisibilityHandoff does not expose the full publication decision matrix",
                recommendation="Include primaryDecision plus action rows for release publication, notes, assets, adoption/security evidence, and keeping the current public release unchanged.",
            )
        for action in actions:
            if (
                isinstance(action, dict)
                and action.get("required") is False
                and action.get("status") == "pass"
                and str(action.get("nextCommand") or "") != "not-needed"
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-release-visibility-completed-action-command-noise",
                    evidence=f"{path_name} releaseVisibilityHandoff action `{action.get('id')}` is complete but still suggests `{action.get('nextCommand')}`",
                    recommendation="Set nextCommand to `not-needed` for pass/not-required release visibility actions so only real work rows carry commands.",
                )
            if (
                isinstance(action, dict)
                and action.get("id") == "keep-current-public-release-unchanged"
                and action.get("required") is False
                and action.get("status") == "blocked"
                and str(action.get("nextCommand") or "") != "blocked-by-required-actions"
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-release-visibility-keep-current-command-noise",
                    evidence=f"{path_name} releaseVisibilityHandoff keep-current row is blocked but still suggests `{action.get('nextCommand')}`",
                    recommendation="Set keep-current-public-release-unchanged.nextCommand to `blocked-by-required-actions` while earlier publication gates remain required.",
                )
            if isinstance(action, dict) and (
                not action.get("nextCommandPurpose") or not action.get("proofCommandAfterCompletion")
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-release-visibility-proof-after-action-missing",
                    evidence=f"{path_name} releaseVisibilityHandoff action `{action.get('id')}` hides command purpose or proof-after-action guidance",
                    recommendation="Add nextCommandPurpose and proofCommandAfterCompletion to every release visibility action row.",
                )
        notes_kit_for_visibility = (
            report.get("stablePublicationReleaseNotesAuthoringKit")
            if isinstance(report.get("stablePublicationReleaseNotesAuthoringKit"), dict)
            else {}
        )
        release_notes_proof_for_visibility = (
            report.get("releaseNotesProof")
            if isinstance(report.get("releaseNotesProof"), dict)
            else {}
        )
        if (
            int(notes_kit_for_visibility.get("schemaVersion") or 1) >= 2
            and (
                release_notes_proof_for_visibility.get("status") == "review"
                or notes_kit_for_visibility.get("status") == "review"
                or bool(notes_kit_for_visibility.get("missingTopicIds"))
            )
        ):
            update_notes_action = next(
                (action for action in actions if isinstance(action, dict) and action.get("id") == "update-release-notes"),
                {},
            )
            update_notes_command = str(update_notes_action.get("nextCommand") or "")
            expected_notes_command = str(notes_kit_for_visibility.get("publicReleaseEditCommand") or "")
            if (
                not expected_notes_command
                or update_notes_command != expected_notes_command
                or "gh release edit" not in update_notes_command
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-release-visibility-update-notes-command-missing",
                    evidence=f"{path_name} releaseVisibilityHandoff update-release-notes action does not point at the release-notes edit command",
                    recommendation="Set update-release-notes.nextCommand to stablePublicationReleaseNotesAuthoringKit.publicReleaseEditCommand.",
                )
        if (
            boundary.get("doesNotPublishRelease") is not True
            or boundary.get("doesNotEditGitHubRelease") is not True
            or boundary.get("doesNotPostExternally") is not True
            or boundary.get("latestPublicGitHubReleaseIsPublicationTruth") is not True
            or boundary.get("localHeadIsNotPublicationProof") is not True
            or boundary.get("localMainIsNotPublicationProof") is not True
            or boundary.get("unpublishedLocalCodeCountsAsReleased") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-boundary-missing",
                evidence=f"{path_name} releaseVisibilityHandoff weakens release/publication boundaries",
                recommendation="State that the handoff does not publish, edit releases, or post externally, and that local HEAD/main are not publication proof.",
            )
        if report.get("stableV4Release") is True and visibility.get("primaryDecision") != "announce-current-public-release":
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-decision-mismatch",
                evidence=f"{path_name} claims stableV4Release=true but releaseVisibilityHandoff does not announce the current public release",
                recommendation="When stable-v4 publication passes, the handoff should make the current public release the announcement target.",
            )
        delta_comparisons = public_delta.get("comparisons") if isinstance(public_delta.get("comparisons"), dict) else {}
        publication_mismatch = any(
            delta_comparisons.get(key) is not True
            for key in (
                "selectedReleaseMatchesLatestGitHubRelease",
                "publicTagTargetMatchesReleaseManifestCommit",
            )
        )
        if publication_mismatch:
            publish_action = next((action for action in actions if isinstance(action, dict) and action.get("id") == "publish-new-github-release"), {})
            if publish_action.get("required") is not True:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-release-visibility-publication-mismatch-hidden",
                    evidence=f"{path_name} has a selected/latest release or public tag/manifest mismatch but releaseVisibilityHandoff does not require publication action",
                    recommendation="Mark publish-new-github-release as required when the selected public release is not latest or its public tag target does not match the release manifest.",
                )
        if "Release Visibility Handoff" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-markdown-missing",
                evidence=f"{path_name} has releaseVisibilityHandoff but Markdown does not render it",
                recommendation="Render the release visibility handoff in Markdown so maintainers can choose the next public-release action without opening JSON.",
            )
        elif "Command purpose" not in markdown or "Proof after action" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-proof-after-action-markdown-missing",
                evidence=f"{path_name} Markdown renders releaseVisibilityHandoff but hides command purpose or proof-after-action guidance",
                recommendation="Render nextCommandPurpose and proofCommandAfterCompletion in the Release Visibility Handoff table.",
            )
        elif (
            int(notes_kit_for_visibility.get("schemaVersion") or 1) >= 2
            and (
                release_notes_proof_for_visibility.get("status") == "review"
                or notes_kit_for_visibility.get("status") == "review"
                or bool(notes_kit_for_visibility.get("missingTopicIds"))
            )
            and "update-release-notes" in markdown
            and "gh release edit" not in markdown
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-visibility-update-notes-markdown-missing",
                evidence=f"{path_name} Markdown renders releaseVisibilityHandoff but hides the update-release-notes edit command",
                recommendation="Render action-level next commands in the Release Visibility Handoff table.",
            )

    final_claim = (
        report.get("finalStableV4ClaimPacket")
        if isinstance(report.get("finalStableV4ClaimPacket"), dict)
        else {}
    )
    final_claim_expected = (
        report.get("stableV4Release") is True
        or bool(public_evidence)
        or any("final stable-v4 claim packet" in normalized_question_text(question) for question in report.get("reportQualityQuestions", []))
    )
    if final_claim_expected and not final_claim:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-final-claim-packet-missing",
            evidence=f"{path_name} has no finalStableV4ClaimPacket",
            recommendation="Emit one final claim packet with copy-ready allowed/blocked wording, evidence rows, next command, approval boundary, and non-claims.",
        )
    elif final_claim:
        boundary = final_claim.get("claimBoundary") if isinstance(final_claim.get("claimBoundary"), dict) else {}
        approval = final_claim.get("approvalBoundary") if isinstance(final_claim.get("approvalBoundary"), dict) else {}
        readiness = (
            final_claim.get("claimPublicationReadiness")
            if isinstance(final_claim.get("claimPublicationReadiness"), dict)
            else {}
        )
        evidence_summary = final_claim.get("evidenceSummary") if isinstance(final_claim.get("evidenceSummary"), list) else []
        expected_decision = "allowed" if report.get("stableV4Release") is True else "blocked"
        if final_claim.get("claimDecision") != expected_decision or final_claim.get("stableV4Release") is not report.get("stableV4Release"):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-decision-mismatch",
                evidence=f"{path_name} finalStableV4ClaimPacket does not match stableV4Release={report.get('stableV4Release')}",
                recommendation="Set the final claim decision from the stable-publication status so blocked reports cannot emit allowed v4 wording.",
            )
        if (
            readiness.get("stableV4ClaimMayBePublished") is not (expected_decision == "allowed")
            or readiness.get("explicitHumanApprovalRequiredForPosting") is not True
            or readiness.get("computerUseMayPost") is not False
            or (expected_decision == "blocked" and not readiness.get("firstBlockingGateId"))
            or (expected_decision == "blocked" and not readiness.get("nextCommand"))
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-readiness-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket lacks a consistent claimPublicationReadiness gate",
                recommendation="Expose claimPublicationReadiness with publishable status, first blocker, next command, and explicit human-approval/computer-use posting boundaries.",
            )
        if not final_claim.get("copyReadyClaim") or not isinstance(final_claim.get("blockedClaims"), list) or not final_claim.get("blockedClaims"):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-wording-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket lacks copy-ready wording or blocked claims",
                recommendation="Include explicit wording the maintainer may say now and wording they must not say.",
            )
        if len(evidence_summary) < len(required_rows):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-evidence-summary-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket does not mirror required evidence rows",
                recommendation="Mirror stablePublicationEvidencePacket.requiredEvidence into the final claim packet so every claim maps back to proof status.",
            )
        if expected_decision == "blocked" and not final_claim.get("nextCommand"):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-next-command-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket is blocked without a next command",
                recommendation="Carry the first blocker or stable-publication rerun command into the final claim packet.",
            )
        allowed_claims = final_claim.get("allowedClaims") if isinstance(final_claim.get("allowedClaims"), list) else []
        if expected_decision == "blocked" and allowed_claims:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-allowed-claims-while-blocked",
                evidence=f"{path_name} finalStableV4ClaimPacket is blocked but still lists allowed claims",
                recommendation="Keep allowedClaims empty until stableV4Release is true; put progress context in copyReadyClaim or blockedClaims.",
            )
        if expected_decision == "allowed" and not allowed_claims:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-allowed-claims-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket is allowed but lists no allowed claims",
                recommendation="List the bounded stable-v4 statements that the passed report supports.",
            )
        if (
            boundary.get("stablePublicationReportRequired") is not True
            or boundary.get("allRequiredEvidenceMustPass") is not True
            or boundary.get("sourceOnlyProofCountsAsStableV4") is not False
            or boundary.get("fixtureProofCountsAsStableV4") is not False
            or boundary.get("githubDownloadCountsCountAsAdoptionEvidence") is not False
            or boundary.get("marketplaceAcceptanceClaimed") is not False
            or boundary.get("externalPostingClaimed") is not False
            or approval.get("publicPostingRequiresExplicitApproval") is not True
            or approval.get("computerUseMayPost") is not False
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-boundary-missing",
                evidence=f"{path_name} finalStableV4ClaimPacket weakens proof, marketplace, adoption, or posting boundaries",
                recommendation="State that all real stable-publication evidence must pass, source/fixture/download proof is insufficient, marketplace/posting are not claimed, and public posting requires explicit approval.",
            )
        if public_delta.get("unpublishedLocalDelta") is True:
            delta_summary = (
                final_claim.get("publicReleaseDeltaSummary")
                if isinstance(final_claim.get("publicReleaseDeltaSummary"), dict)
                else {}
            )
            if (
                not delta_summary
                or delta_summary.get("unpublishedLocalDelta") is not True
                or delta_summary.get("stableV4ClaimCoversLocalCheckout") is not public_delta.get("stableV4ClaimCoversLocalCheckout")
                or delta_summary.get("unpublishedLocalCodeCountsAsReleased") is not False
                or "Final claim public-release delta" not in markdown
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-final-claim-release-delta-summary-missing",
                    evidence=f"{path_name} finalStableV4ClaimPacket does not carry the unpublished-local-delta warning",
                    recommendation="Mirror publicReleaseDeltaProof into finalStableV4ClaimPacket and Markdown so claim copy cannot imply unpublished local main is already released.",
                )
        if "Final Stable V4 Claim Packet" in markdown and "Final claim public-release delta" in markdown:
            final_claim_section = markdown.split("Final Stable V4 Claim Packet", 1)[1].split("\n## ", 1)[0]
            table_index = final_claim_section.find("| Evidence | Status |")
            delta_index = final_claim_section.find("Final claim public-release delta")
            first_row_index = final_claim_section.find("| `", table_index + len("| Evidence | Status |")) if table_index >= 0 else -1
            if table_index >= 0 and first_row_index >= 0 and table_index < delta_index < first_row_index:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-final-claim-markdown-table-interrupted",
                    evidence=f"{path_name} renders final claim delta inside the evidence table",
                    recommendation="Render final claim evidence rows contiguously, then render the public-release delta summary after the table.",
                )
        if "Final Stable V4 Claim Packet" not in markdown or "Copy-ready claim" not in markdown or "Claim may be published" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-final-claim-markdown-missing",
                evidence=f"{path_name} has finalStableV4ClaimPacket but Markdown does not render it",
                recommendation="Render the final claim packet in Markdown so maintainers do not need JSON to know what they may safely say.",
            )

    non_claims = packet.get("nonClaims")
    if not isinstance(non_claims, list) or not non_claims:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-non-claims-missing",
            evidence=f"{path_name} evidence packet has no nonClaims",
            recommendation="Keep fake adoption, marketplace acceptance, and fixture-proof non-claims visible in the packet.",
        )
    if "Evidence Packet" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-packet-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication evidence packet",
            recommendation="Render the packet summary and evidence statuses in Markdown so maintainers can review it without opening JSON.",
        )
    templates = report.get("stablePublicationEvidenceTemplates")
    if not isinstance(templates, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-templates-missing",
            evidence=f"{path_name} has no stablePublicationEvidenceTemplates",
            recommendation="Emit draft-only adoption and security-review evidence templates so maintainers can collect real stable-v4 evidence without reverse-engineering JSON from tests.",
        )
    else:
        template_items = templates.get("templates")
        if not isinstance(template_items, list) or len(template_items) < 2:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-template-list-incomplete",
                evidence=f"{path_name} stablePublicationEvidenceTemplates does not list both stable-v4 evidence templates",
                recommendation="List independent adoption and final security-review templates with paths, copy commands, accepted evidence classes, and draft-only instructions.",
            )
        else:
            by_id = {str(item.get("id") or ""): item for item in template_items if isinstance(item, dict)}
            expected_templates = {
                "independent-adoption-evidence": "templates/stable-publication/external-adoption-evidence.template.json",
                "final-security-review-evidence": "templates/stable-publication/security-review-evidence.template.json",
            }
            for template_id, expected_path in expected_templates.items():
                item = by_id.get(template_id)
                if not item:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id=f"stable-publication-{template_id}-template-missing",
                        evidence=f"{path_name} stablePublicationEvidenceTemplates missing {template_id}",
                        recommendation="Expose a draft-only template for every stable-v4 evidence record users must collect.",
                    )
                    continue
                if item.get("path") != expected_path or not item.get("copyCommand"):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id=f"stable-publication-{template_id}-template-routing-missing",
                        evidence=f"{path_name} template {template_id} does not expose the expected path and copy command",
                        recommendation="Attach repo-relative template paths and copy commands so users can create evidence records without searching docs.",
                    )
                if item.get("exists") is not True:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id=f"stable-publication-{template_id}-template-file-missing",
                        evidence=f"{path_name} template {template_id} was reported as missing on disk",
                        recommendation="Package and validate the stable-publication evidence template files.",
                    )
            required_items = required if isinstance(required, list) else []
            required_by_id = {str(item.get("id") or ""): item for item in required_items if isinstance(item, dict)}
            for evidence_id in expected_templates:
                evidence_item = required_by_id.get(evidence_id)
                if not evidence_item:
                    continue
                if not evidence_item.get("templatePath") or not evidence_item.get("templateCommand"):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id=f"stable-publication-{evidence_id}-packet-template-link-missing",
                        evidence=f"{path_name} packet evidence {evidence_id} does not link to its template",
                        recommendation="Include templatePath and templateCommand on adoption and security evidence packet entries.",
                    )
        if templates.get("draftOnly") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-templates-draft-boundary-missing",
                evidence=f"{path_name} stablePublicationEvidenceTemplates does not mark templates as draft-only",
                recommendation="Keep template output honest: unchanged templates must guide collection, not pass as evidence.",
            )
    if "Evidence Templates" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-templates-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication evidence templates",
            recommendation="Render stable-publication evidence templates in Markdown so maintainers can copy the right starting files without opening JSON.",
        )
    starter = report.get("stablePublicationEvidenceStarterKit")
    if not isinstance(starter, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-starter-kit-missing",
            evidence=f"{path_name} has no stablePublicationEvidenceStarterKit",
            recommendation="Emit a draft-only evidence starter kit manifest and write ready-to-fill evidence files into the report directory.",
        )
    else:
        if starter.get("draftOnly") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-starter-kit-draft-boundary-missing",
                evidence=f"{path_name} stablePublicationEvidenceStarterKit is not marked draft-only",
                recommendation="Make clear that generated starter-kit files are collection aids, not stable-v4 evidence.",
            )
        starter_files = starter.get("files")
        starter_paths = {str(item.get("path") or "") for item in starter_files if isinstance(item, dict)} if isinstance(starter_files, list) else set()
        expected_starter_paths = {
            "stable-publication-evidence-kit/README.md",
            "stable-publication-evidence-kit/stable-publication-checklist.json",
            "stable-publication-evidence-kit/external-adoption-evidence.json",
            "stable-publication-evidence-kit/security-review-evidence.json",
        }
        missing_starter_paths = sorted(expected_starter_paths - starter_paths)
        if missing_starter_paths:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-starter-kit-files-missing",
                evidence=f"{path_name} starter kit missing files: {', '.join(missing_starter_paths)}",
                recommendation="List the checklist, README, adoption starter, and security-review starter files in stablePublicationEvidenceStarterKit.files.",
            )
        next_command_template = str(starter.get("nextCommandTemplate") or "")
        if (
            "stable-publication-evidence-kit/external-adoption-evidence.json" not in next_command_template
            or "stable-publication-evidence-kit/security-review-evidence.json" not in next_command_template
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-starter-kit-next-command-missing",
                evidence=f"{path_name} starter kit does not include an attach-ready nextCommandTemplate",
                recommendation="Include a stable-publication nextCommandTemplate that references the generated adoption and security starter files.",
            )
        ladder = starter.get("evidenceLadder")
        ladder_ids = {str(item.get("id") or "") for item in ladder if isinstance(item, dict)} if isinstance(ladder, list) else set()
        expected_ladder_ids = {
            "public-consumer-proof",
            "private-maintainer-qa",
            "independent-adoption-evidence",
            "final-security-review-evidence",
        }
        if not expected_ladder_ids <= ladder_ids:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-starter-kit-ladder-missing",
                evidence=f"{path_name} starter kit does not separate consumer proof, maintainer QA, adoption, and security review evidence",
                recommendation="Add an evidenceLadder to stablePublicationEvidenceStarterKit so maintainers do not mistake private dogfooding for independent adoption or security proof.",
            )
        intake = starter.get("externalEvidenceIntakeChecklist")
        intake_by_id = {str(item.get("id") or ""): item for item in intake if isinstance(item, dict)} if isinstance(intake, list) else {}
        expected_intake = {
            "independent-adoption-evidence": {
                "classes": {"public-external", "private-redacted-external"},
                "fields": {"actorRelationship", "privateDataRedacted", "commands", "artifacts", "outcome", "nonClaims"},
            },
            "final-security-review-evidence": {
                "classes": {"public-security-review", "private-redacted-security-review"},
                "fields": {"scope", "methodology", "findingsSummary", "privateDataRedacted", "nonClaims"},
            },
        }
        missing_intake_ids = sorted(set(expected_intake) - set(intake_by_id))
        if missing_intake_ids:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-evidence-intake-checklist-missing",
                evidence=f"{path_name} starter kit missing external evidence intake checklist ids: {', '.join(missing_intake_ids)}",
                recommendation="Add externalEvidenceIntakeChecklist so draft adoption and security-review records cannot be mistaken for pass-eligible proof.",
            )
        else:
            incomplete_intake_ids = []
            for intake_id, expected in expected_intake.items():
                item = intake_by_id[intake_id]
                classes = set(item.get("acceptedEvidenceClasses") or [])
                fields = set(item.get("requiredFields") or [])
                redaction = item.get("redactionBoundary") if isinstance(item.get("redactionBoundary"), dict) else {}
                if (
                    not expected["classes"] <= classes
                    or not expected["fields"] <= fields
                    or redaction.get("privateDataRedactedMustBeTrue") is not True
                ):
                    incomplete_intake_ids.append(intake_id)
            if incomplete_intake_ids:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-evidence-intake-checklist-incomplete",
                    evidence=f"{path_name} starter kit has incomplete external evidence intake checklist ids: {', '.join(incomplete_intake_ids)}",
                    recommendation="Include accepted evidence classes, required fields, and a strict privateDataRedacted boundary for adoption and security-review starter records.",
                )
        adoption_checklist = starter.get("adoptionEvidenceChecklist")
        if not isinstance(adoption_checklist, dict) or not adoption_checklist:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-adoption-evidence-checklist-missing",
                evidence=f"{path_name} starter kit has no adoptionEvidenceChecklist",
                recommendation="Add an adoption evidence checklist with accepted classes, independent actor requirement, proof fields, artifact expectations, redaction boundaries, weak-signal exclusions, and pass decision.",
            )
        else:
            classes = set(adoption_checklist.get("acceptedEvidenceClasses") or [])
            fields = set(adoption_checklist.get("requiredProofFields") or [])
            artifacts = adoption_checklist.get("artifactExpectations") if isinstance(adoption_checklist.get("artifactExpectations"), list) else []
            redaction = adoption_checklist.get("redactionBoundaries") if isinstance(adoption_checklist.get("redactionBoundaries"), list) else []
            exclusions = set(adoption_checklist.get("weakSignalExclusions") or [])
            pass_decision = str(adoption_checklist.get("passDecision") or "")
            if (
                not {"public-external", "private-redacted-external"} <= classes
                or adoption_checklist.get("requiredActorRelationship") != "independent"
                or not {"commands", "artifacts", "outcome", "nonClaims"} <= fields
                or len(artifacts) < 2
                or "privateDataRedacted must be true" not in redaction
                or not {"GitHub stars", "download counts", "maintainer-only private app runs"} <= exclusions
                or "non-maintainer actor" not in pass_decision
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-adoption-evidence-checklist-incomplete",
                    evidence=f"{path_name} adoptionEvidenceChecklist does not fully define independent adoption pass evidence",
                    recommendation="List accepted evidence classes, independent actor relationship, command/artifact/outcome fields, redaction boundaries, weak-signal exclusions, and the pass decision.",
                )
        security_checklist = starter.get("securityReviewChecklist")
        expected_security_surfaces = {"cli", "plugin", "github-actions", "release-proof", "package-install", "redaction-privacy"}
        expected_security_fields = {"reviewerRelationship", "scope", "methodology", "commands", "artifacts", "findingsSummary", "nonClaims"}
        if not isinstance(security_checklist, dict) or not security_checklist:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-security-review-checklist-missing",
                evidence=f"{path_name} starter kit has no securityReviewChecklist",
                recommendation="Add a concise final security-review checklist with required surfaces, severity thresholds, required fields, redaction boundaries, and pass decision.",
            )
        else:
            surfaces = set(security_checklist.get("requiredReviewSurfaces") or [])
            fields = set(security_checklist.get("requiredEvidenceFields") or [])
            thresholds = security_checklist.get("severityThresholds") if isinstance(security_checklist.get("severityThresholds"), dict) else {}
            redaction = security_checklist.get("redactionBoundaries") if isinstance(security_checklist.get("redactionBoundaries"), list) else []
            pass_decision = str(security_checklist.get("passDecision") or "")
            if (
                not expected_security_surfaces <= surfaces
                or not expected_security_fields <= fields
                or thresholds.get("criticalOpen") != 0
                or thresholds.get("highOpen") != 0
                or "privateDataRedacted must be true" not in redaction
                or "criticalOpen" not in pass_decision
                or "highOpen" not in pass_decision
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-security-review-checklist-incomplete",
                    evidence=f"{path_name} securityReviewChecklist does not fully define final security-review pass evidence",
                    recommendation="List all required review surfaces, critical/high zero thresholds, required fields, redaction boundaries, and a pass decision tied to those gates.",
                )
        starter_schema = starter.get("schemaVersion")
        if isinstance(starter_schema, int) and starter_schema >= 2:
            report_release_version = str(report.get("releaseVersion") or "")
            if report_release_version and str(starter.get("releaseVersion") or "") != report_release_version:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-evidence-starter-kit-release-version-missing",
                    evidence=f"{path_name} starter kit does not carry the report releaseVersion",
                    recommendation="Copy the report releaseVersion into stablePublicationEvidenceStarterKit and the written starter checklist so users know which public release the packet closes.",
                )
            related_kits = starter.get("relatedAuthoringKits")
            release_notes_related = [
                item for item in related_kits
                if isinstance(item, dict)
                and item.get("id") == "release-notes-authoring-kit"
                and item.get("directory") == "stable-publication-release-notes"
            ] if isinstance(related_kits, list) else []
            if isinstance(report.get("stablePublicationReleaseNotesAuthoringKit"), dict) and not release_notes_related:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="stable-publication-evidence-starter-kit-release-notes-link-missing",
                    evidence=f"{path_name} starter kit does not link to the release-notes authoring kit",
                    recommendation="Add stablePublicationEvidenceStarterKit.relatedAuthoringKits with the release-notes directory, status, missing topics, files, and rerun command.",
                )
    if "Evidence Starter Kit" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-starter-kit-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication evidence starter kit",
            recommendation="Render the generated starter-kit directory and files in Markdown so maintainers can find them immediately.",
        )
    if "private-maintainer-qa" not in markdown or "public-consumer-proof" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-ladder-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication evidence ladder",
            recommendation="Render the evidence ladder in Markdown so public consumer proof, maintainer QA, independent adoption, and security review stay visually separate.",
        )
    if "External Evidence Intake Checklist" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-evidence-intake-checklist-markdown-missing",
            evidence=f"{path_name} Markdown does not render the external evidence intake checklist",
            recommendation="Render accepted evidence classes, required fields, and redaction boundaries in Markdown before starter records can be used.",
        )
    if "Security Review Evidence Checklist" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-security-review-checklist-markdown-missing",
            evidence=f"{path_name} Markdown does not render the security review evidence checklist",
            recommendation="Render required review surfaces, severity thresholds, required fields, redaction boundaries, and pass decision in Markdown.",
        )
    if "Adoption Evidence Checklist" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-adoption-evidence-checklist-markdown-missing",
            evidence=f"{path_name} Markdown does not render the adoption evidence checklist",
            recommendation="Render accepted evidence classes, actor relationship, proof artifacts, redaction boundaries, weak-signal exclusions, and pass decision in Markdown.",
        )
    notes_kit = report.get("stablePublicationReleaseNotesAuthoringKit")
    if not isinstance(notes_kit, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-release-notes-authoring-kit-missing",
            evidence=f"{path_name} has no stablePublicationReleaseNotesAuthoringKit",
            recommendation="Emit a draft-only release-notes authoring kit with a checklist and copy-ready draft for the stable-publication topics.",
        )
    else:
        if notes_kit.get("draftOnly") is not True:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-notes-authoring-kit-draft-boundary-missing",
                evidence=f"{path_name} release-notes authoring kit is not marked draft-only",
                recommendation="Make clear that generated release notes are an authoring aid, not proof that the public GitHub release was edited.",
            )
        note_files = notes_kit.get("files")
        note_paths = {str(item.get("path") or "") for item in note_files if isinstance(item, dict)} if isinstance(note_files, list) else set()
        expected_note_paths = {
            "stable-publication-release-notes/README.md",
            "stable-publication-release-notes/release-notes-checklist.json",
            "stable-publication-release-notes/draft-release-notes.md",
        }
        missing_note_paths = sorted(expected_note_paths - note_paths)
        if missing_note_paths:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-notes-authoring-kit-files-missing",
                evidence=f"{path_name} release-notes authoring kit missing files: {', '.join(missing_note_paths)}",
                recommendation="List README, release-notes checklist, and draft release notes in stablePublicationReleaseNotesAuthoringKit.files.",
            )
        kit_missing_topics = notes_kit.get("missingTopicIds")
        proof = report.get("releaseNotesProof") if isinstance(report.get("releaseNotesProof"), dict) else {}
        proof_missing_topics = proof.get("missingTopicIds")
        if isinstance(proof_missing_topics, list) and kit_missing_topics != proof_missing_topics:
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-notes-authoring-kit-topic-drift",
                evidence=f"{path_name} release-notes authoring kit missingTopicIds does not match releaseNotesProof",
                recommendation="Copy releaseNotesProof.missingTopicIds into the authoring kit so the draft answers the actual blocked topics.",
            )
        if "stable-publication" not in str(notes_kit.get("nextCommandTemplate") or ""):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-notes-authoring-kit-next-command-missing",
                evidence=f"{path_name} release-notes authoring kit has no stable-publication rerun command",
                recommendation="Include the command to rerun stable-publication after editing public release notes.",
            )
        edit_command = str(notes_kit.get("publicReleaseEditCommand") or "")
        requires_edit_command = int(notes_kit.get("schemaVersion") or 1) >= 2
        review_notes = notes_kit.get("status") == "review" or bool(kit_missing_topics)
        if requires_edit_command and review_notes and (
            "gh release edit" not in edit_command
            or "--notes-file" not in edit_command
            or "stable-publication-release-notes/draft-release-notes.md" not in edit_command
        ):
            add_issue(
                issues,
                severity="review",
                rule_id="stable-publication-release-notes-authoring-kit-edit-command-missing",
                evidence=f"{path_name} release-notes authoring kit does not include a copy-ready GitHub release edit command",
                recommendation="Include publicReleaseEditCommand with gh release edit, --notes-file, and the generated draft-release-notes path.",
            )
    if "Release Notes Authoring Kit" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-release-notes-authoring-kit-markdown-missing",
            evidence=f"{path_name} Markdown does not render the stable-publication release-notes authoring kit",
            recommendation="Render the generated release-notes authoring kit so maintainers can find the checklist and draft without opening JSON.",
        )
    elif (
        isinstance(notes_kit, dict)
        and int(notes_kit.get("schemaVersion") or 1) >= 2
        and notes_kit.get("status") == "review"
        and "gh release edit" not in markdown
    ):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-release-notes-authoring-kit-edit-command-markdown-missing",
            evidence=f"{path_name} Markdown renders the release-notes kit but hides the GitHub release edit command",
            recommendation="Render publicReleaseEditCommand in the Release Notes Authoring Kit section.",
        )
    questions_text = " ".join(str(item) for item in report.get("reportQualityQuestions") or [])
    relay_required = stable_publication_launch_relay_question(questions_text) or isinstance(
        report.get("stablePublicationLaunchRelayDrafts"), dict
    )
    if not relay_required:
        return issues

    relay = report.get("stablePublicationLaunchRelayDrafts")
    if not isinstance(relay, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-drafts-missing",
            evidence=f"{path_name} declares launch relay actionability but has no stablePublicationLaunchRelayDrafts",
            recommendation="Emit a draft-only launch relay packet with Product Hunt, Reddit, X, and HN drafts plus explicit approval boundaries.",
        )
        return issues
    posting_policy = relay.get("postingPolicy") if isinstance(relay.get("postingPolicy"), dict) else {}
    if relay.get("draftOnly") is not True:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-draft-boundary-missing",
            evidence=f"{path_name} launch relay packet is not marked draftOnly",
            recommendation="Mark launch relay drafts as draft-only so they cannot be mistaken for published launch proof.",
        )
    if relay.get("approvalRequired") is not True or posting_policy.get("requiresExplicitApproval") is not True:
        add_issue(
            issues,
            severity="high",
            rule_id="stable-publication-launch-relay-approval-gate-missing",
            evidence=f"{path_name} launch relay packet does not require explicit approval before public posting",
            recommendation="Require explicit human approval for the exact launch run before public posting, publishing, submission, scheduling, or account-visible actions.",
        )
    if relay.get("publicPostingAllowed") is not False or posting_policy.get("publicPostingAllowed") is not False:
        add_issue(
            issues,
            severity="high",
            rule_id="stable-publication-launch-relay-posting-not-blocked",
            evidence=f"{path_name} launch relay packet does not block public posting by default",
            recommendation="Keep publicPostingAllowed=false until a human approves the exact external launch action.",
        )
    if posting_policy.get("computerUseMayPost") is not False:
        add_issue(
            issues,
            severity="high",
            rule_id="stable-publication-launch-relay-computer-use-autopost-risk",
            evidence=f"{path_name} launch relay packet does not explicitly forbid computer-use autoposting",
            recommendation="State that computer-use may stage drafts only after explicit approval and must not post by default.",
        )
    relay_files = relay.get("files")
    relay_paths = {str(item.get("path") or "") for item in relay_files if isinstance(item, dict)} if isinstance(relay_files, list) else set()
    expected_relay_paths = {
        "stable-publication-launch-relay/README.md",
        "stable-publication-launch-relay/launch-relay-checklist.json",
        "stable-publication-launch-relay/product-hunt-draft.md",
        "stable-publication-launch-relay/reddit-r-shipguard-draft.md",
        "stable-publication-launch-relay/x-thread-draft.md",
        "stable-publication-launch-relay/hacker-news-draft.md",
    }
    missing_relay_paths = sorted(expected_relay_paths - relay_paths)
    if missing_relay_paths:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-files-missing",
            evidence=f"{path_name} launch relay packet missing files: {', '.join(missing_relay_paths)}",
            recommendation="List README, checklist, Product Hunt, Reddit, X, and Hacker News draft files in stablePublicationLaunchRelayDrafts.files.",
        )
    channel_ids = {
        str(item.get("id") or "")
        for item in relay.get("channels", [])
        if isinstance(item, dict)
    }
    expected_channels = {"product-hunt", "reddit-r-shipguard", "x-thread", "hacker-news"}
    missing_channels = sorted(expected_channels - channel_ids)
    if missing_channels:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-channels-missing",
            evidence=f"{path_name} launch relay packet missing channels: {', '.join(missing_channels)}",
            recommendation="Expose the intended public launch channels so a maintainer can review every draft before approval.",
        )
    if "stable-publication" not in str(relay.get("nextCommandTemplate") or ""):
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-next-proof-command-missing",
            evidence=f"{path_name} launch relay packet has no stable-publication rerun command",
            recommendation="Include the stable-publication proof command so launch copy stays tied to the current evidence packet.",
        )
    relay_non_claims = " ".join(str(item) for item in relay.get("nonClaims") or [])
    if "publish" not in relay_non_claims.lower() or "computer-use" not in relay_non_claims.lower():
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-non-claims-missing",
            evidence=f"{path_name} launch relay packet nonClaims do not block posting and computer-use overclaims",
            recommendation="Keep launch relay non-claims explicit: no publishing/submission/posting and no computer-use account action without approval.",
        )
    if "Launch Relay Drafts" not in markdown or "Approval required" not in markdown or "Public posting allowed" not in markdown:
        add_issue(
            issues,
            severity="review",
            rule_id="stable-publication-launch-relay-markdown-missing",
            evidence=f"{path_name} Markdown does not render the launch relay approval boundary",
            recommendation="Render Launch Relay Drafts in Markdown with approval-required and public-posting-allowed fields.",
        )
    return issues


def spec_workflow_quality_issues(report: dict[str, Any], *, path: Path, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    inputs = report.get("reportInputs")
    if not isinstance(inputs, dict):
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-report-inputs-missing",
            evidence=f"{path_name} has no reportInputs object",
            recommendation="Generate spec workflows from report-quality or source-scanner outputs so adoption work is grounded in evidence.",
        )
        return issues

    reports = inputs.get("reports")
    questions = inputs.get("actionabilityQuestions")
    if not isinstance(reports, list) or not reports:
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-report-context-missing",
            evidence=f"{path_name} has no reportInputs.reports entries",
            recommendation="Pass --from-report <report-quality-dir> or another ShipGuard report so the spec workflow is tied to observed tool output.",
        )
    if not isinstance(questions, list) or not questions:
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-actionability-missing",
            evidence=f"{path_name} has no reportInputs.actionabilityQuestions entries",
            recommendation="Feed report-quality output into spec-workflow so real actionability questions become clarifying questions and tasks.",
        )

    expected_questions = spec_workflow_expected_questions(inputs)
    expected_task_questions = spec_workflow_expected_questions(inputs, limit=16)
    if expected_questions:
        feature_spec = report.get("featureSpec")
        clarifying_questions = feature_spec.get("clarifyingQuestions") if isinstance(feature_spec, dict) else None
        normalized_clarifying = {
            normalized_question_text(item)
            for item in clarifying_questions
            if isinstance(item, str) and item.strip()
        } if isinstance(clarifying_questions, list) else set()
        missing_question_count = sum(
            1 for question in expected_questions if normalized_question_text(question) not in normalized_clarifying
        )
        if missing_question_count:
            add_issue(
                issues,
                severity="review",
                rule_id="spec-workflow-question-coverage-missing",
                evidence=(
                    f"{path_name} featureSpec.clarifyingQuestions missing "
                    f"{missing_question_count} of {len(expected_questions)} report actionability questions"
                ),
                recommendation="Regenerate the spec workflow so report-quality actionability questions become clarifying questions in JSON.",
            )
    if expected_task_questions:
        task_plan = report.get("taskPlan")
        task_text = ""
        if isinstance(task_plan, list):
            task_text = "\n".join(
                f"{item.get('task') or ''} {item.get('proof') or ''}"
                for item in task_plan
                if isinstance(item, dict)
            )
        normalized_task_text = normalized_question_text(task_text)
        missing_task_count = sum(
            1 for question in expected_task_questions if normalized_question_text(question) not in normalized_task_text
        )
        if missing_task_count:
            add_issue(
                issues,
                severity="review",
                rule_id="spec-workflow-task-coverage-missing",
                evidence=(
                    f"{path_name} taskPlan missing "
                    f"{missing_task_count} of {len(expected_task_questions)} report actionability questions"
                ),
                recommendation="Regenerate the spec workflow so taskPlan includes proof-gated tasks for each report-quality question.",
            )
        feature_spec = report.get("featureSpec")
        acceptance_criteria = feature_spec.get("acceptanceCriteria") if isinstance(feature_spec, dict) else None
        criteria_text = ""
        if isinstance(acceptance_criteria, list):
            criteria_text = "\n".join(str(item) for item in acceptance_criteria if isinstance(item, str))
        normalized_criteria_text = normalized_question_text(criteria_text)
        missing_acceptance_count = sum(
            1 for question in expected_task_questions if normalized_question_text(question) not in normalized_criteria_text
        )
        if missing_acceptance_count:
            add_issue(
                issues,
                severity="review",
                rule_id="spec-workflow-acceptance-coverage-missing",
                evidence=(
                    f"{path_name} featureSpec.acceptanceCriteria missing "
                    f"{missing_acceptance_count} of {len(expected_task_questions)} report actionability questions"
                ),
                recommendation="Regenerate the spec workflow so acceptance criteria state how each report-quality question will be answered.",
            )

    technical_plan = report.get("technicalPlan")
    recommended_validation = (
        technical_plan.get("recommendedValidation") if isinstance(technical_plan, dict) else None
    )
    validation_text = ""
    if isinstance(recommended_validation, list):
        validation_text = "\n".join(str(item) for item in recommended_validation if isinstance(item, str))
    normalized_validation_text = normalized_question_text(validation_text)
    missing_validation_commands = [
        command
        for command in SPEC_WORKFLOW_REQUIRED_VALIDATION_COMMANDS
        if normalized_question_text(command) not in normalized_validation_text
    ]
    if missing_validation_commands:
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-validation-coverage-missing",
            evidence=(
                f"{path_name} technicalPlan.recommendedValidation missing "
                f"{len(missing_validation_commands)} of {len(SPEC_WORKFLOW_REQUIRED_VALIDATION_COMMANDS)} required validation commands"
            ),
            recommendation="Regenerate the spec workflow so recommendedValidation lists exact proof commands before implementation.",
        )

    analysis_gates = report.get("analysisGates")
    analysis_text = ""
    if isinstance(analysis_gates, list):
        analysis_text = "\n".join(str(item) for item in analysis_gates if isinstance(item, str))
    normalized_analysis_text = normalized_question_text(analysis_text)
    missing_analysis_gates = [
        gate
        for gate in SPEC_WORKFLOW_REQUIRED_ANALYSIS_GATES
        if normalized_question_text(gate) not in normalized_analysis_text
    ]
    if missing_analysis_gates:
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-analysis-coverage-missing",
            evidence=(
                f"{path_name} analysisGates missing "
                f"{len(missing_analysis_gates)} of {len(SPEC_WORKFLOW_REQUIRED_ANALYSIS_GATES)} required analysis gates"
            ),
            recommendation="Regenerate the spec workflow so analysisGates preserve the checks needed before implementation.",
        )

    slash_gaps = spec_workflow_slash_handoff_gaps(report)
    if slash_gaps:
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-slash-handoff-incomplete",
            evidence=f"{path_name} slash handoff is incomplete: {', '.join(slash_gaps[:4])}",
            recommendation="Regenerate the spec workflow so slashPlan and slashGoal are copy-ready /plan and /goal commands with validation and next-goal handoff guidance.",
        )

    artifacts = report.get("artifacts")
    if not isinstance(artifacts, dict):
        add_issue(
            issues,
            severity="high",
            rule_id="spec-workflow-artifacts-missing",
            evidence=f"{path_name} has no artifacts manifest",
            recommendation="Emit a complete artifacts map so downstream users know which generated files to review.",
        )
    else:
        missing = sorted(SPEC_WORKFLOW_REQUIRED_ARTIFACTS - set(artifacts))
        if missing:
            add_issue(
                issues,
                severity="review",
                rule_id="spec-workflow-artifacts-incomplete",
                evidence=f"{path_name} artifacts missing: {', '.join(missing)}",
                recommendation="Keep every spec workflow output self-describing: constitution, spec, checklist, integration decisions, plan, tasks, consistency analysis, Devspace guardrails, JSON, and Markdown.",
            )
        base_dir = path.parent
        for artifact_name in sorted(SPEC_WORKFLOW_REQUIRED_ARTIFACTS & set(artifacts)):
            raw_value = artifacts.get(artifact_name)
            if not isinstance(raw_value, str) or not raw_value.strip():
                add_issue(
                    issues,
                    severity="review",
                    rule_id="spec-workflow-artifact-path-invalid",
                    evidence=f"{path_name} artifact {artifact_name} has no usable file path",
                    recommendation="Emit relative file paths for every generated spec-workflow artifact.",
                )
                continue
            artifact_path = Path(raw_value)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                add_issue(
                    issues,
                    severity="high",
                    rule_id="spec-workflow-artifact-path-unsafe",
                    evidence=f"{path_name} artifact {artifact_name} uses an absolute or parent-relative path",
                    recommendation="Keep spec-workflow artifact paths relative to the report directory before sharing or scoring.",
                )
                continue
            local_artifact_path = base_dir / artifact_path
            if not local_artifact_path.is_file():
                add_issue(
                    issues,
                    severity="review",
                    rule_id="spec-workflow-artifact-file-missing",
                    evidence=f"{path_name} artifact {artifact_name} missing file {raw_value}",
                    recommendation="Regenerate or copy the complete spec workflow bundle before report-quality scoring.",
                )
                continue
            try:
                artifact_size = local_artifact_path.stat().st_size
            except OSError:
                artifact_size = 0
            if artifact_size == 0:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="spec-workflow-artifact-file-empty",
                    evidence=f"{path_name} artifact {artifact_name} is empty: {raw_value}",
                    recommendation="Regenerate spec-workflow artifacts so every declared file contains reviewable content.",
                )
                continue
            markers = SPEC_WORKFLOW_ARTIFACT_MARKERS.get(artifact_name, [])
            needs_question_coverage = artifact_name in {"analysis", "checklist", "integrationDecisions", "markdown", "spec"} and bool(expected_questions)
            needs_task_coverage = artifact_name == "tasks" and bool(expected_task_questions)
            needs_acceptance_coverage = artifact_name == "spec" and bool(expected_task_questions)
            needs_validation_coverage = artifact_name == "plan"
            needs_analysis_coverage = artifact_name == "plan"
            needs_slash_handoff_coverage = artifact_name == "markdown"
            artifact_text = ""
            if (
                markers
                or needs_question_coverage
                or needs_task_coverage
                or needs_acceptance_coverage
                or needs_validation_coverage
                or needs_analysis_coverage
                or needs_slash_handoff_coverage
            ):
                artifact_text = local_artifact_path.read_text(encoding="utf-8", errors="ignore")
            if markers:
                missing_markers = [marker for marker in markers if marker not in artifact_text]
                if missing_markers:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-artifact-content-incomplete",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing content markers in {raw_value}: "
                            f"{', '.join(missing_markers[:4])}"
                        ),
                        recommendation="Regenerate the spec workflow so every declared artifact contains its expected headings, proof cues, and guardrails.",
                    )
                if SPEC_WORKFLOW_PLACEHOLDER_RE.search(artifact_text):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-artifact-placeholder-content",
                        evidence=f"{path_name} artifact {artifact_name} still contains placeholder content in {raw_value}",
                        recommendation="Replace placeholder-only spec-workflow content with reviewable tasks, proof lanes, and guardrails before scoring.",
                    )
            if needs_question_coverage:
                normalized_artifact_text = normalized_question_text(artifact_text)
                missing_question_count = sum(
                    1 for question in expected_questions if normalized_question_text(question) not in normalized_artifact_text
                )
                if missing_question_count:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-question-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{missing_question_count} of {len(expected_questions)} report actionability questions in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so feature-spec and main Markdown preserve the report-quality questions.",
                    )
            if needs_task_coverage:
                normalized_artifact_text = normalized_question_text(artifact_text)
                missing_task_count = sum(
                    1 for question in expected_task_questions if normalized_question_text(question) not in normalized_artifact_text
                )
                if missing_task_count:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-task-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{missing_task_count} of {len(expected_task_questions)} report actionability questions in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so tasks.md includes proof-gated tasks for the report-quality questions.",
                    )
            if needs_acceptance_coverage:
                acceptance_text = markdown_section_text(artifact_text, "Acceptance Criteria")
                normalized_artifact_text = normalized_question_text(acceptance_text)
                missing_acceptance_count = sum(
                    1 for question in expected_task_questions if normalized_question_text(question) not in normalized_artifact_text
                )
                if missing_acceptance_count:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-acceptance-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{missing_acceptance_count} of {len(expected_task_questions)} report actionability questions in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so feature-spec.md acceptance criteria preserve the report-quality questions.",
                    )
            if needs_validation_coverage:
                validation_section = markdown_section_text(artifact_text, "Validation")
                normalized_artifact_text = normalized_question_text(validation_section)
                missing_validation_commands = [
                    command
                    for command in SPEC_WORKFLOW_REQUIRED_VALIDATION_COMMANDS
                    if normalized_question_text(command) not in normalized_artifact_text
                ]
                if missing_validation_commands:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-validation-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{len(missing_validation_commands)} of {len(SPEC_WORKFLOW_REQUIRED_VALIDATION_COMMANDS)} validation commands in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so implementation-plan.md lists exact validation commands.",
                    )
            if needs_analysis_coverage:
                analysis_section = markdown_section_text(artifact_text, "Analysis Gates")
                normalized_artifact_text = normalized_question_text(analysis_section)
                missing_analysis_gates = [
                    gate
                    for gate in SPEC_WORKFLOW_REQUIRED_ANALYSIS_GATES
                    if normalized_question_text(gate) not in normalized_artifact_text
                ]
                if missing_analysis_gates:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-analysis-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{len(missing_analysis_gates)} of {len(SPEC_WORKFLOW_REQUIRED_ANALYSIS_GATES)} analysis gates in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so implementation-plan.md lists the required analysis gates.",
                    )
            if needs_slash_handoff_coverage:
                plan_section = markdown_section_text(artifact_text, "Slash Plan")
                goal_section = markdown_section_text(artifact_text, "Slash Goal")
                missing_slash_sections: list[str] = []
                slash_plan = str(report.get("slashPlan") or "").strip()
                slash_goal = str(report.get("slashGoal") or "").strip()
                if slash_plan and normalized_question_text(slash_plan) not in normalized_question_text(plan_section):
                    missing_slash_sections.append("slashPlan")
                if slash_goal and normalized_question_text(slash_goal) not in normalized_question_text(goal_section):
                    missing_slash_sections.append("slashGoal")
                if missing_slash_sections:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="spec-workflow-slash-handoff-artifact-missing",
                        evidence=(
                            f"{path_name} artifact {artifact_name} missing "
                            f"{', '.join(missing_slash_sections)} in {raw_value}"
                        ),
                        recommendation="Regenerate the spec workflow so ios-spec-workflow.md preserves the exact JSON slashPlan and slashGoal handoff text.",
                    )

    section_checks = [
        ("constitution", "spec-workflow-constitution-missing"),
        ("featureSpec", "spec-workflow-feature-spec-missing"),
        ("requirementsChecklist", "spec-workflow-checklist-missing"),
        ("integrationDecisions", "spec-workflow-integration-decisions-missing"),
        ("technicalPlan", "spec-workflow-plan-missing"),
        ("taskPlan", "spec-workflow-tasks-missing"),
        ("consistencyAnalysis", "spec-workflow-consistency-analysis-missing"),
        ("analysisGates", "spec-workflow-analysis-gates-missing"),
        ("devspaceGuardrails", "spec-workflow-devspace-guardrails-missing"),
    ]
    for field, rule_id in section_checks:
        value = report.get(field)
        if not value:
            add_issue(
                issues,
                severity="review",
                rule_id=rule_id,
                evidence=f"{path_name} has empty {field}",
                recommendation="Regenerate the spec workflow so constitution, spec, checklist, integration decisions, plan, tasks, consistency analysis, analysis gates, and Devspace guardrails are all reviewable.",
            )
    if not report.get("slashPlan") or not report.get("slashGoal"):
        add_issue(
            issues,
            severity="review",
            rule_id="spec-workflow-slash-handoff-missing",
            evidence=f"{path_name} is missing slashPlan or slashGoal",
            recommendation="Emit slash plan and slash goal text so the next Codex loop can continue without reconstructing the handoff.",
        )

    return issues


def lean_report_quality_issues(report: dict[str, Any], *, markdown: str, path_name: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    tool = str(report.get("tool") or "")
    if tool in {"shipguard lean audit", "shipguard lean review"}:
        gates = report.get("behaviorGates")
        required_gates = {
            "oneRunnableCheck",
            "hardwareCalibration",
            "requestedExplanation",
            "adapterBoundary",
            "gainHonesty",
        }
        if not isinstance(gates, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-behavior-gates-missing",
                evidence=f"{path_name} has no behaviorGates object",
                recommendation="Emit behavior gates for one-check minimums, hardware calibration, requested explanations, adapter boundaries, and gain honesty.",
            )
        else:
            missing = sorted(required_gates - set(gates))
            if missing:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-behavior-gates-incomplete",
                    evidence=f"{path_name} missing behavior gates: {', '.join(missing)}",
                    recommendation="Keep Lean Deck behavior gates complete so Ponytail-style precision does not become blind less-code pressure.",
                )
        if "Behavior Gates" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-behavior-gates-markdown-missing",
                evidence=f"{path_name} Markdown does not expose behavior gates",
                recommendation="Render behavior gates in Markdown so maintainers see what Lean Deck is protecting.",
            )
    if tool == "shipguard lean review":
        findings = report.get("findings") if isinstance(report.get("findings"), list) else []
        proof_related = [
            item
            for item in findings
            if isinstance(item, dict)
            and str(item.get("ruleId") or "").startswith("one-runnable-check")
        ]
        missing_rule_count = len(
            [
                item
                for item in proof_related
                if str(item.get("ruleId") or "") == "one-runnable-check-missing-diff"
            ]
        )
        same_diff_rule_count = len(
            [
                item
                for item in proof_related
                if str(item.get("ruleId") or "") == "one-runnable-check-signal-present-diff"
            ]
        )
        hardware_rule_count = len(
            [
                item
                for item in findings
                if isinstance(item, dict) and str(item.get("ruleId") or "") == "hardware-calibration-missing-diff"
            ]
        )
        host_adapter_rule_count = len(
            [
                item
                for item in findings
                if isinstance(item, dict) and str(item.get("ruleId") or "") == "host-adapter-boundary-diff"
            ]
        )
        safety_rule_count = len(
            [
                item
                for item in findings
                if isinstance(item, dict) and str(item.get("ruleId") or "") == "do-not-cut-safety-diff-without-proof"
            ]
        )
        lean_mode = report.get("leanMode")
        precision_for_mode = report.get("precisionReview") if isinstance(report.get("precisionReview"), dict) else {}
        if not isinstance(lean_mode, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-mode-missing",
                evidence=f"{path_name} has no leanMode object",
                recommendation="Emit leanMode.mode and leanMode.firstActionBias so readers know whether Lean Review ran in lite, full, or ultra mode.",
            )
            mode = ""
            expected_contract = None
        else:
            mode = str(lean_mode.get("mode") or "")
            expected_contract = LEAN_REVIEW_MODE_BIAS_CONTRACT.get(mode)
            if not expected_contract:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-invalid",
                    evidence=f"{path_name} leanMode.mode={mode!r}",
                    recommendation="Set leanMode.mode to lite, full, or ultra.",
                )
            elif str(lean_mode.get("firstActionBias") or "") != expected_contract["firstActionBias"]:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-bias-incomplete",
                    evidence=(
                        f"{path_name} leanMode.firstActionBias={lean_mode.get('firstActionBias')!r} "
                        f"for mode {mode!r}"
                    ),
                    recommendation=f"Set {mode} mode firstActionBias to {expected_contract['firstActionBias']}.",
                )
            precision_mode = precision_for_mode.get("mode") if isinstance(precision_for_mode.get("mode"), dict) else {}
            if expected_contract and (
                str(precision_mode.get("mode") or "") != mode
                or str(precision_mode.get("firstActionBias") or "") != expected_contract["firstActionBias"]
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-precision-mismatch",
                    evidence=f"{path_name} precisionReview.mode does not mirror leanMode for {mode!r}",
                    recommendation="Mirror the selected mode and first-action bias inside precisionReview.mode so JSON consumers do not need Markdown parsing.",
                )
        mode_bias_review = report.get("modeBiasReview")
        if not isinstance(mode_bias_review, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-mode-bias-review-missing",
                evidence=f"{path_name} has no modeBiasReview object",
                recommendation="Emit modeBiasReview with lite/full/ultra priority orders and the selected top-action match result.",
            )
        elif expected_contract:
            supported_modes = mode_bias_review.get("supportedModes")
            supported_rows = supported_modes if isinstance(supported_modes, list) else []
            supported_by_mode = {
                str(row.get("mode") or ""): row
                for row in supported_rows
                if isinstance(row, dict)
            }
            missing_modes = sorted(set(LEAN_REVIEW_MODE_BIAS_CONTRACT) - set(supported_by_mode))
            if missing_modes:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-bias-matrix-incomplete",
                    evidence=f"{path_name} modeBiasReview.supportedModes missing: {', '.join(missing_modes)}",
                    recommendation="List lite, full, and ultra mode bias contracts in modeBiasReview.supportedModes.",
                )
            for supported_mode, contract in LEAN_REVIEW_MODE_BIAS_CONTRACT.items():
                row = supported_by_mode.get(supported_mode)
                if not isinstance(row, dict):
                    continue
                if str(row.get("firstActionBias") or "") != contract["firstActionBias"] or not list_matches_expected(
                    row.get("priorityOrder"), contract["priorityOrder"]
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-mode-bias-matrix-invalid",
                        evidence=f"{path_name} modeBiasReview has wrong contract for {supported_mode}",
                        recommendation="Keep lite suggestion-first, full proof-ladder, and ultra delete-first priority orders stable.",
                    )
            if (
                str(mode_bias_review.get("selectedMode") or "") != mode
                or str(mode_bias_review.get("selectedFirstActionBias") or "") != expected_contract["firstActionBias"]
                or not list_matches_expected(mode_bias_review.get("selectedPriorityOrder"), expected_contract["priorityOrder"])
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-bias-selected-incomplete",
                    evidence=f"{path_name} modeBiasReview selected fields do not match leanMode {mode!r}",
                    recommendation="Keep selectedMode, selectedFirstActionBias, and selectedPriorityOrder aligned with the selected Lean Review mode.",
                )
            expected_action, expected_source = first_mode_priority_action(
                precision_for_mode, expected_contract["priorityOrder"]
            )
            top_actions = (
                precision_for_mode.get("topActions") if isinstance(precision_for_mode.get("topActions"), list) else []
            )
            selected_top_action = top_actions[0] if top_actions and isinstance(top_actions[0], dict) else None
            clean_state = not any(mode_action_key(expected_action)) and not selected_top_action
            if not clean_state and mode_action_key(expected_action) != mode_action_key(selected_top_action):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-top-action-mismatch",
                    evidence=(
                        f"{path_name} top action does not match {mode} priority source {expected_source}: "
                        f"expected {mode_action_key(expected_action)!r}, got {mode_action_key(selected_top_action)!r}"
                    ),
                    recommendation="Order precisionReview.topActions from the selected mode's priority list.",
                )
            summary = mode_bias_review.get("summary") if isinstance(mode_bias_review.get("summary"), dict) else {}
            if (
                int(summary.get("supportedModeCount") or 0) < 3
                or summary.get("selectedModeMatchesPrecisionReview") is not True
                or summary.get("selectedFirstActionBiasMatchesPrecisionReview") is not True
                or summary.get("selectedTopActionMatchesBias") is not True
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-mode-bias-summary-incomplete",
                    evidence=f"{path_name} modeBiasReview.summary does not prove selected mode/top-action alignment",
                    recommendation="Summarize supported-mode count plus selected mode, first-action bias, and top-action match booleans.",
                )
        mode_markdown_required = ["Lean Mode", "First action bias", "Mode Bias Review", "lite", "full", "ultra"]
        if expected_contract:
            mode_markdown_required.extend([mode, expected_contract["firstActionBias"]])
        missing_mode_markdown = [token for token in mode_markdown_required if token not in markdown]
        if missing_mode_markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-mode-markdown-missing",
                evidence=f"{path_name} Markdown missing mode-bias tokens: {', '.join(missing_mode_markdown)}",
                recommendation="Render Lean Mode and Mode Bias Review so maintainers can see the selected mode and lite/full/ultra first-action behavior without opening JSON.",
            )
        calibration = report.get("proofSignalCalibration")
        if proof_related:
            if not isinstance(calibration, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-proof-signal-calibration-missing",
                    evidence=f"{path_name} has runnable-check findings but no proofSignalCalibration",
                    recommendation="Emit proofSignalCalibration so Lean Review separates missing proof from same-diff test evidence.",
                )
            else:
                status = str(calibration.get("sameDiffProofStatus") or "")
                signal_count = int(calibration.get("sameDiffProofSignalCount") or 0)
                covered_count = int(calibration.get("codeFindingsCoveredBySameDiffProof") or 0)
                missing_count = int(calibration.get("missingRunnableCheckFindings") or 0)
                if status == "present" and signal_count < 1:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-count-missing",
                        evidence=f"{path_name} marks same-diff proof present without proof signals",
                        recommendation="List the changed test/assertion files that caused same-diff proof calibration.",
                    )
                if status == "present" and covered_count < 1 and any(
                    str(item.get("ruleId") or "") == "one-runnable-check-signal-present-diff"
                    for item in proof_related
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-covered-count-missing",
                        evidence=f"{path_name} has same-diff proof findings without a covered count",
                        recommendation="Set codeFindingsCoveredBySameDiffProof so the report shows how many findings were calibrated.",
                    )
                if status == "missing" and missing_count < 1 and any(
                    str(item.get("ruleId") or "") == "one-runnable-check-missing-diff"
                    for item in proof_related
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-missing-count-missing",
                        evidence=f"{path_name} has missing runnable-check findings without a missing count",
                        recommendation="Set missingRunnableCheckFindings so the report explains why proof remains missing.",
                    )
        if proof_related and "Proof Signal Calibration" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-proof-signal-markdown-missing",
                evidence=f"{path_name} Markdown does not expose proof signal calibration",
                recommendation="Render proofSignalCalibration in Markdown so maintainers can see whether tests were absent or present elsewhere in the diff.",
            )
        if proof_related:
            proof_matching = report.get("proofSignalMatching")
            if not isinstance(proof_matching, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-proof-signal-matching-missing",
                    evidence=f"{path_name} has runnable-check findings but no proofSignalMatching",
                    recommendation="Emit proofSignalMatching with matched rows, unmatched proof signals, and a non-global proof boundary.",
                )
            else:
                summary = proof_matching.get("summary") if isinstance(proof_matching.get("summary"), dict) else {}
                rows = proof_matching.get("rows")
                unmatched = proof_matching.get("unmatchedProofSignals")
                boundary = normalized_question_text(proof_matching.get("nonGlobalProofBoundary") or "")
                required_summary = {
                    "changedCodeFiles",
                    "nonTrivialLogicFiles",
                    "matchedSameDiffProofFiles",
                    "missingProofFiles",
                    "inlineCheckFiles",
                    "unmatchedProofSignalCount",
                }
                missing_summary = sorted(key for key in required_summary if key not in summary)
                if missing_summary:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-summary-incomplete",
                        evidence=f"{path_name} proofSignalMatching.summary missing: {', '.join(missing_summary)}",
                        recommendation="Expose changed-code, non-trivial, matched-proof, missing-proof, inline-check, and unmatched-proof counts.",
                    )
                if missing_rule_count and (
                    int(summary.get("missingProofFiles") or 0) < missing_rule_count
                    or not isinstance(rows, list)
                    or len([row for row in rows if isinstance(row, dict) and row.get("matchingDecision") == "missing-proof"])
                    < missing_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-missing-proof-rows-incomplete",
                        evidence=f"{path_name} has {missing_rule_count} missing runnable-check finding(s) but incomplete proofSignalMatching missing-proof rows",
                        recommendation="List every non-trivial changed code file that still lacks matched same-diff proof.",
                    )
                if same_diff_rule_count and (
                    int(summary.get("matchedSameDiffProofFiles") or 0) < same_diff_rule_count
                    or not isinstance(rows, list)
                    or len(
                        [
                            row
                            for row in rows
                            if isinstance(row, dict)
                            and row.get("matchingDecision") == "matched-same-diff-proof"
                            and int(row.get("matchedProofSignalCount") or 0) > 0
                        ]
                    )
                    < same_diff_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-same-diff-rows-incomplete",
                        evidence=f"{path_name} has {same_diff_rule_count} same-diff proof finding(s) but incomplete proofSignalMatching matched rows",
                        recommendation="List each changed code file with its matched same-diff test/assertion proof signal.",
                    )
                signal_count = 0
                if isinstance(calibration, dict):
                    signal_count = int(calibration.get("sameDiffProofSignalCount") or 0)
                matched_signal_count = int(summary.get("matchedProofSignalCount") or 0)
                unmatched_signal_count = int(summary.get("unmatchedProofSignalCount") or 0)
                expected_unmatched = max(0, signal_count - matched_signal_count)
                if signal_count and matched_signal_count + unmatched_signal_count != signal_count:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-counts-incoherent",
                        evidence=f"{path_name} proofSignalMatching matched+unmatched counts do not equal proofSignalCalibration.sameDiffProofSignalCount",
                        recommendation="Keep proofSignalMatching matched and unmatched proof-signal counts coherent with proofSignalCalibration proofSignals.",
                    )
                if expected_unmatched and (
                    unmatched_signal_count < expected_unmatched
                    or not isinstance(unmatched, list)
                    or len(unmatched) < expected_unmatched
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-unmatched-signals-incomplete",
                        evidence=f"{path_name} has proof signals that do not map to same-diff proof findings",
                        recommendation="List unmatched proof signals so unrelated tests cannot satisfy missing proof for another file.",
                    )
                if missing_rule_count and signal_count and (
                    ("unrelated" not in boundary and "unmatched" not in boundary)
                    or ("do not satisfy" not in boundary and "not global" not in boundary)
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-proof-signal-matching-boundary-incomplete",
                        evidence=f"{path_name} proofSignalMatching.nonGlobalProofBoundary does not block unrelated proof overclaims",
                        recommendation="State that unrelated or unmatched proof signals do not satisfy missing proof for other changed files.",
                    )
            runnable_review = report.get("runnableCheckReview")
            if not isinstance(runnable_review, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-runnable-check-review-missing",
                    evidence=f"{path_name} has runnable-check findings but no runnableCheckReview",
                    recommendation="Emit runnableCheckReview with missing-proof rows, same-diff proof rows, and the non-ceremony boundary.",
                )
            else:
                summary = runnable_review.get("summary") if isinstance(runnable_review.get("summary"), dict) else {}
                missing_rows = runnable_review.get("missingProofFindings")
                same_diff_rows = runnable_review.get("sameDiffProofFindings")
                boundary = normalized_question_text(runnable_review.get("nonCeremonyBoundary") or "")
                if missing_rule_count and (
                    int(summary.get("missingRunnableCheckFindings") or 0) < missing_rule_count
                    or not isinstance(missing_rows, list)
                    or len(missing_rows) < missing_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-runnable-check-missing-proof-rows-incomplete",
                        evidence=f"{path_name} has {missing_rule_count} missing runnable-check finding(s) but incomplete runnableCheckReview.missingProofFindings",
                        recommendation="List each changed location that still needs one smallest runnable check.",
                    )
                if same_diff_rule_count and (
                    int(summary.get("sameDiffProofFindings") or 0) < same_diff_rule_count
                    or not isinstance(same_diff_rows, list)
                    or len(same_diff_rows) < same_diff_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-runnable-check-same-diff-proof-rows-incomplete",
                        evidence=f"{path_name} has {same_diff_rule_count} same-diff proof finding(s) but incomplete runnableCheckReview.sameDiffProofFindings",
                        recommendation="List each changed location where same-diff proof should be reviewed instead of requesting duplicate ceremony.",
                    )
                if same_diff_rule_count and int(summary.get("duplicateCeremonyAvoided") or 0) < same_diff_rule_count:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-runnable-check-duplicate-ceremony-count-missing",
                        evidence=f"{path_name} has same-diff proof findings without duplicateCeremonyAvoided coverage",
                        recommendation="Count same-diff proof rows where Lean Review avoided duplicate test ceremony.",
                    )
                if same_diff_rule_count and (
                    "same-diff" not in boundary or "duplicate" not in boundary or "ceremony" not in boundary
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-runnable-check-non-ceremony-boundary-incomplete",
                        evidence=f"{path_name} runnableCheckReview.nonCeremonyBoundary does not explain same-diff duplicate ceremony",
                        recommendation="State that same-diff proof signals still need relevance review but should not trigger duplicate test ceremony.",
                    )
        if proof_related and "Runnable Check Review" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-runnable-check-markdown-missing",
                evidence=f"{path_name} Markdown does not expose runnable check review",
                recommendation="Render runnableCheckReview in Markdown so maintainers see missing checks and same-diff proof signals.",
            )
        if proof_related and "Proof Signal Matching" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-proof-signal-matching-markdown-missing",
                evidence=f"{path_name} Markdown does not expose proof signal matching",
                recommendation="Render proofSignalMatching in Markdown so maintainers see matched and unmatched proof signals.",
            )
        if hardware_rule_count or host_adapter_rule_count:
            boundary_review = report.get("hardwareHostBoundaryReview")
            if not isinstance(boundary_review, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-hardware-host-boundary-review-missing",
                    evidence=f"{path_name} has hardware or host-adapter findings but no hardwareHostBoundaryReview",
                    recommendation="Emit hardwareHostBoundaryReview so Lean Review blocks false less-code pressure on hardware calibration and host adapters.",
                )
            else:
                summary = boundary_review.get("summary") if isinstance(boundary_review.get("summary"), dict) else {}
                hardware_rows = boundary_review.get("hardwareCalibrationFindings")
                host_rows = boundary_review.get("hostAdapterBoundaryFindings")
                policy_text = normalized_question_text(
                    " ".join(
                        str(boundary_review.get(key) or "")
                        for key in ("policy", "hardwareCalibrationPolicy", "hostAdapterPolicy")
                    )
                )
                required_summary = {
                    "hardwareCalibrationFindings",
                    "hostAdapterBoundaryFindings",
                    "falseLessCodePressureBlocked",
                    "proofBlockedHardwareFiles",
                    "keepHostAdapterFiles",
                }
                missing_summary = sorted(key for key in required_summary if key not in summary)
                if missing_summary:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-hardware-host-boundary-summary-incomplete",
                        evidence=f"{path_name} hardwareHostBoundaryReview.summary missing: {', '.join(missing_summary)}",
                        recommendation="Expose hardware, host-adapter, false-pressure, proof-blocked, and keep-boundary counts.",
                    )
                if hardware_rule_count and (
                    int(summary.get("hardwareCalibrationFindings") or 0) < hardware_rule_count
                    or not isinstance(hardware_rows, list)
                    or len(hardware_rows) < hardware_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-hardware-calibration-rows-incomplete",
                        evidence=f"{path_name} has {hardware_rule_count} hardware calibration finding(s) but incomplete hardware rows",
                        recommendation="List every hardware calibration finding with location, recommendation, and proof guidance.",
                    )
                if host_adapter_rule_count and (
                    int(summary.get("hostAdapterBoundaryFindings") or 0) < host_adapter_rule_count
                    or not isinstance(host_rows, list)
                    or len(host_rows) < host_adapter_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-host-adapter-boundary-rows-incomplete",
                        evidence=f"{path_name} has {host_adapter_rule_count} host adapter finding(s) but incomplete host-adapter rows",
                        recommendation="List every host-adapter boundary finding with location, recommendation, and proof guidance.",
                    )
                if hardware_rule_count and (
                    "hardware" not in policy_text
                    or "calibration" not in policy_text
                    or ("device" not in policy_text and "timing" not in policy_text and "sensor" not in policy_text)
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-hardware-calibration-policy-incomplete",
                        evidence=f"{path_name} hardwareHostBoundaryReview policy does not explain calibration or physical-device proof",
                        recommendation="State the hardware calibration proof boundary so source-only less-code pressure cannot remove physical-world tuning.",
                    )
                if host_adapter_rule_count and (
                    "adapter" not in policy_text
                    or "host" not in policy_text
                    or ("protocol" not in policy_text and "plugin" not in policy_text and "runtime" not in policy_text)
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-host-adapter-boundary-policy-incomplete",
                        evidence=f"{path_name} hardwareHostBoundaryReview policy does not explain host adapter proof",
                        recommendation="State that host/plugin/MCP/preview adapters can be the product boundary until protocol or runtime proof says otherwise.",
                    )
                decision_map_for_boundary = report.get("currentDiffDecisionMap")
                if isinstance(decision_map_for_boundary, dict):
                    decisions = decision_map_for_boundary.get("decisions")
                    decision_by_file = {}
                    if isinstance(decisions, list):
                        decision_by_file = {
                            str(row.get("file") or ""): row for row in decisions if isinstance(row, dict)
                        }
                    hardware_files = {
                        str((item.get("evidence") or {}).get("file") or "")
                        for item in findings
                        if isinstance(item, dict)
                        and str(item.get("ruleId") or "") == "hardware-calibration-missing-diff"
                    }
                    bad_hardware = []
                    for file_name in sorted(file for file in hardware_files if file):
                        row = decision_by_file.get(file_name)
                        rule_ids = row.get("ruleIds") if isinstance(row, dict) else []
                        if (
                            not isinstance(row, dict)
                            or row.get("decision") != "proof-blocked"
                            or not isinstance(rule_ids, list)
                            or "hardware-calibration-missing-diff" not in rule_ids
                        ):
                            bad_hardware.append(file_name)
                    if bad_hardware:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-hardware-calibration-decision-map-incomplete",
                            evidence=f"{path_name} currentDiffDecisionMap does not proof-block hardware files: {', '.join(bad_hardware[:5])}",
                            recommendation="Mark hardware calibration files as proof-blocked with hardware-calibration-missing-diff in the current diff decision map.",
                        )
                    host_files = {
                        str((item.get("evidence") or {}).get("file") or "")
                        for item in findings
                        if isinstance(item, dict)
                        and str(item.get("ruleId") or "") == "host-adapter-boundary-diff"
                    }
                    bad_hosts = []
                    for file_name in sorted(file for file in host_files if file):
                        row = decision_by_file.get(file_name)
                        rule_ids = row.get("ruleIds") if isinstance(row, dict) else []
                        if (
                            not isinstance(row, dict)
                            or row.get("decision") != "keep"
                            or not isinstance(rule_ids, list)
                            or "host-adapter-boundary-diff" not in rule_ids
                        ):
                            bad_hosts.append(file_name)
                    if bad_hosts:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-host-adapter-decision-map-incomplete",
                            evidence=f"{path_name} currentDiffDecisionMap does not keep host-adapter files: {', '.join(bad_hosts[:5])}",
                            recommendation="Mark host-adapter files as keep with host-adapter-boundary-diff in the current diff decision map.",
                        )
            required_boundary_markdown = ["Hardware And Host Boundary Review"]
            if hardware_rule_count:
                required_boundary_markdown.append("Hardware Calibration Proof")
            if host_adapter_rule_count:
                required_boundary_markdown.append("Host Adapter Boundaries")
            missing_boundary_markdown = [token for token in required_boundary_markdown if token not in markdown]
            if missing_boundary_markdown:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-hardware-host-boundary-markdown-missing",
                    evidence=f"{path_name} Markdown missing boundary review tokens: {', '.join(missing_boundary_markdown)}",
                    recommendation="Render hardwareHostBoundaryReview in Markdown so maintainers see calibration and host-adapter keep/proof guidance.",
                )
        if safety_rule_count:
            safety_review = report.get("safetyBoundaryReview")
            if not isinstance(safety_review, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-safety-boundary-review-missing",
                    evidence=f"{path_name} has safety-boundary findings but no safetyBoundaryReview",
                    recommendation="Emit safetyBoundaryReview so Lean Review proves safety code stays out of automatic deletion pressure.",
                )
            else:
                summary = safety_review.get("summary") if isinstance(safety_review.get("summary"), dict) else {}
                safety_rows = safety_review.get("safetyBoundaryFindings")
                policy_text = normalized_question_text(
                    " ".join(
                        str(safety_review.get(key) or "")
                        for key in ("policy", "automaticDeletionBoundary")
                    )
                )
                required_summary = {
                    "safetyBoundaryFindings",
                    "falseDeletionPressureBlocked",
                    "keepSafetyBoundaryFiles",
                }
                missing_summary = sorted(key for key in required_summary if key not in summary)
                if missing_summary:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-safety-boundary-summary-incomplete",
                        evidence=f"{path_name} safetyBoundaryReview.summary missing: {', '.join(missing_summary)}",
                        recommendation="Expose safety-boundary row counts, false deletion pressure blocked, and keep-file counts.",
                    )
                if (
                    int(summary.get("safetyBoundaryFindings") or 0) < safety_rule_count
                    or not isinstance(safety_rows, list)
                    or len(safety_rows) < safety_rule_count
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-safety-boundary-rows-incomplete",
                        evidence=f"{path_name} has {safety_rule_count} safety-boundary finding(s) but incomplete safety rows",
                        recommendation="List every safety-boundary finding with location, recommendation, and proof guidance.",
                    )
                if isinstance(safety_rows, list):
                    required_row_fields = {"file", "location", "ruleId", "recommendation", "proofGuidance"}
                    malformed_rows = []
                    for index, row in enumerate(safety_rows):
                        if not isinstance(row, dict):
                            malformed_rows.append(f"row {index}")
                            continue
                        missing_fields = sorted(
                            field
                            for field in required_row_fields
                            if not str(row.get(field) or "").strip()
                        )
                        if str(row.get("ruleId") or "") != "do-not-cut-safety-diff-without-proof":
                            missing_fields.append("ruleId=do-not-cut-safety-diff-without-proof")
                        if missing_fields:
                            malformed_rows.append(f"row {index} missing {', '.join(missing_fields)}")
                    if malformed_rows:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-safety-boundary-row-fields-incomplete",
                            evidence=f"{path_name} safetyBoundaryReview rows incomplete: {'; '.join(malformed_rows[:5])}",
                            recommendation="Each safety-boundary row must include file, location, ruleId, recommendation, and proofGuidance.",
                        )
                if (
                    "safety" not in policy_text
                    or "proof" not in policy_text
                    or ("delete" not in policy_text and "deletion" not in policy_text)
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-safety-boundary-policy-incomplete",
                        evidence=f"{path_name} safetyBoundaryReview policy does not explain the no-automatic-deletion proof boundary",
                        recommendation="State that safety-boundary rows are keep-with-proof decisions and cannot be deleted from source-only less-code pressure.",
                    )
                decision_map_for_safety = report.get("currentDiffDecisionMap")
                if isinstance(decision_map_for_safety, dict):
                    decisions = decision_map_for_safety.get("decisions")
                    decision_by_file = {}
                    if isinstance(decisions, list):
                        decision_by_file = {
                            str(row.get("file") or ""): row for row in decisions if isinstance(row, dict)
                        }
                    safety_files = {
                        str((item.get("evidence") or {}).get("file") or "")
                        for item in findings
                        if isinstance(item, dict)
                        and str(item.get("ruleId") or "") == "do-not-cut-safety-diff-without-proof"
                    }
                    bad_safety = []
                    for file_name in sorted(file for file in safety_files if file):
                        row = decision_by_file.get(file_name)
                        rule_ids = row.get("ruleIds") if isinstance(row, dict) else []
                        if (
                            not isinstance(row, dict)
                            or row.get("decision") != "keep"
                            or not isinstance(rule_ids, list)
                            or "do-not-cut-safety-diff-without-proof" not in rule_ids
                        ):
                            bad_safety.append(file_name)
                    if bad_safety:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-safety-boundary-decision-map-incomplete",
                            evidence=f"{path_name} currentDiffDecisionMap does not keep safety-boundary files: {', '.join(bad_safety[:5])}",
                            recommendation="Mark safety-boundary files as keep with do-not-cut-safety-diff-without-proof in the current diff decision map.",
                        )
            required_safety_markdown = ["Safety Boundary Review", "Keep With Proof Boundaries"]
            missing_safety_markdown = [token for token in required_safety_markdown if token not in markdown]
            if missing_safety_markdown:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-safety-boundary-markdown-missing",
                    evidence=f"{path_name} Markdown missing safety-boundary tokens: {', '.join(missing_safety_markdown)}",
                    recommendation="Render safetyBoundaryReview in Markdown so maintainers see safety keep/proof guidance.",
                )
            elif isinstance(safety_review, dict):
                safety_rows = safety_review.get("safetyBoundaryFindings")
                safety_section = markdown.split("Keep With Proof Boundaries", 1)[1]
                missing_safety_rows = []
                if isinstance(safety_rows, list):
                    for row in safety_rows:
                        if not isinstance(row, dict):
                            continue
                        location = str(row.get("location") or "").strip()
                        file_name = str(row.get("file") or "").strip()
                        token = location or file_name
                        if token and token not in safety_section:
                            missing_safety_rows.append(token)
                if missing_safety_rows:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-review-safety-boundary-markdown-rows-missing",
                        evidence=f"{path_name} Markdown safety table missing rows: {', '.join(missing_safety_rows[:5])}",
                        recommendation="Render each safetyBoundaryReview row in the Markdown Keep With Proof Boundaries table.",
                    )
        decision_map = report.get("currentDiffDecisionMap")
        if not isinstance(decision_map, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-review-current-diff-map-missing",
                evidence=f"{path_name} has no currentDiffDecisionMap",
                recommendation="Emit a currentDiffDecisionMap so Lean Review proves it is scoped to the supplied diff rather than a whole-repo inventory.",
            )
        else:
            scope = str(decision_map.get("scope") or "").strip()
            boundary_text = normalized_question_text(decision_map.get("inventoryBoundary") or "")
            if scope != "current-diff-only":
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-scope-invalid",
                    evidence=f"{path_name} currentDiffDecisionMap.scope={scope!r}",
                    recommendation="Set currentDiffDecisionMap.scope to current-diff-only so readers know this is not a repo-wide audit.",
                )
            if (
                "diff" not in boundary_text
                or "whole-repo" not in boundary_text
                or ("does not" not in boundary_text and "not scan" not in boundary_text)
            ):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-boundary-incomplete",
                    evidence=f"{path_name} currentDiffDecisionMap.inventoryBoundary does not block whole-repo inventory overclaims",
                    recommendation="State that Lean Review uses only the supplied unified diff and does not scan the whole repo or claim whole-repo inventory coverage.",
                )
            summary = decision_map.get("summary") if isinstance(decision_map.get("summary"), dict) else {}
            required_summary = {
                "filesChanged",
                "addedLinesInspected",
                "removedLinesSeen",
                "decisionRows",
                "deleteCandidates",
                "simplifyCandidates",
                "keepBoundaries",
                "proofBlockedCandidates",
                "cleanFiles",
            }
            missing_summary = sorted(key for key in required_summary if key not in summary)
            if missing_summary:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-summary-incomplete",
                    evidence=f"{path_name} currentDiffDecisionMap.summary missing: {', '.join(missing_summary)}",
                    recommendation="Expose changed-file, line, decision, delete, simplify, keep, proof-blocked, and clean counts in the current diff map.",
                )
            decisions = decision_map.get("decisions")
            files_changed = int(summary.get("filesChanged") or report.get("metrics", {}).get("filesChanged") or 0)
            if files_changed > 0 and (not isinstance(decisions, list) or not decisions):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-decisions-missing",
                    evidence=f"{path_name} has {files_changed} changed file(s) but no current diff decision rows",
                    recommendation="Emit one currentDiffDecisionMap.decisions row per changed file so a maintainer sees delete/simplify/keep/proof-blocked/clean decisions.",
                )
            elif isinstance(decisions, list):
                required_decision_fields = {
                    "file",
                    "source",
                    "decision",
                    "addedLines",
                    "removedLines",
                    "firstExperiment",
                    "validationRoute",
                    "stopCondition",
                }
                valid_decisions = {"delete", "simplify", "keep", "proof-blocked", "clean"}
                for index, row in enumerate(decisions[:12], start=1):
                    if not isinstance(row, dict):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-current-diff-decision-invalid",
                            evidence=f"{path_name} currentDiffDecisionMap.decisions[{index}] is not an object",
                            recommendation="Emit each current diff decision as a structured row.",
                        )
                        continue
                    missing_fields = sorted(field for field in required_decision_fields if field not in row or row.get(field) in {"", None})
                    if missing_fields:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-current-diff-decision-incomplete",
                            evidence=f"{path_name} currentDiffDecisionMap.decisions[{index}] missing: {', '.join(missing_fields)}",
                            recommendation="Each current diff decision needs file, source, decision, changed-line counts, first experiment, validation route, and stop condition.",
                        )
                    if str(row.get("source") or "") != "unified-diff":
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-current-diff-decision-source-invalid",
                            evidence=f"{path_name} currentDiffDecisionMap.decisions[{index}].source={row.get('source')!r}",
                            recommendation="Mark every Lean Review decision source as unified-diff so it cannot be confused with a whole-repo inventory row.",
                        )
                    if str(row.get("decision") or "") not in valid_decisions:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-review-current-diff-decision-kind-invalid",
                            evidence=f"{path_name} currentDiffDecisionMap.decisions[{index}].decision={row.get('decision')!r}",
                            recommendation="Use one of delete, simplify, keep, proof-blocked, or clean for current diff decisions.",
                        )
            delete_or_simplify = decision_map.get("deleteOrSimplifyList")
            precision = report.get("precisionReview") if isinstance(report.get("precisionReview"), dict) else {}
            precision_summary = precision.get("summary") if isinstance(precision.get("summary"), dict) else {}
            has_delete_or_simplify = int(precision_summary.get("deleteCandidates") or 0) > 0 or int(
                precision_summary.get("simplifyCandidates") or 0
            ) > 0
            if has_delete_or_simplify and not isinstance(delete_or_simplify, list):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-delete-simplify-list-missing",
                    evidence=f"{path_name} has delete/simplify precision candidates but no currentDiffDecisionMap.deleteOrSimplifyList",
                    recommendation="Expose the current-diff delete/simplify subset so maintainers do not read a whole precision ledger to find the first diff cleanup action.",
                )
            markdown_required = [
                "Current Diff Decision Map",
                "current-diff-only",
                "does not scan the whole repo",
                "shipguard lean audit",
            ]
            missing_markdown = [token for token in markdown_required if token not in markdown]
            if missing_markdown:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-review-current-diff-markdown-incomplete",
                    evidence=f"{path_name} Markdown missing current diff decision tokens: {', '.join(missing_markdown)}",
                    recommendation="Render the current diff decision map, current-diff-only boundary, whole-repo non-claim, and lean-audit fallback in Markdown.",
                )
    if tool == "shipguard lean audit":
        findings = report.get("findings") if isinstance(report.get("findings"), list) else []
        large_findings = [
            item
            for item in findings
            if isinstance(item, dict) and str(item.get("ruleId") or "") == "large-legacy-file-review"
        ]
        for index, item in enumerate(large_findings[:8], start=1):
            evidence = item.get("leanEvidence")
            if not isinstance(evidence, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-large-file-evidence-missing",
                    evidence=f"{path_name} large-legacy-file-review[{index}] has no leanEvidence packet",
                    recommendation="Attach leanEvidence with line count, marker count, first marker lines, marker policy, and the first action hint.",
                )
                continue
            first_markers = evidence.get("firstMarkerLines")
            if int(evidence.get("markerCount") or 0) < 1 or not isinstance(first_markers, list) or not first_markers:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-large-file-marker-evidence-missing",
                    evidence=f"{path_name} large-legacy-file-review[{index}] does not expose actionable marker lines",
                    recommendation="Large-file findings should point at concrete TODO/FIXME/comment markers instead of broad file-size pressure.",
                )
            if not evidence.get("markerPolicy"):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-large-file-marker-policy-missing",
                    evidence=f"{path_name} large-legacy-file-review[{index}] does not explain marker filtering",
                    recommendation="Expose markerPolicy so maintainers know incidental strings and API names were not treated as debt markers.",
                )
            if not evidence.get("actionHint"):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-large-file-action-hint-missing",
                    evidence=f"{path_name} large-legacy-file-review[{index}] has no first action hint",
                    recommendation="Tell maintainers where to start so large-file findings do not become vague rewrite pressure.",
                )
        if large_findings and "Lean Evidence Packets" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-large-file-evidence-markdown-missing",
                evidence=f"{path_name} Markdown does not expose Lean Evidence Packets",
                recommendation="Render leanEvidence in Markdown so the proof packet is visible without opening JSON.",
            )
    if tool in {"shipguard lean audit", "shipguard lean review"}:
        precision = report.get("precisionReview")
        if isinstance(precision, dict):
            summary = precision.get("summary") if isinstance(precision.get("summary"), dict) else {}
            has_precision_work = any(
                int(summary.get(key) or 0) > 0
                for key in ("deleteCandidates", "simplifyCandidates", "proofBlockedCandidates")
            ) or bool(precision.get("topActions"))
            is_clean_pass_state = (
                str(report.get("status") or "") == "pass"
                and not has_precision_work
                and int(summary.get("actionGroups") or 0) == 0
            )
            if has_precision_work:
                groups = precision.get("actionGroups")
                if not isinstance(groups, list) or not groups:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-action-groups-missing",
                        evidence=f"{path_name} has precision findings but no precisionReview.actionGroups",
                        recommendation="Group repeated Lean findings into actionGroups with a first experiment, validation route, and stop condition.",
                    )
                else:
                    required = {
                        "decision",
                        "ruleId",
                        "evidenceCount",
                        "firstLocation",
                        "firstExperiment",
                        "validationRoute",
                        "stopCondition",
                    }
                    for index, group in enumerate(groups[:8], start=1):
                        if not isinstance(group, dict):
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="lean-action-group-invalid",
                                evidence=f"{path_name} actionGroups[{index}] is not an object",
                                recommendation="Emit every action group as a structured object so agents can follow the plan deterministically.",
                            )
                            continue
                        missing = sorted(key for key in required if not group.get(key))
                        if missing:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="lean-action-group-incomplete",
                                evidence=f"{path_name} actionGroups[{index}] missing: {', '.join(missing)}",
                                recommendation="Each Lean action group should explain what to inspect first, how to prove it, and when to stop.",
                            )
                        if int(group.get("evidenceCount") or 0) < 1:
                            add_issue(
                                issues,
                                severity="review",
                                rule_id="lean-action-group-count-missing",
                                evidence=f"{path_name} actionGroups[{index}] has no evidence count",
                                recommendation="Set evidenceCount so repeated findings are summarized instead of hidden.",
                            )
                if "Grouped Action Plan" not in markdown:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-action-groups-markdown-missing",
                        evidence=f"{path_name} Markdown does not expose the grouped action plan",
                        recommendation="Render precisionReview.actionGroups in Markdown so maintainers see the bounded plan before individual findings.",
                    )
            if is_clean_pass_state:
                clean = precision.get("cleanStateAction")
                if not isinstance(clean, dict):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-clean-state-action-missing",
                        evidence=f"{path_name} is pass with no Lean action groups but no precisionReview.cleanStateAction",
                        recommendation="Emit a clean-state action so pass reports still tell maintainers what proof probe or next loop to run.",
                    )
                else:
                    required = {
                        "kind",
                        "summary",
                        "firstExperiment",
                        "evidenceCommand",
                        "nextCommand",
                        "validationRoute",
                        "stopCondition",
                    }
                    missing = sorted(key for key in required if not clean.get(key))
                    if missing:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-clean-state-action-incomplete",
                            evidence=f"{path_name} cleanStateAction missing: {', '.join(missing)}",
                            recommendation="Clean pass reports should include the first proof probe, exact next command, validation route, and stop condition.",
                        )
                if "Clean State Action" not in markdown:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-clean-state-action-markdown-missing",
                        evidence=f"{path_name} Markdown does not expose the clean-state action",
                        recommendation="Render cleanStateAction in Markdown so a pass report remains actionable without opening JSON.",
                    )
    if tool == "shipguard lean gain":
        boundary = report.get("currentRepoBoundary")
        if not isinstance(boundary, dict) or boundary.get("perRepoSavingsClaim") != "not-computed":
            add_issue(
                issues,
                severity="high",
                rule_id="lean-gain-fake-repo-savings-risk",
                evidence=f"{path_name} does not explicitly mark current-repo savings as not-computed",
                recommendation="Do not claim local line, token, cost, or time savings without a matched untreated baseline.",
            )
        elif not boundary.get("reason"):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-current-boundary-incomplete",
                evidence=f"{path_name} currentRepoBoundary has no reason for the not-computed claim",
                recommendation="Explain why current-repo savings are not computed so maintainers cannot turn benchmark direction into a local claim.",
            )
        repo_signals = boundary.get("realRepoSignals") if isinstance(boundary, dict) else None
        repo_signal_text = " ".join(str(item).lower() for item in repo_signals) if isinstance(repo_signals, list) else ""
        missing_signal_routes = [
            label
            for label in ("lean audit", "lean review", "lean debt")
            if label not in repo_signal_text
        ]
        if not isinstance(repo_signals, list) or missing_signal_routes:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-current-routing-missing",
                evidence=f"{path_name} currentRepoBoundary.realRepoSignals missing routes: {', '.join(missing_signal_routes) or 'realRepoSignals list'}",
                recommendation="Route current-repo evidence back to lean audit, lean review, and lean debt instead of implying the benchmark measured this repo.",
            )
        expected_routes = {
            "lean-audit": "shipguard lean audit",
            "lean-review": "shipguard lean review",
            "lean-debt": "shipguard lean debt",
        }
        evidence_routes = boundary.get("evidenceRoutes") if isinstance(boundary, dict) else None
        if not isinstance(evidence_routes, list) or not evidence_routes:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-current-route-contract-missing",
                evidence=f"{path_name} currentRepoBoundary has no structured evidenceRoutes",
                recommendation="Add evidenceRoutes for lean audit, lean review, and lean debt with command, artifact, answer, proof boundary, and non-claim text.",
            )
        else:
            routes_by_id = {
                str(route.get("id") or "").strip(): route
                for route in evidence_routes
                if isinstance(route, dict)
            }
            missing_routes = sorted(route_id for route_id in expected_routes if route_id not in routes_by_id)
            if missing_routes:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-gain-current-route-contract-incomplete",
                    evidence=f"{path_name} evidenceRoutes missing: {', '.join(missing_routes)}",
                    recommendation="Emit one current-repo evidence route each for lean-audit, lean-review, and lean-debt.",
                )
            for route_id, command_token in expected_routes.items():
                route = routes_by_id.get(route_id)
                if not isinstance(route, dict):
                    continue
                required_route_fields = {"command", "expectedArtifact", "answers", "proofBoundary", "nonClaim"}
                missing_route_fields = sorted(field for field in required_route_fields if not str(route.get(field) or "").strip())
                command = str(route.get("command") or "")
                boundary_text = normalized_question_text(route.get("proofBoundary") or "")
                non_claim = normalized_question_text(route.get("nonClaim") or "")
                if missing_route_fields or command_token not in command:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-gain-current-route-incomplete",
                        evidence=(
                            f"{path_name} evidenceRoutes[{route_id}] missing: "
                            f"{', '.join(missing_route_fields) or f'command containing {command_token}'}"
                        ),
                        recommendation="Make each Lean Gain evidence route copy-ready and tied to the exact Lean command that proves that current-repo signal.",
                    )
                if "does not prove" not in boundary_text or "savings" not in boundary_text:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-gain-current-route-boundary-incomplete",
                        evidence=f"{path_name} evidenceRoutes[{route_id}] proofBoundary does not block savings overclaims",
                        recommendation="State that each current-repo route proves only its own signal and does not prove line, token, cost, or time savings.",
                    )
                if "do not" not in non_claim or "savings" not in non_claim:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-gain-current-route-nonclaim-incomplete",
                        evidence=f"{path_name} evidenceRoutes[{route_id}] nonClaim does not explicitly block savings claims",
                        recommendation="Add nonClaim text so current-repo evidence cannot be recast as benchmark or per-repo savings.",
                    )
        scoreboard = report.get("benchmarkScoreboard")
        primary = scoreboard.get("primary") if isinstance(scoreboard, dict) else None
        if not isinstance(primary, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-scoreboard-missing",
                evidence=f"{path_name} has no benchmarkScoreboard.primary",
                recommendation="Show benchmark-backed impact separately from current-repo evidence.",
            )
        else:
            required_primary = {"label", "baseline", "scope", "method", "remainingPercentOfBaseline", "reportedChange"}
            missing_primary = sorted(key for key in required_primary if not primary.get(key))
            scope_text = str(primary.get("scope") or "").lower()
            if missing_primary or "not this repository" not in scope_text:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-gain-scoreboard-incomplete",
                    evidence=f"{path_name} benchmarkScoreboard.primary missing: {', '.join(missing_primary) or 'explicit non-repo scope'}",
                    recommendation="Keep the benchmark label, baseline, method, and non-repo scope visible so benchmark direction cannot become a launch claim for this checkout.",
                )
            remaining = primary.get("remainingPercentOfBaseline")
            reported = primary.get("reportedChange")
            metric_keys = {"linesOfCode", "tokens", "cost", "time", "safety"}
            missing_remaining = sorted(
                key
                for key in metric_keys
                if not isinstance(remaining, dict) or not isinstance(remaining.get(key), (int, float))
            )
            missing_reported = sorted(
                key
                for key in metric_keys
                if not isinstance(reported, dict) or not str(reported.get(key) or "").strip()
            )
            if missing_remaining or missing_reported:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-gain-scoreboard-metrics-missing",
                    evidence=f"{path_name} missing benchmark metrics: remaining={', '.join(missing_remaining) or '-'} reported={', '.join(missing_reported) or '-'}",
                    recommendation="Emit every Lean Gain metric in both remaining-percent and reported-change form so the benchmark card is reviewable.",
                )
        markdown_required = [
            "Benchmark Scoreboard",
            "Honesty Boundary",
            "not-computed",
            "Current Repo Signals",
            "Current Repo Evidence Routes",
            "shipguard lean audit",
            "shipguard lean review",
            "shipguard lean debt",
            "Do not claim current-repo line, token, cost, or time savings",
        ]
        missing_markdown = [token for token in markdown_required if token not in markdown]
        if "Honesty Boundary" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-honesty-markdown-missing",
                evidence=f"{path_name} Markdown does not expose the honesty boundary",
                recommendation="Render the no-per-repo-savings boundary in Markdown, not only JSON.",
            )
        elif missing_markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-gain-honesty-markdown-incomplete",
                evidence=f"{path_name} Markdown missing Lean Gain honesty tokens: {', '.join(missing_markdown)}",
                recommendation="Render benchmark scope, not-computed current-repo status, current repo signals, and no-claim language in Markdown.",
            )
    if tool in {"shipguard lean audit", "shipguard lean debt"}:
        ledger = report.get("leanDebtLedger")
        if not isinstance(ledger, dict):
            add_issue(
                issues,
                severity="review",
                rule_id="lean-debt-ledger-missing",
                evidence=f"{path_name} has no leanDebtLedger object",
                recommendation="Emit leanDebtLedger so intentional shortcuts stay visible with ceilings and upgrade triggers.",
            )
        else:
            summary = ledger.get("summary") if isinstance(ledger.get("summary"), dict) else {}
            required_summary = {"markers", "missingUpgradeTrigger", "omittedByLimit"}
            missing_summary = sorted(key for key in required_summary if key not in summary)
            if missing_summary:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-ledger-summary-missing",
                    evidence=f"{path_name} leanDebtLedger.summary missing: {', '.join(missing_summary)}",
                    recommendation="Report marker count, missing-trigger count, and omitted-by-limit count so shortcut debt is auditable.",
                )
            markers = ledger.get("markers")
            if markers is not None and not isinstance(markers, list):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-ledger-markers-invalid",
                    evidence=f"{path_name} leanDebtLedger.markers is not a list",
                    recommendation="Emit shortcut markers as structured rows with file, line, marker, status, ceiling, and upgrade trigger fields.",
                )
            elif isinstance(markers, list):
                required_marker = {"file", "line", "marker", "status", "summary", "ceiling", "hasUpgradeTrigger"}
                for index, item in enumerate(markers[:20], start=1):
                    if not isinstance(item, dict):
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-ledger-marker-invalid",
                            evidence=f"{path_name} leanDebtLedger.markers[{index}] is not an object",
                            recommendation="Emit every shortcut marker as a structured row so maintainers can review it without source inspection.",
                        )
                        continue
                    missing_marker = sorted(key for key in required_marker if item.get(key) in (None, ""))
                    if missing_marker:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-ledger-marker-incomplete",
                            evidence=f"{path_name} leanDebtLedger.markers[{index}] missing: {', '.join(missing_marker)}",
                            recommendation="Every shortcut marker should show location, marker label, status, shortcut summary, ceiling, and whether an upgrade trigger exists.",
                        )
                    has_trigger = item.get("hasUpgradeTrigger") is True
                    status = str(item.get("status") or "")
                    upgrade = str(item.get("upgrade") or "")
                    if has_trigger and not upgrade:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-ledger-upgrade-missing",
                            evidence=f"{path_name} leanDebtLedger.markers[{index}] claims a trigger but has no upgrade text",
                            recommendation="Keep the trigger text next to the marker so the shortcut has an actionable upgrade path.",
                        )
                    if not has_trigger and status != "needs-trigger":
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-ledger-trigger-status-missing",
                            evidence=f"{path_name} leanDebtLedger.markers[{index}] lacks an upgrade trigger but is not marked needs-trigger",
                            recommendation="Mark shortcut markers without upgrade text as needs-trigger so they cannot look complete.",
                        )
        marker_count = 0
        if isinstance(ledger, dict):
            summary = ledger.get("summary") if isinstance(ledger.get("summary"), dict) else {}
            marker_count = int(summary.get("markers") or 0)
        has_ledger_heading = "Lean Debt Ledger" in markdown or "Shortcut Ledger" in markdown
        missing_marker_columns = marker_count > 0 and ("Ceiling" not in markdown or "Upgrade Trigger" not in markdown)
        if not has_ledger_heading or missing_marker_columns:
            add_issue(
                issues,
                severity="review",
                rule_id="lean-debt-ledger-markdown-missing",
                evidence=f"{path_name} Markdown does not expose the shortcut ledger with ceiling and upgrade-trigger columns",
                recommendation="Render the Lean Debt Ledger in Markdown so maintainers can audit shortcut ceilings and upgrade triggers without opening JSON.",
            )
        if tool == "shipguard lean debt":
            ledger_summary = ledger.get("summary") if isinstance(ledger, dict) and isinstance(ledger.get("summary"), dict) else {}
            ledger_markers = ledger.get("markers") if isinstance(ledger, dict) and isinstance(ledger.get("markers"), list) else []
            marker_review = report.get("markerVisibilityReview")
            if not isinstance(marker_review, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-marker-visibility-review-missing",
                    evidence=f"{path_name} has no markerVisibilityReview object",
                    recommendation="Emit markerVisibilityReview so standalone Lean Debt proves every shortcut row is visible with ceiling and upgrade-trigger status.",
                )
            else:
                review_summary = marker_review.get("summary") if isinstance(marker_review.get("summary"), dict) else {}
                visibility_rows = marker_review.get("visibilityRows")
                required_summary = {
                    "totalMarkers",
                    "visibleMarkerRows",
                    "omittedByLimit",
                    "omittedStateUnknown",
                    "rowsWithCeiling",
                    "rowsMissingCeiling",
                    "rowsWithUpgradeTrigger",
                    "rowsNeedingUpgradeTrigger",
                    "rowsWithUpgradeStatus",
                }
                missing_summary = sorted(key for key in required_summary if key not in review_summary)
                if missing_summary:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-summary-missing",
                        evidence=f"{path_name} markerVisibilityReview.summary missing: {', '.join(missing_summary)}",
                        recommendation="Summarize total, visible, omitted, ceiling, and upgrade-trigger-state marker counts.",
                    )
                if not isinstance(visibility_rows, list):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-rows-invalid",
                        evidence=f"{path_name} markerVisibilityReview.visibilityRows is not a list",
                        recommendation="Emit every visible shortcut marker as a structured visibility row.",
                    )
                    visibility_rows = []
                expected_marker_count = int(ledger_summary.get("markers") or 0)
                expected_visible_rows = len(ledger_markers)
                row_objects = [row for row in visibility_rows if isinstance(row, dict)]
                rows_with_ceiling = sum(
                    1 for row in row_objects if row.get("hasCeiling") is True and str(row.get("ceiling") or "").strip()
                )
                rows_with_upgrade = sum(
                    1
                    for row in row_objects
                    if row.get("hasUpgradeTrigger") is True and str(row.get("upgradeTrigger") or "").strip()
                )
                rows_with_upgrade_status = sum(1 for row in row_objects if row.get("exposesUpgradeStatus") is True)
                rows_missing_ceiling = max(0, len(row_objects) - rows_with_ceiling)
                count_mismatches = []
                if int(review_summary.get("totalMarkers") or 0) != expected_marker_count:
                    count_mismatches.append("totalMarkers")
                if int(review_summary.get("visibleMarkerRows") or 0) != expected_visible_rows:
                    count_mismatches.append("visibleMarkerRows")
                if int(review_summary.get("omittedByLimit") or 0) != int(ledger_summary.get("omittedByLimit") or 0):
                    count_mismatches.append("omittedByLimit")
                if int(ledger_summary.get("omittedByLimit") or 0) > 0 and review_summary.get("omittedStateUnknown") is not True:
                    count_mismatches.append("omittedStateUnknown")
                if int(ledger_summary.get("omittedByLimit") or 0) == 0 and review_summary.get("omittedStateUnknown") is not False:
                    count_mismatches.append("omittedStateUnknown")
                if int(review_summary.get("rowsNeedingUpgradeTrigger") or 0) != max(0, len(row_objects) - rows_with_upgrade):
                    count_mismatches.append("rowsNeedingUpgradeTrigger")
                if int(review_summary.get("rowsWithCeiling") or 0) != rows_with_ceiling:
                    count_mismatches.append("rowsWithCeiling")
                if int(review_summary.get("rowsMissingCeiling") or 0) != rows_missing_ceiling:
                    count_mismatches.append("rowsMissingCeiling")
                if int(review_summary.get("rowsWithUpgradeTrigger") or 0) != rows_with_upgrade:
                    count_mismatches.append("rowsWithUpgradeTrigger")
                if int(review_summary.get("rowsWithUpgradeStatus") or 0) != rows_with_upgrade_status:
                    count_mismatches.append("rowsWithUpgradeStatus")
                if isinstance(visibility_rows, list) and len(visibility_rows) != expected_visible_rows:
                    count_mismatches.append("visibilityRows")
                if count_mismatches:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-counts-mismatch",
                        evidence=f"{path_name} markerVisibilityReview count mismatch: {', '.join(sorted(set(count_mismatches)))}",
                        recommendation="Keep markerVisibilityReview counts aligned with leanDebtLedger so the review cannot hide omitted or missing-trigger rows.",
                    )
                if marker_count and (
                    marker_review.get("allMarkersVisible") is not True
                    and int(ledger_summary.get("omittedByLimit") or 0) == 0
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-flag-incomplete",
                        evidence=f"{path_name} markerVisibilityReview does not confirm all non-omitted markers are visible",
                        recommendation="Set allMarkersVisible only from ledger counts and omitted rows so visible coverage is machine-checkable.",
                    )
                malformed_rows = []
                row_required_text = {"file", "line", "location", "marker", "status", "summary"}
                row_required_keys = row_required_text | {
                    "ceiling",
                    "upgradeTrigger",
                    "hasCeiling",
                    "hasUpgradeTrigger",
                    "exposesUpgradeStatus",
                }
                if isinstance(visibility_rows, list):
                    for index, row in enumerate(visibility_rows[:20], start=1):
                        if not isinstance(row, dict):
                            malformed_rows.append(f"row {index} not object")
                            continue
                        missing_keys = sorted(key for key in row_required_keys if key not in row)
                        missing_text = sorted(key for key in row_required_text if str(row.get(key) or "").strip() == "")
                        missing_bool = sorted(
                            key
                            for key in ("hasCeiling", "hasUpgradeTrigger", "exposesUpgradeStatus")
                            if not isinstance(row.get(key), bool)
                        )
                        if missing_keys or missing_text or missing_bool:
                            parts = []
                            if missing_keys:
                                parts.append(f"missing keys {', '.join(missing_keys)}")
                            if missing_text:
                                parts.append(f"blank fields {', '.join(missing_text)}")
                            if missing_bool:
                                parts.append(f"non-boolean {', '.join(missing_bool)}")
                            malformed_rows.append(f"row {index} {'; '.join(parts)}")
                        has_ceiling = row.get("hasCeiling")
                        ceiling_text = str(row.get("ceiling") or "").strip()
                        if has_ceiling is True and not ceiling_text:
                            malformed_rows.append(f"row {index} claims ceiling but has no ceiling text")
                        if has_ceiling is False and ceiling_text:
                            malformed_rows.append(f"row {index} has ceiling text but hasCeiling is false")
                        has_upgrade = row.get("hasUpgradeTrigger")
                        upgrade_text = str(row.get("upgradeTrigger") or "").strip()
                        if has_upgrade is True and not upgrade_text:
                            malformed_rows.append(f"row {index} claims upgrade trigger but has no trigger text")
                        if row.get("hasUpgradeTrigger") is False and str(row.get("status") or "") != "needs-trigger":
                            malformed_rows.append(f"row {index} missing trigger without needs-trigger status")
                if malformed_rows:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-row-fields-incomplete",
                        evidence=f"{path_name} markerVisibilityReview rows incomplete: {'; '.join(malformed_rows[:5])}",
                        recommendation="Each marker visibility row should include location, marker, summary, ceiling, trigger text field, and boolean trigger-state fields.",
                    )
                required_visibility_markdown = [
                    "Marker Visibility Review",
                    "All markers visible",
                    "Rows with ceiling",
                    "Rows needing upgrade trigger",
                    "Rows with upgrade status",
                ]
                missing_visibility_markdown = [token for token in required_visibility_markdown if token not in markdown]
                if missing_visibility_markdown:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-marker-visibility-markdown-missing",
                        evidence=f"{path_name} Markdown missing marker visibility tokens: {', '.join(missing_visibility_markdown)}",
                        recommendation="Render markerVisibilityReview in Markdown before the raw ledger table.",
                    )
                elif isinstance(visibility_rows, list):
                    visibility_section = markdown.split("Marker Visibility Review", 1)[1]
                    visibility_section = visibility_section.split("\n## ", 1)[0]
                    missing_rows = []
                    for row in visibility_rows[:20]:
                        if not isinstance(row, dict):
                            continue
                        location = str(row.get("location") or "").strip()
                        if location and location not in visibility_section:
                            missing_rows.append(location)
                    if missing_rows:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-marker-visibility-markdown-rows-missing",
                            evidence=f"{path_name} Marker Visibility Review Markdown missing rows: {', '.join(missing_rows[:5])}",
                            recommendation="Render each marker visibility row in Markdown so the ledger can be reviewed without opening JSON.",
                        )
            rot_review = report.get("rotRiskReview")
            if not isinstance(rot_review, dict):
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-rot-risk-review-missing",
                    evidence=f"{path_name} has no rotRiskReview object",
                    recommendation="Emit rotRiskReview so standalone Lean Debt tells maintainers which shortcut marker will rot first and why.",
                )
            else:
                try:
                    lean_debt_schema_version = int(report.get("schemaVersion") or 1)
                except (TypeError, ValueError):
                    lean_debt_schema_version = 1
                trigger_watch_required = lean_debt_schema_version >= 2
                if not trigger_watch_required:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-trigger-watch-schema-outdated",
                        evidence=f"{path_name} schemaVersion {lean_debt_schema_version} predates Lean Debt triggerWatchContract rows",
                        recommendation="Regenerate the source report with the current shipguard lean debt so trigger-watch contracts are available for report-quality scoring.",
                    )
                rot_summary = rot_review.get("summary") if isinstance(rot_review.get("summary"), dict) else {}
                rot_rows = rot_review.get("prioritizedRows")
                required_rot_summary = {
                    "totalMarkers",
                    "rotRiskRows",
                    "highRiskRows",
                    "reviewRiskRows",
                    "trackedRows",
                    "missingCeilingRows",
                    "missingUpgradeTriggerRows",
                    "omittedByLimit",
                    "omittedRiskUnknown",
                    "topRiskLocation",
                    "topRiskReason",
                }
                if trigger_watch_required:
                    required_rot_summary.update(
                        {
                            "triggerWatchContractRows",
                            "missingTriggerWatchContractRows",
                            "trackedTriggerWatchRows",
                            "missingTriggerDefinitionRows",
                            "topTriggerWatchAction",
                        }
                    )
                missing_rot_summary = sorted(key for key in required_rot_summary if key not in rot_summary)
                if missing_rot_summary:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-summary-missing",
                        evidence=f"{path_name} rotRiskReview.summary missing: {', '.join(missing_rot_summary)}",
                        recommendation="Summarize total, risk-level, missing-ceiling, missing-trigger, omitted, and top-risk marker counts.",
                    )
                if not isinstance(rot_rows, list):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-rows-invalid",
                        evidence=f"{path_name} rotRiskReview.prioritizedRows is not a list",
                        recommendation="Emit prioritized rot-risk rows sorted by missing ceiling, missing trigger, then tracked trigger watch.",
                    )
                    rot_rows = []
                rot_row_objects = [row for row in rot_rows if isinstance(row, dict)]
                high_rows = sum(1 for row in rot_row_objects if row.get("riskLevel") == "high")
                review_rows = sum(1 for row in rot_row_objects if row.get("riskLevel") == "review")
                tracked_rows = sum(1 for row in rot_row_objects if row.get("riskLevel") == "tracked")
                missing_ceiling_rows = sum(1 for row in rot_row_objects if row.get("hasCeiling") is False)
                missing_upgrade_rows = sum(1 for row in rot_row_objects if row.get("hasUpgradeTrigger") is False)
                trigger_contract_rows = sum(
                    1 for row in rot_row_objects if isinstance(row.get("triggerWatchContract"), dict)
                )
                top_row = rot_row_objects[0] if rot_row_objects else {}
                top_contract = (
                    top_row.get("triggerWatchContract") if isinstance(top_row.get("triggerWatchContract"), dict) else {}
                )
                rot_mismatches = []
                if int(rot_summary.get("totalMarkers") or 0) != int(ledger_summary.get("markers") or 0):
                    rot_mismatches.append("totalMarkers")
                if int(rot_summary.get("rotRiskRows") or 0) != len(rot_row_objects):
                    rot_mismatches.append("rotRiskRows")
                if int(rot_summary.get("omittedByLimit") or 0) != int(ledger_summary.get("omittedByLimit") or 0):
                    rot_mismatches.append("omittedByLimit")
                if int(rot_summary.get("highRiskRows") or 0) != high_rows:
                    rot_mismatches.append("highRiskRows")
                if int(rot_summary.get("reviewRiskRows") or 0) != review_rows:
                    rot_mismatches.append("reviewRiskRows")
                if int(rot_summary.get("trackedRows") or 0) != tracked_rows:
                    rot_mismatches.append("trackedRows")
                if int(rot_summary.get("missingCeilingRows") or 0) != missing_ceiling_rows:
                    rot_mismatches.append("missingCeilingRows")
                if int(rot_summary.get("missingUpgradeTriggerRows") or 0) != review_rows:
                    rot_mismatches.append("missingUpgradeTriggerRows")
                if trigger_watch_required:
                    if int(rot_summary.get("triggerWatchContractRows") or 0) != trigger_contract_rows:
                        rot_mismatches.append("triggerWatchContractRows")
                    if int(rot_summary.get("missingTriggerWatchContractRows") or 0) != max(0, len(rot_row_objects) - trigger_contract_rows):
                        rot_mismatches.append("missingTriggerWatchContractRows")
                    if int(rot_summary.get("trackedTriggerWatchRows") or 0) != tracked_rows:
                        rot_mismatches.append("trackedTriggerWatchRows")
                    if int(rot_summary.get("missingTriggerDefinitionRows") or 0) != review_rows:
                        rot_mismatches.append("missingTriggerDefinitionRows")
                omitted_count = int(ledger_summary.get("omittedByLimit") or 0)
                if omitted_count > 0 and rot_summary.get("omittedRiskUnknown") is not True:
                    rot_mismatches.append("omittedRiskUnknown")
                if omitted_count == 0 and rot_summary.get("omittedRiskUnknown") is not False:
                    rot_mismatches.append("omittedRiskUnknown")
                if isinstance(rot_rows, list) and len(rot_rows) != len(ledger_markers):
                    rot_mismatches.append("prioritizedRows")
                if marker_count and str(rot_summary.get("topRiskLocation") or "") != str(top_row.get("location") or ""):
                    rot_mismatches.append("topRiskLocation")
                if marker_count and str(rot_summary.get("topRiskReason") or "") != str(top_row.get("rotReason") or ""):
                    rot_mismatches.append("topRiskReason")
                if trigger_watch_required and marker_count and str(rot_summary.get("topTriggerWatchAction") or "") != str(top_contract.get("exactNextAction") or ""):
                    rot_mismatches.append("topTriggerWatchAction")
                if rot_mismatches:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-counts-mismatch",
                        evidence=f"{path_name} rotRiskReview count mismatch: {', '.join(sorted(set(rot_mismatches)))}",
                        recommendation="Keep rotRiskReview counts and top-risk fields aligned with the shortcut ledger.",
                    )
                if marker_count and (
                    rot_review.get("allVisibleRowsHaveRotRisk") is not True
                    or rot_review.get("topRiskActionable") is not True
                ):
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-flag-incomplete",
                        evidence=f"{path_name} rotRiskReview does not confirm visible-row risk coverage and actionable top risk",
                        recommendation="Set rot-risk flags from prioritized row coverage so the first cleanup bet is machine-checkable.",
                    )
                malformed_rot_rows = []
                rot_required_text = {
                    "file",
                    "line",
                    "location",
                    "marker",
                    "status",
                    "riskLevel",
                    "rotReason",
                    "nextAction",
                    "proofGuidance",
                }
                rot_required_keys = rot_required_text | {
                    "rank",
                    "ceiling",
                    "upgradeTrigger",
                    "hasCeiling",
                    "hasUpgradeTrigger",
                }
                if trigger_watch_required:
                    rot_required_keys.add("triggerWatchContract")
                required_contract_text = {
                    "triggerState",
                    "triggerCondition",
                    "exactNextAction",
                    "checkRoute",
                    "proofArtifact",
                    "stopCondition",
                }
                risk_order = {"high": 0, "review": 1, "tracked": 2}
                previous_order = -1
                expected_rank = 1
                for index, row in enumerate(rot_row_objects[:20], start=1):
                    missing_keys = sorted(key for key in rot_required_keys if key not in row)
                    missing_text = sorted(key for key in rot_required_text if str(row.get(key) or "").strip() == "")
                    missing_bool = sorted(
                        key
                        for key in ("hasCeiling", "hasUpgradeTrigger")
                        if not isinstance(row.get(key), bool)
                    )
                    risk_level = str(row.get("riskLevel") or "")
                    risk_index = risk_order.get(risk_level)
                    if not isinstance(row.get("rank"), int) or row.get("rank") != expected_rank:
                        malformed_rot_rows.append(f"row {index} rank should be {expected_rank}")
                    expected_rank += 1
                    if risk_index is None:
                        malformed_rot_rows.append(f"row {index} unknown riskLevel {risk_level or 'blank'}")
                    else:
                        if risk_index < previous_order:
                            malformed_rot_rows.append(f"row {index} is not sorted by risk")
                        previous_order = risk_index
                    if missing_keys or missing_text or missing_bool:
                        parts = []
                        if missing_keys:
                            parts.append(f"missing keys {', '.join(missing_keys)}")
                        if missing_text:
                            parts.append(f"blank fields {', '.join(missing_text)}")
                        if missing_bool:
                            parts.append(f"non-boolean {', '.join(missing_bool)}")
                        malformed_rot_rows.append(f"row {index} {'; '.join(parts)}")
                    if row.get("hasCeiling") is False and risk_level != "high":
                        malformed_rot_rows.append(f"row {index} missing ceiling should be high risk")
                    if row.get("hasCeiling") is True and row.get("hasUpgradeTrigger") is False and risk_level != "review":
                        malformed_rot_rows.append(f"row {index} missing trigger should be review risk")
                    next_action_text = normalized_question_text(row.get("nextAction") or "")
                    proof_text = normalized_question_text(row.get("proofGuidance") or "")
                    if "source inspection" in next_action_text:
                        malformed_rot_rows.append(f"row {index} next action still requires another source inspection pass")
                    if len(next_action_text) < 20 or len(proof_text) < 20:
                        malformed_rot_rows.append(f"row {index} action/proof text is too weak")
                    if risk_level == "high" and "ceiling" not in next_action_text:
                        malformed_rot_rows.append(f"row {index} high risk should ask for a ceiling")
                    if risk_level == "review" and "upgrade trigger" not in next_action_text:
                        malformed_rot_rows.append(f"row {index} review risk should ask for an upgrade trigger")
                    if risk_level == "tracked" and "trigger" not in next_action_text:
                        malformed_rot_rows.append(f"row {index} tracked risk should name the trigger to watch")
                    if not any(token in proof_text for token in ("call site", "call-site", "validation", "release", "dependency", "migration", "milestone", "owner", "scope", "lifetime", "trigger")):
                        malformed_rot_rows.append(f"row {index} proof guidance lacks a concrete proof signal")
                    contract = row.get("triggerWatchContract")
                    if trigger_watch_required:
                        if not isinstance(contract, dict):
                            malformed_rot_rows.append(f"row {index} missing triggerWatchContract")
                            continue
                        missing_contract_fields = sorted(
                            key for key in required_contract_text if str(contract.get(key) or "").strip() == ""
                        )
                        if missing_contract_fields:
                            malformed_rot_rows.append(
                                f"row {index} triggerWatchContract blank fields {', '.join(missing_contract_fields)}"
                            )
                        contract_text = normalized_question_text(json.dumps(contract, sort_keys=True))
                        trigger_state = normalized_question_text(contract.get("triggerState") or "")
                        exact_action = normalized_question_text(contract.get("exactNextAction") or "")
                        check_route = normalized_question_text(contract.get("checkRoute") or "")
                        proof_artifact = normalized_question_text(contract.get("proofArtifact") or "")
                        stop_condition = normalized_question_text(contract.get("stopCondition") or "")
                        if "source inspection" in exact_action or "source inspection" in check_route:
                            malformed_rot_rows.append(f"row {index} triggerWatchContract still depends on source inspection")
                        if risk_level == "high" and "missing-ceiling" not in trigger_state and "missing ceiling" not in trigger_state:
                            malformed_rot_rows.append(f"row {index} high risk triggerWatchContract should be blocked by missing ceiling")
                        if risk_level == "review" and "needs-trigger" not in trigger_state and "needs trigger" not in trigger_state:
                            malformed_rot_rows.append(f"row {index} review risk triggerWatchContract should require trigger definition")
                        if risk_level == "tracked":
                            upgrade_trigger_text = normalized_question_text(row.get("upgradeTrigger") or "")
                            if "watch-trigger" not in trigger_state and "watch trigger" not in trigger_state:
                                malformed_rot_rows.append(f"row {index} tracked triggerWatchContract should be watch-trigger")
                            if upgrade_trigger_text and upgrade_trigger_text not in contract_text:
                                malformed_rot_rows.append(f"row {index} tracked triggerWatchContract should repeat the exact upgrade trigger")
                            if "call site" not in check_route and "call-site" not in check_route:
                                malformed_rot_rows.append(f"row {index} tracked triggerWatchContract should name call-site search")
                            if "validation" not in check_route:
                                malformed_rot_rows.append(f"row {index} tracked triggerWatchContract should name focused validation")
                        if "lean-debt" not in proof_artifact and "validation" not in proof_artifact and "call-site" not in proof_artifact and "call site" not in proof_artifact:
                            malformed_rot_rows.append(f"row {index} triggerWatchContract proofArtifact is not concrete")
                        if "stop" not in stop_condition:
                            malformed_rot_rows.append(f"row {index} triggerWatchContract stopCondition is not explicit")
                if malformed_rot_rows:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-row-fields-incomplete",
                        evidence=f"{path_name} rotRiskReview rows incomplete: {'; '.join(malformed_rot_rows[:5])}",
                        recommendation="Each rot-risk row should expose rank, risk, location, rot reason, next action, proof guidance, and trigger-state fields.",
                    )
                required_rot_markdown = [
                    "Rot-Risk Review",
                    "Top risk location",
                    "Top risk reason",
                    "High-risk rows",
                    "Review-risk rows",
                    "Missing upgrade-trigger rows",
                    "Rot Reason",
                    "Next Action",
                    "Proof Guidance",
                ]
                if trigger_watch_required:
                    required_rot_markdown.extend(
                        [
                            "Trigger-watch contract rows",
                            "Missing trigger-watch contracts",
                            "Top trigger-watch action",
                            "Trigger-Watch Contracts",
                            "Trigger State",
                            "Trigger Condition",
                            "Exact Next Action",
                            "Check Route",
                            "Proof Artifact",
                            "Stop Condition",
                        ]
                    )
                missing_rot_markdown = [token for token in required_rot_markdown if token not in markdown]
                if missing_rot_markdown:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-rot-risk-markdown-missing",
                        evidence=f"{path_name} Markdown missing rot-risk tokens: {', '.join(missing_rot_markdown)}",
                        recommendation="Render rotRiskReview in Markdown so maintainers can pick the first shortcut cleanup bet without opening JSON.",
                    )
                elif isinstance(rot_rows, list):
                    rot_section = markdown.split("Rot-Risk Review", 1)[1]
                    if "\n## Shortcut Ledger" in rot_section:
                        rot_section = rot_section.split("\n## Shortcut Ledger", 1)[0]
                    else:
                        rot_section = rot_section.split("\n## ", 1)[0]
                    missing_rot_rows = []
                    for row in rot_rows[:20]:
                        if not isinstance(row, dict):
                            continue
                        location = str(row.get("location") or "").strip()
                        row_tokens = [
                            location,
                            str(row.get("rotReason") or "").strip(),
                            str(row.get("nextAction") or "").strip(),
                            str(row.get("proofGuidance") or "").strip(),
                        ]
                        if trigger_watch_required:
                            contract = row.get("triggerWatchContract") if isinstance(row.get("triggerWatchContract"), dict) else {}
                            row_tokens.extend(
                                str(contract.get(key) or "").strip()
                                for key in (
                                    "triggerState",
                                    "triggerCondition",
                                    "exactNextAction",
                                    "checkRoute",
                                    "proofArtifact",
                                    "stopCondition",
                                )
                            )
                        if any(not markdown_contains_token(rot_section, token) for token in row_tokens):
                            missing_rot_rows.append(location)
                    if missing_rot_rows:
                        add_issue(
                            issues,
                            severity="review",
                            rule_id="lean-debt-rot-risk-markdown-rows-missing",
                            evidence=f"{path_name} Rot-Risk Review Markdown missing rows: {', '.join(missing_rot_rows[:5])}",
                            recommendation="Render each prioritized rot-risk row in Markdown so the first action stays visible.",
                        )
            boundary = report.get("currentRepoBoundary")
            if not isinstance(boundary, dict) or boundary.get("perRepoSavingsClaim") != "not-computed":
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-benchmark-savings-boundary-missing",
                    evidence=f"{path_name} does not mark Lean Debt current-repo savings as not-computed",
                    recommendation="Emit currentRepoBoundary.perRepoSavingsClaim=not-computed so shortcut marker counts cannot become fake benchmark savings.",
                )
            else:
                reason = normalized_question_text(boundary.get("reason") or "")
                evidence_type = normalized_question_text(boundary.get("evidenceType") or "")
                non_claims = boundary.get("nonClaims")
                non_claim_text = normalized_question_text(" ".join(str(item) for item in non_claims or []))
                route = boundary.get("benchmarkRoute")
                route_text = normalized_question_text(json.dumps(route, sort_keys=True) if isinstance(route, dict) else "")
                missing_boundary_parts = []
                if "shortcut" not in evidence_type or "ledger" not in evidence_type:
                    missing_boundary_parts.append("evidenceType=shortcut-ledger-only")
                if "baseline" not in reason or "savings" not in reason:
                    missing_boundary_parts.append("reason blocks current-repo savings")
                if (
                    not isinstance(non_claims, list)
                    or "do not" not in non_claim_text
                    or "marker" not in non_claim_text
                    or "savings" not in non_claim_text
                    or "line" not in non_claim_text
                    or "token" not in non_claim_text
                    or "cost" not in non_claim_text
                    or "time" not in non_claim_text
                ):
                    missing_boundary_parts.append("nonClaims block marker-count savings")
                if not isinstance(route, dict) or "lean gain" not in route_text or "benchmark" not in route_text:
                    missing_boundary_parts.append("benchmarkRoute points to lean gain")
                if missing_boundary_parts:
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="lean-debt-benchmark-savings-boundary-incomplete",
                        evidence=f"{path_name} currentRepoBoundary incomplete: {', '.join(missing_boundary_parts)}",
                        recommendation="State that Lean Debt is shortcut-ledger evidence only, has no matched baseline, cannot prove line/token/cost/time savings, and routes benchmark direction to lean gain.",
                    )
            required_debt_honesty_markdown = [
                "Benchmark Savings Boundary",
                "not-computed",
                "shortcut marker counts",
                "Do not claim current-repo line, token, cost, or time savings",
                "Do not treat shortcut marker counts as benchmark savings",
                "shipguard lean gain",
            ]
            missing_debt_honesty_markdown = [
                token for token in required_debt_honesty_markdown if token not in markdown
            ]
            if missing_debt_honesty_markdown:
                add_issue(
                    issues,
                    severity="review",
                    rule_id="lean-debt-benchmark-savings-markdown-missing",
                    evidence=f"{path_name} Markdown missing Lean Debt savings-boundary tokens: {', '.join(missing_debt_honesty_markdown)}",
                    recommendation="Render the Lean Debt benchmark-savings boundary in Markdown so marker counts cannot be mistaken for measured savings.",
                )
    return issues


def grade_report(path: Path, *, input_paths: list[Path], shareable: bool, cwd: Path) -> dict[str, Any]:
    loaded = read_json(path)
    markdown_path = paired_markdown(path)
    markdown = markdown_path.read_text(encoding="utf-8", errors="ignore") if markdown_path else ""
    raw_text = path.read_text(encoding="utf-8", errors="ignore") + "\n" + markdown
    issues: list[dict[str, str]] = []
    display_path = path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd)
    display_markdown_path = (
        path_label(markdown_path, input_paths=input_paths, shareable=shareable, cwd=cwd) if markdown_path else None
    )

    if loaded is None:
        add_issue(
            issues,
            severity="high",
            rule_id="report-json-invalid",
            evidence=f"{display_path} is not valid JSON",
            recommendation="Fix the report writer so every report has parseable JSON.",
        )
        return {
            "path": display_path,
            "markdownPath": display_markdown_path,
            "tool": None,
            "intent": None,
            "actionabilityQuestions": [],
            "sourceFindings": [],
            "sourceFindingCount": 0,
            "status": "blocked",
            "score": score_for(issues),
            "issues": issues,
            "issueCount": len(issues),
        }

    tool = str(loaded.get("tool") or "")
    intent = str(loaded.get("intent") or "")
    if tool not in ROOT_REPORT_TOOLS and not tool.startswith("shipguard ios "):
        add_issue(
            issues,
            severity="high",
            rule_id="report-tool-missing",
            evidence=f"{path.name} has tool={tool or 'missing'}",
            recommendation="Set a stable ShipGuard tool name in every report JSON.",
        )
    if tool == REPORT_QUALITY_TOOL:
        add_issue(
            issues,
            severity="opportunity",
            rule_id="self-report-skipped",
            evidence=f"{path.name} is a report-quality report",
            recommendation="Do not include report-quality outputs as inputs to the same scoring run.",
        )
    for required in ("schemaVersion", "generatedAt", "status"):
        if required not in loaded:
            add_issue(
                issues,
                severity="review",
                rule_id="report-metadata-missing",
                evidence=f"{path.name} missing {required}",
                recommendation="Keep report metadata stable for automation and package proof.",
            )

    if markdown_path is None:
        add_issue(
            issues,
            severity="review",
            rule_id="markdown-companion-missing",
            evidence=f"{path.name} has no paired Markdown file",
            recommendation="Write human-readable Markdown beside JSON so the report is useful in Codex and reviews.",
        )

    if intent == "shipguard-evaluation":
        boundary = loaded.get("scopeBoundary")
        if not isinstance(boundary, dict) or boundary.get("shipguardOnly") is not True:
            add_issue(
                issues,
                severity="high",
                rule_id="shipguard-eval-boundary-missing",
                evidence=f"{path.name} is shipguard-evaluation without a shipguardOnly scope boundary",
                recommendation="Keep private app runs explicitly scoped to ShipGuard product QA.",
            )
        if "ShipGuard Evaluation Boundary" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="shipguard-eval-markdown-boundary-missing",
                evidence=f"{path.name} Markdown does not show the eval boundary",
                recommendation="Show the read-only/product-QA boundary in Markdown, not only JSON.",
            )
        questions = loaded.get("reportQualityQuestions")
        if not isinstance(questions, list) or not questions:
            add_issue(
                issues,
                severity="review",
                rule_id="report-quality-questions-missing",
                evidence=f"{path.name} has no reportQualityQuestions",
                recommendation="Add report-quality questions so real-app observations become ShipGuard improvements.",
            )

    if tool in SOURCE_SCANNER_TOOLS:
        scan_scope = find_scan_scope(loaded)
        if scan_scope is None:
            add_issue(
                issues,
                severity="high",
                rule_id="scan-scope-missing",
                evidence=f"{path.name} is a source scanner report without scanScope",
                recommendation="Report skipped generated/proof/cache directories so private-app QA is auditable.",
            )
        elif int(scan_scope.get("skippedDirectoryCount") or 0) > 0 and "Scan Scope" not in markdown and "Scan-scope exclusions" not in markdown:
            add_issue(
                issues,
                severity="review",
                rule_id="scan-scope-markdown-missing",
                evidence=f"{path.name} has skipped directories in JSON but not Markdown",
                recommendation="Surface scan-scope exclusions in Markdown for human review.",
            )

    if shareable and tool in DECLARED_SHAREABILITY_TOOLS:
        issues.extend(declared_shareability_issues(loaded, path_name=path.name))
        issues.extend(private_identifier_shareability_issues(loaded, raw_text=raw_text, path_name=path.name))

    if tool == SPEC_WORKFLOW_TOOL:
        issues.extend(spec_workflow_quality_issues(loaded, path=path, path_name=path.name))
    issues.extend(lean_report_quality_issues(loaded, markdown=markdown, path_name=path.name))

    findings = loaded.get("findings")
    if isinstance(findings, list) and len(findings) > 30 and not loaded.get("ruleSummary"):
        add_issue(
            issues,
            severity="review",
            rule_id="large-report-summary-missing",
            evidence=f"{path.name} has {len(findings)} findings without ruleSummary",
            recommendation="Group repeated rules so Markdown stays scannable while JSON keeps full detail.",
        )
    issues.extend(finding_quality_issues(loaded))
    issues.extend(result_ux_quality_issues(loaded, path_name=path.name))
    issues.extend(verify_pr_report_quality_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_release_asset_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_fresh_install_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_upgrade_rollback_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_download_blocking_proof_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_download_proof_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_external_adoption_gate_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(launchkey_security_review_gate_attachment_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(task_contract_quickstart_replay_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(task_contract_notification_scope_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(task_contract_unsupported_claim_replay_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(task_contract_notification_proof_lane_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(full_audit_slash_handoff_issues(loaded, path_name=path.name))
    issues.extend(full_audit_execution_command_issues(loaded, markdown=markdown, path_name=path.name))
    issues.extend(full_audit_release_packet_plan_issues(loaded, markdown=markdown, path_name=path.name))
    if tool == "shipguard value-gauntlet":
        issues.extend(value_gauntlet_stable_publication_priority_issues(loaded, markdown=markdown, path_name=path.name))
    if tool == "shipguard ios performance":
        issues.extend(performance_runtime_evidence_boundary_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_evidence_promotion_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_finding_explanation_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_grouping_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_high_severity_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_proof_boundary_issues(loaded, markdown=markdown, path_name=path.name))
    if tool == "shipguard ios design":
        issues.extend(design_app_type_tailoring_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(design_principle_vocabulary_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(design_coherence_boundary_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(design_preview_routing_issues(loaded, markdown=markdown, path_name=path.name))
    if tool == "shipguard v4 stable-publication":
        issues.extend(stable_publication_evidence_packet_issues(loaded, markdown=markdown, path_name=path.name))

    if has_local_path(raw_text):
        add_issue(
            issues,
            severity="opportunity",
            rule_id="local-path-shareability-warning",
            evidence=f"{path.name} contains local absolute paths",
            recommendation="Keep this report local or run shipguard ios redact before sharing externally.",
        )

    token_labels = token_risk_labels(raw_text)
    if token_labels:
        add_issue(
            issues,
            severity="high",
            rule_id="token-shareability-risk",
            evidence=f"{path.name} contains token-like connector or auth content ({', '.join(token_labels)})",
            recommendation="Remove token-bearing URLs or run shipguard ios redact before sharing the report outside the local loop.",
        )

    score = score_for(issues)
    source_findings = source_report_findings(
        loaded,
        path_name=path.name,
        report_path=display_path,
        tool=tool,
        shareable=shareable,
    )
    return {
        "path": display_path,
        "markdownPath": display_markdown_path,
        "tool": tool,
        "surface": loaded.get("surface") or None,
        "intent": intent or None,
        "reportStatus": loaded.get("status"),
        "sourcePrioritySignal": source_priority_signal(loaded),
        "actionabilityQuestions": report_questions(loaded, report_path=display_path, tool=tool),
        "sourceFindings": source_findings,
        "sourceFindingCount": len(source_findings),
        "score": score,
        "status": report_status(issues),
        "issues": issues,
        "issueCount": len(issues),
    }


def promotion_manifest_report(path: Path, *, input_paths: list[Path], shareable: bool, cwd: Path) -> dict[str, Any]:
    loaded = read_json(path)
    display_path = path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd)
    guide_path = path.with_name("PROMOTION.md")
    guide_text = guide_path.read_text(encoding="utf-8", errors="ignore") if guide_path.is_file() else ""
    issues: list[dict[str, str]] = []

    if loaded is None:
        add_issue(
            issues,
            severity="high",
            rule_id="fixture-promotion-manifest-invalid",
            evidence=f"{Path(display_path).name} is not valid JSON",
            recommendation="Rewrite the promotion manifest as parseable JSON before using it as fixture-promotion evidence.",
        )
        return {
            "path": display_path,
            "status": report_status(issues),
            "candidateCount": 0,
            "issues": issues,
            "issueCount": len(issues),
        }

    candidates = loaded.get("candidates")
    candidate_count = loaded.get("candidateCount")
    if not isinstance(candidates, list):
        add_issue(
            issues,
            severity="high",
            rule_id="fixture-promotion-candidates-missing",
            evidence=f"{Path(display_path).name} has no candidates list",
            recommendation="Emit a candidates list so report-quality can validate every materialized fixture promotion path.",
        )
        candidates = []
    if not isinstance(candidate_count, int) or candidate_count != len(candidates):
        add_issue(
            issues,
            severity="review",
            rule_id="fixture-promotion-count-mismatch",
            evidence=f"{Path(display_path).name} candidateCount does not match the candidates list",
            recommendation="Keep candidateCount synchronized with candidates so generated promotion guides are machine-checkable.",
        )

    if not guide_path.is_file():
        add_issue(
            issues,
            severity="review",
            rule_id="fixture-promotion-guide-missing",
            evidence=f"{Path(display_path).name} has no paired PROMOTION.md",
            recommendation="Write PROMOTION.md beside the manifest so humans see the copy, validation, and review steps.",
        )

    for index, item in enumerate(candidates[:20], start=1):
        if not isinstance(item, dict):
            add_issue(
                issues,
                severity="high",
                rule_id="fixture-promotion-candidate-invalid",
                evidence=f"{Path(display_path).name} candidate #{index} is not an object",
                recommendation="Emit each promotion candidate as an object with candidateId, suggestedFixturePath, files, copyCommands, validationCommands, and reviewChecklist.",
            )
            continue
        candidate_id = str(item.get("candidateId") or "").strip()
        suggested_path = str(item.get("suggestedFixturePath") or "").strip()
        if not candidate_id:
            add_issue(
                issues,
                severity="high",
                rule_id="fixture-promotion-candidate-id-missing",
                evidence=f"{Path(display_path).name} candidate #{index} has no candidateId",
                recommendation="Keep candidateId stable so generated directories and suggested fixture paths can be reconciled.",
            )
        if not suggested_path.startswith("fixtures/ios-report-quality/") or has_local_path(suggested_path) or ".." in Path(suggested_path).parts:
            add_issue(
                issues,
                severity="high",
                rule_id="fixture-promotion-path-unsafe",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} has an unsafe suggestedFixturePath",
                recommendation="Use a repo-relative fixtures/ios-report-quality/<candidate-id> path and never local absolute paths or parent traversal.",
            )
        elif candidate_id and not suggested_path.endswith(candidate_id):
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-path-mismatch",
                evidence=f"{Path(display_path).name} candidate {candidate_id} path does not end with the candidate id",
                recommendation="Keep suggestedFixturePath aligned with candidateId so promotion stays deterministic.",
            )

        expected_files = item.get("files")
        if not isinstance(expected_files, list) or not expected_files:
            expected_files = ["README.md", "fixture-candidate.json", "fixture-report.json", "fixture-report.md"]
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-files-missing",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} has no files list",
                recommendation="Declare the materialized files so promotion can be reviewed before copying.",
            )
        candidate_dir = path.parent / candidate_id if candidate_id else None
        if candidate_dir is not None:
            for name in expected_files:
                if not isinstance(name, str):
                    continue
                if not (candidate_dir / name).is_file():
                    add_issue(
                        issues,
                        severity="review",
                        rule_id="fixture-promotion-file-missing",
                        evidence=f"{Path(display_path).name} candidate {candidate_id} is missing {name}",
                        recommendation="Keep the manifest synchronized with the materialized candidate directory before promotion.",
                    )
                    break

        source_directory = str(item.get("sourceDirectory") or "")
        copy_commands = item.get("copyCommands")
        validation_commands = item.get("validationCommands")
        review_checklist = item.get("reviewChecklist")
        command_text = "\n".join(str(command) for command in copy_commands) if isinstance(copy_commands, list) else ""
        manifest_text = json.dumps(item, sort_keys=True)
        if has_local_path(source_directory) or has_local_path(command_text) or token_risk_labels(manifest_text):
            add_issue(
                issues,
                severity="high",
                rule_id="fixture-promotion-private-data-risk",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} contains local-path or token-like promotion metadata",
                recommendation="Keep promotion metadata placeholder-based and public-safe before sharing or committing generated fixtures.",
            )
        if not isinstance(copy_commands, list) or not any("<materialized-candidate-dir>" in str(command) for command in copy_commands):
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-copy-placeholder-missing",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} copy commands do not use <materialized-candidate-dir>",
                recommendation="Use placeholder copy commands so generated promotion docs do not leak local output directories.",
            )
        validation_text = "\n".join(str(command) for command in validation_commands) if isinstance(validation_commands, list) else ""
        if "ios report-quality" not in validation_text or "./tests/ios_report_quality_test.sh" not in validation_text:
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-validation-missing",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} lacks report-quality promotion validation commands",
                recommendation="Include ios report-quality and ios_report_quality_test.sh validation before a fixture is promoted into the repo.",
            )
        checklist_text = " ".join(str(item) for item in review_checklist) if isinstance(review_checklist, list) else ""
        if "private app code" not in checklist_text.lower() or "scopeboundary" not in checklist_text.lower():
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-review-checklist-incomplete",
                evidence=f"{Path(display_path).name} candidate {candidate_id or index} review checklist is missing privacy or scope-boundary checks",
                recommendation="Require review of private app leakage and scopeBoundary before promoting generated fixtures.",
            )
        if guide_text and suggested_path and suggested_path not in guide_text:
            add_issue(
                issues,
                severity="review",
                rule_id="fixture-promotion-guide-path-missing",
                evidence=f"PROMOTION.md does not mention candidate {candidate_id or index}'s suggested fixture path",
                recommendation="Keep the human promotion guide synchronized with the machine manifest.",
            )

    return {
        "path": display_path,
        "status": report_status(issues),
        "candidateCount": len(candidates),
        "issues": issues,
        "issueCount": len(issues),
    }


def build_redaction_plan(
    inputs: list[str],
    issues: list[dict[str, Any]],
    *,
    input_paths: list[Path],
    shareable: bool,
    cwd: Path,
) -> dict[str, Any]:
    shareability_rules = {"local-path-shareability-warning", "token-shareability-risk"}
    matching = [issue for issue in issues if issue["ruleId"] in shareability_rules]
    commands = []
    for index, path in enumerate(input_paths, start=1):
        suffix = "" if len(input_paths) == 1 else f"-{index}"
        input_label = path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd)
        output_label = "<redacted-report-dir>" if shareable else f"/tmp/ios-shipguard-redacted-report-quality{suffix}"
        commands.append(
            {
                "input": input_label,
                "output": output_label,
                "command": (
                    "./bin/shipguard ios redact "
                    f"--in {shlex.quote(input_label)} "
                    f"--out {shlex.quote(output_label)}"
                ),
            }
        )
    return {
        "needed": bool(matching),
        "blockedUntilRedacted": any(issue["ruleId"] == "token-shareability-risk" for issue in matching),
        "rules": sorted({issue["ruleId"] for issue in matching}),
        "commands": commands if matching else [],
        "note": "Run redaction before sharing report-quality inputs externally; keep unredacted private-app reports local.",
    }


def priority_reason(row: dict[str, Any]) -> str:
    quality_status = str(row.get("reportQualityStatus") or "")
    source_status = str(row.get("sourceStatus") or "")
    tool = str(row.get("tool") or "unknown")
    source_reason = str(row.get("sourcePriorityReason") or "")
    if source_reason:
        return source_reason
    if quality_status and quality_status != "pass":
        return f"report-quality status is {quality_status}"
    if source_status and source_status != "pass":
        return f"source report status is {source_status}"
    return f"{tool} is next in the default ShipGuard report-quality priority order"


def ranked_actionability_questions(graded: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report_index, report in enumerate(graded):
        source_signal = report.get("sourcePrioritySignal") if isinstance(report.get("sourcePrioritySignal"), dict) else {}
        for question_index, question in enumerate(report.get("actionabilityQuestions", [])):
            row = {
                "tool": question.get("tool") or report.get("tool") or "unknown",
                "report": question.get("report") or report.get("path") or "<unknown-report>",
                "question": question.get("question") or "",
                "sourceStatus": report.get("reportStatus") or "unknown",
                "reportQualityStatus": report.get("status") or "unknown",
                "sourcePrioritySignal": source_signal.get("kind"),
                "sourcePriority": source_signal.get("priority") if isinstance(source_signal.get("priority"), int) else 0,
                "sourcePriorityReason": source_signal.get("reason"),
                "score": report.get("score"),
                "sourceMaterializedFixture": bool(question.get("sourceMaterializedFixture")),
                "_reportIndex": report_index,
                "_questionIndex": question_index,
            }
            if not row["question"]:
                continue
            rows.append(row)

    rows.sort(
        key=lambda row: (
            status_rank(row.get("reportQualityStatus")),
            source_block_priority(row),
            question_focus_priority(row),
            status_rank(row.get("sourceStatus")),
            int(row.get("score") if isinstance(row.get("score"), int) else 999),
            tool_priority(row.get("tool")),
            row["_reportIndex"],
            row["_questionIndex"],
        )
    )
    rows = dedupe_question_rows(rows, annotate_duplicates=True)
    for index, row in enumerate(rows, start=1):
        row["priority"] = index
        row["priorityReason"] = priority_reason(row)
        row.pop("_reportIndex", None)
        row.pop("_questionIndex", None)
    return rows


def top_report_quality_issue(issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not issues:
        return None
    return sorted(
        issues,
        key=lambda issue: (
            severity_rank(issue.get("severity")),
            tool_priority(issue.get("tool")),
            str(issue.get("report") or ""),
            str(issue.get("ruleId") or ""),
        ),
    )[0]


def build_priority_action(issues: list[dict[str, Any]], ranked_questions: list[dict[str, Any]]) -> dict[str, Any]:
    issue = top_report_quality_issue(issues)
    if issue:
        return {
            "kind": "fix-report-quality-finding",
            "summary": (
                f"Fix `{issue.get('ruleId')}` in `{Path(str(issue.get('report') or '')).name}`: "
                f"{issue.get('recommendation')}"
            ),
            "severity": issue.get("severity"),
            "ruleId": issue.get("ruleId"),
            "tool": issue.get("tool"),
            "report": issue.get("report"),
            "recommendation": issue.get("recommendation"),
        }
    next_questions = [
        row
        for row in ranked_questions
        if not row.get("existingFixture") and not row.get("sourceMaterializedFixture")
    ]
    if next_questions:
        question = next_questions[0]
        return {
            "kind": "answer-actionability-question",
            "summary": (
                f"Start with `{question['tool']}` question #{question['priority']}: "
                f"{question['question']}"
            ),
            "tool": question["tool"],
            "report": question["report"],
            "sourceStatus": question["sourceStatus"],
            "reportQualityStatus": question["reportQualityStatus"],
            "question": question["question"],
            "priorityReason": question["priorityReason"],
        }
    covered_questions = [row for row in ranked_questions if row.get("existingFixture") or row.get("sourceMaterializedFixture")]
    if covered_questions:
        question = covered_questions[0]
        fixture = question.get("existingFixture") if isinstance(question.get("existingFixture"), dict) else {}
        fixture_path = fixture.get("publicFixturePath") or question.get("existingFixturePath") or "<materialized-fixture>"
        source_reports = {str(row.get("report") or "") for row in covered_questions}
        all_sources_are_fixture_reports = bool(source_reports) and all(
            "fixtures/ios-report-quality/" in report or report.endswith("fixture-report.json")
            for report in source_reports
        )
        if not all_sources_are_fixture_reports:
            return {
                "kind": "all-actionability-covered",
                "summary": (
                    f"All {len(covered_questions)} ranked actionability question(s) already have fixture coverage; "
                    "move to a fresh read-only ShipGuard QA source instead of re-reviewing the first covered fixture."
                ),
                "coveredQuestionCount": len(covered_questions),
                "topCoveredQuestion": question.get("question"),
                "topExistingFixturePath": fixture_path,
                "tool": question.get("tool"),
                "report": question.get("report"),
                "sourceStatus": question.get("sourceStatus"),
                "reportQualityStatus": question.get("reportQualityStatus"),
            }
        return {
            "kind": "review-existing-fixture",
            "summary": (
                f"Use existing fixture `{fixture_path}` for `{question.get('tool') or 'unknown'}` "
                f"question #{question.get('priority') or 1}, then look for the next uncovered actionability gap."
            ),
            "tool": question.get("tool"),
            "report": question.get("report"),
            "sourceStatus": question.get("sourceStatus"),
            "reportQualityStatus": question.get("reportQualityStatus"),
            "question": question.get("question"),
            "existingFixturePath": fixture_path,
        }
    return {
        "kind": "add-actionability-questions",
        "summary": "Add reportQualityQuestions to source reports so report-quality can propose a concrete next ShipGuard improvement.",
        "recommendation": "Regenerate the source report with --shipguard-eval after adding reportQualityQuestions.",
    }


def build_next_actions(priority_action: dict[str, Any], ranked_questions: list[dict[str, Any]]) -> list[str]:
    kind = priority_action.get("kind")
    if kind == "fix-report-quality-finding":
        return [
            priority_action["summary"],
            "Regenerate the affected report and rerun ios report-quality before using it as product-QA evidence.",
            "After report-quality passes, convert the highest-priority remaining question into a public fixture or eval case.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
            "Use shipguard ios redact before sharing reports outside the local development loop.",
        ]
    if kind == "answer-actionability-question":
        return [
            priority_action["summary"],
            "Answer the actionability questions above in priority order instead of choosing from an unranked list.",
            "If the top question is not already covered by Fixture Coverage, convert the answer into a public fixture, eval case, report section, or docs change before editing ShipGuard rules.",
            "If implementation needs planning, feed this report-quality output into ios spec-workflow with --from-report.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
        ]
    if kind == "review-existing-fixture":
        return [
            priority_action["summary"],
            "Run the existing fixture through ios report-quality before creating another fixture for the same question.",
            "Move to the next uncovered actionability question once the existing fixture still passes.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
        ]
    if kind == "all-actionability-covered":
        return [
            priority_action["summary"],
            "Keep the Fixture Coverage section as proof that known questions are covered.",
            "Run the next read-only ShipGuard QA source, such as value-gauntlet plus full-audit or targeted command-family reports.",
            "Only create another fixture when a new uncovered report-quality question appears.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
        ]
    if ranked_questions:
        return [
            "Answer the actionability questions above to decide which ShipGuard rule, report section, fixture, or doc should improve next.",
            "Convert repeated report-quality weaknesses into public fixtures or eval cases.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
        ]
    return [
        priority_action["summary"],
        "Convert repeated report-quality weaknesses into public fixtures or eval cases.",
        "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
    ]


def next_command_for_priority_action(priority_action: dict[str, Any]) -> str:
    kind = str(priority_action.get("kind") or "")
    if kind == "fix-report-quality-finding":
        return "./bin/shipguard ios report-quality --reports <fixed-report-dir> --out <quality-dir> --shareable"
    if kind == "answer-actionability-question":
        question = str(priority_action.get("question") or "")
        if should_create_fixture_candidate(question):
            return (
                "./bin/shipguard ios report-quality --reports <report-dir> --out <quality-dir> "
                "--shareable --write-fixture-candidates <fixture-output-dir>"
            )
        return (
            './bin/shipguard ios spec-workflow --path <repo> --feature "Answer report-quality priority action" '
            "--from-report <report-quality-dir> --out <spec-dir> --shipguard-eval --shareable"
        )
    if kind == "review-existing-fixture":
        return "./bin/shipguard ios report-quality --reports <next-report-dir> --out <quality-dir> --shareable"
    if kind == "all-actionability-covered":
        return (
            "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet && "
            "./bin/shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable"
        )
    if kind == "add-actionability-questions":
        return "./bin/shipguard ios report-quality --reports <updated-report-dir> --out <quality-dir> --shareable"
    return "./bin/shipguard ios report-quality --reports <report-dir> --out <quality-dir> --shareable"


def slugify(value: object, *, limit: int = 72) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    if len(text) <= limit:
        return text or "report-quality-fixture"
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    trimmed_limit = max(1, limit - len(digest) - 1)
    trimmed = text[:trimmed_limit].strip("-") or "report-quality-fixture"
    return f"{trimmed}-{digest}"


def fixture_type_for_question(question: str, tool: str) -> str:
    text = normalized_question_text(f"{tool} {question}")
    question_text = normalized_question_text(question)
    if (
        tool in {"shipguard prepare", "shipguard verify"}
        or tool == "shipguard action verify-pr"
        or "task contract" in text
        or "verify-first" in text
        or "verify-pr" in text
        or "proof report" in text
        or "unsupported completion claim" in text
        or "durable object" in text
    ):
        return "shipguard-verify-first-task-contract-fixture"
    if (
        tool == "shipguard codex marketplace-readiness"
        or "marketplace-readiness" in text
        or "marketplacedeck" in text
    ):
        return "shipguard-marketplace-readiness-fixture"
    if tool == "shipguard docs-check" or "docs-check" in text or "docslink" in text:
        return "shipguard-docs-check-report-fixture"
    if (
        tool.startswith("shipguard lean ")
        or "lean deck" in text
        or "ponytail" in text
        or "one-check" in text
        or "one runnable check" in text
        or "gain honesty" in text
        or "fake per-repo" in text
    ):
        return "shipguard-lean-report-quality-fixture"
    if tool == "shipguard full-audit" and (
        "proof boundaries" in question_text
        or "proof boundary" in question_text
        or "pushing" in question_text
        or "publishing" in question_text
        or "target apps" in question_text
        or "resumable evidence lane" in question_text
        or "slow lanes" in question_text
        or "slash handoff" in question_text
    ):
        return "shipguard-full-audit-proof-boundary-fixture"
    if tool == "shipguard inspect" and (
        "inspectdeck" in question_text
        or "source proof" in question_text
        or "missing inputs" in question_text
        or "underlying full-audit" in question_text
        or "plugin evidence" in question_text
    ):
        return "shipguard-inspect-proof-state-fixture"
    if is_launchdeck_receipt_question(question_text, tool):
        return "ios-launchdeck-receipt-quality-fixture"
    if "design-system coherence" in question_text or "design coherence" in question_text:
        return "ios-design-coherence-boundary-fixture"
    if "private-app" in question_text or "private app" in question_text or "target-app" in question_text or "target app" in question_text:
        return "shipguard-eval-boundary-fixture"
    if (
        tool == "shipguard v4 preview"
        or "v4 preview" in text
        or "shipguard v4 preview" in text
        or "preview-only" in question_text
    ):
        return "shipguard-v4-preview-quality-fixture"
    if "grouped performance" in text or "performance" in text:
        return "ios-performance-report-quality-fixture"
    if "preview" in text or "devspace" in text or "visual proof" in text:
        return "ios-preview-devspace-routing-fixture"
    if (
        "product release" in text
        or "stable publication" in text
        or "stable-publication" in text
        or "launch relay" in text
        or "product hunt" in text
        or "public posting" in text
        or "stable v4" in text
        or "stable-v4" in text
        or "release proof" in text
        or "release consumption" in text
        or "rollback proof" in text
        or "external adoption" in text
        or "security review" in text
    ):
        return "shipguard-release-proof-quality-fixture"
    if (
        "proof boundary" in text
        or "branded name" in text
        or "branded names" in text
        or "useful-looking surface" in text
        or "useful looking surface" in text
    ):
        return "shipguard-surface-proof-boundary-fixture"
    if (
        "plugin skill" in text
        or "plugin skills" in text
        or "starter skill" in text
        or "starter skills" in text
        or "actionable routing" in text
        or "validation commands" in text
    ):
        return "shipguard-plugin-skill-routing-fixture"
    if "design" in text or "app type" in text or "coherence" in text:
        return "ios-design-report-quality-fixture"
    if "evidence" in text or "source suspicion" in text:
        return "report-evidence-promotion-fixture"
    return "report-quality-actionability-fixture"


def should_create_fixture_candidate(question: str) -> bool:
    text = normalized_question_text(question)
    return any(
        token in text
        for token in (
            "fixture",
            "eval case",
            "public",
            "private-app",
            "private app",
            "target-app",
            "target app",
            "grouped performance",
            "devspace",
            "preview",
            "app type",
            "evidence would promote",
            "receipt",
            "execution receipt",
            "execution proof",
            "proof for the selected lane",
            "resumable evidence lane",
            "manual validation ceremony",
            "slow lanes",
            "slash handoff",
            "product release",
            "stable v4",
            "stable-v4",
            "stable publication",
            "stable-publication",
            "launch relay",
            "product hunt",
            "explicit human approval",
            "public posting",
            "release proof",
            "release consumption",
            "rollback proof",
            "external adoption",
            "security review",
            "proof boundary",
            "branded name",
            "branded names",
            "useful-looking surface",
            "useful looking surface",
            "plugin skill",
            "plugin skills",
            "starter skill",
            "starter skills",
            "actionable routing",
            "validation commands",
            "inspectdeck",
            "source proof",
            "missing inputs",
            "underlying full-audit",
            "plugin evidence",
            "fresh codex user",
            "plugin listing",
            "marketplace submission",
            "submission packet",
            "composer icon",
            "screenshot policy",
            "model-choice boundary",
            "github about",
            "social preview",
            "docs/index",
            "first-time users",
            "command dump",
            "release wall",
            "onboarding",
            "plugin install freshness",
            "tracked source",
            "strict status",
            "docs-check",
            "docslink",
            "stable tool name",
            "local documentation links",
            "external urls",
            "in-page anchors",
            "concrete next proof step",
            "broad product wish",
            "roadmap prose",
            "task contract",
            "durable object",
            "goal, risk, scope, proof",
            "unsupported completion claim",
            "unsupported completion claims",
            "exact next action",
            "fresh maintainer",
            "freshmaintainerfailureguide",
            "first blocker",
            "failure guide",
            "runtime reviewer",
            "reviewer handoff",
            "proof-to-attach",
            "proof to attach",
            "merge verdict",
            "vague status note",
            "precisionreview",
            "delete, simplify, keep",
            "proof-blocked",
            "lean deck",
            "lean review",
            "leandebtledger",
            "lean debt",
            "shortcut marker",
            "shortcut markers",
            "which marker will rot",
            "rot-risk",
            "rot risk",
            "without another source inspection",
            "upgrade trigger",
            "benchmark savings",
            "measurable in this repo",
            "benchmark-backed impact",
            "fake per-repo",
            "safety-boundary",
            "host adapters",
            "hardware calibration",
            "same-diff proof signals",
            "runnable check",
            "delete clutter",
            "permission-state",
            "denied-state",
            "physical-device prompt",
            "owner scopes",
            "review-only lifecycle",
            "forbidden entitlement",
            "forbidden entitlement/project",
        )
    )


def fixture_candidate_for_question(row: dict[str, Any], index: int) -> dict[str, Any]:
    question = str(row.get("question") or "")
    normalized_question = normalized_question_text(question)
    tool = str(row.get("tool") or "unknown")
    fixture_type = fixture_type_for_question(question, tool)
    candidate_id = f"{index:02d}-{slugify(f'{tool} {question}', limit=64)}"
    source_reports = [str(row.get("report") or "<unknown-report>")]
    for report in row.get("duplicateReports") or []:
        if isinstance(report, str) and report not in source_reports:
            source_reports.append(report)
    expected_assertions = [
        "report-quality preserves the actionability question in JSON and Markdown",
        "report-quality emits a fixtureCandidates entry for the public synthetic case",
        "the fixture keeps scopeBoundary.shipguardOnly and targetAppsReadOnly explicit",
        "shareable output contains no local absolute paths or private app identifiers",
    ]
    if tool == "shipguard lean review":
        expected_assertions.extend(
            [
                "the fixture exposes currentDiffDecisionMap.scope as current-diff-only",
                "the fixture exposes currentDiffDecisionMap decisions and the delete/simplify subset",
                "the Markdown exposes Current Diff Decision Map plus the whole-repo non-claim and lean-audit fallback",
            ]
        )
        if "runnable check" in normalized_question or "proofsignalcalibration" in normalized_question:
            expected_assertions.extend(
                [
                    "the fixture exposes runnableCheckReview.missingProofFindings for non-trivial logic without proof",
                    "the fixture exposes runnableCheckReview.sameDiffProofFindings for non-trivial logic with a matching same-diff proof signal",
                    "the fixture exposes proofSignalCalibration counts for missing proof and same-diff proof without treating unrelated tests as global proof",
                    "the fixture exposes proofSignalMatching rows plus unmatched proof signals so unrelated tests are not global proof",
                    "the Markdown exposes Runnable Check Review, Missing Runnable Checks, Same-Diff Proof Signals, and the non-ceremony boundary",
                    "the Markdown exposes Proof Signal Matching and Unmatched Proof Signals",
                ]
            )
        if "hardware calibration" in normalized_question and "host boundaries" in normalized_question:
            expected_assertions.extend(
                [
                    "the fixture exposes hardwareHostBoundaryReview.hardwareCalibrationFindings for physical-device proof-blocked rows",
                    "the fixture exposes hardwareHostBoundaryReview.hostAdapterBoundaryFindings for host/plugin adapter keep rows",
                    "the fixture currentDiffDecisionMap proof-blocks hardware calibration and keeps host adapters",
                    "the Markdown exposes Hardware And Host Boundary Review, Hardware Calibration Proof, and Host Adapter Boundaries",
                ]
            )
        if "safety-boundary code" in normalized_question and "automatic deletion" in normalized_question:
            expected_assertions.extend(
                [
                    "the fixture exposes safetyBoundaryReview.safetyBoundaryFindings for keep-with-proof safety rows",
                    "the fixture currentDiffDecisionMap keeps safety-boundary files instead of deleting or proof-blocking them",
                    "the Markdown exposes Safety Boundary Review and Keep With Proof Boundaries",
                ]
            )
        if (
            "selected lite full ultra mode" in normalized_question
            or "bias first actions accordingly" in normalized_question
            or "first action bias" in normalized_question
        ):
            expected_assertions.extend(
                [
                    "the fixture exposes leanMode.mode and leanMode.firstActionBias for the selected mode",
                    "the fixture exposes modeBiasReview.supportedModes for lite, full, and ultra",
                    "the fixture verifies precisionReview.topActions starts from the selected mode's priority order",
                    "the Markdown exposes Lean Mode and Mode Bias Review with the selected first-action bias",
                ]
            )
    if tool == "shipguard lean debt":
        expected_assertions.extend(
            [
                "the fixture exposes markerVisibilityReview.summary counts for total, visible, ceiling, missing-ceiling, upgrade-trigger, missing-trigger, upgrade-status, and omitted marker rows",
                "the fixture exposes markerVisibilityReview.visibilityRows for tracked and needs-trigger shortcuts",
                "the fixture keeps every shortcut marker location, ceiling, and upgrade-trigger status visible without claiming benchmark savings",
                "the Markdown exposes Marker Visibility Review with the same shortcut rows before the raw ledger table",
            ]
        )
        if "benchmark savings" in normalized_question or "measurable in this repo" in normalized_question:
            expected_assertions.extend(
                [
                    "the fixture exposes currentRepoBoundary.perRepoSavingsClaim as not-computed",
                    "the fixture states shortcut markers are shortcut-ledger evidence only and do not prove current-repo line, token, cost, or time savings",
                    "the fixture routes benchmark direction to shipguard lean gain instead of treating Lean Debt marker counts as savings",
                    "the Markdown exposes Benchmark Savings Boundary with the not-computed claim and lean gain route",
                ]
            )
        if (
            "which marker will rot" in normalized_question
            or "without another source inspection" in normalized_question
            or "rot risk" in normalized_question
            or "trigger rot" in normalized_question
            or ("exact next action" in normalized_question and "proof" in normalized_question)
        ):
            expected_assertions.extend(
                [
                    "the fixture exposes rotRiskReview.summary with total, high-risk, review-risk, tracked, missing-ceiling, missing-trigger, omitted, and top-risk fields",
                    "the fixture exposes rotRiskReview.prioritizedRows sorted by missing ceiling, missing upgrade trigger, then tracked trigger watch rows",
                    "each rot-risk row includes the marker location, rot reason, next action, and proof guidance so no source inspection is needed to pick the first cleanup bet",
                    "each rot-risk row includes triggerWatchContract with trigger condition, exact next action, check route, proof artifact, and stop condition",
                    "the Markdown exposes Trigger-Watch Contracts beside the Rot-Risk Review rows",
                    "the Markdown exposes Rot-Risk Review with the same prioritized rows and top-risk location",
                ]
            )
    if tool in {"shipguard prepare", "shipguard verify"}:
        expected_assertions.extend(
            [
                "the fixture exposes quickstartReplay so a fresh maintainer can reach or replay the first useful verdict",
                "the fixture Markdown exposes Quickstart Replay without requiring JSON inspection",
                "prepare fixtures connect goal, risk, scope, proof, claims, verdict, and next action through the replay contract",
                "verify fixtures expose replay command, fast verdict, review packet, and next action",
            ]
        )
    if tool == "shipguard prepare" and is_notification_scope_question(question):
        expected_assertions.extend(
            [
                "the fixture exposes domainRiskPack.id=ios-notification-permission-workflow",
                "the fixture exposes scopeRecommendations.authorized rows with source/test owner patterns and reasons",
                "the fixture exposes scopeRecommendations.reviewOnly rows for Info.plist, AppDelegate, and SceneDelegate with reasons",
                "the fixture exposes scopeRecommendations.forbiddenUnlessExplicit rows for entitlements and project.pbxproj with reasons",
                "the fixture exposes permissionSensitiveFiles source signals that triggered the notification permission workflow",
                "the fixture Markdown renders iOS Notification Permission Workflow with authorized, review-only, and forbidden scope recommendations",
            ]
        )
    if tool == "shipguard prepare" and is_notification_proof_lane_question(question):
        expected_assertions.extend(
            [
                "the fixture exposes domainRiskPack.validationReceiptRequirements for permission-state, denied-state, and not-determined-state scope labels",
                "the fixture exposes a failure meaning that generic validation is not notification permission workflow proof",
                "the fixture nextAction asks for structured receipt scope labels instead of a generic test log",
                "the fixture Markdown renders receipt requirements, failure meanings, permission-state, denied-state, and the generic-test boundary",
            ]
        )
        if is_notification_simulator_device_boundary_question(question):
            expected_assertions.extend(
                [
                    "the fixture exposes simulator-denied-state-recovery and physical-device-prompt-boundary receipt requirements separately",
                    "the fixture exposes proofBoundaries explaining simulator proof is not physical-device prompt proof",
                    "the fixture nextAction distinguishes local simulator permission reset proof from remaining manual/device release proof",
                    "the fixture Markdown renders simulator-denied-state-recovery, simulator-permission-reset, physical-device-prompt-boundary, and the release-claim boundary",
                ]
            )
    if tool == "shipguard verify" and "unsupported completion claim" in normalized_question_text(question):
        expected_assertions.extend(
            [
                "the fixture exposes unsupportedClaimReplay with the rejected claim, proof phrase, replay command, and next action",
                "the fixture Markdown renders Unsupported Claim Replay and tells the developer to revise the claim or attach structured evidence",
                "the fixture keeps replay non-claims clear so a blocked verdict is not treated as product proof or merge approval",
            ]
        )
    if tool == "shipguard verify" and is_notification_proof_lane_question(question):
        expected_assertions.extend(
            [
                "the fixture exposes notificationPermissionWorkflow.proofLanes for permission-state-validation and denied-state-recovery",
                "artifact-only generic evidence keeps the verify verdict at review instead of pass",
                "the fixture nextAction asks for structured permission-state and denied-state receipts",
                "the fixture Markdown renders proof lanes, required receipt scopes, and the generic receipt boundary",
            ]
        )
        if is_notification_simulator_device_boundary_question(question):
            expected_assertions.extend(
                [
                    "the fixture exposes simulator-permission-reset and physical-device-prompt as separate proof lanes",
                    "the physical-device-prompt lane stays manual-required until a real device/manual receipt is attached",
                    "local simulator proof does not become a release or fully verified claim",
                    "the fixture Markdown renders simulator-permission-reset, physical-device-prompt, manual-required, and release claims",
                ]
            )
    return {
        "priority": index,
        "candidateId": candidate_id,
        "fixtureType": fixture_type,
        "sourceTool": tool,
        "sourceReports": source_reports[:8],
        "sourceQuestion": question,
        "duplicateCount": int(row.get("duplicateCount") or 1),
        "publicFixturePath": f"fixtures/ios-report-quality/{candidate_id}",
        "publicFixtureRecipe": (
            "Create a minimal synthetic ShipGuard report pair that reproduces this report-quality question without private app code, "
            "local paths, screenshots, customer data, app names, or proprietary source snippets."
        ),
        "expectedAssertions": expected_assertions,
        "validationCommands": [
            "./bin/shipguard ios report-quality --reports <fixture-dir> --out <quality-dir> --shareable",
            "./tests/ios_report_quality_test.sh",
        ],
        "materialization": {
            "safeSyntheticOnly": True,
            "writeCommand": "./bin/shipguard ios report-quality --reports <report-dir> --out <quality-dir> --shareable --write-fixture-candidates <fixture-output-dir>",
            "files": [
                "README.md",
                "fixture-candidate.json",
                "fixture-report.json",
                "fixture-report.md",
            ],
        },
        "privateDataPolicy": "Use the private app report only to choose the shape of the public fixture. Do not copy private code, local paths, screenshots, app-specific identifiers, or proprietary text into the fixture.",
    }


def existing_public_fixture_index(cwd: Path) -> dict[str, dict[str, Any]]:
    root = cwd / "fixtures" / "ios-report-quality"
    if not root.is_dir():
        return {}

    fixtures: dict[str, dict[str, Any]] = {}
    for candidate_path in sorted(root.rglob("fixture-candidate.json")):
        metadata = read_json(candidate_path)
        if not isinstance(metadata, dict):
            continue
        source_question = str(metadata.get("sourceQuestion") or "").strip()
        if not source_question:
            continue
        key = normalized_question_text(source_question)
        if not key or key in fixtures:
            continue
        try:
            public_path = candidate_path.parent.relative_to(cwd).as_posix()
        except ValueError:
            public_path = "<public-fixture-path>"
        fixtures[key] = {
            "candidateId": metadata.get("candidateId") or candidate_path.parent.name,
            "fixtureType": metadata.get("fixtureType") or "report-quality-actionability-fixture",
            "publicFixturePath": public_path,
            "sourceQuestion": source_question,
            "sourceTool": metadata.get("sourceTool") or "unknown",
        }
    return fixtures


def annotate_existing_fixture_coverage(
    ranked_questions: list[dict[str, Any]],
    *,
    existing_fixtures: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    coverage: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in ranked_questions:
        key = normalized_question_text(row.get("question") or "")
        match = existing_fixtures.get(key)
        if not match:
            continue
        row["existingFixture"] = dict(match)
        row["existingFixturePath"] = match.get("publicFixturePath")
        if key in seen:
            continue
        seen.add(key)
        coverage.append(
            {
                "priority": row.get("priority"),
                "tool": row.get("tool"),
                "report": row.get("report"),
                "question": row.get("question"),
                "publicFixturePath": match.get("publicFixturePath"),
                "fixtureType": match.get("fixtureType"),
                "candidateId": match.get("candidateId"),
                "sourceTool": match.get("sourceTool"),
            }
        )
    return coverage


def build_fixture_candidates(ranked_questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen_types: set[str] = set()
    for row in ranked_questions:
        if row.get("sourceMaterializedFixture") or row.get("existingFixture"):
            continue
        question = str(row.get("question") or "")
        if not should_create_fixture_candidate(question):
            continue
        fixture_type = fixture_type_for_question(question, str(row.get("tool") or "unknown"))
        # Keep the list compact, but allow repeated fixture-focused questions to surface when they cover different report types.
        if fixture_type in seen_types and len(candidates) >= 5:
            continue
        seen_types.add(fixture_type)
        candidates.append(fixture_candidate_for_question(row, len(candidates) + 1))
        if len(candidates) >= 8:
            break
    return candidates


def stable_publication_external_evidence_fixture_index(
    existing_fixtures: dict[str, dict[str, Any]],
    fixture_coverage: list[dict[str, Any]],
) -> dict[str, Any]:
    source_class_polish_summary = [
        {
            "evidence": "independent-adoption-evidence",
            "acceptedEvidenceClasses": ["public-external", "private-redacted-external"],
            "requiredRelationshipField": "actorRelationship",
            "acceptedRelationships": ["independent"],
            "rejectedSubstitutes": [
                "GitHub stars",
                "GitHub forks",
                "download counts",
                "maintainer-only private app runs",
                "fixtureSynthetic records",
                "stale generatedAt records",
                "unchanged starter templates",
            ],
            "passBoundary": "Requires redacted/public command and artifact evidence from an independent actor.",
        },
        {
            "evidence": "final-security-review-evidence",
            "acceptedEvidenceClasses": ["public-security-review", "private-redacted-security-review"],
            "requiredRelationshipField": "reviewerRelationship",
            "acceptedRelationships": ["independent", "maintainer-security-review"],
            "rejectedSubstitutes": [
                "fixtureSynthetic records",
                "stale generatedAt records",
                "vague self-review notes",
                "missing required surfaces",
                "open critical/high findings",
                "unchanged starter templates",
            ],
            "passBoundary": "Requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/high findings.",
        },
    ]
    relationship_gate_summary = [
        {
            "evidence": "independent-adoption-evidence",
            "requiredRelationshipField": "actorRelationship",
            "acceptedRelationships": ["independent"],
            "rejectedRelationships": ["maintainer", "self", "fixtureSynthetic", "unknown"],
            "blockedSubstitute": "maintainer-only private app runs",
            "passBoundary": "Adoption proof requires an independent external actor plus commands, artifacts, redaction, outcome, and non-claims.",
        },
        {
            "evidence": "final-security-review-evidence",
            "requiredRelationshipField": "reviewerRelationship",
            "acceptedRelationships": ["independent", "maintainer-security-review"],
            "rejectedRelationships": ["self", "unknown", "fixtureSynthetic"],
            "blockedSubstitute": "vague self-review notes",
            "passBoundary": "Security proof requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/high findings.",
        },
    ]
    artifact_redaction_summary = [
        {
            "evidence": "independent-adoption-evidence",
            "requiredArtifactFields": ["commands", "artifacts", "privateDataRedacted", "outcome", "nonClaims"],
            "rejectedArtifactProof": [
                "local absolute paths",
                "private screenshots",
                "tokens or account identifiers",
                "unreviewed app-specific notes",
                "missing artifact links",
            ],
            "blockedSubstitute": "private unredacted maintainer artifacts",
            "passBoundary": "Adoption proof requires redacted/public command and artifact evidence with privateDataRedacted=true plus outcome and non-claims.",
        },
        {
            "evidence": "final-security-review-evidence",
            "requiredArtifactFields": [
                "methodology",
                "commands",
                "artifacts",
                "privateDataRedacted",
                "findingsSummary",
                "nonClaims",
            ],
            "rejectedArtifactProof": [
                "vague self-review notes",
                "local absolute paths",
                "private screenshots",
                "tokens or account identifiers",
                "missing methodology",
            ],
            "blockedSubstitute": "unredacted or provenance-free security notes",
            "passBoundary": "Security proof requires reviewed stable-v4 surfaces, methodology, redacted artifacts, findings summary, and no open critical/high findings.",
        },
    ]
    artifact_digest_provenance_summary = [
        {
            "evidence": "independent-adoption-evidence",
            "requiredArtifactProof": ["artifactName", "sha256 or digest", "sourceUrl or sourceCommand", "privateDataRedacted", "capturedAt"],
            "rejectedArtifactProof": [
                "filename only",
                "local absolute path only",
                "private screenshot without digest",
                "missing source command",
                "missing capturedAt",
            ],
            "blockedSubstitute": "artifact names without digest or public/source provenance",
            "passBoundary": "Adoption proof artifacts must include a digest or public/source provenance plus redaction and outcome fields.",
        },
        {
            "evidence": "final-security-review-evidence",
            "requiredArtifactProof": ["artifactName", "sha256 or digest", "reviewSource", "methodology", "privateDataRedacted", "capturedAt"],
            "rejectedArtifactProof": [
                "filename only",
                "vague self-review note",
                "private screenshot without digest",
                "missing methodology",
                "missing review source",
            ],
            "blockedSubstitute": "security notes that name artifacts but omit digest or review-source provenance",
            "passBoundary": "Security proof artifacts must include digest or review-source provenance plus methodology, redaction, and findings summary.",
        },
    ]
    review_scope_mapping_summary = [
        {
            "evidence": "final-security-review-evidence",
            "requiredScope": ["cli", "plugin", "github-actions", "release-proof", "package-install", "redaction-privacy"],
            "requiredMappingFields": ["surface", "releaseScope", "methodology", "evidenceArtifact", "findingStatus"],
            "rejectedReviewProof": [
                "broad reviewed everything wording",
                "missing surface list",
                "missing release scope mapping",
                "unmapped scanner output",
                "methodology without covered surfaces",
            ],
            "blockedSubstitute": "generic final security review notes without stable-v4 surface mapping",
            "passBoundary": "Final security-review proof must map each reviewed surface to the stable-v4 release scope and evidence artifact.",
        }
    ]
    expiry_window_summary = [
        {
            "evidence": "independent-adoption-evidence",
            "requiredExpiryFields": ["generatedAt", "validUntil or expiresAt", "maxEvidenceAgeDays", "releaseManifestGeneratedAt"],
            "rejectedFreshnessProof": [
                "generatedAt only",
                "open-ended adoption record",
                "stale validUntil",
                "missing max evidence age",
                "fixtureSynthetic refresh",
            ],
            "blockedSubstitute": "fresh-looking adoption record without an explicit expiry window",
            "passBoundary": "Adoption proof must state an expiry window or max age in addition to generatedAt freshness.",
        },
        {
            "evidence": "final-security-review-evidence",
            "requiredExpiryFields": ["generatedAt", "validUntil or expiresAt", "maxEvidenceAgeDays", "reviewedReleaseVersion"],
            "rejectedFreshnessProof": [
                "generatedAt only",
                "open-ended security review",
                "stale validUntil",
                "missing reviewed release version",
                "reused old review packet",
            ],
            "blockedSubstitute": "security-review record without explicit expiry or reviewed-release boundary",
            "passBoundary": "Security proof must state the release version and expiry window for the review packet.",
        },
    ]
    expected = [
        {
            "id": "independent-adoption-evidence",
            "label": "Independent adoption evidence",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist",
            "rejectionProved": "weak adoption signals rejected",
            "requiredProof": [
                "independent actor",
                "commands",
                "artifacts",
                "redaction",
                "outcome",
                "non-claims",
            ],
        },
        {
            "id": "final-security-review-evidence",
            "label": "Final security-review evidence",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist",
            "rejectionProved": "vague security evidence rejected",
            "requiredProof": [
                "reviewed surfaces",
                "severity thresholds",
                "redaction",
                "methodology",
                "findings summary",
                "non-claims",
            ],
        },
        {
            "id": "external-evidence-freshness-fixture",
            "label": "External evidence freshness",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-freshness",
            "rejectionProved": "stale adoption/security evidence rejected",
            "requiredProof": [
                "release manifest generatedAt",
                "evidence generatedAt",
                "stale record count",
                "freshness boundary",
                "non-claims",
            ],
        },
        {
            "id": "external-evidence-source-class-fixture",
            "label": "External evidence source classes",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-source-classes",
            "rejectionProved": "weak substitutes rejected as adoption/security proof",
            "requiredProof": [
                "accepted evidence classes",
                "actor/reviewer relationship fields",
                "accepted relationships",
                "rejected substitutes",
                "pass boundaries",
                "Markdown visibility",
            ],
        },
        {
            "id": "external-evidence-relationship-gate-fixture",
            "label": "External evidence relationship gates",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-relationship-gates",
            "rejectionProved": "wrong actor/reviewer relationships rejected as adoption/security proof",
            "requiredProof": [
                "actorRelationship gate",
                "reviewerRelationship gate",
                "accepted relationships",
                "rejected relationships",
                "blocked substitutes",
                "pass boundaries",
                "Markdown visibility",
            ],
        },
        {
            "id": "external-evidence-artifact-redaction-fixture",
            "label": "External evidence artifact redaction",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-artifact-redaction",
            "rejectionProved": "unredacted or provenance-free artifacts rejected as adoption/security proof",
            "requiredProof": [
                "required artifact fields",
                "privateDataRedacted gate",
                "accepted artifact proof",
                "rejected artifact proof",
                "blocked substitutes",
                "Markdown visibility",
            ],
        },
        {
            "id": "external-evidence-artifact-digest-provenance-fixture",
            "label": "External evidence artifact digest provenance",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-artifact-digest-provenance",
            "rejectionProved": "filename-only artifacts rejected as adoption/security proof",
            "requiredProof": [
                "artifact digest",
                "source provenance",
                "capturedAt",
                "privateDataRedacted gate",
                "blocked substitutes",
                "Markdown visibility",
            ],
        },
        {
            "id": "external-evidence-review-scope-mapping-fixture",
            "label": "External evidence review-scope mapping",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-review-scope-mapping",
            "rejectionProved": "broad security-review wording rejected as final security proof",
            "requiredProof": [
                "required review surfaces",
                "stable-v4 scope mapping",
                "methodology per surface",
                "evidence artifact per surface",
                "blocked substitutes",
                "Markdown visibility",
            ],
        },
        {
            "id": "external-evidence-expiry-window-fixture",
            "label": "External evidence expiry window",
            "publicFixturePath": "fixtures/ios-report-quality/stable-publication-external-evidence-expiry-window",
            "rejectionProved": "open-ended external evidence rejected as stable-publication proof",
            "requiredProof": [
                "generatedAt",
                "validUntil or expiresAt",
                "max evidence age",
                "release manifest generatedAt",
                "blocked substitutes",
                "Markdown visibility",
            ],
        },
    ]
    by_path = {
        str(item.get("publicFixturePath") or ""): item
        for item in existing_fixtures.values()
        if isinstance(item, dict)
    }
    covered_paths = {str(item.get("publicFixturePath") or "") for item in fixture_coverage if isinstance(item, dict)}
    rows: list[dict[str, Any]] = []
    for item in expected:
        path = item["publicFixturePath"]
        fixture = by_path.get(path) or {}
        rows.append(
            {
                **item,
                "status": "covered" if fixture else "missing",
                "candidateId": fixture.get("candidateId") or Path(path).name,
                "sourceQuestion": fixture.get("sourceQuestion") or "",
                "coveredInCurrentRun": path in covered_paths,
            }
        )
    missing = [row for row in rows if row["status"] != "covered"]
    next_gap_candidates: list[dict[str, Any]] = []
    next_target = missing[0] if missing else {}
    covered_classes = [row["id"] for row in rows if row["status"] == "covered"]
    remaining_questions = [gap["id"] for gap in next_gap_candidates]
    non_claims = [
        "Fixture coverage proves report-quality behavior only.",
        "Fixture coverage is not independent adoption evidence.",
        "Fixture coverage is not final security-review evidence.",
        "Fixture coverage does not prove stable-v4 publication.",
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "pass" if not missing else "review",
        "purpose": "Compact index of public stable-publication external-evidence fixture coverage.",
        "coveredCount": len(rows) - len(missing),
        "expectedCount": len(rows),
        "decisionSummary": {
            "verdict": "Adoption, security-review, freshness, source-class, relationship-gate, artifact-redaction, artifact digest/provenance, review-scope mapping, and expiry-window fixture questions are covered; evaluate the next real QA gap."
            if not missing
            else "Stable-publication external evidence fixture coverage is incomplete.",
            "coveredEvidenceClasses": covered_classes,
            "remainingExternalEvidenceQuestions": remaining_questions,
            "nextPromotionTarget": next_target.get("id") or next_target.get("candidateId") or "none",
            "nonClaimSummary": "This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.",
        },
        "sourceClassPolishSummary": source_class_polish_summary,
        "relationshipGateSummary": relationship_gate_summary,
        "artifactRedactionSummary": artifact_redaction_summary,
        "artifactDigestProvenanceSummary": artifact_digest_provenance_summary,
        "reviewScopeMappingSummary": review_scope_mapping_summary,
        "expiryWindowSummary": expiry_window_summary,
        "rows": rows,
        "coverage": rows,
        "remainingExternalEvidenceGaps": next_gap_candidates,
        "nextFixtureToPromote": next_target,
        "nextGapCandidateBacklog": next_gap_candidates,
        "nonClaims": non_claims,
    }


def build_report(inputs: list[str], *, shareable: bool = False, shipguard_eval: bool = False) -> dict[str, Any]:
    paths = report_json_files(inputs)
    promotion_manifest_paths = fixture_promotion_manifest_files(inputs)
    input_paths = resolved_input_paths(inputs)
    cwd = Path.cwd().resolve()
    skipped_reports = skipped_report_json_files(inputs)
    graded = [grade_report(path, input_paths=input_paths, shareable=shareable, cwd=cwd) for path in paths]
    promotion_manifests = [
        promotion_manifest_report(path, input_paths=input_paths, shareable=shareable, cwd=cwd)
        for path in promotion_manifest_paths
    ]
    issues = []
    source_findings = []
    actionability_questions = []
    for item in graded:
        for issue in item["issues"]:
            issues.append({**issue, "report": item["path"], "tool": item.get("tool")})
        source_findings.extend(item.get("sourceFindings", []))
        actionability_questions.extend(item.get("actionabilityQuestions", []))
    for item in promotion_manifests:
        for issue in item["issues"]:
            issues.append({**issue, "report": item["path"], "tool": REPORT_QUALITY_TOOL})
    average = round(sum(item["score"] for item in graded) / len(graded), 1)
    status = report_status(issues)
    actionability_questions = dedupe_question_rows(actionability_questions)
    ranked_questions = ranked_actionability_questions(graded)
    existing_fixtures = existing_public_fixture_index(cwd)
    fixture_coverage = annotate_existing_fixture_coverage(
        ranked_questions,
        existing_fixtures=existing_fixtures,
    )
    external_evidence_index = stable_publication_external_evidence_fixture_index(
        existing_fixtures,
        fixture_coverage,
    )
    fixture_candidates = build_fixture_candidates(ranked_questions)
    priority_action = build_priority_action(issues, ranked_questions)
    next_actions = build_next_actions(priority_action, ranked_questions)
    next_command = next_command_for_priority_action(priority_action)
    priority_action["nextCommand"] = next_command
    result_ux = build_result_ux(
        status=status,
        summary=(
            "Report-quality inputs are actionable and shareable."
            if status == "pass"
            else "Report-quality inputs need structural fixes before they should drive implementation."
        ),
        proof_source="graded ShipGuard report JSON, paired Markdown, actionability questions, and shareability checks",
        why_it_matters="This keeps ShipGuard improving its own reports instead of converting target-app findings into accidental app work.",
        next_command=next_command,
        next_action_summary=str(priority_action.get("summary") or priority_action.get("recommendation") or next_command),
    )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": REPORT_QUALITY_TOOL,
        "intent": "shipguard-evaluation" if shipguard_eval else "report-quality",
        "generatedAt": utc_now(),
        "status": status,
        "reportCount": len(graded),
        "averageScore": average,
        "inputs": [path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd) for path in input_paths],
        "skippedReportDiscovery": {
            "skippedReportCount": len(skipped_reports),
            "skippedReports": [
                {
                    "path": path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd),
                    "skippedDirectory": skipped_dir,
                    "reason": "generated proof or package evidence directory; graded through the root ShipGuard report instead",
                }
                for path, skipped_dir in skipped_reports[:50]
            ],
            "truncated": len(skipped_reports) > 50,
            "skipDirectoryNames": sorted(SOURCE_REPORT_SKIP_DIR_NAMES),
        },
        "shareability": {
            "mode": "shareable" if shareable else "local",
            "localAbsolutePathsIncluded": not shareable,
            "note": "Use --shareable before moving report-quality output into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence."
            if not shareable
            else "Local absolute input and report paths are omitted from report-quality fields.",
        },
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Grade ShipGuard report usefulness; do not convert target-app findings into app work.",
            "explicitShipGuardEval": bool(shipguard_eval),
        },
        "reportQualityQuestions": [
            "Did report-quality produce one concrete priority action without turning source findings into target-app work?",
        ]
        if shipguard_eval
        else [],
        "reports": graded,
        "fixturePromotionManifests": promotion_manifests,
        "findings": issues,
        "sourceFindings": source_findings[:80],
        "sourceIssueVisibility": {
            "sourceFindingCount": len(source_findings),
            "reportsWithSourceFindings": sum(1 for item in graded if int(item.get("sourceFindingCount") or 0) > 0),
            "note": "Source report findings are shown separately from report-quality findings so a structurally useful report can pass while its reviewed source issues remain visible.",
            "truncated": len(source_findings) > 80,
        },
        "actionabilityQuestions": actionability_questions[:30],
        "prioritizedActionabilityQuestions": ranked_questions[:30],
        "fixtureCoverage": fixture_coverage[:30],
        "stablePublicationExternalEvidenceFixtureIndex": external_evidence_index,
        "fixtureCandidates": fixture_candidates,
        "priorityAction": priority_action,
        "nextActions": next_actions,
        "resultUX": result_ux,
        "redactionPlan": build_redaction_plan(inputs, issues, input_paths=input_paths, shareable=shareable, cwd=cwd),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# iOS ShipGuard Report Quality",
        "",
        f"- Status: `{report['status']}`",
        f"- Reports: {report['reportCount']}",
        f"- Average score: {report['averageScore']}/100",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        "- Purpose: grade ShipGuard report usefulness, not target-app quality.",
        f"- ShipGuard-eval mode: `{'yes' if report.get('intent') == 'shipguard-evaluation' else 'no'}`",
        "",
        *render_result_markdown(report["resultUX"]),
        "## Reports",
        "",
        "| Score | Quality Status | Source Status | Tool | Surface | Intent | Report | Issues |",
        "| ---: | --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for item in report["reports"]:
        lines.append(
            f"| {item['score']} | {item['status']} | {item.get('reportStatus') or '-'} | `{table_cell(item.get('tool') or 'unknown', 40)}` | {table_cell(item.get('surface') or '-', 42)} | {item.get('intent') or '-'} | `{Path(item['path']).name}` | {item['issueCount']} |"
        )

    skipped = report.get("skippedReportDiscovery") or {}
    lines.extend(["", "## Skipped Generated Report Inputs", ""])
    lines.append(f"- Skipped JSON files: {skipped.get('skippedReportCount', 0)}")
    skipped_reports = skipped.get("skippedReports") or []
    if skipped_reports:
        lines.extend(["", "| Directory | Skipped JSON | Reason |", "| --- | --- | --- |"])
        for item in skipped_reports[:12]:
            lines.append(
                f"| `{table_cell(item.get('skippedDirectory') or '-', 40)}` | `{table_cell(item.get('path') or '-', 80)}` | {table_cell(item.get('reason') or '-', 100)} |"
            )
        if skipped.get("truncated"):
            lines.append("")
            lines.append("Additional skipped generated report inputs are preserved in JSON but omitted from this compact Markdown table.")
    else:
        lines.append("No generated proof directories were skipped.")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Report | Evidence | Recommendation |", "| --- | --- | --- | --- | --- |"])
        for finding in report["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['ruleId']}` | `{Path(finding['report']).name}` | {table_cell(finding['evidence'])} | {table_cell(finding['recommendation'])} |"
            )
    else:
        lines.append("No report-quality issues were detected.")

    source_visibility = report.get("sourceIssueVisibility") or {}
    source_findings = report.get("sourceFindings") or []
    lines.extend(["", "## Source Report Findings", ""])
    lines.append(
        f"- Source findings visible: {source_visibility.get('sourceFindingCount', len(source_findings))}"
    )
    lines.append(
        f"- Reports with source findings: {source_visibility.get('reportsWithSourceFindings', 0)}"
    )
    if source_findings:
        lines.extend(
            [
                "",
                "| Severity | Source Rule | Source Status | Tool | Report | Recommendation | Proof |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for finding in source_findings[:20]:
            lines.append(
                f"| {finding.get('severity') or 'review'} | `{table_cell(finding.get('ruleId') or 'source-finding', 48)}` | {finding.get('sourceStatus') or '-'} | `{table_cell(finding.get('tool') or 'unknown', 40)}` | `{Path(str(finding.get('report') or '')).name}` | {table_cell(finding.get('recommendation') or '-')} | {table_cell(finding.get('proofGuidance') or '-', 120)} |"
            )
        if source_visibility.get("truncated"):
            lines.append("")
            lines.append("Additional source findings are preserved in JSON but omitted from this compact Markdown table.")
    else:
        lines.append("No source report findings were present in the scored reports.")

    priority = report.get("priorityAction") or {}
    lines.extend(["", "## Priority Action", ""])
    if priority:
        lines.append(f"- Kind: `{priority.get('kind') or 'unknown'}`")
        lines.append(f"- Summary: {priority.get('summary') or 'No priority action available.'}")
        if priority.get("priorityReason"):
            lines.append(f"- Reason: {priority['priorityReason']}")
        if priority.get("sourceStatus"):
            lines.append(f"- Source status: `{priority['sourceStatus']}`")
    else:
        lines.append("No priority action was generated.")

    lines.extend(["", "## Actionability Questions", ""])
    ranked_questions = report.get("prioritizedActionabilityQuestions") or report["actionabilityQuestions"]
    if ranked_questions:
        lines.extend(["| Priority | Tool | Source Status | Report | Question | Reason |", "| ---: | --- | --- | --- | --- | --- |"])
        for index, item in enumerate(ranked_questions[:12], start=1):
            lines.append(
                f"| {item.get('priority') or index} | `{table_cell(item.get('tool') or 'unknown', 40)}` | {item.get('sourceStatus') or '-'} | `{Path(item['report']).name}` | {table_cell(item['question'], 140)} | {table_cell(item.get('priorityReason') or '-', 90)} |"
            )
    else:
        lines.append("No report-quality questions were found in the input reports.")

    lines.extend(["", "## Fixture Coverage", ""])
    fixture_coverage = report.get("fixtureCoverage") or []
    if fixture_coverage:
        lines.extend(["| Priority | Tool | Existing Fixture | Source Question |", "| ---: | --- | --- | --- |"])
        for item in fixture_coverage:
            lines.append(
                f"| {item.get('priority') or '-'} | `{table_cell(item.get('tool') or 'unknown', 40)}` | `{table_cell(item.get('publicFixturePath') or '-', 72)}` | {table_cell(item.get('question') or '-', 160)} |"
            )
        lines.append("")
        lines.append("Covered questions keep their actionability evidence, but they do not create duplicate fixture candidates.")
    else:
        lines.append("No existing promoted fixtures matched the current actionability questions.")

    external_index = report.get("stablePublicationExternalEvidenceFixtureIndex") or {}
    if external_index:
        lines.extend(["", "## Stable-Publication External Evidence Fixture Index", ""])
        lines.append(f"- Status: `{external_index.get('status') or 'unknown'}`")
        lines.append(
            f"- Covered: {external_index.get('coveredCount', 0)}/{external_index.get('expectedCount', 0)}"
        )
        decision_summary = external_index.get("decisionSummary") if isinstance(external_index.get("decisionSummary"), dict) else {}
        if decision_summary:
            covered_classes = ", ".join(str(value) for value in decision_summary.get("coveredEvidenceClasses") or [])
            remaining_questions = ", ".join(
                str(value) for value in decision_summary.get("remainingExternalEvidenceQuestions") or []
            )
            lines.extend(["", "Decision summary:"])
            lines.append(f"- Verdict: {decision_summary.get('verdict') or '-'}")
            lines.append(f"- Covered evidence classes: {covered_classes or '-'}")
            lines.append(f"- Remaining questions: {remaining_questions or '-'}")
            lines.append(f"- Next promotion target: `{decision_summary.get('nextPromotionTarget') or 'unknown'}`")
            lines.append(f"- Non-claim: {decision_summary.get('nonClaimSummary') or '-'}")
        lines.extend(["", "| Evidence | Status | Fixture | Rejection Proved | Required Proof |", "| --- | --- | --- | --- | --- |"])
        for item in external_index.get("rows") or []:
            required = ", ".join(str(value) for value in item.get("requiredProof") or [])
            lines.append(
                f"| `{item.get('id') or 'unknown'}` | `{item.get('status') or 'unknown'}` | `{table_cell(item.get('publicFixturePath') or '-', 72)}` | {table_cell(item.get('rejectionProved') or '-')} | {table_cell(required, 120)} |"
            )
        source_summary = external_index.get("sourceClassPolishSummary") or []
        if source_summary:
            lines.extend(
                [
                    "",
                    "Source-class summary:",
                    "",
                    "| Evidence | Accepted classes | Relationship field | Accepted relationships | Rejected substitutes | Pass boundary |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for item in source_summary:
                accepted = ", ".join(str(value) for value in item.get("acceptedEvidenceClasses") or [])
                relationships = ", ".join(str(value) for value in item.get("acceptedRelationships") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedSubstitutes") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | {table_cell(accepted, 90)} | `{item.get('requiredRelationshipField') or '-'}` | {table_cell(relationships or '-', 70)} | {table_cell(rejected, 130)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        relationship_summary = external_index.get("relationshipGateSummary") or []
        if relationship_summary:
            lines.extend(
                [
                    "",
                    "Relationship-gate summary:",
                    "",
                    "| Evidence | Relationship field | Accepted relationships | Rejected relationships | Blocked substitute | Pass boundary |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for item in relationship_summary:
                accepted = ", ".join(str(value) for value in item.get("acceptedRelationships") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedRelationships") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | `{item.get('requiredRelationshipField') or '-'}` | {table_cell(accepted or '-', 70)} | {table_cell(rejected or '-', 90)} | {table_cell(item.get('blockedSubstitute') or '-', 80)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        artifact_summary = external_index.get("artifactRedactionSummary") or []
        if artifact_summary:
            lines.extend(
                [
                    "",
                    "Artifact-redaction summary:",
                    "",
                    "| Evidence | Required artifact fields | Rejected artifact proof | Blocked substitute | Pass boundary |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for item in artifact_summary:
                fields = ", ".join(str(value) for value in item.get("requiredArtifactFields") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedArtifactProof") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | {table_cell(fields or '-', 90)} | {table_cell(rejected or '-', 120)} | {table_cell(item.get('blockedSubstitute') or '-', 80)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        digest_summary = external_index.get("artifactDigestProvenanceSummary") or []
        if digest_summary:
            lines.extend(
                [
                    "",
                    "Artifact digest/provenance summary:",
                    "",
                    "| Evidence | Required artifact proof | Rejected artifact proof | Blocked substitute | Pass boundary |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for item in digest_summary:
                required = ", ".join(str(value) for value in item.get("requiredArtifactProof") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedArtifactProof") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | {table_cell(required or '-', 90)} | {table_cell(rejected or '-', 120)} | {table_cell(item.get('blockedSubstitute') or '-', 80)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        review_scope_summary = external_index.get("reviewScopeMappingSummary") or []
        if review_scope_summary:
            lines.extend(
                [
                    "",
                    "Review-scope mapping summary:",
                    "",
                    "| Evidence | Required scope | Required mapping fields | Rejected review proof | Blocked substitute | Pass boundary |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for item in review_scope_summary:
                required_scope = ", ".join(str(value) for value in item.get("requiredScope") or [])
                fields = ", ".join(str(value) for value in item.get("requiredMappingFields") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedReviewProof") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | {table_cell(required_scope or '-', 100)} | {table_cell(fields or '-', 90)} | {table_cell(rejected or '-', 120)} | {table_cell(item.get('blockedSubstitute') or '-', 90)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        expiry_summary = external_index.get("expiryWindowSummary") or []
        if expiry_summary:
            lines.extend(
                [
                    "",
                    "Expiry-window summary:",
                    "",
                    "| Evidence | Required expiry fields | Rejected freshness proof | Blocked substitute | Pass boundary |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for item in expiry_summary:
                fields = ", ".join(str(value) for value in item.get("requiredExpiryFields") or [])
                rejected = ", ".join(str(value) for value in item.get("rejectedFreshnessProof") or [])
                lines.append(
                    f"| `{item.get('evidence') or 'unknown'}` | {table_cell(fields or '-', 100)} | {table_cell(rejected or '-', 120)} | {table_cell(item.get('blockedSubstitute') or '-', 90)} | {table_cell(item.get('passBoundary') or '-', 130)} |"
                )
        next_fixture = external_index.get("nextFixtureToPromote") if isinstance(external_index.get("nextFixtureToPromote"), dict) else {}
        if next_fixture:
            lines.extend(["", "Next fixture to promote:"])
            lines.append(f"- `{next_fixture.get('id') or next_fixture.get('candidateId') or 'unknown'}`")
            if next_fixture.get("suggestedFixturePath"):
                lines.append(f"- Suggested path: `{next_fixture['suggestedFixturePath']}`")
            if next_fixture.get("summary"):
                lines.append(f"- Summary: {next_fixture['summary']}")
            if next_fixture.get("qaCommand"):
                lines.append(f"- QA command: `{next_fixture['qaCommand']}`")
            if next_fixture.get("promotionBoundary"):
                lines.append(f"- Boundary: {next_fixture['promotionBoundary']}")
        backlog = external_index.get("nextGapCandidateBacklog") or []
        if backlog:
            lines.extend(
                [
                    "",
                    "Next-gap candidate backlog:",
                    "",
                    "| Candidate | Suggested fixture | Summary |",
                    "| --- | --- | --- |",
                ]
            )
            for item in backlog:
                lines.append(
                    f"| `{item.get('id') or 'unknown'}` | `{table_cell(item.get('suggestedFixturePath') or '-', 80)}` | {table_cell(item.get('summary') or '-', 140)} |"
                )
        gaps = external_index.get("remainingExternalEvidenceGaps") or []
        if gaps:
            lines.extend(["", "Remaining external-evidence gaps:"])
            for gap in gaps:
                if isinstance(gap, dict):
                    lines.append(f"- `{gap.get('id') or 'unknown'}`: {gap.get('summary') or '-'}")

    lines.extend(["", "## Fixture Candidates", ""])
    fixture_candidates = report.get("fixtureCandidates") or []
    if fixture_candidates:
        lines.extend(["| Priority | Type | Public Fixture Path | Source Question |", "| ---: | --- | --- | --- |"])
        for item in fixture_candidates:
            lines.append(
                f"| {item.get('priority') or '-'} | `{table_cell(item.get('fixtureType') or 'unknown', 48)}` | `{table_cell(item.get('publicFixturePath') or '-', 72)}` | {table_cell(item.get('sourceQuestion') or '-', 160)} |"
            )
        lines.extend(["", "Fixture candidate rules:", ""])
        lines.append("- Build synthetic public fixtures from the report shape, not from private app code or screenshots.")
        lines.append("- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit in every fixture report.")
        lines.append("- Validate with `./bin/shipguard ios report-quality --reports <fixture-dir> --out <quality-dir> --shareable` and `./tests/ios_report_quality_test.sh`.")
        lines.append("- Materialize starter fixtures with `--write-fixture-candidates <fixture-output-dir>` when the next loop needs concrete files.")
    else:
        lines.append("No fixture candidates were generated from the current actionability questions.")

    materialized = report.get("fixtureMaterialization") or {}
    if materialized:
        lines.extend(["", "## Fixture Materialization", ""])
        lines.append(f"- Status: `{materialized.get('status') or 'unknown'}`")
        lines.append(f"- Output: `{materialized.get('output') or '<fixture-output-dir>'}`")
        entries = materialized.get("candidates") or []
        if entries:
            lines.extend(["", "| Candidate | Directory | Files |", "| --- | --- | --- |"])
            for item in entries:
                files = ", ".join(f"`{name}`" for name in item.get("files", []))
                lines.append(
                    f"| `{table_cell(item.get('candidateId') or 'unknown', 48)}` | `{table_cell(item.get('directory') or '-', 72)}` | {files} |"
                )

    promotion_manifests = report.get("fixturePromotionManifests") or []
    if promotion_manifests:
        lines.extend(["", "## Fixture Promotion Manifests", ""])
        lines.extend(["| Status | Manifest | Candidates | Issues |", "| --- | --- | ---: | ---: |"])
        for item in promotion_manifests:
            lines.append(
                f"| {item.get('status') or 'unknown'} | `{Path(item.get('path') or '').name}` | {item.get('candidateCount') or 0} | {item.get('issueCount') or 0} |"
            )

    plan = report["redactionPlan"]
    lines.extend(["", "## Redaction Plan", ""])
    if plan["needed"]:
        lines.append(f"- Needed before external sharing: `yes`")
        lines.append(f"- Blocked until redacted: `{'yes' if plan['blockedUntilRedacted'] else 'no'}`")
        lines.append(f"- Rules: {', '.join(f'`{rule}`' for rule in plan['rules'])}")
        lines.append("")
        for command in plan["commands"]:
            lines.append(f"- `{command['command']}`")
    else:
        lines.append("No redaction-required shareability issues were detected.")

    lines.extend(["", "## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-report-quality.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-report-quality.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-report-quality.json'}")
    print(f"wrote: {out_dir / 'ios-report-quality.md'}")
    print(f"status: {report['status']}")


def safe_candidate_metadata(candidate: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(candidate)
    source_reports = metadata.pop("sourceReports", [])
    candidate_id = materialized_candidate_id(candidate)
    if "sourceQuestion" in metadata:
        metadata["sourceQuestion"] = materialized_source_question(candidate)
    for text_key in ("fixtureType", "sourceTool"):
        if text_key in metadata:
            metadata[text_key] = sanitize_materialized_text(metadata[text_key])
    metadata["candidateId"] = candidate_id
    metadata["publicFixturePath"] = f"fixtures/ios-report-quality/{candidate_id}"
    metadata["sourceReportCount"] = len(source_reports) if isinstance(source_reports, list) else 0
    metadata["sourceReportsRedacted"] = True
    metadata["promotion"] = promotion_metadata(candidate_id)
    metadata["privateDataPolicy"] = (
        "This materialized starter is synthetic. Use source reports only to choose report shape; do not copy "
        "private app code, local paths, screenshots, app-specific identifiers, or proprietary text."
    )
    return metadata


def promotion_target_path(candidate_id: str) -> str:
    return f"fixtures/ios-report-quality/{candidate_id}"


def promotion_metadata(candidate_id: str) -> dict[str, Any]:
    target_path = promotion_target_path(candidate_id)
    files = [
        "README.md",
        "fixture-candidate.json",
        "fixture-report.json",
        "fixture-report.md",
    ]
    return {
        "candidateId": candidate_id,
        "sourceDirectory": f"<materialized-fixture-output>/{candidate_id}",
        "suggestedFixturePath": target_path,
        "files": files,
        "copyCommands": [
            f"mkdir -p {target_path}",
            *[
                f"cp <materialized-candidate-dir>/{name} {target_path}/{name}"
                for name in files
            ],
        ],
        "validationCommands": [
            f"./bin/shipguard ios report-quality --reports {target_path} --out <quality-dir> --shareable",
            "./tests/ios_report_quality_test.sh",
            "./bin/shipguard validate",
        ],
        "reviewChecklist": [
            "Confirm the fixture is synthetic and public-safe.",
            "Confirm no private app code, screenshots, local paths, tokens, app identifiers, or proprietary text were copied.",
            "Confirm scopeBoundary.shipguardOnly and targetAppsReadOnly remain explicit.",
            "Confirm scoring the promoted fixture does not emit recursive fixtureCandidates.",
            "Register the fixture in validation only after the report-quality check passes.",
        ],
        "promotionPolicy": "Promotion is explicit maintainer work. ShipGuard writes starter files only to the requested output directory and does not auto-copy them into the repository.",
    }


def sanitize_materialized_text(value: object) -> str:
    text = ios_shareable.redact_text(value, private_terms=list(ios_shareable.DEFAULT_PRIVATE_TERMS))
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def materialized_source_question(candidate: dict[str, Any]) -> str:
    question = sanitize_materialized_text(candidate.get("sourceQuestion"))
    if question:
        return question
    fixture_type = sanitize_materialized_text(candidate.get("fixtureType")) or "report-quality-actionability-fixture"
    return f"Which ShipGuard report-quality behavior should this {fixture_type} cover?"


def materialized_candidate_id(candidate: dict[str, Any]) -> str:
    raw_candidate_id = sanitize_materialized_text(candidate.get("candidateId"))
    if raw_candidate_id:
        stable_candidate_id = slugify(raw_candidate_id, limit=96)
        if stable_candidate_id != "report-quality-fixture":
            return stable_candidate_id
    try:
        priority = int(candidate.get("priority") or 0)
    except (TypeError, ValueError):
        priority = 0
    prefix = f"{priority:02d}" if priority > 0 else "00"
    fixture_type = sanitize_materialized_text(candidate.get("fixtureType")) or "report-quality-actionability-fixture"
    return slugify(f"{prefix}-{fixture_type}", limit=96)


def synthetic_performance_findings() -> list[dict[str, Any]]:
    local_proof = (
        "Record the synthetic screen at rest and during one interaction, then compare samples after gating the animation."
    )
    manual_proof = (
        "Use physical-device Instruments before making FPS, ProMotion, thermal, battery, or hardware-display claims."
    )
    findings: list[dict[str, Any]] = []
    for line in (12, 28, 44, 60):
        findings.append(
            {
                "severity": "review",
                "category": "SwiftUI Rendering",
                "ruleId": "swiftui-repeat-forever-animation",
                "title": "Review continuous repeatForever animation",
                "file": "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift",
                "line": line,
                "evidence": ".repeatForever(autoreverses: true)",
                "severityReason": (
                    "Review because repeatForever can keep the render loop active until it is gated by visibility, "
                    "Reduce Motion, or user value."
                ),
                "impact": (
                    "Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, "
                    "or tab backgrounds."
                ),
                "recommendation": (
                    "Gate decorative repeatForever motion behind Reduce Motion, active screen visibility, and measurable "
                    "interaction value before changing broader animation architecture."
                ),
                "localProof": local_proof,
                "manualProof": manual_proof,
                "proof": f"{local_proof} {manual_proof}",
                "proofGuidance": f"Codex local proof: {local_proof} Manual/device proof: {manual_proof}",
            }
        )
    return findings


def synthetic_performance_rule_summary() -> list[dict[str, Any]]:
    return [
        {
            "ruleId": "swiftui-repeat-forever-animation",
            "count": 4,
            "highestSeverity": "review",
            "severityMix": {"review": 4},
            "firstLocations": [
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:12",
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:28",
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:44",
            ],
        }
    ]


def synthetic_performance_grouped_action_plan() -> list[dict[str, Any]]:
    local_proof = (
        "Capture the same synthetic screen at rest and during one interaction before and after the animation gate."
    )
    manual_proof = (
        "Attach physical-device Instruments proof before promoting the source suspicion into FPS, thermal, battery, "
        "or hardware-display guidance."
    )
    return [
        {
            "ruleId": "swiftui-repeat-forever-animation",
            "count": 4,
            "severity": "review",
            "firstLocations": [
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:12",
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:28",
                "Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:44",
            ],
            "recommendation": (
                "Start with one decorative repeatForever animation and prove that gating it changes the measured route "
                "before broad animation cleanup."
            ),
            "firstExperiment": (
                "Disable or gate one decorative repeatForever animation behind Reduce Motion and active-screen visibility, "
                "then compare an at-rest screen recording plus a same-route sample."
            ),
            "validationRoute": (
                "Run the same local sample or trace before and after the single gate; use device Instruments before "
                "claiming FPS, ProMotion, battery, or thermal improvement."
            ),
            "stopCondition": (
                "Stop after the first gated animation unless the same-route proof shows a measurable improvement and "
                "the UI still communicates the intended state."
            ),
            "recommendedFirstMove": "Gate one animation, do not rewrite the full motion system.",
            "localProof": local_proof,
            "manualProof": manual_proof,
            "proofGuidance": f"Codex local proof: {local_proof} Manual/device proof: {manual_proof}",
        }
    ]


def synthetic_performance_evidence_promotion() -> dict[str, Any]:
    return {
        "sourceEvidence": "source heuristic",
        "promotionStatus": "missing-runtime-proof",
        "firstCandidateRule": "swiftui-repeat-forever-animation",
        "proofRequired": [
            "Same-route Simulator trace, sample, or log evidence for local-only claims.",
            "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.",
        ],
        "nextAction": {
            "owner": "developer",
            "kind": "manual-proof",
            "command": "shipguard ios launchdeck --path <repo> --workflow performance --out <launchdeck-performance-out>",
            "manualProof": (
                "Run the same local sample or trace before and after the single animation gate; attach device "
                "Instruments proof before claiming FPS, ProMotion, battery, thermal, or hardware-display improvement."
            ),
            "expectedArtifact": (
                "Same-route before/after trace, sample, or screen recording for the first "
                "swiftui-repeat-forever-animation experiment."
            ),
            "successCondition": (
                "The same-route proof shows less constant motion work, Reduce Motion or visibility behavior remains "
                "correct, and no broader performance claim is made without device proof."
            ),
            "failureMeaning": (
                "The source suspicion remains unpromoted; keep it as review guidance and do not broaden scanner "
                "heuristics or target-app remediation."
            ),
        },
    }


def synthetic_lean_gain_report_fields() -> dict[str, Any]:
    return {
        "surface": "ShipGuard Lean Gain",
        "target": {"path": ".", "shareable": True},
        "sourceInfluence": {
            "name": "Lean code benchmark influence",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard reports benchmark direction honestly and implements its own native reports. It does not vendor external code.",
        },
        "benchmarkScoreboard": {
            "primary": {
                "label": "Synthetic Lean Gain public benchmark",
                "baseline": "same agent without the lean-code ruleset",
                "scope": "public benchmark, not this repository",
                "method": "paired public fixture tasks with and without the lean-code ruleset",
                "remainingPercentOfBaseline": {
                    "linesOfCode": 46,
                    "tokens": 78,
                    "cost": 80,
                    "time": 73,
                    "safety": 100,
                },
                "reportedChange": {
                    "linesOfCode": "-54%",
                    "tokens": "-22%",
                    "cost": "-20%",
                    "time": "-27%",
                    "safety": "100%",
                },
            },
            "legacySingleShot": {
                "status": "archival-context-only",
                "boundary": "Older single-shot ranges are archival context only and are not the launch claim.",
            },
        },
        "currentRepoBoundary": {
            "perRepoSavingsClaim": "not-computed",
            "reason": "There is no untreated baseline for this repository; ShipGuard cannot subtract code, cost, or time that was never produced.",
            "realRepoSignals": [
                "lean audit findings",
                "lean review findings",
                "lean debt marker counts",
            ],
            "evidenceRoutes": [
                {
                    "id": "lean-audit",
                    "command": "shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable",
                    "expectedArtifact": "lean-audit.json and lean-audit.md",
                    "answers": "Which repo surfaces may be deleted, simplified, kept, or proof-blocked?",
                    "proofBoundary": "Source-scan evidence only; it does not prove line, token, cost, or time savings.",
                    "nonClaim": "Do not treat audit findings as benchmark savings.",
                },
                {
                    "id": "lean-review",
                    "command": "shipguard lean review --path <repo> --diff <diff-file> --out <lean-review-out> --mode full --shipguard-eval --shareable",
                    "expectedArtifact": "lean-review.json and lean-review.md",
                    "answers": "Which current-diff changes can be deleted, simplified, kept, or proof-blocked before merge?",
                    "proofBoundary": "Diff-scoped evidence only; it does not prove whole-repo or benchmark savings.",
                    "nonClaim": "Do not treat a smaller diff as measured token, cost, or time savings without a matched baseline.",
                },
                {
                    "id": "lean-debt",
                    "command": "shipguard lean debt --path <repo> --out <lean-debt-out> --shipguard-eval --shareable",
                    "expectedArtifact": "lean-debt.json and lean-debt.md",
                    "answers": "Which intentional shortcuts have ceilings, upgrade triggers, and missing-trigger debt?",
                    "proofBoundary": "Shortcut-ledger evidence only; it does not prove benchmark or per-repo savings.",
                    "nonClaim": "Do not present shortcut counts as code-size savings.",
                },
            ],
        },
        "leanDebtLedger": {
            "description": "Synthetic shortcut ledger for Lean Gain routing coverage.",
            "summary": {
                "markers": 0,
                "missingUpgradeTrigger": 0,
                "omittedByLimit": 0,
            },
            "markers": [],
        },
        "nextActions": [
            "Use shipguard lean audit for cuttable repo surfaces.",
            "Use shipguard lean review on the active diff before merge.",
            "Use shipguard lean debt to count intentional shortcuts with ceilings and upgrade triggers.",
            "Do not claim per-repo line, token, cost, or time savings unless you have a real matched baseline.",
        ],
    }


def synthetic_lean_debt_report_fields() -> dict[str, Any]:
    markers = [
        {
            "file": "Sources/SyntheticLeanDebt/QueryBridge.swift",
            "line": 12,
            "marker": "shipguard-lean",
            "summary": "use the native query parser while this bridge handles one query shape. ceiling: one query shape. upgrade: replace when repeated-key support is required.",
            "ceiling": "one query shape",
            "hasCeiling": True,
            "upgrade": "replace when repeated-key support is required",
            "hasUpgradeTrigger": True,
            "status": "tracked",
        },
        {
            "file": "Sources/SyntheticLeanDebt/LegacyPanel.swift",
            "line": 27,
            "marker": "ponytail",
            "summary": "keep the temporary compatibility panel during migration. ceiling: one release migration window.",
            "ceiling": "one release migration window",
            "hasCeiling": True,
            "upgrade": "",
            "hasUpgradeTrigger": False,
            "status": "needs-trigger",
        },
    ]
    visibility_rows = [
        {
            "file": item["file"],
            "line": item["line"],
            "location": f"{item['file']}:{item['line']}",
            "marker": item["marker"],
            "status": item["status"],
            "summary": item["summary"],
            "ceiling": item["ceiling"],
            "upgradeTrigger": item["upgrade"],
            "hasCeiling": item["hasCeiling"],
            "hasUpgradeTrigger": item["hasUpgradeTrigger"],
            "exposesUpgradeStatus": True,
        }
        for item in markers
    ]
    rot_rows = [
        {
            "rank": 1,
            "file": "Sources/SyntheticLeanDebt/LegacyPanel.swift",
            "line": 27,
            "location": "Sources/SyntheticLeanDebt/LegacyPanel.swift:27",
            "marker": "ponytail",
            "status": "needs-trigger",
            "riskLevel": "review",
            "rotReason": "Missing upgrade trigger means this shortcut can survive beyond its intended window.",
            "nextAction": "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.",
            "proofGuidance": "Name the release, dependency, migration state, or repeated call-site signal that should trigger cleanup.",
            "ceiling": "one release migration window",
            "upgradeTrigger": "",
            "hasCeiling": True,
            "hasUpgradeTrigger": False,
            "triggerWatchContract": {
                "triggerState": "needs-trigger-definition",
                "triggerCondition": "missing upgrade trigger; define a release, dependency, migration, or repeated call-site signal",
                "exactNextAction": "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.",
                "checkRoute": "Add the upgrade trigger to the marker, rerun shipguard lean debt, and confirm rowsNeedingUpgradeTrigger decreases.",
                "proofArtifact": "lean-debt.json markerVisibilityReview.visibilityRows row with hasUpgradeTrigger=true and a non-empty upgradeTrigger.",
                "stopCondition": "Stop if the trigger cannot be checked later from a release, dependency, migration, or call-site signal.",
            },
        },
        {
            "rank": 2,
            "file": "Sources/SyntheticLeanDebt/QueryBridge.swift",
            "line": 12,
            "location": "Sources/SyntheticLeanDebt/QueryBridge.swift:12",
            "marker": "shipguard-lean",
            "status": "tracked",
            "riskLevel": "tracked",
            "rotReason": "Tracked shortcut should be reviewed when its upgrade trigger becomes true.",
            "nextAction": "Watch the upgrade trigger: replace when repeated-key support is required",
            "proofGuidance": "When the trigger is true, run call-site search plus the smallest focused validation before deleting or replacing it.",
            "ceiling": "one query shape",
            "upgradeTrigger": "replace when repeated-key support is required",
            "hasCeiling": True,
            "hasUpgradeTrigger": True,
            "triggerWatchContract": {
                "triggerState": "watch-trigger",
                "triggerCondition": "replace when repeated-key support is required",
                "exactNextAction": "Check whether this trigger is true: replace when repeated-key support is required",
                "checkRoute": "Run call-site search for the shortcut location, then run the smallest focused validation covering the replacement or deletion.",
                "proofArtifact": "call-site search notes plus focused validation output attached beside lean-debt.json.",
                "stopCondition": "Stop if search or validation shows the shortcut is still active product behavior.",
            },
        },
    ]
    return {
        "schemaVersion": 2,
        "surface": "ShipGuard Lean Debt",
        "target": {"path": ".", "shareable": True},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native shortcut ledger for its own lean-code markers. It does not vendor Ponytail code.",
        },
        "leanDebtLedger": {
            "description": "Synthetic shortcut markers for standalone Lean Debt marker-visibility coverage.",
            "summary": {
                "markers": 2,
                "missingCeiling": 0,
                "missingUpgradeTrigger": 1,
                "omittedByLimit": 0,
            },
            "markers": markers,
        },
        "markerVisibilityReview": {
            "policy": (
                "Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, "
                "upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written."
            ),
            "summary": {
                "totalMarkers": 2,
                "visibleMarkerRows": 2,
                "omittedByLimit": 0,
                "omittedStateUnknown": False,
                "rowsWithCeiling": 2,
                "rowsMissingCeiling": 0,
                "rowsWithUpgradeTrigger": 1,
                "rowsNeedingUpgradeTrigger": 1,
                "rowsWithUpgradeStatus": 2,
            },
            "allMarkersVisible": True,
            "allVisibleRowsHaveCeiling": True,
            "allVisibleRowsExposeUpgradeStatus": True,
            "visibilityRows": visibility_rows,
        },
        "rotRiskReview": {
            "policy": (
                "Start with the highest-risk shortcut marker before opening source again: missing ceiling first, "
                "missing upgrade trigger second, tracked trigger watch third."
            ),
            "summary": {
                "totalMarkers": 2,
                "rotRiskRows": 2,
                "highRiskRows": 0,
                "reviewRiskRows": 1,
                "trackedRows": 1,
                "missingCeilingRows": 0,
                "missingUpgradeTriggerRows": 1,
                "triggerWatchContractRows": 2,
                "missingTriggerWatchContractRows": 0,
                "trackedTriggerWatchRows": 1,
                "missingTriggerDefinitionRows": 1,
                "omittedByLimit": 0,
                "omittedRiskUnknown": False,
                "topRiskLocation": "Sources/SyntheticLeanDebt/LegacyPanel.swift:27",
                "topRiskReason": "Missing upgrade trigger means this shortcut can survive beyond its intended window.",
                "topTriggerWatchAction": "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.",
            },
            "coverageBoundary": (
                "Rot-risk ranking is based on visible shortcut rows. When omittedByLimit is greater than zero, "
                "omitted markers may contain higher risk and must be surfaced by rerunning with a narrower scope or extending the ledger limit."
            ),
            "allVisibleRowsHaveRotRisk": True,
            "topRiskActionable": True,
            "prioritizedRows": rot_rows,
        },
        "currentRepoBoundary": {
            "perRepoSavingsClaim": "not-computed",
            "evidenceType": "shortcut-ledger-only",
            "reason": "Lean Debt counts intentional shortcut markers and missing triggers; it has no untreated baseline for current-repo line, token, cost, or time savings.",
            "nonClaims": [
                "Do not claim current-repo line, token, cost, or time savings from shortcut marker counts.",
                "Do not treat shortcut marker counts as benchmark savings.",
            ],
            "benchmarkRoute": {
                "command": "shipguard lean gain --path <repo> --out <lean-gain-out> --shipguard-eval --shareable",
                "expectedArtifact": "lean-gain.json and lean-gain.md",
                "answers": "What benchmark-backed lean-code direction can be shown without claiming current-repo savings?",
                "proofBoundary": "Benchmark direction is separate from this shortcut-ledger evidence and still does not measure this repo without a matched baseline.",
            },
        },
        "nextActions": [
            "Add an upgrade trigger to every needs-trigger marker.",
            "Remove markers whose ceiling no longer applies.",
            "Use shipguard lean review on active diffs so new shortcuts are tracked before merge.",
        ],
    }


def synthetic_lean_review_report_fields() -> dict[str, Any]:
    delete_finding = {
        "severity": "opportunity",
        "category": "yagni-diff-review",
        "ruleId": "thin-wrapper-diff-review",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/FormatterShim.swift",
            "line": 14,
            "snippet": "func formatTitle(_ value: String) -> String { value.trimmingCharacters(in: .whitespacesAndNewlines) }",
        },
        "recommendation": "Inline or delete this wrapper unless it adds policy, naming, compatibility, logging, typing, or test value.",
        "proofGuidance": "Search call sites and keep one small check if behavior is non-trivial.",
    }
    simplify_finding = {
        "severity": "opportunity",
        "category": "stdlib-diff-review",
        "ruleId": "stdlib-url-params-diff",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/QueryBuilder.swift",
            "line": 22,
            "snippet": "query.split(separator: \"&\").map { $0.split(separator: \"=\") }",
        },
        "recommendation": "Prefer URLComponents or URLQueryItem when runtime support allows it.",
        "proofGuidance": "Add one check for repeated keys, empty values, encoding, and malformed input before replacing behavior.",
    }
    keep_finding = {
        "severity": "info",
        "category": "safety-boundary",
        "ruleId": "do-not-cut-safety-diff-without-proof",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/PermissionGate.swift",
            "line": 31,
            "snippet": "guard authorizationStatus == .authorized else { return .blocked }",
        },
        "recommendation": "Less code is not the goal in this file until behavior proof exists.",
        "proofGuidance": "Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior.",
    }
    missing_check_finding = {
        "severity": "review",
        "category": "proof-diff-review",
        "ruleId": "one-runnable-check-missing-diff",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
            "line": 18,
            "snippet": "if route.kind == .generated { return GeneratedRoute(route.payload) }",
        },
        "recommendation": "Leave one smallest runnable check for the new routing branch instead of treating tests as optional ceremony.",
        "proofGuidance": "Add one focused route-selection check or point to the changed test that covers this branch before merge.",
    }
    same_diff_proof_finding = {
        "severity": "info",
        "category": "proof-signal-diff-review",
        "ruleId": "one-runnable-check-signal-present-diff",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
            "line": 27,
            "snippet": "if option.isPrimary { return .preferred(option.id) }",
        },
        "recommendation": "Do not add duplicate test ceremony before checking whether the same-diff proof signal already covers this logic.",
        "proofGuidance": "Review Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift, then run the focused test before merge.",
    }
    hardware_finding = {
        "severity": "review",
        "category": "hardware-diff-review",
        "ruleId": "hardware-calibration-missing-diff",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/SensorSampler.swift",
            "line": 33,
            "snippet": "let rawSample = adc.read(channel: channel)",
        },
        "recommendation": "Keep a minimal calibration or tuning boundary when code touches real hardware or physical-device behavior.",
        "proofGuidance": "Attach real-device, sensor, timing, or calibration evidence before simplifying the physical-world edge case away.",
    }
    host_adapter_finding = {
        "severity": "info",
        "category": "host-adapter-boundary",
        "ruleId": "host-adapter-boundary-diff",
        "evidence": {
            "file": "Sources/SyntheticLeanReview/PluginHostAdapter.swift",
            "line": 12,
            "snippet": "func handle(_ request: PluginRequest) -> PluginResponse { adapter.handle(request) }",
        },
        "recommendation": "Keep this host, plugin, MCP, preview, simulator, or platform adapter until call-site or protocol proof shows it is redundant.",
        "proofGuidance": "Attach call-site, protocol, plugin, MCP, preview, or runtime proof before simplifying the adapter boundary.",
    }
    action_groups = [
        {
            "rank": 1,
            "decision": "delete",
            "ruleId": "thin-wrapper-diff-review",
            "evidenceCount": 1,
            "firstLocation": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
            "firstExperiment": "Search the changed call sites and delete the wrapper only if it is private and behavior-neutral.",
            "validationRoute": "Run the smallest formatter behavior check plus git diff --check.",
            "stopCondition": "Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy.",
        },
        {
            "rank": 2,
            "decision": "simplify",
            "ruleId": "stdlib-url-params-diff",
            "evidenceCount": 1,
            "firstLocation": "Sources/SyntheticLeanReview/QueryBuilder.swift:22",
            "firstExperiment": "Try URLComponents or URLQueryItem at the changed call site before adding parser code.",
            "validationRoute": "Run one focused query-string behavior check plus git diff --check.",
            "stopCondition": "Stop if repeated keys, empty values, encoding, or malformed input behavior changes.",
        },
        {
            "rank": 3,
            "decision": "proof-blocked",
            "ruleId": "one-runnable-check-missing-diff",
            "evidenceCount": 1,
            "firstLocation": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
            "firstExperiment": "Add or identify one smallest runnable route-selection check before merging the new branch.",
            "validationRoute": "Run the focused route-selection test plus git diff --check.",
            "stopCondition": "Stop if the diff has no runnable proof signal for the changed non-trivial logic.",
        },
        {
            "rank": 4,
            "decision": "proof-blocked",
            "ruleId": "hardware-calibration-missing-diff",
            "evidenceCount": 1,
            "firstLocation": "Sources/SyntheticLeanReview/SensorSampler.swift:33",
            "firstExperiment": "Attach calibration, timing, or real-device evidence before removing the sensor tuning boundary.",
            "validationRoute": "Run or attach the smallest hardware, simulator, or timing proof that covers the changed sampling behavior.",
            "stopCondition": "Stop if the only evidence is source-level less-code pressure without physical-world proof.",
        },
    ]
    decisions = [
        {
            "file": "Sources/SyntheticLeanReview/FormatterShim.swift",
            "source": "unified-diff",
            "decision": "delete",
            "addedLines": 6,
            "removedLines": 0,
            "ruleIds": ["thin-wrapper-diff-review"],
            "firstLocation": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
            "firstExperiment": action_groups[0]["firstExperiment"],
            "validationRoute": action_groups[0]["validationRoute"],
            "stopCondition": action_groups[0]["stopCondition"],
        },
        {
            "file": "Sources/SyntheticLeanReview/QueryBuilder.swift",
            "source": "unified-diff",
            "decision": "simplify",
            "addedLines": 8,
            "removedLines": 1,
            "ruleIds": ["stdlib-url-params-diff"],
            "firstLocation": "Sources/SyntheticLeanReview/QueryBuilder.swift:22",
            "firstExperiment": action_groups[1]["firstExperiment"],
            "validationRoute": action_groups[1]["validationRoute"],
            "stopCondition": action_groups[1]["stopCondition"],
        },
        {
            "file": "Sources/SyntheticLeanReview/PermissionGate.swift",
            "source": "unified-diff",
            "decision": "keep",
            "addedLines": 5,
            "removedLines": 0,
            "ruleIds": ["do-not-cut-safety-diff-without-proof"],
            "firstLocation": "Sources/SyntheticLeanReview/PermissionGate.swift:31",
            "firstExperiment": "Treat this as a keep-with-proof boundary before any deletion or simplification.",
            "validationRoute": "Run focused permission-state behavior proof before changing this branch.",
            "stopCondition": "Stop if the only evidence is less-code pressure without behavior proof.",
        },
        {
            "file": "Sources/SyntheticLeanReview/PluginHostAdapter.swift",
            "source": "unified-diff",
            "decision": "keep",
            "addedLines": 5,
            "removedLines": 0,
            "ruleIds": ["host-adapter-boundary-diff"],
            "firstLocation": "Sources/SyntheticLeanReview/PluginHostAdapter.swift:12",
            "firstExperiment": "Treat this as a host-adapter keep boundary until protocol or runtime proof shows it is redundant.",
            "validationRoute": "Run or attach the smallest plugin, MCP, preview, or runtime proof that covers the adapter boundary.",
            "stopCondition": "Stop if the only evidence is less-code pressure against a product-surface adapter.",
        },
        {
            "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
            "source": "unified-diff",
            "decision": "proof-blocked",
            "addedLines": 7,
            "removedLines": 0,
            "ruleIds": ["one-runnable-check-missing-diff"],
            "firstLocation": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
            "firstExperiment": action_groups[2]["firstExperiment"],
            "validationRoute": action_groups[2]["validationRoute"],
            "stopCondition": action_groups[2]["stopCondition"],
        },
        {
            "file": "Sources/SyntheticLeanReview/SensorSampler.swift",
            "source": "unified-diff",
            "decision": "proof-blocked",
            "addedLines": 6,
            "removedLines": 0,
            "ruleIds": ["hardware-calibration-missing-diff"],
            "firstLocation": "Sources/SyntheticLeanReview/SensorSampler.swift:33",
            "firstExperiment": action_groups[3]["firstExperiment"],
            "validationRoute": action_groups[3]["validationRoute"],
            "stopCondition": action_groups[3]["stopCondition"],
        },
        {
            "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
            "source": "unified-diff",
            "decision": "clean",
            "addedLines": 6,
            "removedLines": 0,
            "ruleIds": ["one-runnable-check-signal-present-diff"],
            "firstLocation": "Sources/SyntheticLeanReview/SelectionPolicy.swift:27",
            "firstExperiment": "Review the matching same-diff test before adding any duplicate test ceremony.",
            "validationRoute": "Run Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift or the equivalent focused lane.",
            "stopCondition": "Stop if the changed same-diff test already proves the new branch and no Lean cleanup remains.",
        },
        {
            "file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift",
            "source": "unified-diff",
            "decision": "clean",
            "addedLines": 5,
            "removedLines": 0,
            "ruleIds": [],
            "firstLocation": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9",
            "firstExperiment": "Run the changed focused test and confirm it covers the changed selection branch.",
            "validationRoute": "Run the focused test lane before broader validation.",
            "stopCondition": "Stop if the test is unrelated to the changed logic.",
        },
        {
            "file": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift",
            "source": "unified-diff",
            "decision": "clean",
            "addedLines": 4,
            "removedLines": 0,
            "ruleIds": [],
            "firstLocation": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7",
            "firstExperiment": "Keep this unrelated smoke test visible as evidence that proof signals are not global.",
            "validationRoute": "Run only if this separate smoke path matters to the task.",
            "stopCondition": "Stop if a maintainer tries to count this unrelated test as proof for a different changed file.",
        },
    ]
    proof_signal = {
        "file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift",
        "line": 9,
        "kind": "test-file",
        "addedLines": 5,
        "snippet": "func testPrimaryOptionWins() { XCTAssertEqual(policy.pick(primary), .preferred(primary.id)) }",
        "checkSignal": True,
    }
    unrelated_proof_signal = {
        "file": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift",
        "line": 7,
        "kind": "test-file",
        "addedLines": 4,
        "snippet": "func testUnrelatedSmokePath() { XCTAssertTrue(smokePath.isEnabled) }",
        "checkSignal": True,
    }
    proof_signals = [proof_signal, unrelated_proof_signal]
    delete_list = [
        {
            "rank": 1,
            "ruleId": "thin-wrapper-diff-review",
            "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
            "severity": "opportunity",
            "action": "Inline or delete this wrapper unless it adds policy.",
            "proofRequired": "Search call sites and keep one small check if behavior is non-trivial.",
        }
    ]
    simplify_first = [
        {
            "rank": 2,
            "ruleId": "stdlib-url-params-diff",
            "location": "Sources/SyntheticLeanReview/QueryBuilder.swift:22",
            "severity": "opportunity",
            "action": "Prefer URLComponents or URLQueryItem when runtime support allows it.",
            "proofRequired": "Add one check for repeated keys, empty values, encoding, and malformed input.",
        }
    ]
    keep_list = [
        {
            "ruleId": "do-not-cut-safety-diff-without-proof",
            "location": "Sources/SyntheticLeanReview/PermissionGate.swift:31",
            "reason": "Less-code pressure is not enough for permission-state branches.",
            "proofRequired": "Attach focused permission-state behavior proof.",
        },
        {
            "ruleId": "host-adapter-boundary-diff",
            "location": "Sources/SyntheticLeanReview/PluginHostAdapter.swift:12",
            "reason": "Thin host adapters can be the product boundary.",
            "proofRequired": "Attach call-site, protocol, plugin, MCP, preview, or runtime proof before simplifying the adapter boundary.",
        },
    ]
    blocked_by_proof = [
        {
            "rank": 3,
            "ruleId": "one-runnable-check-missing-diff",
            "location": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
            "severity": "review",
            "action": "Leave one smallest runnable route-selection check.",
            "proofRequired": "Add one focused route-selection check or point to the changed test that covers this branch before merge.",
        },
        {
            "rank": 4,
            "ruleId": "hardware-calibration-missing-diff",
            "location": "Sources/SyntheticLeanReview/SensorSampler.swift:33",
            "severity": "review",
            "action": "Keep a minimal calibration or tuning boundary for hardware behavior.",
            "proofRequired": "Attach real-device, sensor, timing, or calibration evidence before simplifying the physical-world edge case away.",
        },
    ]
    top_actions = [delete_list[0], simplify_first[0], blocked_by_proof[0], blocked_by_proof[1]]
    mode_bias_review = {
        "selectedMode": "full",
        "selectedFirstActionBias": "proof-ladder",
        "selectedPriorityOrder": ["deleteList", "simplifyFirst", "blockedByProof"],
        "selectedPolicy": "Use the normal proof ladder before adding or deleting code.",
        "expectedFirstSource": "deleteList",
        "expectedFirstAction": {
            "sourceList": "deleteList",
            "rank": 1,
            "ruleId": "thin-wrapper-diff-review",
            "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
            "severity": "opportunity",
        },
        "selectedFirstAction": {
            "sourceList": "deleteList",
            "rank": 1,
            "ruleId": "thin-wrapper-diff-review",
            "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
            "severity": "opportunity",
        },
        "supportedModes": [
            {
                "mode": "lite",
                "firstActionBias": "suggestion-first",
                "priorityOrder": ["simplifyFirst", "deleteList", "blockedByProof"],
                "policy": "Start with the smallest suggestion before delete pressure.",
                "firstAvailableSource": "simplifyFirst",
                "firstAvailableAction": {
                    "sourceList": "simplifyFirst",
                    "rank": 2,
                    "ruleId": "stdlib-url-params-diff",
                    "location": "Sources/SyntheticLeanReview/QueryBuilder.swift:22",
                    "severity": "opportunity",
                },
            },
            {
                "mode": "full",
                "firstActionBias": "proof-ladder",
                "priorityOrder": ["deleteList", "simplifyFirst", "blockedByProof"],
                "policy": "Use the normal proof ladder before adding or deleting code.",
                "firstAvailableSource": "deleteList",
                "firstAvailableAction": {
                    "sourceList": "deleteList",
                    "rank": 1,
                    "ruleId": "thin-wrapper-diff-review",
                    "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
                    "severity": "opportunity",
                },
            },
            {
                "mode": "ultra",
                "firstActionBias": "delete-first",
                "priorityOrder": ["deleteList", "blockedByProof", "simplifyFirst"],
                "policy": "Try deletion and existence proof before simplification.",
                "firstAvailableSource": "deleteList",
                "firstAvailableAction": {
                    "sourceList": "deleteList",
                    "rank": 1,
                    "ruleId": "thin-wrapper-diff-review",
                    "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
                    "severity": "opportunity",
                },
            },
        ],
        "summary": {
            "supportedModeCount": 3,
            "cleanState": False,
            "selectedModeMatchesPrecisionReview": True,
            "selectedFirstActionBiasMatchesPrecisionReview": True,
            "selectedTopActionMatchesBias": True,
        },
    }
    return {
        "surface": "ShipGuard Lean Review",
        "target": {"path": ".", "shareable": True},
        "diff": {"path": "synthetic-current-change.diff", "filesChanged": 9},
        "metrics": {
            "filesChanged": 9,
            "addedLines": 52,
            "findings": 7,
            "reviewFindings": 2,
            "opportunityFindings": 2,
            "infoFindings": 3,
        },
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native diff review for unnecessary code. It does not vendor Ponytail code.",
        },
        "leanMode": {
            "mode": "full",
            "intent": "Use the proof ladder before adding or deleting code.",
            "firstActionBias": "proof-ladder",
            "policy": "Use full mode for current-diff review when proof boundaries matter.",
        },
        "modeBiasReview": mode_bias_review,
        "currentDiffDecisionMap": {
            "scope": "current-diff-only",
            "diffPath": "synthetic-current-change.diff",
            "inventoryBoundary": "This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.",
            "wholeRepoFallbackCommand": "shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable",
            "changedFiles": [
                {"file": "Sources/SyntheticLeanReview/FormatterShim.swift", "addedLines": 6, "removedLines": 0},
                {"file": "Sources/SyntheticLeanReview/QueryBuilder.swift", "addedLines": 8, "removedLines": 1},
                {"file": "Sources/SyntheticLeanReview/PermissionGate.swift", "addedLines": 5, "removedLines": 0},
                {"file": "Sources/SyntheticLeanReview/PluginHostAdapter.swift", "addedLines": 5, "removedLines": 0},
                {"file": "Sources/SyntheticLeanReview/RuleRouter.swift", "addedLines": 7, "removedLines": 0},
                {"file": "Sources/SyntheticLeanReview/SensorSampler.swift", "addedLines": 6, "removedLines": 0},
                {"file": "Sources/SyntheticLeanReview/SelectionPolicy.swift", "addedLines": 6, "removedLines": 0},
                {"file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift", "addedLines": 5, "removedLines": 0},
                {"file": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift", "addedLines": 4, "removedLines": 0},
            ],
            "decisions": decisions,
            "deleteOrSimplifyList": [decisions[0], decisions[1]],
            "summary": {
                "filesChanged": 9,
                "addedLinesInspected": 52,
                "removedLinesSeen": 1,
                "decisionRows": 9,
                "deleteCandidates": 1,
                "simplifyCandidates": 1,
                "keepBoundaries": 2,
                "proofBlockedCandidates": 2,
                "cleanFiles": 3,
            },
            "nonClaims": [
                "Does not prove whole-repo inventory coverage.",
                "Does not prove benchmark savings, token savings, cost savings, or time savings.",
                "Does not authorize private target-app edits from ShipGuard product-QA runs.",
            ],
        },
        "behaviorGates": {
            "oneRunnableCheck": {
                "status": "enforced-in-lean-review",
                "policy": "Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony.",
            },
            "hardwareCalibration": {
                "status": "available",
                "policy": "Hardware, sensors, clocks, and physical devices need calibration/tuning proof before simplification.",
            },
            "requestedExplanation": {
                "status": "policy",
                "policy": "Explicitly requested reports, walkthroughs, or phase notes are not clutter.",
            },
            "adapterBoundary": {
                "status": "available",
                "policy": "Thin host adapters can be the product surface; flag them as keep-with-proof instead of deletion candidates.",
            },
            "gainHonesty": {
                "status": "available-in-lean-gain",
                "policy": "ShipGuard reports benchmark impact separately and does not invent per-repo line, token, cost, or time savings.",
            },
        },
        "proofSignalCalibration": {
            "sameDiffProofStatus": "present",
            "proofSignals": proof_signals,
            "sameDiffProofSignalCount": 2,
            "codeFindingsCoveredBySameDiffProof": 1,
            "missingRunnableCheckFindings": 1,
            "policy": "Lean Review should distinguish no proof signal from same-diff proof signal. Same-diff tests still need human relevance review, but they should not produce duplicate missing-check ceremony.",
        },
        "proofSignalMatching": {
            "policy": "Same-diff proof is file-scoped. A changed test or assertion satisfies a changed code file only when ShipGuard can match it by same file, path stem, or meaningful path tokens.",
            "nonGlobalProofBoundary": "Unrelated or unmatched proof signals are listed separately and do not satisfy missing proof for other changed files; same-diff proof is not treated as global proof.",
            "rows": [
                {
                    "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
                    "line": 18,
                    "nonTrivialLogic": True,
                    "addedCheckInFile": False,
                    "matchedProofSignalCount": 0,
                    "matchedProofSignals": [],
                    "matchingDecision": "missing-proof",
                },
                {
                    "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
                    "line": 27,
                    "nonTrivialLogic": True,
                    "addedCheckInFile": False,
                    "matchedProofSignalCount": 1,
                    "matchedProofSignals": [
                        {
                            **proof_signal,
                            "location": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9",
                        }
                    ],
                    "matchingDecision": "matched-same-diff-proof",
                },
            ],
            "unmatchedProofSignals": [
                {
                    **unrelated_proof_signal,
                    "location": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7",
                }
            ],
            "summary": {
                "changedCodeFiles": 7,
                "nonTrivialLogicFiles": 2,
                "matchedSameDiffProofFiles": 1,
                "missingProofFiles": 1,
                "inlineCheckFiles": 0,
                "matchedProofSignalCount": 1,
                "unmatchedProofSignalCount": 1,
            },
        },
        "runnableCheckReview": {
            "policy": "Non-trivial branch, loop, parser, and collection logic should leave one smallest runnable check.",
            "nonCeremonyBoundary": "If the same diff already changes a focused test, XCTest, assertion, or explicit check signal, Lean Review records that same-diff proof signal instead of asking for duplicate test ceremony. The maintainer still needs to review relevance and run the focused check.",
            "missingProofFindings": [
                {
                    "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
                    "line": 18,
                    "location": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
                    "ruleId": "one-runnable-check-missing-diff",
                    "severity": "review",
                    "evidence": "if route.kind == .generated { return GeneratedRoute(route.payload) }",
                    "recommendation": missing_check_finding["recommendation"],
                    "proofGuidance": missing_check_finding["proofGuidance"],
                }
            ],
            "sameDiffProofFindings": [
                {
                    "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
                    "line": 27,
                    "location": "Sources/SyntheticLeanReview/SelectionPolicy.swift:27",
                    "ruleId": "one-runnable-check-signal-present-diff",
                    "severity": "info",
                    "evidence": "if option.isPrimary { return .preferred(option.id) }",
                    "recommendation": same_diff_proof_finding["recommendation"],
                    "proofGuidance": same_diff_proof_finding["proofGuidance"],
                }
            ],
            "sameDiffProofSignals": proof_signals,
            "summary": {
                "missingRunnableCheckFindings": 1,
                "sameDiffProofFindings": 1,
                "sameDiffProofSignalCount": 2,
                "duplicateCeremonyAvoided": 1,
            },
            "proofToReview": [
                "For missing-proof rows, add or identify the smallest runnable check that covers the changed behavior.",
                "For same-diff proof rows, run the changed check and confirm it exercises the changed non-trivial logic.",
            ],
        },
        "hardwareHostBoundaryReview": {
            "policy": (
                "Lean Review should block false less-code pressure around physical-world behavior and product-surface "
                "host adapters. Hardware needs calibration proof; host adapters need call-site or protocol proof before "
                "they are treated as removable wrappers."
            ),
            "hardwareCalibrationPolicy": (
                "Hardware, sensors, clocks, and physical devices need calibration, timing, or real-device evidence before "
                "simplification removes tuning boundaries."
            ),
            "hostAdapterPolicy": (
                "Thin plugin, MCP, preview, simulator, and platform host adapters can be the product boundary. Keep them "
                "until call-site, protocol, or runtime proof shows the adapter is redundant."
            ),
            "hardwareCalibrationFindings": [
                {
                    "file": "Sources/SyntheticLeanReview/SensorSampler.swift",
                    "line": 33,
                    "location": "Sources/SyntheticLeanReview/SensorSampler.swift:33",
                    "ruleId": "hardware-calibration-missing-diff",
                    "severity": "review",
                    "evidence": "let rawSample = adc.read(channel: channel)",
                    "recommendation": hardware_finding["recommendation"],
                    "proofGuidance": hardware_finding["proofGuidance"],
                }
            ],
            "hostAdapterBoundaryFindings": [
                {
                    "file": "Sources/SyntheticLeanReview/PluginHostAdapter.swift",
                    "line": 12,
                    "location": "Sources/SyntheticLeanReview/PluginHostAdapter.swift:12",
                    "ruleId": "host-adapter-boundary-diff",
                    "severity": "info",
                    "evidence": "func handle(_ request: PluginRequest) -> PluginResponse { adapter.handle(request) }",
                    "recommendation": host_adapter_finding["recommendation"],
                    "proofGuidance": host_adapter_finding["proofGuidance"],
                }
            ],
            "summary": {
                "hardwareCalibrationFindings": 1,
                "hostAdapterBoundaryFindings": 1,
                "falseLessCodePressureBlocked": 2,
                "proofBlockedHardwareFiles": 1,
                "keepHostAdapterFiles": 1,
            },
            "proofToAttach": [
                "For hardware rows, attach calibration, tuning, timing, sensor, or physical-device proof before simplifying.",
                "For host-adapter rows, attach call-site, protocol, plugin, MCP, preview, or runtime proof before deleting a thin adapter.",
            ],
        },
        "safetyBoundaryReview": {
            "policy": (
                "Lean Review must keep safety, trust, permission, accessibility, validation, data-loss, and security "
                "boundaries out of automatic deletion. Less-code pressure is only allowed after focused behavior proof."
            ),
            "automaticDeletionBoundary": (
                "A safety-boundary row is a keep-with-proof decision, even when the same file also contains cleanup pressure."
            ),
            "safetyBoundaryFindings": [
                {
                    "file": "Sources/SyntheticLeanReview/PermissionGate.swift",
                    "line": 31,
                    "location": "Sources/SyntheticLeanReview/PermissionGate.swift:31",
                    "ruleId": "do-not-cut-safety-diff-without-proof",
                    "severity": "info",
                    "evidence": "guard authorizationStatus == .authorized else { return .blocked }",
                    "recommendation": keep_finding["recommendation"],
                    "proofGuidance": keep_finding["proofGuidance"],
                }
            ],
            "summary": {
                "safetyBoundaryFindings": 1,
                "falseDeletionPressureBlocked": 1,
                "keepSafetyBoundaryFiles": 1,
            },
            "proofToAttach": [
                "Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior.",
                "Do not delete or simplify a safety-boundary row from source-only less-code pressure.",
            ],
        },
        "precisionReview": {
            "principle": "The best ShipGuard code is the code that proves it needs to exist.",
            "mode": {"mode": "full", "firstActionBias": "proof-ladder"},
            "deleteList": delete_list,
            "simplifyFirst": simplify_first,
            "keepList": keep_list,
            "blockedByProof": blocked_by_proof,
            "actionGroups": action_groups,
            "topActions": top_actions,
            "summary": {
                "deleteCandidates": 1,
                "simplifyCandidates": 1,
                "keepBoundaries": 2,
                "proofBlockedCandidates": 2,
                "actionGroups": 4,
            },
        },
        "findings": [
            delete_finding,
            simplify_finding,
            keep_finding,
            host_adapter_finding,
            missing_check_finding,
            hardware_finding,
            same_diff_proof_finding,
        ],
        "nextActions": [
            "Start with currentDiffDecisionMap.deleteOrSimplifyList[0] before reading whole-repo inventory.",
            "Use shipguard lean audit only when a whole-repo Lean inventory is actually needed.",
            "Do not convert this ShipGuard product-QA fixture into target-app implementation work.",
        ],
    }


def synthetic_design_tailoring(app_type: str = "education") -> dict[str, Any]:
    return {
        "tailoredFor": app_type,
        "guidanceProfile": "learning-progress" if app_type == "education" else "utility-speed",
        "universalDefaultsRejected": True,
        "sourceSignalSummary": "lesson->education, learn->education, progress->education",
        "sourceSignals": [
            {"appType": "education", "token": "lesson", "file": "Sources/SyntheticDesignFixture/LearningFlow.swift", "count": 12},
            {"appType": "education", "token": "learn", "file": "Sources/SyntheticDesignFixture/LearningFlow.swift", "count": 8},
            {"appType": "education", "token": "progress", "file": "Sources/SyntheticDesignFixture/LearningFlow.swift", "count": 5},
        ],
        "dimensions": {
            "motion": {
                "stance": "production-polish",
                "reason": "Motion should clarify learning state, feedback, and recovery rather than apply utility-only restraint.",
                "observedSignals": {"withAnimation": 4, "animationModifiers": 2, "repeatForever": 1, "timelineView": 0},
            },
            "haptics": {
                "tone": "encouraging, milestone-aware, and interruption-sparse",
                "deviceProofRequired": True,
                "observedSignals": {"uikitFeedbackSignals": 1, "coreHapticsSignals": 0, "sensoryFeedbackSignals": 0},
            },
            "visualDensity": {
                "stance": "allow expressive hierarchy with proof",
                "observedSignals": {"rounded": 8, "shadow": 2, "blur": 1, "cardNames": 3},
            },
            "copyTone": {
                "stance": "specific to the app task and audience",
                "visibleStringCount": 9,
                "localizationSignals": 2,
            },
        },
        "nextAction": {
            "owner": "developer",
            "kind": "manual-proof",
            "manualProof": "Review one synthetic learning flow and confirm motion, haptics, visual density, and copy guidance match the education profile rather than a universal design checklist.",
            "expectedArtifact": "A same-flow screenshot or preview receipt plus one note mapping the learning-progress profile to source signals.",
            "successCondition": "The report explains why learning-progress is the right profile for education and avoids utility-only advice.",
            "failureMeaning": "The design report remains an inventory, not an app-type-specific design QA recommendation.",
        },
        "risk": "Generic utility restraint can make learning feedback feel flat, while generic game delight can distract from comprehension.",
    }


def synthetic_design_coherence_boundary() -> dict[str, Any]:
    return {
        "purpose": "Keep design-system coherence findings as ShipGuard product-QA evidence until target-app work is separately authorized.",
        "sourceInventory": {
            "appType": "education",
            "colorSignals": 12,
            "typographySignals": 6,
            "componentSignals": {"Button": 3, "NavigationStack": 1, "ProgressView": 1},
            "visualEffectSignals": {"blur": 1, "shadow": 2, "rounded": 8, "cardNames": 3},
            "motionSignals": {
                "withAnimation": 4,
                "animationModifiers": 2,
                "repeatForever": 1,
                "timelineView": 0,
                "reduceMotion": 2,
            },
            "hapticSignals": {"uikitFeedbackSignals": 1, "coreHapticsSignals": 0, "sensoryFeedbackSignals": 0},
            "copySignals": {"visibleStringCount": 9, "localizationSignals": 2},
            "iconographySignals": {"sfSymbolSignals": 6, "customImageSignals": 0, "symbolEffectSignals": 1},
        },
        "coherenceRisks": [
            {
                "ruleId": "design-coherence-target-work-boundary",
                "category": "Design DNA",
                "severity": "review",
                "title": "Design coherence finding must not become target-app work",
                "evidence": "Synthetic design inventory has visual, motion, haptic, and copy signals but no app-work authorization.",
            }
        ],
        "separationChecks": {
            "inventoryIsNotRemediation": True,
            "coherenceRiskIsNotTargetTask": True,
            "shipguardActionIsPublicFixtureOrRule": True,
            "appWorkRequiresSeparateAuthorization": True,
        },
        "shipguardNextAction": {
            "owner": "ShipGuard maintainer",
            "kind": "public-fixture-or-report-rule",
            "sourceQuestion": "Did it separate design-system coherence findings from target-app implementation work?",
            "expectedArtifact": "A public synthetic report-quality fixture that checks the coherence boundary without private app data.",
            "successCondition": "Report-quality fails if a design report turns coherence inventory into target-app implementation work or hides the authorization boundary.",
            "failureMeaning": "Private app design evidence can still become unreviewed app remediation advice instead of ShipGuard product QA.",
        },
        "appWorkAuthorization": {
            "status": "not-authorized-from-this-run",
            "requiresExplicitRequest": True,
            "forbiddenActions": [
                "Do not edit the scanned app from this report.",
                "Do not open target-app redesign, icon, haptic, motion, or localization tasks from this report.",
            ],
            "allowedShipGuardActions": [
                "Improve ShipGuard report fields, Markdown, rules, docs, plugin guidance, or public fixtures.",
                "Use private app evidence only to choose the shape of synthetic public eval coverage.",
            ],
        },
        "proofBoundary": {
            "localProof": "Run shipguard ios report-quality on this synthetic design fixture.",
            "manualProof": "A human may later authorize target-app design work, but this fixture does not authorize it.",
            "expectedArtifact": "ios-report-quality.json plus fixture coverage for design coherence boundaries.",
        },
        "targetRemediationStatus": "not-authorized-from-this-run",
    }


def synthetic_professional_design_principle_vocabulary() -> dict[str, Any]:
    return {
        "source": "ShipGuard native design QA vocabulary inspired by professional visual-design principles.",
        "requiredPrinciples": [
            "contrast",
            "hierarchy",
            "alignment",
            "proximity",
            "repetition",
            "balance",
            "white space",
            "unity",
            "motion",
            "haptics",
            "preview proof",
            "app-type fit",
        ],
        "checks": [
            {"principle": "contrast", "question": "Can lesson status and primary actions be distinguished without decorative color dependence?"},
            {"principle": "hierarchy", "question": "Does the learning flow show lesson goal, current task, and next step in that order?"},
            {"principle": "alignment", "question": "Do lesson cards, progress labels, and controls share a deliberate grid?"},
            {"principle": "proximity", "question": "Are related learning controls grouped and recovery actions separated?"},
            {"principle": "repetition", "question": "Are cards, buttons, and success states reused across the learning flow?"},
            {"principle": "balance", "question": "Is progress feedback visually weighted without overwhelming the lesson content?"},
            {"principle": "white space", "question": "Does spacing give comprehension room without wasting mobile screen density?"},
            {"principle": "unity", "question": "Do color, type, symbols, copy, motion, and haptics feel like one education product?"},
            {"principle": "motion", "question": "Does motion clarify progress or recovery while respecting Reduce Motion?"},
            {"principle": "haptics", "question": "Are haptics milestone-aware, sparse, and left unclaimed until device proof exists?"},
            {"principle": "preview proof", "question": "Are visual claims backed by iPhone preview or Devspace evidence?"},
            {"principle": "app-type fit", "question": "Is the guidance tuned for education comprehension instead of generic utility polish?"},
        ],
    }


def synthetic_design_report_fields() -> dict[str, Any]:
    return {
        "status": "review",
        "resultUX": {
            "status": "review",
            "sourceStatus": "review",
            "verdict": "REVIEW: Synthetic design fixture needs preview proof before visual claims.",
            "proofSource": "designTailoring.nextAction + designDNA + optional previewEvidence",
            "whyItMatters": "Design QA must route visual claims through phone-shaped preview or Devspace proof.",
            "nextCommand": "shipguard ios preview --out /tmp/ios-shipguard-preview",
            "nextActionSummary": "Run preview for phone-shaped visual evidence; use Devspace when ChatGPT should plan from the preview widget.",
        },
        "appType": {
            "value": "education",
            "inferred": "education",
            "override": None,
            "confidence": 0.78,
            "scores": {"education": 25, "utility": 4, "game": 3},
            "signals": synthetic_design_tailoring("education")["sourceSignals"],
        },
        "designTailoring": synthetic_design_tailoring("education"),
        "designCoherenceBoundary": synthetic_design_coherence_boundary(),
        "professionalDesignPrincipleVocabulary": synthetic_professional_design_principle_vocabulary(),
        "designDNA": {
            "motion": {"withAnimationSignals": 4, "animationModifiers": 2, "repeatForeverSignals": 1, "timelineViewSignals": 0, "reduceMotionSignals": 2},
            "haptics": {"uikitFeedbackSignals": 1, "coreHapticsSignals": 0, "sensoryFeedbackSignals": 0},
            "layout": {"roundedSignals": 8, "shadowSignals": 2, "blurSignals": 1, "cardNameSignals": 3},
            "copyTone": {"visibleStringCount": 9, "localizationSignals": 2, "samples": ["Lesson complete", "Try again"]},
        },
        "previewEvidence": {
            "status": "not-provided",
            "recommendedCommands": [
                "shipguard ios preview --out /tmp/ios-shipguard-preview",
                "shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN",
            ],
        },
        "findings": [
            {
                "severity": "review",
                "category": "Design DNA",
                "ruleId": "design-coherence-target-work-boundary",
                "title": "Design coherence finding must not become target-app work",
                "evidence": "Synthetic design inventory has visual, motion, haptic, and copy signals but no app-work authorization.",
                "recommendation": "Improve ShipGuard report-quality rules or public fixtures before using this as target-app implementation guidance.",
                "proof": "Review the Design Tailoring Contract and Design Coherence Boundary, then run report-quality on the synthetic fixture.",
                "proofGuidance": "Review the Design Tailoring Contract and Design Coherence Boundary, then run report-quality on the synthetic fixture.",
            },
            {
                "severity": "opportunity",
                "category": "Preview",
                "ruleId": "preview-proof-not-provided",
                "title": "Design audit has no live iPhone preview evidence",
                "evidence": "No synthetic preview receipt was supplied.",
                "recommendation": "Run shipguard ios preview for a phone-shaped visual proof loop; use ios devspace when ChatGPT should plan from that widget.",
                "proof": "Attach preview-events.jsonl, handoff.md, and refreshed screenshot evidence for visual claims.",
                "proofGuidance": "Attach preview-events.jsonl, handoff.md, and refreshed screenshot evidence for visual claims.",
            }
        ],
    }


def synthetic_stable_publication_report_fields() -> dict[str, Any]:
    required = [
        ("github-release-metadata", "githubReleaseMetadataProof"),
        ("release-notes", "releaseNotesProof"),
        ("launchkey-candidate-packet", "releaseCandidatePacketProof"),
        ("downloaded-release-assets", "publishedReleaseAssetProof"),
        ("post-release-consumer-proof", "postReleaseConsumerProof"),
        ("public-release-freshness", "publicReleaseFreshnessProof"),
        ("release-version-coherence", "releaseVersionCoherenceProof"),
        ("release-asset-coherence", "releaseAssetCoherenceProof"),
        ("independent-adoption-evidence", "externalAdoptionEvidenceStableGate"),
        ("final-security-review-evidence", "securityReviewEvidenceStableGate"),
    ]
    evidence_packet = {
        "schemaVersion": 1,
        "releaseVersion": "0.0.0",
        "status": "pass",
        "stableV4Release": True,
        "requiredEvidenceCount": len(required),
        "passedEvidenceCount": len(required),
        "missingEvidenceIds": [],
        "firstBlockingGate": None,
        "requiredEvidence": [
            {
                "id": evidence_id,
                "receipt": receipt,
                "status": "pass",
                "provided": True,
                "requiredForStableV4": True,
                "realEvidenceRequired": True,
                "summary": "Synthetic public fixture evidence row.",
                "nextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
                **(
                    {
                        "templatePath": "templates/stable-publication/external-adoption-evidence.template.json",
                        "templateCommand": "cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json",
                    }
                    if evidence_id == "independent-adoption-evidence"
                    else {}
                ),
                **(
                    {
                        "templatePath": "templates/stable-publication/security-review-evidence.template.json",
                        "templateCommand": "cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json",
                    }
                    if evidence_id == "final-security-review-evidence"
                    else {}
                ),
            }
            for evidence_id, receipt in required
        ],
        "nonClaims": [
            "This synthetic fixture does not publish a GitHub release.",
            "This synthetic fixture does not prove OpenAI marketplace acceptance.",
            "Fixture adoption or security records prove tooling only.",
        ],
    }
    closure_checklist = {
        "schemaVersion": 1,
        "releaseVersion": "0.0.0",
        "status": "pass",
        "stableV4Release": True,
        "blockerCount": 0,
        "blockedEvidenceIds": [],
        "firstBlocker": None,
        "items": [],
        "dependencyOrder": [evidence_id for evidence_id, _ in required],
        "noHiddenLowerOrderBlockers": True,
        "nextCommand": "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
        "nonClaims": [
            "This checklist does not prove stable v4 by itself.",
            "Every listed item must pass from real publication evidence before stable-v4 claims are allowed.",
        ],
    }
    return {
        "surface": "ShipGuard V4 Stable Publication Proof",
        "stableV4Release": True,
        "stablePublicationGates": [
            {"receipt": receipt, "status": "pass", "nextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable"}
            for _, receipt in required
        ],
        "stablePublicationEvidencePacket": evidence_packet,
        "stablePublicationClosureChecklist": closure_checklist,
        "stablePublicationEvidenceTemplates": {
            "schemaVersion": 1,
            "templateDirectory": "templates/stable-publication",
            "draftOnly": True,
            "templateIds": ["independent-adoption-evidence", "final-security-review-evidence"],
            "templates": [
                {
                    "id": "independent-adoption-evidence",
                    "path": "templates/stable-publication/external-adoption-evidence.template.json",
                    "exists": True,
                    "copyCommand": "cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json",
                },
                {
                    "id": "final-security-review-evidence",
                    "path": "templates/stable-publication/security-review-evidence.template.json",
                    "exists": True,
                    "copyCommand": "cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json",
                },
            ],
        },
        "stablePublicationEvidenceStarterKit": {
            "schemaVersion": 1,
            "draftOnly": True,
            "directory": "stable-publication-evidence-kit",
            "files": [
                {"path": "stable-publication-evidence-kit/README.md", "purpose": "Synthetic starter-kit README."},
                {"path": "stable-publication-evidence-kit/stable-publication-checklist.json", "purpose": "Synthetic checklist."},
                {"path": "stable-publication-evidence-kit/external-adoption-evidence.json", "purpose": "Synthetic adoption starter."},
                {"path": "stable-publication-evidence-kit/security-review-evidence.json", "purpose": "Synthetic security starter."},
            ],
            "externalEvidenceIntakeChecklist": [
                {
                    "id": "independent-adoption-evidence",
                    "acceptedEvidenceClasses": ["public-external", "private-redacted-external"],
                    "requiredFields": ["actorRelationship", "privateDataRedacted", "commands", "artifacts", "outcome", "nonClaims"],
                    "redactionBoundary": {"privateDataRedactedMustBeTrue": True},
                },
                {
                    "id": "final-security-review-evidence",
                    "acceptedEvidenceClasses": ["public-security-review", "private-redacted-security-review"],
                    "requiredFields": ["scope", "methodology", "findingsSummary", "privateDataRedacted", "nonClaims"],
                    "redactionBoundary": {"privateDataRedactedMustBeTrue": True},
                },
            ],
            "adoptionEvidenceChecklist": {
                "acceptedEvidenceClasses": ["public-external", "private-redacted-external"],
                "requiredActorRelationship": "independent",
                "requiredProofFields": ["commands", "artifacts", "outcome", "nonClaims"],
                "artifactExpectations": ["install transcript or command log", "generated ShipGuard report or validation output"],
                "redactionBoundaries": ["privateDataRedacted must be true"],
                "weakSignalExclusions": ["GitHub stars", "download counts", "maintainer-only private app runs"],
                "passDecision": "Pass only when a non-maintainer actor supplies redacted/public command and artifact evidence for real ShipGuard use.",
            },
            "securityReviewChecklist": {
                "requiredReviewSurfaces": ["cli", "plugin", "github-actions", "release-proof", "package-install", "redaction-privacy"],
                "severityThresholds": {"criticalOpen": 0, "highOpen": 0},
                "requiredEvidenceFields": ["reviewerRelationship", "scope", "methodology", "commands", "artifacts", "findingsSummary", "nonClaims"],
                "redactionBoundaries": ["privateDataRedacted must be true"],
                "passDecision": "Pass only when every required surface is reviewed and criticalOpen plus highOpen are both 0.",
            },
            "nextCommandTemplate": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --external-adoption-evidence stable-publication-evidence-kit/external-adoption-evidence.json --security-review-evidence stable-publication-evidence-kit/security-review-evidence.json --shipguard-eval --shareable",
        },
        "stablePublicationReleaseNotesAuthoringKit": {
            "schemaVersion": 2,
            "draftOnly": True,
            "directory": "stable-publication-release-notes",
            "releaseTag": "v0.0.0",
            "releaseUrl": "https://github.com/example/shipguard/releases/tag/v0.0.0",
            "missingTopicIds": [],
            "publicReleaseEditCommand": "gh release edit v0.0.0 --repo example/shipguard --notes-file stable-publication-release-notes/draft-release-notes.md",
            "files": [
                {"path": "stable-publication-release-notes/README.md", "purpose": "Synthetic release-notes README."},
                {"path": "stable-publication-release-notes/release-notes-checklist.json", "purpose": "Synthetic checklist."},
                {"path": "stable-publication-release-notes/draft-release-notes.md", "purpose": "Synthetic draft release notes."},
            ],
            "nextCommandTemplate": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
        },
        "stablePublicationLaunchRelayDrafts": {
            "schemaVersion": 1,
            "draftOnly": True,
            "directory": "stable-publication-launch-relay",
            "releaseVersion": "0.0.0",
            "status": "ready-to-stage",
            "approvalRequired": True,
            "publicPostingAllowed": False,
            "stableV4Release": True,
            "postingPolicy": {
                "requiresExplicitApproval": True,
                "publicPostingAllowed": False,
                "computerUseMayStageDrafts": True,
                "computerUseMayPost": False,
                "approvalText": "Public posting, publishing, submission, or account-visible external actions require explicit human approval for that exact launch run.",
            },
            "channels": [
                {"id": "product-hunt", "draftPath": "stable-publication-launch-relay/product-hunt-draft.md"},
                {"id": "reddit-r-shipguard", "draftPath": "stable-publication-launch-relay/reddit-r-shipguard-draft.md"},
                {"id": "x-thread", "draftPath": "stable-publication-launch-relay/x-thread-draft.md"},
                {"id": "hacker-news", "draftPath": "stable-publication-launch-relay/hacker-news-draft.md"},
            ],
            "files": [
                {"path": "stable-publication-launch-relay/README.md", "purpose": "Synthetic approval boundary."},
                {"path": "stable-publication-launch-relay/launch-relay-checklist.json", "purpose": "Synthetic checklist."},
                {"path": "stable-publication-launch-relay/product-hunt-draft.md", "purpose": "Synthetic Product Hunt draft."},
                {"path": "stable-publication-launch-relay/reddit-r-shipguard-draft.md", "purpose": "Synthetic Reddit draft."},
                {"path": "stable-publication-launch-relay/x-thread-draft.md", "purpose": "Synthetic X draft."},
                {"path": "stable-publication-launch-relay/hacker-news-draft.md", "purpose": "Synthetic HN draft."},
            ],
            "nextCommandTemplate": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
            "nonClaims": [
                "This packet does not publish, submit, post, or schedule anything.",
                "This packet does not authorize computer-use to perform account-visible actions.",
            ],
        },
        "publicReleaseDeltaProof": {
            "schemaVersion": 1,
            "status": "pass",
            "releaseVersion": "0.0.0",
            "sourceVersion": "0.0.0",
            "latestGitHubReleaseVersion": "0.0.0",
            "selectedGitHubReleaseTag": "v0.0.0",
            "latestGitHubReleaseTag": "v0.0.0",
            "latestGitHubReleaseStatus": "pass",
            "packageVersion": "0.0.0",
            "localHeadCommit": "0123456789abcdef0123456789abcdef01234567",
            "localMainCommit": "0123456789abcdef0123456789abcdef01234567",
            "selectedPublicReleaseCommit": "0123456789abcdef0123456789abcdef01234567",
            "releaseManifestCommit": "0123456789abcdef0123456789abcdef01234567",
            "stableV4Release": True,
            "stableV4ClaimCoversSelectedPublicRelease": True,
            "stableV4ClaimCoversLocalCheckout": True,
            "unpublishedLocalDelta": False,
            "comparisons": {
                "sourceVersionMatchesRequestedRelease": True,
                "selectedReleaseMatchesLatestGitHubRelease": True,
                "releaseManifestVersionMatchesRequestedRelease": True,
                "packageAssetsVersionMatchesRequestedRelease": True,
                "publicTagTargetMatchesReleaseManifestCommit": True,
                "releaseAssetCoherencePassed": True,
                "releaseVersionCoherencePassed": True,
                "localHeadMatchesSelectedPublicReleaseCommit": True,
                "localMainMatchesSelectedPublicReleaseCommit": True,
            },
            "problems": [],
            "nextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
            "releaseDeltaBoundary": {
                "latestPublicGitHubReleaseIsPublicationSource": True,
                "localHeadIsNotPublicReleaseProof": True,
                "localMainIsNotPublicReleaseProof": True,
                "unpublishedLocalCodeCountsAsReleased": False,
                "downloadedOrSuppliedAssetsAreRequiredForPackageTruth": True,
                "stableV4ClaimCoversSelectedReleaseOnly": True,
            },
        },
        "releaseVisibilityHandoff": {
            "schemaVersion": 1,
            "releaseVersion": "0.0.0",
            "status": "pass",
            "primaryDecision": "announce-current-public-release",
            "summary": "ShipGuard 0.0.0 can be announced from the current public release.",
            "latestGitHubReleaseVersion": "0.0.0",
            "selectedGitHubReleaseTag": "v0.0.0",
            "latestGitHubReleaseTag": "v0.0.0",
            "unpublishedLocalDelta": False,
            "stableV4Release": True,
            "currentPublicReleaseCanBeAnnounced": True,
            "localMainCanBeAnnounced": True,
            "requiredActions": [
                {"id": "publish-new-github-release", "required": False, "status": "pass", "reason": "Synthetic release is aligned.", "nextCommand": "not-needed", "nextCommandPurpose": "not-needed", "proofCommandAfterCompletion": "not-needed"},
                {"id": "update-release-notes", "required": False, "status": "pass", "reason": "Synthetic release notes passed.", "nextCommand": "not-needed", "nextCommandPurpose": "not-needed", "proofCommandAfterCompletion": "not-needed"},
                {"id": "attach-launchkey-candidate-proof", "required": False, "status": "pass", "reason": "Synthetic LaunchKey candidate proof passed.", "nextCommand": "not-needed", "nextCommandPurpose": "not-needed", "proofCommandAfterCompletion": "not-needed"},
                {"id": "update-release-assets", "required": False, "status": "pass", "reason": "Synthetic assets passed.", "nextCommand": "not-needed", "nextCommandPurpose": "not-needed", "proofCommandAfterCompletion": "not-needed"},
                {"id": "attach-adoption-security-evidence", "required": False, "status": "pass", "reason": "Synthetic evidence closure passed.", "nextCommand": "not-needed", "nextCommandPurpose": "not-needed", "proofCommandAfterCompletion": "not-needed"},
                {"id": "keep-current-public-release-unchanged", "required": True, "status": "pass", "reason": "The current public release can remain the announcement target.", "nextCommand": "./bin/shipguard value-gauntlet --path . --out <gauntlet-dir>", "nextCommandPurpose": "final-claim-review", "proofCommandAfterCompletion": "not-needed"},
            ],
            "nextCommand": "./bin/shipguard value-gauntlet --path . --out <gauntlet-dir>",
            "visibilityBoundary": {
                "doesNotPublishRelease": True,
                "doesNotEditGitHubRelease": True,
                "doesNotPostExternally": True,
                "latestPublicGitHubReleaseIsPublicationTruth": True,
                "localHeadIsNotPublicationProof": True,
                "localMainIsNotPublicationProof": True,
                "unpublishedLocalCodeCountsAsReleased": False,
            },
        },
        "finalStableV4ClaimPacket": {
            "schemaVersion": 1,
            "releaseVersion": "0.0.0",
            "status": "allowed",
            "stableV4Release": True,
            "claimDecision": "allowed",
            "copyReadyClaim": "ShipGuard 0.0.0 has passed stable-v4 publication proof.",
            "allowedClaims": [
                "Stable-v4 publication proof passed.",
                "The attached report is the local proof source for the stable-v4 claim.",
            ],
            "blockedClaims": [
                "OpenAI marketplace acceptance is proven.",
                "Public launch posts were published or submitted.",
                "GitHub stars, forks, or downloads prove independent adoption.",
            ],
            "evidenceSummary": [
                {"id": evidence_id, "status": "pass", "requiredForStableV4": True, "nextCommand": "not-needed"}
                for evidence_id in [
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
                ]
            ],
            "missingEvidenceIds": [],
            "firstBlockingGate": None,
            "publicEvidenceClosureStatus": "pass",
            "nextCommand": "./bin/shipguard value-gauntlet --path . --out <gauntlet-dir>",
            "approvalBoundary": {
                "publicPostingRequiresExplicitApproval": True,
                "computerUseMayPost": False,
                "launchRelayStatus": "ready-to-stage",
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
        },
        "releaseNotesProof": {"missingTopicIds": []},
        "publicReleaseFreshnessProof": {
            "status": "pass",
            "provided": True,
            "requiredForStableV4": True,
            "releaseVersion": "0.0.0",
            "releaseTag": "v0.0.0",
            "releaseTargetCommitish": "0123456789abcdef0123456789abcdef01234567",
            "tagTargetSha": "0123456789abcdef0123456789abcdef01234567",
            "releaseManifestPath": "<downloaded-assets>/release-manifest.json",
            "manifestVersion": "0.0.0",
            "manifestTag": "v0.0.0",
            "manifestCommit": "0123456789abcdef0123456789abcdef01234567",
            "manifestGeneratedAt": "2026-06-20T00:00:00Z",
            "comparisons": {
                "manifestVersionMatchesRequested": True,
                "manifestTagMatchesMetadataTag": True,
                "tagTargetMatchesManifestCommit": True,
                "manifestGeneratedNoLaterThanPublishedAt": True,
            },
            "problems": [],
        },
        "releaseVersionCoherenceProof": {
            "status": "pass",
            "provided": True,
            "requiredForStableV4": True,
            "sourceVersion": "0.0.0",
            "releaseVersion": "0.0.0",
            "expectedTag": "v0.0.0",
            "metadataTagName": "v0.0.0",
            "manifestVersion": "0.0.0",
            "packageVersion": "0.0.0",
            "consumerReportVersion": "0.0.0",
            "expectedTarballName": "shipguard-v0.0.0.tar.gz",
            "manifestArtifactName": "shipguard-v0.0.0.tar.gz",
            "comparisons": {
                "sourceVersionMatchesRequested": True,
                "metadataReturnedTagMatchesRequested": True,
                "manifestVersionMatchesRequested": True,
                "packageVersionMatchesRequested": True,
                "consumerReportVersionMatchesRequested": True,
            },
            "versionCoherenceBoundary": {
                "versionMustMatchAcrossSourceMetadataManifestPackageAndConsumerProof": True,
                "sourceOnlyProofCountsAsVersionCoherenceProof": False,
            },
        },
        "releaseAssetCoherenceProof": {
            "status": "pass",
            "provided": True,
            "requiredForStableV4": True,
            "expectedTarballName": "shipguard-v0.0.0.tar.gz",
            "requiredAssetNames": ["shipguard-v0.0.0.tar.gz"],
            "metadataAssetNames": ["shipguard-v0.0.0.tar.gz"],
            "localAssetNames": ["shipguard-v0.0.0.tar.gz"],
            "digestAssetNames": ["shipguard-v0.0.0.tar.gz"],
            "manifestArtifactName": "shipguard-v0.0.0.tar.gz",
            "digestTarballName": "shipguard-v0.0.0.tar.gz",
            "manifestArtifactSha256": "abc123",
            "digestTarballSha256": "abc123",
            "consumerArtifactSha256": "abc123",
            "comparisons": {
                "localAssetsCoverRequired": True,
                "digestAssetsCoverRequired": True,
                "expectedTarballInLocalAssets": True,
                "manifestArtifactShaMatchesDigestTarball": True,
                "consumerArtifactShaMatchesDigestTarball": True,
            },
            "assetCoherenceBoundary": {
                "downloadedOrSuppliedAssetsRequired": True,
                "assetDigestMatrixRequired": True,
                "sourceOnlyProofCountsAsAssetCoherenceProof": False,
                "metadataOnlyProofCountsAsAssetCoherenceProof": False,
            },
        },
        "publicEvidenceClosureProof": {
            "schemaVersion": 1,
            "releaseVersion": "0.0.0",
            "status": "pass",
            "requiredForStableV4": True,
            "evidenceRows": [
                {
                    "id": "independent-adoption-evidence",
                    "status": "pass",
                    "provided": True,
                    "stableV4GateStatus": "pass",
                    "freshnessStatus": "pass",
                    "stableV4EligibleEvidenceCount": 1,
                    "freshStableRecordCount": 1,
                    "staleStableRecordCount": 0,
                    "starterPath": "stable-publication-evidence-kit/external-adoption-evidence.json",
                    "templatePath": "templates/stable-publication/external-adoption-evidence.template.json",
                    "copyCommand": "cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json",
                    "copyReadyNextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
                },
                {
                    "id": "final-security-review-evidence",
                    "status": "pass",
                    "provided": True,
                    "stableV4GateStatus": "pass",
                    "freshnessStatus": "pass",
                    "stableV4EligibleEvidenceCount": 1,
                    "freshStableRecordCount": 1,
                    "staleStableRecordCount": 0,
                    "starterPath": "stable-publication-evidence-kit/security-review-evidence.json",
                    "templatePath": "templates/stable-publication/security-review-evidence.template.json",
                    "copyCommand": "cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json",
                    "copyReadyNextCommand": "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
                },
            ],
            "copyReadyCommands": [
                "cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json",
                "cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json",
                "./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable",
            ],
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
        },
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "doesNotPublishRelease": True,
            "doesNotPostExternally": True,
        },
        "blockedClaims": [
            "Do not publish, submit, post, schedule, or perform account-visible external launch actions without explicit human approval for that exact launch run.",
        ],
    }


def synthetic_fixture_report(candidate: dict[str, Any]) -> dict[str, Any]:
    question = materialized_source_question(candidate)
    source_tool = sanitize_materialized_text(candidate.get("sourceTool")) or "shipguard ios report-quality"
    fixture_type = sanitize_materialized_text(candidate.get("fixtureType")) or "report-quality-actionability-fixture"
    report = {
        "schemaVersion": 1,
        "tool": source_tool,
        "intent": "shipguard-evaluation",
        "generatedAt": utc_now(),
        "status": "pass",
        "shareability": {
            "mode": "shareable",
            "localAbsolutePathsIncluded": False,
        },
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Synthetic public fixture for ShipGuard report-quality behavior.",
        },
        "scanScope": {
            "skippedDirectoryCount": 0,
            "skippedDirectories": [],
            "note": "Synthetic fixture; no private source tree was scanned.",
        },
        "findings": [],
        "reportQualityQuestions": [question],
        "fixtureCandidate": safe_candidate_metadata(candidate),
    }
    if source_tool == "shipguard ios performance":
        report["runtimeEvidenceBoundary"] = {
            "evidence": "source heuristic",
            "confidence": "medium",
            "runtimeProof": "missing",
            "blocking": "no",
            "interpretation": (
                "Synthetic source-only performance fixture; it does not prove actual CPU, GPU, memory, energy, hitch, FPS, "
                "or frame-rate problems."
            ),
            "promotionRule": "Promote only after a public fixture or same-route runtime proof confirms the issue shape.",
            "requiredRuntimeProof": [
                "Same-route Simulator trace, sample, or log evidence for local-only claims.",
                "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.",
            ],
        }
        report["evidencePromotion"] = synthetic_performance_evidence_promotion()
    if source_tool == "shipguard ios performance" and fixture_type == "ios-performance-report-quality-fixture":
        report["status"] = "review"
        report["findings"] = synthetic_performance_findings()
        report["ruleSummary"] = synthetic_performance_rule_summary()
        report["groupedActionPlan"] = synthetic_performance_grouped_action_plan()
    if source_tool == "shipguard lean gain":
        report.update(synthetic_lean_gain_report_fields())
    if source_tool == "shipguard lean debt":
        report.update(synthetic_lean_debt_report_fields())
    if source_tool == "shipguard lean review":
        report.update(synthetic_lean_review_report_fields())
    if source_tool == "shipguard v4 stable-publication":
        report.update(synthetic_stable_publication_report_fields())
    if source_tool == "shipguard prepare":
        report.update(
            {
                "surface": "ShipGuard Task Contract",
                "goal": "Synthetic verify-first task",
                "riskClassification": {"level": "high"},
                "authorizedFiles": ["Sources/SyntheticApp/**", "Tests/SyntheticAppTests/**"],
                "protectedBoundaries": [".github/workflows/release*.yml", "**/*.entitlements"],
                "validationContract": {
                    "required": [
                        {
                            "requirementId": "synthetic-unit-tests",
                            "command": "swift test",
                            "expectedArtifact": "structured validation receipt",
                        }
                    ]
                },
                "verdict": {"status": "prepared"},
                "nextAction": {"command": "swift test"},
                "quickstartReplay": {
                    "phase": "prepare",
                    "taskArtifact": "shipguard-task.json",
                    "markdownArtifact": "shipguard-task.md",
                    "firstUsefulVerdictCommand": (
                        "shipguard verify --task <task-dir>/shipguard-task.json --diff <patch.diff> "
                        "--evidence <validation-receipt.json> --claim <scoped-claim> --out <verdict-dir>"
                    ),
                    "proofInputs": ["<patch.diff>", "<validation-receipt.json>", "<scoped-claim>"],
                    "successSignal": "shipguard-verdict.json returns pass, review, blocked, or incomplete with one nextAction.",
                    "connects": [
                        "goal",
                        "riskClassification",
                        "authorizedFiles",
                        "protectedBoundaries",
                        "validationContract",
                        "agentClaims",
                        "verdict",
                        "nextAction",
                    ],
                    "boundary": "Synthetic replay contract only; it does not authorize target-app work.",
                },
            }
        )
        if is_notification_scope_question(question) or is_notification_proof_lane_question(question):
            report["domainRiskPack"] = synthetic_notification_domain_risk_pack()
    if source_tool == "shipguard verify":
        unsupported_fixture = "unsupported completion claim" in normalized_question_text(question)
        status = "blocked" if unsupported_fixture else "pass"
        replay_command = (
            "shipguard verify --task <shipguard-task.json> --diff <patch.diff> "
            "--evidence <validation-receipt.json> "
            "--claim 'Notification permission copy is fully verified.' --out <verdict-dir>"
            if unsupported_fixture
            else "shipguard verify --task <shipguard-task.json> --diff <patch.diff> "
            "--evidence <validation-receipt.json> --claim <scoped-claim> --out <verdict-dir>"
        )
        fast_verdict = (
            "ShipGuard Proof Report: blocked. Validation 1/1 covered; claims 0/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable."
            if unsupported_fixture
            else "ShipGuard Proof Report: pass. Validation 1/1 covered; claims 1/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable."
        )
        next_action = (
            {
                "owner": "developer",
                "command": "Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify.",
                "expectedArtifact": "updated claim or structured evidence receipt",
                "successCondition": "No unsupported completion claim remains",
                "failureMeaning": "unsupported completion claim without evidence",
                "resolves": ["unsupported-completion-claim"],
                "priority": 6,
            }
            if unsupported_fixture
            else {"command": "Attach shipguard-verdict.json and the evidence receipts to the review."}
        )
        report.update(
            {
                "surface": "ShipGuard Task Contract Verdict",
                "goal": "Synthetic verify-first task",
                "status": status,
                "proofReport": {
                    "copyReadyText": fast_verdict,
                    "status": status,
                    "claims": {
                        "checkedCount": 1,
                        "acceptedCount": 0 if unsupported_fixture else 1,
                        "rejectedCount": 1 if unsupported_fixture else 0,
                        "manualProofCount": 0,
                        "label": "0/1 accepted" if unsupported_fixture else "1/1 accepted",
                    },
                },
                "nextAction": next_action,
                "quickstartReplay": {
                    "phase": "verify",
                    "status": status,
                    "replayCommand": replay_command,
                    "fastVerdict": fast_verdict,
                    "reviewPacket": [
                        "shipguard-verdict.json",
                        "shipguard-verdict.md",
                        "<shipguard-task.json>",
                        "<patch.diff>",
                        "<validation-receipt.json>",
                    ],
                    "nextAction": next_action.get("command"),
                    "successSignal": "Reviewer can replay the same verdict shape and inspect the JSON plus Markdown packet before merging.",
                    "boundary": "Synthetic replay contract only; it does not replace target validation.",
                },
            }
        )
        if unsupported_fixture:
            report["agentClaims"] = ["Notification permission copy is fully verified."]
            report["claimChecks"] = {
                "rejectedClaims": ["fully verified"],
                "rawRejectedClaims": ["fully verified"],
                "claimDecisions": [
                    {
                        "claim": "Notification permission copy is fully verified.",
                        "status": "rejected",
                        "reason": "Broad completion claim lacks covered validation evidence.",
                        "requiredProofPhrases": ["fully verified"],
                    }
                ],
                "requiredProofPhrases": ["fully verified"],
            }
            report["unsupportedClaimReplay"] = {
                "schemaVersion": 1,
                "status": "blocked",
                "unsupportedPhrases": ["fully verified"],
                "unsupportedClaimCount": 1,
                "unsupportedClaims": [
                    {
                        "claim": "Notification permission copy is fully verified.",
                        "status": "rejected",
                        "reason": "Broad completion claim lacks covered validation evidence.",
                        "requiredProofPhrases": ["fully verified"],
                        "resolution": "Revise the claim or attach structured evidence receipts that prove it.",
                    }
                ],
                "rejectedClaimCount": 1,
                "rejectedClaims": [
                    {
                        "claim": "Notification permission copy is fully verified.",
                        "status": "rejected",
                        "reason": "Broad completion claim lacks covered validation evidence.",
                        "requiredProofPhrases": ["fully verified"],
                        "resolution": "Revise the claim or attach structured evidence receipts that prove it.",
                    }
                ],
                "manualProofClaimCount": 0,
                "manualProofClaims": [],
                "replayCommand": report["quickstartReplay"]["replayCommand"],
                "fastVerdict": fast_verdict,
                "reviewPacket": report["quickstartReplay"]["reviewPacket"],
                "nextAction": {
                    "command": next_action["command"],
                    "expectedArtifact": next_action["expectedArtifact"],
                    "successCondition": next_action["successCondition"],
                    "failureMeaning": next_action["failureMeaning"],
                    "resolves": next_action["resolves"],
                },
                "proofBoundary": (
                    "This replay proves ShipGuard did not accept the supplied completion claim against the attached task, diff, "
                    "and evidence receipts. It does not prove the claimed behavior; the claim must be narrowed or backed by "
                    "new structured proof or manual/device proof."
                ),
                "nonClaims": [
                    "An unsupported-claim replay is not product proof.",
                    "A review or blocked verdict is not a merge or release approval.",
                    "Changing the wording is not enough unless the new claim matches the attached evidence.",
                ],
            }
    if source_tool == "shipguard ios design":
        report.update(synthetic_design_report_fields())
    return report


def synthetic_fixture_markdown(candidate: dict[str, Any]) -> str:
    question = materialized_source_question(candidate)
    fixture_type = sanitize_materialized_text(candidate.get("fixtureType")) or "report-quality-actionability-fixture"
    source_tool = sanitize_materialized_text(candidate.get("sourceTool")) or "shipguard ios report-quality"
    lines = [
            "# Synthetic Report-Quality Fixture",
            "",
            "## ShipGuard Evaluation Boundary",
            "",
            "This is a public synthetic ShipGuard fixture. It is not copied from a private app report.",
            "",
            "## Scan Scope",
            "",
            "No private source tree was scanned. The fixture exists to exercise report-quality behavior.",
            "",
            "## Fixture Intent",
            "",
            f"- Type: `{fixture_type}`",
            f"- Source question: {question}",
            "",
    ]
    if source_tool == "shipguard lean debt":
        lines.extend(
            [
                "## Marker Visibility Review",
                "",
                "- All markers visible: `true`",
                "- Visible marker rows: 2 of 2",
                "- Rows with ceiling: 2",
                "- Rows missing ceiling: 0",
                "- Rows with upgrade trigger: 1",
                "- Rows needing upgrade trigger: 1",
                "- Rows with upgrade status: 2",
                "- Omitted state unknown: `false`",
                "- Policy: Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written.",
                "",
                "| Status | Marker | Location | Ceiling | Upgrade Trigger |",
                "| --- | --- | --- | --- | --- |",
                "| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | one query shape | replace when repeated-key support is required |",
                "| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | one release migration window | - |",
                "",
                "## Rot-Risk Review",
                "",
                "- Top risk location: Sources/SyntheticLeanDebt/LegacyPanel.swift:27",
                "- Top risk reason: Missing upgrade trigger means this shortcut can survive beyond its intended window.",
                "- High-risk rows: 0",
                "- Review-risk rows: 1",
                "- Tracked rows: 1",
                "- Missing ceiling rows: 0",
                "- Missing upgrade-trigger rows: 1",
                "- Trigger-watch contract rows: 2",
                "- Missing trigger-watch contracts: 0",
                "- Tracked trigger-watch rows: 1",
                "- Missing trigger definitions: 1",
                "- Omitted by limit: 0",
                "- Omitted risk unknown: `false`",
                "- Top trigger-watch action: Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.",
                "- Coverage boundary: Rot-risk ranking is based on visible shortcut rows. When omittedByLimit is greater than zero, omitted markers may contain higher risk and must be surfaced by rerunning with a narrower scope or extending the ledger limit.",
                "- Policy: Start with the highest-risk shortcut marker before opening source again: missing ceiling first, missing upgrade trigger second, tracked trigger watch third.",
                "",
                "| Rank | Risk | Status | Marker | Location | Rot Reason | Next Action | Proof Guidance |",
                "| ---: | --- | --- | --- | --- | --- | --- | --- |",
                "| 1 | review | needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | Missing upgrade trigger means this shortcut can survive beyond its intended window. | Add an upgrade trigger that tells the maintainer exactly when to replace or delete it. | Name the release, dependency, migration state, or repeated call-site signal that should trigger cleanup. |",
                "| 2 | tracked | tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | Tracked shortcut should be reviewed when its upgrade trigger becomes true. | Watch the upgrade trigger: replace when repeated-key support is required | When the trigger is true, run call-site search plus the smallest focused validation before deleting or replacing it. |",
                "",
                "## Trigger-Watch Contracts",
                "",
                "| Rank | Trigger State | Location | Trigger Condition | Exact Next Action | Check Route | Proof Artifact | Stop Condition |",
                "| ---: | --- | --- | --- | --- | --- | --- | --- |",
                "| 1 | needs-trigger-definition | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | missing upgrade trigger; define a release, dependency, migration, or repeated call-site signal | Add an upgrade trigger that tells the maintainer exactly when to replace or delete it. | Add the upgrade trigger to the marker, rerun shipguard lean debt, and confirm rowsNeedingUpgradeTrigger decreases. | lean-debt.json markerVisibilityReview.visibilityRows row with hasUpgradeTrigger=true and a non-empty upgradeTrigger. | Stop if the trigger cannot be checked later from a release, dependency, migration, or call-site signal. |",
                "| 2 | watch-trigger | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | replace when repeated-key support is required | Check whether this trigger is true: replace when repeated-key support is required | Run call-site search for the shortcut location, then run the smallest focused validation covering the replacement or deletion. | call-site search notes plus focused validation output attached beside lean-debt.json. | Stop if search or validation shows the shortcut is still active product behavior. |",
                "",
                "## Shortcut Ledger",
                "",
                "- Markers: 2; missing upgrade trigger: 1",
                "",
                "| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |",
                "| --- | --- | --- | --- | --- | --- |",
                "| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | use the native query parser while this bridge handles one query shape. ceiling: one query shape. upgrade: replace when repeated-key support is required. | one query shape | replace when repeated-key support is required |",
                "| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | keep the temporary compatibility panel during migration. ceiling: one release migration window. | one release migration window | - |",
                "",
                "## Current Repo Boundary",
                "",
                "- Shortcut markers are current-repo evidence only.",
                "- Do not claim benchmark, line, token, cost, or time savings from marker counts.",
                "",
                "## Benchmark Savings Boundary",
                "",
                "- Per-repo savings claim: `not-computed`",
                "- Evidence type: `shortcut-ledger-only`",
                "- Reason: Lean Debt counts intentional shortcut markers and missing triggers; it has no untreated baseline for current-repo line, token, cost, or time savings.",
                "- Do not claim current-repo line, token, cost, or time savings from shortcut marker counts.",
                "- Do not treat shortcut marker counts as benchmark savings.",
                "- Benchmark route: `shipguard lean gain --path <repo> --out <lean-gain-out> --shipguard-eval --shareable`",
                "- Benchmark artifact: lean-gain.json and lean-gain.md",
                "- Boundary: Benchmark direction is separate from this shortcut-ledger evidence and still does not measure this repo without a matched baseline.",
                "",
            ]
        )
    if source_tool == "shipguard prepare":
        lines.extend(
            [
                "## Quickstart Replay",
                "",
                "- Phase: `prepare`",
                "- First useful verdict: `shipguard verify --task <task-dir>/shipguard-task.json --diff <patch.diff> --evidence <validation-receipt.json> --claim <scoped-claim> --out <verdict-dir>`",
                "- Proof inputs: `<patch.diff>`, `<validation-receipt.json>`, `<scoped-claim>`",
                "- Success signal: shipguard-verdict.json returns pass, review, blocked, or incomplete with one nextAction.",
                "- Connects: goal, riskClassification, authorizedFiles, protectedBoundaries, validationContract, agentClaims, verdict, nextAction",
                "- Boundary: Synthetic replay contract only; it does not authorize target-app work.",
                "",
            ]
        )
        if is_notification_scope_question(question) or is_notification_proof_lane_question(question):
            lines.extend(synthetic_notification_scope_markdown_lines())
    if source_tool == "shipguard verify":
        unsupported_fixture = "unsupported completion claim" in normalized_question_text(question)
        replay_command = (
            "shipguard verify --task <shipguard-task.json> --diff <patch.diff> --evidence <validation-receipt.json> "
            "--claim 'Notification permission copy is fully verified.' --out <verdict-dir>"
            if unsupported_fixture
            else "shipguard verify --task <shipguard-task.json> --diff <patch.diff> --evidence <validation-receipt.json> "
            "--claim <scoped-claim> --out <verdict-dir>"
        )
        fast_verdict = (
            "ShipGuard Proof Report: blocked. Validation 1/1 covered; claims 0/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable."
            if unsupported_fixture
            else "ShipGuard Proof Report: pass. Validation 1/1 covered; claims 1/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable."
        )
        next_action = (
            "Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify."
            if unsupported_fixture
            else "Attach shipguard-verdict.json and the evidence receipts to the review."
        )
        lines.extend(
            [
                "## Quickstart Replay",
                "",
                "- Phase: `verify`",
                f"- Replay command: `{replay_command}`",
                f"- Fast verdict: `{fast_verdict}`",
                "- Review packet: `shipguard-verdict.json`, `shipguard-verdict.md`, `<shipguard-task.json>`, `<patch.diff>`, `<validation-receipt.json>`",
                f"- Next action: {next_action}",
                "- Boundary: Synthetic replay contract only; it does not replace target validation.",
                "",
            ]
        )
        if unsupported_fixture:
            lines.extend(
                [
                    "## Unsupported Claim Replay",
                    "",
                    "- Status: `blocked`",
                    "- Unsupported phrases: `fully verified`",
                    f"- Replay command: `{replay_command}`",
                    "- Next action: `Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify.`",
                    "- Expected artifact: updated claim or structured evidence receipt",
                    "- Success condition: No unsupported completion claim remains",
                    "- Boundary: This replay proves ShipGuard did not accept the supplied completion claim against the attached task, diff, and evidence receipts. It does not prove the claimed behavior; the claim must be narrowed or backed by new structured proof or manual/device proof.",
                    "",
                    "| Status | Claim | Reason | Resolution |",
                    "| --- | --- | --- | --- |",
                    "| rejected | Notification permission copy is fully verified. | Broad completion claim lacks covered validation evidence. | Revise the claim or attach structured evidence receipts that prove it. |",
                    "",
                    "## Non-Claims",
                    "",
                    "- An unsupported-claim replay is not product proof.",
                    "- A review or blocked verdict is not a merge or release approval.",
                    "- Changing the wording is not enough unless the new claim matches the attached evidence.",
                    "",
                ]
            )
    if source_tool == "shipguard v4 stable-publication":
        lines.extend(
            [
                "## Evidence Packet",
                "",
                "- Packet status: `pass`",
                "- Required evidence passed: `10/10`",
                "- First blocking gate: `none`",
                "",
                "| Evidence | Status |",
                "| --- | --- |",
                "| `github-release-metadata` | `pass` |",
                "| `release-notes` | `pass` |",
                "| `launchkey-candidate-packet` | `pass` |",
                "| `downloaded-release-assets` | `pass` |",
                "| `post-release-consumer-proof` | `pass` |",
                "| `public-release-freshness` | `pass` |",
                "| `release-version-coherence` | `pass` |",
                "| `release-asset-coherence` | `pass` |",
                "| `independent-adoption-evidence` | `pass` |",
                "| `final-security-review-evidence` | `pass` |",
                "",
                "## Closure Checklist",
                "",
                "- Checklist status: `pass`",
                "- Remaining blockers: `0`",
                "- No hidden lower-order blockers: `True`",
                "",
                "| Rank | Evidence | Status | First | Next command | Proof boundary |",
                "| --- | --- | --- | --- | --- | --- |",
                "| `none` | `none` | `pass` | `False` | `not-needed` | Every stable-publication gate passed. |",
                "",
                "## Evidence Templates",
                "",
                "- Draft-only templates: `True`",
                "",
                "| Template | Exists | Copy command |",
                "| --- | --- | --- |",
                "| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |",
                "| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |",
                "",
                "## Evidence Starter Kit",
                "",
                "- Directory: `stable-publication-evidence-kit`",
                "- Draft-only: `True`",
                "",
                "## External Evidence Intake Checklist",
                "",
                "| Evidence | Accepted classes | Required fields | Redaction boundary |",
                "| --- | --- | --- | --- |",
                "| `independent-adoption-evidence` | public-external, private-redacted-external | actorRelationship, privateDataRedacted, commands, artifacts, outcome, nonClaims | privateDataRedacted must be `True` |",
                "| `final-security-review-evidence` | public-security-review, private-redacted-security-review | scope, methodology, findingsSummary, privateDataRedacted, nonClaims | privateDataRedacted must be `True` |",
                "",
                "## Adoption Evidence Checklist",
                "",
                "- Accepted evidence classes: public-external, private-redacted-external",
                "- Required actor relationship: `independent`",
                "- Required proof fields: commands, artifacts, outcome, nonClaims",
                "- Artifact expectations: install transcript or command log, generated ShipGuard report or validation output",
                "- Redaction boundaries: privateDataRedacted must be true",
                "- Weak-signal exclusions: GitHub stars, download counts, maintainer-only private app runs",
                "- Pass decision: Pass only when a non-maintainer actor supplies redacted/public command and artifact evidence for real ShipGuard use.",
                "",
                "## Security Review Evidence Checklist",
                "",
                "- Required review surfaces: cli, plugin, github-actions, release-proof, package-install, redaction-privacy",
                "- Severity threshold: `criticalOpen=0`, `highOpen=0`",
                "- Required evidence fields: reviewerRelationship, scope, methodology, commands, artifacts, findingsSummary, nonClaims",
                "- Redaction boundaries: privateDataRedacted must be true",
                "- Pass decision: Pass only when every required surface is reviewed and criticalOpen plus highOpen are both 0.",
                "",
                "## Release Notes Authoring Kit",
                "",
                "- Directory: `stable-publication-release-notes`",
                "- Draft-only: `True`",
                "- Public release edit command: `gh release edit v0.0.0 --repo example/shipguard --notes-file stable-publication-release-notes/draft-release-notes.md`",
                "- Missing topics: `none`",
                "",
                "## Launch Relay Drafts",
                "",
                "- Directory: `stable-publication-launch-relay`",
                "- Draft-only: `True`",
                "- Approval required: `True`",
                "- Public posting allowed: `False`",
                "- Computer-use may post: `False`",
                "- Status: `ready-to-stage`",
                "",
                "| File | Purpose |",
                "| --- | --- |",
                "| `stable-publication-launch-relay/README.md` | Synthetic approval boundary. |",
                "| `stable-publication-launch-relay/launch-relay-checklist.json` | Synthetic checklist. |",
                "| `stable-publication-launch-relay/product-hunt-draft.md` | Synthetic Product Hunt draft. |",
                "| `stable-publication-launch-relay/reddit-r-shipguard-draft.md` | Synthetic Reddit draft. |",
                "| `stable-publication-launch-relay/x-thread-draft.md` | Synthetic X draft. |",
                "| `stable-publication-launch-relay/hacker-news-draft.md` | Synthetic HN draft. |",
                "",
                "Approval boundary:",
                "",
                "Public posting, publishing, submission, or account-visible external actions require explicit human approval for that exact launch run.",
                "",
                "## Public Release Delta",
                "",
                "- Status: `pass`",
                "- Source version: `0.0.0`",
                "- Selected release: `0.0.0`",
                "- Latest GitHub release: `0.0.0`",
                "- Package version: `0.0.0`",
                "- Unpublished local delta: `False`",
                "- Stable-v4 claim covers selected public release: `True`",
                "- Stable-v4 claim covers local checkout: `True`",
                "- Unpublished local code counts as released: `False`",
                "",
                "| Comparison | Value |",
                "| --- | --- |",
                "| `sourceVersionMatchesRequestedRelease` | `True` |",
                "| `selectedReleaseMatchesLatestGitHubRelease` | `True` |",
                "| `releaseManifestVersionMatchesRequestedRelease` | `True` |",
                "| `packageAssetsVersionMatchesRequestedRelease` | `True` |",
                "| `publicTagTargetMatchesReleaseManifestCommit` | `True` |",
                "| `releaseAssetCoherencePassed` | `True` |",
                "| `releaseVersionCoherencePassed` | `True` |",
                "| `localHeadMatchesSelectedPublicReleaseCommit` | `True` |",
                "| `localMainMatchesSelectedPublicReleaseCommit` | `True` |",
                "",
                "## Release Visibility Handoff",
                "",
                "- Status: `pass`",
                "- Primary decision: `announce-current-public-release`",
                "- Latest GitHub release: `0.0.0`",
                "- Selected release tag: `v0.0.0`",
                "- Unpublished local delta: `False`",
                "- Current public release can be announced: `True`",
                "- Local main can be announced: `True`",
                "- Unpublished local code counts as released: `False`",
                "",
                "| Action | Required | Status | Command purpose | Next command | Proof after action |",
                "| --- | ---: | --- | --- | --- | --- |",
                "| `publish-new-github-release` | `False` | `pass` | `not-needed` | `not-needed` | `not-needed` |",
                "| `update-release-notes` | `False` | `pass` | `not-needed` | `not-needed` | `not-needed` |",
                "| `attach-launchkey-candidate-proof` | `False` | `pass` | `not-needed` | `not-needed` | `not-needed` |",
                "| `update-release-assets` | `False` | `pass` | `not-needed` | `not-needed` | `not-needed` |",
                "| `attach-adoption-security-evidence` | `False` | `pass` | `not-needed` | `not-needed` | `not-needed` |",
                "| `keep-current-public-release-unchanged` | `True` | `pass` | `final-claim-review` | `./bin/shipguard value-gauntlet --path . --out <gauntlet-dir>` | `not-needed` |",
                "",
                "## Final Stable V4 Claim Packet",
                "",
                "- Claim decision: `allowed`",
                "- Stable v4 release: `True`",
                "- Public evidence closure: `pass`",
                "- Public posting requires explicit approval: `True`",
                "- Computer-use may post: `False`",
                "- Source-only proof counts as stable v4: `False`",
                "- Fixture proof counts as stable v4: `False`",
                "- GitHub downloads count as adoption evidence: `False`",
                "",
                "Copy-ready claim:",
                "",
                "ShipGuard 0.0.0 has passed stable-v4 publication proof.",
                "",
                "| Evidence | Status |",
                "| --- | --- |",
                "| `github-release-metadata` | `pass` |",
                "| `release-notes` | `pass` |",
                "| `launchkey-candidate-packet` | `pass` |",
                "| `downloaded-release-assets` | `pass` |",
                "| `post-release-consumer-proof` | `pass` |",
                "| `public-release-freshness` | `pass` |",
                "| `release-version-coherence` | `pass` |",
                "| `release-asset-coherence` | `pass` |",
                "| `independent-adoption-evidence` | `pass` |",
                "| `final-security-review-evidence` | `pass` |",
                "",
                "Blocked claim wording:",
                "",
                "- OpenAI marketplace acceptance is proven.",
                "- Public launch posts were published or submitted.",
                "- GitHub stars, forks, or downloads prove independent adoption.",
                "",
            ]
        )
    if source_tool == "shipguard lean gain":
        lines.extend(
            [
                "## Benchmark Scoreboard",
                "",
                "- Benchmark: Synthetic Lean Gain public benchmark",
                "- Scope: public benchmark, not this repository",
                "- Baseline: same agent without the lean-code ruleset",
                "- Method: paired public fixture tasks with and without the lean-code ruleset",
                "",
                "| Metric | Baseline | Lean-code result | Change |",
                "| --- | --- | --- | --- |",
                "| Lines of code | 100% | 46% | -54% |",
                "| Tokens | 100% | 78% | -22% |",
                "| Cost | 100% | 80% | -20% |",
                "| Time | 100% | 73% | -27% |",
                "| Safety | 100% | 100% | 100% |",
                "",
                "## Honesty Boundary",
                "",
                "- Per-repo savings claim: `not-computed`",
                "- Reason: There is no untreated baseline for this repository; ShipGuard cannot subtract code, cost, or time that was never produced.",
                "- Do not claim current-repo line, token, cost, or time savings without a matched baseline.",
                "",
                "## Current Repo Signals",
                "",
                "- Lean audit findings show possible cuttable surfaces.",
                "- Lean review findings show current-diff delete or simplify opportunities.",
                "- Lean debt marker counts show intentional shortcuts that still need ceilings and upgrade triggers.",
                "",
                "## Current Repo Evidence Routes",
                "",
                "| Route | Command | Artifact | Answers | Boundary |",
                "| --- | --- | --- | --- | --- |",
                "| `lean-audit` | `shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable` | lean-audit.json and lean-audit.md | Which repo surfaces may be deleted, simplified, kept, or proof-blocked? | Source-scan evidence only; it does not prove line, token, cost, or time savings. Do not treat audit findings as benchmark savings. |",
                "| `lean-review` | `shipguard lean review --path <repo> --diff <diff-file> --out <lean-review-out> --mode full --shipguard-eval --shareable` | lean-review.json and lean-review.md | Which current-diff changes can be deleted, simplified, kept, or proof-blocked before merge? | Diff-scoped evidence only; it does not prove whole-repo or benchmark savings. Do not treat a smaller diff as measured token, cost, or time savings without a matched baseline. |",
                "| `lean-debt` | `shipguard lean debt --path <repo> --out <lean-debt-out> --shipguard-eval --shareable` | lean-debt.json and lean-debt.md | Which intentional shortcuts have ceilings, upgrade triggers, and missing-trigger debt? | Shortcut-ledger evidence only; it does not prove benchmark or per-repo savings. Do not present shortcut counts as code-size savings. |",
                "",
            ]
        )
    if source_tool == "shipguard lean review":
        lines.extend(
            [
                "## Lean Mode",
                "",
                "- Mode: `full`",
                "- Intent: Use the proof ladder before adding or deleting code.",
                "- First action bias: `proof-ladder`",
                "- Policy: Use full mode for current-diff review when proof boundaries matter.",
                "",
                "## Mode Bias Review",
                "",
                "- Selected mode: `full`",
                "- Selected first action bias: `proof-ladder`",
                "- Selected priority order: `deleteList -> simplifyFirst -> blockedByProof`",
                "- Expected first source: `deleteList`",
                "- Top action matches selected bias: `true`",
                "",
                "| Mode | First Action Bias | Priority Order | First Available Source |",
                "| --- | --- | --- | --- |",
                "| `lite` | `suggestion-first` | `simplifyFirst -> deleteList -> blockedByProof` | `simplifyFirst` |",
                "| `full` | `proof-ladder` | `deleteList -> simplifyFirst -> blockedByProof` | `deleteList` |",
                "| `ultra` | `delete-first` | `deleteList -> blockedByProof -> simplifyFirst` | `deleteList` |",
                "",
                "## Current Diff Decision Map",
                "",
                "- Scope: `current-diff-only`",
                "- Diff: `synthetic-current-change.diff`",
                "- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.",
                "- Whole-repo fallback: `shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable`",
                "- Decision rows: 9; delete: 1; simplify: 1; keep: 2; proof-blocked: 2; clean files: 3",
                "",
                "| File | Decision | Added | Removed | Rules | First Experiment | Validation | Stop Condition |",
                "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
                "| Sources/SyntheticLeanReview/FormatterShim.swift | `delete` | 6 | 0 | thin-wrapper-diff-review | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |",
                "| Sources/SyntheticLeanReview/QueryBuilder.swift | `simplify` | 8 | 1 | stdlib-url-params-diff | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |",
                "| Sources/SyntheticLeanReview/PermissionGate.swift | `keep` | 5 | 0 | do-not-cut-safety-diff-without-proof | Treat this as a keep-with-proof boundary before any deletion or simplification. | Run focused permission-state behavior proof before changing this branch. | Stop if the only evidence is less-code pressure without behavior proof. |",
                "| Sources/SyntheticLeanReview/PluginHostAdapter.swift | `keep` | 5 | 0 | host-adapter-boundary-diff | Treat this as a host-adapter keep boundary until protocol or runtime proof shows it is redundant. | Run or attach the smallest plugin, MCP, preview, or runtime proof that covers the adapter boundary. | Stop if the only evidence is less-code pressure against a product-surface adapter. |",
                "| Sources/SyntheticLeanReview/RuleRouter.swift | `proof-blocked` | 7 | 0 | one-runnable-check-missing-diff | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |",
                "| Sources/SyntheticLeanReview/SensorSampler.swift | `proof-blocked` | 6 | 0 | hardware-calibration-missing-diff | Attach calibration, timing, or real-device evidence before removing the sensor tuning boundary. | Run or attach the smallest hardware, simulator, or timing proof that covers the changed sampling behavior. | Stop if the only evidence is source-level less-code pressure without physical-world proof. |",
                "| Sources/SyntheticLeanReview/SelectionPolicy.swift | `clean` | 6 | 0 | one-runnable-check-signal-present-diff | Review the matching same-diff test before adding any duplicate test ceremony. | Run Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift or the equivalent focused lane. | Stop if the changed same-diff test already proves the new branch and no Lean cleanup remains. |",
                "| Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift | `clean` | 5 | 0 | - | Run the changed focused test and confirm it covers the changed selection branch. | Run the focused test lane before broader validation. | Stop if the test is unrelated to the changed logic. |",
                "| Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift | `clean` | 4 | 0 | - | Keep this unrelated smoke test visible as evidence that proof signals are not global. | Run only if this separate smoke path matters to the task. | Stop if a maintainer tries to count this unrelated test as proof for a different changed file. |",
                "",
                "Non-claims:",
                "- Does not prove whole-repo inventory coverage.",
                "- Does not prove benchmark savings, token savings, cost savings, or time savings.",
                "- Does not authorize private target-app edits from ShipGuard product-QA runs.",
                "",
                "## Behavior Gates",
                "",
                "- `oneRunnableCheck`: enforced-in-lean-review - Non-trivial new logic should leave one smallest runnable check.",
                "- `hardwareCalibration`: available - Hardware and physical devices need calibration proof before simplification.",
                "- `requestedExplanation`: policy - Explicitly requested reports are not clutter.",
                "- `adapterBoundary`: available - Thin host adapters can be the product surface.",
                "- `gainHonesty`: available-in-lean-gain - Benchmark impact is separate from current-repo evidence.",
                "",
                "## Proof Signal Calibration",
                "",
                "- Same-diff proof status: `present`",
                "- Proof signals: 2",
                "- Code findings covered by same-diff proof: 1",
                "- Missing runnable-check findings: 1",
                "- Policy: Lean Review should distinguish no proof signal from same-diff proof signal. Same-diff tests still need human relevance review, but they should not produce duplicate missing-check ceremony.",
                "",
                "| Kind | Location | Added Lines | Signal |",
                "| --- | --- | ---: | --- |",
                "| test-file | Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9 | 5 | func testPrimaryOptionWins() { XCTAssertEqual(policy.pick(primary), .preferred(primary.id)) } |",
                "| test-file | Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7 | 4 | func testUnrelatedSmokePath() { XCTAssertTrue(smokePath.isEnabled) } |",
                "",
                "## Runnable Check Review",
                "",
                "- Missing proof findings: 1",
                "- Same-diff proof findings: 1",
                "- Same-diff proof signals: 2",
                "- Duplicate ceremony avoided: 1",
                "- Policy: Non-trivial branch, loop, parser, and collection logic should leave one smallest runnable check.",
                "- Non-ceremony boundary: If the same diff already changes a focused test, XCTest, assertion, or explicit check signal, Lean Review records that same-diff proof signal instead of asking for duplicate test ceremony. The maintainer still needs to review relevance and run the focused check.",
                "",
                "### Missing Runnable Checks",
                "",
                "| Location | Recommendation | Proof |",
                "| --- | --- | --- |",
                "| Sources/SyntheticLeanReview/RuleRouter.swift:18 | Leave one smallest runnable check for the new routing branch instead of treating tests as optional ceremony. | Add one focused route-selection check or point to the changed test that covers this branch before merge. |",
                "",
                "### Same-Diff Proof Signals",
                "",
                "| Location | Recommendation | Proof Review |",
                "| --- | --- | --- |",
                "| Sources/SyntheticLeanReview/SelectionPolicy.swift:27 | Do not add duplicate test ceremony before checking whether the same-diff proof signal already covers this logic. | Review Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift, then run the focused test before merge. |",
                "",
                "## Proof Signal Matching",
                "",
                "- Changed code files: 7",
                "- Non-trivial logic files: 2",
                "- Matched same-diff proof files: 1",
                "- Missing proof files: 1",
                "- Unmatched proof signals: 1",
                "- Policy: Same-diff proof is file-scoped. A changed test or assertion satisfies a changed code file only when ShipGuard can match it by same file, path stem, or meaningful path tokens.",
                "- Non-global proof boundary: Unrelated or unmatched proof signals are listed separately and do not satisfy missing proof for other changed files; same-diff proof is not treated as global proof.",
                "",
                "| File | Decision | Matched Proof Signals |",
                "| --- | --- | ---: |",
                "| Sources/SyntheticLeanReview/RuleRouter.swift | `missing-proof` | 0 |",
                "| Sources/SyntheticLeanReview/SelectionPolicy.swift | `matched-same-diff-proof` | 1 |",
                "",
                "### Unmatched Proof Signals",
                "",
                "| Location | Kind | Signal |",
                "| --- | --- | --- |",
                "| Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7 | test-file | func testUnrelatedSmokePath() { XCTAssertTrue(smokePath.isEnabled) } |",
                "",
                "## Hardware And Host Boundary Review",
                "",
                "- Hardware calibration findings: 1",
                "- Host adapter boundary findings: 1",
                "- False less-code pressure blocked: 2",
                "- Policy: Lean Review should block false less-code pressure around physical-world behavior and product-surface host adapters. Hardware needs calibration proof; host adapters need call-site or protocol proof before they are treated as removable wrappers.",
                "- Hardware calibration policy: Hardware, sensors, clocks, and physical devices need calibration, timing, or real-device evidence before simplification removes tuning boundaries.",
                "- Host adapter policy: Thin plugin, MCP, preview, simulator, and platform host adapters can be the product boundary. Keep them until call-site, protocol, or runtime proof shows the adapter is redundant.",
                "",
                "### Hardware Calibration Proof",
                "",
                "| Location | Recommendation | Proof |",
                "| --- | --- | --- |",
                "| Sources/SyntheticLeanReview/SensorSampler.swift:33 | Keep a minimal calibration or tuning boundary when code touches real hardware or physical-device behavior. | Attach real-device, sensor, timing, or calibration evidence before simplifying the physical-world edge case away. |",
                "",
                "### Host Adapter Boundaries",
                "",
                "| Location | Recommendation | Proof |",
                "| --- | --- | --- |",
                "| Sources/SyntheticLeanReview/PluginHostAdapter.swift:12 | Keep this host, plugin, MCP, preview, simulator, or platform adapter until call-site or protocol proof shows it is redundant. | Attach call-site, protocol, plugin, MCP, preview, or runtime proof before simplifying the adapter boundary. |",
                "",
                "## Safety Boundary Review",
                "",
                "- Safety-boundary findings: 1",
                "- False deletion pressure blocked: 1",
                "- Keep safety-boundary files: 1",
                "- Policy: Lean Review must keep safety, trust, permission, accessibility, validation, data-loss, and security boundaries out of automatic deletion. Less-code pressure is only allowed after focused behavior proof.",
                "- Automatic deletion boundary: A safety-boundary row is a keep-with-proof decision, even when the same file also contains cleanup pressure.",
                "",
                "### Keep With Proof Boundaries",
                "",
                "| Location | Recommendation | Proof |",
                "| --- | --- | --- |",
                "| Sources/SyntheticLeanReview/PermissionGate.swift:31 | Less code is not the goal in this file until behavior proof exists. | Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior. |",
                "",
                "## Precision Ledger",
                "",
                "- Delete candidates: 1; simplify candidates: 1; keep boundaries: 2; proof-blocked candidates: 2; action groups: 4",
                "",
                "### Grouped Action Plan",
                "",
                "| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |",
                "| ---: | --- | --- | ---: | --- | --- | --- | --- |",
                "| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |",
                "| 2 | simplify | `stdlib-url-params-diff` | 1 | Sources/SyntheticLeanReview/QueryBuilder.swift:22 | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |",
                "| 3 | proof-blocked | `one-runnable-check-missing-diff` | 1 | Sources/SyntheticLeanReview/RuleRouter.swift:18 | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |",
                "| 4 | proof-blocked | `hardware-calibration-missing-diff` | 1 | Sources/SyntheticLeanReview/SensorSampler.swift:33 | Attach calibration, timing, or real-device evidence before removing the sensor tuning boundary. | Run or attach the smallest hardware, simulator, or timing proof that covers the changed sampling behavior. | Stop if the only evidence is source-level less-code pressure without physical-world proof. |",
                "",
            ]
        )
    if source_tool == "shipguard ios performance":
        lines.extend(
            [
                "## Runtime Evidence Boundary",
                "",
                "- Evidence: `source heuristic`",
                "- Confidence: `medium`",
                "- Runtime proof: `missing`",
                "- Blocking: `no`",
                "- Interpretation: Synthetic source-only performance fixture; it does not prove actual CPU, GPU, memory, energy, hitch, FPS, or frame-rate problems.",
                "- Promotion rule: Promote only after a public fixture or same-route runtime proof confirms the issue shape.",
                "",
                "Required runtime proof:",
                "- Same-route Simulator trace, sample, or log evidence for local-only claims.",
                "- Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.",
                "",
                "## Evidence Promotion Contract",
                "",
                "- Source evidence: `source heuristic`",
                "- Promotion status: `missing-runtime-proof`",
                "- First candidate rule: `swiftui-repeat-forever-animation`",
                "- Owner: `developer`",
                "- Manual proof: Run the same local sample or trace before and after the single animation gate; attach device Instruments proof before claiming FPS, ProMotion, battery, thermal, or hardware-display improvement.",
                "- Expected artifact: Same-route before/after trace, sample, or screen recording for the first swiftui-repeat-forever-animation experiment.",
                "- Success condition: The same-route proof shows less constant motion work, Reduce Motion or visibility behavior remains correct, and no broader performance claim is made without device proof.",
                "- Failure meaning: The source suspicion remains unpromoted; keep it as review guidance and do not broaden scanner heuristics or target-app remediation.",
                "",
            ]
        )
        if fixture_type == "ios-performance-report-quality-fixture":
            lines.extend(
                [
                    "## Grouped Next Actions",
                    "",
                    "| Rule | Count | Severity | First experiment | Validation route | Stop condition |",
                    "| --- | ---: | --- | --- | --- | --- |",
                    (
                        "| `swiftui-repeat-forever-animation` | 4 | review | Disable or gate one decorative repeatForever animation behind Reduce Motion and active-screen visibility, then compare an at-rest screen recording plus a same-route sample. | Run the same local sample or trace before and after the single gate; use device Instruments before claiming FPS, ProMotion, battery, or thermal improvement. | Stop after the first gated animation unless the same-route proof shows a measurable improvement and the UI still communicates the intended state. |"
                    ),
                    "",
                    "## Top Findings",
                    "",
                    "| Severity | Rule | Location | Why severity | Why it matters |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for line in (12, 28, 44, 60):
                lines.append(
                    (
                        "| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:"
                        f"{line}` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |"
                    )
                )
            lines.extend(
                [
                    "",
                    "## Proof Boundaries",
                    "",
                    "| Severity | Rule | Codex local proof | Manual/device proof |",
                    "| --- | --- | --- | --- |",
                    (
                        "| review | `swiftui-repeat-forever-animation` | Record the synthetic screen at rest and during one interaction, then compare samples after gating the animation. | Use physical-device Instruments before making FPS, ProMotion, thermal, battery, or hardware-display claims. |"
                    ),
                    "",
                ]
            )
    if source_tool == "shipguard ios design":
        lines.extend(
            [
                "## App Type Signals",
                "",
                "| App Type | Score |",
                "| --- | ---: |",
                "| education | 25 |",
                "| utility | 4 |",
                "",
                "Top signals:",
                "- `lesson` -> education (12) in Sources/SyntheticDesignFixture/LearningFlow.swift",
                "- `learn` -> education (8) in Sources/SyntheticDesignFixture/LearningFlow.swift",
                "",
                "## Design Tailoring Contract",
                "",
                "- Tailored for: `education`",
                "- Guidance profile: `learning-progress`",
                "- Universal defaults rejected: `true`",
                "- Source signals: lesson->education, learn->education, progress->education",
                "- Motion stance: production-polish",
                "- Haptics tone: encouraging, milestone-aware, and interruption-sparse",
                "- Visual density stance: allow expressive hierarchy with proof",
                "- Copy tone stance: specific to the app task and audience",
                "- Risk: Generic utility restraint can make learning feedback feel flat, while generic game delight can distract from comprehension.",
                "- Owner: `developer`",
                "- Manual proof: Review one synthetic learning flow and confirm motion, haptics, visual density, and copy guidance match the education profile rather than a universal design checklist.",
                "- Expected artifact: A same-flow screenshot or preview receipt plus one note mapping the learning-progress profile to source signals.",
                "- Success condition: The report explains why learning-progress is the right profile for education and avoids utility-only advice.",
                "- Failure meaning: The design report remains an inventory, not an app-type-specific design QA recommendation.",
                "",
                "## Professional Design Principle Vocabulary",
                "",
                "- Source: ShipGuard native design QA vocabulary inspired by professional visual-design principles.",
                "",
                "| Principle | Review question |",
                "| --- | --- |",
                "| contrast | Can lesson status and primary actions be distinguished without decorative color dependence? |",
                "| hierarchy | Does the learning flow show lesson goal, current task, and next step in that order? |",
                "| alignment | Do lesson cards, progress labels, and controls share a deliberate grid? |",
                "| proximity | Are related learning controls grouped and recovery actions separated? |",
                "| repetition | Are cards, buttons, and success states reused across the learning flow? |",
                "| balance | Is progress feedback visually weighted without overwhelming the lesson content? |",
                "| white space | Does spacing give comprehension room without wasting mobile screen density? |",
                "| unity | Do color, type, symbols, copy, motion, and haptics feel like one education product? |",
                "| motion | Does motion clarify progress or recovery while respecting Reduce Motion? |",
                "| haptics | Are haptics milestone-aware, sparse, and left unclaimed until device proof exists? |",
                "| preview proof | Are visual claims backed by iPhone preview or Devspace evidence? |",
                "| app-type fit | Is the guidance tuned for education comprehension instead of generic utility polish? |",
                "",
                "## Findings",
                "",
                "| Severity | Category | Rule | Finding | Recommendation | Proof |",
                "| --- | --- | --- | --- | --- | --- |",
                "| review | Design DNA | `design-coherence-target-work-boundary` | Design coherence finding must not become target-app work | Improve ShipGuard report-quality rules or public fixtures before using this as target-app implementation guidance. | Review the Design Tailoring Contract and Design Coherence Boundary, then run report-quality on the synthetic fixture. |",
                "",
                "## Design Coherence Boundary",
                "",
                "- Purpose: Keep design-system coherence findings as ShipGuard product-QA evidence until target-app work is separately authorized.",
                "- Source inventory app type: `education`",
                "- Coherence risks: 1",
                "- Inventory is not remediation: `true`",
                "- Coherence risk is not target task: `true`",
                "- ShipGuard action is public fixture or rule: `true`",
                "- App work requires separate authorization: `true`",
                "- Target remediation status: `not-authorized-from-this-run`",
                "",
                "ShipGuard next action:",
                "- Owner: `ShipGuard maintainer`",
                "- Kind: `public-fixture-or-report-rule`",
                "- Source question: Did it separate design-system coherence findings from target-app implementation work?",
                "- Expected artifact: A public synthetic report-quality fixture that checks the coherence boundary without private app data.",
                "- Success condition: Report-quality fails if a design report turns coherence inventory into target-app implementation work or hides the authorization boundary.",
                "- Failure meaning: Private app design evidence can still become unreviewed app remediation advice instead of ShipGuard product QA.",
                "",
                "App work authorization:",
                "- Status: `not-authorized-from-this-run`",
                "- Requires explicit request: `true`",
                "",
                "Proof boundary:",
                "- Local proof: Run shipguard ios report-quality on this synthetic design fixture.",
                "- Manual proof: A human may later authorize target-app design work, but this fixture does not authorize it.",
                "- Expected artifact: ios-report-quality.json plus fixture coverage for design coherence boundaries.",
                "",
                "## Preview And Devspace",
                "",
                "- No preview directory was supplied.",
                "- Run `shipguard ios preview --out /tmp/ios-shipguard-preview` for a phone-shaped visual proof loop.",
                "- Run `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN` when ChatGPT should plan from the preview widget.",
                "- ChatGPT model selection happens in ChatGPT; ShipGuard exposes the MCP/App bridge but cannot force a model.",
                "",
            ]
        )
    return "\n".join(lines)


def fixture_readme(candidate: dict[str, Any]) -> str:
    candidate_id = materialized_candidate_id(candidate)
    validation = candidate.get("validationCommands") if isinstance(candidate.get("validationCommands"), list) else []
    promotion = promotion_metadata(candidate_id)
    lines = [
        f"# {candidate_id}",
        "",
        "Public synthetic fixture starter generated by `shipguard ios report-quality --write-fixture-candidates`.",
        "",
        "## Boundary",
        "",
        "- Synthetic report shape only.",
        "- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.",
        "- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.",
        "",
        "## Files",
        "",
        "- `fixture-candidate.json`: public-safe candidate metadata.",
        "- `fixture-report.json`: minimal synthetic source report.",
        "- `fixture-report.md`: paired Markdown report for report-quality checks.",
        "",
        "## Validation",
        "",
    ]
    if validation:
        lines.extend(f"- `{command}`" for command in validation)
    else:
        lines.append("- `./bin/shipguard ios report-quality --reports <fixture-dir> --out <quality-dir> --shareable`")
    lines.extend(
        [
            "",
            "## Promotion",
            "",
            f"- Suggested repo path: `{promotion['suggestedFixturePath']}`",
            "- Promotion is explicit maintainer work; generated candidates are not auto-copied into the repo.",
            "",
            "Copy commands:",
            "",
        ]
    )
    lines.extend(f"- `{command}`" for command in promotion["copyCommands"])
    lines.extend(["", "Promotion validation:", ""])
    lines.extend(f"- `{command}`" for command in promotion["validationCommands"])
    lines.extend(["", "Review checklist:", ""])
    lines.extend(f"- {item}" for item in promotion["reviewChecklist"])
    lines.append("")
    return "\n".join(lines)


def render_promotion_markdown(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Fixture Promotion Guide",
        "",
        "These generated fixtures are public-safe starters. Promotion remains explicit maintainer work; ShipGuard does not auto-copy candidates into the repository.",
        "",
        "## Candidates",
        "",
        "| Candidate | Suggested Repo Path |",
        "| --- | --- |",
    ]
    for item in entries:
        promotion = item.get("promotion") or {}
        lines.append(
            f"| `{item.get('candidateId') or 'unknown'}` | `{promotion.get('suggestedFixturePath') or '-'}` |"
        )
    lines.extend(["", "## Copy Commands", ""])
    for item in entries:
        promotion = item.get("promotion") or {}
        lines.append(f"### {item.get('candidateId') or 'unknown'}")
        lines.append("")
        for command in promotion.get("copyCommands") or []:
            lines.append(f"- `{command}`")
        lines.append("")
    lines.extend(["## Validation", ""])
    seen_commands: set[str] = set()
    for item in entries:
        promotion = item.get("promotion") or {}
        for command in promotion.get("validationCommands") or []:
            if command in seen_commands:
                continue
            seen_commands.add(command)
            lines.append(f"- `{command}`")
    lines.extend(["", "## Review Checklist", ""])
    checklist: list[str] = []
    for item in entries:
        promotion = item.get("promotion") or {}
        for check in promotion.get("reviewChecklist") or []:
            if check not in checklist:
                checklist.append(check)
    lines.extend(f"- {check}" for check in checklist)
    lines.append("")
    return "\n".join(lines)


def write_fixture_candidate_files(report: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for candidate in report.get("fixtureCandidates") or []:
        if not isinstance(candidate, dict):
            continue
        candidate_id = materialized_candidate_id(candidate)
        candidate_dir = output_dir / candidate_id
        candidate_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": fixture_readme(candidate),
            "fixture-candidate.json": json.dumps(safe_candidate_metadata(candidate), indent=2, sort_keys=True) + "\n",
            "fixture-report.json": json.dumps(synthetic_fixture_report(candidate), indent=2, sort_keys=True) + "\n",
            "fixture-report.md": synthetic_fixture_markdown(candidate),
        }
        for name, content in files.items():
            (candidate_dir / name).write_text(content, encoding="utf-8")
        entries.append(
            {
                "candidateId": candidate_id,
                "directory": candidate_id,
                "files": sorted(files),
                "promotion": promotion_metadata(candidate_id),
            }
        )
    promotion_manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": REPORT_QUALITY_TOOL,
        "generatedAt": utc_now(),
        "status": "pass",
        "candidateCount": len(entries),
        "promotionPolicy": "Generated candidates are public-safe starters. Promotion into fixtures/ios-report-quality is explicit maintainer work and must pass validation first.",
        "candidates": [item["promotion"] for item in entries],
    }
    index = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": REPORT_QUALITY_TOOL,
        "generatedAt": utc_now(),
        "status": "pass",
        "output": "<fixture-output-dir>",
        "candidateCount": len(entries),
        "candidates": entries,
        "promotionManifest": "fixture-promotion-manifest.json",
        "promotionGuide": "PROMOTION.md",
        "privateDataPolicy": "Generated fixtures are synthetic and path-safe. Source reports are not copied into fixture files.",
    }
    (output_dir / "fixture-candidates-index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "fixture-promotion-manifest.json").write_text(
        json.dumps(promotion_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "PROMOTION.md").write_text(render_promotion_markdown(entries), encoding="utf-8")
    index_lines = [
        "# Fixture Candidates Index",
        "",
        "Synthetic public fixture starters generated from report-quality fixtureCandidates.",
        "",
        "- `fixture-promotion-manifest.json`: machine-readable suggested repo paths, placeholder copy commands, validation commands, and review checklist.",
        "- `PROMOTION.md`: human-readable promotion guide. Promotion is explicit maintainer work.",
        "",
        "| Candidate | Directory |",
        "| --- | --- |",
    ]
    for item in entries:
        index_lines.append(f"| `{item['candidateId']}` | `{item['directory']}` |")
    index_lines.append("")
    (output_dir / "README.md").write_text("\n".join(index_lines), encoding="utf-8")
    return index


def main() -> int:
    args = parse_args()
    report = build_report(args.reports, shareable=args.shareable, shipguard_eval=args.shipguard_eval)
    if args.write_fixture_candidates:
        materialization = write_fixture_candidate_files(report, Path(args.write_fixture_candidates).expanduser().resolve())
        report["fixtureMaterialization"] = materialization
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(report), end="")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
