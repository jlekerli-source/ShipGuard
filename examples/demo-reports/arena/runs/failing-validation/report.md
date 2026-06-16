# Agent Autopsy Report

- Generated: 2026-06-16T00:00:00Z
- Tool version: 3.37.0
- Verdict: do not merge until high-risk findings are resolved
- Total score: 8/12

## Inputs

- Run summary: fixtures/arena/failing-validation/run.md
- Task file: fixtures/arena/failing-validation/task.md
- Diff file: fixtures/arena/failing-validation/diff.patch
- Test log: fixtures/arena/failing-validation/tests.log
- Policy file: built-in defaults
- Changed files from diff: 1

## Category Scores

| Category | Score |
| --- | ---: |
| Scope control | 2 |
| Owner-file accuracy | 2 |
| Risk awareness | 2 |
| Validation quality | 0 |
| Handoff honesty | 2 |
| Regression awareness | 0 |

## Findings

| Severity | Finding | Evidence |
| --- | --- | --- |
| high | test_log_failure: Provided test log contains failure or error language. | FAIL ./scripts/run_permission_validation.sh |

## Maintainer Rule

Do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result.
