# Release Proof Action

`actions/release-proof` builds the same release proof chain used by the CLI:

```text
package -> release-manifest -> release-index -> release-replay -> release-attest
```

Example workflow step:

```yaml
- name: Build release proof
  uses: jlekerli-source/ringly-codex-workflows/actions/release-proof@v3.33.0
  with:
    release-url: https://github.com/owner/repo/releases/tag/v3.33.0
    issue-url: https://github.com/owner/repo/issues/123
    out: artifacts/codex-maintainer-release-proof
```

Outputs:

- `tarball`
- `manifest`
- `replay`
- `attestation`
- `attestation-badge`

Uploaded artifact contents include:

- `codex-maintainer-vX.Y.Z.tar.gz`
- `proof/release-manifest.json`
- `proof/proof-ledger.md`
- `index/release-index.json`
- `index/release-index.md`
- `replay/replay-report.json`
- `replay/replay-report.md`
- `attestation/attestation.json`
- `attestation/attestation.md`
- `attestation/attestation-badge.json`

The action requires a `release-url` because replay verification and attestation are meant to bind artifact proof to a public release page. Use the predictable tag URL before publishing, then verify the final release after upload. For complete workflow files, see `release-proof-workflows.md`.

For the same proof chain outside GitHub Actions, use `codex-maintainer release-proof build`. For downstream verification after publishing, see `release-proof-consumption.md`.
