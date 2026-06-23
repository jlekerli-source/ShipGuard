---
name: expo-readiness
description: Expo and EAS modernization workflow for Codex. Use when auditing or upgrading Expo/React Native apps, especially Expo SDK 56 readiness, Expo UI stable native primitives, professional design QA for AI-generated app UI, EAS build timing, inline Expo modules, Hermes/update behavior, Expo Router migration, or AI-agent scaffolding with Expo skills.
---

# Expo Readiness

Use this skill when the target app is Expo or React Native and the task mentions Expo SDK upgrades, EAS, Expo UI, native modules, build speed, Expo Router, AI-generated UI quality, professional design principles, or official Expo agent skills.

## Start

1. Read the nearest `AGENTS.md`.
2. Resolve ShipGuard:

```bash
if [ -x ./bin/shipguard ]; then
  SHIPGUARD_CLI=./bin/shipguard
elif command -v shipguard >/dev/null 2>&1; then
  SHIPGUARD_CLI="$(command -v shipguard)"
elif [ -x "$HOME/.local/bin/shipguard" ]; then
  SHIPGUARD_CLI="$HOME/.local/bin/shipguard"
else
  SHIPGUARD_CLI=
fi
```

3. If available, run the read-only ExpoDeck audit:

```bash
"$SHIPGUARD_CLI" expo readiness --path . --out /tmp/shipguard-expo-readiness --shareable
```

4. Read `/tmp/shipguard-expo-readiness/expo-readiness.md` before proposing edits.

## Rules

- Keep `shipguard expo readiness` read-only. It should inspect files and recommend proof commands, not run `npx expo`, mutate dependencies, prebuild native projects, or edit EAS config.
- Treat Expo SDK 56 features as opportunities until the repo proves them with `npx expo-doctor`, app tests, native builds, EAS timing, or runtime evidence.
- Treat professional design findings as source-level critique until a screenshot, simulator, device, or browser preview proves the rendered UI.
- Use concrete design vocabulary for AI-built UI: contrast, hierarchy, alignment, proximity, repetition, balance, white space, and unity.
- Do not claim build-speed wins without before/after timing evidence from local builds or EAS.
- For Expo UI migrations, prototype one low-risk component first and verify iOS, Android, accessibility, and visual behavior.
- For inline Expo modules, scaffold through official Expo tooling and verify generated TypeScript plus native build proof.
- For Expo Router plus React Navigation, inspect imports and run diagnostics before removing navigation packages.
- For AI-agent scaffolding, use official Expo skills as additive guidance and keep project-specific safety rules in `AGENTS.md`.

## Common Routes

- SDK upgrade: `shipguard expo readiness`, then `npx expo install expo@latest`, `npx expo install --fix`, `npx expo-doctor`, and the app validation lane.
- Build performance: compare clean build or EAS timing before/after SDK 56 and precompiled-module changes.
- EAS assurance: attach EAS build/update/timing artifacts to `shipguard agent trace --expo-eas-evidence <dir>`.
- ShipGuard product QA: if a private Expo app is used only to improve ShipGuard, add `--shipguard-eval --shareable`, then feed ExpoDeck into `shipguard ios report-quality`.

## Output

End with the ExpoDeck status, top finding, proof commands that still need to run, files changed if any, and any remaining manual/EAS proof.
