# SARIF Evidence Export

`codex-maintainer sarif` converts an Autopsy `report.json` into SARIF 2.1.0.

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out /tmp/autopsy-dangerous

./bin/codex-maintainer sarif \
  --report /tmp/autopsy-dangerous/report.json \
  --out /tmp/autopsy-dangerous/results.sarif
```

Severity mapping:

| Autopsy severity | SARIF level |
| --- | --- |
| `high` | `error` |
| `medium` | `warning` |
| other | `note` |

`codex-maintainer ci-gate` also writes `sarif/results.sarif` into its artifact bundle and references it from `gate.json`.

The SARIF output is meant for CI systems and code-scanning consumers that understand SARIF. It does not claim the findings are source-code vulnerabilities; it preserves them as maintainer evidence findings from the Autopsy report.
