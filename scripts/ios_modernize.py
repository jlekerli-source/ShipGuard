#!/usr/bin/env python3
"""Audit Swift and SwiftUI modernization opportunities for iOS projects."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope
import ios_shareable


SCHEMA_VERSION = 1
MAX_FINDINGS_PER_RULE = 12
SEVERITY_RANK = {
    "high": 0,
    "review": 1,
    "opportunity": 2,
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-modernize: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Swift, SwiftUI, concurrency, availability, and system-modernization opportunities."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-modernize.md and ios-modernize.json")
    parser.add_argument("--focus", choices=["swift"], default="swift", help="Modernization focus. Default: swift")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Mark output as path-safe for ChatGPT, GitHub, docs, benchmarks, release evidence, or report-quality scoring.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of Markdown")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def shareability_block(shareable: bool) -> dict[str, Any]:
    return {
        "mode": "shareable" if shareable else "local",
        "localAbsolutePathsIncluded": not shareable,
        "note": "Use --shareable before moving this modernization report into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring."
        if not shareable
        else "Report fields are intended to avoid local absolute paths for external sharing.",
    }


def should_skip_dir(path: Path) -> bool:
    return ios_scan_scope.should_skip_dir(path)


def iter_files(root: Path) -> list[Path]:
    return ios_scan_scope.iter_files(root).files


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def parse_version(value: str) -> tuple[int, ...]:
    parts = []
    for part in re.split(r"[._-]", value):
        if part.isdigit():
            parts.append(int(part))
    return tuple(parts)


def version_at_least(value: str, minimum: str) -> bool:
    parsed = parse_version(value)
    required = parse_version(minimum)
    if not parsed:
        return False
    width = max(len(parsed), len(required))
    return parsed + (0,) * (width - len(parsed)) >= required + (0,) * (width - len(required))


def collect_doctor_facts(root: Path) -> dict[str, Any]:
    report = ios_doctor.build_report(root)
    swift_versions: list[str] = []
    deployment_targets: list[str] = []
    targets: list[dict[str, Any]] = []

    for project in report.get("xcode_projects", []):
        swift_versions.extend(str(item) for item in project.get("swift_versions", []))
        deployment_targets.extend(str(item) for item in project.get("deployment_targets", []))
        for target in project.get("target_details", []):
            targets.append(
                {
                    "name": target.get("name"),
                    "kind": target.get("kind"),
                    "swiftVersions": target.get("swift_versions", []),
                    "deploymentTargets": target.get("deployment_targets", []),
                }
            )

    for package in report.get("swift_packages", []):
        swift_versions.append(str(package.get("swift_tools_version") or ""))
        deployment_targets.extend(str(item).replace("_", ".") for item in package.get("ios_platforms", []))
        for target in package.get("target_details", []):
            targets.append(
                {
                    "name": target.get("name"),
                    "kind": target.get("kind"),
                    "package": package.get("path"),
                    "swiftVersions": [package.get("swift_tools_version")] if package.get("swift_tools_version") else [],
                    "deploymentTargets": [item.replace("_", ".") for item in package.get("ios_platforms", [])],
                }
            )

    return {
        "swiftVersions": unique_sorted(swift_versions),
        "deploymentTargets": unique_sorted(deployment_targets),
        "targets": targets,
    }


def source_context(lines: list[str], index: int, before: int = 3) -> str:
    start = max(0, index - before)
    return "\n".join(lines[start : index + 1])


def add_finding(findings: list[dict[str, Any]], finding: dict[str, Any]) -> None:
    rule_count = sum(1 for item in findings if item["ruleId"] == finding["ruleId"])
    if rule_count >= MAX_FINDINGS_PER_RULE:
        return
    findings.append(finding)


def finding(
    *,
    rule_id: str,
    category: str,
    severity: str,
    title: str,
    file: str | None,
    line: int | None,
    evidence: str,
    recommendation: str,
    availability: str,
    codex_mode: str,
    proof: str,
) -> dict[str, Any]:
    return {
        "ruleId": rule_id,
        "category": category,
        "severity": severity,
        "title": title,
        "file": file,
        "line": line,
        "evidence": evidence.strip(),
        "recommendation": recommendation,
        "availability": availability,
        "codexMode": codex_mode,
        "proof": proof,
    }


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate ShipGuard modernization-report quality.",
            "Identify noisy, generic, or poorly grouped modernization rules.",
            "Create redacted public fixtures or eval cases in ShipGuard.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not create app-specific modernization tasks from this run.",
            "Do not present target-app findings as the active development goal.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Did repeated availability, concurrency, or accessibility findings collapse into a scannable rule mix?",
        "Are high findings justified by specific source evidence?",
        "Does the report separate ShipGuard rule-quality issues from target-app remediation?",
        "Which private-app observation should become a public fixture or eval case?",
    ]


def summarize_rules(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in findings:
        rule_id = str(item["ruleId"])
        group = grouped.setdefault(
            rule_id,
            {
                "ruleId": rule_id,
                "category": item["category"],
                "count": 0,
                "high": 0,
                "review": 0,
                "opportunity": 0,
                "firstLocations": [],
            },
        )
        group["count"] += 1
        group[item["severity"]] += 1
        if len(group["firstLocations"]) < 3:
            location = item["file"] or "repo"
            if item.get("line"):
                location = f"{location}:{item['line']}"
            group["firstLocations"].append(location)
    return sorted(
        grouped.values(),
        key=lambda item: (
            SEVERITY_RANK["high"] if item["high"] else SEVERITY_RANK["review"] if item["review"] else SEVERITY_RANK["opportunity"],
            -int(item["count"]),
            str(item["ruleId"]),
        ),
    )


def select_markdown_findings(findings: list[dict[str, Any]], limit: int = 40, per_rule: int = 5) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    rule_counts: dict[str, int] = defaultdict(int)
    for item in findings:
        rule_id = str(item["ruleId"])
        if item["severity"] == "high" or rule_counts[rule_id] < per_rule:
            selected.append(item)
            rule_counts[rule_id] += 1
        if len(selected) >= limit:
            break
    return selected


def scan_swift_file(path: Path, root: Path, findings: list[dict[str, Any]], metrics: dict[str, int]) -> None:
    text = read_text(path)
    rel_path = rel(path, root)
    lines = text.splitlines()
    imports_swiftui = bool(re.search(r"^\s*import\s+SwiftUI\b", text, re.M))
    has_main_actor = "@MainActor" in text
    has_accessibility_label = ".accessibilityLabel" in text

    if imports_swiftui:
        metrics["swiftuiFiles"] += 1
    if "async" in text or "await" in text:
        metrics["asyncFiles"] += 1
    if "AppIntent" in text or "AppIntents" in text:
        metrics["appIntentFiles"] += 1
    if "Widget" in text or "WidgetKit" in text:
        metrics["widgetFiles"] += 1

    for index, line in enumerate(lines):
        stripped = line.strip()
        line_number = index + 1

        if re.search(r"\bTask\.detached\s*\{", line):
            add_finding(
                findings,
                finding(
                    rule_id="swift-concurrency-task-detached",
                    category="Swift Concurrency",
                    severity="high",
                    title="Review detached task isolation and cancellation",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Prefer structured tasks or document actor, priority, cancellation, and Sendable boundaries before Codex edits this path.",
                    availability="Swift concurrency behavior depends on the target Swift language mode; validate with a build or test lane.",
                    codex_mode="swift-6-modernization-gate",
                    proof="Run the affected test target or an XcodeBuildMCP build after changing this code.",
                ),
            )

        if re.search(r"\bTask\s*\{", line) and "Task.detached" not in line:
            add_finding(
                findings,
                finding(
                    rule_id="swift-concurrency-unstructured-task",
                    category="Swift Concurrency",
                    severity="review",
                    title="Check unstructured task lifecycle",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Confirm the task is cancelled with the owning view or model; prefer `.task(id:)` in SwiftUI views when lifecycle should follow rendering state.",
                    availability="No OS change is required, but behavior should be proven across appear, disappear, and cancellation states.",
                    codex_mode="async-state-gate",
                    proof="Add or run a test covering cancellation, stale state, and repeated view appearances.",
                ),
            )

        if re.search(r"\bfunc\b.*\basync\b|\bawait\b", line):
            add_finding(
                findings,
                finding(
                    rule_id="swift-concurrency-async-proof",
                    category="Swift Concurrency",
                    severity="opportunity",
                    title="Record proof for async state behavior",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Before refactoring this async path, identify the owning actor, cancellation behavior, and stale-result handling that must remain true.",
                    availability="Async behavior is source-level, but stricter diagnostics depend on the Swift language mode and target settings.",
                    codex_mode="swift-6-modernization-gate",
                    proof="Run the affected async unit test, UI flow, or simulator reproduction after edits.",
                ),
            )

        if re.search(r"\bclass\s+\w+[^:]*:\s*.*ObservableObject", line) and not has_main_actor:
            add_finding(
                findings,
                finding(
                    rule_id="swiftui-observableobject-mainactor",
                    category="Actor Isolation",
                    severity="review",
                    title="ObservableObject should declare UI actor ownership",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="If this object drives SwiftUI state, add explicit `@MainActor` or isolate mutation paths before enabling stricter concurrency checks.",
                    availability="Actor annotations are source-level modernization; validate against the app's Swift language mode.",
                    codex_mode="swift-6-modernization-gate",
                    proof="Build the target with concurrency diagnostics enabled and run state-update tests.",
                ),
            )

        if "@Published" in line and not has_main_actor:
            add_finding(
                findings,
                finding(
                    rule_id="swiftui-published-mainactor",
                    category="Actor Isolation",
                    severity="review",
                    title="Published UI state lacks visible actor boundary",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Add an explicit owner actor or migrate to Observation only after checking call sites and background updates.",
                    availability="Observation is a newer SwiftUI pattern; keep fallbacks or avoid migration when older deployment targets require it.",
                    codex_mode="observation-migration-gate",
                    proof="Run tests that mutate this state from async paths.",
                ),
            )

        if re.search(r"\b(ObservableObject|@Published)\b", line):
            add_finding(
                findings,
                finding(
                    rule_id="swiftui-observation-migration",
                    category="Observation",
                    severity="opportunity",
                    title="Consider Observation migration",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Evaluate whether `@Observable` reduces boilerplate; keep Combine compatibility if older app surfaces still subscribe directly.",
                    availability="Guard migrations by deployment target and package consumers before removing ObservableObject or Published APIs.",
                    codex_mode="observation-migration-gate",
                    proof="Build every target that imports this type and run UI state tests.",
                ),
            )

        if imports_swiftui and re.search(r"\b(?:Text|Button|Label|Toggle)\s*\(\s*\"[^\"]{2,}\"", line) and not has_accessibility_label:
            add_finding(
                findings,
                finding(
                    rule_id="swiftui-accessibility-copy",
                    category="Accessibility And Localization",
                    severity="opportunity",
                    title="Review visible copy and accessibility labels",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="Confirm user-facing copy has the right localization key and add accessibility labels or hints where the surrounding UI is not self-describing.",
                    availability="Localization and accessibility changes need simulator or snapshot proof across the edited screen.",
                    codex_mode="accessibility-localization-gate",
                    proof="Verify the rendered screen and accessibility tree after copy or label changes.",
                ),
            )

        if re.search(r"\bgetTimeline\s*\([^)]*completion:\s*@escaping", line):
            add_finding(
                findings,
                finding(
                    rule_id="widgetkit-completion-timeline",
                    category="SwiftUI System Surfaces",
                    severity="opportunity",
                    title="Review WidgetKit timeline modernization",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    recommendation="If widget behavior changes, check whether newer async timeline APIs or App Intent-backed configuration would reduce callback state.",
                    availability="Keep existing WidgetKit behavior for deployed OS versions; prove stale-data and refresh behavior.",
                    codex_mode="widget-shared-state-gate",
                    proof="Run widget preview or simulator proof for snapshot, timeline, stale, and refresh states.",
                ),
            )

    if imports_swiftui and "#available" not in text and "@available" not in text:
        add_finding(
            findings,
            finding(
                rule_id="swiftui-availability-fallbacks",
                category="Availability And Fallbacks",
                severity="review",
                title="Add availability gates before adopting newer SwiftUI visual APIs",
                file=rel_path,
                line=None,
                evidence="SwiftUI file has no visible availability guard.",
                recommendation="Before adopting newer visual-system APIs such as Liquid Glass-specific styling, isolate the change behind availability checks and keep a fallback rendering path.",
                availability="Use the app's deployment target to decide whether the fallback is runtime-guarded or source-conditional.",
                codex_mode="liquid-glass-readiness-gate",
                proof="Capture simulator screenshots on the newest target OS and the minimum supported OS, or document the unavailable runtime blocker.",
            ),
        )


def build_checks(facts: dict[str, Any], metrics: dict[str, int], findings: list[dict[str, Any]]) -> list[dict[str, str]]:
    swift_versions = facts["swiftVersions"]
    deployment_targets = facts["deploymentTargets"]
    has_swift_6 = any(version_at_least(version, "6.0") for version in swift_versions)
    has_deployment_target = bool(deployment_targets)
    high_count = sum(1 for item in findings if item["severity"] == "high")
    review_count = sum(1 for item in findings if item["severity"] == "review")

    return [
        {
            "id": "swift-language-mode",
            "status": "pass" if has_swift_6 else "review",
            "summary": "Swift 6 language mode detected." if has_swift_6 else "No Swift 6 language mode detected; strict concurrency readiness needs review.",
        },
        {
            "id": "deployment-targets",
            "status": "pass" if has_deployment_target else "review",
            "summary": "Deployment targets are available for availability decisions."
            if has_deployment_target
            else "No deployment target was discovered; availability guidance is conservative.",
        },
        {
            "id": "swiftui-modernization",
            "status": "review" if metrics["swiftuiFiles"] else "skipped",
            "summary": f"{metrics['swiftuiFiles']} SwiftUI file(s) need availability, accessibility, and visual-system review."
            if metrics["swiftuiFiles"]
            else "No SwiftUI files were detected.",
        },
        {
            "id": "strict-concurrency-hotspots",
            "status": "blocked" if high_count else ("review" if review_count else "pass"),
            "summary": f"{high_count} high-risk and {review_count} review concurrency or availability finding(s).",
        },
    ]


def build_report(root: Path, focus: str, *, shipguard_eval: bool = False, shareable: bool = False) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")

    scan = ios_scan_scope.iter_files(root)
    files = scan.files
    swift_files = [path for path in files if path.suffix == ".swift"]
    facts = collect_doctor_facts(root)
    metrics = {
        "swiftFiles": len(swift_files),
        "swiftuiFiles": 0,
        "asyncFiles": 0,
        "appIntentFiles": 0,
        "widgetFiles": 0,
    }
    findings: list[dict[str, Any]] = []

    for path in swift_files:
        scan_swift_file(path, root, findings, metrics)

    severity_counts: dict[str, int] = {"high": 0, "review": 0, "opportunity": 0}
    for item in findings:
        severity_counts[item["severity"]] = severity_counts.get(item["severity"], 0) + 1

    checks = build_checks(facts, metrics, findings)
    status = "pass"
    if any(check["status"] == "blocked" for check in checks):
        status = "blocked"
    elif findings:
        status = "review"

    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios modernize",
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "generatedAt": utc_now(),
        "focus": focus,
        "shareability": shareability_block(shareable),
        "status": status,
        "summary": {
            **metrics,
            "findings": len(findings),
            "severityCounts": severity_counts,
            "swiftVersions": facts["swiftVersions"],
            "deploymentTargets": facts["deploymentTargets"],
            "targets": len(facts["targets"]),
        },
        "scanScope": ios_scan_scope.summary(scan),
        "checks": checks,
        "targets": facts["targets"],
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "ruleSummary": summarize_rules(findings),
        "findings": findings,
        "guidance": [
            "Treat findings as a Codex planning input, not proof that a modernization is safe.",
            "For Swift concurrency work, run the affected build or test lane after every edit.",
            "For SwiftUI visual changes, capture screenshots for the newest supported OS and the minimum supported OS, or record the runtime blocker.",
            "For Observation, SwiftData, App Intents, Foundation Models, or Liquid Glass adoption, preserve availability and privacy fallbacks until the user explicitly accepts the migration.",
        ],
    }
    if shipguard_eval and shareable:
        report = ios_shareable.redact_shipguard_eval_report(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# iOS Swift Modernization Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Focus: `{report['focus']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Swift files: {summary['swiftFiles']}",
        f"- SwiftUI files: {summary['swiftuiFiles']}",
        f"- Findings: {summary['findings']}",
        f"- Skipped generated/proof/cache directories: {report['scanScope']['skippedDirectoryCount']}",
        f"- Swift versions: {', '.join(summary['swiftVersions']) if summary['swiftVersions'] else 'unknown'}",
        f"- Deployment targets: {', '.join(summary['deploymentTargets']) if summary['deploymentTargets'] else 'unknown'}",
        "",
    ]
    if report["intent"] == "shipguard-evaluation":
        boundary = report["scopeBoundary"]
        lines.extend(
            [
                "## ShipGuard Evaluation Boundary",
                "",
                "- This scan is ShipGuard product QA only.",
                "- The scanned app is a read-only input; do not edit it from this run.",
                "- Use findings to improve ShipGuard rules, grouping, report shape, docs, or eval fixtures.",
                "- Do not turn findings into target-app remediation tasks unless a separate app-work request explicitly authorizes it.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )
    lines.extend(
        [
        "## Checks",
        "",
        "| Check | Status | Summary |",
        "| --- | --- | --- |",
        ]
    )
    for check in report["checks"]:
        lines.append(f"| {check['id']} | {check['status']} | {check['summary']} |")

    if report["scanScope"]["skippedDirectories"]:
        lines.extend(["", "## Scan Scope", ""])
        for directory in report["scanScope"]["skippedDirectories"][:8]:
            lines.append(f"- Skipped `{directory}`")
        if report["scanScope"]["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")

    lines.extend(
        [
            "",
            "## Finding Mix",
            "",
            "| Rule | Count | Severity Mix | First Locations |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for summary_item in report["ruleSummary"]:
        severity_mix = f"{summary_item['high']} high, {summary_item['review']} review, {summary_item['opportunity']} opportunity"
        locations = "<br>".join(f"`{location}`" for location in summary_item["firstLocations"])
        lines.append(f"| `{summary_item['ruleId']}` | {summary_item['count']} | {severity_mix} | {locations} |")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        selected_findings = select_markdown_findings(report["findings"])
        lines.append("Repeated rules are capped here so the Markdown stays scannable; the JSON report contains every finding.")
        lines.append("")
        lines.extend(["| Severity | Category | Location | Finding | Recommendation |", "| --- | --- | --- | --- | --- |"])
        for item in selected_findings:
            location = item["file"] or "repo"
            if item.get("line"):
                location = f"{location}:{item['line']}"
            lines.append(
                f"| {item['severity']} | {item['category']} | `{location}` | {item['title']} | {item['recommendation']} |"
            )
        hidden_count = len(report["findings"]) - len(selected_findings)
        if hidden_count > 0:
            lines.append(f"| ... | ... | ... | ... | {hidden_count} more findings in JSON |")
    else:
        lines.append("No modernization findings were detected.")

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Availability And Proof Guidance", ""])
    for item in report["guidance"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-modernize.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-modernize.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-modernize.md'}")
    print(f"wrote: {out_dir / 'ios-modernize.json'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(root, args.focus, shipguard_eval=args.shipguard_eval, shareable=args.shareable)

    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
