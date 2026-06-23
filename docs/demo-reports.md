# Demo Reports

The repository includes two public demo paths:

- [Verify-First Quickstart](verify-first-quickstart.md): the shortest installable proof loop, using one task contract, one demo diff, and one structured receipt.
- `examples/demo-reports/`: generated Arena, leaderboard, and transcript reports from public fixtures.

Use the quickstart first when you want to understand what ShipGuard does for a normal PR. Use generated demo reports when you want to inspect report formats and benchmark fixtures.

Regenerate them with:

```bash
./scripts/build_demo_reports.sh
```

The generated output includes:

- the verify-first pass, review, and blocked demo path documented in `docs/verify-first-quickstart.md`
- arena aggregate results
- per-case autopsy reports
- leaderboard JSON
- transcript corpus JSON, Markdown, badge, and per-case verification reports

The demo reports are generated from public fixtures only. They do not include private app source, credentials, local paths, or real adoption claims.
