#!/usr/bin/env python3
"""Local iOS Simulator preview bridge for Codex."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


MAX_EVENT_BYTES = 16 * 1024
MAX_NOTE_CHARS = 1000
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
EVENT_TYPES = {"tap-request", "note", "navigate-request", "visual-bug", "copy-change"}
EVENT_SOURCES = {"widget-click", "widget-context-menu", "chatgpt", "manual"}
EVENT_ACTIONS = {"tap", "navigate", "change-copy", "fix-visual", "inspect", "accessibility"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-preview: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve a local Codex browser preview of a booted iOS Simulator."
    )
    parser.add_argument("--out", required=True, help="Directory for session receipts and event logs.")
    parser.add_argument("--device", default="booted", help='simctl device UDID or "booted".')
    parser.add_argument("--host", default="127.0.0.1", help="Loopback host to bind. Default: 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind, or 0 for an ephemeral port.")
    parser.add_argument("--refresh-ms", type=int, default=1000, help="Browser screenshot refresh interval.")
    parser.add_argument("--fixture-image", help="Image file to serve instead of capturing a simulator screenshot.")
    parser.add_argument("--ready-file", help="Optional file that receives the preview URL after bind.")
    parser.add_argument("--event-limit", type=int, default=50, help="Number of recent events returned by APIs.")
    return parser.parse_args()


def bounded_number(value: Any, minimum: float, maximum: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number < minimum or number > maximum:
        return None
    return number


def bounded_int(value: Any, minimum: int, maximum: int) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < minimum or value > maximum:
        return None
    return value


def safe_text(value: Any, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


class PreviewSession:
    def __init__(
        self,
        *,
        out_dir: Path,
        device: str,
        refresh_ms: int,
        fixture_image: Path | None,
        event_limit: int,
    ) -> None:
        self.out_dir = out_dir
        self.device = device
        self.refresh_ms = refresh_ms
        self.fixture_image = fixture_image
        self.event_limit = event_limit
        self.created_at = utc_now()
        self.url = ""
        self.capture_mode = "fixture" if fixture_image else "simctl"
        self.session_path = out_dir / "session.json"
        self.ready_path = out_dir / "preview-url.txt"
        self.event_log = out_dir / "preview-events.jsonl"
        self.last_screenshot = out_dir / "last-screenshot.png"
        self.lock = threading.Lock()

    def initialize(self, url: str, ready_file: Path | None) -> None:
        self.url = url
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.event_log.touch(exist_ok=True)
        self.ready_path.write_text(url + "\n", encoding="utf-8")
        if ready_file:
            ready_file.parent.mkdir(parents=True, exist_ok=True)
            ready_file.write_text(url + "\n", encoding="utf-8")
        self.write_session()

    def session_receipt(self) -> dict[str, Any]:
        return {
            "tool": "codex-maintainer ios preview",
            "createdAt": self.created_at,
            "updatedAt": utc_now(),
            "url": self.url,
            "device": self.device,
            "refreshMs": self.refresh_ms,
            "captureMode": self.capture_mode,
            "outDir": str(self.out_dir),
            "sessionJson": str(self.session_path),
            "eventLog": str(self.event_log),
            "lastScreenshot": str(self.last_screenshot),
            "handoff": [
                "Open the preview URL in Codex's in-app browser or with @Browser.",
                "Use browser comments on the preview page for visual feedback.",
                "Read preview-events.jsonl for click and note receipts before editing SwiftUI code.",
                "Read /api/handoff for the latest Codex/XcodeBuildMCP action plan.",
                "Use XcodeBuildMCP semantic element refs or focused UI tests for simulator actions.",
            ],
        }

    def write_session(self) -> None:
        self.session_path.write_text(json.dumps(self.session_receipt(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def read_events(self) -> list[dict[str, Any]]:
        if not self.event_log.exists():
            return []
        rows = []
        for line in self.event_log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows[-self.event_limit :]

    def latest_event(self) -> dict[str, Any] | None:
        events = self.read_events()
        if not events:
            return None
        return events[-1]

    def agent_handoff(self) -> dict[str, Any]:
        latest_event = self.latest_event()
        prompt = (
            "Use $ios-shipguard preview-bridge mode. Read "
            f"{self.session_path} and {self.event_log}, inspect {self.last_screenshot}, "
            "then address the latest visual event with the smallest scoped code change."
        )
        suggested_actions = [
            "Open the preview URL in Codex's in-app browser if visual context is needed.",
            "Use XcodeBuildMCP screenshot or the preview last-screenshot.png for current visual state.",
            "Use XcodeBuildMCP snapshot_ui before performing any simulator interaction.",
        ]
        if latest_event:
            event_type = latest_event.get("type", "event")
            note = latest_event.get("note", "")
            source = latest_event.get("source", "")
            action = latest_event.get("action", "")
            context_label = latest_event.get("contextLabel", "")
            prompt = (
                f"{prompt} Latest event is {event_type!r}"
                f"{f' from {source}' if source else ''}"
                f"{f' with action {action!r}' if action else ''}"
                f"{f' for {context_label!r}' if context_label else ''}"
                f"{f' with note: {note}' if note else ''}."
            )
            if event_type in {"tap-request", "navigate-request"}:
                suggested_actions.extend(
                    [
                        "Match the event coordinates and note to a visible accessibility element from snapshot_ui.",
                        "Use XcodeBuildMCP touch on the matching elementRef only after the element is identified.",
                        "Refresh the preview screenshot and record proof after the navigation or UI change settles.",
                    ]
                )
            elif event_type == "copy-change":
                suggested_actions.extend(
                    [
                        "Locate the owning SwiftUI text, accessibility label, or localization key before editing copy.",
                        "Update the smallest copy surface that matches the selected coordinates and note.",
                        "Refresh the preview screenshot and check accessibility labels after the copy change.",
                    ]
                )
            elif event_type == "visual-bug":
                suggested_actions.extend(
                    [
                        "Inspect the selected region for layout, contrast, clipping, and Dynamic Type regressions.",
                        "Make the smallest visual fix and refresh the preview screenshot for proof.",
                    ]
                )
            else:
                suggested_actions.append("Treat the latest event as implementation feedback, not a simulator tap.")
        else:
            prompt = f"{prompt} No preview events have been recorded yet."
            suggested_actions.append("Wait for a browser comment or a preview event before editing UI code.")

        return {
            "ok": True,
            "tool": "codex-maintainer ios preview",
            "latestEvent": latest_event,
            "prompt": prompt,
            "suggestedActions": suggested_actions,
            "receipts": {
                "sessionJson": str(self.session_path),
                "eventLog": str(self.event_log),
                "lastScreenshot": str(self.last_screenshot),
                "previewUrl": self.url,
            },
        }

    def state(self) -> dict[str, Any]:
        receipt = self.session_receipt()
        receipt["events"] = self.read_events()
        receipt["eventCount"] = len(receipt["events"])
        receipt["agentHandoff"] = self.agent_handoff()
        return receipt

    def append_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event_type = payload.get("type")
        if not isinstance(event_type, str) or not event_type.strip():
            event_type = "note"
        event_type = event_type.strip()[:80]
        if event_type not in EVENT_TYPES:
            event_type = "note"

        note = payload.get("note", "")
        if not isinstance(note, str):
            note = ""
        note = note.strip()[:MAX_NOTE_CHARS]

        event: dict[str, Any] = {
            "timestamp": utc_now(),
            "type": event_type,
            "note": note,
        }

        source = safe_text(payload.get("source"), 40)
        action = safe_text(payload.get("action"), 80)
        context_label = safe_text(payload.get("contextLabel"), 160)
        if source in EVENT_SOURCES:
            event["source"] = source
        if action in EVENT_ACTIONS:
            event["action"] = action
        if context_label:
            event["contextLabel"] = context_label

        normalized_x = bounded_number(payload.get("normalizedX"), 0.0, 1.0)
        normalized_y = bounded_number(payload.get("normalizedY"), 0.0, 1.0)
        pixel_x = bounded_int(payload.get("pixelX"), 0, 100000)
        pixel_y = bounded_int(payload.get("pixelY"), 0, 100000)
        if normalized_x is not None:
            event["normalizedX"] = normalized_x
        if normalized_y is not None:
            event["normalizedY"] = normalized_y
        if pixel_x is not None:
            event["pixelX"] = pixel_x
        if pixel_y is not None:
            event["pixelY"] = pixel_y

        viewport = payload.get("viewport")
        if isinstance(viewport, dict):
            width = bounded_int(viewport.get("width"), 1, 100000)
            height = bounded_int(viewport.get("height"), 1, 100000)
            if width and height:
                event["viewport"] = {"width": width, "height": height}

        with self.lock:
            with self.event_log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
            self.write_session()
        return event

    def capture_screenshot(self) -> tuple[bytes, str]:
        with self.lock:
            if self.fixture_image:
                data = self.fixture_image.read_bytes()
                self.last_screenshot.write_bytes(data)
                return data, "fixture"

            xcrun = shutil.which("xcrun")
            if not xcrun:
                raise RuntimeError("xcrun not found; pass --fixture-image for non-macOS tests")

            with tempfile.NamedTemporaryFile(prefix="shipguard-screenshot-", suffix=".png", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            try:
                command = [
                    xcrun,
                    "simctl",
                    "io",
                    self.device,
                    "screenshot",
                    "--type=png",
                    str(temp_path),
                ]
                proc = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=15,
                )
                if proc.returncode == 0 and temp_path.exists() and temp_path.stat().st_size > 0:
                    data = temp_path.read_bytes()
                    self.last_screenshot.write_bytes(data)
                    return data, "simctl"
            finally:
                temp_path.unlink(missing_ok=True)
            if self.last_screenshot.exists():
                return self.last_screenshot.read_bytes(), "last-screenshot"
            stderr = proc.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(stderr or "simctl screenshot failed")


class PreviewHandler(BaseHTTPRequestHandler):
    server: "PreviewHTTPServer"

    def log_message(self, format: str, *args: Any) -> None:
        print(f"ios-preview: {self.address_string()} - {format % args}", file=sys.stderr)

    def send_bytes(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        self.send_bytes(status, "application/json; charset=utf-8", json.dumps(payload, sort_keys=True).encode("utf-8"))

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json(status, {"ok": False, "error": message})

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        try:
            if route == "/":
                body = render_html(self.server.preview_session).encode("utf-8")
                self.send_bytes(HTTPStatus.OK, "text/html; charset=utf-8", body)
            elif route == "/api/state":
                self.send_json(HTTPStatus.OK, self.server.preview_session.state())
            elif route == "/api/events":
                self.send_json(HTTPStatus.OK, {"events": self.server.preview_session.read_events()})
            elif route == "/api/handoff":
                self.send_json(HTTPStatus.OK, self.server.preview_session.agent_handoff())
            elif route == "/session.json":
                self.send_json(HTTPStatus.OK, self.server.preview_session.session_receipt())
            elif route == "/screenshot.png":
                data, mode = self.server.preview_session.capture_screenshot()
                self.send_response(HTTPStatus.OK.value)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Shipguard-Capture-Mode", mode)
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error_json(HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # noqa: BLE001 - HTTP boundary must convert failures to JSON.
            self.send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route != "/api/events":
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
        if length > MAX_EVENT_BYTES:
            self.send_error_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "event body too large")
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json(HTTPStatus.BAD_REQUEST, "request body must be JSON")
            return
        if not isinstance(payload, dict):
            self.send_error_json(HTTPStatus.BAD_REQUEST, "event payload must be an object")
            return

        event = self.server.preview_session.append_event(payload)
        self.send_json(HTTPStatus.OK, {"ok": True, "event": event})


class PreviewHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], preview_session: PreviewSession) -> None:
        super().__init__(server_address, handler_class)
        self.preview_session = preview_session


def render_html(session: PreviewSession) -> str:
    safe_device = html.escape(session.device)
    safe_event_log = html.escape(str(session.event_log))
    safe_session_json = html.escape(str(session.session_path))
    safe_url = html.escape(session.url)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>iOS Shipguard Preview</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f5f7fb;
      --text: #172033;
      --muted: #596579;
      --panel: #ffffff;
      --line: #d8dee9;
      --accent: #0f766e;
      --accent-strong: #0b5f59;
      --warning: #9a3412;
      --shadow: rgba(23, 32, 51, 0.16);
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #101418;
        --text: #f0f4f8;
        --muted: #a8b3c4;
        --panel: #171d24;
        --line: #2b3542;
        --accent: #2dd4bf;
        --accent-strong: #5eead4;
        --warning: #fdba74;
        --shadow: rgba(0, 0, 0, 0.42);
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(280px, 430px) minmax(300px, 1fr);
      gap: 24px;
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0;
      align-items: start;
    }}
    header {{
      grid-column: 1 / -1;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
    }}
    h1 {{
      font-size: 24px;
      line-height: 1.2;
      margin: 0 0 6px;
    }}
    h2 {{
      font-size: 15px;
      line-height: 1.3;
      margin: 0 0 10px;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }}
    button {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      cursor: pointer;
    }}
    button.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #ffffff;
    }}
    .phone {{
      background: #05070a;
      border-radius: 34px;
      padding: 14px;
      box-shadow: 0 20px 50px var(--shadow);
      border: 1px solid #252a32;
    }}
    .screen {{
      position: relative;
      overflow: hidden;
      border-radius: 24px;
      background: #000000;
      aspect-ratio: 390 / 844;
      min-height: 520px;
    }}
    .screen img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      background: #000000;
    }}
    .target {{
      position: absolute;
      width: 18px;
      height: 18px;
      margin-left: -9px;
      margin-top: -9px;
      border: 2px solid var(--accent-strong);
      border-radius: 50%;
      pointer-events: none;
      display: none;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .status-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 10px;
    }}
    .status-grid div {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      min-width: 0;
    }}
    .status-grid span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 3px;
    }}
    textarea {{
      width: 100%;
      min-height: 86px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: transparent;
      color: var(--text);
      padding: 10px;
      font: inherit;
      margin: 10px 0;
    }}
    .events {{
      display: grid;
      gap: 8px;
      max-height: 360px;
      overflow: auto;
    }}
    .event {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
    }}
    .event strong {{
      display: block;
      font-size: 13px;
      margin-bottom: 4px;
    }}
    .warning {{
      color: var(--warning);
    }}
    @media (max-width: 860px) {{
      main {{
        grid-template-columns: 1fr;
      }}
      header {{
        align-items: start;
        flex-direction: column;
      }}
      .screen {{
        min-height: 0;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>iOS Shipguard Preview</h1>
        <p>Live-ish simulator screenshot bridge for Codex browser comments and event receipts.</p>
      </div>
      <button id="refresh">Refresh</button>
    </header>

    <section class="phone" aria-label="iOS simulator preview">
      <div class="screen" id="screen">
        <img id="screenshot" src="/screenshot.png" alt="Current iOS simulator screenshot">
        <div class="target" id="target"></div>
      </div>
    </section>

    <section>
      <div class="panel">
        <h2>Session</h2>
        <p>Device <code>{safe_device}</code></p>
        <div class="status-grid">
          <div><span>Preview URL</span><code>{safe_url}</code></div>
          <div><span>Session JSON</span><code>{safe_session_json}</code></div>
          <div><span>Event Log</span><code>{safe_event_log}</code></div>
          <div><span>Last Refresh</span><code id="last-refresh">pending</code></div>
        </div>
      </div>

      <div class="panel">
        <h2>Click Intent</h2>
        <p>Click the phone image, describe what should change, then ask Codex to read the event log.</p>
        <textarea id="note" placeholder="Example: Rename this menu button to Settings and keep the icon."></textarea>
        <button class="primary" id="save-event">Record Event</button>
        <p class="warning" id="event-status"></p>
      </div>

      <div class="panel">
        <h2>Codex Handoff</h2>
        <p><code>Use $ios-shipguard preview-bridge mode. Read {safe_session_json} and {safe_event_log}, inspect the latest screenshot, then make the smallest SwiftUI change that addresses the latest browser comment or event receipt.</code></p>
      </div>

      <div class="panel">
        <h2>Agent Action</h2>
        <p><code id="agent-handoff">pending</code></p>
        <button id="copy-handoff">Copy</button>
        <p class="warning" id="copy-status"></p>
      </div>

      <div class="panel">
        <h2>Recent Events</h2>
        <div class="events" id="events"></div>
      </div>
    </section>
  </main>

  <script>
    const refreshMs = {int(session.refresh_ms)};
    const screenshot = document.getElementById("screenshot");
    const screen = document.getElementById("screen");
    const target = document.getElementById("target");
    const note = document.getElementById("note");
    const statusText = document.getElementById("event-status");
    const copyStatus = document.getElementById("copy-status");
    const agentHandoff = document.getElementById("agent-handoff");
    const events = document.getElementById("events");
    const lastRefresh = document.getElementById("last-refresh");
    let selected = null;

    function refreshImage() {{
      screenshot.src = "/screenshot.png?ts=" + Date.now();
      lastRefresh.textContent = new Date().toLocaleTimeString();
    }}

    async function refreshState() {{
      const response = await fetch("/api/state", {{ cache: "no-store" }});
      const state = await response.json();
      agentHandoff.textContent = state.agentHandoff.prompt;
      events.innerHTML = "";
      for (const event of [...state.events].reverse()) {{
        const item = document.createElement("div");
        item.className = "event";
        const coords = event.normalizedX !== undefined
          ? ` x=${{event.normalizedX.toFixed(3)}} y=${{event.normalizedY.toFixed(3)}}`
          : "";
        item.innerHTML = `<strong>${{event.type}}${{coords}}</strong><code>${{event.timestamp}}</code><p>${{escapeHtml(event.note || "")}}</p>`;
        events.appendChild(item);
      }}
    }}

    function escapeHtml(value) {{
      return value.replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\\"": "&quot;",
        "'": "&#039;"
      }}[char]));
    }}

    screen.addEventListener("click", (event) => {{
      const rect = screen.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      selected = {{
        normalizedX: Math.max(0, Math.min(1, x / rect.width)),
        normalizedY: Math.max(0, Math.min(1, y / rect.height)),
        pixelX: Math.round(x),
        pixelY: Math.round(y),
        viewport: {{ width: Math.round(rect.width), height: Math.round(rect.height) }}
      }};
      target.style.left = `${{x}}px`;
      target.style.top = `${{y}}px`;
      target.style.display = "block";
      statusText.textContent = "Point selected. Add a note and record the event.";
      note.focus();
    }});

    document.getElementById("save-event").addEventListener("click", async () => {{
      const payload = Object.assign({{
        type: selected ? "tap-request" : "note",
        note: note.value
      }}, selected || {{}});
      const response = await fetch("/api/events", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      const result = await response.json();
      if (!result.ok) {{
        statusText.textContent = result.error || "Failed to record event.";
        return;
      }}
      note.value = "";
      selected = null;
      target.style.display = "none";
      statusText.textContent = "Event recorded.";
      await refreshState();
    }});

    document.getElementById("refresh").addEventListener("click", async () => {{
      refreshImage();
      await refreshState();
    }});

    document.getElementById("copy-handoff").addEventListener("click", async () => {{
      try {{
        await navigator.clipboard.writeText(agentHandoff.textContent);
        copyStatus.textContent = "Copied.";
      }} catch (error) {{
        copyStatus.textContent = "Copy failed. Select the text manually.";
      }}
    }});

    refreshImage();
    refreshState();
    setInterval(refreshImage, refreshMs);
    setInterval(refreshState, Math.max(refreshMs, 1000));
  </script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    if args.host not in LOOPBACK_HOSTS:
        fail("--host must be a loopback host: 127.0.0.1, localhost, or ::1")
    if args.port < 0 or args.port > 65535:
        fail("--port must be between 0 and 65535")
    if args.refresh_ms < 250:
        fail("--refresh-ms must be at least 250")
    if args.event_limit < 1:
        fail("--event-limit must be at least 1")

    out_dir = Path(args.out).expanduser().resolve()
    fixture_image = Path(args.fixture_image).expanduser().resolve() if args.fixture_image else None
    if fixture_image and not fixture_image.is_file():
        fail(f"fixture image not found: {fixture_image}")
    ready_file = Path(args.ready_file).expanduser().resolve() if args.ready_file else None

    session = PreviewSession(
        out_dir=out_dir,
        device=args.device,
        refresh_ms=args.refresh_ms,
        fixture_image=fixture_image,
        event_limit=args.event_limit,
    )
    server = PreviewHTTPServer((args.host, args.port), PreviewHandler, session)
    bound_host, bound_port = server.server_address[:2]
    url_host = "127.0.0.1" if bound_host in {"0.0.0.0", ""} else bound_host
    url = f"http://{url_host}:{bound_port}/"
    session.initialize(url, ready_file)

    print(f"ios preview serving: {url}")
    print(f"session: {session.session_path}")
    print(f"events: {session.event_log}")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
