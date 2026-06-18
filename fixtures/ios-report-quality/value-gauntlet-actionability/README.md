# Value Gauntlet Actionability Fixture

Public synthetic fixture for the ShipGuard Tool Value Gauntlet actionability loop.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: minimal synthetic source report.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/value-gauntlet-actionability --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
- `./bin/shipguard validate`
