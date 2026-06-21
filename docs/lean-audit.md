# ShipGuard Lean Deck

`shipguard lean audit` is a read-only audit for code that may not need to exist.
It looks for native platform replacements, standard-library replacements, small dependency cleanup opportunities, thin wrappers, and safety boundaries where less code would be dangerous without proof.

```bash
./bin/shipguard lean audit \
  --path . \
  --out /tmp/shipguard-lean-audit \
  --mode full \
  --shipguard-eval \
  --shareable
```

Outputs:

- `lean-audit.json`
- `lean-audit.md`

The report uses a ShipGuard-native Lean Deck inspired by Ponytail's “best code is the code you never wrote” ladder, but it does not vendor Ponytail code. Source influence stays explicit so ShipGuard remains honest open source.

Use `--mode` to choose the intensity:

- `lite`: name smaller alternatives while preserving implementation momentum.
- `full`: default proof ladder, balancing delete/simplify pressure with safety gates.
- `ultra`: cleanup mode; try deletion and non-existence proof before adding or refactoring code.

The selected mode is written to `leanMode`, mirrored in Markdown, and biases `precisionReview.topActions` so the first action matches the requested intensity. Lean Review also emits `modeBiasReview`, which records the selected priority order, proves the first top action came from that order, and lists the supported `lite`, `full`, and `ultra` contracts so mode behavior is not hidden in prose.

Lean Deck also emits `behaviorGates`:

- `oneRunnableCheck`: diff review expects one smallest runnable check for non-trivial new logic.
- `hardwareCalibration`: hardware, sensor, timing, and physical-device code keeps calibration proof visible.
- `requestedExplanation`: explicitly requested reports or walkthroughs are not treated as clutter.
- `adapterBoundary`: thin plugin, hook, MCP, or agent adapters are keep-with-proof boundaries, not automatic delete targets.
- `gainHonesty`: benchmark impact is shown separately from current-repo evidence.

`nativeOpportunityCatalog` gives maintainers a compact platform-native checklist across browser controls, browser APIs, CSS, Python, Node, and database capabilities before they add code or dependencies.

For current changes, use diff review instead of a whole-repo scan:

```bash
git diff > /tmp/change.diff
./bin/shipguard lean review \
  --path . \
  --diff /tmp/change.diff \
  --out /tmp/shipguard-lean-review \
  --mode full \
  --shipguard-eval \
  --shareable
```

`lean review` writes `lean-review.json` and `lean-review.md` with one-line diff findings plus a mode-aware precision ledger. It also emits `modeBiasReview`, so `lite` starts from suggestion-first rows, `full` follows the default proof ladder, and `ultra` starts from delete-first rows when deletion proof exists. `currentDiffDecisionMap` is a current-diff-only changed-file map with delete, simplify, keep, proof-blocked, or clean decisions, a `deleteOrSimplifyList`, a whole-repo non-claim, and a `shipguard lean audit` fallback for maintainers who actually need repo inventory. `safetyBoundaryReview` lists keep-with-proof rows for security, validation, data-loss, permission, and accessibility changes, plus a no-automatic-deletion policy and false deletion pressure counts. `hardwareHostBoundaryReview` separates hardware calibration proof rows from host-adapter keep rows, so physical-device behavior and plugin/MCP/preview/simulator/platform adapters are not treated as removable wrappers without calibration, protocol, call-site, or runtime proof. Repeated diff findings are also rendered as a `Grouped Action Plan`, so a maintainer sees the first experiment, validation route, and stop condition before chasing individual changed lines. It also emits `proofSignalCalibration`, `proofSignalMatching`, and `runnableCheckReview`: if non-trivial code changes are paired with a matching changed test file or assertion signal in the same diff, Lean Review records the file-scoped match instead of blindly reporting a missing runnable check. Unrelated tests stay visible as unmatched proof signals and do not count as global proof. The Markdown `Mode Bias Review`, `Safety Boundary Review`, `Runnable Check Review`, and `Proof Signal Matching` tables then separate rows that should start first from rows that must be kept with proof, still need one smallest runnable check, or need same-diff proof review before merge. It is the native ShipGuard equivalent of a Ponytail-style “what can this change delete or avoid?” review.

Repo-level audits skip public fixtures, examples, tests, generated packages, and scanner maintenance manifests by default so demo code does not dominate the findings. The JSON `scanScope` records skipped directory names, skipped files, file limits, and whether the scan was truncated. If you point `--path` directly at a fixture or demo repo, ShipGuard scans that target normally.

Large-file findings include a `leanEvidence` packet instead of only saying “this file is big.” The packet records line count, legacy/TODO marker count, first marker lines, marker filtering policy, safety context, and a first-action hint. Lean Deck counts TODO/FIXME markers and comment-line legacy/temporary/compatibility markers; it intentionally ignores incidental strings and API names such as `Legacy SiriKit`, compatibility labels, or `NamedTemporaryFile`. The Markdown report mirrors that in a Lean Evidence Packets table so a maintainer can start with a small marker cluster instead of staring at a giant file.

Lean Deck also emits `precisionReview`, a ShipGuard-native Ponytail-style action ledger:

- `deleteList`: private thin wrappers or needless helper surfaces that may be removable after search proof.
- `simplifyFirst`: native, standard-library, or dependency replacements to try before writing more code.
- `keepList`: safety-boundary files where less-code pressure is not enough.
- `blockedByProof`: large or risky candidates that need call-site evidence before edits.
- `actionGroups`: repeated findings grouped by decision, rule, first experiment, validation route, and stop condition.
- `topActions`: the first few concrete bets a maintainer should inspect.
- `cleanStateAction`: the pass-state handoff when there are no delete, simplify, or proof-blocked action groups. It names the first proof probe, next command, validation route, and stop condition so a clean report does not send a maintainer chasing a missing action group.

It also emits `leanDebtLedger`, a native version of Ponytail's shortcut ledger.
Any `ponytail:` or `shipguard-lean:` comment should name both a ceiling and an
upgrade trigger, for example:

```ts
// shipguard-lean: use the native parser here. ceiling: only one query string shape. upgrade: replace when repeated-key support is required.
```

Markers without an upgrade trigger are reported as `needs-trigger` so intentional
simplifications stay visible instead of turning into permanent mystery debt.
Standalone `lean debt` also emits `markerVisibilityReview`, which summarizes
total markers, visible rows, omitted rows, rows with ceilings, rows missing
ceilings, rows with upgrade triggers, rows needing upgrade triggers, and rows
with explicit upgrade status. The Markdown renders this review before the raw
ledger table so a maintainer can see which shortcut will rot without opening
JSON or re-scanning source.

For a ledger-only pass:

```bash
./bin/shipguard lean debt \
  --path . \
  --out /tmp/shipguard-lean-debt \
  --shipguard-eval \
  --shareable
```

`lean debt` writes `lean-debt.json` and `lean-debt.md`.

For the benchmark-backed impact card:

```bash
./bin/shipguard lean gain \
  --path . \
  --out /tmp/shipguard-lean-gain \
  --shipguard-eval \
  --shareable
```

`lean gain` writes `lean-gain.json` and `lean-gain.md`. It reports Ponytail-style benchmark direction but explicitly marks current-repo savings as `not-computed`; the unbuilt baseline was never produced, so ShipGuard must not claim fake line, token, cost, or time savings for a live repo. Current-repo proof is routed through structured `currentRepoBoundary.evidenceRoutes`: `lean audit` for source-scan simplification candidates, `lean review` for current-diff decisions, and `lean debt` for shortcut-ledger evidence.
`ios report-quality` enforces that boundary: Lean Gain reports must keep benchmark scope, metric pairs, copy-ready current-repo evidence routes, expected artifacts, proof boundaries, non-claims, and Markdown no-claim language visible.

## What It Checks

- Does this code need to exist?
- Can the standard library do it?
- Can the native platform do it?
- Is an installed dependency already enough?
- Can one clear line replace a helper?
- Only then, what is the minimum code that works?
- Is this a host adapter, hardware calibration path, explicitly requested explanation, or one-check minimum that should be kept instead of cut?

## Safety Boundary

Lean Deck is intentionally conservative around security, validation, data-loss handling, payments, migrations, permissions, and accessibility. Those files are marked as proof-required safety boundaries, not as generic deletion targets.

Use `ios report-quality` on Lean Deck output when improving ShipGuard itself:

```bash
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-lean-audit \
  --out /tmp/shipguard-lean-quality \
  --shareable
```
