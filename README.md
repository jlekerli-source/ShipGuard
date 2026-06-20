<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="96" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local proof gates for AI-assisted software work.
</p>

<p align="center">
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps developers use Codex and other coding agents without accepting vague handoffs like "done", "tested", or "looks good".

It turns AI-assisted work into a simple proof loop:

```text
scope the task -> run the work -> check the evidence -> ship, review, or block
```

ShipGuard is local-first, open source, and app-neutral. The strongest track today is iOS, with growing support for web, backend, and CLI projects.

## What You Get

- A local CLI for task contracts, proof checks, release evidence, and repo health.
- Starter profiles for iOS, web, backend, and CLI repos.
- A Codex plugin for iOS maintenance, design QA, performance audits, preview routing, and modernization planning.
- GitHub Action helpers for proof reports on pull requests and releases.
- Public fixtures and evals so useful behavior is tested, not just described.

## Start In 3 Minutes

From this checkout:

```bash
./bin/shipguard validate
./bin/shipguard version
```

Install the CLI locally:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
```

Add ShipGuard to a project:

```bash
shipguard init ios .
shipguard doctor ios .
```

Use `web`, `backend`, or `cli` instead of `ios` for those starter profiles.

## The Core Workflow

Create a scoped task before agent work:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Verify the result after code changes:

```bash
shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --claim "Implemented notification permission copy." \
  --out /tmp/shipguard-verdict
```

The verdict tells you what changed, what proof exists, which claims are unsupported, and the next action.

## Common Commands

| Need | Command |
| --- | --- |
| Validate ShipGuard | `shipguard validate` |
| Add starter files | `shipguard init ios .` |
| Check repo setup | `shipguard doctor ios .` |
| Prepare an AI task | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify AI work | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Audit iOS risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Audit iOS performance | `shipguard ios performance --path . --out /tmp/ios-performance` |
| Audit iOS design | `shipguard ios design --path . --out /tmp/ios-design` |
| Run the full proof lane | `shipguard full-audit --path . --out /tmp/shipguard-full-audit` |

See the [CLI reference](docs/cli.md) and [command matrix](docs/command-matrix.md) for the full surface.

## Codex Plugin

ShipGuard includes an iOS-focused Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill text is loaded.

## GitHub Action

ShipGuard can run proof checks in CI and upload reviewable evidence.

- [GitHub Action](docs/github-action.md)
- [Release proof](docs/release-proof.md)
- [Release proof consumption](docs/release-proof-consumption.md)

## Repo Map

```text
bin/                   CLI entry point
scripts/               report engines and proof tools
plugins/ios-shipguard/ Codex plugin bundle
templates/             starter profiles
docs/                  user and maintainer docs
fixtures/              public regression fixtures
tests/                 validation lanes
actions/               reusable GitHub Actions
```

## ShipYard

ShipYard is the maintainer side of ShipGuard: fixtures, evals, package checks, release proof, plugin readiness, and roadmap execution.

Useful links:

- [Docs index](docs/index.md)
- [Roadmap](ROADMAP.md)
- [Next goal](NEXT_GOAL.md)
- [Changelog](CHANGELOG.md)
- [Open source model](docs/open-source.md)

## License

MIT. See [LICENSE](LICENSE).
