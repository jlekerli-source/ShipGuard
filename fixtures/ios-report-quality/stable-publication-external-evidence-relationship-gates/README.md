# Stable-Publication External Evidence Relationship-Gate Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stable-publication reports keep external evidence relationship gates visible: adoption evidence needs `actorRelationship=independent`, and security review evidence needs `reviewerRelationship` values that are explicitly accepted. Maintainer-only adoption runs, fixture records, vague self-review notes, and unknown relationships remain blocked substitutes.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with `stablePublicationExternalEvidenceRelationshipGateProof`.
- `fixture-report.md`: Markdown proof surface containing `External Evidence Relationship Gates`.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-relationship-gates --out /tmp/shipguard-relationship-gate-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
