# Synthetic Stable-Publication Evidence Templates Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication report provide draft-only evidence templates for independent adoption and final security review without manufacturing proof?

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `1/7`
- First blocking gate: `releaseNotesProof`

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

## Blocked Claims

- Do not claim stable v4 until this report status is pass.
- Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.
- Do not treat GitHub release download counts as independent adoption evidence.

## Report Quality Questions

- Does the stable-publication report provide draft-only evidence templates for independent adoption and final security review without manufacturing proof?
