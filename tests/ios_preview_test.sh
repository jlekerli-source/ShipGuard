#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'if [[ -n "${server_pid:-}" ]]; then kill "$server_pid" >/dev/null 2>&1 || true; wait "$server_pid" >/dev/null 2>&1 || true; fi; rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/fixture.png"
ready_file="$tmp_dir/preview-url.txt"
preview_out="$tmp_dir/preview"

printf 'fixture image bytes\n' > "$fixture"

./bin/codex-maintainer ios preview --help >/dev/null

python3 - "$tmp_dir" <<'PY'
import subprocess
import sys
from pathlib import Path

tmp_dir = Path(sys.argv[1])
result = subprocess.run(
    [
        "./bin/codex-maintainer",
        "ios",
        "preview",
        "--out",
        str(tmp_dir / "bad-host"),
        "--host",
        "0.0.0.0",
        "--port",
        "0",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=3,
    check=False,
)
assert result.returncode != 0
assert b"loopback" in result.stderr
PY

./bin/codex-maintainer ios preview \
  --out "$preview_out" \
  --fixture-image "$fixture" \
  --port 0 \
  --ready-file "$ready_file" \
  --refresh-ms 250 \
  --event-limit 5 >"$tmp_dir/server.log" 2>&1 &
server_pid="$!"

for _ in $(seq 1 80); do
  if [[ -s "$ready_file" ]]; then
    break
  fi
  sleep 0.1
done

test -s "$ready_file"
url="$(cat "$ready_file")"
case "$url" in
  http://127.0.0.1:*/*) ;;
  *)
    echo "unexpected preview URL: $url" >&2
    exit 1
    ;;
esac

python3 - "$url" "$preview_out" <<'PY'
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

url = sys.argv[1].rstrip("/")
preview_out = str(Path(sys.argv[2]).resolve())

with urllib.request.urlopen(url + "/", timeout=5) as response:
    html = response.read().decode("utf-8")
assert "Agent Action" in html
assert "agent-handoff" in html
assert "Full Handoff" in html
assert "handoff-markdown" in html
assert "copy-full-handoff" in html
assert "context-menu" in html
assert 'data-action="change-copy"' in html

with urllib.request.urlopen(url + "/api/state", timeout=5) as response:
    state = json.load(response)
assert state["device"] == "booted"
assert state["eventLog"].endswith("preview-events.jsonl")
assert state["handoffJson"].endswith("handoff.json")
assert state["handoffMarkdown"].endswith("handoff.md")
assert state["outDir"] == preview_out
assert state["captureMode"] == "fixture"
assert state["agentHandoff"]["latestEvent"] is None
assert state["agentHandoff"]["targetResolution"]["status"] == "waiting-for-event"
assert state["agentHandoff"]["targetResolution"]["rawCoordinateTapAllowed"] is False
assert "snapshot_ui" in " ".join(state["agentHandoff"]["suggestedActions"])

with urllib.request.urlopen(url + "/api/handoff.md", timeout=5) as response:
    handoff_md = response.read().decode("utf-8")
assert response.headers.get("Content-Type") == "text/markdown; charset=utf-8"
assert "# iOS Shipguard Preview Handoff" in handoff_md
assert "waiting-for-event" in handoff_md
assert "Raw coordinate tap allowed: `false`" in handoff_md
assert "Do not use browser coordinates as simulator taps." in handoff_md

with urllib.request.urlopen(url + "/screenshot.png", timeout=5) as response:
    screenshot = response.read()
assert screenshot == b"fixture image bytes\n"

payload = json.dumps(
    {
        "type": "tap-request",
        "source": "preview-context-menu",
        "action": "tap",
        "contextLabel": "Tap or navigate here",
        "note": "Rename this menu button",
        "normalizedX": 0.25,
        "normalizedY": 0.75,
        "pixelX": 98,
        "pixelY": 531,
        "viewport": {"width": 390, "height": 844},
    }
).encode("utf-8")
request = urllib.request.Request(
    url + "/api/events",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    result = json.load(response)
assert result["ok"] is True
assert result["event"]["type"] == "tap-request"
assert result["event"]["source"] == "preview-context-menu"
assert result["event"]["action"] == "tap"
assert result["event"]["contextLabel"] == "Tap or navigate here"
assert result["event"]["normalizedX"] == 0.25

with urllib.request.urlopen(url + "/api/events", timeout=5) as response:
    events = json.load(response)["events"]
assert len(events) == 1
assert events[0]["note"] == "Rename this menu button"
assert events[0]["source"] == "preview-context-menu"

with urllib.request.urlopen(url + "/api/handoff", timeout=5) as response:
    handoff = json.load(response)
assert handoff["latestEvent"]["type"] == "tap-request"
assert handoff["latestEvent"]["action"] == "tap"
assert "Rename this menu button" in handoff["prompt"]
assert "elementRef" in " ".join(handoff["suggestedActions"])
resolution = handoff["targetResolution"]
assert resolution["status"] == "needs-element-ref"
assert resolution["intent"] == "tap-request"
assert resolution["rawCoordinateTapAllowed"] is False
assert resolution["xcodeBuildMCP"]["nextTool"] == "snapshot_ui"
assert resolution["xcodeBuildMCP"]["elementRefRequiredBeforeTouch"] is True
assert resolution["xcodeBuildMCP"]["allowedAfterMatch"] == ["touch(elementRef)"]
assert resolution["coordinates"]["normalized"] == {"x": 0.25, "y": 0.75}

copy_payload = json.dumps(
    {
        "type": "copy-change",
        "source": "preview-context-menu",
        "action": "change-copy",
        "contextLabel": "Change copy here",
        "note": "Rename this label to Account",
        "normalizedX": 0.4,
        "normalizedY": 0.2,
        "pixelX": 156,
        "pixelY": 169,
        "viewport": {"width": 390, "height": 844},
    }
).encode("utf-8")
request = urllib.request.Request(
    url + "/api/events",
    data=copy_payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    copy_result = json.load(response)
assert copy_result["ok"] is True
assert copy_result["event"]["type"] == "copy-change"
assert copy_result["event"]["source"] == "preview-context-menu"
assert copy_result["event"]["action"] == "change-copy"

with urllib.request.urlopen(url + "/api/handoff", timeout=5) as response:
    handoff = json.load(response)
assert handoff["latestEvent"]["type"] == "copy-change"
assert "Rename this label to Account" in handoff["prompt"]
resolution = handoff["targetResolution"]
assert resolution["status"] == "source-edit-target"
assert resolution["rawCoordinateTapAllowed"] is False
assert resolution["sourceEdit"]["rule"].startswith("Edit the smallest")

with urllib.request.urlopen(url + "/api/handoff.md", timeout=5) as response:
    handoff_md = response.read().decode("utf-8")
assert "source-edit-target" in handoff_md
assert "Rename this label to Account" in handoff_md
assert "handoffMarkdown" in handoff_md
assert "For copy or visual events, edit source and refresh preview proof instead of tapping the simulator." in handoff_md

oversized = json.dumps({"type": "note", "note": "x" * (17 * 1024)}).encode("utf-8")
request = urllib.request.Request(
    url + "/api/events",
    data=oversized,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    urllib.request.urlopen(request, timeout=5)
except urllib.error.HTTPError as error:
    assert error.code == 413
else:
    raise AssertionError("oversized event body should be rejected")
PY

test -f "$preview_out/session.json"
test -f "$preview_out/preview-url.txt"
test -f "$preview_out/preview-events.jsonl"
test -f "$preview_out/handoff.json"
test -f "$preview_out/handoff.md"
test -f "$preview_out/last-screenshot.png"
grep -q '"tool": "codex-maintainer ios preview"' "$preview_out/session.json"
grep -q '/api/handoff' "$preview_out/session.json"
grep -q 'handoff.md' "$preview_out/session.json"
grep -q '"targetResolution":' "$preview_out/handoff.json"
grep -q '"elementRefRequiredBeforeTouch": true' "$preview_out/handoff.json"
grep -q '# iOS Shipguard Preview Handoff' "$preview_out/handoff.md"
grep -q 'source-edit-target' "$preview_out/handoff.md"
grep -q 'Rename this label to Account' "$preview_out/handoff.md"
grep -q '"type": "tap-request"' "$preview_out/preview-events.jsonl"
grep -q '"source": "preview-context-menu"' "$preview_out/preview-events.jsonl"
grep -q '"action": "tap"' "$preview_out/preview-events.jsonl"
grep -q '"type": "copy-change"' "$preview_out/preview-events.jsonl"
grep -q '"action": "change-copy"' "$preview_out/preview-events.jsonl"
grep -q 'Rename this menu button' "$preview_out/preview-events.jsonl"
grep -q 'Rename this label to Account' "$preview_out/preview-events.jsonl"

echo "ios preview tests passed"
