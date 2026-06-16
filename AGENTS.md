# Codex Maintainer OSS Instructions

Use this file as the operating contract for this repository. The reusable app templates live under `templates/`.

## Repository Overview

- Product: `codex-maintainer`, a local-first toolkit for auditing AI-assisted maintainer work.
- Primary stack: Bash, Markdown, composite GitHub Actions, fixture-based shell tests.
- CLI entrypoint: `bin/codex-maintainer`.
- Core scripts: `scripts/`.
- Reusable actions: `actions/`.
- Starter profiles: `templates/ios`, `templates/web`, `templates/backend`, and `templates/cli`.
- Generated release and demo evidence: `dist/` and `examples/demo-reports/`.

## Startup Routine

1. Read this file before editing.
2. Treat existing worktree changes as user-owned unless you made them.
3. Identify whether the task touches docs, CLI behavior, reusable actions, fixtures, generated evidence, or release packaging.
4. Use the narrowest validation command that proves the touched surface.
5. Do not make release, benchmark, or proof claims without command output or checked artifacts.

## Validation Routing

- Docs-only: `git diff --check` plus `./bin/codex-maintainer docs-check <changed-doc-or-dir> --out /tmp/codex-maintainer-docs-check`.
- CLI dispatch or scripts: `./bin/codex-maintainer validate` plus the touched `tests/*_test.sh`.
- Reusable actions: parse the action YAML with Ruby when available and run the matching `tests/*_action_test.sh`.
- Templates or starter profiles: `./tests/template_profiles_test.sh`.
- Autopsy, arena, transcript, release, or evidence behavior: run the matching focused test before broad validation.
- Release packaging or required-file lists: `./tests/package_release_test.sh` and `./bin/codex-maintainer self-audit --out /tmp/codex-maintainer-audit`.

Blocked, timed-out, interrupted, or infrastructure-failed commands are not passes.

## Generated Or Release Evidence

- Do not edit `dist/` unless the task is explicitly a release packaging task.
- Do not refresh `examples/demo-reports/` unless the task explicitly changes generated report output.
- Keep generated output changes separate from authored docs and script logic in summaries.

## High-Risk Areas

- Shell code that deletes, overwrites, downloads, uploads, or posts to external APIs.
- GitHub Actions that consume tokens, write checks, download releases, or upload artifacts.
- Release proof, replay, attestation, and evidence verification code.
- Transcript redaction and verification code.
- Fixture pack import, sign, and verify behavior.
- Package layout and installer behavior.

## Completion Checklist

Before claiming completion:

1. The requested artifact or behavior exists.
2. Only scoped files changed, aside from pre-existing user-owned edits.
3. Generated evidence was not refreshed unless required.
4. The narrowest validation ran, or the blocker is exact.
5. Any release, proof, benchmark, or security claim cites real evidence.
