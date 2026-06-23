# Stable-Publication External Evidence Artifact-Redaction Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stable-publication reports keep external evidence artifact redaction and provenance gates visible. Adoption and security-review evidence must include redacted artifacts, provenance, required fields, and non-claims; private paths, private screenshots, tokens, missing artifact links, and vague unreviewed notes remain blocked substitutes.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with `stablePublicationExternalEvidenceArtifactRedactionProof`.
- `fixture-report.md`: Markdown proof surface containing `External Evidence Artifact Redaction`.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-artifact-redaction --out /tmp/shipguard-artifact-redaction-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
