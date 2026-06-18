#!/usr/bin/env python3
"""Audit App Intents and system intelligence surfaces for iOS projects."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope
import ios_shareable


SCHEMA_VERSION = 1
MARKDOWN_TYPE_LIMIT = 40
MARKDOWN_ACTION_LIMIT = 20
MARKDOWN_ENTITY_LIMIT = 20
MARKDOWN_FINDING_LIMIT = 20


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-app-intelligence: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit App Intents, entities, shortcuts, Siri, Spotlight, widgets, controls, and Apple Intelligence exposure."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-app-intelligence.md and ios-app-intelligence.json")
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
        "note": "Use --shareable before moving this app-intelligence report into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring."
        if not shareable
        else "Report fields are intended to avoid local absolute paths for external sharing.",
    }


def should_skip_dir(path: Path) -> bool:
    return ios_scan_scope.should_skip_dir(path)


def iter_files(root: Path) -> list[Path]:
    return ios_scan_scope.iter_files(root).files


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def line_record(path: Path, root: Path, line_number: int, evidence: str) -> dict[str, Any]:
    return {"file": rel(path, root), "line": line_number, "evidence": evidence.strip()}


def detect_imports(text: str) -> list[str]:
    return unique_sorted(re.findall(r"^\s*import\s+([A-Za-z0-9_]+)\b", text, re.M))


def extract_type_name(line: str, protocol: str) -> str | None:
    match = re.search(
        rf"\b(?:struct|class|final\s+class|enum|actor)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[^{{\n]*\b{re.escape(protocol)}\b",
        line,
    )
    if not match:
        return None
    return match.group(1)


def add_type(
    collection: list[dict[str, Any]],
    seen: set[tuple[str, str, int]],
    *,
    type_name: str,
    kind: str,
    path: Path,
    root: Path,
    line_number: int,
    evidence: str,
) -> None:
    key = (kind, type_name, line_number)
    if key in seen:
        return
    seen.add(key)
    collection.append(
        {
            "name": type_name,
            "kind": kind,
            "file": rel(path, root),
            "line": line_number,
            "evidence": evidence.strip(),
        }
    )


def add_detection(
    collection: list[dict[str, Any]],
    *,
    surface: str,
    token: str,
    path: Path,
    root: Path,
    line_number: int,
    evidence: str,
) -> None:
    collection.append(
        {
            "surface": surface,
            "token": token,
            "file": rel(path, root),
            "line": line_number,
            "evidence": evidence.strip(),
        }
    )


def scan_swift_files(root: Path, swift_files: list[Path]) -> dict[str, Any]:
    types: list[dict[str, Any]] = []
    detections: list[dict[str, Any]] = []
    imports: dict[str, list[str]] = {}
    seen_types: set[tuple[str, str, int]] = set()
    counters = {
        "appIntentCount": 0,
        "appEntityCount": 0,
        "appEnumCount": 0,
        "entityQueryCount": 0,
        "shortcutsProviderCount": 0,
        "widgetCount": 0,
        "controlCount": 0,
        "spotlightCount": 0,
        "siriLegacyCount": 0,
        "assistantSchemaCount": 0,
        "openAppIntentCount": 0,
        "parameterCount": 0,
    }

    protocol_map = {
        "AppIntent": "appIntentCount",
        "AppEntity": "appEntityCount",
        "AppEnum": "appEnumCount",
        "EntityQuery": "entityQueryCount",
        "AppShortcutsProvider": "shortcutsProviderCount",
        "Widget": "widgetCount",
        "WidgetBundle": "widgetCount",
        "ControlWidget": "controlCount",
        "ControlConfigurationIntent": "controlCount",
        "WidgetConfigurationIntent": "appIntentCount",
    }

    token_map = [
        ("Shortcuts", "AppShortcut", "shortcutsProviderCount"),
        ("Shortcuts", "AppShortcutsProvider", "shortcutsProviderCount"),
        ("Siri", "AssistantSchema", "assistantSchemaCount"),
        ("Siri", "AssistantIntent", "assistantSchemaCount"),
        ("Spotlight", "CoreSpotlight", "spotlightCount"),
        ("Spotlight", "CSSearchableItem", "spotlightCount"),
        ("Spotlight", "NSUserActivity", "spotlightCount"),
        ("Widgets", "WidgetConfiguration", "widgetCount"),
        ("Controls", "ControlWidget", "controlCount"),
        ("Controls", "ControlConfiguration", "controlCount"),
        ("Legacy SiriKit", "INIntent", "siriLegacyCount"),
        ("Legacy SiriKit", "SiriKit", "siriLegacyCount"),
        ("App Runtime Handoff", "openAppWhenRun", "openAppIntentCount"),
        ("Parameters", "@Parameter", "parameterCount"),
    ]

    for path in swift_files:
        text = read_text(path)
        rel_path = rel(path, root)
        imports[rel_path] = detect_imports(text)
        for index, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            for protocol, counter in protocol_map.items():
                type_name = extract_type_name(line, protocol)
                if type_name:
                    add_type(
                        types,
                        seen_types,
                        type_name=type_name,
                        kind=protocol,
                        path=path,
                        root=root,
                        line_number=index,
                        evidence=stripped,
                    )
                    counters[counter] += 1
            for surface, token, counter in token_map:
                if token in line:
                    add_detection(
                        detections,
                        surface=surface,
                        token=token,
                        path=path,
                        root=root,
                        line_number=index,
                        evidence=stripped,
                    )
                    counters[counter] += 1

    return {"types": types, "detections": detections, "imports": imports, "counters": counters}


def collect_doctor_facts(root: Path) -> dict[str, Any]:
    report = ios_doctor.build_report(root)
    target_names: list[str] = []
    source_tokens: list[str] = []
    for project in report.get("xcode_projects", []):
        target_names.extend(project.get("targets", []))
    for package in report.get("swift_packages", []):
        target_names.extend(package.get("targets", []))
    return {
        "targetNames": unique_sorted([str(item) for item in target_names]),
        "storeKitConfigs": report.get("storekit_configs", []),
        "privacyManifests": [item.get("path") for item in report.get("privacy_manifests", []) if isinstance(item, dict)],
        "sourceTokens": source_tokens,
    }


def infer_candidate_actions(types: list[dict[str, Any]], detections: list[dict[str, Any]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for item in types:
        if item["kind"] == "AppIntent":
            actions.append(
                {
                    "name": item["name"],
                    "source": f"{item['file']}:{item['line']}",
                    "recommendation": "Keep this intent narrow; decide whether it completes inline or opens the app through one explicit route.",
                }
            )
    tokens = {item["token"] for item in detections}
    if "WidgetConfiguration" in tokens and not any(action["name"].lower().startswith("configure") for action in actions):
        actions.append(
            {
                "name": "Configure widget content",
                "source": "WidgetKit",
                "recommendation": "Reuse an App Intent or AppEntity surface for widget configuration when users choose app content.",
            }
        )
    return actions


def infer_candidate_entities(types: list[dict[str, Any]], detections: list[dict[str, Any]], facts: dict[str, Any]) -> list[dict[str, str]]:
    if any(item["kind"] == "AppEntity" for item in types):
        return []
    tokens = {item["token"] for item in detections}
    candidates: list[dict[str, str]] = []
    if "WidgetConfiguration" in tokens or "Widget" in {item["kind"] for item in types}:
        candidates.append(
            {
                "name": "Widget destination or filter",
                "reason": "WidgetKit is present, so a small display-friendly entity can help widgets, Spotlight, and Shortcuts choose app content.",
            }
        )
    if facts["storeKitConfigs"]:
        candidates.append(
            {
                "name": "Product or entitlement",
                "reason": "StoreKit config exists; expose only safe subscription or entitlement state if the user explicitly wants purchase-related shortcuts.",
            }
        )
    if not candidates:
        candidates.append(
            {
                "name": "Primary app destination",
                "reason": "No AppEntity was detected; start with the smallest object the system needs for routing or disambiguation.",
            }
        )
    return candidates


def surface_row(surface: str, status: str, evidence: str, recommendation: str, proof: str) -> dict[str, str]:
    return {
        "surface": surface,
        "status": status,
        "evidence": evidence,
        "recommendation": recommendation,
        "proof": proof,
    }


def build_surface_matrix(counters: dict[str, int], types: list[dict[str, Any]], detections: list[dict[str, Any]]) -> list[dict[str, str]]:
    has_intent = counters["appIntentCount"] > 0
    has_entity = counters["appEntityCount"] > 0
    has_shortcuts = counters["shortcutsProviderCount"] > 0
    has_widget = counters["widgetCount"] > 0
    has_spotlight = counters["spotlightCount"] > 0
    has_controls = counters["controlCount"] > 0
    has_assistant_schema = counters["assistantSchemaCount"] > 0
    has_open_app = counters["openAppIntentCount"] > 0

    return [
        surface_row(
            "Shortcuts",
            "covered" if has_shortcuts else ("partial" if has_intent else "opportunity"),
            "AppShortcutsProvider or AppShortcut detected." if has_shortcuts else ("AppIntent exists, but no AppShortcutsProvider was detected." if has_intent else "No App Intent shortcut surface detected."),
            "Add AppShortcutsProvider entries for the first one to three high-value actions; keep phrases concrete and task-oriented.",
            "Build the app and confirm the shortcuts appear with expected titles, symbols, and parameters.",
        ),
        surface_row(
            "Siri",
            "covered" if has_assistant_schema else ("partial" if has_intent else "opportunity"),
            "Assistant schema tokens detected." if has_assistant_schema else ("AppIntent exists, but Siri phrasing and discoverability need review." if has_intent else "No Siri-ready action layer detected."),
            "Use clear verbs, display representations, and App Shortcut phrases before promising Siri or Apple Intelligence exposure.",
            "Run the intent or shortcut and record whether Siri routes to the expected action or app handoff.",
        ),
        surface_row(
            "Spotlight",
            "covered" if has_spotlight else ("partial" if has_entity else "opportunity"),
            "Spotlight indexing APIs detected." if has_spotlight else ("AppEntity exists but no Spotlight indexing was detected." if has_entity else "No AppEntity or Spotlight indexing detected."),
            "Add focused AppEntity display representations or Core Spotlight indexing only for content users should discover outside the app.",
            "Verify indexed item titles, privacy boundaries, and deep links on device or simulator.",
        ),
        surface_row(
            "Widgets",
            "covered" if has_widget else ("opportunity" if has_intent else "not-detected"),
            "WidgetKit surface detected." if has_widget else ("AppIntent exists and could back widget configuration or actions." if has_intent else "No widget surface detected."),
            "Reuse the App Intent and AppEntity model for widget configuration or actions when the same parameters make sense.",
            "Prove widget snapshot, timeline, stale-data, and tap-through behavior.",
        ),
        surface_row(
            "Controls",
            "covered" if has_controls else ("opportunity" if has_intent else "not-detected"),
            "ControlWidget or control configuration detected." if has_controls else ("No controls detected; existing App Intents may be reusable for Control Center or system controls." if has_intent else "No control-ready action detected."),
            "Only expose controls for actions with immediate, reversible, and clearly visible outcomes.",
            "Verify control execution, denied states, and app handoff behavior.",
        ),
        surface_row(
            "Apple Intelligence",
            "partial" if has_intent else "opportunity",
            "AppIntent bridge detected." if has_intent else "No AppIntent bridge detected.",
            "Model actions and entities with small, display-friendly types before claiming Apple Intelligence discoverability.",
            "Record which action, entity, and privacy boundaries were validated through the system surface.",
        ),
        surface_row(
            "App Runtime Handoff",
            "covered" if has_open_app else ("review" if has_intent else "not-detected"),
            "openAppWhenRun detected." if has_open_app else ("Intent exists; decide whether it completes inline or routes into the app." if has_intent else "No intent handoff model detected."),
            "Prefer one explicit app routing path instead of hidden globals or per-feature side channels.",
            "Run the intent and confirm the app opens or completes inline as designed.",
        ),
    ]


def finding(
    rule_id: str,
    severity: str,
    title: str,
    evidence: str,
    recommendation: str,
    proof_guidance: str,
) -> dict[str, str]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "title": title,
        "evidence": evidence,
        "recommendation": recommendation,
        "proofGuidance": proof_guidance,
    }


def build_findings(counters: dict[str, int], actions: list[dict[str, str]], entities: list[dict[str, str]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if counters["appIntentCount"] > 0 and counters["shortcutsProviderCount"] == 0:
        findings.append(
            finding(
                "app-intent-missing-shortcuts-provider",
                "review",
                "App Intent exists without discoverable App Shortcuts",
                f"{counters['appIntentCount']} App Intent type(s) detected; no AppShortcutsProvider detected.",
                "Add AppShortcutsProvider entries only for the first high-value actions users should run from Shortcuts, Siri, Spotlight, or widgets.",
                "Build and inspect Shortcuts/Siri discoverability for the chosen phrases, symbols, parameter labels, and denied or unavailable states.",
            )
        )
    if counters["appIntentCount"] > 0 and counters["appEntityCount"] == 0:
        findings.append(
            finding(
                "app-intent-missing-entity-surface",
                "opportunity",
                "No AppEntity surface detected",
                "No AppEntity type was detected.",
                "Add a small AppEntity only if the system needs to identify, display, search, or disambiguate app content.",
                "Prove the entity has a stable identifier, safe display representation, privacy-reviewed fields, and useful disambiguation behavior before exposing it.",
            )
        )
    if counters["appIntentCount"] > 0 and counters["openAppIntentCount"] == 0:
        findings.append(
            finding(
                "app-intent-handoff-undecided",
                "review",
                "Intent handoff model is not explicit",
                "No openAppWhenRun declaration was detected.",
                "Decide whether each intent completes inline or opens the app, and route open-app intents through one clear app entry path.",
                "Run the intent and record whether it completes inline or opens the exact app route with correct state restoration and error handling.",
            )
        )
    if counters["widgetCount"] > 0 and counters["appIntentCount"] > 0:
        findings.append(
            finding(
                "widget-intent-reuse-opportunity",
                "opportunity",
                "WidgetKit can reuse the App Intent surface",
                "WidgetKit and App Intents were both detected.",
                "Reuse the same action/entity model for widget configuration or widget actions when the parameters match.",
                "Verify widget configuration, timeline refresh, tap-through, stale-data handling, and shared entity display before claiming reuse works.",
            )
        )
    if actions and not entities:
        findings.append(
            finding(
                "system-surface-entity-candidates",
                "opportunity",
                "Entity candidates need product selection",
                "Candidate actions exist, but no entity candidates were inferred.",
                "Ask which user-visible objects should be exposed before creating entity types.",
                "Record the selected user-visible objects, privacy-safe fields, identifiers, and system-surface proof route before adding entity types.",
            )
        )
    return findings


def blocked_questions(counters: dict[str, int], candidate_entities: list[dict[str, str]]) -> list[str]:
    questions = [
        "Which one to three user-visible actions are valuable outside the app UI?",
        "For each action, should it complete inline or open the app to a specific route?",
        "What private data, account state, location, notification, purchase, or health context must never appear in a system phrase, Spotlight result, widget, or Siri response?",
    ]
    if counters["shortcutsProviderCount"] == 0:
        questions.append("What titles, phrases, symbols, and parameter labels should make the first App Shortcuts discoverable?")
    if candidate_entities:
        questions.append("Which candidate entity has a stable identifier and a safe display representation for system surfaces?")
    if counters["appIntentCount"] > 0:
        questions.append("Which build, Shortcuts, Siri, Spotlight, widget, or control proof is required before claiming the action is available system-wide?")
    return questions


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate ShipGuard app-intelligence report quality.",
            "Identify missing or noisy system-surface guidance.",
            "Create redacted public fixtures or eval cases in ShipGuard.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not create app-specific App Intents, widget, Siri, Spotlight, or controls tasks from this run.",
            "Do not present target-app findings as the active development goal.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Did the report distinguish existing system surfaces from optional opportunity areas?",
        "Were candidate actions and entities specific enough to improve ShipGuard fixtures without private app context?",
        "Did privacy guidance prevent overexposing account, purchase, notification, or private content?",
        "Which observation should become a public fixture or eval case before changing the rule again?",
    ]


def capped_items(items: list[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], int]:
    return items[:limit], max(0, len(items) - limit)


def build_report(root: Path, *, shipguard_eval: bool = False, shareable: bool = False) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")

    scan = ios_scan_scope.iter_files(root)
    files = scan.files
    swift_files = [path for path in files if path.suffix == ".swift"]
    scanned = scan_swift_files(root, swift_files)
    facts = collect_doctor_facts(root)
    types = scanned["types"]
    counters = scanned["counters"]
    detections = scanned["detections"]
    actions = infer_candidate_actions(types, detections)
    candidate_entities = infer_candidate_entities(types, detections, facts)
    surface_matrix = build_surface_matrix(counters, types, detections)
    findings = build_findings(counters, actions, candidate_entities)
    questions = blocked_questions(counters, candidate_entities)
    status = "review" if findings or questions else "pass"

    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios app-intelligence",
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "generatedAt": utc_now(),
        "shareability": shareability_block(shareable),
        "status": status,
        "summary": {
            "swiftFiles": len(swift_files),
            "intentCount": counters["appIntentCount"],
            "entityCount": counters["appEntityCount"],
            "shortcutsProviderCount": counters["shortcutsProviderCount"],
            "widgetCount": counters["widgetCount"],
            "controlCount": counters["controlCount"],
            "spotlightCount": counters["spotlightCount"],
            "assistantSchemaCount": counters["assistantSchemaCount"],
            "targetCount": len(facts["targetNames"]),
        },
        "scanScope": ios_scan_scope.summary(scan),
        "types": types,
        "detections": detections,
        "candidateActions": actions,
        "candidateEntities": candidate_entities,
        "systemSurfaceMatrix": surface_matrix,
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "findings": findings,
        "blockedQuestions": questions,
        "privacyReview": [
            "Do not expose account, location, notification, health, purchase, or private content through system phrases or indexed display text without explicit product approval.",
            "Keep AppEntity display fields narrower than the app's persistence model.",
            "Record proof for every claimed system surface; a Swift type alone is not user-visible availability proof.",
        ],
        "doctorFacts": facts,
    }
    if shipguard_eval and shareable:
        report = ios_shareable.redact_shipguard_eval_report(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# iOS App Intelligence Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Swift files: {summary['swiftFiles']}",
        f"- App Intents: {summary['intentCount']}",
        f"- App Entities: {summary['entityCount']}",
        f"- App Shortcuts providers: {summary['shortcutsProviderCount']}",
        f"- Widgets: {summary['widgetCount']}",
        f"- Skipped generated/proof/cache directories: {report['scanScope']['skippedDirectoryCount']}",
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
                "- Use findings to improve ShipGuard system-surface rules, docs, report shape, or eval fixtures.",
                "- Do not turn findings into target-app App Intents, widget, Siri, Spotlight, or controls tasks without a separate app-work request.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )
    if report["scanScope"]["skippedDirectories"]:
        lines.extend(["## Scan Scope", ""])
        for directory in report["scanScope"]["skippedDirectories"][:8]:
            lines.append(f"- Skipped `{directory}`")
        if report["scanScope"]["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")
        lines.append("")
    lines.extend(
        [
        "## App Intents And Entities",
        "",
        ]
    )
    if report["types"]:
        lines.extend(["| Kind | Name | Location |", "| --- | --- | --- |"])
        visible_types, hidden_types = capped_items(report["types"], MARKDOWN_TYPE_LIMIT)
        for item in visible_types:
            lines.append(f"| {item['kind']} | `{item['name']}` | `{item['file']}:{item['line']}` |")
        if hidden_types:
            lines.append(f"| note | `{hidden_types} more type(s) hidden from Markdown` | See ios-app-intelligence.json for the full list. |")
    else:
        lines.append("No App Intents, App Entities, App Enums, or App Shortcuts providers were detected.")

    lines.extend(["", "## System Surface Opportunity Matrix", "", "| Surface | Status | Evidence | Recommendation | Proof |", "| --- | --- | --- | --- | --- |"])
    for item in report["systemSurfaceMatrix"]:
        lines.append(f"| {item['surface']} | {item['status']} | {item['evidence']} | {item['recommendation']} | {item['proof']} |")

    lines.extend(["", "## Candidate Actions", ""])
    if report["candidateActions"]:
        visible_actions, hidden_actions = capped_items(report["candidateActions"], MARKDOWN_ACTION_LIMIT)
        for item in visible_actions:
            lines.append(f"- `{item['name']}` from {item['source']}: {item['recommendation']}")
        if hidden_actions:
            lines.append(f"- {hidden_actions} more candidate action(s) hidden from Markdown; see ios-app-intelligence.json for the full list.")
    else:
        lines.append("- No candidate actions were inferred from App Intents or widgets.")

    lines.extend(["", "## Candidate Entities", ""])
    if report["candidateEntities"]:
        visible_entities, hidden_entities = capped_items(report["candidateEntities"], MARKDOWN_ENTITY_LIMIT)
        for item in visible_entities:
            lines.append(f"- {item['name']}: {item['reason']}")
        if hidden_entities:
            lines.append(f"- {hidden_entities} more candidate entity record(s) hidden from Markdown; see ios-app-intelligence.json for the full list.")
    else:
        lines.append("- Existing AppEntity coverage was detected; review the JSON report for type locations.")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Finding | Recommendation | Proof Guidance |", "| --- | --- | --- | --- | --- |"])
        visible_findings, hidden_findings = capped_items(report["findings"], MARKDOWN_FINDING_LIMIT)
        for item in visible_findings:
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | {item['title']} | {item['recommendation']} | {item['proofGuidance']} |"
            )
        if hidden_findings:
            lines.append(
                f"| note | `markdown-cap` | {hidden_findings} more finding(s) hidden from Markdown | See ios-app-intelligence.json for the full list. | See JSON for proof guidance. |"
            )
    else:
        lines.append("No app-intelligence findings were detected.")

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Blocked Questions", ""])
    for question in report["blockedQuestions"]:
        lines.append(f"- {question}")

    lines.extend(["", "## Privacy Review", ""])
    for item in report["privacyReview"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-app-intelligence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "ios-app-intelligence.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-app-intelligence.md'}")
    print(f"wrote: {out_dir / 'ios-app-intelligence.json'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(root, shipguard_eval=args.shipguard_eval, shareable=args.shareable)
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
