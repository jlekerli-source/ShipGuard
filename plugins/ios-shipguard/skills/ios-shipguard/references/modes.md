# iOS Shipguard Modes

Use this reference when a task touches multiple iOS trust surfaces or when the primary proof path is unclear.

## permission-audit

Use for Info.plist usage descriptions, entitlements, authorization state, onboarding permission copy, settings copy, and denied-state behavior.

Ask:

- What user-visible feature needs this permission?
- Which authorization states must be supported?
- What does the app do when permission is denied, limited, provisional, or unavailable?

Proof:

- `codex-maintainer ios inventory`
- focused source diff
- simulator permission-state walkthrough when UI copy changes

## simulator-debug

Use for visible bugs, navigation regressions, layout defects, crashes, hangs, and flows that require tapping through Simulator.

Ask:

- What is the exact expected behavior?
- What is the exact observed failure?
- Which device, iOS version, account state, or seed data is required?

Proof:

- XcodeBuildMCP project/scheme/simulator selection
- build and launch
- UI hierarchy, screenshot, logs, or LLDB evidence
- rerun of the reproduction path after the fix

## release-proof

Use for release readiness, TestFlight, App Store review, proof packets, privacy-sensitive claims, and final merge/shipping gates.

Ask:

- Which binary, version, build, and commit are being proven?
- Which claims require TestFlight, App Store Connect, physical device, or human tester evidence?
- Which local proof is insufficient?

Proof:

- explicit source commit and build identity
- local validation logs
- device/TestFlight/App Store evidence when required
- blocked-manual note when credentials or device access are missing

## storekit-commerce

Use for paid access, subscriptions, restore, product IDs, introductory offers, entitlement caching, receipt state, and premium copy.

Ask:

- Which product IDs and entitlement states are in scope?
- Is the proof sandbox, StoreKit config, TestFlight sandbox, or live App Store?
- What happens on restore, downgrade, expiration, billing retry, and offline launch?

Proof:

- product mapping check
- entitlement-state source/test proof
- sandbox or live-account evidence for purchase claims

## widgets-intents-shared-store

Use for WidgetKit, App Intents, Shortcuts, Spotlight, app groups, shared persistence, watch surfaces, and extension data consistency.

Ask:

- Which target writes the data and which targets read it?
- What stale-data behavior is acceptable?
- Is there a migration or compatibility concern for existing users?

Proof:

- shared container and entitlement review
- app plus extension state checks
- migration rehearsal when payload shape changes

## preview-bridge

Use when the user wants an in-Codex visual preview loop for the current iOS Simulator screen, browser comments on a phone-shaped preview, or click/note receipts that should guide a SwiftUI edit.

Ask:

- Which simulator, scheme, and app state should be previewed?
- Is the requested feedback a visual edit, a navigation/tap reproduction, or a release-proof claim?
- Should the preview use live `simctl` screenshots or fixture mode for docs/tests?

Proof:

- `codex-maintainer ios preview --out /tmp/ios-shipguard-preview`
- Codex in-app browser opened to the printed localhost URL
- `preview-events.jsonl` receipt when the user clicks or notes a target
- `/api/handoff` payload read before choosing the next Codex or XcodeBuildMCP action
- XcodeBuildMCP `snapshot_ui` plus semantic `touch` elementRefs, UI test, or manual simulator proof for real taps; the preview bridge records visual intent and handoff guidance

## preview-devspace

Use when the user wants ChatGPT, GPT-5.5 Pro, or another MCP Apps-compatible host to see the iOS preview widget, record visual events, and prepare a Codex handoff through MCP tools.

Ask:

- Should Devspace attach to an existing `ios preview` URL or start one?
- Is this local Developer Mode testing, a Codex plugin MCP run, or production hosting research?
- Should `codex_prepare_handoff` write a prompt file, or should the user manually paste the handoff into Codex?

Proof:

- `codex-maintainer ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview`
- `/mcp` responds to `initialize`, `tools/list`, and `resources/read`
- `render_preview_widget` returns `ui://widget/shipguard-preview-v1.html`
- left-click and right-click context menu `preview_record_event` receipts appear in `preview-events.jsonl`
- `codex_prepare_handoff` produces a scoped Codex prompt
- `codex-maintainer ios codex-handoff --prompt-file <file> --out <dir>` prepares the trusted app-server handoff bundle when execution should move from ChatGPT planning into Codex
- actual code edits still require Codex validation, XcodeBuildMCP, UI tests, or manual simulator proof

Notes:

- Devspace is not a remote shell. Do not add arbitrary command tools.
- ChatGPT Developer Mode should connect through an HTTPS tunnel for local testing, with Devspace started using `--bearer-token-env` or `--bearer-token-file`.
- When bearer auth is enabled, MCP/tool routes require `Authorization: Bearer <token>` and the screenshot image uses a separate random per-session view token.
- The connector does not spawn Codex app-server automatically; use `ios codex-handoff --execute` only from a trusted local terminal.

## ui-polish

Use for SwiftUI layout, copy, accessibility, Dynamic Type, localization, onboarding, settings, and product surface polish.

Ask:

- What user job should this screen make easier?
- Which compact, Dynamic Type, localization, denied, empty, loading, and failure states apply?
- Is any copy making a trust, alarm, privacy, or paid-access claim?

Proof:

- focused UI test or simulator screenshot
- accessibility label/identifier review when interactions change
- localization/Dynamic Type check when text or layout changes
