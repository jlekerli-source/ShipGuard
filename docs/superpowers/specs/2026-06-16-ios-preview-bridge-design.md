# iOS Preview Bridge Design

## Purpose

iOS Shipguard should give Codex a practical app preview loop for iOS work without waiting for a new Codex host API. The viable first version is a local preview bridge that serves the booted iOS Simulator screen into Codex's existing in-app browser, records click/comment intent as structured evidence, and exposes an agent handoff payload for edits and simulator proof.

## Feasibility Boundary

Current Codex docs support plugin bundles with skills, apps/connectors, MCP servers, hooks, and assets. They also document the in-app browser, browser comments, Browser use, app-server clients, and plugin-provided MCP servers. They do not document a plugin-owned native side panel or plugin-owned right-click menu inside arbitrary Codex windows.

Because of that boundary, this design does not claim a native embedded phone panel. It ships the useful workflow through a localhost browser page that Codex can open and annotate today. A native panel or right-click integration stays a future host-platform request.

## User Experience

The user starts a preview session:

```bash
./bin/codex-maintainer ios preview --out /tmp/shipguard-preview
```

The command prints and writes a localhost URL. The user opens that URL in the Codex in-app browser. The page shows a phone-shaped preview with an auto-refreshing screenshot from the booted simulator. The user can click an area, add a short note, and Codex records that as an event in `preview-events.jsonl`.

For visual feedback, the user can also use Codex browser comments directly on the preview page. The page keeps stable visible regions and a short Codex handoff block so the next prompt can say: read the preview session, latest event, `/api/handoff`, and screenshot, then modify the owning SwiftUI files or use XcodeBuildMCP semantic element refs.

## Architecture

`bin/codex-maintainer ios preview` dispatches to `scripts/ios_preview.py`.

The Python script uses only the standard library. It starts a loopback HTTP server, captures screenshots with:

```bash
xcrun simctl io <device> screenshot --type=png <tempfile>
```

and serves:

- `/`: preview HTML.
- `/screenshot.png`: latest simulator screenshot.
- `/api/state`: session metadata and recent events.
- `/api/events`: event append and event listing.
- `/api/handoff`: latest event plus Codex/XcodeBuildMCP next-step guidance.
- `/session.json`: session receipt for Codex.

The session writes:

- `session.json`: URL, device, output paths, and handoff instructions.
- `preview-url.txt`: browser URL.
- `preview-events.jsonl`: click/comment intent receipts.
- `last-screenshot.png`: last captured image when capture succeeds.

Tests use `--fixture-image` so the preview server can be validated without a booted simulator.

## Security

The server binds to `127.0.0.1` by default and must not expose a remote listener unless a future option explicitly documents that risk. POST bodies are size-limited JSON. File reads are limited to a caller-provided fixture image and writes stay under `--out`.

The MVP does not execute arbitrary tap commands from browser input. Public `simctl` exposes screenshot/video IO but not touch injection. Clicks are recorded as intent events and translated into `/api/handoff`; Codex or the user can then use XcodeBuildMCP `snapshot_ui` plus semantic `touch` elementRefs, UI tests, or manual simulator interaction to perform the tap in a reviewable path.

## Plugin Integration

The `ios-shipguard` skill gains a `preview-bridge` mode. It tells Codex to:

1. run `ios doctor` or inventory when topology is unknown,
2. start `ios preview`,
3. open the URL with `@Browser`,
4. use browser comments or preview events to scope requested UI changes,
5. validate with the smallest honest proof lane.

The local goal loop gains `shipguard-ios-preview-bridge` so the feature is visible as a slash-goal artifact.

## Non-Goals

- No native Codex panel API is assumed.
- No direct right-click host integration is claimed.
- No default AppleScript or global mouse automation.
- No hosted dashboard.
- No replacement for XcodeBuildMCP simulator driving.

## Future Path

If Codex exposes plugin-owned panels later, the localhost preview page can become the embedded panel content. If a stable simulator tap API is available through XcodeBuildMCP or another supported local tool surface, the event log can be upgraded from intent receipts to approved simulator actions.
