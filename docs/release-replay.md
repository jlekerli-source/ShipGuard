# Release Replay

`codex-maintainer release-replay verify` verifies downloaded release assets against the release proof files that were published with them.

```bash
gh release download v3.24.0 \
  --pattern 'codex-maintainer-v3.24.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --dir /tmp/codex-maintainer-v3.24.0

./bin/codex-maintainer release-replay verify \
  --manifest /tmp/codex-maintainer-v3.24.0/release-manifest.json \
  --tarball /tmp/codex-maintainer-v3.24.0/codex-maintainer-v3.24.0.tar.gz \
  --index /tmp/codex-maintainer-v3.24.0/release-index.json \
  --ledger /tmp/codex-maintainer-v3.24.0/proof-ledger.md \
  --out /tmp/codex-maintainer-v3.24.0/replay
```

Outputs:

- `replay-report.json`
- `replay-report.md`

The verifier checks:

- manifest schema and required identity fields
- tarball filename, byte count, and SHA-256 against the manifest
- portable artifact path
- required package runtime files
- absence of `.git`, `dist`, cache, build, and local machine path entries
- presence of public GitHub release and CI proof URLs
- optional release-index row matching version, tag, commit, and artifact SHA-256
- optional proof-ledger entries matching version, tag, release URL, and artifact SHA-256

The command is local and deterministic. It does not call the GitHub API itself; download release assets first, then replay the proof offline. Use `codex-maintainer release-attest build` after replay verification when you want a compact release-proof badge and attestation summary. For the full downstream review flow, see `release-proof-consumption.md`.
