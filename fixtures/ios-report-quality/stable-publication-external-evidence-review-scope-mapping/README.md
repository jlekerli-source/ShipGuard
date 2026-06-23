# Stable-Publication External Evidence Review-Scope Mapping Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stable-publication reports keep final security-review surface-to-release-scope mapping visible. Security-review evidence must map reviewed surfaces to the stable-v4 release scope with methodology and evidence artifacts; broad reviewed-everything wording, missing surface lists, unmapped scanner output, and generic review notes remain blocked substitutes.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with `stablePublicationExternalEvidenceReviewScopeMappingProof`.
- `fixture-report.md`: Markdown proof surface containing `External Evidence Review Scope Mapping`.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-review-scope-mapping --out /tmp/shipguard-review-scope-mapping-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
