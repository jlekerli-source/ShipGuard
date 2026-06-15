# Contributing

This repo is for practical Codex workflows that help maintain real software. Contributions should make agent work more reliable, easier to validate, or easier to hand off.

## Good Contributions

- A sharper `AGENTS.md` rule with a clear reason.
- A focused skill that routes a recurring task.
- A validation checklist that catches real project risk.
- A small script that prints a repeatable handoff or proof checklist.
- A realistic evaluation task with expected behavior, current failure, and validation shape.

## Keep It Practical

- Prefer concrete commands, file paths, and decision rules.
- Avoid broad AI advice that cannot be executed or verified.
- Do not include private source code, credentials, App Store data, customer data, or unreleased product secrets.
- Keep examples small enough that another maintainer can copy them into a real repo.

## Pull Request Checklist

- [ ] The change has a clear maintainer use case.
- [ ] The affected workflow is documented in the nearest README or template.
- [ ] New scripts are executable when they need to be run directly.
- [ ] `git diff --check` passes.
- [ ] Any validation gap is stated honestly in the PR description.

## Reporting Workflow Gaps

Open an issue with:

- The kind of task Codex struggled with.
- What the agent did wrong or skipped.
- The rule, checklist, or skill that would have prevented it.
- The smallest validation command or manual proof that should be required.
