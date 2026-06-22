# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication report prepare guarded launch relay drafts without posting, submitting, or bypassing explicit human approval?

## Evidence Packet

- Packet status: `pass`
- Required evidence passed: `9/9`
- First blocking gate: `none`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `release-version-coherence` | `pass` |
| `release-asset-coherence` | `pass` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

## Public Evidence Closure

- Status: `pass`
- Starter kit: `stable-publication-evidence-kit`
- Real adoption evidence required: `True`
- Final security review required: `True`
- GitHub download counts count as adoption evidence: `False`
- Fixture evidence counts as stable-v4 evidence: `False`
- Marketplace acceptance claimed: `False`

| Evidence | Gate | Freshness | Eligible | Fresh | Stale | Starter |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `independent-adoption-evidence` | `pass` | `pass` | `1` | `1` | `0` | `stable-publication-evidence-kit/external-adoption-evidence.json` |
| `final-security-review-evidence` | `pass` | `pass` | `1` | `1` | `0` | `stable-publication-evidence-kit/security-review-evidence.json` |

Copy-ready commands:

- `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json`
- `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json`
- `./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --shipguard-eval --shareable`

Public evidence non-claims:

- GitHub stars, forks, or download counts are not independent adoption evidence.
- Fixture adoption or security records prove the tool path only.
- Security-review evidence does not imply marketplace acceptance.
- Private app evidence must stay redacted before shareable publication proof.

## External Evidence Freshness

| Evidence | Status | Reference timestamp | Fresh stable records | Stale stable records |
| --- | --- | --- | ---: | ---: |
| `independent-adoption-evidence` | `pass` | `2026-06-20T00:00:00Z` | `1` | `0` |
| `final-security-review-evidence` | `pass` | `2026-06-20T00:00:00Z` | `1` | `0` |

Freshness boundary:

- `independent-adoption-evidence` generatedAt no earlier than release manifest: `True`
- `independent-adoption-evidence` first problem: none
- `final-security-review-evidence` generatedAt no earlier than release manifest: `True`
- `final-security-review-evidence` first problem: none

## Release Version Coherence

- Status: `pass`
- Source VERSION: `0.0.0`
- Release version: `0.0.0`
- Expected tag: `v0.0.0`
- GitHub returned tag: `v0.0.0`
- Manifest version: `0.0.0`
- Package version: `0.0.0`
- Consumer report version: `0.0.0`
- Expected tarball: `shipguard-v0.0.0.tar.gz`
- Manifest artifact: `shipguard-v0.0.0.tar.gz`
- Source-only proof counts as version coherence proof: `False`

| Version comparison | Status |
| --- | --- |
| `sourceVersionMatchesRequested` | `True` |
| `metadataReturnedTagMatchesRequested` | `True` |
| `manifestVersionMatchesRequested` | `True` |
| `packageVersionMatchesRequested` | `True` |
| `consumerReportVersionMatchesRequested` | `True` |

Version coherence problems:

- none

## Release Asset Coherence

- Status: `pass`
- Expected tarball: `shipguard-v0.0.0.tar.gz`
- Required assets: `1`
- Local assets: `1`
- Digest assets: `1`
- Manifest artifact: `shipguard-v0.0.0.tar.gz`
- Digest tarball: `shipguard-v0.0.0.tar.gz`
- Manifest artifact SHA-256: `abc123`
- Digest tarball SHA-256: `abc123`
- Consumer artifact SHA-256: `abc123`
- Source-only proof counts as asset coherence proof: `False`

| Asset comparison | Status |
| --- | --- |
| `localAssetsCoverRequired` | `True` |
| `digestAssetsCoverRequired` | `True` |
| `expectedTarballInLocalAssets` | `True` |
| `manifestArtifactShaMatchesDigestTarball` | `True` |
| `consumerArtifactShaMatchesDigestTarball` | `True` |

Asset coherence problems:

- none

## Closure Checklist

- Checklist status: `pass`
- Remaining blockers: `0`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `none` | `none` | `pass` | `False` | `not-needed` | Every stable-publication gate passed. |

## Evidence Templates

- Draft-only templates: `True`

| Template | Exists | Copy command |
| --- | --- | --- |
| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |
| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `none`

## Launch Relay Drafts

- Directory: `stable-publication-launch-relay`
- Draft-only: `True`
- Approval required: `True`
- Public posting allowed: `False`
- Computer-use may post: `False`
- Status: `ready-to-stage`

| File | Purpose |
| --- | --- |
| `stable-publication-launch-relay/README.md` | Synthetic approval boundary. |
| `stable-publication-launch-relay/launch-relay-checklist.json` | Synthetic checklist. |
| `stable-publication-launch-relay/product-hunt-draft.md` | Synthetic Product Hunt draft. |
| `stable-publication-launch-relay/reddit-r-shipguard-draft.md` | Synthetic Reddit draft. |
| `stable-publication-launch-relay/x-thread-draft.md` | Synthetic X draft. |
| `stable-publication-launch-relay/hacker-news-draft.md` | Synthetic HN draft. |

Approval boundary:

Public posting, publishing, submission, or account-visible external actions require explicit human approval for that exact launch run.

## Public Release Delta

- Status: `pass`
- Source version: `0.0.0`
- Selected release: `0.0.0`
- Latest GitHub release: `0.0.0`
- Package version: `0.0.0`
- Unpublished local delta: `False`
- Stable-v4 claim covers selected public release: `True`
- Stable-v4 claim covers local checkout: `True`
- Unpublished local code counts as released: `False`

| Comparison | Value |
| --- | --- |
| `sourceVersionMatchesRequestedRelease` | `True` |
| `selectedReleaseMatchesLatestGitHubRelease` | `True` |
| `releaseManifestVersionMatchesRequestedRelease` | `True` |
| `packageAssetsVersionMatchesRequestedRelease` | `True` |
| `publicTagTargetMatchesReleaseManifestCommit` | `True` |
| `releaseAssetCoherencePassed` | `True` |
| `releaseVersionCoherencePassed` | `True` |
| `localHeadMatchesSelectedPublicReleaseCommit` | `True` |
| `localMainMatchesSelectedPublicReleaseCommit` | `True` |

## Release Visibility Handoff

- Status: `pass`
- Primary decision: `announce-current-public-release`
- Latest GitHub release: `0.0.0`
- Selected release tag: `v0.0.0`
- Unpublished local delta: `False`
- Current public release can be announced: `True`
- Local main can be announced: `True`
- Unpublished local code counts as released: `False`

| Action | Required | Status |
| --- | ---: | --- |
| `publish-new-github-release` | `False` | `pass` |
| `update-release-notes` | `False` | `pass` |
| `attach-launchkey-candidate-proof` | `False` | `pass` |
| `update-release-assets` | `False` | `pass` |
| `attach-adoption-security-evidence` | `False` | `pass` |
| `keep-current-public-release-unchanged` | `True` | `pass` |

## Final Stable V4 Claim Packet

- Claim decision: `allowed`
- Stable v4 release: `True`
- Public evidence closure: `pass`
- Public posting requires explicit approval: `True`
- Computer-use may post: `False`
- Source-only proof counts as stable v4: `False`
- Fixture proof counts as stable v4: `False`
- GitHub downloads count as adoption evidence: `False`

Copy-ready claim:

ShipGuard 0.0.0 has passed stable-v4 publication proof.

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `public-release-freshness` | `pass` |
| `release-version-coherence` | `pass` |
| `release-asset-coherence` | `pass` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

Blocked claim wording:

- OpenAI marketplace acceptance is proven.
- Public launch posts were published or submitted.
- GitHub stars, forks, or downloads prove independent adoption.
