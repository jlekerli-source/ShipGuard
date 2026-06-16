# Shipguard for Codex Docs

Local-first Codex guardrails for solo iOS developers shipping permission-heavy apps.

Shipguard helps Codex understand the app before editing, ask blocked product/proof questions, preview simulator UI through a browser or MCP widget, and keep proof claims tied to real evidence.

## Start Here

| Need | Read |
| --- | --- |
| First adoption path | [Adoption guide](adoption-guide.md) |
| Shortest useful loop | [Core loop](core-loop.md) |
| iOS plugin and modes | [iOS Shipguard](ios-shipguard.md) |
| CLI command map | [Command matrix](command-matrix.md) |
| Full CLI reference | [CLI reference](cli.md) |
| Copy into another repo | [Use in your repo](use-in-your-repo.md) |

## First Run

```bash
./bin/codex-maintainer validate
./bin/codex-maintainer ios demo --out /tmp/ios-shipguard-first-run
```

Then open `/tmp/ios-shipguard-first-run/README.md` to inspect the generated public-fixture report bundle.

For a normal iOS planning path:

```bash
./bin/codex-maintainer ios doctor --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-doctor
./bin/codex-maintainer ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor /tmp/ios-shipguard-doctor/ios-doctor.json \
  --out /tmp/ios-shipguard-inventory
./bin/codex-maintainer ios plan \
  --mode permission-audit \
  --inventory /tmp/ios-shipguard-inventory/ios-inventory.json \
  --out /tmp/ios-shipguard-plan/ios-plan.md
./bin/codex-maintainer ios prove \
  --plan /tmp/ios-shipguard-plan/ios-plan.json \
  --out /tmp/ios-shipguard-proof
```

## iOS Preview And Handoff

| Surface | Purpose |
| --- | --- |
| [iOS Preview](ios-preview.md) | Serve a phone-shaped Simulator screenshot in Codex's browser and record click, right-click, and note receipts. |
| [Shipguard Devspace](shipguard-devspace.md) | Expose the preview bridge as a local ChatGPT Apps / MCP widget with Codex handoff tools. |
| [iOS Shipguard](ios-shipguard.md) | Route preview, permissions, StoreKit, release proof, privacy, and UI-polish work through the right mode. |
| [Workflow diagram](workflow-diagram.md) | Visual overview of the maintainer loop. |

## Maintainer Evidence

| Area | Docs |
| --- | --- |
| Agent claim auditing | [Autopsy](autopsy.md), [Autopsy in GitHub Actions](autopsy-github-actions.md), [SARIF export](sarif.md) |
| CI and PR feedback | [CI gate](ci-gate.md), [CI summary](ci-summary.md), [Check Run payload](check-run.md), [PR review bot](pr-review-bot.md) |
| Benchmarks | [Arena](arena.md), [Arena compare action](arena-compare-action.md), [Benchmark format](benchmark.md), [Demo reports](demo-reports.md) |
| Transcript safety | [Transcript redaction](transcript-redaction.md), [Transcript corpus](transcript-corpus.md), [Transcript verify action](transcript-verify-action.md), [Transcript corpus action](transcript-corpus-action.md) |
| Docs quality | [Docs check](docs-check.md), [Docs check action](docs-check-action.md) |

## Release Proof

| Area | Docs |
| --- | --- |
| Release planning | [Release checklist](release-checklist.md), [Release proof bundle](release-proof.md), [Release proof workflows](release-proof-workflows.md) |
| Release metadata | [Release manifest](release-manifest.md), [Release index](release-index.md), [Release replay](release-replay.md), [Release attestation](release-attest.md) |
| Downstream verification | [Release consume](release-consume.md), [Release consume action](release-consume-action.md), [Release proof consumption](release-proof-consumption.md) |
| Cross-release review | [Release diff](release-diff.md), [Release diff action](release-diff-action.md) |
| Evidence publishing | [Release evidence bundle](release-evidence-bundle.md), [Release evidence site](release-evidence-site.md), [Release evidence index](release-evidence-index.md), [Release evidence action](release-evidence-action.md), [Release evidence verification](release-evidence-verify.md) |

## Project Reference

| Need | Read |
| --- | --- |
| Starter profiles | [Template profiles](template-profiles.md) |
| Policy configuration | [Policy configuration](policy.md) |
| Slash-goal release planning | [Next goal generator](next-goal.md) |
| Full reliability loop | [Maintainer Reliability OS](maintainer-reliability-os.md) |
| Reusable action overview | [GitHub Action](github-action.md) |
| Release history | [Changelog](../CHANGELOG.md) |
