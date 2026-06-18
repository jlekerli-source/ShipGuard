# materialized-external-audit

Public synthetic fixture for a materialized ShipGuard report-quality candidate.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keeps `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.
- Proves report-quality does not create recursive fixture candidates from an already-materialized fixture.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/materialized-external-audit --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`
