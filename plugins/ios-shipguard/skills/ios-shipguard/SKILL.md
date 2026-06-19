---
name: ios-shipguard
description: Solo iOS development workflow for Codex. Use when planning, implementing, reviewing, or validating iOS app changes that touch build/run/debug routes, permissions, notifications, AlarmKit, widgets, App Intents, StoreKit, background modes, Live Activities, UI/UX, motion, haptics, app icons, simulator proof, release readiness, or any risky user-trust surface.
---

# iOS ShipGuard

Use this skill to make Codex behave like a careful iOS release assistant instead of a generic coding agent. The ShipGuard ShipYard is the toolkit workshop around that assistant: CLI commands, skills, plugin metadata, reports, fixtures, tests, packages, and proof loops. The goal is to force the missing product and proof questions before edits, then let Codex use its native iOS simulator, Git, worktree, and inline comment features for execution.

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
6. Classify exactly one primary mode: `task-contract`, `permission-audit`, `simulator-debug`, `brand-audit`, `shipyard-value-audit`, `launchdeck`, `release-proof`, `storekit-commerce`, `widgets-intents-shared-store`, `performance-audit`, `design-audit`, `external-source-audit`, `preview-bridge`, `preview-devspace`, `privacy-security`, or `ui-polish`.
7. If the inventory says `needs-user-answer`, stop and ask the required question before editing.
8. Prefer Codex-native features for execution: XcodeBuildMCP for simulator driving, the LaunchDeck `ios-simulator-browser` skill for in-app browser mirroring, SwiftUI previews, and package-backed hot reload when available, built-in Git diff comments for requested changes, worktrees for experiments, and computer use only when a GUI path cannot be verified from files or structured tools. Use ShipGuard preview/Devspace when you need typed visual receipts, target-resolution handoff, report-quality evidence, ChatGPT planning, redaction, or release-proof boundaries. Do not claim hot reload proof unless the launcher output and a browser-visible frame prove the updated UI rendered.

## Mode Rules

Read `references/modes.md` when the task touches more than one risky surface or when you are unsure which proof path applies.

Default routing:

- `permission-audit`: Info.plist usage descriptions, entitlements, authorization copy, denied states.
- `task-contract`: proof-gated Codex change loop using `shipguard prepare` before edits and `shipguard verify` after diff/evidence capture.
- `simulator-debug`: UI reproduction, navigation bugs, screenshots, logs, UI hierarchy, LLDB.
- `brand-audit`: ShipGuard Brand Deck naming scheme, branded surface labels, nitty-gritty call signs for scripts/logs/reports, public-command coverage, active-doc wording, and future naming contract.
- `shipyard-value-audit`: ShipGuard Tool Value Gauntlet for testing every command, skill, plugin, GitHub Action, doc, package proof, and proof boundary for actual developer usefulness.
- `launchdeck`: ShipGuard-native routing into LaunchDeck for XcodeBuildMCP build/run, debugger/log capture, simulator browser, SwiftUI preview hot reload, and profiler proof.
- `release-proof`: TestFlight/App Store handoff, physical device evidence, release claims.
- `storekit-commerce`: product IDs, purchases, restore, current entitlements, sandbox account proof.
- `widgets-intents-shared-store`: WidgetKit, App Intents, app groups, stale data, shared persistence.
- `performance-audit`: FPS, hitches, launch or scroll stutter, Instruments traces, sampled stacks, thermal pressure, and device-vs-simulator proof gaps.
- `design-audit`: UI/UX coherence, app-type fit, ShipGuard-native motion quality gates, haptics, app icon direction, visual DNA, and preview/Devspace proof routing.
- `external-source-audit`: Spec Kit, CodexPro, Expo, Design Motion Principles, X posts, plugin/skill inspiration, or other external workflow ideas that need a ShipGuard-native capability matrix, replacement ledger, implementation backlog, license boundary, and report-quality questions before adoption is claimed.
- `preview-bridge`: Codex in-app-browser preview loop for a booted simulator screenshot, visual comments, and event receipts; prefer LaunchDeck simulator browser or SwiftUI preview hot reload for live visual iteration when that plugin is available, then use ShipGuard receipts and handoff for proof.
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
- Brand Deck: run `shipguard brand --path . --out /tmp/shipguard-brand --strict` before adding or renaming public ShipGuard surfaces; `shipguard ios brand` remains a compatibility route. Keep literal CLI commands and filesystem paths stable, make branded names and file-family call signs visible beside plain purpose and proof boundaries, and update docs/tests/package proof before claiming a naming scheme is complete.
- Task Contract: run `shipguard prepare "<goal>" --path . --out /tmp/shipguard-task --profile ios` before Codex edits when the task is risky or proof-sensitive. Add `--shareable` only for product-QA sharing; external shareable contracts redact target names and are not the private checkout's machine-verification contract. Expect prepare output to include `domainPackSDK` registry metadata. For notification, permission, authorization, denied-state, or provisional-flow goals, expect the `ios-notification-permission-workflow` risk pack with scope recommendations and receipt requirements. After Codex produces a diff and structured validation receipt, run `shipguard verify --task /tmp/shipguard-task/shipguard-task.json --diff <patch> --evidence <receipt.json> --out /tmp/shipguard-verdict`. Plain logs are review context only, and a generic green receipt is still review-only until it proves the active domain pack's proof lanes. Treat `blocked`, `review`, or `incomplete` as stop conditions until `nextAction` is satisfied.
- Tool Value Gauntlet: run `shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet` when the user asks whether every ShipGuard skill, plugin, command, action, or docs surface is genuinely useful. Check `runtimeOutputProbe`, `skillPluginRuntimeReceipts`, `workflowChainReceipts`, `adoptionReceipts`, `targetOnboardingReceipts`, `multiProfileOnboardingReceipts`, `profileNativeFirstAuditReceipts`, `profileNativeFixPlanReceipts`, `profileNativeValidationReceipts`, `profileNativeValidationRerunReceipts`, `profileNativeProofHandoffReceipts`, `commandFamilyRuntimeOutputReceipts`, `trustHardeningReceipts`, `taskContractReceipts`, `externalPilotVerdictBenchReceipts`, `domainPackSDKReceipts`, `configurationBaselineReceipts`, `structuredEvidenceReceipts`, and `agentAdapterReceipts`, then feed the report to `shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable`. If the next weak surface is web/backend/CLI first-audit quality, use `shipguard web audit`, `shipguard backend audit`, and `shipguard cli audit` on public or read-only targets. If the weak surface is profile-native fix-plan, validation-receipt, validation-rerun, or proof-handoff quality, use `shipguard web plan`, `shipguard backend plan`, and `shipguard cli plan` with `--target <repo>` on public or read-only audit reports so validation commands are classified and copy-ready evidence packets are produced without executing arbitrary target commands. If the weak surface is command-family runtime-output quality, add public fixtures that execute each major command family and judge useful JSON/Markdown output beyond `--help`. If the weak surface is trust-hardening quality, add public fixtures for GitHub Action input interpolation, Devspace URL/response caps, deletion/archive extraction, and release provenance. If the weak surface is task-contract quality, improve `shipguard prepare`, `shipguard verify`, docs, receipts, and exact next-action behavior. If the weak surface is ShipGuard PilotBench quality, add public-safe trace fixtures and tighten verdict precision, redaction, false-positive, and one-next-action scoring. If the weak surface is Domain Pack SDK quality, improve `DomainPackRegistry`, synthetic pack receipts, and compatibility tests. If the gauntlet escalates to configuration baselines and suppressions, scope the ShipGuard change around accepted findings, expiry, owners, proof boundaries, and regression behavior. If the gauntlet escalates to structured evidence receipts v2, scope the ShipGuard change around one shared proof schema for validation, runtime, manual, simulator, device, CI, and release receipts. If the gauntlet escalates to the Codex-native task and trace adapter, scope v3.120 around the Agent Adapter Kernel, Codex trace capture, receipt emission, automatic verify, verdict handoff, and agent-budget enforcement. If agent adapter receipts pass and the gauntlet escalates to XcodeBuildMCP, scope v3.121 around typed simulator/build/UI/profiler evidence on the same task timeline. Improve ShipGuard rules, tests, docs, package proof, or skill guidance rather than target apps.
- LaunchDeck: run `ios launchdeck --path . --out /tmp/ios-shipguard-launchdeck` before build/run/debug/preview/performance investigation when the route is unclear. Add `--workflow build-run|debug|preview|performance` when the user already named the lane. After Codex executes the LaunchDeck route or XcodeBuildMCP tools, rerun with `--receipt <proof-file-or-dir>` so ShipGuard grades whether build/run, UI, preview, log, or profiler proof is actually present. Add `--shipguard-eval --shareable` when a private app is only a read-only sample for improving ShipGuard.
- Existing Xcode project: use the `ios launchdeck` report to choose XcodeBuildMCP defaults, then use XcodeBuildMCP to confirm project/workspace, scheme, and simulator before building or running.
- Source reports: use `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, or `ios ai-readiness` before related work. Add `--shareable` before report-quality scoring or external planning. Treat `ios performance` as source-heuristic evidence until a same-route profiler/sample or physical-device trace exists; performance smoothness still needs matching route proof and physical-device Instruments evidence before 10/10 claims. Treat `ios design` as design inventory unless its `designTailoring` contract ties source signals, app type, tailored guidance dimensions, and an exact next proof action together, and its `designCoherenceBoundary` keeps source inventory, coherence risks, ShipGuard follow-up, app-work authorization, and proof boundaries separate.
- ShipGuard product QA: for read-only private-app samples, add `--shipguard-eval --shareable`, then run `ios report-quality --shareable`. Improve ShipGuard rules, fields, Markdown, docs, fixtures, or redaction, not the scanned app.
- External source adoption: run `ios external-audit --shareable` with `--source-path` for local read-only checkouts and `--source-url` for public repos/posts before claiming an external idea is integrated. Feed the audit into `ios report-quality --shareable`, then `ios spec-workflow --from-report` for implementation work. When auditing Design Motion Principles, useful motion ideas should land as `ios design` report fields and tests, not as a copied branded audit. Do not vendor external code unless a separate license/package decision explicitly approves it.
- Spec workflow: run `ios spec-workflow --from-report <report-quality-dir>` before implementing a ShipGuard improvement from report-quality questions. The bundle must preserve questions in acceptance criteria, tasks, validation commands, analysis gates, and `/plan` plus `/goal` handoff text.
- Preview loop: run `ios launchdeck --workflow preview` when the correct live-render route is unclear, then prefer LaunchDeck `ios-simulator-browser` for live mirror, SwiftUI preview, or hot reload when available. Use `ios preview`, `ios target-match`, and `handoff.md` when you need ShipGuard receipts, target matching, redaction, or Codex handoff proof.
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
