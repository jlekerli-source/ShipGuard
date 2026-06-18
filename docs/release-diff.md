# Release Diff Audit

`shipguard release-diff compare` compares two release proof asset directories and writes a reviewer-facing diff report.

Use it when you want to answer what changed between two published or locally built release proof bundles:

```bash
./bin/shipguard release-diff compare \
  --left /tmp/shipguard-old \
  --right /tmp/shipguard-v3.102.0 \
  --out /tmp/shipguard-release-diff
```

The input directories may be flat GitHub release downloads or nested output from `shipguard release-proof build`.

Outputs:

- `release-diff.json`
- `release-diff.md`

The report compares:

- release version, tag, commit, artifact name, artifact bytes, and artifact SHA-256
- release tarball
- release manifest
- release index JSON and Markdown
- proof ledger
- replay report JSON and Markdown
- attestation JSON and Markdown
- attestation badge

Required assets are the release tarball, `release-manifest.json`, `release-index.json`, and `proof-ledger.md`. Missing required assets block the audit. Optional proof assets are still shown as added, removed, changed, unchanged, or missing on both sides.

For GitHub Actions usage, `actions/release-diff` wraps downloading two releases, running the diff audit, and uploading the report. See `release-diff-action.md` and `examples/workflows/release-diff-compare.yml`.
