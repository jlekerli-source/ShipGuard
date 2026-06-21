# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-verify-first-task-contract-fixture`
- Source question: Did prepare identify notification/permission owner scopes, review-only lifecycle/plist surfaces, and forbidden entitlement/project changes?

## Quickstart Replay

- Phase: `prepare`
- First useful verdict: `shipguard verify --task <task-dir>/shipguard-task.json --diff <patch.diff> --evidence <validation-receipt.json> --claim <scoped-claim> --out <verdict-dir>`
- Proof inputs: `<patch.diff>`, `<validation-receipt.json>`, `<scoped-claim>`
- Success signal: shipguard-verdict.json returns pass, review, blocked, or incomplete with one nextAction.
- Connects: goal, riskClassification, authorizedFiles, protectedBoundaries, validationContract, agentClaims, verdict, nextAction
- Boundary: Synthetic replay contract only; it does not authorize target-app work.

## iOS Notification Permission Workflow

- Status: `active`
- Trigger signals: `profile:ios`, `goal:notification`, `goal:permission`

### Permission-sensitive source signals

| Path | Signals |
| --- | --- |
| `Sources/SyntheticPermissions/NotificationPermissionCopy.swift` | source references UNUserNotificationCenter; path references notification permission |
| `Tests/SyntheticPermissionsTests/NotificationPermissionStateTests.swift` | test path references permission-state |

### Scope recommendations

Authorized candidate:

| Pattern | Reason |
| --- | --- |
| `Sources/SyntheticPermissions/**` | Synthetic source owner for notification permission copy and copy-only UI. |
| `Tests/SyntheticPermissionsTests/**` | Synthetic test owner for permission-state validation. |

Review only:

| Pattern | Reason |
| --- | --- |
| `**/Info.plist` | Permission purpose strings can change review behavior and require human review. |
| `**/*AppDelegate*.swift` | Notification registration lifecycle changes must be reviewed before editing. |
| `**/*SceneDelegate*.swift` | Scene lifecycle notification routing must be reviewed before editing. |

Forbidden unless explicit:

| Pattern | Reason |
| --- | --- |
| `**/*.entitlements` | Entitlement changes are release/signing sensitive and require explicit authorization. |
| `**/project.pbxproj` | Project graph changes are forbidden unless the task explicitly authorizes Xcode project edits. |

### Receipt requirements

- Permission-state: structured receipt must prove authorized, denied, and notDetermined state handling.
- Simulator denied-state: show the denied-state path or explain why unavailable.
- Physical-device prompt boundary: prompt timing and delivery claims need device proof before release claims.

### Proof boundaries

- Generic Swift tests do not prove permission prompt timing, denied-state behavior, or device delivery.
- Simulator denied-state proof is not physical-device prompt proof.
