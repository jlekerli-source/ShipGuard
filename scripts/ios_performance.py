#!/usr/bin/env python3
"""Scan iOS Swift projects for common app-side performance risks."""

from __future__ import annotations

import argparse
import ast
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


SCHEMA_VERSION = 1
MAX_FINDINGS_PER_RULE = 20

SEVERITY_RANK = {
    "high": 0,
    "review": 1,
    "opportunity": 2,
}
NUMERIC_BINOPS = {
    ast.Add: lambda left, right: left + right,
    ast.Sub: lambda left, right: left - right,
    ast.Mult: lambda left, right: left * right,
    ast.Div: lambda left, right: left / right,
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-performance: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit SwiftUI and runtime performance hotspots before Codex edits an iOS app."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-performance.md and ios-performance.json")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute project paths before moving the report into ChatGPT, GitHub, docs, benchmarks, or report-quality scoring.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def report_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return path.as_posix()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return f"<{placeholder}>"
    text = relative.as_posix()
    return text or "."


def eval_numeric_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = eval_numeric_ast(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        op = NUMERIC_BINOPS.get(type(node.op))
        if op is None:
            raise ValueError("unsupported operator")
        return float(op(eval_numeric_ast(node.left), eval_numeric_ast(node.right)))
    raise ValueError("unsupported numeric expression")


def numeric_interval(expression: str) -> float | None:
    cleaned = expression.strip()
    if not re.fullmatch(r"[0-9. /\t+\-*]+", cleaned):
        return None
    try:
        value = eval_numeric_ast(ast.parse(cleaned, mode="eval").body)
    except Exception:
        return None
    if value > 0:
        return value
    return None


def severity_for_interval(interval: float | None) -> str:
    if interval is None:
        return "review"
    if interval <= 1.0 / 30.0:
        return "high"
    if interval < 1.0:
        return "review"
    return "opportunity"


def severity_reason_for_interval(interval: float | None) -> str:
    if interval is None:
        return "Review because the TimelineView cadence could not be parsed statically; verify the actual redraw rate on the affected screen."
    if interval <= 1.0 / 30.0:
        return f"High because the periodic TimelineView cadence is {interval:.4g}s, at or faster than roughly 30 redraws per second."
    if interval < 1.0:
        return f"Review because the periodic TimelineView cadence is {interval:.4g}s, which can still redraw visible UI repeatedly."
    return f"Opportunity because the periodic TimelineView cadence is {interval:.4g}s and may be acceptable if it is user-visible."


def add_finding(findings: list[dict[str, Any]], finding: dict[str, Any]) -> None:
    rule_count = sum(1 for item in findings if item["ruleId"] == finding["ruleId"])
    if rule_count >= MAX_FINDINGS_PER_RULE:
        return
    findings.append(finding)


def make_finding(
    *,
    rule_id: str,
    severity: str,
    category: str,
    title: str,
    file: str,
    line: int,
    evidence: str,
    severity_reason: str,
    impact: str,
    recommendation: str,
    local_proof: str,
    manual_proof: str,
) -> dict[str, Any]:
    proof = f"Local proof: {local_proof} Manual/device proof: {manual_proof}"
    return {
        "ruleId": rule_id,
        "severity": severity,
        "category": category,
        "title": title,
        "file": file,
        "line": line,
        "evidence": evidence.strip(),
        "severityReason": severity_reason,
        "impact": impact,
        "recommendation": recommendation,
        "localProof": local_proof,
        "manualProof": manual_proof,
        "proof": proof,
    }


def nearby_contains(lines: list[str], index: int, pattern: str, before: int = 8) -> bool:
    start = max(0, index - before)
    text = "\n".join(lines[start : index + 1])
    return re.search(pattern, text) is not None


def scan_file(path: Path, root: Path, findings: list[dict[str, Any]], metrics: dict[str, int]) -> None:
    text = read_text(path)
    lines = text.splitlines()
    rel_path = rel(path, root)
    imports_swiftui = bool(re.search(r"^\s*import\s+SwiftUI\b", text, re.M))
    has_swiftui_view = imports_swiftui and bool(
        re.search(r":\s*View\b|var\s+body\s*:\s*some\s+View\b|@ViewBuilder\b|->\s*some\s+View\b", text)
    )

    if imports_swiftui:
        metrics["swiftuiFiles"] += 1

    shadow_window: list[int] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        line_number = index + 1

        timeline_match = re.search(r"TimelineView\s*\(\s*\.periodic\s*\([^)]*\bby:\s*([^,)]+)", line)
        if timeline_match:
            interval = numeric_interval(timeline_match.group(1))
            severity = severity_for_interval(interval)
            severity_reason = severity_reason_for_interval(interval)
            add_finding(
                findings,
                make_finding(
                    rule_id="swiftui-periodic-timeline",
                    severity=severity,
                    category="SwiftUI Rendering",
                    title="Review periodic TimelineView redraw cadence",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    severity_reason=severity_reason,
                    impact="Frequent TimelineView updates can redraw the view tree even when the visual change is small.",
                    recommendation="Use the slowest cadence that preserves the user-visible state; disable or lower cadence for Reduce Motion, inactive state, and non-critical ambience.",
                    local_proof="Compare the same route before and after in Simulator with Animation Hitches, Time Profiler, or a symbolicated sample fallback; verify inactive and Reduce Motion gates from source.",
                    manual_proof="Use physical-device Instruments before claiming 10/10 smoothness, touch latency, ProMotion behavior, thermal behavior, or display-specific performance.",
                ),
            )

        if ".repeatForever" in line:
            add_finding(
                findings,
                make_finding(
                    rule_id="swiftui-repeat-forever-animation",
                    severity="review",
                    category="SwiftUI Rendering",
                    title="Review continuous repeatForever animation",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    severity_reason="Review because repeatForever animation keeps the render loop active until gated by view visibility, user value, or Reduce Motion.",
                    impact="Always-on animations keep the renderer active and can combine poorly with large gradients, blur, material, or tab backgrounds.",
                    recommendation="Gate decorative motion behind Reduce Motion, active screen visibility, and measurable value; prefer static states for background ambience.",
                    local_proof="Record the affected screen at rest and during interaction, then compare sampled CPU/GPU pressure after reducing or gating the animation.",
                    manual_proof="Use physical-device Instruments before claiming battery, thermal, touch-latency, or ProMotion smoothness improvements.",
                ),
            )

        blur_match = re.search(r"\.blur\s*\(\s*radius:\s*([0-9.]+)", line)
        if blur_match:
            radius = float(blur_match.group(1))
            if radius >= 20:
                add_finding(
                    findings,
                    make_finding(
                        rule_id="swiftui-large-blur",
                        severity="review",
                        category="GPU Composition",
                        title="Large blur may be expensive on scrolling or animated surfaces",
                        file=rel_path,
                        line=line_number,
                        evidence=stripped,
                        severity_reason=f"Review because blur radius {radius:g} can create offscreen composition cost when repeated, animated, or used under large surfaces.",
                        impact="Large blur radii can increase offscreen rendering and composition cost, especially when animated or repeated under tab shells.",
                        recommendation="Prefer precomposed assets, static gradients, smaller radii, or one shared background layer per screen.",
                        local_proof="Capture before/after screenshots and a profiler or sample run on the exact screen being optimized.",
                        manual_proof="Use physical-device GPU or Instruments proof before claiming device-class, thermal, or ProMotion smoothness wins.",
                    ),
                )

        if ".shadow(" in line:
            shadow_window = [item for item in shadow_window if line_number - item <= 12]
            shadow_window.append(line_number)
            if len(shadow_window) == 3:
                add_finding(
                    findings,
                    make_finding(
                        rule_id="swiftui-shadow-stack",
                        severity="opportunity",
                        category="GPU Composition",
                        title="Stacked shadows can increase composition work",
                        file=rel_path,
                        line=line_number,
                        evidence=stripped,
                        severity_reason="Opportunity because three shadows were detected within a short source window; confirm whether they sit on the same repeated or scrolling surface.",
                        impact="Multiple shadows close together can create extra offscreen rendering cost and make scrolling surfaces heavier.",
                        recommendation="Keep only shadows that materially improve hierarchy; flatten repeated card shadows into a shared style.",
                        local_proof="Use screenshots plus a sampled scroll or interaction run to confirm the simplified style preserves hierarchy and lowers local work.",
                        manual_proof="Use device scroll or Instruments proof before claiming production scroll smoothness on real hardware.",
                    ),
                )

        if re.search(r"\b(DateFormatter|NumberFormatter|MeasurementFormatter)\s*\(", line):
            static_context = nearby_contains(lines, index, r"\bstatic\s+(let|var)\b|\blazy\s+var\b", before=4)
            if has_swiftui_view and not static_context:
                add_finding(
                    findings,
                    make_finding(
                        rule_id="formatter-created-in-view",
                        severity="review",
                        category="Body Work",
                        title="Formatter allocation should usually be cached",
                        file=rel_path,
                        line=line_number,
                        evidence=stripped,
                        severity_reason="Review because formatter construction appears inside a SwiftUI view path rather than a static or lazy cache.",
                        impact="Formatter creation in SwiftUI view paths can add repeated work during redraws.",
                        recommendation="Move stable formatters to static cached helpers or pass formatted values from the model layer.",
                        local_proof="Run the relevant view flow or tests locally and confirm formatted output remains unchanged; sample the view if redraw cost is the concern.",
                        manual_proof="Manual/device proof is usually not required unless this is tied to a launch, scroll, or device-level smoothness claim.",
                    ),
                )

        if "UIImage(data:" in line:
            add_finding(
                findings,
                make_finding(
                    rule_id="image-decoding-in-view-path",
                    severity="review" if imports_swiftui else "opportunity",
                    category="Image Decoding",
                    title="Review image decoding on UI paths",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    severity_reason="Review because image data decoding was detected on a source line that may execute during UI updates or interaction.",
                    impact="Decoding image data during view updates or interaction can cause hitches, memory pressure, or scroll stalls.",
                    recommendation="Cache decoded images, downsample large assets, and move decoding off hot SwiftUI body/update paths.",
                    local_proof="Use a sample trace during the image-heavy screen and compare local memory and CPU after caching or downsampling.",
                    manual_proof="Use physical-device memory, thermal, and scroll proof before claiming production image-performance gains.",
                ),
            )

        if "removePendingNotificationRequests" in line or "removeAllPendingNotificationRequests" in line:
            main_actor_context = nearby_contains(lines, index, r"@MainActor", before=12)
            severity = "high" if main_actor_context else "review"
            severity_reason = (
                "High because notification cleanup is inside a @MainActor context, so any synchronous wait can block launch or interaction work."
                if main_actor_context
                else "Review because notification cleanup can still be near launch or interaction work even when @MainActor was not detected nearby."
            )
            add_finding(
                findings,
                make_finding(
                    rule_id="notification-removal-ui-stall",
                    severity=severity,
                    category="Main Thread Blocking",
                    title="Notification request removal can block UI work",
                    file=rel_path,
                    line=line_number,
                    evidence=stripped,
                    severity_reason=severity_reason,
                    impact="UNUserNotificationCenter removal may synchronously wait on the notification service; if called from MainActor or launch/UI tasks it can feel like jank.",
                    recommendation="Keep notification cleanup off user-interaction hot paths where product semantics allow it, and preserve alarm/permission correctness when moving work.",
                    local_proof="Symbolicate sampled stacks before editing; after editing, rerun launch/tab interaction samples and the relevant notification or alarm validation lane.",
                    manual_proof="Use physical-device proof for wake paths, locked/background/killed delivery, notification timing, TestFlight behavior, or release claims.",
                ),
            )


def collect_guardrails(root: Path) -> list[dict[str, str]]:
    guardrails: list[dict[str, str]] = []
    for relative in ("AGENTS.md", "BEST_PRACTICES.md", "docs/validation-commands.md"):
        if (root / relative).is_file():
            guardrails.append({"kind": "repo-guidance", "path": relative})
    if (root / "scripts" / "check_alarm_runtime_freeze.sh").is_file():
        guardrails.append(
            {
                "kind": "protected-boundary",
                "path": "scripts/check_alarm_runtime_freeze.sh",
            }
        )
    return guardrails


def app_development_next_steps() -> list[str]:
    return [
        "Start with high findings on the exact slow screen or launch path; do not refactor every listed surface.",
        "Run xctrace Animation Hitches or Time Profiler when available; record sample/top/log fallback when profiler templates fail.",
        "Symbolicate sampled app frames before changing runtime or notification code.",
        "Treat physical-device smoothness, touch latency, ProMotion, thermal, audio, sensors, and wake-path timing as device-proof claims.",
    ]


def shipguard_eval_next_steps() -> list[str]:
    return [
        "Use this scan only to judge ShipGuard report usefulness, prioritization, noise, and missing guidance.",
        "Do not edit the scanned app, open app remediation tasks, or present findings as an app improvement backlog.",
        "Convert useful private-app observations into redacted public fixtures or deterministic ShipGuard eval cases.",
        "Improve ShipGuard wording, rule ranking, grouping, proof guidance, or docs when the report is generic, noisy, or hard to act on.",
    ]


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate ShipGuard report quality.",
            "Identify missing or noisy ShipGuard rules.",
            "Create redacted public fixtures or eval cases in ShipGuard.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not create app-specific remediation tasks from this run.",
            "Do not present target-app findings as the active development goal.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Did report wording keep target-app remediation separate from ShipGuard product QA next steps?",
        "Which grouped performance observation should become a public fixture or eval case before changing scanner heuristics again?",
        "Did the report make it obvious which evidence would promote a source suspicion into broader work?",
    ]


def runtime_evidence_boundary() -> dict[str, Any]:
    return {
        "evidence": "source heuristic",
        "confidence": "medium",
        "runtimeProof": "missing",
        "blocking": "no",
        "interpretation": (
            "Source-only findings nominate review and proof candidates; they do not prove actual CPU, GPU, memory, "
            "energy, hitch, touch-latency, FPS, or frame-rate problems."
        ),
        "promotionRule": (
            "Promote a performance suspicion only after same-route local profiling or physical-device evidence confirms "
            "the issue and the proposed change stays inside the authorized task boundary."
        ),
        "requiredRuntimeProof": [
            "Same-route Simulator trace, sample, or log evidence for local-only claims.",
            "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.",
        ],
    }


def evidence_promotion_contract(groups: list[dict[str, Any]]) -> dict[str, Any]:
    if not groups:
        return {
            "sourceEvidence": "source heuristic",
            "promotionStatus": "not-needed",
            "firstCandidateRule": None,
            "proofRequired": runtime_evidence_boundary()["requiredRuntimeProof"],
            "nextAction": {
                "owner": "developer",
                "kind": "no-op",
                "manualProof": "No performance findings were emitted, so there is no source suspicion to promote.",
                "expectedArtifact": "No runtime artifact required until a future report emits a source performance finding.",
                "successCondition": "Report remains pass with no source performance findings.",
                "failureMeaning": "If runtime symptoms exist despite a pass report, collect a same-route trace and add a public ShipGuard fixture before changing scanner heuristics.",
            },
        }

    first = groups[0]
    rule_id = str(first.get("ruleId") or "first-performance-group")
    validation_route = str(first.get("validationRoute") or "Run the same-route local or device proof for the first grouped performance action.")
    stop_condition = str(first.get("stopCondition") or "Stop after the first experiment unless same-route evidence shows useful signal.")
    first_experiment = str(first.get("firstExperiment") or "Change one flagged location only.")
    return {
        "sourceEvidence": "source heuristic",
        "promotionStatus": "missing-runtime-proof",
        "firstCandidateRule": rule_id,
        "proofRequired": runtime_evidence_boundary()["requiredRuntimeProof"],
        "nextAction": {
            "owner": "developer",
            "kind": "manual-proof",
            "manualProof": f"{validation_route} Attach the resulting trace, sample, log, or device Instruments receipt before broadening the work.",
            "expectedArtifact": f"Same-route before/after evidence for `{rule_id}` after this first experiment: {first_experiment}",
            "successCondition": f"{stop_condition} Runtime evidence must confirm the source suspicion before it is promoted into broader work.",
            "failureMeaning": "The source suspicion remains unpromoted; keep it as review guidance and do not broaden scanner heuristics or target-app remediation.",
        },
    }


def summarize_rules(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for finding in findings:
        rule_id = str(finding["ruleId"])
        group = grouped.setdefault(
            rule_id,
            {
                "ruleId": rule_id,
                "category": finding["category"],
                "title": finding["title"],
                "count": 0,
                "high": 0,
                "review": 0,
                "opportunity": 0,
                "firstLocations": [],
            },
        )
        group["count"] += 1
        group[finding["severity"]] += 1
        if len(group["firstLocations"]) < 3:
            group["firstLocations"].append(f"{finding['file']}:{finding['line']}")

    return sorted(
        grouped.values(),
        key=lambda item: (
            SEVERITY_RANK["high"] if item["high"] else SEVERITY_RANK["review"] if item["review"] else SEVERITY_RANK["opportunity"],
            -int(item["count"]),
            str(item["ruleId"]),
        ),
    )


def grouped_action_plan(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        by_rule[str(finding["ruleId"])].append(finding)

    groups: list[dict[str, Any]] = []
    for rule_id, items in by_rule.items():
        first = items[0]
        severity_mix = {
            "high": sum(1 for item in items if item["severity"] == "high"),
            "review": sum(1 for item in items if item["severity"] == "review"),
            "opportunity": sum(1 for item in items if item["severity"] == "opportunity"),
        }
        groups.append(
            {
                "ruleId": rule_id,
                "category": first["category"],
                "title": first["title"],
                "count": len(items),
                "severity": first["severity"],
                "severityMix": severity_mix,
                "firstLocations": [f"{item['file']}:{item['line']}" for item in items[:3]],
                "exampleEvidence": first["evidence"],
                "severityReason": first["severityReason"],
                "whyThisGroupMatters": first["impact"],
                "firstExperiment": first_experiment_for_rule(rule_id),
                "validationRoute": validation_route_for_rule(rule_id),
                "stopCondition": stop_condition_for_rule(rule_id),
                "recommendedFirstMove": first["recommendation"],
                "localProof": first["localProof"],
                "manualProof": first["manualProof"],
                "proofGuidance": first["proof"],
            }
        )

    return sorted(
        groups,
        key=lambda item: (
            SEVERITY_RANK.get(str(item["severity"]), 99),
            -int(item["count"]),
            str(item["ruleId"]),
        ),
    )


def first_experiment_for_rule(rule_id: str) -> str:
    experiments = {
        "notification-removal-ui-stall": "Move only the first notification cleanup call behind the existing non-interaction/background path or defer it one run-loop tick, then compare launch/tap samples before touching scheduler semantics.",
        "swiftui-periodic-timeline": "Change one visible TimelineView to the slowest acceptable cadence or pause it when inactive/Reduce Motion is enabled, then rerun the same screen sample before changing other timelines.",
        "formatter-created-in-view": "Cache one formatter as a static helper for the first flagged view and verify the rendered text is unchanged before moving broader formatting work.",
        "swiftui-large-blur": "Replace one large blur on the slow screen with a static/precomposed or lower-radius treatment, capture before/after screenshots, then sample the same interaction.",
        "swiftui-repeat-forever-animation": "Disable or gate one decorative repeatForever animation behind Reduce Motion/visibility and compare an at-rest screen recording plus sample before changing other motion.",
        "swiftui-shadow-stack": "Flatten one repeated card/surface shadow stack to the smallest hierarchy-preserving style and compare screenshot hierarchy plus one scroll/interaction sample.",
        "image-decoding-in-view-path": "Cache or downsample one decoded image path outside the view update path and compare the same image-heavy screen sample before broader image pipeline work.",
    }
    return experiments.get(
        rule_id,
        "Change one flagged location only, rerun the smallest matching local proof route, and keep the broader refactor blocked until that experiment shows useful signal.",
    )


def validation_route_for_rule(rule_id: str) -> str:
    routes = {
        "notification-removal-ui-stall": "Compare launch or tap samples on the same route, then run the relevant notification/alarm validation lane that proves delivery semantics were not changed.",
        "swiftui-periodic-timeline": "Record or sample the same visible screen before and after the cadence/visibility gate, including inactive or Reduce Motion state when applicable.",
        "formatter-created-in-view": "Run the focused view/test route that renders the formatted value, then sample the same screen only if redraw cost was the concern.",
        "swiftui-large-blur": "Capture before/after screenshots and sample the same slow interaction or scroll route after changing one blur treatment.",
        "swiftui-repeat-forever-animation": "Capture an at-rest screen recording plus a same-route sample with Reduce Motion or visibility gating enabled.",
        "swiftui-shadow-stack": "Compare hierarchy screenshots and one scroll or interaction sample on the repeated card/surface route.",
        "image-decoding-in-view-path": "Sample the same image-heavy screen or scroll route and compare memory/CPU after moving one decode/downsample path.",
    }
    return routes.get(
        rule_id,
        "Rerun the smallest local proof route that exercises the first flagged location and compare before/after evidence at the same grain.",
    )


def stop_condition_for_rule(rule_id: str) -> str:
    conditions = {
        "notification-removal-ui-stall": "Stop after one moved/deferred cleanup if main-thread samples no longer show notification removal on the interaction path and notification/alarm semantics still pass; otherwise revert or record the remaining device/manual blocker.",
        "swiftui-periodic-timeline": "Stop if the sampled route shows reduced redraw/hitch pressure without stale UI or Reduce Motion regression; do not change additional timelines without that signal.",
        "formatter-created-in-view": "Stop if rendered text remains unchanged and the local route passes; skip mass formatter migration if the sample shows no measurable redraw or launch signal.",
        "swiftui-large-blur": "Stop if screenshots preserve visual hierarchy and the same interaction sample improves or stays neutral; do not broaden the visual rewrite on appearance regressions or no signal.",
        "swiftui-repeat-forever-animation": "Stop if the at-rest recording/sample shows less constant motion work and Reduce Motion/visibility behavior is correct; do not remove more motion without that proof.",
        "swiftui-shadow-stack": "Stop if hierarchy screenshots still read clearly and the interaction sample improves or stays neutral; do not flatten unrelated card styles on visual regression.",
        "image-decoding-in-view-path": "Stop if the same image-heavy route shows lower decode/memory pressure with unchanged image quality; avoid broader pipeline work when the first path has no signal.",
    }
    return conditions.get(
        rule_id,
        "Stop after the first flagged location unless the same-route proof shows useful signal and no visible, semantic, or test regression.",
    )


def build_report(root: Path, *, shipguard_eval: bool = False, shareable: bool = False) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    root = root.resolve()
    doctor = ios_doctor.build_report(root)
    findings: list[dict[str, Any]] = []
    metrics = {
        "swiftFiles": 0,
        "swiftuiFiles": 0,
    }
    scan = ios_scan_scope.iter_files(root, {".swift"})
    files = scan.files
    metrics["swiftFiles"] = len(files)
    for path in files:
        scan_file(path, root, findings, metrics)

    findings.sort(
        key=lambda item: (
            SEVERITY_RANK.get(str(item.get("severity")), 99),
            str(item.get("file")),
            int(item.get("line") or 0),
        )
    )
    high_count = sum(1 for item in findings if item["severity"] == "high")
    review_count = sum(1 for item in findings if item["severity"] == "review")
    status = "blocked" if high_count else "review" if review_count else "pass"
    action_plan = grouped_action_plan(findings)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios performance",
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "generatedAt": utc_now(),
        "project": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
        "shareability": {
            "mode": "shareable" if shareable else "local",
            "localAbsolutePathsIncluded": not shareable,
            "note": "Use --shareable before moving this performance report into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring."
            if not shareable
            else "Local absolute project paths are omitted from report fields intended for external sharing.",
        },
        "status": status,
        "metrics": {
            **metrics,
            "xcodeProjects": len(doctor.get("xcode_projects", [])),
            "swiftPackages": len(doctor.get("swift_packages", [])),
            "findings": len(findings),
            "high": high_count,
            "review": review_count,
            "opportunity": sum(1 for item in findings if item["severity"] == "opportunity"),
        },
        "scanScope": ios_scan_scope.summary(scan),
        "runtimeEvidenceBoundary": runtime_evidence_boundary(),
        "guardrails": collect_guardrails(root),
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "ruleSummary": summarize_rules(findings),
        "groupedActionPlan": action_plan,
        "evidencePromotion": evidence_promotion_contract(action_plan),
        "findings": findings,
        "nextSteps": shipguard_eval_next_steps() if shipguard_eval else app_development_next_steps(),
    }


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def select_markdown_findings(findings: list[dict[str, Any]], limit: int = 40, per_rule: int = 3) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    rule_counts: dict[str, int] = defaultdict(int)
    for finding in findings:
        rule_id = str(finding["ruleId"])
        if rule_counts[rule_id] < per_rule:
            selected.append(finding)
            rule_counts[rule_id] += 1
        if len(selected) >= limit:
            break
    return selected


def markdown_report(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# iOS Performance Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Project: `{report['project']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Swift files: {metrics['swiftFiles']}",
        f"- SwiftUI files: {metrics['swiftuiFiles']}",
        f"- Findings: {metrics['findings']} ({metrics['high']} high, {metrics['review']} review, {metrics['opportunity']} opportunity)",
        f"- Skipped generated/proof/cache directories: {report['scanScope']['skippedDirectoryCount']}",
        "",
    ]
    boundary = report["runtimeEvidenceBoundary"]
    lines.extend(
        [
            "## Runtime Evidence Boundary",
            "",
            f"- Evidence: `{boundary['evidence']}`",
            f"- Confidence: `{boundary['confidence']}`",
            f"- Runtime proof: `{boundary['runtimeProof']}`",
            f"- Blocking: `{boundary['blocking']}`",
            f"- Interpretation: {boundary['interpretation']}",
            f"- Promotion rule: {boundary['promotionRule']}",
            "",
            "Required runtime proof:",
        ]
    )
    for item in boundary["requiredRuntimeProof"]:
        lines.append(f"- {item}")
    lines.append("")
    promotion = report.get("evidencePromotion")
    if isinstance(promotion, dict):
        action = promotion.get("nextAction") if isinstance(promotion.get("nextAction"), dict) else {}
        lines.extend(
            [
                "## Evidence Promotion Contract",
                "",
                f"- Source evidence: `{promotion.get('sourceEvidence', 'unknown')}`",
                f"- Promotion status: `{promotion.get('promotionStatus', 'unknown')}`",
                f"- First candidate rule: `{promotion.get('firstCandidateRule') or 'none'}`",
                f"- Owner: `{action.get('owner', 'developer')}`",
                f"- Manual proof: {action.get('manualProof', 'No manual proof specified.')}",
                f"- Expected artifact: {action.get('expectedArtifact', 'No expected artifact specified.')}",
                f"- Success condition: {action.get('successCondition', 'No success condition specified.')}",
                f"- Failure meaning: {action.get('failureMeaning', 'No failure meaning specified.')}",
                "",
            ]
        )
    if report["intent"] == "shipguard-evaluation":
        boundary = report["scopeBoundary"]
        lines.extend(
            [
                "## ShipGuard Evaluation Boundary",
                "",
                "- This scan is ShipGuard product QA only.",
                "- The scanned app is a read-only input; do not edit it from this run.",
                "- Use findings to improve ShipGuard rules, report shape, docs, or eval fixtures.",
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
        "## Guardrails Detected",
        "",
        ]
    )
    if report["guardrails"]:
        for guardrail in report["guardrails"]:
            lines.append(f"- `{guardrail['path']}` ({guardrail['kind']})")
    else:
        lines.append("- None detected.")

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
    for summary in report["ruleSummary"]:
        severity_mix = f"{summary['high']} high, {summary['review']} review, {summary['opportunity']} opportunity"
        locations = "<br>".join(f"`{location}`" for location in summary["firstLocations"])
        lines.append(f"| `{summary['ruleId']}` | {summary['count']} | {severity_mix} | {locations} |")

    if report["groupedActionPlan"]:
        lines.extend(
            [
                "",
                "## Grouped Next Actions",
                "",
                "Start with rule groups, not individual duplicate rows. Inspect the first locations, prove the group on the slow screen, then decide whether the pattern is real before broad refactors.",
                "",
                "| Rule | Count | First Locations | Why severity | Why this group matters | First experiment | Validation route | Stop condition | First move | Codex local proof | Manual/device proof |",
                "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for group in report["groupedActionPlan"]:
            locations = "<br>".join(f"`{location}`" for location in group["firstLocations"])
            lines.append(
                f"| `{group['ruleId']}` | {group['count']} | {locations} | {table_cell(group['severityReason'])} | {table_cell(group['whyThisGroupMatters'])} | {table_cell(group['firstExperiment'])} | {table_cell(group['validationRoute'])} | {table_cell(group['stopCondition'])} | {table_cell(group['recommendedFirstMove'])} | {table_cell(group['localProof'])} | {table_cell(group['manualProof'])} |"
            )

    selected_findings = select_markdown_findings(report["findings"])
    lines.extend(
        [
            "",
            "## Top Findings",
            "",
            "Repeated rules are capped here after the grouped action plan so the Markdown stays scannable; the JSON report contains every finding.",
            "",
            "| Severity | Rule | Location | Finding | Evidence | Why severity | Why it matters | Recommendation |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for finding in selected_findings:
        location = f"`{finding['file']}:{finding['line']}`"
        lines.append(
            f"| {finding['severity']} | `{finding['ruleId']}` | {location} | {table_cell(finding['title'])} | `{table_cell(finding['evidence'], 90)}` | {table_cell(finding['severityReason'])} | {table_cell(finding['impact'])} | {table_cell(finding['recommendation'])} |"
        )
    hidden_count = len(report["findings"]) - len(selected_findings)
    if hidden_count > 0:
        lines.append(f"| ... | ... | ... | ... | ... | ... | ... | {hidden_count} more findings in JSON |")

    if selected_findings:
        lines.extend(
            [
                "",
                "## Proof Boundaries",
                "",
                "| Severity | Rule | Location | Codex local proof | Manual/device proof |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for finding in selected_findings:
            location = f"`{finding['file']}:{finding['line']}`"
            lines.append(
                f"| {finding['severity']} | `{finding['ruleId']}` | {location} | {table_cell(finding['localProof'])} | {table_cell(finding['manualProof'])} |"
            )

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Proof Guidance", ""])
    for step in report["nextSteps"]:
        lines.append(f"- {step}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(Path(args.path), shipguard_eval=args.shipguard_eval, shareable=args.shareable)
    markdown = markdown_report(report)
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "ios-performance.json"
        md_path = out_dir / "ios-performance.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")
        print(f"wrote: {json_path}")
        print(f"wrote: {md_path}")
        print(f"status: {report['status']}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)


if __name__ == "__main__":
    main()
