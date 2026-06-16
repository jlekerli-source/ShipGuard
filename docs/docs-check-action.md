# Docs Check Action

`actions/docs-check` runs `codex-maintainer docs-check` in GitHub Actions, uploads the generated report directory, and exposes the report paths as action outputs.

Use it on pull requests or release-prep branches where docs drift is easy to miss:

```yaml
- name: Check docs links
  uses: jlekerli-source/ringly-codex-workflows/actions/docs-check@v3.39.0
  with:
    path: .
    mode: fail
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | File or directory to scan for Markdown links. |
| `out` | `artifacts/codex-maintainer-docs-check` | Output directory for `docs-check.json` and `docs-check.md`. |
| `upload-artifact` | `true` | Upload the report directory with `actions/upload-artifact`. |
| `artifact-name` | `codex-maintainer-docs-check` | Uploaded artifact name. |
| `mode` | `fail` | Use `fail` to fail the job on broken links or `warn` to emit warnings only. |

## Outputs

| Output | Description |
| --- | --- |
| `status` | `pass`, `blocked`, or `failed`. |
| `report-json` | Path to `docs-check.json`. |
| `report-md` | Path to `docs-check.md`. |

The action ignores external URLs and in-page anchors because `docs-check` is designed to catch local repo drift, missing docs pages, stale fixture references, and deleted report paths.
