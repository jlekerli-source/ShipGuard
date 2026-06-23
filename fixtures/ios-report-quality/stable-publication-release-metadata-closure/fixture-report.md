# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source tool: `shipguard v4 stable-publication`
- Source question: Does the GitHub release metadata closure row expose repo inference, release tag, API endpoint, release state, required/missing assets, release-note digest, repair/pass/fail criteria, rerun command, and public-metadata/source-only/fixture-API boundaries?

# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: 2 stable-v4 publication blocker(s) remain; first blocker: GitHub release metadata could not be loaded.
- Proof source: GitHub release metadata
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.
- Next command: `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable`
- Next action: Work the Closure Checklist in order; first complete GitHub release metadata before claiming stable-v4 publication.


## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `blocked` |
| `releaseNotesProof` | `review` |
| `releaseCandidatePacketProof` | `pass` |
| `publishedReleaseAssetProof` | `pass` |
| `postReleaseConsumerProof` | `pass` |
| `externalAdoptionEvidenceStableGate` | `pass` |
| `securityReviewEvidenceStableGate` | `pass` |

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `5/7`
- First blocking gate: `githubReleaseMetadataProof`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `blocked` |
| `release-notes` | `review` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `2`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `github-release-metadata` | `blocked` | `True` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --release-assets <stable-publication-work>/downloaded --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable` | Public GitHub release metadata must exist for the requested tag and must not be draft-only or prerelease-only proof. |
| `2` | `release-notes` | `review` | `False` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --release-assets <stable-publication-work>/downloaded --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable` | Public release notes must describe the stable-v4 proof packet, downloaded assets, consumer proof, adoption evidence, security review, and non-claims. |

### GitHub Release Metadata Closure Kit

- Status: `blocked`
- Repository: `jlekerli-source/ShipGuard`
- Repository inference: `not-needed` from `explicit-argument`
- Release tag: `v3.131.0`
- API URL: `<github-api-url>`
- Release endpoint: `<github-api-url>/repos/jlekerli-source/ShipGuard/releases/tags/v3.131.0`
- Release URL: `not-provided`
- Target commitish: `not-provided`
- Draft release: `False`
- Prerelease: `False`
- Required assets: `attestation-badge.json, attestation.json, proof-ledger.md, release-index.json, release-manifest.json, replay-report.json, shipguard-v3.131.0.tar.gz`
- Metadata assets: `none`
- Metadata missing assets: `none`
- Release notes SHA-256: `not-provided`
- Release notes missing topics: `none`
- Public GitHub release metadata required: `True`
- Draft or prerelease counts as stable-publication proof: `False`
- Source-only proof counts as release metadata proof: `False`
- Fixture API proof counts as stable-v4 publication proof: `False`

Repair criteria:

- Pass `--github-release-repo <owner/repo>` explicitly when the origin remote is missing, private, mirrored, or not the publication repository.
- Confirm `--release-version <version>` resolves to the exact public GitHub release tag ShipGuard should validate.
- Publish or update the GitHub release so it is not draft-only or prerelease-only and includes every required stable-publication asset.
- After repairing the repository, tag, release state, or asset list, rerun `shipguard v4 stable-publication` so release notes, downloaded assets, consumer proof, adoption, and security gates remain visible.

Pass criteria:

- The GitHub release repository is explicit or successfully inferred from `origin`.
- The release tag exists in the selected repository.
- The release is not draft-only and not prerelease-only.
- Every required stable-publication asset is present in GitHub release metadata.
- The release URL, target commitish, asset names, and release-note digest are recorded for downstream proof.

Fail criteria:

- No GitHub release repository is supplied or inferred.
- `--github-release-repo` is not in `owner/repo` form.
- The selected API endpoint cannot load the requested release tag.
- The release is draft or prerelease when stable-v4 publication proof is requested.
- GitHub metadata is missing one or more required release assets.
- A source checkout, local package build, fixture API, or generated report is treated as public release metadata proof.

Rerun release metadata proof:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --release-assets <stable-publication-work>/downloaded --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
```

### Release Notes Closure Kit

- Missing topics: `stable-v4-claim, publication-proof-boundary, downloaded-release-assets, post-release-consumer-proof, independent-adoption-evidence, final-security-review-evidence, non-claims-boundary`
- Public release edit required: `True`
- ShipGuard edits public release: `False`
- Release URL: `not-provided`

| Authoring file |
| --- |
| `stable-publication-release-notes/release-notes-checklist.json` |
| `stable-publication-release-notes/draft-release-notes.md` |
| `stable-publication-release-notes/README.md` |

Rerun after editing public release notes:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-pass.json --release-assets <stable-publication-work>/downloaded --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
```

## Release Notes Proof

- Notes digest: `not-available`
- Missing topics: `stable-v4-claim, publication-proof-boundary, downloaded-release-assets, post-release-consumer-proof, independent-adoption-evidence, final-security-review-evidence, non-claims-boundary`

| Topic | Status | Matched terms |
| --- | --- | --- |
| `stable-v4-claim` | `missing` | none |
| `publication-proof-boundary` | `missing` | none |
| `downloaded-release-assets` | `missing` | none |
| `post-release-consumer-proof` | `missing` | none |
| `independent-adoption-evidence` | `missing` | none |
| `final-security-review-evidence` | `missing` | none |
| `non-claims-boundary` | `missing` | none |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `stable-v4-claim, publication-proof-boundary, downloaded-release-assets, post-release-consumer-proof, independent-adoption-evidence, final-security-review-evidence, non-claims-boundary`

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

| Evidence class | Status | What it means |
| --- | --- | --- |
| `public-consumer-proof` | `can-be-produced-by-maintainer` | Install and verify ShipGuard from public release assets only; this proves public consumability, not adoption. |
| `private-maintainer-qa` | `useful-but-not-adoption` | Ringly, Ilmify, or other maintainer app runs may expose ShipGuard product gaps, but they do not satisfy independent adoption evidence. |
| `independent-adoption-evidence` | `requires-external-actor` | A non-maintainer user, repo, issue, PR, or redacted external install report must supply the adoption record. |
| `final-security-review-evidence` | `requires-review-record` | A security review record must cover the required ShipGuard surfaces and show no open critical or high findings. |

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

- GitHub release metadata: `blocked`
- Release notes: `review`
- LaunchKey package packet: `pass`
- Release assets: `pass`
- Post-release consumer proof: `pass`
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
