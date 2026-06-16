# Command Matrix

`codex-maintainer` is organized around maintainer evidence. Start with the core loop, then add CI, benchmark, transcript, or release proof commands only when the repository needs them.

## Core First Run

| Job | Command | Output |
| --- | --- | --- |
| Install workflow kit | `init ios`, `init web`, `init backend`, `init cli` | Starter workflow files |
| Check workflow kit | `validate` | Validation pass/fail |
| Check target repo setup | `doctor ios`, `doctor web`, `doctor backend`, `doctor cli` | Missing file report |
| Configure project policy | `policy init`, `policy show` | Plain policy file |
| Discover iOS app topology | `ios doctor` | Xcode/Swift package topology, schemes, versions, privacy, StoreKit, and proof-readiness report |
| Inventory iOS permission/runtime surfaces | `ios inventory` | Target risk map plus ask-before-editing gates for permissions, entitlements, StoreKit, privacy, and modernization surfaces |
| Preview a booted iOS Simulator in Codex | `ios preview` | Local browser preview, simulator screenshot, and typed click/right-click/note event receipts |
| Match iOS preview target | `ios target-match` | Ranked UI snapshot candidates for a preview event |
| Generate an iOS Codex brief | `ios plan` | Mode, blocked questions, owner files, target summary, proof route, and copy-ready brief |
| Route iOS proof | `ios prove` | Checklist with source, simulator, StoreKit, release, privacy, preview, and blocked-manual evidence lanes |
| Expose iOS preview to ChatGPT | `ios devspace` | Bearer-authenticated MCP endpoint, phone widget resource, screenshot proxy, target resolution, target matching, production-readiness reporting, and Codex handoff tools |
| Prepare a Codex app-server handoff | `ios codex-handoff` | Prompt file, app-server request plan, JSONL message template, optional explicit execution transcript |
| Audit Swift modernization | `ios modernize` | Swift concurrency, SwiftUI, Observation, accessibility/localization, and availability fallback findings |
| Audit app intelligence surfaces | `ios app-intelligence` | App Intent, AppEntity, Shortcuts, Siri, Spotlight, widget, controls, Apple Intelligence, and privacy-readiness matrix |
| Audit AI capability choices | `ios ai-readiness` | Foundation Models, Core AI, Core ML, OpenAI API, no-AI decision matrix plus privacy, latency, cost, and fallback questions |
| Redact iOS report artifacts | `ios redact` | Redacted report files plus JSON counts for local paths, team IDs, bundle IDs, tokens, accounts, emails, and device IDs |
| Evaluate Shipguard behavior | `ios eval` | Deterministic mode-routing, missing-question, proof-honesty, and Codex brief quality report |
| Try Shipguard from a clean checkout | `ios demo` | Static first-run bundle with doctor, inventory, plan, proof, modernization, intelligence, AI readiness, eval, and redaction reports |
| Continue Shipguard implementation loop | `ios goals init`, `ios goals next`, `ios goals emit`, `ios goals complete` | Evidence-gated `/goal` file and local progress state |
| Audit one AI run | `autopsy` | Markdown and JSON report |
| Check docs links | `docs-check` | Broken local Markdown link report |

## CI And PR Evidence

| Job | Command | Output |
| --- | --- | --- |
| Enforce in CI | `ci-gate` | Gate bundle and optional failure |
| Summarize CI gate | `ci-summary` | Step-summary Markdown |
| Generate PR comment | `review-comment` | Comment Markdown and badge JSON |
| Export CI evidence | `sarif` | SARIF 2.1.0 results |
| Prepare or post Check Run payload | `check-run`, `check-run post` | GitHub Checks API payload and response JSON |
| Check docs links in CI | `actions/docs-check` | Uploaded docs-check artifact |

## Benchmarks

| Job | Command | Output |
| --- | --- | --- |
| Run fixture packs | `arena run` | Aggregate results and per-case reports |
| Compare fixture runs | `arena compare` | Benchmark delta JSON and Markdown |
| Compare fixture runs in CI | `actions/arena-compare` | Uploaded benchmark comparison artifact |
| Import fixture packs | `arena import` | Validated local fixture pack |
| Sign fixture packs | `arena sign`, `arena verify` | SHA-256 pack metadata with optional signer provenance |
| Publish benchmark data | `leaderboard build` | Stable leaderboard JSON |

## Transcript Safety

| Job | Command | Output |
| --- | --- | --- |
| Redact, verify, or index maintainer transcripts | `transcript redact`, `transcript verify`, `transcript corpus` | Redacted Markdown, leak-audit JSON, verification Markdown, corpus index, and badge JSON |
| Verify transcripts in CI | `actions/transcript-verify` | Uploaded transcript verification artifact |
| Verify transcript corpora in CI | `actions/transcript-corpus` | Uploaded corpus index, badge, and per-case verification artifact |

## Release Proof

| Job | Command | Output |
| --- | --- | --- |
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
| Continue the release loop | `next-goal` | Slash-goal Markdown plan |

The commands are dependency-light Bash so release packages remain portable.
