# Shipguard Devspace MCP Implementation Plan

## Goal

Build the first working Shipguard Devspace connector: an MCP/App bridge that exposes the iOS preview bridge to ChatGPT Developer Mode and the iOS Shipguard Codex plugin.

## Phase 1: Connector Core

- Add `scripts/shipguard_devspace_mcp.py`.
- Support HTTP `/mcp` and stdio JSON-RPC.
- Implement `initialize`, `tools/list`, `tools/call`, `resources/list`, and `resources/read`.
- Keep the implementation dependency-light and Python stdlib only.

Proof:

- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`
- stdio smoke request for `tools/list`

## Phase 2: Preview Tooling

- Implement `preview_start`, `preview_stop`, `preview_state`, `preview_screenshot`, `preview_record_event`, and `preview_handoff`.
- Start `codex-maintainer ios preview` as a child process only through `preview_start`.
- Proxy screenshots through `/preview-screenshot.png`.
- Preserve loopback-only and bounded event behavior.

Proof:

- fixture-mode MCP test starts preview and records a tap request

## Phase 3: Widget Resource

- Register `ui://widget/shipguard-preview-v1.html`.
- Serve widget HTML as `text/html;profile=mcp-app`.
- Include MCP Apps bridge behavior, ChatGPT `window.openai.callTool` compatibility, and follow-up handoff messaging.

Proof:

- `resources/read` returns the widget resource and expected metadata
- `render_preview_widget` returns `_meta.ui.resourceUri`

## Phase 4: Codex Handoff

- Implement `codex_goal_emit`.
- Implement `codex_prepare_handoff`.
- Do not spawn Codex app-server automatically.
- Document trusted-supervisor requirements for future app-server execution.

Proof:

- test emits a slash-goal
- test writes a prompt file from the latest preview handoff

## Phase 4b: Trusted Local Supervisor

- Add `codex-maintainer ios codex-handoff`.
- Default to prepared artifacts only: prompt file, app-server request plan, and JSONL message template.
- Require explicit local `--execute` before starting `codex app-server`.
- Record an app-server transcript when execution is enabled.

Proof:

- `./tests/ios_codex_handoff_test.sh`
- `./tests/shipguard_devspace_mcp_test.sh`

## Phase 5: Plugin And Docs

- Add `plugins/ios-shipguard/.mcp.json`.
- Add `mcpServers` to plugin manifest.
- Add `preview-devspace` mode to the skill.
- Add `docs/shipguard-devspace.md`.
- Link docs from README, CLI, command matrix, iOS preview, and iOS Shipguard guide.

Proof:

- plugin validator
- docs-check
- package release test

## Phase 5b: HTTP Auth Hardening

- Add optional bearer-token auth for HTTP mode through `--bearer-token-env` and `--bearer-token-file`.
- Reject bearer-token flags in stdio mode.
- Keep widget screenshot rendering viable with a random per-session view token scoped to `/preview-screenshot.png`.
- Redact the screenshot view token from server logs.

Proof:

- authenticated HTTP path in `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Future Phases

- Add production-hosting mode for non-local Devspace.
- Add UI snapshot target resolution helpers once XcodeBuildMCP exposes callable tools to this connector context.
- Add redaction of screenshot-derived text if OCR is introduced.
