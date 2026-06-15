# Prompt Pack

Copy these prompts into Codex when adapting the workflow to another app. Replace bracketed values with project-specific details.

## Bug Triage

```text
Inspect this bug before editing.

Bug:
[paste report]

Read the nearest AGENTS.md and only the files needed to identify the owner area.

Return:
- expected behavior
- current failure
- reproduction input or source evidence
- likely owner files
- risk class
- narrowest validation command
- open questions that block implementation

Do not change files yet.
```

## Bug Fix

```text
Implement the smallest safe fix for this bug.

Use this triage summary:
[paste summary]

Constraints:
- keep the change limited to the named owner files unless inspection proves another owner is required
- update or add a focused test near the behavior
- do not touch release/status/proof files
- if validation is blocked, state the exact blocker instead of claiming success

After implementation, run:
[paste validation command]
```

## UI Polish Pass

```text
Polish this UI surface without changing product behavior.

Surface:
[name screen or flow]

User job:
[state what the user is trying to do]

Constraints:
- preserve existing navigation and data behavior
- keep copy truthful for permissions, payments, and reliability
- check compact layout and Dynamic Type risk
- prefer existing components and accessibility identifiers

Validation:
[paste focused UI test or screenshot/manual proof route]
```

## Release Readiness Pass

```text
Prepare a release-readiness handoff.

Candidate:
[version/build/commit]

Read the release docs and list:
- local proof already available
- local proof still required
- human/operator proof required
- blockers that cannot be solved by code
- exact next command or operator action

Do not say release-ready unless the required proof exists.
```

## Review Pass

```text
Review this diff as a maintainer.

Prioritize:
- behavioral regressions
- alarm, notification, StoreKit, persistence, localization, or release risk
- missing tests
- unsupported claims
- overbroad scope

Return findings first with file and line references.
If there are no findings, say that clearly and name remaining residual risk.
```

## Score A Run

```text
Score this Codex run using SCORECARD.md.

Run summary:
[paste final answer or PR description]

Diff:
[paste diff or file list]

Validation:
[paste commands/results]

Return category scores, total score, and the one improvement that would most improve maintainer confidence.
```
