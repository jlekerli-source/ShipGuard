# Changelog

## Unreleased

- Added `scenarioFailureReceipts` to `shipguard value-gauntlet`: a public bad-evidence receipt now proves ShipGuard blocks unsafe transcripts, broken docs, stale Codex plugin cache metadata, and incomplete release proof with non-zero exits or blocked reports before the next priority advances to scenario-remediation receipts.
- Added expected non-zero receipt-command support to the value-gauntlet receipt runner so failure-path receipts pass only when ShipGuard rejects bad evidence and still writes the expected machine-readable proof.
- Added `scenarioMatrixReceipts` to `shipguard value-gauntlet`: a public full maintainer-loop receipt now runs iOS doctor/inventory/plan/design, report-quality, docs-check, transcript redaction and verification, CI gate and summary, Codex plugin status, and release manifest/index/replay against public fixtures and a synthetic release package before the next priority advances to scenario-failure receipts.
- Added safe receipt fixture preparation to `shipguard value-gauntlet`, including temporary prepared files and deterministic synthetic tarballs under the receipt output directory so release workflows can be tested without mutating `dist/` or private app repos.
- Fixed `shipguard transcript redact` so redaction works when no `--private-term` arguments are supplied on macOS Bash with `set -u`, and added coverage for the default no-private-term privacy path.
- Added `workflowChainReceipts` to `shipguard value-gauntlet`: a public end-to-end receipt now runs design report -> report-quality -> spec-workflow -> spec report-quality -> next-goal against `fixtures/demo-ios-repo`, proving report-quality questions become SpecForge tasks, validation commands, slash plan/goal text, and a NextRail handoff before the next priority advances to scenario-matrix receipts.
- Added `skillPluginRuntimeReceipts` to `shipguard value-gauntlet`: public receipt fixtures now execute iOS ShipGuard design-audit routing, starter UI-polish inventory/plan routing, and plugin cache status proof against public/demo inputs, so skill/plugin usefulness is tested through real ShipGuard commands before the next priority advances to workflow-chain receipts.
- Added `runtimeCommandFamilyCoverage` to `shipguard value-gauntlet`: it now executes `--help` for all 51 registered public ShipGuard commands, fixes top-level help routing for command families that previously treated `--help` as an invalid file/path/subcommand, and moves the next priority to skill/plugin runtime receipt fixtures.
- Added `runtimeOutputNegativeFixtures` to `shipguard value-gauntlet`: synthetic public bad-output fixtures now prove decorative empty reports and boundaryless design reports are rejected, and the next priority advances to broader command-family runtime execution.
- Added `runtimeOutputProbe` to `shipguard value-gauntlet`: it runs representative ShipGuard commands on public/demo inputs, scores their JSON/Markdown artifacts for machine-readable usefulness, tightens Brand Deck and DockCheck report shape, and retired the old "just run representative commands" next step.
- Added a Lowest-Value Surface Probe to `shipguard value-gauntlet`: after command/skill/plugin/action/doc coverage passes, it ranks deeper evidence signals, upgrades thin starter-skill QA hooks, and escalates all-green static coverage into a runtime-output usefulness probe instead of pretending the ShipYard is finished.
- Added report-quality fixture coverage detection so questions already covered by promoted public fixtures under `fixtures/ios-report-quality` keep their actionability evidence, suppress duplicate fixtureCandidates, render a `Fixture Coverage` section, and move the priority action to the next uncovered question.
- Fixed `release-proof build` so optional proof links like `--issue-url` and `--ci-run-url` are only forwarded when present, matching the documented release command and allowing proof bundles without a tracking issue URL.
- Promoted the ShipGuard Tool Value Gauntlet actionability question into a public `fixtures/ios-report-quality/value-gauntlet-actionability` synthetic fixture so report-quality proves low-value surface concerns can become reusable eval coverage without copying private app evidence.
- Added ShipGuard Tool Value Gauntlet with `shipguard value-gauntlet`, JSON/Markdown output, command/skill/plugin/action/doc/package-proof scoring, report-quality routing, package proof, self-audit coverage, and deterministic eval routing for "test every skill/plugin" product-QA requests.
- Expanded ShipGuard Brand Deck into a toolkit-wide naming system with `shipguard brand`, 51 public command-family surface names, compatibility for `shipguard ios brand`, public-command coverage checks, docs coverage, package proof, self-audit coverage, and routing eval support for funny/vibey/techy naming requests.
- Added ShipGuard ShipYard as the workshop-level product place for the toolkit bundle, with Brand Deck JSON/Markdown proof and docs/plugin guidance while keeping repository and automation paths unchanged.
- Added Brand Deck nitty-gritty call signs for script, scanner, test, action, fixture, JSON, Markdown, log, package, and plugin file families so human-facing output can feel ShipGuard-native without renaming automation-sensitive paths.
- Added Brand Deck actionability questions so `shipguard ios report-quality` can turn read-only `shipguard brand` output into prioritized naming-system improvements instead of the generic "add reportQualityQuestions" fallback; `next-goal` required proof now includes Brand Deck strict proof and `tests/ios_branding_test.sh`.
- Renamed the iOS build/debug/preview/profiler front door to `shipguard ios launchdeck`, with `ios-launchdeck.*` outputs, LaunchDeck receipt rules, LaunchDeck report-quality fixtures, and LaunchDeck routing eval modes replacing the previous generic naming.
- Added report-quality source-finding visibility: source report findings now appear in `sourceFindings`, `sourceIssueVisibility`, and a Markdown `Source Report Findings` section, while report-quality's own `findings` still only represent report-quality defects.
- Promoted LaunchDeck receipt gaps into first-class report-quality fixture work: weak `ios launchdeck` receipt reports now prioritize receipt-specific actionability questions and materialize `ios-launchdeck-receipt-quality-fixture` starter fixtures instead of generic performance/preview candidates.
- Added `shipguard ios launchdeck --receipt <file-or-dir>` so ShipGuard can grade LaunchDeck/XcodeBuildMCP execution receipts after a run, distinguish route plans from proof, and flag missing build/run, UI, preview, log, or profiler evidence for the selected lane.
- Added `shipguard ios launchdeck` as a ShipGuard-native front door for the LaunchDeck surface, emitting repo-aware XcodeBuildMCP build/run, debugger, simulator browser, SwiftUI preview hot reload, and performance-profiler handoffs with proof boundaries, shareable output, report-quality scoring, and package coverage.
- Routed shell-backed `bin/shipguard` subcommands through `bash` from the wrapper so macOS provenance metadata cannot kill helper scripts before their help or validation paths run.
- Expanded `ios spec-workflow` into a fuller ShipGuard-native integration of external workflow inspiration: it now emits `requirements-checklist.md`, `integration-decisions.md`, and `consistency-analysis.md`, records ShipGuard-owned adaptations from Spec Kit, CodexPro, Expo, Xcode Build Optimization Agent Skills, and the OpenAI native iOS preview loop, and keeps those ideas as native proof/report-quality artifacts rather than vendored code.
- Tightened `ios report-quality` so spec-workflow bundles must declare and include the requirements checklist, integration decisions, and consistency analysis, preserve report-quality questions through those artifacts, and fail review when those native integration files are missing or placeholder-only.
- Added `shipguard ios external-audit` so external repos, workflow projects, and post URLs become a ShipGuard-native source audit with capability matrix, replacement ledger, implementation backlog, license boundary, and report-quality questions before any integration claim.
- Added Design Motion Principles as a native external-audit source profile and extended `ios design` with `motionQualityGates` for frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance checks; Expo source matching now avoids false positives such as matching `EAS` inside `easing`.
- Added an `external-source-audit` routing eval fixture so requests to integrate Spec Kit, CodexPro, Expo, Design Motion Principles, X posts, or other external sources must route through read-only external-audit, report-quality, replacement-ledger, and validation-command proof instead of Devspace or generic planning.
- Hardened `bin/shipguard` iOS Python subcommands to run through `${PYTHON:-python3}` instead of direct script execution, avoiding macOS executable-metadata kills while preserving the public CLI.
- Added `ios report-quality --write-fixture-candidates <dir>` so fixtureCandidates can be materialized as public-safe synthetic starter directories with fixture metadata, a minimal report pair, validation notes, and no copied private report paths or app details.
- Added promotion metadata for materialized report-quality fixtures, including `fixture-promotion-manifest.json`, `PROMOTION.md`, suggested repo-relative fixture paths, placeholder copy commands, validation commands, and a private-data review checklist without auto-copying candidates into the repo.
- Taught `ios report-quality` to consume `fixture-promotion-manifest.json` as materialized-fixture metadata instead of grading it as a source report, and to flag unsafe suggested fixture paths, missing copy placeholders, missing validation commands, incomplete review checklists, or stale promotion guides.
- Added a public materialized external-audit fixture and stopped already-materialized synthetic fixture reports from recursively generating another `fixtureCandidates` entry while preserving their actionability questions.
- Added report-quality `fixtureCandidates` so private read-only Ringly/Ilmify observations can be converted into public synthetic fixture recipes with validation commands and private-data policy instead of copying private code or app-specific details.
- Deduplicated repeated report-quality actionability questions while preserving duplicate counts and duplicate source reports, so real-app product-QA output stays prioritized without hiding later unique questions.

## v3.70.1 - Package Codex Status Fallback

- Fixed `shipguard codex status --strict` for clean package/CI environments by resolving the current checkout or extracted package CLI when no installed global `shipguard` command exists.
- Added package-release coverage that runs Codex status without `SHIPGUARD_CLI`, without `~/.local`, and without `shipguard` on `PATH` so release proof catches consumer install assumptions.
- Added diagnostics to the package release test so GitHub Actions reports the exact failing line and command instead of hiding package proof failures.

## v3.70.0 - Plugin Review And Devspace MCP Launch

- Fixed the iOS ShipGuard plugin MCP launcher so installed Codex plugin caches resolve an installed `shipguard` CLI instead of pointing at missing cache-relative source scripts.
- Added Codex status/package checks for stale Devspace MCP sidecar configuration and stale installed CLI versions used by the MCP launcher.
- Added plugin interface website, privacy, and terms URLs and trimmed default prompts to the three Codex actually uses.
- Made release packaging write tarballs atomically so parallel validation cannot leave a partially written `dist/shipguard-vX.Y.Z.tar.gz`.
- Added a ShipGuard-native open-source operating surface with support, governance, code of conduct, proposal/bug templates, package proof, and docs routing.
- Added LaunchDeck visual-loop routing guidance so ShipGuard complements simulator browser, SwiftUI preview, and hot reload workflows with receipts, redaction, report quality, and Codex handoff proof.

## v3.69.0 - Performance Validation Gates And Starter Hygiene

- Added `validationRoute` and `stopCondition` to grouped `ios performance` actions so reports show how to prove the first experiment and when to stop before broad refactors; `ios report-quality` now flags grouped performance output that hides validation routes or stop conditions from JSON or Markdown.
- Made copied starter skills product-neutral instead of Ringly-branded, copied the bug-triage prompt helper during `shipguard init`, and taught `doctor`, validation, and package tests to require that generated helper file.

## v3.68.0 - Performance First Experiment Gate

- Added `firstExperiment` to grouped `ios performance` actions so reports name one reversible proof step before broad refactors, and let `ios report-quality` flag grouped performance output that hides the first experiment from JSON or Markdown.
- Hardened release packaging and prefix installation so dirty local `__pycache__`, `*.pyc`, `.cache`, `DerivedData`, `dist`, and `.git` artifacts cannot leak into published or installed ShipGuard payloads.
- Fixed iOS ShipGuard skill CLI routing for app checkouts by resolving `SHIPGUARD_CLI` from app-local `./bin/shipguard`, installed `shipguard`, or `$HOME/.local/bin/shipguard` instead of assuming every target app repo contains ShipGuard's source tree.
- Split `ios performance` proof guidance into `localProof` and `manualProof`, render Codex-local versus manual/device proof in Markdown, and let `ios report-quality` flag performance reports that keep proof guidance vague or hidden from Markdown.
- Added high-severity justification for `ios performance` findings so high findings explain the threshold, actor context, or source signal behind severity, render that reason in Markdown, and let `ios report-quality` flag missing JSON or Markdown severity explanations.
- Added grouped performance next actions so `ios performance` summarizes repeated rule clusters before individual findings, caps repeated high rows in Markdown, and lets `ios report-quality` flag repeated performance reports that lack `groupedActionPlan` or a visible `Grouped Next Actions` section.
- Added a performance finding explanation gate so `ios report-quality` flags `ios performance` findings that omit an `impact`/`whyItMatters` explanation or hide that explanation from Markdown, and adjusted performance product-QA questions so completed explanation coverage no longer remains the top next action.
- Added report-quality priority actions so read-only ShipGuard product-QA passes rank the next concrete finding or actionability question instead of leaving developers with an unprioritized checklist.
- Added spec-workflow slash handoff coverage so report-quality flags bundles whose `slashPlan`, `slashGoal`, or `ios-spec-workflow.md` drops the copy-ready `/plan` and `/goal` next-loop handoff.
- Fixed spec-workflow actionability question preservation so repeated report-quality questions are deduplicated before clarifying-question and task caps are applied.

## v3.59.0 - iOS Product QA and Spec Workflow Gates

- Added scoped `shipguard next-goal` output with bounded scope, completion receipt, and following `/goal` handoff support.
- Added iOS `performance-audit` mode and `shipguard ios performance` source scanner for FPS, hitches, profiler fallback, sampled stacks, before/after comparison, ranked SwiftUI/runtime hotspots, physical-device smoothness proof boundaries, and `--shipguard-eval` product-QA runs.
- Added `shipguard ios design` for genre-aware UI/UX coherence, motion, haptics, preview routing, and ChatGPT ImageGen app-icon handoff reports.
- Added `shipguard ios report-quality` to score read-only ShipGuard product-QA reports for eval boundaries, scan scope, proof guidance, Markdown companions, and shareability without grading the target app.
- Added a public report-quality token-shareability fixture and redaction-plan output so Devspace-style connector URLs are blocked from sharing without echoing token values.
- Added `shipguard ios devspace-check` to statically grade Devspace connector readiness, public URL safety, preview evidence, MCP widget metadata, handoff boundaries, and ChatGPT model-choice honesty without grading target apps.
- Added a public Devspace complete-preview fixture and handoff-quality checks for target-resolution, event receipts, raw-coordinate safety, and paste-safe handoff Markdown.
- Added `ios devspace-check --shareable` so connector-readiness reports can omit local absolute paths before report-quality scoring or external sharing.
- Added `ios design --shareable` so design QA reports can omit local absolute app and preview paths before report-quality scoring or external planning.
- Added `ios report-quality --shareable` so the report-quality artifact itself can omit local input/report paths before external sharing.
- Added `ios performance --shareable` so performance/source-hotspot reports can omit local absolute project paths before report-quality scoring or external sharing.
- Added `ios modernize --shareable`, `ios app-intelligence --shareable`, and `ios ai-readiness --shareable` so modernization and system-exposure reports carry an explicit shareability contract before scoring or external sharing.
- Added declared-shareability report-quality findings so shareable scoring flags source reports that are missing shareability metadata or still declare local-mode output.
- Added report-quality actionability aggregation so input `reportQualityQuestions` become a public, shareable checklist for the next ShipGuard rule, fixture, report section, or docs improvement.
- Added `shipguard ios spec-workflow` to turn report-quality actionability questions into ShipGuard-owned constitution, feature spec, implementation plan, tasks, analysis gates, slash plan/goal, and Devspace guardrails inspired by Spec Kit and CodexPro without vendoring external code.
- Added spec-workflow adoption quality findings so report-quality flags shareable spec workflows that were generated without `--from-report` evidence or actionability questions.
- Added spec-workflow artifact completeness findings so report-quality flags declared spec bundles whose generated files are missing, empty, or unsafe.
- Added spec-workflow artifact content findings so report-quality flags placeholder-only or structurally weak generated spec files.
- Added spec-workflow question coverage findings so report-quality flags spec bundles that drop report-quality actionability questions from JSON or Markdown clarifying sections.
- Added spec-workflow task coverage findings so report-quality flags spec bundles whose task plan does not answer the source actionability questions.
- Added spec-workflow acceptance-criteria coverage so Spec Kit-style specs answer report-quality actionability questions in acceptance criteria, not only in clarifying questions or tasks.
- Added spec-workflow validation-command coverage so implementation plans must preserve exact proof commands in JSON and Markdown before adoption passes.
- Added spec-workflow analysis-gate coverage so implementation plans must preserve pre-implementation analysis checks before adoption passes.
- Extended `--shipguard-eval` product-QA boundaries to `ios modernize`, `ios app-intelligence`, and `ios ai-readiness`, with summarized/capped Markdown output where real-app read-only checks showed noisy reports.
- Refined iOS read-only scanners to skip generated/proof/cache directories, disclose scan-scope exclusions in reports, and weight design app-type inference toward app/project source instead of repeated instruction-document tokens.

## v3.38.0 - Docs Link Audit

- Added `shipguard docs-check` for dependency-free local Markdown link audits.
- Added JSON and Markdown docs-check reports plus broken-link failure behavior.
- Extended CI, self-audit, next-goal, source validation, package proof, README, and CLI docs for docs-heavy release guardrails.

## v3.37.0 - Arena Signer Metadata

- Added optional `--signer` and `--signer-url` metadata to `shipguard arena sign` manifests.
- Added `identity_digest` verification so Arena manifests fail when signer metadata is tampered or unsafe.
- Extended Arena signing docs, source tests, package proof, and release docs for signer metadata without claiming private-key identity signing.

## v3.36.0 - Transcript Corpus Demo Proof

- Added a `release-evidence-consumption` redacted transcript fixture with a checked redaction report.
- Extended demo report generation to publish transcript corpus JSON, Markdown, badge, and per-case verification outputs.
- Updated corpus, package, source validation, self-audit, docs, and action tests for the four-case public transcript fixture pack.

## v3.35.0 - Docs Release Proof Arena Fixture

- Added a `docs-release-proof-drift` Maintainer Arena case for stale release proof documentation and workflow references.
- Updated the public Arena and leaderboard baselines to ten cases with explicit docs drift coverage.
- Extended source validation, package proof, docs, demo reports, and benchmark tests for the expanded fixture pack.

## v3.34.0 - Transcript Corpus GitHub Action

- Added `actions/transcript-corpus` to run `shipguard transcript corpus` in GitHub Actions and upload corpus artifacts.
- Added a copyable transcript corpus workflow plus action docs for warn/fail publication checks.
- Extended CI, source validation, self-audit, next-goal, package proof, and docs coverage for transcript corpus action output.

## v3.33.0 - Transcript Corpus Verification

- Added `shipguard transcript corpus` to verify and index public-safe redacted transcript fixtures.
- Added three checked transcript fixtures with redaction reports plus corpus JSON, Markdown, badge, and per-case verification outputs.
- Extended CI, source validation, self-audit, next-goal, docs, and extracted-package proof coverage for corpus publication checks.

## v3.32.0 - Transcript Verification GitHub Action

- Added `actions/transcript-verify` to run `shipguard transcript verify` in GitHub Actions and upload verification artifacts.
- Added a copyable transcript verification workflow plus action docs for warn/fail publication checks.
- Extended CI, self-audit, next-goal, source validation, and extracted-package proof coverage for the new action.

## v3.31.0 - Transcript Verification

- Added `shipguard transcript verify` for checking redacted transcript Markdown and optional redaction reports before public sharing.
- Added verification JSON, Markdown, and badge outputs with blocking behavior for remaining emails, token-like values, secret assignments, local paths, and long hex strings.
- Extended CI, self-audit, next-goal, source validation, and extracted-package proof coverage for transcript verification.

## v3.30.0 - Maintainer Transcript Redaction

- Added `shipguard transcript redact` for redacting maintainer transcripts into public-safe Markdown plus JSON leak-audit reports.
- Added transcript redaction docs, a synthetic redacted transcript example, and focused test coverage for emails, token-like values, secret assignments, local paths, long hex strings, bearer tokens, and custom private terms.
- Extended CI, self-audit, next-goal, source validation, and extracted-package proof coverage for the new transcript command.

## v3.29.0 - Arena Compare GitHub Action

- Added `actions/arena-compare` to run `shipguard arena compare` in GitHub Actions and upload comparison artifacts.
- Added a copyable Arena compare workflow plus action docs for warn/fail benchmark regression checks.
- Extended CI, self-audit, next-goal, source validation, and package proof coverage for the new action.

## v3.28.0 - Arena Regression Compare

- Added `shipguard arena compare` for JSON and Markdown diffs between Arena `results.json` files.
- Added regression classification for average-score, high-risk-finding, case-count, added-case, removed-case, and per-case changes.
- Extended CLI, self-audit, next-goal, CI, package, and docs coverage for benchmark comparison proof.

## v3.27.0 - Frontend Async State Arena Fixture

- Added a frontend async-state regression case to the public Maintainer Arena fixture pack.
- Updated Arena, leaderboard, package, and validation checks for the nine-case benchmark baseline.
- Refreshed public docs and demo expectations with the new aggregate benchmark metrics.

## v3.26.0 - Release Evidence Negative Fixture HTML Report

- Added a browsable `index.html` report to `shipguard release-evidence negative-index` outputs.
- Exposed `index-html` from `actions/release-evidence-negative-index` so CI artifacts can link directly to the visual report.
- Extended CLI, action, docs, and package proof coverage for the HTML output.

## v3.25.0 - Release Evidence Negative Index Action

- Added `actions/release-evidence-negative-index` to run the bundled negative evidence fixture manifest in GitHub Actions and upload the guardrail index artifact.
- Added a copyable workflow example plus action docs for publishing `negative-fixture-index.json`, Markdown, badge, and per-case verifier outputs from CI.
- Extended CI, next-goal generation, source validation, self-audit, and package proof coverage for the new action.

## v3.24.0 - Release Evidence Negative Fixture Index

- Added `shipguard release-evidence negative-index` to run the checked-in negative fixture manifest and publish JSON, Markdown, badge, and per-case verifier outputs.
- Added `fixtures/release-evidence/negative/cases.tsv` so expected blocked checks are data-driven instead of only hardcoded in tests.
- Extended source validation, self-audit, docs, and package proof coverage for the negative fixture index path.

## v3.23.0 - Release Evidence Verification Negative Fixtures

- Added checked-in negative fixtures for `release-evidence verify`, covering missing source reports, consumer/evidence release mismatches, digest summary mismatches, and missing bundle outputs.
- Extended verifier tests so each negative fixture must exit nonzero while still writing `evidence-verify.json`, `evidence-verify.md`, and `badge.json`.
- Added source validation, self-audit, docs, and package proof coverage for the negative fixture pack.

## v3.22.0 - Release Evidence Verify Action Download Mode

- Added optional artifact download mode to `actions/release-evidence-verify` with `download-artifact` and `source-artifact-name` inputs.
- Updated the release evidence consume workflow so downstream evidence verification can download and verify the producer artifact in one action step.
- Updated docs and package checks for the one-step evidence artifact verification path.

## v3.21.0 - Release Evidence Action Consumption Proof

- Added `shipguard release-evidence verify` to consume downloaded release evidence artifacts and verify their static evidence, copied source reports, optional index, and optional bundle metadata.
- Added `actions/release-evidence-verify` plus a two-job workflow example that builds a release evidence artifact, downloads it, and verifies it as a downstream consumer.
- Added package, self-audit, docs, and CI coverage for release evidence artifact verification.

## v3.20.0 - Release Evidence Bundle CI Action Mode

- Added bundle mode to `actions/release-evidence` so CI can download release assets and run the one-command evidence bundle path.
- Added bundle-mode inputs, `bundle.json` output exposure, and a copyable `release-evidence-bundle.yml` workflow example.
- Added docs, action tests, package verification, self-audit coverage, and release-train metadata.

## v3.19.0 - One-Command Release Evidence Bundle

- Added `shipguard release-evidence bundle` to run release consumption, optional release diff, evidence site export, and evidence index generation in one local command.
- Added `bundle.json` and bundle README output for reviewing the full local evidence export.
- Added docs, tests, package verification, self-audit coverage, and release-train metadata.

## v3.18.0 - Release Evidence GitHub Action

- Added `actions/release-evidence` for exporting release evidence sites and optional indexes in GitHub Actions.
- Added a copyable release-evidence workflow, docs, CI coverage, package verification, self-audit coverage, and next-goal proof.
- The action uploads a static evidence artifact derived from release-consume and optional release-diff reports.

## v3.17.0 - Release Evidence Index

- Added `shipguard release-evidence index` for collecting multiple evidence site exports into one static release history.
- The index writes `index.html`, `evidence-index.json`, `README.md`, and copied evidence sites under `sites/<release>/`.
- Added docs, tests, package verification, self-audit coverage, and release-train metadata.

## v3.16.0 - Release Evidence Site Export

- Added `shipguard release-evidence site` for exporting release-consume and release-diff reports as a static evidence page.
- The export writes `index.html`, `evidence.json`, `README.md`, and copied source JSON under `sources/`.
- Added docs, tests, CI coverage, package verification, self-audit coverage, and next-goal proof.

## v3.15.0 - Release Diff CI Action

- Added `actions/release-diff` for comparing two published release proof asset sets in GitHub Actions.
- Added a copyable release-diff workflow, docs, CI coverage, package verification, self-audit coverage, and next-goal proof.
- The action uploads `release-diff.json` and `release-diff.md` as CI artifacts and supports fail/warn modes.

## v3.14.0 - Release Diff Audit

- Added `shipguard release-diff compare` for comparing two release proof asset directories.
- The diff audit writes JSON and Markdown reports for tarball, manifest, index, ledger, replay, attestation, and badge changes.
- Added docs, tests, CI coverage, self-audit coverage, next-goal proof, and package verification.

## v3.13.0 - Release Consumption CI Action

- Added `actions/release-consume` for downloading and verifying published release proof assets in GitHub Actions.
- Added a copyable release-consume workflow, docs, CI coverage, package verification, and self-audit coverage.
- The action uploads consumer reports, SHA-256 output, asset digest matrices, replay proof, and regenerated attestation proof.

## v3.12.0 - Release Asset Digest Matrix

- Added `asset-digests.json` and `asset-digests.md` outputs to `shipguard release-consume verify`.
- The digest matrix records present or missing release assets, roles, required flags, byte counts, and SHA-256 values.
- Updated release-consume docs, tests, package verification, demo reports, and release-train metadata.

## v3.11.0 - Published Proof Crosscheck

- Extended `shipguard release-consume verify` to cross-check downloaded replay, attestation, and badge assets against locally regenerated proof.
- Added blocking behavior for mismatched published proof assets, including tampered attestation badges.
- Updated release-consume docs, tests, package verification, demo reports, and release-train metadata.

## v3.10.0 - Release Proof Consumer CLI

- Added `shipguard release-consume verify` for one-command verification of downloaded release proof assets.
- Added consumer reports, SHA-256 output, replay output, attestation output, CLI docs, and package verification.
- Added release-consume tests, CI coverage, self-audit coverage, and next-goal proof.

## v3.9.0 - Release Proof Consumption Guide

- Added `docs/release-proof-consumption.md` for downstream release reviewers who want to verify downloaded proof assets.
- Added a copyable release proof consumption checklist for tarball digest, replay, attestation, badge, and blocked-check review.
- Added executable consumption tests, CI coverage, self-audit coverage, next-goal proof, and package verification.

## v3.8.0 - Release Proof Bundle CLI

- Added `shipguard release-proof build` for generating the full release proof bundle in one command.
- Added bundle output for the release tarball, manifest, proof ledger, release index, replay report, attestation, and attestation badge.
- Added release-proof CLI docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.7.0 - Release Proof Workflow Example Pack

- Added tag-triggered and manual-dispatch GitHub Actions workflow examples for `actions/release-proof`.
- Added `docs/release-proof-workflows.md` to explain when to use each workflow and what proof artifacts they produce.
- Added workflow example tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.6.0 - Release Proof Composite Action

- Added `actions/release-proof` for generating release tarball, manifest, index, replay, and attestation proof in GitHub Actions.
- Added composite action outputs for tarball, manifest, replay report, attestation, and attestation badge paths.
- Added release-proof action docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.5.0 - Release Attestation Bundle

- Added `shipguard release-attest build` for generating release attestation bundles from manifest and replay proof.
- Added `attestation.json`, `attestation.md`, and Shields-compatible `attestation-badge.json` outputs.
- Added validation that manifest and replay proof agree on version, tag, commit, artifact bytes, and artifact SHA-256.
- Added release-attest docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.4.0 - Release Forensics And Asset Replay

- Added `shipguard release-replay verify` for replay-verifying downloaded release assets.
- Added `replay-report.json` and `replay-report.md` outputs with manifest, tarball, release-index, and proof-ledger checks.
- Added tarball runtime-file checks, forbidden-entry checks, and private-path or secret-looking token scans.
- Added release-replay docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.3.0 - Release Index And Proof Catalog

- Added `shipguard release-index build` for cataloging release manifest files.
- Added `release-index.json` and `release-index.md` outputs with sorted release proof history.
- Added duplicate-version detection for manifest catalogs.
- Added release-index docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.2.0 - Release Manifest Verification

- Added `shipguard release-manifest verify`.
- Added verification for manifest schema, version, tag, commit presence, artifact name, byte count, SHA-256, and portable artifact path.
- Added tamper-detection tests for changed digests and local machine paths.
- Updated release-manifest docs, self-audit coverage, package verification, CI coverage, and release proof.

## v3.1.0 - Release Manifest And Proof Ledger

- Added `shipguard release-manifest` for release tarball proof files.
- Added `release-manifest.json` with version, tag, commit, artifact bytes, SHA-256, and proof URLs.
- Added `proof-ledger.md` for human release audits.
- Added release-manifest docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.0.0 - Expanded Backend And CLI Arena Pack

- Added backend webhook idempotency and dangerous CLI cleanup arena cases.
- Expanded the public fixture pack from six to eight maintainer tasks.
- Regenerated demo arena reports and leaderboard output for the expanded pack.
- Updated benchmark docs, tests, package verification, CI coverage, and release proof.

## v2.9.0 - Backend And CLI Template Profiles

- Added `shipguard init backend` and `shipguard doctor backend`.
- Added `shipguard init cli` and `shipguard doctor cli`.
- Added backend-service and CLI-tool maintainer instruction templates.
- Added profile docs, adoption docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.8.0 - Optional Check Run Posting

- Added `shipguard check-run post` for opt-in GitHub Checks API posting from generated payloads.
- Added dry-run request proof with token redaction and payload SHA-256 metadata.
- Updated the reusable CI gate action with optional `post-check-run` support and `checks: write` guidance.
- Added check-run post docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.7.0 - Signed Fixture Pack Metadata

- Added `shipguard arena sign` and `shipguard arena verify`.
- Added deterministic `PACK.json` metadata with file SHA-256 values, byte counts, and pack digest.
- Added tamper-detection tests, docs, self-audit coverage, CI coverage, and package verification.

## v2.6.0 - External Fixture Pack Import

- Added `shipguard arena import` for validating and copying external Maintainer Arena fixture packs.
- Added sample external arena fixtures and import metadata output.
- Added import safety checks for supported files, overwrite behavior, local paths, and secret-looking values.
- Added arena import docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.5.0 - Template Profile Expansion

- Added `shipguard init web` and `shipguard doctor web`.
- Added a framework-neutral web app workflow starter under `templates/web/`.
- Added template profile docs, adoption docs, demo walkthrough updates, tests, self-audit coverage, CI coverage, and package verification.

## v2.4.1 - Next Goal Proof List Patch

- Updated `shipguard next-goal` so generated release plans include check-run, CI summary, and SARIF tests.
- Strengthened next-goal and package tests to catch stale proof-command lists.

## v2.4.0 - Check Run Payload Export

- Added `shipguard check-run` for GitHub Checks API payload JSON from `gate.json`.
- Updated `actions/ci-gate` to generate `check-run/payload.json` in the artifact bundle.
- Added check-run docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.3.0 - CI Step Summary Output

- Added `shipguard ci-summary` for GitHub Actions step-summary Markdown from `gate.json`.
- Added automatic `summary.md` output to `shipguard ci-gate`.
- Updated `actions/ci-gate` to append the summary to `$GITHUB_STEP_SUMMARY`.
- Added CI summary docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.2.0 - SARIF Evidence Export

- Added `shipguard sarif` for converting Autopsy report JSON into SARIF 2.1.0.
- Added SARIF output to `shipguard ci-gate` artifact bundles and `gate.json`.
- Added SARIF docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.1.0 - Next Goal Generator

- Added `shipguard next-goal` for deterministic slash-goal release planning.
- Added next-goal docs, command matrix coverage, and Maintainer Reliability OS loop updates.
- Added next-goal tests, CI coverage, self-audit coverage, and package verification.

## v2.0.0 - Maintainer Reliability OS

- Added `shipguard self-audit` for toolkit readiness proof.
- Added command matrix, release checklist, and Maintainer Reliability OS docs.
- Added self-audit tests and package verification.

## v1.3.0 - Expanded reliability benchmark pack

- Added failing-validation, no-diff implementation, and review-only arena fixtures.
- Expanded generated demo reports and leaderboard output.
- Updated arena, benchmark, package, and leaderboard tests for the larger fixture pack.

## v1.2.0 - CI gate mode

- Added `shipguard ci-gate` for Autopsy, review comments, badges, and gate JSON in one command.
- Added fail/warn CI behavior with policy threshold support.
- Added `actions/ci-gate` with artifact upload.
- Added CI gate docs, examples, tests, and package verification.

## v1.1.0 - Policy configuration

- Added plain `key=value` policy files for protected patterns, risky claims, validation claims, scope limits, and thresholds.
- Added `shipguard policy init` and `shipguard policy show`.
- Added `shipguard autopsy --policy`.
- Added policy docs, fixtures, tests, and package verification.

## v1.0.0 - Public AI Maintainer Reliability Benchmark

- Stabilized CLI docs for `autopsy`, `arena`, `review-comment`, and `leaderboard`.
- Added stable `leaderboard.json` schema version `1.0`.
- Added demo reports generated from public fixtures.
- Added benchmark and demo-report docs.
- Added leaderboard tests and package verification.

## v0.8.0 - PR Review Bot Mode

- Added `shipguard review-comment` for PR-ready Markdown comments and Shields-compatible badge JSON.
- Added warn/fail thresholds with safe default `mode=warn`.
- Added an artifact bundle containing report JSON, report Markdown, comment Markdown, and badge JSON.
- Added a reusable `actions/review-comment` composite action.
- Added PR review bot docs, examples, CI tests, and package verification.

## v0.7.0 - Maintainer Arena

- Added `shipguard arena run` for fixture-pack benchmark execution.
- Added public good, weak, and dangerous Maintainer Arena fixtures.
- Added aggregate `results.json` and `index.md` output.
- Added arena docs, example output, CI tests, and package verification.

## v0.6.1 - Autopsy artifact bridge

- Added a manual GitHub Actions workflow that generates autopsy reports and uploads them as artifacts.
- Added documentation for using autopsy in GitHub Actions.
- Added artifact workflow tests and package verification.

## v0.6.0 - Agent Autopsy Foundation

- Added `shipguard autopsy` for Markdown and JSON evidence reports.
- Added claim-risk detection for validation claims without tests, high-assurance claims, protected-area touches, diff scope creep, and missing evidence.
- Added good, weak, and dangerous public autopsy fixtures.
- Added autopsy tests and package-level release verification.
- Added Agent Autopsy docs and examples.

## v0.5.0 - Release-installable toolkit and demo fixture

- Added `VERSION` and `shipguard version`.
- Added release tarball packaging with `scripts/package_release.sh`.
- Added `scripts/install.sh` for prefix-based CLI installation from an unpacked release.
- Added a public demo iOS-style fixture and walkthrough.
- Added package release tests and CI coverage.

## v0.4.0 - Adoption docs and Pages shell

- Added maintainer adoption guide.
- Added copy/paste setup instructions for using the kit in another repo.
- Added a Mermaid workflow diagram with a plain-text fallback.
- Added GitHub Pages-ready docs landing page and `_config.yml`.
- Added an adoption checklist example.
- Added a sanitized Codex task template and expanded subagent coordination guidance.

## v0.3.0 - Maintainer CLI and validation action

- Added `bin/shipguard` with `init`, `validate`, `doctor`, and `score`.
- Added reusable composite action at `actions/validate`.
- Added CLI and GitHub Action docs.
- Added scored-run example and CLI smoke tests.
- Updated CI to validate through the CLI and reusable action.

## v0.2.0 - Examples and scorecard

- Added a worked issue-to-plan-to-validation example.
- Added a prompt pack for common maintainer tasks.
- Added `SCORECARD.md`.
- Added iOS starter template files.
- Strengthened validator coverage.

## v0.1.0 - Public workflow kit

- Published the initial public workflow kit.
- Added MIT license, contribution guide, security policy, roadmap, issue template, CI, and release metadata.
