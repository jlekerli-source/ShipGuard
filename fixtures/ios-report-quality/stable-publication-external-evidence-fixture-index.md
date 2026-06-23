# Stable-Publication External Evidence Fixture Index

Compact index of public stable-publication external-evidence fixture coverage.

Status: `pass`
Covered: `5/5`

## Decision Summary

- Verdict: Adoption, security-review, freshness, source-class, and relationship-gate fixture questions are covered; the next public fixture promotion remains.
- Covered evidence classes: independent-adoption-evidence, final-security-review-evidence, external-evidence-freshness-fixture, external-evidence-source-class-fixture, external-evidence-relationship-gate-fixture
- Remaining questions: external-evidence-next-public-fixture
- Next promotion target: `external-evidence-next-public-fixture`
- Non-claim: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

## Coverage

| Evidence | Status | Fixture | Rejection Proved | Required Proof |
| --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist` | weak adoption signals rejected | independent actor, commands, artifacts, redaction, outcome, non-claims |
| `final-security-review-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist` | vague security evidence rejected | reviewed surfaces, severity thresholds, redaction, methodology, findings summary, non-claims |
| `external-evidence-freshness-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-freshness` | stale adoption/security evidence rejected | release manifest generatedAt, evidence generatedAt, stale record count, freshness boundary, non-claims |
| `external-evidence-source-class-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-source-classes` | weak substitutes rejected as adoption/security proof | accepted evidence classes, actor/reviewer relationship fields, accepted relationships, rejected substitutes, pass boundaries, Markdown visibility |
| `external-evidence-relationship-gate-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-relationship-gates` | wrong actor/reviewer relationships rejected as adoption/security proof | actorRelationship gate, reviewerRelationship gate, accepted relationships, rejected relationships, blocked substitutes, pass boundaries, Markdown visibility |

## Source-Class Summary

| Evidence | Accepted Classes | Relationship Field | Accepted Relationships | Rejected Substitutes | Pass Boundary |
| --- | --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | public-external, private-redacted-external | `actorRelationship` | independent | GitHub stars, GitHub forks, download counts, maintainer-only private app runs, fixtureSynthetic records, stale generatedAt records, unchanged starter templates | Requires redacted/public command and artifact evidence from an independent actor. |
| `final-security-review-evidence` | public-security-review, private-redacted-security-review | `reviewerRelationship` | independent, maintainer-security-review | fixtureSynthetic records, stale generatedAt records, vague self-review notes, missing required surfaces, open critical/high findings, unchanged starter templates | Requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/high findings. |

## Relationship-Gate Summary

| Evidence | Relationship Field | Accepted Relationships | Rejected Relationships | Blocked Substitute | Pass Boundary |
| --- | --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `actorRelationship` | independent | maintainer, self, fixtureSynthetic, unknown | maintainer-only private app runs | Adoption proof requires an independent external actor plus commands, artifacts, redaction, outcome, and non-claims. |
| `final-security-review-evidence` | `reviewerRelationship` | independent, maintainer-security-review | self, unknown, fixtureSynthetic | vague self-review notes | Security proof requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/high findings. |

## Remaining Gaps

- `external-evidence-next-public-fixture`: Promote the next stable-publication external-evidence public fixture found by real report QA without treating fixture coverage as adoption or security proof. Suggested path: `fixtures/ios-report-quality/stable-publication-external-evidence-relationship-gates`

## Non-Claims

- Fixture coverage proves report-quality behavior only.
- Fixture coverage is not independent adoption evidence.
- Fixture coverage is not final security-review evidence.
- Fixture coverage does not prove stable-v4 publication.
