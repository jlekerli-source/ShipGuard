# Release Evidence Bundle

`codex-maintainer release-evidence bundle` builds the downstream release evidence path in one local command.

Use it after downloading a published release asset set:

```bash
./bin/codex-maintainer release-evidence bundle \
  --assets /tmp/codex-maintainer-v3.28.0 \
  --left /tmp/codex-maintainer-v3.19.0 \
  --out /tmp/codex-maintainer-v3.28.0-evidence-bundle \
  --version 3.28.0 \
  --title "Codex Maintainer v3.28.0 Evidence" \
  --index-title "Codex Maintainer Release Evidence"
```

Outputs:

- `consumer-proof/consumer-report.json`
- `consumer-proof/asset-digests.json`
- `release-diff/release-diff.json` when `--left` is provided
- `site/index.html`
- `site/evidence.json`
- `index/index.html`
- `index/evidence-index.json`
- `bundle.json`
- `README.md`

The bundle command runs `release-consume verify`, optionally runs `release-diff compare`, exports the evidence site, builds a local evidence index, and writes `bundle.json` as the machine-readable manifest for the whole local proof export.

Keep `--out` outside both `--assets` and `--left`; the command blocks nested output directories so generated evidence cannot contaminate release asset scans.

Use the lower-level `release-evidence site` and `release-evidence index` commands when you already have consumer or diff reports. Use `actions/release-evidence` with `run: bundle` and `download-assets: true` when this export should happen in GitHub Actions.

After publishing the bundle as a GitHub Actions artifact, run `codex-maintainer release-evidence verify --dir <artifact-dir> --out <verify-dir> --require-diff true --require-index true` or use `actions/release-evidence-verify` in a downstream job. That verifies `bundle.json`, the evidence site, copied source reports, and evidence index as a consumer would see them.
