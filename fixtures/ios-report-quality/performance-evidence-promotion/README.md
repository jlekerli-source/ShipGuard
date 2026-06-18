# Performance Evidence Promotion Fixture

This public synthetic fixture covers the read-only product-QA question:

> Did the report make it obvious which evidence would promote a source suspicion into broader work?

It locks the performance report shape for source-only findings: a source heuristic must remain unpromoted until same-route runtime or device proof exists, and the report must provide one exact next action with owner, proof, expected artifact, success condition, and failure meaning.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard ios performance` report.
- `fixture-report.md`: paired Markdown report.

## Validation

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/performance-evidence-promotion --out /tmp/shipguard-performance-evidence-promotion-quality --shareable
./tests/ios_report_quality_test.sh
```
