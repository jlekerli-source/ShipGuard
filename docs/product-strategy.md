# ShipGuard Product Strategy

ShipGuard's product center is not a large branded CLI, a generic agent interface, or a collection of reports.

ShipGuard is the local policy, context, and evidence layer for high-risk Codex changes, starting with production iOS apps.

The internal ambition can stay broad, but the user-facing promise must stay narrow:

```text
Understand the repository
Understand the requested change
Identify risk and protected boundaries
Generate a narrow Codex execution contract
Capture what actually happened
Verify claims against evidence
Return PASS, REVIEW, or BLOCKED with the next exact action
```

## Product Layers

ShipGuard should organize around four layers.

1. ShipGuard Core:
   project graph, risk graph, task contract, evidence ledger, and verdict engine.

2. Domain Packs:
   iOS first, then web, backend, and CLI only after the core contract is stable.

3. Adapters:
   Codex skill and plugin, Codex SDK paths, GitHub, XcodeBuildMCP, and local shell.

4. ShipGuard Development Tools:
   Arena, Value Gauntlet, Self-Audit, fixture promotion, and release proof used to improve ShipGuard itself.

Development tools are important, but they should not dominate the user-facing story.

## Near-Term Product Rule

Freeze broad public-command expansion unless a command directly supports the proof-gated change loop.

For every new public surface, answer:

- What user decision does this improve?
- What evidence does it inspect?
- What exact next action can it return?
- What task object fields does it read or enrich?
- What fixture proves it is useful?
- What existing surface should be merged or retired instead?

## Persistent Task Object

The first implementation of the durable local task object is `shipguard prepare` plus `shipguard verify`. It connects the whole change:

```json
{
  "taskId": "SG-2026-0042",
  "goal": "Add provisional notification onboarding",
  "projectSnapshot": {},
  "riskClassification": {},
  "protectedBoundaries": [],
  "authorizedFiles": [],
  "validationContract": {},
  "agentRun": {},
  "evidence": [],
  "verdict": {}
}
```

Every command in the primary workflow should eventually read or enrich that object instead of producing disconnected report folders. Diagnostics that cannot affect scope, evidence, claims, or verdict should remain secondary.

## Primary Workflow

The first killer workflow is proof-gated Codex change for risky iOS work.

Initial wedge:

```bash
shipguard prepare "Add a provisional-notification onboarding flow"
```

ShipGuard should produce:

- project summary,
- owning files,
- risk classification,
- authorized edit scope,
- protected boundaries,
- validation contract,
- manual proof requirements,
- task-specific Codex guidance.

After Codex works:

```bash
shipguard verify
```

ShipGuard should inspect the diff, commands, logs, screenshots, manual evidence, and agent claims, then return one clear verdict.

Example result shape:

```text
BLOCKED

Why:
Notification authorization code changed, but device permission prompt proof is missing.

Verified:
- Scope stayed inside authorized files.
- Permission-state unit tests passed.
- Denied-state UI path was captured.

Missing:
- Physical-device authorization prompt proof.
- Confirmation that provisional delivery works after app termination.

Next action:
Run the device notification proof checklist and attach the resulting receipt.
```

## What To Accelerate

1. Repo understanding and task routing:
   project map, ownership map, validation lane discovery, protected boundaries, risk classification, and exact next action.

2. The iOS notification and permission workflow:
   use it as the first evaluated domain pack because it combines permission truth, lifecycle state, simulator/device limits, background behavior, and agent overclaim risk.

3. Evaluation as a permanent parallel track:
   every feature needs gold fixtures, negative fixtures, mutation cases, human or expert labels when appropriate, model critique, actionability scoring, and regression gates.

4. Diff-first verification:
   after the proof-gated task contract, the next architecture step is deeper verification of the exact AI-generated diff: changed behaviors, deleted tests, validation coverage, protected boundaries, evidence, agent claims, exact next action, and verdict.

## What To Delay

Delay broad web/backend/CLI maturity until:

- the core task and evidence schemas are stable,
- the iOS proof-gated workflow demonstrates measurable value,
- external users have run real tasks,
- false-positive and precision thresholds are known,
- external maintainers request another profile.

Delay large design, performance, modernization, and AI-readiness expansions unless they can feed the task object and return an exact decision.

## What To Merge Or Demote

The mature product surface should move toward:

```text
shipguard init
shipguard inspect
shipguard prepare
shipguard verify
shipguard doctor
```

Potential merge direction:

- `ios doctor`, `ios inventory`, `app-intelligence`, and `ai-readiness` feed `inspect --profile ios`.
- `ios plan`, `spec-workflow`, `goals`, and `next-goal` feed `prepare`.
- `score`, `autopsy`, `report-quality`, `ci-gate`, `review-comment`, `check-run`, and `sarif` feed `verify` plus output adapters.
- `ios performance`, `ios design`, and `ios modernize` become iOS check packs, not standalone product pillars.
- `arena`, `leaderboard`, and fixture promotion become `shipguard eval` or maintainer-only tools.
- `brand`, `value-gauntlet`, and `self-audit` stay as ShipGuard development tools, not the main user story.
- Transcript redaction and iOS report redaction should converge into one shared redaction engine.

## Weak-Sounding Features

Command-family runtime-output receipts are useful regression coverage. They prove commands emit expected artifacts. They do not prove relevance, precision, correctness, time saved, or better user decisions. Keep them, but do not present them as a headline capability.

Design DNA is a design inventory until it uses screenshots, flow context, accessibility inspection, interaction evidence, and human labels.

Source-only performance findings are review candidates, not runtime proof. Reports should label them as source heuristics and avoid blocking unless measured evidence exists.

AI readiness is useful only when tied to a decision: on-device viability, privacy boundary, fallback requirement, model path, or support cost. Generic readiness scores should be removed or reframed.

Release evidence sites are secondary until provenance is authoritative and users repeatedly consume the evidence.

Model-evaluator bridges should not encode a single model as architecture. ShipGuard should record evaluator type, provider, model, rubric version, prompt digest, and calibration status.

## Evaluation Gates

Stable features should define target thresholds before being called dependable:

- blocking finding precision at or above 90 percent,
- critical benchmark recall at 100 percent,
- actionable precision at or above 80 percent,
- false-positive dismissal rate below 15 percent,
- exact next-action completeness at 100 percent,
- independent task completion at or above 80 percent,
- median first useful result below five minutes.

These are product goals, not current claims.

## Acquisition-Quality Assets

The valuable asset is not another agent UI or generic code scanner.

The valuable assets are:

- high-quality app-maintenance evaluation corpus,
- expert-labeled iOS task fixtures,
- task-to-proof graph,
- measurable improvement to Codex outcomes,
- Codex-native integration using skills, plugins, local policy, and evidence,
- genuine external adoption and retention,
- clean trust and security posture.

## Revised Roadmap

### Phase A: Trustworthy Foundation

- Separate maintainer templates from user starter templates.
- Keep GitHub Action input handling, Devspace URL boundaries, archive extraction safety, and release provenance covered by public regression receipts.
- Introduce one canonical configuration format.
- Create the persistent task object.
- Freeze new public commands unless tied to the proof-gated loop.
- Move internal tools toward `shipguard dev`.
- Establish schema and deprecation policy.

Exit gate: a stranger installs ShipGuard and initializes a repository without receiving ShipGuard-internal or app-specific templates.

### Phase B: Killer Workflow

- Implement `prepare`.
- Implement `verify`.
- Connect them through the task object.
- Integrate the Codex skill/plugin.
- Add task-specific protected boundaries.
- Capture diff and test evidence.
- Perfect the notification and permission workflow.
- Run external pilot tasks.

Exit gate: independent iOS developers complete risky notification changes using ShipGuard without author assistance.

### Phase C: iOS Assurance Platform

Add one evaluated domain pack at a time:

1. Notifications and permissions.
2. StoreKit and entitlements.
3. Persistence and migrations.
4. Widgets, App Intents, and shared state.
5. Background execution and lifecycle.
6. Performance with runtime evidence.
7. Design with screenshots and flow evidence.
8. Modernization with compiler-backed validation.

### Parallel Track: Evaluation Flywheel

- Real task traces.
- Human labels.
- Model critiques.
- Gold fixtures.
- Negative fixtures.
- Mutation tests.
- Calibration.
- Regression gates.
- Public-safe fixture promotion.

### Phase D: Multi-Stack Expansion

Start only after the core architecture and iOS pack succeed. Choose one profile whose users request it most rather than developing web, backend, and CLI equally by default.

### Phase E: v4 Productization

v4 requires stable task and evidence schemas, stable CLI contracts, migration support, minimal runtime package, reliable upgrade/uninstall, strong security posture, independent benchmark results, and meaningful external adoption.

## Invariant

For every Codex task, ShipGuard must help the developer make a safer and better-supported decision than they would have made without it.
