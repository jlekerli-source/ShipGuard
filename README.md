<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="96" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local-first CLI + Codex plugin for proof-gated app maintenance.
</p>

ShipGuard helps developers use AI coding agents without accepting vague claims like "tests passed" or "looks good."

It turns agent work into a simple loop:

```text
prepare the task -> make the change -> attach proof -> verify the diff -> ship only what is proven
```

## Why ShipGuard

- Keeps AI work scoped to the task.
- Checks changed files, protected paths, evidence receipts, and agent claims.
- Produces reviewer-friendly Markdown and machine-readable JSON.
- Runs locally against your repo; ShipGuard does not require a hosted service.
- Includes a Codex plugin, CLI reports, GitHub Actions examples, public fixtures, and release-proof tooling.

ShipGuard is not tied to any single app. The strongest current workflow is iOS, but the core proof loop also supports web, backend, and CLI projects.

## Quick Start

Install from a checkout or extracted release package:

```bash
# if using a release package:
tar -xzf shipguard-v3.131.0.tar.gz && cd shipguard-v3.131.0

PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" version
"$HOME/.local/bin/shipguard" validate
```

Initialize a repo and run RepoVitals:

```bash
shipguard init ios .
shipguard doctor ios .
```

Start a proof-gated task:

```bash
shipguard prepare "Add notification permission copy" \
  --path . \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable
```

After Codex or another agent edits the repo, verify the exact diff and proof:

```bash
shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

The report starts with a concise verdict:

```text
ShipGuard Proof Report
Status: pass
Validation: 1/1 covered
Claims checked: 1/1 accepted
Risk files: 0 risk file(s)
```

## Try The Demo

Run the public verify-first demo:

```bash
./tests/verify_first_quickstart_test.sh
```

Or read the walkthrough:

- [Install And Doctor](docs/install-doctor.md)
- [Verify-First Quickstart](docs/verify-first-quickstart.md)
- [Task Contract](docs/task-contract.md)

## Core Commands

| Goal | Command |
| --- | --- |
| Install and prove the CLI works | `docs/install-doctor.md` |
| Add ShipGuard to a repo | `shipguard init ios .` |
| Check starter files | `shipguard doctor ios .` |
| Prepare a scoped task | `shipguard prepare "task" --path . --out /tmp/task --profile ios` |
| Verify a diff and proof | `shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/receipt.json --out /tmp/verdict` |
| Inspect iOS project risk | `shipguard ios doctor --path . --out /tmp/ios-doctor` |
| Run the product-value audit | `shipguard value-gauntlet --path . --out /tmp/shipguard-value` |
| Check docs | `shipguard docs-check . --out /tmp/shipguard-docs` |

## Codex Plugin

ShipGuard includes an iOS-focused Codex plugin:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the updated skill metadata is loaded.

## Documentation

- [Documentation Index](docs/index.md)
- [CLI Reference](docs/cli.md)
- [Command Matrix](docs/command-matrix.md)
- [iOS ShipGuard](docs/ios-shipguard.md)
- [GitHub Actions](docs/github-action.md)
- [Open Source Model](docs/open-source.md)
- [Privacy](docs/privacy.md)
- [Security Threat Model](docs/security-threat-model.md)
- [Product Strategy](docs/product-strategy.md)
- [Roadmap](ROADMAP.md)

## Project Layout

- `bin/shipguard`: CLI entry point.
- `scripts/`: report engines and proof tooling.
- `plugins/ios-shipguard/`: Codex plugin bundle.
- `templates/`: starter profiles for iOS, web, backend, and CLI repos.
- `docs/`: user docs and product strategy.
- `examples/` and `fixtures/`: public demos and regression fixtures.
- `tests/`: shell-based validation lanes.
- `actions/`: reusable GitHub Actions.

## Status

Current published release: `v3.131.0`.

`main` is ahead of the published release and is actively improving the first-run install, doctor, verify, report-quality, and release-proof paths. See [NEXT_GOAL.md](NEXT_GOAL.md), [CHANGELOG.md](CHANGELOG.md), and [ROADMAP.md](ROADMAP.md) for the current ShipYard work.

## License

MIT. See [LICENSE](LICENSE).
