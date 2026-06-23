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
./bin/shipguard v4 stable-publication --path . --out <dir> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable
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
./bin/shipguard v4 stable-publication --path . --out <dir> --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable
```

## Evidence Templates

- `templates/stable-publication/external-adoption-evidence.template.json`
- `templates/stable-publication/security-review-evidence.template.json`

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Checklist: `stable-publication-evidence-kit/stable-publication-checklist.json`
- Adoption starter: `stable-publication-evidence-kit/external-adoption-evidence.json`
- Security starter: `stable-publication-evidence-kit/security-review-evidence.json`

## External Evidence Intake Checklist

| Evidence | Accepted classes | Required fields | Redaction boundary |
| --- | --- | --- | --- |
| `independent-adoption-evidence` | public-external, private-redacted-external | actorRelationship, privateDataRedacted, commands, artifacts, outcome, nonClaims | privateDataRedacted must be `True` |
| `final-security-review-evidence` | public-security-review, private-redacted-security-review | scope, methodology, findingsSummary, privateDataRedacted, nonClaims | privateDataRedacted must be `True` |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Checklist: `stable-publication-release-notes/release-notes-checklist.json`
- Draft: `stable-publication-release-notes/draft-release-notes.md`
- Brief: `stable-publication-release-notes/README.md`

| Evidence class | Status | What it means |
| --- | --- | --- |
| `public-consumer-proof` | `can-be-produced-by-maintainer` | Install and verify ShipGuard from public release assets only; this proves public consumability, not adoption. |
| `private-maintainer-qa` | `useful-but-not-adoption` | Ringly, Ilmify, or other maintainer app runs may expose ShipGuard product gaps, but they do not satisfy independent adoption evidence. |
| `independent-adoption-evidence` | `requires-external-actor` | A non-maintainer user, repo, issue, PR, or redacted external install report must supply the adoption record. |
| `final-security-review-evidence` | `requires-review-record` | A security review record must cover the required ShipGuard surfaces and show no open critical or high findings. |
