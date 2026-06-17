# ShipGuard Devspace

`shipguard ios devspace` turns the local iOS preview bridge into a ChatGPT Apps / MCP connector surface. It is the path for using ChatGPT as the planning and visual feedback layer while Codex remains the local implementation and proof agent.

## Architecture

```text
ChatGPT Developer Mode
  -> ShipGuard Devspace /mcp
  -> phone preview widget
  -> ios preview bridge
  -> Xcode Simulator screenshot and event receipts
  -> Codex handoff prompt
```

The Devspace connector has two run modes:

- HTTP mode for ChatGPT Developer Mode and widget rendering.
- stdio mode for the `ios-shipguard` Codex plugin MCP sidecar.

The app archetype is `interactive-decoupled`: data/action tools stay separate from the render tool so ChatGPT can reason about preview state before showing the widget.

The MCP `initialize` response includes server-level instructions for host models. Those instructions describe the expected start, render, record, target-resolution, target-match, and Codex handoff sequence, and restate the no-raw-coordinate-tap and no-token-in-prompts boundaries.

## Start HTTP Mode

Start the Devspace MCP endpoint:

```bash
./bin/shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview
```

For deterministic testing without a booted simulator:

```bash
./bin/shipguard ios devspace \
  --port 8787 \
  --fixture-image path/to/screenshot.png \
  --preview-out /tmp/ios-shipguard-preview
```

When exposing Devspace through an HTTPS tunnel, require a bearer token:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"

./bin/shipguard ios devspace \
  --port 8787 \
  --preview-out /tmp/ios-shipguard-preview \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN
```

Codex streamable HTTP MCP config can pass this token with `bearer_token_env_var`. For ChatGPT Developer Mode, configure the app's auth setting for the tunneled MCP endpoint when available. Do not paste the token into prompts, preview notes, or logs.

The command prints:

- `http://127.0.0.1:<port>/mcp`: JSON-RPC MCP endpoint.
- `http://127.0.0.1:<port>/healthz`: local health and state endpoint.
- `http://127.0.0.1:<port>/preview-screenshot.png`: screenshot proxy used by the widget after a preview starts.
- `auth: bearer token required` when `--bearer-token-env` or `--bearer-token-file` is configured.

HTTP mode binds to loopback only. In unauthenticated local mode, Devspace rejects non-loopback `Host`, `Origin`, and `Referer` headers and requires `application/json` for `/mcp` POST bodies. To connect ChatGPT Developer Mode, expose the endpoint with an HTTPS tunnel and use the tunneled URL plus `/mcp` with bearer auth.

## ChatGPT Developer Mode

1. Start `ios devspace` locally.
2. Expose the local port with an HTTPS tunnel.
3. In ChatGPT, enable Developer Mode under Apps and Connectors advanced settings.
4. Create a new app from the tunneled MCP URL.
5. Ask ChatGPT to call `preview_start`, then `render_preview_widget`.
6. Right-click a point in the phone preview to choose a typed action such as tap, copy change, visual fix, or inspection.
7. Ask ChatGPT to prepare a Codex handoff once the event is recorded.

Useful prompt:

```text
Use the ShipGuard Devspace app. Start the iOS preview, render the phone widget, and wait for my visual event before preparing a Codex handoff.
```

Refresh or reconnect the ChatGPT app after changing tool descriptors, widget HTML, or resource metadata.

## MCP Tools

| Tool | Purpose | Mutates local state |
| --- | --- | --- |
| `preview_start` | Start or attach to `shipguard ios preview` | Yes |
| `preview_stop` | Stop the preview process started by Devspace | Yes |
| `preview_state` | Read Devspace and preview state | No |
| `preview_screenshot` | Capture screenshot metadata and proxy URL | No |
| `preview_record_event` | Record click, note, navigation, visual-bug, or copy-change intent | Yes |
| `preview_handoff` | Read the latest Codex/XcodeBuildMCP handoff payload | No |
| `preview_handoff_markdown` | Read the copy-ready Markdown handoff from the active preview | No |
| `preview_target_resolution` | Read structured guidance for mapping the latest visual event to source or a semantic `elementRef` | No |
| `preview_match_target` | Rank `describe_ui` or `snapshot_ui` elements against the latest visual event | No |
| `render_preview_widget` | Return the widget template and current preview data | No |
| `simulator_list` | List local iOS Simulator devices from `simctl` | No |
| `production_readiness` | Report Developer Mode readiness, production blockers, and hosting/security invariants | No |
| `codex_goal_emit` | Emit a ShipGuard slash-goal from the local catalog | No |
| `codex_prepare_handoff` | Prepare a Codex app-server turn prompt, optionally writing it and supervisor artifacts locally | Yes |

The widget resource URI is:

```text
ui://widget/shipguard-preview-v2.html
```

It is served as:

```text
text/html;profile=mcp-app
```

The widget uses the MCP Apps bridge for tool results, `tools/call` for portable widget tool calls, and `window.openai.callTool` when available for ChatGPT-hosted button actions. A right-click in the phone preview opens an in-widget context menu that records bounded event metadata: `source`, `action`, `contextLabel`, coordinates, and the user's note.

The preview widget auto-refreshes through bounded calls to the read-only `render_preview_widget` tool. Manual refresh remains available, and the widget reports a paused or unavailable live state when it is not running inside ChatGPT or another MCP Apps host. When bearer auth is enabled, screenshot view-token URLs are returned in widget-only `_meta` rather than model-visible `structuredContent`. The widget and `preview_handoff_markdown` surface the preview's full `handoff.md` so ChatGPT can hand Codex the target-resolution plan, receipts, and safety rules without reconstructing them.

Use `production_readiness` before discussing hosted or production Devspace. It reports whether bearer auth is enabled, whether a public HTTPS endpoint is configured, which local-first security invariants are active, and which reviews are still required before production hosting. It does not enable non-loopback binding.

## Codex Handoff

`codex_prepare_handoff` prepares the prompt that should be sent into Codex. When an active preview exposes `handoff.md`, this tool uses that Markdown as the default prompt; otherwise it falls back to the JSON handoff prompt plus target-resolution summary. It does not spawn Codex automatically. That guard is intentional: Codex app-server execution should run through a trusted local supervisor or explicit user action because it can edit code and run tools.

The handoff path is:

```text
preview event -> preview_handoff_markdown -> codex_prepare_handoff -> Codex turn -> validation proof
```

When a `tap-request` or `navigate-request` exists, the handoff instructs Codex to use XcodeBuildMCP `describe_ui` or `snapshot_ui`, map the visual event to a semantic `elementRef`, then use `tap` or `touch` only after the target is identified. The same rule is exposed as `targetResolution.status = needs-element-ref` with `rawCoordinateTapAllowed = false`. `preview_match_target` can rank UI snapshot candidates, but it never performs simulator input. Copy and visual-fix context events route to source-code edits and preview proof instead of simulator taps.

## Codex Handoff Supervisor

For an explicit local app-server handoff, prepare a supervisor bundle:

```bash
./bin/shipguard ios codex-handoff \
  --prompt-file /tmp/ios-shipguard-preview/codex-handoff.md \
  --out /tmp/ios-shipguard-preview/codex-supervisor
```

This writes:

- `codex-handoff-prompt.md`
- `codex-app-server-plan.json`
- `codex-app-server-messages.jsonl`

To actually start `codex app-server`, add `--execute` yourself from a trusted local terminal:

```bash
./bin/shipguard ios codex-handoff \
  --prompt-file /tmp/ios-shipguard-preview/codex-supervisor/codex-handoff-prompt.md \
  --out /tmp/ios-shipguard-preview/codex-supervisor \
  --cwd /path/to/repo \
  --execute
```

Devspace can also prepare these artifacts through `codex_prepare_handoff` by passing `supervisorOutDir`. It still does not execute Codex from MCP.

## Codex Plugin Mode

The `ios-shipguard` plugin includes `.mcp.json` for stdio MCP integration:

```json
{
  "mcpServers": {
    "shipguard-devspace": {
      "command": "python3",
      "args": ["./scripts/shipguard_devspace_mcp.py", "--stdio", "--repo-root", "."]
    }
  }
}
```

In this repository's local plugin layout, the MCP server runs from the repository root so it can call `bin/shipguard`.

## Security Boundary

Threat model:

- Assets: app screenshots, UI event notes, local paths, team IDs, bundle IDs, Apple accounts, bearer tokens, Codex handoff prompts, and any generated report that might later be pasted into ChatGPT, GitHub, or CI logs.
- Trust boundaries: the local terminal and loopback server are trusted developer space; tunneled ChatGPT Developer Mode is semi-trusted planning space; public issues, release evidence, and benchmark corpora are untrusted publication space.
- Attacker-controlled inputs: MCP request bodies, preview event notes, context-menu labels, handoff prompt text, local report contents, and tunnel-origin HTTP metadata.
- Invariants: Devspace must not expose arbitrary shell execution, must not treat browser coordinates as simulator taps, must not place bearer tokens in prompts, must not leak screenshot view tokens to model-visible tool content, and should run `ios redact` before report artifacts cross from local proof into publication or external planning.

- HTTP mode rejects non-loopback hosts.
- HTTP mode can require `Authorization: Bearer <token>` through `--bearer-token-env` or `--bearer-token-file`.
- MCP request bodies are size-limited.
- Preview event payloads are bounded and schema-like.
- Unauthenticated local HTTP mode rejects non-loopback `Host`, `Origin`, and `Referer` headers.
- `/mcp` accepts JSON POST bodies only.
- In bearer-auth HTTP mode, MCP file-write path arguments must stay inside the active `previewOut` directory.
- In bearer-auth HTTP mode, `preview_start.fixtureImage` overrides are disabled; use a trusted local `--fixture-image` at server startup for tests.
- The connector does not expose arbitrary shell execution.
- The connector does not treat browser click coordinates as simulator taps.
- The context menu records typed visual intent; it does not execute Codex or Xcode actions.
- The connector does not spawn Codex app-server automatically.
- `ios codex-handoff --execute` is a separate local terminal action and records a transcript.
- When bearer auth is enabled, the screenshot proxy URL includes a random per-session view token because browser `<img>` requests cannot attach an Authorization header. That token is returned only in tool-result `_meta`, can only fetch the current screenshot proxy, and cannot call MCP tools.
- Use HTTPS tunneling only for local Developer Mode testing; production hosting needs its own auth, logging, and secret-handling review.

Do not paste secrets into preview notes. Treat screenshots and event receipts as local planning evidence, not release proof. Before sharing generated reports or logs, run:

```bash
./bin/shipguard ios redact --in /tmp/ios-shipguard-preview --out /tmp/ios-shipguard-preview-redacted
```

## Validation

Focused validation:

```bash
./tests/shipguard_devspace_mcp_test.sh
python3 -m py_compile scripts/shipguard_devspace_mcp.py
```

Plugin validation:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ios-shipguard
```
