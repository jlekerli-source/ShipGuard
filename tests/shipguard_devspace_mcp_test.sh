#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"

cleanup() {
  if [[ -n "${server_pid:-}" ]]; then
    kill "$server_pid" >/dev/null 2>&1 || true
    wait "$server_pid" >/dev/null 2>&1 || true
  fi
  if [[ -n "${auth_server_pid:-}" ]]; then
    kill "$auth_server_pid" >/dev/null 2>&1 || true
    wait "$auth_server_pid" >/dev/null 2>&1 || true
  fi
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

cd "$repo_root"

fixture="$tmp_dir/fixture.png"
ready_file="$tmp_dir/devspace-url.txt"
auth_ready_file="$tmp_dir/auth-devspace-url.txt"
preview_out="$tmp_dir/preview"
auth_preview_out="$tmp_dir/auth-preview"
prompt_out="$tmp_dir/codex-handoff.md"
supervisor_out="$tmp_dir/supervisor"
auth_token="shipguard-test-token"

printf 'devspace fixture image bytes\n' > "$fixture"

./bin/codex-maintainer ios devspace --help >/dev/null

python3 - "$tmp_dir" <<'PY'
import subprocess
import sys
from pathlib import Path

tmp_dir = Path(sys.argv[1])
result = subprocess.run(
    [
        "./bin/codex-maintainer",
        "ios",
        "devspace",
        "--host",
        "0.0.0.0",
        "--port",
        "0",
        "--ready-file",
        str(tmp_dir / "bad-ready.txt"),
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=3,
    check=False,
)
assert result.returncode != 0
assert b"loopback" in result.stderr
PY

python3 - <<'PY'
import os
import subprocess

missing_env = "SHIPGUARD_DEVSPACE_TEST_MISSING_TOKEN"
env = os.environ.copy()
env.pop(missing_env, None)
result = subprocess.run(
    [
        "./bin/codex-maintainer",
        "ios",
        "devspace",
        "--port",
        "0",
        "--bearer-token-env",
        missing_env,
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=3,
    check=False,
    env=env,
)
assert result.returncode != 0
assert b"environment variable is empty" in result.stderr

stdio_result = subprocess.run(
    [
        "./bin/codex-maintainer",
        "ios",
        "devspace",
        "--stdio",
        "--bearer-token-env",
        missing_env,
    ],
    input=b"",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=3,
    check=False,
    env=env,
)
assert stdio_result.returncode != 0
assert b"HTTP mode" in stdio_result.stderr
PY

./bin/codex-maintainer ios devspace \
  --port 0 \
  --ready-file "$ready_file" \
  --fixture-image "$fixture" \
  --preview-out "$preview_out" \
  --event-limit 5 >"$tmp_dir/server.log" 2>&1 &
server_pid="$!"

for _ in $(seq 1 80); do
  if [[ -s "$ready_file" ]]; then
    break
  fi
  sleep 0.1
done

test -s "$ready_file"
mcp_url="$(cat "$ready_file")"
case "$mcp_url" in
  http://127.0.0.1:*'/mcp') ;;
  *)
    echo "unexpected MCP URL: $mcp_url" >&2
    exit 1
    ;;
esac

python3 - "$mcp_url" "$preview_out" "$prompt_out" "$supervisor_out" <<'PY'
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

mcp_url = sys.argv[1]
base_url = mcp_url.rsplit("/", 1)[0]
preview_out = str(Path(sys.argv[2]).resolve())
prompt_out = str(Path(sys.argv[3]).resolve())
supervisor_out = str(Path(sys.argv[4]).resolve())

counter = 0

def rpc(method, params=None):
    global counter
    counter += 1
    body = json.dumps(
        {"jsonrpc": "2.0", "id": counter, "method": method, "params": params or {}}
    ).encode("utf-8")
    request = urllib.request.Request(
        mcp_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.load(response)
    assert payload["id"] == counter
    if "error" in payload:
        raise AssertionError(payload["error"])
    return payload["result"]

def expect_http_error(request, status):
    try:
        urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as exc:
        assert exc.code == status, exc.code
        return exc.read().decode("utf-8")
    raise AssertionError(f"expected HTTP {status}")

probe_body = json.dumps({"jsonrpc": "2.0", "id": "probe", "method": "ping", "params": {}}).encode("utf-8")
evil_origin = urllib.request.Request(
    mcp_url,
    data=probe_body,
    headers={"Content-Type": "application/json", "Origin": "https://evil.example"},
    method="POST",
)
assert "non-loopback Origin" in expect_http_error(evil_origin, 403)

plain_post = urllib.request.Request(
    mcp_url,
    data=probe_body,
    headers={"Content-Type": "text/plain"},
    method="POST",
)
assert "application/json" in expect_http_error(plain_post, 415)

evil_host = urllib.request.Request(
    base_url + "/healthz",
    headers={"Host": "evil.example"},
    method="GET",
)
assert "non-loopback Host" in expect_http_error(evil_host, 403)

init = rpc("initialize", {"protocolVersion": "test"})
assert init["serverInfo"]["name"] == "shipguard-devspace"
assert "preview_start" in init["instructions"]
assert "render_preview_widget" in init["instructions"]
assert "preview_handoff_markdown" in init["instructions"]
assert "preview_match_target" in init["instructions"]
assert "production_readiness" in init["instructions"]
assert "semantic XcodeBuildMCP elementRef" in init["instructions"]
assert "not a remote shell" in init["instructions"]
assert "screenshot view-token URLs" in init["instructions"]

tools = rpc("tools/list")["tools"]
tool_names = {tool["name"] for tool in tools}
tools_by_name = {tool["name"]: tool for tool in tools}
for expected in {
    "preview_start",
    "preview_state",
    "preview_screenshot",
    "preview_record_event",
    "preview_handoff",
    "preview_handoff_markdown",
    "preview_target_resolution",
    "preview_match_target",
    "render_preview_widget",
    "production_readiness",
    "codex_prepare_handoff",
}:
    assert expected in tool_names
assert tools_by_name["render_preview_widget"]["_meta"]["ui"]["resourceUri"] == "ui://widget/shipguard-preview-v2.html"
assert tools_by_name["render_preview_widget"]["_meta"]["ui"]["visibility"] == ["model", "app"]
assert tools_by_name["render_preview_widget"]["_meta"]["openai/widgetAccessible"] is True
assert tools_by_name["preview_record_event"]["_meta"]["openai/widgetAccessible"] is True
assert "openai/widgetAccessible" not in tools_by_name["preview_stop"]["_meta"]

readiness = rpc("tools/call", {"name": "production_readiness", "arguments": {}})["structuredContent"]
assert readiness["productionReady"] is False
assert readiness["developerModeReady"] is False
assert readiness["status"] == "local-only"
assert "bearer-auth" in readiness["blockers"]
assert any(check["id"] == "no-raw-coordinate-taps" and check["status"] == "pass" for check in readiness["checks"])
assert any(check["id"] == "local-browser-origin-guard" and check["status"] == "pass" for check in readiness["checks"])
assert any(check["id"] == "json-mcp-post-only" and check["status"] == "pass" for check in readiness["checks"])

resources = rpc("resources/list")["resources"]
assert resources[0]["uri"] == "ui://widget/shipguard-preview-v2.html"

resource = rpc("resources/read", {"uri": "ui://widget/shipguard-preview-v2.html"})["contents"][0]
assert resource["mimeType"] == "text/html;profile=mcp-app"
assert "window.openai.callTool" in resource["text"]
assert "tools/call" in resource["text"]
assert "ui/message" in resource["text"]
assert "context-menu" in resource["text"]
assert "toggle-live" in resource["text"]
assert "refreshPreview" in resource["text"]
assert "Target Resolution" in resource["text"]
assert 'data-action="change-copy"' in resource["text"]
assert resource["_meta"]["ui"]["prefersBorder"] is True

with urllib.request.urlopen(base_url + "/widget/shipguard-preview-v2.html", timeout=5) as response:
    widget_html = response.read().decode("utf-8")
    assert response.headers.get("Content-Type") == "text/html;profile=mcp-app"
assert "Shipguard Devspace" in widget_html
assert "toggle-live" in widget_html

started = rpc(
    "tools/call",
    {
        "name": "preview_start",
        "arguments": {
            "outDir": preview_out,
            "port": 0,
            "refreshMs": 250,
        },
    },
)["structuredContent"]
assert started["previewUrl"].startswith("http://127.0.0.1:")

state = rpc("tools/call", {"name": "preview_state", "arguments": {}})["structuredContent"]
assert state["preview"]["captureMode"] == "fixture"
assert os.path.realpath(state["devspace"]["previewOut"]) == os.path.realpath(preview_out)

shot = rpc("tools/call", {"name": "preview_screenshot", "arguments": {}})["structuredContent"]
assert shot["captureMode"] == "fixture"
assert shot["bytes"] == len(b"devspace fixture image bytes\n")
assert shot["proxyUrl"].endswith("/preview-screenshot.png")

with urllib.request.urlopen(base_url + "/preview-screenshot.png", timeout=5) as response:
    screenshot = response.read()
    mode = response.headers.get("X-Shipguard-Capture-Mode")
assert screenshot == b"devspace fixture image bytes\n"
assert mode == "fixture"

event_result = rpc(
    "tools/call",
    {
        "name": "preview_record_event",
        "arguments": {
            "type": "tap-request",
            "note": "Make this menu button clearer",
            "normalizedX": 0.4,
            "normalizedY": 0.3,
            "pixelX": 120,
            "pixelY": 240,
            "viewport": {"width": 300, "height": 600},
        },
    },
)["structuredContent"]
assert event_result["recorded"]["ok"] is True
assert "Make this menu button clearer" in event_result["handoff"]["prompt"]
assert event_result["handoff"]["targetResolution"]["status"] == "needs-element-ref"
assert event_result["handoff"]["targetResolution"]["rawCoordinateTapAllowed"] is False

handoff = rpc("tools/call", {"name": "preview_handoff", "arguments": {}})["structuredContent"]
assert "elementRef" in " ".join(handoff["handoff"]["suggestedActions"])
assert handoff["handoff"]["targetResolution"]["xcodeBuildMCP"]["elementRefRequiredBeforeTouch"] is True

target_match = rpc(
    "tools/call",
    {
        "name": "preview_match_target",
        "arguments": {
            "maxCandidates": 3,
            "uiSnapshot": {
                "screen": {"width": 300, "height": 600},
                "elements": [
                    {
                        "elementRef": "button-menu",
                        "label": "Menu",
                        "role": "Button",
                        "frame": {"x": 90, "y": 150, "width": 60, "height": 60},
                        "isHittable": True,
                    },
                    {
                        "elementRef": "button-settings",
                        "label": "Settings",
                        "role": "Button",
                        "frame": {"x": 210, "y": 480, "width": 70, "height": 60},
                        "isHittable": True,
                    },
                ],
            },
        },
    },
)["structuredContent"]
assert target_match["match"]["rawCoordinateTapAllowed"] is False
assert target_match["match"]["candidates"][0]["elementRef"] == "button-menu"
assert target_match["match"]["candidates"][0]["confidence"] in {"high", "medium"}

context_event = rpc(
    "tools/call",
    {
        "name": "preview_record_event",
        "arguments": {
            "type": "copy-change",
            "source": "widget-context-menu",
            "action": "change-copy",
            "contextLabel": "Change copy here",
            "note": "Rename this menu item to Account",
            "normalizedX": 0.2,
            "normalizedY": 0.1,
            "pixelX": 60,
            "pixelY": 80,
            "viewport": {"width": 300, "height": 600},
        },
    },
)["structuredContent"]
event = context_event["recorded"]["event"]
assert event["source"] == "widget-context-menu"
assert event["action"] == "change-copy"
assert event["contextLabel"] == "Change copy here"
assert "change-copy" in context_event["handoff"]["prompt"]
assert "localization key" in " ".join(context_event["handoff"]["suggestedActions"])
assert context_event["handoff"]["targetResolution"]["status"] == "source-edit-target"
assert context_event["handoff"]["targetResolution"]["sourceEdit"]["rule"].startswith("Edit the smallest")

target_resolution = rpc("tools/call", {"name": "preview_target_resolution", "arguments": {}})["structuredContent"]
assert target_resolution["targetResolution"]["status"] == "source-edit-target"
assert target_resolution["targetResolution"]["rawCoordinateTapAllowed"] is False
assert target_resolution["targetResolution"]["xcodeBuildMCP"]["nextTool"] == "snapshot_ui"

markdown_handoff = rpc("tools/call", {"name": "preview_handoff_markdown", "arguments": {}})["structuredContent"]
assert markdown_handoff["markdown"].startswith("# iOS Shipguard Preview Handoff")
assert "Rename this menu item to Account" in markdown_handoff["markdown"]
assert "source-edit-target" in markdown_handoff["markdown"]
assert "Do not use browser coordinates as simulator taps." in markdown_handoff["markdown"]

widget = rpc("tools/call", {"name": "render_preview_widget", "arguments": {}})
assert widget["_meta"]["ui"]["resourceUri"] == "ui://widget/shipguard-preview-v2.html"
assert "screenshotProxyUrl" not in widget["structuredContent"]
assert widget["_meta"]["shipguard/screenshotProxyUrl"].endswith("/preview-screenshot.png")
assert widget["_meta"]["shipguard/screenshotProxyRequiresViewToken"] is False
assert widget["structuredContent"]["targetResolution"]["status"] == "source-edit-target"
assert widget["structuredContent"]["handoffMarkdown"].startswith("# iOS Shipguard Preview Handoff")

goal = rpc(
    "tools/call",
    {"name": "codex_goal_emit", "arguments": {"goal": "shipguard-devspace-mcp"}},
)["structuredContent"]
assert "/goal Implement shipguard-devspace-mcp" in goal["slashGoal"]

prepared = rpc(
    "tools/call",
    {"name": "codex_prepare_handoff", "arguments": {"outFile": prompt_out, "supervisorOutDir": supervisor_out}},
)["structuredContent"]
assert prepared["writtenPrompt"] == prompt_out
assert prepared["promptSource"] == "preview-handoff-markdown"
assert Path(prompt_out).read_text(encoding="utf-8").startswith("# iOS Shipguard Preview Handoff")
assert "Status: `source-edit-target`" in Path(prompt_out).read_text(encoding="utf-8")
assert "Raw coordinate tap allowed: `false`" in Path(prompt_out).read_text(encoding="utf-8")
assert "Do not use browser coordinates as simulator taps." in Path(prompt_out).read_text(encoding="utf-8")
assert prepared["codexSupervisor"]["prepared"] is True
assert prepared["targetResolution"]["status"] == "source-edit-target"
assert prepared["handoffMarkdown"].startswith("# iOS Shipguard Preview Handoff")
assert Path(prepared["codexSupervisor"]["planFile"]).is_file()
assert Path(prepared["codexSupervisor"]["messagesFile"]).read_text(encoding="utf-8").count("turn/start") == 1

rpc("tools/call", {"name": "preview_stop", "arguments": {}})

stdio = subprocess.run(
    [
        "./scripts/shipguard_devspace_mcp.py",
        "--stdio",
        "--repo-root",
        ".",
    ],
    input='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    timeout=5,
    check=False,
)
assert stdio.returncode == 0
stdio_payload = json.loads(stdio.stdout)
assert any(tool["name"] == "render_preview_widget" for tool in stdio_payload["result"]["tools"])

plugin_config = json.loads(Path("plugins/ios-shipguard/.mcp.json").read_text(encoding="utf-8"))
plugin_server = plugin_config["mcpServers"]["shipguard-devspace"]
plugin_root = Path("plugins/ios-shipguard").resolve()
plugin_cwd = (plugin_root / plugin_server["cwd"]).resolve()
plugin_stdio = subprocess.run(
    [plugin_server["command"], *plugin_server["args"]],
    cwd=str(plugin_cwd),
    input='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    timeout=5,
    check=False,
)
assert plugin_stdio.returncode == 0, plugin_stdio.stderr
plugin_payload = json.loads(plugin_stdio.stdout)
plugin_tool_names = {tool["name"] for tool in plugin_payload["result"]["tools"]}
assert {"render_preview_widget", "preview_handoff_markdown", "preview_match_target", "codex_prepare_handoff"} <= plugin_tool_names
PY

SHIPGUARD_DEVSPACE_TOKEN="$auth_token" ./bin/codex-maintainer ios devspace \
  --port 0 \
  --ready-file "$auth_ready_file" \
  --fixture-image "$fixture" \
  --preview-out "$auth_preview_out" \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN >"$tmp_dir/auth-server.log" 2>&1 &
auth_server_pid="$!"

for _ in $(seq 1 80); do
  if [[ -s "$auth_ready_file" ]]; then
    break
  fi
  sleep 0.1
done

test -s "$auth_ready_file"
auth_mcp_url="$(cat "$auth_ready_file")"

python3 - "$auth_mcp_url" "$auth_preview_out" "$auth_token" "$tmp_dir/auth-server.log" <<'PY'
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

mcp_url = sys.argv[1]
base_url = mcp_url.rsplit("/", 1)[0]
preview_out = str(Path(sys.argv[2]).resolve())
token = sys.argv[3]
log_path = Path(sys.argv[4])
counter = 0

def expect_http_error(request, status):
    try:
        urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as exc:
        assert exc.code == status, exc.code
        return exc
    raise AssertionError(f"expected HTTP {status}")

health_error = expect_http_error(base_url + "/healthz", 401)
assert "Bearer" in health_error.headers.get("WWW-Authenticate", "")

body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}).encode("utf-8")
unauth_request = urllib.request.Request(
    mcp_url,
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
expect_http_error(unauth_request, 401)

bad_request = urllib.request.Request(
    mcp_url,
    data=body,
    headers={"Content-Type": "application/json", "Authorization": "Bearer wrong-token"},
    method="POST",
)
expect_http_error(bad_request, 401)

def authed_request(url, *, data=None, content_type=None):
    headers = {"Authorization": f"Bearer {token}"}
    if content_type:
        headers["Content-Type"] = content_type
    return urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")

with urllib.request.urlopen(authed_request(base_url + "/healthz"), timeout=5) as response:
    health = json.load(response)
assert health["ok"] is True
assert health["state"]["auth"]["enabled"] is True
assert health["state"]["auth"]["scheme"] == "Bearer"
assert health["state"]["auth"]["screenshotProxy"] == "session-view-token"

def rpc(method, params=None):
    global counter
    counter += 1
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": counter, "method": method, "params": params or {}}
    ).encode("utf-8")
    request = authed_request(mcp_url, data=payload, content_type="application/json")
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.load(response)
    assert result["id"] == counter
    if "error" in result:
        raise AssertionError(result["error"])
    return result["result"]

def rpc_error(method, params=None):
    global counter
    counter += 1
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": counter, "method": method, "params": params or {}}
    ).encode("utf-8")
    request = authed_request(mcp_url, data=payload, content_type="application/json")
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.load(response)
    assert result["id"] == counter
    assert "error" in result
    return result["error"]["message"]

init = rpc("initialize", {"protocolVersion": "test"})
assert init["serverInfo"]["name"] == "shipguard-devspace"
assert "Do not treat widget or browser coordinates as simulator input" in init["instructions"]

resource = rpc("resources/read", {"uri": "ui://widget/shipguard-preview-v2.html"})["contents"][0]
assert resource["mimeType"] == "text/html;profile=mcp-app"

readiness = rpc("tools/call", {"name": "production_readiness", "arguments": {}})["structuredContent"]
assert readiness["productionReady"] is False
assert readiness["developerModeReady"] is True
assert readiness["status"] == "developer-mode-ready"
assert readiness["publicEndpointConfigured"] is False
assert readiness["blockers"] == []
assert "stable public HTTPS hosting" in " ".join(readiness["requiredBeforeProduction"])

outside_preview = str(Path(preview_out).parent / "auth-outside-preview")
message = rpc_error(
    "tools/call",
    {"name": "preview_start", "arguments": {"outDir": outside_preview, "port": 0}},
)
assert "outDir must stay inside previewOut" in message

message = rpc_error(
    "tools/call",
    {
        "name": "preview_start",
        "arguments": {
            "outDir": preview_out,
            "port": 0,
            "fixtureImage": str(Path(preview_out).parent / "fixture.png"),
        },
    },
)
assert "fixtureImage override is disabled" in message

started = rpc(
    "tools/call",
    {
        "name": "preview_start",
        "arguments": {
            "outDir": preview_out,
            "port": 0,
            "refreshMs": 250,
        },
    },
)["structuredContent"]
assert started["previewUrl"].startswith("http://127.0.0.1:")

shot_result = rpc("tools/call", {"name": "preview_screenshot", "arguments": {}})
shot = shot_result["structuredContent"]
assert "view=" not in shot["proxyUrl"]
assert "view=" in shot_result["_meta"]["shipguard/screenshotProxyUrl"]
assert shot_result["_meta"]["shipguard/screenshotProxyRequiresViewToken"] is True
expect_http_error(base_url + "/preview-screenshot.png", 401)

message = rpc_error(
    "tools/call",
    {"name": "codex_prepare_handoff", "arguments": {"outFile": str(Path(preview_out).parent / "blocked-handoff.md")}},
)
assert "outFile must stay inside previewOut" in message

with urllib.request.urlopen(authed_request(base_url + "/preview-screenshot.png"), timeout=5) as response:
    assert response.read() == b"devspace fixture image bytes\n"

with urllib.request.urlopen(shot_result["_meta"]["shipguard/screenshotProxyUrl"], timeout=5) as response:
    assert response.read() == b"devspace fixture image bytes\n"

widget = rpc("tools/call", {"name": "render_preview_widget", "arguments": {}})
assert "screenshotProxyUrl" not in widget["structuredContent"]
widget_url = widget["_meta"]["shipguard/screenshotProxyUrl"]
assert "view=" in widget_url
with urllib.request.urlopen(widget_url, timeout=5) as response:
    assert response.headers.get("X-Shipguard-Capture-Mode") == "fixture"
    assert response.read() == b"devspace fixture image bytes\n"

view_token = parse_qs(urlparse(widget_url).query)["view"][0]
for _ in range(20):
    log_text = log_path.read_text(encoding="utf-8")
    if "<redacted>" in log_text:
        break
    time.sleep(0.05)
else:
    raise AssertionError("expected redacted screenshot token in auth server log")
assert view_token not in log_text

rpc("tools/call", {"name": "preview_stop", "arguments": {}})
PY

echo "shipguard devspace MCP tests passed"
