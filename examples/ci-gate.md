# CI Gate Example

Passing gate:

```bash
./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --policy templates/policy/default.conf \
  --out /tmp/good-gate \
  --mode warn
```

Expected:

```json
{
  "status": "pass",
  "score": 11,
  "sarif": "sarif/results.sarif",
  "summary": "summary.md"
}
```

Blocked gate:

```bash
./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --policy templates/policy/default.conf \
  --out /tmp/dangerous-gate \
  --mode warn
```

Use `--mode fail` after the team agrees that blocked reports should fail CI.
