# Synthetic Lean Gain Current-Repo Evidence Routing Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does it route current-repo evidence back to lean audit, lean review, and lean debt?

## Benchmark Scoreboard

- Benchmark: Synthetic Lean Gain public benchmark
- Scope: public benchmark, not this repository
- Baseline: same agent without the lean-code ruleset
- Method: paired public fixture tasks with and without the lean-code ruleset

| Metric | Baseline | Lean-code result | Change |
| --- | --- | --- | --- |
| Lines of code | 100% | 46% | -54% |
| Tokens | 100% | 78% | -22% |
| Cost | 100% | 80% | -20% |
| Time | 100% | 73% | -27% |
| Safety | 100% | 100% | 100% |

## Honesty Boundary

- Per-repo savings claim: `not-computed`
- Reason: There is no untreated baseline for this repository; ShipGuard cannot subtract code, cost, or time that was never produced.
- Do not claim current-repo line, token, cost, or time savings without a matched baseline.

## Current Repo Signals

- Lean audit findings show possible cuttable surfaces.
- Lean review findings show current-diff delete or simplify opportunities.
- Lean debt marker counts show intentional shortcuts that still need ceilings and upgrade triggers.

## Current Repo Evidence Routes

| Route | Command | Artifact | Answers | Boundary |
| --- | --- | --- | --- | --- |
| `lean-audit` | `shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable` | lean-audit.json and lean-audit.md | Which repo surfaces may be deleted, simplified, kept, or proof-blocked? | Source-scan evidence only; it does not prove line, token, cost, or time savings. Do not treat audit findings as benchmark savings. |
| `lean-review` | `shipguard lean review --path <repo> --diff <diff-file> --out <lean-review-out> --mode full --shipguard-eval --shareable` | lean-review.json and lean-review.md | Which current-diff changes can be deleted, simplified, kept, or proof-blocked before merge? | Diff-scoped evidence only; it does not prove whole-repo or benchmark savings. Do not treat a smaller diff as measured token, cost, or time savings without a matched baseline. |
| `lean-debt` | `shipguard lean debt --path <repo> --out <lean-debt-out> --shipguard-eval --shareable` | lean-debt.json and lean-debt.md | Which intentional shortcuts have ceilings, upgrade triggers, and missing-trigger debt? | Shortcut-ledger evidence only; it does not prove benchmark or per-repo savings. Do not present shortcut counts as code-size savings. |

## Scope Boundary

This is ShipGuard product QA. The benchmark explains expected direction; only local Lean Deck reports prove current repo observations.

## Report Quality Questions

- Does it route current-repo evidence back to lean audit, lean review, and lean debt?
