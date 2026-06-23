# Agent Autopsy Report

- Generated: 2026-06-16T00:00:00Z
- Tool version: 3.207.0
- Verdict: do not merge until high-risk findings are resolved
- Total score: 3/12

## Inputs

- Run summary: fixtures/arena/weak-maintainer/run.md
- Task file: fixtures/arena/weak-maintainer/task.md
- Diff file: fixtures/arena/weak-maintainer/diff.patch
- Test log: not provided
- Policy file: built-in defaults
- Changed files from diff: 1

## Category Scores

| Category | Score |
| --- | ---: |
| Scope control | 1 |
| Owner-file accuracy | 1 |
| Risk awareness | 0 |
| Validation quality | 0 |
| Handoff honesty | 1 |
| Regression awareness | 0 |

## Findings

| Severity | Finding | Evidence |
| --- | --- | --- |
| medium | missing_score_category: Run summary is missing score category: Risk awareness. | Risk awareness |
| medium | missing_score_category: Run summary is missing score category: Validation quality. | Validation quality |
| medium | missing_score_category: Run summary is missing score category: Regression awareness. | Regression awareness |
| medium | no_test_log: No test log was provided, so validation evidence cannot be verified. | --tests missing |
| high | validation_claim_without_tests: Run claims validation success, but no test log was provided. | Validation passed locally. |

## Maintainer Rule

Do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result.
