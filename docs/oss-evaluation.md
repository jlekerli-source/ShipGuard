# ShipGuard Evaluation

Generated: 2026-06-17

This is the current usefulness and refinement evaluation for ShipGuard after the rename and README repositioning work.

## Current Full Audit Fixture Promotion

## Current Verify-First Structured Receipt Proof-Lane QA

The v3.159 read-only verify-first loop stayed ShipGuard-only and used the public quickstart reports to test whether report-quality can distinguish real notification-permission proof from a generic green log.

- Finding: the task contract already carried notification permission receipt requirements in JSON, but report-quality did not enforce that prepare/verify reports expose permission-state and denied-state proof lanes clearly enough for a fresh maintainer.
- Product weakness: a generic test log can look like progress unless the report says that permission-state and denied-state behavior need structured receipt scope labels before claims can move beyond review.
- Native fix: `shipguard prepare` Markdown now renders receipt success and failure meanings, and `ios report-quality` fails prepare/verify reports that hide structured receipt requirements, generic-log boundaries, proof-lane status, or the matching Markdown.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-prepare-did-verify-require-permission-state-a-aa77287a` promotes the proof-lane question into public synthetic coverage without copying private app code.

Fresh verify-first QA now treats durable-object replay, unsupported-claim replay, notification scope, and structured receipt proof-lane specificity as covered, so the next useful question is the simulator denied-state versus physical-device prompt boundary.

## Current Stable Publication Launch Relay QA

The v3.156 read-only ShipGuard self-QA loop moved from verify-first quickstart into the launch boundary described in the roadmap: major milestones need launch drafts, but public posting must remain approval-gated.

- Finding: `v4 stable-publication` could produce release proof packets and draft release notes, but it did not give maintainers a guarded Product Hunt, r/ShipGuard, X, or Hacker News launch relay packet.
- Product weakness: without a machine-readable launch boundary, a future computer-use or promotion workflow could blur "prepare draft copy" into "post publicly" even though public account-visible actions require explicit approval for the exact launch run.
- Native fix: `shipguard v4 stable-publication` now writes `stable-publication-launch-relay/` with draft-only channel copy, `approvalRequired: true`, `publicPostingAllowed: false`, and `computerUseMayPost: false`.
- Report-quality fix: `ios report-quality` now flags stable-publication reports that declare launch-relay actionability but omit the launch packet, weaken the explicit approval gate, allow public posting, or hide the boundary in Markdown.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f059d5b6` promotes the guarded launch relay question into public synthetic coverage.

Fresh stable-publication QA can now keep launch copy useful without turning ShipGuard into an autoposting tool or bypassing user approval.

## Current Ponytail SourceScout Surface-Proof QA

The latest read-only Ponytail QA pass refreshed the installed Codex Ponytail marketplace, inspected the public Ponytail checkout, then ran `shipguard ios external-audit`, `shipguard lean audit`, `shipguard lean review`, and `ios report-quality --write-fixture-candidates` against this checkout.

- Finding: SourceScout recognized Ponytail and produced the right native replacement ledger, but every Ponytail capability had `surfacePresent: false` because the detector only compared hidden script paths against prose such as `lean audit`, `lean review`, and `codex status`.
- Product weakness: ShipGuard could claim a capability had a native action while the machine-readable proof bit said the surface was missing, making the adoption ledger harder to trust.
- Native fix: `ios external-audit` now maps capability prose to stable ShipGuard command aliases and renders whether the native surface is present in Markdown.
- Guardrail: adopted external capabilities now produce an `external-adoption-surface-unproven` finding when no detected ShipGuard surface backs the claim.

Fresh Ponytail SourceScout QA now reports all five Ponytail capabilities as native-surface present while keeping Ponytail as a named MIT influence rather than vendoring its hooks, commands, or skills.

## Current Lean Deck Priority Question Fixture QA

The v3.138 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout.

- Finding: fresh Lean Deck reports scored cleanly, but the top ranked actionability question, "Does precisionReview identify delete, simplify, keep, and proof-blocked decisions instead of dumping findings?", did not materialize as a public fixture candidate.
- Product weakness: the report told maintainers to convert the top question into a fixture, but `--write-fixture-candidates` produced zero candidates, forcing manual interpretation or a broader spec-workflow detour.
- Native fix: `ios report-quality` now treats Lean Deck priority wording such as `precisionReview`, proof-blocked decisions, safety-boundary separation, host adapters, hardware calibration, same-diff proof signals, runnable checks, and benchmark-honesty prompts as Lean report-quality fixture candidates.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-precisionreview-identify-dele-286dc4bb` promotes the top Lean question into public synthetic coverage, so fresh Lean QA can advance to the next uncovered Lean question and materialize it as `shipguard-lean-report-quality-fixture`.

Fresh QA now proves Lean Deck questions can move from ranked report-quality output into public fixtures without depending on private app scans or manual fixture taxonomy decisions.

## Current Lean Deck Safety-Boundary Fixture QA

The v3.139 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout after the first Lean Deck priority fixture landed.

- Finding: fresh Lean Deck QA passed, but the next uncovered actionability question was "Does Lean Deck separate real simplification candidates from safety-boundary files?"
- Product weakness: without a promoted public fixture, report-quality could keep asking the same safety-boundary separation question instead of advancing to the next useful Lean Deck gap.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-deck-separate-real-simpl-fa325230` now uses public synthetic evidence with one native simplification candidate and one trust-boundary keep/proof lane.
- Guardrail: the fixture exposes `Behavior Gates` in Markdown and `behaviorGates` in JSON, so the human-facing report must preserve host-adapter, hardware-calibration, requested-explanation, one-runnable-check, gain-honesty, and shortcut-debt boundaries.

Fresh QA now treats the safety-boundary separation question as covered and advances to the host-adapter, hardware-calibration, requested-explanation, and one-check protection question.

## Current Lean Deck Host-Adapter Fixture QA

The v3.140 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout after the safety-boundary fixture landed.

- Finding: fresh Lean Deck QA passed, but the next uncovered actionability question was "Does Lean Deck protect host adapters, hardware calibration, requested explanation, and one-check minimums from false less-code pressure?"
- Product weakness: generated fixture starters preserved the question but did not expose the behavior gates that explain why these lanes are protected, so the starter itself scored `review`.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-deck-protect-host-adapte-6c18ff70` now uses public synthetic evidence for four protected lanes: host adapter, hardware calibration, requested explanation, and one runnable check.
- Guardrail: the fixture keeps `behaviorGates` in JSON and `Behavior Gates` in Markdown, plus grouped action plans that tell maintainers what proof is needed before deleting or simplifying those lanes.

Fresh QA now treats the host-adapter protection question as covered and advances to the solo-developer deletion-usefulness question.

## Current Lean Deck Deletion-Usefulness Fixture QA

The v3.141 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout after the host-adapter fixture landed.

- Finding: fresh Lean Deck QA passed, but the next uncovered actionability question was "Does the report help a solo developer delete clutter without deleting product behavior?"
- Product weakness: a starter fixture preserved the question but did not make behavior gates visible enough, so the report could still feel like less-code pressure instead of a safe solo-developer decision map.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-the-report-help-a-solo-develo-e645ec7e` now uses public synthetic evidence for delete, simplify, keep, and proof-blocked lanes.
- Guardrail: the fixture keeps `Behavior Gates`, a grouped action plan, and a solo-developer decision map in Markdown, while JSON preserves `behaviorGates`, `precisionReview.actionGroups`, and explicit ShipGuard-only scope.

Fresh QA now treats the deletion-usefulness question as covered and advances to the `leanDebtLedger` shortcut-audit question.

## Current Lean Deck Shortcut-Ledger Fixture QA

The v3.142 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout after the deletion-usefulness fixture landed.

- Finding: fresh Lean Deck QA passed, but the next uncovered actionability question was "Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?"
- Product weakness: generated fixture starters preserved the question but did not prove the actual shortcut-ledger contract, so a report could look useful while hiding marker status, ceilings, upgrade triggers, or the Markdown table.
- Native fix: `ios report-quality` now flags Lean Deck and Lean Debt reports that omit `leanDebtLedger` summary counts, marker fields, trigger status, or Markdown ledger visibility.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-leandebtledger-make-intention-e856e9a3` uses public synthetic evidence for one tracked shortcut and one `needs-trigger` shortcut.

Fresh QA now treats the shortcut-ledger question as covered and advances to the Lean Gain fake-savings question.

## Current Lean Gain Honesty Fixture QA

The v3.143 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, `shipguard value-gauntlet`, and `ios report-quality --write-fixture-candidates` against this checkout after the shortcut-ledger fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?"
- Product weakness: the generated fixture starter preserved the question but did not prove the actual Lean Gain contract, so a report could make benchmark impact look like measured current-repo savings.
- Native fix: `ios report-quality` now flags Lean Gain reports that omit benchmark scope, benchmark metrics, the `not-computed` current-repo boundary, current-repo evidence routes, or Markdown no-claim language.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-gain-avoid-fake-per-repo-08315752` uses public synthetic evidence for a benchmark scoreboard plus explicit no-current-repo-savings boundary.

Fresh combined Lean QA now treats the fake-savings question as covered and advances to the Lean Gain current-repo evidence-routing question.

## Current Lean Gain Evidence-Routing Fixture QA

The v3.144 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the Lean Gain honesty fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does it route current-repo evidence back to lean audit, lean review, and lean debt?"
- Product weakness: Lean Gain named those signals but did not give maintainers a copy-ready route showing which command to run, what artifact to expect, and what each route does not prove.
- Native fix: `shipguard lean gain` now emits `currentRepoBoundary.evidenceRoutes` for `lean audit`, `lean review`, and `lean debt`, each with command, expected artifact, answer, proof boundary, and non-claim text.
- Report-quality fix: `ios report-quality` now flags Lean Gain reports that omit the route contract, omit a route, hide command/artifact/answer fields, or fail to block savings overclaims in route boundaries and Markdown.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-gain-does-it-route-current-repo-evidence-9bae8f6f` uses public synthetic evidence for the structured route contract.

Fresh combined Lean QA now treats the current-repo evidence-routing question as covered and advances to the Lean Review current-diff usefulness question.

## Current Lean Review Current-Diff Fixture QA

The v3.145 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the Lean Gain evidence-routing fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?"
- Product weakness: Lean Review had a precision ledger and grouped plan, but the report did not expose a dedicated current-diff-only decision map that says which changed files are delete, simplify, keep, proof-blocked, or clean.
- Native fix: `shipguard lean review` now emits `currentDiffDecisionMap` with `scope: current-diff-only`, changed-file rows, a delete/simplify subset, whole-repo non-claims, and a `shipguard lean audit` fallback for maintainers who actually need a repo inventory.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that omit the map, use a repo-inventory scope, hide decision rows, hide the delete/simplify subset, or omit the Markdown `Current Diff Decision Map`.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-give-a-current-d-9a6d6c8a` uses public synthetic evidence for current-diff delete, simplify, and keep decisions.

Fresh combined Lean QA now treats the current-diff usefulness question as covered and advances to the Lean Review runnable-check question.

## Current Lean Review Runnable-Check Fixture QA

The v3.146 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the current-diff fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does Lean Review require one smallest runnable check for non-trivial new logic?"
- Product weakness: Lean Review had proof-signal calibration, but same-diff proof was too coarse if any test file appeared in the diff, and the public fixture generator still produced a current-diff fixture rather than a runnable-check fixture.
- Native fix: `shipguard lean review` now matches same-diff proof signals to the changed file, emits `runnableCheckReview` with missing-proof rows, same-diff proof rows, duplicate-ceremony avoidance, and Markdown tables, and keeps unrelated tests from hiding missing proof on another changed file.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that omit `runnableCheckReview`, hide missing-proof rows, hide same-diff proof rows, omit duplicate-ceremony counts, or skip the Markdown `Runnable Check Review`.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-require-one-smal-247885c9` uses public synthetic evidence for both cases: one non-trivial route branch that still needs one smallest runnable check and one selection branch with a matching same-diff test signal.

Fresh combined Lean QA now treats the runnable-check question as covered and advances to the proof-signal calibration question.

## Current Lean Review Proof-Signal Fixture QA

The v3.147 read-only loop reran the Lean Deck self-QA set after the runnable-check fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?"
- Product weakness: Lean Review counted raw proof signals and covered findings, but the report did not show the exact matched versus unmatched proof-signal map that proves unrelated tests are not global proof.
- Native fix: `shipguard lean review` now emits `proofSignalMatching` with file-scoped rows, matched same-diff proof files, missing-proof files, unmatched proof signals, and a non-global proof boundary.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that omit `proofSignalMatching`, hide matched or missing rows, hide unmatched proof signals, miscount matched plus unmatched signals, omit the non-global boundary, or skip the Markdown `Proof Signal Matching` section.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-proofsignalcalibration-disti-013d0422` uses public synthetic evidence for all three lanes: one route branch still missing proof, one selection branch matched to its same-diff test, and one unrelated smoke test listed as unmatched.

Fresh combined Lean QA now treats the proof-signal calibration question as covered and advances to the hardware-boundary question.

## Current Lean Review Hardware Boundary Fixture QA

The v3.148 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the proof-signal fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does Lean Review protect hardware calibration and host boundaries from false less-code pressure?"
- Product weakness: Lean Review had behavior gates and generic hardware findings, but it did not expose a first-class packet that says which hardware rows are proof-blocked and which host/plugin/MCP/preview adapter rows should be kept until protocol or runtime proof exists.
- Native fix: `shipguard lean review` now emits `hardwareHostBoundaryReview` with hardware calibration rows, host-adapter keep rows, false less-code pressure counts, and Markdown tables for `Hardware Calibration Proof` and `Host Adapter Boundaries`.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that have hardware or host-adapter findings but omit the packet, undercount rows, hide calibration or adapter policy, or skip the Markdown boundary review.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-protect-hardware-c8a9af68` uses public synthetic evidence for two protected lanes: one sensor calibration row that stays proof-blocked and one plugin host adapter row that stays keep-with-proof.

Fresh combined Lean QA now treats the hardware-boundary question as covered and advances to the safety-boundary question.

## Current Lean Review Safety Boundary Fixture QA

The v3.149 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the hardware/host boundary fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does it keep safety-boundary code out of automatic deletion?"
- Product weakness: Lean Review had generic safety findings, but it did not expose a first-class packet that proves permission, security, validation, accessibility, and data-loss rows are keep-with-proof decisions instead of cleanup targets.
- Native fix: `shipguard lean review` now emits `safetyBoundaryReview` with safety keep rows, no-automatic-deletion policy, false deletion pressure counts, and Markdown `Safety Boundary Review` / `Keep With Proof Boundaries` tables.
- Detector fix: safety-boundary findings are now limited to code or explicit safety/privacy configuration surfaces, so public fixture report prose does not create noisy keep rows during ShipGuard self-review.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that have safety-boundary findings but omit the packet, undercount rows, hide policy, contradict the current-diff decision map, or skip the Markdown boundary review.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-it-keep-safety-boundary-code-df36ee0b` uses public synthetic evidence for one permission-gate row that stays `keep`.

Fresh combined Lean QA now treats the safety-boundary question as covered and advances to the selected-mode question.

## Current Lean Review Mode Bias Fixture QA

The v3.150 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the safety-boundary fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does Lean Review expose the selected lite/full/ultra mode and bias first actions accordingly?"
- Product weakness: Lean Review wrote `leanMode`, but report-quality did not yet prove that the selected mode actually changed the first action source or that the supported `lite`, `full`, and `ultra` contracts were visible in JSON and Markdown.
- Native fix: `shipguard lean review` now emits `modeBiasReview` with selected priority order, expected first source, selected top-action match proof, and a supported-mode matrix for `lite`, `full`, and `ultra`.
- Report-quality fix: `ios report-quality` now flags Lean Review reports that omit `modeBiasReview`, mismatch `leanMode` and `precisionReview.mode`, use the wrong first-action bias, hide the Markdown mode-bias section, or order `precisionReview.topActions` against the selected mode.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-expose-the-selec-bb4e13be` uses public synthetic evidence to prove the selected-mode contract without private app code.

Fresh combined Lean QA now treats the selected-mode question as covered and advances to the Lean Debt marker-visibility question.

## Current Lean Debt Marker Visibility Fixture QA

The v3.151 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the selected-mode fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does Lean Debt make every shortcut marker visible with a ceiling and upgrade trigger?"
- Product weakness: standalone Lean Debt had the raw `leanDebtLedger`, but it did not expose a first-class review packet that proved marker rows, ceilings, upgrade-trigger status, omitted rows, and missing-trigger rows were visible in JSON and Markdown.
- Native fix: `shipguard lean debt` now emits `markerVisibilityReview` with total, visible, omitted, ceiling, missing-ceiling, upgrade-trigger, missing-trigger, and upgrade-status counts plus row-level `visibilityRows`.
- Report-quality fix: `ios report-quality` now flags standalone Lean Debt reports that omit the marker-visibility review, miscount the ledger, hide row fields, or skip the Markdown `Marker Visibility Review`.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-debt-does-lean-debt-make-every-shortcut-034a83d4` uses public synthetic evidence for one tracked shortcut and one `needs-trigger` shortcut.

Fresh combined Lean QA now treats the marker-visibility question as covered and advances to the Lean Debt benchmark-savings honesty question.

## Current Lean Debt Benchmark-Savings Honesty Fixture QA

The v3.152 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the marker-visibility fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Does it avoid pretending benchmark savings are measurable in this repo?"
- Product weakness: standalone Lean Debt showed shortcut marker counts but did not yet carry its own no-savings boundary, so a downstream report could reframe marker counts as line, token, cost, or time savings.
- Native fix: `shipguard lean debt` now emits `currentRepoBoundary` with `perRepoSavingsClaim: not-computed`, `evidenceType: shortcut-ledger-only`, explicit no-claim text, and a `lean gain` benchmark route.
- Report-quality fix: `ios report-quality` now flags standalone Lean Debt reports that omit, weaken, or under-render the benchmark-savings boundary.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-debt-does-it-avoid-pretending-benchmark-e86ef9dc` uses public synthetic evidence to prove marker counts remain ledger evidence and do not become fake benchmark savings.

Fresh combined Lean QA now treats the benchmark-savings honesty question as covered and advances to the Lean Debt rot-risk visibility question.

## Current Lean Debt Rot-Risk Visibility Fixture QA

The v3.153 read-only loop reran `shipguard lean audit`, `shipguard lean review`, `shipguard lean gain`, `shipguard lean debt`, and `ios report-quality --write-fixture-candidates` against this checkout after the benchmark-savings fixture landed.

- Finding: fresh combined Lean QA passed, but the next uncovered actionability question was "Can a maintainer tell which marker will rot without another source inspection pass?"
- Product weakness: standalone Lean Debt could show every shortcut marker and its savings boundary, but it still did not rank which marker would rot first or explain the next proof-backed action.
- Native fix: `shipguard lean debt` now emits `rotRiskReview` with top-risk location, risk-level counts, prioritized rows, rot reasons, exact next actions, and proof guidance.
- Report-quality fix: `ios report-quality` now flags standalone Lean Debt reports that omit, miscount, under-render, or weaken the rot-risk review.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-debt-can-a-maintainer-tell-which-marker-f778022c` uses public synthetic evidence to prove a `needs-trigger` marker is prioritized before a tracked trigger-watch marker.

Fresh combined Lean QA now treats the rot-risk visibility question as covered and advances to the Lean Debt trigger-rot next-action question.

## Current Lean Debt Trigger-Rot Next-Action Fixture QA

The v3.154 read-only loop reran `shipguard lean debt` and `ios report-quality --write-fixture-candidates` against public synthetic shortcut markers after the rot-risk fixture landed.

- Finding: fresh Lean Debt reports now ranked the first marker, but tracked rows still needed a machine-readable trigger-watch contract so tooling could prove the exact condition, check route, proof artifact, and stop condition.
- Product weakness: prose such as "watch the trigger" was useful to a human but too weak for report-quality, fixture promotion, and future agent routing.
- Native fix: `shipguard lean debt` now emits `triggerWatchContract` on each `rotRiskReview.prioritizedRows[]` item with trigger state, trigger condition, exact next action, check route, proof artifact, and stop condition.
- Report-quality fix: `ios report-quality` now flags standalone Lean Debt reports that omit or under-render the trigger-watch contract in JSON or Markdown.
- Fixture fix: `fixtures/ios-report-quality/01-shipguard-lean-debt-does-each-rot-risk-row-give-the-exa-691cec38` uses public synthetic evidence to prove the trigger-rot next-action question without private app source.

Fresh combined Lean QA now treats the trigger-rot next-action question as covered instead of materializing a duplicate candidate.

## Current Verify-PR First-Run QA

The v3.198 read-only loop ran `shipguard inspect`, `shipguard value-gauntlet`, `shipguard full-audit --plan-only`, docs-check, and the verify-first quickstart tests against this checkout.

- Finding: the verify-first demo and `examples/workflows/verify-pr.yml` were covered by tests, but a fresh maintainer had no ShipGuard command that audits a copied GitHub Actions verify-PR workflow before trusting it.
- Product weakness: first-run users could copy the starter with the placeholder validation command or accidentally remove the task, diff, receipt, verify, or artifact-upload chain and only discover the mistake after a failed GitHub run.
- Native fix: `shipguard action verify-pr` now writes `action-verify-pr.json` and `action-verify-pr.md`, blocks missing proof wiring, returns `review` while `replace-with-your-test-command` is still present, and marks runtime PR artifact proof as required before trust.
- Boundary: the command is read-only. It does not execute target tests, push code, or claim the GitHub workflow has run.

Fresh QA now runs the action audit over the bundled starter, a configured copy, and a broken workflow fixture before treating the first PR-proof path as healthy.

## Current Verify-PR Runtime Artifact QA

The v3.199 read-only loop reran the configured Verify-PR static audit, `shipguard inspect`, `shipguard value-gauntlet`, and `ios report-quality` over the current action report.

- Finding: the static Verify-PR report correctly ended at `gh run download`, but ShipGuard did not yet have a native way to consume the downloaded `shipguard-verdict` artifact and prove that the JSON/Markdown proof packet was complete enough for review.
- Product weakness: a fresh maintainer could see a structurally valid workflow and still manually inspect a partial, wrong, duplicated, or decorative artifact without ShipGuard catching that the runtime proof packet was unusable.
- Native fix: `shipguard action verify-pr --artifact-dir <downloaded-artifact-dir>` now consumes the downloaded artifact, checks `shipguard-verdict.json`, Markdown, `tool: shipguard verify`, known verdict status, proof report, validation coverage, v2 evidence schema, diff-first merge verdict, and reviewer next action.
- Boundary: artifact consumption proves the CI proof packet is readable and routable. It does not approve the PR, execute target tests locally, or turn the runtime verdict status into a merge claim.

Fresh QA now runs the action audit over static, valid-runtime, broken-runtime, and broken-workflow fixtures before treating the first PR-proof path as healthy.

## Current Verify-PR Fresh Maintainer Failure Guidance QA

The v3.201 read-only loop reran `shipguard action verify-pr` over the starter workflow, configured workflow, valid runtime artifact, broken runtime artifact, and broken workflow fixture, then graded the reports with `ios report-quality`.

- Finding: the broken workflow report was blocked but its next action could point at a lower-severity checkout review before the first real blocker.
- Finding: a shareable broken-runtime report still carried an absolute local path in one artifact finding.
- Product weakness: a fresh maintainer needs the first real fix and the static-versus-runtime proof lane immediately, without local path leakage or generic checklist noise.
- Native fix: `shipguard action verify-pr` now emits `freshMaintainerFailureGuide`, separates static workflow setup from runtime artifact proof, routes blocked reports to the first blocking rule, and uses path-safe artifact evidence under `--shareable`.
- Fixture fix: report-quality now enforces the failure guide and two public fixtures cover the fresh-maintainer explanation question and first-blocker-before-review question.

Fresh QA now runs the broken workflow and broken runtime artifact through report-quality before treating Verify-PR guidance as useful for new maintainers.

## Current Verify-PR Runtime Reviewer Handoff QA

The v3.202 read-only loop reran `shipguard action verify-pr` over configured static setup, valid runtime artifact, and broken runtime artifact fixtures, then graded the reports with `ios report-quality`.

- Finding: a passing runtime artifact report was structurally correct but still told reviewers to "use the verdict status to decide" and exposed a rerun command instead of a reviewer-ready decision.
- Product weakness: a maintainer reviewing a first ShipGuard PR needs the artifact translated into ready-for-maintainer-review, needs-review, do-not-merge, or do-not-use-artifact, plus the exact proof files to attach and what failure means.
- Native fix: `shipguard action verify-pr` now emits `runtimeReviewerHandoff`, extracting verdict status, diff-first merge verdict, validation coverage, v2 schema, proof-to-attach files, reviewer action, failure meaning, and a read-only PR state command.
- Report-quality fix: `ios report-quality` now flags runtime artifact reports that omit the reviewer handoff, omit its Markdown section, hide proof-to-attach, or route invalid artifacts to anything other than a do-not-use/do-not-merge decision.

Fresh QA now treats a passing artifact as proof routing for human review, not automatic merge permission.

## Current Ponytail Behavior-Gate QA

The v3.200 read-only QA pass inspected the public Ponytail repo and ran ShipGuard's native Lean Deck against both this checkout and the public Ponytail checkout.

- Finding: ShipGuard already had the core ladder, diff review, shortcut debt, and safety boundaries, but it lacked behavior gates for one runnable check, hardware calibration, requested explanation, adapter boundaries, and benchmark-gain honesty.
- Finding: running Lean Deck on the public Ponytail repo produced thin-wrapper noise on plugin, hook, MCP, and agent-host adapters; those are often the product boundary rather than needless helpers.
- Product weakness: without explicit gates, "less code" can become false pressure to delete host adapters, physical-world calibration knobs, explicitly requested reports, or the single check that proves non-trivial logic.
- Native fix: `shipguard lean audit` and `shipguard lean review` now emit `behaviorGates`, Lean Deck keeps adapter/hardware calibration surfaces as proof-required boundaries, and `shipguard lean gain` reports benchmark direction without inventing per-repo line/token/cost/time savings.
- Boundary: ShipGuard remains native and does not vendor Ponytail source. The source influence stays explicit, and any copied/adapted content must keep license boundaries honest.

Fresh QA now runs `lean audit`, `lean review`, `lean debt`, `lean gain`, report-quality, and command-family runtime-output receipts before treating precise-code work as integrated.

## Current Ponytail SourceScout QA

The next read-only Ponytail QA pass showed Lean Deck was native, but `ios external-audit` still treated a Ponytail checkout and URL as unclassified external sources. That meant ShipGuard could claim precise-code ideas were represented while its adoption ledger could not prove the source profile.

- Finding: SourceScout needed a first-class Ponytail profile rather than relying on generic external-source fallback text.
- Native fix: `shipguard ios external-audit` now recognizes Ponytail checkouts and URLs, maps the lean ladder, diff review, shortcut ledger, benchmark-honesty card, and always-on host mode into ShipGuard-native decisions, and leaves host-plugin activation as an optional separate Codex plugin path.
- Boundary: ShipGuard keeps Ponytail as a named MIT source influence and implements explicit Lean Deck reports instead of vendoring Ponytail hooks, commands, or skills.

Fresh QA now runs Ponytail-only SourceScout classification, Lean Deck self-audit, report-quality, and Codex plugin refresh proof before claiming this integration is current.

## Current Ponytail Native Precision QA

The v3.197 read-only QA pass inspected the public Ponytail repo, refreshed the installed local Codex Ponytail plugin, then ran ShipGuard's existing Lean Deck against this checkout as the native precision-code baseline.

- Finding: ShipGuard already had `lean audit`, `precisionReview`, safety-boundary handling, and a shortcut ledger, but it lacked a fast current-diff review path and a standalone debt-only command.
- Product weakness: a solo developer needs to answer "what in this change can be deleted or avoided?" before merge without reading a whole-repo audit. They also need a shortcut ledger without running the entire audit.
- Native fix: `shipguard lean review` now writes `lean-review.json` and `lean-review.md` from a unified diff, and `shipguard lean debt` now writes `lean-debt.json` and `lean-debt.md` from `ponytail:` / `shipguard-lean:` markers.
- Boundary: ShipGuard keeps Ponytail as explicit source influence and implements its own read-only report logic instead of vendoring Ponytail code or hiding attribution.

Fresh self-QA now runs `lean audit`, `lean review`, `lean debt`, and report-quality on the generated outputs before treating precise-code work as integrated.

## Current Release Proof Freshness Audit

The v3.184 read-only QA rotation generated a fresh local release package, built release proof, reshaped it into downloaded release assets, verified `release-consume`, ran package hygiene, ran LaunchKey release-candidate proof, and ran stable-publication proof. `ios report-quality` found a concrete recursive-scoring weakness:

- Finding: generated `stable-publication-release-notes/release-notes-checklist.json` was scored as a standalone ShipGuard report and blocked with `report-tool-missing`.
- Product weakness: the release-notes authoring kit is a draft attachment inside the stable-publication report, not a separate report-quality source. Scoring it recursively hides the actual root stable-publication actionability questions.

This slice fixes the boundary:

- `ios report-quality` now skips generated `stable-publication-release-notes/` directories during recursive report discovery.
- The root `v4-stable-publication.json` report remains graded, including release-notes proof, evidence packet, templates, starter kit, authoring kit, blocked claims, and next command.
- The docs now state that the generated release-notes kit is an authoring attachment, not independent proof or a separate report.

Fresh release-proof QA now passes report-quality and advances to legitimate stable-publication fixture candidates instead of a false metadata block.

## Current V4 Preview Fixture Taxonomy Promotion

The next read-only QA rotation used `inspect`, `codex marketplace-readiness`, and `v4 preview` as fresh ShipGuard product-QA sources after MarketplaceDeck and DocsLink coverage landed. The reports passed, but `ios report-quality --write-fixture-candidates` exposed a reusable taxonomy weakness:

- Finding: `shipguard v4 preview` questions containing the word "preview" were materialized as generic `ios-preview-devspace-routing-fixture` candidates.
- Product weakness: v4 product-contract reports need their own fixture family, otherwise release-readiness and preview-only stability questions get mixed with iOS simulator preview and Devspace visual-planning routing.

This slice fixes the classifier precedence:

- `shipguard v4 preview` claims, stability, and preview-only questions now materialize as `shipguard-v4-preview-quality-fixture`.
- Private-app boundary questions keep the stronger `shipguard-eval-boundary-fixture` classification.
- Public fixtures now cover v4 runnable-command backing, stable-versus-preview-only clarity, concrete next proof-step guidance, and private-app observation boundaries.
- Fresh `v4 preview` report-quality runs now return `all-actionability-covered` instead of generating duplicate or misleading generic preview candidates.

This keeps the QA rotation honest about v4 product readiness without confusing it with iOS preview bridge work.

## Current DocsLink Report Contract Promotion

The next read-only QA rotation used `value-gauntlet`, `inspect`, and an actual quick `full-audit` as fresh ShipGuard product-QA sources after MarketplaceDeck became fully covered. `ios report-quality` found a concrete nested-report weakness inside the full-audit output:

- Finding: `docs-check.json` did not expose a report-quality-compatible stable report contract.
- Product weakness: full-audit embeds docs-check as release-loop evidence, but report-quality could not treat that nested report as a first-class ShipGuard report because it lacked stable metadata and result fields.

This slice upgrades `shipguard docs-check` into `ShipGuard DocsLink`:

- JSON now includes `tool`, `surface`, `schemaVersion`, `generatedAt`, `resultUX`, `scopeBoundary`, and `reportQualityQuestions`.
- Markdown now renders `Result`, `Scope Boundary`, and `Report Quality Questions`.
- `ios report-quality` recognizes `shipguard docs-check` as a root/nested report tool.
- Public fixtures cover the three docs-check report-quality questions: stable tool/result metadata, broken local-link rows, and the boundary that external URLs and in-page anchors are ignored rather than verified.

This turns a hidden full-audit nested-report blocker into reusable docs-link proof.

## Current MarketplaceDeck GitHub Presentation Fixture Promotion

The next read-only MarketplaceDeck QA pass started from a state where fresh-user comprehension, plugin install freshness, submission-packet readiness, and docs-index clarity were already covered by public fixtures. Fresh `shipguard codex marketplace-readiness` plus `ios report-quality --write-fixture-candidates` advanced to the last current MarketplaceDeck gap:

- Question: "Does the GitHub About/sidebar copy and social preview still match the latest published release without claiming unreleased v4 stability?"
- Candidate type: `shipguard-marketplace-readiness-fixture`
- Product weakness: public marketplace readiness must cover the live GitHub profile surface, not only tracked README/docs/plugin files.

This slice promotes `fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side` as public synthetic coverage. Fresh MarketplaceDeck report-quality now covers all five current MarketplaceDeck actionability questions and returns `all-actionability-covered`, which tells the maintainer to rotate to a fresh read-only ShipGuard QA source instead of re-reviewing the first covered fixture.

This keeps the public-distribution QA loop honest about GitHub-facing presentation while avoiding claims about manually changed GitHub settings beyond the tracked guidance and social-preview asset.

## Current MarketplaceDeck Docs-Index Clarity Fixture Promotion

The next read-only MarketplaceDeck QA pass started from a real product weakness: the README had been simplified, but `docs/index.md` still behaved like a command dump. `shipguard codex marketplace-readiness` and `ios report-quality` both passed before the cleanup, which showed a ShipGuard weakness rather than an app weakness:

- Question: "Can docs/index.md guide first-time users without a long command dump or stale release wall?"
- Candidate type: `shipguard-marketplace-readiness-fixture`
- Product weakness: public marketplace readiness must check human onboarding clarity, not only plugin metadata, install proof, icons, screenshots, and submission-packet fields.

This slice adds a native MarketplaceDeck public-onboarding check. `shipguard codex marketplace-readiness` now emits `publicOnboarding.docsIndex` with line, link, numbered-step, command-dump, and release-wall signals; Markdown renders a `Public Onboarding` section; strict readiness fails if the docs index becomes a giant first-run command list again.

This slice also promotes `fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi` as public synthetic coverage. Fresh MarketplaceDeck report-quality now covers fresh-user comprehension, plugin install freshness, submission-packet readiness, and docs-index clarity before advancing to GitHub About/sidebar and social-preview alignment.

## Current MarketplaceDeck Submission-Packet Fixture Promotion

The next read-only MarketplaceDeck QA pass started from the state where fresh-user comprehension and plugin install freshness were already covered by promoted public fixtures. Fresh `shipguard codex marketplace-readiness` plus `ios report-quality --write-fixture-candidates` advanced to the next marketplace-readiness gap:

- Question: "Are icon, composer icon, screenshot policy, privacy notes, model-choice boundary, and proof commands ready for a public marketplace submission packet?"
- Candidate type: `shipguard-marketplace-readiness-fixture`
- Product weakness: a public plugin submission is more than a working local install. It needs icon assets, screenshot policy, privacy/model-choice boundaries, and copy-ready proof commands to stay reviewable without overclaiming what ShipGuard can publish or which ChatGPT/Codex model a user selects.

This slice promotes `fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr` as public synthetic coverage. Fresh MarketplaceDeck report-quality now covers fresh-user comprehension, plugin install freshness, and public submission-packet readiness, then advances to the GitHub About/sidebar and social-preview alignment question.

This keeps ShipGuard's public distribution QA focused on the actual submission packet a maintainer needs, not only on local command success.

## Current MarketplaceDeck Plugin Freshness Fixture Promotion

The next read-only MarketplaceDeck QA pass started from the state where the fresh-user README/plugin-listing question was already covered by a promoted public fixture. Fresh `shipguard codex marketplace-readiness` plus `ios report-quality --write-fixture-candidates` advanced to the next public-distribution gap:

- Question: "Can a maintainer prove plugin install freshness from tracked source, local marketplace, and strict status output?"
- Candidate type: `shipguard-marketplace-readiness-fixture`
- Product weakness: a marketplace-ready Codex plugin must not only look understandable. Maintainers need a repeatable proof trail showing the installed plugin came from the tracked source, the local marketplace source is current, and strict status output confirms there is no stale plugin cache.

This slice promotes `fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu` as public synthetic coverage. Fresh MarketplaceDeck report-quality now covers both the fresh-user comprehension question and the plugin install freshness question, then advances to the public submission-packet question for icon, screenshot policy, privacy notes, model-choice boundary, and proof commands.

This keeps the public distribution QA loop focused on install trust and submission readiness instead of only README wording.

## Current MarketplaceDeck Fresh-User Fixture Promotion

The next read-only QA rotation moved beyond the saturated InspectDeck fixture set and used `shipguard codex marketplace-readiness` as the fresh root ShipGuard report source. Fresh MarketplaceDeck output plus `ios report-quality --write-fixture-candidates` exposed the next public-readiness gap:

- Question: "Can a fresh Codex user understand what ShipGuard does from the README and plugin listing without prior private-app context?"
- Initial candidate type: generic `shipguard-eval-boundary-fixture`
- Product weakness: Marketplace readiness is not only install metadata. A public Codex user must understand ShipGuard from the README, plugin listing, icon, privacy/model-choice boundaries, and proof commands without knowing the original private app history.

This slice closes the first gap:

- `ios report-quality` now classifies `shipguard codex marketplace-readiness` questions as `shipguard-marketplace-readiness-fixture` candidates.
- `fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und` promotes the fresh-user README/plugin-listing question into public synthetic coverage.
- The promoted fixture stays ShipGuard-only and public-safe, with explicit target-app read-only boundaries.
- Fresh MarketplaceDeck report-quality now covers the fresh-user question and advances to the plugin install freshness question.

This keeps the QA loop moving into public distribution quality instead of repeatedly asking whether private-app context leaked into the product story.

## Current InspectDeck Underlying-Evidence Fixture Promotion

The next read-only InspectDeck QA pass started from the v3.174 state, where the next-action/source-proof and missing-input honesty questions were already covered by public fixtures. Fresh `shipguard inspect` plus `ios report-quality --write-fixture-candidates` advanced to the last current InspectDeck actionability gap:

- Question: "Can a maintainer jump from the summary to the underlying full-audit, value-gauntlet, release, and plugin evidence?"
- Candidate type: `shipguard-inspect-proof-state-fixture`
- Product weakness: InspectDeck is only useful as a control panel if it preserves the route from the concise summary back to the underlying proof receipts.

This slice promotes `fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the` as public synthetic coverage. Fresh InspectDeck report-quality now covers all three current InspectDeck questions and returns `all-actionability-covered`, which tells the next loop to rotate to a fresh ShipGuard QA source instead of repeatedly fixture-promoting the same root report.

## Current InspectDeck Missing-Inputs Fixture Promotion

The next read-only InspectDeck QA pass started from the v3.173 state, where the next-action/source-proof question was already covered by a promoted public fixture. Fresh `shipguard inspect` plus `ios report-quality --write-fixture-candidates` advanced to the next useful gap:

- Question: "Are missing inputs marked as missing instead of silently downgraded into confidence?"
- Candidate type: `shipguard-inspect-proof-state-fixture`
- Product weakness: InspectDeck reports are only useful if missing proof inputs stay visibly missing instead of becoming implied confidence.

This slice promotes `fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o` as public synthetic coverage. The fixture stays ShipGuard-only, target-app read-only, and shareable. Fresh InspectDeck report-quality now covers both InspectDeck next-action/source-proof and missing-input honesty, then advances to the underlying-evidence navigation question.

## Current InspectDeck Fixture Promotion

The latest read-only QA rotation moved away from Full Audit after all four current Full Audit questions were covered. A fresh `shipguard value-gauntlet` pass also returned `all-actionability-covered`, so the loop used `shipguard inspect` as the next targeted root report source.

InspectDeck produced a useful report-quality gap:

- Question: "Does InspectDeck make the next action obvious without hiding the source proof?"
- Initial weakness: the question was prioritized, but `ios report-quality --write-fixture-candidates` did not classify InspectDeck proof-state questions as materializable fixture candidates.

This slice closes that gap:

- `ios report-quality` now classifies InspectDeck next-action, missing-input, source-proof, and underlying-evidence questions as `shipguard-inspect-proof-state-fixture` candidates.
- `fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious` promotes the top InspectDeck question into public synthetic coverage.
- The promoted fixture stays ShipGuard-only and public-safe, with explicit target-app read-only boundaries.
- Fresh InspectDeck report-quality now covers the next-action/source-proof question and advances to the missing-inputs question instead of stalling with no candidate.

This keeps the read-only QA rotation moving across root ShipGuard reports instead of relying only on Full Audit or Value Gauntlet.

## Current Full Audit Slash Handoff Fixture

The latest read-only Full Audit QA pass advanced from the slow-lane rerun question to the slash-handoff freshness question:

- Question: "Does the slash handoff come from the current NEXT_GOAL.md instead of stale hardcoded roadmap text?"
- Candidate type: `shipguard-full-audit-proof-boundary-fixture`

This slice promotes that final current Full Audit question into public fixture coverage:

- `fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren` covers the NEXT_GOAL-backed slash-handoff question without private app data.
- The fixture keeps ShipGuard-only and target-app read-only boundaries explicit, and it preserves the synthetic Full Audit report shape needed for report-quality scoring.
- Fresh Full Audit report-quality now covers proof boundaries, the resumable evidence lane, slow-lane rerun guidance, and slash-handoff freshness.
- With all four current Full Audit actionability questions covered, fresh Full Audit QA returns `all-actionability-covered` and zero duplicate fixture candidates, telling the maintainer to move to a fresh read-only ShipGuard QA source.

This completes the current Full Audit report-quality fixture flywheel without claiming executed release proof from a plan-only report.

## Current Full Audit Evidence Lane Fixture

## Current Full Audit Slow Lane Fixture

The latest read-only Full Audit QA pass advanced from the evidence-lane question to the slow-lane rerun question:

- Question: "Are slow lanes summarized clearly enough for a solo developer to decide what to rerun?"
- Candidate type: `shipguard-full-audit-proof-boundary-fixture`

This slice promotes that question into public fixture coverage:

- `fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo` covers the slow-lane rerun question without private app data.
- The fixture keeps ShipGuard-only and target-app read-only boundaries explicit and includes synthetic slash handoff fields so it represents a valid Full Audit report.
- Fresh Full Audit report-quality now covers proof boundaries, the resumable evidence lane, and slow-lane rerun guidance, then advances to the slash-handoff freshness question.
- Focused tests prove the slow-lane fixture scores as `review-existing-fixture`, emits no recursive `fixtureCandidates`, and ships in release packages.

This keeps the Full Audit report-quality flywheel moving through each remaining Full Audit proof-lane question instead of recurring on the same report weakness.

## Previous Full Audit Evidence Lane Fixture

The latest read-only ShipGuard QA loop reran Full Audit after the proof-boundary fixture was promoted. Report-quality correctly advanced to the next Full Audit question:

- Question: "Does the full-audit report replace repeated manual validation ceremony with one resumable evidence lane?"
- Initial weakness: the question was prioritized, but `--write-fixture-candidates` did not materialize a promotion-ready candidate for this evidence-lane wording.

This slice closes that gap:

- `ios report-quality` now treats `resumable evidence lane`, `manual validation ceremony`, `slow lanes`, and `slash handoff` as fixture-candidate triggers.
- `fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated` promotes the evidence-lane question as a public synthetic fixture.
- The fixture stays ShipGuard-only and public-safe, with explicit target-app read-only boundaries and synthetic slash handoff fields.
- Fresh Full Audit report-quality now covers both proof-boundary and evidence-lane questions, emits no duplicate evidence-lane candidate, and advances to the slow-lane rerun question.

This turns Full Audit report-quality from a single proof-boundary check into a stepwise fixture flywheel across the whole Full Audit proof lane.

## Previous Full Audit Fixture Promotion

The latest read-only ShipGuard QA loop reran `shipguard full-audit --profile quick --plan-only --shipguard-eval --shareable` and graded the output with `ios report-quality`. The top actionability question was still the Full Audit proof-boundary prompt:

- Question: "Does the command preserve proof boundaries instead of pushing, publishing, or editing target apps?"
- Candidate type: `shipguard-full-audit-proof-boundary-fixture`

This slice promotes that candidate into a public synthetic fixture:

- `fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries` now covers the Full Audit proof-boundary question without private app code, local paths, screenshots, app identifiers, or proprietary text.
- The fixture includes explicit `scopeBoundary.shipguardOnly`, `targetAppsReadOnly`, `slashPlan`, `slashGoal`, and `slashHandoffSource` fields so it scores as a valid Full Audit report instead of a broken synthetic starter.
- Fresh Full Audit report-quality runs now report fixture coverage for question #1, emit no duplicate candidate, and advance priority to question #2: whether Full Audit replaces repeated manual validation ceremony with one resumable evidence lane.
- Focused tests prove the fixture scores as `review-existing-fixture`, emits no recursive `fixtureCandidates`, and ships in release packages.

This keeps the read-only QA loop moving from candidate generation into durable public regression coverage.

## Previous Fresh QA Source Expansion

The latest read-only ShipGuard QA loop moved beyond the saturated value-gauntlet path and used `shipguard full-audit --profile quick --plan-only --shipguard-eval --shareable` as a fresh source. Report-quality passed the Full Audit report, but the materialized candidate for the top question was still generic:

- Question: "Does the command preserve proof boundaries instead of pushing, publishing, or editing target apps?"
- Old fixture type: `shipguard-eval-boundary-fixture`

That was too vague for a Full Audit-specific proof lane. This slice makes the new QA source useful:

- Full Audit proof-boundary, pushing/publishing, target-app, slow-lane, resumable evidence-lane, and slash-handoff questions now materialize as `shipguard-full-audit-proof-boundary-fixture`.
- The focused report-quality test runs Full Audit in plan-only/shareable mode, grades it, and fails if the candidate falls back to the generic boundary fixture type.
- The fixture remains a starter candidate only; ShipGuard does not auto-promote it into the repo or claim executed release proof from a plan-only report.

This expands the loop from value-gauntlet-only QA to another root ShipGuard report family while preserving the read-only boundary.

## Current Fixture Review Priority UX

The latest read-only ShipGuard QA loop ran `shipguard value-gauntlet` and graded the output with `shipguard ios report-quality`. The gauntlet passed, and report-quality correctly detected that the five ranked value-gauntlet actionability questions already have promoted public fixture coverage.

The weakness was priority UX: even with no findings and no new fixture candidates, the top `priorityAction` still said `review-existing-fixture` for the first covered fixture. That made the maintainer manually infer that the loop should advance to a fresh QA source.

This slice fixes the loop:

- Fresh reports whose ranked questions are all covered now return `priorityAction.kind = all-actionability-covered`.
- The priority action keeps the top covered question and fixture path visible as evidence, but its summary tells the maintainer to move to a fresh read-only ShipGuard QA source.
- Actual fixture runs still use `review-existing-fixture`, so recursion-safety checks remain explicit.
- Focused report-quality tests prove fresh value-gauntlet QA advances beyond fixture review while promoted fixture reports still avoid duplicate fixture candidates.

This keeps the fixture flywheel from wasting the next iteration on already-covered questions.

## Current Real Stable Publication Blocked-State QA

The latest read-only real-release QA run used the public `v3.131.0` ShipGuard release assets as the target evidence. It found a useful ShipGuard product weakness without editing any target app:

- Public release metadata and downloaded release assets passed consumer verification.
- Fresh install and rollback proof passed for the current `shipguard-v3.131.0.tar.gz` package.
- Same-prefix upgrade proof blocked because the previous `v3.130.0` tarball contains generated AppleDouble metadata.
- Stable publication correctly remained blocked because release notes do not describe stable-v4 publication proof and independent adoption/security evidence is not supplied.

The weakness was report UX: the detailed upgrade receipt said blocked, but the top `Readiness Proof` summary still said `Upgrade: pass` because it was reporting route availability instead of supplied proof status. This slice fixes that:

- `v4 release-candidate` readiness summary rows now prefer actual supplied receipt status for fresh install, upgrade, rollback, and release-consume proof.
- Blocked same-prefix upgrade proof now points to `./scripts/package_release.sh && ./tests/package_release_test.sh && ./tests/v4_release_candidate_test.sh` instead of only the focused test.
- Focused tests now assert that blocked supplied upgrade and release-asset proof cannot appear as passing readiness summary rows.

This preserves the honest boundary: real stable v4 remains unclaimed until the public release notes, LaunchKey candidate packet, release assets, independent adoption evidence, and final security review all pass.

## Current Stable Publication Evidence Starter Kit

The latest read-only stable-publication QA run showed a practical usability gap: ShipGuard could identify the missing stable-v4 evidence packet, but a maintainer still had to assemble the fillable evidence files by hand.

This slice improves the execution path without weakening the gate:

- `shipguard v4 stable-publication` now writes `stable-publication-evidence-kit/` into every report directory.
- The kit contains `README.md`, `stable-publication-checklist.json`, `external-adoption-evidence.json`, and `security-review-evidence.json`.
- The JSON report exposes the same artifact as `stablePublicationEvidenceStarterKit`, and Markdown renders an `Evidence Starter Kit` section.
- `ios report-quality`, focused stable-publication tests, and package proof now fail if the starter-kit manifest or generated files disappear.

The starter kit is still draft-only. It helps collect real independent adoption and final security-review evidence; it does not turn fixture evidence or placeholders into stable-v4 proof.

## Current Stable Release Notes Proof Gate

The next stable-publication QA pass showed that the release-notes gate was too easy to satisfy: a short phrase like "stable v4 release proof is ready" could pass the old keyword check even when the public notes did not explain downloaded release assets, post-release consumer proof, independent adoption, final security review, or non-claim boundaries.

This slice makes the gate evidence-shaped:

- `shipguard v4 stable-publication` now analyzes the full GitHub release body, not only the preview stored for human reading.
- `releaseNotesProof` emits a notes digest, line count, seven-topic matrix, and exact `missingTopicIds`.
- Markdown renders a `Release Notes Proof` section so the maintainer can fix the release page directly.
- Focused tests prove weak notes block stable publication even when the candidate packet, release assets, adoption evidence, and security review all pass.

The stable-v4 claim remains blocked until the public release notes describe the real stable-publication proof packet.

## Current Release Notes Authoring Kit

The next read-only QA loop showed a follow-on usability gap: after the stricter release-notes proof gate identified missing topics, ShipGuard still left the maintainer to write the public release body manually.

This slice makes the blocked gate actionable:

- `shipguard v4 stable-publication` now writes `stable-publication-release-notes/` into every report directory.
- The kit contains `README.md`, `release-notes-checklist.json`, and `draft-release-notes.md`.
- The JSON report exposes `stablePublicationReleaseNotesAuthoringKit`, and Markdown renders a `Release Notes Authoring Kit` section.
- The checklist mirrors `releaseNotesProof.missingTopicIds`, so the draft answers the actual blocked topics instead of a generic template.
- `ios report-quality`, focused stable-publication tests, and package proof now fail if the release-notes authoring kit disappears.

The kit is draft-only. It helps edit the public GitHub release notes, then the maintainer must rerun stable-publication against the actual release metadata.

## Current Stable Publication Report Quality Fixtures

The next report-quality pass showed that the stable-publication report shape was now useful, but the public fixture coverage did not recognize the stable-publication proof and release-notes authoring questions as promoted. That meant ShipGuard kept generating duplicate fixture candidates even after the behavior existed.

This slice turns the stable-publication surface into reusable public QA:

- `fixtures/ios-report-quality/stable-publication-complete` now contains a synthetic complete stable-publication report with evidence packet, evidence templates, evidence starter kit, release-notes proof, and release-notes authoring kit.
- `fixtures/ios-report-quality/stable-publication-release-notes-authoring` marks the release-notes authoring question as separately covered.
- `./tests/ios_report_quality_test.sh` now runs the complete fixture and asserts report-quality returns `pass`, detects both fixture coverage entries, and emits no duplicate fixture candidates.

This keeps the next loop moving to new product gaps instead of repeatedly rediscovering the stable-publication authoring work.

## Current Stable Publication Value-Gauntlet Fixture

The next ShipGuard-only read-only QA pass used `shipguard value-gauntlet` and then graded that report with `shipguard ios report-quality`. The gauntlet correctly passed the fixture-backed proof families and identified the remaining real-world gap: stable-v4 publication still needs public GitHub release assets, independent adoption evidence, final security-review evidence, release notes, and post-release consumer proof.

The report-quality weakness was loop hygiene. That stable-v4 publication question is now a known external/publication gate, but it still appeared as a new fixture candidate. This slice promotes the question into a public synthetic fixture:

- `fixtures/ios-report-quality/stable-publication-value-gauntlet-question` records the value-gauntlet stable-publication question without private app data.
- `ios report-quality` now reports it as existing fixture coverage and emits no duplicate `fixtureCandidates` for that question.
- The priority action advances to the next uncovered product-release stabilization question while the ranked list still shows the covered stable-publication question with existing fixture metadata.
- Focused report-quality and package tests prove the fixture ships and keeps the ShipGuard-only/read-only boundary explicit.

This keeps the loop honest: ShipGuard does not fake real stable-v4 publication evidence, but it also does not waste the next refinement cycle rediscovering the same external evidence gate as a missing public fixture.

## Current Product Release Stabilization Value-Gauntlet Fixture

The next read-only ShipGuard QA pass advanced to the product-release stabilization question: whether ShipGuard should stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption. The useful defect was in ShipGuard itself: `ios report-quality --write-fixture-candidates` did not treat release/adoption/security/rollback/consumption proof questions as promotion-ready release-proof fixtures.

This slice improves the loop:

- `ios report-quality` now classifies product-release, stable-v4, release-proof, release-consumption, rollback-proof, external-adoption, and security-review questions as `shipguard-release-proof-quality-fixture` candidates.
- `fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question` promotes the product-release stabilization value-gauntlet question into public synthetic coverage.
- Focused tests prove the promoted fixture scores as `review-existing-fixture`, emits no recursive `fixtureCandidates`, and lets fresh value-gauntlet report-quality runs advance to the next uncovered proof-boundary question.
- Package proof now checks that the new fixture ships in release tarballs.

This is still ShipGuard-only product QA. It does not claim stable v4 is released, does not edit private apps, and does not treat synthetic fixture evidence as external adoption or security evidence.

## Current Surface Proof-Boundary Value-Gauntlet Fixture

The next read-only ShipGuard QA pass advanced to the proof-boundary question: whether every useful-looking surface has docs, tests, package proof, and a concrete proof boundary instead of only a branded name. The weakness was again in ShipGuard's loop mechanics: the question was prioritized, but `ios report-quality --write-fixture-candidates` produced no materialized candidate for this proof-boundary class.

This slice makes that gap reusable:

- `ios report-quality` now classifies proof-boundary, branded-name, and useful-surface questions as `shipguard-surface-proof-boundary-fixture` candidates.
- `fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question` promotes the value-gauntlet proof-boundary question into public synthetic coverage.
- Focused tests prove the promoted fixture scores as `review-existing-fixture`, emits no recursive `fixtureCandidates`, and lets fresh value-gauntlet report-quality runs advance to the next uncovered plugin-skill routing question.
- Package proof now checks that the new fixture ships in release tarballs.

This keeps ShipGuard's funny/vibey naming work honest: names are allowed only when the docs, tests, package proof, and proof boundary are also visible.

## Current Development Loop Efficiency Receipt

The latest self-QA pass showed a real development-process weakness: after the design observation question was promoted into a public fixture, the existing workflow-chain receipt became too coupled to that now-covered design question. The receipt failed even though the product behavior was improving, which meant the proof loop could waste maintainer time on manual interpretation.

This slice fixes the ShipGuard development loop:

- `fixtures/tool-value-gauntlet/workflow-chain-receipts/report-quality-to-spec-and-next-goal` now uses its own synthetic uncovered report-quality question instead of depending on whichever design question happens to be uncovered that day.
- The receipt proves the intended chain directly: report-quality priority question -> `ios spec-workflow` -> SpecForge tasks and validation commands -> slash plan/goal -> `next-goal`.
- `shipguard value-gauntlet` now reports the workflow-chain receipt as passing again, so the next weak surface moves forward to stable-v4 publication proof instead of getting stuck on stale fixture coupling.

## Current Stable Publication Evidence Templates

The latest stable-publication product-QA pass showed the next usability gap: ShipGuard could tell users that independent adoption and final security-review evidence were missing, but users still had to infer the exact record shape from implementation details.

This slice improves the real publication-proof path:

- `templates/stable-publication/external-adoption-evidence.template.json` and `templates/stable-publication/security-review-evidence.template.json` now ship as draft-only public templates.
- `shipguard v4 stable-publication` now emits `stablePublicationEvidenceTemplates`, including template paths, accepted evidence classes, required fields, copy commands, validation commands, and draft-only instructions.
- The adoption and security entries in `stablePublicationEvidencePacket.requiredEvidence` link to their template path and copy command, and Markdown reports render an `Evidence Templates` section.
- `ios report-quality` now flags stable-publication reports that hide the template catalog or omit template links from the evidence packet.

The templates deliberately do not pass unchanged: they default to draft status and require a real redaction review before they can become stable-v4 evidence.

## Current Verify-First Launch Priority

The next product-facing slice should make `shipguard verify` the obvious launch feature. The repo already has the core pieces: `prepare`, `verify`, release proof, GitHub Actions, check-run/review-comment/SARIF adapters, init profiles, badges, package proof, and Codex plugin guidance. The weakness is discoverability and first-run value, not absence of a verdict engine.

Near-term launch work should therefore orbit one clean proof report:

- one short install/quickstart path
- one tiny broken demo repo or fixture where ShipGuard catches weak proof
- one GitHub Action path for PR proof reports
- one README/docs-site story around proof-gated AI maintenance
- one guarded launch-relay draft workflow for Product Hunt, X, Reddit, GitHub, and ShipYard channels, with final public posting still requiring action-time approval

The v3.153 slice begins that by adding a concise `proofReport` to `shipguard verify`, a public `examples/verify-first/` pass/review/blocked demo, `docs/verify-first-quickstart.md`, and a transparent `examples/workflows/verify-pr.yml` starter workflow. This is deliberately centered on the existing verdict engine rather than adding another branded command.

## Current Stable Publication Evidence Packet

The next ShipYard gauntlet pass keeps every fixture-backed receipt green and correctly leaves `runtimeV4StableReleasePublication` as the remaining real-world gap. The useful improvement is not to fake a stable v4 release; it is to make the final gate easier to execute and review.

This slice improves the real publication-proof path:

- `shipguard v4 stable-publication` now emits `stablePublicationEvidencePacket`, a single machine-readable checklist with all seven required real-evidence inputs, stable evidence IDs, pass/missing counts, the first blocking gate, exact next command, proof order, and non-claims.
- The Markdown report renders the same packet as `Evidence Packet`, so a maintainer can review the proof packet without opening JSON.
- `ios report-quality` now flags stable-publication reports that expose gates but hide this packet, keeping the final v4 claim gate action-oriented without pretending fixture receipts prove real adoption or security review.

## Current Design Observation Promotion Fixture

The latest broad read-only ShipGuard product-QA loop against local app checkouts generated 10 shareable reports across performance, design, modernization, app-intelligence, and AI-readiness. Report-quality scored the set 100/100, and the next uncovered ShipGuard-owned question was design-specific: which private-app observation should become a public design fixture or eval case.

This slice fixes ShipGuard's fixture flywheel, not either target app:

- A new public `fixtures/ios-report-quality/design-observation-promotion` fixture covers the repeated design observation-promotion question without copying private app code, paths, screenshots, or identifiers.
- The fixture keeps `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit, includes app-type tailoring, design-coherence boundary, preview guidance, and synthetic education-profile source signals, and proves the promoted question does not recurse into another fixture candidate.
- Fresh read-only product-QA now treats that design question as fixture-covered, so future loops can move to the next uncovered modernize or app-intelligence report-quality gap instead of re-deciding the same design fixture promotion.

## Current Fixture Candidate Naming

The latest broad read-only ShipGuard product-QA loop against local app checkouts generated 10 shareable source reports across performance, design, modernization, app-intelligence, and AI-readiness. Report-quality scored the set 100/100, but the materialized fixture starter directories still exposed a ShipGuard product weakness: repeated boundary-oriented candidates were written as generic duplicate names such as `01-shipguard-eval-boundary-fixture`, even though the report itself already knew the more useful tool/question slug.

This slice fixes the ShipGuard promotion workflow, not either target app:

- `ios report-quality --write-fixture-candidates` now preserves the generated candidate's descriptive tool/question ID when writing starter directories and promotion metadata.
- Materialized candidates now read like `01-shipguard-ios-design-which-private-app-observation...` or `04-shipguard-ios-app-intelligence-were-candidate-actions...`, making promotion, review, and fixture dedupe easier to follow.
- The focused report-quality regression lane now fails if materialized candidates collapse back to generic fixture-type names.

## Current Design Preview/Devspace Routing Fixture

The latest read-only ShipGuard product-QA loop against local app checkouts showed the next ShipGuard-owned design gap after app-type tailoring and coherence boundaries: `ios design` mentioned the iPhone preview and Devspace bridge, but `ios report-quality` did not yet enforce whether that visual-proof path was obvious, authenticated, and honest about ChatGPT-side model selection.

This slice fixes the ShipGuard report contract and public eval coverage, not either target app:

- `ios report-quality` now checks `shipguard ios design` reports for `previewEvidence`, preview and Devspace recommended commands, bearer-token Devspace guidance, Markdown preview routing, and the statement that model selection happens in ChatGPT rather than inside ShipGuard.
- Generated design fixture candidates now include synthetic `previewEvidence`, a preview `resultUX.nextCommand`, authenticated Devspace guidance, and a Markdown `Preview And Devspace` section.
- A public `fixtures/ios-report-quality/preview-devspace-routing` fixture covers the repeated read-only product-QA question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only design report-quality set scored 100/100; fixture coverage now suppresses app-type, coherence-boundary, and preview/Devspace questions, moving the next uncovered priority to deciding which private-app observation should become the next public design fixture or eval case.

## v3.113.0 Design Coherence Boundary Fixtures

The next read-only ShipGuard product-QA loop against local app checkouts showed the expected next ShipGuard-owned design gap: `ios design` reports had app-type tailoring, but report-quality still needed a durable proof that design-system coherence findings remain ShipGuard product QA evidence and do not become target-app redesign tasks.

The v3.113.0 slice fixes the ShipGuard report contract and public eval coverage, not either target app:

- `ios-design.json` now includes `designCoherenceBoundary` with separate source inventory, coherence risks, `separationChecks`, a ShipGuard-owned next action, app-work authorization, proof boundary, and `targetRemediationStatus: not-authorized-from-this-run`.
- `ios-design.md` now renders a `Design Coherence Boundary` section so the same authorization and proof boundary is visible to humans.
- `ios report-quality --shareable` now flags ShipGuard-evaluation design reports that omit the coherence boundary, separation checks, ShipGuard-owned next action, app-work authorization status, proof boundary, or Markdown rendering.
- A public `fixtures/ios-report-quality/design-coherence-boundary` fixture covers the repeated read-only product-QA question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only performance and design report set scored 100/100; fixture coverage now suppresses runtime-boundary, grouped-performance, evidence-promotion, design app-type-tailoring, and design-coherence questions, moving the next uncovered priority to preview and Devspace guidance.

Current read-only report-quality result:

```bash
./bin/shipguard ios performance --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3113/performance --shipguard-eval --shareable
# status: blocked
./bin/shipguard ios design --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3113/design --shipguard-eval --shareable --icon-brief
# status: review
./bin/shipguard ios performance --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3113/performance --shipguard-eval --shareable
# status: review
./bin/shipguard ios design --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3113/design --shipguard-eval --shareable --icon-brief
# status: review
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-app-a-v3113/performance \
  --reports /tmp/shipguard-readonly-app-a-v3113/design \
  --reports /tmp/shipguard-readonly-app-b-v3113/performance \
  --reports /tmp/shipguard-readonly-app-b-v3113/design \
  --out /tmp/shipguard-readonly-quality-v3113 \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3113/fixture-candidates
# status: pass
# reports: 4
# priority action: answer the preview/Devspace guidance question
```

## v3.112.0 Design App-Type Tailoring Fixtures

The next read-only ShipGuard product-QA loop against local app checkouts showed the expected next ShipGuard-owned design gap: `ios design` inferred app type and emitted motion/haptic guidance, but report-quality needed a durable proof that advice was actually tailored to the inferred app category instead of applying one universal design rule.

The v3.112.0 slice fixes the ShipGuard report contract and public eval coverage, not either target app:

- `ios-design.json` now includes `designTailoring` with `tailoredFor`, `guidanceProfile`, `universalDefaultsRejected`, source signals, tailored motion/haptics/visual-density/copy dimensions, and one `nextAction`.
- `nextAction` names owner, manual proof, expected artifact, success condition, and failure meaning so design reports do not stop at a source inventory.
- `ios-design.md` now renders a `Design Tailoring Contract` section so the same app-type proof is visible to humans.
- `ios report-quality --shareable` now flags design reports that omit the tailoring contract, source signals, tailored dimensions, Markdown rendering, or next-action proof fields.
- A public `fixtures/ios-report-quality/design-app-type-tailoring` fixture covers the repeated read-only product-QA question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only performance and design report set scored 100/100; fixture coverage now suppresses runtime-boundary, grouped-performance, evidence-promotion, and design app-type-tailoring questions, moving the next uncovered priority to design-system coherence boundary separation.

Current read-only report-quality result:

```bash
./bin/shipguard ios performance --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3112-after/performance --shipguard-eval --shareable
# status: blocked
./bin/shipguard ios design --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3112-after/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios performance --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3112-after/performance --shipguard-eval --shareable
# status: review
./bin/shipguard ios design --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3112-after/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-app-a-v3112-after \
  --reports /tmp/shipguard-readonly-app-b-v3112-after \
  --out /tmp/shipguard-readonly-quality-v3112-after \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3112-after/fixture-candidates
# status: pass
# reports: 4
# priority action: answer the design-system coherence boundary question
```

## v3.111.0 Performance Evidence Promotion Fixtures

The next read-only ShipGuard product-QA loop against local app checkouts showed the expected next ShipGuard-owned gap: `ios performance` already separated source heuristics from runtime proof and grouped repeated findings, but the report still needed one machine-readable promotion contract that tells a solo developer exactly what evidence would move a source suspicion into broader work.

The v3.111.0 slice fixes the ShipGuard report contract and public eval coverage, not either target app:

- `ios-performance.json` now includes `evidencePromotion` with `sourceEvidence`, `promotionStatus`, `firstCandidateRule`, `proofRequired`, and one `nextAction`.
- `nextAction` names the owner, manual proof or command, expected artifact, success condition, and failure meaning so a non-pass performance report does not leave the developer interpreting broad advice.
- `ios-performance.md` now renders an `Evidence Promotion Contract` section so the same proof requirement is visible to humans.
- `ios report-quality --shareable` now flags non-pass performance reports that omit the evidence-promotion contract or hide it from Markdown.
- A public `fixtures/ios-report-quality/performance-evidence-promotion` fixture covers the repeated read-only product-QA question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only performance and design report set scored 100/100; fixture coverage now suppresses the runtime-boundary, grouped-performance, and evidence-promotion questions, moving the next uncovered priority to design app-type tailoring.

Current read-only report-quality result:

```bash
./bin/shipguard ios performance --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3111-after/performance --shipguard-eval --shareable
# status: blocked
./bin/shipguard ios design --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3111-after/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios performance --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3111-after/performance --shipguard-eval --shareable
# status: review
./bin/shipguard ios design --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3111-after/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-app-a-v3111-after \
  --reports /tmp/shipguard-readonly-app-b-v3111-after \
  --out /tmp/shipguard-readonly-quality-v3111-after \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3111-after/fixture-candidates
# status: pass
# reports: 4
# priority action: answer the design app-type tailoring question
```

## v3.110.0 Grouped Performance Observation Fixtures

The next read-only ShipGuard product-QA loop against local app checkouts showed a ShipGuard-owned fixture gap: `ios performance` already grouped repeated source heuristics into actionable clusters, but materialized report-quality fixture candidates for grouped performance questions were too generic. They preserved the question and boundaries, but did not include a synthetic repeated finding, grouped action plan, proof boundary, or Markdown table that actually exercised the grouped report contract.

The v3.110.0 slice fixes report-quality fixture generation and public eval coverage, not either target app:

- `ios report-quality --write-fixture-candidates` now materializes `ios-performance-report-quality-fixture` reports with four synthetic `swiftui-repeat-forever-animation` findings, `ruleSummary`, `groupedActionPlan`, `firstExperiment`, `validationRoute`, `stopCondition`, and split local/manual proof guidance.
- Generated fixture Markdown now renders `Grouped Next Actions`, `Top Findings`, and `Proof Boundaries` so report-quality checks the same reader-facing grouped-performance surface that real app reports rely on.
- A public `fixtures/ios-report-quality/grouped-performance-observation` fixture covers the repeated read-only product-QA question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only performance and design report set scored 100/100; fixture coverage now suppresses both the runtime-boundary and grouped-performance questions, moving the next uncovered priority to performance evidence promotion.

Current read-only report-quality result:

```bash
./bin/shipguard ios performance --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3110/performance --shipguard-eval --shareable
# status: blocked
./bin/shipguard ios design --path <app-a-checkout> --out /tmp/shipguard-readonly-app-a-v3110/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios performance --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3110/performance --shipguard-eval --shareable
# status: review
./bin/shipguard ios design --path <app-b-checkout> --out /tmp/shipguard-readonly-app-b-v3110/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-app-a-v3110 \
  --reports /tmp/shipguard-readonly-app-b-v3110 \
  --out /tmp/shipguard-readonly-quality-v3110-after \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3110-after/fixture-candidates
# status: pass
# reports: 4
# priority action: answer the performance evidence-promotion question
```

## v3.109.0 Performance Runtime Boundary Fixtures

Read-only ShipGuard product-QA against local Ringly and Ilmify checkouts showed a ShipGuard-owned ambiguity: `shipguard ios performance` had strong grouping, proof, and read-only scope language, but the report contract did not explicitly say that source-only performance findings are heuristics rather than measured runtime proof.

The v3.109.0 slice fixes PulseRadar and report-quality itself, not either target app:

- `ios-performance.json` now includes `runtimeEvidenceBoundary` with `evidence: source heuristic`, `confidence: medium`, `runtimeProof: missing`, and `blocking: no`.
- `ios-performance.md` now renders a `Runtime Evidence Boundary` section before findings, making clear that CPU, GPU, memory, energy, hitch, touch-latency, FPS, ProMotion, thermal, and hardware-display claims still need same-route profiling or physical-device proof.
- `ios report-quality --shareable` now flags `shipguard ios performance` reports that omit the runtime-evidence boundary.
- A public `fixtures/ios-report-quality/performance-runtime-boundary` synthetic fixture covers the repeated read-only boundary question without copying private app code, paths, screenshots, or app identifiers.
- Regenerating the same read-only Ringly/Ilmify performance and design report set scored 100/100 with no report-quality findings; fixture coverage suppressed the already-covered boundary question and moved the next uncovered priority to grouped performance observation fixtures.

Current read-only report-quality result:

```bash
./bin/shipguard ios performance --path <ringly-checkout> --out /tmp/shipguard-readonly-ringly-v3109b/performance --shipguard-eval --shareable
# status: blocked
./bin/shipguard ios design --path <ringly-checkout> --out /tmp/shipguard-readonly-ringly-v3109b/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios performance --path <ilmify-checkout> --out /tmp/shipguard-readonly-ilmify-v3109b/performance --shipguard-eval --shareable
# status: review
./bin/shipguard ios design --path <ilmify-checkout> --out /tmp/shipguard-readonly-ilmify-v3109b/design --shipguard-eval --shareable
# status: review
./bin/shipguard ios report-quality \
  --reports /tmp/shipguard-readonly-ringly-v3109b \
  --reports /tmp/shipguard-readonly-ilmify-v3109b \
  --out /tmp/shipguard-readonly-quality-v3109b \
  --shareable \
  --write-fixture-candidates /tmp/shipguard-readonly-quality-v3109b/fixture-candidates
# status: pass
# reports: 4
# average score: 100.0/100
# priority action: answer the grouped performance observation fixture question
```

## v3.108.0 DockCheck Report Contract

Read-only ShipGuard product-QA against local Ringly and Ilmify checkouts showed a ShipGuard-owned weakness: `shipguard ios doctor` produced useful topology facts, but its JSON still used an older report shape. `ios report-quality --shareable` blocked on missing stable metadata, missing structured finding fields, and local absolute project paths in DockCheck output.

The v3.108.0 slice fixes DockCheck itself, not either target app:

- `ios-doctor.json` now includes `schemaVersion`, `generatedAt`, a privacy-safe `<target-repo>` project root, and target metadata.
- Every DockCheck finding now includes `ruleId`, backward-compatible `code`, `evidence`, `recommendation`, and `proofGuidance`.
- The focused doctor test builds a synthetic public package-only fixture and proves the generated doctor report passes `ios report-quality --shareable`.
- Regenerating the same read-only Ringly/Ilmify report set moved report-quality from blocked to pass with an average score of 100/100 and no report-quality findings.

The next report-quality question from that clean run is performance-boundary wording: blocked performance reports must make it unmistakable that target-app remediation is evidence for ShipGuard product QA unless app work is separately authorized.

## Evidence Run

Current checkout:

```bash
./bin/shipguard version
# 3.113.0

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

The LaunchDeck integration pass showed ShipGuard had useful references to XcodeBuildMCP, simulator browser, SwiftUI preview, and profiler workflows, but no single ShipGuard command that made those workflows feel native. `shipguard ios launchdeck` now inspects repo topology, recommends the right LaunchDeck route, emits XcodeBuildMCP build/run, debugger/log, simulator browser, SwiftUI preview hot reload, and performance profiler handoffs, and keeps the execution boundary honest: ShipGuard owns routing and proof reports, while Codex iOS execution tools execute simulator/debugger/profiler routes.

The next LaunchDeck QA pass showed that a good route report still was not enough: ShipGuard could not tell whether Codex actually ran `build_run_sim`, captured a UI snapshot, opened `serve-sim`, hot-reloaded a SwiftUI preview, or preserved an Animation Hitches/Time Profiler receipt. `shipguard ios launchdeck --receipt <file-or-dir>` now grades explicit proof bundles after execution and flags missing lane-specific evidence while keeping the target app read-only.

A follow-up read-only receipt-quality pass showed the next weakness: weak `ios launchdeck` receipt reports generated fixture candidates, but report-quality ranked a generic front-door question first and classified receipt gaps as performance or preview fixture types. Receipt gaps now rank ahead of generic launchdeck questions, and report-quality emits `ios-launchdeck-receipt-quality-fixture` candidates backed by a public synthetic fixture in `fixtures/ios-report-quality/launchdeck-receipts`.

The next LaunchDeck receipt visibility loop showed another gap: `ios report-quality` could pass a structurally useful source report while hiding that the source report itself was still `review` with receipt findings. Report-quality now keeps those layers separate: `findings` remains report-quality defects, while `sourceFindings`, `sourceIssueVisibility`, and Markdown `Source Report Findings` carry reviewed source issues such as missing Harbor Check build/run proof or Trace Radar profiler proof.

The next read-only loop showed the report-quality artifact itself still carried absolute input/report paths even when its source design reports were shareable. `ios report-quality --shareable` now omits local absolute input and report paths from its own JSON, Markdown, findings, and redaction commands before ChatGPT/GitHub/docs/release-evidence sharing.

A follow-up read-only loop over the full Ringly/Ilmify report set showed another report-quality gap: the source reports carried useful `reportQualityQuestions`, but the quality artifact ended with only generic next actions. `ios report-quality` now aggregates those questions into an `Actionability Questions` section so the next ShipGuard rule, fixture, report section, or docs improvement is explicit.

The next performance explanation pass showed the quality loop could keep prioritizing "why does this matter?" even when `ios performance` already emitted an impact column. Report-quality now verifies `ios performance` findings have an `impact` or `whyItMatters` field and that Markdown surfaces the explanation, while the performance product-QA questions move on to grouping, evidence, proof, and fixture usefulness.

The next repeated-performance pass used a public read-only fixture with many high findings from the same rules. It showed that `ruleSummary` existed, but Markdown still repeated the same high rule rows before giving a rule-level action. `ios performance` now emits `groupedActionPlan`, renders `Grouped Next Actions` before capped individual findings, and `ios report-quality` flags repeated performance reports that omit either JSON grouping or visible Markdown grouping.

The following high-evidence pass showed high findings had source snippets and impact text, but no explicit explanation for why severity was `high`. `ios performance` now emits `severityReason` for findings, renders it as `Why severity` in grouped and top-finding Markdown tables, and `ios report-quality` flags high performance findings that omit the JSON reason or hide it from Markdown. The next product-QA priority moved to local-vs-manual proof guidance.

The next proof-boundary pass showed performance findings still used one blended proof sentence. `ios performance` now emits `localProof` and `manualProof`, renders `Codex local proof` and `Manual/device proof` in Markdown, and `ios report-quality` flags performance reports that omit those split fields or hide them from Markdown. The next product-QA priority moved to whether grouped actions name the smallest first experiment before broad refactors.

A public read-only full-report pass then showed report-quality still prioritized that first-experiment question because grouped performance actions had only broad `recommendedFirstMove` text. `ios performance` now emits a `firstExperiment` for each grouped action, Markdown renders a `First experiment` column before broader first-move advice, and `ios report-quality` emits `performance-grouped-first-experiment-missing` or `performance-markdown-first-experiment-missing` when grouped actions hide the smallest reversible proof step.

The next public fixture plus read-only Ringly/Ilmify performance pass showed the same remaining report-quality weakness: first experiments were present, but the grouped action did not make the validation route and stop condition explicit as report data. `ios performance` now emits `validationRoute` and `stopCondition` for each grouped action, Markdown renders those columns, and `ios report-quality` emits grouped or Markdown findings when validation routes or stop conditions are missing.

A real plugin run from an app checkout showed the iOS skill tried the app-local `./bin/shipguard` path and then fell back to source inspection because the Codex plugin bundle does not install the CLI into every target repo. The skill now resolves `SHIPGUARD_CLI` from app-local `./bin/shipguard`, installed `shipguard`, or `$HOME/.local/bin/shipguard`, and the docs clarify that plugin install loads skill metadata while CLI install provides the executable.

The next read-only performance pass showed `ios performance --shipguard-eval` still carried absolute local project roots, so report-quality correctly raised a local-path shareability warning. `ios performance --shareable` now omits local absolute project paths from JSON and Markdown before report-quality scoring or external planning, while default local reports keep operator paths.

The next remaining-shareability pass over modernize, app-intelligence, and AI-readiness showed no local path leaks in real-app reports, but those reports had no explicit shareability contract. `ios modernize --shareable`, `ios app-intelligence --shareable`, and `ios ai-readiness --shareable` now record shareability metadata and Markdown mode lines so report-quality passes are intentional rather than accidental.

The next declared-shareability pass showed `ios report-quality --shareable` still passed local-mode source reports when their contents happened not to leak paths. Report-quality now emits `declared-shareability-missing` for source reports without shareability metadata and `declared-shareability-local-mode` for reports that explicitly declare local mode, while regenerated shareable Ringly/Ilmify reports continue to pass.

The next read-only Ringly/Ilmify LaunchDeck, app-intelligence, and AI-readiness pass exposed the remaining unbounded source-read paths. `ios launchdeck` now budgets SwiftUI preview-signal reads, `ios app-intelligence` budgets App Intents/system-surface reads, and `ios ai-readiness` budgets AI source-token reads. Each report emits sampled, omitted, and timed-out text evidence in JSON/Markdown, and LaunchDeck shareable ShipGuard-eval output now redacts private target identifiers before report-quality scoring.

The next read-only ShipGuard self-QA pass scored v4 release-candidate, MarketplaceDeck, Full Audit plan-only, and Value Gauntlet reports together. It exposed a report-quality false block: full-audit `stage-receipts/*.json` are internal machine receipts, but recursive directory scoring treated them as standalone reports, and newer root reports such as `shipguard full-audit` and `shipguard codex marketplace-readiness` were missing from the known-tool list. Report-quality now skips full-audit stage receipts during directory scans and treats Full Audit, InspectDeck, MarketplaceDeck, and trace reports as first-class root report tools.

The next LaunchKey self-QA pass showed the same class of false block after fresh package proof landed: `shipguard v4 release-candidate --package-tarball` can write a default `fresh-install-prefix` under the report output, and report-quality recursively scored the installed ShipGuard package as if it were part of the candidate report. Report-quality now skips LaunchKey's generated `fresh-install-prefix`, `fresh-install-work`, and `release-consume` proof directories so the root readiness report remains the scored artifact while the attached receipts stay visible through LaunchKey fields.

The next LaunchKey self-QA pass showed the readiness report still asked whether a fresh user could install, upgrade, uninstall, and validate ShipGuard even after fresh-install proof existed, because upgrade and rollback remained static command guidance. `shipguard v4 release-candidate` now accepts `--upgrade-from-tarball`, installs a previous package, installs the candidate package over the same prefix, verifies the upgraded `shipguard` and `codex-maintainer` versions, runs validation, and records `upgradePackageProof`. When `--package-tarball` is supplied it also installs into a temporary rollback prefix, removes known ShipGuard package paths, verifies no package state remains, and records `rollbackPackageProof`. The same self-QA exposed the matching report-quality boundary: generated `upgrade-prefix`, `upgrade-work`, `rollback-prefix`, and `rollback-work` directories are now skipped as proof attachments, not source reports. Once package install, upgrade, and rollback receipts pass, LaunchKey advances its report-quality question to downloaded release-asset verification instead of repeating the package-proof question.

The next public-release self-QA pass downloaded the published `v3.131.0` assets and showed a sharper package-proof issue: release-consume verification passed, but the package tarball contained AppleDouble `._*` archive members that made installed validation fail. LaunchKey now blocks generated archive members before install, including `._*`, `.DS_Store`, `__MACOSX`, bytecode, and cache paths, and exposes `blockingProof` when any supplied fresh-install, upgrade, rollback, or release-asset receipt fails. The result UX now names the exact blocked receipt, short failure evidence, and next repair command instead of falling back to a generic `./tests/v4_release_candidate_test.sh` instruction.

The next LaunchKey self-QA pass isolated a workflow gap: once package fresh-install, upgrade, and rollback receipts passed, the report still required a separately downloaded release-asset directory. `shipguard v4 release-candidate --download-release-assets --github-release-repo <owner/repo>` now downloads release assets from GitHub, records `githubReleaseAssetDownloadProof`, feeds the downloaded directory into `release-consume verify`, and keeps the manual `--release-assets` path as an offline/pre-downloaded fallback. The live public-release run then exposed the matching report-quality boundary: generated `downloaded-release-assets` directories must be skipped as proof attachments, not recursively scored as source reports.

The next LaunchKey self-QA pass ran package fresh-install, same-prefix upgrade, rollback cleanup, native GitHub release-asset download, and consumer proof together. All machine receipts passed, but the result still ended with prose about finishing external adoption evidence. `shipguard v4 release-candidate --external-adoption-evidence <json-or-dir>` now validates independent adoption evidence records, separates synthetic fixture evidence from stable-v4 eligible evidence, redacts evidence paths in shareable output, and blocks records with private paths, private app identifiers, token-like strings, missing non-claims, or maintainer-only actors. When real adoption evidence is missing, the report now gives a concrete next command instead of a vague stable-v4 checklist.

The next isolated LaunchKey self-QA pass supplied passing package fresh-install, same-prefix upgrade, rollback cleanup, release-asset, and external-adoption evidence. That moved the report to the final security-review gap, but the next action was still a generic test rerun. `shipguard v4 release-candidate --security-review-evidence <json-or-dir>` now validates redacted security review records, requires CLI/plugin/GitHub Actions/release-proof/package-install/redaction-privacy scope coverage, separates synthetic fixture evidence from stable-v4 eligible review evidence, blocks private paths, private app identifiers, token-like strings, missing methodology/artifacts/non-claims, and rejects open critical/high findings. When final security evidence is missing, the report now gives a concrete security-evidence command before any stable-v4 claim.

The next release-packet self-QA pass ran Full Audit in read-only plan mode after LaunchKey could reach the final packet handoff. It exposed an honesty gap: `shipguard full-audit --plan-only` returned `status: pass` even though every stage was only planned. Full Audit now reports plan-only output as `review`, keeps planned stage receipts visible, and sets `resultUX.nextCommand` to the executable profile or exact selected stages with missing `--release-url`, `--version`, `--tag`, `--commit`, and `--ci-run-url` placeholders. That keeps route planning useful without letting planned proof masquerade as executed release proof.

The follow-up Full Audit self-QA pass exposed a different handoff gap: the report was honest about plan-only state, but `slashPlan` and `slashGoal` still contained an old hardcoded v3.132 release-stabilization placeholder while `NEXT_GOAL.md` had already advanced. Full Audit now reads `NEXT_GOAL.md`, prefers the `Following Slash Plan` and `Following Slash Goal` when a completion receipt exists, records `slashHandoffSource`, and falls back to a refresh instruction only when the file cannot be read. Report-quality now emits `full-audit-slash-handoff-source-missing` or `full-audit-slash-handoff-stale` when a Full Audit report lacks that source proof or carries the old hardcoded handoff.

The next Full Audit self-QA pass showed the JSON already carried structured `stages[].command` arrays, but the human Markdown only listed stage names and purposes. A maintainer could see that 14 release stages were planned but could not audit the exact commands from the report itself. Full Audit now renders a Markdown `Execution Commands` table from `stages[].command`, and report-quality emits `full-audit-execution-commands-markdown-missing` or `full-audit-execution-command-missing` when the copy-ready command ledger is absent or incomplete.

The next mixed self-QA bundle scored Full Audit plan-only, InspectDeck, LaunchKey, and Value Gauntlet together. The structure passed, but report-quality picked the generic Full Audit proof-boundary question because the source report status was `review`, even though Value Gauntlet and LaunchKey both pointed at the real v4 release-proof gap. Report-quality now keeps blocked source reports first, then lets Value Gauntlet lowest-value signals, LaunchKey release-readiness gaps, and result-UX release-stabilization signals outrank generic non-blocked review questions. The priority action now starts with the v4 product-release stabilization question instead of a broad Full Audit checklist prompt.

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

The next read-only spec-workflow loop over public demo reports showed repeated actionability questions could consume the first-eight clarifying-question cap and hide a later unique question. Spec-workflow now deduplicates report-quality questions before applying clarifying-question and task caps, and the regression fixture verifies the generated JSON and Markdown pass report-quality.

The next source-integration review showed the external-repo learning was still too shallow: ShipGuard described checklist/analyze-style workflow inspiration, but did not emit a real requirements checklist or consistency analysis artifact. Spec-workflow now creates `requirements-checklist.md` as planning-requirement unit tests and `consistency-analysis.md` as a cross-artifact coverage review, records ShipGuard-owned adaptation notes for Spec Kit, CodexPro, Expo, Xcode Build Optimization Agent Skills, and the OpenAI native iOS preview loop, and report-quality requires those artifacts before adoption passes.

The next read-only Ringly/Ilmify loop passed report-quality structurally but still showed that "fully integrated" external learning needed an explicit replace/extend/keep/defer decision layer. Spec-workflow now emits `integration-decisions.md` and JSON `integrationDecisions`, evaluates each external workflow idea against the current ShipGuard surface, states what it replaces or keeps, and gives validation evidence. Report-quality now requires that decision artifact and checks it preserves the report-quality questions before adoption passes.

The next external-source review showed even that was still too static: Spec Kit, CodexPro, Ponytail, Expo, and social-post ideas were represented as hardcoded inspiration inside spec-workflow instead of a repeatable source audit. `ios external-audit` now records read-only source checkouts and URLs, classifies source capabilities, emits a native replacement ledger, states what ShipGuard replaces, extends, keeps, routes, or defers, and carries license/no-vendoring boundaries plus report-quality questions. A source is not considered integrated until its capability has a ShipGuard-native action and validation command.

The next design-source pass used the installed Design Motion Principles skill as a read-only input and exposed a classifier weakness: the Expo profile could match `EAS` inside ordinary words such as `easing`. External-audit now uses boundary-aware source signals and has a first-class Design Motion Principles profile; `ios design` emits ShipGuard-native `motionQualityGates` so frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance checks are product report data, not a copied skill artifact.

The next external-source eval loop showed the CLI reports were structurally green, but deterministic routing still had no `external-source-audit` mode: a request to integrate Spec Kit, CodexPro, Expo, Design Motion Principles, and X posts routed to `preview-devspace` and missed external-audit, replacement-ledger, capability-matrix, and validation-command proof. `ios eval` now includes an `external-source-native-adoption` fixture and routes those requests through `external-source-audit`.

The next fixture-candidate loop showed the report-quality artifact could name safe public fixture candidates but still left materialization as manual work. `ios report-quality --write-fixture-candidates <dir>` now writes synthetic public starter directories with redacted candidate metadata, a minimal source report JSON/Markdown pair, validation notes, and no local paths or private app details.

The next materialized-fixture loop showed a promoted synthetic fixture could pass report-quality but still emit a new `fixtureCandidates` entry for itself, creating a recursive "fixture of a fixture" loop. Report-quality now marks already-materialized synthetic fixture reports as actionability evidence while suppressing recursive fixture candidates, and `fixtures/ios-report-quality/materialized-external-audit` locks that behavior into a public fixture.

The next promotion-workflow loop showed generated materialized fixtures were safe and recursive-fixture-proof, but still left the repo promotion step implicit. `ios report-quality --write-fixture-candidates` now emits `fixture-promotion-manifest.json`, `PROMOTION.md`, and per-candidate promotion metadata with repo-relative suggested paths, placeholder copy commands, validation commands, and a private-data review checklist without auto-copying candidates into the repository.

The next value-gauntlet loop showed skill/plugin receipt proof was useful but still stopped before the full ShipGuard product workflow: a report-quality question could exist without proof that it became a spec task, validation command, slash plan, and following goal. `shipguard value-gauntlet` now emits `workflowChainReceipts` and runs a public chain over `fixtures/demo-ios-repo`: `ios design --shipguard-eval --shareable`, `ios report-quality --shareable`, `ios spec-workflow --from-report --shipguard-eval --shareable`, spec report-quality, and `next-goal`.

The next promotion-manifest consumption loop scored the full materialized fixture root and exposed a second-order gap: `fixture-promotion-manifest.json` was being graded as a report-quality source report, creating false `self-report-skipped` and Markdown companion findings. Report-quality now excludes promotion manifests from source-report discovery, consumes them as fixture metadata, renders a `Fixture Promotion Manifests` section, and flags unsafe paths, local/token-like metadata, missing copy placeholders, missing validation commands, incomplete review checklists, stale guide paths, or missing materialized files.

The next read-only Ringly/Ilmify report-quality pass still left a manual gap: it asked which private observation should become a public fixture, but did not produce a safe fixture recipe. `ios report-quality` now emits `fixtureCandidates` with fixture type, synthetic public fixture path, source question, validation commands, and a private-data policy. The goal is to turn private-app evidence into public ShipGuard fixtures without copying private app code, screenshots, local paths, identifiers, or proprietary text.

The next read-only full-report pass showed report-quality could score all source reports as structurally valid while leaving 21 actionability questions unranked and even suggesting "fix high report-quality issues" when there were no findings. `ios report-quality` now emits `priorityAction` and `prioritizedActionabilityQuestions`, ranks report-quality findings before questions, and ranks questions from blocked/review source reports before lower-risk output so the next ShipGuard improvement is concrete.

The installed Codex cache should be refreshed to `ios-shipguard` metadata version `0.2.46+codex.20260619125045`, repository `https://github.com/jlekerli-source/ShipGuard`, display name `iOS ShipGuard`, and no stale `ringly-codex-workflows`, `Shipguard`, source-path MCP sidecar, or primary `codex-maintainer` guidance. The tracked checkout includes `plugins/ios-shipguard`, and package proof requires that plugin source.

The next value-gauntlet pass scored the ShipYard at 100.0 but still prioritized whether low-value patterns should become public fixtures. That question is now promoted into `fixtures/ios-report-quality/value-gauntlet-actionability`, a synthetic report-quality fixture that keeps `shipguard value-gauntlet` actionability visible while proving materialized fixtures do not recursively emit more fixture candidates.

The next command-depth probe showed the loop could still waste time by asking for the same value-gauntlet fixture again even after promotion. `ios report-quality` now detects promoted public fixtures under `fixtures/ios-report-quality`, renders `Fixture Coverage`, suppresses duplicate fixtureCandidates for covered questions, and moves the priority action to the next uncovered question.

The next ShipYard value loop showed `shipguard value-gauntlet` needed to answer its own "which surface is weakest?" question instead of handing a human an unranked all-green report. It now emits `lowestValueSurfaceProbe`, upgrades the copied starter skills with ShipGuard QA hooks, verifies starter-skill docs/test linkage, and escalates all-green static coverage into a runtime-output usefulness probe for the next implementation slice.

The runtime-output slice now executes representative ShipGuard commands on public/demo inputs: Brand Deck, DockCheck, VibeCheck, and QualityRadar. `runtimeOutputProbe` scores their generated JSON/Markdown for exit status, artifacts, machine-readable status, required keys, boundary language, Markdown sections, and usefulness signals. This exposed thin machine output in Brand Deck and DockCheck, so those reports now include top-level surface/status summary fields. With representative runtime output passing, the next weakness is negative runtime-output fixtures that fail decorative but low-value reports instead of letting them pass because they look complete.

The negative runtime-output slice now adds public synthetic fixtures under `fixtures/tool-value-gauntlet/runtime-output`. One fixture is report-shaped but empty; another has plausible design content but no ShipGuard-only boundary. `runtimeOutputNegativeFixtures` proves both are rejected while the fixture expectations pass, which unlocked the command help execution slice instead of another static metadata check.

The command-family runtime slice now executes `--help` for all registered public ShipGuard commands through `runtimeCommandFamilyCoverage`. That probe exposed top-level wrapper routes where `--help` was treated as an invalid file, path, or missing subcommand; the wrapper now handles top-level help consistently. With all public command help paths passing, ShipGuard could move beyond command entry points and test skill/plugin runtime receipts.

The skill/plugin receipt slice now adds public fixtures under `fixtures/tool-value-gauntlet/skill-plugin-receipts`. `skillPluginRuntimeReceipts` executes the iOS ShipGuard design-audit route, a starter UI-polish inventory/plan route, and plugin cache status proof against a synthetic Codex plugin cache. The receipts must produce real JSON/Markdown artifacts or stdout proof before the skill/plugin layer passes.

The workflow-chain receipt slice added a public fixture under `fixtures/tool-value-gauntlet/workflow-chain-receipts`. `workflowChainReceipts` executes design -> report-quality -> spec-workflow -> spec report-quality -> next-goal, and requires the source actionability question, proof-gated task, validation commands, copy-ready slash plan/goal, and following NextRail handoff to survive the chain.

The scenario-matrix receipt slice added a public fixture under `fixtures/tool-value-gauntlet/scenario-matrix-receipts`. `scenarioMatrixReceipts` executes a complete maintainer loop across iOS doctor, inventory, plan, design, report-quality, docs-check, transcript redaction and verification, CI gate and summary, Codex plugin status, and release manifest/index/replay using public fixtures plus a synthetic release package.

The scenario-failure receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/scenario-failure-receipts`. `scenarioFailureReceipts` feeds unsafe transcript text, broken docs, stale Codex plugin cache metadata, and incomplete release proof into real ShipGuard commands and requires non-zero exits or blocked reports with machine-readable evidence.

The scenario-remediation receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/scenario-remediation-receipts`. `scenarioRemediationReceipts` proves those same blocked journeys recover through the smallest repair step and successful rerun: transcript redact plus verify, missing docs target plus docs-check, fresh Codex plugin cache plus strict status, and complete release manifest/index plus release replay. With that receipt green, the next weakness is adoption receipts that prove a fresh user can install ShipGuard, refresh the Codex plugin, run the first useful audit, and understand the next command without maintainer context.

The fresh-user adoption receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/adoption-receipts`. `adoptionReceipts` copies the current checkout to a temporary package source, runs `scripts/package_release.sh` there, extracts the tarball, installs ShipGuard into a temporary prefix, prepares a fresh synthetic Codex plugin cache, verifies `shipguard codex status --strict`, runs the first Brand Deck audit from the installed CLI, and scores that audit with `ios report-quality --shareable`. With package adoption green, the next weakness is target-onboarding receipts that prove a fresh app repo can install starter files, run doctor/validate, and get the first scoped plan without maintainer context.

The target-onboarding receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/target-onboarding-receipts`. `targetOnboardingReceipts` copies `fixtures/demo-ios-repo` into a temporary fresh target, runs `shipguard init ios`, starter `doctor`, toolkit `validate`, iOS doctor, iOS inventory, and the first permission-audit plan. The receipt proves a fresh iOS app can reach actionable ShipGuard output without maintainer context.

The multi-profile onboarding receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/multi-profile-onboarding-receipts`. `multiProfileOnboardingReceipts` creates fresh iOS, web, backend, and CLI target repos, runs each starter `init` and `doctor`, verifies each target receives `SHIPGUARD_PROFILE.md`, and keeps the whole proof ShipGuard-only.

The profile-native first-audit receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/profile-native-first-audit-receipts`. `profileNativeFirstAuditReceipts` creates fresh web, backend, and CLI starter targets, prepares synthetic framework/API/CLI signals, runs ShipGuard WebScan, ServiceRadar, and CommandLens, checks shareable JSON/Markdown outputs, verifies generated ShipGuard starter files are separated from target evidence, and grades the reports with `ios report-quality`.

The profile-native fix-plan receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/profile-native-fix-plan-receipts`. `profileNativeFixPlanReceipts` creates fresh web, backend, and CLI starter targets, runs the first audits, converts each report through ShipGuard WebForge, ServiceForge, and CommandForge, checks scoped tasks, validation commands, stop conditions, shareable Markdown, and report-quality handoff.

The profile-native validation receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/profile-native-validation-receipts`. `profileNativeValidationReceipts` runs WebForge, ServiceForge, and CommandForge against synthetic target repos with `--target`, then requires `validationReceipts` to classify each validation lane as runnable, blocked, manual, or not checked without executing arbitrary target commands.

The profile-native validation rerun receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/profile-native-validation-rerun-receipts`. `profileNativeValidationRerunReceipts` starts WebForge, ServiceForge, and CommandForge with one blocked synthetic validation lane each, applies the fixture-local smallest repair, reruns the plan, and requires `blockedCount` plus `validationRerunReceipts.pairCount` to clear.

The profile-native proof handoff receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/profile-native-proof-handoff-receipts`. `profileNativeProofHandoffReceipts` runs repaired WebForge, ServiceForge, and CommandForge plans and requires `proofHandoff.copyReady=true`, local-path-safe copy-ready Markdown, validation status, commands to capture, and explicit no-implementation/no-validation-authorization boundaries.

The command-family runtime-output receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/command-family-runtime-output-receipts`. `commandFamilyRuntimeOutputReceipts` runs Brand Deck, DockCheck, VibeCheck, WebScan, WebForge, LinkSweep, and ManifestForge against public or synthetic inputs, then requires useful JSON/Markdown artifacts, local-path-safe shareable reports where applicable, and machine-readable proof that each command produced actionable output beyond `--help`.

The trust-hardening receipt slice adds a public fixture under `fixtures/tool-value-gauntlet/trust-hardening-receipts`. `trustHardeningReceipts` scans composite action shell bodies for raw `${{ inputs.* }}` interpolation, runs the Devspace public URL token blocker, exercises unsafe archive extraction rejection, and proves release provenance rejects bad or tag-mismatched release URLs while still emitting valid provenance for a synthetic release manifest. With those receipts green, the next weakness was the persistent proof-gated task contract that connects prepare, verify, scope, evidence, and verdict.

The proof-gated task-contract slice adds `shipguard prepare`, `shipguard verify`, `scripts/task_contract.py`, `docs/task-contract.md`, focused task-contract tests, and `fixtures/tool-value-gauntlet/task-contract-receipts`. `taskContractReceipts` now proves a public iOS task can create one durable task object, use bounded project snapshots, discover generic iOS scope, pass a scoped diff only with structured validation receipt coverage, reject a plain log as proof, block invalid receipts, and block a protected/out-of-scope diff plus unsupported "fully verified" claim with an exact next action. With diff-first receipts green, the next weakness is an iOS notification and permission workflow that turns permission-risk discovery into prepare/verify task contracts, focused validation receipts, and simulator/device proof guidance.

The notification-permission workflow slice uses read-only product-QA evidence as a ShipGuard weakness, not as app work. The observed gap was that `prepare` could correctly classify notification/permission work as risky while still returning a generic task contract. The public fixture now proves `prepare` emits `domainRiskPack.id = ios-notification-permission-workflow`, receipt requirements, simulator/device boundaries, and review-only lifecycle/plist surfaces. A new negative receipt proves `verify` returns `review` when a generic structured test receipt covers the command but lacks permission-state, denied-state, not-determined-state, and simulator permission-reset proof labels.

The Domain Pack SDK slice turns that first pack into a reusable extension point. `scripts/task_domain_packs.py` now exposes `DomainPackRegistry`, `domainPackSDK` metadata, pack result fields, notification-permission compatibility, and a synthetic public fixture pack. `domainPackSDKReceipts` prove a second pack can prepare and verify through the same task-contract verdict engine without activating unrelated notification proof lanes.

The configuration-baseline slice answers the next read-only value-gauntlet weakness. `scripts/shipguard_baseline.py` loads `.shipguard.yml` and `.shipguard-baseline.json`, requires exact finding fingerprints, and keeps accepted findings visible with owner, expiry, and proof-boundary metadata. `configurationBaselineReceipts` prove three public cases: an exact accepted protected-boundary finding can pass, an expired suppression blocks, and a second unsuppressed protected file remains a new regression.

The structured-evidence slice answered the next weakness after baselines. `scripts/shipguard_receipts.py` normalizes current v2 receipts, legacy task-contract receipts, artifact-only files, unsupported schema versions, stale receipts, invalid receipts, and downgraded manual/runtime proof receipts into one `evidenceReceiptSchema` contract. `structuredEvidenceReceipts` prove six public cases: prepare a neutral task, pass with a v2 validation receipt, pass with a legacy-compatible receipt, block an unsupported schema receipt, return review for a manual proof receipt that cannot satisfy automated validation, and block a stale v2 receipt.

The agent-adapter slice answered the next weakness after structured receipts. `scripts/agent_trace.py` adds ShipGuard TraceBridge through `shipguard agent trace` and `shipguard codex trace`: a dependency-light adapter that consumes exported or synthetic Codex-style traces, normalizes evidence receipts, optionally runs `shipguard verify`, attaches the verdict handoff, emits a v2 runtime receipt, and enforces the 2-3 worker / five-worker cap policy. `agentAdapterReceipts` prove four public paths: prepare a task, run a trace with verify and a v2 receipt, block an over-budget trace, and route the Codex alias.

The Expo/EAS assurance slice answered the next weakness after XcodeBuildMCP evidence. `shipguard agent trace --expo-eas-evidence <file-or-dir>` and `shipguard codex trace --expo-eas-evidence <file-or-dir>` attach Expo MCP routing, Expo prebuild, EAS build/update, native runtime logs, artifact-integrity metadata, and credential-boundary proof to the same task timeline and runtime receipt. `expoEASAssuranceReceipts` prove the adapter with public synthetic evidence while keeping Expo/EAS assurance separate from store, TestFlight, physical-device, and production-rollout proof.

The universal-agent packaging slice answers the next weakness after Expo/EAS assurance. `shipguard agent trace --adapter claude|gemini|cursor|mcp|generic` now emits adapter packaging guidance, shared schema metadata, and `universal-agent-packaging-adapter` runtime receipts for non-Codex traces. `universalAgentPackagingReceipts` prove the adapter with public synthetic Claude, Gemini, Cursor, MCP, and auto-detection traces.

The full-audit slice answers the next weakness after universal packaging. `shipguard full-audit` now plans and runs validation, value-gauntlet, report-quality, package proof, install refresh, plugin status, CI proof, and release-proof preparation through resumable stage receipts. `fullAuditOrchestratorReceipts` prove plan-only release coverage, mini execution, and resume reuse on public fixtures. With those receipts green, the next value-gauntlet weakness was the v3.125 unified inspect experience: ShipGuard proof state was split across too many reports and needed one concise inspect surface without hiding underlying evidence.

The unified inspect slice adds `shipguard inspect` and `fixtures/tool-value-gauntlet/unified-inspect-receipts`. `unifiedInspectReceipts` create synthetic value-gauntlet, full-audit, and release-proof inputs, run InspectDeck, and require one shareable report with repo state, proof inputs, plugin state, release state, underlying evidence, scope boundary, and one exact next action.

The concise result-UX slice adds `scripts/shipguard_result.py` and `fixtures/tool-value-gauntlet/concise-verdict-result-ux-receipts`. `conciseVerdictResultUXReceipts` run full-audit, iOS design, iOS performance, and InspectDeck on public/synthetic inputs and require each report to lead with `resultUX` plus Markdown `## Result`: verdict, proof source, why it matters, and one next command.

The Codex marketplace-readiness slice adds `scripts/codex_marketplace_readiness.py`, `docs/codex-marketplace-readiness.md`, and `fixtures/tool-value-gauntlet/codex-marketplace-readiness-receipts`. `codexMarketplaceReadinessReceipts` run the public MarketplaceDeck path and require plugin metadata, local marketplace source, README/profile presentation, icon assets, screenshot policy, strict status proof, privacy/model-choice boundaries, and a copy-ready submission packet.

The External Benchmark v2 slice extends `shipguard pilot-bench` with `--benchmark-v2` and adds `fixtures/tool-value-gauntlet/external-benchmark-v2-receipts`. `externalBenchmarkV2Receipts` run public-safe comparative traces with `baselineVerdict`, require meaningful ShipGuard score lift, and prove verdict usefulness without private app leakage. With those receipts green, the next value-gauntlet weakness was v4 preview stabilization.

The V4 Release Candidate Readiness slice adds `shipguard v4 release-candidate`, `docs/v4-release-candidate.md`, and `fixtures/tool-value-gauntlet/v4-release-candidate-readiness-receipts`. `v4ReleaseCandidateReadinessReceipts` prove the release-candidate report has fresh install, package-tarball fresh-install proof, same-prefix upgrade proof, rollback cleanup proof, release-proof consumption, external adoption evidence proof, final security-review evidence proof, external adoption packet, final schema docs, plugin refresh proof, release-readiness checks, blocked stable-release claims, and shared result UX. `v4ProductReleaseStabilizationReceipts` now extend that proof with a public fixture that builds release proof, derives a previous package, assembles downloaded release assets, runs LaunchKey with package/upgrade/rollback/release-consume/adoption/security evidence, and hands the result to report-quality. With those receipts green, the next value-gauntlet weakness is real stable-v4 publication proof from downloaded GitHub release assets plus independent adoption/security evidence.

A later read-only Ringly/Ilmify product-QA loop exposed a ShipGuard-owned performance problem rather than an app task: large or file-provider-backed source trees could make `ios doctor`, `ios performance`, `ios design`, and `ios modernize` spend too long reading Swift/text files before any useful report appeared. ShipGuard now uses a shared bounded text reader for source heuristics, records `scanScope.textBytesPerFileLimit`, `textReadTimeoutSeconds`, truncated files, omitted large files, and timed-out files in JSON/Markdown, and proves the behavior with `tests/ios_scan_scope_budget_test.sh` using a public synthetic large Swift file. These reports remain useful first-pass evidence, but sampled or omitted files are explicitly disclosed so source coverage is not overstated.

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
- `shipguard ios launchdeck` as the native ShipGuard front door for LaunchDeck build/run/debug/preview/profiler workflows without vendoring the plugin or faking MCP execution from the CLI.
- `shipguard ios performance` as a read-only source scanner for ranked SwiftUI/runtime performance hotspots before Codex chooses edits.
- `--shipguard-eval` as the explicit ShipGuard-only product QA mode for private real-app samples across `ios performance`, `ios design`, `ios modernize`, `ios app-intelligence`, and `ios ai-readiness`.
- `shipguard ios design` for genre-aware UI/UX coherence, design DNA, motion, haptics, preview routing, and ImageGen app-icon handoff.
- `shipguard ios report-quality` to score ShipGuard's own read-only reports for boundaries, evidence, proof guidance, scan scope, Markdown usefulness, token/path shareability, and redaction handoff before turning observations into public fixtures or eval cases.
- `shipguard value-gauntlet` to score every ShipGuard command, skill, plugin, GitHub Action, doc, package proof path, and proof boundary for developer usefulness before a branded surface is treated as mature.
- `shipguard ios devspace-check` to score Devspace connector readiness, public URL safety, MCP widget metadata, preview evidence, handoff execution boundaries, handoff fixture quality, and ChatGPT model-choice honesty before tunneled visual planning is treated as useful.
- `shipguard ios spec-workflow` to convert report-quality actionability questions into ShipGuard-owned constitution, spec, requirements checklist, native integration decisions, implementation plan, tasks, consistency analysis, analysis gates, slash plan/goal, and Devspace guardrails before Codex implementation.
- `shipguard ios external-audit` to convert Spec Kit, CodexPro, Ponytail, Expo, Design Motion Principles, native iOS workflow skills, X posts, and other external ideas into a native replacement ledger before ShipGuard claims adoption.
- Shared iOS scan-scope exclusions for generated/proof/cache directories, plus tests that generated artifacts do not become report findings.
- A repository threat model artifact before running a full Codex Security scan.
- More Arena fixtures for security-sensitive workflows: credentials, untrusted paths, generated artifacts, network posting, GitHub token scope, and release asset trust.
- Optional OpenAI Agents SDK evaluation only if ShipGuard becomes a runnable agent service. Do not add OpenAI API dependencies to the CLI without that product decision.
- Keep the open-source operating model first-class: contribution flow, support routing, governance, code of conduct, issue templates, package proof, and public docs should stay ShipGuard-native rather than copied from another project.

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

## Current Plugin Skill Routing Value-Gauntlet Fixture

The next read-only ShipGuard self-QA pass showed `shipguard value-gauntlet` still prioritized this question after the stable-publication, product-release, and surface proof-boundary questions were covered: "Do plugin skills and starter skills give Codex actionable routing and validation commands, not just vague advice?" `ios report-quality --write-fixture-candidates` now classifies plugin-skill, starter-skill, actionable-routing, and validation-command questions as `shipguard-plugin-skill-routing-fixture` candidates.

The promoted public fixture is `fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question`. Focused tests prove the live value-gauntlet report now marks that question as covered, emits no duplicate fixture candidate, and scores the promoted fixture as an existing fixture instead of recursively generating another candidate. The package proof also checks the fixture files ship in release archives.

## Current Stable-Publication Fixture Review

The following read-only self-QA pass moved from uncovered candidate generation to existing-fixture review. Reviewing `fixtures/ios-report-quality/stable-publication-value-gauntlet-question` exposed stale generated metadata inside the promoted fixture: nested candidate ids and suggested paths still referenced the original materialized slug instead of the stable public fixture path. The fixture now uses `stable-publication-value-gauntlet-question` consistently and records the fixture type as `shipguard-release-proof-quality-fixture`; focused tests assert both fields during report-quality scoring.

## Current Existing-Fixture Metadata Sweep

The next read-only sweep broadened that review from one fixture to all promoted report-quality fixtures. It found older fixtures whose `fixture-candidate.json` or nested `fixtureCandidate` metadata did not consistently name the promoted folder or public fixture path. The fixture set now carries canonical `candidateId`, `publicFixturePath`, and nested fixture type metadata, and `ios_report_quality_test.sh` includes a repository-wide consistency check so future promoted fixtures cannot drift from their public paths.

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
- Added `shipguard ios launchdeck` after integration review showed LaunchDeck should be reachable through a native ShipGuard command that records topology, workflow routing, proof boundaries, and report-quality questions before Codex executes simulator or profiler tools.
- Added `--shipguard-eval` so private Ringly/Ilmify-style checks are explicitly ShipGuard-only QA, not target-app remediation work.
- Changed the performance report shape to include rule summaries, capped repeated rules in Markdown, exact evidence snippets, and full JSON findings for deeper follow-up.
- Added grouped performance `firstExperiment` output after report-quality kept prioritizing whether grouped actions named the smallest reversible proof step before broad refactors.
- Added grouped performance `validationRoute` and `stopCondition` output after public fixture, Ringly, and Ilmify read-only passes showed first experiments still needed explicit proof routes and stop gates before broader work.
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
- Added the preview/Devspace routing fixture after read-only design-QA reports showed the iPhone visual-proof path needed to be enforced as a report-quality contract, not repeated as private-app advice.
- Improved first-run adoption docs around CLI versus plugin usage.
- Reworked the README after GitHub-facing evaluation showed the front page had become a noisy release-internals dump. The public entry point now leads with a short product promise, install, RepoVitals, prepare/verify, demo, and core docs, while detailed release and v4 proof work stays in dedicated docs. The same slice added `docs/install-doctor.md`, RepoVitals-style `shipguard doctor` output, and installed-CLI proof in `tests/install_doctor_test.sh`.
- Fixed the next verify-first launch QA gap after a fresh read-only run of the public quickstart pass/review/blocked reports: `ios report-quality` ranked the task-contract actionability questions but produced no fixture candidates. Prepare/verify questions now materialize as `shipguard-verify-first-task-contract-fixture` starters, and the focused report-quality test proves all five quickstart questions can become public synthetic fixtures.
- Promoted the first verify-first task-contract fixture after a fresh read-only quickstart QA run kept re-materializing the durable-object question. `prepare` and `verify` now emit `quickstartReplay` in JSON plus Markdown so new maintainers see the first verdict or replay path in the report itself; report-quality fails task-contract reports that hide this contract; and the promoted public fixture makes the next fresh quickstart QA run advance to unsupported-claim coverage.
- Promoted the unsupported-claim replay fixture after fresh verify-first QA advanced to that question. `verify` now emits `unsupportedClaimReplay` for rejected or manual-proof broad completion wording, Markdown renders the claim-specific replay and repair path, report-quality fails missing/weak unsupported-claim replay sections, and the public synthetic fixture keeps this covered so the next fresh QA run advances to notification-permission scope specificity.
- Promoted the notification-permission scope specificity fixture after fresh verify-first QA advanced to that question. `ios report-quality` now fails prepare reports that claim notification/permission scope specificity but hide authorized owner scopes, review-only lifecycle/plist surfaces, forbidden entitlement/project boundaries, permission-sensitive source signals, or the Markdown `iOS Notification Permission Workflow`; the public synthetic fixture keeps this covered and led into the now-covered structured receipt proof-lane specificity fixture.
- The next one-command installer QA pass installed ShipGuard into a temporary prefix and proved the installed CLI could validate, initialize, doctor, prepare, and verify the public quickstart pass report. The product weakness was first-run guidance and proof coverage: `install.sh` only listed file destinations, README immediately used `shipguard` as if PATH were already configured, and the focused install test stopped before installed `verify`. The installer now emits a `ShipGuard Install Receipt` with exact installed-binary next commands and the install test proves the installed wrapper reaches a passing proof report.
- Upgraded `shipguard next-goal` so the next improvement loop emits a reviewable `/plan` before the `/goal`, and can now carry bounded scope, completion evidence, and the following `/goal` handoff.
- Added Brand Deck actionability questions after a read-only `shipguard brand` plus `ios report-quality` pass showed the naming report was structurally clean but still produced the generic "add reportQualityQuestions" priority action instead of a concrete naming-system improvement.
- Expanded Brand Deck from an iOS-heavy surface list to a toolkit-wide naming contract after the full-renaming request showed root commands, release commands, CI tools, transcript tools, plugin status, and smaller preview handoff helpers also needed branded names and future coverage checks.
- Moved legacy command-wrapper guidance out of primary README and CLI flow into `docs/compatibility.md`.
- Keep Agents SDK deferred unless ShipGuard becomes a runnable agent service with a concrete eval target.
