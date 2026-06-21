# Synthetic Stable-Publication Evidence Packet Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?

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
| `5` | `independent-adoption-evidence` | `not-provided` | `False` | `./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --external-adoption-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Independent public adoption evidence must pass structure, redaction, and independence checks; fixture evidence is not enough. |
| `6` | `final-security-review-evidence` | `not-provided` | `False` | `./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Final security review evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings. |

## Evidence Templates

- Draft-only templates: `True`

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`

## Blocked Claims

- Do not claim stable v4 until this report status is pass.
- Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.
- Do not treat GitHub release download counts as independent adoption evidence.

## Report Quality Questions

- Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?
