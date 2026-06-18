---
name: alarm-testing
description: iOS alarm-runtime and wake-path testing workflow. Use when a task touches alarms, AlarmKit, notification fallback, wake screens, Live Activity, missions, hardware volume, repeating alarms, alarm persistence, or physical-device alarm proof.
---

# Alarm Testing

Use this skill to keep alarm work narrow, truthful, and evidence-backed.

## Steps

1. Read the nearest `AGENTS.md`, `docs/change-review-matrix.md`, `docs/alarm-trust-rules.md`, `docs/alarm-runtime-architecture.md`, and `docs/validation-commands.md` as routed.
2. Print protected runtime files before edits:

```bash
./scripts/check_alarm_runtime_freeze.sh --print-protected-files
```

3. Stop if the task needs a protected file but no `Alarm runtime unlock:` note exists.
4. Reproduce or describe the wake-path state: foreground, inactive, background, lock screen, killed app, TestFlight, or physical device.
5. Check edge cases: selected sound, AlarmKit carrier sound, notification fallback, hardware volume, Focus/mute, Bluetooth route, Dynamic Island, Live Activity cleanup, challenge or mission enforcement when present, repeat coverage, stale duplicate fire, and disabled-off behavior.
6. Choose the narrowest validation lane:

## Required Checks To Consider

```bash
./scripts/check_alarm_runtime_freeze.sh --print-protected-files
./scripts/ci_validate.sh fast
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh all
./scripts/check_alarm_runtime_freeze.sh
./scripts/check_alarm_runtime_test_proof.sh
./scripts/check_alarmkit_readiness.sh
```

7. For release or trust claims, require real-device proof through the release/device handoff scripts. Simulator proof alone is not alarm-trust proof.
8. Report exact command status and evidence path. Treat timeouts and infrastructure stalls as blockers, not passes.

## ShipGuard QA Hooks

When this skill is being audited inside the ShipGuard ShipYard, keep the skill useful by running the product-QA loop:

```bash
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable
```

Proof should show that alarm-testing has concrete commands, validation language, docs linkage, and test coverage; otherwise upgrade the skill before treating it as mature.

## Output

Return the behavior checked, files or lanes touched, command status, evidence path, and any manual device action still required.
