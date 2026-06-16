# Changelog

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
