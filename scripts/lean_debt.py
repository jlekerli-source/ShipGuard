#!/usr/bin/env python3
"""ShipGuard Lean Debt: harvest intentional lean shortcut markers."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from lean_audit import iter_files, scan_lean_debt


TOOL = "shipguard lean debt"
SURFACE = "ShipGuard Lean Debt"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Harvest ponytail: and shipguard-lean: comments into an auditable shortcut ledger."
    )
    parser.add_argument("--path", default=".", help="Repo to inspect")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"lean-debt: path does not exist: {root}")
    files, scan_scope = iter_files(root)
    ledger = scan_lean_debt(root, files)
    missing = int(ledger.get("summary", {}).get("missingUpgradeTrigger", 0))
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": "review" if missing else "pass",
        "target": {"path": "." if args.shareable else str(root), "shareable": bool(args.shareable)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native shortcut ledger for its own lean-code markers. It does not vendor Ponytail code.",
        },
        "leanDebtLedger": ledger,
        "scanScope": scan_scope,
        "nextActions": [
            "Add an upgrade trigger to every needs-trigger marker.",
            "Remove markers whose ceiling no longer applies.",
            "Use shipguard lean review on active diffs so new shortcuts are tracked before merge.",
        ],
    }
    if args.shipguard_eval:
        report["scopeBoundary"] = (
            "This is ShipGuard product QA. Shortcut markers in a target repo are evidence about report usefulness, not authorization to edit that repo."
        )
        report["reportQualityQuestions"] = [
            "Does Lean Debt make every shortcut marker visible with a ceiling and upgrade trigger?",
            "Does it avoid pretending benchmark savings are measurable in this repo?",
            "Can a maintainer tell which marker will rot without another source inspection pass?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    ledger = report.get("leanDebtLedger", {})
    summary = ledger.get("summary", {})
    lines = [
        "# ShipGuard Lean Debt",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        f"- Markers: {summary.get('markers', 0)}",
        f"- Missing upgrade trigger: {summary.get('missingUpgradeTrigger', 0)}",
        "",
        "## Shortcut Ledger",
        "",
    ]
    markers = ledger.get("markers", [])
    if markers:
        lines.extend(["| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |", "| --- | --- | --- | --- | --- | --- |"])
        for item in markers:
            location = f"{item.get('file', '')}:{item.get('line', '')}"
            lines.append(
                f"| {item.get('status', '')} | `{item.get('marker', '')}` | {location} | "
                f"{str(item.get('summary', '')).replace('|', '\\|')} | "
                f"{str(item.get('ceiling', '') or '-').replace('|', '\\|')} | "
                f"{str(item.get('upgrade', '') or '-').replace('|', '\\|')} |"
            )
    else:
        lines.append("No `ponytail:` or `shipguard-lean:` shortcut markers found.")
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
    (out / "lean-debt.json").write_text(json_text, encoding="utf-8")
    (out / "lean-debt.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
