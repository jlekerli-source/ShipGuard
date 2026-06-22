<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local-first proof reports for AI-assisted development.
</p>

<p align="center">
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps you use Codex and other coding agents without accepting vague handoffs like "done", "tested", or "should work".

It gives every task a simple loop:

```text
scope the work -> collect proof -> check the claims -> review or block
```

ShipGuard is open source, local-first, and app-neutral. It works as a CLI today, with deeper Codex and iOS support where proof needs to be especially concrete.

## Why ShipGuard Exists

AI agents can make useful code changes quickly. The hard part is knowing whether the work is actually safe to review.

ShipGuard checks the parts that usually get hand-waved:

- What was the task supposed to touch?
- Which files changed?
- Were risky or protected files touched?
- Did tests or runtime checks actually run?
- Are the agent's claims supported by evidence?
- What should the maintainer do next?

The output is a Markdown and JSON report you can read, attach to a PR, or archive as release proof.

## Install

From a ShipGuard checkout or release package:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" version
"$HOME/.local/bin/shipguard" validate
```

The installer prints a short install receipt with the exact next commands and a `PATH` hint. Add `$HOME/.local/bin` to `PATH` when you want to run `shipguard` without the absolute path.

Add ShipGuard starter files to a project:

```bash
"$HOME/.local/bin/shipguard" init ios .
"$HOME/.local/bin/shipguard" doctor ios .
```

Starter profiles are available for `ios`, `web`, `backend`, and `cli`.

## Try It In 3 Minutes

Run the built-in proof demo from this repository:

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

Open:

```bash
/tmp/shipguard-verdict/shipguard-verdict.md
```

You should see a verdict plus a replay block:

```text
ShipGuard Proof Report
Status: pass
Validation: covered
Claims checked: accepted
Next action: review or merge with the attached proof

Quickstart Replay
Replay command: shipguard verify --task <shipguard-task.json> ...
Review packet: shipguard-verdict.json, shipguard-verdict.md, task, diff, receipt
```

If an agent claims something broad like "fully verified" without enough proof, the blocked report also includes `Unsupported Claim Replay`: the exact phrase, replay command, repair action, and non-claims so nobody mistakes a blocked verdict for proof.

For more examples, see [Verify-First Quickstart](docs/verify-first-quickstart.md).

## Daily Commands

Most users only need these:

| Command | Use it when |
| --- | --- |
| `shipguard init <profile> <repo>` | Add ShipGuard workflow files to a project. |
| `shipguard doctor <profile> <repo>` | Check whether the workflow files are present. |
| `shipguard prepare ...` | Create a scoped task contract before agent work. |
| `shipguard verify ...` | Check a diff, evidence, and claims after agent work. |
| `shipguard action verify-pr ...` | Audit the first GitHub Actions PR-proof workflow and consume the downloaded verdict artifact before trusting uploaded proof. |
| `shipguard lean audit --mode full ...` | Find repo-level code that may not need to exist, with mode-aware delete/simplify/keep/proof-blocked actions, clean-pass next probes, and proof-required safety boundaries. |
| `shipguard lean review --mode ultra ...` | Review the current diff before merge with selected-mode first-action proof, a current-diff-only decision map, delete/simplify subset, safety-boundary keep rows, hardware/host proof rows, matched/unmatched proof signals, runnable-check proof rows, and whole-repo non-claim. |
| `shipguard lean debt ...` | Harvest `ponytail:` and `shipguard-lean:` shortcut markers into marker-visibility, rot-risk, and trigger-watch reviews with ceilings, upgrade-trigger status, exact next actions, proof artifacts, stop conditions, and no fake benchmark-savings claims. |
| `shipguard lean gain ...` | Show benchmark-backed lean-code impact without inventing fake per-repo savings. |
| `shipguard docs-check ...` | Find broken local Markdown links. |
| `shipguard full-audit ...` | Run a broader ShipGuard maintainer audit. |

Common flow:

```bash
shipguard prepare "Fix the checkout empty state" --path . --out /tmp/task --profile ios
shipguard verify --task /tmp/task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/test-receipt.json --out /tmp/verdict
```

Full reference: [CLI](docs/cli.md) and [Command Matrix](docs/command-matrix.md).

## iOS And Codex

ShipGuard has first-class iOS and Codex support:

```bash
shipguard ios design --path . --out /tmp/ios-design --icon-brief
shipguard ios performance --path . --out /tmp/ios-performance
shipguard ios modernize --focus swift --path . --out /tmp/ios-modernize
shipguard ios report-quality --reports /tmp/ios-design --out /tmp/report-quality --shipguard-eval
```

Useful iOS surfaces:

- `ios design`: UI, motion, haptics, app type, design DNA, and icon brief guidance.
- `ios performance`: source-level performance risk report.
- `ios preview`: phone-shaped simulator preview for visual review.
- `ios devspace`: ChatGPT/Codex visual planning bridge for the preview.
- `ios report-quality`: checks whether ShipGuard reports are actually useful.

Refresh the local Codex plugin while developing ShipGuard:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill text is loaded.

## GitHub Action

ShipGuard can run in CI and attach proof reports to pull requests.

Start here:

- [GitHub Action guide](docs/github-action.md)
- [PR review bot mode](docs/pr-review-bot.md)
- [Release proof bundle](docs/release-proof.md)
- [Stable publication proof](docs/v4-stable-publication.md)

Stable publication requires public GitHub release metadata, downloaded or supplied public release assets, tag/manifest freshness, and post-release `release-consume` proof with digest coverage from those assets. It also includes a release visibility handoff so maintainers know whether to publish a new release, update notes/assets, attach external evidence, or keep the current public release unchanged. Source checkout proof, generated starter kits, fixture API responses, and synthetic fixtures only prove ShipGuard report quality.

For major ShipGuard milestones, `shipguard v4 stable-publication` can also write draft-only launch relay copy for Product Hunt, r/ShipGuard, X, and Hacker News. It does not post or submit anything; public actions require explicit approval for that exact launch run.

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

ShipGuard is the product. ShipYard is the maintainer layer around it: fixtures, evals, release proof, marketplace checks, report-quality tests, and product QA.

That split matters:

- ShipGuard is what developers install and run.
- ShipYard is how contributors keep ShipGuard honest.

## Learn More

- [Docs Home](docs/index.md)
- [Install and Doctor](docs/install-doctor.md)
- [Use in your repo](docs/use-in-your-repo.md)
- [iOS ShipGuard](docs/ios-shipguard.md)
- [Codex Marketplace Readiness](docs/codex-marketplace-readiness.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Open Source Model](docs/open-source.md)
- [Security Policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
