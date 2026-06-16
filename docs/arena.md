# Maintainer Arena

Maintainer Arena runs multiple public agent-run fixtures through Agent Autopsy and writes aggregate benchmark output.

## Command

```bash
./bin/codex-maintainer arena run \
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
./bin/codex-maintainer arena import \
  --source external-pack \
  --out /tmp/imported-arena-pack \
  --pack-name "external-pack"

./bin/codex-maintainer arena run \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-results
```

The importer:

- requires `run.md` in every case directory
- copies only `run.md`, `task.md`, `diff.patch`, and `tests.log`
- writes `PACK.md` with source, import time, and case IDs
- refuses to overwrite existing cases unless `--force` is passed
- rejects obvious local machine paths and secret-looking strings

## Sign And Verify Packs

After importing a pack, write deterministic integrity metadata:

```bash
./bin/codex-maintainer arena sign \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-pack/PACK.json \
  --pack-name "external-pack"
```

Verify a pack before running it:

```bash
./bin/codex-maintainer arena verify \
  --fixture /tmp/imported-arena-pack \
  --manifest /tmp/imported-arena-pack/PACK.json
```

`PACK.json` includes case IDs, supported file paths, byte counts, file SHA-256 values, and a pack-level SHA-256 content digest. This is integrity metadata for reproducibility; it is not identity signing with a private key.

## Aggregate Metrics

`results.json` includes:

- case count
- average total score
- high-risk finding count
- validation evidence case count and ratio
- validation quality average
- scope control average

The public fixture pack includes clean, weak, dangerous, failing-validation, missing-diff, review-only, backend webhook, frontend async-state, and CLI cleanup maintainer runs so the benchmark shows multiple evidence and failure modes.
