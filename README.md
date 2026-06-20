<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  A local proof layer for AI-assisted software work.
</p>

<p align="center">
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps you use Codex and other coding agents without accepting vague status updates like "done", "tested", or "looks good".

It turns agent work into a reviewable loop:

```text
scope the change -> collect evidence -> check the claims -> ship or block
```

The result is a local Markdown and JSON verdict that says what was actually proven, what is still missing, and what to do next.

ShipGuard is not tied to any single app. It is a reusable proof system for production software maintenance.

## Why ShipGuard

AI can write code quickly. Production maintenance still needs discipline.

ShipGuard is built for developers who want agent speed without losing control of:

- task scope
- risky files and ownership boundaries
- test and build evidence
- unsupported agent claims
- release proof
- local-first review artifacts

The strongest track today is iOS, with Codex plugin support and audits for app risk, performance, design quality, modernization, previews, release readiness, and proof handoff. ShipGuard also includes starter profiles for web, backend, and CLI projects.

## Try It

From a ShipGuard checkout:

```bash
./bin/shipguard validate
./bin/shipguard version
```

Latest release package: `shipguard-v3.131.0.tar.gz`.

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

## The Core Loop

Create a task contract before agent work:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

Check the result after the agent works:

```bash
shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --claim "Implemented notification permission copy." \
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

## Useful Commands

| Need | Command |
| --- | --- |
| Check ShipGuard itself | `shipguard validate` |
| Add starter files | `shipguard init ios .` |
| Check a repo setup | `shipguard doctor ios .` |
| Scope agent work | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify claims and proof | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Inspect iOS risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Audit iOS performance | `shipguard ios performance --path . --out /tmp/ios-performance` |
| Audit iOS design | `shipguard ios design --path . --out /tmp/ios-design` |
| Run the maintainer proof lane | `shipguard full-audit --path . --out /tmp/shipguard-full-audit` |

See the [CLI reference](docs/cli.md) for the complete command list.

## Codex Plugin

ShipGuard ships with an iOS-focused Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill text is loaded.

## GitHub Action

ShipGuard can run proof checks in CI and attach evidence to pull requests.

Start here:

- [GitHub Action](docs/github-action.md)
- [Verify-first quickstart](docs/verify-first-quickstart.md)
- [Release proof](docs/release-proof.md)

## What Is In The Repo

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

ShipYard is the maintainer side of ShipGuard: fixtures, evals, release proof, package checks, plugin readiness, and roadmap execution.

Useful links:

- [Docs index](docs/index.md)
- [Roadmap](ROADMAP.md)
- [Next goal](NEXT_GOAL.md)
- [Changelog](CHANGELOG.md)
- [Open source model](docs/open-source.md)

Current published release: `v3.131.0`.

## License

MIT. See [LICENSE](LICENSE).
