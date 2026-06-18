# Design App-Type Tailoring Fixture

This public synthetic fixture covers the read-only product-QA question:

> Did the report tailor advice to the app type instead of applying one universal design rule?

It locks the `shipguard ios design` report shape for app-type-specific design guidance. A design report must name the app type, state a guidance profile, reject universal defaults, show source signals, tailor motion/haptics/visual-density/copy guidance, and provide one exact next proof action.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard ios design` report.
- `fixture-report.md`: paired Markdown report.

## Validation

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/design-app-type-tailoring --out /tmp/shipguard-design-app-type-tailoring-quality --shareable
./tests/ios_report_quality_test.sh
```
