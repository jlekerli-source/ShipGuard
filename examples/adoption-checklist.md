# Adoption Checklist

Use this checklist when rolling the workflow kit into another repo.

## Setup

- [ ] Run `./bin/codex-maintainer init ios <target>`.
- [ ] Replace placeholders in `<target>/AGENTS.md`.
- [ ] Add real validation commands.
- [ ] Remove Ringly-specific assumptions that do not apply.
- [ ] Run `./bin/codex-maintainer doctor <target>`.

## First Task

- [ ] Pick a low-risk issue.
- [ ] Ask Codex to inspect before editing.
- [ ] Require expected behavior, current failure, owner files, risks, and validation route.
- [ ] Approve implementation only after the scope is narrow.
- [ ] Run the smallest proof command.

## After The First Task

- [ ] Score the run with `SCORECARD.md`.
- [ ] Add one project-specific rule to `AGENTS.md`.
- [ ] Add one project-specific skill if a pattern repeated.
- [ ] Decide whether to add CI validation.

## Adoption Is Working When

- [ ] Codex stops guessing broad architecture.
- [ ] Risky changes have plans.
- [ ] Validation claims cite commands or blockers.
- [ ] Handoffs name the next exact action.
- [ ] Maintainer review is faster, not skipped.
