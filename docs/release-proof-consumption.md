# Release Proof Consumption

This guide is for maintainers, reviewers, and downstream users who want to verify a published `shipguard` release without trusting README claims alone.

For CI, use `jlekerli-source/ShipGuard/actions/release-consume@v3.173.0` to download the assets, run this verification, upload the consumer proof bundle, and fail the job when proof is invalid. Use `jlekerli-source/ShipGuard/actions/release-evidence@v3.173.0` afterward when you want a static HTML evidence artifact.

Download the release assets from GitHub:

```bash
mkdir -p /tmp/shipguard-v3.173.0
gh release download v3.173.0 \
  --repo jlekerli-source/ShipGuard \
  --pattern 'shipguard-v3.173.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --pattern 'replay-report.json' \
  --pattern 'attestation.json' \
  --pattern 'attestation-badge.json' \
  --dir /tmp/shipguard-v3.173.0
```

Use the consumer CLI for the full local verification path:

```bash
./bin/shipguard release-consume verify \
  --dir /tmp/shipguard-v3.173.0 \
  --out /tmp/shipguard-v3.173.0/consumer-proof \
  --version 3.173.0
```

The command writes `sha256.txt`, `asset-digests.json`, `asset-digests.md`, replay output, attestation output, and `consumer-report.json`. When downloaded `replay-report.json`, `attestation.json`, and `attestation-badge.json` are present, it cross-checks them against locally regenerated proof and blocks on mismatches.

For manual review, check the tarball digest:

```bash
shasum -a 256 /tmp/shipguard-v3.173.0/shipguard-v3.173.0.tar.gz
```

Replay the release proof locally:

```bash
./bin/shipguard release-replay verify \
  --manifest /tmp/shipguard-v3.173.0/release-manifest.json \
  --tarball /tmp/shipguard-v3.173.0/shipguard-v3.173.0.tar.gz \
  --index /tmp/shipguard-v3.173.0/release-index.json \
  --ledger /tmp/shipguard-v3.173.0/proof-ledger.md \
  --out /tmp/shipguard-v3.173.0/consumer-replay
```

Rebuild the compact attestation from the downloaded manifest and your local replay result:

```bash
./bin/shipguard release-attest build \
  --manifest /tmp/shipguard-v3.173.0/release-manifest.json \
  --replay /tmp/shipguard-v3.173.0/consumer-replay/replay-report.json \
  --out /tmp/shipguard-v3.173.0/consumer-attestation
```

Review these files:

- `/tmp/shipguard-v3.173.0/consumer-proof/consumer-report.json`
- `/tmp/shipguard-v3.173.0/consumer-proof/consumer-report.md`
- `/tmp/shipguard-v3.173.0/consumer-proof/asset-digests.json`
- `/tmp/shipguard-v3.173.0/consumer-proof/asset-digests.md`
- `/tmp/shipguard-v3.173.0/consumer-proof/replay/replay-report.json`
- `/tmp/shipguard-v3.173.0/consumer-proof/replay/replay-report.md`
- `/tmp/shipguard-v3.173.0/consumer-proof/attestation/attestation.json`
- `/tmp/shipguard-v3.173.0/consumer-proof/attestation/attestation.md`
- `/tmp/shipguard-v3.173.0/consumer-proof/attestation/attestation-badge.json`

Optionally export a static evidence page:

```bash
./bin/shipguard release-evidence site \
  --consume /tmp/shipguard-v3.173.0/consumer-proof \
  --out /tmp/shipguard-v3.173.0/evidence-site
```

Or build the consumer proof, optional diff proof, evidence site, and evidence index together:

```bash
./bin/shipguard release-evidence bundle \
  --assets /tmp/shipguard-v3.173.0 \
  --left /tmp/shipguard-v3.119.0 \
  --out /tmp/shipguard-v3.173.0-evidence-bundle \
  --version 3.173.0
```

Accept the release only when:

- `replay-report.json` has `"status": "pass"`.
- `attestation.json` has `"status" : "pass"` and `"blocked" : 0`.
- `attestation-badge.json` says `pass v3.173.0`.
- The manifest tag and release URL both point to the release you downloaded.
- The tarball SHA-256 from `shasum -a 256` matches the manifest artifact SHA-256.

Reject or re-check the release when:

- the tag, release URL, commit, or artifact SHA-256 disagree
- the replay report reports any blocked check
- the tarball contains `.git`, `dist`, local machine paths, cache files, or secret-looking tokens
- the proof was generated for a different repository, tag, or release page

This proof is deterministic release evidence, not a cryptographic signature. It makes release claims replayable and reviewable, but it does not replace signed tags, artifact signing, or provenance systems such as Sigstore.
