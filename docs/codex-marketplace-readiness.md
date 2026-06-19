# Codex Marketplace Readiness

`shipguard codex marketplace-readiness` checks whether the tracked `ios-shipguard` Codex plugin source is ready for a public marketplace-style install and review.

It is read-only. It does not install the plugin, mutate the Codex cache, create a GitHub release, upload screenshots, or submit anything to OpenAI.

## Usage

```bash
./bin/shipguard codex marketplace-readiness \
  --path . \
  --out /tmp/shipguard-marketplace \
  --cache "$HOME/.codex/plugins/cache" \
  --strict \
  --shareable
```

Use `--cache <dir>` with a fixture cache in tests or with the real Codex plugin cache after refreshing the local marketplace install.

## What It Checks

- tracked plugin metadata in `plugins/ios-shipguard/.codex-plugin/plugin.json`
- local marketplace source in `.agents/plugins/marketplace.json`
- plugin logo and composer icon assets under `plugins/ios-shipguard/assets/`
- README logo and release-install presentation
- app-neutral public positioning with no Ringly-only framing
- install and refresh docs for `codex plugin marketplace add .`
- strict `shipguard codex status --strict` proof against the selected plugin cache
- a copy-ready submission packet with install commands, proof commands, privacy notes, and model-choice boundaries

## Submission Packet

Listing title: `iOS ShipGuard`

Developer: `ShipGuard`

Category: `Developer`

Short description: Guardrails and preview handoffs for iOS Codex work.

Repository: `https://github.com/jlekerli-source/ShipGuard`

Install Commands:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

After refreshing the plugin, start a new Codex thread before relying on refreshed skill metadata.

Proof Commands:

```bash
./bin/shipguard codex marketplace-readiness --path . --out /tmp/shipguard-marketplace --strict --shareable
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./tests/codex_marketplace_readiness_test.sh
./tests/package_release_test.sh
```

## Asset Checklist

- README logo: `.github/assets/shipguard-icon.png`
- Plugin logo: `plugins/ios-shipguard/assets/app-icon.png`
- Composer icon: `plugins/ios-shipguard/assets/composer-icon.png`
- Screenshots: generate from a real demo, Devspace preview, or marketplace-requested capture when a public directory asks for screenshots.

Do not fabricate screenshots. Do not use CSS/SVG mock art as proof of the product experience. Do not publish private app screenshots, local paths, tokens, app identifiers, or proprietary reports.

## Boundaries

ShipGuard exposes CLI, plugin, and MCP/App surfaces. ChatGPT or Codex model selection happens outside ShipGuard.

Ordinary interactive CLI/plugin use should not require a separate ShipGuard API key.

The readiness report can be shared with `--shareable`; it replaces local checkout and cache paths with placeholders.
