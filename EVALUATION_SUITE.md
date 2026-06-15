# Mini Evaluation Suite

These are benchmark candidates for future Codex runs. Do not fix them as part of this workflow bundle.

## 1. Release localization exposure is wider than the release-clean language set

- Expected behavior: only release-clean locales should be selectable and exposed in release metadata until future locales are translated and visually checked.
- Current failure: the language-option source, localization exposure config, strip script, and release tests can drift so unfinished catalog locales become selectable before cleanup.
- Why it is a good benchmark: it requires aligning source, tests, build script, and release docs without breaking catalog coverage.

## 2. Today weather fallback can show fake weather on DEBUG device builds

- Expected behavior: simulator fallback weather should be limited to simulator-only or explicitly test-only failure paths.
- Current failure: a broad debug fallback can show hard-coded sunny weather on a real debug device when WeatherKit fails, instead of an honest unavailable state.
- Why it is a good benchmark: it is small, source-observable, and forces Codex to preserve simulator convenience while protecting device truth.

## 3. Today weather foreground-refresh throttle is declared but unused

- Expected behavior: foreground-triggered weather refreshes should respect a documented minimum interval to avoid rapid repeated WeatherKit requests.
- Current failure: a throttle property can exist without being read or updated by the refresh path.
- Why it is a good benchmark: it is a contained state-management fix with clear unit-test shape and no alarm-runtime risk.

## 4. Sleep Plan reminder reconciliation removes old reminders before replacement succeeds

- Expected behavior: existing reminder notifications should not be deleted until replacement scheduling succeeds, or failures should restore a safe previous state.
- Current failure: a reconcile path can remove pending reminders before adding replacements. If all adds fail, the user sees a failed result and may also lose previously scheduled reminders.
- Why it is a good benchmark: it tests reliability thinking around side effects, partial failure, and user trust.

## 5. Quick-alarm empty-state UI lookup is intermittently flaky

- Expected behavior: an empty-state quick alarm test should find and tap the Power Nap action deterministically from a clean state.
- Current failure: short waits, fallback label lookup, and scrolling around a dynamic empty-state surface can make the test intermittently miss a real button.
- Why it is a good benchmark: it forces Codex to distinguish product flake from infrastructure, improve accessibility/test determinism, and validate with a focused UI lane.
