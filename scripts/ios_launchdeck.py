#!/usr/bin/env python3
"""ShipGuard LaunchDeck: route iOS build, preview, debug, and profiler proof."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope
import ios_shareable


SCHEMA_VERSION = 1
SURFACE_NAME = "ShipGuard LaunchDeck"
SURFACE_CODENAME = "launchdeck"
SURFACE_TAGLINE = "Launch control for iOS build, preview, debug, profiler, and proof-cargo work."
LANE_NAMES = {
    "xcodebuildmcp-build-run": "Harbor Check",
    "xcodebuildmcp-debug": "Black Box Replay",
    "simulator-browser-preview": "Glass Deck",
    "swiftui-preview-hot-reload": "Hot-Swap Dock",
    "ios-profiler-performance": "Trace Radar",
    "repo-build-topology-review": "Map Room",
}
WORKFLOWS = {
    "auto",
    "build-run",
    "debug",
    "preview",
    "performance",
}
SOURCE_SUFFIXES = {
    ".swift",
    ".plist",
    ".entitlements",
    ".storekit",
    ".xctestplan",
    ".xcconfig",
    ".pbxproj",
    ".md",
}
MAX_RECEIPT_FILES = 200
MAX_RECEIPT_BYTES = 256 * 1024
RECEIPT_REQUIRED_SIGNALS = {
    "xcodebuildmcp-build-run": ["buildRunProof", "uiProof"],
    "xcodebuildmcp-debug": ["buildRunProof", "logProof", "uiProof"],
    "simulator-browser-preview": ["simulatorBrowserProof", "uiProof"],
    "swiftui-preview-hot-reload": ["swiftuiPreviewProof", "simulatorBrowserProof", "uiProof"],
    "ios-profiler-performance": ["buildRunProof", "performanceProof"],
}
RECEIPT_SIGNAL_TITLES = {
    "buildRunProof": "XcodeBuildMCP build/run proof",
    "uiProof": "UI screenshot or describe_ui proof",
    "logProof": "Runtime log capture proof",
    "simulatorBrowserProof": "Simulator browser serve-sim proof",
    "swiftuiPreviewProof": "SwiftUI preview hot reload proof",
    "performanceProof": "Profiler or performance capture proof",
    "deviceProof": "Physical-device proof",
}
RECEIPT_MISSING_RULES = {
    "buildRunProof": "launchdeck-build-run-receipt-missing",
    "uiProof": "launchdeck-ui-receipt-missing",
    "logProof": "launchdeck-log-receipt-missing",
    "simulatorBrowserProof": "launchdeck-simulator-browser-receipt-missing",
    "swiftuiPreviewProof": "launchdeck-swiftui-preview-receipt-missing",
    "performanceProof": "launchdeck-performance-receipt-missing",
    "deviceProof": "launchdeck-device-receipt-missing",
}
TEXT_RECEIPT_SUFFIXES = {
    ".json",
    ".log",
    ".md",
    ".txt",
    ".html",
    ".xml",
    ".plist",
    ".swift",
    ".sh",
    ".stdout",
    ".stderr",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-launchdeck: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"{SURFACE_NAME}: route iOS build, debug, preview, profiler, and proof-cargo workflows."
    )
    parser.add_argument("--path", default=".", help="iOS repo root to inspect")
    parser.add_argument("--out", help="Output directory for ios-launchdeck.md and ios-launchdeck.json")
    parser.add_argument(
        "--workflow",
        choices=sorted(WORKFLOWS),
        default="auto",
        help="Workflow emphasis. Default: auto",
    )
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument(
        "--receipt",
        action="append",
        default=[],
        help="LaunchDeck proof-cargo file or directory to grade after Codex/XcodeBuildMCP execution. May be passed multiple times.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from JSON and Markdown before external sharing or report-quality scoring.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


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
    return relative.as_posix() or "."


def receipt_path_label(path: Path, *, inputs: list[Path], shareable: bool) -> str:
    if not shareable:
        return path.as_posix()
    for index, input_path in enumerate(inputs, start=1):
        base = input_path if input_path.is_dir() else input_path.parent
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        suffix = relative.as_posix()
        return f"<receipt-input-{index}>" if not suffix or suffix == "." else f"<receipt-input-{index}>/{suffix}"
    return "<receipt-path>"


def read_text(path: Path) -> str:
    return ios_scan_scope.read_text_limited(path).text


def shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def read_receipt_text(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return ""
    suffix = path.suffix.lower()
    if suffix not in TEXT_RECEIPT_SUFFIXES and size > MAX_RECEIPT_BYTES:
        return ""
    try:
        data = path.read_bytes()[:MAX_RECEIPT_BYTES]
    except OSError:
        return ""
    if b"\x00" in data[:2048]:
        return ""
    return data.decode("utf-8", errors="ignore")


def iter_receipt_files(path: Path) -> tuple[list[Path], bool]:
    if path.is_file():
        return [path], False
    files: list[Path] = []
    truncated = False
    if not path.is_dir():
        return files, False
    for candidate in sorted(path.rglob("*")):
        if not candidate.is_file():
            continue
        files.append(candidate)
        if len(files) >= MAX_RECEIPT_FILES:
            truncated = True
            break
    return files, truncated


def receipt_matchers(path: Path, text: str) -> dict[str, list[str]]:
    lowered_name = path.name.lower()
    suffix = path.suffix.lower()
    lowered = text.lower()
    matches: dict[str, list[str]] = {key: [] for key in RECEIPT_SIGNAL_TITLES}

    def mark(signal: str, marker: str) -> None:
        if marker not in matches[signal]:
            matches[signal].append(marker)

    if suffix in {".png", ".jpg", ".jpeg"} or "screenshot" in lowered_name:
        mark("uiProof", "screenshot image")
    if suffix == ".log" or "log" in lowered_name:
        mark("logProof", "log file")
    if suffix in {".trace", ".xcresult"} or lowered_name.endswith(".trace") or lowered_name.endswith(".xcresult"):
        mark("performanceProof", suffix or "trace artifact")

    token_groups = {
        "buildRunProof": [
            "session_show_defaults",
            "session_set_defaults",
            "build_run_sim",
            "build succeeded",
            "** build succeeded **",
            "launch_app_sim",
            "install_app_sim",
            "xcodebuild",
            "launching ",
        ],
        "uiProof": ["describe_ui", "elementref", "\"elements\"", "ui snapshot", "screenshot"],
        "logProof": ["start_sim_log_cap", "stop_sim_log_cap", "console output", "os_log", "runtime log"],
        "simulatorBrowserProof": ["serve-sim", "simulator browser", "preview url", "localhost", "127.0.0.1"],
        "swiftuiPreviewProof": [
            "swiftui-preview-browser.mjs",
            "hot reload",
            "hot reloaded package preview",
            "#preview",
            "previewprovider",
        ],
        "performanceProof": [
            "animation hitches",
            "time profiler",
            "xctrace",
            "instruments",
            "ettrace",
            "flamegraph",
            "sample ",
            "spindump",
        ],
        "deviceProof": [
            "physical device",
            "pro motion",
            "promotion",
            "touch latency",
            "thermal",
            "haptic",
            "iphone",
            "udid",
        ],
    }
    for signal, tokens in token_groups.items():
        for token in tokens:
            if token in lowered or token in lowered_name:
                mark(signal, token.strip())
    return matches


def collect_execution_receipts(raw_inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    if not raw_inputs:
        return {
            "status": "not-provided",
            "inputs": [],
            "summary": {
                "inputCount": 0,
                "existingInputCount": 0,
                "fileCount": 0,
                "filesScanned": 0,
                "truncated": False,
                **{signal: False for signal in RECEIPT_SIGNAL_TITLES},
            },
            "signals": [
                {
                    "id": signal,
                    "title": title,
                    "present": False,
                    "evidence": [],
                }
                for signal, title in RECEIPT_SIGNAL_TITLES.items()
            ],
        }

    resolved_inputs = [Path(item).expanduser().resolve() for item in raw_inputs]
    files: list[Path] = []
    input_rows: list[dict[str, Any]] = []
    any_truncated = False
    existing_count = 0
    for index, path in enumerate(resolved_inputs, start=1):
        exists = path.exists()
        kind = "missing"
        input_files: list[Path] = []
        truncated = False
        if exists:
            existing_count += 1
            kind = "directory" if path.is_dir() else "file" if path.is_file() else "other"
            input_files, truncated = iter_receipt_files(path)
            any_truncated = any_truncated or truncated
            files.extend(input_files)
        input_rows.append(
            {
                "index": index,
                "path": f"<receipt-input-{index}>" if shareable else path.as_posix(),
                "kind": kind,
                "exists": exists,
                "fileCount": len(input_files),
                "truncated": truncated,
            }
        )

    unique_files = sorted({path for path in files})
    signal_evidence: dict[str, list[dict[str, str]]] = {signal: [] for signal in RECEIPT_SIGNAL_TITLES}
    for path in unique_files[:MAX_RECEIPT_FILES]:
        text = read_receipt_text(path)
        matches = receipt_matchers(path, text)
        display_path = receipt_path_label(path, inputs=resolved_inputs, shareable=shareable)
        for signal, markers in matches.items():
            for marker in markers:
                if len(signal_evidence[signal]) >= 8:
                    continue
                row = {"path": display_path, "marker": marker}
                if row not in signal_evidence[signal]:
                    signal_evidence[signal].append(row)

    summary = {
        "inputCount": len(raw_inputs),
        "existingInputCount": existing_count,
        "fileCount": len(unique_files),
        "filesScanned": min(len(unique_files), MAX_RECEIPT_FILES),
        "truncated": any_truncated or len(unique_files) > MAX_RECEIPT_FILES,
    }
    for signal in RECEIPT_SIGNAL_TITLES:
        summary[signal] = bool(signal_evidence[signal])

    status = "provided" if existing_count and unique_files else "missing"
    return {
        "status": status,
        "inputs": input_rows,
        "summary": summary,
        "signals": [
            {
                "id": signal,
                "title": RECEIPT_SIGNAL_TITLES[signal],
                "present": bool(signal_evidence[signal]),
                "evidence": signal_evidence[signal],
            }
            for signal in RECEIPT_SIGNAL_TITLES
        ],
    }


def first_project(doctor: dict[str, Any]) -> dict[str, Any] | None:
    projects = doctor.get("xcode_projects")
    if isinstance(projects, list) and projects:
        return projects[0]
    return None


def first_workspace(doctor: dict[str, Any]) -> dict[str, Any] | None:
    workspaces = doctor.get("xcode_workspaces")
    if isinstance(workspaces, list) and workspaces:
        return workspaces[0]
    return None


def first_package(doctor: dict[str, Any]) -> dict[str, Any] | None:
    packages = doctor.get("swift_packages")
    if isinstance(packages, list) and packages:
        return packages[0]
    return None


def first_scheme(project: dict[str, Any] | None) -> str | None:
    if not project:
        return None
    schemes = project.get("schemes")
    if isinstance(schemes, list) and schemes:
        return str(schemes[0])
    targets = project.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if isinstance(target, str) and not target.lower().endswith("tests"):
                return target
    return None


def first_app_target(project: dict[str, Any] | None) -> str | None:
    if not project:
        return None
    details = project.get("target_details")
    if isinstance(details, list):
        for item in details:
            if isinstance(item, dict) and item.get("kind") == "app" and item.get("name"):
                return str(item["name"])
        for item in details:
            if isinstance(item, dict) and item.get("name"):
                name = str(item["name"])
                if not name.lower().endswith("tests"):
                    return name
    targets = project.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if isinstance(target, str) and not target.lower().endswith("tests"):
                return target
    return None


def target_label(value: str | None) -> str:
    return value if value else "<choose-target>"


def collect_preview_metrics(root: Path) -> dict[str, Any]:
    scan = ios_scan_scope.iter_files(root, {".swift"})
    preview_files: list[str] = []
    declaration_count = 0
    truncated_files: list[Path] = []
    omitted_files: list[Path] = []
    timed_out_files: list[Path] = []
    for path in scan.files:
        source = ios_scan_scope.read_text_limited(path)
        if source.omitted:
            omitted_files.append(path)
            if source.timed_out:
                timed_out_files.append(path)
            continue
        if source.truncated:
            truncated_files.append(path)
        text = source.text
        count = text.count("#Preview") + text.count("PreviewProvider")
        if count:
            preview_files.append(rel(path, root))
            declaration_count += count
    return {
        "swiftFilesScanned": len(scan.files),
        "truncatedSwiftFiles": len(truncated_files),
        "omittedLargeSwiftFiles": len(omitted_files),
        "timedOutSwiftFiles": len(timed_out_files),
        "previewDeclarationCount": declaration_count,
        "previewFiles": preview_files[:12],
        "previewFileListTruncated": len(preview_files) > 12,
        "scanScope": ios_scan_scope.summary_with_text_limits(
            scan,
            root,
            truncated_text_files=truncated_files,
            omitted_large_text_files=omitted_files,
            timed_out_text_files=timed_out_files,
        ),
    }


def build_target(root: Path, doctor: dict[str, Any], *, shareable: bool) -> dict[str, Any]:
    project = first_project(doctor)
    workspace = first_workspace(doctor)
    package = first_package(doctor)
    scheme = first_scheme(project)
    app_target = first_app_target(project)
    package_targets = package.get("targets") if isinstance(package, dict) and isinstance(package.get("targets"), list) else []
    package_target = str(package_targets[0]) if package_targets else None
    has_xcode_target = project is not None and scheme is not None
    has_package_target = package is not None and package_target is not None
    status = "ready" if has_xcode_target or has_package_target else "needs-project-selection"
    return {
        "status": status,
        "workspacePath": workspace.get("path") if isinstance(workspace, dict) else None,
        "projectPath": project.get("path") if isinstance(project, dict) else None,
        "packagePath": package.get("path") if isinstance(package, dict) else None,
        "scheme": scheme,
        "appTarget": app_target,
        "packageTarget": package_target,
        "preferredXcodeSelector": "workspace" if workspace else "project" if project else "package" if package else "none",
        "recommendedSimulator": "Use XcodeBuildMCP list_sims through LaunchDeck's Harbor Check route and choose a bootable iPhone simulator; do not assume a simulator ID from source.",
        "root": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
    }


def workflow_id(requested: str, target: dict[str, Any], preview: dict[str, Any]) -> str:
    if requested == "build-run":
        return "xcodebuildmcp-build-run"
    if requested == "debug":
        return "xcodebuildmcp-debug"
    if requested == "preview":
        if target.get("packageTarget"):
            return "swiftui-preview-hot-reload"
        return "simulator-browser-preview"
    if requested == "performance":
        return "ios-profiler-performance"
    if target.get("status") == "ready" and target.get("scheme"):
        return "xcodebuildmcp-build-run"
    if target.get("packageTarget") or int(preview.get("previewDeclarationCount") or 0) > 0:
        return "swiftui-preview-hot-reload"
    return "repo-build-topology-review"


def xcode_selector(target: dict[str, Any]) -> dict[str, str] | None:
    if target.get("workspacePath"):
        return {"kind": "workspace", "path": str(target["workspacePath"])}
    if target.get("projectPath"):
        return {"kind": "project", "path": str(target["projectPath"])}
    return None


def build_xcodebuildmcp_workflow(target: dict[str, Any]) -> dict[str, Any]:
    selector = xcode_selector(target)
    selector_text = f"{selector['kind']}={selector['path']}" if selector else "select project/workspace"
    scheme = target_label(target.get("scheme"))
    return {
        "id": "xcodebuildmcp-build-run",
        "title": "Harbor Check",
        "plainTitle": "XcodeBuildMCP Build/Run",
        "capability": "launchdeck:ios-debugger-agent",
        "codexTools": [
            "session_show_defaults",
            "session_set_defaults",
            "build_run_sim",
            "describe_ui or screenshot",
            "start_sim_log_cap / stop_sim_log_cap when investigating runtime behavior",
        ],
        "commands": [
            "session_show_defaults",
            f"session_set_defaults with {selector_text}, scheme={scheme}, simulator=<chosen simulator from list_sims>",
            "build_run_sim",
            "describe_ui or screenshot",
        ],
        "proofArtifacts": [
            "build output or failure summary",
            "running simulator screenshot or UI description",
            "log capture when debugging runtime behavior",
        ],
        "shipguardRole": "LaunchDeck chooses the repo-aware route, records target assumptions, and turns proof cargo into reports.",
        "executionRole": "Codex iOS execution tools run the simulator build, launch, UI snapshot, and log capture.",
    }


def build_debug_workflow() -> dict[str, Any]:
    return {
        "id": "xcodebuildmcp-debug",
        "title": "Black Box Replay",
        "plainTitle": "Debugger And Runtime Investigation",
        "capability": "launchdeck:ios-debugger-agent",
        "codexTools": [
            "build_run_sim",
            "start_sim_log_cap",
            "stop_sim_log_cap",
            "ui_describe",
            "simctl-aware screenshots",
        ],
        "commands": [
            "Build and launch the same scheme in Simulator.",
            "Capture logs around one reproduction path.",
            "Attach UI snapshot or screenshot to every behavioral claim.",
        ],
        "proofArtifacts": [
            "focused log excerpt",
            "one reproduction path",
            "screenshot/UI tree before and after the investigated action",
        ],
        "shipguardRole": "LaunchDeck keeps the debug path scoped to a single reproduction and prevents vague app-wide claims.",
        "executionRole": "Codex iOS execution tools drive the simulator, capture logs, and expose UI/runtime evidence.",
    }


def build_simulator_browser_workflow() -> dict[str, Any]:
    return {
        "id": "simulator-browser-preview",
        "title": "Glass Deck",
        "plainTitle": "Simulator Browser Preview",
        "capability": "launchdeck:ios-simulator-browser",
        "codexTools": [
            "serve-sim through the LaunchDeck simulator browser workflow",
            "browser screenshot after the simulator frame is visible",
        ],
        "commands": [
            "npx --yes serve-sim@latest <simulator-udid>",
            "Open the served URL in the Codex in-app browser.",
            "npx --yes serve-sim@latest --kill <simulator-udid>",
        ],
        "proofArtifacts": [
            "phone-shaped simulator browser screenshot",
            "served preview URL",
            "cleanup command evidence",
        ],
        "shipguardRole": "LaunchDeck points visual QA, design QA, and Devspace planning at a stable preview route.",
        "executionRole": "Codex iOS execution tools stream the selected simulator into the browser.",
    }


def build_swiftui_preview_workflow(target: dict[str, Any]) -> dict[str, Any]:
    package_path = target_label(target.get("packagePath"))
    package_target = target_label(target.get("packageTarget") or target.get("appTarget"))
    command = (
        "node <launchdeck>/scripts/swiftui-preview-browser.mjs "
        f"{shell_quote(package_path)} --package-target {shell_quote(package_target)} --device <simulator-udid>"
    )
    return {
        "id": "swiftui-preview-hot-reload",
        "title": "Hot-Swap Dock",
        "plainTitle": "SwiftUI Preview Hot Reload",
        "capability": "launchdeck:swiftui-ui-patterns",
        "codexTools": [
            "swiftui-preview-browser.mjs",
            "serve-sim scoped to the preview simulator",
            "screenshot after the preview surface loads",
        ],
        "commands": [
            command,
            "Keep the preview process running only while validating the local UI loop.",
            "Capture one screenshot before claiming preview or hot-reload proof.",
        ],
        "proofArtifacts": [
            "preview browser URL",
            "loaded preview screenshot",
            "hot-reload or rebuild receipt when a preview source changes",
        ],
        "shipguardRole": "LaunchDeck selects when preview proof is enough and when a full app build is still required.",
        "executionRole": "Codex iOS execution tools run the preview browser and simulator-backed hot reload loop.",
    }


def build_performance_workflow() -> dict[str, Any]:
    return {
        "id": "ios-profiler-performance",
        "title": "Trace Radar",
        "plainTitle": "Performance Profiling",
        "capability": "launchdeck:swiftui-performance-audit and ios-ettrace-performance",
        "codexTools": [
            "Animation Hitches or Time Profiler trace when Instruments templates are available",
            "xctrace list templates before recording",
            "sample/log/screenshot fallback when templates are unavailable",
        ],
        "commands": [
            "Run `shipguard ios performance --path <repo> --out <dir> --shareable` for static risk routing.",
            "Use LaunchDeck profiler guidance for one route: launch, scroll, tap, or animation.",
            "Use a physical iPhone before claiming ProMotion, touch latency, haptic quality, thermal behavior, or display-specific smoothness.",
        ],
        "proofArtifacts": [
            "static ShipGuard performance report",
            "Instruments trace or recorded fallback evidence",
            "device-only proof receipt for hardware claims",
        ],
        "shipguardRole": "LaunchDeck names the route, proof boundary, and stop condition before performance edits.",
        "executionRole": "Codex iOS execution tools capture and interpret simulator or device profiler evidence.",
    }


def build_workflows(target: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        build_xcodebuildmcp_workflow(target),
        build_debug_workflow(),
        build_simulator_browser_workflow(),
        build_swiftui_preview_workflow(target),
        build_performance_workflow(),
    ]


def integration_summary() -> dict[str, Any]:
    return {
        "surface": SURFACE_NAME,
        "codename": SURFACE_CODENAME,
        "tagline": SURFACE_TAGLINE,
        "integration": "native-shipguard-launch-control",
        "lanes": LANE_NAMES,
        "capabilities": {
            "xcodeBuildMCP": "Build, run, debug, inspect UI, and capture logs from iOS Simulator.",
            "simulatorBrowser": "Expose a selected simulator as a browser-visible phone frame.",
            "swiftUIPreviewHotReload": "Run SwiftUI package previews through the simulator browser loop.",
            "performanceProfiling": "Capture Animation Hitches, Time Profiler, samples, or fallback evidence for iOS smoothness work.",
        },
        "boundary": [
            "ShipGuard CLI cannot directly call Codex MCP tools from a non-Codex shell.",
            "LaunchDeck owns discovery, routing, report quality, proof boundaries, and handoff text.",
            "Codex iOS execution tools perform actual simulator, debugger, browser-preview, and profiler work inside Codex.",
        ],
    }


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate whether ShipGuard makes LaunchDeck workflows obvious.",
            "Identify missing build/run/debug/preview/performance routing in ShipGuard reports.",
            "Create public fixtures or eval cases that exercise LaunchDeck without private app code.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not convert simulator or profiler findings into target-app remediation tasks.",
            "Do not present target-app build issues as the active development goal unless separately authorized.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Does the report make ShipGuard feel like the front door for LaunchDeck rather than a separate plugin the user must remember?",
        "Does it name the exact XcodeBuildMCP default-setting and build_run_sim route for this repo?",
        "Does it separate ShipGuard routing/proof ownership from Codex execution ownership?",
        "Does it choose between full app build, simulator browser preview, SwiftUI preview hot reload, and performance profiling using repo evidence?",
        "Does it distinguish planned LaunchDeck routing from execution receipt quality after Codex runs the workflow?",
        "When receipts are supplied, does it name missing build/run, UI, preview, log, or profiler proof for the selected lane?",
    ]


def receipt_signal_title(signal: str) -> str:
    return RECEIPT_SIGNAL_TITLES.get(signal, signal)


def grade_receipt_quality(workflow: str, execution_receipts: dict[str, Any]) -> dict[str, Any]:
    required = RECEIPT_REQUIRED_SIGNALS.get(workflow, [])
    summary = execution_receipts.get("summary") if isinstance(execution_receipts.get("summary"), dict) else {}
    present = [signal for signal in required if summary.get(signal) is True]
    missing = [signal for signal in required if signal not in present]
    findings: list[dict[str, str]] = []
    receipt_status = str(execution_receipts.get("status") or "not-provided")

    if receipt_status == "not-provided":
        findings.append(
            {
                "severity": "opportunity",
                "category": "execution-receipts",
                "ruleId": "launchdeck-execution-receipts-not-provided",
                "evidence": "No --receipt input was supplied, so this report is a route plan rather than execution proof.",
                "recommendation": "After Codex executes the selected LaunchDeck route or XcodeBuildMCP tools, rerun this command with --receipt <file-or-dir> to grade proof completeness.",
                "proofGuidance": "Attach build logs, describe_ui or screenshot output, serve-sim/browser proof, preview hot-reload output, profiler traces, or device receipts depending on the selected lane.",
            }
        )
        return {
            "status": "not-assessed",
            "requiredForWorkflow": required,
            "present": [],
            "missing": [],
            "findings": findings,
            "summary": "No execution receipts were supplied; ShipGuard only selected the route.",
        }

    if receipt_status == "missing":
        findings.append(
            {
                "severity": "review",
                "category": "execution-receipts",
                "ruleId": "launchdeck-execution-receipts-empty",
                "evidence": "Receipt inputs were supplied, but none resolved to readable receipt files.",
                "recommendation": "Point --receipt at the directory or files that contain the LaunchDeck/XcodeBuildMCP output.",
                "proofGuidance": "Use a small explicit receipt folder containing build logs, UI snapshots, screenshots, preview logs, trace summaries, and device notes.",
            }
        )
    for signal in missing:
        title = receipt_signal_title(signal)
        findings.append(
            {
                "severity": "review",
                "category": "execution-receipts",
                "ruleId": RECEIPT_MISSING_RULES.get(signal, "launchdeck-receipt-missing"),
                "evidence": f"The selected `{workflow}` lane requires {title}, but supplied receipts did not contain that signal.",
                "recommendation": f"Add {title} before claiming the selected LaunchDeck workflow has been executed and proven.",
                "proofGuidance": "Re-run the relevant Codex/XcodeBuildMCP step, preserve the log/screenshot/trace output, then rerun `shipguard ios launchdeck --receipt <dir>`.",
            }
        )

    status = "pass" if receipt_status == "provided" and not missing else "review"
    return {
        "status": status,
        "requiredForWorkflow": required,
        "present": present,
        "missing": missing,
        "findings": findings,
        "summary": "Execution receipts cover the selected workflow." if status == "pass" else "Execution receipts are incomplete for the selected workflow.",
    }


def next_actions(target: dict[str, Any], workflow: str, receipt_quality: dict[str, Any]) -> list[str]:
    actions = [
        "Run `shipguard ios doctor --path <repo> --out <dir>` when topology assumptions need a separate receipt.",
        "Run `shipguard ios inventory --path <repo> --out <dir>` before permission, entitlement, StoreKit, widget, App Intent, or release-sensitive work.",
    ]
    if target.get("status") == "ready" and target.get("scheme"):
        actions.append(
            "In Codex, call XcodeBuildMCP session_show_defaults, then set the discovered project/workspace, scheme, and simulator before build_run_sim."
        )
    else:
        actions.append("Choose a project/workspace and scheme before attempting simulator proof.")
    if workflow in {"simulator-browser-preview", "swiftui-preview-hot-reload"}:
        actions.append("Use `shipguard ios preview` or Glass Deck serve-sim proof for visual inspection before design claims.")
    if workflow == "ios-profiler-performance":
        actions.append("Pair `shipguard ios performance` with an Instruments or sample-based route proof before changing performance-sensitive code.")
    receipt_status = str(receipt_quality.get("status") or "")
    if receipt_status == "not-assessed":
        actions.append(
            "After Codex executes the selected LaunchDeck route or XcodeBuildMCP tools, rerun this command with `--receipt <proof-dir>` to grade build/run, UI, preview, log, or profiler receipt completeness."
        )
    elif receipt_status == "review":
        missing = ", ".join(receipt_signal_title(item) for item in receipt_quality.get("missing", [])) or "required receipt proof"
        actions.append(f"Collect the missing execution receipts before making proof claims: {missing}.")
    elif receipt_status == "pass":
        actions.append("Use the receipt-quality section as proof that the selected LaunchDeck lane has matching execution artifacts.")
    actions.append("Use `shipguard ios report-quality` on the generated report when this is ShipGuard product QA.")
    return actions


def status_for(target: dict[str, Any], receipt_quality: dict[str, Any]) -> str:
    if target.get("status") != "ready":
        return "review"
    if receipt_quality.get("status") == "review":
        return "review"
    return "pass"


def build_report(
    root: Path,
    *,
    workflow: str,
    receipts: list[str] | None = None,
    shipguard_eval: bool = False,
    shareable: bool = False,
) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")
    root = root.resolve()
    scan = ios_scan_scope.iter_files(root, SOURCE_SUFFIXES)
    doctor = ios_doctor.build_report(root)
    target = build_target(root, doctor, shareable=shareable)
    preview = collect_preview_metrics(root)
    selected_workflow = workflow_id(workflow, target, preview)
    execution_receipts = collect_execution_receipts(receipts or [], shareable=shareable)
    receipt_quality = grade_receipt_quality(selected_workflow, execution_receipts)
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios launchdeck",
        "generatedAt": utc_now(),
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "status": status_for(target, receipt_quality),
        "root": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
        "shareability": {
            "mode": "shareable" if shareable else "local",
            "localAbsolutePathsIncluded": not shareable,
            "note": "Use --shareable before moving this LaunchDeck report into ChatGPT, GitHub, docs, benchmark fixtures, or report-quality scoring."
            if not shareable
            else "Local absolute paths are omitted from report fields; still run report-quality before public sharing.",
        },
        "requestedWorkflow": workflow,
        "recommendedWorkflow": selected_workflow,
        "buildTarget": target,
        "sourceSummary": {
            "filesScanned": len(scan.files),
            "swiftFiles": doctor.get("counts", {}).get("swift_files", 0),
            "xcodeProjects": doctor.get("counts", {}).get("xcode_projects", 0),
            "xcodeWorkspaces": doctor.get("counts", {}).get("xcode_workspaces", 0),
            "swiftPackages": doctor.get("counts", {}).get("swift_packages", 0),
            "testPlans": doctor.get("test_plans", []),
            "storeKitConfigs": doctor.get("storekit_configs", []),
            "privacyManifests": [item.get("path") for item in doctor.get("privacy_manifests", []) if isinstance(item, dict)],
            "scanScope": ios_scan_scope.summary(scan),
        },
        "previewSignals": preview,
        "launchdeckIntegration": integration_summary(),
        "workflows": build_workflows(target),
        "executionReceipts": execution_receipts,
        "receiptQuality": receipt_quality,
        "findings": receipt_quality["findings"],
        "proofBoundaries": [
            "Simulator proof is useful for build/run/debug and many UI checks, but physical-device proof is still required for haptics, ProMotion, touch latency, thermal behavior, background delivery, and display-specific claims.",
            "LaunchDeck can recommend XcodeBuildMCP and Codex iOS execution calls; a Codex thread must execute those calls.",
            "Do not claim an app is fixed from this LaunchDeck report alone. Use it to choose the proof route and then attach the actual build, preview, trace, log, or screenshot receipt.",
        ],
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "nextActions": next_actions(target, selected_workflow, receipt_quality),
    }
    if shipguard_eval and shareable:
        report = ios_shareable.redact_shipguard_eval_report(report)
    return report


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_markdown(report: dict[str, Any]) -> str:
    target = report["buildTarget"]
    integration = report["launchdeckIntegration"]
    source = report["sourceSummary"]
    preview = report["previewSignals"]
    lines = [
        "# ShipGuard LaunchDeck",
        "",
        SURFACE_TAGLINE,
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Requested workflow: `{report['requestedWorkflow']}`",
        f"- Recommended workflow: `{report['recommendedWorkflow']}`",
        f"- Xcode projects: {source['xcodeProjects']}",
        f"- Xcode workspaces: {source['xcodeWorkspaces']}",
        f"- Swift packages: {source['swiftPackages']}",
        f"- Preview text scan budget: {preview['scanScope']['largeTextReadMode']} at {preview['scanScope']['textBytesPerFileLimit']} bytes",
        f"- Preview Swift files sampled: {preview['truncatedSwiftFiles']}; large Swift files omitted: {preview['omittedLargeSwiftFiles']}; timed out: {preview['timedOutSwiftFiles']}",
        f"- Skipped generated/proof/cache directories: {source['scanScope']['skippedDirectoryCount']}",
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
                "- Use findings to improve ShipGuard build/run/debug/preview/performance routing, docs, reports, or fixtures.",
                "- Do not turn target-app build or profiler observations into remediation tasks without separate app-work authorization.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )

    lines.extend(
        [
            "## LaunchDeck Console",
            "",
            f"- Surface: `{integration['surface']}`",
            f"- Codename: `{integration['codename']}`",
            f"- Integration mode: `{integration['integration']}`",
            f"- XcodeBuildMCP: {integration['capabilities']['xcodeBuildMCP']}",
            f"- Simulator browser: {integration['capabilities']['simulatorBrowser']}",
            f"- SwiftUI preview hot reload: {integration['capabilities']['swiftUIPreviewHotReload']}",
            f"- Performance profiling: {integration['capabilities']['performanceProfiling']}",
            "",
            "Boundary:",
        ]
    )
    for item in integration["boundary"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Discovered Target",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Target status | `{target['status']}` |",
            f"| Preferred selector | `{target['preferredXcodeSelector']}` |",
            f"| Workspace | `{target.get('workspacePath') or '-'}` |",
            f"| Project | `{target.get('projectPath') or '-'}` |",
            f"| Package | `{target.get('packagePath') or '-'}` |",
            f"| Scheme | `{target.get('scheme') or '-'}` |",
            f"| App target | `{target.get('appTarget') or '-'}` |",
            f"| Package target | `{target.get('packageTarget') or '-'}` |",
            "",
        ]
    )

    scan_scope = source["scanScope"]
    if scan_scope["skippedDirectories"]:
        lines.extend(["## Scan Scope", ""])
        for directory in scan_scope["skippedDirectories"][:8]:
            lines.append(f"- Skipped `{directory}`")
        if scan_scope["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")
    preview_scan_scope = preview["scanScope"]
    if preview_scan_scope["truncatedTextFiles"]:
        if not scan_scope["skippedDirectories"]:
            lines.extend(["## Scan Scope", ""])
        for file in preview_scan_scope["truncatedTextFiles"][:8]:
            lines.append(f"- Sampled preview source `{file}` up to {preview_scan_scope['textBytesPerFileLimit']} bytes")
        if preview_scan_scope["truncatedTextFileListTruncated"]:
            lines.append("- Additional sampled preview files are listed in JSON.")
    if preview_scan_scope["omittedLargeTextFiles"]:
        if not scan_scope["skippedDirectories"] and not preview_scan_scope["truncatedTextFiles"]:
            lines.extend(["## Scan Scope", ""])
        for file in preview_scan_scope["omittedLargeTextFiles"][:8]:
            lines.append(f"- Omitted large preview source `{file}` above {preview_scan_scope['textBytesPerFileLimit']} bytes")
        if preview_scan_scope["omittedLargeTextFileListTruncated"]:
            lines.append("- Additional omitted preview files are listed in JSON.")
    if preview_scan_scope["timedOutTextFiles"]:
        if not scan_scope["skippedDirectories"] and not preview_scan_scope["truncatedTextFiles"] and not preview_scan_scope["omittedLargeTextFiles"]:
            lines.extend(["## Scan Scope", ""])
        for file in preview_scan_scope["timedOutTextFiles"][:8]:
            lines.append(f"- Timed out reading preview source `{file}` after {preview_scan_scope['textReadTimeoutSeconds']} seconds")
        if preview_scan_scope["timedOutTextFileListTruncated"]:
            lines.append("- Additional timed-out preview files are listed in JSON.")
    if (
        scan_scope["skippedDirectories"]
        or preview_scan_scope["truncatedTextFiles"]
        or preview_scan_scope["omittedLargeTextFiles"]
        or preview_scan_scope["timedOutTextFiles"]
    ):
        lines.append("")

    lines.extend(
        [
            "## Preview Signals",
            "",
            f"- Swift files scanned for previews: {preview['swiftFilesScanned']}",
            f"- SwiftUI preview declarations: {preview['previewDeclarationCount']}",
        ]
    )
    if preview["previewFiles"]:
        lines.append("- Preview files: " + ", ".join(f"`{item}`" for item in preview["previewFiles"][:5]))
    lines.append("")

    section_titles = {
        "xcodebuildmcp-build-run": LANE_NAMES["xcodebuildmcp-build-run"],
        "xcodebuildmcp-debug": LANE_NAMES["xcodebuildmcp-debug"],
        "simulator-browser-preview": LANE_NAMES["simulator-browser-preview"],
        "swiftui-preview-hot-reload": LANE_NAMES["swiftui-preview-hot-reload"],
        "ios-profiler-performance": LANE_NAMES["ios-profiler-performance"],
    }
    for workflow in report["workflows"]:
        title = section_titles.get(workflow["id"], workflow["title"])
        lines.extend(["## " + title, ""])
        if workflow.get("plainTitle"):
            lines.append(f"- Route family: {workflow['plainTitle']}")
        lines.append(f"- Capability: `{workflow['capability']}`")
        lines.append(f"- ShipGuard role: {workflow['shipguardRole']}")
        lines.append(f"- Execution role: {workflow['executionRole']}")
        lines.append("")
        lines.append("Codex tools:")
        for tool in workflow["codexTools"]:
            lines.append(f"- {tool}")
        lines.append("")
        lines.append("Route:")
        for command in workflow["commands"]:
            lines.append(f"- {command}")
        lines.append("")
        lines.append("Proof artifacts:")
        for artifact in workflow["proofArtifacts"]:
            lines.append(f"- {artifact}")
        lines.append("")

    receipts = report["executionReceipts"]
    receipt_quality = report["receiptQuality"]
    lines.extend(["## Execution Receipts", ""])
    lines.append(f"- Receipt input status: `{receipts['status']}`")
    lines.append(f"- Receipt quality: `{receipt_quality['status']}`")
    lines.append(f"- Receipt summary: {receipt_quality['summary']}")
    required_titles = [receipt_signal_title(item) for item in receipt_quality.get("requiredForWorkflow", [])]
    lines.append("- Required for selected workflow: " + (", ".join(required_titles) if required_titles else "none"))
    if receipts["inputs"]:
        lines.append("")
        lines.append("| Input | Kind | Exists | Files |")
        lines.append("| --- | --- | --- | --- |")
        for item in receipts["inputs"]:
            lines.append(
                f"| `{table_cell(item['path'])}` | `{item['kind']}` | `{item['exists']}` | {item['fileCount']} |"
            )
    else:
        lines.append(
            "- No execution receipts were supplied. After Codex executes the LaunchDeck route or XcodeBuildMCP, rerun with `--receipt <proof-dir>`."
        )
    lines.append("")
    lines.append("| Signal | Present | Evidence |")
    lines.append("| --- | --- | --- |")
    for signal in receipts["signals"]:
        evidence = signal["evidence"]
        if evidence:
            evidence_text = "; ".join(f"{item['marker']} in `{item['path']}`" for item in evidence[:3])
        else:
            evidence_text = "-"
        lines.append(f"| {signal['title']} | `{signal['present']}` | {table_cell(evidence_text)} |")
    if receipt_quality["findings"]:
        lines.append("")
        lines.append("Receipt findings:")
        for finding in receipt_quality["findings"]:
            lines.append(
                f"- `{finding['ruleId']}` ({finding['severity']}): {finding['recommendation']} Proof: {finding['proofGuidance']}"
            )
    lines.append("")

    lines.extend(["## Proof Boundaries", ""])
    for boundary in report["proofBoundaries"]:
        lines.append(f"- {boundary}")

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ios-launchdeck.json"
    md_path = out_dir / "ios-launchdeck.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {md_path}")
    print(f"wrote: {json_path}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(
        root,
        workflow=args.workflow,
        receipts=args.receipt,
        shipguard_eval=args.shipguard_eval,
        shareable=args.shareable,
    )
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
