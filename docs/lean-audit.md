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

`lean review` writes `lean-review.json` and `lean-review.md` with one-line diff findings plus a precision ledger. It is the native ShipGuard equivalent of a Ponytail-style “what can this change delete or avoid?” review.

Repo-level audits skip public fixtures, examples, tests, generated packages, and scanner maintenance manifests by default so demo code does not dominate the findings. The JSON `scanScope` records skipped directory names, skipped files, file limits, and whether the scan was truncated. If you point `--path` directly at a fixture or demo repo, ShipGuard scans that target normally.

Large-file findings include a `leanEvidence` packet instead of only saying “this file is big.” The packet records line count, legacy/TODO marker count, first marker lines, safety context, and a first-action hint. The Markdown report mirrors that in a Lean Evidence Packets table so a maintainer can start with a small marker cluster instead of staring at a giant file.

Lean Deck also emits `precisionReview`, a ShipGuard-native Ponytail-style action ledger:

- `deleteList`: private thin wrappers or needless helper surfaces that may be removable after search proof.
- `simplifyFirst`: native, standard-library, or dependency replacements to try before writing more code.
- `keepList`: safety-boundary files where less-code pressure is not enough.
- `blockedByProof`: large or risky candidates that need call-site evidence before edits.
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

## What It Checks

- Does this code need to exist?
- Can the standard library do it?
- Can the native platform do it?
- Is an installed dependency already enough?
- Can one clear line replace a helper?
- Only then, what is the minimum code that works?

## Safety Boundary

Lean Deck is intentionally conservative around security, validation, data-loss handling, payments, migrations, permissions, and accessibility. Those files are marked as proof-required safety boundaries, not as generic deletion targets.

Use `ios report-quality` on Lean Deck output when improving ShipGuard itself:

```bash
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-lean-audit \
  --out /tmp/shipguard-lean-quality \
  --shareable
```
