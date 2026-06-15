# Ringly Codex Workflows

Public operating rules for using Codex on risk-sensitive solo iOS work.

This repository shares the workflow layer I use around Ringly, an iPhone alarm app where reliability, notification truth, StoreKit behavior, and release proof matter. It does not contain private Ringly source code. It contains the reusable process: agent instructions, planning templates, validation routing, skill prompts, release checklists, and evaluation tasks.

The goal is simple: make AI-assisted coding repeatable, reviewable, and useful for real product maintenance.

## Who This Is For

- Solo developers using Codex or similar coding agents on production apps.
- iOS developers working near alarms, notifications, widgets, subscriptions, or release gates.
- Maintainers who want agents to plan, test, and hand off work with evidence instead of vague claims.

## Quick Start

1. Copy `AGENTS.md` into your repo root and replace the Ringly-specific paths with your project paths.
2. Use `PLANS.md` before risky work, release work, or changes that touch persistence, notifications, payments, or app lifecycle code.
3. Pick the relevant skill under `.agents/skills/` and paste it into your Codex task context.
4. Run the narrowest validation lane that proves the change.
5. Record blockers and proof honestly before merging or shipping.

To validate this workflow bundle itself:

```bash
./scripts/validate_workflow_bundle.sh
```

## What Is Inside

- `AGENTS.md`: a root instruction template for mobile-app maintenance with high-risk feature areas.
- `PLANS.md`: a planning template that forces objective, scope, risks, tests, and rollback thinking.
- `SUBAGENTS.md`: inspector, implementer, tester, and reviewer roles for larger Codex tasks.
- `.agents/skills/`: reusable Codex skills for alarm testing, notification permissions, UI polish, release checklists, and bug triage.
- `scripts/`: small checklists and prompts for release handoff, bug triage, and alarm/notification validation.
- `.github/workflows/validate.yml`: a lightweight CI check for required files, skill metadata, shell syntax, and whitespace.
- `EVALUATION_SUITE.md`: realistic benchmark tasks for future agent runs.
- `POSTS.md`: short public posts explaining the workflow.

## Workflow Map

```text
request
  -> read AGENTS.md
  -> choose risk lane
  -> write or update PLANS.md
  -> make the smallest scoped change
  -> run the narrowest proof command
  -> review the diff and evidence
  -> ship only what is proven
```

## Why This Matters

AI coding agents are strongest when the project gives them structure. Ringly is my live test bed for that structure: narrow scopes, explicit guardrails, real validation, and clear handoffs when proof is missing.

This repository turns those habits into public templates that other developers can adapt without copying the private app.

## Current Status

This is an early public workflow kit. The next priorities are documented in `ROADMAP.md`, and contribution guidance lives in `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.
