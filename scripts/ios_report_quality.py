#!/usr/bin/env python3
"""Grade ShipGuard iOS reports for usefulness as product-QA artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
SOURCE_SCANNER_TOOLS = {
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
    "shipguard ios performance": 0,
    "shipguard ios design": 1,
    "shipguard ios modernize": 2,
    "shipguard ios app-intelligence": 3,
    "shipguard ios ai-readiness": 4,
    "shipguard ios external-audit": 5,
    "shipguard ios spec-workflow": 6,
    "shipguard ios devspace-check": 7,
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
PRIVATE_EVAL_APP_RE = re.compile(r"(?i)\b(?:Ringly|Ilmify|InweFi)\b")


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


def report_json_files(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            fail(f"report path not found: {path}")
        if path.is_file():
            paths.append(path)
            continue
        for candidate in sorted(path.rglob("*.json")):
            if candidate.name in {"ios-report-quality.json", "fixture-candidate.json", "fixture-candidates-index.json"}:
                continue
            paths.append(candidate)
    unique = sorted({path for path in paths})
    if not unique:
        fail("no report JSON files found")
    return unique


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
            "status": "blocked",
            "score": score_for(issues),
            "issues": issues,
            "issueCount": len(issues),
        }

    tool = str(loaded.get("tool") or "")
    intent = str(loaded.get("intent") or "")
    if not tool.startswith("shipguard ios "):
        add_issue(
            issues,
            severity="high",
            rule_id="report-tool-missing",
            evidence=f"{path.name} has tool={tool or 'missing'}",
            recommendation="Set a stable ShipGuard iOS tool name in every report JSON.",
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
    if tool == "shipguard ios performance":
        issues.extend(performance_finding_explanation_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_grouping_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_high_severity_issues(loaded, markdown=markdown, path_name=path.name))
        issues.extend(performance_proof_boundary_issues(loaded, markdown=markdown, path_name=path.name))

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
    return {
        "path": display_path,
        "markdownPath": display_markdown_path,
        "tool": tool,
        "intent": intent or None,
        "reportStatus": loaded.get("status"),
        "actionabilityQuestions": report_questions(loaded, report_path=display_path, tool=tool),
        "score": score,
        "status": report_status(issues),
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
    return f"{tool} is next in the default iOS maintenance priority order"


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
    if ranked_questions:
        question = ranked_questions[0]
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
            "Convert the top answer into a public fixture, eval case, report section, or docs change before editing ShipGuard rules.",
            "If implementation needs planning, feed this report-quality output into ios spec-workflow with --from-report.",
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


def slugify(value: object, *, limit: int = 72) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return (text[:limit].strip("-") or "report-quality-fixture")


def fixture_type_for_question(question: str, tool: str) -> str:
    text = normalized_question_text(f"{tool} {question}")
    question_text = normalized_question_text(question)
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


def build_fixture_candidates(ranked_questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen_types: set[str] = set()
    for row in ranked_questions:
        if row.get("sourceMaterializedFixture"):
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
    input_paths = resolved_input_paths(inputs)
    cwd = Path.cwd().resolve()
    graded = [grade_report(path, input_paths=input_paths, shareable=shareable, cwd=cwd) for path in paths]
    issues = []
    actionability_questions = []
    for item in graded:
        for issue in item["issues"]:
            issues.append({**issue, "report": item["path"], "tool": item.get("tool")})
        actionability_questions.extend(item.get("actionabilityQuestions", []))
    average = round(sum(item["score"] for item in graded) / len(graded), 1)
    status = "pass"
    if any(item["status"] == "blocked" for item in graded):
        status = "blocked"
    elif any(item["status"] == "review" for item in graded):
        status = "review"
    actionability_questions = dedupe_question_rows(actionability_questions)
    ranked_questions = ranked_actionability_questions(graded)
    fixture_candidates = build_fixture_candidates(ranked_questions)
    priority_action = build_priority_action(issues, ranked_questions)
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
        "findings": issues,
        "actionabilityQuestions": actionability_questions[:30],
        "prioritizedActionabilityQuestions": ranked_questions[:30],
        "fixtureCandidates": fixture_candidates,
        "priorityAction": priority_action,
        "nextActions": build_next_actions(priority_action, ranked_questions),
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
        "## Reports",
        "",
        "| Score | Quality Status | Source Status | Tool | Intent | Report | Issues |",
        "| ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for item in report["reports"]:
        lines.append(
            f"| {item['score']} | {item['status']} | {item.get('reportStatus') or '-'} | `{table_cell(item.get('tool') or 'unknown', 40)}` | {item.get('intent') or '-'} | `{Path(item['path']).name}` | {item['issueCount']} |"
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
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return ""
    text = LOCAL_PATH_VALUE_RE.sub("<local-path>", text)
    for pattern in TOKEN_RISK_PATTERNS.values():
        text = pattern.sub("<token-like-value>", text)
    text = PRIVATE_EVAL_APP_RE.sub("<private-app>", text)
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


def synthetic_fixture_report(candidate: dict[str, Any]) -> dict[str, Any]:
    question = materialized_source_question(candidate)
    source_tool = sanitize_materialized_text(candidate.get("sourceTool")) or "shipguard ios report-quality"
    return {
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


def synthetic_fixture_markdown(candidate: dict[str, Any]) -> str:
    question = materialized_source_question(candidate)
    fixture_type = sanitize_materialized_text(candidate.get("fixtureType")) or "report-quality-actionability-fixture"
    return "\n".join(
        [
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
    )


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
