# ShipGuard Naming

ShipGuard should feel like a real product, not a pile of generic helper scripts. Public CLI commands stay literal because they need to be searchable, scriptable, and boring in CI. The personality lives in branded surface names, report headings, section names, docs, and aliases.

The rule is simple: a fun name is allowed only when its plain job and proof boundary are visible beside it.

## Naming Rules

- Keep CLI verbs literal and searchable; add personality through surface names, section labels, and report copy.
- Pair every branded surface with a plain-purpose sentence and a proof-boundary sentence.
- Use short techy nouns from the ShipGuard universe: Deck, Dock, Radar, Forge, Lens, Port, Vault, Bay, Arena, Engine, Lab, Tower, Beacon, Rail, Rig, Harbor, and Compass.
- Avoid app-specific branding in reusable surfaces. Private app names belong only in read-only product-QA evidence.
- Never let a vibe label weaken proof language. Release, payment, privacy, haptic, performance, and simulator claims stay literal.
- New public surfaces must update `shipguard brand`, docs, skill routing, self-audit, package proof, and focused tests.
- Make the nitty-gritty fun through call signs in human-facing output, not by renaming automation-sensitive files.

## Product Places

| Name | Plain Purpose | Where It Appears | Proof Boundary |
| --- | --- | --- | --- |
| ShipGuard ShipYard | The workshop layer for the whole toolkit: commands, docs, tests, fixtures, plugins, packages, and proof loops. | README, Brand Deck reports, naming docs, release handoffs, and human-facing summaries. | ShipYard names the workspace experience; it is not a repo rename and does not change automation paths. |

## Surface Scheme

| Command | Branded Surface | Plain Purpose |
| --- | --- | --- |
| `shipguard brand` / `shipguard ios brand` | ShipGuard Brand Deck | Keep ShipGuard naming, tone, and future feature labels consistent across the whole toolkit. |
| `shipguard init` | ShipGuard StarterBay | Install starter workflow profiles into iOS, web, backend, or CLI repos. |
| `shipguard validate` | ShipGuard RigCheck | Validate that a ShipGuard checkout or package contains the required workflow bundle. |
| `shipguard doctor` | ShipGuard RepoVitals | Check whether a target repo has the starter workflow files it should have. |
| `shipguard prepare` | ShipGuard Task Contract | Create a durable proof-gated Codex task object before edits. |
| `shipguard verify` | ShipGuard Task Verdict | Verify the exact diff, evidence receipts, and agent claims against a task contract. |
| `shipguard web audit` | ShipGuard WebScan | Run a first web-app audit for framework signals, auth/payment risks, validation lanes, starter workflow health, and next commands. |
| `shipguard web plan` | ShipGuard WebForge | Turn WebScan output into scoped web tasks, validation commands, stop conditions, and report-quality questions. |
| `shipguard backend audit` | ShipGuard ServiceRadar | Run a first backend-service audit for API, auth, migration, queue, webhook, observability, validation, and next-command signals. |
| `shipguard backend plan` | ShipGuard ServiceForge | Turn ServiceRadar output into scoped backend tasks, validation commands, stop conditions, and report-quality questions. |
| `shipguard cli audit` | ShipGuard CommandLens | Run a first CLI-tool audit for command dispatch, argument parsing, stdout/stderr contracts, exit codes, redaction, packaging, and next commands. |
| `shipguard cli plan` | ShipGuard CommandForge | Turn CommandLens output into scoped CLI tasks, smoke commands, contract checks, stop conditions, and report-quality questions. |
| `shipguard policy` | ShipGuard RuleHarbor | Initialize or inspect policy config for scoped agent behavior. |
| `shipguard score` | ShipGuard RunScore | Score a Codex run against scope, ownership, risk, validation, and handoff quality. |
| `shipguard transcript` | ShipGuard TraceVault | Redact, verify, and index maintainer transcripts for public-safe evidence. |
| `shipguard review-comment` | ShipGuard ReviewBeacon | Turn autopsy output into a PR-ready review comment and badge. |
| `shipguard ci-gate` | ShipGuard GateTower | Create CI gate output from run, diff, task, policy, and validation logs. |
| `shipguard ci-summary` | ShipGuard BriefBeacon | Render CI gate JSON into a GitHub Actions step summary. |
| `shipguard check-run` | ShipGuard CheckPilot | Generate or post GitHub Checks API payloads from gate output. |
| `shipguard sarif` | ShipGuard AlertBeacon | Convert autopsy findings into SARIF for code scanning surfaces. |
| `shipguard docs-check` | ShipGuard LinkSweep | Check Markdown docs for broken local links. |
| `shipguard value-gauntlet` | ShipGuard Tool Value Gauntlet | Grade every ShipGuard command, skill, plugin, action, doc, and proof path for real developer usefulness. |
| `shipguard full-audit` | ShipGuard Full Audit | Run or plan the full ShipYard validation, value, package, plugin, CI, and release-proof lane from one resumable report. |
| `shipguard inspect` | ShipGuard InspectDeck | Summarize repo state, proof receipts, plugin state, release state, underlying evidence, and one exact next action. |
| `shipguard v4 preview` | ShipGuard V4 Preview | Stabilize the v4 product contract, schema-freeze posture, migration plan, deprecation policy, and release-readiness proof without claiming v4 stable. |
| `shipguard v4 schema-freeze` | ShipGuard V4 Schema Freeze | Freeze the v4 schema contract with compatibility fixtures, migration checks, changelog policy, and deprecation rules without claiming v4 product release. |
| `shipguard v4 release-candidate` | ShipGuard V4 Release Candidate Readiness / LaunchKey | Prove install, optional package-tarball fresh-install proof, upgrade, uninstall, release-consume, optional downloaded release-asset proof, adoption packet, final schema docs, and plugin refresh readiness without claiming stable v4 release. |
| `shipguard pilot-bench` | ShipGuard PilotBench | Score public-safe read-only task traces and optional benchmark-v2 verdict lift against baseline agent output. |
| `shipguard agent trace` / `shipguard codex trace` | ShipGuard TraceBridge | Connect prompts, tool calls, receipts, task verdicts, next actions, and worker budgets into one adapter timeline. |
| `shipguard ios doctor` | ShipGuard DockCheck | Inspect Xcode, SwiftPM, schemes, targets, and proof readiness. |
| `shipguard ios inventory` | ShipGuard CargoScan | Map permissions, entitlements, StoreKit, widgets, intents, and runtime risk. |
| `shipguard ios plan` | ShipGuard BriefForge | Turn inventory into a scoped Codex brief with blockers and proof route. |
| `shipguard ios prove` | ShipGuard ProofVault | Separate local proof, simulator proof, manual proof, and blocked claims. |
| `shipguard ios launchdeck` | ShipGuard LaunchDeck | Route build/run, debugger, live preview, hot reload, and profiler work. |
| `shipguard ios performance` | ShipGuard PulseRadar | Find SwiftUI, rendering, main-thread, and profiler-proof performance risks. |
| `shipguard ios design` | ShipGuard VibeCheck | Audit UI/UX coherence, motion, haptics, preview routing, and icon direction. |
| `shipguard ios modernize` | ShipGuard UpgradeForge | Plan Swift, SwiftUI, Observation, availability, and platform modernization. |
| `shipguard ios app-intelligence` | ShipGuard SignalLens | Audit App Intents, shortcuts, widgets, Spotlight, Siri, and system exposure. |
| `shipguard ios ai-readiness` | ShipGuard ModelDock | Compare on-device, cloud, Core ML, no-AI, privacy, latency, and cost choices. |
| `shipguard ios external-audit` | ShipGuard SourceScout | Audit external repos, posts, and skills before native ShipGuard adoption. |
| `shipguard ios spec-workflow` | ShipGuard SpecForge | Generate ShipGuard-owned constitution, spec, plan, tasks, and analysis gates. |
| `shipguard ios report-quality` | ShipGuard QualityRadar | Grade ShipGuard reports for usefulness, boundaries, shareability, and fixtures. |
| `shipguard ios preview` | ShipGuard MirrorPort | Serve the phone-shaped preview and typed visual-event receipts. |
| `shipguard ios devspace` | ShipGuard Devspace Bridge | Expose preview evidence to ChatGPT/MCP planning and guarded Codex handoff. |
| `shipguard ios devspace-check` | ShipGuard BridgeWatch | Grade Devspace connector readiness, public URL safety, and widget handoff quality. |
| `shipguard ios target-match` | ShipGuard TapCompass | Match preview events to UI snapshot elements before a visual handoff becomes action. |
| `shipguard ios codex-handoff` | ShipGuard HandoffRail | Package a guarded Codex app-server handoff from a prompt or preview planning bundle. |
| `shipguard ios redact` | ShipGuard RedactionBay | Redact paths, tokens, IDs, accounts, and private terms before sharing. |
| `shipguard ios eval` | ShipGuard EvalArena | Run deterministic behavior evals for routing, proof honesty, and plugin guidance. |
| `shipguard ios demo` | ShipGuard DemoDock | Run a clean first-run iOS ShipGuard demo without Xcode, credentials, or private code. |
| `shipguard ios goals` | ShipGuard GoalEngine | Keep slash-goal loops evidence-gated and restartable. |
| `shipguard release-proof` | ShipGuard ReleaseDock | Package, replay, consume, diff, attest, and publish release evidence. |
| `shipguard release-manifest` | ShipGuard ManifestForge | Build or verify release manifests and proof ledgers for packaged artifacts. |
| `shipguard release-index` | ShipGuard ReleaseAtlas | Build a catalog from release manifests. |
| `shipguard release-replay` | ShipGuard ReplayRig | Replay release verification against downloaded assets, manifests, and ledgers. |
| `shipguard release-attest` | ShipGuard TrustStamp | Build release attestation JSON, Markdown, and badge evidence. |
| `shipguard release-consume` | ShipGuard ConsumerDock | Verify downloaded release assets from a consumer's perspective. |
| `shipguard release-diff` | ShipGuard DiffLens | Compare two release proof asset directories and report what changed. |
| `shipguard release-evidence` | ShipGuard EvidenceHarbor | Export or verify release evidence sites, indexes, and local evidence bundles. |
| `shipguard autopsy` | ShipGuard AutopsyLab | Score AI coding runs, diffs, tasks, validation logs, and PR-ready gates. |
| `shipguard arena` | ShipGuard ArenaBench | Run, compare, import, sign, and verify public benchmark fixture packs. |
| `shipguard codex status` | ShipGuard PluginRadar | Check local Codex plugin install state, stale metadata, and CLI resolution. |
| `shipguard codex marketplace-readiness` | ShipGuard MarketplaceDeck | Prove tracked Codex plugin metadata, local marketplace source, public assets, status proof, and submission-packet readiness. |
| `shipguard leaderboard` | ShipGuard ScoreTower | Build stable leaderboard JSON from arena benchmark results. |
| `shipguard self-audit` | ShipGuard SelfScan | Generate toolkit readiness proof for the ShipGuard checkout. |
| `shipguard next-goal` | ShipGuard NextRail | Generate the next slash-plan and slash-goal handoff for the improvement loop. |
| `shipguard version` | ShipGuard VersionBeacon | Print the toolkit version from `VERSION`. |

## Nitty-Gritty Call Signs

Use these labels when reports, logs, docs, or CI summaries refer to file families. The physical file paths stay literal so scripts, CI, packages, and docs links remain stable.

| Path Pattern | Call Sign | Example Label | Plain Purpose |
| --- | --- | --- | --- |
| `scripts/*.sh` | Deckhand Scripts | `[deckhand]` | Small shell operators that move validation, packaging, and proof work forward. |
| `scripts/ios_*.py` | Sonar Modules | `[sonar]` | Python scanners that read source, classify risk, and emit structured iOS reports. |
| `tests/*_test.sh` | Gauntlet Runs | `[gauntlet]` | Repeatable tests that prove a ShipGuard behavior did not drift. |
| `actions/*/action.yml` | Signal Flares | `[flare]` | GitHub Action entrypoints that publish ShipGuard proof into CI. |
| `fixtures/**` | Proof Playground | `[playground]` | Synthetic public cases that make report quality and routing behavior testable. |
| `*.json` | Blackbox Receipts | `[blackbox]` | Machine-readable evidence, status, findings, and release metadata. |
| `*.md` | Bridge Notes | `[bridge]` | Human-readable handoffs, reports, docs, and release summaries. |
| `*.log` | Engine Tapes | `[engine]` | Raw command output, build traces, profiler notes, and failure trails. |
| `dist/*.tar.gz` | Cargo Crates | `[cargo]` | Release packages that users can unpack and verify outside the source checkout. |
| `plugins/**` | Docking Gear | `[dock]` | Codex plugin metadata, skills, and MCP launch configuration. |

## Future Naming Contract

Before shipping a new command or major report surface:

1. Add the literal CLI command to `bin/shipguard`.
2. Add a branded surface row to `scripts/ios_branding.py`.
3. Mention the surface here and in `docs/command-matrix.md`.
4. Add skill or eval routing when a user would ask for the surface by name.
5. Add or reuse an artifact call sign for any new script, log, fixture, package, or plugin family.
6. Add self-audit, package, and focused tests.
7. Run `./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict`.

Do not rename stable public commands only for flavor. ShipGuard can be vibey in reports and docs while keeping automation-safe CLI names.
