# Stable-Publication External Evidence Fixture Index

- Status: `pass`
- Covered: 6/6

Decision summary:
- Verdict: Adoption, security-review, freshness, source-class, relationship-gate, and artifact-redaction fixture questions are covered; the next real QA gap remains.
- Covered evidence classes: independent-adoption-evidence, final-security-review-evidence, external-evidence-freshness-fixture, external-evidence-source-class-fixture, external-evidence-relationship-gate-fixture, external-evidence-artifact-redaction-fixture
- Remaining questions: external-evidence-artifact-digest-provenance-candidate
- Next promotion target: `external-evidence-artifact-digest-provenance-candidate`
- Non-claim: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

| Evidence | Status | Fixture | Rejection Proved | Required Proof |
| --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checkl...` | weak adoption signals rejected | independent actor, commands, artifacts, redaction, outcome, non-claims |
| `final-security-review-evidence` | `covered` | `fixtures/ios-report-quality/stable-publication-security-review-evidence...` | vague security evidence rejected | reviewed surfaces, severity thresholds, redaction, methodology, findings summary, non-claims |
| `external-evidence-freshness-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-freshn...` | stale adoption/security evidence rejected | release manifest generatedAt, evidence generatedAt, stale record count, freshness boundary, non-claims |
| `external-evidence-source-class-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-source...` | weak substitutes rejected as adoption/security proof | accepted evidence classes, actor/reviewer relationship fields, accepted relationships, rejected substitutes, pass bound... |
| `external-evidence-relationship-gate-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-relati...` | wrong actor/reviewer relationships rejected as adoption/security proof | actorRelationship gate, reviewerRelationship gate, accepted relationships, rejected relationships, blocked substitutes,... |
| `external-evidence-artifact-redaction-fixture` | `covered` | `fixtures/ios-report-quality/stable-publication-external-evidence-artifa...` | unredacted or provenance-free artifacts rejected as adoption/security proof | required artifact fields, privateDataRedacted gate, accepted artifact proof, rejected artifact proof, blocked substitut... |

Source-class summary:

| Evidence | Accepted classes | Relationship field | Accepted relationships | Rejected substitutes | Pass boundary |
| --- | --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | public-external, private-redacted-external | `actorRelationship` | independent | GitHub stars, GitHub forks, download counts, maintainer-only private app runs, fixtureSynthetic records, stale generatedAt record... | Requires redacted/public command and artifact evidence from an independent actor. |
| `final-security-review-evidence` | public-security-review, private-redacted-security-review | `reviewerRelationship` | independent, maintainer-security-review | fixtureSynthetic records, stale generatedAt records, vague self-review notes, missing required surfaces, open critical/high findi... | Requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/high findings. |

Relationship-gate summary:

| Evidence | Relationship field | Accepted relationships | Rejected relationships | Blocked substitute | Pass boundary |
| --- | --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | `actorRelationship` | independent | maintainer, self, fixtureSynthetic, unknown | maintainer-only private app runs | Adoption proof requires an independent external actor plus commands, artifacts, redaction, outcome, and non-claims. |
| `final-security-review-evidence` | `reviewerRelationship` | independent, maintainer-security-review | self, unknown, fixtureSynthetic | vague self-review notes | Security proof requires reviewed stable-v4 surfaces, methodology, findings summary, artifacts, redaction, and no open critical/hi... |

Artifact-redaction summary:

| Evidence | Required artifact fields | Rejected artifact proof | Blocked substitute | Pass boundary |
| --- | --- | --- | --- | --- |
| `independent-adoption-evidence` | commands, artifacts, privateDataRedacted, outcome, nonClaims | local absolute paths, private screenshots, tokens or account identifiers, unreviewed app-specific notes, missing artifa... | private unredacted maintainer artifacts | Adoption proof requires redacted/public command and artifact evidence with privateDataRedacted=true plus outcome and non-claims. |
| `final-security-review-evidence` | methodology, commands, artifacts, privateDataRedacted, findingsSummary, nonClaims | vague self-review notes, local absolute paths, private screenshots, tokens or account identifiers, missing methodology | unredacted or provenance-free security notes | Security proof requires reviewed stable-v4 surfaces, methodology, redacted artifacts, findings summary, and no open critical/high... |

Next fixture to promote:
- `external-evidence-artifact-digest-provenance-candidate`
- Suggested path: `fixtures/ios-report-quality/stable-publication-external-evidence-artifact-digest-provenance`
- Summary: Check whether adoption/security artifact proof shows digest or source provenance instead of only naming artifact files.
- QA command: `./bin/shipguard ios report-quality --reports <stable-publication-report-dir> --out <quality-dir> --shareable --write-fixture-candidates <fixture-output-dir>`
- Boundary: Promote only a public synthetic fixture; do not copy private app artifacts, paths, screenshots, tokens, or account data.

Next-gap candidate backlog:

| Candidate | Suggested fixture | Summary |
| --- | --- | --- |
| `external-evidence-artifact-digest-provenance-candidate` | `fixtures/ios-report-quality/stable-publication-external-evidence-artifact-diges...` | Check whether adoption/security artifact proof shows digest or source provenance instead of only naming artifact files. |
| `external-evidence-review-scope-mapping-candidate` | `fixtures/ios-report-quality/stable-publication-external-evidence-review-scope-m...` | Check whether final security-review evidence maps reviewed surfaces to the stable-v4 release scope instead of using broad review wording. |
| `external-evidence-evidence-expiry-window-candidate` | `fixtures/ios-report-quality/stable-publication-external-evidence-expiry-window` | Check whether external evidence has an explicit age/expiry boundary beyond generatedAt freshness against the release manifest. |

Remaining external-evidence gaps:
- `external-evidence-artifact-digest-provenance-candidate`: Check whether adoption/security artifact proof shows digest or source provenance instead of only naming artifact files.
