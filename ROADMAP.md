# Roadmap

This roadmap keeps the repo useful without pretending it is a finished framework.

## Product Center

ShipGuard is the local policy, context, and evidence layer for high-risk Codex changes, starting with production iOS apps.

The roadmap should optimize for one proof-gated change loop:

```text
inspect the repository and proof state
prepare a narrow Codex task contract
execute under protected boundaries
verify the diff, evidence, and agent claims
return PASS, REVIEW, or BLOCKED with the next exact action
```

Near-term strategy:

- Freeze broad public-command expansion unless the command feeds `inspect`, `prepare`, `verify`, `doctor`, or core initialization.
- Build a persistent task object that connects repo context, risk, authorized files, validation, agent run evidence, and verdict.
- Treat command-family runtime-output receipts as regression coverage, not a headline product pillar.
- Remove development-loop waste when proof shows it: workflow-chain receipts should prove that report-quality questions become SpecForge tasks, validation commands, slash plans/goals, and the following goal without manual interpretation.
- Accelerate trust hardening, task contracts, and the iOS notification/permission proof workflow.
- Delay broad web/backend/CLI maturity until the core task/evidence schema and first iOS domain pack prove value.
- Keep evaluation running beside every feature through gold fixtures, negative fixtures, model critique, and human review where useful.

## Major-Version Arc

The long-term ambition is larger than the current v3 release train:

```text
v3 = prove that ShipGuard changes real developer decisions
v4 = become a stable local-first assurance product
v5 = become an organization-wide AI change control plane
v6 = become an open protocol and ecosystem for AI change assurance
post-v6 = become trust infrastructure for autonomous software development
```

The invariant across all of those eras is the same: ShipGuard must connect intent, scope, execution, evidence, claims, verdict, and provenance for one software change. It should not become another generic AI coding agent, a cloud-only source-upload scanner, a dashboard without a strong local engine, or a report generator that does not change decisions.

Major-version definitions:

- v4 means product: a solo developer can trust and recommend ShipGuard without author help.
- v5 means platform: teams can govern AI-generated changes across repositories, policies, agents, approvals, and releases.
- v6 means standard: other tools can produce and consume ShipGuard-compatible task contracts, evidence receipts, verdicts, domain packs, and attestations.

When a major milestone reaches its exit gate (`v4`, `v5`, `v6`, or later), the release loop must create a fresh Codex launch/promotion thread before final announcement work. That thread should be separate from implementation context and should prepare Product Hunt, r/ShipGuard, X, README/release copy, screenshots/assets, and launch proof from the verified milestone state. Computer-use may help prepare drafts, fill preview fields, and stage launch pages, but public posting, publishing, submission, or account-visible external actions require explicit approval for that exact launch run.

Keep the core open-source verdict engine honest. Future Pro, Team, or Enterprise surfaces can add Studio, Hub, policy simulation, registries, analytics, or hosted/self-hosted collaboration, but the local `prepare` -> `verify` decision loop must not become decorative or paywalled into uselessness.

## Phase Map

The roadmap is intentionally larger than the earlier v3.105-v3.110 loop. The current published baseline treats v3.115-v3.131 as shipped foundations. Active ShipYard work after v3.131 is v4 product release stabilization, including report-quality polish, result-UX command discipline, external adoption evidence, security review, package proof, rollback proof, and release proof consumption. The latest LaunchKey, Full Audit, and verify-first polish attaches same-prefix upgrade and rollback cleanup receipts, blocks generated archive members before package install, exposes `blockingProof` for failed receipts, downloads GitHub release assets natively before consumer proof, validates external adoption and final security-review evidence without faking adoption/security proof, keeps generated package install/work/upgrade/rollback/download/consume proof directories from being recursively scored as source reports, makes Full Audit release lanes human-copyable through Markdown execution-command receipts, promotes stable-publication closure kits for GitHub release metadata, release notes, LaunchKey candidate proof, downloaded release assets, post-release consumer proof, adoption evidence, and security evidence, adds external evidence freshness so adoption/security records cannot predate the release manifest they are used to publish, adds public release delta and release visibility handoff proof so local `main` is not mistaken for the current public release, promotes `unsupportedClaimReplay` fixtures so broad completion claims are blocked with a replayable claim-specific repair path, promotes notification-permission scope fixtures so prepare reports must show authorized owner scopes, review-only lifecycle/plist surfaces, forbidden entitlement/project boundaries, and permission-sensitive source signals, promotes structured receipt proof-lane fixtures so generic logs cannot satisfy permission-state or denied-state proof, and promotes simulator/device boundary fixtures so simulator denied-state proof cannot be recast as physical-device prompt or release proof. The full product plan continues from there instead of replaying completed notification-pack, PilotBench, Domain Pack SDK, configuration-baseline, structured-receipt, agent-adapter, XcodeBuildMCP evidence-adapter, Expo/EAS assurance, universal-agent packaging, full-audit orchestration, unified inspect, concise result-UX, Codex marketplace-readiness, External Benchmark v2, V4 Preview, V4 Schema Freeze, or V4 Release Candidate Readiness work.

### Phase A: Trustworthy Foundation

Next three to five releases should harden the core before broadening the surface:

- Separate maintainer-only ShipYard tools from the public app-developer story.
- Keep GitHub Action, archive, Devspace, and release-provenance trust receipts green.
- Introduce and stabilize the canonical task object through `shipguard prepare`.
- Make `shipguard verify` the default post-Codex verdict path.
- Make `shipguard verify` the launch-facing hero before promoting internal ShipYard machinery: one short quickstart, one tiny broken demo repo, one PR Action path, one clean proof report, and a visible `quickstartReplay` block in prepare/verify outputs.
- Keep the PR Action path proofable with `shipguard action verify-pr`, so copied workflows fail setup mistakes and downloaded `shipguard-verdict` artifacts are consumable before maintainers trust missing or decorative proof.
- Treat one-command install, GitHub Action setup, agent templates, demo project, docs site, release proof, honesty checker, PR review, badges, and integrations as the launch ladder around `verify`, not as disconnected feature work.
- Establish schema, compatibility, and deprecation rules before adding more public verbs.

Exit gate: a new developer can install ShipGuard, initialize a repo, prepare a risky task, and get a useful verify verdict without reading internal ShipYard docs.

### Phase B: Killer Workflow

The first killer workflow is proof-gated iOS notification and permission work:

- Identify owner files and protected boundaries.
- Generate a task-specific Codex contract.
- Capture diff, validation receipts, simulator proof, and manual/device gaps.
- Reject unsupported completion claims.
- Return one exact next action.

Exit gate: independent iOS developers complete risky notification changes using ShipGuard without author assistance.

### Phase C: iOS Assurance Packs

Add one evaluated iOS domain pack at a time:

1. Notifications and permissions.
2. StoreKit and entitlements.
3. Persistence and migrations.
4. Widgets, App Intents, and shared state.
5. Background execution and lifecycle.
6. Performance with runtime evidence.
7. Design with screenshots and flow evidence.
8. Modernization with compiler-backed validation.

Each stable pack needs gold fixtures, negative fixtures, mutation cases, and precision/actionability thresholds.

### Parallel Track: Evaluation Flywheel

Every product slice should ship with:

- Real or synthetic task traces.
- Human or expert labels where useful.
- Model critique only as calibrated input, not automatic truth.
- Public-safe fixture promotion.
- False-positive and next-action quality checks.

### Phase D: Multi-Stack Expansion

Do not mature web, backend, and CLI equally by default. Expand after the core task/evidence schema and the first iOS pack show measurable value.

### Phase E: v4 Productization

v4 should require stable schemas, migration support, clean package/install/uninstall behavior, strong security posture, independent benchmark results, and external adoption proof.

## Release Ladder

Version numbers are planning bands, not promises. A release can skip ahead only when the exit gate for its current band is already proven.

### Immediate v3 Sequence

The current v3 line should remain decision-centered:

```text
v3.115  Notification/permission domain pack
v3.116  ShipGuard PilotBench and honest usefulness metrics
v3.117  Domain Pack SDK and core extraction
v3.118  Configuration, baselines, and suppressions
v3.119  Structured evidence receipts v2
v3.120  Agent Adapter Kernel and Codex-native task/trace adapter
v3.121  XcodeBuildMCP evidence adapter
v3.122  Expo MCP and EAS assurance adapter
v3.123  Claude, Gemini, Cursor, and generic MCP packaging
v3.124  Efficient "Unleash the Beast" full-audit orchestrator
v3.125  Unified inspect experience
v3.126  Concise verdict and result UX
v3.127  Codex marketplace readiness
v3.128  External benchmark v2
v3.129  v4 preview stabilization
v3.130  v4 schema freeze and compatibility policy
v3.131  v4 release-candidate readiness
v3.132  v4 product release stabilization
v3.133  root report-quality and bounded source-scan hardening
v3.134  result-UX command-field polish for source reports
v3.135  InspectDeck missing-receipt priority
v3.136  InspectDeck executable next-command normalization
v3.137  LaunchKey published release-asset proof attachment
v3.138  LaunchKey fresh-install receipt attachment
v3.139  LaunchKey generated proof-directory report-quality exclusion
v3.140  LaunchKey upgrade and rollback receipt attachment
v3.141  LaunchKey downloaded-asset blocking proof detail
v3.142  LaunchKey native GitHub release-asset download
v3.143  Stable-v4 external adoption evidence gate
v3.144  Stable-v4 final security-review evidence gate
v3.145  Full Audit release-packet plan honesty
v3.146  Full Audit NEXT_GOAL-backed slash handoff
v3.147  Full Audit copy-ready execution-command receipts
v3.148  Tool Value Gauntlet stable-publication priority
v3.149  Stable-publication final claim gate
v3.150  Lean Review selected-mode bias fixture
v3.151  Lean Debt marker-visibility fixture
v3.152  Lean Debt benchmark-savings honesty fixture
v3.153  Lean Debt rot-risk visibility fixture
v3.154  Lean Debt trigger-rot next-action fixture
v3.155  Verify-first launch quickstart
v3.156  Guarded launch relay drafts
v3.157  One-command installer proof path
v3.158  GitHub Action first-run proof path
v3.159  Demo project and docs-site quickstart polish
```

Current state: latest published release `v3.131.0` adds `shipguard v4 release-candidate` and V4 Release Candidate Readiness receipts that make fresh install, upgrade, uninstall, release-proof consumption, external adoption packet, final schema docs, plugin refresh proof, release-readiness commands, and blocked stable-release claims explicit. Active local ShipYard handoffs may target later v3 stabilization slices, but those are not stable-v4 release claims. Current `main` has moved through LaunchKey published release-asset proof, package fresh-install proof, report-quality proof-directory exclusion, same-prefix upgrade receipts, rollback cleanup receipts, generated archive-member blocking, blocking-proof result UX, native GitHub release-asset download, external adoption evidence gating, final security-review evidence gating, Full Audit release-packet plan honesty, NEXT_GOAL-backed Full Audit slash handoff proof, stable-publication evidence packets, draft-only stable-publication evidence templates, guarded stable-publication launch relay drafts, Verify-PR runtime artifact consumption, and Lean Deck behavior-gate/gain-honesty hardening. v3.170 added public release freshness proof so stale GitHub tag targets, release manifest commits, release target SHAs, or timestamp mismatches block stable-v4 claims before adoption/security evidence can make a stale public release look complete. v3.171 hardens post-release consumer proof by carrying digest freshness from `asset-digests.json`: required asset rows, missing required assets, missing SHA-256 rows, release tarball digest, consumer artifact SHA-256, and tarball-digest comparison now appear in stable-publication JSON, Markdown, report-quality rules, and fixtures. v3.172 hardens external evidence freshness so independent adoption and final security-review records must be generated no earlier than the release manifest timestamp before they can support stable-v4 publication. v3.173 hardens release version coherence so `VERSION`, requested release version, GitHub metadata, release manifest, package proof, consumer report, and versioned tarball name must agree before stable-v4 publication can pass. v3.174 hardens release asset coherence so required asset names and SHA-256 values must agree across GitHub metadata, downloaded assets, release manifest, digest matrix, and consumer proof. v3.175 hardens public evidence closure so adoption/security gate status, freshness, starter paths, copy-ready commands, and non-claims are summarized before stable-v4 publication can be claimed. v3.176 hardens the final stable-v4 claim packet so maintainers get copy-ready allowed or blocked wording, evidence rows, first blocker, approval boundary, and non-claims before announcement copy. v3.177 hardens public release delta proof so maintainers can see when local `main`, latest GitHub release, package assets, and stable-publication claim scope are out of sync instead of treating unpublished local code as released. v3.184 hardens release-notes authoring handoff so blocked stable-publication reports carry the exact manual `gh release edit ... --notes-file stable-publication-release-notes/draft-release-notes.md` command instead of a vague "update notes" instruction. v3.185 routes that same command through `releaseVisibilityHandoff.requiredActions[update-release-notes].nextCommand` and Markdown so the public-release action matrix does not send maintainers back to a rerun before editing notes. These slices do not replace real public release metadata, downloaded assets, release-consume, independent adoption, or final security proof. The active architectural priority remains v4 product release stabilization: public release metadata, external adoption evidence, final security review, package proof, rollback proof, report-quality precision, result-UX command discipline, release freshness, consumer digest freshness, external evidence freshness, version coherence, asset coherence, public evidence closure, final claim packet, public release delta proof, and release proof consumption on published assets before any stable v4 claim.

v3.186 continues that release-notes actionability cleanup by routing the same edit command through `stablePublicationEvidencePacket.firstBlockingGate.nextCommand`, release-notes closure `nextCommand`, and `resultUX.nextCommand`; `rerunCommand` remains the after-edit verifier.

v3.187 cleans the stable-publication release visibility handoff so completed `pass`/not-required rows say `not-needed` instead of leaking fallback commands like test scripts into maintainer-facing next-action tables.

v3.188 extends that cleanup to the blocked `keep-current-public-release-unchanged` row: while earlier gates are still required, it now says `blocked-by-required-actions` instead of duplicating the primary repair command.

v3.189 humanizes the stable-publication result UX so the top proof source and first action use reader-facing evidence labels instead of leaking internal JSON names like `stablePublicationClosureChecklist` or `releaseNotesProof`.

v3.190 makes stable-publication default asset downloads rerunnable: generated `--out/downloaded-release-assets` state is refreshed before a new download, while explicit custom download directories and supplied release-asset directories remain caller-owned and protected from deletion.

v3.191 makes release-notes edit commands path-safe: stable-publication now points `gh release edit --notes-file` at the generated draft under the report output directory, so the first blocker command works from a normal repo shell instead of assuming the maintainer has changed into the report directory.

v3.192 makes the release-notes authoring kit self-locating: stable-publication now emits generated README/checklist/draft paths in `stablePublicationReleaseNotesAuthoringKit.generatedPaths` and `files[].generatedPath`, with shareable reports redacting the local output root.

v3.193 makes the release-loop bottleneck visible: `tests/package_release_test.sh` now prints coarse phase timings for package build, manifest/privacy checks, packaged CLI smoke proof, full-audit/value-gauntlet proof, v4 proof gates, and install proof so maintainers can tell whether the slow package lane is progressing.

v3.194 makes next-goal release lineage explicit: generated handoffs now compare `VERSION`, the expected next semantic release, the planned target release, the current pre-bump package artifact, and the expected post-bump release artifact, then stop slash plan/goal publishing language at version-lineage resolution when a planning-only stabilization slice skips the next semantic release.

v3.195 keeps that lineage honest for the normal next-release path: a passing next-goal lineage check no longer implies the current checkout already builds the post-bump tarball; it now names the pre-bump artifact and tells maintainers to bump `VERSION` before release packaging.

Release-line note: local `VERSION` now advances to `3.133.0` for the buildable v4-stabilization package path. The latest public GitHub release remains `v3.131.0` until a separate release publication and consumer-proof pass is completed.

v3.133 starts real stable-publication packet QA by making missing GitHub release metadata actionable: the closure kit now includes a manual `gh release create ...` starter with the required release-proof assets and a boundary that ShipGuard prepares proof but does not publish public releases.

v3.134 continues result-UX command-field hardening by making report-quality reject prose or Markdown in `priorityAction.nextCommand`, so copy-facing source-report actions stay executable while explanation stays in summary fields.

v3.134 also continues InspectDeck release-proof receipt priority by making missing release proof keep `shipguard inspect` in `review` and route `nextAction` / `resultUX.nextCommand` to `shipguard release-proof build` before lower-priority value-gauntlet recommendations.

v3.135 continues InspectDeck release-proof receipt detail by keeping readable-but-incomplete release manifests in `review`, listing missing required receipt fields, and routing the next action back to `shipguard release-proof build`.

v3.135 continues InspectDeck missing-receipt priority by exposing `missingReceiptPriority` in JSON and Markdown, keeping the first executable next action singular while showing the remaining value-gauntlet, full-audit, and release-proof queue.

v3.136 continues InspectDeck executable next-command normalization by falling back to a runnable full-audit command when a failed-stage receipt has a missing or unsafe `stageId`, instead of leaking malformed `--stage` commands into `resultUX.nextCommand`.

v3.136 also continues InspectDeck release-proof badge detail by keeping supplied non-pass attestation badges in `review`, listing badge problems, and routing the next action back to `shipguard release-proof build`.

v3.137 continues InspectDeck release-proof path handoff by exposing release-assets, manifest, and badge paths plus a rerun template and no-mutation boundary in release-state reports.

v3.137 continues LaunchKey published release-asset proof attachment by adding a compact `releaseAssetProofAttachment` to `publishedReleaseAssetProof`, so release-consume paths, digest status, missing artifacts, next command, and source-only/fixture-proof boundaries travel with the candidate packet.

v3.138 continues LaunchKey fresh-install receipt attachment by adding a compact `freshInstallProofAttachment` to `freshInstallPackageProof`, so install paths, version and validation exits, forbidden installed paths, missing artifacts, next command, and source-only/fixture-proof boundaries travel with the candidate packet.

v3.138 also adds a LaunchKey fresh-install receipt handoff so the attachment points stable-publication at the containing candidate report, names the proof artifacts, and makes clear the install prefix alone is not stable-v4 proof.

v3.139 continues LaunchKey generated proof-directory report-quality exclusion by making skipped generated package/install/upgrade/rollback/download/consume JSON files visible through `skippedReportDiscovery` and Markdown while still scoring only the root report.

v3.139 also adds LaunchKey upgrade and rollback receipt handoffs so same-prefix upgrade and cleanup attachments point stable-publication at the containing candidate report, name proof artifacts, and make clear proof prefixes alone are not stable-v4 proof.

v3.140 adds LaunchKey release-asset receipt handoff so verified downloaded or supplied release assets point stable-publication at the containing candidate report, name release-consume proof artifacts, and make clear a release-assets directory alone is not stable-v4 proof.

v3.140 continues LaunchKey upgrade and rollback receipt attachment by adding compact `upgradeProofAttachment` and `rollbackProofAttachment` blocks so same-prefix upgrade and rollback cleanup proof travel with the candidate packet.

v3.141 continues LaunchKey downloaded-asset blocking proof detail by adding `downloadBlockingProof` to failed native GitHub release-asset downloads so repo, tag, endpoint, destination, error, rerun command, and proof boundaries are visible.

v3.141 also adds LaunchKey download receipt handoff so successful native GitHub asset downloads point stable-publication at the containing candidate report, name download proof artifacts, and make clear the download directory alone is not stable-v4 proof.

v3.142 adds LaunchKey download-blocking receipt handoff so failed native GitHub asset downloads keep the candidate report path, failure evidence, repair command, stable-publication command, and blocked-download non-proof boundary with the blocking receipt.

v3.142 continues LaunchKey native GitHub release-asset download by adding `downloadProofAttachment` to successful native downloads so repo, tag, endpoint, destination, downloaded asset names, SHA-256 rows, rerun command, and source-only/fixture-proof boundaries travel with the candidate packet.

v3.143 continues Stable-v4 external adoption evidence gating by adding `adoptionGateAttachment` to supplied adoption evidence so record counts, accepted classes, required fields, first invalid record diagnostics, next command, and source-only/fixture/download/marketplace boundaries travel with the candidate packet.

v3.144 continues Stable-v4 final security-review evidence gating by adding `securityReviewGateAttachment` to supplied security review evidence so record counts, accepted classes, accepted reviewer relationships, required scope, required fields, first invalid record diagnostics, next command, and source-only/fixture/marketplace boundaries travel with the candidate packet.

v3.145 continues Full Audit release-packet plan honesty by adding `releasePacketPlan` to release-related Full Audit runs so selected release stages, required metadata, missing metadata, next command, non-claims, and proof boundaries are visible before anyone treats a plan as release proof.

v3.146 continues Full Audit NEXT_GOAL-backed slash handoff proof by adding `slashHandoffProof` so selected section, completion receipt presence, version-lineage status, copy-ready slash commands, stale-handoff rejection, and no-publication boundaries are visible beside the copied `/plan` and `/goal`.

v3.147 continues Full Audit copy-ready execution-command receipts by adding `executionCommandReceipt` so execute/resume commands, per-stage command rows, empty/manual stage fallbacks, and no-push/no-publish boundaries are visible in JSON and Markdown.

v3.148 continues Tool Value Gauntlet stable-publication priority by adding `stablePublicationPriority` so the v4 blocker, proof packet, copy-ready stable-publication command, and source/fixture non-claims are visible without digging through the lowest-value probe internals.

v3.149 continues Stable-publication final claim gate hardening by keeping `allowedClaims` empty on blocked `finalStableV4ClaimPacket` reports and making report-quality reject mixed blocked/allowed claim wording before any stable-v4 announcement.

Every release proposal must answer:

1. Which developer decision changes?
2. Which evidence supports that decision?
3. Which task-object fields are added or enriched?
4. What is the exact non-pass next action?
5. Which public positive and negative fixtures prove it?
6. Which existing surface should be merged, demoted, or retired?
7. What is the exit gate?
8. What is the expected model/agent budget?
9. Does normal use require a separate API key?
10. Does the feature work through the core rather than one platform-specific fork?

### v3.110-v3.114: Report-Quality Discipline

Goal: finish the current read-only ShipGuard product-QA loop without expanding the public surface.

- Promote repeated local real-app read-only report weaknesses into public synthetic fixtures.
- Keep private target-app findings framed only as ShipGuard report-quality evidence.
- Close the grouped performance observation fixture gap.
- Add performance evidence-promotion fixtures: source suspicion versus measured runtime proof.
- Tighten exact next-action checks in report-quality so every blocked/review report names owner, command/manual proof, expected artifact, success condition, and failure meaning.
- Reframe weak standalone report families as inventories when they lack runtime, screenshot, compiler, or human evidence.

Exit gate: `ios report-quality` can turn a private-app observation into a public fixture candidate, score that fixture, suppress covered repeat questions, and move to the next uncovered question without leaking private paths, identifiers, or app-specific remediation tasks.

### v3.115-v3.124: Trust Hardening And Surface Simplification

Goal: make ShipGuard feel trustworthy before adding more capability.

- Introduce one canonical `.shipguard.yml` configuration shape with safe defaults.
- Add `.shipguard-baseline.json` and justified suppressions with reason and review/expiry metadata.
- Converge transcript/report/path redaction into one shared redaction engine.
- Harden GitHub Action input handling, Devspace URL boundaries, archive extraction, package install, and release provenance failure paths.
- Move maintainer-only tools toward `shipguard dev` while keeping compatibility shims and deprecation warnings.
- Stop adding new public commands unless they directly feed `init`, `inspect`, `prepare`, `verify`, or `doctor`.

Exit gate: a new external developer can install ShipGuard, initialize a repo, run the first useful command, and understand the next step without seeing ShipYard-internal branding, app-specific templates, or report-directory maze behavior.

### v3.125-v3.139: Task Object And Core Loop

Goal: make the persistent task object the center of the product.

- Stabilize `shipguard prepare` as the task-contract writer.
- Stabilize `shipguard verify` as the diff/evidence/claim verdict reader.
- Add explicit task fields for allowed automatically, allowed after agent review, requires human approval, forbidden in this task, and manual-only proof.
- Teach existing iOS reports to enrich the task object instead of producing disconnected reports.
- Add `inspect --profile ios` as the clearer long-term route for topology and ownership discovery while preserving current iOS commands as compatibility/check-pack paths.
- Make every non-pass verdict return one `nextAction` with owner, command or manual proof, expected artifact, success condition, and failure meaning.

Exit gate: one task can be prepared, edited by Codex, verified against a diff and evidence receipts, and returned as PASS, REVIEW, or BLOCKED without the user manually stitching reports together.

### v3.140-v3.159: First Killer Workflow

Goal: make proof-gated iOS notification and permission work exceptional.

- Build a labeled fixture matrix for notification authorization states, denied-state recovery, provisional flows, scheduling truth, app lifecycle, background/killed-state limits, and simulator versus device proof.
- Map owner files, protected boundaries, validation lanes, and manual proof requirements for the workflow.
- Generate task-specific Codex skill guidance from `prepare`.
- Verify the resulting diff, validation output, screenshots/logs, manual receipts, and agent completion claims through `verify`.
- Run external pilot tasks and record whether ShipGuard changed task scope, prevented unsafe edits, rejected overclaims, or saved review time.

Exit gate: independent iOS developers can complete risky notification/permission changes using ShipGuard without author assistance, and the labeled eval set shows the workflow improves review decisions.

### v3.160-v3.179: Diff-First Verification And Learning

Goal: answer "is this exact AI-generated change safe enough to review or merge?"

- Inspect changed files, deleted tests, entitlements, plist/config changes, validation coverage, and protected-boundary crossings.
- Compare agent claims against captured evidence and known manual-only proof.
- Use local history for accepted ownership mappings, validation commands, suppressions, recurring mistakes, and dismissed findings.
- Measure false positives, recurring dismissals, first useful result time, and recommendation follow-through locally.
- Add PR and CI adapters only after the local verdict is strong.

Exit gate: ShipGuard can explain the risk and evidence state of a real diff more usefully than a broad repo scan.

### v3.180-v3.199: Evaluated iOS Assurance Packs

Goal: add one measured iOS pack at a time after the core loop works.

- StoreKit and entitlements with sandbox transaction and entitlement fixtures.
- Persistence and migrations with compiler/test-backed migration examples.
- Widgets, App Intents, and shared state with ownership and shared-store proof.
- Background execution and lifecycle with simulator/device limitation boundaries.
- Performance only with runtime evidence promotion from source suspicion to measured proof.
- Design only with screenshots, flow context, accessibility inspection, interaction evidence, and human or calibrated model labels.
- Modernization only with compiler-backed examples and regression tests.

Exit gate: each stable pack meets its own precision, recall, actionability, and independent task-completion thresholds before being marketed as dependable.

### v4.0: Productization

Goal: ship a smaller, stable, externally usable product instead of a growing internal toolkit.

- Stable task/evidence schemas and migration tools.
- Clean install, upgrade, uninstall, and package verification.
- A narrow public command story: `init`, `inspect`, `prepare`, `verify`, `doctor`, with specialist check packs behind profiles.
- Independent benchmark results and public-safe eval corpus.
- Security posture strong enough for a proof-centered tool.
- Real external adoption and retention evidence.

Exit gate: ShipGuard is recommendable because it repeatedly catches unsafe changes, selects better proof, rejects unsupported claims, and gives exact next actions.

## Always-On Evaluation Track

Every release band keeps an eval track running beside product work:

- Gold fixtures for expected pass/review/blocked behavior.
- Negative fixtures for overclaims, unsafe edits, missing proof, stale docs, and private-data leaks.
- Mutation cases for protected-boundary bypass attempts.
- Human or expert labels for task routing, design quality, and next-action usefulness.
- Model critique recorded as evaluator metadata, not hard truth until calibrated.
- Precision, recall, false-positive dismissal rate, exact next-action completeness, independent task completion, and time-to-first-useful-result tracking.

Suggested stable-rule targets:

| Metric | Target |
| --- | ---: |
| Blocking finding precision | >= 90% |
| Critical benchmark recall | 100% |
| Overall actionable precision | >= 80% |
| False-positive dismissal rate | < 15% |
| Exact next-action completeness | 100% |
| Independent task completion | >= 80% |
| Median first useful result | < 5 minutes |

## Now

- Keep the CLI stable for `init`, `validate`, `doctor`, and `score`.
- Keep Agent Autopsy stable for Markdown and JSON reports from run summaries, diffs, tasks, and test logs.
- Keep autopsy artifact generation available through GitHub Actions.
- Keep Maintainer Arena fixture aggregation stable for public benchmark examples.
- Keep Maintainer Arena comparison output stable for benchmark regression reviews.
- Keep Maintainer Arena comparison action output aligned with the CLI compare command.
- Keep transcript redaction and verification output stable enough for safe public examples and benchmark notes.
- Keep transcript verification action output aligned with the CLI verifier.
- Keep transcript corpus indexing and checked demo output strict enough for public-safe maintainer example collections.
- Keep transcript corpus action output aligned with the CLI corpus verifier.
- Keep frontend, backend, CLI, and docs release-proof arena cases in the public benchmark fixture pack.
- Keep PR review-comment output stable for warn/fail adoption.
- Keep leaderboard schema `1.0` stable for public benchmark consumers.
- Keep policy config plain, auditable, and non-executable.
- Keep CI gate outputs stable for artifact and PR workflows.
- Keep CI step-summary output readable in GitHub Actions workflow runs.
- Keep GitHub Check Run payload export stable and opt-in.
- Keep optional GitHub Check Run posting explicit, token-scoped, and disabled by default.
- Keep SARIF export stable for Autopsy findings and CI gate artifacts.
- Keep local Markdown link audits dependency-free and strict enough for docs-heavy release work.
- Keep external arena fixture import strict about supported files and obvious secret leakage.
- Keep fixture-pack integrity and optional signer metadata deterministic and verifiable.
- Keep self-audit output stable enough to prove release readiness from source and extracted packages.
- Keep next-goal output deterministic enough to restart the improvement loop after each release, including scoped plans, completion receipts, and following-goal handoffs when evidence is supplied.
- Keep `shipguard prepare` and `shipguard verify` as the first public core loop: prepare writes one durable task object with repo context, risk, authorized files, protected boundaries, validation contract, tracked claims, and next action; verify checks the exact diff, evidence receipts, and claims against that object before returning pass, review, or blocked.
- Keep value-gauntlet runtime proof moving beyond names: adoption receipts prove a fresh package can be installed from an extracted tarball, paired with a fresh Codex plugin cache, used for a first Brand Deck audit, and routed through report-quality to the next action. Target-onboarding receipts prove a fresh iOS app repo can install starter files, pass starter doctor, validate the toolkit, run iOS doctor/inventory, and get the first scoped permission-audit plan without maintainer context. Multi-profile onboarding receipts now prove iOS, web, backend, and CLI starter profiles each install, pass doctor, and leave `SHIPGUARD_PROFILE.md` next commands. Profile-native first-audit receipts now prove web, backend, and CLI targets get real WebScan, ServiceRadar, and CommandLens reports beyond init/doctor starter files, while the scanners exclude generated ShipGuard starter files from target validation and risk signals. Profile-native fix-plan receipts now prove those first audits become WebForge, ServiceForge, and CommandForge scoped tasks with validation commands, stop conditions, and report-quality handoff. Profile-native validation receipts now prove those plans classify runnable, blocked, manual, and unchecked validation lanes without executing arbitrary target commands. Profile-native validation rerun receipts now prove blocked lanes expose the smallest repair and clear after rerunning the plan. Profile-native proof handoff receipts now prove repaired plans emit copy-ready evidence packets for Codex and maintainers. Command-family runtime-output receipts now prove major report-producing families emit useful JSON/Markdown output, not only `--help` wiring. Trust-hardening receipts now prove GitHub Action input handoff, Devspace public URL boundaries, archive extraction safety, and release provenance failure paths. Task-contract receipts now prove prepare/verify share scope, evidence, claims, and verdict through one object. The next expansion should make verification diff-first so the exact AI-generated change is explained before merge.
- Keep the ShipGuard Brand Deck naming contract current so new public surfaces get a branded name, plain purpose, proof boundary, docs coverage, skill/eval routing when needed, self-audit coverage, and package proof before release.
- Keep `ios launchdeck` as the native ShipGuard front door for LaunchDeck workflows: it should inspect repo topology, recommend XcodeBuildMCP build/run defaults, simulator browser proof, SwiftUI preview hot reload, debugger/log capture, and profiler routes, while keeping execution ownership in Codex iOS execution tools and proof/report ownership in ShipGuard.
- Keep improving `ios launchdeck --receipt` until every LaunchDeck execution lane has concrete receipt grading: build/run logs, UI snapshots, simulator-browser frames, SwiftUI hot-reload output, profiler traces, fallback samples, and explicit device-only proof gaps.
- Grow public report-quality fixtures for LaunchDeck receipt gaps so private-app proof failures become synthetic, reusable ShipGuard tests instead of one-off notes.
- Keep iOS performance-audit routing, `ios performance` findings, `--shareable` output, and `--shipguard-eval` product-QA boundaries strict about profiler evidence, fallback samples, symbolication, before/after comparison, protected boundaries, ranked source hotspots, impact explanations, high-severity reasons, Codex-local versus manual/device proof boundaries, grouped repeated-rule action plans with smallest first experiments, validation routes, stop conditions, private-app read-only use, local-path omission before report-quality scoring or external planning, and physical-device proof gaps.
- Keep iOS source scanners fast and honest about scope: skip generated/proof/cache directories, report those exclusions, and keep private-app scans read-only.
- Keep `ios design` genre-aware and shareable so UI/UX, motion, haptics, preview, Devspace, and app-icon guidance changes with utility, game, health, fitness, commerce, creative, and SaaS app context; motionQualityGates should keep frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance gates native to ShipGuard reports; app-type inference should prefer app/project source over repeated instruction-document wording, and `--shareable` should omit local roots before report-quality scoring or external planning.
- Keep `--shipguard-eval` and `--shareable` supported across `ios modernize`, `ios app-intelligence`, and `ios ai-readiness` so private-app learning improves ShipGuard report quality and public fixtures without becoming target-app work or relying on accidental path safety.
- Keep `ios report-quality` strict, shareable, and actionable enough to turn private read-only report weaknesses into ShipGuard rules, docs, and public fixtures without grading or editing the scanned app; `--shareable` should omit local input/report paths from the quality artifact itself, require supported source reports to declare shareability, keep source report issues visible through `sourceFindings`, `sourceIssueVisibility`, and Markdown `Source Report Findings` without mixing them into report-quality defects, require performance and Lean Deck findings to explain why they matter in JSON and Markdown, require high performance findings to explain why severity is high in JSON and Markdown, require performance proof guidance to separate local Codex proof from manual/device proof in JSON and Markdown, require repeated performance and Lean precision rules to have grouped JSON and Markdown actions with smallest first experiments, validation routes, and stop conditions, emit fixture candidates for public synthetic eval coverage, materialize those candidates into path-safe starter files when requested, emit and consume promotion manifests and review checklists for those materialized fixtures without auto-copying them into the repo, avoid recursive fixture candidates when a materialized synthetic fixture is scored again, and make the next ShipGuard improvement explicit through `priorityAction` plus prioritized actionability questions.
- Keep report-quality shareability checks aligned with Devspace-style connector risks: token-bearing URLs must be blocked before sharing and redaction commands should be explicit.
- Keep `ios devspace-check` useful as a ShipGuard-only connector readiness report for loopback defaults, bearer auth, MCP widget metadata, screenshot token handling, semantic target resolution, Codex handoff boundaries, public URL safety, preview handoff fixture quality, shareable report output, and honest ChatGPT model-boundary language.
- Keep `ios external-audit` as the native adoption gate for Spec Kit, CodexPro, Ponytail, Expo, Design Motion Principles, native iOS workflow skills, X posts, and other external workflow ideas: source inputs should become a capability matrix, replacement ledger, implementation backlog, license boundary, and report-quality questions before ShipGuard claims an idea is integrated, and routing evals should keep external-source adoption from drifting into Devspace or generic planning.
- Keep the ShipGuard-native spec workflow useful for turning report-quality questions into constitution/spec/requirements-checklist/native-integration-decisions/plan/tasks/consistency-analysis artifacts and CodexPro-style Devspace guardrails without vendoring external code or weakening local proof, redaction, and read-only product-QA boundaries; shareable spec workflows should stay grounded in report input and actionability questions, and report-quality should verify the declared artifact files are present, preserve the report-quality questions in clarifying questions, acceptance criteria, checklist coverage, integration decisions, consistency analysis, proof-gated tasks, exact validation commands, and analysis gates, and contain expected headings, proof cues, replacement/evaluation decisions, and guardrails before adoption passes.
- Keep iOS, web, backend, and CLI starter profiles stable for external repository adoption.
- Keep release packaging and installer scripts reproducible.
- Keep release manifests and proof ledgers reproducible from local release artifacts.
- Keep release proof indexes deterministic and based on verified manifests.
- Keep release replay reports deterministic for downloaded tarball, manifest, index, and ledger assets.
- Keep release attestations compact, deterministic, and derived from passing replay proof.
- Keep release-proof GitHub Action output aligned with the CLI proof chain.
- Keep release-proof workflow examples copy/paste-safe for tag-triggered and manual release proof runs.
- Keep the one-command release proof bundle aligned with the manual CLI chain and GitHub Action.
- Keep downstream release proof consumption docs aligned with the published tarball, replay, and attestation assets.
- Keep release-consume output aligned with the documented downstream verification path.
- Keep published proof asset cross-checks strict enough to catch replay, attestation, and badge mismatches.
- Keep release asset digest matrices explicit about every known release asset, SHA-256, byte count, and required/optional status.
- Keep release-consume GitHub Action output aligned with the CLI consumer proof chain.
- Keep release-diff audits useful for comparing published release proof bundles across versions.
- Keep release-diff GitHub Action output aligned with the CLI diff audit.
- Keep release evidence site exports static, self-contained, and derived from verified proof reports.
- Keep release evidence indexes static, browsable, and sorted newest-to-oldest by release version.
- Keep release evidence bundles aligned with release-consume, release-diff, site, and index output.
- Keep release-evidence GitHub Action output aligned with the CLI site, index, and bundle exporters.
- Keep release-evidence artifact verification aligned with downloaded GitHub Actions artifacts.
- Keep release-evidence verification workflows concise enough to consume uploaded artifacts without custom glue steps.
- Keep release-evidence negative fixtures current so blocked verification paths stay explicit and reproducible.
- Keep release-evidence negative fixture indexes current so intentional failure coverage is reviewable from one report.
- Keep release-evidence negative fixture index action output aligned with the CLI guardrail index.
- Keep release-evidence negative fixture HTML reports static, dependency-free, and aligned with JSON and Markdown outputs.
- Keep the reusable GitHub Action aligned with the CLI validator.
- Maintain the public examples, scorecard, autopsy fixtures, and iOS starter template as the workflow evolves.
- Keep the adoption docs and GitHub Pages shell current with each release.
- Keep ShipGuard's open-source operating surface complete: README, license, contribution guide, support policy, governance, code of conduct, security policy, issue templates, package proof, and docs index should all ship together.

## Next

- Add more anonymized transcript cases only when they can be fully redacted and verified through the corpus gate.
- Expand Maintainer Arena with more task types and stronger fixture provenance only when the fixture contract needs it.
- Add more specialized profiles only when they have clear maintainer workflows.
- Consider npm or Homebrew distribution after the release tarball path stays stable.
- Enable GitHub Pages in repository settings after the docs shell is reviewed.

## Later

- Publish a small collection of anonymized maintainer workflows from real production app work.
- Add stricter markdown linting and shell linting when dependency cost is justified.
- Build a comparison matrix against other agent-workflow formats.
