# ShipGuard Evaluation

Generated: 2026-06-17

This is the current usefulness and refinement evaluation for ShipGuard after the rename and README repositioning work.

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

The next external-source review showed even that was still too static: Spec Kit, CodexPro, Expo, and social-post ideas were represented as hardcoded inspiration inside spec-workflow instead of a repeatable source audit. `ios external-audit` now records read-only source checkouts and URLs, classifies source capabilities, emits a native replacement ledger, states what ShipGuard replaces, extends, keeps, routes, or defers, and carries license/no-vendoring boundaries plus report-quality questions. A source is not considered integrated until its capability has a ShipGuard-native action and validation command.

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

The V4 Release Candidate Readiness slice adds `shipguard v4 release-candidate`, `docs/v4-release-candidate.md`, and `fixtures/tool-value-gauntlet/v4-release-candidate-readiness-receipts`. `v4ReleaseCandidateReadinessReceipts` prove the release-candidate report has fresh install, package-tarball fresh-install proof, same-prefix upgrade proof, rollback cleanup proof, release-proof consumption, external adoption packet, final schema docs, plugin refresh proof, release-readiness checks, blocked stable-release claims, and shared result UX. With those receipts green, the next value-gauntlet weakness is v4 product release stabilization: external adoption evidence, final security review, package proof, rollback proof, and release proof consumption on published assets.

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
- `shipguard ios external-audit` to convert Spec Kit, CodexPro, Expo, Design Motion Principles, native iOS workflow skills, X posts, and other external ideas into a native replacement ledger before ShipGuard claims adoption.
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
- Improved first-run adoption docs around CLI versus plugin usage.
- Upgraded `shipguard next-goal` so the next improvement loop emits a reviewable `/plan` before the `/goal`, and can now carry bounded scope, completion evidence, and the following `/goal` handoff.
- Added Brand Deck actionability questions after a read-only `shipguard brand` plus `ios report-quality` pass showed the naming report was structurally clean but still produced the generic "add reportQualityQuestions" priority action instead of a concrete naming-system improvement.
- Expanded Brand Deck from an iOS-heavy surface list to a toolkit-wide naming contract after the full-renaming request showed root commands, release commands, CI tools, transcript tools, plugin status, and smaller preview handoff helpers also needed branded names and future coverage checks.
- Moved legacy command-wrapper guidance out of primary README and CLI flow into `docs/compatibility.md`.
- Keep Agents SDK deferred unless ShipGuard becomes a runnable agent service with a concrete eval target.
