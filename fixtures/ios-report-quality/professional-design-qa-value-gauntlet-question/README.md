# professional-design-qa-value-gauntlet-question

Public synthetic fixture for the Professional Design QA starter-skill value-gauntlet question.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: minimal synthetic source report.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/professional-design-qa-value-gauntlet-question --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
