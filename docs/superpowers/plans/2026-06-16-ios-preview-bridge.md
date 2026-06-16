# iOS Preview Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dependency-light iOS Simulator preview bridge that opens in Codex's in-app browser and records visual feedback as reviewable evidence.

**Architecture:** Add `codex-maintainer ios preview` as a Python stdlib HTTP server. It captures simulator screenshots with `xcrun simctl io`, serves a localhost phone preview, records click/comment events to JSONL, and updates iOS Shipguard docs/skill/goal routing.

**Tech Stack:** Bash dispatcher, Python stdlib HTTP server, `xcrun simctl`, Markdown docs, shell tests.

---

### Task 1: Preview CLI And Server

**Files:**
- Create: `scripts/ios_preview.py`
- Modify: `bin/codex-maintainer`
- Test: `tests/ios_preview_test.sh`

- [ ] **Step 1: Add a failing CLI test**

Create `tests/ios_preview_test.sh` that starts the preview server on port `0` with a generated PNG fixture, waits for `preview-url.txt`, checks `/api/state`, downloads `/screenshot.png`, posts one tap event, verifies `preview-events.jsonl`, checks `handoff.md` plus `/api/handoff.md`, and checks `--help`.

- [ ] **Step 2: Run the focused test**

Run:

```bash
./tests/ios_preview_test.sh
```

Expected before implementation: failure because `codex-maintainer ios preview` is not dispatched.

- [ ] **Step 3: Implement `scripts/ios_preview.py`**

Implement:

- args: `--out`, `--device`, `--host`, `--port`, `--refresh-ms`, `--fixture-image`, `--ready-file`, `--event-limit`.
- loopback default: `127.0.0.1`.
- endpoints: `/`, `/api/state`, `/api/events`, `/api/handoff`, `/api/handoff.md`, `/session.json`, `/screenshot.png`.
- JSON body limit for event POSTs.
- screenshot capture through `xcrun simctl io <device> screenshot --type=png <tempfile>`, with fixture fallback.
- session files: `session.json`, `preview-url.txt`, `preview-events.jsonl`, `handoff.json`, `handoff.md`, `last-screenshot.png`.

- [ ] **Step 4: Wire the dispatcher**

Update `bin/codex-maintainer` usage, iOS subcommand validation, and iOS case dispatch so `ios preview` calls the new script.

- [ ] **Step 5: Run the focused test**

Run:

```bash
./tests/ios_preview_test.sh
```

Expected: `ios preview tests passed`.

### Task 2: Shipguard Plugin Routing

**Files:**
- Modify: `plugins/ios-shipguard/skills/ios-shipguard/SKILL.md`
- Modify: `plugins/ios-shipguard/skills/ios-shipguard/references/modes.md`
- Modify: `docs/ios-shipguard.md`
- Create: `docs/ios-preview.md`

- [ ] **Step 1: Document the user flow**

Add `docs/ios-preview.md` with commands, browser workflow, event log format, security boundaries, and future native-panel boundary.

- [ ] **Step 2: Add plugin mode routing**

Add `preview-bridge` to the skill mode list and mode reference. The mode should route to `ios preview`, `@Browser`, browser comments, event receipts, and XcodeBuildMCP for simulator actions.

- [ ] **Step 3: Link from Shipguard docs**

Add the preview bridge to `docs/ios-shipguard.md` as a Codex-native preview workflow.

- [ ] **Step 4: Run docs validation**

Run:

```bash
git diff --check
./bin/codex-maintainer docs-check docs/ios-preview.md --out /tmp/codex-maintainer-docs-check-ios-preview
```

Expected: both pass.

### Task 3: Goal Loop And Package Readiness

**Files:**
- Modify: `scripts/ios_goal_loop.py`
- Modify: `tests/ios_goal_loop_test.sh`
- Modify: `tests/cli_smoke_test.sh`
- Modify: `tests/package_release_test.sh`
- Modify: `scripts/validate_workflow_bundle.sh`
- Modify: `scripts/self_audit.sh`
- Modify: `tests/self_audit_test.sh`

- [ ] **Step 1: Add preview goal**

Add `shipguard-ios-preview-bridge` to the iOS goal catalog with proof commands:

```bash
./tests/ios_preview_test.sh
./bin/codex-maintainer docs-check docs/ios-preview.md --out /tmp/shipguard-preview-docs
```

- [ ] **Step 2: Update tests and required-file lists**

Update focused tests and required-file manifests so the new script, test, and doc are covered by validation, package release, and self-audit.

- [ ] **Step 3: Run focused validation**

Run:

```bash
./tests/ios_preview_test.sh
./tests/ios_goal_loop_test.sh
./tests/cli_smoke_test.sh
```

Expected: all pass.

- [ ] **Step 4: Run package/self-audit focused checks**

Run:

```bash
./tests/self_audit_test.sh
./tests/package_release_test.sh
```

Expected: both pass.

### Task 4: Final Validation

**Files:**
- All touched files.

- [ ] **Step 1: Run narrow validation for scripts and CLI dispatch**

Run:

```bash
./bin/codex-maintainer validate
./tests/ios_preview_test.sh
```

Expected: validation passes and the preview test passes.

- [ ] **Step 2: Record any live-simulator limitation**

If no booted simulator is available, record that fixture mode was validated and live simulator proof remains manual. Do not claim live simulator proof without command output from an actual simulator capture.
