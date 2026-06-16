# Command Matrix

`codex-maintainer` is organized around the core maintainer jobs below.

| Job | Command | Output |
| --- | --- | --- |
| Install workflow kit | `init ios`, `init web`, `init backend`, `init cli` | Starter workflow files |
| Check workflow kit | `validate` | Validation pass/fail |
| Check target repo setup | `doctor ios`, `doctor web`, `doctor backend`, `doctor cli` | Missing file report |
| Configure project policy | `policy init`, `policy show` | Plain policy file |
| Audit one AI run | `autopsy` | Markdown and JSON report |
| Export CI evidence | `sarif` | SARIF 2.1.0 results |
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
| Continue the release loop | `next-goal` | Slash-goal Markdown plan |

The commands are dependency-light Bash so release packages remain portable.
