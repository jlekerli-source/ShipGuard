#!/usr/bin/env python3
"""Route iOS ShipGuard proof from a generated plan."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-prove: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the smallest honest proof checklist for an iOS ShipGuard plan.")
    parser.add_argument("--plan", required=True, help="ios-plan.json path")
    parser.add_argument("--out", required=True, help="Output directory for ios-proof.md and ios-proof.json")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def load_plan(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"plan not found: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(loaded, dict) or loaded.get("tool") != "shipguard ios plan":
        fail(f"expected shipguard ios plan JSON: {path}")
    return loaded


def unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def surface_names(plan: dict[str, Any]) -> set[str]:
    return {str(surface.get("surface", "")) for surface in plan.get("selectedSurfaces", []) if isinstance(surface, dict)}


def blocker_text(plan: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if plan.get("status") == "needs-user-answer":
        blockers.append("Plan has blocked questions that must be answered before edits or proof claims.")
    mode = plan.get("mode")
    names = surface_names(plan)
    if mode == "release-proof":
        blockers.append("Release claims need build identity plus TestFlight, App Store Connect, physical-device, or human tester evidence.")
    if mode == "storekit-commerce":
        blockers.append("Purchase claims need StoreKit config, sandbox, TestFlight sandbox, or live-account evidence.")
    if mode in {"preview-bridge", "preview-devspace"}:
        blockers.append("Preview click coordinates are visual intent only; simulator input needs semantic elementRef proof.")
    if mode == "privacy-security":
        blockers.append("Screenshots stay local unless the user explicitly approves sharing them.")
    if {"AlarmKit", "Push Notifications", "NFC", "HealthKit", "HomeKit"} & names:
        blockers.append("Hardware, account, push, wake-path, or health/home data behavior may require physical-device proof.")
    return unique(blockers)


def checklist_for(plan: dict[str, Any]) -> list[dict[str, str]]:
    mode = str(plan.get("mode"))
    route = plan.get("proofRoute", {})
    items: list[dict[str, str]] = [
        {
            "lane": "source",
            "status": "required",
            "evidence": "Review owner files and selected surfaces before editing.",
        },
        {
            "lane": "commands",
            "status": "required",
            "evidence": "; ".join(route.get("commands", [])) or "Run the selected proof route commands.",
        },
    ]
    if plan.get("status") == "needs-user-answer":
        items.append(
            {
                "lane": "blocked-questions",
                "status": "blocked-manual",
                "evidence": "Answer blocked questions before claiming implementation or proof completion.",
            }
        )
    if mode in {"permission-audit", "simulator-debug", "ui-polish", "preview-bridge"}:
        simulator_evidence = (
            "Use XcodeBuildMCP build/run, UI snapshot, screenshot, logs, or reproduction proof when UI/runtime behavior changes."
        )
        if mode == "permission-audit":
            simulator_evidence = (
                "Use XcodeBuildMCP build/run plus a simulator permission-state walkthrough when permission UI copy changes."
            )
        items.append(
            {
                "lane": "simulator",
                "status": "required",
                "evidence": simulator_evidence,
            }
        )
    if mode == "storekit-commerce":
        items.append(
            {
                "lane": "storekit",
                "status": "blocked-manual",
                "evidence": "StoreKit config can prove mapping; sandbox or live-account evidence is required for purchase claims.",
            }
        )
    if mode == "release-proof":
        items.append(
            {
                "lane": "release",
                "status": "blocked-manual",
                "evidence": "Record binary, version, build, commit, TestFlight/App Store Connect/device evidence, or a manual blocker.",
            }
        )
    if mode in {"preview-bridge", "preview-devspace"}:
        items.append(
            {
                "lane": "preview",
                "status": "required",
                "evidence": "Read handoff.md and use semantic target matching before simulator actions.",
            }
        )
    if mode == "privacy-security":
        items.append(
            {
                "lane": "privacy",
                "status": "required",
                "evidence": "Run ios redact and require remainingRiskCount 0 before sharing text reports.",
            }
        )
    if mode == "widgets-intents-shared-store":
        items.append(
            {
                "lane": "app-extension",
                "status": "required",
                "evidence": "Verify app plus extension/shared-store stale-data and migration behavior.",
            }
        )
    return items


def build_report(plan_path: Path, plan: dict[str, Any]) -> dict[str, Any]:
    blockers = blocker_text(plan)
    checklist = checklist_for(plan)
    has_blocked_item = any(item["status"] == "blocked-manual" for item in checklist)
    status = "blocked-manual" if blockers or has_blocked_item else "ready"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios prove",
        "generatedAt": utc_now(),
        "plan": str(plan_path),
        "planMode": plan.get("mode"),
        "status": status,
        "proofLane": plan.get("proofRoute", {}).get("lane"),
        "checklist": checklist,
        "manualBlockers": blockers,
        "claimBoundaries": [
            "Do not report timed-out, skipped, blocked, or manual-only evidence as a pass.",
            "Do not claim App Store, TestFlight, purchase, physical-device, or release proof without named evidence.",
            "Do not treat preview click coordinates as simulator action proof.",
        ],
    }


def markdown_report(report: dict[str, Any], plan: dict[str, Any]) -> str:
    lines = [
        "# iOS ShipGuard Proof Route",
        "",
        f"- Status: `{report['status']}`",
        f"- Plan mode: `{report['planMode']}`",
        f"- Proof lane: `{report['proofLane']}`",
        f"- Plan: `{report['plan']}`",
        "",
        "## Checklist",
        "",
        "| Lane | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for item in report["checklist"]:
        lines.append(f"| {item['lane']} | {item['status']} | {item['evidence']} |")
    lines.extend(["", "## Manual Blockers", ""])
    if report["manualBlockers"]:
        for blocker in report["manualBlockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Claim Boundaries", ""])
    for boundary in report["claimBoundaries"]:
        lines.append(f"- {boundary}")
    lines.extend(["", "## Blocked Questions From Plan", ""])
    for question in plan.get("blockedQuestions", []):
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    plan_path = Path(args.plan)
    plan = load_plan(plan_path)
    report = build_report(plan_path, plan)
    markdown = markdown_report(report, plan)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ios-proof.json"
    md_path = out_dir / "ios-proof.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    print(f"wrote: {json_path}")
    print(f"wrote: {md_path}")
    print(f"status: {report['status']}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)


if __name__ == "__main__":
    main()
