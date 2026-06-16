# Optional Live Evals

The default benchmark for this repository is still `codex-maintainer arena run`, which scores saved maintainer-run artifacts deterministically.

This folder is an optional live-eval scaffold for checking whether a current OpenAI model can follow the same maintainer-evidence rules. It is not required for normal toolkit validation and it does not run unless `OPENAI_API_KEY` is present.

## Run

```bash
python3 evals/run_local.py
```

Without `OPENAI_API_KEY`, the runner exits with status `2` and explains that live evals are skipped.

With `OPENAI_API_KEY`, it reads `evals/cases.jsonl`, calls the OpenAI Responses API, grades simple include/exclude expectations, writes `evals/results/latest.json`, and exits non-zero if any case fails.

## What This Measures

- instruction following around scope, validation, and handoff honesty
- refusal to turn missing evidence into release or approval claims
- basic wording constraints that are stable enough for substring grading

## What This Does Not Measure

- production model quality across the full maintainer arena
- private Ringly source behavior
- correctness of code edits
- release approval, TestFlight status, or App Store Connect state

Keep deterministic fixture scoring as the source of truth for CI. Use live evals as an optional signal when comparing model or prompt behavior.

