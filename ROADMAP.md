# Roadmap

This roadmap keeps the repo useful without pretending it is a finished framework.

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
- Keep value-gauntlet runtime proof moving beyond names: adoption receipts prove a fresh package can be installed from an extracted tarball, paired with a fresh Codex plugin cache, used for a first Brand Deck audit, and routed through report-quality to the next action. Target-onboarding receipts prove a fresh iOS app repo can install starter files, pass starter doctor, validate the toolkit, run iOS doctor/inventory, and get the first scoped permission-audit plan without maintainer context. Multi-profile onboarding receipts now prove iOS, web, backend, and CLI starter profiles each install, pass doctor, and leave `SHIPGUARD_PROFILE.md` next commands. The next expansion should add profile-native first-audit receipts so web, backend, and CLI targets get real report commands beyond init/doctor starter files.
- Keep the ShipGuard Brand Deck naming contract current so new public surfaces get a branded name, plain purpose, proof boundary, docs coverage, skill/eval routing when needed, self-audit coverage, and package proof before release.
- Keep `ios launchdeck` as the native ShipGuard front door for LaunchDeck workflows: it should inspect repo topology, recommend XcodeBuildMCP build/run defaults, simulator browser proof, SwiftUI preview hot reload, debugger/log capture, and profiler routes, while keeping execution ownership in Codex iOS execution tools and proof/report ownership in ShipGuard.
- Keep improving `ios launchdeck --receipt` until every LaunchDeck execution lane has concrete receipt grading: build/run logs, UI snapshots, simulator-browser frames, SwiftUI hot-reload output, profiler traces, fallback samples, and explicit device-only proof gaps.
- Grow public report-quality fixtures for LaunchDeck receipt gaps so private-app proof failures become synthetic, reusable ShipGuard tests instead of one-off notes.
- Keep iOS performance-audit routing, `ios performance` findings, `--shareable` output, and `--shipguard-eval` product-QA boundaries strict about profiler evidence, fallback samples, symbolication, before/after comparison, protected boundaries, ranked source hotspots, impact explanations, high-severity reasons, Codex-local versus manual/device proof boundaries, grouped repeated-rule action plans with smallest first experiments, validation routes, stop conditions, private-app read-only use, local-path omission before report-quality scoring or external planning, and physical-device proof gaps.
- Keep iOS source scanners fast and honest about scope: skip generated/proof/cache directories, report those exclusions, and keep private-app scans read-only.
- Keep `ios design` genre-aware and shareable so UI/UX, motion, haptics, preview, Devspace, and app-icon guidance changes with utility, game, health, fitness, commerce, creative, and SaaS app context; motionQualityGates should keep frequency, purpose, keyboard, Reduce Motion, AI-slop, and performance gates native to ShipGuard reports; app-type inference should prefer app/project source over repeated instruction-document wording, and `--shareable` should omit local roots before report-quality scoring or external planning.
- Keep `--shipguard-eval` and `--shareable` supported across `ios modernize`, `ios app-intelligence`, and `ios ai-readiness` so private-app learning improves ShipGuard report quality and public fixtures without becoming target-app work or relying on accidental path safety.
- Keep `ios report-quality` strict, shareable, and actionable enough to turn private read-only report weaknesses into ShipGuard rules, docs, and public fixtures without grading or editing the scanned app; `--shareable` should omit local input/report paths from the quality artifact itself, require supported source reports to declare shareability, keep source report issues visible through `sourceFindings`, `sourceIssueVisibility`, and Markdown `Source Report Findings` without mixing them into report-quality defects, require performance findings to explain why they matter in JSON and Markdown, require high performance findings to explain why severity is high in JSON and Markdown, require performance proof guidance to separate local Codex proof from manual/device proof in JSON and Markdown, require repeated performance rules to have grouped JSON and Markdown actions with smallest first experiments, validation routes, and stop conditions, emit fixture candidates for public synthetic eval coverage, materialize those candidates into path-safe starter files when requested, emit and consume promotion manifests and review checklists for those materialized fixtures without auto-copying them into the repo, avoid recursive fixture candidates when a materialized synthetic fixture is scored again, and make the next ShipGuard improvement explicit through `priorityAction` plus prioritized actionability questions.
- Keep report-quality shareability checks aligned with Devspace-style connector risks: token-bearing URLs must be blocked before sharing and redaction commands should be explicit.
- Keep `ios devspace-check` useful as a ShipGuard-only connector readiness report for loopback defaults, bearer auth, MCP widget metadata, screenshot token handling, semantic target resolution, Codex handoff boundaries, public URL safety, preview handoff fixture quality, shareable report output, and honest ChatGPT model-boundary language.
- Keep `ios external-audit` as the native adoption gate for Spec Kit, CodexPro, Expo, Design Motion Principles, native iOS workflow skills, X posts, and other external workflow ideas: source inputs should become a capability matrix, replacement ledger, implementation backlog, license boundary, and report-quality questions before ShipGuard claims an idea is integrated, and routing evals should keep external-source adoption from drifting into Devspace or generic planning.
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
