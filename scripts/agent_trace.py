#!/usr/bin/env python3
"""Agent-neutral task trace adapter with a Codex-native first route."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from shipguard_receipts import SCHEMA_VERSION as RECEIPT_SCHEMA_VERSION
from shipguard_receipts import evidence_entries as load_evidence_entries


SCHEMA_VERSION = 1
ADAPTERS = ("auto", "codex", "claude", "gemini", "cursor", "mcp", "generic")
UNIVERSAL_AGENT_ADAPTERS = ("claude", "gemini", "cursor", "mcp", "generic")
MAX_NORMAL_WORKERS = 5
RECOMMENDED_WORKERS = "2-3"
TRACE_FILENAMES = ("trace.json", "codex-trace.json", "agent-trace.json")
MAX_XCODE_EVIDENCE_FILES = 200
MAX_XCODE_EVIDENCE_BYTES = 256 * 1024
TEXT_EVIDENCE_SUFFIXES = {
    ".json",
    ".log",
    ".md",
    ".txt",
    ".stdout",
    ".stderr",
    ".trace",
    ".xml",
}
XCODEBUILD_MCP_SIGNALS = {
    "sessionDefaultsProof": {
        "title": "Session defaults proof",
        "tokens": ["session_show_defaults", "session_set_defaults", "project", "workspace", "scheme", "simulator"],
        "proofBoundary": "Shows XcodeBuildMCP was pointed at an explicit project/workspace, scheme, and simulator before execution.",
    },
    "buildRunProof": {
        "title": "Build/run proof",
        "tokens": ["build_run_sim", "build succeeded", "** build succeeded **", "launch_app_sim", "install_app_sim", "launching "],
        "proofBoundary": "Shows simulator build/run execution happened; it is not physical-device, TestFlight, or App Store proof.",
    },
    "uiSnapshotProof": {
        "title": "UI snapshot proof",
        "tokens": ["describe_ui", "snapshot_ui", "elementref", "\"elements\"", "ui snapshot", "accessibility"],
        "proofBoundary": "Shows structured simulator UI state; visual claims still need screenshot review when layout or polish matters.",
    },
    "screenshotProof": {
        "title": "Screenshot proof",
        "tokens": ["screenshot", "simctl io", "preview-screenshot"],
        "proofBoundary": "Shows a captured simulator frame; redact or keep local when screenshots contain private app content.",
    },
    "logProof": {
        "title": "Runtime log proof",
        "tokens": ["start_sim_log_cap", "stop_sim_log_cap", "runtime log", "os_log", "console output", "log stream"],
        "proofBoundary": "Shows focused runtime evidence; logs can include private data and should be redacted before sharing.",
    },
    "profilerProof": {
        "title": "Profiler proof",
        "tokens": ["animation hitches", "time profiler", "xctrace", "instruments", "ettrace", "sample ", "spindump", "flamegraph"],
        "proofBoundary": "Shows simulator or local profiler evidence; physical-device proof is still required for haptics, thermal, touch latency, and ProMotion claims.",
    },
    "deviceProof": {
        "title": "Physical-device proof",
        "tokens": ["physical device", "connected device", "device run", "thermal", "haptic", "promotion", "pro motion", "touch latency"],
        "proofBoundary": "Shows device-related evidence is present, but ShipGuard still treats device claims as manual unless the receipt names the device route.",
    },
}
EXPO_EAS_SIGNALS = {
    "expoMCPProof": {
        "title": "Expo MCP proof",
        "tokens": ["expo mcp", "mcp__expo", "codex-expo-run-actions", "expo run action", "expo plugin"],
        "proofBoundary": "Shows Expo-specific agent tooling or MCP routing was involved; it is not enough by itself to prove a native build or update.",
    },
    "expoProjectProof": {
        "title": "Expo project proof",
        "tokens": ["app.json", "app.config", "expo sdk", "\"expo\"", "expo doctor", "expo diagnostics", "package.json"],
        "proofBoundary": "Shows the target is an Expo project or has Expo metadata; it does not prove prebuild, EAS, or native runtime behavior.",
    },
    "prebuildProof": {
        "title": "Expo prebuild proof",
        "tokens": ["expo prebuild", "npx expo prebuild", "prebuild", "config plugin", "ios directory", "android directory"],
        "proofBoundary": "Shows native project generation or config-plugin routing; generated native output still needs validation before release claims.",
    },
    "easBuildProof": {
        "title": "EAS build proof",
        "tokens": ["eas build", "build id", "build url", "build profile", "eas.json", "artifact url", ".ipa", ".apk", ".aab"],
        "proofBoundary": "Shows an EAS build route or artifact; it is not App Store, Play Store, or device-install proof unless those receipts are attached too.",
    },
    "easUpdateProof": {
        "title": "EAS update proof",
        "tokens": ["eas update", "update group", "runtimeversion", "runtime version", "channel", "branch", "rollout"],
        "proofBoundary": "Shows an EAS Update route; runtime-version compatibility and native-code boundaries still need explicit proof.",
    },
    "nativeRuntimeProof": {
        "title": "Native runtime proof",
        "tokens": ["simulator", "device", "launch", "runtime log", "xcodebuild", "gradle", "install", "build_run_sim"],
        "proofBoundary": "Shows local runtime evidence; keep device, TestFlight, and store claims separate unless those artifacts are present.",
    },
    "artifactIntegrityProof": {
        "title": "Artifact integrity proof",
        "tokens": ["sha256", "checksum", "artifact", "download url", "build artifact", "fingerprint"],
        "proofBoundary": "Shows artifact identity or integrity metadata; never include signing secrets, Expo tokens, or credential payloads in public reports.",
    },
    "credentialBoundaryProof": {
        "title": "Credential boundary proof",
        "tokens": ["credential", "credentials", "provisioning profile", "distribution certificate", "asc api key", "secrets redacted"],
        "proofBoundary": "Shows credentials were part of the route; ShipGuard treats this as boundary evidence and does not expose secret values.",
    },
}
AGENT_PACKAGING_PROFILES = {
    "codex": {
        "title": "Codex native trace",
        "sourceSignals": ["codex", "functions.exec_command", "codex trace", "Codex task thread"],
        "handoffCommand": "shipguard codex trace --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Use the Codex trace alias when the thread already comes from Codex; it pins --adapter codex while preserving the shared Agent Adapter Kernel schema.",
    },
    "claude": {
        "title": "Claude trace package",
        "sourceSignals": ["claude", "claude-code", "claude desktop", "tool_use"],
        "handoffCommand": "shipguard agent trace --adapter claude --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Export Claude prompts, tool_use/tool_result blocks, validation receipts, verdicts, and next actions as JSON or JSONL events; keep credentials and private files out of shared traces.",
    },
    "gemini": {
        "title": "Gemini trace package",
        "sourceSignals": ["gemini", "gemini-cli", "google.generativeai", "function_call"],
        "handoffCommand": "shipguard agent trace --adapter gemini --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Export Gemini prompts, function calls, function responses, validation receipts, verdicts, and next actions into the same JSON/JSONL event shape used by ShipGuard TraceBridge.",
    },
    "cursor": {
        "title": "Cursor trace package",
        "sourceSignals": ["cursor", "composer", "cursor-agent", "apply_patch"],
        "handoffCommand": "shipguard agent trace --adapter cursor --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Export Cursor composer prompts, command/edit actions, receipts, verdicts, and next actions; use --shareable before taking reports outside the local machine.",
    },
    "mcp": {
        "title": "Generic MCP trace package",
        "sourceSignals": ["mcp", "modelcontextprotocol", "tools/call", "mcp__"],
        "handoffCommand": "shipguard agent trace --adapter mcp --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Export MCP prompts, tools/call requests, tool results, receipts, verdicts, and next actions without vendor-specific assumptions.",
    },
    "generic": {
        "title": "Generic agent trace package",
        "sourceSignals": ["generic", "jsonl", "tool_call", "command"],
        "handoffCommand": "shipguard agent trace --adapter generic --trace <trace.json> --out <shipguard-trace-dir> --shipguard-eval --shareable",
        "exportGuidance": "Use generic when the source agent is unknown; provide canonical prompt, tool_call, receipt, verdict, and next_action events so ShipGuard can still grade proof.",
    },
}
SHARED_AGENT_SCHEMA = {
    "taskContract": "Optional shipguard-task.json handoff from `shipguard prepare`.",
    "traceTimeline": "Canonical prompt, tool_call, receipt, verdict, next_action, and worker_spawn events.",
    "evidenceReceipts": "ShipGuard v2 evidence receipts supplied with --evidence.",
    "runtimeReceipt": "agent-trace-receipt.json emitted for every adapter run.",
    "verifyHandoff": "Optional `shipguard verify` execution or copy-ready verify command.",
    "redactionBoundary": "--shareable redacts local absolute paths from reports.",
    "nextGoalHandoff": "Slash plan/goal text remains in the shared report schema.",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"agent-trace: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json_object(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        fail(f"expected JSON object in {path}")
    return data


def resolve_file(path_value: str | None, filename: str) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_dir():
        path = path / filename
    return path


def resolve_trace(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_file():
        return path
    if path.is_dir():
        for name in TRACE_FILENAMES:
            candidate = path / name
            if candidate.is_file():
                return candidate
    fail(f"trace not found: {path}")


def load_trace(path: Path) -> tuple[Any, list[dict[str, Any]], str]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            events = parsed.get("events")
            if isinstance(events, list):
                return parsed, [event for event in events if isinstance(event, dict)], "json-object"
            return parsed, [parsed], "json-object"
        if isinstance(parsed, list):
            return parsed, [event for event in parsed if isinstance(event, dict)], "json-list"
        fail(f"trace JSON must be an object or array: {path}")
    events: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL in {path}:{line_no}: {exc}")
        if isinstance(event, dict):
            events.append(event)
    return {"events": events}, events, "jsonl"


def event_type(event: dict[str, Any]) -> str:
    value = event.get("type") or event.get("kind") or event.get("event") or ""
    return str(value).strip().lower().replace("-", "_")


def text_value(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def event_summary(event: dict[str, Any]) -> str:
    return text_value(
        event.get("summary"),
        event.get("text"),
        event.get("prompt"),
        event.get("command"),
        event.get("tool"),
        event.get("path"),
        event.get("status"),
    )


def classify_event(event: dict[str, Any]) -> str:
    kind = event_type(event)
    role = str(event.get("role") or "").lower()
    if kind in {"prompt", "user_prompt", "message", "user_message"} or role == "user":
        return "prompt"
    if kind in {"tool_call", "tool", "command", "exec", "shell_command"} or event.get("tool") or event.get("command"):
        return "tool_call"
    if kind in {"receipt", "evidence_receipt", "validation_receipt", "runtime_receipt"} or event.get("receiptId"):
        return "receipt"
    if kind in {"verdict", "verify", "verify_result"} or event.get("verdictStatus"):
        return "verdict"
    if kind in {"next_action", "nextaction", "handoff"} or event.get("nextAction"):
        return "next_action"
    if kind in {"worker_spawn", "subagent_spawn", "agent_spawn"}:
        return "worker_spawn"
    return "other"


def timeline_item(index: int, event: dict[str, Any]) -> dict[str, Any]:
    category = classify_event(event)
    return {
        "index": index,
        "category": category,
        "type": event_type(event) or category,
        "role": event.get("role"),
        "tool": event.get("tool") or event.get("name"),
        "command": event.get("command"),
        "path": event.get("path"),
        "status": event.get("status") or event.get("verdictStatus"),
        "receiptId": event.get("receiptId"),
        "summary": event_summary(event),
    }


def count_categories(timeline: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "promptCount": sum(1 for item in timeline if item["category"] == "prompt"),
        "toolCallCount": sum(1 for item in timeline if item["category"] == "tool_call"),
        "receiptCount": sum(1 for item in timeline if item["category"] == "receipt"),
        "verdictCount": sum(1 for item in timeline if item["category"] == "verdict"),
        "nextActionCount": sum(1 for item in timeline if item["category"] == "next_action"),
        "workerSpawnCount": sum(1 for item in timeline if item["category"] == "worker_spawn"),
        "xcodeBuildMCPEvidenceCount": sum(1 for item in timeline if item["category"] == "xcodebuildmcp_evidence"),
        "expoEASAssuranceEvidenceCount": sum(1 for item in timeline if item["category"] == "expo_eas_evidence"),
    }


def normalize_adapter(value: object) -> str:
    text = str(value or "").strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "claude-code": "claude",
        "claude-desktop": "claude",
        "gemini-cli": "gemini",
        "google-gemini": "gemini",
        "cursor-agent": "cursor",
        "generic-mcp": "mcp",
        "model-context-protocol": "mcp",
        "modelcontextprotocol": "mcp",
    }
    return aliases.get(text, text)


def adapter_signal_scores(source: str) -> dict[str, list[str]]:
    scores: dict[str, list[str]] = {adapter: [] for adapter in AGENT_PACKAGING_PROFILES}
    for adapter, profile in AGENT_PACKAGING_PROFILES.items():
        for token in profile["sourceSignals"]:
            lowered = token.lower()
            if lowered in source and lowered not in scores[adapter]:
                scores[adapter].append(lowered)
    return scores


def infer_adapter(requested: str, trace_root: Any, timeline: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    if requested != "auto":
        return {"type": requested, "confidence": "override", "sourceSignals": [f"--adapter {requested}"]}
    source = json.dumps(trace_root, sort_keys=True).lower() if isinstance(trace_root, (dict, list)) else ""
    source += " " + trace_path.name.lower()
    source += " " + " ".join(str(item.get("tool") or "").lower() for item in timeline)
    source += " " + " ".join(str(item.get("command") or "").lower() for item in timeline)
    explicit = normalize_adapter(trace_root.get("adapter")) if isinstance(trace_root, dict) else ""
    if explicit in AGENT_PACKAGING_PROFILES:
        return {"type": explicit, "confidence": "metadata", "sourceSignals": [f"trace.adapter={explicit}"]}
    scores = adapter_signal_scores(source)
    ranked = sorted(scores.items(), key=lambda item: (len(item[1]), item[0] != "generic"), reverse=True)
    adapter, signals = ranked[0]
    if not signals:
        adapter = "generic"
        signals = ["no known adapter tokens found"]
    return {
        "type": adapter,
        "confidence": "high" if signals and not signals[0].startswith("no known") else "medium",
        "sourceSignals": signals,
    }


def adapter_packaging_report(adapter: dict[str, Any]) -> dict[str, Any]:
    adapter_type = str(adapter.get("type") or "generic")
    profile = AGENT_PACKAGING_PROFILES.get(adapter_type, AGENT_PACKAGING_PROFILES["generic"])
    profiles = []
    for key in ("codex", "claude", "gemini", "cursor", "mcp", "generic"):
        item = AGENT_PACKAGING_PROFILES[key]
        profiles.append(
            {
                "adapter": key,
                "title": item["title"],
                "handoffCommand": item["handoffCommand"],
                "exportGuidance": item["exportGuidance"],
                "native": key == "codex",
                "thinAdapter": key in UNIVERSAL_AGENT_ADAPTERS,
            }
        )
    return {
        "status": "pass",
        "currentAdapter": adapter_type,
        "currentProfile": {
            "title": profile["title"],
            "handoffCommand": profile["handoffCommand"],
            "exportGuidance": profile["exportGuidance"],
        },
        "supportedAdapters": [item["adapter"] for item in profiles],
        "profiles": profiles,
        "sharedSchema": SHARED_AGENT_SCHEMA,
        "proofBoundary": "Adapter packaging normalizes traces into one ShipGuard schema; it does not prove the source agent, target app, device, store, or deployment unless matching receipts are attached.",
        "nextActions": [
            f"Use `{profile['handoffCommand']}` for {profile['title']}.",
            "Attach v2 evidence receipts with --evidence and use --shareable before external review.",
            "Keep target app work read-only unless a separate task explicitly authorizes app edits.",
        ],
    }


def display_path(path: Path | None, *, shareable: bool, label: str) -> str | None:
    if path is None:
        return None
    if shareable and path.is_absolute():
        return f"<{label}>/{path.name}"
    return path.as_posix()


def redact_text(value: str, roots: list[Path]) -> str:
    text = value
    for root in roots:
        candidates = [str(root)]
        if not root.is_absolute():
            candidates.append(str(root.absolute()))
        try:
            candidates.append(str(root.resolve()))
        except FileNotFoundError:
            pass
        for candidate in dict.fromkeys(item for item in candidates if item):
            text = text.replace(candidate, "<local-path>")
    return text


def redact_paths(value: Any, roots: list[Path]) -> Any:
    if isinstance(value, dict):
        return {key: redact_paths(item, roots) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_paths(item, roots) for item in value]
    if isinstance(value, str):
        return redact_text(value, roots)
    return value


def normalized_receipts(paths: list[str], *, shareable: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries, summary = load_evidence_entries(paths)
    if shareable:
        for entry in entries:
            raw_path = Path(str(entry.get("path") or ""))
            entry["path"] = display_path(raw_path, shareable=True, label="evidence")
            artifact = entry.get("artifact")
            if isinstance(artifact, dict) and artifact.get("path"):
                artifact_path = Path(str(artifact["path"]))
                artifact["path"] = artifact_path.name
    return entries, summary


def iter_evidence_files(path: Path) -> tuple[list[Path], bool]:
    if path.is_file():
        return [path], False
    if not path.is_dir():
        return [], False
    files: list[Path] = []
    truncated = False
    for candidate in sorted(path.rglob("*")):
        if not candidate.is_file():
            continue
        files.append(candidate)
        if len(files) >= MAX_XCODE_EVIDENCE_FILES:
            truncated = True
            break
    return files, truncated


def evidence_path_label(path: Path, *, inputs: list[Path], shareable: bool) -> str:
    if not shareable:
        return path.as_posix()
    for index, input_path in enumerate(inputs, start=1):
        base = input_path if input_path.is_dir() else input_path.parent
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        suffix = relative.as_posix()
        return f"<xcodebuildmcp-evidence-{index}>" if not suffix or suffix == "." else f"<xcodebuildmcp-evidence-{index}>/{suffix}"
    return "<xcodebuildmcp-evidence>"


def typed_evidence_path_label(path: Path, *, inputs: list[Path], shareable: bool, label_prefix: str) -> str:
    if not shareable:
        return path.as_posix()
    for index, input_path in enumerate(inputs, start=1):
        base = input_path if input_path.is_dir() else input_path.parent
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        suffix = relative.as_posix()
        root_label = f"<{label_prefix}-{index}>"
        return root_label if not suffix or suffix == "." else f"{root_label}/{suffix}"
    return f"<{label_prefix}>"


def read_evidence_text(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return ""
    suffix = path.suffix.lower()
    if suffix not in TEXT_EVIDENCE_SUFFIXES and size > MAX_XCODE_EVIDENCE_BYTES:
        return ""
    try:
        data = path.read_bytes()[:MAX_XCODE_EVIDENCE_BYTES]
    except OSError:
        return ""
    if b"\x00" in data[:2048]:
        return ""
    return data.decode("utf-8", errors="ignore")


def xcode_signal_matches(path: Path, text: str) -> dict[str, list[str]]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    lowered = text.lower()
    matches: dict[str, list[str]] = {signal: [] for signal in XCODEBUILD_MCP_SIGNALS}

    def mark(signal: str, marker: str) -> None:
        if marker and marker not in matches[signal]:
            matches[signal].append(marker)

    if suffix in {".png", ".jpg", ".jpeg", ".heic"} or "screenshot" in name:
        mark("screenshotProof", "screenshot artifact")
    if suffix in {".trace", ".xcresult"} or name.endswith(".trace") or name.endswith(".xcresult"):
        mark("profilerProof", suffix or "trace artifact")
    if suffix == ".log" or "log" in name:
        mark("logProof", "log artifact")
    if suffix == ".json" and text.strip():
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        serialized = json.dumps(data, sort_keys=True).lower() if data is not None else lowered
        if "elementref" in serialized or '"elements"' in serialized or "snapshot_ui" in serialized or "describe_ui" in serialized:
            mark("uiSnapshotProof", "structured UI JSON")
        if "build_run_sim" in serialized or "session_show_defaults" in serialized:
            mark("buildRunProof", "XcodeBuildMCP JSON")
    for signal, config in XCODEBUILD_MCP_SIGNALS.items():
        for token in config["tokens"]:
            if token in lowered or token in name:
                mark(signal, token.strip())
    return matches


def expo_eas_signal_matches(path: Path, text: str) -> dict[str, list[str]]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    lowered = text.lower()
    matches: dict[str, list[str]] = {signal: [] for signal in EXPO_EAS_SIGNALS}

    def mark(signal: str, marker: str) -> None:
        if marker and marker not in matches[signal]:
            matches[signal].append(marker)

    if name in {"app.json", "app.config.js", "app.config.ts", "package.json"}:
        mark("expoProjectProof", name)
    if name == "eas.json":
        mark("easBuildProof", "eas.json")
    if suffix in {".ipa", ".apk", ".aab"}:
        mark("easBuildProof", suffix)
        mark("artifactIntegrityProof", "native artifact")
    if suffix in {".log", ".txt", ".md"} and ("eas" in name or "expo" in name):
        mark("expoProjectProof", name)
    if suffix == ".json" and text.strip():
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        serialized = json.dumps(data, sort_keys=True).lower() if data is not None else lowered
        if '"expo"' in serialized or "expo sdk" in serialized:
            mark("expoProjectProof", "Expo JSON metadata")
        if "eas build" in serialized or "build id" in serialized or "build url" in serialized:
            mark("easBuildProof", "EAS build JSON")
        if "eas update" in serialized or "update group" in serialized or "runtimeversion" in serialized:
            mark("easUpdateProof", "EAS update JSON")
        if "sha256" in serialized or "checksum" in serialized or "fingerprint" in serialized:
            mark("artifactIntegrityProof", "artifact integrity JSON")
    for signal, config in EXPO_EAS_SIGNALS.items():
        for token in config["tokens"]:
            if token in lowered or token in name:
                mark(signal, token.strip())
    return matches


def collect_xcodebuildmcp_evidence(raw_inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    if not raw_inputs:
        return {
            "status": "not-provided",
            "adapter": "xcodebuildmcp",
            "inputs": [],
            "summary": {
                "inputCount": 0,
                "existingInputCount": 0,
                "fileCount": 0,
                "filesScanned": 0,
                "truncated": False,
                **{signal: False for signal in XCODEBUILD_MCP_SIGNALS},
            },
            "signals": [
                {
                    "id": signal,
                    "title": config["title"],
                    "present": False,
                    "evidence": [],
                    "proofBoundary": config["proofBoundary"],
                }
                for signal, config in XCODEBUILD_MCP_SIGNALS.items()
            ],
            "nextActions": [
                "After Codex/XcodeBuildMCP executes build/run, UI, log, or profiler tools, rerun with --xcodebuildmcp-evidence <proof-dir> to attach typed proof to this timeline.",
            ],
        }

    resolved_inputs = [Path(item).expanduser().resolve() for item in raw_inputs]
    files: list[Path] = []
    inputs: list[dict[str, Any]] = []
    existing_count = 0
    any_truncated = False
    for index, path in enumerate(resolved_inputs, start=1):
        exists = path.exists()
        input_files: list[Path] = []
        truncated = False
        if exists:
            existing_count += 1
            input_files, truncated = iter_evidence_files(path)
            files.extend(input_files)
            any_truncated = any_truncated or truncated
        inputs.append(
            {
                "index": index,
                "path": f"<xcodebuildmcp-evidence-{index}>" if shareable else path.as_posix(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
                "exists": exists,
                "fileCount": len(input_files),
                "truncated": truncated,
            }
        )

    unique_files = sorted({path for path in files})
    signal_evidence: dict[str, list[dict[str, str]]] = {signal: [] for signal in XCODEBUILD_MCP_SIGNALS}
    for path in unique_files[:MAX_XCODE_EVIDENCE_FILES]:
        text = read_evidence_text(path)
        matches = xcode_signal_matches(path, text)
        label = evidence_path_label(path, inputs=resolved_inputs, shareable=shareable)
        for signal, markers in matches.items():
            for marker in markers:
                if len(signal_evidence[signal]) >= 8:
                    continue
                row = {"path": label, "marker": marker}
                if row not in signal_evidence[signal]:
                    signal_evidence[signal].append(row)

    summary = {
        "inputCount": len(raw_inputs),
        "existingInputCount": existing_count,
        "fileCount": len(unique_files),
        "filesScanned": min(len(unique_files), MAX_XCODE_EVIDENCE_FILES),
        "truncated": any_truncated or len(unique_files) > MAX_XCODE_EVIDENCE_FILES,
    }
    for signal in XCODEBUILD_MCP_SIGNALS:
        summary[signal] = bool(signal_evidence[signal])
    visual = bool(summary["uiSnapshotProof"] or summary["screenshotProof"])
    status = "missing" if not existing_count or not unique_files else "pass" if any(summary[signal] for signal in XCODEBUILD_MCP_SIGNALS) else "review"
    next_actions: list[str] = []
    if status == "missing":
        next_actions.append("Point --xcodebuildmcp-evidence at the proof directory or files produced by Codex/XcodeBuildMCP.")
    if not summary["buildRunProof"]:
        next_actions.append("Attach session_show_defaults/session_set_defaults plus build_run_sim output before claiming simulator build/run proof.")
    if not visual:
        next_actions.append("Attach describe_ui, snapshot_ui, or screenshot evidence before making UI-state or visual claims.")
    if not summary["profilerProof"]:
        next_actions.append("Attach xctrace, Instruments, sample, or ETTrace output before making performance-proof claims.")
    if summary["profilerProof"] and not summary["deviceProof"]:
        next_actions.append("Keep profiler claims scoped to simulator/local proof unless physical-device evidence is also attached.")
    return {
        "status": status,
        "adapter": "xcodebuildmcp",
        "inputs": inputs,
        "summary": summary,
        "signals": [
            {
                "id": signal,
                "title": config["title"],
                "present": bool(signal_evidence[signal]),
                "evidence": signal_evidence[signal],
                "proofBoundary": config["proofBoundary"],
            }
            for signal, config in XCODEBUILD_MCP_SIGNALS.items()
        ],
        "nextActions": next_actions,
    }


def collect_expo_eas_evidence(raw_inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    if not raw_inputs:
        return {
            "status": "not-provided",
            "adapter": "expo-eas",
            "inputs": [],
            "summary": {
                "inputCount": 0,
                "existingInputCount": 0,
                "fileCount": 0,
                "filesScanned": 0,
                "truncated": False,
                **{signal: False for signal in EXPO_EAS_SIGNALS},
            },
            "signals": [
                {
                    "id": signal,
                    "title": config["title"],
                    "present": False,
                    "evidence": [],
                    "proofBoundary": config["proofBoundary"],
                }
                for signal, config in EXPO_EAS_SIGNALS.items()
            ],
            "nextActions": [
                "After Codex/Expo/EAS tooling runs, rerun with --expo-eas-evidence <proof-dir> to attach Expo prebuild, EAS build/update, and runtime proof to this timeline.",
            ],
        }

    resolved_inputs = [Path(item).expanduser().resolve() for item in raw_inputs]
    files: list[Path] = []
    inputs: list[dict[str, Any]] = []
    existing_count = 0
    any_truncated = False
    for index, path in enumerate(resolved_inputs, start=1):
        exists = path.exists()
        input_files: list[Path] = []
        truncated = False
        if exists:
            existing_count += 1
            input_files, truncated = iter_evidence_files(path)
            files.extend(input_files)
            any_truncated = any_truncated or truncated
        inputs.append(
            {
                "index": index,
                "path": f"<expo-eas-evidence-{index}>" if shareable else path.as_posix(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
                "exists": exists,
                "fileCount": len(input_files),
                "truncated": truncated,
            }
        )

    unique_files = sorted({path for path in files})
    signal_evidence: dict[str, list[dict[str, str]]] = {signal: [] for signal in EXPO_EAS_SIGNALS}
    for path in unique_files[:MAX_XCODE_EVIDENCE_FILES]:
        text = read_evidence_text(path)
        matches = expo_eas_signal_matches(path, text)
        label = typed_evidence_path_label(path, inputs=resolved_inputs, shareable=shareable, label_prefix="expo-eas-evidence")
        for signal, markers in matches.items():
            for marker in markers:
                if len(signal_evidence[signal]) >= 8:
                    continue
                row = {"path": label, "marker": marker}
                if row not in signal_evidence[signal]:
                    signal_evidence[signal].append(row)

    summary = {
        "inputCount": len(raw_inputs),
        "existingInputCount": existing_count,
        "fileCount": len(unique_files),
        "filesScanned": min(len(unique_files), MAX_XCODE_EVIDENCE_FILES),
        "truncated": any_truncated or len(unique_files) > MAX_XCODE_EVIDENCE_FILES,
    }
    for signal in EXPO_EAS_SIGNALS:
        summary[signal] = bool(signal_evidence[signal])
    has_project_route = bool(summary["expoProjectProof"] or summary["expoMCPProof"])
    has_build_or_update = bool(summary["prebuildProof"] or summary["easBuildProof"] or summary["easUpdateProof"])
    has_assurance = bool(summary["nativeRuntimeProof"] or summary["artifactIntegrityProof"])
    if not existing_count or not unique_files:
        status = "missing"
    elif has_project_route and has_build_or_update and has_assurance:
        status = "pass"
    elif any(summary[signal] for signal in EXPO_EAS_SIGNALS):
        status = "review"
    else:
        status = "review"
    next_actions: list[str] = []
    if status == "missing":
        next_actions.append("Point --expo-eas-evidence at the proof directory or files produced by Expo MCP, Expo CLI, or EAS.")
    if not has_project_route:
        next_actions.append("Attach Expo project or Expo MCP metadata before claiming Expo-specific assurance.")
    if not has_build_or_update:
        next_actions.append("Attach Expo prebuild, EAS build, or EAS update output before claiming deployment-route proof.")
    if not summary["nativeRuntimeProof"]:
        next_actions.append("Attach simulator/device/runtime logs before claiming the built app actually launched.")
    if not summary["artifactIntegrityProof"]:
        next_actions.append("Attach artifact URL/checksum/fingerprint evidence before claiming a specific EAS artifact was preserved.")
    if summary["credentialBoundaryProof"]:
        next_actions.append("Keep Expo tokens, ASC keys, certificates, and provisioning details redacted; this report only records credential-boundary proof.")
    return {
        "status": status,
        "adapter": "expo-eas",
        "inputs": inputs,
        "summary": summary,
        "signals": [
            {
                "id": signal,
                "title": config["title"],
                "present": bool(signal_evidence[signal]),
                "evidence": signal_evidence[signal],
                "proofBoundary": config["proofBoundary"],
            }
            for signal, config in EXPO_EAS_SIGNALS.items()
        ],
        "nextActions": next_actions,
    }


def xcodebuildmcp_timeline(start_index: int, evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if evidence.get("status") == "not-provided":
        return []
    items: list[dict[str, Any]] = []
    index = start_index
    for signal in evidence.get("signals") or []:
        if not signal.get("present"):
            continue
        first = (signal.get("evidence") or [{}])[0]
        items.append(
            {
                "index": index,
                "category": "xcodebuildmcp_evidence",
                "type": signal["id"],
                "role": "runtime-proof",
                "tool": "XcodeBuildMCP",
                "command": signal["title"],
                "path": first.get("path"),
                "status": "pass",
                "receiptId": None,
                "summary": f"{signal['title']}: {first.get('marker') or 'typed proof present'}",
            }
        )
        index += 1
    return items


def expo_eas_timeline(start_index: int, evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if evidence.get("status") == "not-provided":
        return []
    items: list[dict[str, Any]] = []
    index = start_index
    for signal in evidence.get("signals") or []:
        if not signal.get("present"):
            continue
        first = (signal.get("evidence") or [{}])[0]
        items.append(
            {
                "index": index,
                "category": "expo_eas_evidence",
                "type": signal["id"],
                "role": "runtime-proof",
                "tool": "Expo/EAS",
                "command": signal["title"],
                "path": first.get("path"),
                "status": "pass",
                "receiptId": None,
                "summary": f"{signal['title']}: {first.get('marker') or 'typed proof present'}",
            }
        )
        index += 1
    return items


def xcodebuildmcp_findings(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if evidence.get("status") in {"not-provided", "pass"}:
        return []
    summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    findings: list[dict[str, Any]] = []
    if evidence.get("status") == "missing":
        findings.append(
            {
                "severity": "review",
                "category": "xcodebuildmcp-evidence",
                "ruleId": "xcodebuildmcp-evidence-input-missing",
                "evidence": "XcodeBuildMCP evidence inputs were supplied, but none resolved to readable files.",
                "recommendation": "Attach the proof directory produced by Codex/XcodeBuildMCP or remove the input until proof exists.",
                "proofGuidance": "Rerun with --xcodebuildmcp-evidence <dir> containing build logs, UI snapshots, screenshots, runtime logs, or profiler output.",
            }
        )
    if not any(bool(summary.get(signal)) for signal in XCODEBUILD_MCP_SIGNALS):
        findings.append(
            {
                "severity": "review",
                "category": "xcodebuildmcp-evidence",
                "ruleId": "xcodebuildmcp-evidence-untyped",
                "evidence": "Supplied evidence did not match build/run, UI, screenshot, log, profiler, or device signals.",
                "recommendation": "Keep XcodeBuildMCP proof explicit enough that ShipGuard can classify the receipt type.",
                "proofGuidance": "Attach session_show_defaults, build_run_sim, describe_ui/snapshot_ui, screenshots, log capture, or xctrace/sample outputs.",
            }
        )
    return findings


def expo_eas_findings(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if evidence.get("status") in {"not-provided", "pass"}:
        return []
    summary = evidence.get("summary") if isinstance(evidence.get("summary"), dict) else {}
    findings: list[dict[str, Any]] = []
    if evidence.get("status") == "missing":
        findings.append(
            {
                "severity": "review",
                "category": "expo-eas-evidence",
                "ruleId": "expo-eas-evidence-input-missing",
                "evidence": "Expo/EAS evidence inputs were supplied, but none resolved to readable files.",
                "recommendation": "Attach the proof directory produced by Expo MCP, Expo CLI, or EAS, or remove the input until proof exists.",
                "proofGuidance": "Rerun with --expo-eas-evidence <dir> containing Expo metadata, prebuild output, EAS build/update logs, runtime logs, or artifact checksums.",
            }
        )
        return findings
    if not summary.get("expoProjectProof") and not summary.get("expoMCPProof"):
        findings.append(
            {
                "severity": "review",
                "category": "expo-eas-evidence",
                "ruleId": "expo-eas-project-route-missing",
                "evidence": "Supplied evidence did not show Expo project metadata or Expo MCP routing.",
                "recommendation": "Attach app.json/app.config/package metadata, Expo doctor output, or Expo MCP trace evidence.",
                "proofGuidance": "Include Expo project metadata in the evidence directory before claiming Expo-specific assurance.",
            }
        )
    if not any(bool(summary.get(signal)) for signal in ("prebuildProof", "easBuildProof", "easUpdateProof")):
        findings.append(
            {
                "severity": "review",
                "category": "expo-eas-evidence",
                "ruleId": "expo-eas-build-update-route-missing",
                "evidence": "Supplied evidence did not show Expo prebuild, EAS build, or EAS update output.",
                "recommendation": "Attach the actual prebuild/build/update output instead of only project metadata.",
                "proofGuidance": "Include `expo prebuild`, `eas build`, or `eas update` receipts with build IDs, channels, branches, or runtime versions.",
            }
        )
    if not summary.get("nativeRuntimeProof"):
        findings.append(
            {
                "severity": "review",
                "category": "expo-eas-evidence",
                "ruleId": "expo-eas-native-runtime-proof-missing",
                "evidence": "Supplied evidence did not show native launch/runtime proof.",
                "recommendation": "Keep Expo/EAS proof scoped to build/update assurance until simulator or device runtime evidence is attached.",
                "proofGuidance": "Attach simulator/device launch logs, install proof, or runtime logs for the generated native app.",
            }
        )
    return findings


def load_task_summary(task_path: Path | None, *, shareable: bool) -> dict[str, Any]:
    if not task_path:
        return {"present": False}
    if not task_path.is_file():
        return {"present": False, "path": display_path(task_path, shareable=shareable, label="task")}
    task = read_json_object(task_path)
    return {
        "present": True,
        "path": display_path(task_path, shareable=shareable, label="task"),
        "taskId": task.get("taskId"),
        "goal": task.get("goal"),
        "profile": (task.get("projectSnapshot") or {}).get("profile"),
        "requiredValidationCount": len((task.get("validationContract") or {}).get("required") or []),
        "scopeBoundary": task.get("scopeBoundary") or {},
    }


def run_verify(args: argparse.Namespace, task_path: Path | None, evidence_paths: list[str], *, shareable: bool) -> dict[str, Any]:
    if not args.run_verify:
        return {
            "status": "not-run",
            "reason": "Use --run-verify with --task and --diff to attach a ShipGuard Task Verdict.",
            "copyReadyCommand": "shipguard verify --task <shipguard-task.json> --diff <patch.diff> --evidence <receipt.json> --out <dir>",
        }
    if not task_path or not task_path.is_file() or not args.diff:
        return {
            "status": "blocked",
            "reason": "--run-verify requires --task and --diff",
        }
    out_dir = Path(args.out) / "verify"
    command = [
        sys.executable,
        str(Path(__file__).parent / "task_contract.py"),
        "verify",
        "--task",
        str(task_path),
        "--diff",
        str(Path(args.diff)),
        "--out",
        str(out_dir),
        "--claim",
        "Agent trace connected prompts, tools, evidence receipts, verdicts, and next actions.",
    ]
    for evidence in evidence_paths:
        command.extend(["--evidence", evidence])
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    verdict_path = out_dir / "shipguard-verdict.json"
    verdict = read_json_object(verdict_path) if verdict_path.is_file() else {}
    status = str(verdict.get("status") or ("pass" if completed.returncode == 0 else "blocked"))
    return {
        "status": status,
        "exitCode": completed.returncode,
        "command": " ".join(command),
        "verdictPath": display_path(verdict_path, shareable=shareable, label="verify"),
        "verdictStatus": verdict.get("status"),
        "nextAction": verdict.get("nextAction"),
        "stdoutPreview": completed.stdout[-2000:],
        "stderrPreview": completed.stderr[-2000:],
    }


def budget_report(args: argparse.Namespace, trace_root: Any, timeline: list[dict[str, Any]]) -> dict[str, Any]:
    trace_budget = trace_root.get("agentBudget") if isinstance(trace_root, dict) and isinstance(trace_root.get("agentBudget"), dict) else {}
    workers_requested = args.budget_workers
    if workers_requested is None:
        raw = trace_budget.get("workersRequested", trace_budget.get("workerCount"))
        try:
            workers_requested = int(raw) if raw is not None else None
        except (TypeError, ValueError):
            workers_requested = None
    if workers_requested is None:
        workers_requested = max(1, sum(1 for item in timeline if item["category"] == "worker_spawn"))
    max_workers = min(int(args.max_workers), MAX_NORMAL_WORKERS)
    recursive = bool(trace_budget.get("recursiveSpawning") or trace_budget.get("recursiveSpawnDetected"))
    recursive = recursive or any(str(item.get("type") or "").lower() in {"recursive_spawn", "recursive"} for item in timeline)
    findings: list[dict[str, Any]] = []
    if int(args.max_workers) > MAX_NORMAL_WORKERS:
        findings.append(
            {
                "severity": "blocked",
                "ruleId": "agent-budget-max-cap",
                "evidence": f"--max-workers {args.max_workers} exceeds ShipGuard normal cap {MAX_NORMAL_WORKERS}",
                "recommendation": "Keep normal ShipGuard adapter runs capped at five workers.",
                "proofGuidance": "Rerun with --max-workers 5 or fewer.",
            }
        )
    if workers_requested > max_workers:
        findings.append(
            {
                "severity": "blocked",
                "ruleId": "agent-budget-worker-count",
                "evidence": f"{workers_requested} worker(s) requested; cap is {max_workers}",
                "recommendation": "Use 2-3 workers for normal ShipGuard work and never exceed five without a separate explicit strategy.",
                "proofGuidance": "Rerun the trace with --budget-workers <= 5 and no duplicate worker routes.",
            }
        )
    if recursive:
        findings.append(
            {
                "severity": "blocked",
                "ruleId": "agent-budget-recursive-spawn",
                "evidence": "Trace reports recursive worker spawning.",
                "recommendation": "Flatten the worker plan; ShipGuard should not recursively spawn agents.",
                "proofGuidance": "Attach a trace with one bounded worker layer.",
            }
        )
    return {
        "status": "blocked" if findings else "pass",
        "workerCount": workers_requested,
        "maxWorkers": max_workers,
        "recommendedWorkers": RECOMMENDED_WORKERS,
        "recursiveSpawnDetected": recursive,
        "findings": findings,
    }


def trace_findings(timeline: list[dict[str, Any]], verify_handoff: dict[str, Any]) -> list[dict[str, Any]]:
    counts = count_categories(timeline)
    findings: list[dict[str, Any]] = []
    required = [
        ("promptCount", "trace-missing-prompt", "prompt"),
        ("toolCallCount", "trace-missing-tool-call", "tool call"),
        ("receiptCount", "trace-missing-receipt", "evidence receipt"),
        ("verdictCount", "trace-missing-verdict", "verdict"),
        ("nextActionCount", "trace-missing-next-action", "next action"),
    ]
    for key, rule_id, label in required:
        if counts[key] == 0:
            findings.append(
                {
                    "severity": "review",
                    "category": "trace-completeness",
                    "ruleId": rule_id,
                    "evidence": f"Trace contains no {label} events.",
                    "recommendation": f"Export or synthesize the {label} into the adapter trace so the maintainer can review the whole task chain.",
                    "proofGuidance": "Rerun `shipguard agent trace` with a trace containing prompt, tool_call, receipt, verdict, and next_action events.",
                }
            )
    if verify_handoff.get("status") in {"blocked"}:
        findings.append(
            {
                "severity": "blocked",
                "category": "verify-handoff",
                "ruleId": "trace-verify-blocked",
                "evidence": str(verify_handoff.get("reason") or verify_handoff.get("verdictStatus") or "verify blocked"),
                "recommendation": "Fix the task contract, diff, or evidence receipt before treating the trace as complete.",
                "proofGuidance": "Attach the resulting shipguard-verdict.json or rerun with --run-verify after the blocker is repaired.",
            }
        )
    return findings


def status_from_findings(findings: list[dict[str, Any]], budget: dict[str, Any], verify_handoff: dict[str, Any]) -> str:
    if budget.get("status") == "blocked" or any(item.get("severity") == "blocked" for item in findings):
        return "blocked"
    if verify_handoff.get("status") == "review" or findings:
        return "review"
    return "pass"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_runtime_receipt(out_dir: Path, report_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    xcode_status = (report.get("xcodeBuildMCPEvidence") or {}).get("status")
    expo_status = (report.get("expoEASAssuranceEvidence") or {}).get("status")
    adapter_type = str((report.get("adapter") or {}).get("type") or "")
    scope = ["agent-trace", "task-contract", "receipts", "verdict-handoff", "agent-budget"]
    requirement_id = "codex-task-trace-adapter"
    if xcode_status != "not-provided":
        scope.append("xcodebuildmcp-evidence")
        requirement_id = "xcodebuildmcp-evidence-adapter"
    if expo_status != "not-provided":
        scope.append("expo-eas-evidence")
        requirement_id = "expo-eas-assurance-adapter"
    if adapter_type in UNIVERSAL_AGENT_ADAPTERS:
        scope.append("agent-neutral-packaging")
        if expo_status == "not-provided" and xcode_status == "not-provided":
            requirement_id = "universal-agent-packaging-adapter"
    receipt = {
        "schemaVersion": RECEIPT_SCHEMA_VERSION,
        "receiptId": "agent-trace-runtime",
        "receiptType": "runtime",
        "requirementId": requirement_id,
        "command": report.get("tool"),
        "exitCode": 0,
        "status": report.get("status"),
        "startedAt": report.get("generatedAt"),
        "completedAt": report.get("generatedAt"),
        "repositoryCommit": "local",
        "environment": "local-cli",
        "artifact": {
            "path": "agent-trace.json",
            "bytes": report_path.stat().st_size,
            "sha256": sha256_file(report_path),
        },
        "scope": scope,
    }
    receipt_path = out_dir / "agent-trace-receipt.json"
    write_json(receipt_path, receipt)
    return receipt


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_markdown(report: dict[str, Any]) -> str:
    adapter = report["adapter"]
    summary = report["traceSummary"]
    lines = [
        "# ShipGuard Agent Trace",
        "",
        f"- Status: {report['status']}",
        f"- Adapter: {adapter['type']} ({adapter['confidence']})",
        f"- Events: {summary['eventCount']}",
        f"- Prompts/tools/receipts/verdicts/next actions: {summary['promptCount']}/{summary['toolCallCount']}/{summary['receiptCount']}/{summary['verdictCount']}/{summary['nextActionCount']}",
        f"- Runtime receipt: {report['runtimeReceiptPath']}",
        "",
        "## Scope Boundary",
        "",
        "- ShipGuard-only product QA: true" if report["scopeBoundary"]["shipguardOnly"] else "- ShipGuard-only product QA: false",
        "- Target apps read-only: true" if report["scopeBoundary"]["targetAppsReadOnly"] else "- Target apps read-only: false",
        "",
        "## Agent Budget",
        "",
        f"- Status: {report['agentBudget']['status']}",
        f"- Workers: {report['agentBudget']['workerCount']} requested, cap {report['agentBudget']['maxWorkers']}, normal recommendation {report['agentBudget']['recommendedWorkers']}",
        f"- Recursive spawning: {str(report['agentBudget']['recursiveSpawnDetected']).lower()}",
        "",
        "## Timeline",
        "",
        "| # | Category | Tool/Command | Status | Summary |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for item in report["taskTrace"]["timeline"][:40]:
        command = item.get("command") or item.get("tool") or "-"
        summary = str(item.get("summary") or "-").replace("|", "\\|")
        if len(summary) > 140:
            summary = summary[:137].rstrip() + "..."
        lines.append(f"| {item['index']} | {item['category']} | `{command}` | {item.get('status') or '-'} | {summary} |")
    verify = report["verifyHandoff"]
    lines.extend(
        [
            "",
            "## Verify Handoff",
            "",
            f"- Status: {verify.get('status')}",
            f"- Verdict status: {verify.get('verdictStatus') or '-'}",
            f"- Verdict path: {verify.get('verdictPath') or '-'}",
            "",
            "## Agent Packaging",
            "",
            f"- Status: {report['adapterPackaging']['status']}",
            f"- Current adapter: {report['adapterPackaging']['currentAdapter']}",
            f"- Handoff command: `{report['adapterPackaging']['currentProfile']['handoffCommand']}`",
            f"- Proof boundary: {report['adapterPackaging']['proofBoundary']}",
            "",
            "| Adapter | Title | Thin Adapter |",
            "| --- | --- | --- |",
        ]
    )
    for profile in report["adapterPackaging"]["profiles"]:
        lines.append(f"| `{profile['adapter']}` | {profile['title']} | {str(profile['thinAdapter']).lower()} |")
    lines.extend(
        [
            "",
            "## XcodeBuildMCP Evidence",
            "",
            f"- Status: {report['xcodeBuildMCPEvidence']['status']}",
            f"- Files scanned: {report['xcodeBuildMCPEvidence']['summary']['filesScanned']}",
            "",
            "| Signal | Present | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for signal in report["xcodeBuildMCPEvidence"]["signals"]:
        evidence_rows = signal.get("evidence") or []
        evidence_text = ", ".join(f"{item.get('path')} ({item.get('marker')})" for item in evidence_rows[:3]) or "-"
        lines.append(f"| {signal['title']} | {str(signal['present']).lower()} | {table_cell(evidence_text, 160)} |")
    if report["xcodeBuildMCPEvidence"]["nextActions"]:
        lines.extend(["", "Next proof actions:"])
        for item in report["xcodeBuildMCPEvidence"]["nextActions"]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Expo/EAS Assurance Evidence",
            "",
            f"- Status: {report['expoEASAssuranceEvidence']['status']}",
            f"- Files scanned: {report['expoEASAssuranceEvidence']['summary']['filesScanned']}",
            "",
            "| Signal | Present | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for signal in report["expoEASAssuranceEvidence"]["signals"]:
        evidence_rows = signal.get("evidence") or []
        evidence_text = ", ".join(f"{item.get('path')} ({item.get('marker')})" for item in evidence_rows[:3]) or "-"
        lines.append(f"| {signal['title']} | {str(signal['present']).lower()} | {table_cell(evidence_text, 160)} |")
    if report["expoEASAssuranceEvidence"]["nextActions"]:
        lines.extend(["", "Next Expo/EAS proof actions:"])
        for item in report["expoEASAssuranceEvidence"]["nextActions"]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Receipt Handoff",
            "",
            f"- Schema: {report['receiptHandoff']['schema'].get('schemaVersion')}",
            f"- Receipts: {len(report['receiptHandoff']['receipts'])}",
            f"- Validation-usable: {report['receiptHandoff']['schema'].get('usableForValidationCount', 0)}",
            "",
            "## Findings",
            "",
        ]
    )
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] {finding['ruleId']}: {finding['recommendation']} Evidence: {finding['evidence']}")
    else:
        lines.append("- No adapter findings.")
    lines.extend(["", "## Slash Plan", "", "```text", report["slashPlan"], "```", "", "## Slash Goal", "", "```text", report["slashGoal"], "```", ""])
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    trace_path = resolve_trace(args.trace)
    trace_root, events, source_format = load_trace(trace_path)
    base_timeline = [timeline_item(index, event) for index, event in enumerate(events, start=1)]
    xcodebuildmcp_evidence = collect_xcodebuildmcp_evidence(args.xcodebuildmcp_evidence or [], shareable=args.shareable)
    xcode_timeline = xcodebuildmcp_timeline(len(base_timeline) + 1, xcodebuildmcp_evidence)
    expo_eas_evidence = collect_expo_eas_evidence(args.expo_eas_evidence or [], shareable=args.shareable)
    expo_timeline = expo_eas_timeline(len(base_timeline) + len(xcode_timeline) + 1, expo_eas_evidence)
    timeline = base_timeline + xcode_timeline + expo_timeline
    adapter = infer_adapter(args.adapter, trace_root, timeline, trace_path)
    adapter_packaging = adapter_packaging_report(adapter)
    task_path = resolve_file(args.task, "shipguard-task.json")
    verdict_path = resolve_file(args.verdict, "shipguard-verdict.json")
    evidence_paths = args.evidence or []
    receipts, receipt_schema = normalized_receipts(evidence_paths, shareable=args.shareable)
    verify_handoff = run_verify(args, task_path, evidence_paths, shareable=args.shareable)
    budget = budget_report(args, trace_root, timeline)
    findings = trace_findings(timeline, verify_handoff) + xcodebuildmcp_findings(xcodebuildmcp_evidence) + expo_eas_findings(expo_eas_evidence) + budget["findings"]
    status = status_from_findings(findings, budget, verify_handoff)
    counts = count_categories(timeline)
    task_id = text_value(
        trace_root.get("taskId") if isinstance(trace_root, dict) else None,
        load_task_summary(task_path, shareable=args.shareable).get("taskId"),
        "trace-task",
    )
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": args.surface_command,
        "surface": "ShipGuard Agent Adapter Kernel",
        "intent": "shipguard-product-qa" if args.shipguard_eval else "agent-trace-review",
        "status": status,
        "generatedAt": utc_now(),
        "adapter": {**adapter, "sourceFormat": source_format},
        "adapterPackaging": adapter_packaging,
        "scopeBoundary": {
            "shipguardOnly": bool(args.shipguard_eval),
            "targetAppsReadOnly": bool(args.shipguard_eval),
            "privateAppsUsed": False,
            "targetAppRemediationAuthorized": False,
            "policy": "Trace samples are product-QA inputs for ShipGuard. They do not authorize target app edits.",
        },
        "traceInput": {
            "path": display_path(trace_path, shareable=args.shareable, label="trace"),
            "shareable": bool(args.shareable),
        },
        "traceSummary": {"eventCount": len(timeline), **counts},
        "taskTrace": {
            "taskId": task_id,
            "timeline": timeline,
            "promptTimeline": [item for item in timeline if item["category"] == "prompt"],
            "toolTimeline": [item for item in timeline if item["category"] == "tool_call"],
            "receiptTimeline": [item for item in timeline if item["category"] == "receipt"],
            "verdictTimeline": [item for item in timeline if item["category"] == "verdict"],
            "xcodeBuildMCPEvidenceTimeline": [item for item in timeline if item["category"] == "xcodebuildmcp_evidence"],
            "expoEASAssuranceEvidenceTimeline": [item for item in timeline if item["category"] == "expo_eas_evidence"],
            "nextActions": [item for item in timeline if item["category"] == "next_action"],
        },
        "taskHandoff": load_task_summary(task_path, shareable=args.shareable),
        "verdictHandoff": {
            "present": bool(verdict_path and verdict_path.is_file()),
            "path": display_path(verdict_path, shareable=args.shareable, label="verdict"),
        },
        "receiptHandoff": {"schema": receipt_schema, "receipts": receipts},
        "xcodeBuildMCPEvidence": xcodebuildmcp_evidence,
        "expoEASAssuranceEvidence": expo_eas_evidence,
        "verifyHandoff": verify_handoff,
        "agentBudget": budget,
        "findings": findings,
        "reportQualityQuestions": [
            "Does this trace connect the user prompt, tools, evidence receipts, verdict, and next action without relying on pasted summaries?",
            "Can Claude, Gemini, Cursor, and generic MCP traces enter the same ShipGuard schema through thin adapters instead of forked workflows?",
            "Does XcodeBuildMCP build/run, UI snapshot, screenshot, log, or profiler proof attach to the same task trace timeline with local-path redaction?",
            "Does Expo prebuild, EAS build/update, native runtime, artifact integrity, and credential-boundary proof attach to the same timeline without leaking tokens?",
            "Does the next full-audit orchestrator reduce repeated manual validation work while preserving exact proof boundaries?",
        ],
        "slashPlan": "/plan v3.124.0 Efficient Unleash The Beast Full-Audit Orchestrator for jlekerli-source/ShipGuard: collapse repeated broad validation, value-gauntlet, report-quality, install, plugin, CI, and release-proof checks into one evidence-aware orchestrator with resumable receipts." if adapter.get("type") in UNIVERSAL_AGENT_ADAPTERS else "/plan v3.123.0 Claude, Gemini, Cursor, And Generic MCP Packaging for jlekerli-source/ShipGuard: add thin agent/package adapters after Expo/EAS proof can attach to TraceBridge.",
        "slashGoal": "/goal Implement v3.124.0 Efficient Unleash The Beast Full-Audit Orchestrator for jlekerli-source/ShipGuard: make the full audit fast, summarized, resumable, and proof-preserving without weakening package or release gates." if adapter.get("type") in UNIVERSAL_AGENT_ADAPTERS else "/goal Implement v3.123.0 Claude, Gemini, Cursor, And Generic MCP Packaging for jlekerli-source/ShipGuard: keep one core proof schema while packaging thin adapters for non-Codex agents.",
        "runtimeReceiptPath": "agent-trace-receipt.json",
    }
    if args.shareable:
        roots = [Path.cwd(), Path(args.out), trace_path.parent]
        if task_path:
            roots.append(task_path.parent)
        if args.diff:
            roots.append(Path(args.diff).parent)
        for evidence_path in args.evidence or []:
            roots.append(Path(evidence_path).parent)
        for evidence_path in args.xcodebuildmcp_evidence or []:
            roots.append(Path(evidence_path).expanduser())
        for evidence_path in args.expo_eas_evidence or []:
            roots.append(Path(evidence_path).expanduser())
        report = redact_paths(report, roots)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize agent task traces into ShipGuard receipts, verdict handoffs, and next actions.")
    parser.add_argument("--trace", required=True, help="Trace JSON, JSONL, or directory containing trace.json")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--adapter", choices=ADAPTERS, default="auto", help="Trace adapter type")
    parser.add_argument("--task", help="shipguard-task.json or directory containing it")
    parser.add_argument("--diff", help="Unified diff to pass into shipguard verify")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence receipt JSON to normalize and optionally pass to verify")
    parser.add_argument(
        "--xcodebuildmcp-evidence",
        action="append",
        default=[],
        help="File or directory containing XcodeBuildMCP build/run, UI snapshot, screenshot, log, or profiler proof to attach to the trace",
    )
    parser.add_argument(
        "--expo-eas-evidence",
        action="append",
        default=[],
        help="File or directory containing Expo MCP, Expo prebuild, EAS build/update, native runtime, or artifact-integrity proof to attach to the trace",
    )
    parser.add_argument("--verdict", help="shipguard-verdict.json or directory containing it")
    parser.add_argument("--run-verify", action="store_true", help="Run shipguard verify from --task, --diff, and --evidence")
    parser.add_argument("--budget-workers", type=int, help="Worker count to grade for this trace")
    parser.add_argument("--max-workers", type=int, default=MAX_NORMAL_WORKERS, help="Maximum allowed workers, capped at 5")
    parser.add_argument("--shipguard-eval", action="store_true", help="Mark output as ShipGuard-only product QA")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    parser.add_argument("--surface-command", default="shipguard agent trace", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    json_path = out_dir / "agent-trace.json"
    md_path = out_dir / "agent-trace.md"
    write_json(json_path, report)
    write_runtime_receipt(out_dir, json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(md_path.read_text(encoding="utf-8"))
    else:
        print(f"wrote: {json_path}")
        print(f"wrote: {md_path}")
        print(f"wrote: {out_dir / 'agent-trace-receipt.json'}")
        print(f"status: {report['status']}")


if __name__ == "__main__":
    main()
