# Autopsy In GitHub Actions

The toolkit includes a manual workflow that turns an autopsy fixture into a downloadable GitHub Actions artifact.

Run it from the Actions tab:

```text
Generate autopsy artifact
```

Default input:

```text
fixture = good-run
```

The workflow runs:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out artifacts/autopsy-good-run
```

It uploads the output directory with:

```yaml
uses: actions/upload-artifact@v4
```

The artifact contains:

- `report.md`
- `report.json`

Use this workflow as the minimal copy/paste shape for product repos that want evidence artifacts without enabling pull request comments yet.
