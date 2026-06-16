# Ringly Codex Workflows

This is the documentation landing page for the workflow kit.

Start here:

- [Adoption guide](adoption-guide.md)
- [Use in your repo](use-in-your-repo.md)
- [Workflow diagram](workflow-diagram.md)
- [Maintainer Arena](arena.md)
- [CLI reference](cli.md)
- [Agent Autopsy](autopsy.md)
- [Autopsy in GitHub Actions](autopsy-github-actions.md)
- [Benchmark Format](benchmark.md)
- [Check Run Payload](check-run.md)
- [CI Gate Mode](ci-gate.md)
- [CI Step Summary](ci-summary.md)
- [Command Matrix](command-matrix.md)
- [Demo Reports](demo-reports.md)
- [Maintainer Reliability OS](maintainer-reliability-os.md)
- [Next Goal Generator](next-goal.md)
- [Policy Configuration](policy.md)
- [PR Review Bot Mode](pr-review-bot.md)
- [Release Checklist](release-checklist.md)
- [Release Attestation](release-attest.md)
- [Release Consume](release-consume.md)
- [Release Index](release-index.md)
- [Release Manifest](release-manifest.md)
- [Release Proof Bundle](release-proof.md)
- [Release Proof Action](release-proof-action.md)
- [Release Proof Consumption](release-proof-consumption.md)
- [Release Proof Workflows](release-proof-workflows.md)
- [Release Replay](release-replay.md)
- [SARIF Evidence Export](sarif.md)
- [Template Profiles](template-profiles.md)
- [GitHub Action](github-action.md)
- [Changelog](../CHANGELOG.md)

## What This Kit Provides

- Root instructions for Codex in a risk-sensitive iOS repo.
- Planning and subagent templates.
- Reusable skills for alarm testing, notification permissions, release work, bug triage, and UI polish.
- A small CLI for validation, starter profile initialization, doctor checks, run scoring, autopsy reports, SARIF export, fixture arena runs, review comments, CI gates, CI summaries, check-run payloads, leaderboard JSON, release manifests, release indexes, release replay verification, release attestations, one-command release consumption, toolkit self-audits, and next-goal generation.
- Reusable GitHub Actions for validation, CI gates, review comments, and release proof artifacts.
- Reusable GitHub Actions for validation and review-comment generation.
- Examples and a scorecard for judging agent output quality.

## First 30 Minutes

1. Read the [adoption guide](adoption-guide.md).
2. Run `./bin/codex-maintainer validate` in this repo.
3. Run `./bin/codex-maintainer init ios ../my-ios-app` against a test repo.
4. Open the generated `AGENTS.md` and replace placeholders.
5. Run `./bin/codex-maintainer doctor ../my-ios-app`.
6. Run `./bin/codex-maintainer init web ../my-web-app` against a test repo when adopting the web profile.
7. Run `./bin/codex-maintainer init backend ../my-service` or `./bin/codex-maintainer init cli ../my-tool` when adopting those profiles.
8. Run `./bin/codex-maintainer autopsy --run fixtures/autopsy/good-run/run.md --diff fixtures/autopsy/good-run/diff.patch --tests fixtures/autopsy/good-run/tests.log --out /tmp/autopsy-good`.
9. Run `./bin/codex-maintainer sarif --report /tmp/autopsy-good/report.json --out /tmp/autopsy-good/results.sarif`.
10. Run `./bin/codex-maintainer ci-summary --gate /tmp/codex-gate/gate.json --out /tmp/codex-gate/summary.md` after a gate run.
11. Run `./bin/codex-maintainer check-run --gate /tmp/codex-gate/gate.json --head-sha "$GITHUB_SHA" --out /tmp/codex-gate/check-run/payload.json` after a gate run.
12. Run `./bin/codex-maintainer check-run post --payload /tmp/codex-gate/check-run/payload.json --repo "$GITHUB_REPOSITORY" --out /tmp/codex-gate/check-run/response.json --dry-run` before enabling real posting.
13. Run `./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena`.
14. Run `./bin/codex-maintainer arena import --source fixtures/external-arena-pack --out /tmp/imported-arena`.
15. Run `./bin/codex-maintainer arena sign --fixture /tmp/imported-arena --out /tmp/imported-arena/PACK.json`.
16. Run `./bin/codex-maintainer arena verify --fixture /tmp/imported-arena --manifest /tmp/imported-arena/PACK.json`.
17. Run `./bin/codex-maintainer leaderboard build --arena-results /tmp/arena/results.json --out /tmp/leaderboard.json`.
18. Run `./bin/codex-maintainer release-manifest --tarball dist/codex-maintainer-v3.11.0.tar.gz --out /tmp/codex-maintainer-release-proof` after packaging.
19. Run `./bin/codex-maintainer release-index build --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --out /tmp/codex-maintainer-release-index`.
20. Run `./bin/codex-maintainer release-replay verify --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --tarball dist/codex-maintainer-v3.11.0.tar.gz --index /tmp/codex-maintainer-release-index/release-index.json --ledger /tmp/codex-maintainer-release-proof/proof-ledger.md --out /tmp/codex-maintainer-release-replay`.
21. Run `./bin/codex-maintainer release-attest build --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --replay /tmp/codex-maintainer-release-replay/replay-report.json --out /tmp/codex-maintainer-release-attestation`.
22. Run `./bin/codex-maintainer release-proof build --out /tmp/codex-maintainer-release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/v3.11.0`.
23. Run `./bin/codex-maintainer release-consume verify --dir /tmp/codex-maintainer-v3.11.0 --out /tmp/codex-maintainer-v3.11.0/consumer-proof --version 3.11.0` after downloading published assets.
24. Run `./bin/codex-maintainer self-audit --out /tmp/codex-maintainer-self-audit`.
25. Run `./bin/codex-maintainer next-goal --out /tmp/NEXT_GOAL.md`.
