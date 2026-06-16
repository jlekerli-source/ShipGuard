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
| Compare fixture runs | `arena run` | Aggregate results and per-case reports |
| Import fixture packs | `arena import` | Validated local fixture pack |
| Sign fixture packs | `arena sign`, `arena verify` | SHA-256 pack metadata |
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
| Audit this toolkit | `self-audit` | Self-audit Markdown and JSON |
| Continue the release loop | `next-goal` | Slash-goal Markdown plan |

The commands are dependency-light Bash so release packages remain portable.
