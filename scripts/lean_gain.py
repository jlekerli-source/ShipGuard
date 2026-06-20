#!/usr/bin/env python3
"""ShipGuard Lean Gain: honest benchmark impact report for lean-code mode."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from lean_audit import iter_files, scan_lean_debt


TOOL = "shipguard lean gain"
SURFACE = "ShipGuard Lean Gain"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show benchmark-backed lean-code impact without inventing per-repo savings."
    )
    parser.add_argument("--path", default=".", help="Repo to inspect for shortcut-ledger context")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def bar(percent: int, width: int = 20) -> str:
    filled = max(0, min(width, round((percent / 100) * width)))
    return "#" * filled + "-" * (width - filled)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"lean-gain: path does not exist: {root}")
    files, scan_scope = iter_files(root)
    ledger = scan_lean_debt(root, files)
    display_root = "." if args.shareable else str(root)
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": "pass",
        "target": {"path": display_root, "shareable": bool(args.shareable)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard reports the lean-code benchmark honestly and implements its own native reports. It does not vendor Ponytail code.",
        },
        "benchmarkScoreboard": {
            "primary": {
                "label": "Ponytail agentic benchmark",
                "baseline": "same agent without the lean-code ruleset",
                "scope": "public benchmark, not this repository",
                "method": "real agent sessions on public FastAPI + React tasks",
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
                "boundary": "Older single-shot ranges are not the launch claim because conversation-only baselines overstate savings.",
            },
        },
        "currentRepoBoundary": {
            "perRepoSavingsClaim": "not-computed",
            "reason": "There is no untreated baseline for this repository; ShipGuard cannot subtract code, cost, or time that was never produced.",
            "realRepoSignals": [
                "lean audit findings",
                "lean review findings",
                "lean debt marker counts",
                "diff size after an actual change",
            ],
        },
        "leanDebtLedger": ledger,
        "scanScope": scan_scope,
        "nextActions": [
            "Use shipguard lean audit for cuttable repo surfaces.",
            "Use shipguard lean review on the active diff before merge.",
            "Use shipguard lean debt to count intentional shortcuts with ceilings and upgrade triggers.",
            "Do not claim per-repo line, token, cost, or time savings unless you have a real matched baseline.",
        ],
    }
    if args.shipguard_eval:
        report["scopeBoundary"] = (
            "This is ShipGuard product QA. The benchmark explains expected direction; only local Lean Deck reports prove current repo observations."
        )
        report["reportQualityQuestions"] = [
            "Does Lean Gain make benchmark impact visible without pretending it measured this repo?",
            "Does it route current-repo evidence back to lean audit, lean review, and lean debt?",
            "Does the report prevent fake launch claims about line, token, cost, or time savings?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    primary = report["benchmarkScoreboard"]["primary"]
    remaining = primary["remainingPercentOfBaseline"]
    change = primary["reportedChange"]
    ledger_summary = report.get("leanDebtLedger", {}).get("summary", {})
    lines = [
        "# ShipGuard Lean Gain",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        "",
        "## Benchmark Scoreboard",
        "",
        f"- Benchmark: {primary['label']}",
        f"- Scope: {primary['scope']}",
        f"- Baseline: {primary['baseline']}",
        "",
        "| Metric | Baseline | Lean-code result | Change |",
        "| --- | --- | --- | --- |",
    ]
    metric_labels = [
        ("linesOfCode", "Lines of code"),
        ("tokens", "Tokens"),
        ("cost", "Cost"),
        ("time", "Time"),
        ("safety", "Safety"),
    ]
    for key, label in metric_labels:
        percent = int(remaining[key])
        lines.append(f"| {label} | `{bar(100)}` 100% | `{bar(percent)}` {percent}% | {change[key]} |")
    lines.extend(
        [
            "",
            "## Honesty Boundary",
            "",
            f"- Per-repo savings claim: `{report['currentRepoBoundary']['perRepoSavingsClaim']}`",
            f"- Reason: {report['currentRepoBoundary']['reason']}",
            "- Do not claim current-repo line, token, cost, or time savings without a matched baseline.",
            "",
            "## Current Repo Signals",
            "",
            f"- Lean debt markers: {ledger_summary.get('markers', 0)}",
            f"- Missing upgrade trigger: {ledger_summary.get('missingUpgradeTrigger', 0)}",
        ]
    )
    lines.extend(["", "## Source Influence", ""])
    lines.append(
        f"Native ShipGuard implementation influenced by {report['sourceInfluence']['name']} "
        f"({report['sourceInfluence']['url']}). {report['sourceInfluence']['boundary']}"
    )
    if report.get("scopeBoundary"):
        lines.extend(["", "## Scope Boundary", "", report["scopeBoundary"]])
    if report.get("reportQualityQuestions"):
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")
    lines.extend(["", "## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    md_text = render_markdown(report)
    (out / "lean-gain.json").write_text(json_text, encoding="utf-8")
    (out / "lean-gain.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
