# ShipGuard Product Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn ShipGuard from a broad toolkit into the local policy, context, evidence, and verdict layer for high-risk Codex changes, starting with production iOS apps.

**Architecture:** Keep the public product centered on one proof-gated loop: inspect repository context, prepare a task contract, execute through Codex, verify the exact diff and evidence, then return PASS, REVIEW, or BLOCKED with one exact next action. Keep evals running beside every phase so real-app learning becomes public-safe fixtures instead of private-app remediation work.

**Tech Stack:** Python CLI scripts in `scripts/`, shell tests in `tests/`, public fixtures in `fixtures/`, Codex plugin metadata in `plugins/ios-shipguard/`, docs in `README.md`, `ROADMAP.md`, and `docs/`.

---

## File Structure

- Modify `ROADMAP.md`: public phase map, release ladder, eval gates, and current priorities.
- Modify `docs/product-strategy.md`: product center, roadmap discipline, command demotion rules, and exit gates.
- Modify `scripts/task_contract.py` and related tests during the Task Object phase.
- Modify `scripts/ios_report_quality.py`, `tests/ios_report_quality_test.sh`, and `fixtures/ios-report-quality/` during the report-quality discipline phase.
- Modify `scripts/profile_audit.py`, `scripts/profile_fix_plan.py`, `scripts/shipguard_cli.py`, and command docs only when a phase explicitly needs command consolidation.
- Modify `plugins/ios-shipguard/` only when the Codex skill/plugin behavior changes.

## Phase 1: Report-Quality Discipline, v3.110-v3.114

**Purpose:** Finish the read-only product-QA loop without expanding public scope.

- [ ] Promote grouped performance observation evidence into a public fixture.

Run:

```bash
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-app-a-v3110 \
  --reports /tmp/shipguard-readonly-app-b-v3110 \
  --out /tmp/shipguard-readonly-quality-v3110 \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3110/fixture-candidates
```

Expected: `priorityAction` names the grouped performance observation fixture question, and generated fixture candidates contain no private paths, app identifiers, screenshots, or target-app remediation tasks.

- [ ] Add public synthetic fixture coverage for that priority.

Create or update:

```text
fixtures/ios-report-quality/grouped-performance-observation/
```

Expected fixture contents:

```json
{
  "sourceTool": "shipguard ios performance",
  "fixtureType": "ios-performance-report-quality-fixture",
  "sourceQuestion": "Which grouped performance observation should become a public fixture or eval case before changing scanner heuristics again?"
}
```

- [ ] Validate that fixture scoring does not recurse forever.

Run:

```bash
./bin/shipguard ios report-quality \
  --reports fixtures/ios-report-quality/grouped-performance-observation \
  --out /tmp/shipguard-grouped-performance-quality \
  --shareable
```

Expected: status `pass`, `sourceMaterializedFixture: true`, and no new fixture candidates for the same covered question.

- [ ] Repeat this phase for performance evidence-promotion, exact next-action completeness, design inventory boundaries, and AI-readiness de-scoping.

Exit gate: report-quality turns repeated real-app weaknesses into public-safe fixtures, suppresses covered repeat questions, and names the next uncovered ShipGuard product improvement.

## Phase 2: Trust Hardening, v3.115-v3.124

**Purpose:** Make ShipGuard trustworthy before adding more capability.

- [ ] Add canonical configuration.

Create:

```text
.shipguard.yml
docs/configuration.md
tests/config_test.sh
```

Required config sections:

```yaml
profile: ios
shareableOutput: true
protectedPaths: []
validationCommands: []
manualProof: []
redaction:
  localPaths: true
  tokens: true
```

- [ ] Add baseline and suppression support.

Create:

```text
.shipguard-baseline.json
docs/baselines.md
tests/baseline_test.sh
```

Every suppression must include `ruleId`, `reason`, `createdAt`, and `reviewAfter`.

- [ ] Unify redaction.

Move duplicated redaction logic into one script module and verify:

```bash
./tests/redaction_test.sh
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/performance-runtime-boundary --out /tmp/redaction-quality --shareable
```

- [ ] Harden trust boundaries.

Run:

```bash
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./tests/package_release_test.sh
./tests/self_audit_test.sh
```

Expected: trust-hardening receipts remain pass and failure fixtures still fail intentionally.

Exit gate: a fresh developer can install ShipGuard and get a useful first result without seeing app-specific templates, internal ShipYard work, unsafe shell interpolation, or unclear data-boundary behavior.

## Phase 3: Task Object Core, v3.125-v3.139

**Purpose:** Make one durable local task object connect scope, evidence, claims, and verdict.

- [ ] Stabilize `shipguard prepare`.

Required JSON fields:

```json
{
  "taskId": "SG-LOCAL-0001",
  "goal": "Add provisional notification onboarding",
  "projectSnapshot": {},
  "riskClassification": {},
  "protectedBoundaries": [],
  "authorizedFiles": [],
  "approvalPolicy": {
    "allowedAutomatically": [],
    "allowedAfterAgentReview": [],
    "requiresHumanApproval": [],
    "forbiddenInThisTask": [],
    "manualOnlyProof": []
  },
  "validationContract": {},
  "nextAction": {}
}
```

- [ ] Stabilize `shipguard verify`.

Verification must inspect:

```text
diff
changed files
deleted tests
validation receipts
manual proof receipts
agent claims
protected-boundary crossings
```

- [ ] Add exact next-action enforcement.

Every non-pass verdict must include:

```json
{
  "owner": "developer",
  "command": "xcodebuild test ...",
  "expectedArtifact": "TestSummaries.plist",
  "successCondition": "NotificationPermissionTests pass",
  "failureMeaning": "Notification behavior remains unproven"
}
```

- [ ] Route existing iOS checks into the task object.

Do not remove compatibility commands yet. Add fields that allow `ios doctor`, `ios inventory`, `ios performance`, `ios design`, and `ios modernize` to enrich `projectSnapshot`, `riskClassification`, `validationContract`, or `nextAction`.

Exit gate: a prepared task, Codex diff, validation log, and completion claim produce one clear PASS, REVIEW, or BLOCKED verdict without manual report stitching.

## Phase 4: Killer Workflow, v3.140-v3.159

**Purpose:** Make iOS notification and permission work the first exceptional workflow.

- [ ] Build the fixture matrix.

Fixture cases:

```text
notDetermined to provisional
denied-state recovery
authorized-state no-op
notification scheduling truth
background and killed-state proof gap
simulator-only limitation
physical-device prompt proof
agent overclaim with missing manual proof
```

- [ ] Add workflow-specific owner mapping.

Expected ownership signals:

```text
UNUserNotificationCenter
authorizationStatus
requestAuthorization
Info.plist notification usage strings
notification scheduling services
onboarding notification views
```

- [ ] Add workflow-specific validation discovery.

Validation must separate:

```text
local unit tests
simulator UI proof
manual physical-device proof
release-only proof
```

- [ ] Run external pilot tasks only after fixtures pass.

Record:

```text
Did ShipGuard prevent unsafe scope?
Did ShipGuard select better tests?
Did ShipGuard reject unsupported claims?
Did ShipGuard reduce review time?
Was the next action independently executable?
```

Exit gate: independent iOS developers complete risky notification or permission changes with ShipGuard and can execute the next action without author help.

## Phase 5: Diff-First Verification, v3.160-v3.179

**Purpose:** Answer whether this exact AI-generated change is safe enough to review or merge.

- [ ] Inspect diff-level risk.

Signals:

```text
changed protected files
new entitlements
plist changes
deleted or skipped tests
validation command mismatch
manual proof still missing
agent claims unsupported by evidence
```

- [ ] Add local learning.

Persist only local, inspectable state:

```text
accepted ownership mappings
known validation commands
approved suppressions
last successful proof lane
repeated agent mistakes
dismissed findings
manual proof requirements
```

- [ ] Add PR and CI adapters after local verdict quality is proven.

Exit gate: ShipGuard gives a better review decision for a real diff than a broad repository scan.

## Phase 6: Evaluated iOS Assurance Packs, v3.180-v3.199

**Purpose:** Add measured iOS packs only when each pack has hard evals.

- [ ] StoreKit and entitlements: sandbox transaction and entitlement fixtures.
- [ ] Persistence and migrations: compiler-backed migration examples and regression tests.
- [ ] Widgets, App Intents, and shared state: ownership and shared-store proof.
- [ ] Background execution and lifecycle: simulator/device limitation boundaries.
- [ ] Performance: source suspicion promoted only by runtime evidence.
- [ ] Design: screenshots, flow context, accessibility inspection, interaction proof, and human or calibrated model labels.
- [ ] Modernization: compiler-backed Swift/iOS upgrade examples.

Exit gate: every stable pack hits its precision, recall, false-positive, next-action, and independent task-completion targets.

## Phase 7: v4 Productization

**Purpose:** Ship a smaller, stable, externally usable product.

- [ ] Collapse the public story toward `init`, `inspect`, `prepare`, `verify`, and `doctor`.
- [ ] Keep specialist checks behind profiles and task packs.
- [ ] Publish stable schemas and migration support.
- [ ] Provide clean install, upgrade, uninstall, and release verification.
- [ ] Publish public-safe benchmark results and adoption evidence.
- [ ] Keep security posture strong enough for a proof-centered tool.

Exit gate: ShipGuard is recommendable because it catches unsafe changes, selects better proof, rejects unsupported claims, and gives exact next actions.

## Validation Commands For Roadmap Slices

Run these after roadmap-only edits:

```bash
git diff --check
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check-roadmap
```

Run these after product-surface or CLI edits:

```bash
git diff --check
./bin/shipguard validate
./tests/cli_smoke_test.sh
./tests/self_audit_test.sh
./tests/package_release_test.sh
```

Run focused test files for the changed command family before the broad checks.

## Self-Review Notes

- The roadmap does not claim the v3.110 slice is the full product plan.
- The roadmap keeps private Ringly and Ilmify evidence as ShipGuard product QA only.
- The roadmap demotes broad public command expansion until the proof-gated loop is stronger.
- The roadmap separates model evaluation from hard product truth unless calibrated against labels.
