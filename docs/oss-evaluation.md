# ShipGuard Evaluation

Generated: 2026-06-17

This is the current usefulness and refinement evaluation for ShipGuard after the rename and README repositioning work.

## Evidence Run

Current checkout:

```bash
./bin/shipguard version
# 3.59.0

./bin/shipguard validate
# workflow bundle validation passed

./bin/shipguard self-audit --out /tmp/shipguard-self-audit
# status: pass

./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
# status: pass
# files_checked: 309
# links_checked: 54
# broken_count: 0

./bin/shipguard arena run --fixture fixtures/arena --out /tmp/shipguard-arena
# average: 4.69/12
```

Codex install check from this machine:

```bash
./bin/shipguard codex status
# Overall status: pass
```

Read-only real-app checks used for ShipGuard product-quality refinement:

```bash
./bin/shipguard ios performance --path <ringly-checkout> --out /tmp/shipguard-real-ringly/performance --shipguard-eval --shareable
# status: blocked
# findings: 73; rule mix: notification-removal-ui-stall, formatter-created-in-view, image-decoding-in-view-path, swiftui-large-blur, swiftui-repeat-forever-animation, swiftui-periodic-timeline, swiftui-shadow-stack
./bin/shipguard ios design --path <ringly-checkout> --out /tmp/shipguard-real-ringly/design-eval --shipguard-eval --shareable
# status: review
# output quality: app-type inference, design DNA, preview routing, motion/haptics, and icon handoff can be judged without turning findings into Ringly work
./bin/shipguard ios modernize --focus swift --path <ringly-checkout> --out /tmp/shipguard-real-ringly/modernize-eval --shipguard-eval --shareable
# status: blocked
# findings: 63; rule summary groups: 7
./bin/shipguard ios app-intelligence --path <ringly-checkout> --out /tmp/shipguard-real-ringly/app-intelligence-eval --shipguard-eval --shareable
# status: review
# App Intents: 14; App Shortcuts providers: 42
./bin/shipguard ios ai-readiness --path <ringly-checkout> --out /tmp/shipguard-real-ringly/ai-readiness-eval --shipguard-eval --shareable
# status: review
# detections: 20

./bin/shipguard ios doctor --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/doctor
./bin/shipguard ios inventory --path <ilmify-checkout> --doctor /tmp/shipguard-real-ilmify/doctor/ios-doctor.json --out /tmp/shipguard-real-ilmify/inventory
./bin/shipguard ios performance --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/performance --shipguard-eval --shareable
# status: review
# findings: 23; rule mix: swiftui-repeat-forever-animation, swiftui-large-blur, swiftui-shadow-stack
./bin/shipguard ios design --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/design-eval --shipguard-eval --shareable
# status: review
# output quality: app-type inference, design DNA, preview routing, motion/haptics, and icon handoff can be judged without turning findings into Ilmify work
./bin/shipguard ios modernize --focus swift --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/modernize-eval --shipguard-eval --shareable
# status: review
# findings: 45; rule summary groups: 4
./bin/shipguard ios app-intelligence --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/app-intelligence-eval --shipguard-eval --shareable
# status: review
# App Intents: 0
./bin/shipguard ios ai-readiness --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/ai-readiness-eval --shipguard-eval --shareable
# status: review
# detections: 152
```

These private-app runs are not app remediation plans. They are read-only samples used to evaluate whether ShipGuard reports are specific, prioritized, low-noise, and useful enough to turn into public fixtures or eval cases. The Ringly and Ilmify evidence showed ShipGuard needed the eval boundary on more than performance, plus rule summaries and capped Markdown for noisy modernize, app-intelligence, and AI-readiness reports while keeping complete JSON.

A later read-only Ringly/Ilmify pass showed two additional ShipGuard weaknesses: iOS source scanners could spend too much time traversing generated/proof/cache folders in large app checkouts, and `ios design` app-type inference over-weighted repeated instruction-document wording. The scanners now share a skip-scope helper, reports disclose skipped directories, and design app-type scoring prefers Swift/project signals with capped document contributions.

A subsequent read-only Ringly/Ilmify report-quality pass showed `ios design --shipguard-eval` was still useful but not shareable by default because the JSON carried the local app root. `ios design --shareable` now omits local absolute roots and preview directories from report fields before report-quality scoring or external planning, while default local reports keep operator paths.

The next read-only loop showed the report-quality artifact itself still carried absolute input/report paths even when its source design reports were shareable. `ios report-quality --shareable` now omits local absolute input and report paths from its own JSON, Markdown, findings, and redaction commands before ChatGPT/GitHub/docs/release-evidence sharing.

A follow-up read-only loop over the full Ringly/Ilmify report set showed another report-quality gap: the source reports carried useful `reportQualityQuestions`, but the quality artifact ended with only generic next actions. `ios report-quality` now aggregates those questions into an `Actionability Questions` section so the next ShipGuard rule, fixture, report section, or docs improvement is explicit.

The next read-only performance pass showed `ios performance --shipguard-eval` still carried absolute local project roots, so report-quality correctly raised a local-path shareability warning. `ios performance --shareable` now omits local absolute project paths from JSON and Markdown before report-quality scoring or external planning, while default local reports keep operator paths.

The next remaining-shareability pass over modernize, app-intelligence, and AI-readiness showed no local path leaks in real-app reports, but those reports had no explicit shareability contract. `ios modernize --shareable`, `ios app-intelligence --shareable`, and `ios ai-readiness --shareable` now record shareability metadata and Markdown mode lines so report-quality passes are intentional rather than accidental.

The next declared-shareability pass showed `ios report-quality --shareable` still passed local-mode source reports when their contents happened not to leak paths. Report-quality now emits `declared-shareability-missing` for source reports without shareability metadata and `declared-shareability-local-mode` for reports that explicitly declare local mode, while regenerated shareable Ringly/Ilmify reports continue to pass.

The next read-only Ringly/Ilmify design and performance pass produced structurally clean report-quality output with useful actionability questions, but ShipGuard still lacked a first-class way to convert those questions into governed implementation work. `ios spec-workflow` now generates ShipGuard-owned constitution, feature spec, implementation plan, tasks, analysis gates, slash plan/goal, and Devspace guardrails from a feature or report-quality artifact so private-app observations become ShipGuard product work instead of app remediation tasks.

A follow-up misuse probe showed a shareable spec workflow generated without `--from-report` still passed report-quality even though it was not grounded in observed ShipGuard output. Report-quality now emits `spec-workflow-report-context-missing` and `spec-workflow-actionability-missing` for that case, so polished-looking spec artifacts need real report evidence before they pass adoption scoring.

The next spec-workflow completeness probe removed a declared generated file from an otherwise valid bundle. Report-quality now dereferences the spec-workflow artifact manifest and emits `spec-workflow-artifact-file-missing` for incomplete bundles while keeping shareable output free of local absolute paths.

The next content-quality probe replaced valid `tasks.md` and `devspace-guardrails.md` files with placeholder text. Report-quality now emits `spec-workflow-artifact-content-incomplete` and `spec-workflow-artifact-placeholder-content`, so present-but-useless generated files no longer pass adoption scoring.

The next question-coverage probe replaced the generated clarifying questions with a generic question while leaving the spec bundle structurally valid. Report-quality now emits `spec-workflow-question-coverage-missing` and `spec-workflow-question-artifact-missing`, so report-grounded spec workflows must preserve the source actionability questions in JSON and Markdown.

The next task-coverage probe showed a report-grounded spec workflow could pass even when `taskPlan` and `tasks.md` stayed generic and answered none of the source actionability questions. Spec-workflow now creates `S007+` proof-gated tasks for those questions, and report-quality emits `spec-workflow-task-coverage-missing` or `spec-workflow-task-artifact-missing` if a bundle drops them.

The next acceptance-criteria probe showed a report-grounded spec workflow could still pass when `featureSpec.acceptanceCriteria` and `feature-spec.md` stayed generic. Spec-workflow now turns deduplicated report-quality actionability questions into acceptance criteria as well as tasks, and report-quality emits `spec-workflow-acceptance-coverage-missing` or `spec-workflow-acceptance-artifact-missing` if a bundle drops them.

The next validation-command probe showed a report-grounded spec workflow could pass even when `technicalPlan.recommendedValidation` was empty and `implementation-plan.md` only said validation needed maintainer selection. Report-quality now emits `spec-workflow-validation-coverage-missing` or `spec-workflow-validation-artifact-missing` when the spec workflow drops exact proof commands.

The next analysis-gate probe showed a report-grounded spec workflow could pass after `analysisGates` and `implementation-plan.md` were reduced to a generic maintainer-selection placeholder. Report-quality now emits `spec-workflow-analysis-coverage-missing` or `spec-workflow-analysis-artifact-missing` when the spec workflow drops the required pre-implementation analysis gates.

The next slash-handoff probe showed a report-grounded spec workflow could pass after `slashPlan`, `slashGoal`, and `ios-spec-workflow.md` were reduced to generic "plan later" placeholders. Report-quality now emits `spec-workflow-slash-handoff-incomplete` or `spec-workflow-slash-handoff-artifact-missing` when a spec bundle drops the copy-ready `/plan` and `/goal` next-loop handoff.

The installed Codex cache now has `ios-shipguard` metadata version `0.2.0+codex.20260617011237`, repository `https://github.com/jlekerli-source/ShipGuard`, display name `iOS ShipGuard`, and no stale `ringly-codex-workflows`, `Shipguard`, or primary `codex-maintainer` guidance. The tracked checkout includes `plugins/ios-shipguard`, and package proof requires that plugin source.

## Verdict

ShipGuard is useful as a CLI and workflow bundle today. It validates itself, produces release proof, checks docs, scores agent runs, exports GitHub Action artifacts, and catches dangerous proof claims in benchmark fixtures.

The Codex plugin source and local cache are now clean enough for local use. The checkout also includes a local marketplace entry under `.agents/plugins/marketplace.json`; after installing or refreshing that plugin source, Codex still needs a new thread before refreshed skill metadata is loaded.

## Keep

- Keep `shipguard` as the CLI and package command.
- Keep `codex-maintainer` only as a compatibility alias for older automation.
- Keep Agent Autopsy, Arena, docs-check, release-proof, release-consume, release-evidence, transcript verification, CI gate, SARIF, and self-audit.
- Keep the scorecard categories. They map well to real maintainer failure modes.
- Keep the current GitHub Actions coverage because it proves the CLI and release artifacts from source.

## Refine

- Keep Codex plugin source first-class and tracked under `plugins/ios-shipguard`.
- Keep plugin metadata on `ShipGuard` casing and repository/homepage URLs on `jlekerli-source/ShipGuard`.
- Keep installed skill guidance on the restored `shipguard ios` helper surface.
- Keep the marketplace-backed reinstall flow documented so direct cache sync is not the only path.
- Keep real-app read-only checks in the refinement loop with `--shipguard-eval` so ShipGuard reports are judged against Ringly and Ilmify usefulness without turning findings into app work.
- Keep scan-scope reporting visible in iOS reports so private-app QA can explain what was intentionally skipped.
- Add regression-awareness benchmark cases because the Arena average is held down partly by weak regression detection.
- Tighten docs around when to use the CLI versus when to install the Codex plugin.

## Add

- `shipguard codex status` for local Codex install-state proof.
- A marketplace source entry for `ios-shipguard`.
- A plugin install or refresh handoff that says exactly when Codex must be restarted or cache-cleared.
- Keep the restored `shipguard ios` helper commands covered by tests, docs, package proof, and plugin guidance.
- `shipguard ios performance` as a read-only source scanner for ranked SwiftUI/runtime performance hotspots before Codex chooses edits.
- `--shipguard-eval` as the explicit ShipGuard-only product QA mode for private real-app samples across `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, and `ios ai-readiness`.
- `shipguard ios design` for genre-aware UI/UX coherence, design DNA, motion, haptics, preview routing, and ImageGen app-icon handoff.
- `shipguard ios report-quality` to score ShipGuard's own read-only reports for boundaries, evidence, proof guidance, scan scope, Markdown usefulness, token/path shareability, and redaction handoff before turning observations into public fixtures or eval cases.
- `shipguard ios devspace-check` to score Devspace connector readiness, public URL safety, MCP widget metadata, preview evidence, handoff execution boundaries, handoff fixture quality, and ChatGPT model-choice honesty before tunneled visual planning is treated as useful.
- `shipguard ios spec-workflow` to convert report-quality actionability questions into ShipGuard-owned constitution, spec, implementation plan, tasks, analysis gates, slash plan/goal, and Devspace guardrails before Codex implementation.
- Shared iOS scan-scope exclusions for generated/proof/cache directories, plus tests that generated artifacts do not become report findings.
- A repository threat model artifact before running a full Codex Security scan.
- More Arena fixtures for security-sensitive workflows: credentials, untrusted paths, generated artifacts, network posting, GitHub token scope, and release asset trust.
- Optional OpenAI Agents SDK evaluation only if ShipGuard becomes a runnable agent service. Do not add OpenAI API dependencies to the CLI without that product decision.

## Remove Or Defer

- Keep stale public references to `ringly-codex-workflows` out of plugin source and future packages.
- Keep legacy wrapper details out of primary README and CLI flow; route them to `docs/compatibility.md` while package tests prove older automation still works.
- Defer npm or Homebrew distribution until the Codex plugin source and release install story are reliable.
- Defer a full Codex Security repository scan until subagent authorization is explicit; use threat modeling first.
- Defer Agents SDK work until there is a clear agent product, input contract, and eval target.

## Plugin And Skill Guidance

- Superpowers: useful for larger feature design and execution plans. Use it when adding a new subsystem, but keep small CLI/doc fixes on the repo-native proof loop.
- Codex Security: use `threat-model` first. Use full `security-scan` only with explicit subagent authorization and when the scan can produce ledger artifacts.
- OpenAI Developers: use Agents SDK only for a deliberate agent/eval app. Not needed for the current shell CLI or docs-only workflow bundle.
- GitHub: keep using local `gh` and Actions verification for publish proof.

## Phased Plan

### Phase 1: Plugin Source And Local Cache

Status: done.

- Restore tracked `plugins/ios-shipguard` source.
- Update plugin metadata and skill text to `ShipGuard`.
- Include plugin source in package, validate, self-audit, and package tests.
- Refresh the installed local Codex cache.
- Prove with `./bin/shipguard codex status --strict`.

### Phase 2: iOS Helper Decision

Status: done.

- Restored the public `shipguard ios ...` helper commands from the last package as the chosen direction.
- Restored the Python helper scripts, demo iOS fixture, eval cases, docs, and tests as one validated slice.
- Normalized the restored surface to `shipguard` and `ShipGuard` naming while keeping `bin/codex-maintainer` as a compatibility wrapper.

### Phase 3: Marketplace-Backed Install

Status: done locally.

- Added `.agents/plugins/marketplace.json` with marketplace id `shipguard` and plugin id `ios-shipguard`.
- Documented the local install flow: `codex plugin marketplace add .`, then `codex plugin add ios-shipguard@shipguard`.
- Documented the new-thread boundary required for Codex to load refreshed skill metadata.
- Added the same Git/source, plugin-cache, and new-thread refresh handoff directly to `shipguard codex status`.
- Remaining distribution work is a real external marketplace/release install path beyond the local checkout.

### Phase 4: Security Evaluation

Status: started.

- Added `docs/security-threat-model.md` before any full scan.
- Added `fixtures/arena/security-token-leakage` for token, local path, and overclaim failure pressure.
- Added an Autopsy `sensitive_data_leak` finding for unredacted local paths, secret-looking tokens, bearer values, and secret assignments without echoing the sensitive value into reports.
- Added `fixtures/arena/release-asset-trust-bypass` and an Autopsy `release_artifact_trust_gap` finding for disabled or bypassed release artifact digest, manifest, attestation, or replay verification.
- Added `fixtures/arena/github-posting-without-dry-run` plus Autopsy findings for broad GitHub token scopes and mutating network calls enabled without dry-run or payload-review safeguards.
- Added `fixtures/arena/generated-artifact-cleanup-bypass` plus an Autopsy `unsafe_artifact_cleanup` finding for generated artifact deletion that bypasses the safe artifact path guard.
- Hardened `shipguard arena import` against unsupported files, nested entries, symlinked fixture files, overlapping source/output paths, and raw local source-path leakage in `PACK.md`.
- Only run the full Codex Security repository scan with explicit subagent authorization.

### Phase 5: Benchmark And Product Polish

Status: started.

- Added `fixtures/arena/storekit-entitlement-regression` to exercise regression-awareness and proof honesty around subscription restore behavior.
- Added `fixtures/arena/data-migration-loss-regression` plus an Autopsy `destructive_migration_risk` finding for migrations that drop persistent user data without backup, rollback, or rehearsal proof.
- Added `shipguard ios performance` after real-app read-only checks showed the previous `performance-audit` route produced proof guidance but not enough concrete source findings.
- Added `--shipguard-eval` so private Ringly/Ilmify-style checks are explicitly ShipGuard-only QA, not target-app remediation work.
- Changed the performance report shape to include rule summaries, capped repeated rules in Markdown, exact evidence snippets, and full JSON findings for deeper follow-up.
- Extended `--shipguard-eval` to design, modernization, app-intelligence, and AI-readiness reports after read-only Ringly/Ilmify evidence showed the product-QA boundary was needed beyond performance.
- Added `shipguard ios design` so real-app design findings become ShipGuard report-quality evidence, public fixtures, and eval cases instead of private app remediation tasks.
- Added shared iOS scan-scope exclusions and design app-type signal weighting after read-only Ringly/Ilmify evidence showed generated artifacts and repeated instruction docs could distort report quality.
- Added `shipguard ios report-quality` so Ringly/Ilmify-style read-only reports can be graded as ShipGuard product QA before any finding becomes a ShipGuard rule, doc, or fixture.
- Added `shipguard ios devspace-check` after connector/plugin trials showed Devspace needed a first-class readiness report instead of relying on scattered docs and live MCP tests.
- Added a public `fixtures/ios-devspace/complete-preview` handoff so Devspace-check can test event receipts and target-resolution quality without private app code.
- Added `ios devspace-check --shareable` after report-quality showed otherwise-clean Devspace-check reports still needed local-path redaction before external sharing.
- Added `ios design --shareable` after the same shareability issue showed up in design/product-QA reports with local app and preview paths.
- Added `ios report-quality --shareable` after read-only Ringly/Ilmify design evals showed the quality artifact itself could carry local input/report paths even when the source reports were already shareable.
- Added a public report-quality actionability fixture and aggregated `Actionability Questions` output after full Ringly/Ilmify read-only evals showed useful source questions were not surfaced in the quality artifact.
- Added `ios performance --shareable` after read-only Ringly/Ilmify performance evals showed otherwise useful source reports still carried local project roots before report-quality scoring.
- Added `ios modernize --shareable`, `ios app-intelligence --shareable`, and `ios ai-readiness --shareable` after read-only Ringly/Ilmify checks showed those path-safe reports still lacked an explicit shareability contract.
- Added declared-shareability report-quality findings after read-only Ringly/Ilmify local-mode reports showed shareable scoring could pass reports that were path-clean but not explicitly generated for sharing.
- Added `shipguard ios spec-workflow` after clean read-only report-quality runs showed the missing step was converting actionability questions into proof-gated ShipGuard specs, tasks, slash plans, and Devspace guardrails.
- Added spec-workflow adoption quality findings after a misuse probe showed report-quality needed to distinguish report-grounded spec workflows from standalone polished plans.
- Added modernization rule summaries and capped Markdown for modernize, app-intelligence, and AI-readiness reports so private-app findings stay useful for improving ShipGuard without becoming app remediation tasks.
- Improved first-run adoption docs around CLI versus plugin usage.
- Upgraded `shipguard next-goal` so the next improvement loop emits a reviewable `/plan` before the `/goal`, and can now carry bounded scope, completion evidence, and the following `/goal` handoff.
- Moved legacy command-wrapper guidance out of primary README and CLI flow into `docs/compatibility.md`.
- Keep Agents SDK deferred unless ShipGuard becomes a runnable agent service with a concrete eval target.
