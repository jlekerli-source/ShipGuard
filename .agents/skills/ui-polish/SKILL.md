---
name: ui-polish
description: Ringly SwiftUI product-polish workflow. Use when a task touches visual hierarchy, copy, interaction states, Dynamic Type, compact layouts, localization/RTL, onboarding, settings, alarm authoring, premium screens, or UI test polish.
---

# UI Polish

Use this skill for narrow UI improvements that preserve alarm trust.

## Steps

1. Read `BEST_PRACTICES.md`, `docs/ui-ux-principles.md`, `docs/change-review-matrix.md`, and `docs/validation-commands.md`.
2. Define the user job and remove unnecessary UI before adding more chrome.
3. Keep the first screen usable. Do not replace real app surfaces with explanatory landing-page copy.
4. Check empty, loading, denied, degraded, failed, cancelled, downgrade, offline, compact, Dynamic Type, and localized states when the surface can enter them.
5. Keep alarm and premium copy truthful. Premium must never imply better alarm delivery.
6. Prefer existing components, themes, symbols, accessibility identifiers, and localization helpers.
7. Validate with the narrow UI lane:

```bash
./scripts/run_onboarding_validation.sh
./scripts/run_alarm_ui_batches.sh alarm-home-smoke
./scripts/run_alarm_ui_batches.sh premium-surfaces
./scripts/run_alarm_ui_batches.sh alarm-authoring-first-tap
python3 ./scripts/check_localization_coverage.py
```

8. If visual proof is missing, say so. Screenshots and simulator proof do not replace physical alarm proof.

## Review Checklist

- Text fits at compact widths and Dynamic Type.
- Buttons have stable identifiers and accessible labels.
- Pinned headers do not show scrolling content underneath.
- Locale and RTL behavior are intentional.
- UI tests target the user-visible behavior, not fragile coordinates.
