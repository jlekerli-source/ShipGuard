# Codex Status

`shipguard codex status` checks whether a ShipGuard-related Codex plugin is installed in the local Codex plugin cache and whether that install looks stale.

It does not install, remove, or edit anything under `~/.codex`.

## Update Model

Updating the Git repository does not automatically update a running Codex thread.

ShipGuard has three separate states:

1. Repository source: GitHub has the latest `plugins/ios-shipguard`, `.agents/plugins/marketplace.json`, docs, tests, and CLI source after a commit is pushed.
2. Local Codex plugin cache: Codex installs plugin bundles under `~/.codex/plugins/cache/...`; refresh or reinstall the plugin from the updated marketplace/source when the cache should change.
3. Current Codex thread: skill metadata is loaded when a thread starts, so start a new Codex thread after refreshing the plugin cache.

For this checkout, the local install flow is:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

Then start a new Codex thread before relying on refreshed skill instructions.

The command prints this refresh handoff in its output so status reports remain actionable even when copied into a Codex thread or issue.

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
- whether `.agents/plugins/marketplace.json` exposes `ios-shipguard@shipguard` from `./plugins/ios-shipguard`
- installed `ios-shipguard` plugin metadata under the Codex plugin cache
- stale repository URLs that still point at `ringly-codex-workflows`
- old `Shipguard` display casing in plugin and agent metadata
- old `codex-maintainer` command guidance inside the installed skill text
- the exact handoff for repository updates, plugin reinstall, new-thread refresh, and stale-cache cleanup

## Interpreting Status

- `pass`: an installed plugin was found and matches the tracked plugin source metadata.
- `stale`: an installed plugin was found, but source, version, branding, repository, or skill text cannot be trusted as current.
- `missing`: no `ios-shipguard` plugin install was found in the selected cache.

When the status is `stale` or `missing`, treat the current Codex plugin as unproven. Use the checked-out CLI and docs as the source of truth until plugin source and installation are refreshed.
