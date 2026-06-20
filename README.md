<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
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

It turns AI work into a simple proof loop:

```text
scope the task -> run the work -> check the evidence -> ship, review, or block
```

ShipGuard is local-first, open source, and app-neutral. It is not tied to any single app. The strongest track today is iOS, with support for repo inspection, task contracts, claim verification, performance and design audits, release proof, GitHub Actions, and a Codex plugin.

## Start Here

From a ShipGuard checkout:

```bash
./bin/shipguard validate
./bin/shipguard version
```

Current release package: `shipguard-v3.131.0.tar.gz`.

Install the CLI locally:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
```

Add ShipGuard to your project:

```bash
shipguard init ios .
shipguard doctor ios .
```

For a guided first run, use the [verify-first quickstart](docs/verify-first-quickstart.md).

## The Core Workflow

Create a task contract before agent work:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Verify the result after the agent changes code:

```bash
shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --claim "Implemented notification permission copy." \
  --out /tmp/shipguard-verdict
```

The output is a Markdown and JSON verdict with:

- what changed
- what proof exists
- which claims are unsupported
- whether the work should pass, be reviewed, or be blocked
- the next exact action

## What ShipGuard Does

| Need | Command |
| --- | --- |
| Validate this toolkit | `shipguard validate` |
| Add starter workflow files | `shipguard init ios .` |
| Check repo setup | `shipguard doctor ios .` |
| Scope agent work | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify claims and evidence | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Inspect iOS risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Audit iOS performance | `shipguard ios performance --path . --out /tmp/ios-performance` |
| Audit iOS design | `shipguard ios design --path . --out /tmp/ios-design` |
| Run the maintainer proof lane | `shipguard full-audit --path . --out /tmp/shipguard-full-audit` |

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

ShipGuard can run proof checks in CI and produce reviewable evidence on pull requests.

Start with:

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
