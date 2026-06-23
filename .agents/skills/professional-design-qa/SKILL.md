---
name: professional-design-qa
description: Critique AI-generated app UI with concrete design principles. Use when reviewing Expo, React Native, SwiftUI, web, or mobile UI for visual quality, coherence, design-system drift, generic AI output, hierarchy, spacing, contrast, motion, screenshots, or preview evidence.
---

# Professional Design QA

Use this skill when a task asks whether an AI-generated interface actually looks good, feels coherent, or fits the app. It is based on ShipGuard's native design QA vocabulary and Expo's public guidance on professional design principles for AI app development.

## Start

1. Read the nearest `AGENTS.md`.
2. Identify the app type, primary screens, design system files, and available visual proof.
3. If the repo is Expo/React Native and ShipGuard is available, run:

```bash
shipguard expo readiness --path . --out /tmp/shipguard-expo-readiness --shipguard-eval --shareable
```

4. For iOS/SwiftUI apps, prefer `shipguard ios design` and `shipguard ios preview` when available.
5. Read the generated report before proposing UI edits.

## Design Vocabulary

Critique the UI with these principles:

- Contrast: important elements need distinguishable size, color, weight, or shape.
- Hierarchy: the screen should make the first action, secondary action, and supporting content obvious.
- Alignment: related elements should share edges or axes so the layout feels intentional.
- Proximity: related items should be grouped without needing excessive borders or cards.
- Repetition: colors, type, spacing, shape, and component behavior should form a reusable system.
- Balance: the screen's visual weight should feel resolved, not randomly heavy on one side.
- White space: empty space should clarify the interface rather than make it sparse or cluttered.
- Unity: every element should feel like it belongs to the same product.

## Rules

- Do not treat source heuristics as visual truth. Require screenshots, simulator preview, browser render, or device proof for final visual claims.
- Do not ask for generic "make it modern" changes. Convert taste into specific contrast, hierarchy, alignment, proximity, repetition, balance, white-space, or unity findings.
- Do not add decorative motion unless it supports orientation, state change, feedback, or product character.
- Check reduced-motion behavior before approving animated UI.
- Flag one-off colors, gradients, cards, button styles, shadows, fonts, and icons when they do not map to a system.
- Prefer fewer stronger components over many custom one-off UI fragments.
- Keep app genre in view: utility and SaaS should be restrained and fast; games, kids, and creative apps can carry more expression; health and finance need calm, trust, and clear confirmation states.

## Output

End with:

- The top design risk.
- The principle it violates.
- The visual proof inspected or still missing.
- The smallest implementation slice that would improve the system.
- The proof command or screenshot/preview needed after the change.
