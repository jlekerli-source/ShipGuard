#!/usr/bin/env python3
"""ShipGuard Lean Deck: audit code for native/stdlib simplification opportunities."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


TOOL = "shipguard lean audit"
SURFACE = "ShipGuard Lean Deck"
SCHEMA_VERSION = 1
TEXT_SUFFIXES = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".py",
    ".sh",
    ".swift",
    ".md",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
}
CODE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".sh", ".swift"}
SKIP_DIRS = {
    ".git",
    ".cache",
    ".next",
    ".turbo",
    "DerivedData",
    "__pycache__",
    "build",
    "dist",
    "examples",
    "fixtures",
    "node_modules",
    "tests",
    "vendor",
}
SCANNER_SELF_SKIP_FILES = {
    "scripts/lean_audit.py",
    "scripts/lean_review.py",
    "scripts/lean_debt.py",
    "scripts/self_audit.sh",
}
SAFETY_TOKENS = (
    "auth",
    "token",
    "password",
    "permission",
    "encrypt",
    "csrf",
    "xss",
    "sql",
    "validate",
    "validation",
    "accessibility",
    "a11y",
    "migration",
    "delete",
    "payment",
)
ADAPTER_TOKENS = (
    ".claude-plugin",
    ".codex-plugin",
    ".opencode",
    "adapter",
    "bridge",
    "claude",
    "codex",
    "gemini",
    "hook",
    "hooks",
    "mcp",
    "opencode",
    "plugin",
    "plugins",
)
HARDWARE_TOKENS = (
    "adc",
    "avcapturedevice",
    "barometer",
    "bluetooth",
    "calibration",
    "calibrate",
    "camera",
    "clock drift",
    "corebluetooth",
    "gps",
    "gyroscope",
    "hardware",
    "mcp3008",
    "pca9685",
    "sensor",
    "thermistor",
)
CALIBRATION_TOKENS = (
    "calibration",
    "calibrate",
    "drift",
    "offset",
    "threshold",
    "trim",
    "tuning",
)
FINDING_PRIORITY = {"review": 0, "opportunity": 1, "info": 2}
LEGACY_MARKER_RE = re.compile(r"\bTODO\b|\bFIXME\b|temporary|legacy|compat", re.IGNORECASE)
LEAN_DEBT_RE = re.compile(
    r"(?P<prefix>#|//|/\*|<!--)\s*(?P<label>ponytail|shipguard-lean):\s*(?P<body>.*)",
    re.IGNORECASE,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a repo for over-engineering, native platform replacements, and code that may not need to exist."
    )
    parser.add_argument("--path", default=".", help="Repo to inspect")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_files(root: Path, limit: int = 550) -> tuple[list[Path], dict[str, Any]]:
    files: list[Path] = []
    skipped_dirs: Counter[str] = Counter()
    skipped_files: list[str] = []
    for path in sorted(root.rglob("*")):
        if len(files) >= limit:
            break
        try:
            relative_parts = path.relative_to(root).parts
        except ValueError:
            relative_parts = path.parts
        skip_part = next((part for part in relative_parts[:-1] if part in SKIP_DIRS), None)
        if skip_part:
            skipped_dirs[skip_part] += 1
            continue
        relative_name = "/".join(relative_parts)
        if relative_name in SCANNER_SELF_SKIP_FILES:
            skipped_files.append(relative_name)
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile"}):
            files.append(path)
    return files, {
        "skippedDirectoryNames": sorted(skipped_dirs),
        "skippedDirectoryFileCount": sum(skipped_dirs.values()),
        "skippedFiles": skipped_files,
        "truncated": len(files) >= limit,
        "fileLimit": limit,
    }


def line_for(text: str, needle: str) -> int | None:
    index = text.find(needle)
    if index < 0:
        return None
    return text[:index].count("\n") + 1


def has_safety_context(path: Path, text: str) -> bool:
    haystack = f"{path.as_posix()}\n{text[:4000]}".lower()
    return any(token in haystack for token in SAFETY_TOKENS)


def has_adapter_context(path: Path, text: str) -> bool:
    haystack = f"{path.as_posix()}\n{text[:1200]}".lower()
    return any(token in haystack for token in ADAPTER_TOKENS)


def has_hardware_context(text: str) -> bool:
    haystack = text[:6000].lower()
    return any(token in haystack for token in HARDWARE_TOKENS)


def has_calibration_signal(text: str) -> bool:
    haystack = text[:6000].lower()
    for token in CALIBRATION_TOKENS:
        if token == "trim":
            if re.search(r"(?<![.\w])trim(?:s|med|ming)?\b", haystack):
                return True
            continue
        if token in haystack:
            return True
    return False


def has_calibration_context(text: str) -> bool:
    return has_calibration_signal(text)


def finding(
    *,
    severity: str,
    category: str,
    rule_id: str,
    file: str,
    line: int | None,
    evidence: str,
    recommendation: str,
    proof: str,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "category": category,
        "ruleId": rule_id,
        "evidence": {"file": file, "line": line, "snippet": evidence},
        "recommendation": recommendation,
        "proofGuidance": proof,
    }


def legacy_signal(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    markers: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        matches = LEGACY_MARKER_RE.findall(line)
        if not matches:
            continue
        markers.append(
            {
                "line": number,
                "markerCount": len(matches),
                "snippet": line.strip()[:140],
            }
        )
    return {
        "lineCount": len(lines),
        "markerCount": sum(int(item["markerCount"]) for item in markers),
        "firstMarkerLines": markers[:5],
    }


def parse_lean_debt_body(body: str) -> dict[str, str]:
    normalized = body.strip().rstrip("*/").rstrip("-->").strip()
    result = {"summary": normalized, "ceiling": "", "upgrade": ""}
    ceiling_match = re.search(r"\bceiling\s*:\s*([^.;]+)", normalized, flags=re.IGNORECASE)
    upgrade_match = re.search(r"\bupgrade\s*:\s*([^.;]+)", normalized, flags=re.IGNORECASE)
    if ceiling_match:
        result["ceiling"] = ceiling_match.group(1).strip()
    if upgrade_match:
        result["upgrade"] = upgrade_match.group(1).strip()
    return result


def scan_lean_debt(root: Path, files: list[Path]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for path in files:
        text = read_text(path)
        if not text:
            continue
        relative = rel(path, root)
        for number, line in enumerate(text.splitlines(), start=1):
            match = LEAN_DEBT_RE.search(line)
            if not match:
                continue
            parsed = parse_lean_debt_body(match.group("body"))
            has_trigger = bool(parsed["upgrade"])
            items.append(
                {
                    "file": relative,
                    "line": number,
                    "marker": match.group("label").lower(),
                    "summary": parsed["summary"][:240],
                    "ceiling": parsed["ceiling"],
                    "upgrade": parsed["upgrade"],
                    "hasUpgradeTrigger": has_trigger,
                    "status": "tracked" if has_trigger else "needs-trigger",
                }
            )
    return {
        "description": "Intentional lean shortcuts found in comments. Every shortcut should name a ceiling and an upgrade trigger so deferrals stay reviewable.",
        "markers": items[:80],
        "summary": {
            "markers": len(items),
            "missingUpgradeTrigger": len([item for item in items if not item["hasUpgradeTrigger"]]),
            "omittedByLimit": max(0, len(items) - 80),
        },
    }


def scan_package(root: Path) -> list[dict[str, Any]]:
    package = root / "package.json"
    if not package.exists():
        return []
    try:
        loaded = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    deps = {}
    for key in ("dependencies", "devDependencies"):
        value = loaded.get(key)
        if isinstance(value, dict):
            deps.update(value)
    findings: list[dict[str, Any]] = []
    date_deps = sorted(set(deps) & {"moment", "date-fns", "luxon", "dayjs", "react-datepicker", "flatpickr"})
    if date_deps:
        findings.append(
            finding(
                severity="opportunity",
                category="dependency-opportunity",
                rule_id="dependency-date-helper-review",
                file="package.json",
                line=None,
                evidence=", ".join(date_deps),
                recommendation="Check whether the app needs a date library here or whether native Date, Intl.DateTimeFormat, or platform date inputs cover the job.",
                proof="Before removing anything, grep actual imports and add/keep date-formatting tests for locale, timezone, and invalid input behavior.",
            )
        )
    utility_deps = sorted(set(deps) & {"lodash", "underscore", "left-pad", "classnames", "clsx"})
    if utility_deps:
        findings.append(
            finding(
                severity="opportunity",
                category="dependency-opportunity",
                rule_id="dependency-small-helper-review",
                file="package.json",
                line=None,
                evidence=", ".join(utility_deps),
                recommendation="Review whether these dependencies carry their weight or whether the current usage is simple enough for language/runtime primitives.",
                proof="List imports first; replace only trivial usage covered by tests. Keep dependencies that provide real edge-case handling.",
            )
        )
    return findings


def scan_file(root: Path, path: Path) -> list[dict[str, Any]]:
    text = read_text(path)
    if not text:
        return []
    relative = rel(path, root)
    findings: list[dict[str, Any]] = []
    safe_context = has_safety_context(path, text)
    adapter_context = has_adapter_context(Path(relative), text)

    if path.suffix in CODE_SUFFIXES:
        checks = [
            (
                "native-date-input",
                r"(?:from\s+[\"'](?:react-datepicker|flatpickr|moment|date-fns|luxon|dayjs)[\"']|"
                r"import\s+.*[\"'](?:react-datepicker|flatpickr|moment|date-fns|luxon|dayjs)[\"']|"
                r"<DatePicker\b|DatePicker\s*\()",
                "native-platform-opportunity",
                "If the UI only captures a simple date/time, prefer native input, SwiftUI DatePicker, or platform formatters over custom picker plumbing.",
                "Prove with one focused interaction test and timezone/locale formatting coverage before deleting custom behavior.",
            ),
            (
                "native-color-input",
                r"(?:SketchPicker|ChromePicker|ColorPicker|react-color|tinycolor|color picker)",
                "native-platform-opportunity",
                "If this is simple color selection, check whether native color controls or design-system tokens remove custom picker code.",
                "Keep custom color logic when alpha, palette constraints, accessibility contrast, or brand-token validation are real product requirements.",
            ),
            (
                "native-dialog",
                r"(?:CustomModal|ModalPortal|aria-modal|role=[\"']dialog[\"'])",
                "native-platform-opportunity",
                "For basic confirmation flows, compare custom modal code with native dialog/sheet patterns or the platform design-system component.",
                "Do not remove focus trapping, escape handling, screen-reader labels, or destructive-action confirmations without accessibility proof.",
            ),
            (
                "browser-storage-wrapper",
                r"(?:localStorage|sessionStorage).{0,80}(?:JSON\.parse|JSON\.stringify)",
                "wrapper-simplification",
                "If this is a thin storage wrapper, consolidate it behind one tiny helper instead of duplicating parse/stringify/error handling.",
                "Keep migration, corrupt-data recovery, and privacy boundaries covered by tests.",
            ),
            (
                "manual-url-params",
                r"(?:split\([\"']&[\"']\)|split\([\"']=[\"']\)|encodeURIComponent|decodeURIComponent)",
                "stdlib-opportunity",
                "Prefer URL and URLSearchParams for query parsing and construction unless a legacy runtime blocks it.",
                "Add tests for repeated keys, empty values, encoding, and malformed input.",
            ),
        ]
        for rule_id, pattern, category, recommendation, proof in checks:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if not match:
                continue
            findings.append(
                finding(
                    severity="review" if safe_context and rule_id in {"native-dialog", "browser-storage-wrapper"} else "opportunity",
                    category=category,
                    rule_id=rule_id,
                    file=relative,
                    line=line_for(text, match.group(0)),
                    evidence=match.group(0).replace("\n", " ")[:160],
                    recommendation=recommendation,
                    proof=proof,
                )
            )

    if path.suffix in CODE_SUFFIXES:
        trivial_wrappers = re.findall(
            r"(?:export\s+)?(?:function|const)\s+([A-Za-z0-9_]+)\s*(?:=\s*)?(?:\([^)]*\)|[^=]*)\s*(?:=>|\{)\s*(?:return\s+)?([A-Za-z0-9_.]+)\([^;\n{}]*\)\s*;?\s*\}?",
            text,
        )
        if trivial_wrappers and adapter_context:
            name, target = trivial_wrappers[0]
            findings.append(
                finding(
                    severity="info",
                    category="adapter-boundary",
                    rule_id="thin-adapter-boundary",
                    file=relative,
                    line=line_for(text, name),
                    evidence=f"{name} delegates to {target}",
                    recommendation="Thin plugin, hook, MCP, or agent adapters may be the correct host boundary; do not treat them as automatic deletion targets.",
                    proof="Keep the adapter unless host registration tests and call-site search prove the bridge is redundant.",
                )
            )
        elif trivial_wrappers and not safe_context:
            name, target = trivial_wrappers[0]
            findings.append(
                finding(
                    severity="opportunity",
                    category="wrapper-simplification",
                    rule_id="thin-wrapper-review",
                    file=relative,
                    line=line_for(text, name),
                    evidence=f"{name} delegates to {target}",
                    recommendation="Check whether this wrapper adds naming, policy, logging, typing, or test value. If not, inline it or delete it.",
                    proof="Use search results to confirm call sites stay readable and no public API/backward-compatibility contract depends on the wrapper.",
                )
            )

    if path.suffix in CODE_SUFFIXES and has_hardware_context(text) and has_calibration_context(text):
        findings.append(
            finding(
                severity="info",
                category="hardware-boundary",
                rule_id="hardware-calibration-proof-boundary",
                file=relative,
                line=None,
                evidence="hardware or sensor code includes calibration/tuning language",
                recommendation="Keep calibration knobs and device proof boundaries visible; less code is not a reason to delete physical-world tuning.",
                proof="Attach real-device, simulator-vs-device, sensor, timing, or calibration evidence before simplifying hardware-facing code.",
            )
        )

    if path.suffix in CODE_SUFFIXES and len(text.splitlines()) > 700 and LEGACY_MARKER_RE.search(text):
        signal = legacy_signal(text)
        first_line = None
        if signal["firstMarkerLines"]:
            first_line = int(signal["firstMarkerLines"][0]["line"])
        large_file_finding = finding(
            severity="review",
            category="does-this-need-to-exist",
            rule_id="large-legacy-file-review",
            file=relative,
            line=first_line,
            evidence=(
                f"{signal['lineCount']} lines, {signal['markerCount']} legacy/TODO markers; "
                "inspect marker lines before splitting"
            ),
            recommendation=(
                "Triage the marker cluster first: delete obsolete compatibility branches only when call-site search "
                "or tests prove they are unused; otherwise split the module around real product jobs."
            ),
            proof="Attach grep/call-site evidence for the marker lines plus focused tests before deleting or splitting behavior.",
        )
        large_file_finding["leanEvidence"] = {
            **signal,
            "safetyContext": safe_context,
            "actionHint": "Start with the first marker lines, not the whole file.",
        }
        findings.append(large_file_finding)

    if safe_context and path.suffix in CODE_SUFFIXES and findings:
        findings.append(
            finding(
                severity="info",
                category="safety-boundary",
                rule_id="do-not-cut-safety-logic-without-proof",
                file=relative,
                line=None,
                evidence="security/validation/accessibility/data-loss terms detected",
                recommendation="Treat this file as a safety boundary. Simplify only with explicit tests and proof, not by applying a generic less-code rule.",
                proof="Require before/after tests for trust-boundary validation, data-loss handling, security behavior, or accessibility behavior.",
            )
        )
    return findings


def precision_action_for(item: dict[str, Any]) -> str:
    rule_id = str(item.get("ruleId", ""))
    if rule_id in {"native-date-input", "native-color-input", "native-dialog"}:
        return "Try the native/platform control first; keep custom code only if product behavior needs it."
    if rule_id == "manual-url-params":
        return "Replace hand parsing with URL/URLSearchParams when tests prove equivalent edge-case behavior."
    if rule_id in {"dependency-date-helper-review", "dependency-small-helper-review"}:
        return "List imports before changing anything; remove the dependency only when usage is trivial and covered."
    if rule_id == "thin-wrapper-review":
        return "Inline or delete the wrapper if search proves it adds no policy, naming, compatibility, or test value."
    if rule_id == "thin-adapter-boundary":
        return "Keep the thin adapter unless host registration proof says the bridge is redundant."
    if rule_id == "hardware-calibration-proof-boundary":
        return "Do not delete calibration/tuning paths without real-device or hardware-facing proof."
    if rule_id == "large-legacy-file-review":
        return "Do not split the whole file first; start at the first marker line and prove one removable branch."
    return str(item.get("recommendation", "Review whether this code still earns its complexity."))


def build_precision_review(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Turn raw lean findings into a Ponytail-style action ledger."""
    candidates = [item for item in findings if item.get("severity") in {"review", "opportunity"}]
    delete_list: list[dict[str, Any]] = []
    keep_list: list[dict[str, Any]] = []
    simplify_first: list[dict[str, Any]] = []
    blocked_by_proof: list[dict[str, Any]] = []

    for index, item in enumerate(candidates, start=1):
        evidence = item.get("evidence", {})
        file_name = str(evidence.get("file", ""))
        line = evidence.get("line")
        location = f"{file_name}:{line}" if line else file_name
        entry = {
            "rank": index,
            "ruleId": item.get("ruleId"),
            "location": location,
            "severity": item.get("severity"),
            "action": precision_action_for(item),
            "proofRequired": item.get("proofGuidance"),
        }
        rule_id = str(item.get("ruleId", ""))
        if rule_id == "thin-wrapper-review":
            delete_list.append({**entry, "deleteWhen": "Search proves the wrapper is private and behavior-neutral."})
        elif rule_id in {"large-legacy-file-review"}:
            blocked_by_proof.append(entry)
        else:
            simplify_first.append(entry)

    safety_items = [item for item in findings if item.get("ruleId") == "do-not-cut-safety-logic-without-proof"]
    boundary_items = safety_items + [
        item
        for item in findings
        if item.get("ruleId") in {"thin-adapter-boundary", "hardware-calibration-proof-boundary"}
    ]
    for item in boundary_items[:20]:
        evidence = item.get("evidence", {})
        keep_list.append(
            {
                "ruleId": item.get("ruleId"),
                "location": str(evidence.get("file", "")),
                "reason": str(item.get("recommendation") or "Less-code pressure is not enough."),
                "proofRequired": item.get("proofGuidance"),
            }
        )

    top_actions = (delete_list + simplify_first + blocked_by_proof)[:5]
    return {
        "principle": "The best ShipGuard code is the code that proves it needs to exist.",
        "decisionLadder": [
            {"rung": 1, "question": "Does this need to exist?", "shipguardAction": "delete or skip when proof says no"},
            {"rung": 2, "question": "Can the standard library do it?", "shipguardAction": "replace custom parsing/formatting with stdlib"},
            {"rung": 3, "question": "Can the native platform do it?", "shipguardAction": "prefer platform controls and platform proof"},
            {"rung": 4, "question": "Is an installed dependency already enough?", "shipguardAction": "reuse before adding a wrapper"},
            {"rung": 5, "question": "Can one clear line replace a helper?", "shipguardAction": "inline private thin wrappers"},
            {"rung": 6, "question": "What is the minimum code that works?", "shipguardAction": "write only the proven missing behavior"},
        ],
        "deleteList": delete_list[:20],
        "simplifyFirst": simplify_first[:20],
        "keepList": keep_list[:20],
        "blockedByProof": blocked_by_proof[:20],
        "topActions": top_actions,
        "summary": {
            "deleteCandidates": len(delete_list),
            "simplifyCandidates": len(simplify_first),
            "keepBoundaries": len(keep_list),
            "proofBlockedCandidates": len(blocked_by_proof),
        },
    }


def build_behavior_gates(findings: list[dict[str, Any]], lean_debt_ledger: dict[str, Any]) -> dict[str, Any]:
    rule_ids = {str(item.get("ruleId") or "") for item in findings}
    return {
        "oneRunnableCheck": {
            "status": "enforced-in-lean-review",
            "ruleIds": ["one-runnable-check-missing-diff"],
            "policy": "Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony.",
        },
        "hardwareCalibration": {
            "status": "active" if "hardware-calibration-proof-boundary" in rule_ids else "available",
            "ruleIds": ["hardware-calibration-proof-boundary", "hardware-calibration-missing-diff"],
            "policy": "Hardware, sensors, clocks, and physical devices need calibration/tuning proof before simplification.",
        },
        "requestedExplanation": {
            "status": "policy",
            "policy": "Explicitly requested reports, walkthroughs, or phase notes are not clutter; Lean Deck targets unrequested code/prose bloat.",
        },
        "adapterBoundary": {
            "status": "active" if "thin-adapter-boundary" in rule_ids else "available",
            "ruleIds": ["thin-adapter-boundary"],
            "policy": "Thin host adapters can be the product surface; flag them as keep-with-proof instead of deletion candidates.",
        },
        "shortcutDebt": {
            "status": "pass"
            if int(lean_debt_ledger.get("summary", {}).get("missingUpgradeTrigger") or 0) == 0
            else "review",
            "markers": int(lean_debt_ledger.get("summary", {}).get("markers") or 0),
            "missingUpgradeTrigger": int(lean_debt_ledger.get("summary", {}).get("missingUpgradeTrigger") or 0),
            "policy": "Every intentional shortcut needs a ceiling and upgrade trigger.",
        },
        "gainHonesty": {
            "status": "available-in-lean-gain",
            "policy": "ShipGuard reports benchmark impact separately and does not invent per-repo line, token, cost, or time savings.",
        },
    }


def native_opportunity_catalog() -> list[dict[str, str]]:
    return [
        {"surface": "browser forms", "insteadOf": "date/color/range/dialog libraries", "prefer": "native input, dialog, details, progress, meter, and datalist controls when product behavior fits"},
        {"surface": "browser APIs", "insteadOf": "query-string, uuid, clipboard, clone, observer wrappers", "prefer": "URLSearchParams, crypto.randomUUID, navigator.clipboard, structuredClone, IntersectionObserver, ResizeObserver"},
        {"surface": "CSS", "insteadOf": "JavaScript for basic layout or motion preferences", "prefer": "container queries, CSS custom properties, prefers-reduced-motion, sticky, scroll snap, aspect-ratio"},
        {"surface": "Python", "insteadOf": "small compatibility packages for modern Python", "prefer": "dataclasses, pathlib, enum, argparse, zoneinfo, datetime.fromisoformat, itertools, functools"},
        {"surface": "Node", "insteadOf": "mkdirp/rimraf/path-exists/load-json wrappers", "prefer": "fs.mkdirSync({recursive:true}), fs.rmSync({recursive:true,force:true}), fs.existsSync, JSON.parse/readFileSync"},
        {"surface": "database", "insteadOf": "application code for constraints and aggregation", "prefer": "unique/check/foreign-key constraints, window functions, recursive CTEs, generated columns, full-text indexes"},
    ]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"lean-audit: path does not exist: {root}")
    files, scan_scope = iter_files(root)
    findings = scan_package(root)
    for path in files:
        findings.extend(scan_file(root, path))
    findings = sorted(
        findings,
        key=lambda item: (
            FINDING_PRIORITY.get(str(item.get("severity")), 9),
            str(item.get("evidence", {}).get("file", "")),
            str(item.get("ruleId", "")),
        ),
    )
    emitted_findings = findings[:120]
    precision_review = build_precision_review(emitted_findings)
    lean_debt_ledger = scan_lean_debt(root, files)
    rule_counts = Counter(str(f["ruleId"]) for f in emitted_findings)
    result = "pass" if not [f for f in emitted_findings if f["severity"] in {"review", "opportunity"}] else "review"
    display_root = "." if args.shareable else str(root)
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": result,
        "target": {"path": display_root, "shareable": bool(args.shareable)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native, read-only lean-code audit. It does not vendor Ponytail code or hide source influence.",
        },
        "leanLadder": [
            "Does this need to exist?",
            "Can the standard library do it?",
            "Can the native platform do it?",
            "Is an installed dependency already enough?",
            "Can one clear line replace a helper?",
            "Only then write the minimum code that works.",
        ],
        "behaviorGates": build_behavior_gates(emitted_findings, lean_debt_ledger),
        "nativeOpportunityCatalog": native_opportunity_catalog(),
        "precisionReview": precision_review,
        "leanDebtLedger": lean_debt_ledger,
        "safetyBoundary": [
            "Do not cut trust-boundary validation without proof.",
            "Do not cut data-loss handling without proof.",
            "Do not cut security controls without proof.",
            "Do not cut accessibility behavior without proof.",
        ],
        "metrics": {
            "filesScanned": len(files),
            "findings": len(emitted_findings),
            "reviewFindings": len([f for f in emitted_findings if f["severity"] == "review"]),
            "opportunityFindings": len([f for f in emitted_findings if f["severity"] == "opportunity"]),
            "infoFindings": len([f for f in emitted_findings if f["severity"] == "info"]),
            "findingsOmittedByLimit": max(0, len(findings) - len(emitted_findings)),
        },
        "scanScope": scan_scope,
        "ruleSummary": [
            {
                "ruleId": rule_id,
                "count": count,
                "firstEvidence": next(
                    (
                        f"{f['evidence']['file']}:{f['evidence']['line']}"
                        if f["evidence"].get("line")
                        else f["evidence"]["file"]
                    )
                    for f in emitted_findings
                    if f["ruleId"] == rule_id
                ),
            }
            for rule_id, count in rule_counts.most_common()
        ],
        "findings": emitted_findings,
        "nextActions": [
            "Start with precisionReview.topActions[0] and prove whether the code earns its complexity.",
            "If precisionReview.deleteList is empty, do not force deletion; simplify the smallest proven surface instead.",
            "Prove current behavior first, then simplify the smallest surface.",
            "Run shipguard ios report-quality on this Lean Deck output if you are improving ShipGuard itself.",
        ],
    }
    if args.shipguard_eval:
        report["scopeBoundary"] = (
            "This is ShipGuard product QA. Real target evidence may show where ShipGuard reports are noisy, vague, or "
            "under-prioritized; it is not authorization to edit that target repo."
        )
        report["reportQualityQuestions"] = [
            "Does precisionReview identify delete, simplify, keep, and proof-blocked decisions instead of dumping findings?",
            "Does Lean Deck separate real simplification candidates from safety-boundary files?",
            "Does Lean Deck protect host adapters, hardware calibration, requested explanation, and one-check minimums from false less-code pressure?",
            "Does each finding explain the proof needed before removing code?",
            "Does the report help a solo developer delete clutter without deleting product behavior?",
            "Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?",
            "Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?",
            "Should this recurring lean-code observation become a public fixture instead of depending on one current repo scan?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Lean Deck",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        f"- Files scanned: {report['metrics']['filesScanned']}",
        f"- Findings: {report['metrics']['findings']}",
        "",
        "## Lean Ladder",
        "",
    ]
    for step in report["leanLadder"]:
        lines.append(f"- {step}")
    gates = report.get("behaviorGates", {})
    if gates:
        lines.extend(["", "## Behavior Gates", ""])
        for name, gate in gates.items():
            if not isinstance(gate, dict):
                continue
            status = gate.get("status", "available")
            policy = str(gate.get("policy", "")).replace("|", "\\|")
            lines.append(f"- `{name}`: {status} - {policy}")
    catalog = report.get("nativeOpportunityCatalog", [])
    if catalog:
        lines.extend(["", "## Native Opportunity Catalog", ""])
        lines.extend(["| Surface | Before Owning Code | Prefer |", "| --- | --- | --- |"])
        for item in catalog:
            lines.append(
                f"| {item.get('surface', '')} | {str(item.get('insteadOf', '')).replace('|', '\\|')} | "
                f"{str(item.get('prefer', '')).replace('|', '\\|')} |"
            )
    precision = report.get("precisionReview", {})
    lines.extend(["", "## Precision Review", ""])
    summary = precision.get("summary", {})
    if summary:
        lines.append(
            f"- Delete candidates: {summary.get('deleteCandidates', 0)}; "
            f"simplify candidates: {summary.get('simplifyCandidates', 0)}; "
            f"keep boundaries: {summary.get('keepBoundaries', 0)}; "
            f"proof-blocked candidates: {summary.get('proofBlockedCandidates', 0)}"
        )
    top_actions = precision.get("topActions", [])
    if top_actions:
        lines.extend(["", "| Rank | Decision | Location | Action | Proof |", "| ---: | --- | --- | --- | --- |"])
        for action in top_actions:
            decision = "delete" if action in precision.get("deleteList", []) else "simplify"
            if action in precision.get("blockedByProof", []):
                decision = "proof-blocked"
            lines.append(
                f"| {action.get('rank', '-')} | {decision} | {action.get('location', '')} | "
                f"{str(action.get('action', '')).replace('|', '\\|')} | "
                f"{str(action.get('proofRequired', '')).replace('|', '\\|')} |"
            )
    keep_list = precision.get("keepList", [])
    if keep_list:
        lines.extend(["", "### Keep Without More Proof", ""])
        for item in keep_list[:8]:
            lines.append(f"- `{item.get('location', '')}`: {item.get('reason', '')}")
    lines.extend(["", "## Safety Boundary", ""])
    for item in report["safetyBoundary"]:
        lines.append(f"- {item}")
    debt = report.get("leanDebtLedger", {})
    if debt:
        debt_summary = debt.get("summary", {})
        lines.extend(["", "## Lean Debt Ledger", ""])
        lines.append(
            f"- Markers: {debt_summary.get('markers', 0)}; "
            f"missing upgrade trigger: {debt_summary.get('missingUpgradeTrigger', 0)}"
        )
        markers = debt.get("markers", [])
        if markers:
            lines.extend(["", "| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |", "| --- | --- | --- | --- | --- | --- |"])
            for item in markers[:20]:
                location = f"{item.get('file', '')}:{item.get('line', '')}"
                lines.append(
                    f"| {item.get('status', '')} | `{item.get('marker', '')}` | {location} | "
                    f"{str(item.get('summary', '')).replace('|', '\\|')} | "
                    f"{str(item.get('ceiling', '') or '-').replace('|', '\\|')} | "
                    f"{str(item.get('upgrade', '') or '-').replace('|', '\\|')} |"
                )
        else:
            lines.append("No `ponytail:` or `shipguard-lean:` shortcut markers found.")
    lines.extend(["", "## Findings", ""])
    if report.get("ruleSummary"):
        lines.extend(["| Rule | Count | First Evidence |", "| --- | ---: | --- |"])
        for item in report["ruleSummary"]:
            lines.append(f"| `{item['ruleId']}` | {item['count']} | {item['firstEvidence']} |")
        lines.append("")
    if not report["findings"]:
        lines.append("No lean-code findings were detected by this bounded scan.")
    else:
        lines.extend(["| Severity | Rule | Evidence | Recommendation | Proof |", "| --- | --- | --- | --- | --- |"])
        for item in report["findings"]:
            evidence = item["evidence"]
            location = evidence["file"]
            if evidence.get("line"):
                location = f"{location}:{evidence['line']}"
            snippet = str(evidence.get("snippet", "")).replace("|", "\\|")
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | {location}: {snippet} | "
                f"{item['recommendation']} | {item['proofGuidance']} |"
            )
    lean_evidence_items = [item for item in report["findings"] if item.get("leanEvidence")]
    if lean_evidence_items:
        lines.extend(["", "## Lean Evidence Packets", ""])
        lines.extend(["| File | Lines | Markers | First Marker Lines | Action Hint |", "| --- | ---: | ---: | --- | --- |"])
        for item in lean_evidence_items[:20]:
            evidence = item["evidence"]
            lean_evidence = item["leanEvidence"]
            marker_lines = ", ".join(str(marker["line"]) for marker in lean_evidence.get("firstMarkerLines", []))
            marker_lines = marker_lines or "-"
            action_hint = str(lean_evidence.get("actionHint", "")).replace("|", "\\|")
            lines.append(
                f"| {evidence['file']} | {lean_evidence.get('lineCount', 0)} | "
                f"{lean_evidence.get('markerCount', 0)} | {marker_lines} | {action_hint} |"
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
    (out / "lean-audit.json").write_text(json_text, encoding="utf-8")
    (out / "lean-audit.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
