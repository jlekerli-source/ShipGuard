# Release Proof Consumption

This guide is for maintainers, reviewers, and downstream users who want to verify a published `codex-maintainer` release without trusting README claims alone.

Download the release assets from GitHub:

```bash
mkdir -p /tmp/codex-maintainer-v3.10.0
gh release download v3.10.0 \
  --repo jlekerli-source/ringly-codex-workflows \
  --pattern 'codex-maintainer-v3.10.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --pattern 'replay-report.json' \
  --pattern 'attestation.json' \
  --pattern 'attestation-badge.json' \
  --dir /tmp/codex-maintainer-v3.10.0
```

Use the consumer CLI for the full local verification path:

```bash
./bin/codex-maintainer release-consume verify \
  --dir /tmp/codex-maintainer-v3.10.0 \
  --out /tmp/codex-maintainer-v3.10.0/consumer-proof \
  --version 3.10.0
```

The command writes `sha256.txt`, replay output, attestation output, and `consumer-report.json`.

For manual review, check the tarball digest:

```bash
shasum -a 256 /tmp/codex-maintainer-v3.10.0/codex-maintainer-v3.10.0.tar.gz
```

Replay the release proof locally:

```bash
./bin/codex-maintainer release-replay verify \
  --manifest /tmp/codex-maintainer-v3.10.0/release-manifest.json \
  --tarball /tmp/codex-maintainer-v3.10.0/codex-maintainer-v3.10.0.tar.gz \
  --index /tmp/codex-maintainer-v3.10.0/release-index.json \
  --ledger /tmp/codex-maintainer-v3.10.0/proof-ledger.md \
  --out /tmp/codex-maintainer-v3.10.0/consumer-replay
```

Rebuild the compact attestation from the downloaded manifest and your local replay result:

```bash
./bin/codex-maintainer release-attest build \
  --manifest /tmp/codex-maintainer-v3.10.0/release-manifest.json \
  --replay /tmp/codex-maintainer-v3.10.0/consumer-replay/replay-report.json \
  --out /tmp/codex-maintainer-v3.10.0/consumer-attestation
```

Review these files:

- `/tmp/codex-maintainer-v3.10.0/consumer-proof/consumer-report.json`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/consumer-report.md`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/replay/replay-report.json`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/replay/replay-report.md`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/attestation/attestation.json`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/attestation/attestation.md`
- `/tmp/codex-maintainer-v3.10.0/consumer-proof/attestation/attestation-badge.json`

Accept the release only when:

- `replay-report.json` has `"status": "pass"`.
- `attestation.json` has `"status" : "pass"` and `"blocked" : 0`.
- `attestation-badge.json` says `pass v3.10.0`.
- The manifest tag and release URL both point to the release you downloaded.
- The tarball SHA-256 from `shasum -a 256` matches the manifest artifact SHA-256.

Reject or re-check the release when:

- the tag, release URL, commit, or artifact SHA-256 disagree
- the replay report reports any blocked check
- the tarball contains `.git`, `dist`, local machine paths, cache files, or secret-looking tokens
- the proof was generated for a different repository, tag, or release page

This proof is deterministic release evidence, not a cryptographic signature. It makes release claims replayable and reviewable, but it does not replace signed tags, artifact signing, or provenance systems such as Sigstore.
