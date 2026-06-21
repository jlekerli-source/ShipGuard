# Synthetic Lean Deck Priority Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does precisionReview identify delete, simplify, keep, and proof-blocked decisions instead of dumping findings?

## Behavior Gates

- `oneRunnableCheck`: Non-trivial new logic should leave one smallest runnable check.
- `hardwareCalibration`: Hardware and physical-device code needs calibration or tuning proof before simplification.
- `requestedExplanation`: Explicitly requested reports and walkthroughs are not clutter.
- `adapterBoundary`: Thin host adapters are keep-with-proof boundaries.
- `gainHonesty`: Benchmark direction is not a current-repo savings claim.

## Precision Review

- Delete candidates: 1; simplify candidates: 1; keep boundaries: 1; proof-blocked candidates: 1; action groups: 1

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | proof-blocked | `large-legacy-file-review` | 2 | scripts/example.py:12 | Open the first marker line and prove one branch before splitting. | Run call-site search plus the focused behavior test before editing. | Stop if search or focused tests show the code is still active product behavior. |

### Individual Starting Points

| Rank | Decision | Location | Action | Proof |
| ---: | --- | --- | --- | --- |
| 1 | delete | scripts/example.py:4 | Inline or delete the wrapper if search proves it adds no policy, naming, compatibility, or test value. | Use search results to confirm no public contract depends on it. |

## Report Quality Questions

- Does precisionReview identify delete, simplify, keep, and proof-blocked decisions instead of dumping findings?
