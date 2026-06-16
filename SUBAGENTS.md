# Subagent Workflow

Use subagents for large tasks when independent passes reduce risk. Keep one lead agent responsible for scope, source-of-truth updates, and final judgment.

## Roles

### Inspector

Run before implementation on unclear or risky work.

- Reads the relevant `AGENTS.md`, router docs, and touched files.
- Produces a short map of current behavior, likely owner files, validation lane, and risks.
- Does not edit source.
- Hands findings to the implementer with exact file references and open questions.

### Implementer

Run after the lead accepts the plan.

- Makes the smallest scoped change.
- Updates or adds tests close to the changed behavior.
- Avoids release/status/memory files unless a source-of-truth fact changed.
- Stops before broad refactors or protected alarm-runtime edits not in scope.

### Tester

Run after implementation.

- Runs the routed validation commands from `docs/validation-commands.md`.
- Reproduces the bug before fix when feasible.
- Classifies failures as product, infrastructure, environment, timeout, or blocked-manual.
- Returns command output paths and a concise verdict.

### Reviewer

Run after tests or before commit on high-risk changes.

- Checks for regressions, missing edge cases, overbroad scope, and incomplete validation.
- Reviews alarm trust, permission truth, rollback path, and user-facing copy.
- Does not rewrite the implementation unless asked; returns findings first.

## Coordination Rules

- The lead agent owns the plan and final answer.
- Subagents receive only the task-local context needed for their role.
- Do not assign two subagents to edit the same file area at the same time.
- Use subagents for independent discovery, verification, or disjoint implementation, not as a replacement for a scoped task contract.
- Inspector output should not include an intended fix unless the task is purely planning.
- Implementer should not claim tests passed.
- Tester should not change product code while validating.
- Reviewer should cite concrete files and lines.
- If a subagent finds a blocker, the lead decides whether to narrow scope, fix, or stop with a handoff.

## Default Split

For messy project-state or regression work, prefer this split:

1. Explorer: find current source-of-truth files and owner areas.
2. Explorer: identify the last known-good proof packet or commit.
3. Verifier: check repo root, git status, ignored generated files, and validation lane.
4. Lead: synthesize the result, choose GO/HOLD, and write the next worker prompt.

## Large Task Sequence

1. Inspector maps scope and validation.
2. Lead writes or updates `PLANS.md` fields for objective, risk, tests, and rollback.
3. Implementer makes the scoped change.
4. Tester runs the narrowest proof lane.
5. Reviewer checks the diff and validation story.
6. Lead stages only intended files and commits.
