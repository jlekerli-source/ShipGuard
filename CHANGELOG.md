# Changelog

## Unreleased

- Fixed the next self-QA priority after stable release fixture proof: `shipguard value-gauntlet` now emits a live report-quality question from `lowestValueSurfaceProbe.answer`, and `ios report-quality` injects the same stable-v4 publication question even when grading older reports that still carry stale product-stabilization wording.
- Added Tool Value Gauntlet `v4ProductReleaseStabilizationReceipts`: public fixtures now build ShipGuard release proof, derive a previous package, assemble downloaded release assets, run LaunchKey with fresh-install/upgrade/rollback/release-consume/adoption/security evidence, and hand the result to report-quality. Once this fixture-backed path passes, the lowest-value probe escalates to real stable-v4 publication proof instead of claiming stable v4 from synthetic receipts.
- Fixed mixed report-quality prioritization for release hardening: `ios report-quality` now lets Value Gauntlet lowest-value and LaunchKey release-readiness signals outrank generic non-blocked Full Audit plan questions, while blocked source reports still stay first.
- Added copy-ready Full Audit execution receipts: `shipguard full-audit` Markdown now renders an `Execution Commands` table from `stages[].command`, and `ios report-quality` flags Full Audit reports that hide planned stage commands from the human-readable report.
- Fixed Full Audit slash-handoff drift: `shipguard full-audit` now sources `slashPlan` and `slashGoal` from `NEXT_GOAL.md`, renders `slashHandoffSource`, and `ios report-quality` flags stale or untracked Full Audit handoffs such as the old v3.132 placeholder.
- Tightened Full Audit release-packet honesty: `shipguard full-audit --plan-only` now reports `review` instead of `pass`, preserves the exact selected profile or stages in `resultUX.nextCommand`, and adds missing release metadata placeholders so planned proof cannot be mistaken for executed proof.
- Added LaunchKey final security-review evidence gate: `shipguard v4 release-candidate --security-review-evidence <json-or-dir>` now validates redacted security review evidence records, requires CLI/plugin/GitHub Actions/release-proof/package-install/redaction-privacy scope coverage, blocks open critical/high findings, separates synthetic fixtures from stable-v4 eligible review evidence, and turns missing final security proof into a concrete next command.
- Added LaunchKey external adoption evidence gate: `shipguard v4 release-candidate --external-adoption-evidence <json-or-dir>` now validates redacted independent adoption evidence records, separates structurally valid fixture evidence from stable-v4 eligible evidence, and turns missing adoption proof into a concrete next command without faking adoption.
- Added LaunchKey native GitHub release-asset download: `shipguard v4 release-candidate --download-release-assets --github-release-repo <owner/repo>` now downloads release assets from GitHub into a local proof directory, runs `release-consume verify`, records `githubReleaseAssetDownloadProof`, and keeps `downloaded-release-assets` out of recursive report-quality scoring.
- Added LaunchKey downloaded-asset blocking proof detail: `shipguard v4 release-candidate` now rejects generated archive members such as AppleDouble `._*`, `.DS_Store`, `__MACOSX`, bytecode, and cache paths before install, and result UX now names the exact blocked receipt plus the next package-rebuild command when supplied release/package proof fails.
- Added LaunchKey upgrade and rollback receipt attachment: `shipguard v4 release-candidate` can now accept `--upgrade-from-tarball`, prove same-prefix upgrade from a previous package to the candidate package, attach rollback cleanup proof from the candidate package, and keep generated upgrade/rollback proof directories out of recursive report-quality scoring.
- Fixed `ios report-quality` recursive scoring for LaunchKey package-proof outputs. Report-quality now skips generated `fresh-install-prefix`, `fresh-install-work`, and `release-consume` directories under a report output so v4 candidate QA grades the root LaunchKey report instead of the embedded installed ShipGuard package or consumer-proof receipts.
- Refined GitHub-facing presentation for the current post-`v3.131.0` state: README, docs index, GitHub Presentation, and roadmap now distinguish the published LaunchKey release from active `main` hardening, and the recommended About copy is app-maintenance oriented instead of iOS-only.
- Added LaunchKey fresh-install receipt attachment: `shipguard v4 release-candidate` now accepts `--package-tarball`, `--fresh-install-prefix`, and `--fresh-install-work-dir`, installs the package into a fresh prefix, checks both CLI aliases, runs installed `shipguard validate`, and records `freshInstallPackageProof`.
- Hardened package/install hygiene after fresh-install proof exposed macOS AppleDouble sidecars during package install. `package_release.sh` and `install.sh` now disable/cull `._*` files, and package release tests require installed `shipguard validate` to pass.
- Added LaunchKey published release-asset proof attachment: `shipguard v4 release-candidate` now accepts `--release-assets`, `--release-version`, and `--release-consume-out`, runs `shipguard release-consume verify`, and records `publishedReleaseAssetProof` so stable-v4 release asset proof is attached to the v4 candidate report instead of living only as a separate manual instruction.
- Fixed InspectDeck result UX after read-only ShipGuard self-QA showed Value Gauntlet prose proof guidance could be copied into `resultUX.nextCommand`. InspectDeck now keeps prose in the action summary/reason and falls back to a runnable value-gauntlet command template.
- Improved InspectDeck next-action ordering after read-only ShipGuard self-QA showed bare `shipguard inspect` runs jumped straight to release-proof build while value-gauntlet and full-audit receipts were also missing. InspectDeck now asks for the missing value-gauntlet receipt first, then full-audit, then release proof.
- Refreshed GitHub-facing presentation docs for the latest published `v3.131.0` capabilities: README/current-state wording, GitHub About/sidebar copy, social-preview/icon guidance, release-page copy, docs index routing, roadmap baseline wording, and release-package demo commands. Removed the unused JPG social-preview mock so the tracked icon stays the presentation source of truth.
- Added `ios report-quality` coverage for source report `resultUX.nextCommand` fields so report families that put prose in the command slot receive `result-ux-next-command-not-command`, and fixed `shipguard value-gauntlet` to emit an executable rerun command while keeping product-release guidance in `nextActionSummary`.
- Tightened `ios report-quality` result UX after read-only self-QA showed the Markdown `Next command` could be a prose actionability question with nested backticks. `resultUX.nextCommand` now emits a command-shaped ShipGuard template, while `nextActionSummary` keeps the human priority question or finding summary.
- Fixed `ios report-quality --shareable` scoring for ShipGuard root report bundles: `shipguard full-audit`, `shipguard inspect`, `shipguard codex marketplace-readiness`, and trace reports are now first-class report tools, and full-audit `stage-receipts/*.json` are treated as internal evidence instead of standalone reports that cause false `report-tool-missing` blocks.
- Extended bounded iOS source scanning to the remaining read-only product-QA report families exposed by the next Ringly/Ilmify loop: `ios launchdeck` now budgets SwiftUI preview-signal reads, `ios app-intelligence` budgets App Intents/system-surface scans, and `ios ai-readiness` budgets AI token scans, all with JSON/Markdown sampled/omitted/timed-out text evidence. `ios launchdeck --shipguard-eval --shareable` now also redacts private target identifiers before report-quality scoring.
- Hardened iOS read-only source scanning after large Ringly/Ilmify product-QA inputs exposed slow unbounded text reads: `ios doctor`, `ios performance`, `ios design`, and `ios modernize` now use a shared per-file text budget plus per-file read timeout, report truncated/omitted/timed-out text files in JSON/Markdown, and have a public `ios_scan_scope_budget_test.sh` regression fixture.
- Added v3.131 ShipGuard V4 Release Candidate Readiness / LaunchKey: `shipguard v4 release-candidate` now emits install, upgrade, uninstall, release proof consumption, external adoption packet, final schema docs, plugin refresh proof, blocked claims, scope boundary, report-quality questions, and result UX without claiming a stable v4 product release.
- Added Tool Value Gauntlet `v4ReleaseCandidateReadinessReceipts` with public candidate-contract fixtures; once those pass, the lowest-value probe points to v4 product release stabilization instead of repeatedly asking for release-candidate proof.
- Added docs, CLI help, self-audit, package proof, report-quality root-report support, plugin guidance, smoke coverage, and package execution for the release-candidate surface so installability and consumer proof are executable gates rather than roadmap prose.
- Added v3.130 ShipGuard V4 Schema Freeze: `shipguard v4 schema-freeze` now emits a schema registry, compatibility policy, compatibility fixtures, migration checks, changelog policy, deprecation policy, release-readiness commands, blocked claims, scope boundary, report-quality questions, and result UX without claiming the v4 product is released.
- Added Tool Value Gauntlet `v4SchemaFreezeReceipts` with public schema-contract fixtures; once those pass, the lowest-value probe now points to v4 release-candidate readiness instead of repeatedly asking for schema-freeze proof.
- Added docs, CLI help, self-audit, package proof, report-quality root-report support, and smoke coverage for the schema-freeze surface so v4 compatibility is executable proof rather than roadmap prose.
- Added v3.129 ShipGuard V4 Preview: `shipguard v4 preview` now emits a release-readiness, schema-freeze, security-review, migration, deprecation, and blocked-claims report for capabilities that are stabilizing but not yet released.
- Added Tool Value Gauntlet `v4PreviewStabilizationReceipts` with public preview-contract fixtures; once those pass, the lowest-value probe now points to v4 schema-freeze compatibility work instead of repeatedly asking for preview stabilization.
- Added shared result UX to `shipguard ios report-quality` so gauntlet self-review has the same concise verdict and exact next command pattern as InspectDeck and other major reports.
- Added v3.128 External Benchmark v2: `shipguard pilot-bench --benchmark-v2` now compares ShipGuard verdict usefulness against `baselineVerdict` output on public-safe traces, records score lift and win rate, and gates the comparison with quality checks.
- Added Tool Value Gauntlet `externalBenchmarkV2Receipts` with public comparative verdict fixtures; once those pass, the lowest-value probe now points to v4 preview stabilization.
- Added v3.127 Codex marketplace readiness: `shipguard codex marketplace-readiness` audits public plugin metadata, local marketplace source, README/profile presentation, icon assets, screenshot honesty, strict status proof, privacy/model-choice boundaries, and a copy-ready submission packet.
- Added Tool Value Gauntlet `codexMarketplaceReadinessReceipts` with public MarketplaceDeck fixtures; once those pass, the lowest-value probe now points to v3.128 External Benchmark v2.
- Added v3.126 concise result UX: major reports now emit a shared `resultUX` object and Markdown `## Result` block with normalized status, verdict, proof source, why it matters, and one next command before detailed evidence.
- Added `scripts/shipguard_result.py` and wired result UX through `shipguard value-gauntlet`, `shipguard full-audit`, `shipguard inspect`, `shipguard ios design`, and `shipguard ios performance` while preserving existing report fields for compatibility.
- Added Tool Value Gauntlet `conciseVerdictResultUXReceipts` with public result-contract fixtures; once those pass, the lowest-value probe now points to v3.127 Codex marketplace readiness.
- Added v3.125 unified inspect experience: `shipguard inspect` now reads repo state, value-gauntlet output, full-audit output, local Codex plugin state, release proof state, and returns one concise verdict plus one exact next action without hiding underlying evidence.
- Added Tool Value Gauntlet `unifiedInspectReceipts` with public synthetic proof-state fixtures; once those pass, the lowest-value probe now points to v3.126 concise verdict and result UX.
- Added `docs/inspect.md`, focused inspect tests, CLI/docs/package/self-audit coverage, and shareable redaction for InspectDeck so proof-state review can happen without editing private target apps.
- Added v3.124 full-audit orchestration: `shipguard full-audit` now plans and runs the ShipYard proof lane with resumable stage receipts, slow-lane summaries, shareable redaction, stage filtering, `--resume`, `--plan-only`, and `quick|release|shipyard` profiles.
- Added Tool Value Gauntlet `fullAuditOrchestratorReceipts` with public plan-only, mini-execution, and resume-reuse proof; once those pass, the lowest-value probe now points to the v3.125 unified inspect experience.
- Added docs, CLI help, self-audit, package proof, and smoke coverage for the full-audit surface so release/product-QA work can use one orchestrator instead of a long manual command ceremony.
- Added v3.123 universal agent packaging: `shipguard agent trace` now supports `--adapter claude|gemini|cursor|mcp|generic` alongside Codex while keeping one TraceBridge schema for prompts, tool calls, receipts, verdicts, next actions, budgets, and proof handoffs.
- Added `adapterPackaging` output and an Agent Packaging Markdown section with source signals, shared schema expectations, handoff commands, and export guidance for non-Codex traces.
- Added Tool Value Gauntlet `universalAgentPackagingReceipts` with public synthetic Claude, Gemini, Cursor, MCP, and auto-detection fixtures; once those pass, the lowest-value probe now points to the v3.124 efficient full-audit orchestrator.
- Added the v3.122 Expo MCP and EAS assurance adapter: `shipguard agent trace` and `shipguard codex trace` now accept `--expo-eas-evidence <file-or-dir>` and attach Expo MCP routing, Expo project metadata, prebuild, EAS build/update, native runtime, artifact-integrity, and credential-boundary proof to the same TraceBridge task timeline.
- Added Tool Value Gauntlet `expoEASAssuranceReceipts` with a public synthetic fixture proving agent and Codex trace aliases attach typed Expo/EAS evidence while keeping EAS assurance separate from TestFlight, store, physical-device, and production-rollout proof.
- Advanced `shipguard value-gauntlet` beyond the v3.122 gap: once Expo/EAS assurance receipts pass, the lowest-value probe now points to v3.123 Claude, Gemini, Cursor, and generic MCP packaging.
- Added the v3.121 XcodeBuildMCP evidence adapter: `shipguard agent trace` and `shipguard codex trace` now accept `--xcodebuildmcp-evidence <file-or-dir>` and attach simulator build/run, UI snapshot, screenshot, runtime log, and profiler proof to the same TraceBridge task timeline.
- Added Tool Value Gauntlet `xcodeBuildMCPEvidenceReceipts` with a public synthetic fixture proving agent and Codex trace aliases attach typed XcodeBuildMCP evidence while keeping physical-device proof separate from simulator proof.
- Advanced `shipguard value-gauntlet` beyond the v3.121 gap: once XcodeBuildMCP receipts pass, the lowest-value probe now points to the v3.122 Expo MCP and EAS assurance adapter.
- Added ShipGuard TraceBridge: `shipguard agent trace` and `shipguard codex trace` now normalize exported/synthetic agent traces into prompt, tool-call, receipt, optional verify verdict, next-action, runtime-receipt, and worker-budget timelines.
- Added `scripts/agent_trace.py`, `docs/agent-trace.md`, focused `tests/agent_trace_test.sh`, and Tool Value Gauntlet `agentAdapterReceipts` proving prepare, trace-with-verify, over-budget blocking, and Codex alias behavior on public synthetic fixtures.
- Advanced `shipguard value-gauntlet` beyond the v3.120 gap: once agent adapter receipts pass, the lowest-value probe now points to the v3.121 XcodeBuildMCP evidence adapter.
- Added Structured Evidence Receipts v2: `scripts/shipguard_receipts.py` now normalizes current v2 validation receipts, legacy receipts, unsupported schema versions, artifact-only evidence, missing artifacts, digest/byte mismatches, stale receipts, and downgraded manual/runtime proof into one shared `evidenceReceiptSchema`.
- Updated `shipguard verify` so `shipguard-verdict.json` and `diffFirstAnalysis` expose v2, legacy, invalid, stale, downgraded, structured-proof, artifact-only, and missing receipt counts while keeping manual/runtime proof from silently satisfying automated validation.
- Added `tests/structured_evidence_receipts_test.sh` and Tool Value Gauntlet `structuredEvidenceReceipts` proving v2 pass, legacy-compatible pass, unsupported schema blocking, manual proof downgrade-to-review, and stale receipt blocking on public synthetic fixtures.
- Advanced `shipguard value-gauntlet` beyond the v3.119 gap: once structured evidence receipts pass, the lowest-value probe now points to the v3.120 Agent Adapter Kernel / Codex-native task and trace adapter.
- Added configuration baselines and suppressions to the proof-gated task contract: `shipguard prepare` now records `.shipguard.yml` / `.shipguard-baseline.json`, and `shipguard verify` emits `configurationBaseline`, exact finding fingerprints, accepted findings, expired/invalid suppressions, unmatched suppressions, and raw/effective scope checks.
- Added `scripts/shipguard_baseline.py`, focused `tests/configuration_baseline_test.sh`, and Tool Value Gauntlet `configurationBaselineReceipts` proving exact accepted findings can pass, expired suppressions block, and new protected-file regressions are not hidden by old waivers.
- Advanced `shipguard value-gauntlet` beyond the v3.118 gap: once configuration-baseline receipts pass, the lowest-value probe points to v3.119 structured evidence receipts v2.
- Extracted the Domain Pack SDK core for `shipguard prepare` / `shipguard verify`: `scripts/task_domain_packs.py` now exposes `DomainPackRegistry`, `domainPackSDK` metadata, pack-specific result fields, and a public synthetic fixture pack that proves new packs can register prepare/verify hooks without editing the generic verdict engine.
- Added Domain Pack SDK focused tests and Tool Value Gauntlet receipts; once synthetic pack receipts pass, the lowest-value probe now advances to configuration baselines and suppressions instead of reporting the SDK as missing.
- Added shared ShipGuard-eval shareable redaction via `scripts/ios_shareable.py` and tightened `shipguard ios report-quality --shareable` so read-only Ringly/Ilmify product-QA evidence cannot leak private app names, local paths, or target identifiers into packaged reports.
- Added `shipguard pilot-bench` / ShipGuard PilotBench as the v3.116 evidence release: public-safe task traces now score owner detection, acceptable and forbidden scope, proof coverage, unsupported-claim rejection, redaction, false-positive risk, exact next-action completeness, and first useful verdict time.
- Added public PilotBench trace fixtures and Tool Value Gauntlet receipts so external/read-only product-QA evidence is tested through reusable synthetic traces instead of private Ringly or Ilmify app details.
- Tightened `shipguard value-gauntlet` so passing PilotBench receipts advance the next weak surface to Domain Pack SDK core extraction instead of declaring the ShipYard finished.
- Fixed `shipguard prepare` metadata and `shipguard ios report-quality` root-tool detection after read-only product-QA showed task contracts were being misclassified as generic/metadata-poor reports.
- Added the first iOS domain risk pack on top of `shipguard prepare` / `shipguard verify`: notification, permission, authorization, denied-state, and provisional-flow goals now emit `domainRiskPack.id = ios-notification-permission-workflow` with scope recommendations, receipt requirements, simulator proof boundaries, and physical-device prompt boundaries.
- Tightened task-contract verification for iOS notification-permission work: a generic structured `swift test` receipt can cover the command but still returns `review` until the evidence proves permission-state, denied-state, not-determined-state, and simulator permission-reset lanes; local passes now explicitly report when physical-device prompt proof remains manual-required.
- Introduced `scripts/task_domain_packs.py` as the first domain-pack boundary: the notification-permission workflow now plugs into the generic task contract through `DomainPackContext` instead of embedding all domain logic directly in `scripts/task_contract.py`.
- Bumped the release line to v3.114.1 so latest release artifacts include the neutral starter planning templates under `templates/common/`, the `shipguard init` copy fix for `PLANS.md` and `SUBAGENTS.md`, and explicit `shipguard next-goal --completed-scope` support for release-loop handoffs.
- Added public `fixtures/ios-report-quality/design-coherence-boundary` coverage after read-only product-QA showed the next uncovered design question was boundary separation: `shipguard ios design` reports now expose `designCoherenceBoundary` with separate source inventory, coherence risks, ShipGuard next action, app-work authorization, proof boundary, and `targetRemediationStatus: not-authorized-from-this-run`.
- Tightened `shipguard ios report-quality` so ShipGuard-evaluation design reports missing the coherence boundary, separation checks, ShipGuard-owned next action, app-work authorization status, proof boundary, or Markdown rendering receive review findings; regenerated read-only Ringly/Ilmify product-QA output now has fixture coverage for runtime boundary, grouped performance, evidence promotion, app-type tailoring, and design coherence boundaries.
- Added public `fixtures/ios-report-quality/design-app-type-tailoring` coverage after read-only product-QA showed the next uncovered design question was app-type tailoring: `shipguard ios design` reports now expose a machine-readable `designTailoring` contract with source signals, guidance profile, tailored motion/haptics/visual-density/copy dimensions, and one exact next proof action.
- Tightened `shipguard ios report-quality` so design reports missing the app-type tailoring contract, source signals, tailored dimensions, Markdown rendering, or next-action proof fields receive review findings; regenerated read-only Ringly/Ilmify product-QA output now has fixture coverage for runtime boundary, grouped performance, evidence promotion, and design app-type tailoring, moving the next priority to design-system coherence boundary separation.
- Added public `fixtures/ios-report-quality/performance-evidence-promotion` coverage after read-only product-QA showed the next uncovered performance question was promotion evidence: source-only suspicions now need a machine-readable next action before they become broader work.
- Added `evidencePromotion` to `shipguard ios performance` JSON and Markdown: reports now name source evidence, promotion status, first candidate rule, required proof, and one exact next action with owner, manual proof, expected artifact, success condition, and failure meaning.
- Tightened `shipguard ios report-quality` so non-pass performance reports missing the evidence-promotion next-action contract receive review findings; regenerated read-only Ringly/Ilmify product-QA output now has fixture coverage for runtime boundary, grouped performance, and evidence promotion, moving the next priority to design app-type tailoring.
- Added public `fixtures/ios-report-quality/grouped-performance-observation` coverage after read-only product-QA showed grouped performance fixture candidates were too generic; the fixture uses synthetic `swiftui-repeat-forever-animation` findings and keeps private app evidence out of public files.
- Upgraded `shipguard ios report-quality --write-fixture-candidates` so generated `ios-performance-report-quality-fixture` reports include repeated synthetic findings, `ruleSummary`, `groupedActionPlan`, `firstExperiment`, `validationRoute`, `stopCondition`, Markdown `Grouped Next Actions`, and split local/manual proof boundaries before promotion.
- Regenerated the read-only performance/design product-QA loop and proved fixture coverage now suppresses both runtime-boundary and grouped-performance questions, moving the next uncovered priority to performance evidence promotion.
- Added the `runtimeEvidenceBoundary` contract to `shipguard ios performance`: source-only performance reports now state `evidence: source heuristic`, `confidence: medium`, `runtimeProof: missing`, and `blocking: no` in JSON and Markdown so PulseRadar cannot imply CPU/GPU/FPS proof without a matching trace or physical-device evidence.
- Tightened `shipguard ios report-quality` so performance reports missing that runtime-proof boundary receive a review finding, promoted a public `fixtures/ios-report-quality/performance-runtime-boundary` fixture for the repeated read-only product-QA boundary question, and proved regenerated Ringly/Ilmify read-only reports score 100/100 while moving the next uncovered priority to grouped performance fixture work.
- Upgraded `shipguard ios doctor` / ShipGuard DockCheck after read-only Ringly and Ilmify product-QA: doctor reports now emit `schemaVersion`, `generatedAt`, privacy-safe `<target-repo>` roots, target metadata, and structured finding fields (`ruleId`, `evidence`, `recommendation`, `proofGuidance`) so `ios report-quality --shareable` can grade DockCheck output at 100/100 without leaking local paths.
- Upgraded the proof-gated task contract core: `shipguard prepare` now uses bounded project snapshots, generic discovered iOS scope, and runnable validation discovery instead of private-app defaults or placeholder commands; `shipguard verify` now emits `diffFirstAnalysis`, structured validation coverage, evidence coverage, claim decisions, merge verdict, and next-action priority.
- Tightened `taskContractReceipts` in `shipguard value-gauntlet`: the public receipt now proves prepare/verify pass a scoped diff only with a structured validation receipt, treats a plain log as review context, blocks invalid receipts where the command failed despite "passed" text, blocks protected/out-of-scope diffs plus unsupported "fully verified" claims, and advances the lowest-value probe to the iOS notification and permission workflow.
- Added `docs/task-contract.md`, direct task-contract tests, package/self-audit coverage, and roadmap updates that center ShipGuard on the proof-gated Codex change loop before broader iOS packs or multi-stack expansion.
- Added `trustHardeningReceipts` to `shipguard value-gauntlet`: the public receipt fixture now proves composite GitHub Actions do not interpolate raw inputs inside shell bodies, Devspace blocks token-bearing public URLs, unsafe archive extraction is rejected, and release provenance rejects bad or mismatched release URLs. With those receipts green, the lowest-value probe now advances to the persistent proof-gated task contract.
- Added `docs/product-strategy.md` from the 5.5 Pro roadmap critique: ShipGuard's product center is now the proof-gated Codex change loop with a persistent task object, `prepare`/`verify` direction, iOS notification/permission wedge, trust-hardening priority, and a narrower public-command expansion rule.
- Packaged `NEXT_GOAL.md` and added it to validation/self-audit proof so extracted release packages preserve the same value-gauntlet doc surface as the source checkout.
- Added `commandFamilyRuntimeOutputReceipts` to `shipguard value-gauntlet`: a public major-family receipt now runs Brand Deck, DockCheck, VibeCheck, WebScan, WebForge, LinkSweep, and ManifestForge against public/synthetic inputs, verifies useful JSON/Markdown artifacts beyond `--help`, and advances the next priority to trust-hardening receipts for GitHub Actions, Devspace, archive/deletion safety, and release provenance.
- Added `proofHandoff` to `shipguard web plan`, `shipguard backend plan`, and `shipguard cli plan`: repaired WebForge, ServiceForge, and CommandForge plans now emit copy-ready evidence packets with validation status, commands to capture, attachment guidance, local-path-safe Markdown, and explicit no-implementation/no-validation-authorization boundaries.
- Added `profileNativeProofHandoffReceipts` to `shipguard value-gauntlet`: a public web/backend/CLI receipt now proves repaired plans produce shareable copy-ready proof handoffs, then advances the next priority to command-family runtime-output receipts so ShipGuard keeps moving from help-path coverage toward real output proof for every major family.
- Fixed profile-native first audits so ShipGuard starter files are profile-health evidence only: WebScan, ServiceRadar, and CommandLens now exclude generated starter handoffs from target framework, validation, and risk signals, expose scan-transparency metadata, and require real target source/config/test evidence before reporting proof readiness.
- Replaced the root maintainer instructions and plan template with ShipGuard-native operating guidance so public package users no longer see private app or sample-app instructions at the repository root.
- Added `validationRerunReceipts` to `shipguard web plan`, `shipguard backend plan`, and `shipguard cli plan`: WebForge, ServiceForge, and CommandForge now show the smallest repair plus rerun command for blocked or unchecked validation lanes while keeping target repos read-only.
- Added `profileNativeValidationRerunReceipts` to `shipguard value-gauntlet`: a public web/backend/CLI receipt now starts with blocked validation lanes, applies fixture-local smallest repairs, reruns the plans, proves the blockers clear, and advances the next priority to profile-native proof handoff receipts.
- Added `--target <repo>` validation receipts to `shipguard web plan`, `shipguard backend plan`, and `shipguard cli plan`: WebForge, ServiceForge, and CommandForge now classify validation lanes as runnable, blocked, manual, or not checked without executing arbitrary target commands.
- Added `profileNativeValidationReceipts` to `shipguard value-gauntlet`: a public web/backend/CLI receipt now proves the profile plan commands emit target-backed validation evidence and advances the next priority to validation rerun receipts.
- Added `shipguard web plan`, `shipguard backend plan`, and `shipguard cli plan` as profile-native fix-plan commands: ShipGuard WebForge, ServiceForge, and CommandForge now convert first-audit reports into scoped tasks, validation commands, stop conditions, ShipGuard-only eval boundaries, shareable output, and report-quality questions without editing target repos.
- Added `profileNativeFixPlanReceipts` to `shipguard value-gauntlet`: a public web/backend/CLI receipt now initializes fresh starter targets, runs first audits, converts each through the new plan commands, grades those plans with `ios report-quality`, and advances the next priority to profile-native validation receipts.
- Added `shipguard web audit`, `shipguard backend audit`, and `shipguard cli audit` as profile-native first audits: ShipGuard WebScan, ServiceRadar, and CommandLens now emit JSON/Markdown reports with source signals, validation guidance, next commands, ShipGuard-only eval boundaries, shareable output, report-quality questions, and package/self-audit proof.
- Added `profileNativeFirstAuditReceipts` to `shipguard value-gauntlet`: a public web/backend/CLI receipt now initializes fresh starter targets, prepares synthetic source signals, runs each first-audit report, grades the reports with `ios report-quality`, and advances the next priority to profile-native fix-plan receipts.
- Added `multiProfileOnboardingReceipts` to `shipguard value-gauntlet`: a public all-starter-profiles receipt now runs `shipguard init` and `shipguard doctor` for iOS, web, backend, and CLI fresh target repos, verifies each target receives `SHIPGUARD_PROFILE.md`, and advances the next priority to profile-native first-audit receipts for non-iOS profiles.
- Added `SHIPGUARD_PROFILE.md` copying to `shipguard init` so every starter profile leaves a profile-specific next-command guide inside the target repo without requiring maintainer context.
- Added `targetOnboardingReceipts` to `shipguard value-gauntlet`: a public fresh iOS target receipt now copies `fixtures/demo-ios-repo` into a temporary app repo, runs `shipguard init ios`, starter `doctor`, toolkit `validate`, iOS doctor, iOS inventory, and the first permission-audit plan, then advances the next priority to multi-profile onboarding receipts.
- Added `adoptionReceipts` to `shipguard value-gauntlet`: a public fresh-package receipt now builds from a temporary checkout copy, installs the extracted package into a temporary prefix, verifies a fresh Codex plugin cache with `codex status --strict`, runs the first Brand Deck audit from the installed CLI, scores that audit with report-quality, and advances the next priority to target-repo onboarding receipts.
- Added `scenarioRemediationReceipts` to `shipguard value-gauntlet`: a public blocked-to-repaired receipt now proves unsafe transcripts, broken docs, stale Codex plugin cache metadata, and incomplete release proof first block with evidence, then recover through the smallest repair step and a successful rerun before the next priority advances to fresh-user adoption receipts.
- Added `scenarioFailureReceipts` to `shipguard value-gauntlet`: a public bad-evidence receipt now proves ShipGuard blocks unsafe transcripts, broken docs, stale Codex plugin cache metadata, and incomplete release proof with non-zero exits or blocked reports before the next priority advances to scenario-remediation receipts.
- Added expected non-zero receipt-command support to the value-gauntlet receipt runner so failure-path receipts pass only when ShipGuard rejects bad evidence and still writes the expected machine-readable proof.
- Added `scenarioMatrixReceipts` to `shipguard value-gauntlet`: a public full maintainer-loop receipt now runs iOS doctor/inventory/plan/design, report-quality, docs-check, transcript redaction and verification, CI gate and summary, Codex plugin status, and release manifest/index/replay against public fixtures and a synthetic release package before the next priority advances to scenario-failure receipts.
- Added safe receipt fixture preparation to `shipguard value-gauntlet`, including temporary prepared files and deterministic synthetic tarballs under the receipt output directory so release workflows can be tested without mutating `dist/` or private app repos.
- Fixed `shipguard transcript redact` so redaction works when no `--private-term` arguments are supplied on macOS Bash with `set -u`, and added coverage for the default no-private-term privacy path.
- Added `workflowChainReceipts` to `shipguard value-gauntlet`: a public end-to-end receipt now runs design report -> report-quality -> spec-workflow -> spec report-quality -> next-goal against `fixtures/demo-ios-repo`, proving report-quality questions become SpecForge tasks, validation commands, slash plan/goal text, and a NextRail handoff before the next priority advances to scenario-matrix receipts.
- Added `skillPluginRuntimeReceipts` to `shipguard value-gauntlet`: public receipt fixtures now execute iOS ShipGuard design-audit routing, starter UI-polish inventory/plan routing, and plugin cache status proof against public/demo inputs, so skill/plugin usefulness is tested through real ShipGuard commands before the next priority advances to workflow-chain receipts.
- Added `runtimeCommandFamilyCoverage` to `shipguard value-gauntlet`: it now executes `--help` for all registered public ShipGuard commands, fixes top-level help routing for command families that previously treated `--help` as an invalid file/path/subcommand, and moves the next priority to skill/plugin runtime receipt fixtures.
- Added `runtimeOutputNegativeFixtures` to `shipguard value-gauntlet`: synthetic public bad-output fixtures now prove decorative empty reports and boundaryless design reports are rejected, and the next priority advances to broader command-family runtime execution.
- Added `runtimeOutputProbe` to `shipguard value-gauntlet`: it runs representative ShipGuard commands on public/demo inputs, scores their JSON/Markdown artifacts for machine-readable usefulness, tightens Brand Deck and DockCheck report shape, and retired the old "just run representative commands" next step.
- Added a Lowest-Value Surface Probe to `shipguard value-gauntlet`: after command/skill/plugin/action/doc coverage passes, it ranks deeper evidence signals, upgrades thin starter-skill QA hooks, and escalates all-green static coverage into a runtime-output usefulness probe instead of pretending the ShipYard is finished.
- Added report-quality fixture coverage detection so questions already covered by promoted public fixtures under `fixtures/ios-report-quality` keep their actionability evidence, suppress duplicate fixtureCandidates, render a `Fixture Coverage` section, and move the priority action to the next uncovered question.
- Fixed `release-proof build` so optional proof links like `--issue-url` and `--ci-run-url` are only forwarded when present, matching the documented release command and allowing proof bundles without a tracking issue URL.
- Promoted the ShipGuard Tool Value Gauntlet actionability question into a public `fixtures/ios-report-quality/value-gauntlet-actionability` synthetic fixture so report-quality proves low-value surface concerns can become reusable eval coverage without copying private app evidence.
- Added ShipGuard Tool Value Gauntlet with `shipguard value-gauntlet`, JSON/Markdown output, command/skill/plugin/action/doc/package-proof scoring, report-quality routing, package proof, self-audit coverage, and deterministic eval routing for "test every skill/plugin" product-QA requests.
- Expanded ShipGuard Brand Deck into a toolkit-wide naming system with 57 public command-family surface names, compatibility for `shipguard ios brand`, public-command coverage checks, docs coverage, package proof, self-audit coverage, and routing eval support for funny/vibey/techy naming requests.
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
