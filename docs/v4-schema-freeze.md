# ShipGuard V4 Schema Freeze

`shipguard v4 schema-freeze` is the contract-freeze checkpoint for the v4 track. It does not publish ShipGuard v4. It reads the ShipGuard checkout and writes a report that records the schema registry, compatibility policy, compatibility fixtures, migration checks, changelog policy, deprecation policy, release-readiness commands, and blocked claims.

## Usage

```bash
./bin/shipguard v4 schema-freeze \
  --path . \
  --out /tmp/shipguard-v4-schema-freeze \
  --shipguard-eval \
  --shareable
```

Outputs:

- `v4-schema-freeze.json`
- `v4-schema-freeze.md`

Use `--json` or `--markdown` to write only one format.

## Compatibility Policy

The v4 schema contract is frozen only when the local checks pass.

- Additive JSON fields are allowed.
- Field renames or removals require compatibility fixtures, changelog policy, migration checks, and report-quality proof.
- Deprecated fields stay readable for at least two minor releases unless they leak secrets or create unsafe claims.
- Shareable reports must continue to redact local paths, private app data, screenshots, URLs, and tokens.

## Compatibility Fixtures

The Tool Value Gauntlet runs the public fixture at `fixtures/tool-value-gauntlet/v4-schema-freeze-receipts/schema-contract/receipt.json`.

That fixture proves:

- `shipguard v4 schema-freeze` emits useful JSON and Markdown.
- The report keeps `releaseClaim` as `not-released`.
- The schema registry, compatibility policy, compatibility fixtures, migration checks, changelog policy, deprecation policy, release readiness, blocked claims, scope boundary, report-quality questions, and result UX are present.
- `shipguard ios report-quality` can score the schema-freeze report.
- `shipguard docs-check` still passes after the schema-freeze docs are added.

## Migration Checks

Run the migration lane in this order:

1. `./bin/shipguard v4 preview --path . --out /tmp/shipguard-v4-preview --shipguard-eval --shareable`
2. `./bin/shipguard v4 schema-freeze --path . --out /tmp/shipguard-v4-schema-freeze --shipguard-eval --shareable`
3. `./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet`
4. `./tests/package_release_test.sh`

The value gauntlet should no longer report `runtimeV4SchemaFreeze` as missing once the schema-freeze receipts pass. The next product gap should move to v4 release-candidate readiness.

## Changelog Policy

Any schema-affecting change must name:

- The command or report affected.
- The schema or field affected.
- Whether compatibility is additive, deprecated, migrated, or breaking.
- The migration proof and fixture proof that make the change safe.

## Deprecation Policy

- Keep deprecated fields readable for at least two minor releases.
- Require package proof, report-quality proof, and a migration note before removal.
- Remove unsafe fields immediately only when they leak secrets or private app data, and record the security reason.

## Blocked Claims

This command freezes the local v4 schema contract. It does not claim:

- ShipGuard v4 is released.
- OpenAI or any marketplace has accepted ShipGuard.
- A third party has audited ShipGuard.
- Any private app was validated.
- Simulator or schema fixtures prove physical-device behavior.

## Release-Candidate Follow-Up

After schema freeze passes, the next useful ShipGuard slice is v4 release-candidate readiness: fresh install, upgrade, uninstall, release-proof consumption, external adoption packet, final schema docs, and plugin refresh proof.
