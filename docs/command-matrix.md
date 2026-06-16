# Command Matrix

`codex-maintainer` is organized around the core maintainer jobs below.

| Job | Command | Output |
| --- | --- | --- |
| Install workflow kit | `init ios`, `init web` | Starter workflow files |
| Check workflow kit | `validate` | Validation pass/fail |
| Check target repo setup | `doctor ios`, `doctor web` | Missing file report |
| Configure project policy | `policy init`, `policy show` | Plain policy file |
| Audit one AI run | `autopsy` | Markdown and JSON report |
| Export CI evidence | `sarif` | SARIF 2.1.0 results |
| Compare fixture runs | `arena run` | Aggregate results and per-case reports |
| Import fixture packs | `arena import` | Validated local fixture pack |
| Generate PR comment | `review-comment` | Comment Markdown and badge JSON |
| Enforce in CI | `ci-gate` | Gate bundle and optional failure |
| Summarize CI gate | `ci-summary` | Step-summary Markdown |
| Prepare Check Run payload | `check-run` | GitHub Checks API payload JSON |
| Publish benchmark data | `leaderboard build` | Stable leaderboard JSON |
| Audit this toolkit | `self-audit` | Self-audit Markdown and JSON |
| Continue the release loop | `next-goal` | Slash-goal Markdown plan |

The commands are dependency-light Bash so release packages remain portable.
