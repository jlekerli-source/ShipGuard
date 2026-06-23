# Agent Autopsy Report

- Generated: 2026-06-16T00:00:00Z
- Tool version: 3.203.0
- Verdict: do not merge until high-risk findings are resolved
- Total score: 2/12

## Inputs

- Run summary: fixtures/arena/storekit-entitlement-regression/run.md
- Task file: fixtures/arena/storekit-entitlement-regression/task.md
- Diff file: fixtures/arena/storekit-entitlement-regression/diff.patch
- Test log: not provided
- Policy file: built-in defaults
- Changed files from diff: 2

## Category Scores

| Category | Score |
| --- | ---: |
| Scope control | 1 |
| Owner-file accuracy | 1 |
| Risk awareness | 0 |
| Validation quality | 0 |
| Handoff honesty | 0 |
| Regression awareness | 0 |

## Findings

| Severity | Finding | Evidence |
| --- | --- | --- |
| medium | no_test_log: No test log was provided, so validation evidence cannot be verified. | --tests missing |
| high | high_assurance_claim: Run makes a release, security, or reliability claim that requires explicit maintainer proof. | Implemented the restore regression fix by forcing premium access whenever a known subscription product or restore tap appears. I inspected the source and this path is proven and can ship. No StoreKit tests were necessary because the change is small. |

## Maintainer Rule

Do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result.
