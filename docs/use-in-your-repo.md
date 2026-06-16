# Use In Your Repo

This page shows the minimal setup for another repository.

## 1. Initialize

From this repository:

```bash
./bin/codex-maintainer init ios ../my-ios-app
```

This writes:

- `AGENTS.md`
- `PLANS.md`
- `SUBAGENTS.md`
- `SCORECARD.md`
- `.agents/skills/`

Existing files are skipped unless you pass `--force`.

## 2. Customize

Edit `../my-ios-app/AGENTS.md` first.

Replace placeholders, then add:

- the app's actual build and test commands
- protected high-risk files
- release handoff rules
- permission, persistence, payment, localization, and lifecycle risks

## 3. Check Installation

```bash
./bin/codex-maintainer doctor ../my-ios-app
```

## 4. Add CI

In a repo that contains this workflow bundle, use:

```yaml
- name: Validate Codex workflow bundle
  uses: jlekerli-source/ringly-codex-workflows/actions/validate@v0.4.0
```

For a product repo that only copied starter files, keep using `doctor` from a checkout of this toolkit until that repo has its own validator.

## 5. First Codex Task

Use this low-risk pattern:

```text
Read AGENTS.md and inspect this issue without editing files.

Return expected behavior, current failure, owner files, risks, validation route, and open questions.
```

Only move to implementation after the inspection output is narrow and testable.
