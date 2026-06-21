# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-verify-first-task-contract-fixture`
- Source question: Did the verdict separate simulator denied-state proof from physical-device prompt proof before release claims?

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

- permission-state-validation: permission-state, denied-state, not-determined-state
  Expected: structured validation receipt with permission-state scope labels
  Success: Tests or UI automation cover not-determined, denied, and authorized/provisional states.
  Failure meaning: Permission-state behavior remains a generic test claim, not a permission workflow proof.
- simulator-denied-state-recovery: ios-permission-simulator-reset
  Expected: simulator screenshot, UI log, or receipt after resetting notification permission state
  Success: Denied-state recovery is observed after a simulator permission reset.
  Failure meaning: The denied-state recovery path remains unproven in a runnable local environment.
- physical-device-prompt-boundary: ios-permission-prompt-physical-device
  Expected: physical-device prompt receipt or manually reviewed screenshot reference
  Success: Real-device prompt timing and wording are observed before release claims.
  Failure meaning: ShipGuard must not treat simulator/source evidence as physical-device prompt proof.

### Proof boundaries

- localAutomation: Structured validation receipts can prove state handling and regression coverage.
- simulator: Simulator proof can show reset/denied-state recovery, but not final physical-device prompt truth.
- physicalDevice: Physical-device prompt timing, OS-level permission UI, and release claims need manual/device proof.

### Next action

- Command: `swift test`
- Expected artifact: structured receipt with scope labels: permission-state, denied-state, not-determined-state, simulator-permission-reset
- Success: ShipGuard verify can distinguish local permission workflow proof from manual device proof.
- Failure meaning: Notification permission work remains generic validation rather than a permission workflow contract.
