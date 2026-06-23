# CLI

`bin/shipguard` is a dependency-light helper for validating and reusing this workflow kit. Inside the ShipGuard source checkout, examples use `./bin/shipguard`. Inside an app checkout, install the CLI once with `PREFIX="$HOME/.local" ./scripts/install.sh` from the ShipGuard source or release package, then run `shipguard` or `$HOME/.local/bin/shipguard`.

## Validate

Run this from a checkout of this repository:

```bash
./bin/shipguard validate
```

You can also pass a path to another checkout of this workflow bundle:

```bash
./bin/shipguard validate ../shipguard
```

Validation checks required files, skill metadata, shell syntax, executable scripts, local markdown links, YAML files, and whitespace.

## Policy

Create or inspect a policy file:

```bash
./bin/shipguard policy init .shipguard/policy.conf
./bin/shipguard policy show .shipguard/policy.conf
```

Pass a policy into Autopsy with `--policy`. See `policy.md`.

## Version

Print the toolkit version:

```bash
./bin/shipguard version
```

The command reads `VERSION`, which is also used by the release packaging script.

## Init

Copy a starter workflow profile into another project:

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard init web ../my-web-app
./bin/shipguard init backend ../my-service
./bin/shipguard init cli ../my-tool
```

The command writes:

- `AGENTS.md`
- `PLANS.md` from `templates/common/PLANS.md`
- `SUBAGENTS.md` from `templates/common/SUBAGENTS.md`
- `SCORECARD.md`
- `.agents/skills/`

Existing files are skipped. Use `--force` to overwrite generated workflow files:

```bash
./bin/shipguard init ios ../my-ios-app --force
./bin/shipguard init web ../my-web-app --force
./bin/shipguard init backend ../my-service --force
./bin/shipguard init cli ../my-tool --force
```

See `template-profiles.md` for profile details.

## Doctor

Check whether a target repo has the starter workflow files:

```bash
./bin/shipguard doctor --help
./bin/shipguard doctor ../my-ios-app
./bin/shipguard doctor ios ../my-ios-app
./bin/shipguard doctor web ../my-web-app
./bin/shipguard doctor backend ../my-service
./bin/shipguard doctor cli ../my-tool
```

`doctor` without a profile defaults to `ios` for compatibility with older releases.
The report is ShipGuard RepoVitals: it starts with the selected profile and target, prints file-level `ok:` or `missing:` checks, then ends with `Status`, `Required files`, and the next action. Missing starter files exit non-zero and point back to `shipguard init <profile> <target>`.

See `install-doctor.md` for the first-run install and RepoVitals path.

## Task Contract

Use `prepare` before Codex edits and `verify` after Codex edits when a task needs scoped proof instead of a loose report directory:

```bash
./bin/shipguard prepare \
  "Add provisional notification onboarding flow" \
  --path ../my-ios-app \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "xcodebuild test -scheme MyApp -only-testing:NotificationPermissionTests" \
  --shareable

./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/xcodebuild-receipt.json \
  --claim "Implemented the onboarding permission flow." \
  --out /tmp/shipguard-verdict
```

`prepare` writes `shipguard-task.json` and `shipguard-task.md` with repo context, risk, allowed files, protected boundaries, required validation, tracked claims, `domainPackSDK` registry metadata, `quickstartReplay`, and the next exact action. For iOS notification, permission, authorization, denied-state, or provisional-flow goals, it also emits `domainRiskPack.id = ios-notification-permission-workflow` with scope recommendations, receipt requirements, and simulator/device proof boundaries. `verify` writes `shipguard-verdict.json` and `shipguard-verdict.md` with a concise `Proof Report` first, then `Quickstart Replay`, changed files, scope violations, v2 evidence receipt normalization, structured validation coverage, rejected overclaims, manual-proof overclaims, diff-first merge status, active domain-workflow proof lanes, compatibility fields such as `notificationPermissionWorkflow`, and the next exact action. The verdict includes `proofReport` for copy-ready PR/status summaries, `quickstartReplay` for the replay command and review packet, `unsupportedClaimReplay` when broad completion wording is not fully backed, and `evidenceReceiptSchema` so current v2, legacy-compatible, stale, invalid, downgraded, artifact-only, and missing evidence are visible instead of collapsed into a vague pass/fail.

When reviewer disposition is missing, `verify` also prints two labeled repair commands. `Record reviewer outcome without note` is for an obvious accepted/dismissed/follow-up decision. `Record reviewer outcome with note` adds `--reviewer-note` for decisions that should explain maintainer judgment before ShipGuard uses the local outcome as future rule-tuning evidence. These labels are maintainer routing hints only; reviewer disposition remains local feedback, not adoption, benchmark, or security-review proof.

See `task-contract.md` and `verify-first-quickstart.md`.

## GitHub Action First Run

Use `action verify-pr` after copying `examples/workflows/verify-pr.yml` into another repository:

```bash
./bin/shipguard action verify-pr \
  --workflow .github/workflows/shipguard-verify-pr.yml \
  --out /tmp/shipguard-action-verify-pr \
  --shareable
```

The command writes `action-verify-pr.json` and `action-verify-pr.md`. It is read-only and checks the static setup for the first PR-proof workflow: pull request trigger, checkout depth, ShipGuard install, PR diff generation, configured validation command, `prepare` validation wiring, validation execution, v2 structured receipt, `verify` task/diff/evidence wiring, `if: always()` proof generation, and uploaded `shipguard-verdict` artifact. A copied starter with `replace-with-your-test-command` still present returns `review`; missing install, diff, receipt, verify, or upload wiring returns `blocked`. Blocked reports include a `freshMaintainerFailureGuide` that separates static setup from runtime artifact proof and points to the first blocking rule before lower-severity review items. Static pass is not a runtime claim: open a small PR and inspect the uploaded `shipguard-verdict` artifact before treating the workflow as proven.

After downloading the GitHub artifact, add `--artifact-dir /tmp/shipguard-verdict-artifact` to the same command. ShipGuard then consumes `shipguard-verdict.json` and Markdown, verifies that the artifact came from `shipguard verify`, checks proof-report, validation-coverage, v2 receipt, diff-first, and next-action fields, and reports the runtime verdict status separately from the workflow setup status. Runtime artifact reports include `runtimeReviewerHandoff`, which translates the verdict into a reviewer decision, merge verdict, proof-to-attach list, failure meaning, and read-only PR state command instead of leaving reviewers with a vague status note.

See `action-verify-pr.md` and `github-action.md`.

## Lean Deck

Use `lean audit` when you want ShipGuard to look for code that may not need to exist before asking an agent to add more code:

```bash
./bin/shipguard lean audit \
  --path . \
  --out /tmp/shipguard-lean-audit \
  --mode full \
  --shipguard-eval \
  --shareable
```

The command writes `lean-audit.json` and `lean-audit.md`. It reports native platform, standard-library, dependency, and thin-wrapper opportunities, while marking security, validation, data-loss, permission, payment, migration, accessibility, hardware calibration, and host-adapter files as proof-required boundaries. The JSON includes `leanMode`, `behaviorGates`, `nativeOpportunityCatalog`, `precisionReview.deleteList`, `simplifyFirst`, `keepList`, `blockedByProof`, `actionGroups`, `topActions`, `cleanStateAction`, and `leanDebtLedger` so repeated findings become a grouped simplification plan and clean pass-state reports still name a proof probe instead of pointing at missing work. Use `--mode lite` for lighter suggestions, `--mode full` for the default proof ladder, and `--mode ultra` when cleanup should try deletion before adding or refactoring code. See `lean-audit.md`.

Use `lean review` on the active diff before merge:

```bash
git diff > /tmp/change.diff
./bin/shipguard lean review \
  --path . \
  --diff /tmp/change.diff \
  --out /tmp/shipguard-lean-review \
  --mode full \
  --shipguard-eval \
  --shareable
```

The command writes `lean-review.json` and `lean-review.md`. It is diff-scoped and reports native, standard-library, dependency, speculative placeholder, and thin-wrapper findings without turning a whole-repo audit into noise. JSON now includes `currentDiffDecisionMap` with `scope: current-diff-only`, changed-file decisions, a delete/simplify subset, whole-repo non-claims, and a `lean audit` fallback when a maintainer actually needs repo inventory. It also emits `modeBiasReview`, which proves the selected `lite|full|ultra` priority order, mirrors the selected first-action bias, and verifies `precisionReview.topActions[0]` starts from the selected mode's source list. `safetyBoundaryReview` keeps security, validation, data-loss, permission, and accessibility rows out of automatic deletion until focused behavior proof exists. `hardwareHostBoundaryReview` separates hardware calibration rows from host-adapter keep rows so sensor, timing, plugin, MCP, preview, simulator, and platform adapter code is not removed by false less-code pressure. `--mode lite|full|ultra` biases `precisionReview.topActions` toward suggestion-first, balanced proof-ladder, or delete-first review. When repeated diff findings share the same rule, `precisionReview.actionGroups` and the Markdown `Grouped Action Plan` make the first experiment, validation route, and stop condition visible before individual line items. Clean diffs emit `precisionReview.cleanStateAction` so pass-state reports say which proof probe or next diff to inspect instead of referencing an empty top action. `proofSignalCalibration` summarizes missing runnable checks versus same-diff proof signals, `proofSignalMatching` is the file-scoped matched/unmatched proof map, and `runnableCheckReview` lists the exact missing-proof rows, matched same-diff proof rows, and duplicate-ceremony avoidance. Unrelated test files are listed as unmatched proof signals and no longer hide a missing runnable check for a different changed file.

Use `lean debt` when you only need the shortcut ledger:

```bash
./bin/shipguard lean debt \
  --path . \
  --out /tmp/shipguard-lean-debt \
  --shipguard-eval \
  --shareable
```

The command writes `lean-debt.json` and `lean-debt.md`. It harvests `ponytail:` and `shipguard-lean:` markers, emits `markerVisibilityReview` with total, visible, ceiling, missing-ceiling, upgrade-trigger, missing-trigger, upgrade-status, and omitted-row counts, and flags any marker that lacks a `ceiling:` or `upgrade:` trigger without hiding the incomplete row. It also emits `rotRiskReview`, a prioritized row list that names the top visible marker likely to rot, why it is risky, the exact next action, and the proof needed before cleanup, so a maintainer does not need another source inspection pass to pick the first bet. If marker rows are omitted by the ledger cap, both reviews mark the omitted state/risk as unknown instead of pretending visible rows are exhaustive. It also emits `currentRepoBoundary.perRepoSavingsClaim = not-computed`, because shortcut marker counts are ledger evidence only; use `lean gain` for benchmark direction and do not claim current-repo line, token, cost, or time savings from marker counts.

Use `lean gain` when you want the Ponytail-style impact scoreboard without pretending the current repo has measured savings:

```bash
./bin/shipguard lean gain \
  --path . \
  --out /tmp/shipguard-lean-gain \
  --shipguard-eval \
  --shareable
```

The command writes `lean-gain.json` and `lean-gain.md`. It reports benchmark-backed line/token/cost/time direction, marks current-repo savings as `not-computed`, and points current repo proof back to structured evidence routes for `lean audit`, `lean review`, and `lean debt`, including the command to run, expected artifact, answer, proof boundary, and non-claim for each route.

## Release Package Hygiene

Use `release-package hygiene` before package install or upgrade proof when release tarball lineage matters:

```bash
./bin/shipguard release-package hygiene \
  --path . \
  --out /tmp/shipguard-package-hygiene \
  --shareable

./bin/shipguard release-package hygiene \
  --path . \
  --tarball dist/shipguard-v3.131.0.tar.gz \
  --assets /tmp/downloaded-release-assets \
  --out /tmp/shipguard-package-hygiene \
  --shareable
```

The command is read-only. It scans `shipguard-v*.tar.gz` members without extraction, blocks generated metadata such as AppleDouble `._*`, `.DS_Store`, `__MACOSX`, bytecode/cache paths, unsafe links/devices, path traversal, and missing installable package roots, then emits `release-package-hygiene.json` and `release-package-hygiene.md` with affected versions, safe current baseline, repair commands, non-claims, and report-quality questions. See `release-package-hygiene.md`.

## V4 Product Track

Use `v4 preview` to inspect the v4 stabilization contract, `v4 schema-freeze` to prove the schema contract is frozen, `v4 release-candidate` to prove install, upgrade, uninstall, release proof consumption, external adoption packet, final schema docs, and plugin refresh readiness, and `v4 stable-publication` to prove the actual published release from public GitHub release metadata, latest release context, release notes, downloaded assets, tag/manifest freshness, version/asset coherence, public release delta proof, independent adoption evidence, and final security-review evidence.

For stable publication, `release-consume` must run against the published release assets. Fixture-backed or source-only receipts remain ShipGuard QA, not stable-v4 consumer proof:

```bash
./bin/shipguard v4 preview \
  --path . \
  --out /tmp/shipguard-v4-preview \
  --shipguard-eval \
  --shareable

./bin/shipguard v4 schema-freeze \
  --path . \
  --out /tmp/shipguard-v4-schema-freeze \
  --shipguard-eval \
  --shareable

./bin/shipguard v4 release-candidate \
  --path . \
  --out /tmp/shipguard-v4-release-candidate \
  --shipguard-eval \
  --shareable

./bin/shipguard v4 release-candidate \
  --path . \
  --out /tmp/shipguard-v4-release-candidate \
  --package-tarball <release-tarball> \
  --upgrade-from-tarball <previous-release-tarball> \
  --fresh-install-prefix /tmp/shipguard-fresh-install \
  --upgrade-prefix /tmp/shipguard-upgrade-install \
  --rollback-prefix /tmp/shipguard-rollback-install \
  --download-release-assets \
  --github-release-repo <owner/repo> \
  --release-version <version> \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable

./bin/shipguard v4 release-candidate \
  --path . \
  --out /tmp/shipguard-v4-release-candidate \
  --package-tarball <release-tarball> \
  --upgrade-from-tarball <previous-release-tarball> \
  --release-assets <downloaded-assets-dir> \
  --release-version <version> \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable

./bin/shipguard v4 stable-publication \
  --path . \
  --out /tmp/shipguard-v4-stable-publication \
  --release-version <version> \
  --release-candidate-report <v4-release-candidate-json-or-dir> \
  --download-release-assets \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable
```

`v4 stable-publication` infers `--github-release-repo` from the target repo's `origin` remote when possible; pass it explicitly for forks, mirrors, fixtures, or any publication target that is not `origin`.

For `v4 stable-publication --download-release-assets`, the default generated `--out/downloaded-release-assets` directory is refreshed on rerun; explicit `--download-release-assets-dir` paths remain caller-owned and keep the non-empty destination guard, and `--release-assets` paths are never refreshed by ShipGuard. When verified local release assets exist but the public asset packet needs repair, the update-assets handoff emits a manual `gh release upload ... --clobber` command; ShipGuard does not upload assets itself. When the missing public GitHub release is the first blocker, result UX points at the manual `gh release create ...` handoff instead of a generic rerun.

When release notes are the first blocker, the generated `gh release edit --notes-file` command points at the draft under the report output directory; `stablePublicationReleaseNotesAuthoringKit.generatedPaths` and `files[].generatedPath` expose the generated README/checklist/draft paths, and shareable reports redact the local output root.

When the release visibility handoff decides `publish-new-github-release`, its action row uses the generated `gh release create ...` command with the draft release-notes path and concrete supplied/downloaded release-asset files when available; ShipGuard still does not publish the release.

`v4 schema-freeze` writes `v4-schema-freeze.json` and `v4-schema-freeze.md` with the schema registry, compatibility policy, compatibility fixtures, migration checks, changelog policy, deprecation policy, release-readiness commands, blocked claims, scope boundary, report-quality questions, and result UX. `v4 release-candidate` writes `v4-release-candidate.json` and `v4-release-candidate.md` with readiness proof, install proof, optional fresh package install proof, optional same-prefix upgrade proof, optional rollback cleanup proof, release proof consumption, optional native GitHub release-asset download or supplied published release asset proof, external adoption packet, external adoption evidence proof, security review evidence proof, plugin refresh proof, blocked claims, and stable-v4 non-claims. Without `--package-tarball`, fresh package proof and rollback cleanup proof are marked `not-provided`; with `--package-tarball`, LaunchKey screens the tarball for generated archive members, extracts it, installs to a fresh prefix, checks both CLI aliases, runs `shipguard validate`, records `freshInstallPackageProof`, and removes a temporary package install to record `rollbackPackageProof`. Without `--upgrade-from-tarball`, upgrade package proof is marked `not-provided`; with `--upgrade-from-tarball`, LaunchKey screens the previous tarball, installs the previous package into a prefix, installs the candidate package over the same prefix, verifies versions and the compatibility alias, runs validation, and records `upgradePackageProof`. Without `--release-assets` or `--download-release-assets`, published release proof is marked `not-provided`; with `--download-release-assets --github-release-repo <owner/repo>`, LaunchKey downloads GitHub release assets into a local proof directory, records `githubReleaseAssetDownloadProof`, then runs `release-consume verify` and attaches the consumer receipt. With `--release-assets`, LaunchKey uses an already downloaded asset directory instead. Without `--external-adoption-evidence`, external adoption proof is marked `not-provided`; with `--external-adoption-evidence`, LaunchKey validates JSON records, separates structurally valid fixture evidence from stable-v4 eligible independent evidence, and blocks private paths, private app identifiers, or token-like strings. Without `--security-review-evidence`, security proof is marked `not-provided`; with `--security-review-evidence`, LaunchKey validates JSON records, requires CLI/plugin/GitHub Actions/release-proof/package-install/redaction-privacy scope coverage, separates structurally valid fixture evidence from stable-v4 eligible review evidence, and blocks private paths, private app identifiers, token-like strings, missing scope, or open critical/high findings. `v4 stable-publication` writes `v4-stable-publication.json` and `v4-stable-publication.md` with GitHub release metadata proof, structured release-notes proof, the supplied LaunchKey candidate packet, downloaded or supplied release-asset consumer proof, public release freshness proof, release version coherence, release asset coherence, `publicEvidenceClosureProof`, `publicReleaseDeltaProof`, `releaseVisibilityHandoff`, `finalStableV4ClaimPacket`, stable adoption/security gates, a `stablePublicationEvidencePacket` checklist, a `stablePublicationClosureChecklist` ordered blocker list, draft-only `stablePublicationEvidenceTemplates` for adoption and security-review records, a generated draft-only `stable-publication-evidence-kit/` containing a README, checklist JSON, adoption starter JSON, and security-review starter JSON, a generated draft-only `stable-publication-release-notes/` authoring kit with a checklist and draft release notes, and a generated draft-only `stable-publication-launch-relay/` packet with Product Hunt, r/ShipGuard, X, and Hacker News drafts. The public evidence closure proof summarizes adoption/security gate status, freshness, starter paths, copy-ready commands, and non-claims for GitHub downloads, fixtures, marketplace acceptance, and external posting. The public release delta proof compares local `HEAD`/`main`, the selected release, the latest GitHub release, package assets, and claim scope so unpublished local code is not mistaken for a published release. The release visibility handoff turns that delta into one primary decision: publish a new GitHub release, update release notes, attach LaunchKey candidate proof, update release assets, attach adoption/security evidence, or keep the current public release unchanged. The final claim packet gives copy-ready allowed or blocked wording, mirrors evidence status rows, names the first blocker, carries the next command, and keeps posting approval and marketplace non-claims visible. The launch relay has `approvalRequired: true`, `publicPostingAllowed: false`, and `computerUseMayPost: false`; it prepares local copy only and does not publish, submit, post, schedule, or perform account-visible actions. The release-notes proof analyzes the full GitHub release body and requires stable-v4 claim wording, publication-proof boundaries, downloaded release assets, post-release consumer proof, independent adoption evidence, final security review evidence, and non-claim boundaries. It also emits blocked claims, scope boundary, and result UX. It returns `review` unless every stable-publication gate passes and `stableV4Release` is true. When any supplied package, upgrade, rollback, GitHub metadata, GitHub download, release-asset, freshness, version-coherence, asset-coherence, adoption-evidence, security-evidence, release-notes, or publication receipt fails, the result UX, evidence packet, closure checklist, GitHub release metadata closure kit, release-notes closure kit, LaunchKey candidate closure kit, release-asset closure kit, post-release consumer closure kit, public release freshness closure kit, public evidence closure proof, release visibility handoff, adoption/security evidence closure kits, template catalog, starter kit, and launch relay identify every remaining failing receipt, first blocker, next command, selected repo, repo inference, release tag, API endpoint, draft/prerelease state, public-metadata/source-only/fixture-API boundary, public-edit boundary, supplied candidate report path, nested blocking receipt, required LaunchKey proof areas, package-hygiene diagnostics, required release assets, GitHub metadata/local/digest missing assets, missing SHA-256 rows, manifest/digest/consumer SHA-256 comparisons, download source/status, release-consume paths/statuses, missing proof artifacts, digest/replay/attestation crosschecks, tag-target/manifest comparisons, metadata-only/source-only/fixture-proof boundaries, starter path, required fields, privacy boundary, pass/fail criteria, current diagnostics, and guarded draft path. `ios report-quality` treats LaunchKey's generated `fresh-install-prefix`, `fresh-install-work`, `upgrade-prefix`, `upgrade-work`, `rollback-prefix`, `rollback-work`, `downloaded-release-assets`, `release-consume`, and stable-publication `stable-publication-evidence-kit`, `stable-publication-release-notes`, and `stable-publication-launch-relay` directories as internal proof attachments when they live under report output. See `v4-preview.md`, `v4-schema-freeze.md`, `v4-release-candidate.md`, and `v4-stable-publication.md`.

## Agent Trace

Use `agent trace` after or during agent work when you have an exported/synthetic trace and want one timeline that connects prompts, tool calls, receipts, optional `shipguard verify` output, verdicts, next actions, worker-budget state, and optional XcodeBuildMCP proof:

```bash
./bin/shipguard agent trace \
  --trace /tmp/codex-trace.json \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --xcodebuildmcp-evidence /tmp/xcodebuildmcp-proof \
  --expo-eas-evidence /tmp/expo-eas-proof \
  --run-verify \
  --out /tmp/shipguard-agent-trace \
  --adapter codex \
  --shipguard-eval \
  --shareable
```

`codex trace` is the Codex-native alias:

```bash
./bin/shipguard codex trace --trace /tmp/codex-trace.json --xcodebuildmcp-evidence /tmp/xcodebuildmcp-proof --expo-eas-evidence /tmp/expo-eas-proof --out /tmp/shipguard-codex-trace --shipguard-eval --shareable
```

Both commands write `agent-trace.json`, `agent-trace.md`, and `agent-trace-receipt.json`. See `agent-trace.md`.

## Inspect

Use `inspect` when you want the current ShipGuard state from one concise surface:

```bash
./bin/shipguard inspect \
  --path . \
  --out /tmp/shipguard-inspect \
  --value-gauntlet /tmp/shipguard-value-gauntlet \
  --full-audit /tmp/shipguard-full-audit \
  --release-assets dist/release-proof-bundle-v3.131.0 \
  --shipguard-eval \
  --shareable
```

`inspect` writes `shipguard-inspect.json` and `shipguard-inspect.md` with repo state, proof inputs, value-gauntlet summary, full-audit summary, local Codex plugin state, release proof state, one verdict, one next action, and underlying evidence pointers. It is read-only and does not push, publish, or edit target apps. See `inspect.md`.

## V4 Preview

Use `v4 preview` when the roadmap says a v4 capability is ready enough to stabilize, but not ready to call released:

```bash
./bin/shipguard v4 preview \
  --path . \
  --out /tmp/shipguard-v4-preview \
  --shipguard-eval \
  --shareable
```

`v4 preview` writes `v4-preview.json` and `v4-preview.md` with the v4 product contract, schema-freeze posture, security-review gates, migration plan, deprecation policy, release-readiness commands, blocked claims, scope boundary, report-quality questions, and compact result UX. It is read-only, ShipGuard-only product QA. It does not edit target apps, publish a release, or claim v4 is stable. See `v4-preview.md`.

## Profile Audits

After a starter profile is installed, run the profile-native first audit for non-iOS targets:

```bash
./bin/shipguard web audit --path ../my-web-app --out /tmp/shipguard-web-audit --shareable
./bin/shipguard backend audit --path ../my-service --out /tmp/shipguard-backend-audit --shareable
./bin/shipguard cli audit --path ../my-tool --out /tmp/shipguard-cli-audit --shareable
./bin/shipguard web plan --report /tmp/shipguard-web-audit --target ../my-web-app --out /tmp/shipguard-web-plan --shareable
./bin/shipguard backend plan --report /tmp/shipguard-backend-audit --target ../my-service --out /tmp/shipguard-backend-plan --shareable
./bin/shipguard cli plan --report /tmp/shipguard-cli-audit --target ../my-tool --out /tmp/shipguard-cli-plan --shareable
```

- `shipguard web audit` writes ShipGuard WebScan reports with framework, auth/payment, validation, starter-health, scan-transparency, and next-command evidence. Generated ShipGuard starter files count toward starter health, not target framework, validation, or risk signals.
- `shipguard web plan` writes ShipGuard WebForge reports that convert WebScan findings into scoped tasks, validation commands, stop conditions, and report-quality questions.
- `shipguard backend audit` writes ShipGuard ServiceRadar reports with API, auth, migration, queue, webhook, observability, validation, scan-transparency, and next-command evidence. Generated ShipGuard starter files count toward starter health, not target framework, validation, or risk signals.
- `shipguard backend plan` writes ShipGuard ServiceForge reports that convert ServiceRadar findings into scoped backend tasks, validation commands, stop conditions, and report-quality questions.
- `shipguard cli audit` writes ShipGuard CommandLens reports with dispatch, argument parsing, stdout/stderr, exit-code, redaction, packaging, scan-transparency, and next-command evidence. Generated ShipGuard starter files count toward starter health, not target framework, validation, or risk signals.
- `shipguard cli plan` writes ShipGuard CommandForge reports that convert CommandLens findings into CLI contract tasks, smoke checks, validation commands, stop conditions, and report-quality questions.

Add `--shipguard-eval` when using a target repo only as ShipGuard product QA, and use `shipguard ios report-quality --reports <audit-or-plan-dir> --out <quality-dir> --shareable` to grade whether the report itself is actionable. Profile plan commands are still read-only; they do not authorize target-app edits.

## iOS ShipGuard

Run iOS-specific topology, inventory, planning, proof, preview, and privacy helpers before risky Codex edits:

```bash
./bin/shipguard ios doctor --path ../my-ios-app --out /tmp/ios-shipguard-doctor
./bin/shipguard ios inventory --path ../my-ios-app --out /tmp/ios-shipguard-inventory
./bin/shipguard ios plan --mode permission-audit --inventory /tmp/ios-shipguard-inventory/ios-inventory.json --out /tmp/ios-shipguard-plan
./bin/shipguard ios plan --mode performance-audit --inventory /tmp/ios-shipguard-inventory/ios-inventory.json --out /tmp/ios-shipguard-performance-plan
./bin/shipguard ios prove --plan /tmp/ios-shipguard-plan/ios-plan.json --out /tmp/ios-shipguard-proof
./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard v4 preview --path . --out /tmp/shipguard-v4-preview --shipguard-eval --shareable
./bin/shipguard web audit --path ../my-web-app --out /tmp/shipguard-web-audit --shipguard-eval --shareable
./bin/shipguard web plan --report /tmp/shipguard-web-audit --target ../my-web-app --out /tmp/shipguard-web-plan --shipguard-eval --shareable
./bin/shipguard backend audit --path ../my-service --out /tmp/shipguard-backend-audit --shipguard-eval --shareable
./bin/shipguard backend plan --report /tmp/shipguard-backend-audit --target ../my-service --out /tmp/shipguard-backend-plan --shipguard-eval --shareable
./bin/shipguard cli audit --path ../my-tool --out /tmp/shipguard-cli-audit --shipguard-eval --shareable
./bin/shipguard cli plan --report /tmp/shipguard-cli-audit --target ../my-tool --out /tmp/shipguard-cli-plan --shipguard-eval --shareable
./bin/shipguard ios launchdeck --path ../my-ios-app --out /tmp/ios-shipguard-launchdeck
./bin/shipguard ios performance --path ../my-ios-app --out /tmp/ios-shipguard-performance
./bin/shipguard ios design --path ../my-ios-app --out /tmp/ios-shipguard-design --icon-brief
./bin/shipguard ios launchdeck --path ../my-ios-app --workflow performance --out /tmp/ios-shipguard-launchdeck-eval --shipguard-eval --shareable
./bin/shipguard ios launchdeck --path ../my-ios-app --workflow performance --receipt /tmp/codex-launchdeck-proof --out /tmp/ios-shipguard-launchdeck-receipts --shipguard-eval --shareable
./bin/shipguard ios performance --path ../my-ios-app --out /tmp/ios-shipguard-performance-eval --shipguard-eval --shareable
./bin/shipguard ios design --path ../my-ios-app --out /tmp/ios-shipguard-design-eval --shipguard-eval --shareable
./bin/shipguard ios modernize --focus swift --path ../my-ios-app --out /tmp/ios-shipguard-modernize-eval --shipguard-eval --shareable
./bin/shipguard ios app-intelligence --path ../my-ios-app --out /tmp/ios-shipguard-app-intelligence-eval --shipguard-eval --shareable
./bin/shipguard ios ai-readiness --path ../my-ios-app --out /tmp/ios-shipguard-ai-readiness-eval --shipguard-eval --shareable
./bin/shipguard ios external-audit --path . --source-path /tmp/spec-kit --source-path /tmp/codexpro --source-path /tmp/ponytail --source-url https://github.com/expo/expo --out /tmp/ios-shipguard-external-audit --shipguard-eval --shareable
./bin/shipguard ios report-quality --reports /tmp/ios-shipguard-performance-eval --reports /tmp/ios-shipguard-design-eval --out /tmp/ios-shipguard-report-quality --shareable
./bin/shipguard ios spec-workflow --path ../my-ios-app --feature "Improve report actionability" --from-report /tmp/ios-shipguard-report-quality --out /tmp/ios-shipguard-spec --shipguard-eval --shareable
./bin/shipguard ios devspace-check --path . --preview-out /tmp/ios-shipguard-preview --out /tmp/ios-shipguard-devspace-check
./bin/shipguard prepare "Add provisional notification onboarding flow" --path ../my-ios-app --out /tmp/shipguard-task --profile ios --shareable
./bin/shipguard verify --task /tmp/shipguard-task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/validation-receipt.json --reviewer-disposition accepted --out /tmp/shipguard-verdict
./bin/shipguard verify --task /tmp/shipguard-task/shipguard-task.json --diff /tmp/change.diff --evidence /tmp/validation-receipt.json --reviewer-disposition accepted --reviewer-note "Accepted after reviewing the proof packet." --out /tmp/shipguard-verdict
```

`ios doctor` writes `ios-doctor.json` and `ios-doctor.md` with a privacy-safe `<target-repo>` root, stable `schemaVersion`/`generatedAt` metadata, target topology, and structured findings. That makes DockCheck usable as first evidence for `ios inventory`, `ios report-quality`, and release/package proof without exposing local checkout paths.

The iOS namespace also includes:

- `brand` or `ios brand`: run ShipGuard Brand Deck, the toolkit-wide naming contract for future surfaces. It audits the branded surface scheme, public-command coverage, active docs coverage, stale active wording, and the rule that fun names must sit beside plain purpose and proof boundaries.
- `prepare` and `verify`: run the core ShipGuard Task Contract loop. `prepare` creates one durable task object before Codex edits; `verify` checks the exact diff, evidence receipts, and agent claims against that object and returns pass, review, or blocked with one exact next action. Add `--reviewer-disposition accepted|dismissed|follow-up|unknown` after review to leave a local outcome receipt for recurring-signal tuning.
- `action verify-pr`: run the read-only first-run GitHub Actions proof-path audit for a copied `verify-pr.yml` workflow, then optionally consume the downloaded `shipguard-verdict` artifact with `--artifact-dir` and emit a runtime reviewer handoff before trusting uploaded PR proof.
- `value-gauntlet`: run ShipGuard Tool Value Gauntlet, a read-only ShipYard product-QA report that grades every command, skill, plugin, GitHub Action, doc, test, package proof, and proof boundary for real developer usefulness before new surfaces are treated as mature. Its Lowest-Value Surface Probe ranks deeper evidence signals, executes representative ShipGuard commands on public/demo inputs through `runtimeOutputProbe`, rejects decorative or boundaryless reports through `runtimeOutputNegativeFixtures`, executes `--help` for all public commands through `runtimeCommandFamilyCoverage`, executes skill/plugin workflow receipts through `skillPluginRuntimeReceipts`, proves report-quality-to-spec-to-next-goal handoffs through `workflowChainReceipts`, runs complete public maintainer-loop proof through `scenarioMatrixReceipts`, proves bad evidence is blocked through `scenarioFailureReceipts`, proves repair and successful rerun paths through `scenarioRemediationReceipts`, proves fresh package install/plugin/audit handoff through `adoptionReceipts`, proves fresh iOS target starter onboarding through `targetOnboardingReceipts`, proves iOS/web/backend/CLI starter onboarding through `multiProfileOnboardingReceipts`, proves web/backend/CLI first-audit reports through `profileNativeFirstAuditReceipts`, proves web/backend/CLI fix plans through `profileNativeFixPlanReceipts`, proves web/backend/CLI validation classification through `profileNativeValidationReceipts`, proves blocked web/backend/CLI validation lanes clear after fixture-local smallest repairs through `profileNativeValidationRerunReceipts`, proves repaired web/backend/CLI plans emit copy-ready evidence packets through `profileNativeProofHandoffReceipts`, proves major command-family JSON/Markdown runtime output through `commandFamilyRuntimeOutputReceipts`, proves trust-hardening through `trustHardeningReceipts`, proves diff-first prepare/verify behavior through `taskContractReceipts`, proves ShipGuard PilotBench traces through `externalPilotVerdictBenchReceipts`, proves synthetic Domain Pack SDK extension through `domainPackSDKReceipts`, proves accepted-risk baseline behavior through `configurationBaselineReceipts`, proves structured evidence receipts v2 through `structuredEvidenceReceipts`, proves TraceBridge through `agentAdapterReceipts`, proves typed XcodeBuildMCP proof through `xcodeBuildMCPEvidenceReceipts`, proves Expo/EAS assurance proof through `expoEASAssuranceReceipts`, proves Claude, Gemini, Cursor, MCP, and generic trace packaging through `universalAgentPackagingReceipts`, proves resumable full-audit orchestration through `fullAuditOrchestratorReceipts`, proves one-surface proof inspection through `unifiedInspectReceipts`, proves compact result blocks through `conciseVerdictResultUXReceipts`, proves public MarketplaceDeck readiness through `codexMarketplaceReadinessReceipts`, proves public-safe comparative benchmark lift through `externalBenchmarkV2Receipts`, proves v4 preview stabilization through `v4PreviewStabilizationReceipts`, proves v4 schema freeze through `v4SchemaFreezeReceipts`, proves v4 release-candidate readiness through `v4ReleaseCandidateReadinessReceipts`, and proves fixture-backed product-release stabilization through `v4ProductReleaseStabilizationReceipts`. Once those pass, it escalates to real stable-v4 publication proof instead of declaring v4 stable from synthetic receipts. The report itself also emits `resultUX` so the top of the Markdown and JSON answers status, verdict, proof source, why it matters, and the next command before the detailed ledger.
- `v4 preview`: run ShipGuard V4 Preview, the read-only product contract report for schema-freeze posture, security-review gates, migration plan, deprecation policy, and release-readiness proof before v4 packaging.
- `v4 schema-freeze`: run ShipGuard V4 Schema Freeze, the read-only schema contract report for the schema registry, compatibility policy, compatibility fixtures, migration checks, changelog policy, deprecation policy, and blocked release claims before v4 release-candidate work.
- `v4 release-candidate`: run ShipGuard V4 Release Candidate Readiness / LaunchKey, the read-only readiness report for fresh install, optional package-tarball install receipt, optional same-prefix upgrade receipt, optional rollback cleanup receipt, release proof consumption, optional native GitHub release-asset download or supplied downloaded release-asset consumer proof, external adoption evidence proof, security review evidence proof, generated archive-member screening, compact package-hygiene evidence for unsafe package blockers, blocking-proof result UX, external adoption packet, final schema docs, plugin refresh proof, and stable-v4 blocked claims. When report-quality is run on the candidate output directory, generated package install/work/consume/upgrade/rollback/download proof directories are skipped so only report artifacts are scored.
- `v4 stable-publication`: run ShipGuard V4 Stable Publication Proof, the read-only final publication gate for public GitHub release metadata, stable-v4 release notes, LaunchKey candidate packet proof, downloaded release assets, post-release consumer proof, public release freshness, release version coherence, release asset coherence, `publicEvidenceClosureProof`, independent adoption evidence, final security-review evidence, one machine-readable evidence packet, an ordered closure checklist for every remaining stable-v4 blocker, GitHub release metadata closure kit with repo inference, release tag, API endpoint, release state, required/missing assets, release-note digest, repair/pass/fail criteria, rerun command, and public-metadata/source-only/fixture-API boundaries, release-notes closure kit with missing-topic IDs and public-edit boundary, LaunchKey candidate closure kit with supplied candidate path, nested receipt, proof areas, package-hygiene diagnostics, repair/pass/fail criteria, nested and full rerun commands, release-asset closure kit with required assets, GitHub metadata/local missing assets, download source/status, repair/pass/fail criteria, rerun commands, and metadata-only/source-only/fixture-proof boundaries, post-release consumer closure kit with release-consume paths/statuses, missing proof artifacts, digest/replay/attestation crosschecks, repair/pass/fail criteria, direct release-consume and full stable-publication rerun commands, source-only and fixture-proof boundaries, public evidence closure with adoption/security gate status, freshness, starter paths, copy-ready commands, and non-claims, public release delta proof with local/latest/package/claim alignment, final claim packet with copy-ready allowed/blocked wording, evidence rows, first blocker, next command, and approval boundary, adoption/security closure kits with starter paths, required fields, privacy boundaries, pass/fail criteria, diagnostics, rerun commands, generated draft-only evidence/release-notes/launch-relay kits, draft-only evidence templates, blocked stable claims, and shareable result UX.
- `full-audit`: run ShipGuard Full Audit, the resumable release/product-QA orchestrator for validation, value-gauntlet, report-quality, package proof, install refresh, plugin status, CI proof, and release-proof preparation. Use `--plan-only` to see the lane without running it; plan-only output is `review`, not completed proof, and its result block points to the executable command with missing release metadata placeholders. Markdown includes an `Execution Commands` table built from `stages[].command` so the planned lane is copy-ready without opening JSON. Full Audit loads `slashPlan` and `slashGoal` from `NEXT_GOAL.md` and reports `slashHandoffSource` so stale hardcoded handoffs are visible. Use `--resume` to reuse existing stage receipts, `--profile quick|release|shipyard` to choose depth, and `--shareable` when report output will move outside the machine.
- `inspect`: run ShipGuard InspectDeck, the concise state surface that reads value-gauntlet, full-audit, Codex plugin status, release proof, repo state, and emits one verdict plus one next action without hiding underlying evidence.
- `pilot-bench`: run ShipGuard PilotBench, a read-only measurement report for verdict-quality traces gathered from external or synthetic pilot work. It scores public-safe traces for owner detection, acceptable and forbidden scope, required proof coverage, unsupported claim checking, redaction, exact next-action completeness, false-positive rate, and first useful verdict time. Add `--benchmark-v2` when traces include `baselineVerdict`; ShipGuard then emits `comparativeBenchmark` with ShipGuard score, baseline score, score lift, win rate, and quality gates. Use private-app traces only locally after shareable redaction; repeated weaknesses should become synthetic public traces under `fixtures/external-pilot-verdict-bench/` or `fixtures/external-benchmark-v2/`.
- `web audit`, `backend audit`, and `cli audit`: run ShipGuard WebScan, ServiceRadar, and CommandLens for non-iOS repos. These are read-only first audits that turn starter-profile installation into concrete target source/config/test signals, validation guidance, next commands, and report-quality questions instead of stopping at `init` and `doctor`. The reports list generated ShipGuard starter files separately and do not count them as target proof.
- `web plan`, `backend plan`, and `cli plan`: run ShipGuard WebForge, ServiceForge, and CommandForge for non-iOS audit reports. These are read-only fix-plan receipts that turn first-audit output into scoped tasks, validation commands, validation receipts, validation rerun receipts, stop conditions, and report-quality questions without authorizing target-app edits. Add `--target <repo>` to classify each validation lane as runnable, blocked, manual, or not checked without executing arbitrary target commands; blocked or unchecked lanes also get the smallest repair guidance and a shareable rerun command.
- `ios preview`: serve a local simulator screenshot preview for the Codex in-app browser.
- `ios devspace`: expose the preview bridge as a local MCP/App surface.
- `ios devspace-check`: statically grade ShipGuard Devspace connector readiness, public URL safety, widget metadata, handoff boundaries, and preview evidence without starting the server or grading a target app; add `--shareable` to omit local absolute paths before external sharing.
- `ios target-match`: rank visual preview events against XcodeBuildMCP UI snapshots.
- `ios codex-handoff`: prepare a guarded Codex app-server handoff.
- `ios plan --mode performance-audit`: route FPS, hitches, launch/scroll stutter, profiler fallback, and device-vs-simulator proof gaps.
- `ios launchdeck`: make ShipGuard the front door for the LaunchDeck surface. It inspects project/workspace/package/scheme topology, selects the right launch workflow, and emits XcodeBuildMCP build/run, simulator browser, SwiftUI preview hot reload, debugger, and performance-profiler handoff steps plus proof boundaries. Add `--receipt <file-or-dir>` after Codex executes the LaunchDeck route to grade whether build/run, UI, preview, log, or profiler proof is actually present. LaunchDeck owns routing and receipt grading; Codex iOS execution tools perform the simulator, preview, debugger, and profiler work.
- `ios performance`: run ShipGuard PulseRadar, scanning Swift source for ranked app-side performance hotspots before Codex edits; reports carry a `runtimeEvidenceBoundary` that labels source-only evidence as `source heuristic`, `confidence: medium`, `runtimeProof: missing`, and `blocking: no`, plus an `evidencePromotion` contract that names the first promotable source suspicion and one exact next action with owner, manual proof or command, expected artifact, success condition, and failure meaning. Findings include impact/why-it-matters explanations, high-severity reasons, local/manual proof boundaries, and grouped next actions for repeated rule clusters in JSON and Markdown. Add `--shareable` when performance reports will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring.
- `ios design`: run ShipGuard VibeCheck, auditing app-type-specific UI/UX coherence, motion, haptics, preview routing, and ImageGen app-icon handoff before visual work; it emits native `motionQualityGates` for frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance checks, a `designTailoring` contract that ties app type, source signals, guidance profile, tailored motion/haptics/visual-density/copy dimensions, and one exact next proof action together, plus `designCoherenceBoundary` so source inventory, coherence risks, ShipGuard next actions, app-work authorization, and proof boundaries do not collapse into target-app remediation. Add `--shareable` when design reports will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or report-quality scoring.
- iOS source scanners skip generated/proof/cache directories such as build output, release artifacts, scratch folders, web assets, and plugin/editor caches; reports include a scan-scope summary so private-app product QA stays auditable.
- `--shipguard-eval`: mark `ios launchdeck`, `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, or `ios ai-readiness` as ShipGuard product QA only, so findings improve ShipGuard rather than becoming target-app work; add `--shareable` before those reports move into report-quality scoring or external planning.
- `ios report-quality`: grade ShipGuard report usefulness across read-only product-QA outputs; it evaluates report structure, boundaries, proof guidance, scan scope, performance runtime-evidence boundaries, performance evidence-promotion next actions, design app-type tailoring contracts, design coherence boundaries, design preview/Devspace routing, prepare/verify quickstart replay, notification-permission `domainRiskPack.scopeRecommendations.authorized`, `reviewOnly`, `forbiddenUnlessExplicit`, permission-sensitive source signals, structured permission-state/denied-state receipt requirements, simulator denied-state versus physical-device prompt receipt boundaries, generic-log failure meanings, verify proof-lane status, physical-device prompt overclaiming, performance finding impact explanations, high-severity reasons, local/manual proof boundaries, repeated performance and Lean Deck grouping, Lean Debt trigger-watch contracts, grouped first experiments, declared shareability, token/path shareability, redaction handoff, aggregated actionability questions, fixture candidates, promotion manifests, existing fixture coverage, and a prioritized next action, not target-app quality. Add `--shipguard-eval` when the report-quality run itself is part of ShipGuard product QA, and add `--shareable` when the artifact will move into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence. Add `--write-fixture-candidates <dir>` to materialize generated fixture candidates as synthetic public starter files plus `fixture-promotion-manifest.json` and `PROMOTION.md`; already-materialized synthetic fixtures and questions covered by promoted public fixtures keep their evidence but do not generate recursive or duplicate fixture candidates, and materialized-root scoring consumes promotion manifests as metadata instead of grading them as reports.
- `ios modernize`: run ShipGuard UpgradeForge for Swift, SwiftUI, Observation, accessibility, localization, and availability risks; add `--shareable` before report-quality scoring or external sharing.
- `ios app-intelligence`: run ShipGuard SignalLens for App Intents, shortcuts, widgets, Spotlight, controls, and system exposure; add `--shareable` before report-quality scoring or external sharing.
- `ios ai-readiness`: run ShipGuard ModelDock to compare on-device, cloud, Core ML, and no-AI options before model work; add `--shareable` before report-quality scoring or external sharing.
- `ios external-audit`: run ShipGuard SourceScout to inspect external workflow checkouts or URLs as ShipGuard product inputs and emit a native replacement ledger with source inputs, capability matrix, implementation backlog, license boundary, and report-quality questions. Use this before saying Spec Kit, CodexPro, Ponytail, Expo, Design Motion Principles, X posts, or another repo has been "integrated"; adoption only counts when a capability has a ShipGuard-native action, validation command, and detected ShipGuard surface through `capabilityMatrix[].surfacePresent`. Add `--shareable` before report-quality scoring or external sharing.
- `ios spec-workflow`: run ShipGuard SpecForge to convert a feature idea or report-quality actionability questions into ShipGuard-owned constitution, spec, requirements checklist, native integration decisions, plan, tasks, consistency analysis, analysis gates, slash plan/goal, and Devspace guardrails; add `--from-report <report-quality-dir>` to ground adoption work in observed ShipGuard output, and add `--shareable` before report-quality scoring or external planning. Repeated report-quality questions are deduplicated before the clarifying-question and task caps. Report-quality verifies the declared spec-workflow files exist, are non-empty, preserve report-quality questions in clarifying questions, acceptance criteria, proof-gated tasks, checklist coverage, integration decisions, consistency analysis, exact validation commands, analysis gates, and copy-ready `/plan` plus `/goal` next-loop handoff text, and include expected headings, proof cues, replacement/evaluation decisions, and guardrails before the bundle passes.
- `ios redact`: run ShipGuard RedactionBay to redact local iOS reports before sharing.
- `ios eval`: run ShipGuard EvalArena deterministic behavior evals.
- `ios demo`: run the clean first-run iOS ShipGuard loop without Xcode, Simulator, credentials, or an API key.
- `ios goals`: run ShipGuard GoalEngine to emit and complete evidence-gated ShipGuard slash-goals; use `ios goals init --completed-through <goal-id> --completion-evidence <proof>` to bootstrap a loop from already-proven shipped work without replaying stale goals one by one.

See `ios-shipguard.md`, `ios-preview.md`, `shipguard-devspace.md`, and `shipguard-naming.md`.

## Score

Score a Codex run markdown file:

```bash
./bin/shipguard score examples/scored-run.md
```

The score file must include these categories:

- Scope control
- Owner-file accuracy
- Risk awareness
- Validation quality
- Handoff honesty
- Regression awareness

Each category should include a value from `0` to `2`.

## Autopsy

Generate Markdown and JSON evidence reports for an AI coding run:

```bash
./bin/shipguard autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

The command writes:

- `report.md`
- `report.json`

It checks the run score, validation claims, test evidence, diff size, high-assurance claims, and protected-area touches. High-severity findings produce a `do not merge until high-risk findings are resolved` verdict.

See `autopsy.md` for the full guide.

## Arena

Run a fixture pack through Autopsy and aggregate the results:

```bash
./bin/shipguard arena run \
  --fixture fixtures/arena \
  --out /tmp/arena
```

The command writes aggregate `results.json`, a readable `index.md`, and per-case autopsy reports under `runs/<case-id>/`.

See `arena.md` for the fixture format and metrics.

Import an external fixture pack before running it:

```bash
./bin/shipguard arena import \
  --source external-pack \
  --out /tmp/imported-arena-pack \
  --pack-name "external-pack"
```

The import command copies only supported fixture files, writes `PACK.md` with the source basename, rejects overlapping source/output directories, and blocks unsupported files, nested directories, symlinks, obvious local paths, or secret-looking values.

Sign and verify fixture-pack metadata:

```bash
./bin/shipguard arena sign \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-pack/PACK.json \
  --pack-name "external-pack" \
  --signer "Example Maintainers" \
  --signer-url "https://github.com/example/repo"

./bin/shipguard arena verify \
  --fixture /tmp/imported-arena-pack \
  --manifest /tmp/imported-arena-pack/PACK.json
```

The signature is a deterministic SHA-256 content digest for integrity checks. Optional signer metadata adds an `identity_digest` so edited signer fields fail `arena verify`; it is provenance metadata, not private-key signing.

Compare two Arena result files:

```bash
./bin/shipguard arena compare \
  --left /tmp/arena-old/results.json \
  --right /tmp/arena-new/results.json \
  --out /tmp/arena-compare
```

The command writes `arena-compare.json` and `arena-compare.md`. It reports score, case-count, high-risk, added-case, removed-case, and per-case deltas so benchmark changes are reviewable instead of implied by a new average.

## Transcript Redaction

Redact a maintainer transcript before publishing it as an example, benchmark note, or public proof:

```bash
./bin/shipguard transcript redact \
  --in raw-transcript.md \
  --out /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --private-term "InternalProjectName"
```

The command writes redacted Markdown and a JSON report. It redacts emails, token-like values, secret assignments, local user paths, long hex strings, bearer tokens, and custom private terms. See `transcript-redaction.md`.

Verify a redacted transcript and optional redaction report:

```bash
./bin/shipguard transcript verify \
  --in /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --out /tmp/transcript-verify
```

The command writes `transcript-verify.json`, `transcript-verify.md`, and `badge.json`. It exits non-zero when risky content remains.

Build a public-safe transcript corpus index:

```bash
./bin/shipguard transcript corpus \
  --source fixtures/transcripts \
  --out /tmp/transcript-corpus \
  --require-report true
```

The command writes `corpus.json`, `index.md`, `badge.json`, and per-case verification reports under `runs/`. It exits non-zero when any transcript verification is blocked or when `--require-report true` is set and a case is missing `redaction-report.json`. See `transcript-corpus.md`.

## Review Comment

Generate a PR-ready comment and Shields-compatible badge from an autopsy report:

```bash
./bin/shipguard review-comment \
  --report /tmp/autopsy/report.json \
  --out /tmp/review/comment.md \
  --badge /tmp/review/badge.json \
  --artifact-dir /tmp/review \
  --mode warn
```

Use `--mode fail` to exit non-zero when the report is blocked. See `pr-review-bot.md` for the GitHub Actions workflow shape.

## CI Gate

Run Autopsy, review-comment, badge generation, and gate JSON in one command:

```bash
./bin/shipguard ci-gate \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --policy .shipguard/policy.conf \
  --out artifacts/shipguard-gate \
  --mode warn
```

Use `--mode fail` when blocked gates should fail CI. See `ci-gate.md`.

## CI Summary

Generate GitHub Actions step-summary Markdown from `gate.json`:

```bash
./bin/shipguard ci-summary \
  --gate /tmp/codex-gate/gate.json \
  --out /tmp/codex-gate/summary.md
```

`ci-gate` writes `summary.md` automatically. See `ci-summary.md`.

## Check Run

Generate a GitHub Checks API payload from `gate.json`:

```bash
./bin/shipguard check-run \
  --gate /tmp/codex-gate/gate.json \
  --head-sha "$GITHUB_SHA" \
  --out /tmp/codex-gate/check-run/payload.json
```

Post the payload only when the workflow has an explicit token and `checks: write` permission:

```bash
./bin/shipguard check-run post \
  --payload /tmp/codex-gate/check-run/payload.json \
  --repo "$GITHUB_REPOSITORY" \
  --out /tmp/codex-gate/check-run/response.json
```

Use `--dry-run` to write the request metadata without contacting GitHub. The reusable CI gate action writes this payload into the artifact bundle and can post it when `post-check-run` is enabled. See `check-run.md`.

## SARIF

Convert an Autopsy report into SARIF 2.1.0:

```bash
./bin/shipguard sarif \
  --report /tmp/autopsy/report.json \
  --out /tmp/autopsy/results.sarif
```

`ci-gate` writes `sarif/results.sarif` automatically. See `sarif.md`.

## Docs Check

Check Markdown files for broken local links:

```bash
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
```

External URLs and in-page anchors are ignored. The command writes `docs-check.json` and `docs-check.md` when `--out` is provided. See `docs-check.md`.

## Codex Status

Check whether the local Codex plugin cache has a ShipGuard-related plugin install and whether it looks current:

```bash
./bin/shipguard codex status
```

Use `--cache` for fixture caches or non-default Codex plugin locations, and `--strict` when stale or missing installs should fail the command:

```bash
./bin/shipguard codex status --cache /tmp/codex-plugin-cache --strict
```

The command is read-only. It reports installed `ios-shipguard` plugin metadata, old repository URLs, old `Shipguard` casing, old `codex-maintainer` guidance, whether tracked plugin source exists in the checkout, whether a matching ShipGuard CLI resolves from the install or current package, and the exact refresh handoff for Git source, plugin cache, and new Codex threads. See `codex-status.md`.

## Codex Marketplace Readiness

Check whether the tracked Codex plugin source is adopter-ready before publishing, submitting, or sharing it:

```bash
./bin/shipguard codex marketplace-readiness \
  --path . \
  --out /tmp/shipguard-marketplace \
  --cache "$HOME/.codex/plugins/cache" \
  --strict \
  --shareable
```

The command is read-only. It checks plugin metadata, `.agents/plugins/marketplace.json`, README/profile presentation, icon assets, screenshot policy, strict `codex status` proof, privacy/model-choice boundaries, and a copy-ready submission packet. It does not install the plugin, create screenshots, upload assets, or submit to a marketplace. See `codex-marketplace-readiness.md`.

## Leaderboard

Build a stable public leaderboard JSON file from arena results:

```bash
./bin/shipguard leaderboard build \
  --arena-results /tmp/arena/results.json \
  --out /tmp/leaderboard.json
```

See `benchmark.md` for the schema and `demo-reports.md` for checked-in generated examples.

## Release Manifest

Generate release proof files for a tarball:

```bash
./bin/shipguard release-manifest \
  --tarball dist/shipguard-v3.131.0.tar.gz \
  --out /tmp/shipguard-release-proof
```

Verify the manifest against the tarball:

```bash
./bin/shipguard release-manifest verify \
  --manifest /tmp/shipguard-release-proof/release-manifest.json \
  --tarball dist/shipguard-v3.131.0.tar.gz
```

The command writes `release-manifest.json` and `proof-ledger.md`. Add `--ci-run-url`, `--release-url`, and `--issue-url` after publishing to bind the local artifact digest to public release proof. See `release-manifest.md`.

Build a release proof catalog from manifests:

```bash
./bin/shipguard release-index build \
  --manifest dist/release-proof-v3.5.0/release-manifest.json \
  --manifest dist/release-proof-v3.131.0/release-manifest.json \
  --out /tmp/shipguard-release-index
```

The command writes `release-index.json` and `release-index.md`. See `release-index.md`.

Replay-verify downloaded release assets:

```bash
./bin/shipguard release-replay verify \
  --manifest /tmp/shipguard-release-proof/release-manifest.json \
  --tarball /tmp/shipguard-release-assets/shipguard-v3.131.0.tar.gz \
  --index /tmp/shipguard-release-index/release-index.json \
  --ledger /tmp/shipguard-release-proof/proof-ledger.md \
  --out /tmp/shipguard-release-replay
```

The command writes `replay-report.json` and `replay-report.md`. See `release-replay.md`.

Build a compact release attestation:

```bash
./bin/shipguard release-attest build \
  --manifest /tmp/shipguard-release-proof/release-manifest.json \
  --replay /tmp/shipguard-release-replay/replay-report.json \
  --out /tmp/shipguard-release-attestation
```

The command writes `attestation.json`, `attestation.md`, and `attestation-badge.json`. See `release-attest.md`.

Build the full release proof bundle in one command:

```bash
./bin/shipguard release-proof build \
  --out /tmp/shipguard-release-proof-bundle \
  --release-url https://github.com/owner/repo/releases/tag/v3.131.0
```

The command writes the release tarball, manifest, release index, replay report, attestation, and attestation badge. See `release-proof.md`.

## Release Consume

Verify a flat directory of downloaded release assets and write a consumer report:

```bash
./bin/shipguard release-consume verify \
  --dir /tmp/shipguard-v3.131.0 \
  --out /tmp/shipguard-v3.131.0/consumer-proof \
  --version 3.131.0
```

The command writes `consumer-report.json`, `consumer-report.md`, `asset-digests.json`, `asset-digests.md`, `sha256.txt`, replay outputs, and attestation outputs. It also cross-checks downloaded replay, attestation, and badge assets when they are present. Use `actions/release-consume` when this verification should run in GitHub Actions. See `release-consume.md` and `release-consume-action.md`.

## Release Diff

Compare two release proof asset directories and write JSON/Markdown diff reports:

```bash
./bin/shipguard release-diff compare \
  --left /tmp/shipguard-old \
  --right /tmp/shipguard-v3.131.0 \
  --out /tmp/shipguard-release-diff
```

The command accepts flat GitHub release downloads or nested `release-proof build` output. It compares release tarballs, manifests, indexes, ledgers, replay reports, attestations, and badges. Use `actions/release-diff` when this comparison should run in GitHub Actions. See `release-diff.md` and `release-diff-action.md`.

## Release Evidence

Export release proof reports as a static evidence page:

```bash
./bin/shipguard release-evidence site \
  --consume /tmp/shipguard-v3.131.0/consumer-proof \
  --diff /tmp/shipguard-release-diff \
  --out /tmp/shipguard-release-site
```

The command writes `index.html`, `evidence.json`, `README.md`, and source JSON copies under `sources/`. Use `actions/release-evidence` when this export should run in GitHub Actions. See `release-evidence-site.md` and `release-evidence-action.md`.

Build a static index from one or more evidence site exports:

```bash
./bin/shipguard release-evidence index \
  --site /tmp/shipguard-previous-site \
  --site /tmp/shipguard-v3.131.0-site \
  --out /tmp/shipguard-release-history
```

The command writes `index.html`, `evidence-index.json`, `README.md`, and copied site exports under `sites/`. Use `actions/release-evidence` with `build-index: true` when this index should run in GitHub Actions. See `release-evidence-index.md` and `release-evidence-action.md`.

Build the full local evidence path from downloaded release assets:

```bash
./bin/shipguard release-evidence bundle \
  --assets /tmp/shipguard-v3.131.0 \
  --left /tmp/shipguard-old \
  --out /tmp/shipguard-release-evidence-bundle \
  --version 3.131.0 \
  --title "ShipGuard v3.131.0 Evidence"
```

The command writes consumer proof, optional release-diff proof, `site/index.html`, `index/evidence-index.json`, `bundle.json`, and `README.md`. See `release-evidence-bundle.md`.

Verify a downloaded release evidence artifact:

```bash
./bin/shipguard release-evidence verify \
  --dir /tmp/shipguard-release-evidence \
  --out /tmp/shipguard-release-evidence-verify \
  --require-diff true \
  --require-index true
```

The command writes `evidence-verify.json`, `evidence-verify.md`, and `badge.json`. It checks the static evidence site, copied source reports, optional evidence index, and optional `bundle.json` for consistency. Use `actions/release-evidence-verify` when this consumption proof should run in GitHub Actions. See `release-evidence-verify.md`.

Run the checked-in negative fixture pack as a single guardrail index:

```bash
./bin/shipguard release-evidence negative-index \
  --fixture fixtures/release-evidence/negative \
  --out /tmp/shipguard-negative-evidence
```

The command reads `cases.tsv`, runs each intentionally broken fixture through `release-evidence verify`, and writes `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, and per-case verifier outputs under `runs/<case>/`. It exits successfully only when every case blocks on the expected failed check.

Use `actions/release-evidence-negative-index` when this guardrail index should run in GitHub Actions. See `release-evidence-negative-index-action.md`.

## Release Proof Consumption

Download a published release bundle, verify the tarball digest, replay the proof, and rebuild the compact attestation:

```bash
gh release download v3.131.0 \
  --repo jlekerli-source/ShipGuard \
  --pattern 'shipguard-v3.131.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --pattern 'attestation-badge.json' \
  --dir /tmp/shipguard-v3.131.0

shasum -a 256 /tmp/shipguard-v3.131.0/shipguard-v3.131.0.tar.gz

./bin/shipguard release-replay verify \
  --manifest /tmp/shipguard-v3.131.0/release-manifest.json \
  --tarball /tmp/shipguard-v3.131.0/shipguard-v3.131.0.tar.gz \
  --index /tmp/shipguard-v3.131.0/release-index.json \
  --ledger /tmp/shipguard-v3.131.0/proof-ledger.md \
  --out /tmp/shipguard-v3.131.0/consumer-replay

./bin/shipguard release-attest build \
  --manifest /tmp/shipguard-v3.131.0/release-manifest.json \
  --replay /tmp/shipguard-v3.131.0/consumer-replay/replay-report.json \
  --out /tmp/shipguard-v3.131.0/consumer-attestation
```

See `release-proof-consumption.md` for the rejection rules and trust model.

## Self-Audit

Generate release-readiness proof for the toolkit itself:

```bash
./bin/shipguard self-audit --out /tmp/shipguard-self-audit
```

The command writes:

- `self-audit.md`
- `self-audit.json`

It checks stable command availability and the core artifacts that make the Maintainer Reliability OS useful: policy config, CI gate action, review-comment action, demo leaderboard, and demo arena results.

See `maintainer-reliability-os.md`, `command-matrix.md`, and `release-checklist.md`.

## Next Goal

Generate slash-plan and slash-goal guidance for the next release:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```

Override the target release and title when the next improvement is already known:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "SARIF Evidence Export" \
  --out /tmp/next-goal.md
```

When the scope is already chosen, include it in the generated `/plan` and `/goal`:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "Scoped Goal Handoff" \
  --scope "Make next-goal emit scoped plans and completion receipts." \
  --out /tmp/scoped-next-goal.md
```

After the slice is complete, add caller-supplied proof evidence and the title for the following goal:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "Scoped Goal Handoff" \
  --scope "Make next-goal emit scoped plans and completion receipts." \
  --completion-evidence "./tests/next_goal_test.sh and ./tests/package_release_test.sh passed" \
  --following-title "Next Reliability Slice" \
  --out NEXT_GOAL.md
```

The command writes a Markdown plan with `/plan` and `/goal` blocks, a version lineage check that separates the current pre-bump `VERSION` package artifact from the expected post-bump release artifact and warns when a planned release skips the next semantic target, optional bounded scope and completion receipt sections, release constraints, Brand Deck strict proof for public surface naming changes, proof commands, publishing checks, and the command to generate the following goal. See `next-goal.md`.

## Install From Release Tarball

Download and extract a release package:

```bash
tar -xzf shipguard-v3.131.0.tar.gz
cd shipguard-v3.131.0
PREFIX="$HOME/.local" ./scripts/install.sh
```

The installer copies toolkit files into `${PREFIX:-/usr/local}/lib/shipguard` and writes a `shipguard` wrapper into `${PREFIX:-/usr/local}/bin`.

## Package Contents

Release packages include the CLI, compatibility wrappers, scripts, skills, templates, examples, demo fixtures, docs, scorecard, planning templates, and license. They exclude `.git`, `dist`, generated caches, and local machine paths.

See `compatibility.md` for the legacy wrapper policy.
