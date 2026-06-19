# ShipGuard

ShipGuard is a local-first CLI and Codex plugin for proof-gated app maintenance. It helps developers turn AI-assisted work into scoped tasks, evidence receipts, review verdicts, and release proof instead of vague "looks good" handoffs.

Current published release: `v3.131.0`. That release adds V4 Release Candidate Readiness / LaunchKey. Active `main` work currently contains later ShipYard stabilization slices for external adoption evidence gating, native GitHub release-asset download, published-release asset proof, package fresh-install receipts, same-prefix upgrade receipts, rollback cleanup receipts, generated archive-member screening, blocking-proof result UX, and report-quality handling of generated LaunchKey proof directories, but v4 is not called stable until release assets prove install, upgrade, uninstall, rollback, schema, security, plugin refresh, independent adoption evidence, and release-proof consumption.

## Fast Routes

- New to ShipGuard: [Adoption guide](adoption-guide.md), [Use in your repo](use-in-your-repo.md), [Template Profiles](template-profiles.md).
- Picking a command: [Command Matrix](command-matrix.md), [CLI reference](cli.md), [Workflow diagram](workflow-diagram.md).
- Working with Codex: [Task Contract](task-contract.md), [iOS ShipGuard](ios-shipguard.md), [ShipGuard Devspace](shipguard-devspace.md), [Codex Status](codex-status.md).
- Checking UI or runtime proof: [iOS Preview Bridge](ios-preview.md), [ShipGuard Evaluation](oss-evaluation.md), [Demo Reports](demo-reports.md).
- Publishing or consuming releases: [Release Proof Bundle](release-proof.md), [Release Proof Consumption](release-proof-consumption.md), [Release Evidence Bundle](release-evidence-bundle.md), [Release Evidence Verification](release-evidence-verify.md).
- Reviewing the public repo page: [GitHub Presentation](github-presentation.md), [Open Source Operating Model](open-source.md), [Privacy](privacy.md), [Security Threat Model](security-threat-model.md).

## Documentation Map

Core workflow:

- [Adoption guide](adoption-guide.md)
- [Use in your repo](use-in-your-repo.md)
- [Workflow diagram](workflow-diagram.md)
- [Command Matrix](command-matrix.md)
- [CLI reference](cli.md)
- [Task Contract](task-contract.md)
- [Policy Configuration](policy.md)
- [Compatibility](compatibility.md)
- [Next Goal Generator](next-goal.md)

iOS and Codex surfaces:

- [iOS ShipGuard](ios-shipguard.md)
- [iOS Preview Bridge](ios-preview.md)
- [ShipGuard Devspace](shipguard-devspace.md)
- [Codex Status](codex-status.md)
- [Codex Marketplace Readiness](codex-marketplace-readiness.md)
- [PR Review Bot Mode](pr-review-bot.md)
- [GitHub Action](github-action.md)

Evidence, evaluation, and reports:

- [Agent Autopsy](autopsy.md)
- [Autopsy in GitHub Actions](autopsy-github-actions.md)
- [Maintainer Arena](arena.md)
- [Arena Compare Action](arena-compare-action.md)
- [Benchmark Format](benchmark.md)
- [Demo Reports](demo-reports.md)
- [ShipGuard Evaluation](oss-evaluation.md)
- [Docs Check](docs-check.md)
- [SARIF Evidence Export](sarif.md)
- [Transcript Redaction](transcript-redaction.md)
- [Transcript Verify Action](transcript-verify-action.md)
- [Transcript Corpus](transcript-corpus.md)
- [Transcript Corpus Action](transcript-corpus-action.md)

Release and provenance:

- [Release Checklist](release-checklist.md)
- [Release Manifest](release-manifest.md)
- [Release Index](release-index.md)
- [Release Replay](release-replay.md)
- [Release Attestation](release-attest.md)
- [Release Proof Bundle](release-proof.md)
- [Release Proof Action](release-proof-action.md)
- [Release Proof Workflows](release-proof-workflows.md)
- [Release Proof Consumption](release-proof-consumption.md)
- [Release Consume](release-consume.md)
- [Release Consume Action](release-consume-action.md)
- [Release Diff Audit](release-diff.md)
- [Release Diff Action](release-diff-action.md)
- [Release Evidence Site](release-evidence-site.md)
- [Release Evidence Index](release-evidence-index.md)
- [Release Evidence Action](release-evidence-action.md)
- [Release Evidence Bundle](release-evidence-bundle.md)
- [Release Evidence Verification](release-evidence-verify.md)

Product and open-source posture:

- [Product Strategy](product-strategy.md)
- [Maintainer Reliability OS](maintainer-reliability-os.md)
- [ShipGuard Naming](shipguard-naming.md)
- [ShipGuard V4 Preview](v4-preview.md)
- [V4 Schema Freeze](v4-schema-freeze.md)
- [V4 Release Candidate](v4-release-candidate.md)
- [Codex Marketplace Readiness](codex-marketplace-readiness.md)
- [GitHub Presentation](github-presentation.md)
- [Open Source Operating Model](open-source.md)
- [Privacy](privacy.md)
- [Security Threat Model](security-threat-model.md)
- [Changelog](../CHANGELOG.md)

## What This Kit Provides

- App-neutral root instructions for Codex in risk-sensitive repos.
- Starter profiles for iOS, web, backend, and CLI projects.
- Proof-gated `prepare` / `verify` task contracts for scoped AI changes.
- iOS reports for inventory, launch routing, performance, design, modernization, app intelligence, AI readiness, preview handoff, Devspace, and report quality.
- ShipYard QA reports: Tool Value Gauntlet, Full Audit, InspectDeck, MarketplaceDeck, PilotBench, TraceBridge, and v4 preview/schema/release-candidate gates.
- Release-proof tooling for manifests, indexes, replay, attestations, consumer verification, diffs, evidence sites, evidence bundles, and GitHub Actions.
- Public fixtures, demo reports, and evals that prove behavior without private app code.

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
13. Run `./bin/shipguard codex status` to inspect the local Codex plugin install state.
14. Install or refresh the local plugin with `codex plugin marketplace add .`, then `codex plugin add ios-shipguard@shipguard`, then start a new Codex thread.
15. Run `./bin/shipguard ios demo --out /tmp/ios-shipguard-first-run`.
16. Run `./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-doctor`.
17. Run `./bin/shipguard ios inventory --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-inventory`.
18. Run `./bin/shipguard ios performance --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-performance`.
19. Run `./bin/shipguard ios design --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-design --icon-brief`.
20. Run `./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict` before adding or renaming public ShipGuard surfaces.
21. Run `./bin/shipguard prepare "Add provisional notification onboarding flow" --path fixtures/demo-ios-repo --out /tmp/shipguard-task --profile ios --shareable`.
22. Run `./bin/shipguard verify --task /tmp/shipguard-task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/validation-receipt.json --out /tmp/shipguard-verdict` after Codex has a diff and proof receipt.
23. Use `--shipguard-eval` with `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, or `ios ai-readiness` only when a private app is a read-only sample for improving ShipGuard.
24. Run `./bin/shipguard ios report-quality --reports /tmp/ios-shipguard-performance --reports /tmp/ios-shipguard-design --out /tmp/ios-shipguard-report-quality` to grade ShipGuard report usefulness.
25. Run `./bin/shipguard ios external-audit --path . --source-url https://github.com/github/spec-kit --source-url https://github.com/rebel0789/codexpro --source-url https://github.com/expo/expo --out /tmp/ios-shipguard-external-audit --shareable` before treating external workflow ideas as integrated.
26. Run `./bin/shipguard ios spec-workflow --path fixtures/demo-ios-repo --feature "First-run spec workflow" --from-report /tmp/ios-shipguard-report-quality --out /tmp/ios-shipguard-spec --shareable`.
27. Read [Security Threat Model](security-threat-model.md) before adding network posting, plugin execution, release publishing, or external scan work.
28. Run `./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena`.
29. Run `./bin/shipguard arena import --source fixtures/external-arena-pack --out /tmp/imported-arena`.
30. Run `./bin/shipguard arena compare --left /tmp/arena-old/results.json --right /tmp/arena/results.json --out /tmp/arena-compare`.
31. Use `jlekerli-source/ShipGuard/actions/arena-compare@v3.131.0` when the same comparison should run in GitHub Actions.
32. Run `./bin/shipguard arena sign --fixture /tmp/imported-arena --out /tmp/imported-arena/PACK.json --signer "Example Maintainers" --signer-url "https://github.com/example/repo"`.
33. Run `./bin/shipguard arena verify --fixture /tmp/imported-arena --manifest /tmp/imported-arena/PACK.json`.
34. Run `./bin/shipguard leaderboard build --arena-results /tmp/arena/results.json --out /tmp/leaderboard.json`.
35. Run `./bin/shipguard release-manifest --tarball dist/shipguard-v3.131.0.tar.gz --out /tmp/shipguard-release-proof` after packaging.
36. Run `./bin/shipguard release-index build --manifest /tmp/shipguard-release-proof/release-manifest.json --out /tmp/shipguard-release-index`.
37. Run `./bin/shipguard release-replay verify --manifest /tmp/shipguard-release-proof/release-manifest.json --tarball dist/shipguard-v3.131.0.tar.gz --index /tmp/shipguard-release-index/release-index.json --ledger /tmp/shipguard-release-proof/proof-ledger.md --out /tmp/shipguard-release-replay`.
38. Run `./bin/shipguard release-attest build --manifest /tmp/shipguard-release-proof/release-manifest.json --replay /tmp/shipguard-release-replay/replay-report.json --out /tmp/shipguard-release-attestation`.
39. Run `./bin/shipguard release-proof build --out /tmp/shipguard-release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/v3.131.0`.
40. Run `./bin/shipguard release-consume verify --dir /tmp/shipguard-v3.131.0 --out /tmp/shipguard-v3.131.0/consumer-proof --version 3.131.0` after downloading published assets.
41. Use `jlekerli-source/ShipGuard/actions/release-consume@v3.131.0` when the same verification should run in GitHub Actions.
42. Run `./bin/shipguard release-diff compare --left /tmp/shipguard-old --right /tmp/shipguard-v3.131.0 --out /tmp/shipguard-release-diff`.
43. Use `jlekerli-source/ShipGuard/actions/release-diff@v3.131.0` when the same diff should run in GitHub Actions.
44. Run `./bin/shipguard release-evidence site --consume /tmp/shipguard-v3.131.0/consumer-proof --diff /tmp/shipguard-release-diff --out /tmp/shipguard-release-site`.
45. Run `./bin/shipguard release-evidence index --site /tmp/shipguard-release-site --out /tmp/shipguard-release-history`.
46. Run `./bin/shipguard release-evidence bundle --assets /tmp/shipguard-v3.131.0 --left /tmp/shipguard-old --out /tmp/shipguard-release-evidence-bundle --version 3.131.0`.
47. Use `jlekerli-source/ShipGuard/actions/release-evidence@v3.131.0` when the same evidence export should run in GitHub Actions.
48. Run `./bin/shipguard release-evidence verify --dir /tmp/shipguard-release-evidence --out /tmp/shipguard-release-evidence-verify --require-diff true --require-index true` after downloading an evidence artifact.
49. Use `jlekerli-source/ShipGuard/actions/release-evidence-verify@v3.131.0` when the evidence artifact verification should run in GitHub Actions.
50. Run `./bin/shipguard release-evidence negative-index --fixture fixtures/release-evidence/negative --out /tmp/shipguard-negative-evidence`.
51. Use `jlekerli-source/ShipGuard/actions/release-evidence-negative-index@v3.131.0` when the same negative fixture index should run in GitHub Actions.
52. Use `jlekerli-source/ShipGuard/actions/transcript-verify@v3.131.0` when redacted transcripts should be checked in GitHub Actions.
53. Run `./bin/shipguard transcript corpus --source fixtures/transcripts --out /tmp/transcript-corpus --require-report true` before publishing transcript examples.
54. Use `jlekerli-source/ShipGuard/actions/transcript-corpus@v3.131.0` when transcript corpus checks should run in GitHub Actions.
55. Run `./bin/shipguard self-audit --out /tmp/shipguard-self-audit`.
56. Run `./bin/shipguard next-goal --out /tmp/NEXT_GOAL.md`.
