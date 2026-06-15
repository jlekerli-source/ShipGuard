# AGENTS.md Template For iOS App Work

Use this as the root instruction file for Codex in `[APP_NAME]`.

## Project Overview

- Product: `[APP_NAME]`
- Primary stack: Swift, SwiftUI, XCTest, XCUITest
- Main project: `[XCODE_PROJECT].xcodeproj`
- App source: `[APP_SOURCE_DIRECTORY]/`
- Tests: `[TEST_DIRECTORY]/`
- Release evidence: `[RELEASE_ARTIFACTS_DIRECTORY]/`

## Startup Routine

1. Read this file before editing.
2. Identify the user-visible behavior being changed.
3. Route the task by risk before choosing files.
4. Prefer the smallest validation command that proves the change.
5. Do not make release, device, payment, notification, or reliability claims without evidence.

## Risk Routing

- UI-only copy or layout: run the focused UI or snapshot check.
- Persistence or migration: add a migration rehearsal or unit test.
- Notifications or background delivery: test denied, not-determined, granted, and fallback states.
- StoreKit or payments: validate product identifiers, entitlement state, downgrade/restore paths, and App Store copy.
- Widgets, intents, or extensions: check shared-store compatibility.
- Release work: separate local proof from TestFlight, App Store, legal, or physical-device proof.

## Validation Commands

Replace these placeholders with real project commands.

```bash
git diff --check
[FAST_CI_COMMAND]
[FOCUSED_UI_COMMAND]
[STOREKIT_CHECK_COMMAND]
[RELEASE_PREFLIGHT_COMMAND]
```

Blocked, timed-out, interrupted, or infrastructure-failed commands are not passes.

## Do Not Touch Without Explicit Scope

- App lifecycle and root navigation.
- Persistence models and migrations.
- Notification scheduling and background delivery.
- StoreKit configuration.
- Release metadata, privacy files, and production credentials.
- Historical proof packets or generated artifacts.

## Completion Checklist

Before claiming completion:

1. The requested behavior or artifact exists.
2. Only scoped files changed.
3. Risk areas are named.
4. The narrowest validation ran, or the blocker is exact.
5. Remaining manual proof is written as a concrete next action.
