# Agent Autopsy Example

This example shows the public fixture path for a dangerous run.

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out /tmp/autopsy-dangerous
```

Expected summary:

```text
Verdict: do not merge until high-risk findings are resolved
Total score: 1/12
Changed files from diff: 4
```

Expected finding IDs:

```text
no_test_log
validation_claim_without_tests
high_assurance_claim
scope_creep_signal
protected_area_touch
```

The same command also writes `report.json`, which can be consumed by future CI gates, pull request comments, or dashboard tooling.

For a clean contrast, run:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

The good fixture should produce `11/12`, `usable maintainer-quality run`, and no findings.
