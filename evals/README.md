# Evals

The default benchmark for this repository is still `codex-maintainer arena run`, which scores saved maintainer-run artifacts deterministically.

This folder contains two eval lanes:

- deterministic local Shipguard evals for mode routing, missing-question detection, proof honesty, and Codex brief quality
- optional live OpenAI evals for checking whether a current model follows the same maintainer-evidence rules

Deterministic Shipguard evals are CI-safe and do not require an API key:

```bash
./bin/codex-maintainer ios eval --cases evals/ios_shipguard_cases.jsonl --out /tmp/ios-shipguard-eval
```

The command writes `ios-shipguard-eval.json` and `ios-shipguard-eval.md`, and exits non-zero if any case fails.

For a complete static first-run route that also runs doctor, inventory, guided plan, proof routing, modernization, app intelligence, AI readiness, eval, and redaction checks against the public fixture:

```bash
./bin/codex-maintainer ios demo --out /tmp/ios-shipguard-first-run
```

## Optional Live Run

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
