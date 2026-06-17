# Maintainer Arena

Maintainer Arena runs multiple public agent-run fixtures through Agent Autopsy and writes aggregate benchmark output.

## Command

```bash
./bin/shipguard arena run \
  --fixture fixtures/arena \
  --out /tmp/arena
```

Outputs:

- `/tmp/arena/results.json`
- `/tmp/arena/index.md`
- `/tmp/arena/runs/<case-id>/report.md`
- `/tmp/arena/runs/<case-id>/report.json`

## Fixture Format

Each case is a directory under the fixture root:

```text
fixtures/arena/<case-id>/run.md
fixtures/arena/<case-id>/task.md
fixtures/arena/<case-id>/diff.patch
fixtures/arena/<case-id>/tests.log
```

Only `run.md` is required. Missing task, diff, or test evidence is passed through to Autopsy and can affect findings.

## Import External Packs

External fixture packs can be validated and copied into a local arena directory:

```bash
./bin/shipguard arena import \
  --source external-pack \
  --out /tmp/imported-arena-pack \
  --pack-name "external-pack"

./bin/shipguard arena run \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-results
```

The importer:

- requires `run.md` in every case directory
- copies only `run.md`, `task.md`, `diff.patch`, and `tests.log`
- rejects unsupported files, nested directories, and symlinked fixture entries
- rejects overlapping source and output directories
- writes `PACK.md` with the source basename, import time, and case IDs
- refuses to overwrite existing cases unless `--force` is passed
- rejects obvious local machine paths and secret-looking strings

## Sign And Verify Packs

After importing a pack, write deterministic integrity metadata:

```bash
./bin/shipguard arena sign \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-pack/PACK.json \
  --pack-name "external-pack" \
  --signer "Example Maintainers" \
  --signer-url "https://github.com/example/repo"
```

Verify a pack before running it:

```bash
./bin/shipguard arena verify \
  --fixture /tmp/imported-arena-pack \
  --manifest /tmp/imported-arena-pack/PACK.json
```

`PACK.json` includes case IDs, supported file paths, byte counts, file SHA-256 values, and a pack-level SHA-256 content digest. When `--signer` is provided, it also includes signer metadata plus an `identity_digest` that fails verification if the signer fields are edited later.

The signer fields are provenance metadata for public review. They are intentionally not private-key signing; use them to identify the fixture publisher while keeping the pack digest reproducible.

## Aggregate Metrics

`results.json` includes:

- case count
- average total score
- high-risk finding count
- validation evidence case count and ratio
- validation quality average
- scope control average

The public fixture pack includes clean, weak, dangerous, failing-validation, missing-diff, review-only, backend webhook, frontend async-state, docs release-proof drift, CLI cleanup, security token-leakage, generated artifact cleanup bypass, GitHub posting without dry-run, release asset trust-bypass, and StoreKit entitlement regression maintainer runs so the benchmark shows multiple evidence and failure modes.

## Compare Runs

Compare two Arena result files when the fixture pack, scoring policy, or agent run set changes:

```bash
./bin/shipguard arena compare \
  --left /tmp/arena-old/results.json \
  --right /tmp/arena-new/results.json \
  --out /tmp/arena-compare
```

The comparison writes `arena-compare.json` and `arena-compare.md` with case-count, average-score, high-risk-finding, added-case, removed-case, changed-case, and unchanged-case deltas. The summary status is `regressed` when score, high-risk findings, or removed cases move in the wrong direction.

Use `actions/arena-compare` when the same comparison should run in GitHub Actions and upload `arena-compare.json` plus `arena-compare.md` as a workflow artifact.
