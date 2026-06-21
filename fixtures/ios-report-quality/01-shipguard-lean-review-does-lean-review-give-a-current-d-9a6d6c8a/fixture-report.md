# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?

## Current Diff Decision Map

- Scope: `current-diff-only`
- Diff: `synthetic-current-change.diff`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.
- Whole-repo fallback: `shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable`
- Decision rows: 3; delete: 1; simplify: 1; keep: 1; proof-blocked: 0; clean files: 0

| File | Decision | Added | Removed | Rules | First Experiment | Validation | Stop Condition |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| Sources/SyntheticLeanReview/FormatterShim.swift | `delete` | 6 | 0 | thin-wrapper-diff-review | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| Sources/SyntheticLeanReview/QueryBuilder.swift | `simplify` | 8 | 1 | stdlib-url-params-diff | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
| Sources/SyntheticLeanReview/PermissionGate.swift | `keep` | 5 | 0 | do-not-cut-safety-diff-without-proof | Treat this as a keep-with-proof boundary before any deletion or simplification. | Run focused permission-state behavior proof before changing this branch. | Stop if the only evidence is less-code pressure without behavior proof. |

Non-claims:
- Does not prove whole-repo inventory coverage.
- Does not prove benchmark savings, token savings, cost savings, or time savings.
- Does not authorize private target-app edits from ShipGuard product-QA runs.

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review - Non-trivial new logic should leave one smallest runnable check.
- `hardwareCalibration`: available - Hardware and physical devices need calibration proof before simplification.
- `requestedExplanation`: policy - Explicitly requested reports are not clutter.
- `adapterBoundary`: available - Thin host adapters can be the product surface.
- `gainHonesty`: available-in-lean-gain - Benchmark impact is separate from current-repo evidence.

## Precision Ledger

- Delete candidates: 1; simplify candidates: 1; keep boundaries: 1; proof-blocked candidates: 0; action groups: 2

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| 2 | simplify | `stdlib-url-params-diff` | 1 | Sources/SyntheticLeanReview/QueryBuilder.swift:22 | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
