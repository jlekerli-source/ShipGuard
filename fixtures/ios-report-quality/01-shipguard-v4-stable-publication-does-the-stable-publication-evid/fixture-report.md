# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source tool: `shipguard v4 stable-publication`

# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: Release notes do not yet explicitly describe stable-v4 publication proof.
- Proof source: releaseNotesProof
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.
- Next command: `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable`
- Next action: Complete `releaseNotesProof` before claiming stable-v4 publication.


## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `pass` |
| `releaseNotesProof` | `review` |
| `releaseCandidatePacketProof` | `not-provided` |
| `publishedReleaseAssetProof` | `not-provided` |
| `postReleaseConsumerProof` | `not-provided` |
| `externalAdoptionEvidenceStableGate` | `not-provided` |
| `securityReviewEvidenceStableGate` | `not-provided` |

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `1/7`
- First blocking gate: `releaseNotesProof`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `review` |
| `launchkey-candidate-packet` | `not-provided` |
| `downloaded-release-assets` | `not-provided` |
| `post-release-consumer-proof` | `not-provided` |
| `independent-adoption-evidence` | `not-provided` |
| `final-security-review-evidence` | `not-provided` |

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `6`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `release-notes` | `review` | `True` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | The public release body must include stable-v4 claims, proof boundaries, assets, consumer proof, adoption, security review, and non-claim language. |
| `2` | `launchkey-candidate-packet` | `not-provided` | `False` | `./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --download-release-assets --github-release-repo <owner/repo> --release-version <version> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | A prior LaunchKey release-candidate report must pass every required install, upgrade, rollback, asset, adoption, security, plugin, and package-hygiene proof gate. |
| `3` | `downloaded-release-assets` | `not-provided` | `False` | `./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --release-assets <downloaded-assets-dir> --release-version <version> --shipguard-eval --shareable` | Release assets must be downloaded or supplied and consumed by release-consume verification. |
| `4` | `post-release-consumer-proof` | `not-provided` | `False` | `./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>` | A consumer proof must verify the published release assets outside the local build-only path. |
| `5` | `independent-adoption-evidence` | `not-provided` | `False` | `./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable` | Independent public adoption evidence must pass structure, redaction, and independence checks; fixture evidence is not enough. |
| `6` | `final-security-review-evidence` | `not-provided` | `False` | `./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable` | Final security review evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings. |

### Release Notes Closure Kit

- Missing topics: `stable-v4-claim, downloaded-release-assets, post-release-consumer-proof, final-security-review-evidence`
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
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable
```

### LaunchKey Candidate Closure Kit

- Candidate report path: `not-provided`
- Nested blocking receipt: `releaseCandidatePacketProof`
- Nested blocking status: `not-provided`
- Nested blocking summary: No LaunchKey release-candidate report was supplied; stable publication needs prior package install, upgrade, and rollback proof.
- Fixture candidate proof counts as stable-v4 publication proof: `False`

| LaunchKey proof area | Receipt | Status | Stable-publication gate |
| --- | --- | --- | --- |
| Fresh package install | `freshInstallPackageProof` | `not-reported` | `launchkey-candidate-packet` |
| Same-prefix upgrade | `upgradePackageProof` | `not-reported` | `launchkey-candidate-packet` |
| Rollback cleanup | `rollbackPackageProof` | `not-reported` | `launchkey-candidate-packet` |
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
./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --download-release-assets --github-release-repo <owner/repo> --release-version <version> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable
```

Rerun the full stable-publication gate after LaunchKey passes:

```bash
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable
```

### Evidence Closure Kit: `independent-adoption-evidence`

- Starter path: `stable-publication-evidence-kit/external-adoption-evidence.json`
- Template path: `templates/stable-publication/external-adoption-evidence.template.json`
- Attach argument: `--external-adoption-evidence stable-publication-evidence-kit/external-adoption-evidence.json`
- Accepted evidence classes: `public-external, private-redacted-external`
- Required fields: `schemaVersion, evidenceType, evidenceClass, actorRelationship, generatedAt, status, privateDataRedacted, commands, artifacts, outcome, nonClaims`
- Required scope: `not-required`
- Private data redacted required: `True`
- Current gate: `not-provided`
- Current error: `none`
- Evidence records: `None` total, `None` valid, `None` stable-v4 eligible

Pass criteria:

- At least one JSON record has status=pass.
- evidenceType is shipguard-external-adoption.
- evidenceClass is public-external or private-redacted-external.
- actorRelationship is independent.
- privateDataRedacted is true.
- commands, artifacts, outcome, and nonClaims are present.
- fixtureSynthetic is not true.
- The record is public-shareable or summary-shareable with consent/privacy reviewed.

Fail criteria:

- The unchanged template or generated starter file is submitted as evidence.
- status is not pass.
- privateDataRedacted is not true.
- actorRelationship is not independent.
- fixtureSynthetic is true.
- Evidence relies only on GitHub downloads or maintainer-only runs.
- The record contains local paths, private app identifiers, screenshots with private data, tokens, or account data.

Rerun after attaching real evidence:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable
```

### Evidence Closure Kit: `final-security-review-evidence`

- Starter path: `stable-publication-evidence-kit/security-review-evidence.json`
- Template path: `templates/stable-publication/security-review-evidence.template.json`
- Attach argument: `--security-review-evidence stable-publication-evidence-kit/security-review-evidence.json`
- Accepted evidence classes: `public-security-review, private-redacted-security-review`
- Required fields: `schemaVersion, evidenceType, evidenceClass, reviewerRelationship, generatedAt, status, privateDataRedacted, scope, methodology, commands, artifacts, findingsSummary, nonClaims`
- Required scope: `cli, plugin, github-actions, release-proof, package-install, redaction-privacy`
- Private data redacted required: `True`
- Current gate: `not-provided`
- Current error: `none`
- Evidence records: `None` total, `None` valid, `None` stable-v4 eligible

Pass criteria:

- At least one JSON record has status=pass.
- evidenceType is shipguard-security-review.
- evidenceClass is public-security-review or private-redacted-security-review.
- privateDataRedacted is true.
- scope covers cli, plugin, github-actions, release-proof, package-install, and redaction-privacy.
- methodology, commands, artifacts, findingsSummary, and nonClaims are present.
- findingsSummary.criticalOpen is 0 and findingsSummary.highOpen is 0.
- fixtureSynthetic is not true.

Fail criteria:

- The unchanged template or generated starter file is submitted as evidence.
- status is not pass.
- privateDataRedacted is not true.
- required security scope is missing.
- findingsSummary.criticalOpen or findingsSummary.highOpen is not 0.
- fixtureSynthetic is true.
- The record claims zero risk instead of reporting scope, findings, and residual risk.
- The record contains local paths, private app identifiers, screenshots with private data, tokens, or account data.

Rerun after attaching real evidence:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable
```

## Release Notes Proof

- Notes digest: `1406862bd17a3ea91efba613932e7d678b5ba4aa4b2f762bbf316c3ef9b00451`
- Missing topics: `stable-v4-claim, downloaded-release-assets, post-release-consumer-proof, final-security-review-evidence`

| Topic | Status | Matched terms |
| --- | --- | --- |
| `stable-v4-claim` | `missing` | none |
| `publication-proof-boundary` | `pass` | release proof |
| `downloaded-release-assets` | `missing` | none |
| `post-release-consumer-proof` | `missing` | none |
| `independent-adoption-evidence` | `pass` | external adoption |
| `final-security-review-evidence` | `missing` | none |
| `non-claims-boundary` | `pass` | blocked claim, blocked claims |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `stable-v4-claim, downloaded-release-assets, post-release-consumer-proof, final-security-review-evidence`

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
- Release-consume required: `True`
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
./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable
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

## Proof Summary

- GitHub release metadata: `None`
- Release notes: `review`
- LaunchKey package packet: `None`
- Release assets: `None`
- Post-release consumer proof: `None`
- External adoption stable gate: `None`
- Security review stable gate: `None`
- Stable v4 release claim allowed: `False`

## Blocked Claims

- Do not claim stable v4 until this report status is pass.
- Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.
- Do not treat GitHub release download counts as independent adoption evidence.
- Do not include private app paths, screenshots, identifiers, or token-like text in shareable proof.

## Report Quality Questions

- Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?

## Scope Boundary

- `purpose`: `Synthetic public fixture for ShipGuard report-quality behavior.`
- `shipguardOnly`: `True`
- `targetAppsReadOnly`: `True`
