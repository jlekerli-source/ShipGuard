---
name: ios-shipguard
description: Solo iOS development workflow for Codex. Use when planning, implementing, reviewing, or validating iOS app changes that touch permissions, notifications, AlarmKit, widgets, App Intents, StoreKit, background modes, Live Activities, UI/UX, motion, haptics, app icons, simulator proof, release readiness, or any risky user-trust surface.
---

# iOS ShipGuard

Use this skill to make Codex behave like a careful iOS release assistant instead of a generic coding agent. The goal is to force the missing product and proof questions before edits, then let Codex use its native iOS simulator, Git, worktree, and inline comment features for execution.

## Start Here

1. Read the nearest `AGENTS.md`.
2. Resolve the ShipGuard CLI before running commands. In the ShipGuard source checkout, `./bin/shipguard` is available. In a target app checkout such as Ringly or Ilmify, use an installed CLI such as `shipguard` on `PATH` or `$HOME/.local/bin/shipguard`:

```bash
if [ -x ./bin/shipguard ]; then
  SHIPGUARD_CLI=./bin/shipguard
elif command -v shipguard >/dev/null 2>&1; then
  SHIPGUARD_CLI="$(command -v shipguard)"
elif [ -x "$HOME/.local/bin/shipguard" ]; then
  SHIPGUARD_CLI="$HOME/.local/bin/shipguard"
else
  SHIPGUARD_CLI=
fi
```

3. If `SHIPGUARD_CLI` is set, run an inventory before editing:

```bash
"$SHIPGUARD_CLI" ios inventory --path . --out /tmp/ios-shipguard-inventory
```

4. If `SHIPGUARD_CLI` is empty, say that the ShipGuard CLI is not installed in this Codex environment, do not invent iOS CLI proof, and continue with source inspection, `AGENTS.md`, XcodeBuildMCP, and explicit manual blockers. The fix is to install ShipGuard from a release/source checkout with `PREFIX="$HOME/.local" ./scripts/install.sh`, then start a new Codex thread.
5. Read `/tmp/ios-shipguard-inventory/ios-inventory.md` if it exists.
6. Classify exactly one primary mode: `permission-audit`, `simulator-debug`, `release-proof`, `storekit-commerce`, `widgets-intents-shared-store`, `performance-audit`, `design-audit`, `preview-bridge`, `preview-devspace`, `privacy-security`, or `ui-polish`.
7. If the inventory says `needs-user-answer`, stop and ask the required question before editing.
8. Prefer Codex-native features for execution: XcodeBuildMCP for simulator driving, the Build iOS Apps `ios-simulator-browser` skill for in-app browser mirroring, SwiftUI previews, and package-backed hot reload when available, built-in Git diff comments for requested changes, worktrees for experiments, and computer use only when a GUI path cannot be verified from files or structured tools. Use ShipGuard preview/Devspace when you need typed visual receipts, target-resolution handoff, report-quality evidence, ChatGPT planning, redaction, or release-proof boundaries. Do not claim hot reload proof unless the launcher output and a browser-visible frame prove the updated UI rendered.

## Mode Rules

Read `references/modes.md` when the task touches more than one risky surface or when you are unsure which proof path applies.

Default routing:

- `permission-audit`: Info.plist usage descriptions, entitlements, authorization copy, denied states.
- `simulator-debug`: UI reproduction, navigation bugs, screenshots, logs, UI hierarchy, LLDB.
- `release-proof`: TestFlight/App Store handoff, physical device evidence, release claims.
- `storekit-commerce`: product IDs, purchases, restore, current entitlements, sandbox account proof.
- `widgets-intents-shared-store`: WidgetKit, App Intents, app groups, stale data, shared persistence.
- `performance-audit`: FPS, hitches, launch or scroll stutter, Instruments traces, sampled stacks, thermal pressure, and device-vs-simulator proof gaps.
- `design-audit`: UI/UX coherence, app-type fit, motion, haptics, app icon direction, visual DNA, and preview/Devspace proof routing.
- `preview-bridge`: Codex in-app-browser preview loop for a booted simulator screenshot, visual comments, and event receipts; prefer Build iOS Apps simulator browser or SwiftUI preview hot reload for live visual iteration when that plugin is available, then use ShipGuard receipts and handoff for proof.
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

- Inventory/plan/proof: run `ios inventory`, then `ios plan`, then `ios prove` for blocked questions, owner files, proof routes, and honest local-vs-manual evidence.
- Existing Xcode project: use XcodeBuildMCP to confirm project/workspace, scheme, and simulator before building or running.
- Source reports: use `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, or `ios ai-readiness` before related work. Add `--shareable` before report-quality scoring or external planning. Performance smoothness still needs matching route proof and physical-device Instruments evidence before 10/10 claims.
- ShipGuard product QA: for read-only private-app samples, add `--shipguard-eval --shareable`, then run `ios report-quality --shareable`. Improve ShipGuard rules, fields, Markdown, docs, fixtures, or redaction, not the scanned app.
- Spec workflow: run `ios spec-workflow --from-report <report-quality-dir>` before implementing a ShipGuard improvement from report-quality questions. The bundle must preserve questions in acceptance criteria, tasks, validation commands, analysis gates, and `/plan` plus `/goal` handoff text.
- Preview loop: prefer Build iOS Apps `ios-simulator-browser` for live mirror, SwiftUI preview, or hot reload when available. Use `ios preview`, `ios target-match`, and `handoff.md` when you need ShipGuard receipts, target matching, redaction, or Codex handoff proof.
- Devspace loop: run `ios devspace-check --shareable` before sharing a tunnel, then `ios devspace` with bearer auth for ChatGPT planning. Use `preview_handoff_markdown`, `preview_target_resolution`, `preview_match_target`, and `codex_prepare_handoff`; execute Codex only through an explicit local handoff.
- Redaction/evals/demo: use `ios redact` before public sharing, `ios eval` before routing or proof-language changes, and `ios demo` for clean package proof without Xcode or credentials.
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
