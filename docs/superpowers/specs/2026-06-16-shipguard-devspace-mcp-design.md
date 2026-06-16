# Shipguard Devspace MCP Design

## Purpose

Shipguard Devspace turns the iOS preview bridge into a ChatGPT Apps / MCP connector so ChatGPT can see a phone preview widget, record visual events, and prepare a Codex handoff. This addresses the "ChatGPT becomes Codex, sort of" workflow by exposing local preview and planning tools through MCP while keeping code mutation inside Codex and local validation.

## App Archetype

Primary archetype: `interactive-decoupled`.

Data and action tools are separate from the render tool:

- data/action tools: preview start, state, screenshot, event record, handoff, simulator list, goal emit, Codex prompt preparation
- render tool: `render_preview_widget`
- widget resource: `ui://widget/shipguard-preview-v2.html`

This lets ChatGPT inspect preview state before choosing whether to render UI or prepare a Codex handoff.

## Surfaces

HTTP mode:

- `GET /healthz`
- `GET /widget/shipguard-preview-v2.html`
- `GET /preview-screenshot.png`
- `POST /mcp`

HTTP mode accepts optional bearer-token auth through `--bearer-token-env` or `--bearer-token-file`. When bearer auth is enabled, MCP and health routes require `Authorization: Bearer <token>`. Screenshot rendering uses a separate random per-session view token in the image URL because browser image requests cannot attach bearer headers. The view-token URL is delivered as widget-only `_meta`; model-visible `structuredContent` keeps only the non-token proxy path and screenshot metadata.

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
- `preview_handoff_markdown`
- `preview_target_resolution`
- `preview_match_target`
- `render_preview_widget`
- `simulator_list`
- `production_readiness`
- `codex_goal_emit`
- `codex_prepare_handoff`
- `codex-maintainer ios codex-handoff` local CLI supervisor for explicit app-server execution

Every tool has a single intent, JSON-schema-like inputs, and MCP annotations for read-only versus local mutation. Tool descriptors expose `_meta.ui.visibility = ["model", "app"]`; only the widget-called tools opt into the OpenAI compatibility `openai/widgetAccessible` field. `preview_handoff_markdown` is read-only and returns the active preview's copy-ready `handoff.md` for Codex. `preview_target_resolution` is read-only and returns the structured mapping plan from the latest visual event to either source editing or a semantic XcodeBuildMCP `elementRef`; it never performs simulator input. `preview_match_target` is also read-only: it ranks `describe_ui` or `snapshot_ui` candidates for review without tapping.

The MCP `initialize` response returns server-level instructions that describe the expected start, render, record, Markdown handoff, target-resolution, target-match, production-readiness, and Codex handoff sequence. The instructions also restate core safety boundaries: no raw coordinate taps, semantic `elementRef` matching before touch, no arbitrary shell behavior, no automatic Codex execution, and no token leakage in prompts or notes.

`production_readiness` is a read-only report, not a production-mode switch. It keeps Devspace local-first while giving hosts a machine-readable distinction between local-only, Developer Mode tunnel readiness, and production hosting blockers.

HTTP mode keeps the unauthenticated local path usable for Codex while rejecting browser-origin footguns: no-auth requests must use loopback `Host`, `Origin`, and `Referer` headers, and `/mcp` POSTs must use a JSON content type. Tunneled Developer Mode remains bearer-authenticated.

## Widget

The widget renders the screenshot proxy in a phone frame, records a selected point and note, calls `preview_record_event`, refreshes through `render_preview_widget`, shows target-resolution status, and sends a follow-up message for Codex handoff. Live refresh is a bounded widget loop over the read-only render tool, with manual refresh and pause/unavailable states when the widget is not running inside ChatGPT or another MCP Apps host.

The widget resource uses:

```text
text/html;profile=mcp-app
```

Widget resource URIs are cache keys. Current widget markup is served as `ui://widget/shipguard-preview-v2.html`; future breaking HTML, CSS, or JavaScript changes should bump the version and update `_meta.ui.resourceUri`, `openai/outputTemplate`, `contents[].uri`, docs, and tests together.

It supports the MCP Apps bridge message path and uses `window.openai.callTool` when hosted in ChatGPT.

## Trust Boundary

Devspace is a local bridge, not a general remote shell.

Required invariants:

- HTTP mode binds only to loopback.
- Tunneled HTTP mode requires bearer auth for MCP/tool access.
- Unauthenticated local HTTP mode rejects non-loopback `Host`, `Origin`, and `Referer` headers.
- `/mcp` accepts JSON POST bodies only.
- MCP request body size is bounded.
- Event payloads are bounded.
- The screenshot view token is scoped to the image proxy and is redacted from server logs.
- Screenshot view-token URLs stay out of model-visible `structuredContent`.
- In bearer-auth HTTP mode, MCP file-write path arguments are scoped to the active `previewOut` directory and `preview_start.fixtureImage` overrides are disabled.
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
