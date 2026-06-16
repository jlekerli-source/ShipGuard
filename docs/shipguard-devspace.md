# Shipguard Devspace

`codex-maintainer ios devspace` turns the local iOS preview bridge into a ChatGPT Apps / MCP connector surface. It is the path for using ChatGPT as the planning and visual feedback layer while Codex remains the local implementation and proof agent.

## Architecture

```text
ChatGPT Developer Mode
  -> Shipguard Devspace /mcp
  -> phone preview widget
  -> ios preview bridge
  -> Xcode Simulator screenshot and event receipts
  -> Codex handoff prompt
```

The Devspace connector has two run modes:

- HTTP mode for ChatGPT Developer Mode and widget rendering.
- stdio mode for the `ios-shipguard` Codex plugin MCP sidecar.

The app archetype is `interactive-decoupled`: data/action tools stay separate from the render tool so ChatGPT can reason about preview state before showing the widget.

## Start HTTP Mode

Start the Devspace MCP endpoint:

```bash
./bin/codex-maintainer ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview
```

For deterministic testing without a booted simulator:

```bash
./bin/codex-maintainer ios devspace \
  --port 8787 \
  --fixture-image path/to/screenshot.png \
  --preview-out /tmp/ios-shipguard-preview
```

When exposing Devspace through an HTTPS tunnel, require a bearer token:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"

./bin/codex-maintainer ios devspace \
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

HTTP mode binds to loopback only. To connect ChatGPT Developer Mode, expose the endpoint with an HTTPS tunnel and use the tunneled URL plus `/mcp`.

## ChatGPT Developer Mode

1. Start `ios devspace` locally.
2. Expose the local port with an HTTPS tunnel.
3. In ChatGPT, enable Developer Mode under Apps and Connectors advanced settings.
4. Create a new app from the tunneled MCP URL.
5. Ask ChatGPT to call `preview_start`, then `render_preview_widget`.
6. Right-click a point in the phone preview to choose a typed action such as tap, copy change, visual fix, or inspection.

Useful prompt:

```text
Use the Shipguard Devspace app. Start the iOS preview, render the phone widget, and wait for my visual event before preparing a Codex handoff.
```

Refresh or reconnect the ChatGPT app after changing tool descriptors, widget HTML, or resource metadata.

## MCP Tools

| Tool | Purpose | Mutates local state |
| --- | --- | --- |
| `preview_start` | Start or attach to `codex-maintainer ios preview` | Yes |
| `preview_stop` | Stop the preview process started by Devspace | Yes |
| `preview_state` | Read Devspace and preview state | No |
| `preview_screenshot` | Capture screenshot metadata and proxy URL | No |
| `preview_record_event` | Record click, note, navigation, visual-bug, or copy-change intent | Yes |
| `preview_handoff` | Read the latest Codex/XcodeBuildMCP handoff payload | No |
| `render_preview_widget` | Return the widget template and current preview data | No |
| `simulator_list` | List local iOS Simulator devices from `simctl` | No |
| `codex_goal_emit` | Emit a Shipguard slash-goal from the local catalog | No |
| `codex_prepare_handoff` | Prepare a Codex app-server turn prompt, optionally writing it and supervisor artifacts locally | Yes |

The widget resource URI is:

```text
ui://widget/shipguard-preview-v1.html
```

It is served as:

```text
text/html;profile=mcp-app
```

The widget uses the MCP Apps bridge for tool results and `window.openai.callTool` when available for ChatGPT-hosted button actions. A right-click in the phone preview opens an in-widget context menu that records bounded event metadata: `source`, `action`, `contextLabel`, coordinates, and the user's note.

## Codex Handoff

`codex_prepare_handoff` prepares the prompt that should be sent into Codex. It does not spawn Codex automatically. That guard is intentional: Codex app-server execution should run through a trusted local supervisor or explicit user action because it can edit code and run tools.

The handoff path is:

```text
preview event -> preview_handoff -> codex_prepare_handoff -> Codex turn -> validation proof
```

When a `tap-request` or `navigate-request` exists, the handoff instructs Codex to use XcodeBuildMCP `snapshot_ui`, map the visual event to a semantic `elementRef`, then use `touch` only after the target is identified. Copy and visual-fix context events route to source-code edits and preview proof instead of simulator taps.

## Codex Handoff Supervisor

For an explicit local app-server handoff, prepare a supervisor bundle:

```bash
./bin/codex-maintainer ios codex-handoff \
  --prompt-file /tmp/ios-shipguard-preview/codex-handoff.md \
  --out /tmp/ios-shipguard-preview/codex-supervisor
```

This writes:

- `codex-handoff-prompt.md`
- `codex-app-server-plan.json`
- `codex-app-server-messages.jsonl`

To actually start `codex app-server`, add `--execute` yourself from a trusted local terminal:

```bash
./bin/codex-maintainer ios codex-handoff \
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

In this repository's local plugin layout, the MCP server runs from the repository root so it can call `bin/codex-maintainer`.

## Security Boundary

- HTTP mode rejects non-loopback hosts.
- HTTP mode can require `Authorization: Bearer <token>` through `--bearer-token-env` or `--bearer-token-file`.
- MCP request bodies are size-limited.
- Preview event payloads are bounded and schema-like.
- The connector does not expose arbitrary shell execution.
- The connector does not treat browser click coordinates as simulator taps.
- The context menu records typed visual intent; it does not execute Codex or Xcode actions.
- The connector does not spawn Codex app-server automatically.
- `ios codex-handoff --execute` is a separate local terminal action and records a transcript.
- When bearer auth is enabled, the screenshot proxy URL includes a random per-session view token because browser `<img>` requests cannot attach an Authorization header. That token can only fetch the current screenshot proxy; it cannot call MCP tools.
- Use HTTPS tunneling only for local Developer Mode testing; production hosting needs its own auth, logging, and secret-handling review.

Do not paste secrets into preview notes. Treat screenshots and event receipts as local planning evidence, not release proof.

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
