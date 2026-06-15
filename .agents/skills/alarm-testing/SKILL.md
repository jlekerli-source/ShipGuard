---
name: alarm-testing
description: Ringly alarm-runtime and wake-path testing workflow. Use when a task touches alarms, AlarmKit, notification fallback, wake screens, Live Activity, missions, hardware volume, Daily Shift, repeating alarms, alarm persistence, or physical-device alarm proof.
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
5. Check edge cases: selected sound, AlarmKit carrier sound, notification fallback, hardware volume, Focus/mute, Bluetooth route, Dynamic Island, Live Activity cleanup, mission enforcement, Daily Shift, repeat coverage, stale duplicate fire, and disabled-off behavior.
6. Choose the narrowest validation lane:

```bash
./scripts/ci_validate.sh fast
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh all
./scripts/check_alarm_runtime_freeze.sh
./scripts/check_alarm_runtime_test_proof.sh
./scripts/check_alarmkit_readiness.sh
```

7. For release or trust claims, require real-device proof through the release/device handoff scripts. Simulator proof alone is not alarm-trust proof.
8. Report exact command status and evidence path. Treat timeouts and infrastructure stalls as blockers, not passes.
