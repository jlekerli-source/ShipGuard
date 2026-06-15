# Codex Run Scorecard

Use this scorecard after a Codex run to decide whether the result is usable maintainer work or just plausible output.

Score each category from 0 to 2.

- `0`: missing or actively risky.
- `1`: present but incomplete.
- `2`: clear, specific, and useful.

## Categories

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Scope control | Edited unrelated areas or changed the product goal. | Mostly scoped, but included unclear extras. | Stayed inside the requested behavior and named out-of-scope work. |
| Owner-file accuracy | Worked in the wrong files or guessed architecture. | Found likely files but missed one important owner. | Read routed context and touched the narrowest owner files. |
| Risk awareness | Missed alarm, permission, StoreKit, persistence, or release risk. | Named risk but did not route proof well. | Matched risk to the right validation and rollback path. |
| Validation quality | Claimed success without proof or treated a blocker as a pass. | Ran a weak or broad check. | Ran the smallest proof command and reported exact status. |
| Handoff honesty | Hid uncertainty or wrote vague next steps. | Mentioned uncertainty without concrete action. | Stated blockers, evidence, and the next exact operator action. |
| Regression awareness | Ignored adjacent user flows. | Mentioned adjacent flows generally. | Checked specific regressions tied to the changed behavior. |

## Interpreting The Score

- `10-12`: usable maintainer-quality run.
- `7-9`: probably useful, but review the weak categories before merging.
- `4-6`: keep the analysis, but ask for a narrower repair pass.
- `0-3`: discard as implementation evidence.

## Example: Weak Run

Task: fix a quick-alarm empty-state UI test.

- Scope control: `1`, because the run adjusted multiple unrelated views.
- Owner-file accuracy: `1`, because it found the UI test but missed the accessibility identifier owner.
- Risk awareness: `0`, because it did not mention alarm-authoring risk.
- Validation quality: `0`, because it claimed success without running the UI lane.
- Handoff honesty: `1`, because it said tests were not run but gave no next action.
- Regression awareness: `0`, because it did not check compact layout or Dynamic Type.

Total: `3`. Do not merge from this run.

## Example: Strong Run

Task: fix a quick-alarm empty-state UI test.

- Scope control: `2`, because only the test lookup and missing accessibility identifier changed.
- Owner-file accuracy: `2`, because the run identified the empty-state view and UI test owner.
- Risk awareness: `2`, because it named alarm-authoring first-tap risk.
- Validation quality: `2`, because it ran the focused UI lane and reported command status.
- Handoff honesty: `2`, because it listed the exact simulator and residual visual check.
- Regression awareness: `1`, because it checked the empty state but not full Dynamic Type.

Total: `11`. Review normally.
