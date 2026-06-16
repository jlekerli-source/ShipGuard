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

## Aggregate Metrics

`results.json` includes:

- case count
- average total score
- high-risk finding count
- validation evidence case count and ratio
- validation quality average
- scope control average

The first public fixture pack includes good, weak, and dangerous maintainer runs so the benchmark shows both clean evidence and failure modes.
