---
name: ios-shipguard
description: Solo iOS development workflow for Codex. Use when planning, implementing, reviewing, or validating iOS app changes that touch permissions, notifications, AlarmKit, widgets, App Intents, StoreKit, background modes, Live Activities, simulator proof, release readiness, or any risky user-trust surface.
---

# iOS ShipGuard

Use this skill to make Codex behave like a careful iOS release assistant instead of a generic coding agent. The goal is to force the missing product and proof questions before edits, then let Codex use its native iOS simulator, Git, worktree, and inline comment features for execution.

## Start Here

1. Read the nearest `AGENTS.md`.
2. If this repo includes `bin/shipguard` and `./bin/shipguard ios inventory --help` succeeds, run an inventory before editing:

```bash
./bin/shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory
```

3. If the `shipguard ios` subcommands are unavailable in this checkout, do not invent iOS CLI proof. Continue with source inspection, `AGENTS.md`, XcodeBuildMCP, and the validation ladder entries that do not require `shipguard ios`.
4. Read `/tmp/ios-shipguard-inventory/ios-inventory.md` if it exists.
5. Classify exactly one primary mode:
   - `permission-audit`
   - `simulator-debug`
   - `release-proof`
   - `storekit-commerce`
   - `widgets-intents-shared-store`
   - `preview-bridge`
   - `preview-devspace`
   - `privacy-security`
   - `ui-polish`
6. If the inventory says `needs-user-answer`, stop and ask the required question before editing.
7. Prefer Codex-native features for execution: XcodeBuildMCP for simulator driving, built-in Git diff comments for requested changes, worktrees for experiments, and computer use only when a GUI path cannot be verified from files or structured tools.

## Mode Rules

Read `references/modes.md` when the task touches more than one risky surface or when you are unsure which proof path applies.

Default routing:

- `permission-audit`: Info.plist usage descriptions, entitlements, authorization copy, denied states.
- `simulator-debug`: UI reproduction, navigation bugs, screenshots, logs, UI hierarchy, LLDB.
- `release-proof`: TestFlight/App Store handoff, physical device evidence, release claims.
- `storekit-commerce`: product IDs, purchases, restore, current entitlements, sandbox account proof.
- `widgets-intents-shared-store`: WidgetKit, App Intents, app groups, stale data, shared persistence.
- `preview-bridge`: Codex in-app-browser preview loop for a booted simulator screenshot, visual comments, and event receipts.
- `preview-devspace`: ChatGPT Apps / MCP connector loop for the preview bridge, widget resource, and Codex handoff tools.
- `privacy-security`: iOS report redaction, Devspace trust boundaries, screenshot/token handling, and shareability review.
- `ui-polish`: SwiftUI layout, copy, accessibility, Dynamic Type, localization.

## Ask-Before-Editing Gates

Ask the user for a concrete answer before edits when any of these are true:

- A permission is used in source but its usage description is missing or unclear.
- An entitlement is added, removed, renamed, or environment-specific.
- The change can affect alarms, notification delivery, wake paths, Live Activities, or background behavior.
- The change can affect paid access, subscriptions, restore, receipts, product IDs, or App Store review.
- The change spans app, widget, intent, watch, or shared container surfaces.
- Final proof requires a physical device, TestFlight install, sandbox account, App Store Connect access, or human tester feedback.

Do not turn a missing answer into an assumption. Ask one short question, wait, then continue.

## Validation Ladder

Use the smallest proof that matches the mode:

- Source-only permission inventory when available: `./bin/shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory`
- Existing Xcode project: use XcodeBuildMCP to confirm project/workspace, scheme, and simulator before building or running.
- Guided plan: run `./bin/shipguard ios plan --mode <mode> --inventory <ios-inventory.json> --out <file-or-dir>` to generate the Codex brief, owner files, blocked questions, and proof route.
- Proof route: run `./bin/shipguard ios prove --plan <ios-plan.json> --out <dir>` to record source, simulator, StoreKit, release, privacy, preview, and blocked-manual evidence lanes before claiming proof.
- Preview loop: run `./bin/shipguard ios preview --out /tmp/ios-shipguard-preview`, open the printed URL with `@Browser`, and read `handoff.md`, `preview-events.jsonl`, or `/api/handoff.md` target resolution before editing. If you have XcodeBuildMCP UI JSON, run `ios target-match` to rank semantic targets.
- Devspace loop: run `./bin/shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN`, connect ChatGPT Developer Mode to `/mcp` through an HTTPS tunnel, and use `production_readiness`, `preview_handoff_markdown`, `preview_target_resolution`, `preview_match_target`, plus `codex_prepare_handoff` before asking Codex to edit.
- Codex handoff supervisor: run `./bin/shipguard ios codex-handoff --prompt-file <file> --out <dir>` to prepare app-server artifacts; add `--execute` only after explicit local approval.
- Swift modernization: run `./bin/shipguard ios modernize --focus swift --path . --out /tmp/ios-shipguard-modernize` before concurrency, SwiftUI, Observation, accessibility/localization, or Liquid Glass-style work.
- App intelligence: run `./bin/shipguard ios app-intelligence --path . --out /tmp/ios-shipguard-app-intelligence` before adding App Intents, AppEntity, Shortcuts, Siri, Spotlight, widget, controls, or Apple Intelligence exposure.
- AI readiness: run `./bin/shipguard ios ai-readiness --path . --out /tmp/ios-shipguard-ai-readiness` before choosing Foundation Models, Core AI, Core ML, OpenAI API, or no-AI implementation.
- Report sharing: run `./bin/shipguard ios redact --in <file-or-dir> --out <file-or-dir>` before moving ShipGuard reports, preview logs, app-intelligence reports, AI-readiness output, or handoff artifacts into public issues, benchmark notes, release evidence, or external planning.
- ShipGuard evals: run `./bin/shipguard ios eval --cases evals/ios_shipguard_cases.jsonl --out /tmp/ios-shipguard-eval` before changing routing, proof-honesty language, or plugin mode guidance.
- First-run demo: run `./bin/shipguard ios demo --out /tmp/ios-shipguard-first-run` when validating a clean checkout or release package without Xcode, a booted Simulator, credentials, or an API key.
- Simulator UI bug: build, launch, inspect UI, execute the reproduction path, capture screenshot or logs, then rerun after the fix.
- Release proof: state which proof is local, simulator, TestFlight, physical-device, App Store Connect, or blocked-manual.
- StoreKit proof: verify product mapping and entitlement states; do not claim live purchase proof without sandbox or live-account evidence.

## Output Shape

End with:

- Mode used.
- Inventory findings that changed the plan.
- Questions asked and answers received.
- Files changed.
- Validation run, with exact command or simulator proof.
- Remaining manual proof if Codex cannot complete it locally.
