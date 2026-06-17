# iOS Preview Bridge

`shipguard ios preview` gives iOS ShipGuard a local visual loop that works inside Codex today. It serves a phone-shaped localhost page for the Codex in-app browser, refreshes the current Simulator screenshot, and records click, right-click, or note intent as evidence.

## Start A Preview

Boot and launch your app with XcodeBuildMCP, Xcode, or your normal local workflow. Then run:

```bash
./bin/shipguard ios preview --out /tmp/ios-shipguard-preview
```

The command writes:

- `session.json`: URL, device, output paths, and Codex handoff guidance.
- `preview-url.txt`: the local URL to open in Codex.
- `preview-events.jsonl`: click, right-click context menu, and note receipts.
- `handoff.json`: latest Codex/XcodeBuildMCP handoff, target resolution, and receipts.
- `handoff.md`: copy-ready Markdown prompt, target-resolution plan, receipts, and safety rules.
- `last-screenshot.png`: the last captured simulator screenshot.

The server also exposes `/api/handoff` and `/api/handoff.md`, which turn the latest preview event into a Codex prompt, XcodeBuildMCP next steps, receipts, safety rules, and a structured `targetResolution` object.

Open the printed URL in the Codex in-app browser. You can also ask:

```text
@Browser open the iOS ShipGuard preview URL from /tmp/ios-shipguard-preview/preview-url.txt.
```

## Use It With Codex

Use Codex browser comments for visual feedback on the preview page. For structured event receipts, click the phone preview for a tap intent, or right-click the preview to choose typed intent such as tap/navigation, copy change, visual fix, or inspection. Add a short note, then record the event.

Then ask Codex:

```text
Use $ios-shipguard preview-bridge mode. Read /tmp/ios-shipguard-preview/handoff.md and /tmp/ios-shipguard-preview/preview-events.jsonl. Inspect the latest screenshot, then make the smallest SwiftUI change for the latest event.
```

For a `tap-request`, Codex should capture a fresh XcodeBuildMCP `snapshot_ui`, match the event coordinates and note to a visible accessibility `elementRef`, and use XcodeBuildMCP `touch` only after the target is identified. For `copy-change` and `visual-bug` events, Codex should edit source and refresh preview proof instead of tapping the simulator. The `targetResolution` payload records this as `rawCoordinateTapAllowed: false`. The bridge does not send raw coordinate taps into the Simulator because public `simctl` exposes screenshot and video IO, not touch injection. Use XcodeBuildMCP, a focused UI test, or manual simulator interaction for actual tap/swipe proof.

If you save the XcodeBuildMCP `describe_ui` or `snapshot_ui` JSON, rank likely targets locally:

```bash
./bin/shipguard ios target-match \
  --handoff /tmp/ios-shipguard-preview/handoff.json \
  --snapshot /tmp/ios-shipguard-preview/describe-ui.json \
  --out /tmp/ios-shipguard-preview/target-match
```

This produces candidate `elementRef`, label, and role matches for review. It does not tap the simulator.

## Fixture Mode

Tests and docs can avoid a live simulator by passing a fixture image:

```bash
./bin/shipguard ios preview \
  --out /tmp/ios-shipguard-preview \
  --fixture-image path/to/screenshot.png \
  --port 0
```

`--port 0` asks the OS for a free loopback port. Use `--ready-file <path>` when another process needs to wait for the URL.

## Security Boundary

The server binds to `127.0.0.1` by default and rejects non-loopback hosts. Event posts are size-limited JSON. The server writes under `--out` and reads only the optional `--fixture-image`.

The preview page is for local development feedback. Do not paste secrets into the page, and do not treat preview events as release proof. For release claims, keep distinguishing local, simulator, TestFlight, physical-device, App Store Connect, and blocked-manual evidence.

## Platform Boundary

Current Codex plugin docs describe bundled skills, apps/connectors, MCP servers, hooks, and assets. They do not document a plugin-owned native Codex side panel or arbitrary global right-click integration inside Codex. This bridge implements right-click intent inside its own local preview page and uses the documented in-app browser path for local visual previews and browser comments.

If Codex later exposes plugin-owned panels, this localhost page can become the embedded UI. Until then, the reliable path is: simulator screenshot -> local preview page -> browser comments or event receipts -> `/api/handoff.md` or `handoff.md` -> Codex/XcodeBuildMCP action -> simulator proof.

## ChatGPT Devspace

When you want the ChatGPT Apps / MCP version of this workflow, start ShipGuard Devspace:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"
./bin/shipguard ios devspace \
  --port 8787 \
  --preview-out /tmp/ios-shipguard-preview \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN
```

Devspace exposes `/mcp`, a versioned phone preview widget resource, a screenshot proxy, preview event tools, `preview_target_resolution`, `preview_match_target`, `production_readiness`, and a guarded Codex handoff preparation tool. Use bearer auth for tunneled HTTP mode. See `shipguard-devspace.md`.
