# 01-shipguard-lean-gain-does-it-route-current-repo-evidence-9bae8f6f

Public synthetic fixture for the Lean Gain current-repo evidence routing question.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic Lean Gain source report with structured current-repo evidence routes.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/01-shipguard-lean-gain-does-it-route-current-repo-evidence-9bae8f6f --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
