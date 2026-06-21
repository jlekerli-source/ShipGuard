# stable-publication-post-release-consumer-closure

Public synthetic fixture for `shipguard ios report-quality`.

## Boundary

- Synthetic ShipGuard report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard v4 stable-publication` source report.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-post-release-consumer-closure --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
