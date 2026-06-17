#!/usr/bin/env python3
"""Self-advancing iOS ShipGuard goal loop."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1

GOALS: list[dict[str, Any]] = [
    {
        "id": "shipguard-ios-doctor",
        "phase": "Phase 1: App Understanding",
        "title": "Implement iOS Doctor",
        "objective": "Discover the app's Xcode projects, workspaces, schemes, targets, deployment targets, Swift versions, test plans, and package managers before Codex edits code.",
        "deliverables": [
            "`shipguard ios doctor --path <repo> --out <dir>`",
            "JSON and Markdown app topology report",
            "fixture coverage for an app target plus extension-like source",
        ],
        "proof": [
            "./tests/ios_doctor_test.sh",
            "./tests/ios_inventory_test.sh",
            "./bin/shipguard validate",
        ],
    },
    {
        "id": "shipguard-target-risk-map",
        "phase": "Phase 1: App Understanding",
        "title": "Map Target Risk Surfaces",
        "objective": "Attach Info.plists, entitlements, privacy manifests, StoreKit files, widgets, App Intents, Live Activities, app groups, and background modes to the target that owns them.",
        "deliverables": [
            "per-target risk classification in the iOS inventory report",
            "extension/widget/intent/shared-store detection",
            "ask-before-editing gates tied to target ownership",
        ],
        "proof": [
            "./tests/ios_inventory_test.sh",
            "./tests/package_release_test.sh",
        ],
    },
    {
        "id": "shipguard-guided-plan",
        "phase": "Phase 2: Guided Planning",
        "title": "Generate Codex-Ready iOS Plans",
        "objective": "Turn app facts, selected mode, blocked questions, owner files, and proof route into a concise Codex task brief.",
        "deliverables": [
            "`shipguard ios plan --mode <mode> --inventory <json> --out <file>`",
            "mode-specific blocked questions",
            "Codex-native handoff text for XcodeBuildMCP, inline comments, and worktrees",
        ],
        "proof": [
            "./tests/ios_plan_test.sh",
            "./tests/cli_smoke_test.sh",
        ],
    },
    {
        "id": "shipguard-proof-router",
        "phase": "Phase 3: Proof Loop",
        "title": "Route iOS Proof",
        "objective": "Select the smallest honest proof lane for a ShipGuard plan: source, build, simulator, StoreKit, privacy, TestFlight, physical device, or blocked manual evidence.",
        "deliverables": [
            "`shipguard ios prove --plan <file> --out <dir>`",
            "proof checklist JSON and Markdown",
            "manual blocker language for device, account, and App Store Connect proof",
        ],
        "proof": [
            "./tests/ios_prove_test.sh",
            "./bin/shipguard docs-check docs --out /tmp/shipguard-proof-docs",
        ],
    },
    {
        "id": "shipguard-ios-preview-bridge",
        "phase": "Phase 3: Proof Loop",
        "title": "Preview iOS App In Codex",
        "objective": "Serve a booted iOS Simulator screenshot into Codex's in-app browser, capture click, right-click context-menu, and note receipts, and route visual feedback back into the ShipGuard proof loop.",
        "deliverables": [
            "`shipguard ios preview --out <dir>`",
            "localhost phone preview for Codex browser comments",
            "session JSON, screenshot, and typed preview event receipts",
            "copy-ready handoff.md with target resolution, receipts, and safety rules",
            "plugin mode routing and docs for the native-panel boundary",
        ],
        "proof": [
            "./tests/ios_preview_test.sh",
            "./bin/shipguard docs-check docs/ios-preview.md --out /tmp/shipguard-preview-docs",
        ],
    },
    {
        "id": "shipguard-devspace-mcp",
        "phase": "Phase 3: Proof Loop",
        "title": "Bridge ShipGuard Preview To ChatGPT",
        "objective": "Expose the iOS preview bridge through a ShipGuard Devspace MCP/App connector with a versioned widget resource, visual event tools, target resolution, UI snapshot target matching, production-readiness reporting, and Codex handoff preparation.",
        "deliverables": [
            "`shipguard ios devspace --port <port>`",
            "`shipguard ios target-match --handoff <handoff.json> --snapshot <ui.json>`",
            "HTTP `/mcp` endpoint for ChatGPT Developer Mode",
            "stdio MCP mode for the iOS ShipGuard Codex plugin",
            "`ui://widget/shipguard-preview-v2.html` phone preview widget resource and screenshot proxy",
            "tools for preview start, state, screenshots, events, Markdown handoff, target resolution, target matching, simulator list, production readiness, and Codex prompt preparation",
        ],
        "proof": [
            "./tests/ios_target_match_test.sh",
            "./tests/shipguard_devspace_mcp_test.sh",
            "python3 <plugin-creator>/scripts/validate_plugin.py plugins/ios-shipguard",
            "./bin/shipguard docs-check docs/shipguard-devspace.md --out /tmp/shipguard-devspace-docs",
        ],
    },
    {
        "id": "shipguard-codex-handoff-supervisor",
        "phase": "Phase 3: Proof Loop",
        "title": "Supervise Codex Handoffs",
        "objective": "Prepare and optionally execute a guarded Codex app-server turn from the latest ShipGuard Devspace handoff after explicit local approval.",
        "deliverables": [
            "`shipguard ios codex-handoff --prompt-file <file> --out <dir>`",
            "prepared Codex app-server prompt, request plan, and JSONL message template",
            "explicit `--execute` path that initializes app-server, starts a thread, starts a turn, and records a transcript",
        ],
        "proof": [
            "./tests/ios_codex_handoff_test.sh",
            "./tests/shipguard_devspace_mcp_test.sh",
            "./bin/shipguard docs-check docs/shipguard-devspace.md --out /tmp/shipguard-supervisor-docs",
        ],
    },
    {
        "id": "shipguard-swift-modernization",
        "phase": "Phase 4: Modernization Intelligence",
        "title": "Audit Swift And SwiftUI Modernization",
        "objective": "Detect modernization opportunities for Swift 6 strict concurrency, actor isolation, Observation, SwiftData, async state, accessibility, localization, and Liquid Glass readiness.",
        "deliverables": [
            "`shipguard ios modernize --focus swift --path <repo> --out <dir>`",
            "Swift concurrency and SwiftUI modernization findings",
            "availability and fallback guidance for newer APIs",
        ],
        "proof": [
            "./tests/ios_modernize_test.sh",
            "./tests/package_release_test.sh",
        ],
    },
    {
        "id": "shipguard-app-intelligence-audit",
        "phase": "Phase 4: Modernization Intelligence",
        "title": "Audit App Intelligence Surfaces",
        "objective": "Recommend App Intents, entities, Spotlight, Shortcuts, Siri, controls, widgets, and Apple Intelligence exposure based on actual app capabilities.",
        "deliverables": [
            "`shipguard ios app-intelligence --path <repo> --out <dir>`",
            "App Intents and entity coverage report",
            "system-surface opportunity matrix",
            "blocked questions for user-visible actions and data privacy",
        ],
        "proof": [
            "./tests/ios_app_intelligence_test.sh",
            "./bin/shipguard validate",
        ],
    },
    {
        "id": "shipguard-ai-capability-audit",
        "phase": "Phase 4: Modernization Intelligence",
        "title": "Audit AI Capability Choices",
        "objective": "Choose between Foundation Models, Core AI, Core ML, OpenAI API, or no AI based on privacy, latency, device support, cost, fallback, and feature value.",
        "deliverables": [
            "`shipguard ios ai-readiness --path <repo> --out <dir>`",
            "AI capability decision report",
            "on-device versus cloud tradeoff table",
            "privacy and fallback questions before implementation",
        ],
        "proof": [
            "./tests/ios_ai_readiness_test.sh",
            "./bin/shipguard docs-check docs/ios-shipguard.md --out /tmp/shipguard-ai-docs",
        ],
    },
    {
        "id": "shipguard-privacy-security-redaction",
        "phase": "Phase 5: Privacy, Security, And Distribution",
        "title": "Harden Privacy And Security Reports",
        "objective": "Redact sensitive iOS project data from reports and threat-model plugin execution, local marketplace trust, generated artifacts, screenshots, logs, and uploads.",
        "deliverables": [
            "`shipguard ios redact --in <file-or-dir> --out <file-or-dir>`",
            "security threat model for ShipGuard plugin/runtime surfaces",
            "tests for local path, team ID, bundle ID, token, and account redaction",
        ],
        "proof": [
            "./tests/ios_redaction_test.sh",
            "./tests/safe_paths_test.sh",
        ],
    },
    {
        "id": "shipguard-evals",
        "phase": "Phase 6: Evals And Quality Gates",
        "title": "Evaluate ShipGuard Behavior",
        "objective": "Grade whether ShipGuard catches missing questions, routes the right mode, avoids false proof claims, and produces useful Codex briefs.",
        "deliverables": [
            "`shipguard ios eval --cases evals/ios_shipguard_cases.jsonl --out <dir>`",
            "deterministic ShipGuard eval cases",
            "optional OpenAI trace/eval harness guidance",
            "quality gate for mode routing and proof honesty",
        ],
        "proof": [
            "./tests/ios_shipguard_eval_test.sh",
            "python3 evals/run_local.py  # expected no-key skip or live run when configured",
        ],
    },
    {
        "id": "shipguard-plugin-polish",
        "phase": "Phase 6: Evals And Quality Gates",
        "title": "Polish Plugin Packaging",
        "objective": "Make iOS ShipGuard easy to install, inspect, validate, package, and try from a clean checkout.",
        "deliverables": [
            "plugin metadata and install docs",
            "`shipguard ios demo --out <dir>` clean first-run demo path",
            "release package assertions for every ShipGuard artifact",
        ],
        "proof": [
            "./tests/ios_shipguard_demo_test.sh",
            "python3 <plugin-creator>/scripts/validate_plugin.py plugins/ios-shipguard",
            "./tests/package_release_test.sh",
        ],
    },
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def catalog_digest() -> str:
    payload = json.dumps(GOALS, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def fail(message: str) -> None:
    print(f"ios-goals: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"state file not found: {path}; run ios goals init first")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"state file is not valid JSON: {exc}")
    if state.get("schema_version") != SCHEMA_VERSION:
        fail(f"unsupported state schema: {state.get('schema_version')}")
    if state.get("catalog_digest") != catalog_digest():
        fail("goal catalog changed; run ios goals init --force to refresh the loop state")
    return state


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def new_state() -> dict[str, Any]:
    goals = []
    for index, goal in enumerate(GOALS):
        item = dict(goal)
        item["index"] = index
        item["status"] = "pending"
        item["receipts"] = []
        goals.append(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_digest": catalog_digest(),
        "generated_at": utc_now(),
        "updated_at": utc_now(),
        "current_index": 0,
        "goals": goals,
    }


def current_goal(state: dict[str, Any]) -> dict[str, Any] | None:
    goals = state["goals"]
    index = state["current_index"]
    if index >= len(goals):
        return None
    return goals[index]


def catalog_goal(goal_id: str) -> dict[str, Any]:
    for index, goal in enumerate(GOALS):
        if goal["id"] == goal_id:
            item = dict(goal)
            item["index"] = index
            item["status"] = "pending"
            item["receipts"] = []
            return item
    fail(f"unknown goal: {goal_id}")


def advance_to_next_pending(state: dict[str, Any]) -> None:
    goals = state["goals"]
    index = state["current_index"]
    while index < len(goals) and goals[index]["status"] == "completed":
        index += 1
    state["current_index"] = index
    state["updated_at"] = utc_now()


def render_goal(goal: dict[str, Any] | None, state_path: Path) -> str:
    if goal is None:
        return "\n".join(
            [
                "# iOS ShipGuard Goal Loop Complete",
                "",
                "All ShipGuard goals in the local catalog are complete.",
                "",
                "Run a full release validation before claiming the product is complete:",
                "",
                "```bash",
                "./bin/shipguard validate",
                "./tests/package_release_test.sh",
                "```",
                "",
            ]
        )

    lines = [
        f"# iOS ShipGuard Goal: {goal['title']}",
        "",
        f"- Goal id: `{goal['id']}`",
        f"- Phase: {goal['phase']}",
        f"- Status: {goal['status']}",
        "",
        "```text",
        f"/goal Implement {goal['id']} for iOS ShipGuard: {goal['objective']} Deliver the listed artifacts, run the required proof, record evidence, then complete this goal so the next ShipGuard goal starts automatically.",
        "```",
        "",
        "## Objective",
        "",
        goal["objective"],
        "",
        "## Deliverables",
        "",
    ]
    lines.extend(f"- {item}" for item in goal["deliverables"])
    lines.extend(["", "## Required Proof", ""])
    lines.extend(f"- `{item}`" for item in goal["proof"])
    lines.extend(
        [
            "",
            "## Complete And Advance",
            "",
            "When the proof exists, advance the loop with:",
            "",
            "```bash",
            f"./bin/shipguard ios goals complete --state {state_path} --goal {goal['id']} --evidence <proof-path-or-command> --out NEXT_SHIPGUARD_GOAL.md",
            "```",
            "",
            "The command records a completion receipt and writes the next goal automatically.",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_print(markdown: str, out: str | None) -> None:
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        print(f"wrote: {path}")
    else:
        print(markdown, end="")


def command_init(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    if state_path.exists() and not args.force:
        fail(f"state file already exists: {state_path}; use --force to overwrite")
    state = new_state()
    write_state(state_path, state)
    print(f"wrote: {state_path}")
    if args.out:
        write_or_print(render_goal(current_goal(state), state_path), args.out)


def command_status(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    state = load_state(state_path)
    goal = current_goal(state)
    completed = sum(1 for item in state["goals"] if item["status"] == "completed")
    total = len(state["goals"])
    lines = [
        "# iOS ShipGuard Goal Loop Status",
        "",
        f"- State: `{state_path}`",
        f"- Completed: {completed}/{total}",
        f"- Current goal: `{goal['id']}`" if goal else "- Current goal: complete",
        "",
    ]
    write_or_print("\n".join(lines), args.out)


def command_next(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    state = load_state(state_path)
    write_or_print(render_goal(current_goal(state), state_path), args.out)


def command_emit(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    write_or_print(render_goal(catalog_goal(args.goal), state_path), args.out)


def command_complete(args: argparse.Namespace) -> None:
    state_path = Path(args.state)
    state = load_state(state_path)
    goal = current_goal(state)
    if goal is None:
        fail("all goals are already complete")
    if args.goal != goal["id"]:
        fail(f"current goal is {goal['id']}, not {args.goal}")
    if not args.evidence.strip():
        fail("--evidence must be non-empty")

    receipt = {
        "completed_at": utc_now(),
        "evidence": args.evidence,
    }
    if args.notes:
        receipt["notes"] = args.notes
    goal["status"] = "completed"
    goal["receipts"].append(receipt)
    advance_to_next_pending(state)
    write_state(state_path, state)
    print(f"completed: {args.goal}")
    next_goal = current_goal(state)
    if next_goal:
        print(f"next: {next_goal['id']}")
    else:
        print("next: complete")
    if args.out:
        write_or_print(render_goal(next_goal, state_path), args.out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the self-advancing iOS ShipGuard goal loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a ShipGuard goal state file")
    init.add_argument("--state", default=".shipguard/goals.json")
    init.add_argument("--out")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)

    status = subparsers.add_parser("status", help="Print goal loop status")
    status.add_argument("--state", default=".shipguard/goals.json")
    status.add_argument("--out")
    status.set_defaults(func=command_status)

    next_goal_parser = subparsers.add_parser("next", help="Print the current ShipGuard goal")
    next_goal_parser.add_argument("--state", default=".shipguard/goals.json")
    next_goal_parser.add_argument("--out")
    next_goal_parser.set_defaults(func=command_next)

    emit = subparsers.add_parser("emit", help="Print a specific ShipGuard catalog goal without changing state")
    emit.add_argument("--state", default=".shipguard/goals.json")
    emit.add_argument("--goal", required=True)
    emit.add_argument("--out")
    emit.set_defaults(func=command_emit)

    complete = subparsers.add_parser("complete", help="Complete the current goal and advance to the next one")
    complete.add_argument("--state", default=".shipguard/goals.json")
    complete.add_argument("--goal", required=True)
    complete.add_argument("--evidence", required=True)
    complete.add_argument("--notes")
    complete.add_argument("--out")
    complete.set_defaults(func=command_complete)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
