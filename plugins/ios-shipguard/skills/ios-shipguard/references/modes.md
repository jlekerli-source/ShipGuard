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

## brand-audit

Use when the user asks to rename ShipGuard surfaces, make the tool more vibey/funny/techy, clean up stale public wording, or keep future feature names coherent.

Ask:

- Is this only ShipGuard product naming, or should any target app code be renamed too?
- Should stable CLI command names remain script-safe while report/docs surfaces get branded names?
- Which new or renamed surface needs a plain-purpose and proof-boundary line?

Proof:

- `shipguard brand --path . --out /tmp/shipguard-brand --strict`
- active docs and skill guidance mention the branded surface names
- focused test such as `tests/ios_branding_test.sh`
- package, self-audit, CLI smoke, and docs-check coverage before claiming the naming scheme is complete
- do not rename stable public commands only for flavor; keep automation-safe commands and put personality in surface names, report headings, section labels, docs, and aliases

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

- `shipguard ios launchdeck --path . --workflow performance --out /tmp/ios-shipguard-launchdeck` to choose the LaunchDeck profiler route before tracing
- `shipguard ios performance --path . --out <dir>` for ranked source hotspots before choosing edits; add `--shareable` before report-quality scoring or external planning
- Add `--shipguard-eval` to `shipguard ios performance`, `shipguard ios design`, `shipguard ios modernize`, `shipguard ios app-intelligence`, or `shipguard ios ai-readiness` when a private app is only a read-only sample for improving ShipGuard itself; add `--shareable` to any report that will be scored or shared
- XcodeBuildMCP project/scheme/simulator selection before build/run
- build and launch the same route being measured
- Animation Hitches or Time Profiler trace when the simulator/device supports it
- fallback `sample`, `top`, logs, screenshots, and symbolicated app frames when xctrace is unavailable or hangs
- source audit for continuous redraw, expensive body work, formatter/image decoding, large blur/shadow/material layers, main-actor blocking work, and protected-runtime boundaries
- before/after comparison using the same build configuration, seed data, route, and device state
- physical-device Instruments trace before claiming 10/10 smoothness, touch latency, ProMotion behavior, thermal behavior, display-specific behavior, sensors, audio, or wake-path timing

## launchdeck

Use when the user wants ShipGuard to be the front door for building, running, debugging, previewing, or investigating an iOS repo with the LaunchDeck surface.

Ask:

- Is the desired lane build/run, debugger/log investigation, live simulator browser preview, SwiftUI preview hot reload, or performance profiling?
- Which scheme, simulator, app state, or route should be used if the repo exposes more than one option?
- Is this app work, or is the target app only a read-only sample for judging ShipGuard output quality?

Proof:

- `shipguard ios launchdeck --path . --out /tmp/ios-shipguard-launchdeck`
- Add `--workflow build-run`, `--workflow debug`, `--workflow preview`, or `--workflow performance` when the lane is known.
- After Codex executes the LaunchDeck route or XcodeBuildMCP tools, rerun `shipguard ios launchdeck --path . --workflow <lane> --receipt <proof-file-or-dir> --out /tmp/ios-shipguard-launchdeck-receipts` so ShipGuard grades receipt completeness.
- Add `--shipguard-eval --shareable` when a private app is only product-QA evidence for improving ShipGuard.
- Use the report's XcodeBuildMCP section before calling `session_show_defaults`, `session_set_defaults`, and `build_run_sim`.
- Use the report's simulator browser or SwiftUI preview hot reload section before launching `serve-sim` or `swiftui-preview-browser.mjs`.
- Use the report's performance profiling section before recording Animation Hitches, Time Profiler, sample/log fallback evidence, or physical-device traces.
- Run `shipguard ios report-quality --reports <launchdeck-report-dir> --out <quality-dir> --shareable` when judging whether LaunchDeck itself is useful.
- ShipGuard owns routing, proof boundaries, shareability, and report quality; Codex iOS execution tools perform actual simulator/debugger/browser/profiler execution inside Codex.
- Do not claim the CLI performed a simulator build, debug session, preview loop, or profiler capture unless the corresponding LaunchDeck or XcodeBuildMCP proof actually ran and was attached as a receipt.

## shipyard-value-audit

Use when the user asks to test every ShipGuard skill, plugin, command, GitHub Action, doc, package path, or named surface and upgrade anything that is only decorative.

Ask:

- Is this a ShipGuard-only product QA pass, or is any target app explicitly authorized for edits?
- Should the gauntlet result become a release blocker, a prioritized backlog, or a scoped next-goal handoff?

Proof:

- `shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet` to grade command wiring, docs, tests, package proof, self-audit coverage, skills, plugin metadata, actions, proof boundaries, runtime receipts, adoption receipts, and fresh target-onboarding receipts
- `shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable` to score the gauntlet report itself and surface prioritized actionability questions
- focused tests for any upgraded surface, plus `tests/tool_value_gauntlet_test.sh`, self-audit, package proof, docs-check, and plugin status before claiming the ShipYard is stronger
- do not use Ringly, Ilmify, or another private app as the implementation target unless a later task explicitly authorizes app work

## ShipGuard product QA

Use when Ringly, Ilmify, or another private app is only a read-only sample for improving ShipGuard itself.

Ask:

- Which ShipGuard report is being judged: performance, design, modernization, app intelligence, or AI readiness?
- Is the target app explicitly out of scope for edits and remediation planning?
- Which noisy, generic, missing, or hard-to-act-on report behavior should become a public fixture or eval case?

Proof:

- Run the selected command with `--shipguard-eval` and `--shareable` before the report leaves local proof space.
- Run `shipguard ios report-quality --reports <eval-output-dir> --out <quality-dir> --shareable` to grade ShipGuard report usefulness, not target-app quality.
- Use `priorityAction` and prioritized Actionability Questions to choose the next ShipGuard rule, fixture, report section, docs improvement, or spec workflow.
- Run `shipguard ios spec-workflow --from-report <quality-dir> --shipguard-eval --shareable` when those questions need to become proof-gated ShipGuard implementation work.
- If report-quality flags missing impact, severity reason, proof boundary, grouping, shareability, redaction, or spec-workflow coverage, improve ShipGuard output shape or regeneration logic instead of turning scanned-app findings into app work.
- Keep generated private-app reports local unless the user approves redaction and sharing.
- Convert useful observations into ShipGuard rules, report shape, docs, or public fixtures only.
- Do not edit the scanned app or present its findings as the active app-work target.

## external-source-audit

Use when the user points ShipGuard at Spec Kit, CodexPro, Expo, Design Motion Principles, X posts, plugins, skills, or another workflow/tooling project and asks to integrate it into ShipGuard.

Ask:

- Is the external source available as a local read-only checkout, a public URL, or only a post/screenshot?
- Which ShipGuard surface should this influence: CLI command, report-quality gate, Devspace, spec workflow, plugin skill guidance, docs, fixtures, or release/package proof?
- Does the user want native adaptation only, or have they explicitly approved vendoring with license/package review?

Proof:

- Run `shipguard ios external-audit --path <shipguard-repo> --source-path <external-checkout> --source-url <url> --out <dir> --shareable` when local source or URLs are available.
- Treat `replacement-ledger.md` as the adoption contract: a source is not integrated until each claimed capability has a decision, native action, and validation command.
- Run `shipguard ios report-quality --reports <external-audit-dir> --out <quality-dir> --shareable`.
- Run `shipguard ios spec-workflow --from-report <quality-dir> --shipguard-eval --shareable` before implementing replacement work from that audit.
- Keep the default path as native ShipGuard implementation. Do not copy external code, templates, assets, or docs unless a separate license and packaging decision explicitly approves it.
- For X/social posts, capture them as source URLs and convert the idea into a public fixture or ShipGuard report-quality question before implementation; do not rely on a post alone as proof.

## design-audit

Use for UI/UX coherence, app-type fit, ShipGuard-native motion quality gates, haptics, visual DNA, app icon direction, preview routing, and design proof planning.

Ask:

- Is the inferred app type correct, or should `--app-type` override it?
- Is the work about design evaluation, app icon direction, motion/haptics, or implementation?
- Is there an existing `ios preview` output directory or should the preview be started first?

Proof:

- `shipguard ios design --path . --out /tmp/ios-shipguard-design`
- Add `--app-type <type>` when the app genre is known or the inference is wrong
- Add `--preview-out <dir>` when phone-shaped preview receipts already exist
- Add `--icon-brief` when app icon direction is in scope, then use ChatGPT ImageGen for bitmap candidates
- Check `motionQualityGates` before approving animation, especially frequency, keyboard-triggered actions, Reduce Motion, AI-slop, continuous animation, and device/profiler proof
- Add `--shareable` when design reports will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring
- `shipguard ios preview --out /tmp/ios-shipguard-preview` for phone-shaped visual proof
- `shipguard ios devspace-check --path . --preview-out /tmp/ios-shipguard-preview --shareable --out /tmp/ios-shipguard-devspace-check` before judging connector readiness or sharing a tunneled endpoint
- `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN` when ChatGPT should plan from the preview widget; model choice happens in ChatGPT, not ShipGuard
- physical-device proof before claiming haptic quality
- do not treat local CSS, SVG, or placeholder drawings as production app icon output

## preview-bridge

Use when the user wants an in-Codex visual preview loop for the current iOS Simulator screen, browser comments on a phone-shaped preview, or typed click/right-click/note receipts that should guide a SwiftUI edit.

If the LaunchDeck `ios-simulator-browser` skill is available, prefer it for live Simulator mirroring, SwiftUI preview rendering, and package-backed hot reload. Use ShipGuard preview after that when the task needs typed receipts, target-resolution handoff, redaction, report-quality evidence, or a ChatGPT/Codex handoff. The two loops are complementary: LaunchDeck is the fast visual renderer, ShipGuard is the proof and workflow guard.

Ask:

- Which simulator, scheme, and app state should be previewed?
- Is the requested feedback a visual edit, a navigation/tap reproduction, or a release-proof claim?
- Should the preview use live `simctl` screenshots or fixture mode for docs/tests?

Proof:

- `shipguard ios launchdeck --path . --workflow preview --out /tmp/ios-shipguard-launchdeck` when choosing between app build, simulator browser, and SwiftUI preview hot reload
- LaunchDeck `serve-sim` browser proof or SwiftUI preview hot reload proof when that skill is available and live rendering is the goal
- `shipguard ios preview --out /tmp/ios-shipguard-preview`
- Codex in-app browser opened to the printed localhost URL
- `preview-events.jsonl` receipt when the user clicks, right-clicks a typed context-menu action, or notes a target
- `handoff.md` or `/api/handoff.md` payload read before choosing the next Codex or XcodeBuildMCP action, including `targetResolution.rawCoordinateTapAllowed: false`
- `shipguard ios target-match --handoff <handoff.json> --snapshot <ui.json> --out <dir>` when an XcodeBuildMCP UI JSON snapshot is available
- XcodeBuildMCP `snapshot_ui` plus semantic `touch` elementRefs, UI test, or manual simulator proof for real taps; the preview bridge records visual intent and handoff guidance
- Do not claim hot reload success unless launcher output and a browser-visible frame show the changed preview

## preview-devspace

Use when the user wants ChatGPT, GPT-5.5 Pro, or another MCP Apps-compatible host to see the iOS preview widget, record visual events, and prepare a Codex handoff through MCP tools.

Ask:

- Should Devspace attach to an existing `ios preview` URL or start one?
- Is this local Developer Mode testing, a Codex plugin MCP run, or production hosting research?
- Should `codex_prepare_handoff` write a prompt file, or should the user manually paste the handoff into Codex?

Proof:

- `shipguard ios devspace-check --path . --preview-out /tmp/ios-shipguard-preview --shareable --out /tmp/ios-shipguard-devspace-check` records loopback, auth, widget, preview, redaction, handoff, and model-boundary readiness before tunneled use without local absolute paths
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
- `shipguard ios spec-workflow --path . --feature <feature-or-improvement> --from-report <report-dir> --shareable --out <dir>` turns Devspace or report-quality findings into ShipGuard-owned constitution/spec/plan/tasks/analysis artifacts before implementation
- `shipguard ios modernize --focus swift --path . --out <dir>` records Swift concurrency, SwiftUI, Observation, accessibility/localization, and availability fallback findings before modernization work; add `--shareable` before scoring or sharing the report
- `shipguard ios plan --mode <mode> --inventory <ios-inventory.json> --out <file-or-dir>` turns inventory into owner files, blocked questions, target summary, proof route, and a Codex-ready brief
- `shipguard ios prove --plan <ios-plan.json> --out <dir>` records the smallest honest proof lane and manual blockers before proof claims
- `shipguard ios app-intelligence --path . --out <dir>` records App Intent, AppEntity, Shortcuts, Siri, Spotlight, widget, controls, Apple Intelligence, and privacy-readiness gaps before system exposure work; add `--shareable` before scoring or sharing the report
- `shipguard ios ai-readiness --path . --out <dir>` records Foundation Models, Core AI, Core ML, OpenAI API, no-AI, privacy, latency, cost, and fallback tradeoffs before model work; add `--shareable` before scoring or sharing the report
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
