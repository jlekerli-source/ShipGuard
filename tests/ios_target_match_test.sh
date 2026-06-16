#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

handoff="$tmp_dir/handoff.json"
snapshot="$tmp_dir/snapshot.json"
out_dir="$tmp_dir/match"

./bin/codex-maintainer ios target-match --help >/dev/null

cat >"$handoff" <<'JSON'
{
  "ok": true,
  "latestEvent": {
    "type": "tap-request",
    "source": "widget-context-menu",
    "action": "tap",
    "contextLabel": "Tap or navigate here",
    "note": "Rename this menu button",
    "normalizedX": 0.25,
    "normalizedY": 0.75,
    "pixelX": 98,
    "pixelY": 633,
    "viewport": {"width": 390, "height": 844}
  },
  "targetResolution": {
    "status": "needs-element-ref",
    "intent": "tap-request",
    "rawCoordinateTapAllowed": false,
    "xcodeBuildMCP": {
      "nextTool": "describe_ui",
      "elementRefRequiredBeforeTouch": true
    }
  }
}
JSON

cat >"$snapshot" <<'JSON'
{
  "screen": {"width": 390, "height": 844},
  "elements": [
    {
      "elementRef": "title-welcome",
      "label": "Welcome",
      "role": "StaticText",
      "frame": {"x": 28, "y": 80, "width": 180, "height": 40}
    },
    {
      "elementRef": "button-menu",
      "label": "Menu",
      "role": "Button",
      "frame": {"x": 70, "y": 604, "width": 84, "height": 56},
      "isHittable": true,
      "isEnabled": true
    },
    {
      "elementRef": "button-home",
      "label": "Home",
      "role": "Button",
      "frame": {"x": 250, "y": 604, "width": 84, "height": 56},
      "isHittable": true,
      "isEnabled": true
    }
  ]
}
JSON

./bin/codex-maintainer ios target-match \
  --handoff "$handoff" \
  --snapshot "$snapshot" \
  --out "$out_dir" >/dev/null

test -f "$out_dir/ios-target-match.json"
test -f "$out_dir/ios-target-match.md"

python3 - "$out_dir/ios-target-match.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["ok"] is True
assert payload["status"] == "matched"
assert payload["rawCoordinateTapAllowed"] is False
assert payload["screenSize"] == {"width": 390.0, "height": 844.0}
assert payload["candidateCount"] == 3
top = payload["candidates"][0]
assert top["elementRef"] == "button-menu"
assert top["confidence"] in {"high", "medium"}
assert top["score"] > payload["candidates"][1]["score"]
assert any("coordinate distance" in reason for reason in top["reasons"])
assert any("menu" in reason for reason in top["reasons"])
assert "Do not use raw browser coordinates" in " ".join(payload["nextSteps"])
PY

grep -q '# iOS Target Match' "$out_dir/ios-target-match.md"
grep -q 'button-menu' "$out_dir/ios-target-match.md"

json_output="$(./bin/codex-maintainer ios target-match --handoff "$handoff" --snapshot "$snapshot")"
case "$json_output" in
  *'"elementRef": "button-menu"'*) ;;
  *)
    echo "expected stdout JSON to include button-menu" >&2
    exit 1
    ;;
esac

echo "ios target match tests passed"
