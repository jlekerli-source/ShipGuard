# Example Scored Run

Task: improve a quick-alarm empty-state UI test without changing alarm scheduling.

## Evidence

- The run inspected the alarm home empty-state view and the focused UI test.
- It left scheduling and notification authorization code untouched.
- It ran the focused alarm-authoring UI lane and reported simulator status.
- It did not claim physical-device alarm proof.

## Scores

- Scope control: 2
- Owner-file accuracy: 2
- Risk awareness: 2
- Validation quality: 2
- Handoff honesty: 2
- Regression awareness: 1

## Expected CLI Result

```text
Total score: 11/12
Verdict: usable maintainer-quality run
```
