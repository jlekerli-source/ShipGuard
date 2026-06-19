# ShipGuard V4 Preview

`shipguard v4 preview` is the product-readiness checkpoint for the v4 track. It is not an iOS simulator preview and it does not publish v4. It reads the ShipGuard checkout and writes a stabilization report that says what is stable, what remains preview-only, and what proof must exist before a v4 release claim is honest.

## Run It

```bash
./bin/shipguard v4 preview \
  --path . \
  --out /tmp/shipguard-v4-preview \
  --shipguard-eval \
  --shareable
```

Outputs:

- `v4-preview.json`
- `v4-preview.md`

The JSON contains `stableContract`, `schemaFreeze`, `securityReview`, `migrationPlan`, `deprecationPolicy`, `releaseReadiness`, `blockedClaims`, `scopeBoundary`, `reportQualityQuestions`, and `resultUX`.

## Preview Contract

The preview contract is deliberately conservative:

- The v4 front door stays the existing local CLI and plugin package, not a separate hosted service.
- Codex remains first-class, but the core evidence schema must stay agent-neutral.
- Adapter work is thin. Codex, XcodeBuildMCP, Expo/EAS, Claude, Gemini, Cursor, and generic MCP adapters should emit the same ShipGuard task, trace, receipt, and verdict structures instead of forking product logic.
- No separate API key is required for ordinary interactive use.
- Private app checkouts may be used only as read-only product-QA inputs. Public artifacts must use redacted fixtures.

## Schema Freeze Posture

The command distinguishes preview stabilization from a final schema freeze:

- `schemaFreeze.frozenForPreview = true` means the current preview fields are stable enough for fixture and report-quality work.
- `schemaFreeze.frozenForV4Release = false` means v4 is not yet a stable release contract.
- The next gate is a compatibility-fixture pass for additive changes, blocked breaking changes, migration notes, and changelog policy.

Schemas that matter for v4:

- Structured evidence receipts.
- Agent adapter traces.
- Value Gauntlet reports.
- Release proof bundles.
- Plugin metadata and install proof.

## Security Review

The preview report checks that trust boundaries exist before v4 expands:

- Shareable reports must not include local paths, tokens, private screenshots, private app source, or account identifiers.
- Release proof must be consumable from a fresh checkout before a release is called ready.
- Adapter reports must separate local proof, manual proof, and blocked proof.
- Marketplace/plugin readiness remains a local install and status proof until OpenAI public publishing is available.

The command does not claim a formal third-party security audit.

## Migration Plan

v4 should feel like a product upgrade, not a repo scramble:

1. Stabilize the preview command and v4 receipt family.
2. Freeze schema names, compatibility policy, and migration fixtures.
3. Publish adapter compatibility notes for Codex, XcodeBuildMCP, Expo/EAS, and generic MCP users.
4. Keep v3-compatible command aliases through the deprecation window.
5. Require package, install, plugin, docs, value, and release proof before announcing v4 as stable.

## Deprecation Policy

- Do not remove existing public commands during v4 preview stabilization.
- Prefer additive machine-readable fields over renamed fields.
- Breaking schema changes require a migration note, fixture update, and changelog entry.
- Deprecated fields keep compatibility shims for at least two minor releases unless they leak secrets or create unsafe behavior.

## Release Readiness

Before v4 can be called stable, the release lane must include at least:

```bash
git diff --check
./tests/v4_preview_test.sh
./tests/tool_value_gauntlet_test.sh
./bin/shipguard validate
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
./tests/self_audit_test.sh
./tests/cli_smoke_test.sh
./tests/package_release_test.sh
./bin/shipguard codex status --strict
```

The value gauntlet tracks this as `v4PreviewStabilizationReceipts`. When that passes, the next product weakness becomes v4 schema freeze rather than another vague roadmap item.
