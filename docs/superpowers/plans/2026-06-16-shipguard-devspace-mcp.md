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

- Register `ui://widget/shipguard-preview-v2.html`.
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

## Phase 5c: Target Resolution Handoff

- Add structured `targetResolution` metadata to the preview `/api/handoff` payload.
- Add read-only `preview_target_resolution` to Devspace MCP.
- Add read-only `preview_handoff_markdown` to expose the preview's copy-ready `handoff.md` through MCP.
- Prefer the full Markdown handoff in generated Codex handoff prompts, falling back to a compact target-resolution plan when Markdown is unavailable.
- Show target-resolution status in the widget while preserving the no-raw-coordinate-tap boundary.

Proof:

- `./tests/ios_preview_test.sh`
- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/ios_preview.py scripts/shipguard_devspace_mcp.py`

## Phase 5d: UI Snapshot Candidate Matching

- Add `codex-maintainer ios target-match` for ranking XcodeBuildMCP `describe_ui` or `snapshot_ui` JSON against a preview handoff.
- Add read-only `preview_match_target` to Devspace MCP.
- Keep matching advisory: produce candidate `elementRef`, label, role, score, and rationale; never execute simulator input.

Proof:

- `./tests/ios_target_match_test.sh`
- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/ios_target_match.py scripts/shipguard_devspace_mcp.py`

## Phase 5e: Live Widget Refresh

- Make widget-refresh behavior explicit through `render_preview_widget` tool metadata.
- Add bounded widget auto-refresh using `tools/call` / `window.openai.callTool`.
- Preserve manual refresh and pause/unavailable states when the widget is not running inside ChatGPT or another MCP Apps host.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5f: Screenshot Token Containment

- Keep bearer-auth screenshot view-token URLs out of model-visible `structuredContent`.
- Return non-token screenshot proxy paths in structured content and tokenized image URLs in widget-only `_meta`.
- Keep existing screenshot view-token log redaction and image-only scope.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5g: Bearer-Auth Path Scope

- Scope bearer-auth MCP file-write path arguments to the active `previewOut` directory.
- Disable `preview_start.fixtureImage` overrides in bearer-auth HTTP mode; only the trusted local startup `--fixture-image` can provide a fixture.
- Keep loopback-only no-auth local development behavior unchanged.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5h: MCP Server Instructions

- Return server-level `instructions` from `initialize` so ChatGPT and MCP hosts understand the correct preview workflow.
- Include sequencing guidance for start, render, record, target resolution, target matching, and Codex handoff.
- Include safety guidance for semantic `elementRef` matching, no raw coordinate taps, no remote shell behavior, no automatic Codex execution, and no token leakage in prompts.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5i: Production Readiness Report

- Add read-only `production_readiness` MCP tool.
- Report local-only, Developer Mode, and production-hosting status without enabling non-loopback binding.
- Include auth, public HTTPS endpoint, no raw coordinate tap, no automatic Codex execution, screenshot token containment, and path-scope checks.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5j: Widget Resource Versioning

- Version the widget resource URI from `ui://widget/shipguard-preview-v1.html` to `ui://widget/shipguard-preview-v2.html` after the live-refresh, target-resolution, token-containment, and readiness UI changes.
- Derive the HTTP widget route from the widget version constant so tool metadata, resource contents, and direct HTTP serving stay aligned.
- Update docs, plugin guidance, and tests to reference the current cache key.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Phase 5k: Local HTTP Origin Guard

- Reject non-loopback `Host`, `Origin`, and `Referer` headers in unauthenticated local HTTP mode.
- Require JSON content types for `/mcp` POST requests.
- Surface the origin and content-type guards in `production_readiness`.
- Preserve bearer-auth tunneled Developer Mode behavior.

Proof:

- `./tests/shipguard_devspace_mcp_test.sh`
- `python3 -m py_compile scripts/shipguard_devspace_mcp.py`

## Future Phases

- Add production-hosting mode for non-local Devspace after the readiness report's required auth, logging, secret-handling, simulator-access, and hosted-endpoint reviews are complete.
- Add richer UI snapshot capture once XcodeBuildMCP exposes callable tools to this connector context.
- Add redaction of screenshot-derived text if OCR is introduced.
