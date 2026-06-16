# Release Consume

`codex-maintainer release-consume verify` verifies a directory of downloaded release proof assets and writes a consumer-facing proof report.

Use it after downloading release assets from GitHub:

```bash
mkdir -p /tmp/codex-maintainer-v3.10.0
gh release download v3.10.0 \
  --repo jlekerli-source/ringly-codex-workflows \
  --pattern 'codex-maintainer-v3.10.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --dir /tmp/codex-maintainer-v3.10.0

./bin/codex-maintainer release-consume verify \
  --dir /tmp/codex-maintainer-v3.10.0 \
  --out /tmp/codex-maintainer-v3.10.0/consumer-proof \
  --version 3.10.0
```

Inputs expected in `--dir`:

- `codex-maintainer-vX.Y.Z.tar.gz`
- `release-manifest.json`
- `release-index.json`
- `proof-ledger.md`

Outputs:

- `consumer-report.json`
- `consumer-report.md`
- `sha256.txt`
- `replay/replay-report.json`
- `replay/replay-report.md`
- `attestation/attestation.json`
- `attestation/attestation.md`
- `attestation/attestation-badge.json`

The command wraps:

```text
manifest parse -> shasum -a 256 -> release-replay verify -> release-attest build -> consumer report
```

It fails when:

- the downloaded asset directory is missing required proof files
- `--version` does not match the release manifest
- the tarball SHA-256 does not match the manifest
- replay verification reports blocked checks
- attestation generation cannot prove a passing replay

This command still does not download assets itself. Keeping download separate makes the reviewed files explicit and keeps the verifier local and deterministic.
