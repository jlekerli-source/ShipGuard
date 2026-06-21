# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication report block every stable-v4 claim until independent adoption and final security evidence are attached?

## Stable Publication Evidence Packet

- Status: `blocked`
- Stable v4 release: `false`
- First blocking gate: `independent-adoption-evidence`
- Next command: `./bin/shipguard v4 stable-publication --path . --out <dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <candidate-report> --download-release-assets --external-adoption-evidence <evidence.json> --security-review-evidence <security.json> --shipguard-eval --shareable`
- Non-claim: this fixture proves report-quality behavior only.

## Closure Checklist

- Checklist status: `review`
- Remaining blockers: `2`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `1` | `independent-adoption-evidence` | `not-provided` | `True` | `./bin/shipguard v4 stable-publication --path . --out <dir> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Independent public adoption evidence must pass structure, redaction, and independence checks; fixture evidence is not enough. |
| `2` | `final-security-review-evidence` | `not-provided` | `False` | `./bin/shipguard v4 stable-publication --path . --out <dir> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable` | Final security review evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy with no open critical or high findings. |

## Evidence Templates

- `templates/stable-publication/external-adoption-evidence.template.json`
- `templates/stable-publication/security-review-evidence.template.json`

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Checklist: `stable-publication-evidence-kit/stable-publication-checklist.json`
- Adoption starter: `stable-publication-evidence-kit/external-adoption-evidence.json`
- Security starter: `stable-publication-evidence-kit/security-review-evidence.json`

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Checklist: `stable-publication-release-notes/release-notes-checklist.json`
- Draft: `stable-publication-release-notes/draft-release-notes.md`
- Brief: `stable-publication-release-notes/README.md`
