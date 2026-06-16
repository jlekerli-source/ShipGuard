# Changelog

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
