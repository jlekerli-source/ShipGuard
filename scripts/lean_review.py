#!/usr/bin/env python3
"""ShipGuard Lean Review: review a diff for unnecessary code."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from lean_audit import (
    build_lean_mode_profile,
    build_behavior_gates,
    build_clean_state_action,
    build_precision_review,
    finding,
    has_calibration_signal,
    has_safety_context,
    next_actions_for_precision,
    read_text,
)


TOOL = "shipguard lean review"
SURFACE = "ShipGuard Lean Review"
SCHEMA_VERSION = 1
CODE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".sh", ".swift"}
NONTRIVIAL_LOGIC_RE = re.compile(
    r"\b(if|for|while|try|except|catch|switch|case)\b|=>\s*\{|\bparse[A-Za-z0-9_]*\s*\(|\.map\(|\.filter\(|\.reduce\(",
    re.IGNORECASE,
)
CHECK_SIGNAL_RE = re.compile(
    r"\b(assert|console\.assert|unittest|pytest|describe\s*\(|it\s*\(|test\s*\(|XCTest|__main__|demo\s*\()\b",
    re.IGNORECASE,
)
STRONG_CHECK_SIGNAL_RE = re.compile(
    r"\b(assert|console\.assert|XCTAssert[A-Za-z0-9_]*|expect\s*\(|describe\s*\(|it\s*\(|test\s*\(|func\s+test[A-Za-z0-9_]*)\b",
    re.IGNORECASE,
)
SPECULATIVE_MARKER_TOKENS = (
    "to" + "do",
    "fix" + "me",
    "temp" + "orary",
    "future" + "-proof",
    "place" + "holder",
    "for" + " later",
)
HARDWARE_DIFF_RE = re.compile(
    r"(adc|avcapturedevice|barometer|bluetooth|corebluetooth|gps|gyroscope|mcp3008|pca9685|sensor|thermistor)|clock drift",
    re.IGNORECASE,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review a unified diff for over-engineering, thin wrappers, native replacements, and proof-required safety boundaries."
    )
    parser.add_argument("--diff", required=True, help="Unified diff/patch to inspect")
    parser.add_argument("--path", default=".", help="Repository root used for context and shareable locations")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument(
        "--mode",
        choices=["lite", "full", "ultra"],
        default="full",
        help="Lean Review intensity: lite suggests smaller alternatives, full enforces the proof ladder, ultra prioritizes delete-first action.",
    )
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def parse_unified_diff(text: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    new_line = 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            if current:
                files.append(current)
            parts = line.split()
            file_name = parts[-1][2:] if len(parts) >= 4 and parts[-1].startswith("b/") else parts[-1]
            current = {"file": file_name, "added": [], "removed": []}
            new_line = 0
            continue
        if current is None:
            continue
        if line.startswith("+++ "):
            target = line[4:].strip()
            if target.startswith("b/"):
                current["file"] = target[2:]
            continue
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            new_line = int(hunk.group(1)) - 1
            continue
        if line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            current["added"].append({"line": new_line, "text": line[1:]})
            continue
        if line.startswith("-") and not line.startswith("---"):
            current["removed"].append({"text": line[1:]})
            continue
        if line.startswith(" "):
            new_line += 1
    if current:
        files.append(current)
    return files


def line_texts(file_diff: dict[str, Any]) -> list[str]:
    return [str(item.get("text", "")) for item in file_diff.get("added", [])]


def is_test_file(file_name: str) -> bool:
    lowered = file_name.lower()
    return any(part in lowered for part in ("test", "tests", "spec", "specs"))


def first_added_line(file_diff: dict[str, Any], pattern: str) -> int | None:
    regex = re.compile(pattern, re.IGNORECASE)
    for item in file_diff.get("added", []):
        if regex.search(str(item.get("text", ""))):
            return int(item.get("line") or 0) or None
    return None


def has_added_check(file_name: str, added_text: str) -> bool:
    if is_test_file(file_name):
        return True
    return bool(CHECK_SIGNAL_RE.search(added_text))


def is_speculative_detector_command(line: str) -> bool:
    lowered = line.lower()
    if "rg -n" in lowered and any(token in lowered for token in SPECULATIVE_MARKER_TOKENS):
        return True
    return (
        any(token in lowered for token in SPECULATIVE_MARKER_TOKENS[:2])
        and any(token in lowered for token in SPECULATIVE_MARKER_TOKENS[3:])
        and any(token in lowered for token in ("marker", "markers", "token", "tokens", "pattern", "regex"))
    )


def has_calibration_token(text: str) -> bool:
    return has_calibration_signal(text)


def has_hardware_diff_context(text: str) -> bool:
    return bool(HARDWARE_DIFF_RE.search(text))


def collect_proof_signals(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for file_diff in files:
        file_name = str(file_diff.get("file", ""))
        added_items = file_diff.get("added", [])
        if not added_items:
            continue
        added_text = "\n".join(str(item.get("text", "")) for item in added_items)
        check_line = next(
            (item for item in added_items if STRONG_CHECK_SIGNAL_RE.search(str(item.get("text", "")))),
            None,
        )
        if check_line is None:
            check_line = next(
                (item for item in added_items if CHECK_SIGNAL_RE.search(str(item.get("text", "")))),
                None,
            )
        if check_line is None and is_test_file(file_name):
            check_line = added_items[0]
        if not check_line:
            continue
        kind = "test-file" if is_test_file(file_name) else "inline-check-signal"
        signals.append(
            {
                "file": file_name,
                "line": int(check_line.get("line") or 0) or None,
                "kind": kind,
                "addedLines": len(added_items),
                "snippet": str(check_line.get("text", "")).strip()[:160],
                "checkSignal": bool(CHECK_SIGNAL_RE.search(added_text)),
            }
        )
    return signals[:20]


def normalized_path_tokens(file_name: str) -> set[str]:
    stem = Path(file_name).stem.lower()
    stem = re.sub(r"(tests?|specs?)$", "", stem)
    parts = re.split(r"[^a-z0-9]+|(?<=[a-z])(?=[A-Z])", stem)
    return {part.lower() for part in parts if len(part) >= 4}


def proof_signals_for_file(file_name: str, proof_signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lowered_file = file_name.lower()
    file_stem = Path(file_name).stem.lower()
    file_tokens = normalized_path_tokens(file_name)
    matched: list[dict[str, Any]] = []
    for signal in proof_signals:
        signal_file = str(signal.get("file") or "")
        lowered_signal = signal_file.lower()
        if lowered_signal == lowered_file:
            matched.append(signal)
            continue
        signal_stem = Path(signal_file).stem.lower()
        if file_stem and file_stem in signal_stem:
            matched.append(signal)
            continue
        signal_tokens = normalized_path_tokens(signal_file)
        if file_tokens and file_tokens & signal_tokens:
            matched.append(signal)
    return matched[:8]


def proof_signal_summary(proof_signals: list[dict[str, Any]]) -> str:
    first = proof_signals[0] if proof_signals else {}
    location = str(first.get("file") or "")
    if first.get("line"):
        location = f"{location}:{first['line']}"
    if not location:
        return "same diff includes runnable-check signals"
    return f"same diff includes runnable-check signals starting at {location}"


def build_proof_signal_calibration(
    *,
    proof_signals: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    same_diff_count = len(
        [
            item
            for item in findings
            if item.get("ruleId") == "one-runnable-check-signal-present-diff"
        ]
    )
    missing_count = len([item for item in findings if item.get("ruleId") == "one-runnable-check-missing-diff"])
    return {
        "sameDiffProofStatus": "present" if proof_signals else "missing",
        "proofSignals": proof_signals,
        "sameDiffProofSignalCount": len(proof_signals),
        "codeFindingsCoveredBySameDiffProof": same_diff_count,
        "missingRunnableCheckFindings": missing_count,
        "policy": (
            "Lean Review should distinguish no proof signal from same-diff proof signal. Same-diff tests still need "
            "human relevance review, but they should not produce duplicate missing-check ceremony."
        ),
    }


def finding_location(item: dict[str, Any]) -> str:
    evidence = item.get("evidence", {})
    file_name = str(evidence.get("file") or "")
    line = evidence.get("line")
    return f"{file_name}:{line}" if file_name and line else file_name


def runnable_check_finding_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "file": str((item.get("evidence") or {}).get("file") or ""),
        "line": (item.get("evidence") or {}).get("line"),
        "location": finding_location(item),
        "ruleId": str(item.get("ruleId") or ""),
        "severity": str(item.get("severity") or ""),
        "evidence": str((item.get("evidence") or {}).get("snippet") or item.get("evidence") or "")[:200],
        "recommendation": str(item.get("recommendation") or ""),
        "proofGuidance": str(item.get("proofGuidance") or ""),
    }


def build_runnable_check_review(
    *,
    proof_signals: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    missing_findings = [
        item
        for item in findings
        if isinstance(item, dict) and item.get("ruleId") == "one-runnable-check-missing-diff"
    ]
    covered_findings = [
        item
        for item in findings
        if isinstance(item, dict) and item.get("ruleId") == "one-runnable-check-signal-present-diff"
    ]
    return {
        "policy": "Non-trivial branch, loop, parser, and collection logic should leave one smallest runnable check.",
        "nonCeremonyBoundary": (
            "If same-diff proof already changes a focused test, XCTest, assertion, or explicit check signal, Lean Review "
            "records that proof signal instead of asking for duplicate test ceremony. The maintainer still needs to "
            "review relevance and run the focused check."
        ),
        "missingProofFindings": [runnable_check_finding_row(item) for item in missing_findings],
        "sameDiffProofFindings": [runnable_check_finding_row(item) for item in covered_findings],
        "sameDiffProofSignals": proof_signals,
        "summary": {
            "missingRunnableCheckFindings": len(missing_findings),
            "sameDiffProofFindings": len(covered_findings),
            "sameDiffProofSignalCount": len(proof_signals),
            "duplicateCeremonyAvoided": len(covered_findings) if proof_signals else 0,
        },
        "proofToReview": [
            "For missing-proof rows, add or identify the smallest runnable check that covers the changed behavior.",
            "For same-diff proof rows, run the changed check and confirm it exercises the changed non-trivial logic.",
        ],
    }


def scan_diff(root: Path, files: list[dict[str, Any]], proof_signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for file_diff in files:
        file_name = str(file_diff.get("file", ""))
        suffix = Path(file_name).suffix
        is_code = suffix in CODE_SUFFIXES
        added_lines = line_texts(file_diff)
        added_text = "\n".join(added_lines)
        if not added_text.strip():
            continue
        context_path = root / file_name
        context_text = read_text(context_path)
        safe_context = has_safety_context(context_path, context_text + "\n" + added_text)

        if is_code and NONTRIVIAL_LOGIC_RE.search(added_text) and not has_added_check(file_name, added_text):
            matching_proof_signals = proof_signals_for_file(file_name, proof_signals)
            if matching_proof_signals:
                findings.append(
                    finding(
                        severity="info",
                        category="proof-signal-diff-review",
                        rule_id="one-runnable-check-signal-present-diff",
                        file=file_name,
                        line=first_added_line(file_diff, NONTRIVIAL_LOGIC_RE.pattern),
                        evidence=(
                            "non-trivial branch, loop, parser, or collection logic added; "
                            f"{proof_signal_summary(matching_proof_signals)}"
                        ),
                        recommendation=(
                            "Do not add duplicate test ceremony before checking whether the same-diff proof signal "
                            "already covers this logic."
                        ),
                        proof=(
                            "Review the changed test/assertion files listed in proofSignalCalibration, then run the "
                            "focused validation command before merge."
                        ),
                    )
                )
                continue
            findings.append(
                finding(
                    severity="review",
                    category="proof-diff-review",
                    rule_id="one-runnable-check-missing-diff",
                    file=file_name,
                    line=first_added_line(file_diff, NONTRIVIAL_LOGIC_RE.pattern),
                    evidence="non-trivial branch, loop, parser, or collection logic added without a runnable check signal",
                    recommendation="Leave one smallest runnable check for the new logic instead of treating tests as optional ceremony.",
                    proof="Add an assert-based self-check, one focused test, or an equivalent existing test reference before merge.",
                )
            )

        if is_code and has_hardware_diff_context(added_text) and not has_calibration_token(added_text):
            findings.append(
                finding(
                    severity="review",
                    category="hardware-diff-review",
                    rule_id="hardware-calibration-missing-diff",
                    file=file_name,
                    line=first_added_line(file_diff, HARDWARE_DIFF_RE.pattern),
                    evidence="hardware or sensor code added without an obvious calibration/tuning knob",
                    recommendation="Keep a minimal calibration or tuning boundary when code touches real hardware or physical-device behavior.",
                    proof="Attach real-device, sensor, timing, or calibration evidence before simplifying the physical-world edge case away.",
                )
            )

        checks = [
            (
                "native-date-input-diff",
                r"<DatePicker\b|DatePicker\s*\(|"
                r"(?:import|from|require\().{0,120}(?<![\w-])"
                r"(react-datepicker|flatpickr|moment|date-fns|luxon|dayjs)(?![\w-])|"
                r"[\"'](?:react-datepicker|flatpickr|moment|date-fns|luxon|dayjs)[\"']\s*:",
                "native",
                "Date-picker/date-helper code added in this diff. Try the platform date control or formatter before owning custom picker plumbing.",
                "Prove locale, timezone, invalid input, and interaction behavior before deleting or adding custom date behavior.",
            ),
            (
                "native-color-input-diff",
                r"(react-color|tinycolor|SketchPicker|ChromePicker|ColorPicker)",
                "native",
                "Color-picker code added in this diff. Try native color controls or design-token selection before custom picker state.",
                "Keep custom code only when palette constraints, alpha, contrast, or brand-token rules are product requirements.",
            ),
            (
                "stdlib-url-params-diff",
                r"(split\([\"']&[\"']\)|split\([\"']=[\"']\)|encodeURIComponent|decodeURIComponent)",
                "stdlib",
                "Manual query-string parsing appeared in the diff. Prefer URL and URLSearchParams when runtime support allows it.",
                "Add one check for repeated keys, empty values, encoding, and malformed input before replacing behavior.",
            ),
            (
                "dependency-small-helper-diff",
                r"(from [\"']lodash|require\([\"']lodash|from [\"']underscore|require\([\"']underscore)",
                "stdlib",
                "A general utility dependency was added or touched. Check whether language/runtime primitives cover the actual call site.",
                "List actual imports and keep the dependency when it provides meaningful edge-case behavior.",
            ),
            (
                "deferred-shortcut-without-trigger",
                r"^\s*(#|//|/\*|<!--)\s*(ponytail|shipguard-lean):(?!(?=.*\bceiling\s*:)(?=.*\bupgrade\s*:))",
                "debt",
                "A lean shortcut marker was added without both a ceiling and an upgrade trigger.",
                "Use `ceiling:` and `upgrade:` in the comment so the shortcut is reviewable later.",
            ),
            (
                "speculative-future-hook-diff",
                r"\b(TODO|FIXME|temporary|for later|future-proof|placeholder)\b",
                "delete",
                "Speculative or placeholder wording was added. Delete it unless it is tied to an accepted task or proof boundary.",
                "If the placeholder must stay, link it to an owner, trigger, and validation path.",
            ),
        ]
        for rule_id, pattern, category, recommendation, proof in checks:
            if category == "delete" and not is_code:
                continue
            matched_items = [
                item
                for item in file_diff.get("added", [])
                if re.search(pattern, str(item.get("text", "")), flags=re.IGNORECASE | re.MULTILINE)
            ]
            if rule_id == "speculative-future-hook-diff":
                matched_items = [
                    item for item in matched_items if not is_speculative_detector_command(str(item.get("text", "")))
                ]
            if not matched_items:
                continue
            first_match = matched_items[0]
            findings.append(
                finding(
                    severity="review" if category in {"delete", "debt"} else "opportunity",
                    category=f"{category}-diff-review",
                    rule_id=rule_id,
                    file=file_name,
                    line=int(first_match.get("line") or 0) or None,
                    evidence=str(first_match.get("text", "")).strip()[:160],
                    recommendation=recommendation,
                    proof=proof,
                )
            )

        wrapper_match = re.search(
            r"(?:export\s+)?(?:function|const)\s+([A-Za-z0-9_]+)\s*(?:=\s*)?(?:\([^)]*\)|[^=]*)\s*(?:=>|\{)\s*(?:return\s+)?([A-Za-z0-9_.]+)\([^;\n{}]*\)",
            added_text,
        )
        if wrapper_match and not safe_context:
            findings.append(
                finding(
                    severity="opportunity",
                    category="yagni-diff-review",
                    rule_id="thin-wrapper-diff-review",
                    file=file_name,
                    line=first_added_line(file_diff, re.escape(wrapper_match.group(1))),
                    evidence=f"{wrapper_match.group(1)} delegates to {wrapper_match.group(2)}",
                    recommendation="Inline or delete this wrapper unless it adds policy, naming, compatibility, logging, typing, or test value.",
                    proof="Search call sites and keep one small check if behavior is non-trivial.",
                )
            )

        if safe_context:
            findings.append(
                finding(
                    severity="info",
                    category="safety-boundary",
                    rule_id="do-not-cut-safety-diff-without-proof",
                    file=file_name,
                    line=None,
                    evidence="diff touches security/validation/accessibility/data-loss terms",
                    recommendation="Less code is not the goal in this file until behavior proof exists.",
                    proof="Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior.",
                )
            )
    return findings


def review_lines(findings: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for item in findings:
        if item.get("severity") == "info":
            continue
        evidence = item.get("evidence", {})
        location = str(evidence.get("file", ""))
        if evidence.get("line"):
            location = f"{location}:L{evidence['line']}"
        tag = str(item.get("category", "")).split("-")[0] or "review"
        lines.append(f"{location}: {tag}: {item.get('recommendation')}")
    return lines


def changed_file_summary(file_diff: dict[str, Any]) -> dict[str, Any]:
    return {
        "file": str(file_diff.get("file") or ""),
        "addedLines": len(file_diff.get("added", [])),
        "removedLines": len(file_diff.get("removed", [])),
    }


def location_for_finding(item: dict[str, Any], fallback_file: str) -> str:
    evidence = item.get("evidence", {})
    file_name = str(evidence.get("file") or fallback_file)
    line = evidence.get("line")
    return f"{file_name}:{line}" if line else file_name


def decision_for_findings(items: list[dict[str, Any]]) -> str:
    rule_ids = {str(item.get("ruleId") or "") for item in items}
    categories = {str(item.get("category") or "") for item in items}
    if not items:
        return "clean"
    if rule_ids & {"thin-wrapper-diff-review", "speculative-future-hook-diff"}:
        return "delete"
    if "do-not-cut-safety-diff-without-proof" in rule_ids or "safety-boundary" in categories:
        return "keep"
    if rule_ids & {
        "one-runnable-check-missing-diff",
        "hardware-calibration-missing-diff",
        "deferred-shortcut-without-trigger",
    }:
        return "proof-blocked"
    return "simplify"


def decision_guidance(decision: str) -> dict[str, str]:
    if decision == "delete":
        return {
            "firstExperiment": "Search the changed call sites, then delete the candidate only if the wrapper or placeholder has no behavior, owner, or proof value.",
            "validationRoute": "Run the smallest test or smoke command that covers the changed file, then run git diff --check.",
            "stopCondition": "Stop if the search finds external call sites, compatibility behavior, or a requested proof boundary.",
        }
    if decision == "simplify":
        return {
            "firstExperiment": "Try the native, standard-library, or already-installed dependency replacement at this changed call site before adding more code.",
            "validationRoute": "Run the focused check for this changed behavior plus git diff --check.",
            "stopCondition": "Stop if the simpler form drops edge-case behavior, validation, accessibility, or user-visible output.",
        }
    if decision == "keep":
        return {
            "firstExperiment": "Treat this as a keep-with-proof boundary; identify the behavior proof before any deletion or simplification.",
            "validationRoute": "Run or attach focused proof for the safety, trust, data-loss, permission, accessibility, or lifecycle behavior.",
            "stopCondition": "Stop if the only evidence is less-code pressure without behavior proof.",
        }
    if decision == "proof-blocked":
        return {
            "firstExperiment": "Add or identify one smallest runnable check before merging the changed logic.",
            "validationRoute": "Run the focused validation command named by the task or changed test file before broader cleanup.",
            "stopCondition": "Stop if the diff has no runnable proof signal and the change is non-trivial, hardware-related, or shortcut debt.",
        }
    return {
        "firstExperiment": "No Lean finding for this changed file; confirm the diff is intentional instead of inventing cleanup work.",
        "validationRoute": "Use git diff --stat and git diff --check, then run the task's normal focused validation if this file matters.",
        "stopCondition": "Stop if the file has no changed Lean candidate in the supplied diff.",
    }


def build_current_diff_decision_map(
    *,
    diff_path: Path,
    files: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    precision: dict[str, Any],
) -> dict[str, Any]:
    findings_by_file: dict[str, list[dict[str, Any]]] = {}
    for item in findings:
        evidence = item.get("evidence", {})
        file_name = str(evidence.get("file") or "")
        if not file_name:
            continue
        findings_by_file.setdefault(file_name, []).append(item)

    decisions: list[dict[str, Any]] = []
    for file_diff in files:
        summary = changed_file_summary(file_diff)
        file_name = str(summary["file"])
        file_findings = findings_by_file.get(file_name, [])
        decision = decision_for_findings(file_findings)
        guidance = decision_guidance(decision)
        first_finding = file_findings[0] if file_findings else {}
        decisions.append(
            {
                "file": file_name,
                "source": "unified-diff",
                "decision": decision,
                "addedLines": summary["addedLines"],
                "removedLines": summary["removedLines"],
                "ruleIds": sorted({str(item.get("ruleId") or "") for item in file_findings if item.get("ruleId")}),
                "firstLocation": location_for_finding(first_finding, file_name) if first_finding else file_name,
                "firstExperiment": guidance["firstExperiment"],
                "validationRoute": guidance["validationRoute"],
                "stopCondition": guidance["stopCondition"],
            }
        )

    summary = precision.get("summary") if isinstance(precision.get("summary"), dict) else {}
    return {
        "scope": "current-diff-only",
        "diffPath": diff_path.name,
        "inventoryBoundary": "This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.",
        "wholeRepoFallbackCommand": "shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable",
        "changedFiles": [changed_file_summary(file_diff) for file_diff in files],
        "decisions": decisions,
        "deleteOrSimplifyList": [
            item for item in decisions if item.get("decision") in {"delete", "simplify"}
        ],
        "summary": {
            "filesChanged": len(files),
            "addedLinesInspected": sum(len(item.get("added", [])) for item in files),
            "removedLinesSeen": sum(len(item.get("removed", [])) for item in files),
            "decisionRows": len(decisions),
            "deleteCandidates": int(summary.get("deleteCandidates") or 0),
            "simplifyCandidates": int(summary.get("simplifyCandidates") or 0),
            "keepBoundaries": int(summary.get("keepBoundaries") or 0),
            "proofBlockedCandidates": int(summary.get("proofBlockedCandidates") or 0),
            "cleanFiles": len([item for item in decisions if item.get("decision") == "clean"]),
        },
        "nonClaims": [
            "Does not prove whole-repo inventory coverage.",
            "Does not prove benchmark savings, token savings, cost savings, or time savings.",
            "Does not authorize private target-app edits from ShipGuard product-QA runs.",
        ],
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    diff_path = Path(args.diff)
    if not diff_path.exists():
        raise SystemExit(f"lean-review: diff does not exist: {diff_path}")
    diff_text = diff_path.read_text(encoding="utf-8", errors="ignore")
    files = parse_unified_diff(diff_text)
    proof_signals = collect_proof_signals(files)
    findings = scan_diff(root, files, proof_signals)
    lean_mode = build_lean_mode_profile(args.mode)
    precision = build_precision_review(findings, mode=args.mode)
    if not precision.get("actionGroups") and not precision.get("topActions"):
        precision["cleanStateAction"] = build_clean_state_action(
            tool=TOOL,
            mode=str(lean_mode.get("mode") or args.mode),
        )
    behavior_gates = build_behavior_gates(findings, {"summary": {"markers": 0, "missingUpgradeTrigger": 0}})
    if proof_signals and isinstance(behavior_gates.get("oneRunnableCheck"), dict):
        behavior_gates["oneRunnableCheck"]["status"] = "same-diff-proof-signal-present"
        behavior_gates["oneRunnableCheck"][
            "policy"
        ] = "Same-diff runnable-check signals are visible; verify relevance before adding duplicate proof ceremony."
    proof_calibration = build_proof_signal_calibration(proof_signals=proof_signals, findings=findings)
    runnable_check_review = build_runnable_check_review(proof_signals=proof_signals, findings=findings)
    current_diff_decision_map = build_current_diff_decision_map(
        diff_path=diff_path,
        files=files,
        findings=findings,
        precision=precision,
    )
    status = "pass" if not [item for item in findings if item.get("severity") in {"review", "opportunity"}] else "review"
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": status,
        "target": {"path": "." if args.shareable else str(root), "shareable": bool(args.shareable)},
        "diff": {"path": diff_path.name if args.shareable else str(diff_path), "filesChanged": len(files)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native diff review for unnecessary code. It does not vendor Ponytail code.",
        },
        "leanMode": lean_mode,
        "reviewLines": review_lines(findings),
        "currentDiffDecisionMap": current_diff_decision_map,
        "behaviorGates": behavior_gates,
        "proofSignalCalibration": proof_calibration,
        "runnableCheckReview": runnable_check_review,
        "precisionReview": precision,
        "findings": findings,
        "metrics": {
            "filesChanged": len(files),
            "addedLines": sum(len(item.get("added", [])) for item in files),
            "findings": len(findings),
            "reviewFindings": len([item for item in findings if item.get("severity") == "review"]),
            "opportunityFindings": len([item for item in findings if item.get("severity") == "opportunity"]),
            "infoFindings": len([item for item in findings if item.get("severity") == "info"]),
        },
        "nextActions": next_actions_for_precision(str(lean_mode.get("mode") or args.mode), precision),
    }
    if args.shipguard_eval:
        report["scopeBoundary"] = (
            "This is ShipGuard product QA. The diff is an evaluation input for report usefulness, not authorization to edit a private target."
        )
        report["reportQualityQuestions"] = [
            "Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?",
            "Does Lean Review require one smallest runnable check for non-trivial new logic?",
            "Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?",
            "Does Lean Review protect hardware calibration and host boundaries from false less-code pressure?",
            "Does it keep safety-boundary code out of automatic deletion?",
            "Does it make the first simplification action obvious enough for a solo developer?",
            "Does Lean Review expose the selected lite/full/ultra mode and bias first actions accordingly?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Lean Review",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        f"- Diff files changed: {report['metrics']['filesChanged']}",
        f"- Added lines inspected: {report['metrics']['addedLines']}",
        "",
        "## Lean Mode",
        "",
        f"- Mode: `{report.get('leanMode', {}).get('mode', 'full')}`",
        f"- Intent: {report.get('leanMode', {}).get('intent', '')}",
        f"- First action bias: `{report.get('leanMode', {}).get('firstActionBias', 'proof-ladder')}`",
        f"- Policy: {report.get('leanMode', {}).get('policy', '')}",
        "",
        "## Diff Review",
        "",
    ]
    if report["reviewLines"]:
        for item in report["reviewLines"]:
            lines.append(f"- {item}")
    else:
        lines.append("Lean already. Ship.")
    decision_map = report.get("currentDiffDecisionMap", {})
    if isinstance(decision_map, dict):
        summary = decision_map.get("summary") if isinstance(decision_map.get("summary"), dict) else {}
        lines.extend(["", "## Current Diff Decision Map", ""])
        lines.append(f"- Scope: `{decision_map.get('scope', 'current-diff-only')}`")
        lines.append(f"- Diff: `{decision_map.get('diffPath', '')}`")
        lines.append(
            f"- Boundary: {decision_map.get('inventoryBoundary', 'This report does not scan the whole repo.')}"
        )
        lines.append(
            f"- Whole-repo fallback: `{decision_map.get('wholeRepoFallbackCommand', 'shipguard lean audit --path <repo> --out <lean-audit-out>')}`"
        )
        lines.append(
            f"- Decision rows: {summary.get('decisionRows', 0)}; delete: {summary.get('deleteCandidates', 0)}; "
            f"simplify: {summary.get('simplifyCandidates', 0)}; keep: {summary.get('keepBoundaries', 0)}; "
            f"proof-blocked: {summary.get('proofBlockedCandidates', 0)}; clean files: {summary.get('cleanFiles', 0)}"
        )
        decisions = decision_map.get("decisions")
        if isinstance(decisions, list) and decisions:
            lines.extend(
                [
                    "",
                    "| File | Decision | Added | Removed | Rules | First Experiment | Validation | Stop Condition |",
                    "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
                ]
            )
            for item in decisions[:12]:
                rules = ", ".join(str(rule) for rule in item.get("ruleIds", []) if rule) or "-"
                lines.append(
                    f"| {str(item.get('file', '')).replace('|', '\\|')} | `{item.get('decision', '')}` | "
                    f"{item.get('addedLines', 0)} | {item.get('removedLines', 0)} | {rules.replace('|', '\\|')} | "
                    f"{str(item.get('firstExperiment', '')).replace('|', '\\|')} | "
                    f"{str(item.get('validationRoute', '')).replace('|', '\\|')} | "
                    f"{str(item.get('stopCondition', '')).replace('|', '\\|')} |"
                )
        else:
            lines.append("")
            lines.append("No changed-file decision rows were found in the supplied diff.")
        non_claims = decision_map.get("nonClaims")
        if isinstance(non_claims, list) and non_claims:
            lines.extend(["", "Non-claims:"])
            for item in non_claims:
                lines.append(f"- {item}")
    precision = report.get("precisionReview", {})
    gates = report.get("behaviorGates", {})
    if gates:
        lines.extend(["", "## Behavior Gates", ""])
        for name, gate in gates.items():
            if not isinstance(gate, dict):
                continue
            lines.append(f"- `{name}`: {gate.get('status', 'available')} - {gate.get('policy', '')}")
    calibration = report.get("proofSignalCalibration", {})
    if isinstance(calibration, dict):
        lines.extend(["", "## Proof Signal Calibration", ""])
        lines.append(f"- Same-diff proof status: `{calibration.get('sameDiffProofStatus', 'missing')}`")
        lines.append(f"- Proof signals: {calibration.get('sameDiffProofSignalCount', 0)}")
        lines.append(
            f"- Code findings covered by same-diff proof: {calibration.get('codeFindingsCoveredBySameDiffProof', 0)}"
        )
        lines.append(f"- Missing runnable-check findings: {calibration.get('missingRunnableCheckFindings', 0)}")
        policy = calibration.get("policy")
        if policy:
            lines.append(f"- Policy: {policy}")
        signals = calibration.get("proofSignals")
        if isinstance(signals, list) and signals:
            lines.extend(["", "| Kind | Location | Added Lines | Signal |", "| --- | --- | ---: | --- |"])
            for signal in signals[:8]:
                location = str(signal.get("file", ""))
                if signal.get("line"):
                    location = f"{location}:{signal['line']}"
                lines.append(
                    f"| {signal.get('kind', '')} | {location} | {signal.get('addedLines', 0)} | "
                    f"{str(signal.get('snippet', '')).replace('|', '\\|')} |"
                )
    runnable_review = report.get("runnableCheckReview", {})
    if isinstance(runnable_review, dict):
        summary = runnable_review.get("summary") if isinstance(runnable_review.get("summary"), dict) else {}
        lines.extend(["", "## Runnable Check Review", ""])
        lines.append(f"- Missing proof findings: {summary.get('missingRunnableCheckFindings', 0)}")
        lines.append(f"- Same-diff proof findings: {summary.get('sameDiffProofFindings', 0)}")
        lines.append(f"- Same-diff proof signals: {summary.get('sameDiffProofSignalCount', 0)}")
        lines.append(f"- Duplicate ceremony avoided: {summary.get('duplicateCeremonyAvoided', 0)}")
        if runnable_review.get("policy"):
            lines.append(f"- Policy: {runnable_review.get('policy')}")
        if runnable_review.get("nonCeremonyBoundary"):
            lines.append(f"- Non-ceremony boundary: {runnable_review.get('nonCeremonyBoundary')}")
        missing_rows = runnable_review.get("missingProofFindings")
        if isinstance(missing_rows, list) and missing_rows:
            lines.extend(["", "### Missing Runnable Checks", ""])
            lines.extend(["| Location | Recommendation | Proof |", "| --- | --- | --- |"])
            for row in missing_rows[:8]:
                lines.append(
                    f"| {str(row.get('location', '')).replace('|', '\\|')} | "
                    f"{str(row.get('recommendation', '')).replace('|', '\\|')} | "
                    f"{str(row.get('proofGuidance', '')).replace('|', '\\|')} |"
                )
        covered_rows = runnable_review.get("sameDiffProofFindings")
        if isinstance(covered_rows, list) and covered_rows:
            lines.extend(["", "### Same-Diff Proof Signals", ""])
            lines.extend(["| Location | Recommendation | Proof Review |", "| --- | --- | --- |"])
            for row in covered_rows[:8]:
                lines.append(
                    f"| {str(row.get('location', '')).replace('|', '\\|')} | "
                    f"{str(row.get('recommendation', '')).replace('|', '\\|')} | "
                    f"{str(row.get('proofGuidance', '')).replace('|', '\\|')} |"
                )
    summary = precision.get("summary", {})
    lines.extend(["", "## Precision Ledger", ""])
    lines.append(
        f"- Delete candidates: {summary.get('deleteCandidates', 0)}; "
        f"simplify candidates: {summary.get('simplifyCandidates', 0)}; "
        f"keep boundaries: {summary.get('keepBoundaries', 0)}; "
        f"proof-blocked candidates: {summary.get('proofBlockedCandidates', 0)}; "
        f"action groups: {summary.get('actionGroups', 0)}"
    )
    action_groups = precision.get("actionGroups", [])
    if action_groups:
        lines.extend(["", "### Grouped Action Plan", ""])
        lines.extend(
            [
                "| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |",
                "| ---: | --- | --- | ---: | --- | --- | --- | --- |",
            ]
        )
        for group in action_groups[:8]:
            lines.append(
                f"| {group.get('rank', '-')} | {group.get('decision', '')} | `{group.get('ruleId', '')}` | "
                f"{group.get('evidenceCount', 0)} | {group.get('firstLocation', '')} | "
                f"{str(group.get('firstExperiment', '')).replace('|', '\\|')} | "
                f"{str(group.get('validationRoute', '')).replace('|', '\\|')} | "
                f"{str(group.get('stopCondition', '')).replace('|', '\\|')} |"
            )
    clean_state = precision.get("cleanStateAction")
    if isinstance(clean_state, dict):
        lines.extend(["", "### Clean State Action", ""])
        lines.append(f"- Summary: {clean_state.get('summary', '')}")
        lines.append(f"- First experiment: {clean_state.get('firstExperiment', '')}")
        lines.append(f"- Evidence command: `{clean_state.get('evidenceCommand', '')}`")
        lines.append(f"- Next command: `{clean_state.get('nextCommand', '')}`")
        lines.append(f"- Validation route: {clean_state.get('validationRoute', '')}")
        lines.append(f"- Stop condition: {clean_state.get('stopCondition', '')}")
    top_actions = precision.get("topActions", [])
    if top_actions:
        lines.extend(["", "### Individual Starting Points", ""])
        lines.extend(["| Rank | Decision | Location | Action | Proof |", "| ---: | --- | --- | --- | --- |"])
        for action in top_actions:
            decision = "delete" if action in precision.get("deleteList", []) else "simplify"
            if action in precision.get("blockedByProof", []):
                decision = "proof-blocked"
            lines.append(
                f"| {action.get('rank', '-')} | {decision} | {action.get('location', '')} | "
                f"{str(action.get('action', '')).replace('|', '\\|')} | "
                f"{str(action.get('proofRequired', '')).replace('|', '\\|')} |"
            )
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation | Proof |", "| --- | --- | --- | --- | --- |"])
        for item in report["findings"]:
            evidence = item["evidence"]
            location = str(evidence.get("file", ""))
            if evidence.get("line"):
                location = f"{location}:{evidence['line']}"
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | {location}: {str(evidence.get('snippet', '')).replace('|', '\\|')} | "
                f"{str(item['recommendation']).replace('|', '\\|')} | {str(item['proofGuidance']).replace('|', '\\|')} |"
            )
    else:
        lines.append("No diff-specific lean findings were detected.")
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
    (out / "lean-review.json").write_text(json_text, encoding="utf-8")
    (out / "lean-review.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
