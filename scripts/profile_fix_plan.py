#!/usr/bin/env python3
"""Profile-native fix-plan reports for ShipGuard starter audits."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

from profile_audit import PROFILE_CONFIG


PLAN_CONFIG: dict[str, dict[str, Any]] = {
    "web": {
        "tool": "shipguard web plan",
        "surface": "ShipGuard WebForge",
        "json": "web-plan.json",
        "markdown": "web-plan.md",
        "auditJson": "web-audit.json",
        "auditTool": "shipguard web audit",
        "auditSurface": "ShipGuard WebScan",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-web-plan --out /tmp/shipguard-web-plan-quality --shareable",
    },
    "backend": {
        "tool": "shipguard backend plan",
        "surface": "ShipGuard ServiceForge",
        "json": "backend-plan.json",
        "markdown": "backend-plan.md",
        "auditJson": "backend-audit.json",
        "auditTool": "shipguard backend audit",
        "auditSurface": "ShipGuard ServiceRadar",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-backend-plan --out /tmp/shipguard-backend-plan-quality --shareable",
    },
    "cli": {
        "tool": "shipguard cli plan",
        "surface": "ShipGuard CommandForge",
        "json": "cli-plan.json",
        "markdown": "cli-plan.md",
        "auditJson": "cli-audit.json",
        "auditTool": "shipguard cli audit",
        "auditSurface": "ShipGuard CommandLens",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-cli-plan --out /tmp/shipguard-cli-plan-quality --shareable",
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise SystemExit(f"profile-fix-plan: {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn a ShipGuard profile first-audit report into a scoped fix plan.")
    parser.add_argument("profile", choices=sorted(PLAN_CONFIG), help="Profile to plan")
    parser.add_argument("--report", required=True, help="Profile audit JSON file or directory")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report quality questions and scope boundary")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"could not read audit report {path}: {exc}")
    if not isinstance(loaded, dict):
        fail(f"audit report is not a JSON object: {path}")
    return loaded


def resolve_report(report_path: Path, profile: str) -> Path:
    config = PLAN_CONFIG[profile]
    if report_path.is_file():
        return report_path
    if not report_path.is_dir():
        fail(f"--report is not a file or directory: {report_path}")
    direct = report_path / str(config["auditJson"])
    if direct.is_file():
        return direct
    candidates = sorted(report_path.glob("*-audit.json"))
    if not candidates:
        candidates = sorted(report_path.glob("*.json"))
    if not candidates:
        fail(f"no audit JSON found in {report_path}")
    return candidates[0]


def display_report_path(path: Path, *, shareable: bool, profile: str) -> str:
    return f"<{profile}-audit-report>" if shareable else path.resolve().as_posix()


def normalize_commands(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    commands: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in commands:
            commands.append(text)
    return commands


def finding_title(finding: dict[str, Any]) -> str:
    rule_id = str(finding.get("ruleId") or "finding")
    category = str(finding.get("category") or "audit")
    return f"{category}: {rule_id}"


def task(
    task_id: str,
    title: str,
    *,
    source: str,
    recommendation: str,
    proof: str,
    validation: list[str],
    severity: str = "review",
) -> dict[str, Any]:
    return {
        "id": task_id,
        "title": title,
        "severity": severity,
        "source": source,
        "recommendation": recommendation,
        "proofGuidance": proof,
        "validationCommands": validation,
        "status": "ready",
    }


def task_from_finding(profile: str, finding: dict[str, Any], index: int) -> dict[str, Any]:
    rule_id = str(finding.get("ruleId") or f"finding-{index}")
    proof = str(finding.get("proofGuidance") or f"Rerun `shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable`.")
    return task(
        f"finding-{index}-{rule_id}",
        finding_title(finding),
        source=f"audit finding `{rule_id}`",
        recommendation=str(finding.get("recommendation") or "Address the audit finding with the smallest reversible change."),
        proof=proof,
        validation=[
            f"shipguard doctor {profile} .",
            f"shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable",
        ],
        severity=str(finding.get("severity") or "review"),
    )


def build_tasks(profile: str, audit: dict[str, Any]) -> list[dict[str, Any]]:
    profile_config = PROFILE_CONFIG[profile]
    validation = normalize_commands(audit.get("recommendedValidation")) or normalize_commands(profile_config.get("recommendedValidation"))
    first_commands = normalize_commands(audit.get("recommendedFirstCommands")) or normalize_commands(profile_config.get("firstCommands"))
    findings = audit.get("findings") if isinstance(audit.get("findings"), list) else []
    tasks = [task_from_finding(profile, item, index) for index, item in enumerate(findings, start=1) if isinstance(item, dict)]
    tasks.extend(
        [
            task(
                "starter-handoff-readiness",
                "Verify starter handoff and repo-local guardrails",
                source="starter profile",
                recommendation="Confirm the target has AGENTS.md, planning templates, scorecard, and profile-specific handoff files before authorizing edits.",
                proof=f"Run `shipguard doctor {profile} .` and keep missing starter files out of release claims.",
                validation=[f"shipguard doctor {profile} .", *first_commands[:1]],
                severity="review",
            ),
            task(
                "validation-lane-hardening",
                "Name the narrowest validation lane before the next Codex edit",
                source="recommendedValidation",
                recommendation="Replace generic validation placeholders with commands the repo can actually run, then keep blocked commands as blockers.",
                proof="Run the smallest listed validation command and capture the exact pass, fail, timeout, or infrastructure blocker.",
                validation=validation,
                severity="review",
            ),
            task(
                "risk-boundary-map",
                "Map product risk into proof boundaries",
                source="audit signals",
                recommendation="Turn detected framework, validation, and risk signals into protected areas, stop conditions, and proof requirements in the target handoff.",
                proof=f"Rerun `shipguard {profile} audit` and confirm the report names concrete risk signals instead of generic advice.",
                validation=[f"shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable"],
                severity="opportunity",
            ),
            task(
                "report-quality-handoff",
                "Grade this plan as ShipGuard output before treating it as useful",
                source="ShipGuard product QA",
                recommendation="Run report-quality on the generated plan so ShipGuard learns when plans are too generic, too noisy, or missing proof guidance.",
                proof="Use QualityRadar results as ShipGuard product QA, not as target-app remediation authorization.",
                validation=[str(PLAN_CONFIG[profile]["qualityCommand"])],
                severity="opportunity",
            ),
        ]
    )
    return tasks


def collect_validation_commands(tasks: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for item in tasks:
        for command in item.get("validationCommands") or []:
            text = str(command).strip()
            if text and text not in commands:
                commands.append(text)
    return commands


def build_report(profile: str, report_path: Path, *, shareable: bool, shipguard_eval: bool) -> dict[str, Any]:
    config = PLAN_CONFIG[profile]
    audit_path = resolve_report(report_path, profile)
    audit = read_json(audit_path)
    if audit.get("profile") != profile:
        fail(f"audit profile mismatch: expected {profile}, got {audit.get('profile') or 'missing'}")
    if audit.get("tool") not in {config["auditTool"], PROFILE_CONFIG[profile]["tool"]}:
        fail(f"audit tool mismatch: expected {config['auditTool']}, got {audit.get('tool') or 'missing'}")
    tasks = build_tasks(profile, audit)
    validation = collect_validation_commands(tasks)
    status = "review" if audit.get("status") != "pass" or any(task["severity"] == "review" for task in tasks) else "pass"
    questions = [
        f"Does {config['surface']} turn {config['auditSurface']} findings into scoped tasks with validation commands?",
        f"Are the {profile} plan tasks concrete enough for a solo developer to execute without guessing?",
        f"Does the {profile} plan keep target-app work read-only until a separate implementation task is authorized?",
    ]
    if shipguard_eval:
        questions.insert(0, f"Did ShipGuard produce a useful {profile} fix plan, or is this still decorative guidance?")
    return {
        "schemaVersion": 1,
        "tool": config["tool"],
        "surface": config["surface"],
        "profile": profile,
        "generatedAt": utc_now(),
        "status": status,
        "sourceAudit": {
            "tool": audit.get("tool"),
            "surface": audit.get("surface"),
            "status": audit.get("status"),
            "profile": audit.get("profile"),
            "path": display_report_path(audit_path, shareable=shareable, profile=profile),
            "findingCount": len(audit.get("findings") or []),
            "recommendedValidationCount": len(normalize_commands(audit.get("recommendedValidation"))),
        },
        "scopeBoundary": {
            "shipguardOnly": bool(shipguard_eval),
            "targetAppsReadOnly": True,
            "privateAppDetailsAllowed": False,
            "shareable": shareable,
            "implementationAuthorized": False,
        },
        "fixPlan": {
            "intent": "turn-profile-first-audit-into-scoped-work",
            "taskCount": len(tasks),
            "tasks": tasks,
        },
        "validationCommands": validation,
        "stopConditions": [
            "Stop before editing the target repo unless the user explicitly changes the task from ShipGuard product QA to app implementation.",
            "Stop if validation commands are placeholders or cannot run locally; record the exact blocker instead of claiming proof.",
            "Stop if report-quality flags missing scope boundary, local path leakage, or generic recommendations.",
        ],
        "reportQualityQuestions": questions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['surface']}",
        "",
        f"- Tool: `{report['tool']}`",
        f"- Status: {report['status']}",
        f"- Profile: {report['profile']}",
        f"- ShipGuard-only: {str(report['scopeBoundary']['shipguardOnly']).lower()}",
        f"- Implementation authorized: {str(report['scopeBoundary']['implementationAuthorized']).lower()}",
        "",
        "## Source Audit",
        "",
        f"- Audit tool: `{report['sourceAudit']['tool']}`",
        f"- Audit surface: {report['sourceAudit']['surface']}",
        f"- Audit status: {report['sourceAudit']['status']}",
        f"- Audit path: `{report['sourceAudit']['path']}`",
        f"- Findings: {report['sourceAudit']['findingCount']}",
        "",
        "## Scoped Fix Plan",
        "",
    ]
    for item in report["fixPlan"]["tasks"]:
        lines.append(f"### {item['id']}: {item['title']}")
        lines.append(f"- Severity: {item['severity']}")
        lines.append(f"- Source: {item['source']}")
        lines.append(f"- Recommendation: {item['recommendation']}")
        lines.append(f"- Proof: {item['proofGuidance']}")
        if item.get("validationCommands"):
            lines.append("- Validation:")
            for command in item["validationCommands"]:
                lines.append(f"  - `{command}`")
        lines.append("")
    lines.extend(["## Validation Commands", ""])
    for command in report["validationCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Stop Conditions", ""])
    for condition in report["stopConditions"]:
        lines.append(f"- {condition}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args.profile, Path(args.report), shareable=args.shareable, shipguard_eval=args.shipguard_eval)
    markdown = render_markdown(report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = PLAN_CONFIG[args.profile]
    json_path = out_dir / config["json"]
    markdown_path = out_dir / config["markdown"]
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(markdown)
    print(f"wrote: {json_path}")
    print(f"wrote: {markdown_path}")
    print(f"status: {report['status']}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
