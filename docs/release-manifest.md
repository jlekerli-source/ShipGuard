# Release Manifest

`codex-maintainer release-manifest` generates a machine-readable release manifest and a human-readable proof ledger for a release tarball. `codex-maintainer release-manifest verify` verifies the manifest against the tarball later.

```bash
tarball="$(./scripts/package_release.sh)"

./bin/codex-maintainer release-manifest \
  --tarball "$tarball" \
  --out /tmp/codex-maintainer-release-proof \
  --ci-run-url "https://github.com/owner/repo/actions/runs/123" \
  --release-url "https://github.com/owner/repo/releases/tag/v3.7.0" \
  --issue-url "https://github.com/owner/repo/issues/37"
```

Verify the manifest before using it as release evidence:

```bash
./bin/codex-maintainer release-manifest verify \
  --manifest /tmp/codex-maintainer-release-proof/release-manifest.json \
  --tarball "$tarball"
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

Verification checks schema version, optional expected version and tag, commit presence, artifact name, byte count, SHA-256, and whether the artifact path is portable. Use `codex-maintainer release-replay verify` after downloading release assets when you also want package-entry, release-index, proof-ledger, and private-path checks. Neither command publishes a release, closes issues, or verifies remote GitHub state.
