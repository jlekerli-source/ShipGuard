# Ringly Codex Workflows

Public operating rules for using Codex on risk-sensitive solo iOS work.

This repository shares the workflow layer I use around Ringly, an iPhone alarm app where reliability, notification truth, StoreKit behavior, and release proof matter. It does not contain private Ringly source code. It contains the reusable process: agent instructions, planning templates, validation routing, skill prompts, release checklists, and evaluation tasks.

The goal is simple: make AI-assisted coding repeatable, reviewable, and useful for real product maintenance.

## Who This Is For

- Solo developers using Codex or similar coding agents on production apps.
- iOS developers working near alarms, notifications, widgets, subscriptions, or release gates.
- Maintainers who want agents to plan, test, and hand off work with evidence instead of vague claims.

## Quick Start

Install from a release tarball:

```bash
tar -xzf codex-maintainer-v3.34.0.tar.gz
cd codex-maintainer-v3.34.0
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" version
```

Read the guided setup first:

- `docs/adoption-guide.md`: first 30 minutes with the workflow kit.
- `docs/arena.md`: benchmark runner for multiple maintainer fixtures.
- `docs/arena-compare-action.md`: GitHub Action for Arena comparison artifacts.
- `docs/autopsy.md`: evidence checks for AI coding runs.
- `docs/autopsy-github-actions.md`: upload autopsy reports as GitHub Actions artifacts.
- `docs/benchmark.md`: stable public benchmark and leaderboard format.
- `docs/check-run.md`: GitHub Checks API payloads from gate JSON.
- `docs/ci-gate.md`: CI gate command and GitHub Action for policy enforcement.
- `docs/ci-summary.md`: GitHub Actions step-summary output from gate JSON.
- `docs/command-matrix.md`: one-page map from maintainer jobs to CLI commands.
- `docs/demo-reports.md`: checked-in demo reports generated from public fixtures.
- `docs/maintainer-reliability-os.md`: the full policy-to-self-audit evidence loop.
- `docs/next-goal.md`: generate the next slash-goal release plan.
- `docs/policy.md`: configure protected paths, risky claims, and scope limits.
- `docs/pr-review-bot.md`: generate PR-ready review comments and badge JSON from autopsy reports.
- `docs/release-checklist.md`: release proof commands and publishing checks.
- `docs/release-attest.md`: compact release attestation and badge generation.
- `docs/release-consume.md`: one-command verification for downloaded release proof assets.
- `docs/release-consume-action.md`: GitHub Action for downstream release proof consumption.
- `docs/release-diff.md`: compare two release proof bundles across versions.
- `docs/release-diff-action.md`: GitHub Action for release proof bundle diff audits.
- `docs/release-evidence-action.md`: GitHub Action for static release evidence exports.
- `docs/release-evidence-bundle.md`: one-command local release evidence bundle.
- `docs/release-evidence-site.md`: static HTML export for release proof evidence.
- `docs/release-evidence-index.md`: static release history index for evidence site exports.
- `docs/release-evidence-verify.md`: consume and verify downloaded release evidence artifacts.
- `docs/release-index.md`: release proof catalog generation from manifests.
- `docs/release-manifest.md`: release tarball manifest and proof ledger output.
- `docs/release-proof.md`: one-command release proof bundle generation.
- `docs/release-proof-action.md`: GitHub Action for the release proof chain.
- `docs/release-proof-consumption.md`: downstream release proof verification from downloaded assets.
- `docs/release-proof-workflows.md`: copyable release proof workflow examples.
- `docs/release-replay.md`: replay verification for downloaded release assets.
- `docs/sarif.md`: convert Autopsy findings into SARIF for CI consumers.
- `docs/template-profiles.md`: iOS, web, backend, and CLI starter profile usage.
- `docs/transcript-corpus-action.md`: GitHub Action for transcript corpus verification artifacts.
- `docs/transcript-redaction.md`: redact and verify maintainer transcripts before public sharing.
- `docs/transcript-corpus.md`: verify and index a public-safe transcript corpus.
- `docs/transcript-verify-action.md`: GitHub Action for transcript verification artifacts.
- `docs/use-in-your-repo.md`: copy/paste setup for another repository.
- `docs/workflow-diagram.md`: visual workflow map.
- `docs/index.md`: GitHub Pages-ready documentation landing page.
- `CHANGELOG.md`: release history.
- `CODEX_TASK_TEMPLATE.md`: pasteable task contracts for new Codex threads.

Validate this workflow bundle:

```bash
./bin/codex-maintainer validate
```

Copy the iOS starter into another project:

```bash
./bin/codex-maintainer init ios ../my-ios-app
```

Copy the web starter into another project:

```bash
./bin/codex-maintainer init web ../my-web-app
```

1. Start each non-trivial Codex thread from `CODEX_TASK_TEMPLATE.md`.
2. Copy `AGENTS.md` into your repo root and replace the Ringly-specific paths with your project paths.
3. Use `PLANS.md` before risky work, release work, or changes that touch persistence, notifications, payments, or app lifecycle code.
4. Pick the relevant skill under `.agents/skills/` and paste it into your Codex task context.
5. Run the narrowest validation lane that proves the change.
6. Record blockers and proof honestly before merging or shipping.

For a worked example, read `examples/issue-to-plan-to-validation.md`.
For public proof without private app code, read `examples/demo-walkthrough.md`.
For agent-claim auditing, run `./bin/codex-maintainer autopsy` against `fixtures/autopsy/`.
For aggregate benchmark proof, run `./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena`.
For benchmark regression proof, run `./bin/codex-maintainer arena compare --left /tmp/arena-old/results.json --right /tmp/arena/results.json --out /tmp/arena-compare`.
To compare Arena results in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/arena-compare@v3.34.0`.
To publish a maintainer transcript safely, run `./bin/codex-maintainer transcript redact --in raw-transcript.md --out /tmp/redacted-transcript.md --report /tmp/redaction-report.json --private-term "InternalProjectName"`.
To verify a redacted transcript before publishing, run `./bin/codex-maintainer transcript verify --in /tmp/redacted-transcript.md --report /tmp/redaction-report.json --out /tmp/transcript-verify`.
To verify a redacted transcript in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/transcript-verify@v3.34.0`.
To publish a checked transcript corpus, run `./bin/codex-maintainer transcript corpus --source fixtures/transcripts --out /tmp/transcript-corpus --require-report true`.
To verify a checked transcript corpus in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/transcript-corpus@v3.34.0`.
For external benchmark packs, run `./bin/codex-maintainer arena import --source external-pack --out /tmp/imported-arena`.
For fixture-pack integrity metadata, run `./bin/codex-maintainer arena sign --fixture /tmp/imported-arena --out /tmp/imported-arena/PACK.json`.
For toolkit release readiness, run `./bin/codex-maintainer self-audit --out /tmp/codex-maintainer-audit`.
For the next improvement loop, run `./bin/codex-maintainer next-goal --out NEXT_GOAL.md`.
For CI-consumable findings, run `./bin/codex-maintainer sarif --report /tmp/autopsy/report.json --out /tmp/results.sarif`.
For workflow-run summaries, run `./bin/codex-maintainer ci-summary --gate /tmp/codex-gate/gate.json --out /tmp/codex-gate/summary.md`.
For Check Run payloads, run `./bin/codex-maintainer check-run --gate /tmp/codex-gate/gate.json --head-sha "$GITHUB_SHA" --out /tmp/codex-gate/check-run/payload.json`.
To post a Check Run after reviewing the payload, run `./bin/codex-maintainer check-run post --payload /tmp/codex-gate/check-run/payload.json --repo "$GITHUB_REPOSITORY" --out /tmp/codex-gate/check-run/response.json`.
For release proof files, run `./bin/codex-maintainer release-manifest --tarball dist/codex-maintainer-v3.34.0.tar.gz --out /tmp/release-proof`.
To verify release proof files, run `./bin/codex-maintainer release-manifest verify --manifest /tmp/release-proof/release-manifest.json --tarball dist/codex-maintainer-v3.34.0.tar.gz`.
To catalog release proof files, run `./bin/codex-maintainer release-index build --manifest /tmp/release-proof/release-manifest.json --out /tmp/release-index`.
To replay release proof from downloaded assets, run `./bin/codex-maintainer release-replay verify --manifest /tmp/release-proof/release-manifest.json --tarball dist/codex-maintainer-v3.34.0.tar.gz --index /tmp/release-index/release-index.json --ledger /tmp/release-proof/proof-ledger.md --out /tmp/release-replay`.
To generate a compact release attestation, run `./bin/codex-maintainer release-attest build --manifest /tmp/release-proof/release-manifest.json --replay /tmp/release-replay/replay-report.json --out /tmp/release-attestation`.
To generate the full proof bundle in one command, run `./bin/codex-maintainer release-proof build --out /tmp/release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/v3.34.0`.
To consume a published proof bundle, run `./bin/codex-maintainer release-consume verify --dir /tmp/codex-maintainer-v3.34.0 --out /tmp/codex-maintainer-v3.34.0/consumer-proof --version 3.34.0`.
To verify a published proof bundle in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.34.0`.
To compare two release proof bundles, run `./bin/codex-maintainer release-diff compare --left /tmp/codex-maintainer-old --right /tmp/codex-maintainer-v3.34.0 --out /tmp/release-diff`.
To compare two published proof bundles in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-diff@v3.34.0`.
To export a static evidence page, run `./bin/codex-maintainer release-evidence site --consume /tmp/codex-maintainer-v3.34.0/consumer-proof --diff /tmp/release-diff --out /tmp/release-site`.
To build a static evidence history, run `./bin/codex-maintainer release-evidence index --site /tmp/release-site --out /tmp/release-history`.
To build the local release evidence proof path in one command, run `./bin/codex-maintainer release-evidence bundle --assets /tmp/codex-maintainer-v3.34.0 --left /tmp/codex-maintainer-old --out /tmp/release-evidence-bundle --version 3.34.0`.
To export release evidence in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.34.0`.
To consume a downloaded release evidence artifact, run `./bin/codex-maintainer release-evidence verify --dir /tmp/codex-maintainer-release-evidence --out /tmp/codex-maintainer-release-evidence-verify --require-diff true --require-index true`.
To audit the checked-in broken evidence fixtures, run `./bin/codex-maintainer release-evidence negative-index --fixture fixtures/release-evidence/negative --out /tmp/codex-maintainer-negative-evidence`.
To verify release evidence artifacts in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-evidence-verify@v3.34.0`.
To publish the negative fixture index in GitHub Actions, use `jlekerli-source/ringly-codex-workflows/actions/release-evidence-negative-index@v3.34.0`.

## What Is Inside

- `AGENTS.md`: a root instruction template for mobile-app maintenance with high-risk feature areas.
- `CODEX_TASK_TEMPLATE.md`: a copyable task contract for Codex threads, including Command Center, verification, creative/game, and subagent splits.
- `PLANS.md`: a planning template that forces objective, scope, risks, tests, and rollback thinking.
- `SUBAGENTS.md`: inspector, implementer, tester, and reviewer roles for larger Codex tasks.
- `.agents/skills/`: reusable Codex skills for alarm testing, notification permissions, UI polish, release checklists, and bug triage.
- `scripts/`: release handoff, bug triage, alarm validation, packaging, and autopsy report generation.
- `bin/codex-maintainer`: a dependency-light CLI for profile init, validation, doctor checks, run scoring, autopsy reports, Arena comparison, transcript redaction, verification, corpus indexing, CI artifacts, and release-loop proof.
- `VERSION`: the release version used by the CLI and package script.
- `actions/validate/`: a reusable GitHub composite action for workflow-bundle validation.
- `actions/arena-compare/`: a reusable GitHub composite action for Arena comparison artifacts.
- `actions/release-proof/`: a reusable GitHub composite action for release proof artifacts.
- `actions/release-consume/`: a reusable GitHub composite action for downstream release proof verification.
- `actions/release-diff/`: a reusable GitHub composite action for release proof diff audits.
- `actions/release-evidence/`: a reusable GitHub composite action for static release evidence exports.
- `actions/release-evidence-verify/`: a reusable GitHub composite action for downloaded release evidence artifact verification.
- `actions/transcript-corpus/`: a reusable GitHub composite action for transcript corpus verification artifacts.
- `actions/transcript-verify/`: a reusable GitHub composite action for transcript verification artifacts.
- `docs/cli.md`: command reference for the CLI.
- `docs/arena.md`: guide for running the public maintainer fixture arena.
- `docs/arena-compare-action.md`: GitHub Action guide for comparing Arena result files.
- `docs/autopsy.md`: guide for auditing AI coding claims against diffs and tests.
- `docs/autopsy-github-actions.md`: minimal workflow for downloadable autopsy evidence.
- `docs/benchmark.md`: public AI maintainer reliability benchmark format.
- `docs/check-run.md`: GitHub Checks API payload export and optional posting from gate results.
- `docs/ci-gate.md`: generate CI artifacts and optional failure from maintainer evidence.
- `docs/ci-summary.md`: GitHub Actions step-summary Markdown from gate JSON.
- `docs/command-matrix.md`: command surface map for maintainer jobs.
- `docs/demo-reports.md`: generated reports from the fixture pack.
- `docs/maintainer-reliability-os.md`: policy, audit, arena, PR, CI, leaderboard, and self-audit loop.
- `docs/next-goal.md`: slash-goal release planning for the next improvement loop.
- `docs/policy.md`: plain policy config for project-specific risk rules.
- `docs/pr-review-bot.md`: warn/fail PR review comment mode for autopsy reports.
- `docs/release-checklist.md`: release validation and publishing checklist.
- `docs/release-attest.md`: compact release attestation and badge output.
- `docs/release-consume.md`: one-command downstream verification for downloaded release proof assets.
- `docs/release-consume-action.md`: GitHub Action for release proof consumption in CI.
- `docs/release-diff.md`: release proof bundle diff reports.
- `docs/release-diff-action.md`: GitHub Action for release proof bundle diff reports.
- `docs/release-evidence-action.md`: GitHub Action for release evidence site and index exports.
- `docs/release-evidence-bundle.md`: one-command local release evidence bundle.
- `docs/release-evidence-site.md`: static release evidence HTML export.
- `docs/release-evidence-index.md`: static release evidence history export.
- `docs/release-evidence-verify.md`: release evidence artifact consumption and verification.
- `docs/release-index.md`: release proof catalog generation.
- `docs/release-manifest.md`: release manifest and proof-ledger generation.
- `docs/release-proof.md`: one-command release proof bundle generation.
- `docs/release-proof-action.md`: GitHub Action for package, replay, and attestation proof.
- `docs/release-proof-consumption.md`: downstream verification flow for release proof assets.
- `docs/release-proof-workflows.md`: tag-triggered and manual workflow examples for release proof.
- `docs/release-replay.md`: downloaded release asset replay verification.
- `docs/sarif.md`: SARIF export for Autopsy findings and CI gate artifacts.
- `docs/template-profiles.md`: profile docs for iOS, web, backend, and CLI workflow starters.
- `docs/transcript-redaction.md`: transcript redaction, verification, and leak-audit report format.
- `docs/transcript-verify-action.md`: GitHub Action guide for transcript verification artifacts.
- `docs/github-action.md`: usage guide for the reusable action.
- `docs/adoption-guide.md`: practical onboarding path for new maintainers.
- `docs/use-in-your-repo.md`: copyable setup instructions for another repo.
- `docs/workflow-diagram.md`: visual map of the maintainer workflow.
- `docs/index.md`: lightweight documentation landing page for GitHub Pages.
- `.github/workflows/validate.yml`: a lightweight CI check for required files, skill metadata, shell syntax, and whitespace.
- `examples/issue-to-plan-to-validation.md`: an anonymized sample from messy issue to plan, proof, and handoff.
- `examples/prompt-pack.md`: copyable prompts for common maintainer tasks.
- `examples/review-comment.md`: expected PR comment and badge output from a dangerous report.
- `examples/adoption-checklist.md`: copyable rollout checklist for a new project.
- `examples/arena-results.md`: expected aggregate output from the public arena fixture pack.
- `examples/redacted-transcript.md`: synthetic redacted transcript output for public sharing.
- `examples/demo-walkthrough.md`: proof path for clone and release-package usage.
- `examples/workflows/arena-compare.yml`: manual workflow for uploading Arena comparison artifacts.
- `examples/workflows/transcript-verify.yml`: manual workflow for uploading transcript verification artifacts.
- `examples/workflows/release-consume-verify.yml`: manual release proof consumption workflow.
- `examples/workflows/release-diff-compare.yml`: manual release proof diff workflow.
- `examples/workflows/release-evidence-bundle.yml`: manual one-action release evidence bundle workflow.
- `examples/workflows/release-evidence-consume.yml`: two-job workflow that exports and verifies release evidence.
- `examples/workflows/release-evidence-export.yml`: manual release evidence export workflow.
- `examples/demo-reports/`: generated demo arena reports and leaderboard JSON.
- `examples/autopsy-report.md`: sample autopsy expectations for dangerous and clean runs.
- `fixtures/demo-ios-repo/`: fake iOS-style repo for demo and package testing.
- `fixtures/autopsy/`: good, weak, and dangerous AI-run fixtures for report testing.
- `fixtures/arena/`: public benchmark fixture pack for aggregate arena runs.
- `fixtures/external-arena-pack/`: sample external fixture pack for import testing.
- `fixtures/release-evidence/negative/`: invalid release evidence fixtures for verifier failure coverage.
- `templates/ios/`: a starter workflow bundle for adapting these rules to another iOS app.
- `templates/web/`: a starter workflow bundle for adapting these rules to a web app.
- `SCORECARD.md`: a lightweight rubric for judging whether a Codex run produced usable maintainer evidence.
- `EVALUATION_SUITE.md`: realistic benchmark tasks for future agent runs.
- `POSTS.md`: short public posts explaining the workflow.
- `CHANGELOG.md`: release history and adoption milestones.
- `CODEX_TASK_TEMPLATE.md`: copyable thread-start template for audit, implementation, verification, release, and design work.

## Workflow Map

```text
request
  -> read AGENTS.md
  -> choose risk lane
  -> write or update PLANS.md
  -> make the smallest scoped change
  -> run the narrowest proof command
  -> review the diff and evidence
  -> ship only what is proven
```

## Why This Matters

AI coding agents are strongest when the project gives them structure. Ringly is my live test bed for that structure: narrow scopes, explicit guardrails, real validation, and clear handoffs when proof is missing.

This repository turns those habits into public templates that other developers can adapt without copying the private app.

## Current Status

This is an early public workflow kit. The next priorities are documented in `ROADMAP.md`, and contribution guidance lives in `CONTRIBUTING.md`.

The repository is also configured as a GitHub template, so you can start from it directly and then remove the Ringly-specific examples you do not need.

## License

MIT. See `LICENSE`.
