#!/usr/bin/env python3
"""Run deterministic iOS ShipGuard behavior eval cases."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "ios_shipguard_cases.jsonl"

MODE_COMMANDS = {
    "permission-audit": ["shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory"],
    "simulator-debug": ["XcodeBuildMCP session_show_defaults", "XcodeBuildMCP build/run and UI snapshot proof"],
    "release-proof": ["shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory"],
    "storekit-commerce": ["shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory"],
    "widgets-intents-shared-store": ["shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory"],
    "performance-audit": [
        "XcodeBuildMCP session_show_defaults",
        "XcodeBuildMCP build/run",
        "xcrun xctrace record when supported, otherwise sample/top/log evidence",
    ],
    "design-audit": [
        "shipguard ios design --path . --out /tmp/ios-shipguard-design",
        "shipguard ios preview --out /tmp/ios-shipguard-preview",
        "shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN",
    ],
    "preview-bridge": [
        "shipguard ios preview --out /tmp/ios-shipguard-preview",
        "shipguard ios target-match --handoff <handoff.json> --snapshot <ui.json> --out <dir>",
    ],
    "preview-devspace": [
        "shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN",
        "production_readiness",
        "codex_prepare_handoff",
    ],
    "privacy-security": ["shipguard ios redact --in <file-or-dir> --out <file-or-dir>"],
    "ui-polish": ["XcodeBuildMCP screenshot or UI snapshot proof", "accessibility and Dynamic Type review"],
}

MODE_PROOF = {
    "permission-audit": [
        "inventory finding review",
        "focused source diff",
        "simulator permission-state walkthrough when UI copy changes",
    ],
    "simulator-debug": ["build and launch", "UI hierarchy, screenshot, logs, or LLDB evidence", "rerun reproduction path"],
    "release-proof": [
        "source commit and build identity",
        "local validation logs",
        "TestFlight, physical-device, or App Store Connect evidence when claims require it",
        "blocked-manual when account or device proof is missing",
    ],
    "storekit-commerce": [
        "product mapping check",
        "entitlement-state source/test proof",
        "sandbox or live-account evidence for purchase claims",
    ],
    "widgets-intents-shared-store": [
        "shared container and entitlement review",
        "app plus extension state checks",
        "migration rehearsal when payload shape changes",
    ],
    "performance-audit": [
        "build and launch the same route being measured",
        "Animation Hitches or Time Profiler trace when supported",
        "sampled stacks plus symbolication when profiler templates are unavailable",
        "before/after comparison on the same build, device state, and seed data",
        "physical-device Instruments trace for smoothness claims",
    ],
    "design-audit": [
        "app-type inference or --app-type override",
        "design DNA, motion, haptics, and icon brief review",
        "ios preview evidence for visual claims",
        "Devspace handoff when ChatGPT should plan from the phone widget",
        "physical-device proof for haptic quality claims",
    ],
    "preview-bridge": [
        "preview-events.jsonl receipt",
        "handoff.md or /api/handoff.md review",
        "semantic elementRef target matching before simulator tap",
        "raw coordinate taps are not proof",
    ],
    "preview-devspace": [
        "/mcp initialize and tools/list",
        "preview_handoff_markdown",
        "preview_match_target",
        "production_readiness",
        "explicit Codex handoff, not automatic execution",
    ],
    "privacy-security": [
        "ios-redaction.json status pass",
        "remainingRiskCount equals 0",
        "screenshots stay local unless explicitly approved",
    ],
    "ui-polish": [
        "focused simulator screenshot or UI test",
        "accessibility label/identifier review when interactions change",
        "localization and Dynamic Type check when text or layout changes",
    ],
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-shipguard-eval: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic ShipGuard mode-routing and proof-honesty evals.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="JSONL case file")
    parser.add_argument("--out", help="Output directory for ios-shipguard-eval.md and ios-shipguard-eval.json")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def load_cases(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"cases file not found: {path}")
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(f"invalid JSON on {path}:{line_number}: {exc}")
            if not isinstance(case, dict) or not case.get("id"):
                fail(f"case on {path}:{line_number} must contain an id")
            cases.append(case)
    return cases


def case_text(case: dict[str, Any]) -> str:
    parts: list[str] = []
    input_data = case.get("input", {})
    for field in ("request", "inventory", "evidence", "previewEvent"):
        value = input_data.get(field)
        if isinstance(value, str):
            parts.append(value)
        elif value is not None:
            parts.append(json.dumps(value, sort_keys=True))
    return "\n".join(parts)


def contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def classify_mode(text: str) -> str:
    if contains_any(text, ["redact", "public issue", "share the", "token", "team id", "bundle id", "local path", "privacy leak"]):
        return "privacy-security"
    if contains_any(text, ["chatgpt", "gpt-5.5", "devspace", "mcp", "developer mode", "widget resource"]):
        return "preview-devspace"
    if contains_any(text, ["ui/ux", "design coherence", "design dna", "app icon", "imagegen", "haptic", "haptics", "motion", "animation blueprint", "visual dna", "app-type", "genre-aware"]):
        return "design-audit"
    if contains_any(text, ["preview", "right-click", "clicked", "handoff", "visual event", "tap-request"]):
        return "preview-bridge"
    if contains_any(text, ["testflight", "app store", "release", "approval", "app store connect", "binary", "shipping"]):
        return "release-proof"
    if contains_any(text, ["storekit", "purchase", "subscription", "restore", "entitlement", "product id", "billing"]):
        return "storekit-commerce"
    if contains_any(text, ["widget", "app intent", "shortcut", "spotlight", "siri", "app group", "shared container", "extension"]):
        return "widgets-intents-shared-store"
    if contains_any(text, ["fps", "frame", "hitch", "smooth", "stutter", "lag", "slow", "thermal", "proMotion", "instruments", "xctrace", "performance"]):
        return "performance-audit"
    if contains_any(text, ["permission", "camera", "microphone", "location", "photos", "healthkit", "usage description", "authorization"]):
        return "permission-audit"
    if contains_any(text, ["layout", "copy", "accessibility", "dynamic type", "localization", "voiceover", "polish"]):
        return "ui-polish"
    return "simulator-debug"


def questions_for(mode: str, text: str) -> list[str]:
    if mode == "permission-audit":
        surface = "this permission"
        lowered = text.lower()
        for candidate in ("camera", "microphone", "location", "photos", "healthkit", "notifications"):
            if candidate in lowered:
                surface = candidate
                break
        return [
            f"What user-visible feature needs {surface} permission?",
            "Which denied, limited, provisional, unavailable, and first-run states must be supported?",
        ]
    if mode == "release-proof":
        return [
            "Which binary, version, build, commit, and release channel are being proven?",
            "Who can provide TestFlight, App Store Connect, physical-device, or human tester evidence, or should this remain blocked-manual?",
        ]
    if mode == "storekit-commerce":
        return [
            "Which product IDs and entitlement states are in scope?",
            "Is the purchase proof StoreKit config, sandbox, TestFlight sandbox, or live App Store evidence?",
        ]
    if mode == "widgets-intents-shared-store":
        return [
            "Which target writes the data and which app, widget, intent, watch, or shared container target reads it?",
            "What stale-data behavior and migration path are acceptable for existing users?",
        ]
    if mode == "performance-audit":
        return [
            "Which screen, gesture, launch path, or device behavior feels slow?",
            "Which device, display refresh rate, thermal state, power mode, seed data, and build configuration must be measured?",
        ]
    if mode == "design-audit":
        return [
            "Is the inferred app type correct, or should --app-type override it?",
            "Is there an ios preview output directory, or should ShipGuard start the phone-shaped preview first?",
        ]
    if mode == "preview-bridge":
        return [
            "Which simulator, scheme, and app state should be previewed?",
            "Should this visual event become a source edit, semantic elementRef tap, or blocked release-proof claim?",
        ]
    if mode == "preview-devspace":
        return [
            "Should Devspace attach to an existing preview URL or start one?",
            "Is this local Developer Mode testing, Codex plugin MCP, or production hosting research?",
        ]
    if mode == "privacy-security":
        return [
            "Which private terms must be redacted before this report leaves local proof space?",
            "Are screenshots allowed to be shared, or should only redacted text reports leave the machine?",
        ]
    if mode == "ui-polish":
        return [
            "Which compact, Dynamic Type, localization, denied, empty, loading, and failure states apply?",
            "Is any copy making a trust, privacy, alarm, release, or paid-access claim?",
        ]
    return [
        "What is the exact expected behavior and observed failure?",
        "Which device, iOS version, account state, or seed data is required to reproduce it?",
    ]


def claim_boundaries_for(mode: str, text: str) -> list[str]:
    claims = ["Do not claim file edits or completion without validation evidence."]
    lowered = text.lower()
    if mode == "release-proof" or "app store connect" in lowered or "approval" in lowered:
        claims.append("Do not claim release approval without App Store Connect, TestFlight, device, or human tester evidence.")
    if mode == "storekit-commerce":
        claims.append("Do not claim purchase verification without StoreKit config, sandbox, TestFlight sandbox, or live-account evidence.")
    if mode == "performance-audit":
        claims.append("Do not claim 10/10 smoothness from source review alone; name profiler output, sampled stacks, before/after proof, and device-only gaps.")
    if mode == "design-audit":
        claims.append("Do not claim visual coherence, app icon quality, or haptic quality without preview, ImageGen review, or physical-device evidence as applicable.")
    if mode in {"preview-bridge", "preview-devspace"}:
        claims.append("Do not use raw coordinates as simulator proof or run Codex automatically from the preview.")
    if mode == "privacy-security":
        claims.append("Do not publish screenshots by default; redaction reduces disclosure risk but does not prove impossible leakage.")
    return claims


def build_brief(case: dict[str, Any]) -> dict[str, Any]:
    text = case_text(case)
    mode = classify_mode(text)
    lower_text = text.lower()
    blocked_reasons: list[str] = []
    if "needs-user-answer" in lower_text:
        blocked_reasons.append("inventory reports needs-user-answer")
    if "no app store connect" in lower_text or "appstoreconnect" in lower_text and "false" in lower_text:
        blocked_reasons.append("App Store Connect evidence is missing")
    if "no sandbox" in lower_text or "sandboxaccount" in lower_text and "false" in lower_text:
        blocked_reasons.append("sandbox or live purchase evidence is missing")
    if "raw coordinate" in lower_text or "tap-request" in lower_text:
        blocked_reasons.append("visual tap intent still needs semantic elementRef target resolution")

    questions = questions_for(mode, text)
    commands = MODE_COMMANDS[mode]
    proof = MODE_PROOF[mode]
    claim_boundaries = claim_boundaries_for(mode, text)
    next_steps = [
        "Ask required blocked questions before editing when answers are missing.",
        "Run the smallest proof lane that matches the selected mode.",
        "Report remaining manual proof instead of converting missing evidence into a pass.",
    ]

    return {
        "mode": mode,
        "blockedReasons": blocked_reasons,
        "questions": questions,
        "commands": commands,
        "proofBoundaries": proof,
        "claimBoundaries": claim_boundaries,
        "nextSteps": next_steps,
    }


def searchable_text(brief: dict[str, Any]) -> str:
    return json.dumps(brief, sort_keys=True).lower()


def grade_case(case: dict[str, Any]) -> dict[str, Any]:
    brief = build_brief(case)
    expected = case.get("expect", {})
    text = searchable_text(brief)
    missing: list[str] = []
    forbidden: list[str] = []

    expected_mode = expected.get("mode")
    if expected_mode and brief["mode"] != expected_mode:
        missing.append(f"mode:{expected_mode}")

    for field in ("mustAsk", "mustInclude", "proofMustInclude"):
        for term in expected.get(field, []):
            if term.lower() not in text:
                missing.append(term)
    for term in expected.get("mustNotInclude", []):
        if term.lower() in text:
            forbidden.append(term)

    return {
        "id": case["id"],
        "status": "pass" if not missing and not forbidden else "fail",
        "mode": brief["mode"],
        "missing": missing,
        "forbidden": forbidden,
        "brief": brief,
    }


def build_report(cases_path: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    results = [grade_case(case) for case in cases]
    failed = [result for result in results if result["status"] != "pass"]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios eval",
        "generatedAt": utc_now(),
        "cases": cases_path.name,
        "status": "pass" if not failed else "fail",
        "caseCount": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# iOS ShipGuard Eval",
        "",
        f"- Status: {report['status']}",
        f"- Cases: {report['caseCount']}",
        f"- Passed: {report['passed']}",
        f"- Failed: {report['failed']}",
        "",
        "| Case | Status | Mode | Missing | Forbidden |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in report["results"]:
        missing = ", ".join(result["missing"]) if result["missing"] else "-"
        forbidden = ", ".join(result["forbidden"]) if result["forbidden"] else "-"
        lines.append(f"| {result['id']} | {result['status']} | {result['mode']} | {missing} | {forbidden} |")
    lines.extend(
        [
            "",
            "## Quality Gates",
            "",
            "- Mode routing must match the expected primary ShipGuard mode.",
            "- Missing product or proof answers must appear as questions or blockers.",
            "- Release, StoreKit, and preview cases must not convert missing evidence into proof claims.",
            "- Briefs must include at least one concrete command or proof lane.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    cases_path = Path(args.cases)
    cases = load_cases(cases_path)
    report = build_report(cases_path, cases)
    markdown = markdown_report(report)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ios-shipguard-eval.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (out_dir / "ios-shipguard-eval.md").write_text(markdown, encoding="utf-8")
        print(f"wrote: {out_dir / 'ios-shipguard-eval.json'}")
        print(f"wrote: {out_dir / 'ios-shipguard-eval.md'}")
        print(f"status: {report['status']}")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)

    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
