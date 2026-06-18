# Use In Your Repo

This page shows the minimal setup for another repository.

## 1. Initialize

From a cloned repository:

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard init web ../my-web-app
./bin/shipguard init backend ../my-service
./bin/shipguard init cli ../my-tool
```

From a release tarball:

```bash
tar -xzf shipguard-v3.111.0.tar.gz
cd shipguard-v3.111.0
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" init ios ../my-ios-app
"$HOME/.local/bin/shipguard" init web ../my-web-app
"$HOME/.local/bin/shipguard" init backend ../my-service
"$HOME/.local/bin/shipguard" init cli ../my-tool
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
- rules for when agent run summaries need `shipguard autopsy`

## 3. Check Installation

```bash
./bin/shipguard doctor ../my-ios-app
./bin/shipguard doctor web ../my-web-app
./bin/shipguard doctor backend ../my-service
./bin/shipguard doctor cli ../my-tool
```

## 4. Add CI

In a repo that contains this workflow bundle, use:

```yaml
- name: Validate Codex workflow bundle
  uses: jlekerli-source/ShipGuard/actions/validate@v1.0.0
```

For a product repo that only copied starter files, keep using `doctor` from a checkout of this toolkit until that repo has its own validator.

## 5. Optional Codex Plugin

Install the plugin only when you want Codex itself to start with ShipGuard iOS guidance. The CLI remains the source of repeatable proof commands.

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

After install or refresh, start a new Codex thread. Updating GitHub or the local checkout does not update skill metadata inside an already-running thread.

## 6. First Codex Task

Use this low-risk pattern:

```text
Read AGENTS.md and inspect this issue without editing files.

Return expected behavior, current failure, owner files, risks, validation route, and open questions.
```

Only move to implementation after the inspection output is narrow and testable.

After implementation, ask the agent for a scored run summary and run an autopsy before treating the output as merge evidence:

```bash
shipguard autopsy --run run.md --diff change.patch --tests test.log --task task.md --out autopsy
```
