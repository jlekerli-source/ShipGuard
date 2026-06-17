# Governance

ShipGuard is maintained as a local-first, open-source workflow kit. The project accepts outside contributions, but it does not trade away its core boundary: private app evidence can improve ShipGuard only after it is converted into public-safe rules, fixtures, docs, tests, or report behavior.

## Maintainer Responsibilities

Maintainers decide:

- Which commands, plugin surfaces, docs, fixtures, and actions are part of the supported public interface.
- Which validation commands are required before a change can merge.
- Whether a private-app observation is safe to turn into a public fixture or report-quality rule.
- Whether a feature belongs in ShipGuard or should remain an app-specific workflow.
- When a release is ready and which proof artifacts must ship with it.

## Contribution Areas

Good first contribution areas:

- Documentation fixes that make a command or workflow easier to adopt.
- Public fixtures that reproduce a report-quality weakness without private code.
- Tests for CLI routing, report shape, release proof, redaction, or plugin install state.
- Issue templates, examples, and adoption docs that reduce maintainer ambiguity.

Higher-review contribution areas:

- New CLI commands.
- Changes to redaction, Devspace, MCP, release proof, GitHub Actions, or plugin metadata.
- Any workflow that can execute code, call networks, publish artifacts, or move reports into public systems.

## Decision Principles

- Prefer source-visible proof over claims.
- Prefer local-first behavior over hosted state.
- Prefer explicit user approval before executing or publishing anything.
- Prefer public fixtures over private-app dependency.
- Prefer narrow commands and focused tests over broad automation.
- Keep ShipGuard native to its mission instead of copying another project's structure or code.

## Release Policy

Every release should be reproducible from source and should include validation, package, and install proof. Release notes must describe user-visible behavior, not only internal refactors. If proof is blocked, the release should say exactly which proof is missing.

## Private App Evidence

Ringly, Ilmify, or any other app can be used only as read-only product QA for ShipGuard when explicitly authorized. The output may inform a ShipGuard rule, fixture, report section, or docs improvement. It must not become an app remediation plan unless the user separately authorizes app work.
