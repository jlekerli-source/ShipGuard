# Roadmap

This roadmap keeps the repo useful without pretending it is a finished framework.

## Now

- Keep the CLI stable for `init`, `validate`, `doctor`, and `score`.
- Keep Agent Autopsy stable for Markdown and JSON reports from run summaries, diffs, tasks, and test logs.
- Keep autopsy artifact generation available through GitHub Actions.
- Keep Maintainer Arena fixture aggregation stable for public benchmark examples.
- Keep backend and CLI arena cases in the public benchmark fixture pack.
- Keep PR review-comment output stable for warn/fail adoption.
- Keep leaderboard schema `1.0` stable for public benchmark consumers.
- Keep policy config plain, auditable, and non-executable.
- Keep CI gate outputs stable for artifact and PR workflows.
- Keep CI step-summary output readable in GitHub Actions workflow runs.
- Keep GitHub Check Run payload export stable and opt-in.
- Keep optional GitHub Check Run posting explicit, token-scoped, and disabled by default.
- Keep SARIF export stable for Autopsy findings and CI gate artifacts.
- Keep external arena fixture import strict about supported files and obvious secret leakage.
- Keep fixture-pack integrity metadata deterministic and verifiable.
- Keep self-audit output stable enough to prove release readiness from source and extracted packages.
- Keep next-goal output deterministic enough to restart the improvement loop after each release.
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
- Keep the reusable GitHub Action aligned with the CLI validator.
- Maintain the public examples, scorecard, autopsy fixtures, and iOS starter template as the workflow evolves.
- Keep the adoption docs and GitHub Pages shell current with each release.

## Next

- Add more anonymized transcripts from real maintenance work.
- Expand Maintainer Arena with more task types and optional identity signing when the fixture contract needs it.
- Add more specialized profiles only when they have clear maintainer workflows.
- Consider npm or Homebrew distribution after the release tarball path stays stable.
- Enable GitHub Pages in repository settings after the docs shell is reviewed.

## Later

- Publish a small collection of anonymized maintainer workflows from real Ringly work.
- Add stricter markdown linting and shell linting when dependency cost is justified.
- Build a comparison matrix against other agent-workflow formats.
