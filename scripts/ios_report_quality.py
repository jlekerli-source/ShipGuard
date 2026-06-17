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
    "plan",
    "tasks",
    "devspaceGuardrails",
    "json",
    "markdown",
}
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
            if candidate.name == "ios-report-quality.json":
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


def report_questions(report: dict[str, Any], *, report_path: str, tool: str) -> list[dict[str, str]]:
    questions = report.get("reportQualityQuestions")
    if not isinstance(questions, list):
        return []
    rows: list[dict[str, str]] = []
    for question in questions[:8]:
        if not isinstance(question, str):
            continue
        text = question.strip()
        if not text:
            continue
        rows.append(
            {
                "tool": tool,
                "report": report_path,
                "question": text,
            }
        )
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
                recommendation="Keep every spec workflow output self-describing: constitution, spec, plan, tasks, Devspace guardrails, JSON, and Markdown.",
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

    section_checks = [
        ("constitution", "spec-workflow-constitution-missing"),
        ("featureSpec", "spec-workflow-feature-spec-missing"),
        ("technicalPlan", "spec-workflow-plan-missing"),
        ("taskPlan", "spec-workflow-tasks-missing"),
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
                recommendation="Regenerate the spec workflow so constitution, spec, plan, tasks, analysis gates, and Devspace guardrails are all reviewable.",
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
        "nextActions": [
            "Fix high report-quality issues before using the report as product QA evidence.",
            "Answer the actionability questions above to decide which ShipGuard rule, report section, fixture, or doc should improve next.",
            "Convert repeated report-quality weaknesses into public fixtures or eval cases.",
            "Run private-app reports with --shipguard-eval and keep unredacted reports local.",
            "Use shipguard ios redact before sharing reports outside the local development loop.",
        ],
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
        "| Score | Status | Tool | Intent | Report | Issues |",
        "| ---: | --- | --- | --- | --- | ---: |",
    ]
    for item in report["reports"]:
        lines.append(
            f"| {item['score']} | {item['status']} | `{table_cell(item.get('tool') or 'unknown', 40)}` | {item.get('intent') or '-'} | `{Path(item['path']).name}` | {item['issueCount']} |"
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

    lines.extend(["", "## Actionability Questions", ""])
    if report["actionabilityQuestions"]:
        lines.extend(["| Tool | Report | Question |", "| --- | --- | --- |"])
        for item in report["actionabilityQuestions"][:12]:
            lines.append(
                f"| `{table_cell(item.get('tool') or 'unknown', 40)}` | `{Path(item['report']).name}` | {table_cell(item['question'], 140)} |"
            )
    else:
        lines.append("No report-quality questions were found in the input reports.")

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


def main() -> int:
    args = parse_args()
    report = build_report(args.reports, shareable=args.shareable)
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
