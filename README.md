# Ringly Codex Workflows

Public operating rules for using Codex on risk-sensitive solo iOS work.

This repository shares the workflow layer I use around Ringly, an iPhone alarm app where reliability, notification truth, StoreKit behavior, and release proof matter. It does not contain private Ringly source code. It contains the reusable process: agent instructions, planning templates, validation routing, skill prompts, release checklists, and evaluation tasks.

The goal is simple: make AI-assisted coding repeatable, reviewable, and useful for real product maintenance.

## Who This Is For

- Solo developers using Codex or similar coding agents on production apps.
- iOS developers working near alarms, notifications, widgets, subscriptions, or release gates.
- Maintainers who want agents to plan, test, and hand off work with evidence instead of vague claims.

## Quick Start

Read the guided setup first:

- `docs/adoption-guide.md`: first 30 minutes with the workflow kit.
- `docs/use-in-your-repo.md`: copy/paste setup for another repository.
- `docs/workflow-diagram.md`: visual workflow map.
- `docs/index.md`: GitHub Pages-ready documentation landing page.
- `CHANGELOG.md`: release history.
- `CODEX_TASK_TEMPLATE.md`: pasteable task contracts for new Codex threads.

Validate this workflow bundle:

```bash
./bin/codex-maintainer validate
```

Copy the iOS starter into another project:

```bash
./bin/codex-maintainer init ios ../my-ios-app
```

1. Start each non-trivial Codex thread from `CODEX_TASK_TEMPLATE.md`.
2. Copy `AGENTS.md` into your repo root and replace the Ringly-specific paths with your project paths.
3. Use `PLANS.md` before risky work, release work, or changes that touch persistence, notifications, payments, or app lifecycle code.
4. Pick the relevant skill under `.agents/skills/` and paste it into your Codex task context.
5. Run the narrowest validation lane that proves the change.
6. Record blockers and proof honestly before merging or shipping.

For a worked example, read `examples/issue-to-plan-to-validation.md`.

## What Is Inside

- `AGENTS.md`: a root instruction template for mobile-app maintenance with high-risk feature areas.
- `CODEX_TASK_TEMPLATE.md`: a copyable task contract for Codex threads, including Command Center, verification, creative/game, and subagent splits.
- `PLANS.md`: a planning template that forces objective, scope, risks, tests, and rollback thinking.
- `SUBAGENTS.md`: inspector, implementer, tester, and reviewer roles for larger Codex tasks.
- `.agents/skills/`: reusable Codex skills for alarm testing, notification permissions, UI polish, release checklists, and bug triage.
- `scripts/`: small checklists and prompts for release handoff, bug triage, and alarm/notification validation.
- `bin/codex-maintainer`: a dependency-light CLI for init, validation, doctor checks, and run scoring.
- `actions/validate/`: a reusable GitHub composite action for workflow-bundle validation.
- `docs/cli.md`: command reference for the CLI.
- `docs/github-action.md`: usage guide for the reusable action.
- `docs/adoption-guide.md`: practical onboarding path for new maintainers.
- `docs/use-in-your-repo.md`: copyable setup instructions for another repo.
- `docs/workflow-diagram.md`: visual map of the maintainer workflow.
- `docs/index.md`: lightweight documentation landing page for GitHub Pages.
- `.github/workflows/validate.yml`: a lightweight CI check for required files, skill metadata, shell syntax, and whitespace.
- `examples/issue-to-plan-to-validation.md`: an anonymized sample from messy issue to plan, proof, and handoff.
- `examples/prompt-pack.md`: copyable prompts for common maintainer tasks.
- `examples/adoption-checklist.md`: copyable rollout checklist for a new project.
- `templates/ios/`: a starter workflow bundle for adapting these rules to another iOS app.
- `SCORECARD.md`: a lightweight rubric for judging whether a Codex run produced usable maintainer evidence.
- `EVALUATION_SUITE.md`: realistic benchmark tasks for future agent runs.
- `POSTS.md`: short public posts explaining the workflow.
- `CHANGELOG.md`: release history and adoption milestones.
- `CODEX_TASK_TEMPLATE.md`: copyable thread-start template for audit, implementation, verification, release, and design work.

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

The repository is also configured as a GitHub template, so you can start from it directly and then remove the Ringly-specific examples you do not need.

## License

MIT. See `LICENSE`.
