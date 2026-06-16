# PR Review Bot Mode

PR Review Bot Mode turns an autopsy `report.json` into:

- a PR-ready Markdown comment
- a Shields-compatible badge JSON file
- an optional artifact bundle containing `report.json`, `report.md`, `comment.md`, and `badge.json`

## Command

```bash
./bin/codex-maintainer review-comment \
  --report /tmp/autopsy/report.json \
  --out /tmp/review/comment.md \
  --badge /tmp/review/badge.json \
  --artifact-dir /tmp/review \
  --mode warn
```

Defaults:

- `--mode warn`
- `--warn-below 10`
- `--fail-below 7`

`warn` mode always exits zero. `fail` mode exits non-zero when the report is blocked by high-risk findings or a score below the fail threshold.

## Reusable Action

```yaml
- name: Generate Codex maintainer review comment
  uses: jlekerli-source/ringly-codex-workflows/actions/review-comment@v0.8.0
  with:
    report: autopsy/report.json
    mode: warn
```

To post the generated comment on a pull request:

```yaml
permissions:
  contents: read
  pull-requests: write

steps:
  - uses: actions/checkout@v5
  - name: Generate autopsy report
    run: ./bin/codex-maintainer autopsy --run run.md --diff change.patch --tests test.log --out autopsy
  - name: Generate review comment
    uses: jlekerli-source/ringly-codex-workflows/actions/review-comment@v0.8.0
    with:
      report: autopsy/report.json
      mode: warn
  - name: Comment on PR
    env:
      GH_TOKEN: ${{ github.token }}
    run: gh pr comment "${{ github.event.pull_request.number }}" --body-file artifacts/codex-maintainer-review/comment.md
```

Use `mode: fail` only after the project agrees that blocked autopsy reports should fail CI.
