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
}
REPORT_QUALITY_TOOL = "shipguard ios report-quality"
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
    for item in graded:
        for issue in item["issues"]:
            issues.append({**issue, "report": item["path"], "tool": item.get("tool")})
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
        "nextActions": [
            "Fix high report-quality issues before using the report as product QA evidence.",
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
