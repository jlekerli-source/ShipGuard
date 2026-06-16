# Check Run Payload

`codex-maintainer check-run` converts `gate.json` into a GitHub Checks API payload. `codex-maintainer check-run post` can post that payload when a workflow explicitly opts in.

```bash
./bin/codex-maintainer check-run \
  --gate /tmp/codex-gate/gate.json \
  --head-sha "$GITHUB_SHA" \
  --out /tmp/codex-gate/check-run/payload.json
```

The payload includes:

- check name
- commit SHA
- completed status
- conclusion derived from gate status
- title, summary, and artifact references

Conclusion mapping:

| Gate status | Check conclusion |
| --- | --- |
| `pass` | `success` |
| `blocked` | `failure` |
| other | `neutral` |

## Post A Check Run

Posting is disabled by default. In GitHub Actions, grant `checks: write`, then pass `GITHUB_TOKEN` through the environment:

```bash
./bin/codex-maintainer check-run post \
  --payload /tmp/codex-gate/check-run/payload.json \
  --repo "$GITHUB_REPOSITORY" \
  --out /tmp/codex-gate/check-run/response.json
```

Use `--dry-run` to verify the request URL, payload SHA-256, and token presence without contacting GitHub:

```bash
./bin/codex-maintainer check-run post \
  --payload /tmp/codex-gate/check-run/payload.json \
  --repo owner/repo \
  --out /tmp/codex-gate/check-run/dry-run.json \
  --dry-run
```

The dry-run output never writes the token value.

## Reusable Action

The reusable `actions/ci-gate` action writes `check-run/payload.json` into the artifact bundle. It does not post the check run unless `post-check-run: "true"` is set.
