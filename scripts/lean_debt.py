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
SCHEMA_VERSION = 2


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
    rows_needing_trigger = max(0, len(rows) - rows_with_upgrade)
    return {
        "policy": (
            "Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, "
            "upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written."
        ),
        "summary": {
            "totalMarkers": total_markers,
            "visibleMarkerRows": len(rows),
            "omittedByLimit": omitted,
            "omittedStateUnknown": omitted > 0,
            "rowsWithCeiling": rows_with_ceiling,
            "rowsMissingCeiling": rows_missing_ceiling,
            "rowsWithUpgradeTrigger": rows_with_upgrade,
            "rowsNeedingUpgradeTrigger": rows_needing_trigger,
            "rowsWithUpgradeStatus": rows_with_upgrade_status,
        },
        "allMarkersVisible": total_markers == len(rows) and omitted == 0,
        "allVisibleRowsHaveCeiling": rows_missing_ceiling == 0,
        "allVisibleRowsExposeUpgradeStatus": rows_with_upgrade_status == len(rows),
        "visibilityRows": rows,
    }


def build_trigger_watch_contract(
    *,
    has_ceiling: bool,
    has_upgrade: bool,
    upgrade: str,
    next_action: str,
) -> dict[str, str]:
    if not has_ceiling:
        return {
            "triggerState": "blocked-missing-ceiling",
            "triggerCondition": "missing ceiling; define the bounded scope or lifetime before relying on trigger cleanup",
            "exactNextAction": next_action,
            "checkRoute": "Add the ceiling to the marker, rerun shipguard lean debt, and confirm the row is no longer high risk.",
            "proofArtifact": "lean-debt.json markerVisibilityReview.visibilityRows row with hasCeiling=true and a non-empty ceiling.",
            "stopCondition": "Stop if no owner, milestone, release, scope, or lifetime can bound the shortcut.",
        }
    if not has_upgrade:
        return {
            "triggerState": "needs-trigger-definition",
            "triggerCondition": "missing upgrade trigger; define a release, dependency, migration, or repeated call-site signal",
            "exactNextAction": next_action,
            "checkRoute": "Add the upgrade trigger to the marker, rerun shipguard lean debt, and confirm rowsNeedingUpgradeTrigger decreases.",
            "proofArtifact": "lean-debt.json markerVisibilityReview.visibilityRows row with hasUpgradeTrigger=true and a non-empty upgradeTrigger.",
            "stopCondition": "Stop if the trigger cannot be checked later from a release, dependency, migration, or call-site signal.",
        }
    return {
        "triggerState": "watch-trigger",
        "triggerCondition": upgrade,
        "exactNextAction": f"Check whether this trigger is true: {upgrade}",
        "checkRoute": "Run call-site search for the shortcut location, then run the smallest focused validation covering the replacement or deletion.",
        "proofArtifact": "call-site search notes plus focused validation output attached beside lean-debt.json.",
        "stopCondition": "Stop if search or validation shows the shortcut is still active product behavior.",
    }


def build_rot_risk_review(marker_visibility: dict[str, Any]) -> dict[str, Any]:
    summary = marker_visibility.get("summary") if isinstance(marker_visibility.get("summary"), dict) else {}
    visibility_rows = (
        marker_visibility.get("visibilityRows") if isinstance(marker_visibility.get("visibilityRows"), list) else []
    )
    risk_rank = {"high": 0, "review": 1, "tracked": 2}
    rows: list[dict[str, Any]] = []
    for item in visibility_rows:
        if not isinstance(item, dict):
            continue
        has_ceiling = item.get("hasCeiling") is True
        has_upgrade = item.get("hasUpgradeTrigger") is True
        ceiling = str(item.get("ceiling") or "")
        upgrade = str(item.get("upgradeTrigger") or "")
        if not has_ceiling:
            risk_level = "high"
            rot_reason = "Missing ceiling means this shortcut has no bounded stop condition."
            next_action = "Add a ceiling that states the maximum scope or lifetime for this shortcut."
            proof_guidance = "Point to the smallest owner, milestone, release, or call-site condition that limits the shortcut."
        elif not has_upgrade:
            risk_level = "review"
            rot_reason = "Missing upgrade trigger means this shortcut can survive beyond its intended window."
            next_action = "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it."
            proof_guidance = "Name the release, dependency, migration state, or repeated call-site signal that should trigger cleanup."
        else:
            risk_level = "tracked"
            rot_reason = "Tracked shortcut should be reviewed when its upgrade trigger becomes true."
            next_action = f"Watch the upgrade trigger: {upgrade}"
            proof_guidance = "When the trigger is true, run call-site search plus the smallest focused validation before deleting or replacing it."
        trigger_watch_contract = build_trigger_watch_contract(
            has_ceiling=has_ceiling,
            has_upgrade=has_upgrade,
            upgrade=upgrade,
            next_action=next_action,
        )
        rows.append(
            {
                "rank": 0,
                "file": str(item.get("file") or ""),
                "line": item.get("line") or "",
                "location": str(item.get("location") or ""),
                "marker": str(item.get("marker") or ""),
                "status": str(item.get("status") or ""),
                "riskLevel": risk_level,
                "rotReason": rot_reason,
                "nextAction": next_action,
                "proofGuidance": proof_guidance,
                "ceiling": ceiling,
                "upgradeTrigger": upgrade,
                "hasCeiling": has_ceiling,
                "hasUpgradeTrigger": has_upgrade,
                "triggerWatchContract": trigger_watch_contract,
            }
        )
    rows.sort(key=lambda row: (risk_rank.get(str(row["riskLevel"]), 99), str(row["location"])))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    top = rows[0] if rows else {}
    high_rows = sum(1 for row in rows if row["riskLevel"] == "high")
    review_rows = sum(1 for row in rows if row["riskLevel"] == "review")
    tracked_rows = sum(1 for row in rows if row["riskLevel"] == "tracked")
    trigger_contract_rows = sum(1 for row in rows if isinstance(row.get("triggerWatchContract"), dict))
    top_trigger_contract = top.get("triggerWatchContract") if isinstance(top.get("triggerWatchContract"), dict) else {}
    return {
        "policy": (
            "Start with the highest-risk shortcut marker before opening source again: missing ceiling first, "
            "missing upgrade trigger second, tracked trigger watch third."
        ),
        "summary": {
            "totalMarkers": int(summary.get("totalMarkers") or len(rows)),
            "rotRiskRows": len(rows),
            "highRiskRows": high_rows,
            "reviewRiskRows": review_rows,
            "trackedRows": tracked_rows,
            "missingCeilingRows": high_rows,
            "missingUpgradeTriggerRows": review_rows,
            "triggerWatchContractRows": trigger_contract_rows,
            "missingTriggerWatchContractRows": max(0, len(rows) - trigger_contract_rows),
            "trackedTriggerWatchRows": tracked_rows,
            "missingTriggerDefinitionRows": review_rows,
            "omittedByLimit": int(summary.get("omittedByLimit") or 0),
            "omittedRiskUnknown": int(summary.get("omittedByLimit") or 0) > 0,
            "topRiskLocation": str(top.get("location") or ""),
            "topRiskReason": str(top.get("rotReason") or ""),
            "topTriggerWatchAction": str(top_trigger_contract.get("exactNextAction") or ""),
        },
        "coverageBoundary": (
            "Rot-risk ranking is based on visible shortcut rows. When omittedByLimit is greater than zero, "
            "omitted markers may contain higher risk and must be surfaced by rerunning with a narrower scope or extending the ledger limit."
        ),
        "allVisibleRowsHaveRotRisk": len(rows) == int(summary.get("visibleMarkerRows") or len(rows)),
        "topRiskActionable": bool(top.get("location") and top.get("nextAction")),
        "prioritizedRows": rows,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"lean-debt: path does not exist: {root}")
    files, scan_scope = iter_files(root)
    ledger = scan_lean_debt(root, files)
    marker_visibility = build_marker_visibility_review(ledger)
    rot_risk = build_rot_risk_review(marker_visibility)
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
        "rotRiskReview": rot_risk,
        "currentRepoBoundary": {
            "perRepoSavingsClaim": "not-computed",
            "evidenceType": "shortcut-ledger-only",
            "reason": "Lean Debt counts intentional shortcut markers and missing triggers; it has no untreated baseline for current-repo line, token, cost, or time savings.",
            "nonClaims": [
                "Do not claim current-repo line, token, cost, or time savings from shortcut marker counts.",
                "Do not treat shortcut marker counts as benchmark savings.",
            ],
            "benchmarkRoute": {
                "command": "shipguard lean gain --path <repo> --out <lean-gain-out> --shipguard-eval --shareable",
                "expectedArtifact": "lean-gain.json and lean-gain.md",
                "answers": "What benchmark-backed lean-code direction can be shown without claiming current-repo savings?",
                "proofBoundary": "Benchmark direction is separate from this shortcut-ledger evidence and still does not measure this repo without a matched baseline.",
            },
        },
        "scanScope": scan_scope,
        "nextActions": [
            "Start with the Rot-Risk Review top row before opening source for another inspection pass.",
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
            "Does each rot-risk row give the exact next action and proof to prevent trigger rot?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    ledger = report.get("leanDebtLedger", {})
    summary = ledger.get("summary", {})
    marker_review = report.get("markerVisibilityReview", {})
    marker_summary = marker_review.get("summary", {}) if isinstance(marker_review, dict) else {}
    visibility_rows = marker_review.get("visibilityRows", []) if isinstance(marker_review, dict) else []
    rot_review = report.get("rotRiskReview", {})
    rot_summary = rot_review.get("summary", {}) if isinstance(rot_review, dict) else {}
    rot_rows = rot_review.get("prioritizedRows", []) if isinstance(rot_review, dict) else []
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
        f"- Omitted state unknown: `{str(marker_summary.get('omittedStateUnknown', False)).lower()}`",
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
            "## Rot-Risk Review",
            "",
            f"- Top risk location: {rot_summary.get('topRiskLocation') or '-'}",
            f"- Top risk reason: {rot_summary.get('topRiskReason') or '-'}",
            f"- High-risk rows: {rot_summary.get('highRiskRows', 0)}",
            f"- Review-risk rows: {rot_summary.get('reviewRiskRows', 0)}",
            f"- Tracked rows: {rot_summary.get('trackedRows', 0)}",
            f"- Missing ceiling rows: {rot_summary.get('missingCeilingRows', 0)}",
            f"- Missing upgrade-trigger rows: {rot_summary.get('missingUpgradeTriggerRows', 0)}",
            f"- Trigger-watch contract rows: {rot_summary.get('triggerWatchContractRows', 0)}",
            f"- Missing trigger-watch contracts: {rot_summary.get('missingTriggerWatchContractRows', 0)}",
            f"- Tracked trigger-watch rows: {rot_summary.get('trackedTriggerWatchRows', 0)}",
            f"- Missing trigger definitions: {rot_summary.get('missingTriggerDefinitionRows', 0)}",
            f"- Omitted by limit: {rot_summary.get('omittedByLimit', 0)}",
            f"- Omitted risk unknown: `{str(rot_summary.get('omittedRiskUnknown', False)).lower()}`",
            f"- Top trigger-watch action: {rot_summary.get('topTriggerWatchAction') or '-'}",
            f"- Coverage boundary: {rot_review.get('coverageBoundary', '')}",
            f"- Policy: {rot_review.get('policy', '')}",
            "",
            "| Rank | Risk | Status | Marker | Location | Rot Reason | Next Action | Proof Guidance |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in rot_rows:
        lines.append(
            f"| {item.get('rank', '')} | {item.get('riskLevel', '')} | {item.get('status', '')} | "
            f"`{item.get('marker', '')}` | {item.get('location', '')} | "
            f"{str(item.get('rotReason', '')).replace('|', '\\|')} | "
            f"{str(item.get('nextAction', '')).replace('|', '\\|')} | "
            f"{str(item.get('proofGuidance', '')).replace('|', '\\|')} |"
        )
    if not rot_rows:
        lines.append("| 0 | tracked | pass | - | - | No shortcut markers found. | Keep Lean Review on active diffs. | No marker proof needed. |")
    lines.extend(
        [
            "",
            "## Trigger-Watch Contracts",
            "",
            "| Rank | Trigger State | Location | Trigger Condition | Exact Next Action | Check Route | Proof Artifact | Stop Condition |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in rot_rows:
        contract = item.get("triggerWatchContract") if isinstance(item.get("triggerWatchContract"), dict) else {}
        lines.append(
            f"| {item.get('rank', '')} | {contract.get('triggerState', '')} | {item.get('location', '')} | "
            f"{str(contract.get('triggerCondition', '')).replace('|', '\\|')} | "
            f"{str(contract.get('exactNextAction', '')).replace('|', '\\|')} | "
            f"{str(contract.get('checkRoute', '')).replace('|', '\\|')} | "
            f"{str(contract.get('proofArtifact', '')).replace('|', '\\|')} | "
            f"{str(contract.get('stopCondition', '')).replace('|', '\\|')} |"
        )
    if not rot_rows:
        lines.append("| 0 | watch-trigger | - | No marker trigger to watch. | Keep Lean Review on active diffs. | No check route needed. | No marker proof needed. | No shortcut cleanup is open. |")
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
    boundary = report.get("currentRepoBoundary", {})
    benchmark_route = boundary.get("benchmarkRoute", {}) if isinstance(boundary, dict) else {}
    lines.extend(
        [
            "",
            "## Benchmark Savings Boundary",
            "",
            f"- Per-repo savings claim: `{boundary.get('perRepoSavingsClaim', 'not-computed')}`",
            f"- Evidence type: `{boundary.get('evidenceType', 'shortcut-ledger-only')}`",
            f"- Reason: {boundary.get('reason', '')}",
            "- Do not claim current-repo line, token, cost, or time savings from shortcut marker counts.",
            "- Do not treat shortcut marker counts as benchmark savings.",
            f"- Benchmark route: `{benchmark_route.get('command', 'shipguard lean gain --path <repo> --out <lean-gain-out> --shipguard-eval --shareable')}`",
            f"- Benchmark artifact: {benchmark_route.get('expectedArtifact', 'lean-gain.json and lean-gain.md')}",
            f"- Boundary: {benchmark_route.get('proofBoundary', '')}",
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
    (out / "lean-debt.json").write_text(json_text, encoding="utf-8")
    (out / "lean-debt.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
