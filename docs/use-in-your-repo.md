# Use In Your Repo

This page shows the minimal setup for another repository.

## 1. Initialize

From a cloned repository:

```bash
./bin/codex-maintainer init ios ../my-ios-app
./bin/codex-maintainer init web ../my-web-app
./bin/codex-maintainer init backend ../my-service
./bin/codex-maintainer init cli ../my-tool
```

From a release tarball:

```bash
tar -xzf codex-maintainer-v3.9.0.tar.gz
cd codex-maintainer-v3.9.0
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" init ios ../my-ios-app
"$HOME/.local/bin/codex-maintainer" init web ../my-web-app
"$HOME/.local/bin/codex-maintainer" init backend ../my-service
"$HOME/.local/bin/codex-maintainer" init cli ../my-tool
```

This writes:

- `AGENTS.md`
- `PLANS.md`
- `SUBAGENTS.md`
- `SCORECARD.md`
- `.agents/skills/`

Existing files are skipped unless you pass `--force`.

## 2. Customize

Edit the generated `AGENTS.md` first.

Replace placeholders, then add:

- the app's actual build and test commands
- protected high-risk files
- release handoff rules
- permission, persistence, payment, localization, and lifecycle risks
- rules for when agent run summaries need `codex-maintainer autopsy`

## 3. Check Installation

```bash
./bin/codex-maintainer doctor ../my-ios-app
./bin/codex-maintainer doctor web ../my-web-app
./bin/codex-maintainer doctor backend ../my-service
./bin/codex-maintainer doctor cli ../my-tool
```

## 4. Add CI

In a repo that contains this workflow bundle, use:

```yaml
- name: Validate Codex workflow bundle
  uses: jlekerli-source/ringly-codex-workflows/actions/validate@v1.0.0
```

For a product repo that only copied starter files, keep using `doctor` from a checkout of this toolkit until that repo has its own validator.

## 5. First Codex Task

Use this low-risk pattern:

```text
Read AGENTS.md and inspect this issue without editing files.

Return expected behavior, current failure, owner files, risks, validation route, and open questions.
```

Only move to implementation after the inspection output is narrow and testable.

After implementation, ask the agent for a scored run summary and run an autopsy before treating the output as merge evidence:

```bash
codex-maintainer autopsy --run run.md --diff change.patch --tests test.log --task task.md --out autopsy
```
