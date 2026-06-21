# Synthetic Lean Deck Safety-Boundary Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does Lean Deck separate real simplification candidates from safety-boundary files?

## Precision Review

- Simplify candidates: 1
- Keep boundaries: 1
- Proof-blocked candidates: 1
- Action groups: 2

## Behavior Gates

| Gate | Status | Policy |
| --- | --- | --- |
| Adapter boundary | policy | Thin host adapters can be the product surface; keep them unless host registration proof says they are redundant. |
| Hardware calibration | available | Hardware, sensors, clocks, and physical devices need calibration or tuning proof before simplification. |
| Requested explanation | policy | Explicitly requested reports, walkthroughs, or phase notes are not clutter. |
| One runnable check | enforced-in-lean-review | Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony. |
| Gain honesty | available-in-lean-gain | Benchmark impact is not a current-repo savings claim without a matched baseline. |
| Shortcut debt | pass | Intentional lean shortcuts need a ceiling and upgrade trigger. |

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | simplify | `native-url-components` | 1 | Sources/PlainUtility.swift:12 | Replace only the utility parser with the native API in a tiny synthetic branch. | Run the focused query parsing check before accepting the simplification. | Stop if encoding, empty values, or repeated-key checks fail. |
| 2 | keep | `do-not-cut-safety-logic-without-proof` | 1 | Sources/PaymentPermissionBoundary.swift:28 | Leave the trust-boundary file untouched and write down the missing proof. | Require focused trust-boundary tests before any simplification. | Stop if denied-state, rollback, permission, or purchase validation behavior lacks before/after proof. |

### Individual Starting Points

| Rank | Decision | Location | Action | Proof |
| ---: | --- | --- | --- | --- |
| 1 | simplify | Sources/PlainUtility.swift:12 | Try URLComponents after an encoding equivalence test. | Add checks for repeated keys, empty values, and encoding. |
| 2 | keep | Sources/PaymentPermissionBoundary.swift:28 | Do not simplify trust-boundary validation from a less-code report alone. | Attach denied-state, rollback, and purchase validation tests first. |

## Lean Debt Ledger

- Markers: 0
- Missing upgrade trigger: 0
- Omitted by limit: 0

No `ponytail:` or `shipguard-lean:` shortcut markers found.

## Report Quality Questions

- Does Lean Deck separate real simplification candidates from safety-boundary files?
