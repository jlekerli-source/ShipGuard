# Release Evidence Site

`codex-maintainer release-evidence site` exports release proof reports as a static, self-contained evidence page.

Use it after running `release-consume verify`, and optionally after running `release-diff compare`:

```bash
./bin/codex-maintainer release-evidence site \
  --consume /tmp/codex-maintainer-v3.38.0/consumer-proof \
  --diff /tmp/codex-maintainer-release-diff \
  --out /tmp/codex-maintainer-release-site \
  --title "Codex Maintainer v3.38.0 Evidence"
```

Outputs:

- `index.html`
- `evidence.json`
- `README.md`
- `sources/consumer-report.json`
- `sources/asset-digests.json`
- `sources/release-diff.json` when `--diff` is provided

The HTML page includes release metadata, artifact SHA-256, published proof crosschecks, proof links, the asset digest matrix, and optional release-diff summary. The JSON file keeps a compact machine-readable summary for automation or archiving.

The command blocks when the consumer report is not `pass` or when an included release-diff report is not `pass`.

Use `codex-maintainer release-evidence index` when you want to collect multiple site exports into a release history. See `release-evidence-index.md`.

Use `codex-maintainer release-evidence bundle` when you want to start from downloaded release assets and produce consumer proof, optional diff proof, the site, and an index in one command. See `release-evidence-bundle.md`.

For GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.38.0` after `actions/release-consume` and optional `actions/release-diff`. See `release-evidence-action.md`.
