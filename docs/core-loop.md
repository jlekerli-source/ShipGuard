# Core Loop

Use this path before adopting release proof, transcript publishing, Check Run posting, or static evidence sites.

## 1. Validate The Toolkit

```bash
./bin/codex-maintainer validate
```

This proves the local checkout has the required files, valid skill metadata, parseable shell scripts, parseable workflow YAML when Ruby is available, clean Markdown local links, and no `git diff --check` failures.

## 2. Start From A Task Contract

Use `CODEX_TASK_TEMPLATE.md` before a non-trivial agent run. The task should name:

- requested behavior
- owner files or search area
- risk lane
- validation command
- known blockers

The first useful agent output is often an inspection, not a patch.

```text
Read AGENTS.md and inspect this issue without editing files.

Return expected behavior, current failure, owner files, risks, validation route, and open questions.
```

## 3. Audit One Run

After an agent run, save the run summary, patch, task, and validation log. Then run:

```bash
./bin/codex-maintainer autopsy \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --task task.md \
  --out /tmp/codex-autopsy
```

The output is a Markdown and JSON report that scores scope control, owner-file accuracy, risk awareness, validation quality, handoff honesty, and regression awareness.

## 4. Gate It In CI

Use `ci-gate` when the autopsy result should produce CI artifacts or fail a pull request.

```bash
./bin/codex-maintainer ci-gate \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --task task.md \
  --out /tmp/codex-gate \
  --mode fail
```

Use `--mode warn` while introducing the workflow to an existing repository.

## 5. Compare Fixtures When Policy Changes

Run the public fixture pack when changing scoring logic, policy behavior, review comments, or CI gate output.

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/codex-arena
```

The arena is deterministic. It scores saved maintainer-run artifacts; it does not claim live model quality.

## What To Ignore At First

These integrations are useful after the core loop proves value in one repository:

- release proof and release evidence
- release diff and downstream proof consumption
- transcript redaction and corpus publishing
- SARIF export
- GitHub Check Run posting
- static evidence sites

Start with one audited run. Add the advanced proof chain only when the maintainer workflow needs it.

