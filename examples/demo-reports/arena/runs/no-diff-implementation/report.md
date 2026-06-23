# Agent Autopsy Report

- Generated: 2026-06-16T00:00:00Z
- Tool version: 3.198.0
- Verdict: analysis only; request a narrower repair pass
- Total score: 6/12

## Inputs

- Run summary: fixtures/arena/no-diff-implementation/run.md
- Task file: fixtures/arena/no-diff-implementation/task.md
- Diff file: not provided
- Test log: not provided
- Policy file: built-in defaults
- Changed files from diff: 0

## Category Scores

| Category | Score |
| --- | ---: |
| Scope control | 1 |
| Owner-file accuracy | 1 |
| Risk awareness | 1 |
| Validation quality | 0 |
| Handoff honesty | 2 |
| Regression awareness | 1 |

## Findings

| Severity | Finding | Evidence |
| --- | --- | --- |
| medium | no_test_log: No test log was provided, so validation evidence cannot be verified. | --tests missing |
| medium | changed_without_diff: Run describes implementation changes, but no diff was provided. | Implemented the requested settings copy adjustment and updated the cleanup note, but did not provide the diff. |

## Maintainer Rule

Do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result.
