# iOS ShipGuard

`iOS ShipGuard` is the product-facing layer for this repository: a Codex plugin, skill, and CLI mode for solo iOS developers working on apps where permissions, notifications, StoreKit, widgets, App Intents, background work, and release proof matter.

The existing `shipguard` CLI remains the engine. ShipGuard is the iOS-focused workflow that makes the engine easier to use.

## What Codex Already Does

Do not duplicate Codex platform features. Use them directly:

- Codex app skills, modes, worktrees, terminal, and built-in Git tools: [Codex app features](https://developers.openai.com/codex/app/features).
- Inline diff comments for asking Codex to change specific code: [Codex app features](https://developers.openai.com/codex/app/features).
- Simulator debugging through XcodeBuildMCP and the Build iOS Apps plugin: [Debug in iOS simulator](https://developers.openai.com/codex/use-cases/ios-simulator-bug-debugging).
- Browser comments on local previews through the Codex in-app browser: [In-app browser](https://developers.openai.com/codex/app/browser).
- GUI-only verification through computer use when structured tools are not enough: [Computer Use](https://developers.openai.com/codex/app/computer-use).

ShipGuard adds the missing layer before those tools run: risk routing, permission inventory, ask-before-editing gates, and evidence prompts.

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

The `ios performance` report is read-only. It scans Swift source for ranked hotspots such as high-frequency `TimelineView`, continuous `repeatForever` animation, large blur/shadow composition, formatter allocation in SwiftUI paths, image decoding in UI paths, and notification cleanup that may block launch or interaction. iOS source scanners skip generated/proof/cache directories and list those scan-scope exclusions in JSON and Markdown so large app workspaces do not turn release artifacts or scratch files into product findings.

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
  --reports /tmp/ios-shipguard-performance-eval \
  --reports /tmp/ios-shipguard-design-eval \
  --reports /tmp/ios-shipguard-modernize-eval \
  --reports /tmp/ios-shipguard-app-intelligence-eval \
  --reports /tmp/ios-shipguard-ai-readiness-eval \
  --out /tmp/ios-shipguard-report-quality \
  --shareable
```

Those reports add a ShipGuard evaluation boundary. Findings from those runs must be used to improve ShipGuard rules, report shape, docs, or public fixtures; they must not become target-app remediation tasks without a separate explicit app-work request. Markdown output may be grouped or capped to stay reviewable; JSON keeps the full finding list for deeper ShipGuard product QA. Use `--shareable` on every report that will move into report-quality scoring or external planning so the shareability contract is explicit.

`ios report-quality` then grades ShipGuard's output quality, not the scanned app. It checks whether the reports are parseable, scoped to read-only product QA, paired with Markdown, honest about skipped scan scope, useful in finding evidence/recommendation/proof guidance, explicitly declared shareable when scored in `--shareable` mode, and safe to share or redact. It also aggregates each input report's `reportQualityQuestions` into an actionability checklist and emits `priorityAction` plus `prioritizedActionabilityQuestions`, preferring report-quality findings first and otherwise questions from lower-status source reports, so the next ShipGuard rule, fixture, report section, or docs improvement is explicit. Token-like connector URLs or auth strings are detected without echoing token values, then a redaction plan with `shipguard ios redact` commands is emitted for any report set that should not be shared raw. Add `--shareable` when the report-quality artifact itself will move into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence; default local output keeps absolute input/report paths for operator debugging.

In `--shareable` report-quality mode, supported source reports that are missing `shareability` metadata receive `declared-shareability-missing`, and reports that declare `mode=local` or `localAbsolutePathsIncluded=true` receive `declared-shareability-local-mode`. Regenerate those source reports with `--shareable`; redaction remains the right path only for actual token or local-path findings.

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

The command is read-only against `--path` and writes only to `--out`. It creates `ios-spec-workflow.json`, `ios-spec-workflow.md`, `shipguard-constitution.md`, `feature-spec.md`, `implementation-plan.md`, `tasks.md`, and `devspace-guardrails.md`. The workflow adapts the useful parts of Spec Kit-style constitution/spec/plan/tasks/analyze sequencing and CodexPro-style MCP bridge guardrails into ShipGuard-owned artifacts; it does not install, vendor, or depend on either project.

Add `--from-report` for `ios report-quality` output or any source-scanner report so actionability questions become clarifying questions instead of app-remediation tasks. Repeated report-quality questions are deduplicated before spec-workflow applies its clarifying-question and task caps, so the first unique questions survive into JSON and Markdown. Add `--shipguard-eval` when the scanned repo is Ringly, Ilmify, or another private app used only as ShipGuard product QA. Add `--shareable` before moving the generated spec workflow into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or another `ios report-quality` pass.

`ios report-quality --shareable` checks spec-workflow adoption quality. A spec workflow with no `--from-report` evidence or no actionability questions receives `spec-workflow-report-context-missing` or `spec-workflow-actionability-missing`, because otherwise the generated plan can look polished without being grounded in an observed ShipGuard report weakness. It also verifies that declared spec-workflow artifact files exist and are non-empty beside `ios-spec-workflow.json`; missing bundle files receive `spec-workflow-artifact-file-missing` without exposing local absolute paths. Placeholder-only or structurally weak artifact text receives `spec-workflow-artifact-content-incomplete` or `spec-workflow-artifact-placeholder-content`. If actionability questions are present but not preserved in JSON or Markdown clarifying questions, report-quality emits `spec-workflow-question-coverage-missing` or `spec-workflow-question-artifact-missing`. If the acceptance criteria drop those questions, it emits `spec-workflow-acceptance-coverage-missing` or `spec-workflow-acceptance-artifact-missing`. If those questions do not become proof-gated tasks in `taskPlan` and `tasks.md`, it emits `spec-workflow-task-coverage-missing` or `spec-workflow-task-artifact-missing`. If validation commands are missing from `technicalPlan.recommendedValidation` or `implementation-plan.md`, it emits `spec-workflow-validation-coverage-missing` or `spec-workflow-validation-artifact-missing`. If the analysis gates are replaced by generic placeholders, it emits `spec-workflow-analysis-coverage-missing` or `spec-workflow-analysis-artifact-missing`. If `slashPlan`, `slashGoal`, or `ios-spec-workflow.md` drops the copy-ready `/plan` and `/goal` next-loop handoff, it emits `spec-workflow-slash-handoff-incomplete` or `spec-workflow-slash-handoff-artifact-missing`.

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

The report infers app type, records design DNA signals, applies motion guidance from the Design Motion Principles frequency gate, emits an iOS haptics blueprint, and tells Codex when `ios preview` or `ios devspace` should be used. App-type inference weights app/project source above repeated docs or agent-instruction wording; use `--app-type` when the automatic genre inference is wrong or the user has already named the product category.

Use `--shareable` when a design report will move into ChatGPT, GitHub, docs, benchmark fixtures, release evidence, or `ios report-quality`; default local reports keep absolute roots for operator debugging.

Use `--icon-brief` for app-icon work. ShipGuard writes `app-icon-imagegen-brief.md` for ChatGPT ImageGen and an App Store asset checklist; it does not generate CSS, SVG, or local placeholder icon art.

## Preview Bridge

ShipGuard can serve a local phone-shaped preview page for Codex's in-app browser:

```bash
./bin/shipguard ios preview --out /tmp/ios-shipguard-preview
```

The command binds to `127.0.0.1`, captures the booted Simulator with `xcrun simctl io booted screenshot --type=png <tempfile>`, and writes `session.json`, `preview-url.txt`, `preview-events.jsonl`, `handoff.json`, `handoff.md`, and `last-screenshot.png`.

Open the printed URL in Codex's in-app browser or ask `@Browser` to open it. You can leave browser comments on the rendered phone preview, click the preview page for tap intent, or right-click inside the preview page to choose copy, visual, navigation, or inspection intent before recording a note. Codex should read `handoff.md`, `preview-events.jsonl`, or the preview server's `/api/handoff.md` payload before editing or choosing an XcodeBuildMCP action.

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
- `ui-polish`: SwiftUI layout, copy, accessibility, Dynamic Type, localization.

The skill lives at `plugins/ios-shipguard/skills/ios-shipguard/SKILL.md`.

## Product Direction

Keep the scope narrow:

- Make Codex ask the right iOS questions before editing.
- Produce local evidence a solo developer can trust.
- Use Codex native simulator, Git, worktree, and comment features instead of cloning them.
- Keep scripts dependency-light so the workflow can run in CI or a local terminal.

Do not expand ShipGuard into a hosted dashboard, generic agent framework, or replacement for XcodeBuildMCP.
