# Release Manifest

`codex-maintainer release-manifest` generates a machine-readable release manifest and a human-readable proof ledger for a release tarball.

```bash
tarball="$(./scripts/package_release.sh)"

./bin/codex-maintainer release-manifest \
  --tarball "$tarball" \
  --out /tmp/codex-maintainer-release-proof \
  --ci-run-url "https://github.com/owner/repo/actions/runs/123" \
  --release-url "https://github.com/owner/repo/releases/tag/v3.1.0" \
  --issue-url "https://github.com/owner/repo/issues/37"
```

Outputs:

- `release-manifest.json`
- `proof-ledger.md`

The manifest records:

- schema version
- generated timestamp
- toolkit version
- release tag
- commit SHA
- tarball name, path, byte count, and SHA-256
- CI, release, and issue proof URLs when supplied

The proof ledger is meant for release notes and maintainer audits. It lists the release artifact digest and the manual checks that must be confirmed after publishing.

This command does not publish a release, close issues, or verify remote GitHub state. It creates deterministic proof files that make those release checks easier to review.
