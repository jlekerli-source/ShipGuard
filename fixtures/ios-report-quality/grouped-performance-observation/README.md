# Grouped Performance Observation Fixture

Public synthetic fixture for `shipguard ios report-quality`.

This fixture covers the read-only ShipGuard product-QA question:

> Which grouped performance observation should become a public fixture or eval case before changing scanner heuristics again?

It locks the performance report shape that real-app read-only evidence exposed: repeated source-only performance findings should become a grouped action with a first experiment, validation route, stop condition, and separate local/manual proof boundaries.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard ios performance` report.
- `fixture-report.md`: paired Markdown report.

## Validation

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/grouped-performance-observation --out /tmp/shipguard-grouped-performance-observation-quality --shareable
```
