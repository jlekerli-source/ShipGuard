---
name: notification-permissions
description: Ringly notification, AlarmKit access, and permission-truth workflow. Use when a task touches notification authorization, AlarmKit readiness, fallback alerts, permission copy, settings permission UI, onboarding permission prompts, or alarm scheduling availability.
---

# Notification Permissions

Use this skill when permission truth or fallback delivery matters.

## Permission States

Check each relevant state:

- Not determined.
- Full AlarmKit access.
- Notification fallback only.
- Notifications denied.
- Provisional or limited notification behavior.
- Reopened from notification, alarm, widget, shortcut, or normal launch.

## Steps

1. Identify the exact access state being changed or tested: AlarmKit full access, normal notification authorization, fallback-only, denied, not determined, unavailable, or simulator override.
2. Read the routed files from `AGENTS.md` and `docs/change-review-matrix.md`; for alarm delivery, also read `docs/alarm-trust-rules.md`.
3. Keep copy truthful. Do not imply notification fallback is as reliable as a system alarm.
4. Check the user path in onboarding, Settings, Alarm Home, add/edit alarm, widgets, intents, and shortcuts when those surfaces use the permission state.
5. Use relevant commands:

```bash
./scripts/check_alarmkit_readiness.sh
./scripts/ci_validate.sh fast
./scripts/run_onboarding_validation.sh
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
```

6. For permission-denied or fallback states, verify the app still allows safe free exploration while clearly blocking or warning about armed alarms that cannot be trusted.
7. For release claims, record whether proof is simulator, TestFlight, physical-device, or blocked-manual.

## Rules

- UI must describe the actual permission state, not the desired state.
- Fallback behavior must be explicit and testable.
- Do not remove existing scheduled notifications before replacement succeeds unless the rollback path is proven.
- If the proof requires a physical device, state that directly.

## Output

Return the observed state, the UI surfaces checked, commands run, and any manual device or Settings action still required.
