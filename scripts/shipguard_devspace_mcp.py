#!/usr/bin/env python3
"""Shipguard Devspace MCP/App bridge for the iOS preview loop."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hmac
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


MAX_MCP_BODY_BYTES = 128 * 1024
MAX_EVENT_BYTES = 16 * 1024
MAX_NOTE_CHARS = 1000
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
WIDGET_URI = "ui://widget/shipguard-preview-v1.html"
RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"
EVENT_TYPES = {"tap-request", "note", "navigate-request", "visual-bug", "copy-change"}
EVENT_SOURCES = {"widget-click", "widget-context-menu", "chatgpt", "manual"}
EVENT_ACTIONS = {"tap", "navigate", "change-copy", "fix-visual", "inspect", "accessibility"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"shipguard-devspace: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve a Shipguard MCP/App bridge for ChatGPT and Codex preview handoffs."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Loopback host to bind. Default: 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8787, help="HTTP port to bind, or 0 for an ephemeral port.")
    parser.add_argument("--stdio", action="store_true", help="Run as a stdio MCP server for Codex plugin integration.")
    parser.add_argument("--public-url", help="External HTTP origin used in widget metadata when running stdio mode.")
    parser.add_argument("--repo-root", default=".", help="Repository root that owns bin/codex-maintainer.")
    parser.add_argument("--preview-url", help="Existing ios preview URL to attach instead of starting one.")
    parser.add_argument("--preview-out", default="/tmp/ios-shipguard-preview", help="Default preview output directory.")
    parser.add_argument("--device", default="booted", help='Default simctl device UDID or "booted".')
    parser.add_argument("--fixture-image", help="Optional default fixture image for preview_start.")
    parser.add_argument("--ready-file", help="Optional file that receives the Devspace MCP URL after bind.")
    parser.add_argument("--event-limit", type=int, default=50, help="Number of recent preview events to return.")
    parser.add_argument("--bearer-token-env", help="Environment variable containing a bearer token required for HTTP requests.")
    parser.add_argument("--bearer-token-file", help="File containing a bearer token required for HTTP requests.")
    parser.add_argument(
        "--allow-codex-app-server",
        action="store_true",
        help="Advertise Codex app-server start instructions as enabled. This server still does not spawn Codex automatically.",
    )
    return parser.parse_args()


def bounded_int(value: Any, minimum: int, maximum: int) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < minimum or value > maximum:
        return None
    return value


def bounded_number(value: Any, minimum: float, maximum: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number < minimum or number > maximum:
        return None
    return number


def safe_text(value: Any, limit: int = MAX_NOTE_CHARS) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def load_bearer_token(args: argparse.Namespace) -> str | None:
    if args.bearer_token_env and args.bearer_token_file:
        fail("use either --bearer-token-env or --bearer-token-file, not both")
    token = None
    if args.bearer_token_env:
        name = safe_text(args.bearer_token_env, 120)
        if not name:
            fail("--bearer-token-env requires a variable name")
        token = os.environ.get(name, "")
        if not token.strip():
            fail(f"bearer token environment variable is empty: {name}")
    elif args.bearer_token_file:
        path = Path(args.bearer_token_file).expanduser().resolve()
        if not path.is_file():
            fail(f"bearer token file not found: {path}")
        token = path.read_text(encoding="utf-8")
    if token is None:
        return None
    token = token.strip()
    if not token:
        fail("bearer token must not be empty")
    if len(token) > 4096:
        fail("bearer token is too large")
    return token


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_json_url(url: str, timeout: int = 8) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return data


def post_json_url(url: str, payload: dict[str, Any], timeout: int = 8) -> dict[str, Any]:
    body = json_bytes(payload)
    if len(body) > MAX_EVENT_BYTES:
        raise RuntimeError("event body too large")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return data


def normalize_preview_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise RuntimeError("preview URL must be http or https")
    if not parsed.netloc:
        raise RuntimeError("preview URL is missing host")
    normalized = url.rstrip("/") + "/"
    return normalized


class PreviewClient:
    def __init__(self, preview_url: str) -> None:
        self.preview_url = normalize_preview_url(preview_url)

    def url(self, path: str) -> str:
        return self.preview_url.rstrip("/") + path

    def state(self) -> dict[str, Any]:
        return read_json_url(self.url("/api/state"))

    def handoff(self) -> dict[str, Any]:
        return read_json_url(self.url("/api/handoff"))

    def events(self) -> list[dict[str, Any]]:
        payload = read_json_url(self.url("/api/events"))
        events = payload.get("events", [])
        return events if isinstance(events, list) else []

    def record_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        return post_json_url(self.url("/api/events"), payload)

    def screenshot(self) -> tuple[bytes, str]:
        with urllib.request.urlopen(self.url("/screenshot.png"), timeout=20) as response:
            data = response.read()
            mode = response.headers.get("X-Shipguard-Capture-Mode", "unknown")
        return data, mode


class DevspaceState:
    def __init__(
        self,
        *,
        repo_root: Path,
        preview_url: str | None,
        preview_out: Path,
        default_device: str,
        default_fixture_image: Path | None,
        event_limit: int,
        allow_codex_app_server: bool,
        auth_enabled: bool,
    ) -> None:
        self.repo_root = repo_root
        self.preview_url = normalize_preview_url(preview_url) if preview_url else None
        self.preview_out = preview_out
        self.default_device = default_device
        self.default_fixture_image = default_fixture_image
        self.event_limit = event_limit
        self.allow_codex_app_server = allow_codex_app_server
        self.auth_enabled = auth_enabled
        self.screenshot_view_token = uuid.uuid4().hex if auth_enabled else None
        self.created_at = utc_now()
        self.session_id = f"shipguard-devspace-{uuid.uuid4().hex[:12]}"
        self.server_url = ""
        self.preview_process: subprocess.Popen[bytes] | None = None
        self.lock = threading.Lock()

    def preview_client(self) -> PreviewClient:
        if not self.preview_url:
            raise RuntimeError("no active preview; call preview_start first")
        return PreviewClient(self.preview_url)

    def write_ready_file(self, path: Path | None) -> None:
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.server_url.rstrip("/") + "/mcp\n", encoding="utf-8")

    def public_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {
            "sessionId": self.session_id,
            "createdAt": self.created_at,
            "updatedAt": utc_now(),
            "serverUrl": self.server_url,
            "mcpUrl": self.server_url.rstrip("/") + "/mcp",
            "widgetUri": WIDGET_URI,
            "previewUrl": self.preview_url,
            "previewOut": str(self.preview_out),
            "device": self.default_device,
            "eventLimit": self.event_limit,
            "codexAppServer": {
                "enabled": self.allow_codex_app_server,
                "note": "This bridge prepares Codex app-server handoffs but does not spawn Codex automatically.",
            },
            "auth": {
                "enabled": self.auth_enabled,
                "scheme": "Bearer" if self.auth_enabled else None,
                "screenshotProxy": "session-view-token" if self.auth_enabled else "none",
            },
        }
        if self.preview_process:
            state["previewPid"] = self.preview_process.pid
            state["previewRunning"] = self.preview_process.poll() is None
        else:
            state["previewPid"] = None
            state["previewRunning"] = False
        return state

    def screenshot_proxy_url(self) -> str:
        url = self.server_url.rstrip("/") + "/preview-screenshot.png"
        if self.screenshot_view_token:
            return f"{url}?view={self.screenshot_view_token}"
        return url

    def start_preview(self, params: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            existing = params.get("previewUrl")
            if isinstance(existing, str) and existing.strip():
                self.preview_url = normalize_preview_url(existing.strip())
                return {"attached": True, "previewUrl": self.preview_url, "state": self.public_state()}

            if self.preview_process and self.preview_process.poll() is None and self.preview_url:
                return {"attached": False, "previewUrl": self.preview_url, "state": self.public_state()}

            out_dir = Path(safe_text(params.get("outDir")) or str(self.preview_out)).expanduser().resolve()
            device = safe_text(params.get("device")) or self.default_device
            refresh_ms = bounded_int(params.get("refreshMs"), 250, 60000) or 1000
            port = bounded_int(params.get("port"), 0, 65535)
            preview_port = 0 if port is None else port
            fixture = safe_text(params.get("fixtureImage"))
            fixture_path = Path(fixture).expanduser().resolve() if fixture else self.default_fixture_image
            if fixture_path and not fixture_path.is_file():
                raise RuntimeError(f"fixture image not found: {fixture_path}")

            ready_dir = Path(tempfile.mkdtemp(prefix="shipguard-preview-ready-"))
            ready_file = ready_dir / "preview-url.txt"
            command = [
                str(self.repo_root / "bin" / "codex-maintainer"),
                "ios",
                "preview",
                "--out",
                str(out_dir),
                "--device",
                device,
                "--port",
                str(preview_port),
                "--ready-file",
                str(ready_file),
                "--refresh-ms",
                str(refresh_ms),
                "--event-limit",
                str(self.event_limit),
            ]
            if fixture_path:
                command.extend(["--fixture-image", str(fixture_path)])

            proc = subprocess.Popen(
                command,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                for _ in range(100):
                    if ready_file.exists() and ready_file.stat().st_size > 0:
                        break
                    if proc.poll() is not None:
                        stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", errors="replace")
                        raise RuntimeError(stderr.strip() or "preview process exited before writing ready file")
                    time.sleep(0.1)
                if not ready_file.exists() or ready_file.stat().st_size == 0:
                    proc.terminate()
                    raise RuntimeError("timed out waiting for preview URL")
                self.preview_url = normalize_preview_url(ready_file.read_text(encoding="utf-8").strip())
                self.preview_out = out_dir
                self.default_device = device
                self.preview_process = proc
                return {"attached": False, "previewUrl": self.preview_url, "state": self.public_state()}
            finally:
                shutil.rmtree(ready_dir, ignore_errors=True)

    def stop_preview(self) -> dict[str, Any]:
        with self.lock:
            stopped = False
            if self.preview_process and self.preview_process.poll() is None:
                self.preview_process.terminate()
                try:
                    self.preview_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.preview_process.kill()
                    self.preview_process.wait(timeout=5)
                stopped = True
            self.preview_process = None
            return {"stopped": stopped, "state": self.public_state()}

    def preview_state(self) -> dict[str, Any]:
        client = self.preview_client()
        preview = client.state()
        return {"devspace": self.public_state(), "preview": preview}

    def preview_handoff(self) -> dict[str, Any]:
        client = self.preview_client()
        handoff = client.handoff()
        return {"devspace": self.public_state(), "handoff": handoff}

    def preview_events(self) -> dict[str, Any]:
        client = self.preview_client()
        return {"events": client.events(), "devspace": self.public_state()}

    def record_event(self, params: dict[str, Any]) -> dict[str, Any]:
        event_type = safe_text(params.get("type"), 80) or "note"
        if event_type not in EVENT_TYPES:
            event_type = "note"
        note = safe_text(params.get("note"))
        payload: dict[str, Any] = {"type": event_type, "note": note}

        source = safe_text(params.get("source"), 40)
        action = safe_text(params.get("action"), 80)
        context_label = safe_text(params.get("contextLabel"), 160)
        if source in EVENT_SOURCES:
            payload["source"] = source
        if action in EVENT_ACTIONS:
            payload["action"] = action
        if context_label:
            payload["contextLabel"] = context_label

        normalized_x = bounded_number(params.get("normalizedX"), 0.0, 1.0)
        normalized_y = bounded_number(params.get("normalizedY"), 0.0, 1.0)
        pixel_x = bounded_int(params.get("pixelX"), 0, 100000)
        pixel_y = bounded_int(params.get("pixelY"), 0, 100000)
        if normalized_x is not None:
            payload["normalizedX"] = normalized_x
        if normalized_y is not None:
            payload["normalizedY"] = normalized_y
        if pixel_x is not None:
            payload["pixelX"] = pixel_x
        if pixel_y is not None:
            payload["pixelY"] = pixel_y

        viewport = params.get("viewport")
        if isinstance(viewport, dict):
            width = bounded_int(viewport.get("width"), 1, 100000)
            height = bounded_int(viewport.get("height"), 1, 100000)
            if width and height:
                payload["viewport"] = {"width": width, "height": height}

        client = self.preview_client()
        result = client.record_event(payload)
        return {"recorded": result, "handoff": client.handoff()}

    def screenshot_metadata(self) -> dict[str, Any]:
        data, mode = self.preview_client().screenshot()
        encoded = base64.b64encode(data[:192]).decode("ascii")
        return {
            "bytes": len(data),
            "captureMode": mode,
            "contentType": "image/png",
            "sampleBase64": encoded,
            "proxyUrl": self.screenshot_proxy_url(),
            "devspace": self.public_state(),
        }

    def render_widget_result(self) -> dict[str, Any]:
        preview: dict[str, Any] | None = None
        handoff: dict[str, Any] | None = None
        events: list[dict[str, Any]] = []
        screenshot_proxy_url = self.screenshot_proxy_url()
        if self.preview_url:
            client = self.preview_client()
            preview = client.state()
            handoff = client.handoff()
            events = client.events()

        return {
            "structuredContent": {
                "devspace": self.public_state(),
                "preview": preview,
                "handoff": handoff,
                "events": events[-self.event_limit :],
                "screenshotProxyUrl": screenshot_proxy_url,
            },
            "content": [
                {
                    "type": "text",
                    "text": "Shipguard Devspace preview widget is ready."
                    if self.preview_url
                    else "Shipguard Devspace is ready. Call preview_start to attach a simulator preview.",
                }
            ],
            "_meta": {
                "ui": {"resourceUri": WIDGET_URI},
                "openai/outputTemplate": WIDGET_URI,
                "openai/toolInvocation/invoked": "Preview ready",
            },
        }

    def simulator_list(self) -> dict[str, Any]:
        xcrun = shutil.which("xcrun")
        if not xcrun:
            return {"available": False, "error": "xcrun not found", "devices": []}
        proc = subprocess.run(
            [xcrun, "simctl", "list", "devices", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
        )
        if proc.returncode != 0:
            return {
                "available": False,
                "error": proc.stderr.decode("utf-8", errors="replace").strip(),
                "devices": [],
            }
        payload = json.loads(proc.stdout.decode("utf-8"))
        devices = []
        for runtime, runtime_devices in payload.get("devices", {}).items():
            if not isinstance(runtime_devices, list):
                continue
            for device in runtime_devices:
                if isinstance(device, dict):
                    devices.append(
                        {
                            "runtime": runtime,
                            "name": device.get("name"),
                            "udid": device.get("udid"),
                            "state": device.get("state"),
                            "isAvailable": device.get("isAvailable"),
                        }
                    )
        return {"available": True, "devices": devices}

    def codex_goal_emit(self, params: dict[str, Any]) -> dict[str, Any]:
        goal = safe_text(params.get("goal"), 120) or "shipguard-devspace-mcp"
        with tempfile.NamedTemporaryFile(prefix="shipguard-goal-", suffix=".md", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        try:
            command = [
                str(self.repo_root / "bin" / "codex-maintainer"),
                "ios",
                "goals",
                "emit",
                "--goal",
                goal,
                "--out",
                str(temp_path),
            ]
            proc = subprocess.run(
                command,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip() or "goal emit failed")
            return {"goal": goal, "slashGoal": temp_path.read_text(encoding="utf-8")}
        finally:
            temp_path.unlink(missing_ok=True)

    def codex_prepare_handoff(self, params: dict[str, Any]) -> dict[str, Any]:
        handoff = self.preview_handoff()["handoff"] if self.preview_url else {}
        prompt = safe_text(params.get("prompt"), 8000)
        if not prompt:
            prompt = safe_text(handoff.get("prompt"), 8000)
        if not prompt:
            prompt = (
                "Use $ios-shipguard preview-bridge mode. Start or attach the Shipguard preview, "
                "read /api/handoff, then make the smallest scoped code change and validate it."
            )

        app_server_command = "codex app-server"
        turn_command = {
            "transport": "stdio",
            "command": app_server_command,
            "note": "Start codex app-server yourself or through a trusted supervisor, then send turn/start with this prompt.",
        }
        out_file = safe_text(params.get("outFile"), 1000)
        written = None
        if out_file:
            path = Path(out_file).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(prompt + "\n", encoding="utf-8")
            written = str(path)

        supervisor_out = safe_text(params.get("supervisorOutDir"), 1000)
        supervisor: dict[str, Any] | None = None
        if supervisor_out:
            supervisor_dir = Path(supervisor_out).expanduser().resolve()
            supervisor_dir.mkdir(parents=True, exist_ok=True)
            prompt_source = Path(written) if written else supervisor_dir / "shipguard-source-prompt.md"
            if not written:
                prompt_source.write_text(prompt + "\n", encoding="utf-8")
            command = [
                str(self.repo_root / "bin" / "codex-maintainer"),
                "ios",
                "codex-handoff",
                "--prompt-file",
                str(prompt_source),
                "--out",
                str(supervisor_dir),
                "--cwd",
                str(self.repo_root),
            ]
            proc = subprocess.run(
                command,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode("utf-8", errors="replace").strip() or "codex handoff prepare failed")
            supervisor = {
                "prepared": True,
                "outDir": str(supervisor_dir),
                "promptFile": str(supervisor_dir / "codex-handoff-prompt.md"),
                "planFile": str(supervisor_dir / "codex-app-server-plan.json"),
                "messagesFile": str(supervisor_dir / "codex-app-server-messages.jsonl"),
                "executeCommand": [
                    str(self.repo_root / "bin" / "codex-maintainer"),
                    "ios",
                    "codex-handoff",
                    "--prompt-file",
                    str(supervisor_dir / "codex-handoff-prompt.md"),
                    "--out",
                    str(supervisor_dir),
                    "--cwd",
                    str(self.repo_root),
                    "--execute",
                ],
            }

        return {
            "prompt": prompt,
            "writtenPrompt": written,
            "codexAppServerEnabled": self.allow_codex_app_server,
            "codexAppServer": turn_command,
            "codexSupervisor": supervisor,
            "handoff": handoff,
        }


def tool_descriptor(name: str, title: str, description: str, input_schema: dict[str, Any], annotations: dict[str, Any], *, render: bool = False) -> dict[str, Any]:
    descriptor: dict[str, Any] = {
        "name": name,
        "title": title,
        "description": description,
        "inputSchema": input_schema,
        "annotations": annotations,
        "_meta": {
            "openai/toolInvocation/invoking": title[:64],
            "openai/toolInvocation/invoked": f"{title[:52]} ready",
        },
    }
    if render:
        descriptor["_meta"]["ui"] = {"resourceUri": WIDGET_URI}
        descriptor["_meta"]["openai/outputTemplate"] = WIDGET_URI
    return descriptor


def object_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


def tool_descriptors() -> list[dict[str, Any]]:
    read_only = {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True}
    local_write = {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False, "idempotentHint": False}
    return [
        tool_descriptor(
            "preview_start",
            "Start iOS preview",
            "Use this when ChatGPT should start or attach to the local iOS Shipguard preview loop.",
            object_schema(
                {
                    "previewUrl": {"type": "string", "description": "Existing preview URL to attach."},
                    "outDir": {"type": "string", "description": "Output directory for preview receipts."},
                    "device": {"type": "string", "description": "simctl device UDID or booted."},
                    "fixtureImage": {"type": "string", "description": "Fixture screenshot path for tests."},
                    "port": {"type": "integer", "minimum": 0, "maximum": 65535},
                    "refreshMs": {"type": "integer", "minimum": 250, "maximum": 60000},
                }
            ),
            local_write,
        ),
        tool_descriptor(
            "preview_stop",
            "Stop iOS preview",
            "Use this when ChatGPT should stop the preview process started by this Devspace bridge.",
            object_schema({}),
            local_write,
        ),
        tool_descriptor(
            "preview_state",
            "Read preview state",
            "Use this when ChatGPT needs current preview session metadata and recent events.",
            object_schema({}),
            read_only,
        ),
        tool_descriptor(
            "preview_screenshot",
            "Capture preview screenshot",
            "Use this when ChatGPT needs screenshot metadata and the widget image proxy URL.",
            object_schema({}),
            read_only,
        ),
        tool_descriptor(
            "preview_record_event",
            "Record preview event",
            "Use this when a widget click or note should be logged as local visual intent.",
            object_schema(
                {
                    "type": {"type": "string", "enum": ["tap-request", "note", "navigate-request", "visual-bug", "copy-change"]},
                    "note": {"type": "string", "maxLength": MAX_NOTE_CHARS},
                    "source": {"type": "string", "enum": ["widget-click", "widget-context-menu", "chatgpt", "manual"]},
                    "action": {"type": "string", "enum": ["tap", "navigate", "change-copy", "fix-visual", "inspect", "accessibility"]},
                    "contextLabel": {"type": "string", "maxLength": 160},
                    "normalizedX": {"type": "number", "minimum": 0, "maximum": 1},
                    "normalizedY": {"type": "number", "minimum": 0, "maximum": 1},
                    "pixelX": {"type": "integer", "minimum": 0, "maximum": 100000},
                    "pixelY": {"type": "integer", "minimum": 0, "maximum": 100000},
                    "viewport": {
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "minimum": 1, "maximum": 100000},
                            "height": {"type": "integer", "minimum": 1, "maximum": 100000},
                        },
                        "additionalProperties": False,
                    },
                },
                ["type"],
            ),
            local_write,
        ),
        tool_descriptor(
            "preview_handoff",
            "Read preview handoff",
            "Use this when ChatGPT should convert the latest visual event into a Codex/XcodeBuildMCP plan.",
            object_schema({}),
            read_only,
        ),
        tool_descriptor(
            "render_preview_widget",
            "Render preview widget",
            "Use this after preview_state or preview_start when ChatGPT should show the phone preview widget.",
            object_schema({}),
            read_only,
            render=True,
        ),
        tool_descriptor(
            "simulator_list",
            "List simulators",
            "Use this when ChatGPT needs local iOS Simulator names, states, and UDIDs before starting preview.",
            object_schema({}),
            read_only,
        ),
        tool_descriptor(
            "codex_goal_emit",
            "Emit Shipguard goal",
            "Use this when ChatGPT should produce a Shipguard slash-goal block for Codex.",
            object_schema({"goal": {"type": "string", "description": "Goal id from the iOS goal catalog."}}),
            read_only,
        ),
        tool_descriptor(
            "codex_prepare_handoff",
            "Prepare Codex handoff",
            "Use this when ChatGPT should prepare a Codex app-server turn prompt from the latest preview event.",
            object_schema(
                {
                    "prompt": {"type": "string", "description": "Optional explicit Codex prompt."},
                    "outFile": {"type": "string", "description": "Optional local file to write the prompt."},
                    "supervisorOutDir": {"type": "string", "description": "Optional local directory for prepared codex-handoff supervisor artifacts."},
                }
            ),
            local_write,
        ),
    ]


def widget_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shipguard Devspace</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #637083;
      --line: #d8dee8;
      --accent: #0f766e;
      --accent-strong: #0b5f59;
      --warning: #9a3412;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #11161c;
        --panel: #18202a;
        --text: #eef3f8;
        --muted: #aab6c5;
        --line: #2a3542;
        --accent: #2dd4bf;
        --accent-strong: #5eead4;
        --warning: #fdba74;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    main {
      display: grid;
      grid-template-columns: minmax(220px, 340px) minmax(240px, 1fr);
      gap: 14px;
      padding: 14px;
      min-height: 520px;
    }
    .phone {
      background: #05070a;
      border: 1px solid #262d36;
      border-radius: 30px;
      padding: 12px;
      align-self: start;
    }
    .screen {
      position: relative;
      border-radius: 22px;
      background: #000;
      overflow: hidden;
      aspect-ratio: 390 / 844;
      min-height: 460px;
    }
    .screen img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }
    .target {
      position: absolute;
      width: 18px;
      height: 18px;
      margin-left: -9px;
      margin-top: -9px;
      border: 2px solid var(--accent-strong);
      border-radius: 50%;
      display: none;
      pointer-events: none;
    }
    .context-menu {
      position: absolute;
      z-index: 4;
      display: none;
      min-width: 170px;
      max-width: 210px;
      padding: 6px;
      border: 1px solid #2f3a46;
      border-radius: 8px;
      background: #111820;
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
    }
    .context-menu button {
      width: 100%;
      display: block;
      margin: 0;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: #eef3f8;
      text-align: left;
      padding: 8px;
    }
    .context-menu button:hover,
    .context-menu button:focus {
      background: rgba(45, 212, 191, 0.16);
      outline: none;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 12px;
    }
    h1, h2 { margin: 0 0 8px; line-height: 1.2; }
    h1 { font-size: 18px; }
    h2 { font-size: 14px; }
    p { margin: 0; color: var(--muted); line-height: 1.4; }
    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      word-break: break-word;
    }
    textarea {
      width: 100%;
      min-height: 76px;
      margin: 8px 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: transparent;
      color: var(--text);
      padding: 8px;
      font: inherit;
      resize: vertical;
    }
    button {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      cursor: pointer;
      margin-right: 6px;
      margin-bottom: 6px;
    }
    button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }
    .events {
      display: grid;
      gap: 8px;
      max-height: 220px;
      overflow: auto;
    }
    .event {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
    }
    .warning { color: var(--warning); }
    @media (max-width: 720px) {
      main { grid-template-columns: 1fr; }
      .screen { min-height: 0; }
    }
  </style>
</head>
<body>
  <main>
    <section class="phone" aria-label="iOS simulator preview">
      <div class="screen" id="screen">
        <img id="screenshot" alt="Current iOS simulator screenshot">
        <div class="target" id="target"></div>
        <div class="context-menu" id="context-menu" role="menu" aria-label="Preview target actions">
          <button type="button" role="menuitem" data-type="tap-request" data-action="tap" data-label="Tap or navigate here">Tap or navigate here</button>
          <button type="button" role="menuitem" data-type="copy-change" data-action="change-copy" data-label="Change copy here">Change copy here</button>
          <button type="button" role="menuitem" data-type="visual-bug" data-action="fix-visual" data-label="Fix visual issue here">Fix visual issue here</button>
          <button type="button" role="menuitem" data-type="note" data-action="inspect" data-label="Inspect this area">Inspect this area</button>
        </div>
      </div>
    </section>
    <section>
      <div class="panel">
        <h1>Shipguard Devspace</h1>
        <p id="session">Waiting for preview data.</p>
      </div>
      <div class="panel">
        <h2>Visual Event</h2>
        <p id="selection">No target selected.</p>
        <textarea id="note" placeholder="Example: this Settings button should be easier to read."></textarea>
        <button class="primary" id="record">Record Event</button>
        <button id="refresh">Refresh</button>
        <button id="handoff">Ask ChatGPT to hand this to Codex</button>
        <p class="warning" id="status"></p>
      </div>
      <div class="panel">
        <h2>Agent Handoff</h2>
        <p><code id="prompt">No handoff yet.</code></p>
      </div>
      <div class="panel">
        <h2>Recent Events</h2>
        <div class="events" id="events"></div>
      </div>
    </section>
  </main>
  <script>
    const screenEl = document.getElementById("screen");
    const screenshotEl = document.getElementById("screenshot");
    const targetEl = document.getElementById("target");
    const contextMenuEl = document.getElementById("context-menu");
    const noteEl = document.getElementById("note");
    const statusEl = document.getElementById("status");
    const promptEl = document.getElementById("prompt");
    const sessionEl = document.getElementById("session");
    const selectionEl = document.getElementById("selection");
    const eventsEl = document.getElementById("events");
    let selected = null;
    let current = window.openai?.toolOutput || null;

    function escapeHtml(value) {
      return String(value || "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\\"": "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function render(data) {
      current = data || current || {};
      const preview = current.preview || {};
      const handoff = current.handoff || {};
      const devspace = current.devspace || {};
      const screenshotUrl = current.screenshotProxyUrl;
      if (screenshotUrl) {
        screenshotEl.src = screenshotUrl + "?ts=" + Date.now();
      }
      sessionEl.innerHTML = devspace.previewUrl
        ? `Preview <code>${escapeHtml(devspace.previewUrl)}</code>`
        : "No preview attached. Ask ChatGPT to call preview_start.";
      promptEl.textContent = handoff.prompt || handoff.handoff?.prompt || "No handoff yet.";
      const events = current.events || preview.events || [];
      eventsEl.innerHTML = "";
      for (const event of [...events].reverse()) {
        const item = document.createElement("div");
        item.className = "event";
        const coords = event.normalizedX !== undefined
          ? ` x=${Number(event.normalizedX).toFixed(3)} y=${Number(event.normalizedY).toFixed(3)}`
          : "";
        const action = event.action ? ` ${event.action}` : "";
        item.innerHTML = `<strong>${escapeHtml(event.type)}${escapeHtml(action)}${coords}</strong><br><code>${escapeHtml(event.timestamp)}</code><p>${escapeHtml(event.note || event.contextLabel || "")}</p>`;
        eventsEl.appendChild(item);
      }
    }

    async function callTool(name, args) {
      if (window.openai?.callTool) {
        return window.openai.callTool(name, args || {});
      }
      statusEl.textContent = "Tool calls are available only inside ChatGPT or another MCP Apps host.";
      return null;
    }

    function selectPoint(event, source) {
      const rect = screenEl.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      selected = {
        normalizedX: Math.max(0, Math.min(1, x / rect.width)),
        normalizedY: Math.max(0, Math.min(1, y / rect.height)),
        pixelX: Math.round(x),
        pixelY: Math.round(y),
        viewport: { width: Math.round(rect.width), height: Math.round(rect.height) },
        source
      };
      targetEl.style.left = `${x}px`;
      targetEl.style.top = `${y}px`;
      targetEl.style.display = "block";
      selectionEl.textContent = `Target x=${selected.normalizedX.toFixed(3)} y=${selected.normalizedY.toFixed(3)}`;
      return { x, y, rect };
    }

    function hideContextMenu() {
      contextMenuEl.style.display = "none";
    }

    function showContextMenu(x, y, rect) {
      const width = 210;
      const left = Math.max(6, Math.min(x, rect.width - width - 6));
      const top = Math.max(6, Math.min(y, rect.height - 190));
      contextMenuEl.style.left = `${left}px`;
      contextMenuEl.style.top = `${top}px`;
      contextMenuEl.style.display = "block";
    }

    screenEl.addEventListener("click", (event) => {
      if (contextMenuEl.contains(event.target)) return;
      selectPoint(event, "widget-click");
      hideContextMenu();
      noteEl.focus();
    });

    screenEl.addEventListener("contextmenu", (event) => {
      event.preventDefault();
      const point = selectPoint(event, "widget-context-menu");
      showContextMenu(point.x, point.y, point.rect);
    });

    contextMenuEl.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-type]");
      if (!button || !selected) return;
      selected.type = button.dataset.type;
      selected.action = button.dataset.action;
      selected.contextLabel = button.dataset.label;
      selectionEl.textContent = `${selected.contextLabel} at x=${selected.normalizedX.toFixed(3)} y=${selected.normalizedY.toFixed(3)}`;
      hideContextMenu();
      noteEl.focus();
    });

    document.addEventListener("click", (event) => {
      if (!contextMenuEl.contains(event.target) && event.target !== screenEl) {
        hideContextMenu();
      }
    });

    document.getElementById("record").addEventListener("click", async () => {
      const payload = Object.assign({
        type: selected?.type || (selected ? "tap-request" : "note"),
        note: noteEl.value
      }, selected || {});
      const result = await callTool("preview_record_event", payload);
      if (result?.structuredContent?.handoff) {
        promptEl.textContent = result.structuredContent.handoff.prompt || "Event recorded.";
      }
      noteEl.value = "";
      selected = null;
      selectionEl.textContent = "No target selected.";
      targetEl.style.display = "none";
      hideContextMenu();
      statusEl.textContent = "Event recorded.";
    });

    document.getElementById("refresh").addEventListener("click", async () => {
      const result = await callTool("render_preview_widget", {});
      if (result?.structuredContent) render(result.structuredContent);
    });

    document.getElementById("handoff").addEventListener("click", async () => {
      const prompt = promptEl.textContent || "Use Shipguard Devspace to hand the latest preview event to Codex.";
      if (window.openai?.sendFollowUpMessage) {
        await window.openai.sendFollowUpMessage({ prompt });
      } else {
        window.parent.postMessage({
          jsonrpc: "2.0",
          method: "ui/message",
          params: { role: "user", content: [{ type: "text", text: prompt }] }
        }, "*");
      }
    });

    window.addEventListener("message", (event) => {
      if (event.source !== window.parent) return;
      const message = event.data;
      if (!message || message.jsonrpc !== "2.0") return;
      if (message.method === "ui/notifications/tool-result") {
        render(message.params?.structuredContent);
      }
    }, { passive: true });

    window.addEventListener("openai:set_globals", (event) => {
      render(event.detail?.globals?.toolOutput || window.openai?.toolOutput);
    }, { passive: true });

    render(current);
  </script>
</body>
</html>
"""


class DevspaceHandler(BaseHTTPRequestHandler):
    server: "DevspaceHTTPServer"

    def log_message(self, format: str, *args: Any) -> None:
        message = format % args
        view_token = self.server.devspace.screenshot_view_token
        if view_token:
            message = message.replace(view_token, "<redacted>")
        print(f"shipguard-devspace: {self.address_string()} - {message}", file=sys.stderr)

    def send_bytes(self, status: HTTPStatus, content_type: str, body: bytes, extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def send_json(self, status: HTTPStatus, payload: Any) -> None:
        self.send_bytes(status, "application/json; charset=utf-8", json_bytes(payload))

    def send_error_json(self, status: HTTPStatus, message: str, request_id: Any = None) -> None:
        if request_id is not None:
            self.send_json(status, {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": message}})
        else:
            self.send_json(status, {"ok": False, "error": message})

    def has_screenshot_view_token(self) -> bool:
        view_token = self.server.devspace.screenshot_view_token
        if not view_token:
            return False
        parsed = urlparse(self.path)
        if parsed.path != "/preview-screenshot.png":
            return False
        values = parse_qs(parsed.query).get("view", [])
        return any(hmac.compare_digest(value, view_token) for value in values)

    def require_auth(self, *, allow_screenshot_view_token: bool = False) -> bool:
        token = self.server.bearer_token
        if token is None:
            return True
        if allow_screenshot_view_token and self.has_screenshot_view_token():
            return True
        header = self.headers.get("Authorization", "")
        prefix = "Bearer "
        if header.startswith(prefix) and hmac.compare_digest(header[len(prefix) :], token):
            return True
        self.send_response(HTTPStatus.UNAUTHORIZED.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("WWW-Authenticate", 'Bearer realm="shipguard-devspace"')
        body = json_bytes({"ok": False, "error": "missing or invalid bearer token"})
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return False

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if not self.require_auth(allow_screenshot_view_token=route == "/preview-screenshot.png"):
            return
        try:
            if route == "/healthz":
                self.send_json(HTTPStatus.OK, {"ok": True, "state": self.server.devspace.public_state()})
            elif route == "/widget/shipguard-preview-v1.html":
                self.send_bytes(HTTPStatus.OK, RESOURCE_MIME_TYPE, widget_html().encode("utf-8"))
            elif route == "/preview-screenshot.png":
                data, mode = self.server.devspace.preview_client().screenshot()
                self.send_bytes(HTTPStatus.OK, "image/png", data, {"X-Shipguard-Capture-Mode": mode})
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # noqa: BLE001 - HTTP boundary must convert failures.
            self.send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:
        if not self.require_auth():
            return
        route = urlparse(self.path).path
        if route != "/mcp":
            self.send_error_json(HTTPStatus.NOT_FOUND, "not found")
            return

        content_length = self.headers.get("Content-Length")
        try:
            length = int(content_length or "0")
        except ValueError:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "invalid content length")
            return
        if length <= 0:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "empty request body")
            return
        if length > MAX_MCP_BODY_BYTES:
            self.send_error_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "request body too large")
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json(HTTPStatus.BAD_REQUEST, "request body must be JSON")
            return

        if isinstance(payload, list):
            responses = [response for response in (self.handle_rpc(item) for item in payload) if response is not None]
            self.send_json(HTTPStatus.OK, responses)
            return
        response = self.handle_rpc(payload)
        if response is None:
            self.send_bytes(HTTPStatus.NO_CONTENT, "application/json; charset=utf-8", b"")
        else:
            self.send_json(HTTPStatus.OK, response)

    def handle_rpc(self, payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
        request_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        if not isinstance(method, str):
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32600, "message": "method is required"}}
        if request_id is None and method.startswith("notifications/"):
            return None
        try:
            result = self.server.devspace_rpc(method, params)
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as exc:  # noqa: BLE001 - JSON-RPC boundary must convert failures.
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}}


class DevspaceHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        devspace: DevspaceState,
        bearer_token: str | None,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.devspace = devspace
        self.bearer_token = bearer_token

    def devspace_rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        return dispatch_rpc(self.devspace, method, params)

    def call_tool(self, name: Any, params: dict[str, Any]) -> dict[str, Any]:
        if name == "preview_start":
            result = self.devspace.start_preview(params)
        elif name == "preview_stop":
            result = self.devspace.stop_preview()
        elif name == "preview_state":
            result = self.devspace.preview_state()
        elif name == "preview_screenshot":
            result = self.devspace.screenshot_metadata()
        elif name == "preview_record_event":
            result = self.devspace.record_event(params)
        elif name == "preview_handoff":
            result = self.devspace.preview_handoff()
        elif name == "render_preview_widget":
            return self.devspace.render_widget_result()
        elif name == "simulator_list":
            result = self.devspace.simulator_list()
        elif name == "codex_goal_emit":
            result = self.devspace.codex_goal_emit(params)
        elif name == "codex_prepare_handoff":
            result = self.devspace.codex_prepare_handoff(params)
        else:
            raise RuntimeError(f"unknown tool: {name}")

        return {
            "structuredContent": result,
            "content": [{"type": "text", "text": f"{name} completed."}],
        }


def dispatch_rpc(devspace: DevspaceState, method: str, params: dict[str, Any]) -> dict[str, Any]:
    if method == "initialize":
        requested_version = params.get("protocolVersion")
        return {
            "protocolVersion": requested_version if isinstance(requested_version, str) else "2024-11-05",
            "serverInfo": {"name": "shipguard-devspace", "version": "0.1.0"},
            "capabilities": {"tools": {}, "resources": {}},
            "instructions": (
                "Shipguard Devspace exposes a local iOS Simulator preview to ChatGPT. "
                "Start or attach preview first, render the widget for visual feedback, "
                "then use preview_handoff and codex_prepare_handoff before asking Codex to edit code."
            ),
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": tool_descriptors()}
    if method == "resources/list":
        return {
            "resources": [
                {
                    "uri": WIDGET_URI,
                    "name": "Shipguard iOS preview widget",
                    "title": "Shipguard Devspace",
                    "description": "Interactive phone preview for local iOS Shipguard events.",
                    "mimeType": RESOURCE_MIME_TYPE,
                }
            ]
        }
    if method == "resources/read":
        uri = params.get("uri")
        if uri != WIDGET_URI:
            raise RuntimeError(f"unknown resource: {uri}")
        origin = devspace.server_url.rstrip("/") or "http://127.0.0.1:8787"
        return {
            "contents": [
                {
                    "uri": WIDGET_URI,
                    "mimeType": RESOURCE_MIME_TYPE,
                    "text": widget_html(),
                    "_meta": {
                        "ui": {
                            "prefersBorder": True,
                            "csp": {
                                "connectDomains": [origin],
                                "resourceDomains": [origin],
                            },
                        },
                        "openai/widgetDescription": "Phone-shaped iOS Simulator preview for Shipguard visual feedback.",
                        "openai/widgetPrefersBorder": True,
                    },
                }
            ]
        }
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments")
        args = arguments if isinstance(arguments, dict) else {}
        if name == "preview_start":
            result = devspace.start_preview(args)
        elif name == "preview_stop":
            result = devspace.stop_preview()
        elif name == "preview_state":
            result = devspace.preview_state()
        elif name == "preview_screenshot":
            result = devspace.screenshot_metadata()
        elif name == "preview_record_event":
            result = devspace.record_event(args)
        elif name == "preview_handoff":
            result = devspace.preview_handoff()
        elif name == "render_preview_widget":
            return devspace.render_widget_result()
        elif name == "simulator_list":
            result = devspace.simulator_list()
        elif name == "codex_goal_emit":
            result = devspace.codex_goal_emit(args)
        elif name == "codex_prepare_handoff":
            result = devspace.codex_prepare_handoff(args)
        else:
            raise RuntimeError(f"unknown tool: {name}")
        return {
            "structuredContent": result,
            "content": [{"type": "text", "text": f"{name} completed."}],
        }
    raise RuntimeError(f"unknown method: {method}")


def rpc_response(devspace: DevspaceState, payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
    if not isinstance(method, str):
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32600, "message": "method is required"}}
    if request_id is None and method.startswith("notifications/"):
        return None
    try:
        return {"jsonrpc": "2.0", "id": request_id, "result": dispatch_rpc(devspace, method, params)}
    except Exception as exc:  # noqa: BLE001 - JSON-RPC boundary must convert failures.
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}}


def stdio_loop(devspace: DevspaceState) -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            if isinstance(payload, list):
                responses = [response for response in (rpc_response(devspace, item) for item in payload) if response is not None]
                if responses:
                    print(json.dumps(responses, sort_keys=True), flush=True)
            else:
                response = rpc_response(devspace, payload)
                if response is not None:
                    print(json.dumps(response, sort_keys=True), flush=True)
        except Exception as exc:  # noqa: BLE001 - stdio boundary must stay alive.
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(exc)}}, sort_keys=True), flush=True)
    devspace.stop_preview()
    return 0


def main() -> int:
    args = parse_args()
    if not args.stdio and args.host not in LOOPBACK_HOSTS:
        fail("--host must be a loopback host: 127.0.0.1, localhost, or ::1")
    if args.port < 0 or args.port > 65535:
        fail("--port must be between 0 and 65535")
    if args.event_limit < 1:
        fail("--event-limit must be at least 1")
    if args.stdio and (args.bearer_token_env or args.bearer_token_file):
        fail("bearer-token options apply only to HTTP mode")
    bearer_token = load_bearer_token(args) if not args.stdio else None

    repo_root = Path(args.repo_root).expanduser().resolve()
    if not (repo_root / "bin" / "codex-maintainer").is_file():
        fail(f"repo root is missing bin/codex-maintainer: {repo_root}")
    preview_out = Path(args.preview_out).expanduser().resolve()
    fixture_image = Path(args.fixture_image).expanduser().resolve() if args.fixture_image else None
    if fixture_image and not fixture_image.is_file():
        fail(f"fixture image not found: {fixture_image}")

    state = DevspaceState(
        repo_root=repo_root,
        preview_url=args.preview_url,
        preview_out=preview_out,
        default_device=args.device,
        default_fixture_image=fixture_image,
        event_limit=args.event_limit,
        allow_codex_app_server=args.allow_codex_app_server,
        auth_enabled=bearer_token is not None,
    )
    if args.stdio:
        state.server_url = (args.public_url or "").rstrip("/")
        try:
            return stdio_loop(state)
        finally:
            state.stop_preview()

    server = DevspaceHTTPServer((args.host, args.port), DevspaceHandler, state, bearer_token)
    bound_host, bound_port = server.server_address[:2]
    url_host = "127.0.0.1" if bound_host in {"0.0.0.0", ""} else bound_host
    state.server_url = f"http://{url_host}:{bound_port}"
    ready_file = Path(args.ready_file).expanduser().resolve() if args.ready_file else None
    state.write_ready_file(ready_file)

    print(f"shipguard devspace mcp: {state.server_url}/mcp")
    print(f"health: {state.server_url}/healthz")
    if bearer_token:
        print("auth: bearer token required")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    finally:
        state.stop_preview()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
