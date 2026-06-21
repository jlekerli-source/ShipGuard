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


def build_marker_visibility_review(ledger: dict[str, Any]) -> dict[str, Any]:
    summary = ledger.get("summary") if isinstance(ledger.get("summary"), dict) else {}
    markers = ledger.get("markers") if isinstance(ledger.get("markers"), list) else []
    rows: list[dict[str, Any]] = []
    for item in markers:
        if not isinstance(item, dict):
            continue
        file_name = str(item.get("file") or "")
        line = item.get("line") or ""
        location = f"{file_name}:{line}" if file_name or line else ""
        ceiling = str(item.get("ceiling") or "")
        upgrade = str(item.get("upgrade") or "")
        has_ceiling = bool(item.get("hasCeiling") is True or ceiling)
        has_upgrade = bool(item.get("hasUpgradeTrigger") is True and upgrade)
        rows.append(
            {
                "file": file_name,
                "line": line,
                "location": location,
                "marker": str(item.get("marker") or ""),
                "status": str(item.get("status") or ""),
                "summary": str(item.get("summary") or ""),
                "ceiling": ceiling,
                "upgradeTrigger": upgrade,
                "hasCeiling": has_ceiling,
                "hasUpgradeTrigger": has_upgrade,
                "exposesUpgradeStatus": isinstance(item.get("hasUpgradeTrigger"), bool)
                and str(item.get("status") or "") in {"tracked", "needs-trigger", "needs-ceiling"},
            }
        )
    total_markers = int(summary.get("markers") or len(rows))
    omitted = int(summary.get("omittedByLimit") or max(0, total_markers - len(rows)))
    rows_with_ceiling = sum(1 for row in rows if row["hasCeiling"])
    rows_with_upgrade = sum(1 for row in rows if row["hasUpgradeTrigger"])
    rows_with_upgrade_status = sum(1 for row in rows if row["exposesUpgradeStatus"])
    rows_missing_ceiling = max(0, len(rows) - rows_with_ceiling)
    rows_needing_trigger = int(summary.get("missingUpgradeTrigger") or max(0, len(rows) - rows_with_upgrade))
    return {
        "policy": (
            "Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, "
            "upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written."
        ),
        "summary": {
            "totalMarkers": total_markers,
            "visibleMarkerRows": len(rows),
            "omittedByLimit": omitted,
            "rowsWithCeiling": rows_with_ceiling,
            "rowsMissingCeiling": int(summary.get("missingCeiling") or rows_missing_ceiling),
            "rowsWithUpgradeTrigger": rows_with_upgrade,
            "rowsNeedingUpgradeTrigger": rows_needing_trigger,
            "rowsWithUpgradeStatus": rows_with_upgrade_status,
        },
        "allMarkersVisible": total_markers == len(rows) and omitted == 0,
        "allVisibleRowsHaveCeiling": rows_missing_ceiling == 0,
        "allVisibleRowsExposeUpgradeStatus": rows_with_upgrade_status == len(rows),
        "visibilityRows": rows,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"lean-debt: path does not exist: {root}")
    files, scan_scope = iter_files(root)
    ledger = scan_lean_debt(root, files)
    marker_visibility = build_marker_visibility_review(ledger)
    visibility_summary = marker_visibility["summary"]
    missing = int(visibility_summary.get("rowsNeedingUpgradeTrigger", 0))
    missing_ceiling = int(visibility_summary.get("rowsMissingCeiling", 0))
    omitted = int(visibility_summary.get("omittedByLimit", 0))
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": "review" if missing or missing_ceiling or omitted else "pass",
        "target": {"path": "." if args.shareable else str(root), "shareable": bool(args.shareable)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native shortcut ledger for its own lean-code markers. It does not vendor Ponytail code.",
        },
        "leanDebtLedger": ledger,
        "markerVisibilityReview": marker_visibility,
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
    marker_review = report.get("markerVisibilityReview", {})
    marker_summary = marker_review.get("summary", {}) if isinstance(marker_review, dict) else {}
    visibility_rows = marker_review.get("visibilityRows", []) if isinstance(marker_review, dict) else []
    lines = [
        "# ShipGuard Lean Debt",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        f"- Markers: {summary.get('markers', 0)}",
        f"- Missing ceiling: {summary.get('missingCeiling', 0)}",
        f"- Missing upgrade trigger: {summary.get('missingUpgradeTrigger', 0)}",
        "",
        "## Marker Visibility Review",
        "",
        f"- All markers visible: `{str(marker_review.get('allMarkersVisible', False)).lower()}`",
        f"- Visible marker rows: {marker_summary.get('visibleMarkerRows', 0)} of {marker_summary.get('totalMarkers', summary.get('markers', 0))}",
        f"- Rows with ceiling: {marker_summary.get('rowsWithCeiling', 0)}",
        f"- Rows missing ceiling: {marker_summary.get('rowsMissingCeiling', 0)}",
        f"- Rows with upgrade trigger: {marker_summary.get('rowsWithUpgradeTrigger', 0)}",
        f"- Rows needing upgrade trigger: {marker_summary.get('rowsNeedingUpgradeTrigger', 0)}",
        f"- Rows with upgrade status: {marker_summary.get('rowsWithUpgradeStatus', 0)}",
        f"- Policy: {marker_review.get('policy', '')}",
        "",
        "| Status | Marker | Location | Ceiling | Upgrade Trigger |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in visibility_rows:
        lines.append(
            f"| {item.get('status', '')} | `{item.get('marker', '')}` | {item.get('location', '')} | "
            f"{str(item.get('ceiling', '') or '-').replace('|', '\\|')} | "
            f"{str(item.get('upgradeTrigger', '') or '-').replace('|', '\\|')} |"
        )
    if not visibility_rows:
        lines.append("| pass | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Shortcut Ledger",
            "",
        ]
    )
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
