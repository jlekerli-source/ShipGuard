# Stable-Publication External Evidence Freshness Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stale external adoption and final security-review records are rejected when their `generatedAt` timestamps predate the release manifest timestamp.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with stale external evidence freshness receipts.
- `fixture-report.md`: Markdown proof surface containing the freshness boundary.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-freshness --out /tmp/shipguard-freshness-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
