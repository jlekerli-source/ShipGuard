# Arena Compare Action

`actions/arena-compare` runs `shipguard arena compare` in GitHub Actions and uploads the comparison output as an artifact.

Use it when a workflow has already produced two Arena `results.json` files and you want CI-visible proof that a benchmark fixture or scoring change improved, stayed unchanged, or regressed.

## Example

```yaml
- name: Compare Arena results
  uses: jlekerli-source/ShipGuard/actions/arena-compare@v3.104.0
  with:
    left-results: artifacts/arena-old/results.json
    right-results: artifacts/arena-current/results.json
    mode: fail
```

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `left-results` | yes | | Older Arena `results.json`. |
| `right-results` | yes | | Newer Arena `results.json`. |
| `out` | no | `artifacts/shipguard-arena-compare` | Output directory. |
| `title` | no | `ShipGuard Arena Compare` | Report title. |
| `upload-artifact` | no | `true` | Upload the output directory. |
| `artifact-name` | no | `shipguard-arena-compare` | Uploaded artifact name. |
| `mode` | no | `warn` | Use `fail` to fail the job when status is `regressed` or comparison generation fails. |

## Outputs

| Output | Description |
| --- | --- |
| `status` | `improved`, `unchanged`, `regressed`, or `failed`. |
| `arena-compare` | Path to `arena-compare.json`. |
| `arena-compare-md` | Path to `arena-compare.md`. |

The action does not run Arena itself. Keep the run step separate so each workflow can decide which fixture pack, branch, artifact, or external benchmark corpus is being compared.
