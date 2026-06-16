# Changelog

## v3.31.0 - Transcript Verification

- Added `codex-maintainer transcript verify` for checking redacted transcript Markdown and optional redaction reports before public sharing.
- Added verification JSON, Markdown, and badge outputs with blocking behavior for remaining emails, token-like values, secret assignments, local paths, and long hex strings.
- Extended CI, self-audit, next-goal, source validation, and extracted-package proof coverage for transcript verification.

## v3.30.0 - Maintainer Transcript Redaction

- Added `codex-maintainer transcript redact` for redacting maintainer transcripts into public-safe Markdown plus JSON leak-audit reports.
- Added transcript redaction docs, a synthetic redacted transcript example, and focused test coverage for emails, token-like values, secret assignments, local paths, long hex strings, bearer tokens, and custom private terms.
- Extended CI, self-audit, next-goal, source validation, and extracted-package proof coverage for the new transcript command.

## v3.29.0 - Arena Compare GitHub Action

- Added `actions/arena-compare` to run `codex-maintainer arena compare` in GitHub Actions and upload comparison artifacts.
- Added a copyable Arena compare workflow plus action docs for warn/fail benchmark regression checks.
- Extended CI, self-audit, next-goal, source validation, and package proof coverage for the new action.

## v3.28.0 - Arena Regression Compare

- Added `codex-maintainer arena compare` for JSON and Markdown diffs between Arena `results.json` files.
- Added regression classification for average-score, high-risk-finding, case-count, added-case, removed-case, and per-case changes.
- Extended CLI, self-audit, next-goal, CI, package, and docs coverage for benchmark comparison proof.

## v3.27.0 - Frontend Async State Arena Fixture

- Added a frontend async-state regression case to the public Maintainer Arena fixture pack.
- Updated Arena, leaderboard, package, and validation checks for the nine-case benchmark baseline.
- Refreshed public docs and demo expectations with the new aggregate benchmark metrics.

## v3.26.0 - Release Evidence Negative Fixture HTML Report

- Added a browsable `index.html` report to `codex-maintainer release-evidence negative-index` outputs.
- Exposed `index-html` from `actions/release-evidence-negative-index` so CI artifacts can link directly to the visual report.
- Extended CLI, action, docs, and package proof coverage for the HTML output.

## v3.25.0 - Release Evidence Negative Index Action

- Added `actions/release-evidence-negative-index` to run the bundled negative evidence fixture manifest in GitHub Actions and upload the guardrail index artifact.
- Added a copyable workflow example plus action docs for publishing `negative-fixture-index.json`, Markdown, badge, and per-case verifier outputs from CI.
- Extended CI, next-goal generation, source validation, self-audit, and package proof coverage for the new action.

## v3.24.0 - Release Evidence Negative Fixture Index

- Added `codex-maintainer release-evidence negative-index` to run the checked-in negative fixture manifest and publish JSON, Markdown, badge, and per-case verifier outputs.
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

- Added `codex-maintainer release-evidence verify` to consume downloaded release evidence artifacts and verify their static evidence, copied source reports, optional index, and optional bundle metadata.
- Added `actions/release-evidence-verify` plus a two-job workflow example that builds a release evidence artifact, downloads it, and verifies it as a downstream consumer.
- Added package, self-audit, docs, and CI coverage for release evidence artifact verification.

## v3.20.0 - Release Evidence Bundle CI Action Mode

- Added bundle mode to `actions/release-evidence` so CI can download release assets and run the one-command evidence bundle path.
- Added bundle-mode inputs, `bundle.json` output exposure, and a copyable `release-evidence-bundle.yml` workflow example.
- Added docs, action tests, package verification, self-audit coverage, and release-train metadata.

## v3.19.0 - One-Command Release Evidence Bundle

- Added `codex-maintainer release-evidence bundle` to run release consumption, optional release diff, evidence site export, and evidence index generation in one local command.
- Added `bundle.json` and bundle README output for reviewing the full local evidence export.
- Added docs, tests, package verification, self-audit coverage, and release-train metadata.

## v3.18.0 - Release Evidence GitHub Action

- Added `actions/release-evidence` for exporting release evidence sites and optional indexes in GitHub Actions.
- Added a copyable release-evidence workflow, docs, CI coverage, package verification, self-audit coverage, and next-goal proof.
- The action uploads a static evidence artifact derived from release-consume and optional release-diff reports.

## v3.17.0 - Release Evidence Index

- Added `codex-maintainer release-evidence index` for collecting multiple evidence site exports into one static release history.
- The index writes `index.html`, `evidence-index.json`, `README.md`, and copied evidence sites under `sites/<release>/`.
- Added docs, tests, package verification, self-audit coverage, and release-train metadata.

## v3.16.0 - Release Evidence Site Export

- Added `codex-maintainer release-evidence site` for exporting release-consume and release-diff reports as a static evidence page.
- The export writes `index.html`, `evidence.json`, `README.md`, and copied source JSON under `sources/`.
- Added docs, tests, CI coverage, package verification, self-audit coverage, and next-goal proof.

## v3.15.0 - Release Diff CI Action

- Added `actions/release-diff` for comparing two published release proof asset sets in GitHub Actions.
- Added a copyable release-diff workflow, docs, CI coverage, package verification, self-audit coverage, and next-goal proof.
- The action uploads `release-diff.json` and `release-diff.md` as CI artifacts and supports fail/warn modes.

## v3.14.0 - Release Diff Audit

- Added `codex-maintainer release-diff compare` for comparing two release proof asset directories.
- The diff audit writes JSON and Markdown reports for tarball, manifest, index, ledger, replay, attestation, and badge changes.
- Added docs, tests, CI coverage, self-audit coverage, next-goal proof, and package verification.

## v3.13.0 - Release Consumption CI Action

- Added `actions/release-consume` for downloading and verifying published release proof assets in GitHub Actions.
- Added a copyable release-consume workflow, docs, CI coverage, package verification, and self-audit coverage.
- The action uploads consumer reports, SHA-256 output, asset digest matrices, replay proof, and regenerated attestation proof.

## v3.12.0 - Release Asset Digest Matrix

- Added `asset-digests.json` and `asset-digests.md` outputs to `codex-maintainer release-consume verify`.
- The digest matrix records present or missing release assets, roles, required flags, byte counts, and SHA-256 values.
- Updated release-consume docs, tests, package verification, demo reports, and release-train metadata.

## v3.11.0 - Published Proof Crosscheck

- Extended `codex-maintainer release-consume verify` to cross-check downloaded replay, attestation, and badge assets against locally regenerated proof.
- Added blocking behavior for mismatched published proof assets, including tampered attestation badges.
- Updated release-consume docs, tests, package verification, demo reports, and release-train metadata.

## v3.10.0 - Release Proof Consumer CLI

- Added `codex-maintainer release-consume verify` for one-command verification of downloaded release proof assets.
- Added consumer reports, SHA-256 output, replay output, attestation output, CLI docs, and package verification.
- Added release-consume tests, CI coverage, self-audit coverage, and next-goal proof.

## v3.9.0 - Release Proof Consumption Guide

- Added `docs/release-proof-consumption.md` for downstream release reviewers who want to verify downloaded proof assets.
- Added a copyable release proof consumption checklist for tarball digest, replay, attestation, badge, and blocked-check review.
- Added executable consumption tests, CI coverage, self-audit coverage, next-goal proof, and package verification.

## v3.8.0 - Release Proof Bundle CLI

- Added `codex-maintainer release-proof build` for generating the full release proof bundle in one command.
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

- Added `codex-maintainer release-attest build` for generating release attestation bundles from manifest and replay proof.
- Added `attestation.json`, `attestation.md`, and Shields-compatible `attestation-badge.json` outputs.
- Added validation that manifest and replay proof agree on version, tag, commit, artifact bytes, and artifact SHA-256.
- Added release-attest docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.4.0 - Release Forensics And Asset Replay

- Added `codex-maintainer release-replay verify` for replay-verifying downloaded release assets.
- Added `replay-report.json` and `replay-report.md` outputs with manifest, tarball, release-index, and proof-ledger checks.
- Added tarball runtime-file checks, forbidden-entry checks, and private-path or secret-looking token scans.
- Added release-replay docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.3.0 - Release Index And Proof Catalog

- Added `codex-maintainer release-index build` for cataloging release manifest files.
- Added `release-index.json` and `release-index.md` outputs with sorted release proof history.
- Added duplicate-version detection for manifest catalogs.
- Added release-index docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.2.0 - Release Manifest Verification

- Added `codex-maintainer release-manifest verify`.
- Added verification for manifest schema, version, tag, commit presence, artifact name, byte count, SHA-256, and portable artifact path.
- Added tamper-detection tests for changed digests and local machine paths.
- Updated release-manifest docs, self-audit coverage, package verification, CI coverage, and release proof.

## v3.1.0 - Release Manifest And Proof Ledger

- Added `codex-maintainer release-manifest` for release tarball proof files.
- Added `release-manifest.json` with version, tag, commit, artifact bytes, SHA-256, and proof URLs.
- Added `proof-ledger.md` for human release audits.
- Added release-manifest docs, tests, self-audit coverage, CI coverage, next-goal proof, and package verification.

## v3.0.0 - Expanded Backend And CLI Arena Pack

- Added backend webhook idempotency and dangerous CLI cleanup arena cases.
- Expanded the public fixture pack from six to eight maintainer tasks.
- Regenerated demo arena reports and leaderboard output for the expanded pack.
- Updated benchmark docs, tests, package verification, CI coverage, and release proof.

## v2.9.0 - Backend And CLI Template Profiles

- Added `codex-maintainer init backend` and `codex-maintainer doctor backend`.
- Added `codex-maintainer init cli` and `codex-maintainer doctor cli`.
- Added backend-service and CLI-tool maintainer instruction templates.
- Added profile docs, adoption docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.8.0 - Optional Check Run Posting

- Added `codex-maintainer check-run post` for opt-in GitHub Checks API posting from generated payloads.
- Added dry-run request proof with token redaction and payload SHA-256 metadata.
- Updated the reusable CI gate action with optional `post-check-run` support and `checks: write` guidance.
- Added check-run post docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.7.0 - Signed Fixture Pack Metadata

- Added `codex-maintainer arena sign` and `codex-maintainer arena verify`.
- Added deterministic `PACK.json` metadata with file SHA-256 values, byte counts, and pack digest.
- Added tamper-detection tests, docs, self-audit coverage, CI coverage, and package verification.

## v2.6.0 - External Fixture Pack Import

- Added `codex-maintainer arena import` for validating and copying external Maintainer Arena fixture packs.
- Added sample external arena fixtures and import metadata output.
- Added import safety checks for supported files, overwrite behavior, local paths, and secret-looking values.
- Added arena import docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.5.0 - Template Profile Expansion

- Added `codex-maintainer init web` and `codex-maintainer doctor web`.
- Added a framework-neutral web app workflow starter under `templates/web/`.
- Added template profile docs, adoption docs, demo walkthrough updates, tests, self-audit coverage, CI coverage, and package verification.

## v2.4.1 - Next Goal Proof List Patch

- Updated `codex-maintainer next-goal` so generated release plans include check-run, CI summary, and SARIF tests.
- Strengthened next-goal and package tests to catch stale proof-command lists.

## v2.4.0 - Check Run Payload Export

- Added `codex-maintainer check-run` for GitHub Checks API payload JSON from `gate.json`.
- Updated `actions/ci-gate` to generate `check-run/payload.json` in the artifact bundle.
- Added check-run docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.3.0 - CI Step Summary Output

- Added `codex-maintainer ci-summary` for GitHub Actions step-summary Markdown from `gate.json`.
- Added automatic `summary.md` output to `codex-maintainer ci-gate`.
- Updated `actions/ci-gate` to append the summary to `$GITHUB_STEP_SUMMARY`.
- Added CI summary docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.2.0 - SARIF Evidence Export

- Added `codex-maintainer sarif` for converting Autopsy report JSON into SARIF 2.1.0.
- Added SARIF output to `codex-maintainer ci-gate` artifact bundles and `gate.json`.
- Added SARIF docs, tests, self-audit coverage, CI coverage, and package verification.

## v2.1.0 - Next Goal Generator

- Added `codex-maintainer next-goal` for deterministic slash-goal release planning.
- Added next-goal docs, command matrix coverage, and Maintainer Reliability OS loop updates.
- Added next-goal tests, CI coverage, self-audit coverage, and package verification.

## v2.0.0 - Maintainer Reliability OS

- Added `codex-maintainer self-audit` for toolkit readiness proof.
- Added command matrix, release checklist, and Maintainer Reliability OS docs.
- Added self-audit tests and package verification.

## v1.3.0 - Expanded reliability benchmark pack

- Added failing-validation, no-diff implementation, and review-only arena fixtures.
- Expanded generated demo reports and leaderboard output.
- Updated arena, benchmark, package, and leaderboard tests for the larger fixture pack.

## v1.2.0 - CI gate mode

- Added `codex-maintainer ci-gate` for Autopsy, review comments, badges, and gate JSON in one command.
- Added fail/warn CI behavior with policy threshold support.
- Added `actions/ci-gate` with artifact upload.
- Added CI gate docs, examples, tests, and package verification.

## v1.1.0 - Policy configuration

- Added plain `key=value` policy files for protected patterns, risky claims, validation claims, scope limits, and thresholds.
- Added `codex-maintainer policy init` and `codex-maintainer policy show`.
- Added `codex-maintainer autopsy --policy`.
- Added policy docs, fixtures, tests, and package verification.

## v1.0.0 - Public AI Maintainer Reliability Benchmark

- Stabilized CLI docs for `autopsy`, `arena`, `review-comment`, and `leaderboard`.
- Added stable `leaderboard.json` schema version `1.0`.
- Added demo reports generated from public fixtures.
- Added benchmark and demo-report docs.
- Added leaderboard tests and package verification.

## v0.8.0 - PR Review Bot Mode

- Added `codex-maintainer review-comment` for PR-ready Markdown comments and Shields-compatible badge JSON.
- Added warn/fail thresholds with safe default `mode=warn`.
- Added an artifact bundle containing report JSON, report Markdown, comment Markdown, and badge JSON.
- Added a reusable `actions/review-comment` composite action.
- Added PR review bot docs, examples, CI tests, and package verification.

## v0.7.0 - Maintainer Arena

- Added `codex-maintainer arena run` for fixture-pack benchmark execution.
- Added public good, weak, and dangerous Maintainer Arena fixtures.
- Added aggregate `results.json` and `index.md` output.
- Added arena docs, example output, CI tests, and package verification.

## v0.6.1 - Autopsy artifact bridge

- Added a manual GitHub Actions workflow that generates autopsy reports and uploads them as artifacts.
- Added documentation for using autopsy in GitHub Actions.
- Added artifact workflow tests and package verification.

## v0.6.0 - Agent Autopsy Foundation

- Added `codex-maintainer autopsy` for Markdown and JSON evidence reports.
- Added claim-risk detection for validation claims without tests, high-assurance claims, protected-area touches, diff scope creep, and missing evidence.
- Added good, weak, and dangerous public autopsy fixtures.
- Added autopsy tests and package-level release verification.
- Added Agent Autopsy docs and examples.

## v0.5.0 - Release-installable toolkit and demo fixture

- Added `VERSION` and `codex-maintainer version`.
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

- Added `bin/codex-maintainer` with `init`, `validate`, `doctor`, and `score`.
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
