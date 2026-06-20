<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local-first CLI and Codex plugin for proof-gated app maintenance.
</p>

<p align="center">
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps developers use AI coding agents without trusting vague handoffs like "done", "tested", or "should work".

It turns agent work into a simple proof loop:

```text
prepare the task -> attach evidence -> verify the claims -> review or ship
```

ShipGuard is open source, app-neutral, and local-first. The deepest support today is for iOS and Codex, with starter profiles for web, backend, and CLI projects.

## The Problem

AI coding tools can move fast, but the handoff is often weak:

- the task scope is unclear
- the changed files are not easy to review
- test claims are not backed by receipts
- risky files are touched quietly
- the next action is vague

ShipGuard makes those things explicit before the work is treated as ready.

## The Core Loop

1. Prepare a scoped task contract.
2. Let the coding agent work inside that scope.
3. Attach test logs, receipts, screenshots, or runtime proof.
4. Verify the diff, evidence, and claims.
5. Review, merge, or block with a concrete reason.

The goal is not to slow developers down. The goal is to make fast AI-assisted work reviewable.

## Install

From a ShipGuard checkout or release package:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
shipguard validate
```

Add ShipGuard starter files to a project:

```bash
shipguard init ios .
shipguard doctor ios .
```

Use `web`, `backend`, or `cli` instead of `ios` for those starter profiles.

## First Proof Report

Run this from the ShipGuard checkout:

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

Open the verdict:

```bash
/tmp/shipguard-verdict/shipguard-verdict.md
```

The report leads with the decision:

```text
ShipGuard Proof Report
Status: pass
Validation: covered
Claims checked: accepted
Next action: review or merge with the attached proof
```

See [Verify-First Quickstart](docs/verify-first-quickstart.md) for pass, review, and blocked examples.

## What ShipGuard Includes

| Surface | Purpose |
| --- | --- |
| `prepare` / `verify` | task scope, evidence receipts, claim checks, and merge verdicts |
| `init` / `doctor` | starter workflow files and repo setup checks |
| GitHub Action examples | PR proof reports and CI handoff patterns |
| iOS reports | design, performance, modernization, preview, Devspace, and report-quality audits |
| Codex plugin | local Codex guidance for iOS ShipGuard workflows |
| ShipYard | maintainer fixtures, evals, release proof, marketplace checks, and product QA |

Most users should start with `prepare`, `verify`, `init`, and `doctor`.

## Common Commands

```bash
shipguard init ios .
shipguard doctor ios .
shipguard prepare "Fix the checkout empty state" --path . --out /tmp/task --profile ios
shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/test-receipt.json --out /tmp/verdict
shipguard docs-check . --out /tmp/docs-check
```

iOS-specific reports:

```bash
shipguard ios design --path . --out /tmp/ios-design --icon-brief
shipguard ios performance --path . --out /tmp/ios-performance
shipguard ios report-quality --reports /tmp/ios-design --out /tmp/report-quality
```

Full command reference: [CLI](docs/cli.md) and [Command Matrix](docs/command-matrix.md).

## Codex Plugin

Install or refresh the local ShipGuard plugin while developing:

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

## Learn More

- [Install and Doctor](docs/install-doctor.md)
- [Verify-First Quickstart](docs/verify-first-quickstart.md)
- [GitHub Action](docs/github-action.md)
- [iOS ShipGuard](docs/ios-shipguard.md)
- [Codex Marketplace Readiness](docs/codex-marketplace-readiness.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Open Source Model](docs/open-source.md)
- [Security Policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
