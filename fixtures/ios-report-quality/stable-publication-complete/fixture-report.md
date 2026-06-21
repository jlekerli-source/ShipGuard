# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: Stable publication blocked by missing external evidence.
- Proof source: externalAdoptionEvidenceStableGate
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence.
- Next command: `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable`

## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `pass` |
| `releaseNotesProof` | `pass` |
| `releaseCandidatePacketProof` | `pass` |
| `publishedReleaseAssetProof` | `pass` |
| `postReleaseConsumerProof` | `pass` |
| `externalAdoptionEvidenceStableGate` | `not-provided` |
| `securityReviewEvidenceStableGate` | `not-provided` |

## Evidence Packet

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `independent-adoption-evidence` | `not-provided` |
| `final-security-review-evidence` | `not-provided` |

## Release Notes Proof

- Notes digest: `synthetic-fixture-digest`
- Missing topics: `none`

| Topic | Status | Matched terms |
| --- | --- | --- |
| `stable-v4-claim` | `pass` | stable v4 |
| `publication-proof-boundary` | `pass` | release proof |
| `downloaded-release-assets` | `pass` | downloaded release assets |
| `post-release-consumer-proof` | `pass` | post-release consumer |
| `independent-adoption-evidence` | `pass` | independent adoption |
| `final-security-review-evidence` | `pass` | security review |
| `non-claims-boundary` | `pass` | non-claims |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `none`

| File | Purpose |
| --- | --- |
| `stable-publication-release-notes/README.md` | Authoring instructions. |
| `stable-publication-release-notes/release-notes-checklist.json` | Machine-readable topic checklist. |
| `stable-publication-release-notes/draft-release-notes.md` | Copy-ready draft release notes. |

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `2`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `independent-adoption-evidence` | `not-provided` | `True` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Independent public adoption evidence must pass structure, redaction, and independence checks; fixture evidence is not enough. |
| `2` | `final-security-review-evidence` | `not-provided` | `False` | `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Final security review evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings. |

## Evidence Templates

| Template | Exists | Copy command |
| --- | --- | --- |
| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |
| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

| File | Purpose |
| --- | --- |
| `stable-publication-evidence-kit/README.md` | Human checklist for stable-publication evidence collection. |
| `stable-publication-evidence-kit/stable-publication-checklist.json` | Machine-readable stable-publication checklist. |
| `stable-publication-evidence-kit/external-adoption-evidence.json` | Draft-only independent adoption starter record. |
| `stable-publication-evidence-kit/security-review-evidence.json` | Draft-only final security-review starter record. |

## Scope Boundary

- `shipguardOnly`: `True`
- `targetAppsReadOnly`: `True`
- `privateAppsUsed`: `False`

