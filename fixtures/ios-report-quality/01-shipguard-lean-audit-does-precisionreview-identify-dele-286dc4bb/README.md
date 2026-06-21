# 01-shipguard-lean-audit-does-precisionreview-identify-dele-286dc4bb

Public synthetic fixture for the top Lean Deck actionability question.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: minimal synthetic Lean Deck source report.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/01-shipguard-lean-audit-does-precisionreview-identify-dele-286dc4bb --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
