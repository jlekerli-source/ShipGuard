# Adoption Guide

Use this guide when you want to bring the workflow kit into another repository without copying sample-app assumptions blindly.

## The First 30 Minutes

1. Clone or open this repository.
2. Run the local validator:

```bash
./bin/shipguard validate
```

3. Initialize a starter profile into a test project:

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard init web ../my-web-app
./bin/shipguard init backend ../my-service
./bin/shipguard init cli ../my-tool
```

4. Open the generated `AGENTS.md` and replace:

- `[APP_NAME]`
- `[XCODE_PROJECT]`
- `[APP_SOURCE_DIRECTORY]`
- `[TEST_DIRECTORY]`
- placeholder validation commands
- profile-specific high-risk areas that do not apply to your repo

5. Run the doctor check:

```bash
./bin/shipguard doctor ../my-ios-app
./bin/shipguard doctor web ../my-web-app
./bin/shipguard doctor backend ../my-service
./bin/shipguard doctor cli ../my-tool
```

6. Copy one prompt from `examples/prompt-pack.md` and test it on a small, low-risk issue.

## CLI Versus Codex Plugin

Use the CLI when you need repeatable proof from a shell command:

- validate the workflow bundle with `shipguard validate`
- inspect copied starter files with `shipguard doctor`
- score a run with `shipguard autopsy`
- run the public benchmark with `shipguard arena run`
- package or verify release evidence

Use the local Codex plugin when you want Codex to load ShipGuard guidance at thread startup:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

Start a new Codex thread after installing or refreshing the plugin. Existing threads keep the skill metadata they loaded at startup.

Use `shipguard ios ...` helpers before risky iOS work when a project has permissions, StoreKit, widgets, App Intents, notifications, background modes, Live Activities, preview handoffs, or release proof. These commands do not replace Xcode, Simulator, TestFlight, App Store Connect, or device evidence; they route the questions and proof lanes before edits.

## What To Customize First

- Project overview and source paths.
- Real validation commands.
- Protected files and high-risk areas.
- Release and proof rules.
- Product-specific permission, payment, persistence, localization, and lifecycle risks.

## What Not To Copy Blindly

- Alarm-specific assumptions if your app is not alarm-related.
- Web-specific auth, payment, migration, or browser-test assumptions if your app does not use them.
- Backend-specific migration, queue, webhook, or rollout assumptions if your repo is not a service.
- CLI-specific stdout, exit-code, package, or cross-platform assumptions if your repo is not a CLI.
- Commands that do not exist in your repo.
- Release proof rules that do not match your App Store, TestFlight, or deployment process.
- Any text that implies stronger reliability than your product can prove.

## Definition Of Adopted

The workflow is adopted when:

- `AGENTS.md` describes your real app.
- `PLANS.md` is used before risky work.
- At least one skill maps to a recurring task.
- CI runs the validation action or an equivalent local check.
- The maintainer can score a Codex run with `SCORECARD.md`.
