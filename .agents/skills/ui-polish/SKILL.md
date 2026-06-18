---
name: ui-polish
description: SwiftUI product-polish workflow. Use when a task touches visual hierarchy, copy, interaction states, Dynamic Type, compact layouts, localization/RTL, onboarding, settings, authoring flows, premium screens, or UI test polish.
---

# UI Polish

Use this skill for narrow UI improvements that preserve alarm trust.

## Steps

1. Read `BEST_PRACTICES.md`, `docs/ui-ux-principles.md`, `docs/change-review-matrix.md`, and `docs/validation-commands.md`.
2. Define the user job and remove unnecessary UI before adding more chrome.
3. Keep the first screen usable. Do not replace real app surfaces with explanatory landing-page copy.
4. Check empty, loading, denied, degraded, failed, cancelled, downgrade, offline, compact, Dynamic Type, and localized states when the surface can enter them.
5. Keep reliability, permission, and premium copy truthful. Paid features must never imply stronger system delivery than the app can prove.
6. Prefer existing components, themes, symbols, accessibility identifiers, and localization helpers.
7. Validate with the narrow UI lane:

```bash
./scripts/run_onboarding_validation.sh
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh premium-surfaces
./scripts/run_alarm_ui_batches.sh alarm-authoring-first-tap
python3 ./scripts/check_localization_coverage.py
```

8. If visual proof is missing, say so. Screenshots and simulator proof do not replace physical-device proof for delivery or reliability claims.

## ShipGuard QA Hooks

When this skill is being audited inside the ShipGuard ShipYard, keep the skill useful by running the product-QA loop:

```bash
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./bin/shipguard ios report-quality --reports /tmp/shipguard-value-gauntlet --out /tmp/shipguard-value-quality --shareable
```

Proof should show that ui-polish has concrete commands, validation language, docs linkage, and test coverage; otherwise upgrade the skill before treating it as mature.

## Rules

- Match the existing app style before inventing a new visual pattern.
- Keep text short enough for localization and Dynamic Type.
- Avoid layout changes that hide important state, actions, or permission truth.
- Add or update UI tests when the polish changes interaction paths.
- Validate the exact surface touched, not a broad unrelated lane.

## Review Checklist

- Text fits at compact widths and Dynamic Type.
- Buttons have stable identifiers and accessible labels.
- Pinned headers do not show scrolling content underneath.
- Locale and RTL behavior are intentional.
- UI tests target the user-visible behavior, not fragile coordinates.

## Completion Evidence

Return files changed, surface affected, accessibility or localization risk, screenshot or UI-test proof when available, and the remaining manual check if visual proof is not possible locally.
