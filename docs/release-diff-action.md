# Release Diff Action

`actions/release-diff` compares two published release proof asset sets in GitHub Actions. It can download both releases with `gh release download`, run `shipguard release-diff compare`, and upload `release-diff.json` plus `release-diff.md`.

## Usage

```yaml
name: Compare ShipGuard releases

on:
  workflow_dispatch:
    inputs:
      left-tag:
        description: Older release tag.
        required: true
        default: v0.0.0
      right-tag:
        description: Newer release tag.
        required: true
        default: v3.107.0

permissions:
  contents: read

jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - name: Compare release proof assets
        uses: jlekerli-source/ShipGuard/actions/release-diff@v3.107.0
        with:
          repo: jlekerli-source/ShipGuard
          left-tag: ${{ inputs.left-tag }}
          right-tag: ${{ inputs.right-tag }}
          mode: fail
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `left-tag` | required | Older release tag to compare. |
| `right-tag` | required | Newer release tag to compare. |
| `repo` | current repository | Repository containing release assets. |
| `left-assets-dir` | `artifacts/shipguard-release-diff/left` | Directory for older release assets. |
| `right-assets-dir` | `artifacts/shipguard-release-diff/right` | Directory for newer release assets. |
| `out` | `artifacts/shipguard-release-diff/report` | Directory for diff reports. |
| `download-assets` | `true` | Download both releases with `gh release download`; set `false` to compare existing files. |
| `upload-artifact` | `true` | Upload the diff report directory with `actions/upload-artifact`. |
| `artifact-name` | `shipguard-release-diff` | Uploaded artifact name. |
| `mode` | `fail` | `fail` fails invalid diff proof; `warn` emits an annotation and continues. |

## Outputs

- `status`
- `release-diff`
- `release-diff-md`

To include this diff in a static HTML evidence artifact, run `actions/release-evidence` after this action. See `release-evidence-action.md`.
