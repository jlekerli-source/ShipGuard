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
- Keep iOS performance-audit routing, `ios performance` findings, `--shareable` output, and `--shipguard-eval` product-QA boundaries strict about profiler evidence, fallback samples, symbolication, before/after comparison, protected boundaries, ranked source hotspots, private-app read-only use, local-path omission before report-quality scoring or external planning, and physical-device proof gaps.
- Keep iOS source scanners fast and honest about scope: skip generated/proof/cache directories, report those exclusions, and keep private-app scans read-only.
- Keep `ios design` genre-aware and shareable so UI/UX, motion, haptics, preview, Devspace, and app-icon guidance changes with utility, game, health, fitness, commerce, creative, and SaaS app context; app-type inference should prefer app/project source over repeated instruction-document wording, and `--shareable` should omit local roots before report-quality scoring or external planning.
- Keep `--shipguard-eval` and `--shareable` supported across `ios modernize`, `ios app-intelligence`, and `ios ai-readiness` so private-app learning improves ShipGuard report quality and public fixtures without becoming target-app work or relying on accidental path safety.
- Keep `ios report-quality` strict, shareable, and actionable enough to turn private read-only report weaknesses into ShipGuard rules, docs, and public fixtures without grading or editing the scanned app; `--shareable` should omit local input/report paths from the quality artifact itself, require supported source reports to declare shareability, and make the next ShipGuard improvement explicit through actionability questions.
- Keep report-quality shareability checks aligned with Devspace-style connector risks: token-bearing URLs must be blocked before sharing and redaction commands should be explicit.
- Keep `ios devspace-check` useful as a ShipGuard-only connector readiness report for loopback defaults, bearer auth, MCP widget metadata, screenshot token handling, semantic target resolution, Codex handoff boundaries, public URL safety, preview handoff fixture quality, shareable report output, and honest ChatGPT model-boundary language.
- Keep the ShipGuard-native spec workflow useful for turning report-quality questions into constitution/spec/plan/tasks/analyze-style artifacts and CodexPro-style Devspace guardrails without vendoring external code or weakening local proof, redaction, and read-only product-QA boundaries; shareable spec workflows should stay grounded in report input and actionability questions.
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

## Next

- Add more anonymized transcript cases only when they can be fully redacted and verified through the corpus gate.
- Expand Maintainer Arena with more task types and stronger fixture provenance only when the fixture contract needs it.
- Add more specialized profiles only when they have clear maintainer workflows.
- Consider npm or Homebrew distribution after the release tarball path stays stable.
- Enable GitHub Pages in repository settings after the docs shell is reviewed.

## Later

- Publish a small collection of anonymized maintainer workflows from real Ringly work.
- Add stricter markdown linting and shell linting when dependency cost is justified.
- Build a comparison matrix against other agent-workflow formats.
