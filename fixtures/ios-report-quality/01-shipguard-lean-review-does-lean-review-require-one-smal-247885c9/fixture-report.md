# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does Lean Review require one smallest runnable check for non-trivial new logic?

## Current Diff Decision Map

- Scope: `current-diff-only`
- Diff: `synthetic-current-change.diff`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.
- Whole-repo fallback: `shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable`
- Decision rows: 6; delete: 1; simplify: 1; keep: 1; proof-blocked: 1; clean files: 2

| File | Decision | Added | Removed | Rules | First Experiment | Validation | Stop Condition |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| Sources/SyntheticLeanReview/FormatterShim.swift | `delete` | 6 | 0 | thin-wrapper-diff-review | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| Sources/SyntheticLeanReview/QueryBuilder.swift | `simplify` | 8 | 1 | stdlib-url-params-diff | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
| Sources/SyntheticLeanReview/PermissionGate.swift | `keep` | 5 | 0 | do-not-cut-safety-diff-without-proof | Treat this as a keep-with-proof boundary before any deletion or simplification. | Run focused permission-state behavior proof before changing this branch. | Stop if the only evidence is less-code pressure without behavior proof. |
| Sources/SyntheticLeanReview/RuleRouter.swift | `proof-blocked` | 7 | 0 | one-runnable-check-missing-diff | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |
| Sources/SyntheticLeanReview/SelectionPolicy.swift | `clean` | 6 | 0 | one-runnable-check-signal-present-diff | Review the matching same-diff test before adding any duplicate test ceremony. | Run Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift or the equivalent focused lane. | Stop if the changed same-diff test already proves the new branch and no Lean cleanup remains. |
| Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift | `clean` | 5 | 0 | - | Run the changed focused test and confirm it covers the changed selection branch. | Run the focused test lane before broader validation. | Stop if the test is unrelated to the changed logic. |

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

## Proof Signal Calibration

- Same-diff proof status: `present`
- Proof signals: 1
- Code findings covered by same-diff proof: 1
- Missing runnable-check findings: 1
- Policy: Lean Review should distinguish no proof signal from same-diff proof signal. Same-diff tests still need human relevance review, but they should not produce duplicate missing-check ceremony.

| Kind | Location | Added Lines | Signal |
| --- | --- | ---: | --- |
| test-file | Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9 | 5 | func testPrimaryOptionWins() { XCTAssertEqual(policy.pick(primary), .preferred(primary.id)) } |

## Runnable Check Review

- Missing proof findings: 1
- Same-diff proof findings: 1
- Same-diff proof signals: 1
- Duplicate ceremony avoided: 1
- Policy: Non-trivial branch, loop, parser, and collection logic should leave one smallest runnable check.
- Non-ceremony boundary: If the same diff already changes a focused test, XCTest, assertion, or explicit check signal, Lean Review records that same-diff proof signal instead of asking for duplicate test ceremony. The maintainer still needs to review relevance and run the focused check.

### Missing Runnable Checks

| Location | Recommendation | Proof |
| --- | --- | --- |
| Sources/SyntheticLeanReview/RuleRouter.swift:18 | Leave one smallest runnable check for the new routing branch instead of treating tests as optional ceremony. | Add one focused route-selection check or point to the changed test that covers this branch before merge. |

### Same-Diff Proof Signals

| Location | Recommendation | Proof Review |
| --- | --- | --- |
| Sources/SyntheticLeanReview/SelectionPolicy.swift:27 | Do not add duplicate test ceremony before checking whether the same-diff proof signal already covers this logic. | Review Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift, then run the focused test before merge. |

## Precision Ledger

- Delete candidates: 1; simplify candidates: 1; keep boundaries: 1; proof-blocked candidates: 1; action groups: 3

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| 2 | simplify | `stdlib-url-params-diff` | 1 | Sources/SyntheticLeanReview/QueryBuilder.swift:22 | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
| 3 | proof-blocked | `one-runnable-check-missing-diff` | 1 | Sources/SyntheticLeanReview/RuleRouter.swift:18 | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |
