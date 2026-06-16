# Release Attestation

`codex-maintainer release-attest build` turns a valid release manifest plus a passing replay report into a compact attestation bundle.

```bash
./bin/codex-maintainer release-attest build \
  --manifest /tmp/codex-maintainer-v3.27.0/release-manifest.json \
  --replay /tmp/codex-maintainer-v3.27.0/replay-report.json \
  --out /tmp/codex-maintainer-v3.27.0/attestation
```

Outputs:

- `attestation.json`
- `attestation.md`
- `attestation-badge.json`

The command verifies:

- manifest and replay schemas are supported
- replay status is `pass`
- replay has zero blocked checks
- version, tag, and commit match between manifest and replay
- artifact SHA-256 and byte count match between manifest and replay
- manifest includes public release and CI proof URLs

The attestation is not a cryptographic signature. It is a deterministic release-proof summary that is easy to attach to GitHub releases, display as a badge, and inspect during audits. See `release-proof-consumption.md` for the downstream verification flow.
