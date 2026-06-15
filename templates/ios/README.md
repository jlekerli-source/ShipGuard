# iOS Codex Workflow Starter

Copy these files into an iOS app repo when you want Codex to work inside explicit product, risk, and validation rules.

## Files

- `AGENTS.md`: root operating instructions for Codex.

## Adaptation Checklist

1. Replace `[APP_NAME]`, `[XCODE_PROJECT]`, and placeholder command names.
2. List high-risk areas: notifications, alarms, widgets, subscriptions, persistence, app lifecycle, networking, analytics, or release gates.
3. Add the smallest real validation commands your repo supports.
4. Add protected files only when those files genuinely require extra care.
5. Keep the completion checklist strict: no validation, no proof claim.

## Recommended Next Copies

After adapting `AGENTS.md`, copy from the root of this repository:

- `PLANS.md`
- `SUBAGENTS.md`
- `.agents/skills/`
- `SCORECARD.md`
