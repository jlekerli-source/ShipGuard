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
# files_checked: 283
# links_checked: 48
# broken_count: 0

./bin/shipguard arena run --fixture fixtures/arena --out /tmp/shipguard-arena
# average: 7.00/12
```

Codex install check from this machine:

```bash
./bin/shipguard codex status
# Overall status: stale
```

The installed Codex cache still has `ios-shipguard` version `0.2.0+codex.20260616230117` under `~/.codex/plugins/cache/ringly-codex-workflows`, with old repository metadata and old `Shipguard` casing. The tracked checkout does not currently include `plugins/ios-shipguard` source, so the installed plugin cannot be rebuilt or verified from source yet.

## Verdict

ShipGuard is useful as a CLI and workflow bundle today. It validates itself, produces release proof, checks docs, scores agent runs, exports GitHub Action artifacts, and catches dangerous proof claims in benchmark fixtures.

It is not yet clean as a Codex plugin product. The installable plugin path is stale, not tracked as source, and not covered by the same proof loop as the CLI. That should be the next major refinement before adding more surface area.

## Keep

- Keep `shipguard` as the CLI and package command.
- Keep `codex-maintainer` only as a compatibility alias for older automation.
- Keep Agent Autopsy, Arena, docs-check, release-proof, release-consume, release-evidence, transcript verification, CI gate, SARIF, and self-audit.
- Keep the scorecard categories. They map well to real maintainer failure modes.
- Keep the current GitHub Actions coverage because it proves the CLI and release artifacts from source.

## Refine

- Make Codex plugin source first-class and tracked under `plugins/ios-shipguard`.
- Rename plugin metadata to `ShipGuard` casing and update repository/homepage URLs to `jlekerli-source/ShipGuard`.
- Update installed skill guidance to prefer `./bin/shipguard`; mention `codex-maintainer` only as a compatibility alias.
- Add package tests that prove plugin source is included once it is restored.
- Add regression-awareness benchmark cases because the Arena average is held down partly by weak regression detection.
- Tighten docs around when to use the CLI versus when to install the Codex plugin.

## Add

- `shipguard codex status` for local Codex install-state proof.
- A tracked plugin source tree and plugin package test.
- A plugin install or refresh handoff that says exactly when Codex must be restarted or cache-cleared.
- A repository threat model artifact before running a full Codex Security scan.
- More Arena fixtures for security-sensitive workflows: credentials, untrusted paths, generated artifacts, network posting, GitHub token scope, and release asset trust.
- Optional OpenAI Agents SDK evaluation only if ShipGuard becomes a runnable agent service. Do not add OpenAI API dependencies to the CLI without that product decision.

## Remove Or Defer

- Remove stale public references to `ringly-codex-workflows` from plugin source and future packages.
- Remove `codex-maintainer` from primary docs after compatibility coverage is proven for one more release.
- Defer npm or Homebrew distribution until the Codex plugin source and release install story are reliable.
- Defer a full Codex Security repository scan until subagent authorization is explicit; use threat modeling first.
- Defer Agents SDK work until there is a clear agent product, input contract, and eval target.

## Plugin And Skill Guidance

- Superpowers: useful for larger feature design and execution plans. Use it when adding a new subsystem, but keep small CLI/doc fixes on the repo-native proof loop.
- Codex Security: use `threat-model` first. Use full `security-scan` only with explicit subagent authorization and when the scan can produce ledger artifacts.
- OpenAI Developers: use Agents SDK only for a deliberate agent/eval app. Not needed for the current shell CLI or docs-only workflow bundle.
- GitHub: keep using local `gh` and Actions verification for publish proof.

## Next Iteration

1. Restore tracked `plugins/ios-shipguard` source from the last known package or rebuild it from current docs.
2. Update plugin metadata and skill text to `ShipGuard` and `./bin/shipguard`.
3. Extend `shipguard validate`, `self-audit`, and package tests to prove the plugin source and package contents.
4. Publish or install the refreshed plugin into Codex, then rerun `shipguard codex status --strict`.
5. Add one security-oriented Arena fixture around secret/path leakage or token-scoped GitHub posting.
