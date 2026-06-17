#!/usr/bin/env python3
"""Generate ShipGuard-native spec, plan, task, and Devspace guardrail artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope


SCHEMA_VERSION = 1
TOOL = "shipguard ios spec-workflow"
SOURCE_SUFFIXES = {
    ".swift",
    ".plist",
    ".json",
    ".md",
    ".storekit",
    ".xcconfig",
    ".pbxproj",
}
APP_TYPES = [
    "auto",
    "utility",
    "game",
    "fitness",
    "health",
    "education",
    "kids",
    "creative",
    "commerce",
    "social",
    "finance",
    "saas",
]
APP_TYPE_KEYWORDS = {
    "utility": ["alarm", "timer", "reminder", "task", "notification", "widget", "shortcut", "productivity"],
    "game": ["spritekit", "scenekit", "gamekit", "level", "score", "gameplay", "leaderboard"],
    "fitness": ["workout", "fitness", "exercise", "activity", "steps", "training", "run", "pace"],
    "health": ["healthkit", "health", "sleep", "heart", "medication", "symptom", "wellness", "mindfulness"],
    "education": ["lesson", "quiz", "course", "learn", "flashcard", "student", "teacher"],
    "kids": ["kids", "child", "children", "parent", "guardian", "classroom"],
    "creative": ["camera", "photo", "drawing", "canvas", "editor", "design", "portfolio", "media"],
    "commerce": ["storekit", "purchase", "product", "checkout", "cart", "subscription", "entitlement", "price"],
    "social": ["profile", "share", "message", "chat", "follower", "friend", "community", "comment"],
    "finance": ["finance", "budget", "bank", "payment", "invoice", "transaction", "portfolio", "account"],
    "saas": ["dashboard", "workspace", "team", "admin", "organization", "project", "analytics", "crm"],
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-spec-workflow: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate ShipGuard-owned constitution/spec/plan/tasks/analysis artifacts for iOS work."
    )
    parser.add_argument("--path", default=".", help="iOS project, package, or ShipGuard repo root to scan")
    parser.add_argument("--feature", required=True, help="Feature, workflow, or ShipGuard improvement to spec")
    parser.add_argument("--out", help="Output directory for spec workflow artifacts")
    parser.add_argument("--from-report", action="append", default=[], help="Existing ShipGuard report JSON or directory")
    parser.add_argument("--app-type", choices=APP_TYPES, default="auto", help="Override inferred app type")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark private-app inputs as ShipGuard product QA only; findings must not become app work.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from report fields before ChatGPT, GitHub, docs, or report-quality use.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def report_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return path.as_posix()
    try:
        relative = path.relative_to(root)
        return relative.as_posix() or "."
    except ValueError:
        return f"<{placeholder}>"


def report_input_label(path: Path, *, input_paths: list[Path], cwd: Path, shareable: bool) -> str:
    if not shareable:
        return path.as_posix()
    try:
        return path.relative_to(cwd).as_posix() or "."
    except ValueError:
        pass
    for index, root in enumerate(input_paths, start=1):
        try:
            suffix = path.relative_to(root).as_posix()
        except ValueError:
            continue
        return f"<report-input-{index}>" if not suffix or suffix == "." else f"<report-input-{index}>/{suffix}"
    return "<local-report-path>"


def shareability_block(shareable: bool) -> dict[str, Any]:
    return {
        "mode": "shareable" if shareable else "local",
        "localAbsolutePathsIncluded": not shareable,
        "note": "Use --shareable before moving this spec workflow into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring."
        if not shareable
        else "Report fields are intended to avoid local absolute paths for external planning and report-quality scoring.",
    }


def source_records(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scan = ios_scan_scope.iter_files(root, SOURCE_SUFFIXES)
    records: list[dict[str, Any]] = []
    for path in scan.files[:2000]:
        text = read_text(path)
        records.append({"path": rel(path, root), "lower": text.lower()})
    return records, ios_scan_scope.summary(scan)


def infer_app_type(records: list[dict[str, Any]], override: str) -> dict[str, Any]:
    if override != "auto":
        return {"value": override, "override": True, "confidence": 1.0, "signals": [{"source": "cli", "token": override}]}
    scores: dict[str, int] = {}
    signals: dict[str, list[dict[str, str]]] = {}
    for app_type, keywords in APP_TYPE_KEYWORDS.items():
        total = 0
        app_signals: list[dict[str, str]] = []
        for record in records:
            for token in keywords:
                if token in record["lower"]:
                    total += 1
                    if len(app_signals) < 5:
                        app_signals.append({"token": token, "file": record["path"]})
        if total:
            scores[app_type] = total
            signals[app_type] = app_signals
    if not scores:
        return {"value": "utility", "override": False, "confidence": 0.35, "signals": []}
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best, best_score = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0
    confidence = round(min(0.95, 0.45 + ((best_score - second) / max(best_score, 1)) * 0.4), 2)
    return {"value": best, "override": False, "confidence": confidence, "signals": signals.get(best, [])}


def collect_doctor_facts(root: Path) -> dict[str, Any]:
    report = ios_doctor.build_report(root)
    projects = report.get("xcode_projects", [])
    packages = report.get("swift_packages", [])
    targets: list[str] = []
    deployment_targets: list[str] = []
    swift_versions: list[str] = []
    for project in projects:
        deployment_targets.extend(str(item) for item in project.get("deployment_targets", []))
        swift_versions.extend(str(item) for item in project.get("swift_versions", []))
        for target in project.get("target_details", []):
            if target.get("name"):
                targets.append(str(target["name"]))
    for package in packages:
        if package.get("name"):
            targets.append(str(package["name"]))
        if package.get("swift_tools_version"):
            swift_versions.append(str(package["swift_tools_version"]))
        deployment_targets.extend(str(item).replace("_", ".") for item in package.get("ios_platforms", []))
    return {
        "xcodeProjectCount": len(projects),
        "swiftPackageCount": len(packages),
        "targets": sorted(set(targets))[:12],
        "swiftVersions": sorted(set(item for item in swift_versions if item)),
        "deploymentTargets": sorted(set(item for item in deployment_targets if item)),
    }


def json_report_files(inputs: list[str]) -> tuple[list[Path], list[Path]]:
    input_paths = [Path(item).expanduser().resolve() for item in inputs]
    files: list[Path] = []
    for path in input_paths:
        if not path.exists():
            fail(f"report path not found: {path}")
        if path.is_file():
            files.append(path)
        else:
            files.extend(sorted(path.rglob("*.json")))
    unique = sorted({path for path in files if path.name != "ios-spec-workflow.json"})
    return unique, input_paths


def collect_report_context(inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    files, input_paths = json_report_files(inputs)
    cwd = Path.cwd().resolve()
    reports: list[dict[str, Any]] = []
    questions: list[dict[str, str]] = []
    seen_questions: set[str] = set()
    findings: list[dict[str, str]] = []
    for path in files:
        loaded = read_json(path)
        label = report_input_label(path, input_paths=input_paths, cwd=cwd, shareable=shareable)
        if loaded is None:
            findings.append(
                {
                    "severity": "review",
                    "ruleId": "spec-report-json-invalid",
                    "category": "report-context",
                    "evidence": f"{label} is not parseable JSON",
                    "recommendation": "Feed only valid ShipGuard reports into spec-workflow.",
                    "proofGuidance": "Run python3 -m json.tool on the report before spec-workflow.",
                }
            )
            continue
        tool = str(loaded.get("tool") or "unknown")
        reports.append({"path": label, "tool": tool, "status": loaded.get("status")})
        raw_questions = loaded.get("actionabilityQuestions") or loaded.get("reportQualityQuestions") or []
        if isinstance(raw_questions, list):
            for item in raw_questions:
                if isinstance(item, dict):
                    question = str(item.get("question") or "").strip()
                    source_tool = str(item.get("tool") or tool)
                else:
                    question = str(item).strip()
                    source_tool = tool
                key = normalized_actionability_question(question)
                if question and key and key not in seen_questions and len(questions) < 16:
                    questions.append({"tool": source_tool, "report": label, "question": question})
                    seen_questions.add(key)
    return {
        "inputs": [report_input_label(path, input_paths=input_paths, cwd=cwd, shareable=shareable) for path in input_paths],
        "reports": reports,
        "actionabilityQuestions": questions,
        "findings": findings,
    }


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "shipguard-feature"


def normalized_actionability_question(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def unique_actionability_questions(questions: list[dict[str, str]], *, limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in questions:
        question = str(item.get("question") or "").strip()
        key = normalized_actionability_question(question)
        if question and key and key not in seen:
            result.append(question)
            seen.add(key)
            if len(result) >= limit:
                break
    return result


def constitution() -> list[dict[str, str]]:
    return [
        {
            "id": "SG-I",
            "principle": "Proof before claims",
            "enforcement": "Every implementation task names the local, simulator, device, manual, or blocked proof lane.",
        },
        {
            "id": "SG-II",
            "principle": "Read-only product QA stays read-only",
            "enforcement": "Private app evidence may improve ShipGuard rules, fixtures, reports, and docs only.",
        },
        {
            "id": "SG-III",
            "principle": "Devspace is a planning bridge, not a remote shell",
            "enforcement": "Loopback defaults, bearer auth for tunnels, no arbitrary command tools, and no automatic Codex execution.",
        },
        {
            "id": "SG-IV",
            "principle": "Semantic UI proof beats coordinates",
            "enforcement": "Preview events require XcodeBuildMCP semantic target resolution before simulator input.",
        },
        {
            "id": "SG-V",
            "principle": "Shareable artifacts must declare shareability",
            "enforcement": "Reports that leave local proof space use --shareable and pass report-quality before publication.",
        },
    ]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path not found: {root}")
    records, scan_scope = source_records(root)
    app_type = infer_app_type(records, args.app_type)
    doctor = collect_doctor_facts(root)
    report_context = collect_report_context(args.from_report, shareable=bool(args.shareable)) if args.from_report else {
        "inputs": [],
        "reports": [],
        "actionabilityQuestions": [],
        "findings": [],
    }
    feature = args.feature.strip()
    if not feature:
        fail("--feature must not be empty")

    findings: list[dict[str, Any]] = list(report_context["findings"])
    if not report_context["reports"]:
        findings.append(
            {
                "severity": "opportunity",
                "ruleId": "spec-report-context-not-provided",
                "category": "report-context",
                "evidence": "No --from-report input was supplied.",
                "recommendation": "Feed report-quality or source-scanner reports into spec-workflow when converting real-app QA into ShipGuard tasks.",
                "proofGuidance": "Run ios report-quality on read-only ShipGuard reports, then pass that directory with --from-report.",
            }
        )

    slug = slugify(feature)
    questions = report_context["actionabilityQuestions"]
    task_questions = unique_actionability_questions(questions, limit=16)
    clarify_questions = task_questions[:8]
    if not clarify_questions:
        clarify_questions = [
            "Which user or maintainer outcome proves this feature is useful?",
            "Which evidence is required before Codex can claim the work is complete?",
            "Which private-app observations must stay examples instead of implementation tasks?",
        ]
    acceptance_criteria = [
        "The generated plan includes constitution, spec, checklist, tasks, analysis gates, and Devspace guardrails.",
        "Each task names a validation or proof lane.",
        "Shareable output avoids local absolute paths and passes ios report-quality.",
    ]
    for question in task_questions:
        acceptance_criteria.append(f"The ShipGuard change answers report-quality actionability question: {question}")
    task_plan = [
        {"id": "S001", "task": "Record the ShipGuard constitution and non-goals for this feature.", "proof": "shipguard-constitution.md exists."},
        {"id": "S002", "task": "Write the feature spec with user outcomes, non-goals, acceptance criteria, and clarifying questions.", "proof": "feature-spec.md exists."},
        {"id": "S003", "task": "Map implementation phases to local proof commands and manual blockers.", "proof": "implementation-plan.md exists."},
        {"id": "S004", "task": "Prepare ordered tasks with validation commands before edits.", "proof": "tasks.md exists."},
        {"id": "S005", "task": "Check Devspace safety gates before ChatGPT visual planning or MCP exposure.", "proof": "devspace-guardrails.md exists and references devspace-check."},
        {"id": "S006", "task": "Run report-quality on generated ShipGuard artifacts before sharing.", "proof": "ios report-quality returns pass or documented review findings."},
    ]
    for index, question in enumerate(task_questions, start=7):
        task_plan.append(
            {
                "id": f"S{index:03d}",
                "task": f"Resolve report-quality actionability question: {question}",
                "proof": "The resulting ShipGuard rule, fixture, report section, or docs change answers this question without turning private-app evidence into target-app work.",
            }
        )

    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "generatedAt": utc_now(),
        "status": "review" if any(item["severity"] == "review" for item in findings) else "pass",
        "intent": "shipguard-evaluation" if args.shipguard_eval else "spec-driven-planning",
        "feature": {"title": feature, "slug": slug},
        "path": report_path(root, root=root, shareable=bool(args.shareable), placeholder="target-repo"),
        "shareability": shareability_block(bool(args.shareable)),
        "scanScope": scan_scope,
        "appType": app_type,
        "projectFacts": doctor,
        "sourceInspiration": [
            {
                "source": "GitHub Spec Kit",
                "taken": "constitution -> specify -> clarify/checklist -> plan -> tasks -> analyze ordering",
                "shipguardAdaptation": "Artifacts are generated as ShipGuard proof gates and do not vendor Spec Kit code or command names.",
            },
            {
                "source": "CodexPro",
                "taken": "conservative local MCP bridge, handoff mode, workspace safety, and honest model-boundary language",
                "shipguardAdaptation": "Devspace keeps loopback/auth/semantic-target/redaction gates and does not expose arbitrary shell tools.",
            },
        ],
        "reportInputs": report_context,
        "constitution": constitution(),
        "featureSpec": {
            "summary": feature,
            "userOutcomes": [
                "A solo iOS developer can understand what should be built before Codex edits files.",
                "ShipGuard can turn report-quality questions into proof-gated implementation tasks.",
                "Devspace visual planning stays separated from trusted local execution.",
            ],
            "nonGoals": [
                "Do not vendor Spec Kit or CodexPro source.",
                "Do not edit private target apps from product-QA evidence.",
                "Do not claim ChatGPT model access, production hosting readiness, or device proof from static reports.",
            ],
            "acceptanceCriteria": acceptance_criteria,
            "clarifyingQuestions": clarify_questions,
        },
        "technicalPlan": {
            "phases": [
                {"id": "clarify", "goal": "Resolve ambiguous requirements before planning.", "proof": "Answered questions are added to the spec artifact."},
                {"id": "checklist", "goal": "Verify the spec is complete, testable, and bounded.", "proof": "Checklist has no blocking ambiguity."},
                {"id": "plan", "goal": "Choose the smallest ShipGuard CLI/docs/test change.", "proof": "Plan maps files, risks, and validation commands."},
                {"id": "tasks", "goal": "Break work into ordered tasks with independent proof.", "proof": "tasks.md lists commands and expected artifacts."},
                {"id": "analyze", "goal": "Cross-check constitution, spec, plan, and tasks before implementation.", "proof": "Analysis gate passes before code edits."},
                {"id": "implement", "goal": "Apply the smallest aligned change.", "proof": "Git diff is scoped and validation passes."},
            ],
            "recommendedValidation": [
                "git diff --check",
                "./tests/ios_spec_workflow_test.sh",
                "./tests/ios_report_quality_test.sh",
                "./tests/ios_devspace_check_test.sh",
                "./tests/cli_smoke_test.sh",
                "./bin/shipguard validate",
            ],
        },
        "taskPlan": task_plan,
        "analysisGates": [
            "Spec includes what and why before implementation details.",
            "Plan maps every risky surface to a proof lane.",
            "Tasks are ordered and independently verifiable.",
            "Devspace remains a connector and handoff path, not an execution bypass.",
            "Private-app observations remain ShipGuard product-QA evidence only.",
        ],
        "devspaceGuardrails": [
            "Use ios devspace-check before sharing a tunnel.",
            "Use HTTPS plus bearer auth for public or tunneled endpoints.",
            "Keep screenshot view tokens out of model-visible structured content.",
            "Require semantic elementRef matching before simulator taps.",
            "Use codex_prepare_handoff and ios codex-handoff before trusted local execution.",
            "State that model selection happens in ChatGPT, not ShipGuard.",
        ],
        "scopeBoundary": {
            "shipguardOnly": bool(args.shipguard_eval),
            "targetAppsReadOnly": bool(args.shipguard_eval),
            "purpose": "Generate ShipGuard-owned spec workflow artifacts; do not convert private-app findings into app work."
            if args.shipguard_eval
            else "Generate proof-gated ShipGuard spec workflow artifacts before implementation.",
            "forbiddenUses": [
                "Do not use this workflow to edit a scanned private app unless a separate app-work task explicitly authorizes it.",
                "Do not treat Devspace MCP planning as production hosting proof.",
                "Do not claim Spec Kit or CodexPro code was installed or bundled by this command.",
            ],
        },
        "slashPlan": f"/plan {feature}: clarify requirements, write the ShipGuard-owned spec, map proof-gated implementation tasks, run analysis before edits, validate, then generate the next ShipGuard goal.",
        "slashGoal": f"/goal Implement {feature}: follow the ShipGuard spec workflow artifacts, keep private-app evidence read-only when --shipguard-eval is used, validate with the listed proof commands, and record the next slash plan/goal.",
        "findings": findings,
        "reportQualityQuestions": [
            "Did spec-workflow convert report-quality questions into clarifying questions rather than app-remediation tasks?",
            "Are the generated tasks proof-gated enough for Codex to implement without drifting?",
            "Do Devspace guardrails make ChatGPT visual planning safe and explicit?",
            "Does shareable output avoid local absolute paths before report-quality scoring?",
        ],
        "artifacts": {
            "json": "ios-spec-workflow.json",
            "markdown": "ios-spec-workflow.md",
            "constitution": "shipguard-constitution.md",
            "spec": "feature-spec.md",
            "plan": "implementation-plan.md",
            "tasks": "tasks.md",
            "devspaceGuardrails": "devspace-guardrails.md",
        },
    }
    return report


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_main_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# iOS ShipGuard Spec Workflow",
        "",
        f"- Status: `{report['status']}`",
        f"- Feature: {report['feature']['title']}",
        f"- App type: `{report['appType']['value']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Purpose: {report['scopeBoundary']['purpose']}",
        "",
        "## Source Inspiration",
        "",
    ]
    for item in report["sourceInspiration"]:
        lines.append(f"- {item['source']}: {item['shipguardAdaptation']}")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation |", "| --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | {table_cell(item['evidence'])} | {table_cell(item['recommendation'])} |"
            )
    else:
        lines.append("No spec-workflow issues were detected.")
    if report["scopeBoundary"].get("shipguardOnly") is True:
        lines.extend(
            [
                "",
                "## ShipGuard Evaluation Boundary",
                "",
                "- This report is ShipGuard product QA only.",
                "- Private app findings must become ShipGuard rules, fixtures, report sections, or docs only.",
                "- Do not convert this report into target-app remediation work without separate explicit authorization.",
            ]
        )
    lines.extend(["", "## Clarifying Questions", ""])
    for question in report["featureSpec"]["clarifyingQuestions"]:
        lines.append(f"- {question}")
    scan = report["scanScope"]
    lines.extend(["", "## Scan Scope", ""])
    lines.append(f"- Files scanned: {scan['filesScanned']}")
    lines.append(f"- Skipped directories: {scan['skippedDirectoryCount']}")
    for directory in scan.get("skippedDirectories", [])[:8]:
        lines.append(f"- `{directory}`")
    lines.extend(["", "## Slash Plan", "", "```text", report["slashPlan"], "```", "", "## Slash Goal", "", "```text", report["slashGoal"], "```", ""])
    return "\n".join(lines)


def render_constitution(report: dict[str, Any]) -> str:
    lines = ["# ShipGuard Constitution", ""]
    for item in report["constitution"]:
        lines.extend([f"## {item['id']} {item['principle']}", "", item["enforcement"], ""])
    return "\n".join(lines)


def render_spec(report: dict[str, Any]) -> str:
    spec = report["featureSpec"]
    lines = ["# Feature Spec", "", f"## Summary", "", spec["summary"], "", "## User Outcomes", ""]
    lines.extend(f"- {item}" for item in spec["userOutcomes"])
    lines.extend(["", "## Non-Goals", ""])
    lines.extend(f"- {item}" for item in spec["nonGoals"])
    lines.extend(["", "## Acceptance Criteria", ""])
    lines.extend(f"- {item}" for item in spec["acceptanceCriteria"])
    lines.extend(["", "## Clarifying Questions", ""])
    lines.extend(f"- {item}" for item in spec["clarifyingQuestions"])
    lines.append("")
    return "\n".join(lines)


def render_plan(report: dict[str, Any]) -> str:
    lines = ["# Implementation Plan", "", "## Phases", ""]
    for phase in report["technicalPlan"]["phases"]:
        lines.append(f"- `{phase['id']}`: {phase['goal']} Proof: {phase['proof']}")
    lines.extend(["", "## Validation", ""])
    lines.extend(f"- `{item}`" for item in report["technicalPlan"]["recommendedValidation"])
    lines.extend(["", "## Analysis Gates", ""])
    lines.extend(f"- {item}" for item in report["analysisGates"])
    lines.append("")
    return "\n".join(lines)


def render_tasks(report: dict[str, Any]) -> str:
    lines = ["# Tasks", ""]
    for item in report["taskPlan"]:
        lines.append(f"- [ ] `{item['id']}` {item['task']} Proof: {item['proof']}")
    lines.append("")
    return "\n".join(lines)


def render_devspace_guardrails(report: dict[str, Any]) -> str:
    lines = ["# Devspace Guardrails", ""]
    lines.extend(f"- {item}" for item in report["devspaceGuardrails"])
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {item}" for item in report["scopeBoundary"]["forbiddenUses"])
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "ios-spec-workflow.json": json.dumps(report, indent=2, sort_keys=True) + "\n",
        "ios-spec-workflow.md": render_main_markdown(report),
        "shipguard-constitution.md": render_constitution(report),
        "feature-spec.md": render_spec(report),
        "implementation-plan.md": render_plan(report),
        "tasks.md": render_tasks(report),
        "devspace-guardrails.md": render_devspace_guardrails(report),
    }
    for name, body in outputs.items():
        (out_dir / name).write_text(body, encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-spec-workflow.json'}")
    print(f"wrote: {out_dir / 'ios-spec-workflow.md'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    report = build_report(args)
    markdown = render_main_markdown(report)
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
