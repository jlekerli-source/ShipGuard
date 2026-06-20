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

Repo-level audits skip public fixtures, examples, tests, generated packages, and scanner maintenance manifests by default so demo code does not dominate the findings. The JSON `scanScope` records skipped directory names, skipped files, file limits, and whether the scan was truncated. If you point `--path` directly at a fixture or demo repo, ShipGuard scans that target normally.

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
