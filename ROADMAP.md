# Roadmap

This roadmap keeps the repo useful without pretending it is a finished framework.

## Now

- Keep the CLI stable for `init`, `validate`, `doctor`, and `score`.
- Keep Agent Autopsy stable for Markdown and JSON reports from run summaries, diffs, tasks, and test logs.
- Keep autopsy artifact generation available through GitHub Actions.
- Keep Maintainer Arena fixture aggregation stable for public benchmark examples.
- Keep PR review-comment output stable for warn/fail adoption.
- Keep leaderboard schema `1.0` stable for public benchmark consumers.
- Keep policy config plain, auditable, and non-executable.
- Keep CI gate outputs stable for artifact and PR workflows.
- Keep release packaging and installer scripts reproducible.
- Keep the reusable GitHub Action aligned with the CLI validator.
- Maintain the public examples, scorecard, autopsy fixtures, and iOS starter template as the workflow evolves.
- Keep the adoption docs and GitHub Pages shell current with each release.

## Next

- Add more anonymized transcripts from real maintenance work.
- Expand Maintainer Arena with more task types and external fixture packs.
- Add repository-level autopsy configuration for protected paths and custom risky-claim terms.
- Add optional pull request comments from `report.json`.
- Add SARIF or check-run output for CI consumers.
- Add template variants for non-iOS apps, including a web-app workflow kit.
- Consider npm or Homebrew distribution after the release tarball path stays stable.
- Enable GitHub Pages in repository settings after the docs shell is reviewed.

## Later

- Publish a small collection of anonymized maintainer workflows from real Ringly work.
- Add stricter markdown linting and shell linting when dependency cost is justified.
- Build a comparison matrix against other agent-workflow formats.
