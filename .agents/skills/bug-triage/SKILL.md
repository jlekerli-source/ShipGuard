---
name: bug-triage
description: Ringly bug-triage workflow. Use when investigating a reported bug, flaky test, regression, crash, UI mismatch, release blocker, alarm trust issue, StoreKit issue, localization exposure bug, or unclear user feedback before implementation.
---

# Bug Triage

Use this skill before fixing unclear bugs.

## Steps

1. State the expected behavior in one sentence.
2. State the current failure in one sentence.
3. Identify reproduction input: user steps, test name, log packet, screenshot, or source path.
4. Read only routed context from `AGENTS.md`, `docs/change-review-matrix.md`, and the owner files.
5. Search with `rg` before opening broad files.
6. Classify the issue:
   - product bug
   - test flake
   - infrastructure blocker
   - release/proof gap
   - unclear report needing manual reproduction
7. Name likely files and validation commands.
8. Write a small plan with objective, affected files, risks, tests, and rollback.
9. Do not implement until the plan is accepted or the user clearly asked for the fix.

## Useful Resource

Use `scripts/bug-triage/prompts.md` for inspector, implementer, tester, and reviewer prompts.
