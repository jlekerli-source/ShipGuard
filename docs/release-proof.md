# Release Proof Bundle

`codex-maintainer release-proof build` runs the full local release proof chain in one command.

```bash
./bin/codex-maintainer release-proof build \
  --out /tmp/codex-maintainer-release-proof-bundle \
  --release-url https://github.com/owner/repo/releases/tag/v3.20.0 \
  --issue-url https://github.com/owner/repo/issues/123
```

Outputs:

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

The command wraps:

```text
package_release.sh -> release-manifest -> release-index -> release-replay -> release-attest
```

It requires `--release-url` so the proof bundle is anchored to a public release tag URL. The URL must end with `/releases/tag/vX.Y.Z`.

After publishing, use `release-proof-consumption.md` to replay the uploaded assets from a clean download directory.
