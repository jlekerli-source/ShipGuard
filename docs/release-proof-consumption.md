# Release Proof Consumption

This guide is for maintainers, reviewers, and downstream users who want to verify a published `codex-maintainer` release without trusting README claims alone.

For CI, use `jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.19.0` to download the assets, run this verification, upload the consumer proof bundle, and fail the job when proof is invalid. Use `jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.19.0` afterward when you want a static HTML evidence artifact.

Download the release assets from GitHub:

```bash
mkdir -p /tmp/codex-maintainer-v3.19.0
gh release download v3.19.0 \
  --repo jlekerli-source/ringly-codex-workflows \
  --pattern 'codex-maintainer-v3.19.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --pattern 'replay-report.json' \
  --pattern 'attestation.json' \
  --pattern 'attestation-badge.json' \
  --dir /tmp/codex-maintainer-v3.19.0
```

Use the consumer CLI for the full local verification path:

```bash
./bin/codex-maintainer release-consume verify \
  --dir /tmp/codex-maintainer-v3.19.0 \
  --out /tmp/codex-maintainer-v3.19.0/consumer-proof \
  --version 3.19.0
```

The command writes `sha256.txt`, `asset-digests.json`, `asset-digests.md`, replay output, attestation output, and `consumer-report.json`. When downloaded `replay-report.json`, `attestation.json`, and `attestation-badge.json` are present, it cross-checks them against locally regenerated proof and blocks on mismatches.

For manual review, check the tarball digest:

```bash
shasum -a 256 /tmp/codex-maintainer-v3.19.0/codex-maintainer-v3.19.0.tar.gz
```

Replay the release proof locally:

```bash
./bin/codex-maintainer release-replay verify \
  --manifest /tmp/codex-maintainer-v3.19.0/release-manifest.json \
  --tarball /tmp/codex-maintainer-v3.19.0/codex-maintainer-v3.19.0.tar.gz \
  --index /tmp/codex-maintainer-v3.19.0/release-index.json \
  --ledger /tmp/codex-maintainer-v3.19.0/proof-ledger.md \
  --out /tmp/codex-maintainer-v3.19.0/consumer-replay
```

Rebuild the compact attestation from the downloaded manifest and your local replay result:

```bash
./bin/codex-maintainer release-attest build \
  --manifest /tmp/codex-maintainer-v3.19.0/release-manifest.json \
  --replay /tmp/codex-maintainer-v3.19.0/consumer-replay/replay-report.json \
  --out /tmp/codex-maintainer-v3.19.0/consumer-attestation
```

Review these files:

- `/tmp/codex-maintainer-v3.19.0/consumer-proof/consumer-report.json`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/consumer-report.md`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/asset-digests.json`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/asset-digests.md`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/replay/replay-report.json`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/replay/replay-report.md`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/attestation/attestation.json`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/attestation/attestation.md`
- `/tmp/codex-maintainer-v3.19.0/consumer-proof/attestation/attestation-badge.json`

Optionally export a static evidence page:

```bash
./bin/codex-maintainer release-evidence site \
  --consume /tmp/codex-maintainer-v3.19.0/consumer-proof \
  --out /tmp/codex-maintainer-v3.19.0/evidence-site
```

Or build the consumer proof, optional diff proof, evidence site, and evidence index together:

```bash
./bin/codex-maintainer release-evidence bundle \
  --assets /tmp/codex-maintainer-v3.19.0 \
  --left /tmp/codex-maintainer-v3.18.0 \
  --out /tmp/codex-maintainer-v3.19.0-evidence-bundle \
  --version 3.19.0
```

Accept the release only when:

- `replay-report.json` has `"status": "pass"`.
- `attestation.json` has `"status" : "pass"` and `"blocked" : 0`.
- `attestation-badge.json` says `pass v3.19.0`.
- The manifest tag and release URL both point to the release you downloaded.
- The tarball SHA-256 from `shasum -a 256` matches the manifest artifact SHA-256.

Reject or re-check the release when:

- the tag, release URL, commit, or artifact SHA-256 disagree
- the replay report reports any blocked check
- the tarball contains `.git`, `dist`, local machine paths, cache files, or secret-looking tokens
- the proof was generated for a different repository, tag, or release page

This proof is deterministic release evidence, not a cryptographic signature. It makes release claims replayable and reviewable, but it does not replace signed tags, artifact signing, or provenance systems such as Sigstore.
