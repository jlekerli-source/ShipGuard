# ShipGuard

This is the documentation landing page for the workflow kit.

Start here:

- [Adoption guide](adoption-guide.md)
- [Use in your repo](use-in-your-repo.md)
- [Workflow diagram](workflow-diagram.md)
- [Maintainer Arena](arena.md)
- [Arena Compare Action](arena-compare-action.md)
- [CLI reference](cli.md)
- [Agent Autopsy](autopsy.md)
- [Autopsy in GitHub Actions](autopsy-github-actions.md)
- [Benchmark Format](benchmark.md)
- [Check Run Payload](check-run.md)
- [CI Gate Mode](ci-gate.md)
- [CI Step Summary](ci-summary.md)
- [Command Matrix](command-matrix.md)
- [Demo Reports](demo-reports.md)
- [Docs Check](docs-check.md)
- [Maintainer Reliability OS](maintainer-reliability-os.md)
- [Next Goal Generator](next-goal.md)
- [Policy Configuration](policy.md)
- [PR Review Bot Mode](pr-review-bot.md)
- [Release Checklist](release-checklist.md)
- [Release Attestation](release-attest.md)
- [Release Consume](release-consume.md)
- [Release Consume Action](release-consume-action.md)
- [Release Diff Audit](release-diff.md)
- [Release Diff Action](release-diff-action.md)
- [Release Evidence Action](release-evidence-action.md)
- [Release Evidence Bundle](release-evidence-bundle.md)
- [Release Evidence Index](release-evidence-index.md)
- [Release Evidence Site](release-evidence-site.md)
- [Release Evidence Verification](release-evidence-verify.md)
- [Release Index](release-index.md)
- [Release Manifest](release-manifest.md)
- [Release Proof Bundle](release-proof.md)
- [Release Proof Action](release-proof-action.md)
- [Release Proof Consumption](release-proof-consumption.md)
- [Release Proof Workflows](release-proof-workflows.md)
- [Release Replay](release-replay.md)
- [SARIF Evidence Export](sarif.md)
- [Template Profiles](template-profiles.md)
- [Transcript Corpus Action](transcript-corpus-action.md)
- [Transcript Corpus](transcript-corpus.md)
- [Transcript Redaction](transcript-redaction.md)
- [Transcript Verify Action](transcript-verify-action.md)
- [GitHub Action](github-action.md)
- [Changelog](../CHANGELOG.md)

## What This Kit Provides

- Root instructions for Codex in a risk-sensitive iOS repo.
- Planning and subagent templates.
- Reusable skills for alarm testing, notification permissions, release work, bug triage, and UI polish.
- A small CLI for validation, starter profile initialization, doctor checks, run scoring, autopsy reports, SARIF export, docs link checks, fixture arena runs, Arena comparisons, transcript redaction, verification, and corpus indexing, review comments, CI gates, CI summaries, check-run payloads, leaderboard JSON, release manifests, release indexes, release replay verification, release attestations, one-command release consumption, release diffs, release evidence site exports, release evidence indexes, release evidence bundles, release evidence verification, toolkit self-audits, and next-goal generation.
- Reusable GitHub Actions for validation, Arena comparison artifacts, transcript verification, transcript corpus verification, CI gates, review comments, release proof artifacts, release proof consumption, release diff audits, release evidence exports, and release evidence verification.
- Examples and a scorecard for judging agent output quality.

## First 30 Minutes

1. Read the [adoption guide](adoption-guide.md).
2. Run `./bin/shipguard validate` in this repo.
3. Run `./bin/shipguard init ios ../my-ios-app` against a test repo.
4. Open the generated `AGENTS.md` and replace placeholders.
5. Run `./bin/shipguard doctor ../my-ios-app`.
6. Run `./bin/shipguard init web ../my-web-app` against a test repo when adopting the web profile.
7. Run `./bin/shipguard init backend ../my-service` or `./bin/shipguard init cli ../my-tool` when adopting those profiles.
8. Run `./bin/shipguard autopsy --run fixtures/autopsy/good-run/run.md --diff fixtures/autopsy/good-run/diff.patch --tests fixtures/autopsy/good-run/tests.log --out /tmp/autopsy-good`.
9. Run `./bin/shipguard sarif --report /tmp/autopsy-good/report.json --out /tmp/autopsy-good/results.sarif`.
10. Run `./bin/shipguard ci-summary --gate /tmp/codex-gate/gate.json --out /tmp/codex-gate/summary.md` after a gate run.
11. Run `./bin/shipguard check-run --gate /tmp/codex-gate/gate.json --head-sha "$GITHUB_SHA" --out /tmp/codex-gate/check-run/payload.json` after a gate run.
12. Run `./bin/shipguard check-run post --payload /tmp/codex-gate/check-run/payload.json --repo "$GITHUB_REPOSITORY" --out /tmp/codex-gate/check-run/response.json --dry-run` before enabling real posting.
13. Run `./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena`.
14. Run `./bin/shipguard arena import --source fixtures/external-arena-pack --out /tmp/imported-arena`.
15. Run `./bin/shipguard arena compare --left /tmp/arena-old/results.json --right /tmp/arena/results.json --out /tmp/arena-compare`.
16. Use `jlekerli-source/ShipGuard/actions/arena-compare@v3.38.0` when the same comparison should run in GitHub Actions.
17. Run `./bin/shipguard arena sign --fixture /tmp/imported-arena --out /tmp/imported-arena/PACK.json --signer "Example Maintainers" --signer-url "https://github.com/example/repo"`.
18. Run `./bin/shipguard arena verify --fixture /tmp/imported-arena --manifest /tmp/imported-arena/PACK.json`.
19. Run `./bin/shipguard leaderboard build --arena-results /tmp/arena/results.json --out /tmp/leaderboard.json`.
20. Run `./bin/shipguard release-manifest --tarball dist/shipguard-v3.38.0.tar.gz --out /tmp/shipguard-release-proof` after packaging.
21. Run `./bin/shipguard release-index build --manifest /tmp/shipguard-release-proof/release-manifest.json --out /tmp/shipguard-release-index`.
22. Run `./bin/shipguard release-replay verify --manifest /tmp/shipguard-release-proof/release-manifest.json --tarball dist/shipguard-v3.38.0.tar.gz --index /tmp/shipguard-release-index/release-index.json --ledger /tmp/shipguard-release-proof/proof-ledger.md --out /tmp/shipguard-release-replay`.
23. Run `./bin/shipguard release-attest build --manifest /tmp/shipguard-release-proof/release-manifest.json --replay /tmp/shipguard-release-replay/replay-report.json --out /tmp/shipguard-release-attestation`.
24. Run `./bin/shipguard release-proof build --out /tmp/shipguard-release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/v3.38.0`.
25. Run `./bin/shipguard release-consume verify --dir /tmp/shipguard-v3.38.0 --out /tmp/shipguard-v3.38.0/consumer-proof --version 3.38.0` after downloading published assets.
26. Use `jlekerli-source/ShipGuard/actions/release-consume@v3.38.0` when the same verification should run in GitHub Actions.
27. Run `./bin/shipguard release-diff compare --left /tmp/shipguard-old --right /tmp/shipguard-v3.38.0 --out /tmp/shipguard-release-diff`.
28. Use `jlekerli-source/ShipGuard/actions/release-diff@v3.38.0` when the same diff should run in GitHub Actions.
29. Run `./bin/shipguard release-evidence site --consume /tmp/shipguard-v3.38.0/consumer-proof --diff /tmp/shipguard-release-diff --out /tmp/shipguard-release-site`.
30. Run `./bin/shipguard release-evidence index --site /tmp/shipguard-release-site --out /tmp/shipguard-release-history`.
31. Run `./bin/shipguard release-evidence bundle --assets /tmp/shipguard-v3.38.0 --left /tmp/shipguard-old --out /tmp/shipguard-release-evidence-bundle --version 3.38.0`.
32. Use `jlekerli-source/ShipGuard/actions/release-evidence@v3.38.0` when the same evidence export should run in GitHub Actions.
33. Run `./bin/shipguard release-evidence verify --dir /tmp/shipguard-release-evidence --out /tmp/shipguard-release-evidence-verify --require-diff true --require-index true` after downloading an evidence artifact.
34. Use `jlekerli-source/ShipGuard/actions/release-evidence-verify@v3.38.0` when the evidence artifact verification should run in GitHub Actions.
35. Run `./bin/shipguard release-evidence negative-index --fixture fixtures/release-evidence/negative --out /tmp/shipguard-negative-evidence`.
36. Use `jlekerli-source/ShipGuard/actions/release-evidence-negative-index@v3.38.0` when the same negative fixture index should run in GitHub Actions.
37. Use `jlekerli-source/ShipGuard/actions/transcript-verify@v3.38.0` when redacted transcripts should be checked in GitHub Actions.
38. Run `./bin/shipguard transcript corpus --source fixtures/transcripts --out /tmp/transcript-corpus --require-report true` before publishing transcript examples.
39. Use `jlekerli-source/ShipGuard/actions/transcript-corpus@v3.38.0` when transcript corpus checks should run in GitHub Actions.
40. Run `./bin/shipguard self-audit --out /tmp/shipguard-self-audit`.
41. Run `./bin/shipguard next-goal --out /tmp/NEXT_GOAL.md`.
