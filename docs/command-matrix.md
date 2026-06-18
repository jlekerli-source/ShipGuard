# Command Matrix

`shipguard` is organized around the core maintainer jobs below. The whole toolkit workspace is the ShipGuard ShipYard; individual command families keep literal CLI names plus branded surface names and proof boundaries.

| Job | Command | Output |
| --- | --- | --- |
| Install workflow kit | `init ios`, `init web`, `init backend`, `init cli` | Starter workflow files |
| Check workflow kit | `validate` | Validation pass/fail |
| Check target repo setup | `doctor ios`, `doctor web`, `doctor backend`, `doctor cli` | Missing file report |
| Install local Codex plugin source | `codex plugin marketplace add .`, `codex plugin add ios-shipguard@shipguard` | Local plugin cache entry; new Codex thread required to load refreshed skill text |
| Check local Codex plugin install | `codex status` | Installed plugin metadata, stale branding, and missing-source report |
| Keep ShipGuard naming coherent | `brand`, `ios brand` | ShipGuard Brand Deck: toolkit-wide branded surface scheme, nitty-gritty file-family call signs, public-command coverage, active-doc coverage, stale wording checks, and future naming contract |
| Audit actual ShipGuard developer value | `value-gauntlet` | ShipGuard Tool Value Gauntlet: read-only scoring of commands, skills, plugin metadata, GitHub Actions, docs, tests, package proof, proof boundaries, lowest-value surface probing, and runtime-output probe escalation so cool names cannot hide weak tooling |
| Inspect iOS app topology | `ios doctor` | Xcode, SwiftPM, scheme, target, StoreKit, privacy manifest, and proof-readiness report |
| Inventory risky iOS surfaces | `ios inventory` | Permission, entitlement, target risk, modernization, and ask-before-editing report |
| Generate Codex iOS brief | `ios plan` | Mode, owner files, blocked questions, proof route, and task brief |
| Route iOS proof claims | `ios prove` | Source, simulator, performance, StoreKit, privacy, release, and blocked-manual evidence lane |
| Route iOS build/debug/preview/profiler work | `ios launchdeck` | ShipGuard-native LaunchDeck for XcodeBuildMCP build/run, simulator browser, SwiftUI preview hot reload, debugger/log capture, performance profiler routes, `--receipt` execution-proof grading, proof boundaries, and report-quality questions |
| Audit iOS performance hotspots | `ios performance` | ShipGuard PulseRadar: ranked SwiftUI, body-work, GPU composition, image decoding, notification-cleanup findings with impact explanations, high-severity reasons, local/manual proof boundaries, grouped next actions with first experiments, validation routes, stop conditions, optional ShipGuard-only eval boundary, and shareable path-safe output |
| Audit iOS design quality | `ios design` | ShipGuard VibeCheck: app-type inference, design DNA, ShipGuard-native motion quality gates, haptics, preview routing, and ImageGen icon handoff |
| Run iOS preview bridge | `ios preview`, `ios target-match` | Local phone preview, visual event receipts, semantic target matching, and proof handoff around LaunchDeck live preview/hot reload loops |
| Run ShipGuard Devspace | `ios devspace`, `ios devspace-check`, `ios codex-handoff` | MCP/App bridge, connector-readiness report, preview widget, and guarded Codex handoff bundle |
| Audit iOS modernization and system exposure | `ios modernize`, `ios app-intelligence`, `ios ai-readiness` | ShipGuard UpgradeForge, ShipGuard SignalLens, and ShipGuard ModelDock reports with optional ShipGuard-only eval boundaries and shareable path-safe output |
| Audit external workflow sources | `ios external-audit` | ShipGuard SourceScout: source inputs, capability matrix, replacement ledger, implementation backlog, license boundary, and report-quality questions for Spec Kit, CodexPro, Expo, Design Motion Principles, native iOS workflow, and other sources |
| Generate iOS spec workflow | `ios spec-workflow` | ShipGuard SpecForge: constitution, feature spec, requirements checklist, native integration decisions, implementation plan, tasks, consistency analysis, analysis gates, slash plan/goal, Devspace guardrails, and report-quality artifact/question/acceptance/task/validation/analysis checks |
| Redact or evaluate iOS reports | `ios redact`, `ios report-quality`, `ios eval`, `ios demo` | Redacted local reports, shareable report-usefulness scoring with performance explanation, severity, proof-boundary, grouping, first-experiment, validation-route, and stop-condition checks, priority actions, actionability questions, fixture candidates, generated and consumed promotion manifests for materialized synthetic fixtures, materialized-fixture recursion guards, deterministic behavior evals, and clean first-run demo |
| Continue iOS ShipGuard goals | `ios goals` | Evidence-gated slash-goal state and next-goal output |
| Configure project policy | `policy init`, `policy show` | Plain policy file |
| Audit one AI run | `autopsy` | Markdown and JSON report |
| Export CI evidence | `sarif` | SARIF 2.1.0 results |
| Check docs links | `docs-check` | Broken local Markdown link report |
| Run fixture packs | `arena run` | Aggregate results and per-case reports |
| Compare fixture runs | `arena compare` | Benchmark delta JSON and Markdown |
| Compare fixture runs in CI | `actions/arena-compare` | Uploaded benchmark comparison artifact |
| Import fixture packs | `arena import` | Validated local fixture pack |
| Sign fixture packs | `arena sign`, `arena verify` | SHA-256 pack metadata with optional signer provenance |
| Redact, verify, or index maintainer transcripts | `transcript redact`, `transcript verify`, `transcript corpus` | Redacted Markdown, leak-audit JSON, verification Markdown, corpus index, and badge JSON |
| Verify transcripts in CI | `actions/transcript-verify` | Uploaded transcript verification artifact |
| Verify transcript corpora in CI | `actions/transcript-corpus` | Uploaded corpus index, badge, and per-case verification artifact |
| Generate PR comment | `review-comment` | Comment Markdown and badge JSON |
| Enforce in CI | `ci-gate` | Gate bundle and optional failure |
| Summarize CI gate | `ci-summary` | Step-summary Markdown |
| Prepare or post Check Run payload | `check-run`, `check-run post` | GitHub Checks API payload and response JSON |
| Publish benchmark data | `leaderboard build` | Stable leaderboard JSON |
| Record release proof | `release-manifest`, `release-manifest verify`, `release-index build`, `release-replay verify`, `release-attest build`, `release-proof build` | Release manifest JSON, proof ledger Markdown, artifact verification, proof catalog, replay report, attestation badge, and full proof bundle |
| Build release proof artifact | `actions/release-proof` | Uploaded tarball, manifest, replay, and attestation bundle |
| Adopt release proof workflows | `examples/workflows/release-proof-on-tag.yml`, `examples/workflows/release-proof-manual.yml` | Copyable GitHub Actions workflow examples |
| Consume release proof | `release-consume verify` | SHA-256 check, local replay, attestation rebuild, and consumer report from downloaded release assets |
| Consume release proof in CI | `actions/release-consume` | Uploaded consumer proof artifact |
| Compare releases | `release-diff compare`, `actions/release-diff` | Release diff JSON and Markdown |
| Export release evidence | `release-evidence site`, `release-evidence index`, `release-evidence bundle`, `actions/release-evidence` | Static evidence site, optional history index, and one-command local evidence bundle |
| Consume release evidence | `release-evidence verify`, `actions/release-evidence-verify` | Evidence artifact verification report, Markdown summary, and badge JSON |
| Audit release evidence failures | `release-evidence negative-index`, `actions/release-evidence-negative-index` | Index of intentionally broken evidence fixtures and expected blocked checks |
| Audit this toolkit | `self-audit` | Self-audit Markdown and JSON |
| Continue the release loop | `next-goal` | Slash-plan and slash-goal Markdown plan |

The commands are dependency-light Bash so release packages remain portable.
