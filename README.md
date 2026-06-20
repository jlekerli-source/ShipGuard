<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local proof gates for AI-assisted software changes.
</p>

<p align="center">
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/github-action.md">GitHub Actions</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps developers use Codex and other coding agents without accepting vague handoffs like "tests passed" or "looks good."

It turns every risky change into a small proof loop:

```text
prepare the task -> make the change -> attach evidence -> verify the claims -> ship or block
```

ShipGuard runs locally, writes Markdown and JSON reports, and keeps the final decision simple: `pass`, `review`, or `blocked`.

## What It Does

- Creates scoped task contracts before an agent edits code.
- Checks changed files, protected paths, evidence receipts, and completion claims.
- Produces reviewer-friendly proof reports for local work and CI.
- Packages Codex plugin guidance, starter repo profiles, iOS audits, and release-proof tooling.
- Keeps private app work out of public fixtures and docs.

ShipGuard is not tied to any single app. The strongest workflow today is iOS, but the core proof loop is app-neutral and also includes starter profiles for web, backend, and CLI projects.

## Quick Start

Install ShipGuard from this checkout or a release package:

```bash
# release package path:
tar -xzf shipguard-v3.131.0.tar.gz && cd shipguard-v3.131.0

# source checkout or extracted release package:
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" version
"$HOME/.local/bin/shipguard" validate
```

Add ShipGuard to a repo:

```bash
shipguard init ios .
shipguard doctor ios .
```

Prepare a scoped task before agent work:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Verify the diff and evidence after the agent works:

```bash
shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

Example verdict:

```text
ShipGuard Proof Report
Status: pass
Validation: 1/1 covered
Claims checked: 1/1 accepted
Risk files: 0 risk file(s)
```

## Main Commands

| Need | Command |
| --- | --- |
| Install and prove setup | `shipguard version` and `shipguard validate` |
| Add starter files to a repo | `shipguard init ios .` |
| Check repo readiness | `shipguard doctor ios .` |
| Prepare an agent task | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify claims and proof | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Inspect iOS risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Review ShipGuard value | `shipguard value-gauntlet --path . --out /tmp/shipguard-value` |
| Check release package hygiene | `shipguard release-package hygiene --path . --out /tmp/package-hygiene --shareable` |
| Check docs and links | `shipguard docs-check . --out /tmp/shipguard-docs` |

## Codex Plugin

ShipGuard includes an iOS-focused Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill metadata is loaded.

## For Maintainers

The public product should stay simple. Deep release work, evals, and ShipYard maintainer tooling live in the docs:

- [Documentation Index](docs/index.md)
- [CLI Reference](docs/cli.md)
- [Command Matrix](docs/command-matrix.md)
- [Roadmap](ROADMAP.md)
- [Next Goal](NEXT_GOAL.md)
- [Changelog](CHANGELOG.md)

Current published release: `v3.131.0`.

## Project Layout

```text
bin/                  CLI entry point
scripts/              report engines and proof tooling
plugins/ios-shipguard Codex plugin bundle
templates/            starter profiles
docs/                 user and maintainer docs
fixtures/             public regression fixtures
tests/                validation lanes
actions/              reusable GitHub Actions
```

## License

MIT. See [LICENSE](LICENSE).
