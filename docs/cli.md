# CLI

`bin/codex-maintainer` is a dependency-light helper for validating and reusing this workflow kit.

## Validate

Run this from a checkout of this repository:

```bash
./bin/codex-maintainer validate
```

You can also pass a path to another checkout of this workflow bundle:

```bash
./bin/codex-maintainer validate ../ringly-codex-workflows
```

Validation checks required files, skill metadata, shell syntax, executable scripts, local markdown links, YAML files, and whitespace.

## Version

Print the toolkit version:

```bash
./bin/codex-maintainer version
```

The command reads `VERSION`, which is also used by the release packaging script.

## Init

Copy the iOS starter workflow into another project:

```bash
./bin/codex-maintainer init ios ../my-ios-app
```

The command writes:

- `AGENTS.md`
- `PLANS.md`
- `SUBAGENTS.md`
- `SCORECARD.md`
- `.agents/skills/`

Existing files are skipped. Use `--force` to overwrite generated workflow files:

```bash
./bin/codex-maintainer init ios ../my-ios-app --force
```

## Doctor

Check whether a target repo has the starter workflow files:

```bash
./bin/codex-maintainer doctor ../my-ios-app
```

## Score

Score a Codex run markdown file:

```bash
./bin/codex-maintainer score examples/scored-run.md
```

The score file must include these categories:

- Scope control
- Owner-file accuracy
- Risk awareness
- Validation quality
- Handoff honesty
- Regression awareness

Each category should include a value from `0` to `2`.

## Autopsy

Generate Markdown and JSON evidence reports for an AI coding run:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

The command writes:

- `report.md`
- `report.json`

It checks the run score, validation claims, test evidence, diff size, high-assurance claims, and protected-area touches. High-severity findings produce a `do not merge until high-risk findings are resolved` verdict.

See `autopsy.md` for the full guide.

## Arena

Run a fixture pack through Autopsy and aggregate the results:

```bash
./bin/codex-maintainer arena run \
  --fixture fixtures/arena \
  --out /tmp/arena
```

The command writes aggregate `results.json`, a readable `index.md`, and per-case autopsy reports under `runs/<case-id>/`.

See `arena.md` for the fixture format and metrics.

## Install From Release Tarball

Download and extract a release package:

```bash
tar -xzf codex-maintainer-v0.6.0.tar.gz
cd codex-maintainer-v0.6.0
PREFIX="$HOME/.local" ./scripts/install.sh
```

The installer copies toolkit files into `${PREFIX:-/usr/local}/lib/codex-maintainer` and writes a `codex-maintainer` wrapper into `${PREFIX:-/usr/local}/bin`.

## Package Contents

Release packages include the CLI, scripts, skills, templates, examples, demo fixtures, docs, scorecard, planning templates, and license. They exclude `.git`, `dist`, generated caches, and local machine paths.
