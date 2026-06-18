---
name: bug-triage
description: App bug-triage workflow. Use when investigating a reported bug, flaky test, regression, crash, UI mismatch, release blocker, permission/reliability issue, StoreKit issue, localization exposure bug, or unclear user feedback before implementation.
---

# Bug Triage

Use this skill before implementing an unclear bug report.

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

## ShipGuard QA Hooks

When this skill is being audited inside the ShipGuard ShipYard, keep the skill useful by running the product-QA loop:

```bash
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable
```

Proof should show that bug-triage has concrete commands, validation language, docs linkage, and test coverage; otherwise upgrade the skill before treating it as mature.

## Output Shape

Return:

- Expected behavior.
- Current observed or inferred failure.
- Likely owner files.
- Risk class.
- Smallest reproduction or source evidence.
- Smallest validation command.
- Open questions that block implementation.

## Rules

- Inspect first, then edit.
- Do not broaden the fix beyond the reported behavior.
- If alarm, notification, StoreKit, persistence, or release state is involved, call out the risk explicitly.
- Blocked validation is not a pass.

## Useful Resource

Use `scripts/bug-triage/prompts.md` for inspector, implementer, tester, and reviewer prompts.
