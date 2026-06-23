# Stable-Publication External Evidence Fixture Index

Status: pass

Covered: 9/9

## Decision Summary

- Verdict: Adoption, security-review, freshness, source-class, relationship-gate, artifact-redaction, artifact digest/provenance, review-scope mapping, and expiry-window fixture questions are covered; evaluate the next real QA gap.
- Next promotion target: `none`
- Remaining questions: none
- Boundary: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

## Coverage

| Evidence | Status | Fixture | Rejection proved |
| --- | --- | --- | --- |
| `independent-adoption-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist` | weak adoption signals rejected |
| `final-security-review-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist` | vague security evidence rejected |
| `external-evidence-freshness-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-freshness` | stale adoption/security evidence rejected |
| `external-evidence-source-class-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-source-classes` | weak substitutes rejected as adoption/security proof |
| `external-evidence-relationship-gate-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-relationship-gates` | wrong actor/reviewer relationships rejected as adoption/security proof |
| `external-evidence-artifact-redaction-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-artifact-redaction` | unredacted or provenance-free artifacts rejected as adoption/security proof |
| `external-evidence-artifact-digest-provenance-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-artifact-digest-provenance` | filename-only artifacts rejected as adoption/security proof |
| `external-evidence-review-scope-mapping-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-review-scope-mapping` | broad security-review wording rejected as final security proof |
| `external-evidence-expiry-window-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-expiry-window` | open-ended external evidence rejected as stable-publication proof |

## Source-class summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `independent-adoption-evidence` | public-external, private-redacted-external | - |
| `final-security-review-evidence` | public-security-review, private-redacted-security-review | - |

## Relationship-gate summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `independent-adoption-evidence` | independent | maintainer-only private app runs |
| `final-security-review-evidence` | independent, maintainer-security-review | vague self-review notes |

## Artifact-redaction summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `independent-adoption-evidence` | commands, artifacts, privateDataRedacted, outcome, nonClaims | private unredacted maintainer artifacts |
| `final-security-review-evidence` | methodology, commands, artifacts, privateDataRedacted, findingsSummary, nonClaims | unredacted or provenance-free security notes |

## Artifact digest/provenance summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `independent-adoption-evidence` | artifactName, sha256 or digest, sourceUrl or sourceCommand, privateDataRedacted, capturedAt | artifact names without digest or public/source provenance |
| `final-security-review-evidence` | artifactName, sha256 or digest, reviewSource, methodology, privateDataRedacted, capturedAt | security notes that name artifacts but omit digest or review-source provenance |

## Review-scope mapping summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `final-security-review-evidence` | surface, releaseScope, methodology, evidenceArtifact, findingStatus | generic final security review notes without stable-v4 surface mapping |

## Expiry-window summary

| Evidence | Fields | Blocked substitute |
| --- | --- | --- |
| `independent-adoption-evidence` | generatedAt, validUntil or expiresAt, maxEvidenceAgeDays, releaseManifestGeneratedAt | fresh-looking adoption record without an explicit expiry window |
| `final-security-review-evidence` | generatedAt, validUntil or expiresAt, maxEvidenceAgeDays, reviewedReleaseVersion | security-review record without explicit expiry or reviewed-release boundary |

## Non-Claims

- Fixture coverage proves report-quality behavior only.
- Fixture coverage is not independent adoption evidence.
- Fixture coverage is not final security-review evidence.
- Fixture coverage does not prove stable-v4 publication.
