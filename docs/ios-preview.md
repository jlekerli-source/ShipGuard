# iOS Preview Bridge

`codex-maintainer ios preview` gives iOS Shipguard a local visual loop that works inside Codex today. It serves a phone-shaped localhost page for the Codex in-app browser, refreshes the current Simulator screenshot, and records click or note intent as evidence.

## Start A Preview

Boot and launch your app with XcodeBuildMCP, Xcode, or your normal local workflow. Then run:

```bash
./bin/codex-maintainer ios preview --out /tmp/ios-shipguard-preview
```

The command writes:

- `session.json`: URL, device, output paths, and Codex handoff guidance.
- `preview-url.txt`: the local URL to open in Codex.
- `preview-events.jsonl`: click and note receipts.
- `last-screenshot.png`: the last captured simulator screenshot.

The server also exposes `/api/handoff`, which turns the latest preview event into a Codex prompt plus XcodeBuildMCP next steps.

Open the printed URL in the Codex in-app browser. You can also ask:

```text
@Browser open the iOS Shipguard preview URL from /tmp/ios-shipguard-preview/preview-url.txt.
```

## Use It With Codex

Use Codex browser comments for visual feedback on the preview page. For structured event receipts, click the phone preview, write a short note, and record the event.

Then ask Codex:

```text
Use $ios-shipguard preview-bridge mode. Read /tmp/ios-shipguard-preview/session.json, /tmp/ios-shipguard-preview/preview-events.jsonl, and the preview /api/handoff payload. Inspect the latest screenshot, then make the smallest SwiftUI change for the latest event.
```

For a `tap-request`, Codex should capture a fresh XcodeBuildMCP `snapshot_ui`, match the event coordinates and note to a visible accessibility `elementRef`, and use XcodeBuildMCP `touch` only after the target is identified. The bridge does not send raw coordinate taps into the Simulator because public `simctl` exposes screenshot and video IO, not touch injection. Use XcodeBuildMCP, a focused UI test, or manual simulator interaction for actual tap/swipe proof.

## Fixture Mode

Tests and docs can avoid a live simulator by passing a fixture image:

```bash
./bin/codex-maintainer ios preview \
  --out /tmp/ios-shipguard-preview \
  --fixture-image path/to/screenshot.png \
  --port 0
```

`--port 0` asks the OS for a free loopback port. Use `--ready-file <path>` when another process needs to wait for the URL.

## Security Boundary

The server binds to `127.0.0.1` by default and rejects non-loopback hosts. Event posts are size-limited JSON. The server writes under `--out` and reads only the optional `--fixture-image`.

The preview page is for local development feedback. Do not paste secrets into the page, and do not treat preview events as release proof. For release claims, keep distinguishing local, simulator, TestFlight, physical-device, App Store Connect, and blocked-manual evidence.

## Platform Boundary

Current Codex plugin docs describe bundled skills, apps/connectors, MCP servers, hooks, and assets. They do not document a plugin-owned native Codex side panel or arbitrary right-click integration inside Codex. This bridge uses the documented in-app browser path for local visual previews and browser comments.

If Codex later exposes plugin-owned panels, this localhost page can become the embedded UI. Until then, the reliable path is: simulator screenshot -> local preview page -> browser comments or event receipts -> `/api/handoff` -> Codex/XcodeBuildMCP action -> simulator proof.

## ChatGPT Devspace

When you want the ChatGPT Apps / MCP version of this workflow, start Shipguard Devspace:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"
./bin/codex-maintainer ios devspace \
  --port 8787 \
  --preview-out /tmp/ios-shipguard-preview \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN
```

Devspace exposes `/mcp`, a phone preview widget resource, a screenshot proxy, preview event tools, and a guarded Codex handoff preparation tool. Use bearer auth for tunneled HTTP mode. See `shipguard-devspace.md`.
