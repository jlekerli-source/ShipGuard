#!/usr/bin/env python3
"""Grade ShipGuard reports for usefulness as product-QA artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
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
    "shipguard full-audit": 0,
    "shipguard inspect": 0,
    "shipguard web audit": 1,
    "shipguard backend audit": 1,
    "shipguard cli audit": 1,
    "shipguard web plan": 2,
    "shipguard backend plan": 2,
    "shipguard cli plan": 2,
    "shipguard v4 preview": 3,
    "shipguard v4 schema-freeze": 3,
    "shipguard v4 release-candidate": 3,
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
    "shipguard value-gauntlet",
    "shipguard full-audit",
    "shipguard inspect",
    "shipguard v4 preview",
    "shipguard v4 schema-freeze",
    "shipguard v4 release-candidate",
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
}
SOURCE_REPORT_SKIP_DIR_NAMES = {
    "fresh-install-prefix",
    "fresh-install-work",
    "release-consume",
    "stage-receipts",
}


def is_skipped_report_path(path: Path) -> bool:
    return any(parent.name in SOURCE_REPORT_SKIP_DIR_NAMES for parent in path.parents)


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


def report_questions(report: dict[str, Any], *, report_path: str, tool: str) -> list[dict[str, Any]]:
    questions = report.get("reportQualityQuestions")
    if not isinstance(questions, list):
        return []
    materialized_fixture = is_materialized_fixture_report(report)
    rows: list[dict[str, Any]] = []
    for question in questions[:8]:
        if not isinstance(question, str):
            continue
        text = question.strip()
        if not text:
            continue
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


def question_focus_priority(row: dict[str, Any]) -> int:
    question = normalized_question_text(row.get("question") or "")
    tool = str(row.get("tool") or "")
    source_status = str(row.get("sourceStatus") or "")
    if tool == "shipguard ios launchdeck" and source_status != "pass":
        if any(token in question for token in ("missing build/run", "proof for the selected lane", "when receipts")):
            return -30
        if is_launchdeck_receipt_question(question, tool):
            return -20
    if should_create_fixture_candidate(question):
        return -10
    return 0


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
    if tool == "shipguard ios performance":
        issues.extend(performance_runtime_evidence_boundary_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_evidence_promotion_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_finding_explanation_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_grouping_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_high_severity_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_proof_boundary_issues(loaded, markdown=markdown, path_name=path.name))
    if tool == "shipguard ios design":
        issues.extend(design_app_type_tailoring_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(design_coherence_boundary_issues(loaded, markdown=markdown, path_name=path.name))

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
    if quality_status and quality_status != "pass":
        return f"report-quality status is {quality_status}"
    if source_status and source_status != "pass":
        return f"source report status is {source_status}"
    return f"{tool} is next in the default ShipGuard report-quality priority order"


def ranked_actionability_questions(graded: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report_index, report in enumerate(graded):
        for question_index, question in enumerate(report.get("actionabilityQuestions", [])):
            row = {
                "tool": question.get("tool") or report.get("tool") or "unknown",
                "report": question.get("report") or report.get("path") or "<unknown-report>",
                "question": question.get("question") or "",
                "sourceStatus": report.get("reportStatus") or "unknown",
                "reportQualityStatus": report.get("status") or "unknown",
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
            status_rank(row.get("sourceStatus")),
            question_focus_priority(row),
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
    if kind == "add-actionability-questions":
        return "./bin/shipguard ios report-quality --reports <updated-report-dir> --out <quality-dir> --shareable"
    return "./bin/shipguard ios report-quality --reports <report-dir> --out <quality-dir> --shareable"


def slugify(value: object, *, limit: int = 72) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return (text[:limit].strip("-") or "report-quality-fixture")


def fixture_type_for_question(question: str, tool: str) -> str:
    text = normalized_question_text(f"{tool} {question}")
    question_text = normalized_question_text(question)
    if is_launchdeck_receipt_question(question_text, tool):
        return "ios-launchdeck-receipt-quality-fixture"
    if "design-system coherence" in question_text or "design coherence" in question_text:
        return "ios-design-coherence-boundary-fixture"
    if "private-app" in question_text or "private app" in question_text or "target-app" in question_text or "target app" in question_text:
        return "shipguard-eval-boundary-fixture"
    if "grouped performance" in text or "performance" in text:
        return "ios-performance-report-quality-fixture"
    if "preview" in text or "devspace" in text or "visual proof" in text:
        return "ios-preview-devspace-routing-fixture"
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
        )
    )


def fixture_candidate_for_question(row: dict[str, Any], index: int) -> dict[str, Any]:
    question = str(row.get("question") or "")
    tool = str(row.get("tool") or "unknown")
    fixture_type = fixture_type_for_question(question, tool)
    candidate_id = f"{index:02d}-{slugify(f'{tool} {question}', limit=64)}"
    source_reports = [str(row.get("report") or "<unknown-report>")]
    for report in row.get("duplicateReports") or []:
        if isinstance(report, str) and report not in source_reports:
            source_reports.append(report)
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
        "expectedAssertions": [
            "report-quality preserves the actionability question in JSON and Markdown",
            "report-quality emits a fixtureCandidates entry for the public synthetic case",
            "the fixture keeps scopeBoundary.shipguardOnly and targetAppsReadOnly explicit",
            "shareable output contains no local absolute paths or private app identifiers",
        ],
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


def build_report(inputs: list[str], *, shareable: bool = False) -> dict[str, Any]:
    paths = report_json_files(inputs)
    promotion_manifest_paths = fixture_promotion_manifest_files(inputs)
    input_paths = resolved_input_paths(inputs)
    cwd = Path.cwd().resolve()
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
    fixture_coverage = annotate_existing_fixture_coverage(
        ranked_questions,
        existing_fixtures=existing_public_fixture_index(cwd),
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
        "generatedAt": utc_now(),
        "status": status,
        "reportCount": len(graded),
        "averageScore": average,
        "inputs": [path_label(path, input_paths=input_paths, shareable=shareable, cwd=cwd) for path in input_paths],
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
        },
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


def synthetic_design_report_fields() -> dict[str, Any]:
    return {
        "status": "review",
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
        "designDNA": {
            "motion": {"withAnimationSignals": 4, "animationModifiers": 2, "repeatForeverSignals": 1, "timelineViewSignals": 0, "reduceMotionSignals": 2},
            "haptics": {"uikitFeedbackSignals": 1, "coreHapticsSignals": 0, "sensoryFeedbackSignals": 0},
            "layout": {"roundedSignals": 8, "shadowSignals": 2, "blurSignals": 1, "cardNameSignals": 3},
            "copyTone": {"visibleStringCount": 9, "localizationSignals": 2, "samples": ["Lesson complete", "Try again"]},
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
            }
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
    if source_tool == "shipguard ios design" and fixture_type in {
        "ios-design-report-quality-fixture",
        "ios-design-coherence-boundary-fixture",
    }:
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
    if source_tool == "shipguard ios design" and fixture_type in {
        "ios-design-report-quality-fixture",
        "ios-design-coherence-boundary-fixture",
    }:
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
    report = build_report(args.reports, shareable=args.shareable)
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
