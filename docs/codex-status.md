# Codex Status

`shipguard codex status` checks whether a ShipGuard-related Codex plugin is installed in the local Codex plugin cache and whether that install looks stale.

It does not install, remove, or edit anything under `~/.codex`.

## Usage

```bash
./bin/shipguard codex status
```

Use `--cache` when validating a fixture cache or a non-default Codex home:

```bash
./bin/shipguard codex status --cache /tmp/codex-plugin-cache
```

Use `--strict` in local proof scripts when a missing or stale install should fail the command:

```bash
./bin/shipguard codex status --strict
```

## What It Checks

- the ShipGuard toolkit version from `VERSION`
- whether tracked `plugins/ios-shipguard` source exists in this checkout
- installed `ios-shipguard` plugin metadata under the Codex plugin cache
- stale repository URLs that still point at `ringly-codex-workflows`
- old `Shipguard` display casing in plugin and agent metadata
- old `codex-maintainer` command guidance inside the installed skill text

## Interpreting Status

- `pass`: an installed plugin was found and matches the tracked plugin source metadata.
- `stale`: an installed plugin was found, but source, version, branding, repository, or skill text cannot be trusted as current.
- `missing`: no `ios-shipguard` plugin install was found in the selected cache.

When the status is `stale` or `missing`, treat the current Codex plugin as unproven. Use the checked-out CLI and docs as the source of truth until plugin source and installation are refreshed.
