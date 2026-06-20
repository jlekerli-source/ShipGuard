<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Proof gates for AI-assisted software work.
</p>

<p align="center">
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps developers use Codex and other coding agents without accepting vague handoffs like "done", "tested", or "looks good".

It turns agent work into a proof loop:

```text
scope the task -> run the work -> check the evidence -> ship, review, or block
```

ShipGuard is local-first, open source, and app-neutral. It works as a CLI, a set of GitHub Action helpers, and an iOS-focused Codex plugin. The iOS track is the strongest today; web, backend, and CLI profiles are growing from the same proof-first core.

## Why It Exists

AI coding gets risky when the handoff is just a confident summary. ShipGuard makes the handoff reviewable:

- What was the agent allowed to change?
- Which files actually changed?
- What validation really ran?
- Which claims are supported by evidence?
- What should happen next: merge, review, rerun, or block?

The goal is not more process. The goal is less guessing.

## Quick Start

Run ShipGuard from this checkout:

```bash
./bin/shipguard validate
./bin/shipguard version
```

Install it locally:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
```

Add ShipGuard to another repo:

```bash
shipguard init ios ../my-ios-app
shipguard doctor ios ../my-ios-app
```

Use `web`, `backend`, or `cli` instead of `ios` for those starter profiles.

## The Fastest Demo

Create a task contract:

```bash
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Verify a change against that contract:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

Open `/tmp/shipguard-verdict/shipguard-verdict.md`. The report starts with the verdict, then shows the proof behind it.

## What ShipGuard Includes

| Surface | What it does |
| --- | --- |
| `shipguard prepare` | Creates a scoped task contract before agent work starts. |
| `shipguard verify` | Checks a diff, evidence receipts, and claims after agent work. |
| `shipguard full-audit` | Runs the broader ShipYard proof lane for this toolkit. |
| `shipguard ios ...` | Audits iOS structure, design, performance, modernization, preview routing, and report quality. |
| GitHub Actions | Publishes proof reports for PRs, releases, and evidence bundles. |
| Codex plugin | Gives Codex iOS maintenance guidance, proof routing, and report-quality behavior. |

Full command list: [Command Matrix](docs/command-matrix.md).

## Common Paths

For a new project:

```bash
shipguard init ios .
shipguard doctor ios .
```

For an agent task:

```bash
shipguard prepare "Your task" --path . --out /tmp/shipguard-task --profile ios
shipguard verify --task /tmp/shipguard-task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/evidence.json --out /tmp/shipguard-verdict
```

For iOS report quality:

```bash
shipguard ios design --path . --out /tmp/shipguard-design
shipguard ios performance --path . --out /tmp/shipguard-performance
shipguard ios report-quality --reports /tmp/shipguard-design --reports /tmp/shipguard-performance --out /tmp/shipguard-report-quality
```

For the Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill text is loaded.

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
