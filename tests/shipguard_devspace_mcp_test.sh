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

init = rpc("initialize", {"protocolVersion": "test"})
assert init["serverInfo"]["name"] == "shipguard-devspace"

tools = rpc("tools/list")["tools"]
tool_names = {tool["name"] for tool in tools}
for expected in {
    "preview_start",
    "preview_state",
    "preview_screenshot",
    "preview_record_event",
    "preview_handoff",
    "render_preview_widget",
    "codex_prepare_handoff",
}:
    assert expected in tool_names

resources = rpc("resources/list")["resources"]
assert resources[0]["uri"] == "ui://widget/shipguard-preview-v1.html"

resource = rpc("resources/read", {"uri": "ui://widget/shipguard-preview-v1.html"})["contents"][0]
assert resource["mimeType"] == "text/html;profile=mcp-app"
assert "window.openai.callTool" in resource["text"]
assert "ui/message" in resource["text"]
assert "context-menu" in resource["text"]
assert 'data-action="change-copy"' in resource["text"]
assert resource["_meta"]["ui"]["prefersBorder"] is True

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

handoff = rpc("tools/call", {"name": "preview_handoff", "arguments": {}})["structuredContent"]
assert "elementRef" in " ".join(handoff["handoff"]["suggestedActions"])

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

widget = rpc("tools/call", {"name": "render_preview_widget", "arguments": {}})
assert widget["_meta"]["ui"]["resourceUri"] == "ui://widget/shipguard-preview-v1.html"
assert widget["structuredContent"]["screenshotProxyUrl"].endswith("/preview-screenshot.png")

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
assert Path(prompt_out).read_text(encoding="utf-8").startswith("Use $ios-shipguard")
assert prepared["codexSupervisor"]["prepared"] is True
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

init = rpc("initialize", {"protocolVersion": "test"})
assert init["serverInfo"]["name"] == "shipguard-devspace"

resource = rpc("resources/read", {"uri": "ui://widget/shipguard-preview-v1.html"})["contents"][0]
assert resource["mimeType"] == "text/html;profile=mcp-app"

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

shot = rpc("tools/call", {"name": "preview_screenshot", "arguments": {}})["structuredContent"]
assert "view=" in shot["proxyUrl"]
expect_http_error(base_url + "/preview-screenshot.png", 401)

with urllib.request.urlopen(authed_request(base_url + "/preview-screenshot.png"), timeout=5) as response:
    assert response.read() == b"devspace fixture image bytes\n"

with urllib.request.urlopen(shot["proxyUrl"], timeout=5) as response:
    assert response.read() == b"devspace fixture image bytes\n"

widget = rpc("tools/call", {"name": "render_preview_widget", "arguments": {}})
widget_url = widget["structuredContent"]["screenshotProxyUrl"]
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
