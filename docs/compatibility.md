# Compatibility

ShipGuard keeps a legacy command wrapper for older automation, but new docs, scripts, and examples should use `shipguard`.

## Legacy Wrapper

`bin/codex-maintainer` remains in release packages and installer output as a compatibility wrapper. It forwards to the ShipGuard CLI so older workflows can keep running while users migrate.

Do not use the legacy wrapper in new examples, plugin guidance, or release instructions. Prefer:

```bash
./bin/shipguard validate
./bin/shipguard self-audit --out /tmp/shipguard-self-audit
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
```

Compatibility proof lives in `tests/cli_smoke_test.sh`, `tests/package_release_test.sh`, and the release package file list.
