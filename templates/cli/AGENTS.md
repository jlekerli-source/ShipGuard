# CLI Tool ShipGuard Instructions

Use this file as the root operating contract for Codex in a command-line tool repository.

## Scope Discipline

- Read this file, `PLANS.md`, `SUBAGENTS.md`, and the task before editing.
- Keep changes narrowly tied to the requested command, option, parser, output, or packaging behavior.
- Do not refactor command dispatch, config loading, file writes, network behavior, or release packaging unless the task explicitly requires it.
- Preserve existing shell, language, formatting, test, and compatibility conventions.
- Do not add runtime dependencies unless the task justifies them and tests cover the integration.

## High-Risk Areas

Treat these as protected until a maintainer explicitly includes them in scope:

- argument parsing, command aliases, defaults, and backwards compatibility
- filesystem writes, deletes, overwrites, permissions, and path expansion
- stdin, stdout, stderr, exit codes, and machine-readable output
- credential handling, config files, environment variables, and token redaction
- network calls, retries, timeouts, and offline behavior
- package installers, release archives, checksums, and update paths
- cross-platform behavior across macOS, Linux, shells, and CI runners

## Validation Lanes

Pick the narrowest lane that proves the change:

- Static: shellcheck, typecheck, lint, or format check when available.
- Unit: parser, formatter, config, file-safety, or helper tests.
- Smoke: `--help`, `version`, common success path, and expected failure path.
- Golden: stable stdout/stderr, JSON, Markdown, or fixture output comparisons.
- Package: install from an archive or local package and run commands from the installed binary.

If validation cannot run, say exactly why and what remains unproven.

## Handoff Rule

Every handoff must include:

- commands changed
- compatibility impact
- stdout, stderr, and exit-code behavior
- files or network targets touched
- validation commands and results
- known risks or unproven platforms
