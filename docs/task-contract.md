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
- `configurationPolicy`
- `domainPackSDK`
- `agentClaims`
- `evidence`
- `verdict`
- `quickstartReplay`
- `nextAction`

`projectSnapshot.scanScope` is bounded. ShipGuard skips generated, cache, package, and proof directories so real app checkouts do not make `prepare` walk `DerivedData`, `.build`, `node_modules`, or release artifacts.

For iOS, the default authorized scope is discovered from Swift source/test owners such as `Sources/<target>/**`, `Tests/<target>/**`, or root Swift target folders. It is not tied to a private app name. Use `--allowed` and `--forbidden` to override that scope.

If no `--validation` is supplied, ShipGuard emits an executable default when it can: ShipGuard self-validation for this repo, a shared Xcode scheme test for iOS projects with shared schemes, or `swift test` for SwiftPM packages. When no runnable command can be inferred, it emits an explicit selection requirement such as `shipguard choose-ios-validation-scheme` instead of a fake placeholder command.

For iOS notification, permission, authorization, denied-state, or provisional-flow goals, `prepare` adds `domainRiskPack.id = ios-notification-permission-workflow`. That pack records:

- trigger signals from the goal and iOS profile
- permission-sensitive source candidates when discoverable
- authorized, review-only, and forbidden-unless-explicit scope recommendations
- required receipt scopes for permission-state, denied-state, not-determined-state, and simulator permission-reset proof
- a physical-device prompt boundary so simulator/source evidence is not treated as release proof

Report-quality now treats those notification scope and proof-lane rows as part of the public task-contract UX. A prepare report that asks these questions but hides `scopeRecommendations.authorized`, `scopeRecommendations.reviewOnly`, `scopeRecommendations.forbiddenUnlessExplicit`, permission-sensitive source signals, structured receipt requirements, simulator denied-state reset requirements, physical-device prompt requirements, generic-log failure meanings, or the matching Markdown section is a ShipGuard report defect, not a target-app task. A verify report is also defective when it hides `simulator-permission-reset` versus `physical-device-prompt`, marks physical-device prompt proof as locally proven, or omits the manual-required release boundary.

The notification workflow is implemented as a domain pack in `scripts/task_domain_packs.py`, not as another standalone report family. The generic task contract passes bounded scan helpers, shareable redaction helpers, and skip rules through `DomainPackContext`; the pack supplies the iOS-specific applicability, scope, proof requirements, proof-lane evaluation, and next action.

`domainPackSDK` records the reusable extension layer:

- `sdkVersion`
- `registeredPacks`
- `activePack`
- `evaluatedPacks`
- pack-specific `resultField` names such as `notificationPermissionWorkflow` and `syntheticDomainPackWorkflow`

`scripts/task_domain_packs.py` now exposes `DomainPackRegistry` and a public synthetic fixture pack. The synthetic pack is not app advice; it proves a second pack can register prepare/verify hooks, emit its own result field, and pass through the same verdict engine without breaking notification-permission compatibility. Future StoreKit, persistence, lifecycle, performance, design, and modernization packs should register through this SDK instead of growing bespoke branches in `scripts/task_contract.py`.

Use `--shipguard-eval` when a target app is only being used to evaluate ShipGuard output quality; that boundary says the report is not app-work authorization.

When `--shareable` points at an external target checkout, ShipGuard also redacts target names in authorized scope, skipped directories, Xcode projects, and scheme validation commands. Use the redacted contract for product QA or sharing; run without `--shareable` when you need the machine-verification contract for the private checkout.

`quickstartReplay` is the first-user handoff. In `prepare`, it records the task artifact, Markdown artifact, proof inputs, and copy-ready `shipguard verify` template that turns the contract into the first useful verdict. It also lists the fields the durable object connects: goal, risk, authorized scope, protected boundaries, validation, claims, verdict, and next action.

`unsupportedClaimReplay` appears in `verify` when broad completion wording such as "fully verified" is rejected or still needs manual/device proof. It keeps the claim-specific repair path visible even when the overall verdict has a higher-priority blocker such as protected scope: rejected phrase, replay command, exact claim repair action, proof boundary, and non-claims are all rendered in JSON and Markdown.

## Configuration Baselines

ShipGuard reads `.shipguard.yml` and `.shipguard-baseline.json` during `prepare` and stores the policy inside the task object. The first supported shape is intentionally small:

```yaml
baseline:
  path: .shipguard-baseline.json
suppressions:
  requireOwner: true
  requireReason: true
  requireExpiresAt: true
  requireProofBoundary: true
```

The baseline file records exact accepted findings:

```json
{
  "schemaVersion": "1.0",
  "suppressions": [
    {
      "id": "accepted-release-workflow-touch",
      "ruleId": "task-contract.protected-boundary",
      "fingerprint": "a37a1282251f3570",
      "owner": "release-owner",
      "reason": "Synthetic fixture accepts this exact release workflow touch.",
      "expiresAt": "2099-01-01",
      "proofBoundary": "Only .github/workflows/release.yml is accepted; other workflow files remain regressions."
    }
  ]
}
```

`verify` emits finding fingerprints in `contractFindings` and evaluates them through `configurationBaseline`. A valid suppression must match both `ruleId` and `fingerprint`, include the required metadata, and be unexpired. Accepted findings are not hidden: Markdown and JSON still show the rule, fingerprint, owner, expiry, and proof boundary. New findings, expired suppressions, invalid suppressions, and unmatched protected files remain visible and keep their normal `review` or `blocked` behavior.

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

The Markdown report starts with a copy-ready `Proof Report` section:

```text
Status: pass
Validation: 1/1 covered
Claims checked: 1/1 accepted
Risk files: 0 protected, 0 out of scope, 0 deleted tests
Release evidence: not-applicable
```

The same data is exposed in JSON as `proofReport` so PR bots, launch docs, and review comments can show the concise verdict without parsing the full diff analysis.

Every verdict also includes `quickstartReplay`. It records the replay command shape, fast verdict text, review packet files, next action, and boundary. The Markdown renders this as `Quickstart Replay` directly after `Proof Report`, so a maintainer can rerun or attach the proof packet without reading internal ShipYard process docs.

If a verdict has no reviewer disposition yet, the Markdown and JSON include labeled repair commands. Use `Record reviewer outcome without note` for the normal outcome receipt, or `Record reviewer outcome with note` when the decision needs a short maintainer explanation before being used as local tuning evidence. The reviewer outcome is still local feedback, not public adoption or security-review evidence.

The verdict is:

- `pass` when changed files stay inside scope, required validation is covered by structured receipts, and claims do not overreach.
- `review` when automated validation coverage or diff proof is missing but no protected boundary was crossed.
- `blocked` when the diff touches protected or unauthorized paths, or when an unsupported claim such as "fully verified" is made without proof.
- `incomplete` when no usable diff was provided or no changed files were detected.

Plain logs are review context only. Validation coverage requires a structured evidence receipt. v3.119 introduces the shared v2 receipt layer in `scripts/shipguard_receipts.py`; task-contract verification now normalizes current v2 receipts, legacy command receipts, unsupported proof receipts, unsupported schema versions, malformed JSON, missing artifacts, digest mismatches, and stale receipts before any claim is accepted.

The canonical v2 shape is:

```json
{
  "schemaVersion": "2.0",
  "receiptId": "validation-unit-tests",
  "receiptType": "validation",
  "requirementId": "swift-test",
  "command": "swift test",
  "exitCode": 0,
  "status": "pass",
  "startedAt": "2026-06-18T12:00:00Z",
  "completedAt": "2026-06-18T12:00:10Z",
  "repositoryCommit": "abcdef123456",
  "diffDigest": "optional-diff-digest",
  "environment": "simulator",
  "proofType": "ios-permission-simulator-reset",
  "artifact": {"path": "swift-test.log", "sha256": "<sha256>", "bytes": 1024},
  "scope": ["NotificationPermissionTests", "permission-state", "denied-state", "not-determined-state", "simulator-permission-reset"]
}
```

The receipt is usable only when the command or requirement ID matches a required validation item, `receiptType` is validation-compatible, `status` is `pass`, `exitCode` is `0`, the artifact exists and matches its digest and byte count when supplied, and `completedAt` is not older than the task contract. A plain log with "passed" text does not prove the command passed.

Legacy receipts without `schemaVersion` are still accepted when they contain the older `validationId`, `command`, `status`, `exitCode`, and artifact fields, but the verdict marks them as `legacy-compatible` under `evidence[].compatibility` and increments `evidenceReceiptSchema.legacyCount`. Unsupported v2 receipts such as `receiptType: "manual"` or `receiptType: "runtime"` are preserved as structured proof context but downgraded for validation coverage; they increment `validationCoverage.downgradedReceipts` and `evidenceReceiptSchema.downgradedCount` instead of silently satisfying an automated validation command.

`shipguard-verdict.json` and `diffFirstAnalysis` both include `evidenceReceiptSchema` with v2, legacy, artifact-only, missing, invalid, stale, downgraded, and structured-proof counts. This makes receipt confidence machine-readable for report-quality, package proof, and later agent adapters.

For notification-permission workflows, a generic matching receipt such as `scope: ["NotificationPermissionTests"]` proves that the required command ran, but it does not prove the domain workflow. `verify` returns `review` until the receipt metadata proves the relevant lanes, and report-quality fails prepare/verify reports that hide these lanes or present a generic log as enough:

- `permission-state-validation`: needs permission-state, denied-state, and not-determined-state scope labels.
- `denied-state-recovery`: needs denied-state recovery proof.
- `simulator-permission-reset`: needs simulator reset proof, for example `environment: "simulator"` and `proofType: "ios-permission-simulator-reset"`.
- `physical-device-prompt`: remains `manual-required` unless physical-device prompt proof is attached.

When the first three lanes are proven, the task can still pass locally while `notificationPermissionWorkflow.status` reports `local-pass-manual-device-proof-required`. Do not make release or "fully verified" claims until the physical-device prompt lane is proven.

`shipguard-verdict.json` includes `domainWorkflows` for every active pack, preserves compatibility fields such as `notificationPermissionWorkflow`, and includes `diffFirstAnalysis` with changed file summaries, behavior categories, deleted-test warnings, validation coverage, evidence coverage, claim decisions, protected-boundary crossings, merge verdict, domain workflow results, and the next action priority.

`shipguard-verdict.json` also includes `configurationBaseline`, `contractFindings`, and raw/effective scope checks. For example, `scopeChecks.rawForbiddenTouched` records all protected files in the diff, while `scopeChecks.forbiddenTouched` records only the unsuppressed protected files that still affect the verdict.

Blocked and review results always include `nextAction` with:

- `owner`
- `command`
- `expectedArtifact`
- `successCondition`
- `failureMeaning`

For a runnable public demo, see [Verify-First Quickstart](verify-first-quickstart.md) and `examples/verify-first/`.

## Product Rule

Every future high-value ShipGuard workflow should either read, enrich, or verify the task contract. Reports that do not affect scope, evidence, claims, or verdict are secondary diagnostics.
