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
- Decision rows: 9; delete: 1; simplify: 1; keep: 2; proof-blocked: 2; clean files: 3

| File | Decision | Added | Removed | Rules | First Experiment | Validation | Stop Condition |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| Sources/SyntheticLeanReview/FormatterShim.swift | `delete` | 6 | 0 | thin-wrapper-diff-review | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| Sources/SyntheticLeanReview/QueryBuilder.swift | `simplify` | 8 | 1 | stdlib-url-params-diff | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
| Sources/SyntheticLeanReview/PermissionGate.swift | `keep` | 5 | 0 | do-not-cut-safety-diff-without-proof | Treat this as a keep-with-proof boundary before any deletion or simplification. | Run focused permission-state behavior proof before changing this branch. | Stop if the only evidence is less-code pressure without behavior proof. |
| Sources/SyntheticLeanReview/PluginHostAdapter.swift | `keep` | 5 | 0 | host-adapter-boundary-diff | Treat this as a host-adapter keep boundary until protocol or runtime proof shows it is redundant. | Run or attach the smallest plugin, MCP, preview, or runtime proof that covers the adapter boundary. | Stop if the only evidence is less-code pressure against a product-surface adapter. |
| Sources/SyntheticLeanReview/RuleRouter.swift | `proof-blocked` | 7 | 0 | one-runnable-check-missing-diff | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |
| Sources/SyntheticLeanReview/SensorSampler.swift | `proof-blocked` | 6 | 0 | hardware-calibration-missing-diff | Attach calibration, timing, or real-device evidence before removing the sensor tuning boundary. | Run or attach the smallest hardware, simulator, or timing proof that covers the changed sampling behavior. | Stop if the only evidence is source-level less-code pressure without physical-world proof. |
| Sources/SyntheticLeanReview/SelectionPolicy.swift | `clean` | 6 | 0 | one-runnable-check-signal-present-diff | Review the matching same-diff test before adding any duplicate test ceremony. | Run Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift or the equivalent focused lane. | Stop if the changed same-diff test already proves the new branch and no Lean cleanup remains. |
| Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift | `clean` | 5 | 0 | - | Run the changed focused test and confirm it covers the changed selection branch. | Run the focused test lane before broader validation. | Stop if the test is unrelated to the changed logic. |
| Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift | `clean` | 4 | 0 | - | Keep this unrelated smoke test visible as evidence that proof signals are not global. | Run only if this separate smoke path matters to the task. | Stop if a maintainer tries to count this unrelated test as proof for a different changed file. |

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
- Proof signals: 2
- Code findings covered by same-diff proof: 1
- Missing runnable-check findings: 1
- Policy: Lean Review should distinguish no proof signal from same-diff proof signal. Same-diff tests still need human relevance review, but they should not produce duplicate missing-check ceremony.

| Kind | Location | Added Lines | Signal |
| --- | --- | ---: | --- |
| test-file | Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9 | 5 | func testPrimaryOptionWins() { XCTAssertEqual(policy.pick(primary), .preferred(primary.id)) } |
| test-file | Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7 | 4 | func testUnrelatedSmokePath() { XCTAssertTrue(smokePath.isEnabled) } |

## Runnable Check Review

- Missing proof findings: 1
- Same-diff proof findings: 1
- Same-diff proof signals: 2
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

## Proof Signal Matching

- Changed code files: 7
- Non-trivial logic files: 2
- Matched same-diff proof files: 1
- Missing proof files: 1
- Unmatched proof signals: 1
- Policy: Same-diff proof is file-scoped. A changed test or assertion satisfies a changed code file only when ShipGuard can match it by same file, path stem, or meaningful path tokens.
- Non-global proof boundary: Unrelated or unmatched proof signals are listed separately and do not satisfy missing proof for other changed files; same-diff proof is not treated as global proof.

| File | Decision | Matched Proof Signals |
| --- | --- | ---: |
| Sources/SyntheticLeanReview/RuleRouter.swift | `missing-proof` | 0 |
| Sources/SyntheticLeanReview/SelectionPolicy.swift | `matched-same-diff-proof` | 1 |

### Unmatched Proof Signals

| Location | Kind | Signal |
| --- | --- | --- |
| Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift:7 | test-file | func testUnrelatedSmokePath() { XCTAssertTrue(smokePath.isEnabled) } |

## Hardware And Host Boundary Review

- Hardware calibration findings: 1
- Host adapter boundary findings: 1
- False less-code pressure blocked: 2
- Policy: Lean Review should block false less-code pressure around physical-world behavior and product-surface host adapters. Hardware needs calibration proof; host adapters need call-site or protocol proof before they are treated as removable wrappers.
- Hardware calibration policy: Hardware, sensors, clocks, and physical devices need calibration, timing, or real-device evidence before simplification removes tuning boundaries.
- Host adapter policy: Thin plugin, MCP, preview, simulator, and platform host adapters can be the product boundary. Keep them until call-site, protocol, or runtime proof shows the adapter is redundant.

### Hardware Calibration Proof

| Location | Recommendation | Proof |
| --- | --- | --- |
| Sources/SyntheticLeanReview/SensorSampler.swift:33 | Keep a minimal calibration or tuning boundary when code touches real hardware or physical-device behavior. | Attach real-device, sensor, timing, or calibration evidence before simplifying the physical-world edge case away. |

### Host Adapter Boundaries

| Location | Recommendation | Proof |
| --- | --- | --- |
| Sources/SyntheticLeanReview/PluginHostAdapter.swift:12 | Keep this host, plugin, MCP, preview, simulator, or platform adapter until call-site or protocol proof shows it is redundant. | Attach call-site, protocol, plugin, MCP, preview, or runtime proof before simplifying the adapter boundary. |

## Safety Boundary Review

- Safety-boundary findings: 1
- False deletion pressure blocked: 1
- Keep safety-boundary files: 1
- Policy: Lean Review must keep safety, trust, permission, accessibility, validation, data-loss, and security boundaries out of automatic deletion. Less-code pressure is only allowed after focused behavior proof.
- Automatic deletion boundary: A safety-boundary row is a keep-with-proof decision, even when the same file also contains cleanup pressure.

### Keep With Proof Boundaries

| Location | Recommendation | Proof |
| --- | --- | --- |
| Sources/SyntheticLeanReview/PermissionGate.swift:31 | Less code is not the goal in this file until behavior proof exists. | Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior. |

## Precision Ledger

- Delete candidates: 1; simplify candidates: 1; keep boundaries: 2; proof-blocked candidates: 2; action groups: 4

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search the changed call sites and delete the wrapper only if it is private and behavior-neutral. | Run the smallest formatter behavior check plus git diff --check. | Stop if call sites depend on naming, compatibility, logging, typing, or behavior policy. |
| 2 | simplify | `stdlib-url-params-diff` | 1 | Sources/SyntheticLeanReview/QueryBuilder.swift:22 | Try URLComponents or URLQueryItem at the changed call site before adding parser code. | Run one focused query-string behavior check plus git diff --check. | Stop if repeated keys, empty values, encoding, or malformed input behavior changes. |
| 3 | proof-blocked | `one-runnable-check-missing-diff` | 1 | Sources/SyntheticLeanReview/RuleRouter.swift:18 | Add or identify one smallest runnable route-selection check before merging the new branch. | Run the focused route-selection test plus git diff --check. | Stop if the diff has no runnable proof signal for the changed non-trivial logic. |
| 4 | proof-blocked | `hardware-calibration-missing-diff` | 1 | Sources/SyntheticLeanReview/SensorSampler.swift:33 | Attach calibration, timing, or real-device evidence before removing the sensor tuning boundary. | Run or attach the smallest hardware, simulator, or timing proof that covers the changed sampling behavior. | Stop if the only evidence is source-level less-code pressure without physical-world proof. |
