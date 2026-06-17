# iOS ShipGuard Modes

Use this reference when a task touches multiple iOS trust surfaces or when the primary proof path is unclear.

The `shipguard ios ...` proof commands are part of this ShipGuard checkout. If a target app repo only copied starter files and does not include the ShipGuard CLI, run the commands from a ShipGuard checkout against that target path, or fall back to source inspection, XcodeBuildMCP, existing project tests, and explicit manual blockers.

## permission-audit

Use for Info.plist usage descriptions, entitlements, authorization state, onboarding permission copy, settings copy, and denied-state behavior.

Ask:

- What user-visible feature needs this permission?
- Which authorization states must be supported?
- What does the app do when permission is denied, limited, provisional, or unavailable?

Proof:

- `shipguard ios inventory`
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

## performance-audit

Use for FPS drops, animation hitches, scroll or launch stutter, slow tab switches, touch latency, thermal pressure, high CPU/GPU suspicion, and device-specific smoothness problems.

Ask:

- Which screen, gesture, launch path, or device behavior feels slow?
- Which device, display refresh rate, thermal state, Low Power Mode, build configuration, seed data, and route should be measured?
- Is the claim app-side only, or does it involve physical hardware such as replacement displays, touch, ProMotion, sensors, audio, or wake timing?

Proof:

- `shipguard ios performance --path . --out <dir>` for ranked source hotspots before choosing edits
- Add `--shipguard-eval` to `shipguard ios performance`, `shipguard ios design`, `shipguard ios modernize`, `shipguard ios app-intelligence`, or `shipguard ios ai-readiness` when a private app is only a read-only sample for improving ShipGuard itself
- XcodeBuildMCP project/scheme/simulator selection before build/run
- build and launch the same route being measured
- Animation Hitches or Time Profiler trace when the simulator/device supports it
- fallback `sample`, `top`, logs, screenshots, and symbolicated app frames when xctrace is unavailable or hangs
- source audit for continuous redraw, expensive body work, formatter/image decoding, large blur/shadow/material layers, main-actor blocking work, and protected-runtime boundaries
- before/after comparison using the same build configuration, seed data, route, and device state
- physical-device Instruments trace before claiming 10/10 smoothness, touch latency, ProMotion behavior, thermal behavior, display-specific behavior, sensors, audio, or wake-path timing

## ShipGuard product QA

Use when Ringly, Ilmify, or another private app is only a read-only sample for improving ShipGuard itself.

Ask:

- Which ShipGuard report is being judged: performance, design, modernization, app intelligence, or AI readiness?
- Is the target app explicitly out of scope for edits and remediation planning?
- Which noisy, generic, missing, or hard-to-act-on report behavior should become a public fixture or eval case?

Proof:

- Run the selected command with `--shipguard-eval`: `shipguard ios performance`, `shipguard ios design`, `shipguard ios modernize`, `shipguard ios app-intelligence`, or `shipguard ios ai-readiness`
- Run `shipguard ios report-quality --reports <eval-output-dir> --out <quality-dir>` to grade ShipGuard report usefulness, not target-app quality
- If report-quality emits token/path shareability findings, run the generated `shipguard ios redact` command before moving artifacts into ChatGPT, GitHub, docs, or release evidence
- Keep generated private-app reports local unless the user approves redaction and sharing
- Convert useful observations into ShipGuard rules, report shape, docs, or public fixtures only
- Do not edit the scanned app or present its findings as the active app-work target

## design-audit

Use for UI/UX coherence, app-type fit, motion, haptics, visual DNA, app icon direction, preview routing, and design proof planning.

Ask:

- Is the inferred app type correct, or should `--app-type` override it?
- Is the work about design evaluation, app icon direction, motion/haptics, or implementation?
- Is there an existing `ios preview` output directory or should the preview be started first?

Proof:

- `shipguard ios design --path . --out /tmp/ios-shipguard-design`
- Add `--app-type <type>` when the app genre is known or the inference is wrong
- Add `--preview-out <dir>` when phone-shaped preview receipts already exist
- Add `--icon-brief` when app icon direction is in scope, then use ChatGPT ImageGen for bitmap candidates
- `shipguard ios preview --out /tmp/ios-shipguard-preview` for phone-shaped visual proof
- `shipguard ios devspace-check --path . --preview-out /tmp/ios-shipguard-preview --out /tmp/ios-shipguard-devspace-check` before judging connector readiness or sharing a tunneled endpoint
- `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN` when ChatGPT should plan from the preview widget; model choice happens in ChatGPT, not ShipGuard
- physical-device proof before claiming haptic quality
- do not treat local CSS, SVG, or placeholder drawings as production app icon output

## preview-bridge

Use when the user wants an in-Codex visual preview loop for the current iOS Simulator screen, browser comments on a phone-shaped preview, or typed click/right-click/note receipts that should guide a SwiftUI edit.

Ask:

- Which simulator, scheme, and app state should be previewed?
- Is the requested feedback a visual edit, a navigation/tap reproduction, or a release-proof claim?
- Should the preview use live `simctl` screenshots or fixture mode for docs/tests?

Proof:

- `shipguard ios preview --out /tmp/ios-shipguard-preview`
- Codex in-app browser opened to the printed localhost URL
- `preview-events.jsonl` receipt when the user clicks, right-clicks a typed context-menu action, or notes a target
- `handoff.md` or `/api/handoff.md` payload read before choosing the next Codex or XcodeBuildMCP action, including `targetResolution.rawCoordinateTapAllowed: false`
- `shipguard ios target-match --handoff <handoff.json> --snapshot <ui.json> --out <dir>` when an XcodeBuildMCP UI JSON snapshot is available
- XcodeBuildMCP `snapshot_ui` plus semantic `touch` elementRefs, UI test, or manual simulator proof for real taps; the preview bridge records visual intent and handoff guidance

## preview-devspace

Use when the user wants ChatGPT, GPT-5.5 Pro, or another MCP Apps-compatible host to see the iOS preview widget, record visual events, and prepare a Codex handoff through MCP tools.

Ask:

- Should Devspace attach to an existing `ios preview` URL or start one?
- Is this local Developer Mode testing, a Codex plugin MCP run, or production hosting research?
- Should `codex_prepare_handoff` write a prompt file, or should the user manually paste the handoff into Codex?

Proof:

- `shipguard ios devspace-check --path . --preview-out /tmp/ios-shipguard-preview --out /tmp/ios-shipguard-devspace-check` records loopback, auth, widget, preview, redaction, handoff, and model-boundary readiness before tunneled use
- `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview`
- `/mcp` responds to `initialize`, `tools/list`, and `resources/read`
- `render_preview_widget` returns `ui://widget/shipguard-preview-v2.html`
- left-click and right-click context menu `preview_record_event` receipts appear in `preview-events.jsonl`
- `preview_handoff_markdown` returns the active preview's copy-ready `handoff.md`
- `preview_target_resolution` returns structured source-edit or semantic `elementRef` guidance for the latest event
- `preview_match_target` ranks XcodeBuildMCP `describe_ui` or `snapshot_ui` elements without performing simulator input
- `production_readiness` reports Developer Mode readiness and production-hosting blockers before non-local exposure is discussed
- `codex_prepare_handoff` produces a scoped Codex prompt from the Markdown handoff when available
- `shipguard ios codex-handoff --prompt-file <file> --out <dir>` prepares the trusted app-server handoff bundle when execution should move from ChatGPT planning into Codex
- `shipguard ios modernize --focus swift --path . --out <dir>` records Swift concurrency, SwiftUI, Observation, accessibility/localization, and availability fallback findings before modernization work
- `shipguard ios plan --mode <mode> --inventory <ios-inventory.json> --out <file-or-dir>` turns inventory into owner files, blocked questions, target summary, proof route, and a Codex-ready brief
- `shipguard ios prove --plan <ios-plan.json> --out <dir>` records the smallest honest proof lane and manual blockers before proof claims
- `shipguard ios app-intelligence --path . --out <dir>` records App Intent, AppEntity, Shortcuts, Siri, Spotlight, widget, controls, Apple Intelligence, and privacy-readiness gaps before system exposure work
- `shipguard ios ai-readiness --path . --out <dir>` records Foundation Models, Core AI, Core ML, OpenAI API, no-AI, privacy, latency, cost, and fallback tradeoffs before model work
- `shipguard ios redact --in <file-or-dir> --out <file-or-dir>` redacts local paths, Apple team IDs, bundle IDs, tokens, accounts, emails, device IDs, and private terms before reports leave local proof space
- `shipguard ios eval --cases evals/ios_shipguard_cases.jsonl --out <dir>` grades mode routing, missing-question handling, proof honesty, and Codex brief quality before plugin guidance changes
- `shipguard ios demo --out <dir>` proves the clean static first-run path with doctor, inventory, plan, proof, modernization, intelligence, AI readiness, eval, and redaction reports
- actual code edits still require Codex validation, XcodeBuildMCP, UI tests, or manual simulator proof

Notes:

- Devspace is not a remote shell. Do not add arbitrary command tools.
- ChatGPT Developer Mode should connect through an HTTPS tunnel for local testing, with Devspace started using `--bearer-token-env` or `--bearer-token-file`.
- When bearer auth is enabled, MCP/tool routes require `Authorization: Bearer <token>` and the screenshot image uses a separate random per-session view token.
- The connector does not spawn Codex app-server automatically; use `ios codex-handoff --execute` only from a trusted local terminal.
- Treat screenshots and preview receipts as local planning evidence. Run `ios redact` for text reports and keep binary screenshots local unless the user explicitly approves sharing.

## privacy-security

Use when ShipGuard artifacts, screenshots, logs, preview receipts, App Store identifiers, team IDs, bundle IDs, tokens, local paths, or reports may leave local proof space.

Ask:

- Which private terms must be redacted before this report is shared?
- Are screenshots allowed to be shared, or should only redacted text reports leave the machine?
- Is this local-only Developer Mode testing, public issue evidence, benchmark data, or release evidence?

Proof:

- `shipguard ios redact --in <file-or-dir> --out <file-or-dir>`
- `ios-redaction.json` with `status: pass` and `remainingRiskCount: 0`
- screenshot sharing approval or explicit local-only note
- Devspace bearer auth and loopback/tunnel boundary review when MCP is involved

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
