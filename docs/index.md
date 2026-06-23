# ShipGuard Docs

ShipGuard is a local-first CLI and Codex plugin for proof-gated app maintenance.

Use this page as a map. Start with the smallest path that matches what you are trying to do.

## Start Here

| Goal | Read |
| --- | --- |
| Understand the core idea | [Verify-First Quickstart](verify-first-quickstart.md) |
| Inspect public demo outputs | [Demo Reports](demo-reports.md) |
| Install ShipGuard and check a repo | [Install and Doctor](install-doctor.md) |
| Audit the first PR workflow | [Verify-PR Action Audit](action-verify-pr.md) |
| Add ShipGuard to your own project | [Use in your repo](use-in-your-repo.md) |
| Choose the right command | [Command Matrix](command-matrix.md) |
| Look up every CLI option | [CLI reference](cli.md) |
| Find code that may not need to exist | [ShipGuard Lean Deck](lean-audit.md), including selected-mode bias proof, diff review, hardware/host proof boundaries, debt ledger, behavior gates, and benchmark-honest gain report |

## First Useful Run

From a ShipGuard checkout:

```bash
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable

./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

Open `/tmp/shipguard-verdict/shipguard-verdict.md`. The report shows whether the diff is ready to review, needs more proof, or should be blocked.

## Main Workflows

### Proof-Gated Agent Work

- [Task Contract](task-contract.md)
- [Verify-First Quickstart](verify-first-quickstart.md)
- [Policy Configuration](policy.md)
- [GitHub Action](github-action.md)
- [Verify-PR Action Audit](action-verify-pr.md)
- [PR Review Bot Mode](pr-review-bot.md)

### Repo Setup

- [Adoption Guide](adoption-guide.md)
- [Use in your repo](use-in-your-repo.md)
- [Template Profiles](template-profiles.md)
- [Install and Doctor](install-doctor.md)
- [Compatibility](compatibility.md)

### iOS and Codex

- [iOS ShipGuard](ios-shipguard.md)
- [iOS Preview Bridge](ios-preview.md)
- [ShipGuard Devspace](shipguard-devspace.md)
- [Codex Status](codex-status.md)
- [Codex Marketplace Readiness](codex-marketplace-readiness.md)

### Reports and Evaluation

- [Agent Autopsy](autopsy.md)
- [Maintainer Arena](arena.md)
- [Benchmark Format](benchmark.md)
- [Demo Reports](demo-reports.md)
- [ShipGuard Evaluation](oss-evaluation.md)
- [Docs Check](docs-check.md)
- [SARIF Evidence Export](sarif.md)
- [ShipGuard Lean Deck](lean-audit.md)

### Release Proof

- [Release Checklist](release-checklist.md)
- [Release Manifest](release-manifest.md)
- [Release Proof Bundle](release-proof.md)
- [Release Proof Consumption](release-proof-consumption.md)
- [Release Package Hygiene](release-package-hygiene.md)
- [Release Evidence Bundle](release-evidence-bundle.md)
- [Release Evidence Verification](release-evidence-verify.md)

### Product and Maintainer Surfaces

- [Product Strategy](product-strategy.md)
- [Maintainer Reliability OS](maintainer-reliability-os.md)
- [ShipGuard Naming](shipguard-naming.md)
- [GitHub Presentation](github-presentation.md)
- [Open Source Operating Model](open-source.md)
- [Privacy](privacy.md)
- [Security Threat Model](security-threat-model.md)

## V4 Track

These docs describe the v4 readiness path. They do not claim stable v4 publication by themselves.
Only a passing `v4 stable-publication` report with public GitHub release metadata, latest release context, downloaded or supplied public release assets, tag/manifest freshness, release version coherence, release asset coherence, post-release consumer proof with digest coverage, public release delta proof, release visibility handoff, public evidence closure, a final claim packet, and adoption/security evidence freshness from those assets can support a stable-v4 claim.

- [ShipGuard V4 Preview](v4-preview.md)
- [V4 Schema Freeze](v4-schema-freeze.md)
- [V4 Release Candidate](v4-release-candidate.md)
- [V4 Stable Publication](v4-stable-publication.md)

## Maintainer Commands

Use these when working on ShipGuard itself:

```bash
./bin/shipguard validate
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
./bin/shipguard codex marketplace-readiness --path . --out /tmp/shipguard-marketplace --strict --shareable
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard next-goal --out NEXT_GOAL.md
```

See [Changelog](../CHANGELOG.md) and [Roadmap](../ROADMAP.md) for project history and upcoming work.
