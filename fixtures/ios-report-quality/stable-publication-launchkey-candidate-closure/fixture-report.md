# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source tool: `shipguard v4 stable-publication`
- Source question: Does the LaunchKey candidate closure row expose the supplied candidate path, nested receipt, required proof areas, package-hygiene diagnostics, repair/pass criteria, nested rerun, full stable-publication rerun, and fixture-proof boundary?

# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: 1 stable-v4 publication blocker(s) remain; first blocker: LaunchKey report is missing package install, upgrade, or rollback proof required for stable publication.
- Proof source: LaunchKey candidate proof
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.
- Next command: `./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable`
- Next action: Work the Closure Checklist in order; first complete LaunchKey candidate proof before claiming stable-v4 publication.


## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `pass` |
| `releaseNotesProof` | `pass` |
| `releaseCandidatePacketProof` | `review` |
| `publishedReleaseAssetProof` | `pass` |
| `postReleaseConsumerProof` | `pass` |
| `externalAdoptionEvidenceStableGate` | `pass` |
| `securityReviewEvidenceStableGate` | `pass` |

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `6/7`
- First blocking gate: `releaseCandidatePacketProof`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `review` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `1`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `launchkey-candidate-packet` | `review` | `True` | `./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable` | LaunchKey candidate proof must pass before stable publication; package install, upgrade, rollback, release-asset, adoption, and security receipts cannot be inferred. |

### LaunchKey Candidate Closure Kit

- Candidate report path: `<candidate-incomplete.json>`
- Nested blocking receipt: `freshInstallPackageProof`
- Nested blocking status: `not-provided`
- Nested blocking summary: LaunchKey report is missing package install, upgrade, or rollback proof required for stable publication.
- Fixture candidate proof counts as stable-v4 publication proof: `False`

| LaunchKey proof area | Receipt | Status | Stable-publication gate |
| --- | --- | --- | --- |
| Fresh package install | `freshInstallPackageProof` | `not-provided` | `launchkey-candidate-packet` |
| Same-prefix upgrade | `upgradePackageProof` | `not-provided` | `launchkey-candidate-packet` |
| Rollback cleanup | `rollbackPackageProof` | `not-provided` | `launchkey-candidate-packet` |
| GitHub release asset download | `githubReleaseAssetDownloadProof` | `not-reported` | `downloaded-release-assets` |
| Release-consume proof | `publishedReleaseAssetProof` | `not-reported` | `post-release-consumer-proof` |
| Independent adoption evidence | `externalAdoptionEvidenceStableGate` | `not-reported` | `independent-adoption-evidence` |
| Final security review evidence | `securityReviewEvidenceStableGate` | `not-reported` | `final-security-review-evidence` |

Repair criteria:

- Use the supplied candidate report path to inspect the LaunchKey JSON, but fix the failing LaunchKey input or package lineage instead of editing the stable-publication report.
- If package hygiene diagnostics are present, rebuild the affected tarball without AppleDouble, cache, VCS, bytecode, or unsafe archive members, then rerun `shipguard release-package hygiene`.
- Rerun `shipguard v4 release-candidate` with the rebuilt candidate package, previous release package for same-prefix upgrade proof, rollback proof, release assets when needed, and redacted evidence inputs.
- After the LaunchKey candidate report passes, rerun `shipguard v4 stable-publication` with the same publication inputs so later release notes, release assets, adoption, and security gates remain visible.

Pass criteria:

- The supplied report is from `shipguard v4 release-candidate`.
- The supplied report status is `pass`.
- releaseReadiness.releaseClaim is `candidate-ready`.
- releaseReadiness.stableV4Release is `false`.
- freshInstallPackageProof, upgradePackageProof, and rollbackPackageProof all pass.
- No nested blockingProof remains.
- No package-hygiene blocker remains for the candidate or previous release tarball.

Fail criteria:

- The LaunchKey report is missing, unreadable, or from the wrong tool.
- The LaunchKey report status is not `pass`.
- The LaunchKey report claims stable v4 instead of candidate readiness.
- Fresh install, same-prefix upgrade, or rollback cleanup proof is missing or not passing.
- A nested blocking receipt still points at package, release-asset, adoption, security, or consumer proof failure.
- Package hygiene diagnostics report unsafe archive members such as AppleDouble sidecars, `.DS_Store`, `__MACOSX`, bytecode, cache, VCS data, unsafe links/devices, or path traversal.
- Fixture candidate proof is used as stable-v4 publication proof.

Rerun the nested LaunchKey blocker:

```bash
./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable
```

Rerun the full stable-publication gate after LaunchKey passes:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <stable-publication-work>/candidate-incomplete.json --release-assets <stable-publication-work>/downloaded --external-adoption-evidence <stable-publication-work>/evidence/stable-adoption --security-review-evidence <stable-publication-work>/evidence/stable-security --shipguard-eval --shareable
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
- LaunchKey package packet: `review`
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
