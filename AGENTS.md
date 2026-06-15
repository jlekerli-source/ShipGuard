# AGENTS.md Template for Ringly-Style App Work

Use this as a public starter template for a Swift/iOS app where reliability, permissions, and release proof matter. Replace project names and commands with your own, but keep the same discipline: route the task, keep edits narrow, validate the smallest thing that proves the change, and do not make release claims without evidence.

## Project Overview

- Product: Ringly, an iPhone alarm app where alarm trust comes before polish, premium upsell, or growth work.
- Primary app stack: Swift, SwiftUI, XCTest, XCUITest, AlarmKit, UserNotifications, WidgetKit, ActivityKit, StoreKit, and first-party analytics.
- Main project: `Ringly.xcodeproj`.
- App source: `Ringly/`.
- Widgets: `RinglyWidgets/`.
- Website and analytics endpoints: `Website/`.
- Release evidence and proof packets: `release-artifacts/` and `scratch/`.

## Startup Routine

1. Read the nearest `AGENTS.md`.
2. Route the task through `docs/change-review-matrix.md`.
3. Use `docs/validation-commands.md` as command truth.
4. If editing a nested area, read that area's narrower `AGENTS.md`.
5. Before touching alarm runtime files, run:

```bash
./scripts/check_alarm_runtime_freeze.sh --print-protected-files
```

Do not edit protected alarm-runtime files unless the active task explicitly carries an `Alarm runtime unlock:` note and the required proof route is clear.

## Build And Test Commands

Use the smallest command that proves the change.

```bash
./scripts/install_git_hooks.sh
git diff --check
./scripts/ci_validate.sh fast
./scripts/run_onboarding_validation.sh
./scripts/run_alarm_ui_batches.sh onboarding-surfaces
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh premium-surfaces
./scripts/run_alarm_ui_batches.sh alarm-authoring-first-tap
./scripts/run_alarm_ui_batches.sh all
./scripts/run_alarm_ui_batches.sh release-ui-gates
```

Specialized checks:

```bash
./scripts/check_storekit_mapping.sh
./scripts/check_shared_store_integrity.sh
./scripts/run_shared_store_migration_rehearsal.sh --seed
./scripts/run_shared_store_migration_rehearsal.sh --verify
./scripts/check_alarmkit_readiness.sh
./scripts/check_alarm_runtime_freeze.sh
./scripts/check_alarm_runtime_test_proof.sh
python3 ./scripts/check_localization_coverage.py
npm --prefix Website run validate
npm --prefix Website run analytics:contract
```

## Validation Routing

- Docs/process-only: `git diff --check` plus targeted stale-wording scans. Do not run simulator batches.
- Onboarding-only: `./scripts/run_onboarding_validation.sh`.
- Alarm home/add/edit/settings UI: `./scripts/ci_validate.sh fast` plus `./scripts/run_alarm_ui_batches.sh alarm-home-smoke`.
- Premium UI/status only: `./scripts/ci_validate.sh fast` plus `./scripts/run_alarm_ui_batches.sh premium-surfaces`.
- Wake path/runtime/recovery/challenges: `./scripts/ci_validate.sh fast` plus `./scripts/run_alarm_ui_batches.sh all`.
- Shared store, widgets, intents, or migrations: `./scripts/ci_validate.sh fast` plus `./scripts/check_shared_store_integrity.sh`; add migration rehearsal when payload shape changes.
- Website/analytics: use the Website npm validation lane, not simulator tests.

Blocked, timed-out, interrupted, or infrastructure-failed commands are not passes.

## Release Procedures

Read `docs/release-gate.md`, `docs/release-checklist.md`, and `docs/validation-commands.md` before release work.

Operator and evidence commands:

```bash
./scripts/print_release_operator_handoff.sh
./scripts/print_release_status.sh
./scripts/print_testflight_handoff.sh
./scripts/run_release_preflight.sh --with-fast-gate
./scripts/run_release_preflight.sh --with-fast-gate --with-ui-gates
./scripts/begin_device_release_pass.sh --device <udid-or-name>
./scripts/print_premium_upload_handoff.sh
./scripts/create_premium_live_proof_notes.sh
```

Stop and record the exact operator action when blocked by TestFlight install, App Store Connect credentials, live StoreKit accounts, privacy/legal review, physical-device access, or human tester feedback.

## Notification And Alarm Edge Cases

Always check the state the user will rely on, not only the state the code intended.

- AlarmKit full access vs normal notification fallback.
- Notification denied, not determined, provisional, or fallback-only states.
- App states: foreground, inactive, background, locked, killed, and reopened from an alarm.
- Selected sound vs AlarmKit carrier sound vs default fallback sound.
- Hardware volume-down while alarm is active.
- Focus, mute switch, Bluetooth/AirPods, speaker routing, and low output volume.
- Dynamic Island and Live Activity cleanup after mission completion.
- Repeating alarms, Daily Shift, stale duplicate fires, and disabled-off cases.
- Mission enforcement, fallback missions, and recovery from pending wake/mission state.
- Shared-store consistency across app, widgets, intents, and watch surfaces.

## Do Not Touch Without Explicit Scope

- Protected files from `./scripts/check_alarm_runtime_freeze.sh --print-protected-files`.
- Alarm runtime and scheduling code.
- Root app shell and lifecycle coordination.
- App Intents and shared persistence models.
- Widgets, Live Activities, and project build settings.
- Historical audits, previous worktrees, and release proof packets, unless the task explicitly asks for historical comparison or proof entry.

## Completion Checklist

Before claiming completion:

1. The requested artifact exists.
2. Only scoped files were changed.
3. Protected runtime areas were not touched without unlock.
4. The narrowest routed validation ran, or the blocker is stated exactly.
5. Release or proof claims cite real evidence, not intention.
6. Any manual action needed is written as a concrete next step.
