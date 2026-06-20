# ShipGuard Lean Deck

`shipguard lean audit` is a read-only audit for code that may not need to exist.
It looks for native platform replacements, standard-library replacements, small dependency cleanup opportunities, thin wrappers, and safety boundaries where less code would be dangerous without proof.

```bash
./bin/shipguard lean audit \
  --path . \
  --out /tmp/shipguard-lean-audit \
  --shipguard-eval \
  --shareable
```

Outputs:

- `lean-audit.json`
- `lean-audit.md`

The report uses a ShipGuard-native Lean Deck inspired by Ponytail's “best code is the code you never wrote” ladder, but it does not vendor Ponytail code. Source influence stays explicit so ShipGuard remains honest open source.

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
  --shipguard-eval \
  --shareable
```

`lean review` writes `lean-review.json` and `lean-review.md` with one-line diff findings plus a precision ledger. Repeated diff findings are also rendered as a `Grouped Action Plan`, so a maintainer sees the first experiment, validation route, and stop condition before chasing individual changed lines. It is the native ShipGuard equivalent of a Ponytail-style “what can this change delete or avoid?” review.

Repo-level audits skip public fixtures, examples, tests, generated packages, and scanner maintenance manifests by default so demo code does not dominate the findings. The JSON `scanScope` records skipped directory names, skipped files, file limits, and whether the scan was truncated. If you point `--path` directly at a fixture or demo repo, ShipGuard scans that target normally.

Large-file findings include a `leanEvidence` packet instead of only saying “this file is big.” The packet records line count, legacy/TODO marker count, first marker lines, safety context, and a first-action hint. The Markdown report mirrors that in a Lean Evidence Packets table so a maintainer can start with a small marker cluster instead of staring at a giant file.

Lean Deck also emits `precisionReview`, a ShipGuard-native Ponytail-style action ledger:

- `deleteList`: private thin wrappers or needless helper surfaces that may be removable after search proof.
- `simplifyFirst`: native, standard-library, or dependency replacements to try before writing more code.
- `keepList`: safety-boundary files where less-code pressure is not enough.
- `blockedByProof`: large or risky candidates that need call-site evidence before edits.
- `actionGroups`: repeated findings grouped by decision, rule, first experiment, validation route, and stop condition.
- `topActions`: the first few concrete bets a maintainer should inspect.

It also emits `leanDebtLedger`, a native version of Ponytail's shortcut ledger.
Any `ponytail:` or `shipguard-lean:` comment should name both a ceiling and an
upgrade trigger, for example:

```ts
// shipguard-lean: use the native parser here. ceiling: only one query string shape. upgrade: replace when repeated-key support is required.
```

Markers without an upgrade trigger are reported as `needs-trigger` so intentional
simplifications stay visible instead of turning into permanent mystery debt.

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

`lean gain` writes `lean-gain.json` and `lean-gain.md`. It reports Ponytail-style benchmark direction but explicitly marks current-repo savings as `not-computed`; the unbuilt baseline was never produced, so ShipGuard must not claim fake line, token, cost, or time savings for a live repo.

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
