# ShipGuard Evaluation

Generated: 2026-06-17

This is the current usefulness and refinement evaluation for ShipGuard after the rename and README repositioning work.

## Evidence Run

Current checkout:

```bash
./bin/shipguard version
# 3.38.0

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
./bin/shipguard ios performance --path <ringly-checkout> --out /tmp/shipguard-real-ringly/performance --shipguard-eval
# status: blocked
# findings: 73; rule mix: notification-removal-ui-stall, formatter-created-in-view, image-decoding-in-view-path, swiftui-large-blur, swiftui-repeat-forever-animation, swiftui-periodic-timeline, swiftui-shadow-stack
./bin/shipguard ios design --path <ringly-checkout> --out /tmp/shipguard-real-ringly/design-eval --shipguard-eval
# status: review
# output quality: app-type inference, design DNA, preview routing, motion/haptics, and icon handoff can be judged without turning findings into Ringly work
./bin/shipguard ios modernize --focus swift --path <ringly-checkout> --out /tmp/shipguard-real-ringly/modernize-eval --shipguard-eval
# status: blocked
# findings: 63; rule summary groups: 7
./bin/shipguard ios app-intelligence --path <ringly-checkout> --out /tmp/shipguard-real-ringly/app-intelligence-eval --shipguard-eval
# status: review
# App Intents: 14; App Shortcuts providers: 42
./bin/shipguard ios ai-readiness --path <ringly-checkout> --out /tmp/shipguard-real-ringly/ai-readiness-eval --shipguard-eval
# status: review
# detections: 20

./bin/shipguard ios doctor --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/doctor
./bin/shipguard ios inventory --path <ilmify-checkout> --doctor /tmp/shipguard-real-ilmify/doctor/ios-doctor.json --out /tmp/shipguard-real-ilmify/inventory
./bin/shipguard ios performance --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/performance --shipguard-eval
# status: review
# findings: 23; rule mix: swiftui-repeat-forever-animation, swiftui-large-blur, swiftui-shadow-stack
./bin/shipguard ios design --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/design-eval --shipguard-eval
# status: review
# output quality: app-type inference, design DNA, preview routing, motion/haptics, and icon handoff can be judged without turning findings into Ilmify work
./bin/shipguard ios modernize --focus swift --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/modernize-eval --shipguard-eval
# status: review
# findings: 45; rule summary groups: 4
./bin/shipguard ios app-intelligence --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/app-intelligence-eval --shipguard-eval
# status: review
# App Intents: 0
./bin/shipguard ios ai-readiness --path <ilmify-checkout> --out /tmp/shipguard-real-ilmify/ai-readiness-eval --shipguard-eval
# status: review
# detections: 152
```

These private-app runs are not app remediation plans. They are read-only samples used to evaluate whether ShipGuard reports are specific, prioritized, low-noise, and useful enough to turn into public fixtures or eval cases. The Ringly and Ilmify evidence showed ShipGuard needed the eval boundary on more than performance, plus rule summaries and capped Markdown for noisy modernize, app-intelligence, and AI-readiness reports while keeping complete JSON.

A later read-only Ringly/Ilmify pass showed two additional ShipGuard weaknesses: iOS source scanners could spend too much time traversing generated/proof/cache folders in large app checkouts, and `ios design` app-type inference over-weighted repeated instruction-document wording. The scanners now share a skip-scope helper, reports disclose skipped directories, and design app-type scoring prefers Swift/project signals with capped document contributions.

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
- `shipguard ios report-quality` to score ShipGuard's own read-only reports for boundaries, evidence, proof guidance, scan scope, Markdown usefulness, and shareability before turning observations into public fixtures or eval cases.
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
- Added modernization rule summaries and capped Markdown for modernize, app-intelligence, and AI-readiness reports so private-app findings stay useful for improving ShipGuard without becoming app remediation tasks.
- Improved first-run adoption docs around CLI versus plugin usage.
- Upgraded `shipguard next-goal` so the next improvement loop emits a reviewable `/plan` before the `/goal`, and can now carry bounded scope, completion evidence, and the following `/goal` handoff.
- Moved legacy command-wrapper guidance out of primary README and CLI flow into `docs/compatibility.md`.
- Keep Agents SDK deferred unless ShipGuard becomes a runnable agent service with a concrete eval target.
