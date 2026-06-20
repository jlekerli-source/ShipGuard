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

ShipGuard helps you use Codex and other coding agents without trusting vague handoffs like "done", "tested", or "should work".

It turns agent work into a simple review loop:

```text
prepare the task -> attach evidence -> verify the claims -> ship, review, or block
```

ShipGuard is local-first, open source, and app-neutral. The iOS workflow is the most mature today, with web, backend, and CLI profiles growing from the same proof engine.

## What You Get

- A local CLI for proof-gated agent work.
- Starter profiles for iOS, web, backend, and CLI repos.
- GitHub Actions helpers that publish reviewable proof reports.
- A Codex iOS plugin for design, performance, modernization, preview, and report-quality work.
- Public fixtures and tests so ShipGuard improves from evidence, not branding.

## Install

From this checkout:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
shipguard validate
```

Then add ShipGuard to a repo:

```bash
shipguard init ios .
shipguard doctor ios .
```

Use `web`, `backend`, or `cli` instead of `ios` for those starter profiles.

More detail: [Install And Doctor](docs/install-doctor.md).

## First Proof Report

Run the demo from a ShipGuard checkout:

```bash
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable

./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

Open `/tmp/shipguard-verdict/shipguard-verdict.md`.

The report starts with the decision, then shows the evidence behind it:

```text
Status: pass
Validation: covered
Claims checked: accepted
Next action: review or merge with the attached proof
```

Full walkthrough: [Verify-First Quickstart](docs/verify-first-quickstart.md).

## Core Commands

| Command | Use it when you need to |
| --- | --- |
| `shipguard prepare` | define the task, allowed scope, and expected validation before agent work starts |
| `shipguard verify` | check a diff, evidence receipts, and agent claims before review or merge |
| `shipguard init` | add ShipGuard starter files to a repo |
| `shipguard doctor` | confirm the starter profile is installed correctly |
| `shipguard ios design` | review UI/UX, motion, haptics, app-type fit, and icon direction |
| `shipguard ios performance` | find iOS performance risks and proof needed for simulator or device validation |
| `shipguard inspect` | summarize ShipGuard's own proof state and the next maintainer action |

Full command list: [Command Matrix](docs/command-matrix.md).

## GitHub Actions

ShipGuard can run in CI and upload Markdown/JSON proof reports on pull requests.

Start from:

- [GitHub Action guide](docs/github-action.md)
- [Example PR workflow](examples/workflows/verify-pr.yml)

## Codex Plugin

Install the local iOS plugin while developing ShipGuard:

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

ShipYard is the maintainer workspace behind ShipGuard: fixtures, evals, package checks, release proof, plugin readiness, and roadmap execution.

Most users should start with `prepare`, `verify`, `init`, and `doctor`. ShipYard tools exist to keep the product honest.

## Learn More

- [Docs index](docs/index.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Open source model](docs/open-source.md)
- [Security policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
