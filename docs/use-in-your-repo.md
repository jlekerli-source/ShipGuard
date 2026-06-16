# Use In Your Repo

This page shows the minimal setup for another repository.

## 1. Initialize

From a cloned repository:

```bash
./bin/codex-maintainer init ios ../my-ios-app      # iOS app
./bin/codex-maintainer init web ../my-web-app      # web app
./bin/codex-maintainer init backend ../my-service  # backend service
./bin/codex-maintainer init cli ../my-tool         # CLI tool
```

Choose one profile. Do not run all four in the same target repository.

From a release tarball:

```bash
tar -xzf codex-maintainer-v3.39.0.tar.gz
cd codex-maintainer-v3.39.0
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" init ios ../my-ios-app
"$HOME/.local/bin/codex-maintainer" init web ../my-web-app
"$HOME/.local/bin/codex-maintainer" init backend ../my-service
"$HOME/.local/bin/codex-maintainer" init cli ../my-tool
```

Again, choose the one profile that matches the target repository.

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

For iOS apps, run the Shipguard inventory before the first risky Codex task:

```bash
./bin/codex-maintainer ios inventory --path ../my-ios-app --out /tmp/ios-shipguard-inventory
```

To use the repo-local Codex plugin from this checkout:

```bash
codex plugin marketplace add .agents/plugins
codex plugin add ios-shipguard@ringly-codex-workflows
```

## 4. Add CI

In a repo that contains this workflow bundle, use:

```yaml
- name: Validate Codex workflow bundle
  uses: jlekerli-source/ringly-codex-workflows/actions/validate@v3.39.0
```

For a product repo that only copied starter files, keep using `doctor` from a checkout of this toolkit until that repo has its own validator.

## 5. Audit The First Run

Before adopting release proof, prove the core loop with one small run:

```bash
codex-maintainer autopsy \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --task task.md \
  --out autopsy
```

Then gate that same evidence in warn mode:

```bash
codex-maintainer ci-gate \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --task task.md \
  --out codex-gate \
  --mode warn
```

Move to `--mode fail` only after maintainers agree the report is correctly classifying useful and risky runs.

## 6. First Codex Task

Use this low-risk pattern:

```text
Read AGENTS.md and inspect this issue without editing files.

Return expected behavior, current failure, owner files, risks, validation route, and open questions.
```

Only move to implementation after the inspection output is narrow and testable.
