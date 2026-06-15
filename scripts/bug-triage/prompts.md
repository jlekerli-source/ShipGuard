# Bug Triage Prompts

Use these prompts to turn unclear reports into bounded Codex tasks.

## Inspector Prompt

Inspect this Ringly bug without editing files.

- Reproduce the reported behavior from the code, tests, or logs.
- Identify expected behavior, current failure, likely owner files, and validation route.
- Check the nearest `AGENTS.md` and `docs/change-review-matrix.md`.
- If alarm runtime is involved, list protected files before proposing edits.
- Return a concise plan with risks and the smallest proof command.

## Implementer Prompt

Implement the smallest safe fix for this Ringly bug.

- Use the inspector's affected files and validation route.
- Keep the change narrow.
- Add or update focused tests near the behavior.
- Do not touch protected alarm runtime, release proof, or status files unless the plan explicitly routes there.
- Stop after implementation and list the exact validation commands to run.

## Tester Prompt

Validate this Ringly bug fix.

- Run the narrowest routed command from `docs/validation-commands.md`.
- Classify any failure as product, infrastructure, environment, timeout, or blocked-manual.
- Do not call the fix proven unless the command completed with product signal.
- Return command, status, evidence path, and residual risk.

## Reviewer Prompt

Review this Ringly bug-fix diff.

- Findings first, ordered by severity.
- Cite files and lines.
- Check for hidden alarm-trust, permission, persistence, StoreKit, localization, and rollback risks.
- Mention missing tests or proof gaps.
- Do not summarize before findings unless there are no findings.
