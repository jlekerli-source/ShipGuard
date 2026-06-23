# Stable-Publication External Evidence Source-Class Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stable-publication reports keep accepted evidence source classes, actor/reviewer relationships, rejected substitutes, and pass boundaries visible in JSON and Markdown.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with `publicEvidenceClosureProof.sourceClassMatrix`.
- `fixture-report.md`: Markdown proof surface containing `External Evidence Source-Class Matrix`.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-source-classes --out /tmp/shipguard-source-class-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
