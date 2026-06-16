# Review Comment Example

Generate a dangerous autopsy report, then create a PR-ready comment:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out /tmp/autopsy-dangerous

./bin/codex-maintainer review-comment \
  --report /tmp/autopsy-dangerous/report.json \
  --out /tmp/review/comment.md \
  --badge /tmp/review/badge.json \
  --artifact-dir /tmp/review \
  --mode warn
```

Expected comment status:

```text
blocked
```

Expected badge:

```json
{
  "schemaVersion": 1,
  "label": "codex maintainer",
  "message": "blocked 1/12",
  "color": "red"
}
```

In `--mode fail`, the same dangerous report exits non-zero.
