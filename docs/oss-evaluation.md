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
# files_checked: 285
# links_checked: 48
# broken_count: 0

./bin/shipguard arena run --fixture fixtures/arena --out /tmp/shipguard-arena
# average: 7.00/12
```

Codex install check from this machine:

```bash
./bin/shipguard codex status
# Overall status: pass
```

The installed Codex cache now has `ios-shipguard` metadata version `0.2.0+codex.20260617003813`, repository `https://github.com/jlekerli-source/ShipGuard`, display name `iOS ShipGuard`, and no stale `ringly-codex-workflows`, `Shipguard`, or primary `codex-maintainer` guidance. The tracked checkout includes `plugins/ios-shipguard`, and package proof requires that plugin source.

## Verdict

ShipGuard is useful as a CLI and workflow bundle today. It validates itself, produces release proof, checks docs, scores agent runs, exports GitHub Action artifacts, and catches dangerous proof claims in benchmark fixtures.

The Codex plugin source and local cache are now clean enough for local use. The remaining plugin gap is distribution: this is still a direct cache refresh, not a marketplace-backed reinstall flow.

## Keep

- Keep `shipguard` as the CLI and package command.
- Keep `codex-maintainer` only as a compatibility alias for older automation.
- Keep Agent Autopsy, Arena, docs-check, release-proof, release-consume, release-evidence, transcript verification, CI gate, SARIF, and self-audit.
- Keep the scorecard categories. They map well to real maintainer failure modes.
- Keep the current GitHub Actions coverage because it proves the CLI and release artifacts from source.

## Refine

- Keep Codex plugin source first-class and tracked under `plugins/ios-shipguard`.
- Keep plugin metadata on `ShipGuard` casing and repository/homepage URLs on `jlekerli-source/ShipGuard`.
- Keep installed skill guidance honest about `shipguard ios` helper availability.
- Add a marketplace-backed reinstall flow instead of relying on direct cache sync.
- Add regression-awareness benchmark cases because the Arena average is held down partly by weak regression detection.
- Tighten docs around when to use the CLI versus when to install the Codex plugin.

## Add

- `shipguard codex status` for local Codex install-state proof.
- A marketplace source entry for `ios-shipguard`.
- A plugin install or refresh handoff that says exactly when Codex must be restarted or cache-cleared.
- Restore or intentionally retire the `shipguard ios` helper commands. The plugin now treats them as optional because this public checkout does not currently expose them.
- A repository threat model artifact before running a full Codex Security scan.
- More Arena fixtures for security-sensitive workflows: credentials, untrusted paths, generated artifacts, network posting, GitHub token scope, and release asset trust.
- Optional OpenAI Agents SDK evaluation only if ShipGuard becomes a runnable agent service. Do not add OpenAI API dependencies to the CLI without that product decision.

## Remove Or Defer

- Keep stale public references to `ringly-codex-workflows` out of plugin source and future packages.
- Remove `codex-maintainer` from primary docs after compatibility coverage is proven for one more release.
- Defer npm or Homebrew distribution until the Codex plugin source and release install story are reliable.
- Defer a full Codex Security repository scan until subagent authorization is explicit; use threat modeling first.
- Defer Agents SDK work until there is a clear agent product, input contract, and eval target.

## Plugin And Skill Guidance

- Superpowers: useful for larger feature design and execution plans. Use it when adding a new subsystem, but keep small CLI/doc fixes on the repo-native proof loop.
- Codex Security: use `threat-model` first. Use full `security-scan` only with explicit subagent authorization and when the scan can produce ledger artifacts.
- OpenAI Developers: use Agents SDK only for a deliberate agent/eval app. Not needed for the current shell CLI or docs-only workflow bundle.
- GitHub: keep using local `gh` and Actions verification for publish proof.

## Phased Plan

### Phase 1: Plugin Source And Local Cache

Status: done.

- Restore tracked `plugins/ios-shipguard` source.
- Update plugin metadata and skill text to `ShipGuard`.
- Include plugin source in package, validate, self-audit, and package tests.
- Refresh the installed local Codex cache.
- Prove with `./bin/shipguard codex status --strict`.

### Phase 2: iOS Helper Decision

Status: next.

- Decide whether the public ShipGuard CLI should restore the `shipguard ios ...` helper commands from the last private package or retire them from public plugin guidance.
- If restoring, bring back the Python helper scripts, fixtures, docs, and tests as a single validated slice.
- If retiring, simplify the plugin around XcodeBuildMCP, AGENTS routing, and source inspection.

### Phase 3: Marketplace-Backed Install

Status: next.

- Add a local marketplace entry for `ios-shipguard`.
- Use the Codex plugin cachebuster/reinstall flow instead of direct cache sync.
- Document the new-thread boundary required for Codex to load refreshed skill metadata.

### Phase 4: Security Evaluation

Status: planned.

- Write a repository threat model before a full scan.
- Add one Arena fixture for secret/path leakage, token-scoped GitHub posting, or release asset trust.
- Only run the full Codex Security repository scan with explicit subagent authorization.

### Phase 5: Benchmark And Product Polish

Status: planned.

- Add regression-awareness Arena fixtures.
- Improve first-run adoption docs around CLI versus plugin usage.
- Keep Agents SDK deferred unless ShipGuard becomes a runnable agent service with a concrete eval target.
