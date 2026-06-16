# Ringly Codex Workflows

This is the documentation landing page for the workflow kit.

Start here:

- [Adoption guide](adoption-guide.md)
- [Use in your repo](use-in-your-repo.md)
- [Workflow diagram](workflow-diagram.md)
- [CLI reference](cli.md)
- [Agent Autopsy](autopsy.md)
- [GitHub Action](github-action.md)
- [Changelog](../CHANGELOG.md)

## What This Kit Provides

- Root instructions for Codex in a risk-sensitive iOS repo.
- Planning and subagent templates.
- Reusable skills for alarm testing, notification permissions, release work, bug triage, and UI polish.
- A small CLI for validation, starter initialization, doctor checks, run scoring, and agent autopsy reports.
- A reusable validation GitHub Action.
- Examples and a scorecard for judging agent output quality.

## First 30 Minutes

1. Read the [adoption guide](adoption-guide.md).
2. Run `./bin/codex-maintainer validate` in this repo.
3. Run `./bin/codex-maintainer init ios ../my-ios-app` against a test repo.
4. Open the generated `AGENTS.md` and replace placeholders.
5. Run `./bin/codex-maintainer doctor ../my-ios-app`.
6. Run `./bin/codex-maintainer autopsy --run fixtures/autopsy/good-run/run.md --diff fixtures/autopsy/good-run/diff.patch --tests fixtures/autopsy/good-run/tests.log --out /tmp/autopsy-good`.
