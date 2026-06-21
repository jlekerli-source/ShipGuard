# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source tool: `shipguard v4 stable-publication`
- Source question: Does the post-release consumer closure row expose release-consume paths, missing proof artifacts, digest/replay/attestation statuses, repair/pass criteria, release-consume rerun, full stable-publication rerun, and source-only/fixture-proof boundaries?

# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: 2 stable-v4 publication blocker(s) remain; first blocker: No downloaded release assets were supplied; stable v4 proof still needs consumer-side release asset verification.
- Proof source: publishedReleaseAssetProof
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.
- Next command: `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --download-release-assets --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable`
- Next action: Work the stablePublicationClosureChecklist in dependency order; first complete `publishedReleaseAssetProof` before claiming stable-v4 publication.


## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `pass` |
| `releaseNotesProof` | `pass` |
| `releaseCandidatePacketProof` | `pass` |
| `publishedReleaseAssetProof` | `not-provided` |
| `postReleaseConsumerProof` | `not-provided` |
| `externalAdoptionEvidenceStableGate` | `pass` |
| `securityReviewEvidenceStableGate` | `pass` |

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `5/7`
- First blocking gate: `publishedReleaseAssetProof`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `not-provided` |
| `post-release-consumer-proof` | `not-provided` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `2`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `downloaded-release-assets` | `not-provided` | `True` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --download-release-assets --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable` | Release assets must be downloaded or supplied and verified from the publication packet, not assumed from source state. |
| `2` | `post-release-consumer-proof` | `not-provided` | `False` | `./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>` | Post-release consumer proof must come from release-consume verification of the downloaded or supplied assets. |

### Release Asset Closure Kit

- Status: `not-provided`
- Download source: `not-provided`
- Download proof status: `not-provided`
- Release version: `3.131.0`
- Assets directory: `not-provided`
- Required assets: `attestation-badge.json, attestation.json, proof-ledger.md, release-index.json, release-manifest.json, replay-report.json, shipguard-v3.131.0.tar.gz`
- Metadata missing assets: `none`
- Local downloaded assets: `none`
- Missing local assets: `attestation-badge.json, attestation.json, proof-ledger.md, release-index.json, release-manifest.json, replay-report.json, shipguard-v3.131.0.tar.gz`
- Consumer report status: `not-provided`
- Asset digest matrix path: `not-provided`
- Exit code: `not-provided`
- Error: `none`
- Downloaded or supplied assets required: `True`
- GitHub metadata only counts as release-asset proof: `False`
- Source-only proof counts as release-asset proof: `False`
- Fixture proof counts as stable-v4 publication proof: `False`

Repair criteria:

- Use `shipguard v4 stable-publication --download-release-assets` to download the public GitHub release assets, or pass the already downloaded asset directory with `--release-assets`.
- Confirm the downloaded or supplied directory contains every required release asset listed by the GitHub release metadata, including the versioned ShipGuard tarball.
- Do not edit source files, fixture outputs, or generated report JSON to close this gate; repair the public release assets or the supplied downloaded asset directory.
- After the assets are present, rerun `shipguard v4 stable-publication` so the downloaded-release-assets gate and the downstream post-release consumer gate are evaluated together.

Pass criteria:

- GitHub release metadata for the requested tag exists and is not draft-only or prerelease-only.
- Every required stable-publication asset is present in the public GitHub release metadata.
- The assets are downloaded by stable-publication or supplied through `--release-assets` from the exact published release packet.
- The stable-publication report records `publishedReleaseAssetProof.status = pass`; source checkout files, local build output, and fixture assets do not count.

Fail criteria:

- No downloaded or supplied release-assets directory is available.
- The release metadata is missing one or more required assets.
- The downloaded or supplied directory does not contain every required release asset.
- GitHub release asset download fails or points at a draft, prerelease, wrong tag, wrong repository, or wrong version.
- Source-only package tests, LaunchKey fixtures, generated report directories, or local package builds are treated as published release assets.

Rerun release asset proof:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --download-release-assets --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
```

Rerun the full stable-publication gate after release assets pass:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --download-release-assets --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
```

### Post-Release Consumer Closure Kit

- Status: `not-provided`
- Consumer report status: `not-provided`
- Consumer report path: `not-provided`
- Asset digest matrix path: `not-provided`
- Missing proof artifacts: `consumer-report.json, asset-digests.json`
- Download source: `not-provided`
- Download proof status: `not-provided`
- Release version: `not-provided`
- Assets directory: `not-provided`
- Consume output directory: `not-provided`
- Exit code: `not-provided`
- Error: `none`
- Digest freshness status: `not-provided`
- Required digest assets: `not-provided`
- Missing required digest assets: `none`
- Missing SHA-256 digest assets: `none`
- Release tarball digest matches consumer artifact: `None`
- Release-consume required: `True`
- Asset digest matrix must cover required assets: `True`
- Release tarball digest must match consumer artifact: `True`
- Source-only proof counts as consumer proof: `False`
- Fixture proof counts as stable-v4 publication proof: `False`

| Consumer crosscheck | Status |
| --- | --- |
| Replay | `not-provided` |
| Attestation | `not-provided` |
| Published replay report | `not-provided` |
| Published attestation | `not-provided` |
| Published badge | `not-provided` |

Repair criteria:

- Download the published release assets with `shipguard v4 stable-publication --download-release-assets` or supply the exact downloaded asset directory with `--release-assets`.
- Run `shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>` and keep both `consumer-report.json` and `asset-digests.json` with the stable-publication packet.
- Repair missing or mismatched release assets, replay proof, attestation proof, badge proof, manifest, index, ledger, or tarball digest before rerunning stable-publication.
- After `release-consume verify` passes, rerun `shipguard v4 stable-publication` with the same release metadata, LaunchKey, adoption, and security inputs so later gates remain visible.

Pass criteria:

- `shipguard release-consume verify` exits 0.
- `consumer-report.json` exists and reports `status = pass`.
- `asset-digests.json` exists and lists the downloaded release assets with SHA-256 and byte counts.
- Replay and attestation status are `pass` or explicitly verified as matching published assets.
- The stable-publication report records `postReleaseConsumerProof.status = pass` from the consumed release assets, not from source-only or fixture proof.

Fail criteria:

- No downloaded or supplied release-assets directory is available.
- `release-consume verify` times out, exits non-zero, or cannot run from the current checkout.
- `consumer-report.json` is missing, malformed, or reports a non-pass status.
- `asset-digests.json` is missing, incomplete, or shows missing required release assets.
- Replay, attestation, published crosscheck, version, or tarball SHA-256 proof is blocked or mismatched.
- Source checkout tests, package fixtures, or draft release notes are treated as post-release consumer proof.

Rerun release-consume proof:

```bash
./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>
```

Rerun the full stable-publication gate after consumer proof passes:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --download-release-assets --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
```

## Release Notes Proof

- Notes digest: `1cc7b6c54184ecde88b9133805de4530eec2d81de91e139e41be86aa963e7d0f`
- Missing topics: `none`

| Topic | Status | Matched terms |
| --- | --- | --- |
| `stable-v4-claim` | `pass` | stable-v4, stable v4 |
| `publication-proof-boundary` | `pass` | publication proof, release proof |
| `downloaded-release-assets` | `pass` | downloaded release asset, release asset |
| `post-release-consumer-proof` | `pass` | post-release consumer, consumer proof, release consume |
| `independent-adoption-evidence` | `pass` | independent adoption, adoption evidence |
| `final-security-review-evidence` | `pass` | final security, security review |
| `non-claims-boundary` | `pass` | non-claim, blocked claim, blocked claims |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `none`

| File | Purpose |
| --- | --- |
| `stable-publication-release-notes/release-notes-checklist.json` | Machine-readable checklist for the stable-publication release-notes topics. |
| `stable-publication-release-notes/draft-release-notes.md` | Draft-only release notes section that includes every required stable-publication proof topic. |
| `stable-publication-release-notes/README.md` | Human instructions for adapting the draft into the public GitHub release body. |

Next command template:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable
```

## Evidence Templates

- Draft-only templates: `True`

| Template | Exists | Copy command |
| --- | --- | --- |
| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |
| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

| File | Purpose |
| --- | --- |
| `stable-publication-evidence-kit/README.md` | Human checklist for collecting the real stable-v4 publication packet. |
| `stable-publication-evidence-kit/stable-publication-checklist.json` | Machine-readable draft checklist with the seven required stable-publication gates. |
| `stable-publication-evidence-kit/external-adoption-evidence.json` | Draft-only independent adoption evidence record. Fill with real external evidence before use. |
| `stable-publication-evidence-kit/security-review-evidence.json` | Draft-only final security-review evidence record. Fill with real review evidence before use. |

Next command template:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence stable-publication-evidence-kit/external-adoption-evidence.json --security-review-evidence stable-publication-evidence-kit/security-review-evidence.json --shipguard-eval --shareable
```

## Launch Relay Drafts

- Directory: `stable-publication-launch-relay`
- Draft-only: `True`
- Approval required: `True`
- Public posting allowed: `False`
- Computer-use may post: `False`
- Status: `blocked-until-stable-publication-pass`

| File | Purpose |
| --- | --- |
| `stable-publication-launch-relay/README.md` | Human launch-relay guardrails and approval boundary. |
| `stable-publication-launch-relay/launch-relay-checklist.json` | Machine-readable draft-only launch checklist and posting policy. |
| `stable-publication-launch-relay/product-hunt-draft.md` | Draft Product Hunt launch copy; not submitted by ShipGuard. |
| `stable-publication-launch-relay/reddit-r-shipguard-draft.md` | Draft subreddit announcement; not posted by ShipGuard. |
| `stable-publication-launch-relay/x-thread-draft.md` | Draft X thread; not posted by ShipGuard. |
| `stable-publication-launch-relay/hacker-news-draft.md` | Draft Hacker News submission notes; not submitted by ShipGuard. |

Approval boundary:

Public posting, publishing, submission, or account-visible external actions require explicit human approval for that exact launch run.

## Proof Summary

- GitHub release metadata: `pass`
- Release notes: `pass`
- LaunchKey package packet: `pass`
- Release assets: `not-provided`
- Post-release consumer proof: `not-provided`
- External adoption stable gate: `pass`
- Security review stable gate: `pass`
- Stable v4 release claim allowed: `False`

## Blocked Claims

- Do not claim stable v4 until this report status is pass.
- Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.
- Do not treat GitHub release download counts as independent adoption evidence.
- Do not include private app paths, screenshots, identifiers, or token-like text in shareable proof.
- Do not publish, submit, post, schedule, or perform account-visible external launch actions without explicit human approval for that exact launch run.

## Report Quality Questions

- Can ShipGuard prove stable-v4 publication from real release metadata, release notes, downloaded assets, external adoption evidence, security evidence, and post-release consumer proof?
- Does the stable-publication report block every stable-v4 claim until independent adoption and final security evidence are attached?
- Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?
- Does the stable-publication closure checklist list every remaining blocker in dependency order with exact next commands instead of hiding lower-order blockers behind only the first failing gate?
- Does the stable-publication report provide draft-only evidence templates for independent adoption and final security review without manufacturing proof?
- Does the stable-publication report write a draft-only evidence starter kit so maintainers can collect the packet without reverse-engineering JSON shapes?
- Does the LaunchKey candidate closure row expose the supplied candidate path, nested receipt, required proof areas, package-hygiene diagnostics, repair/pass criteria, nested rerun, full stable-publication rerun, and fixture-proof boundary?
- Does the downloaded release-assets closure row expose required assets, metadata/local missing assets, download source/status, asset directory, repair/pass/fail criteria, download rerun, full stable-publication rerun, and metadata-only/source-only/fixture-proof boundaries?
- Does the post-release consumer closure row expose release-consume paths, missing proof artifacts, digest/replay/attestation statuses, repair/pass criteria, release-consume rerun, full stable-publication rerun, and source-only/fixture-proof boundaries?
- Do independent adoption and final security-review closure rows expose starter paths, required fields, redaction/privacy boundaries, pass/fail criteria, current diagnostics, and exact stable-publication rerun commands?
- Does the stable-publication report prepare guarded launch relay drafts without posting, submitting, or bypassing explicit human approval?

## Scope Boundary

- `doesNotEditTargetApps`: `True`
- `doesNotPostExternally`: `True`
- `doesNotPublishRelease`: `True`
- `privateAppsUsed`: `False`
- `shareable`: `True`
- `shipguardOnly`: `True`
- `targetAppsReadOnly`: `True`
