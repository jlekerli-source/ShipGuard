# Release Evidence Action

`actions/release-evidence` turns release proof into a static evidence artifact in GitHub Actions. It can export from existing `actions/release-consume` and `actions/release-diff` reports, or run the one-command evidence bundle path from downloaded release assets.

## Report Usage

```yaml
name: Export ShipGuard release evidence

on:
  workflow_dispatch:
    inputs:
      release-tag:
        description: Release tag to verify.
        required: true
        default: v3.108.0
      previous-tag:
        description: Previous release tag for diff proof.
        required: true
        default: v3.22.0

permissions:
  contents: read

jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - name: Verify published proof assets
        uses: jlekerli-source/ShipGuard/actions/release-consume@v3.108.0
        with:
          repo: jlekerli-source/ShipGuard
          release-tag: ${{ inputs.release-tag }}
          mode: fail

      - name: Compare release proof assets
        uses: jlekerli-source/ShipGuard/actions/release-diff@v3.108.0
        with:
          repo: jlekerli-source/ShipGuard
          left-tag: ${{ inputs.previous-tag }}
          right-tag: ${{ inputs.release-tag }}
          mode: fail

      - name: Export release evidence
        uses: jlekerli-source/ShipGuard/actions/release-evidence@v3.108.0
        with:
          title: ShipGuard Release Evidence
          include-diff: auto
          build-index: true
          mode: fail
```

## Bundle Usage

```yaml
name: Build ShipGuard release evidence bundle

on:
  workflow_dispatch:
    inputs:
      release-tag:
        description: Release tag to verify.
        required: true
        default: v3.108.0
      previous-tag:
        description: Previous release tag for diff proof.
        required: true
        default: v3.22.0

permissions:
  contents: read

jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - name: Build release evidence bundle
        uses: jlekerli-source/ShipGuard/actions/release-evidence@v3.108.0
        with:
          run: bundle
          repo: jlekerli-source/ShipGuard
          release-tag: ${{ inputs.release-tag }}
          previous-tag: ${{ inputs.previous-tag }}
          download-assets: true
          title: ShipGuard Release Evidence
          index-title: ShipGuard Release Evidence
          mode: fail
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `run` | `reports` | `reports` exports from existing consume/diff reports; `bundle` runs `release-evidence bundle`. |
| `repo` | current repository | Repository containing release assets when `download-assets` is `true`. |
| `release-tag` | empty | Release tag to download for `run=bundle` when `download-assets` is `true`. |
| `previous-tag` | empty | Previous release tag to download for bundle diff proof when `download-assets` is `true`. |
| `download-assets` | `false` | Set `true` in bundle mode to download assets with `gh release download`. |
| `consume-dir` | `artifacts/shipguard-release-consume` | Directory containing `consumer-report.json` and `asset-digests.json`. |
| `diff-dir` | `artifacts/shipguard-release-diff/report` | Directory containing `release-diff.json`. |
| `out` | `artifacts/shipguard-release-evidence` | Root directory for generated evidence artifacts. |
| `assets-dir` | `artifacts/shipguard-release-assets` | Release asset directory for `run=bundle`. |
| `left-assets-dir` | empty | Previous release asset directory for `run=bundle` diff proof. |
| `version` | empty | Expected release version for `run=bundle`; omit to let `release-consume` infer it. |
| `title` | `ShipGuard Release Evidence` | Title for the generated evidence site. |
| `include-diff` | `auto` | `auto` includes diff proof when present; `true` requires it; `false` skips it. |
| `build-index` | `false` | Set `true` to build an evidence index containing the generated site. |
| `index-title` | `ShipGuard Release Evidence Index` | Title for the generated evidence index. |
| `extra-index-sites` | empty | Newline-separated evidence site directories to include after the generated site. |
| `upload-artifact` | `true` | Upload the evidence directory with `actions/upload-artifact`. |
| `artifact-name` | `shipguard-release-evidence` | Uploaded artifact name. |
| `mode` | `fail` | `fail` fails invalid evidence; `warn` emits an annotation and continues. |

## Outputs

- `status`
- `site`
- `evidence-json`
- `site-readme`
- `index`
- `evidence-index-json`
- `bundle`

In report mode, the uploaded artifact contains `site/index.html`, `site/evidence.json`, copied source reports, and `index/evidence-index.json` when `build-index` is enabled. In bundle mode, it contains `consumer-proof/`, optional `release-diff/`, `site/`, `index/`, `bundle.json`, and `README.md`.

## Consumption Proof

To prove the uploaded artifact can be consumed outside the producer job, run `actions/release-evidence-verify` in a later job with artifact download enabled:

```yaml
- name: Verify release evidence artifact
  uses: jlekerli-source/ShipGuard/actions/release-evidence-verify@v3.108.0
  with:
    download-artifact: true
    source-artifact-name: shipguard-release-evidence
    dir: artifacts/shipguard-release-evidence
    require-diff: true
    require-index: true
    mode: fail
```

The verifier writes `evidence-verify.json`, `evidence-verify.md`, and `badge.json`. See `release-evidence-verify.md` and `../examples/workflows/release-evidence-consume.yml`.
