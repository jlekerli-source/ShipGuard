# iOS Shipguard

`iOS Shipguard` is the product-facing layer for this repository: a Codex plugin, skill, and CLI mode for solo iOS developers working on apps where permissions, notifications, StoreKit, widgets, App Intents, background work, and release proof matter.

The existing `codex-maintainer` CLI remains the engine. Shipguard is the iOS-focused workflow that makes the engine easier to use.

## What Codex Already Does

Do not duplicate Codex platform features. Use them directly:

- Codex app skills, modes, worktrees, terminal, and built-in Git tools: [Codex app features](https://developers.openai.com/codex/app/features).
- Inline diff comments for asking Codex to change specific code: [Codex app features](https://developers.openai.com/codex/app/features).
- Simulator debugging through XcodeBuildMCP and the Build iOS Apps plugin: [Debug in iOS simulator](https://developers.openai.com/codex/use-cases/ios-simulator-bug-debugging).
- Browser comments on local previews through the Codex in-app browser: [In-app browser](https://developers.openai.com/codex/app/browser).
- GUI-only verification through computer use when structured tools are not enough: [Computer Use](https://developers.openai.com/codex/app/computer-use).

Shipguard adds the missing layer before those tools run: risk routing, permission inventory, ask-before-editing gates, and evidence prompts.

## First Useful Commands

Run doctor first so Codex understands the app topology before choosing a build, simulator, or proof route:

```bash
./bin/codex-maintainer ios doctor --path . --out /tmp/ios-shipguard-doctor
```

The command writes:

- `ios-doctor.md`
- `ios-doctor.json`

It detects Xcode projects, workspaces, Swift packages, schemes, deployment targets, Swift versions, bundle IDs, test plans, StoreKit configs, privacy manifests, plists, entitlements, Swift imports, and proof-readiness findings.

Then inventory risky permission and runtime surfaces. Inventory reuses doctor topology automatically so every detected surface can be mapped back to an app, package, or test target when the local files make ownership clear:

```bash
./bin/codex-maintainer ios inventory --path . --out /tmp/ios-shipguard-inventory
```

Use a saved doctor report when CI or another Codex step should consume the exact same topology:

```bash
./bin/codex-maintainer ios inventory \
  --path . \
  --doctor /tmp/ios-shipguard-doctor/ios-doctor.json \
  --out /tmp/ios-shipguard-inventory
```

The command writes:

- `ios-inventory.md`
- `ios-inventory.json`

It detects permission and runtime surfaces such as notifications, AlarmKit, Location, Camera, Microphone, Photos, HealthKit, Push Notifications, App Groups, Background Modes, Live Activities, WidgetKit, App Intents, StoreKit, Swift concurrency, Foundation Models, and Core ML.

The Markdown report starts with a target risk map, then shows detected surfaces, permission and entitlement review, unmapped surfaces, modernization opportunities, Codex workflow prompts, and ask-before-editing questions.

When source uses a permission-backed surface but the expected usage description or entitlement is missing, the report marks the surface as `needs-user-answer`. Codex should stop and ask the user before editing.

Try the public fixture:

```bash
./bin/codex-maintainer ios doctor --path fixtures/demo-ios-repo --out /tmp/ios-shipguard-demo-doctor
./bin/codex-maintainer ios inventory \
  --path fixtures/demo-ios-repo \
  --doctor /tmp/ios-shipguard-demo-doctor/ios-doctor.json \
  --out /tmp/ios-shipguard-demo
```

## Preview Bridge

Shipguard can serve a local phone-shaped preview page for Codex's in-app browser:

```bash
./bin/codex-maintainer ios preview --out /tmp/ios-shipguard-preview
```

The command binds to `127.0.0.1`, captures the booted Simulator with `xcrun simctl io booted screenshot --type=png <tempfile>`, and writes `session.json`, `preview-url.txt`, `preview-events.jsonl`, and `last-screenshot.png`.

Open the printed URL in Codex's in-app browser or ask `@Browser` to open it. You can leave browser comments on the rendered phone preview, or click the preview page and record a short note. Codex should read `preview-events.jsonl` and the preview server's `/api/handoff` payload before editing or choosing an XcodeBuildMCP action.

The bridge is intentionally not a native plugin-owned Codex side panel. Current plugin docs cover skills, apps/connectors, MCP servers, hooks, and assets, while the in-app browser is the documented surface for local visual previews and comments. See `docs/ios-preview.md`.

## Shipguard Devspace

Shipguard Devspace exposes the preview bridge to ChatGPT Apps / MCP hosts:

```bash
export SHIPGUARD_DEVSPACE_TOKEN="$(openssl rand -hex 32)"
./bin/codex-maintainer ios devspace \
  --port 8787 \
  --preview-out /tmp/ios-shipguard-preview \
  --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN
```

Use this when the user wants ChatGPT or GPT-5.5 Pro to plan from a live phone widget and then prepare a Codex handoff. Devspace serves `/mcp`, registers `ui://widget/shipguard-preview-v1.html`, proxies screenshots, records preview events, and prepares a scoped Codex app-server prompt without spawning Codex automatically. Use bearer auth whenever HTTP mode is exposed through a tunnel.

See `docs/shipguard-devspace.md`.

## Self-Advancing Goal Loop

Shipguard includes a local goal loop for turning the product roadmap into one concrete Codex goal at a time. The loop is intentionally evidence-gated: it does not mark a goal complete by itself. A user, CI job, or Codex thread must provide the proof receipt, and then the command emits the next goal automatically.

Start the loop:

```bash
./bin/codex-maintainer ios goals init \
  --state .shipguard/goals.json \
  --out NEXT_SHIPGUARD_GOAL.md
```

Print the current goal:

```bash
./bin/codex-maintainer ios goals next \
  --state .shipguard/goals.json \
  --out NEXT_SHIPGUARD_GOAL.md
```

Complete the current goal and automatically write the next one:

```bash
./bin/codex-maintainer ios goals complete \
  --state .shipguard/goals.json \
  --goal shipguard-ios-doctor \
  --evidence path/to/proof.md \
  --out NEXT_SHIPGUARD_GOAL.md
```

The built-in phase order is:

1. app understanding
2. guided planning
3. proof routing
4. modernization intelligence
5. privacy/security/distribution
6. evals and quality gates

The full plan lives in `docs/superpowers/plans/2026-06-16-ios-shipguard-autonomous-loop.md`.

## Codex Plugin

The repo includes a local plugin scaffold:

```text
plugins/ios-shipguard/
```

Install it from this checkout as a repo-local marketplace:

```bash
codex plugin marketplace add .agents/plugins
codex plugin add ios-shipguard@ringly-codex-workflows
```

Start a new Codex thread after installing so the skill metadata is loaded.

## Modes

Shipguard routes work into one primary mode:

- `permission-audit`: usage descriptions, entitlements, authorization states, denied UI.
- `simulator-debug`: build, launch, reproduce, screenshot, logs, UI tree, debugger.
- `release-proof`: TestFlight, App Store, device proof, proof packets, release claims.
- `storekit-commerce`: product IDs, purchases, restore, entitlements, sandbox proof.
- `widgets-intents-shared-store`: WidgetKit, App Intents, app groups, stale shared state.
- `preview-bridge`: Codex in-app-browser preview, click/note receipts, and simulator screenshot handoff.
- `preview-devspace`: ChatGPT Apps / MCP connector, phone widget, and Codex handoff preparation.
- `ui-polish`: SwiftUI layout, copy, accessibility, Dynamic Type, localization.

The skill lives at `plugins/ios-shipguard/skills/ios-shipguard/SKILL.md`.

## Product Direction

Keep the scope narrow:

- Make Codex ask the right iOS questions before editing.
- Produce local evidence a solo developer can trust.
- Use Codex native simulator, Git, worktree, and comment features instead of cloning them.
- Keep scripts dependency-light so the workflow can run in CI or a local terminal.

Do not expand Shipguard into a hosted dashboard, generic agent framework, or replacement for XcodeBuildMCP.
