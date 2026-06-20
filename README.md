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

ShipGuard helps developers use Codex and other coding agents without trusting vague handoffs like "tests passed" or "looks good."

It turns AI-assisted work into a clear loop:

```text
scope the task -> make the change -> attach evidence -> verify the claims -> ship or block
```

The output is boring on purpose: Markdown and JSON reports with a simple verdict of `pass`, `review`, or `blocked`.

## Why It Exists

AI coding is fast, but maintenance still needs proof. ShipGuard gives solo developers and small teams a local operating layer for:

- scoped task contracts before an agent edits code
- evidence receipts after tests, builds, reviews, or release checks
- claim checking so reports do not overstate what was proven
- iOS app audits for risk, performance, design, modernization, previews, and release readiness
- release proof that can be reviewed locally or in CI

ShipGuard is not tied to any single app and is not a helper for one private codebase. It is a reusable proof system for production software maintenance. The strongest surface today is iOS, with starter profiles for web, backend, and CLI projects.

## Quick Start

Install from a source checkout or release package:

```bash
# release package:
tar -xzf shipguard-v3.131.0.tar.gz && cd shipguard-v3.131.0

# source checkout or extracted package:
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" version
"$HOME/.local/bin/shipguard" validate
```

Add ShipGuard to a project:

```bash
shipguard init ios .
shipguard doctor ios .
```

Create a task contract before agent work:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Verify the result after the agent works:

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

## Core Commands

| Need | Command |
| --- | --- |
| Prove the checkout works | `shipguard validate` |
| Add ShipGuard starter files | `shipguard init ios .` |
| Check repo readiness | `shipguard doctor ios .` |
| Scope an agent task | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify claims and evidence | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Inspect iOS risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Audit iOS performance | `shipguard ios performance --path . --out /tmp/ios-performance` |
| Audit iOS design quality | `shipguard ios design --path . --out /tmp/ios-design` |
| Run the full ShipYard proof lane | `shipguard full-audit --path . --out /tmp/shipguard-full-audit` |
| Inspect ShipGuard itself | `shipguard inspect --path . --out /tmp/shipguard-inspect` |

For the full command list, see the [CLI reference](docs/cli.md) and [command matrix](docs/command-matrix.md).

## Codex Plugin

ShipGuard includes an iOS-focused Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill metadata is loaded.

## GitHub Actions

ShipGuard can run proof checks in CI and attach reviewable evidence to pull requests.

Start with:

- [GitHub Action](docs/github-action.md)
- [Verify-first quickstart](docs/verify-first-quickstart.md)
- [Release proof](docs/release-proof.md)

## Project Layout

```text
bin/                   CLI entry point
scripts/               report engines and proof tooling
plugins/ios-shipguard/ Codex plugin bundle
templates/             starter profiles
docs/                  user and maintainer docs
fixtures/              public regression fixtures
tests/                 validation lanes
actions/               reusable GitHub Actions
```

## Maintainers

ShipGuard development happens in the ShipYard: the repo-native maintainer layer for fixtures, evals, release proof, package hygiene, plugin readiness, and roadmap execution.

Useful maintainer docs:

- [Documentation index](docs/index.md)
- [Roadmap](ROADMAP.md)
- [Next goal](NEXT_GOAL.md)
- [Changelog](CHANGELOG.md)
- [Open source operating model](docs/open-source.md)

Current published release: `v3.131.0`.

## License

MIT. See [LICENSE](LICENSE).
