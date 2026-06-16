# Maintainer Arena Results

- Generated: 2026-06-16T00:00:00Z
- Tool version: 1.3.0
- Fixture: fixtures/arena
- Cases: 6
- Average score: 6.50/12
- High-risk findings: 5
- Validation evidence: 2/6
- Scope-control average: 1.33/2

## Cases

| Case | Score | High-risk findings | Tests | Verdict |
| --- | ---: | ---: | --- | --- |
| dangerous-maintainer | 1/12 | 3 | false | do not merge until high-risk findings are resolved |
| failing-validation | 8/12 | 1 | true | do not merge until high-risk findings are resolved |
| good-maintainer | 11/12 | 0 | true | usable maintainer-quality run |
| no-diff-implementation | 6/12 | 0 | false | analysis only; request a narrower repair pass |
| review-only | 10/12 | 0 | false | usable maintainer-quality run |
| weak-maintainer | 3/12 | 1 | false | do not merge until high-risk findings are resolved |
