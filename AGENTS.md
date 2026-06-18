# ShipGuard Maintainer Instructions

ShipGuard is a Codex workflow kit for evidence-based app maintenance. It packages starter profiles, CLI reports, Codex skill guidance, validation routing, release proof, and product-quality evals so AI-assisted coding is repeatable, reviewable, and honest about proof.

## Project Overview

- Product: ShipGuard.
- Core surfaces: `bin/shipguard`, `scripts/`, `templates/`, `plugins/ios-shipguard/`, `docs/`, `fixtures/`, `tests/`, `.github/workflows/`, and release proof tooling.
- First-class domain: iOS development, with web, backend, and CLI starter profiles as expanding surfaces.
- Product QA inputs may include private app checkouts, but ShipGuard work must improve ShipGuard itself unless the user explicitly authorizes app edits.

## Startup Routine

1. Read this file before changing the repository.
2. Route the task through `docs/command-matrix.md`, `docs/cli.md`, and the nearest focused docs for the command being changed.
3. Inspect existing tests and fixtures before adding behavior.
4. Keep public CLI behavior stable unless the task explicitly asks for a new or breaking interface.
5. For product-quality runs on private apps, keep the target read-only and convert observations into public ShipGuard fixtures or rules.

## Validation Commands

Use the smallest lane that proves the change:

```bash
git diff --check
python3 -m py_compile scripts/<changed-script>.py
./tests/<focused-test>.sh
./bin/shipguard validate
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
./tests/self_audit_test.sh
./tests/cli_smoke_test.sh
./tests/package_release_test.sh
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard codex status --strict
```

Run broader tests when editing shared routing, package contents, release proof, plugin metadata, or report-quality logic. A timed-out, interrupted, blocked, or infrastructure-failed command is not a pass.

## High-Risk Areas

- `bin/shipguard`: public command routing and compatibility.
- `scripts/shipguard_devspace_mcp.py`: local browser/widget bridge, URL handling, response size, and preview boundaries.
- `scripts/profile_audit.py`, `scripts/profile_fix_plan.py`, and `scripts/tool_value_gauntlet.py`: product-quality scoring and evidence routing.
- `.github/workflows/`: repository permissions, action inputs, release artifacts, and token handling.
- `scripts/release_*`, `scripts/package_release*`, and `tests/package_release_test.sh`: release provenance and install proof.
- `plugins/ios-shipguard/`: installed Codex behavior and skill routing.

## Product QA Boundaries

- Do not edit private app checkouts while evaluating ShipGuard unless the user explicitly changes the task to app work.
- Do not copy private paths, screenshots, source snippets, tokens, or app identifiers into public fixtures or docs.
- Say "real-app evidence showed a ShipGuard weakness" rather than turning that evidence into target-app remediation.
- ShipGuard-generated starter files are profile-health evidence, not target-app validation or risk evidence.

## Public Interface Rules

- Prefer improving existing commands before adding a new public command.
- New public commands need docs, help output, tests, package inclusion, plugin guidance when relevant, and a value-gauntlet or report-quality path.
- Output JSON should stay machine-readable, include scope boundaries, and distinguish local proof, manual proof, and blocked proof.
- Markdown should be useful to a solo developer without pretending that recommendations are completed work.

## Release Procedure

Before claiming a release is ready:

1. Bump versioned files intentionally.
2. Run focused tests plus bundle, self-audit, and package proof lanes.
3. Refresh the local CLI and Codex plugin cache when plugin behavior changed.
4. Push `main` only after validation passes.
5. Watch GitHub Actions for the pushed commit.
6. Create release proof artifacts and verify consumer install/proof checks before announcing the release.

## Completion Checklist

1. The requested ShipGuard artifact or behavior exists.
2. Private-app checkouts were not modified without explicit authorization.
3. Generated reports separate target evidence from ShipGuard starter evidence.
4. Tests or validation commands prove the actual changed behavior.
5. Docs and plugin guidance match the current command behavior.
6. Any remaining blocker is stated as a concrete command, missing permission, or external dependency.
