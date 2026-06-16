# OSS Evaluation

This evaluation checks whether `ringly-codex-workflows` is useful as open source, where it is inefficient today, and what would make it materially better.

## Verdict

Keep the project, but narrow the public promise.

The repo is useful when positioned as a maintainer reliability toolkit for AI-assisted coding: scoped agent instructions, run autopsy, CI evidence, release proof, transcript safety, and fixture-based benchmarks. It is less compelling as a generic "Codex workflow starter" because the first-run surface is large and still carries Ringly-specific assumptions.

If the project stays public, the next phase should optimize for adoption efficiency rather than more release-proof features.

## Product Pivot

The strongest public product is now `iOS Shipguard`: a Codex plugin, skill, and CLI mode for solo iOS developers. Codex already provides app modes, worktrees, inline diff comments, Git operations, terminal integration, computer use, and iOS simulator debugging through XcodeBuildMCP. This repo should not clone those capabilities.

Shipguard should add the missing layer:

- inventory iOS permission and runtime surfaces before edits
- force ask-before-editing gates for missing usage descriptions, entitlements, StoreKit, notification, alarm, widget, intent, and release-proof risk
- route work into one primary mode so Codex uses the right native capability
- produce local Markdown/JSON evidence a solo developer can inspect or attach to CI

That is narrower than "Codex workflows" and more useful than a generic maintainer toolkit.

## Evidence Snapshot

Measured from the current working tree on 2026-06-16:

| Check | Result |
| --- | --- |
| `./bin/codex-maintainer validate` | pass |
| `./bin/codex-maintainer self-audit --out /tmp/ringly-codex-workflows-self-audit` | pass, 36/36 commands checked, 111/111 artifacts checked |
| `./bin/codex-maintainer docs-check . --out /tmp/ios-shipguard-docs-check` | pass, 290 Markdown files checked, 48 local links checked, 0 broken |
| `./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/ringly-codex-workflows-arena` | pass, 10 cases, average 7.00/12, 4.4s wall time |
| Repository surface | 36 CLI help paths, 33 shell scripts, 3 Python scripts, 49 shell tests, 13 composite actions, 50 top-level docs pages |
| Distribution surface | 60 release tarballs in `dist/`, about 13 MB |

## Usefulness Score

Overall: 7/10.

| Dimension | Score | Reason |
| --- | ---: | --- |
| Solves a real problem | 8 | The repo targets a concrete failure mode: AI agents claiming work without scoped proof. |
| Evidence quality | 8 | Autopsy, arena, self-audit, docs-check, release replay, and transcript verification are real proof paths. |
| First-run clarity | 5 | README and docs expose many advanced commands before the core loop is obvious. |
| Maintenance efficiency | 4 | Version and action reference changes touch many docs, examples, tests, and generated reports. |
| Security posture | 6 | Secrets are out of scope and transcript redaction exists, but action inputs that delete/download paths need stricter guardrails. |
| OpenAI/Codex fit | 7 | The repo fits Codex-style maintainer workflows without requiring API keys, but it does not yet include a live model eval harness. |

## What Is Working

The strongest part of the repo is the closed evidence loop:

1. `score` and `autopsy` convert an AI run into a reviewable report.
2. `arena run` turns multiple fixtures into aggregate benchmark evidence.
3. `ci-gate`, `review-comment`, `sarif`, and GitHub Actions make the evidence consumable in pull requests.
4. `release-*` commands prove that published artifacts can be replayed and consumed.
5. `transcript-*` commands address the real OSS risk of publishing private maintainer context.

The dependency-light Bash implementation is also a strength. The arena run completed in roughly 4.4 seconds, and the docs check completed in under a second on this checkout.

## What Is Inefficient

### 1. Release version churn is too expensive

The current working tree shows a release/reference update touching 85 files. Many docs, tests, examples, workflows, and generated reports repeat `v3.39.0` or `3.39.0` directly.

This makes releases expensive, noisy, and easy to get wrong. It also makes code review harder because the actual product change gets buried under mechanical version churn.

Recommended fix:

- Introduce a generated examples/docs refresh command that reads `VERSION`.
- Keep human-authored docs on placeholders like `vX.Y.Z` unless an exact published release is required.
- Move checked demo report refresh into one command with a clear artifact list.
- Add a validation check that finds stale current-version references instead of hard-coding them in many tests.

### 2. The onboarding surface is too large

The README is accurate but overloaded. New users see init, autopsy, arena, transcripts, CI, check runs, release proof, release consume, release diff, release evidence, negative fixtures, and static evidence sites before the core workflow is internalized.

Recommended fix:

- Make the public first path three commands:
  - `codex-maintainer init <profile>`
  - `codex-maintainer autopsy ...`
  - `codex-maintainer ci-gate ...`
- Move release proof and transcript publishing into "advanced" docs.
- Add one "Should I use this?" decision table near the top of the README.

### 3. Root `AGENTS.md` is useful as a template but confusing as repo instructions

The root `AGENTS.md` points to app-specific paths that do not exist in this OSS repo, including `docs/change-review-matrix.md`, `docs/validation-commands.md`, `Ringly.xcodeproj`, `Website/`, and alarm-runtime freeze scripts.

That is acceptable if the file is only a copied starter template. It is inefficient for contributors and agents working inside this repository because it routes them to missing files.

Recommended fix:

- Move the Ringly iOS starter to `templates/ios/AGENTS.md` as the canonical app template.
- Replace root `AGENTS.md` with contributor instructions for this repository:
  - validate with `./bin/codex-maintainer validate`
  - run touched shell tests
  - avoid editing generated release artifacts unless refreshing a release/demo report
  - treat `dist/` and demo reports as generated or release evidence

### 4. Release proof now dominates the product

Release proof is valuable, but it has grown into many commands and actions:

- `release-manifest`
- `release-index`
- `release-replay`
- `release-attest`
- `release-proof`
- `release-consume`
- `release-diff`
- `release-evidence`
- `release-evidence verify`
- `release-evidence negative-index`

For a maintainer reliability OSS, this is powerful but risks crowding out the simpler question: "Did the agent do useful, scoped, proven work?"

Recommended fix:

- Keep the release chain, but present it as an optional module.
- Make `autopsy`, `arena`, and `ci-gate` the core public product.
- Consider grouping release subcommands behind one docs page and one GitHub Action guide.

### 5. Some action inputs need stricter path safety

Several composite actions remove or replace input-controlled directories before downloading or generating artifacts. This is normal in CI, but public reusable actions should reject dangerous paths such as `/`, `.`, empty strings, the repository root, or a parent of the workspace.

Recommended fix:

- Add a shared shell helper for "safe artifact directory" checks.
- Use it before every `rm -rf "$input_dir"` in actions and scripts.
- Add tests for `/`, `.`, `..`, `$GITHUB_WORKSPACE`, and nested safe artifact paths.

## Does It Still Make Sense?

Yes, if the maintained product is:

- AI run auditability.
- Evidence-backed PR and CI workflows.
- Fixture-based maintainer benchmarks.
- Safe publication of transcripts and release proof.

No, if the intended product is:

- A small generic `AGENTS.md` starter.
- A general OpenAI agent framework.
- A polished SaaS-style developer tool.
- A benchmark that claims model quality without live model runs.

The current repo makes the most sense as a local-first maintainer evidence toolkit. That is a narrower and stronger category than "Codex workflows".

## OpenAI Eval Gap

The built-in arena is deterministic and fast, but it evaluates saved run artifacts rather than a live OpenAI model or agent path. That is good for repeatable regression checks, but it cannot answer whether a current model will perform better on the tasks.

Recommended next eval layer:

1. Keep `arena run` as the stable fixture scorer.
2. Add an optional `evals/` harness that can run live model attempts only when `OPENAI_API_KEY` is present.
3. Grade live model outputs with the existing `SCORECARD.md` categories plus tool-use evidence.
4. Store only redacted prompts, outputs, scores, and trace IDs; never store keys or private product data.

This keeps the OSS useful without making OpenAI API access mandatory for adopters.

## Massive Improvement Plan

Status as of the first implementation pass:

- Root `AGENTS.md` now describes this OSS repository instead of private Ringly app paths.
- `docs/core-loop.md` gives the short task-contract -> autopsy -> CI gate -> arena path.
- Reusable release/evidence actions and key local cleanup paths use a shared safe artifact-directory guard.
- Optional live OpenAI eval scaffolding lives under `evals/` and is skipped unless `OPENAI_API_KEY` is present.
- Release packaging now writes tarballs atomically before moving them into `dist/`.

### Phase 1: Reduce adoption friction

- Replace root repo instructions with OSS contributor instructions.
- Add a one-page "core loop" guide: task contract -> autopsy -> CI gate -> arena.
- Shorten README quick start to the first successful maintainer audit.
- Move release proof and transcript publishing to advanced docs.

### Phase 2: Cut release maintenance cost

- Generate versioned examples from `VERSION`.
- Add a `scripts/refresh_docs_examples.sh` or `codex-maintainer docs refresh` command.
- Stop manually updating repeated version strings in tests where a `VERSION` read is enough.
- Keep generated demo reports clearly separated from authored docs.

### Phase 3: Harden reusable actions

- Add safe path guards around destructive artifact-directory cleanup.
- Add tests for action input validation.
- Document token scopes for Check Run posting and release downloads in one security page.

### Phase 4: Improve the usefulness eval

- Add an adoption fixture: install into a blank web/backend/CLI repo, run `doctor`, run one autopsy, and prove the user reaches a useful report in under 10 minutes.
- Add benchmark quality gates:
  - average arena score must not regress
  - validation evidence ratio must not regress
  - high-risk findings must remain detectable
- Add optional live OpenAI evals behind an environment gate.

## Keep/Kill Criteria

Keep investing if the project can prove all of these:

- A new maintainer can run a useful autopsy in under 10 minutes.
- The fixture arena stays deterministic and runs in under 10 seconds locally.
- Release bumps no longer require reviewing dozens of mostly mechanical files.
- Reusable actions reject dangerous artifact paths.
- The public benchmark explains what it measures and what it does not measure.

Stop or drastically narrow the project if these remain true after the next major pass:

- README and docs still require understanding release proof before using autopsy.
- Version bumps keep producing broad manual docs/test churn.
- The benchmark is treated as model-quality evidence without live model runs.
- Root instructions continue to point contributors at missing Ringly app files.
