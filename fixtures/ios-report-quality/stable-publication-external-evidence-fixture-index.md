# Stable-Publication External Evidence Fixture Index

Compact index of public stable-publication external-evidence fixture coverage.

Status: `pass`
Covered: `4/4`

## Decision Summary

- Verdict: Adoption, security-review, freshness, and source-class fixture questions are covered; source-class polish remains the next promotion target.
- Covered evidence classes: independent-adoption-evidence, final-security-review-evidence, external-evidence-freshness-fixture, external-evidence-source-class-fixture
- Remaining questions: external-evidence-source-class-fixture-polish
- Next promotion target: `external-evidence-source-class-fixture-polish`
- Non-claim: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

## Coverage

| Evidence | Status | Fixture | Rejection Proved | Required Proof |
| --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist` | weak adoption signals rejected | independent actor, commands, artifacts, redaction, outcome, non-claims |
| `final-security-review-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist` | vague security evidence rejected | reviewed surfaces, severity thresholds, redaction, methodology, findings summary, non-claims |
| `external-evidence-freshness-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-freshness` | stale adoption/security evidence rejected | release manifest generatedAt, evidence generatedAt, stale record count, freshness boundary, non-claims |
| `external-evidence-source-class-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-source-classes` | weak substitutes rejected as adoption/security proof | accepted evidence classes, actor/reviewer relationship fields, accepted relationships, rejected substitutes, pass boundaries, Markdown visibility |

## Remaining Gaps

- `external-evidence-source-class-fixture-polish`: Polish the source-class fixture and index copy so maintainers can see the next useful evidence-quality refinement. Suggested path: `fixtures/ios-report-quality/stable-publication-external-evidence-source-classes`

## Non-Claims

- Fixture coverage proves report-quality behavior only.
- Fixture coverage is not independent adoption evidence.
- Fixture coverage is not final security-review evidence.
- Fixture coverage does not prove stable-v4 publication.
