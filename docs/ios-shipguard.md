# iOS ShipGuard

`iOS ShipGuard` is the product-facing layer for this repository: a Codex plugin, skill, and CLI mode for solo iOS developers working on apps where permissions, notifications, StoreKit, widgets, App Intents, background work, and release proof matter.

The existing `shipguard` CLI remains the engine. ShipGuard is the iOS-focused workflow that makes the engine easier to use.

ShipGuard uses a toolkit-wide branded surface scheme so the tool feels coherent without making the CLI cryptic. Run ShipGuard Brand Deck before adding or renaming public surfaces:

```bash
./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict
```

The command writes `ios-branding.json` and `ios-branding.md` with the current naming rules, future naming contract, public command coverage, and surface names such as ShipGuard StarterBay, ShipGuard RigCheck, ShipGuard Tool Value Gauntlet, ShipGuard DockCheck, ShipGuard LaunchDeck, ShipGuard PulseRadar, ShipGuard VibeCheck, ShipGuard BridgeWatch, ShipGuard HandoffRail, ShipGuard ReleaseDock, ShipGuard PluginRadar, ShipGuard SelfScan, and ShipGuard NextRail. `shipguard ios brand` remains available as a compatibility route.

Run ShipGuard Tool Value Gauntlet when the question is whether the ShipYard itself is genuinely useful, not just well named:

```bash
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable
```

That report grades ShipGuard commands, skills, plugin metadata, GitHub Actions, docs, tests, package proof, and proof boundaries. It also emits a Lowest-Value Surface Probe, `runtimeOutputProbe`, `runtimeOutputNegativeFixtures`, `runtimeCommandFamilyCoverage`, `skillPluginRuntimeReceipts`, `workflowChainReceipts`, `scenarioMatrixReceipts`, and `scenarioFailureReceipts`: first it ranks deeper evidence signals across the ShipYard, then it executes representative ShipGuard commands on public/demo inputs and scores whether their generated JSON/Markdown is specific, prioritized, proof-oriented, and machine-readable. Negative fixtures prove decorative empty reports and boundaryless design reports are rejected. Command-family coverage executes `--help` for every public command so unwired entry points are caught at runtime. Skill/plugin receipts execute public design-audit, starter UI-polish, and plugin-cache proof workflows so Codex guidance is tested through realistic workflows. Workflow-chain receipts run design report -> report-quality -> spec-workflow -> spec report-quality -> next-goal so actionability questions must become tasks, validation commands, slash plan/goal text, and a following goal. Scenario-matrix receipts run a complete public maintainer loop across iOS discovery/planning/design, report-quality, docs, privacy redaction/verification, CI, Codex plugin status, and release manifest/index/replay. Scenario-failure receipts prove unsafe transcripts, broken docs, stale plugin cache, and incomplete release proof are blocked with concrete evidence. When those probes pass, the next priority becomes scenario-remediation receipts that pair each block with the smallest repair command and successful rerun. Use its priority actions to upgrade ShipGuard itself; do not turn private Ringly or Ilmify evidence into app work unless a later task explicitly asks for app changes.

## What Codex Already Does

Do not duplicate Codex platform features. Use them directly:

- Codex app skills, modes, worktrees, terminal, and built-in Git tools: [Codex app features](https://developers.openai.com/codex/app/features).
- Inline diff comments for asking Codex to change specific code: [Codex app features](https://developers.openai.com/codex/app/features).
- Simulator debugging through XcodeBuildMCP and the LaunchDeck surface: [Debug in iOS simulator](https://developers.openai.com/codex/use-cases/ios-simulator-bug-debugging).
- Browser comments on local previews through the Codex in-app browser: [In-app browser](https://developers.openai.com/codex/app/browser).
- GUI-only verification through computer use when structured tools are not enough: [Computer Use](https://developers.openai.com/codex/app/computer-use).

ShipGuard adds the missing layer before those tools run: repo-aware build routing, risk routing, permission inventory, ask-before-editing gates, and evidence prompts.

## First Useful Commands

Run doctor first so Codex understands the app topology before choosing a build, simulator, or proof route:

```bash
./bin/shipguard ios doctor --path . --out /tmp/ios-shipguard-doctor
```

The command writes:

- `ios-doctor.md`
- `ios-doctor.json`

It detects Xcode projects, workspaces, Swift packages, schemes, deployment targets, Swift versions, bundle IDs, test plans, StoreKit configs, privacy manifests, plists, entitlements, Swift imports, and proof-readiness findings.

Then inventory risky permission and runtime surfaces. Inventory reuses doctor topology automatically so every detected surface can be mapped back to an app, package, or test target when the local files make ownership clear:

```bash
./bin/shipguard ios inventory --path . --out /tmp/ios-shipguard-inventory
```

Use a saved doctor report when CI or another Codex step should consume the exact same topology:

```bash
./bin/shipguard ios inventory \
  --path . \
  --doctor /tmp/ios-shipguard-doctor/ios-doctor.json \
  --out /tmp/ios-shipguard-inventory
```

The command writes:

- `ios-inventory.md`
- `ios-inventory.json`

It detects permission and runtime surfaces such as notifications, AlarmKit, Location, Camera, Microphone, Photos, HealthKit, Push Notifications, App Groups, Background Modes, Live Activities, WidgetKit, App Intents, StoreKit, Swift concurrency, Foundation Models, and Core ML.

The Markdown report starts with a target risk map, then shows detected surfaces, permission and entitlement review, unmapped surfaces, modernization opportunities, Codex workflow prompts, and ask-before-editing questions.

When source uses a permission-backed surface but the expected usage description or entitlement is missing, the report marks the surface as `needs-user-answer`. Codex should stop and ask the user before editing.

Try the public fixture:

```bash
./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-demo-doctor
./bin/shipguard ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor /tmp/ios-shipguard-demo-doctor/ios-doctor.json \
  --out /tmp/ios-shipguard-demo
```

## Guided Plan

Generate a Codex-ready task brief from inventory:

```bash
./bin/shipguard ios plan \
  --mode permission-audit \
  --inventory /tmp/ios-shipguard-demo/ios-inventory.json \
  --out /tmp/ios-shipguard-plan/ios-plan.md
```

The plan captures selected mode, blocked questions, owner files, selected surfaces, target summary, proof route, and a concise Codex brief. When inventory marks `needs-user-answer`, the plan status is also `needs-user-answer`; Codex should ask those questions before editing.

## Proof Router

Route proof from a generated plan:

```bash
./bin/shipguard ios prove \
  --plan /tmp/ios-shipguard-plan/ios-plan.json \
  --out /tmp/ios-shipguard-proof
```

The proof report records the smallest honest evidence lane and names any manual blockers. It does not execute builds, simulator actions, StoreKit purchases, TestFlight checks, App Store Connect checks, or device proof. It tells Codex which proof is still required before a claim can be made.

## LaunchDeck Bridge

Use `ios launchdeck` when the user wants ShipGuard to be the one command they remember for build, run, debug, preview, or performance investigation work:

```bash
./bin/shipguard ios launchdeck \
  --path . \
  --out /tmp/ios-shipguard-launchdeck
./bin/shipguard ios launchdeck \
  --path . \
  --workflow performance \
  --shipguard-eval \
  --shareable \
  --out /tmp/ios-shipguard-launchdeck-eval
./bin/shipguard ios launchdeck \
  --path . \
  --workflow performance \
  --receipt /tmp/codex-launchdeck-proof \
  --shipguard-eval \
  --shareable \
  --out /tmp/ios-shipguard-launchdeck-receipts
```

The command is read-only against `--path` and writes only to `--out`. It creates `ios-launchdeck.json` and `ios-launchdeck.md`. The report discovers Xcode projects, workspaces, Swift packages, schemes, test plans, StoreKit configs, privacy manifests, SwiftUI preview declarations, and skipped generated/proof/cache directories. It then recommends one LaunchDeck route:

- XcodeBuildMCP build/run through `session_show_defaults`, `session_set_defaults`, and `build_run_sim`.
- Debugger and runtime investigation with focused log capture plus UI snapshot or screenshot evidence.
- Simulator browser proof through `serve-sim` when live visual inspection is the goal.
- SwiftUI preview hot reload through `swiftui-preview-browser.mjs` for package-backed preview work.
- Performance profiling through Animation Hitches, Time Profiler, sample/log fallback evidence, and physical-device proof boundaries.

ShipGuard owns the front door: topology discovery, workflow selection, report quality, proof boundaries, redaction/shareability, and next-action text. Codex iOS execution tools perform simulator build/run, UI inspection, simulator browser streaming, SwiftUI preview hosting, logs, debugger, and profiler captures inside Codex. LaunchDeck owns route selection and receipt grading. A plain CLI process cannot call Codex MCP tools by itself, so the report names the MCP/tool route Codex should execute instead of pretending the shell already performed simulator work.

Use `--workflow auto|build-run|debug|preview|performance` when the desired proof lane is known. After Codex executes the LaunchDeck route, add one or more `--receipt <file-or-dir>` inputs to grade whether the actual proof bundle contains the right signals for the selected lane: build/run logs and UI proof for build-run, log plus UI proof for debug, `serve-sim` plus screenshot proof for simulator browser, SwiftUI preview hot-reload output for preview lanes, and Animation Hitches, Time Profiler, `xctrace`, ETTrace, or sample proof for performance lanes. No `--receipt` means the report is only a route plan; supplied but incomplete receipts make the report status `review`.

Use `--shipguard-eval --shareable` when a private app is only a read-only sample for improving ShipGuard's LaunchDeck output, then score the report with `ios report-quality --shareable`.

## Performance Audit Mode

Use `performance-audit` when the user reports FPS drops, hitches, slow launch, laggy scrolling, touch latency, thermal pressure, or device-specific smoothness problems:

```bash
./bin/shipguard ios performance \
  --path . \
  --out /tmp/ios-shipguard-performance
./bin/shipguard ios plan \
  --mode performance-audit \
  --inventory /tmp/ios-shipguard-demo/ios-inventory.json \
  --out /tmp/ios-shipguard-performance-plan
./bin/shipguard ios prove \
  --plan /tmp/ios-shipguard-performance-plan/ios-plan.json \
  --out /tmp/ios-shipguard-performance-proof
```

The `ios performance` report is read-only. It scans Swift source for ranked hotspots such as high-frequency `TimelineView`, continuous `repeatForever` animation, large blur/shadow composition, formatter allocation in SwiftUI paths, image decoding in UI paths, and notification cleanup that may block launch or interaction. Each finding includes an impact explanation that is shown in Markdown as "Why it matters", so private-app product-QA runs can prioritize ShipGuard improvements without relying on hidden app context. High findings also include `severityReason`, rendered as "Why severity", so the report distinguishes explicit thresholds or actor-context signals from broad suspicion. Findings now split proof into `localProof` and `manualProof`, rendered as "Codex local proof" and "Manual/device proof", so a solo developer can tell what Codex can verify in the current thread and what still needs physical-device, account, TestFlight, or human proof. Rules are summarized in `groupedActionPlan` and a Markdown `Grouped Next Actions` section before individual rows; each grouped action includes a `firstExperiment`, `validationRoute`, and `stopCondition` so the report starts from one reversible proof step, states how to validate it, and blocks broader refactors until the first experiment has signal. iOS source scanners skip generated/proof/cache directories and list those scan-scope exclusions in JSON and Markdown so large app workspaces do not turn release artifacts or scratch files into product findings.

Use `--shareable` when a performance report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`; default local reports keep the absolute project root for operator debugging.

The plan tells Codex to build and launch the same route being measured, try Animation Hitches or Time Profiler when supported, fall back to `sample`, logs, screenshots, and symbolication when `xctrace` is unavailable, and keep protected runtime boundaries explicit. It also blocks device-level smoothness claims until a physical-device Instruments trace exists for touch latency, ProMotion refresh, thermal pressure, replacement displays, sensors, audio, or wake timing.

## ShipGuard Report-Quality Eval Mode

Use `--shipguard-eval` only when a real app is acting as a private read-only sample for improving ShipGuard itself:

```bash
./bin/shipguard ios performance \
  --path <private-ios-app> \
  --out /tmp/ios-shipguard-performance-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios design \
  --path <private-ios-app> \
  --out /tmp/ios-shipguard-design-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios launchdeck \
  --path <private-ios-app> \
  --workflow auto \
  --out /tmp/ios-shipguard-launchdeck-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios modernize \
  --focus swift \
  --path <private-ios-app> \
  --out /tmp/ios-shipguard-modernize-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios app-intelligence \
  --path <private-ios-app> \
  --out /tmp/ios-shipguard-app-intelligence-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios ai-readiness \
  --path <private-ios-app> \
  --out /tmp/ios-shipguard-ai-readiness-eval \
  --shipguard-eval \
  --shareable
./bin/shipguard ios report-quality \
  --reports /tmp/ios-shipguard-launchdeck-eval \
  --reports /tmp/ios-shipguard-performance-eval \
  --reports /tmp/ios-shipguard-design-eval \
  --reports /tmp/ios-shipguard-modernize-eval \
  --reports /tmp/ios-shipguard-app-intelligence-eval \
  --reports /tmp/ios-shipguard-ai-readiness-eval \
  --out /tmp/ios-shipguard-report-quality \
  --shareable
```

Those reports add a ShipGuard evaluation boundary. Findings from those runs must be used to improve ShipGuard rules, report shape, docs, or public fixtures; they must not become target-app remediation tasks without a separate explicit app-work request. Markdown output may be grouped or capped to stay reviewable; JSON keeps the full finding list for deeper ShipGuard product QA. Use `--shareable` on every report that will move into report-quality scoring or external planning so the shareability contract is explicit.

`ios report-quality` then grades ShipGuard's output quality, not the scanned app. It checks whether the reports are parseable, scoped to read-only product QA, paired with Markdown, honest about skipped scan scope, useful in finding evidence/recommendation/proof guidance, explicitly declared shareable when scored in `--shareable` mode, and safe to share or redact. For `ios launchdeck`, this means the report must make LaunchDeck workflows obvious while keeping ShipGuard routing/proof ownership separate from simulator/debugger/profiler execution; weak receipt reports prioritize receipt-specific questions and materialize `ios-launchdeck-receipt-quality-fixture` starters so missing build/run, UI, preview, log, or profiler proof becomes a public ShipGuard eval case. Source report issues stay visible even when report-quality itself passes: JSON includes `sourceFindings` and `sourceIssueVisibility`, and Markdown renders `Source Report Findings` separately from report-quality `Findings`. For `ios performance`, it also checks that findings explain their impact in JSON, that Markdown surfaces that explanation for human review, that high findings explain why severity is high in JSON and Markdown, that performance proof guidance is split into local and manual/device fields in JSON and Markdown, that repeated rules have a JSON `groupedActionPlan` plus visible Markdown `Grouped Next Actions`, and that grouped actions expose a smallest `firstExperiment`, `validationRoute`, and `stopCondition` in JSON and Markdown. It aggregates each input report's `reportQualityQuestions` into an actionability checklist and emits `priorityAction` plus `prioritizedActionabilityQuestions`, preferring report-quality findings first and otherwise questions from lower-status source reports, so the next ShipGuard rule, fixture, report section, or docs improvement is explicit. It also emits `fixtureCandidates` when questions point to public fixture or eval-case work; those candidates include a synthetic fixture path, source question, validation commands, materialization metadata, and a private-data policy so Ringly/Ilmify observations become public ShipGuard tests without copying private code, screenshots, paths, or app identifiers. Add `--write-fixture-candidates <dir>` to write path-safe synthetic starter directories containing `fixture-candidate.json`, `fixture-report.json`, `fixture-report.md`, and validation notes. The materialized output also writes `fixture-promotion-manifest.json` and `PROMOTION.md` with suggested repo-relative fixture paths, placeholder copy commands, validation commands, and a private-data review checklist; promotion remains explicit maintainer work and ShipGuard does not auto-copy candidates into the repository. When a materialized fixture root is scored, report-quality consumes `fixture-promotion-manifest.json` as metadata, renders `Fixture Promotion Manifests`, and flags unsafe paths, local/token-like metadata, missing copy placeholders, missing validation commands, incomplete review checklists, stale guide paths, or missing materialized files without treating the manifest as a source report. When an already-materialized synthetic fixture is scored again, report-quality keeps its actionability question evidence but does not emit a recursive fixture candidate for the fixture itself. When a new report repeats a question already covered by a promoted fixture under `fixtures/ios-report-quality`, report-quality now renders `Fixture Coverage`, suppresses the duplicate candidate, and moves `priorityAction` to the next uncovered question. Token-like connector URLs or auth strings are detected without echoing token values, then a redaction plan with `shipguard ios redact` commands is emitted for any report set that should not be shared raw. Add `--shareable` when the report-quality artifact itself will move into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence; default local output keeps absolute input/report paths for operator debugging.

In `--shareable` report-quality mode, supported source reports that are missing `shareability` metadata receive `declared-shareability-missing`, and reports that declare `mode=local` or `localAbsolutePathsIncluded=true` receive `declared-shareability-local-mode`. Regenerate those source reports with `--shareable`; redaction remains the right path only for actual token or local-path findings.

## External Source Audit

Use `ios external-audit` before claiming ShipGuard has integrated another repo, post, or workflow idea:

```bash
./bin/shipguard ios external-audit \
  --path . \
  --source-path /tmp/spec-kit \
  --source-path /tmp/codexpro \
  --source-url https://github.com/expo/expo \
  --source-url https://x.com/example/status/1234567890 \
  --shipguard-eval \
  --shareable \
  --out /tmp/ios-shipguard-external-audit
```

The command is read-only against source checkouts and writes only to `--out`. It creates `ios-external-audit.json`, `ios-external-audit.md`, and `replacement-ledger.md`. The report records source inputs, local evidence signals, license boundaries, a capability matrix, replacement decisions, a ShipGuard-native implementation backlog, and report-quality questions. It treats sources such as Spec Kit, CodexPro, Expo, Design Motion Principles, native iOS workflow skills, and social posts as product inputs; ShipGuard adoption means a capability has a native ShipGuard action plus validation, not that external source code or templates were copied into this repo. The deterministic `ios eval` fixture suite includes an `external-source-audit` case so future routing changes keep source adoption on this read-only proof path.

Use `--source-path` for a local read-only checkout when available; use `--source-url` for a public repo or post that still needs a source snapshot. Use `--shareable` before sending the audit to ChatGPT, GitHub, docs, release evidence, or `ios report-quality`. Feed the audit into `ios report-quality --shareable` and then into `ios spec-workflow --from-report` when a replacement decision needs implementation work.

## Spec Workflow

Use `ios spec-workflow` when a ShipGuard report-quality pass has useful actionability questions but the next implementation still needs a governed spec, plan, and task breakdown:

```bash
./bin/shipguard ios spec-workflow \
  --path <private-ios-app-or-shipguard-repo> \
  --feature "Improve report actionability" \
  --from-report /tmp/ios-shipguard-report-quality \
  --shipguard-eval \
  --shareable \
  --out /tmp/ios-shipguard-spec
```

The command is read-only against `--path` and writes only to `--out`. It creates `ios-spec-workflow.json`, `ios-spec-workflow.md`, `shipguard-constitution.md`, `feature-spec.md`, `requirements-checklist.md`, `integration-decisions.md`, `implementation-plan.md`, `tasks.md`, `consistency-analysis.md`, and `devspace-guardrails.md`. The workflow adapts useful product patterns from Spec Kit-style constitution/spec/checklist/plan/tasks/analyze sequencing, CodexPro-style connector guardrails, Expo-style open-source product shape, Xcode build-optimization recommendation/proof loops, and the OpenAI native iOS preview loop into ShipGuard-owned artifacts. `integration-decisions.md` is the replacement/evaluation layer: each external idea must be marked as native extension, current-surface keeper, weaker-guidance replacement, route integration, or deferral before it counts as adopted. ShipGuard does not install, vendor, or depend on those projects.

Add `--from-report` for `ios report-quality` output or any source-scanner report so actionability questions become clarifying questions instead of app-remediation tasks. Repeated report-quality questions are deduplicated before spec-workflow applies its clarifying-question and task caps, so the first unique questions survive into JSON and Markdown. Add `--shipguard-eval` when the scanned repo is Ringly, Ilmify, or another private app used only as ShipGuard product QA. Add `--shareable` before moving the generated spec workflow into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or another `ios report-quality` pass.

`ios report-quality --shareable` checks spec-workflow adoption quality. A spec workflow with no `--from-report` evidence or no actionability questions receives `spec-workflow-report-context-missing` or `spec-workflow-actionability-missing`, because otherwise the generated plan can look polished without being grounded in an observed ShipGuard report weakness. It also verifies that declared spec-workflow artifact files exist and are non-empty beside `ios-spec-workflow.json`; missing bundle files receive `spec-workflow-artifact-file-missing` without exposing local absolute paths. Placeholder-only or structurally weak artifact text receives `spec-workflow-artifact-content-incomplete` or `spec-workflow-artifact-placeholder-content`, including the requirements checklist, integration decisions, and consistency analysis. If actionability questions are present but not preserved in JSON or Markdown clarifying questions, the requirements checklist, integration decisions, and the consistency analysis, report-quality emits `spec-workflow-question-coverage-missing` or `spec-workflow-question-artifact-missing`. If the acceptance criteria drop those questions, it emits `spec-workflow-acceptance-coverage-missing` or `spec-workflow-acceptance-artifact-missing`. If those questions do not become proof-gated tasks in `taskPlan` and `tasks.md`, it emits `spec-workflow-task-coverage-missing` or `spec-workflow-task-artifact-missing`. If validation commands are missing from `technicalPlan.recommendedValidation` or `implementation-plan.md`, it emits `spec-workflow-validation-coverage-missing` or `spec-workflow-validation-artifact-missing`. If the analysis gates are replaced by generic placeholders, it emits `spec-workflow-analysis-coverage-missing` or `spec-workflow-analysis-artifact-missing`. If `slashPlan`, `slashGoal`, or `ios-spec-workflow.md` drops the copy-ready `/plan` and `/goal` next-loop handoff, it emits `spec-workflow-slash-handoff-incomplete` or `spec-workflow-slash-handoff-artifact-missing`.

## Design QA Audit

Run a genre-aware UI/UX and design-coherence audit before asking Codex to redesign screens, tune motion, add haptics, judge visual DNA, or create an app icon direction:

```bash
./bin/shipguard ios design \
  --path . \
  --out /tmp/ios-shipguard-design
./bin/shipguard ios design \
  --path . \
  --app-type game \
  --preview-out /tmp/ios-shipguard-preview \
  --icon-brief \
  --shareable \
  --out /tmp/ios-shipguard-design-game
```

The report infers app type, records design DNA signals, emits a ShipGuard-native motion blueprint and `motionQualityGates`, emits an iOS haptics blueprint, and tells Codex when `ios preview` or `ios devspace` should be used. Frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance gates are weighted by app type as ShipGuard report data. App-type inference weights app/project source above repeated docs or agent-instruction wording; use `--app-type` when the automatic genre inference is wrong or the user has already named the product category.

Use `--shareable` when a design report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`; default local reports keep absolute roots for operator debugging.

Use `--icon-brief` for app-icon work. ShipGuard writes `app-icon-imagegen-brief.md` for ChatGPT ImageGen and an App Store asset checklist; it does not generate CSS, SVG, or local placeholder icon art.

## Preview Bridge

ShipGuard can serve a local phone-shaped preview page for Codex's in-app browser:

```bash
./bin/shipguard ios preview --out /tmp/ios-shipguard-preview
```

The command binds to `127.0.0.1`, captures the booted Simulator with `xcrun simctl io booted screenshot --type=png <tempfile>`, and writes `session.json`, `preview-url.txt`, `preview-events.jsonl`, `handoff.json`, `handoff.md`, and `last-screenshot.png`.

Open the printed URL in Codex's in-app browser or ask `@Browser` to open it. You can leave browser comments on the rendered phone preview, click the preview page for tap intent, or right-click inside the preview page to choose copy, visual, navigation, or inspection intent before recording a note. Codex should read `handoff.md`, `preview-events.jsonl`, or the preview server's `/api/handoff.md` payload before editing or choosing an XcodeBuildMCP action.

When the LaunchDeck surface is installed, run `shipguard ios launchdeck --workflow preview` first if the correct live-render route is unclear. Prefer LaunchDeck simulator browser or SwiftUI preview hot reload for fast live rendering. Use ShipGuard preview when you need typed visual receipts, target-resolution handoff, redaction boundaries, report-quality evidence, or ChatGPT/Codex handoff preparation. Do not claim hot reload proof unless LaunchDeck launcher output and a browser-visible frame show the changed preview.

The bridge is intentionally not a native plugin-owned Codex side panel. Current plugin docs cover skills, apps/connectors, MCP servers, hooks, and assets, while the in-app browser is the documented surface for local visual previews and comments. See `docs/ios-preview.md`.

## ShipGuard Devspace

ShipGuard Devspace exposes the preview bridge to ChatGPT Apps / MCP hosts:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"
./bin/shipguard ios devspace \
  --port 8787 \
  --preview-out /tmp/ios-shipguard-preview \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN
```

Use this when the user wants ChatGPT or GPT-5.5 Pro to plan from a live phone widget and then prepare a Codex handoff. Devspace serves `/mcp`, registers `ui://widget/shipguard-preview-v2.html`, proxies screenshots, records preview events, and prepares a scoped Codex app-server prompt without spawning Codex automatically. Model selection happens in ChatGPT; ShipGuard exposes the MCP/App bridge but cannot force which ChatGPT model is used. Use bearer auth whenever HTTP mode is exposed through a tunnel.

Before sharing a tunneled URL or evaluating the connector itself, run:

```bash
./bin/shipguard ios devspace-check \
  --path . \
  --preview-out /tmp/ios-shipguard-preview \
  --public-url https://your-tunnel.example/mcp \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN \
  --shareable \
  --out /tmp/ios-shipguard-devspace-check
```

`ios devspace-check` is ShipGuard-only product QA. It statically grades loopback defaults, bearer auth, MCP widget metadata, screenshot-token handling, semantic target-resolution, Codex handoff execution boundaries, production-readiness guidance, redaction routing, and model-choice honesty without grading or editing a target app. With `--preview-out`, it also parses `handoff.json`, `handoff.md`, and `preview-events.jsonl` to verify event receipts, raw-coordinate safety, and paste-safe handoff guidance. Add `--shareable` before moving the report outside local proof space so local absolute paths are omitted.

See `docs/shipguard-devspace.md`.

## Swift Modernization Audit

Run a local Swift and SwiftUI modernization audit before asking Codex to change architecture, async state, or visual-system APIs:

```bash
./bin/shipguard ios modernize \
  --focus swift \
  --path . \
  --out /tmp/ios-shipguard-modernize
```

The report flags Swift concurrency hotspots, SwiftUI/Observation migration opportunities, WidgetKit callback surfaces, accessibility/localization review points, and availability fallback requirements for newer APIs such as Liquid Glass-specific styling. Treat the output as planning evidence; it is not proof that a migration is safe until the relevant build, simulator, or UI checks pass.

Use `--shareable` when a modernization report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`.

## App Intelligence Audit

Run an App Intents and system-surface audit before exposing app actions to Shortcuts, Siri, Spotlight, widgets, controls, or Apple Intelligence:

```bash
./bin/shipguard ios app-intelligence \
  --path . \
  --out /tmp/ios-shipguard-app-intelligence
```

The report maps App Intent, AppEntity, App Shortcuts provider, WidgetKit, Spotlight, Siri, controls, and runtime handoff coverage. It also records candidate actions/entities and blocked privacy questions so Codex does not invent broad system exposure without a product decision.

Use `--shareable` when an app-intelligence report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`.

## AI Readiness Audit

Run an AI capability audit before choosing Foundation Models, Core AI, Core ML, OpenAI API, or no AI:

```bash
./bin/shipguard ios ai-readiness \
  --path . \
  --out /tmp/ios-shipguard-ai-readiness
```

The report scans local source and model assets for AI capability signals, then produces an on-device versus cloud matrix. It forces privacy, latency, cost, fallback, and proof questions before Codex implements model behavior or adds cloud data flow.

Use `--shareable` when an AI-readiness report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`.

## iOS Report Redaction

Run report redaction before moving ShipGuard artifacts into ChatGPT prompts, public issues, benchmark notes, or release evidence:

```bash
./bin/shipguard ios redact \
  --in /tmp/ios-shipguard-preview \
  --out /tmp/ios-shipguard-preview-redacted \
  --private-term "InternalAppName"
```

The command redacts local user paths, Apple team IDs, bundle IDs in iOS project contexts, bearer and API tokens, secret assignments, emails, Apple account identifiers, device IDs, and explicit private terms. It writes `ios-redaction.json` with rule counts and remaining-risk checks. It skips binary screenshots in directory mode; keep screenshots local unless the user explicitly approves sharing them.

## ShipGuard Evals

Run deterministic behavior evals before changing plugin routing, prompt text, or proof policy:

```bash
./bin/shipguard ios eval \
  --cases evals/ios_shipguard_cases.jsonl \
  --out /tmp/ios-shipguard-eval
```

The report grades whether ShipGuard selects the expected mode, asks missing product/proof questions, avoids false proof claims, and emits a useful Codex brief with commands and proof boundaries. The optional live OpenAI runner remains available as `python3 evals/run_local.py`; without `OPENAI_API_KEY`, it exits with status `2` as a skip.

## First-Run Demo

Run the static demo from a clean checkout:

```bash
./bin/shipguard ios demo --out /tmp/ios-shipguard-first-run
```

The demo runs doctor, inventory, guided plan, proof routing, Swift modernization, App Intelligence, AI readiness, deterministic ShipGuard evals, and a redaction pass against the public fixture. It writes a bundle README and JSON summary under the output directory. It intentionally avoids Xcode, a booted Simulator, account credentials, and `OPENAI_API_KEY` so release packages can prove the plugin's first-run path in CI.

## Self-Advancing Goal Loop

ShipGuard includes a local goal loop for turning the product roadmap into one concrete Codex goal at a time. The loop is intentionally evidence-gated: it does not mark a goal complete by itself. A user, CI job, or Codex thread must provide the proof receipt, and then the command emits the next goal automatically.

Start the loop:

```bash
./bin/shipguard ios goals init \
  --state .shipguard/goals.json \
  --out NEXT_SHIPGUARD_GOAL.md
```

Bootstrap the loop from already-proven shipped work when the checkout has moved ahead of the catalog:

```bash
./bin/shipguard ios goals init \
  --state .shipguard/goals.json \
  --completed-through shipguard-devspace-mcp \
  --completion-evidence ./release-proof/current-upgrade.md \
  --out NEXT_SHIPGUARD_GOAL.md
```

`--completed-through` records evidence receipts for all catalog goals up to the named goal and emits the next pending `/goal`. Use it only when the proof receipt exists; it is for keeping the loop aligned with the current ShipGuard direction, not for skipping validation.

Print the current goal:

```bash
./bin/shipguard ios goals next \
  --state .shipguard/goals.json \
  --out NEXT_SHIPGUARD_GOAL.md
```

Complete the current goal and automatically write the next one:

```bash
./bin/shipguard ios goals complete \
  --state .shipguard/goals.json \
  --goal shipguard-ios-doctor \
  --evidence path/to/proof.md \
  --out NEXT_SHIPGUARD_GOAL.md
```

The built-in phase order is:

1. app understanding
2. guided planning
3. proof routing
4. modernization intelligence
5. privacy/security/distribution
6. evals and quality gates

The built-in goal catalog lives in `scripts/ios_goal_loop.py`; generated `/goal` files carry the current phase and required proof.

## Codex Plugin

The repo includes a local plugin scaffold:

```text
plugins/ios-shipguard/
```

Install it from this checkout as a repo-local marketplace:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
```

Start a new Codex thread after installing so the skill metadata is loaded.

The Codex plugin loads the ShipGuard skill and metadata; it does not by itself put a `./bin/shipguard` file into every app checkout. Install the CLI once from the ShipGuard source or release package:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
```

Then app repos should use `shipguard` or `$HOME/.local/bin/shipguard`. The iOS skill resolves `SHIPGUARD_CLI` in this order: app-local `./bin/shipguard`, `shipguard` on `PATH`, then `$HOME/.local/bin/shipguard`. If none exists, Codex must say CLI proof is unavailable and fall back to source inspection instead of claiming it ran ShipGuard.

## Modes

ShipGuard routes work into one primary mode:

- `permission-audit`: usage descriptions, entitlements, authorization states, denied UI.
- `simulator-debug`: build, launch, reproduce, screenshot, logs, UI tree, debugger.
- `release-proof`: TestFlight, App Store, device proof, proof packets, release claims.
- `storekit-commerce`: product IDs, purchases, restore, entitlements, sandbox proof.
- `widgets-intents-shared-store`: WidgetKit, App Intents, app groups, stale shared state.
- `preview-bridge`: Codex in-app-browser preview, typed click/right-click/note receipts, and simulator screenshot handoff.
- `preview-devspace`: ChatGPT Apps / MCP connector, phone widget, and Codex handoff preparation.
- `privacy-security`: iOS report redaction, ShipGuard Devspace trust boundaries, screenshot/token handling, and shareability review.
- `design-audit`: app-type-specific UI/UX coherence, design DNA, motion, haptics, preview routing, and ImageGen app-icon handoff.
- `external-source-audit`: read-only source inputs, replacement ledger, no-vendoring boundary, report-quality scoring, and validation commands before external-source adoption claims.
- `ui-polish`: SwiftUI layout, copy, accessibility, Dynamic Type, localization.

The skill lives at `plugins/ios-shipguard/skills/ios-shipguard/SKILL.md`.

## Product Direction

Keep the scope narrow:

- Make Codex ask the right iOS questions before editing.
- Produce local evidence a solo developer can trust.
- Use Codex native simulator, Git, worktree, and comment features instead of cloning them.
- Keep scripts dependency-light so the workflow can run in CI or a local terminal.

Do not expand ShipGuard into a hosted dashboard, generic agent framework, or replacement for XcodeBuildMCP.
