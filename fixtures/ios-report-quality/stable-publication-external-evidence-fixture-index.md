# Stable-Publication External Evidence Fixture Index

Compact index of public stable-publication external-evidence fixture coverage.

Status: `pass`
Covered: `3/3`

## Decision Summary

- Verdict: Adoption, security-review, and external evidence freshness fixture questions are covered; source-class clarity remains the next promotion target.
- Covered evidence classes: independent-adoption-evidence, final-security-review-evidence, external-evidence-freshness-fixture
- Remaining questions: external-evidence-source-class-fixture
- Next promotion target: `external-evidence-source-class-fixture`
- Non-claim: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

## Coverage

| Evidence | Status | Fixture | Rejection Proved | Required Proof |
| --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist` | weak adoption signals rejected | independent actor, commands, artifacts, redaction, outcome, non-claims |
| `final-security-review-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist` | vague security evidence rejected | reviewed surfaces, severity thresholds, redaction, methodology, findings summary, non-claims |
| `external-evidence-freshness-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-freshness` | stale adoption/security evidence rejected | release manifest generatedAt, evidence generatedAt, stale record count, freshness boundary, non-claims |

## Remaining Gaps

- `external-evidence-source-class-fixture`: Promote a fixture proving accepted external evidence source classes, actor relationships, and rejected substitutes are visible in the report. Suggested path: `fixtures/ios-report-quality/stable-publication-external-evidence-source-classes`

## Non-Claims

- Fixture coverage proves report-quality behavior only.
- Fixture coverage is not independent adoption evidence.
- Fixture coverage is not final security-review evidence.
- Fixture coverage does not prove stable-v4 publication.
