# Release Evidence Negative Index Action

`actions/release-evidence-negative-index` runs the checked-in release evidence negative fixtures in GitHub Actions and uploads a compact report proving each intentionally broken fixture blocks on the expected check.

## Usage

```yaml
name: Audit release evidence negative fixtures

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  negative-evidence:
    runs-on: ubuntu-latest
    steps:
      - name: Audit release evidence negative fixtures
        uses: jlekerli-source/ShipGuard/actions/release-evidence-negative-index@v3.108.0
        with:
          mode: fail
```

The default `fixture: bundled` uses the fixture manifest shipped inside this action. To audit a custom fixture pack from your repository, check out your repo first and pass `fixture: path/to/negative-fixtures`.

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `fixture` | `bundled` | Negative fixture directory, or `bundled` to use the action's checked-in fixtures. |
| `out` | `artifacts/shipguard-release-evidence-negative-index` | Directory for generated reports. |
| `title` | `ShipGuard Release Evidence Negative Fixture Index` | Title for the generated report. |
| `upload-artifact` | `true` | Upload the report directory with `actions/upload-artifact`. |
| `artifact-name` | `shipguard-release-evidence-negative-index` | Uploaded artifact name. |
| `mode` | `fail` | `fail` fails the job when expected blocked checks are missing; `warn` emits an annotation and continues. |

## Outputs

- `status`
- `index-html`
- `report-json`
- `report-md`
- `badge`

The uploaded artifact contains `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, and per-case verifier outputs under `runs/<case>/`.
