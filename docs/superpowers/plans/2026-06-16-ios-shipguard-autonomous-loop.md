# iOS Shipguard Autonomous Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build iOS Shipguard into a self-advancing Codex workflow for solo iOS developers, where each finished goal produces the next concrete goal until the product reaches a complete 10/10 capability set.

**Architecture:** Keep the first loop local, deterministic, and auditable. A versioned goal catalog defines product phases, while a small CLI state machine tracks the current goal, requires evidence receipts before completion, and emits the next Codex `/goal` block automatically.

**Tech Stack:** Bash CLI dispatcher, Python stdlib for structured goal state, Markdown docs, shell tests, existing package/self-audit validators.

---

## Product North Star

iOS Shipguard should become the guided product brain around Codex's native iOS capabilities. Codex already provides editing, diff comments, worktrees, terminal, simulator driving through XcodeBuildMCP, and computer use. Shipguard should add:

- app-aware iOS discovery before edits
- guided planning that asks missing product/proof questions
- simulator and device proof routing
- modernization audits for Swift, SwiftUI, App Intents, Apple Intelligence, Foundation Models, Core AI, Core ML, StoreKit, widgets, Live Activities, and privacy
- evidence receipts that prevent false "done" claims
- a self-advancing goal loop that keeps the project moving

## Phase Catalog

### Phase 1: App Understanding

Build commands that understand the app before Codex edits it.

- Goal 1.1: `ios doctor` discovers projects, workspaces, schemes, targets, bundle IDs, deployment targets, Swift versions, package managers, and test plans.
- Goal 1.2: inventory maps Info.plists, entitlements, privacy manifests, StoreKit config, app groups, widgets, intents, Live Activities, and background modes per target.
- Goal 1.3: risk map classifies each target as app, extension, widget, intent, watch, test, or support package.

### Phase 2: Guided Planning

Build a planner that turns app facts into Codex-ready tasks.

- Goal 2.1: `ios plan` creates a task brief with mode, likely owner files, blocked questions, tools to use, and proof route.
- Goal 2.2: plan modes cover permission audit, simulator bug, modernization, StoreKit, widgets/intents, release proof, and security/privacy.
- Goal 2.3: plan output includes Codex-native handoff text for XcodeBuildMCP, inline diff comments, and worktree use.

### Phase 3: Proof Loop

Make "done" evidence explicit.

- Goal 3.1: `ios prove` reads a plan and selects local build, simulator, UI, StoreKit, privacy, or manual-device proof.
- Goal 3.2: simulator proof captures scheme, device, OS, screenshots/log pointers, and reproduction steps.
- Goal 3.3: release proof distinguishes local, simulator, TestFlight, App Store Connect, physical-device, and blocked-manual evidence.

### Phase 4: Modernization Intelligence

Make Shipguard a modern iOS reviewer.

- Goal 4.1: Swift 6/Swift 6.4 audit for strict concurrency, sendability, actor isolation, `@MainActor`, async cleanup, and legacy callback boundaries.
- Goal 4.2: SwiftUI audit for Observation, `@Observable`, SwiftData boundaries, navigation, sheets, async state, accessibility, Dynamic Type, localization, and Liquid Glass readiness.
- Goal 4.3: App Intelligence audit for App Intents, entities, Spotlight, Shortcuts, controls, widgets, Siri surfaces, and Apple Intelligence discoverability.
- Goal 4.4: AI capability audit for Foundation Models, Core AI, Core ML, OpenAI API, privacy, latency, cost, and fallback routing.

### Phase 5: Privacy, Security, And Distribution

Make it safe for OSS and real app use.

- Goal 5.1: redact local paths, team IDs, bundle IDs, emails, tokens, screenshots/log sensitive strings, and App Store Connect identifiers from reports.
- Goal 5.2: threat model plugin execution, local marketplace trust, generated artifacts, GitHub Actions, uploads, and release packaging.
- Goal 5.3: package plugin, skill, scripts, docs, evals, and fixtures with tamper-evident release proof.

### Phase 6: Evals And Quality Gates

Prove Shipguard works.

- Goal 6.1: deterministic eval cases grade plan quality, blocked-question detection, mode routing, and proof honesty.
- Goal 6.2: optional OpenAI trace/eval harness grades agent workflows with tool calls, guardrails, handoffs, and evidence receipts.
- Goal 6.3: release gate fails if goal loop, inventory, planner, proof router, docs, package, or plugin validation regresses.

## Task 1: Add Goal Loop Engine

**Files:**
- Create: `scripts/ios_goal_loop.py`
- Modify: `bin/codex-maintainer`
- Test: `tests/ios_goal_loop_test.sh`

- [x] **Step 1: Write goal loop test**

Create a shell test that verifies:

- `ios goals init` creates a state file.
- `ios goals next` writes the current `/goal`.
- `ios goals complete --goal <id> --evidence <file>` marks the current goal complete.
- Completing a goal automatically emits the next goal.
- Completing the wrong goal fails.

- [x] **Step 2: Implement goal catalog and state machine**

Implement a Python stdlib script with subcommands:

- `init`
- `status`
- `next`
- `complete`

The state file must include schema version, generated timestamp, current index, completed receipts, and goal catalog digest.

- [x] **Step 3: Wire CLI dispatcher**

Add `codex-maintainer ios goals ...` under the existing `ios` command.

- [x] **Step 4: Verify test passes**

Run:

```bash
./tests/ios_goal_loop_test.sh
```

Expected: `ios goal loop tests passed`.

## Task 2: Document The Loop

**Files:**
- Modify: `docs/ios-shipguard.md`
- Modify: `docs/cli.md`
- Modify: `docs/command-matrix.md`
- Modify: `README.md`

- [x] **Step 1: Add first-run loop commands**

Document:

```bash
./bin/codex-maintainer ios goals init --state .shipguard/goals.json
./bin/codex-maintainer ios goals next --state .shipguard/goals.json --out NEXT_SHIPGUARD_GOAL.md
./bin/codex-maintainer ios goals complete --state .shipguard/goals.json --goal shipguard-ios-doctor --evidence path/to/proof.md --out NEXT_SHIPGUARD_GOAL.md
```

- [x] **Step 2: Explain evidence receipts**

State that the loop advances only when the user or CI provides evidence. Do not claim fully autonomous completion without proof.

## Task 3: Wire Validation And Packaging

**Files:**
- Modify: `scripts/validate_workflow_bundle.sh`
- Modify: `scripts/self_audit.sh`
- Modify: `tests/self_audit_test.sh`
- Modify: `tests/package_release_test.sh`
- Modify: `tests/cli_smoke_test.sh`

- [x] **Step 1: Required-file validation**

Add the new script, test, and plan to the required artifact lists.

- [x] **Step 2: Self-audit validation**

Add `ios goals --help` coverage and the new artifacts.

- [x] **Step 3: Package validation**

Assert the new script, test, and plan ship in the release tarball.

## Task 4: Run Verification

**Files:**
- No new files.

- [x] **Step 1: Focused tests**

Run:

```bash
./tests/ios_goal_loop_test.sh
./tests/cli_smoke_test.sh
./tests/self_audit_test.sh
```

- [x] **Step 2: Broad validation**

Run:

```bash
git diff --check
./bin/codex-maintainer docs-check . --out /tmp/ios-shipguard-loop-docs-check
./bin/codex-maintainer validate
./tests/package_release_test.sh
```

## Future Plans After This Slice

The next generated goals should implement Phase 1.1 through Phase 6.3 in order. Each goal must produce:

- a CLI or plugin capability
- docs
- tests
- package proof
- a completion receipt that unlocks the next goal
