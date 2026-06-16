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
