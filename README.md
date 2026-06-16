# Ringly Codex Workflows

Public operating rules for using Codex on risk-sensitive solo iOS work.

This repository shares the workflow layer I use around Ringly, an iPhone alarm app where reliability, notification truth, StoreKit behavior, and release proof matter. It does not contain private Ringly source code. It contains the reusable process: agent instructions, planning templates, validation routing, skill prompts, release checklists, and evaluation tasks.

The goal is simple: make AI-assisted coding repeatable, reviewable, and useful for real product maintenance.

## Who This Is For

- Solo developers using Codex or similar coding agents on production apps.
- iOS developers working near alarms, notifications, widgets, subscriptions, or release gates.
- Maintainers who want agents to plan, test, and hand off work with evidence instead of vague claims.

## Quick Start

Install from a release tarball:

```bash
tar -xzf codex-maintainer-v0.6.0.tar.gz
cd codex-maintainer-v0.6.0
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" version
```

Read the guided setup first:

- `docs/adoption-guide.md`: first 30 minutes with the workflow kit.
- `docs/arena.md`: benchmark runner for multiple maintainer fixtures.
- `docs/autopsy.md`: evidence checks for AI coding runs.
- `docs/autopsy-github-actions.md`: upload autopsy reports as GitHub Actions artifacts.
- `docs/benchmark.md`: stable public benchmark and leaderboard format.
- `docs/check-run.md`: GitHub Checks API payloads from gate JSON.
- `docs/ci-gate.md`: CI gate command and GitHub Action for policy enforcement.
- `docs/ci-summary.md`: GitHub Actions step-summary output from gate JSON.
- `docs/command-matrix.md`: one-page map from maintainer jobs to CLI commands.
- `docs/demo-reports.md`: checked-in demo reports generated from public fixtures.
- `docs/maintainer-reliability-os.md`: the full policy-to-self-audit evidence loop.
- `docs/next-goal.md`: generate the next slash-goal release plan.
- `docs/policy.md`: configure protected paths, risky claims, and scope limits.
- `docs/pr-review-bot.md`: generate PR-ready review comments and badge JSON from autopsy reports.
- `docs/release-checklist.md`: release proof commands and publishing checks.
- `docs/sarif.md`: convert Autopsy findings into SARIF for CI consumers.
- `docs/template-profiles.md`: iOS and web starter profile usage.
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

Copy the web starter into another project:

```bash
./bin/codex-maintainer init web ../my-web-app
```

1. Start each non-trivial Codex thread from `CODEX_TASK_TEMPLATE.md`.
2. Copy `AGENTS.md` into your repo root and replace the Ringly-specific paths with your project paths.
3. Use `PLANS.md` before risky work, release work, or changes that touch persistence, notifications, payments, or app lifecycle code.
4. Pick the relevant skill under `.agents/skills/` and paste it into your Codex task context.
5. Run the narrowest validation lane that proves the change.
6. Record blockers and proof honestly before merging or shipping.

For a worked example, read `examples/issue-to-plan-to-validation.md`.
For public proof without private app code, read `examples/demo-walkthrough.md`.
For agent-claim auditing, run `./bin/codex-maintainer autopsy` against `fixtures/autopsy/`.
For aggregate benchmark proof, run `./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena`.
For toolkit release readiness, run `./bin/codex-maintainer self-audit --out /tmp/codex-maintainer-audit`.
For the next improvement loop, run `./bin/codex-maintainer next-goal --out NEXT_GOAL.md`.
For CI-consumable findings, run `./bin/codex-maintainer sarif --report /tmp/autopsy/report.json --out /tmp/results.sarif`.
For workflow-run summaries, run `./bin/codex-maintainer ci-summary --gate /tmp/codex-gate/gate.json --out /tmp/codex-gate/summary.md`.
For Check Run payloads, run `./bin/codex-maintainer check-run --gate /tmp/codex-gate/gate.json --head-sha "$GITHUB_SHA" --out /tmp/codex-gate/check-run/payload.json`.

## What Is Inside

- `AGENTS.md`: a root instruction template for mobile-app maintenance with high-risk feature areas.
- `CODEX_TASK_TEMPLATE.md`: a copyable task contract for Codex threads, including Command Center, verification, creative/game, and subagent splits.
- `PLANS.md`: a planning template that forces objective, scope, risks, tests, and rollback thinking.
- `SUBAGENTS.md`: inspector, implementer, tester, and reviewer roles for larger Codex tasks.
- `.agents/skills/`: reusable Codex skills for alarm testing, notification permissions, UI polish, release checklists, and bug triage.
- `scripts/`: release handoff, bug triage, alarm validation, packaging, and autopsy report generation.
- `bin/codex-maintainer`: a dependency-light CLI for init, validation, doctor checks, run scoring, and agent autopsy reports.
- `VERSION`: the release version used by the CLI and package script.
- `actions/validate/`: a reusable GitHub composite action for workflow-bundle validation.
- `docs/cli.md`: command reference for the CLI.
- `docs/arena.md`: guide for running the public maintainer fixture arena.
- `docs/autopsy.md`: guide for auditing AI coding claims against diffs and tests.
- `docs/autopsy-github-actions.md`: minimal workflow for downloadable autopsy evidence.
- `docs/benchmark.md`: public AI maintainer reliability benchmark format.
- `docs/check-run.md`: GitHub Checks API payload export from gate results.
- `docs/ci-gate.md`: generate CI artifacts and optional failure from maintainer evidence.
- `docs/ci-summary.md`: GitHub Actions step-summary Markdown from gate JSON.
- `docs/command-matrix.md`: command surface map for maintainer jobs.
- `docs/demo-reports.md`: generated reports from the fixture pack.
- `docs/maintainer-reliability-os.md`: policy, audit, arena, PR, CI, leaderboard, and self-audit loop.
- `docs/next-goal.md`: slash-goal release planning for the next improvement loop.
- `docs/policy.md`: plain policy config for project-specific risk rules.
- `docs/pr-review-bot.md`: warn/fail PR review comment mode for autopsy reports.
- `docs/release-checklist.md`: release validation and publishing checklist.
- `docs/sarif.md`: SARIF export for Autopsy findings and CI gate artifacts.
- `docs/template-profiles.md`: profile docs for iOS and web workflow starters.
- `docs/github-action.md`: usage guide for the reusable action.
- `docs/adoption-guide.md`: practical onboarding path for new maintainers.
- `docs/use-in-your-repo.md`: copyable setup instructions for another repo.
- `docs/workflow-diagram.md`: visual map of the maintainer workflow.
- `docs/index.md`: lightweight documentation landing page for GitHub Pages.
- `.github/workflows/validate.yml`: a lightweight CI check for required files, skill metadata, shell syntax, and whitespace.
- `examples/issue-to-plan-to-validation.md`: an anonymized sample from messy issue to plan, proof, and handoff.
- `examples/prompt-pack.md`: copyable prompts for common maintainer tasks.
- `examples/review-comment.md`: expected PR comment and badge output from a dangerous report.
- `examples/adoption-checklist.md`: copyable rollout checklist for a new project.
- `examples/arena-results.md`: expected aggregate output from the public arena fixture pack.
- `examples/demo-walkthrough.md`: proof path for clone and release-package usage.
- `examples/demo-reports/`: generated demo arena reports and leaderboard JSON.
- `examples/autopsy-report.md`: sample autopsy expectations for dangerous and clean runs.
- `fixtures/demo-ios-repo/`: fake iOS-style repo for demo and package testing.
- `fixtures/autopsy/`: good, weak, and dangerous AI-run fixtures for report testing.
- `fixtures/arena/`: public benchmark fixture pack for aggregate arena runs.
- `templates/ios/`: a starter workflow bundle for adapting these rules to another iOS app.
- `templates/web/`: a starter workflow bundle for adapting these rules to a web app.
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
