# Task Contract

ShipGuard Task Contract is the first core loop for proof-gated Codex work:

```text
understand the repo
prepare the task scope
run Codex under that scope
verify the exact diff, evidence, and claims
return pass, review, or blocked with one next action
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
- `protectedBoundaries`
- `validationContract`
- `agentClaims`
- `evidence`
- `verdict`
- `nextAction`

Use `--allowed` and `--forbidden` to override the default scope. Use `--shipguard-eval` when a target app is only being used to evaluate ShipGuard output quality; that boundary says the report is not app-work authorization.

## Verify

Run `verify` after Codex edits:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/xcodebuild.log \
  --claim "Implemented the onboarding permission flow." \
  --out /tmp/shipguard-verdict
```

Outputs:

- `shipguard-verdict.json`
- `shipguard-verdict.md`

The verdict is:

- `pass` when changed files stay inside scope, evidence is present, and claims do not overreach.
- `review` when evidence or diff proof is missing but no protected boundary was crossed.
- `blocked` when the diff touches protected or unauthorized paths, or when an unsupported claim such as "fully verified" is made without proof.

Blocked and review results always include `nextAction` with:

- `owner`
- `command`
- `expectedArtifact`
- `successCondition`
- `failureMeaning`

## Product Rule

Every future high-value ShipGuard workflow should either read, enrich, or verify the task contract. Reports that do not affect scope, evidence, claims, or verdict are secondary diagnostics.
