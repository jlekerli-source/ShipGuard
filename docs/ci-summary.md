# CI Step Summary

`codex-maintainer ci-summary` converts `gate.json` into GitHub Actions step-summary Markdown.

```bash
./bin/codex-maintainer ci-summary \
  --gate /tmp/codex-gate/gate.json \
  --out /tmp/codex-gate/summary.md
```

`codex-maintainer ci-gate` writes `summary.md` automatically. The reusable `actions/ci-gate` action appends that file to `$GITHUB_STEP_SUMMARY` when it runs in GitHub Actions.

The summary includes:

- gate status
- warn/fail mode
- score
- high-risk finding count
- threshold values
- artifact paths for Autopsy, SARIF, PR comment, and badge JSON

Use the summary for quick workflow-run triage. Use the uploaded artifact bundle for the full evidence files.
