# Expo Readiness

`shipguard expo readiness` is ShipGuard ExpoDeck: a read-only Expo, EAS, and AI-generated UI quality audit inspired by Expo SDK 56 and Expo's professional design-principles guidance.

```bash
./bin/shipguard expo readiness \
  --path ../my-expo-app \
  --out /tmp/shipguard-expo-readiness \
  --runtime-evidence /tmp/expo-proof \
  --shareable
```

The command writes:

- `expo-readiness.json`
- `expo-readiness.md`

## What It Checks

- Expo project detection from `package.json`, app config, and `eas.json`.
- Expo SDK version compared with SDK 56-era readiness.
- Expo UI migration opportunities from common native component packages.
- Expo Router plus direct React Navigation package pairing.
- `@expo/vector-icons` deprecation exposure.
- Inline Expo module and type-generation signals.
- EAS setup and whether build-timing evidence still needs to be attached.
- AI-agent scaffolding such as `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json`.
- Professional design-principle evidence for AI-generated UI: contrast, hierarchy, alignment, proximity, repetition, balance, white space, and unity.
- Whether design-system, token, style, accessibility, and motion signals are present enough to make AI UI critique actionable.
- Optional `--runtime-evidence` files or directories for Expo Doctor logs, EAS timing logs, preview notes, screenshots, simulator/device proof, and native runtime artifacts.

## Proof Boundary

ExpoDeck does not run `npx expo`, install packages, prebuild native projects, edit EAS config, or claim build-speed improvements. It recommends proof commands and keeps source heuristics separate from real Expo Doctor, EAS Build, native build, runtime, timing, screenshot, and preview evidence. When `--runtime-evidence` is provided, ShipGuard reads those supplied artifacts only and labels them as attached evidence, not work it performed.

Useful follow-up commands:

```bash
npx expo-doctor
npx expo install --fix
shipguard expo readiness --path . --out /tmp/shipguard-expo-readiness --runtime-evidence <proof-file-or-dir> --shareable
shipguard agent trace --trace <agent-trace> --out <trace-dir> --expo-eas-evidence <eas-evidence-dir>
shipguard ios report-quality --reports /tmp/shipguard-expo-readiness --out /tmp/shipguard-expo-quality --shareable
```

Use `--shipguard-eval --shareable` when a private Expo app is only being used as read-only product QA for improving ShipGuard.
