# Codex Task Template

Use this at the start of every non-trivial Codex thread. Fill the fields before asking for implementation, verification, release work, or design changes.

```text
Repo:
Mode: audit / implement / verify / release / design / command-center
One goal:
Out of scope:
Likely touched files or area:
Validation lane:
Stop condition:
Expected result:
```

## iOS App Defaults

```text
Repo: [path-to-your-app]
Mode:
One goal:
Out of scope:
Likely touched files or area:
Validation lane:
Stop condition: pass, fail with evidence, or blocked after the stated timeout
Expected result: changed files, exact validation command, artifact path, and remaining blocker
```

## Command Center Prompt

```text
Repo: [path-to-your-app]
Mode: command-center
One goal: read the live state and choose the next highest-leverage task
Out of scope: source edits, long validation, release operations
Validation lane: docs/status inspection only
Stop condition: return GO/HOLD plus one exact worker prompt
Expected result: current state, why it matters, pasteable worker prompt, and what result I should bring back
```

## Verification Prompt

```text
Repo: [path-to-your-app]
Mode: verify
One goal:
Out of scope: source edits unless one clear failing row identifies one clear owner file
Likely touched files or area: no source edits expected
Validation lane:
Stop condition: pass, fail with packet/result path, or blocked after __ minutes
Expected result: proof matrix with command, artifact path, verdict, cleanup, and next action
```

## Creative / Game Prompt

```text
Repo:
Mode: design / implement / verify
One goal:
Primary reference:
Secondary references:
Camera:
Art style:
Non-goals:
Success checks:
Validation lane: screenshot the app, compare to reference, list top 5 deltas, patch only those
Stop condition:
Expected result:
```

## Subagent Split

```text
Use sub-agents only for independent work:
1. Explorer: find current truth and likely owner files.
2. Explorer: find last known-good proof/commit if this is a regression.
3. Verifier: check repo root, git status, ignored generated files, and validation lane.
Main agent: synthesize, decide the next action, and own the final answer.
```
