# Release Consume Action

`actions/release-consume` verifies published release proof assets in GitHub Actions. It can download a release with `gh release download`, run `codex-maintainer release-consume verify`, and upload the consumer proof bundle as a workflow artifact.

## Usage

```yaml
name: Verify Codex maintainer release proof

on:
  workflow_dispatch:
    inputs:
      release-tag:
        description: Release tag to verify.
        required: true
        default: v3.25.0

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Verify published proof assets
        uses: jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.25.0
        with:
          repo: jlekerli-source/ringly-codex-workflows
          release-tag: ${{ inputs.release-tag }}
          mode: fail
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `release-tag` | required | Release tag to verify, such as `v3.25.0`. |
| `repo` | current repository | Repository containing release assets. |
| `version` | tag without leading `v` | Expected release version. |
| `assets-dir` | `artifacts/codex-maintainer-release-assets` | Directory for downloaded or pre-existing assets. |
| `out` | `artifacts/codex-maintainer-release-consume` | Directory for consumer proof output. |
| `download-assets` | `true` | Download assets with `gh release download`; set `false` to verify existing files. |
| `upload-artifact` | `true` | Upload the consumer proof directory with `actions/upload-artifact`. |
| `artifact-name` | `codex-maintainer-release-consume` | Uploaded artifact name. |
| `mode` | `fail` | `fail` fails invalid proof; `warn` emits an annotation and continues. |

## Outputs

- `status`
- `consumer-report`
- `consumer-report-md`
- `asset-digests`
- `asset-digests-md`
- `sha256`
- `attestation-badge`

The uploaded artifact contains `consumer-report.json`, `consumer-report.md`, `asset-digests.json`, `asset-digests.md`, `sha256.txt`, replay proof, and regenerated attestation proof.

To turn this proof into a static HTML artifact, run `actions/release-evidence` after this action. See `release-evidence-action.md`.
