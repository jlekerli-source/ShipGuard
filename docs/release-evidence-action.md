# Release Evidence Action

`actions/release-evidence` turns verified release proof reports into a static evidence artifact in GitHub Actions. It expects the output from `actions/release-consume` and can include the output from `actions/release-diff`.

## Usage

```yaml
name: Export Codex maintainer release evidence

on:
  workflow_dispatch:
    inputs:
      release-tag:
        description: Release tag to verify.
        required: true
        default: v3.19.0
      previous-tag:
        description: Previous release tag for diff proof.
        required: true
        default: v3.18.0

permissions:
  contents: read

jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - name: Verify published proof assets
        uses: jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.19.0
        with:
          repo: jlekerli-source/ringly-codex-workflows
          release-tag: ${{ inputs.release-tag }}
          mode: fail

      - name: Compare release proof assets
        uses: jlekerli-source/ringly-codex-workflows/actions/release-diff@v3.19.0
        with:
          repo: jlekerli-source/ringly-codex-workflows
          left-tag: ${{ inputs.previous-tag }}
          right-tag: ${{ inputs.release-tag }}
          mode: fail

      - name: Export release evidence
        uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.19.0
        with:
          title: Codex Maintainer Release Evidence
          include-diff: auto
          build-index: true
          mode: fail
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `consume-dir` | `artifacts/codex-maintainer-release-consume` | Directory containing `consumer-report.json` and `asset-digests.json`. |
| `diff-dir` | `artifacts/codex-maintainer-release-diff/report` | Directory containing `release-diff.json`. |
| `out` | `artifacts/codex-maintainer-release-evidence` | Root directory for generated evidence artifacts. |
| `title` | `Codex Maintainer Release Evidence` | Title for the generated evidence site. |
| `include-diff` | `auto` | `auto` includes diff proof when present; `true` requires it; `false` skips it. |
| `build-index` | `false` | Set `true` to build an evidence index containing the generated site. |
| `index-title` | `Codex Maintainer Release Evidence Index` | Title for the generated evidence index. |
| `extra-index-sites` | empty | Newline-separated evidence site directories to include after the generated site. |
| `upload-artifact` | `true` | Upload the evidence directory with `actions/upload-artifact`. |
| `artifact-name` | `codex-maintainer-release-evidence` | Uploaded artifact name. |
| `mode` | `fail` | `fail` fails invalid evidence; `warn` emits an annotation and continues. |

## Outputs

- `status`
- `site`
- `evidence-json`
- `site-readme`
- `index`
- `evidence-index-json`

The uploaded artifact contains `site/index.html`, `site/evidence.json`, copied source reports, and `index/evidence-index.json` when `build-index` is enabled.
