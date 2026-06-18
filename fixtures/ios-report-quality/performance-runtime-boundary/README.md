# Performance Runtime Boundary Fixture

Public synthetic fixture for `shipguard ios report-quality`.

This fixture covers the read-only ShipGuard product-QA question:

> Did report wording keep target-app remediation separate from ShipGuard product QA next steps?

It also locks the performance-specific runtime boundary: source-only performance reports are source heuristics with medium confidence, missing runtime proof, and no target-app blocking authority.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard ios performance` report.
- `fixture-report.md`: paired Markdown report.

## Validation

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/performance-runtime-boundary --out /tmp/shipguard-performance-runtime-boundary-quality --shareable
```
