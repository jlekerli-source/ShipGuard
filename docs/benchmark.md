# Public AI Maintainer Reliability Benchmark

The v1 benchmark is a stable public format for comparing maintainer-style AI runs against evidence.

It is intentionally small:

- fixture tasks live under `fixtures/arena/`
- `codex-maintainer arena run` generates per-case autopsy reports and aggregate arena results
- `codex-maintainer leaderboard build` converts arena results into `leaderboard.json`

## Build

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
./bin/codex-maintainer leaderboard build \
  --arena-results /tmp/arena/results.json \
  --out /tmp/leaderboard.json
```

Compare benchmark runs before publishing a changed fixture pack:

```bash
./bin/codex-maintainer arena compare \
  --left /tmp/arena-previous/results.json \
  --right /tmp/arena-current/results.json \
  --out /tmp/arena-compare
```

Use `actions/arena-compare` to publish the same comparison as a GitHub Actions artifact and optionally fail CI when the comparison status is `regressed`.

## Leaderboard Format

`leaderboard.json` uses schema version `1.0` and includes:

- benchmark name
- generated timestamp
- task IDs and max scores
- agent entries
- average score
- high-risk finding count
- validation evidence ratio
- scope-control average
- per-task scores and verdicts

The checked-in leaderboard is a fixture baseline across ten public maintainer cases. It is not an adoption or model-quality claim.
