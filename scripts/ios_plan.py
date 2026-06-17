#!/usr/bin/env python3
"""Generate a Codex-ready iOS ShipGuard plan from inventory facts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1

MODES = {
    "auto",
    "permission-audit",
    "simulator-debug",
    "release-proof",
    "storekit-commerce",
    "widgets-intents-shared-store",
    "performance-audit",
    "preview-bridge",
    "preview-devspace",
    "privacy-security",
    "ui-polish",
}

MODE_LABELS = {
    "permission-audit": "Permission Audit",
    "simulator-debug": "Simulator Debug",
    "release-proof": "Release Proof",
    "storekit-commerce": "StoreKit Commerce",
    "widgets-intents-shared-store": "Widgets, Intents, And Shared Store",
    "performance-audit": "Performance Audit",
    "preview-bridge": "Preview Bridge",
    "preview-devspace": "Preview Devspace",
    "privacy-security": "Privacy Security",
    "ui-polish": "UI Polish",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-plan: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn iOS ShipGuard inventory into a Codex task brief.")
    parser.add_argument("--mode", default="auto", choices=sorted(MODES), help="Primary ShipGuard mode")
    parser.add_argument("--inventory", required=True, help="ios-inventory.json path")
    parser.add_argument("--out", required=True, help="Output Markdown file or directory")
    parser.add_argument("--title", default="iOS ShipGuard Plan", help="Plan title")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"file not found: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(loaded, dict):
        fail(f"expected JSON object: {path}")
    return loaded


def output_paths(out: Path) -> tuple[Path, Path]:
    if out.suffix.lower() == ".md":
        return out, out.with_suffix(".json")
    if out.suffix.lower() == ".json":
        return out.with_suffix(".md"), out
    return out / "ios-plan.md", out / "ios-plan.json"


def unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def surface_names(surfaces: list[dict[str, Any]]) -> list[str]:
    return unique([str(surface.get("surface", "")) for surface in surfaces])


def infer_mode(inventory: dict[str, Any]) -> str:
    surfaces = inventory.get("surfaces", [])
    needs_answer = [s for s in surfaces if s.get("status") == "needs-user-answer"]
    if any(s.get("kind") == "permission" for s in needs_answer):
        return "permission-audit"
    names = {str(s.get("surface", "")).lower() for s in surfaces}
    kinds = {str(s.get("kind", "")).lower() for s in surfaces}
    if "storekit" in names or "commerce" in kinds:
        return "storekit-commerce"
    if {"widgets", "app intents", "app groups"} & names:
        return "widgets-intents-shared-store"
    if any(s.get("risk") == "high" for s in surfaces):
        return "permission-audit"
    return "simulator-debug"


def mode_questions(mode: str) -> list[str]:
    return {
        "permission-audit": [
            "What user-visible feature justifies each permission?",
            "Which denied, limited, provisional, unavailable, and granted states must remain truthful?",
        ],
        "simulator-debug": [
            "What is the exact expected behavior and observed failure?",
            "Which simulator, OS version, account state, or seed data is required to reproduce it?",
        ],
        "release-proof": [
            "Which binary, version, build, commit, and release channel are being proven?",
            "Which claims require TestFlight, App Store Connect, physical-device, or human tester evidence?",
        ],
        "storekit-commerce": [
            "Which product IDs and entitlement states are in scope?",
            "Is proof StoreKit config, sandbox, TestFlight sandbox, or live App Store?",
        ],
        "widgets-intents-shared-store": [
            "Which target writes the data and which app, widget, intent, watch, or shared container target reads it?",
            "What stale-data behavior and migration path are acceptable for existing users?",
        ],
        "performance-audit": [
            "Which screen, gesture, launch path, or device behavior feels slow?",
            "Which device, display refresh rate, thermal state, power mode, seed data, and build configuration must be measured?",
        ],
        "preview-bridge": [
            "Which simulator, scheme, and app state should be previewed?",
            "Should the visual event become a source edit, semantic elementRef tap, or blocked release-proof claim?",
        ],
        "preview-devspace": [
            "Should Devspace attach to an existing preview URL or start one?",
            "Is this local Developer Mode testing, Codex plugin MCP, or production hosting research?",
        ],
        "privacy-security": [
            "Which private terms must be redacted before reports leave local proof space?",
            "Are screenshots approved for sharing, or should only redacted text leave the machine?",
        ],
        "ui-polish": [
            "Which compact, Dynamic Type, localization, denied, empty, loading, and failure states apply?",
            "Is any copy making a trust, privacy, alarm, release, or paid-access claim?",
        ],
    }[mode]


def proof_route_for(mode: str) -> dict[str, Any]:
    routes = {
        "permission-audit": {
            "lane": "source-plus-simulator",
            "commands": [
                "shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory",
                "XcodeBuildMCP build/run when UI permission copy changes",
            ],
            "manualEvidence": ["physical-device proof when permission or hardware behavior cannot be simulated"],
        },
        "simulator-debug": {
            "lane": "simulator",
            "commands": ["XcodeBuildMCP session_show_defaults", "XcodeBuildMCP build_run_sim", "XcodeBuildMCP snapshot_ui or logs"],
            "manualEvidence": ["account, seed data, or device state that Codex cannot create locally"],
        },
        "release-proof": {
            "lane": "release",
            "commands": ["local validation command chosen by the plan", "record build/version/commit identity"],
            "manualEvidence": ["TestFlight", "App Store Connect", "physical device", "human tester feedback"],
        },
        "storekit-commerce": {
            "lane": "storekit",
            "commands": ["shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory", "StoreKit config or sandbox entitlement checks"],
            "manualEvidence": ["sandbox account or live purchase evidence for purchase claims"],
        },
        "widgets-intents-shared-store": {
            "lane": "app-extension",
            "commands": ["shared container review", "app plus extension/widget state checks"],
            "manualEvidence": ["migration proof when persisted shared payloads change"],
        },
        "performance-audit": {
            "lane": "performance",
            "commands": [
                "XcodeBuildMCP session_show_defaults",
                "XcodeBuildMCP build_run_sim",
                "xcrun xctrace record --template 'Animation Hitches' or 'Time Profiler' when supported",
                "sample <app-pid> <seconds> -file <sample.txt> when xctrace is unavailable",
                "symbolicate sampled app frames with dSYM/atos when needed",
            ],
            "manualEvidence": [
                "physical-device Instruments trace for touch latency, ProMotion refresh, thermal pressure, replacement displays, audio, sensors, or wake-path timing",
                "before/after comparison on the same build configuration, route, seed data, and device state",
            ],
        },
        "preview-bridge": {
            "lane": "preview",
            "commands": [
                "shipguard ios preview --out /tmp/ios-shipguard-preview",
                "shipguard ios target-match --handoff <handoff.json> --snapshot <ui.json> --out <dir>",
            ],
            "manualEvidence": ["semantic elementRef confirmation before simulator taps"],
        },
        "preview-devspace": {
            "lane": "devspace",
            "commands": [
                "shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN",
                "production_readiness",
                "codex_prepare_handoff",
            ],
            "manualEvidence": ["explicit local approval before ios codex-handoff --execute"],
        },
        "privacy-security": {
            "lane": "privacy",
            "commands": ["shipguard ios redact --in <file-or-dir> --out <file-or-dir>"],
            "manualEvidence": ["screenshot sharing approval or local-only note"],
        },
        "ui-polish": {
            "lane": "ui",
            "commands": ["XcodeBuildMCP screenshot or UI snapshot proof", "accessibility and Dynamic Type review"],
            "manualEvidence": ["localized copy review when human language judgment is required"],
        },
    }
    return routes[mode]


def owner_files(inventory: dict[str, Any], selected_surfaces: list[dict[str, Any]]) -> list[str]:
    files: list[str] = []
    selected_names = set(surface_names(selected_surfaces))
    for surface in selected_surfaces:
        for match in surface.get("source_matches", []):
            if isinstance(match, dict) and match.get("file"):
                files.append(str(match["file"]))
        files.extend(str(path) for path in surface.get("project_files", []) if path)
        files.extend(str(item.get("file")) for item in surface.get("plist_keys", []) if isinstance(item, dict) and item.get("file"))
        files.extend(str(item.get("file")) for item in surface.get("entitlements", []) if isinstance(item, dict) and item.get("file"))
    for target in inventory.get("targets", []):
        if not isinstance(target, dict):
            continue
        target_surface_names = {
            str(surface.get("surface", "")) for surface in target.get("surfaces", []) if isinstance(surface, dict)
        }
        if not selected_names or not (selected_names & target_surface_names):
            continue
        files.extend(str(path) for path in target.get("info_plists", []) if path)
        files.extend(str(path) for path in target.get("entitlements", []) if path)
        files.extend(str(path) for path in target.get("storekit_configs", []) if path)
        files.extend(str(path) for path in target.get("privacy_manifests", []) if path)
        files.extend(str(path) for path in target.get("source_roots", []) if path)
    return unique(files)


def selected_surfaces_for_mode(inventory: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    surfaces = [surface for surface in inventory.get("surfaces", []) if isinstance(surface, dict)]
    if mode == "permission-audit":
        return [s for s in surfaces if s.get("kind") == "permission" or s.get("status") == "needs-user-answer"]
    if mode == "storekit-commerce":
        return [s for s in surfaces if s.get("kind") == "commerce" or s.get("surface") == "StoreKit"]
    if mode == "widgets-intents-shared-store":
        wanted = {"Widgets", "App Intents", "App Groups"}
        return [s for s in surfaces if s.get("surface") in wanted or s.get("kind") in {"extension", "system-integration"}]
    if mode == "release-proof":
        return surfaces
    if mode == "performance-audit":
        return surfaces
    if mode == "privacy-security":
        return [s for s in surfaces if s.get("risk") == "high" or s.get("status") == "needs-user-answer"]
    return surfaces


def target_summary(inventory: dict[str, Any], selected_surfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_names = set(surface_names(selected_surfaces))
    rows: list[dict[str, Any]] = []
    for target in inventory.get("targets", []):
        if not isinstance(target, dict):
            continue
        target_surface_names = {str(surface.get("surface", "")) for surface in target.get("surfaces", []) if isinstance(surface, dict)}
        if selected_names and not (selected_names & target_surface_names):
            continue
        rows.append(
            {
                "id": target.get("id"),
                "name": target.get("name"),
                "kind": target.get("kind"),
                "riskCounts": target.get("risk_counts", {}),
                "surfaces": sorted(target_surface_names & selected_names) if selected_names else sorted(target_surface_names),
            }
        )
    return rows


def build_plan(title: str, mode: str, inventory_path: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    selected_mode = infer_mode(inventory) if mode == "auto" else mode
    selected_surfaces = selected_surfaces_for_mode(inventory, selected_mode)
    needs_answer = [surface for surface in selected_surfaces if surface.get("status") == "needs-user-answer"]
    blocked_questions = unique(
        [str(surface.get("question")) for surface in needs_answer if surface.get("question")]
        + mode_questions(selected_mode)
    )
    route = proof_route_for(selected_mode)
    files = owner_files(inventory, selected_surfaces)
    plan = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios plan",
        "generatedAt": utc_now(),
        "title": title,
        "mode": selected_mode,
        "inventory": str(inventory_path),
        "project": inventory.get("project"),
        "status": "needs-user-answer" if needs_answer else "ready",
        "blockedQuestions": blocked_questions,
        "selectedSurfaces": [
            {
                "surface": surface.get("surface"),
                "kind": surface.get("kind"),
                "status": surface.get("status"),
                "risk": surface.get("risk"),
                "question": surface.get("question"),
                "owners": surface.get("owners", []),
            }
            for surface in selected_surfaces
        ],
        "ownerFiles": files,
        "targetSummary": target_summary(inventory, selected_surfaces),
        "proofRoute": route,
        "codexBrief": {
            "mode": selected_mode,
            "summary": f"Use {MODE_LABELS[selected_mode]} mode. Resolve blocked questions before editing, then run the smallest honest proof lane.",
            "mustDo": [
                "Read AGENTS.md before editing.",
                "Use the owner files and target summary as the initial edit boundary.",
                "Ask blocked questions before edits when status is needs-user-answer.",
                "For performance work, report profiler support/failures, sampled stacks, before/after validation, and device-only proof gaps.",
                "Do not claim release, purchase, device, App Store, or preview proof without the required evidence.",
            ],
            "validation": route["commands"],
            "remainingManualProof": route["manualEvidence"],
        },
    }
    return plan


def markdown_report(plan: dict[str, Any]) -> str:
    lines = [
        f"# {plan['title']}",
        "",
        f"- Mode: `{plan['mode']}`",
        f"- Status: `{plan['status']}`",
        f"- Inventory: `{plan['inventory']}`",
        "",
        "## Codex Brief",
        "",
        plan["codexBrief"]["summary"],
        "",
        "## Blocked Questions",
        "",
    ]
    for question in plan["blockedQuestions"]:
        lines.append(f"- {question}")
    lines.extend(["", "## Owner Files", ""])
    for file in plan["ownerFiles"][:30]:
        lines.append(f"- `{file}`")
    if len(plan["ownerFiles"]) > 30:
        lines.append(f"- ... {len(plan['ownerFiles']) - 30} more")
    lines.extend(["", "## Selected Surfaces", "", "| Surface | Kind | Status | Risk |", "| --- | --- | --- | --- |"])
    for surface in plan["selectedSurfaces"]:
        lines.append(
            f"| {surface.get('surface')} | {surface.get('kind')} | {surface.get('status')} | {surface.get('risk')} |"
        )
    lines.extend(["", "## Target Summary", "", "| Target | Kind | Surfaces |", "| --- | --- | --- |"])
    for target in plan["targetSummary"]:
        lines.append(f"| {target.get('name')} | {target.get('kind')} | {', '.join(target.get('surfaces') or []) or '-'} |")
    lines.extend(["", "## Proof Route", "", f"- Lane: `{plan['proofRoute']['lane']}`", "", "Commands:"])
    for command in plan["proofRoute"]["commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "Manual proof that remains outside static analysis:"])
    for item in plan["proofRoute"]["manualEvidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Must Do", ""])
    for item in plan["codexBrief"]["mustDo"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    inventory_path = Path(args.inventory)
    inventory = load_json(inventory_path)
    plan = build_plan(args.title, args.mode, inventory_path, inventory)
    markdown = markdown_report(plan)
    markdown_path, json_path = output_paths(Path(args.out))
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote: {markdown_path}")
    print(f"wrote: {json_path}")
    print(f"status: {plan['status']}")
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)


if __name__ == "__main__":
    main()
