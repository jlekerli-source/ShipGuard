# Notification And Alarm Testing Checklist

Use this checklist for notification, alarm, and wake-path changes. It is not a substitute for physical-device proof when alarm trust is claimed.

## Static And Simulator

- Read the routed `AGENTS.md` and `docs/validation-commands.md`.
- Check protected alarm runtime files:

```bash
./scripts/check_alarm_runtime_freeze.sh --print-protected-files
```

- Run the narrowest matching lane:

```bash
./scripts/ci_validate.sh fast
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh all
./scripts/check_alarmkit_readiness.sh
./scripts/check_shared_store_integrity.sh
```

## Permission States

- Not determined.
- Full AlarmKit access.
- Notification fallback only.
- Notifications denied.
- Focus/mute/low-volume edge states.
- App opened from alarm, notification, widget, shortcut, and normal launch.

## Wake Path

- Foreground fire.
- Inactive/lock-screen fire.
- Background or killed-app handoff.
- Selected sound starts audibly.
- AlarmKit carrier sound does not get stopped before backup audio owns playback.
- Mission flow blocks dismissal until completed.
- Completion silences sound and ends Live Activity.
- Repeating alarms keep future coverage.
- Daily Shift advances without stale duplicate fires.

## Device Proof

- Use the current release/device handoff scripts when proof is required.
- Record exact build/version shown on device.
- Save logs, `.xcresult`, screenshots, and proof packet paths.
- Stop on TestFlight, device, App Store Connect, live StoreKit, or privacy/legal blockers and write the exact operator action.
