# Shipguard Devspace MCP Design

## Purpose

Shipguard Devspace turns the iOS preview bridge into a ChatGPT Apps / MCP connector so ChatGPT can see a phone preview widget, record visual events, and prepare a Codex handoff. This addresses the "ChatGPT becomes Codex, sort of" workflow by exposing local preview and planning tools through MCP while keeping code mutation inside Codex and local validation.

## App Archetype

Primary archetype: `interactive-decoupled`.

Data and action tools are separate from the render tool:

- data/action tools: preview start, state, screenshot, event record, handoff, simulator list, goal emit, Codex prompt preparation
- render tool: `render_preview_widget`
- widget resource: `ui://widget/shipguard-preview-v1.html`

This lets ChatGPT inspect preview state before choosing whether to render UI or prepare a Codex handoff.

## Surfaces

HTTP mode:

- `GET /healthz`
- `GET /widget/shipguard-preview-v1.html`
- `GET /preview-screenshot.png`
- `POST /mcp`

HTTP mode accepts optional bearer-token auth through `--bearer-token-env` or `--bearer-token-file`. When bearer auth is enabled, MCP and health routes require `Authorization: Bearer <token>`. Screenshot rendering uses a separate random per-session view token in the image URL because browser image requests cannot attach bearer headers.

stdio mode:

- line-delimited JSON-RPC over stdin/stdout for Codex plugin MCP integration

The plugin sidecar lives at:

```text
plugins/ios-shipguard/.mcp.json
```

## Tools

- `preview_start`
- `preview_stop`
- `preview_state`
- `preview_screenshot`
- `preview_record_event`
- `preview_handoff`
- `render_preview_widget`
- `simulator_list`
- `codex_goal_emit`
- `codex_prepare_handoff`
- `codex-maintainer ios codex-handoff` local CLI supervisor for explicit app-server execution

Every tool has a single intent, JSON-schema-like inputs, and MCP annotations for read-only versus local mutation.

## Widget

The widget renders the screenshot proxy in a phone frame, records a selected point and note, calls `preview_record_event`, refreshes through `render_preview_widget`, and sends a follow-up message for Codex handoff.

The widget resource uses:

```text
text/html;profile=mcp-app
```

It supports the MCP Apps bridge message path and uses `window.openai.callTool` when hosted in ChatGPT.

## Trust Boundary

Devspace is a local bridge, not a general remote shell.

Required invariants:

- HTTP mode binds only to loopback.
- Tunneled HTTP mode requires bearer auth for MCP/tool access.
- MCP request body size is bounded.
- Event payloads are bounded.
- The screenshot view token is scoped to the image proxy and is redacted from server logs.
- No arbitrary shell tool is exposed.
- No raw browser coordinate is treated as a simulator tap.
- Codex app-server is not spawned automatically.
- The separate `ios codex-handoff --execute` local action is required before app-server execution.
- ChatGPT Developer Mode testing uses an HTTPS tunnel but production hosting requires a separate auth and secret review.

## Completion Proof

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`
- plugin validator for `plugins/ios-shipguard`
- docs-check for `docs/shipguard-devspace.md`
- `./tests/ios_codex_handoff_test.sh`
