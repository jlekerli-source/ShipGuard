# Release Proof Consumption Checklist

Use this checklist before trusting a published toolkit release.

- [ ] Download release assets with `gh release download v3.141.0 --repo jlekerli-source/ShipGuard`.
- [ ] Confirm these assets are present: `shipguard-v3.141.0.tar.gz`, `release-manifest.json`, `release-index.json`, `proof-ledger.md`, `replay-report.json`, `attestation.json`, and `attestation-badge.json`.
- [ ] Run `shasum -a 256 /tmp/shipguard-v3.141.0/shipguard-v3.141.0.tar.gz`.
- [ ] Run `shipguard release-consume verify --dir /tmp/shipguard-v3.141.0 --out /tmp/shipguard-v3.141.0/consumer-proof --version 3.141.0`.
- [ ] Run `shipguard release-replay verify` against the downloaded tarball, manifest, index, and ledger.
- [ ] Run `shipguard release-attest build` against the downloaded manifest and your local `consumer-replay/replay-report.json`.
- [ ] Confirm local replay status is `pass`.
- [ ] Confirm local attestation status is `pass`, blocked checks are `0`, and the badge says `pass v3.141.0`.
- [ ] Confirm the manifest release URL, tag, commit, and artifact SHA-256 match the GitHub release being reviewed.
- [ ] Reject the release if the tarball contains `.git`, `dist`, cache paths, local machine paths, or secret-looking tokens.
- [ ] Save the local replay and attestation files in the release review notes.
