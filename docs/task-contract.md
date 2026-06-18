# Task Contract

ShipGuard Task Contract is the first core loop for proof-gated Codex work:

```text
understand the repo
prepare the task scope
run Codex under that scope
verify the exact diff, structured evidence receipts, and claims
return pass, review, blocked, or incomplete with one next action
```

It is intentionally plain. Fun surface names can stay in product docs, but this command is the durable object that ties a request to proof.

## Prepare

Run `prepare` before implementation:

```bash
./bin/shipguard prepare \
  "Add provisional notification onboarding flow" \
  --path ../my-ios-app \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "xcodebuild test -scheme MyApp -only-testing:NotificationPermissionTests" \
  --shareable
```

Outputs:

- `shipguard-task.json`
- `shipguard-task.md`

The JSON includes:

- `taskId`
- `goal`
- `projectSnapshot`
- `riskClassification`
- `authorizedFiles`
- `authorizedScope`
- `protectedBoundaries`
- `validationContract`
- `agentClaims`
- `evidence`
- `verdict`
- `nextAction`

`projectSnapshot.scanScope` is bounded. ShipGuard skips generated, cache, package, and proof directories so real app checkouts do not make `prepare` walk `DerivedData`, `.build`, `node_modules`, or release artifacts.

For iOS, the default authorized scope is discovered from Swift source/test owners such as `Sources/<target>/**`, `Tests/<target>/**`, or root Swift target folders. It is not tied to a private app name. Use `--allowed` and `--forbidden` to override that scope.

If no `--validation` is supplied, ShipGuard emits an executable default when it can: ShipGuard self-validation for this repo, a shared Xcode scheme test for iOS projects with shared schemes, or `swift test` for SwiftPM packages. When no runnable command can be inferred, it emits an explicit selection requirement such as `shipguard choose-ios-validation-scheme` instead of a fake placeholder command.

Use `--shipguard-eval` when a target app is only being used to evaluate ShipGuard output quality; that boundary says the report is not app-work authorization.

When `--shareable` points at an external target checkout, ShipGuard also redacts target names in authorized scope, skipped directories, Xcode projects, and scheme validation commands. Use the redacted contract for product QA or sharing; run without `--shareable` when you need the machine-verification contract for the private checkout.

## Verify

Run `verify` after Codex edits:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/xcodebuild-receipt.json \
  --claim "Implemented the onboarding permission flow." \
  --out /tmp/shipguard-verdict
```

Outputs:

- `shipguard-verdict.json`
- `shipguard-verdict.md`

The verdict is:

- `pass` when changed files stay inside scope, required validation is covered by structured receipts, and claims do not overreach.
- `review` when automated validation coverage or diff proof is missing but no protected boundary was crossed.
- `blocked` when the diff touches protected or unauthorized paths, or when an unsupported claim such as "fully verified" is made without proof.
- `incomplete` when no usable diff was provided or no changed files were detected.

Plain logs are review context only. Validation coverage requires a JSON receipt with at least:

```json
{
  "receiptId": "validation-unit-tests",
  "validationId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2026-06-18T12:00:00Z",
  "completedAt": "2026-06-18T12:00:10Z",
  "repositoryCommit": "abcdef123456",
  "artifact": {"path": "swift-test.log", "sha256": "<optional-sha256>"},
  "scope": ["NotificationPermissionTests"]
}
```

The receipt is usable only when the command or `validationId` matches a required validation item, `status` is `pass`, `exitCode` is `0`, the artifact exists and matches its digest when supplied, and `completedAt` is not older than the task contract. A plain log with "passed" text does not prove the command passed.

`shipguard-verdict.json` includes `diffFirstAnalysis` with changed file summaries, behavior categories, deleted-test warnings, validation coverage, evidence coverage, claim decisions, protected-boundary crossings, merge verdict, and the next action priority.

Blocked and review results always include `nextAction` with:

- `owner`
- `command`
- `expectedArtifact`
- `successCondition`
- `failureMeaning`

## Product Rule

Every future high-value ShipGuard workflow should either read, enrich, or verify the task contract. Reports that do not affect scope, evidence, claims, or verdict are secondary diagnostics.
