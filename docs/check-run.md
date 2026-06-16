# Check Run Payload

`codex-maintainer check-run` converts `gate.json` into a GitHub Checks API payload.

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

The reusable `actions/ci-gate` action writes `check-run/payload.json` into the artifact bundle. It does not post the check run by default; teams can inspect the payload first and then decide whether to call the GitHub Checks API.
