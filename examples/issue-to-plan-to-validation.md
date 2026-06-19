# Example: Issue To Plan To Validation

This is an anonymized transcript showing how a messy report becomes a bounded Codex task. It uses sample alarm and notification risk, but it does not expose private app source.

## Incoming Issue

> The quick alarm button sometimes disappears on a fresh install. I saw it after denying notifications, then reopening the app. It worked after I tapped around for a while.

## Bad Agent Response

> I will improve the onboarding and alarm home UI. I will also refactor the permission screen so the app is cleaner.

Why this is weak:

- The scope is too broad.
- It combines onboarding, alarm home, and permission UI without proof.
- It does not name the user-visible expected behavior.
- It has no validation lane.

## Inspector Output

Expected behavior:

The quick alarm action remains visible from a clean alarm home state, including after notification denial and app relaunch.

Current failure:

The report suggests the empty-state surface can render without the primary quick alarm action after a denied-permission path.

Likely owner files:

- Alarm home empty-state view.
- Permission-state adapter used by alarm home.
- UI test for first-tap alarm authoring.

Risk:

Notification-denied copy must stay truthful. The app must not imply fallback notifications are as reliable as AlarmKit or a system alarm.

Validation route:

```bash
./scripts/ci_validate.sh fast
./scripts/run_alarm_ui_batches.sh alarm-authoring-first-tap
```

Open question:

Can the failure be reproduced from a clean simulator with notifications denied before first alarm creation?

## Plan

Objective:

Keep the quick alarm action visible in the empty-state alarm home after notification denial and relaunch.

Out of scope:

- Redesigning onboarding.
- Changing alarm scheduling.
- Changing notification authorization prompts.

Affected files:

- Empty-state alarm home view.
- Permission-state display helper if the visibility condition lives there.
- Focused UI test or fixture state.

Risks:

- Hiding permission warnings behind the primary action.
- Accidentally enabling an alarm path that cannot be trusted without permission.
- Making the UI test pass by relying on fragile labels or coordinates.

Proof:

Run the focused alarm-authoring UI lane. If unavailable, provide a manual simulator path with exact denied-permission setup.

Rollback:

Revert the empty-state visibility condition and the matching UI test change.

## Implementation Handoff

Change made:

The primary quick alarm action now depends on alarm-home readiness, not on notification authorization being granted. Denied permission still shows the warning copy and blocks trusted alarm scheduling where required.

Validation:

```bash
./scripts/ci_validate.sh fast
./scripts/run_alarm_ui_batches.sh alarm-authoring-first-tap
```

Result:

Both commands completed. UI lane confirmed the quick alarm action is discoverable from a clean empty state.

Residual risk:

Physical-device alarm delivery was not claimed. This task only proves empty-state action visibility.

## Final Maintainer Summary

This is a good Codex handoff because it:

- Names the expected behavior.
- Separates visibility from alarm-delivery trust.
- Keeps permission truth intact.
- Uses the narrowest proof lane.
- Avoids broad UI redesign.
