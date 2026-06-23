# GitHub Action

This repo exposes reusable composite actions for validating a workflow-bundle checkout, comparing Arena benchmark results, verifying redacted maintainer transcripts, verifying transcript corpora, building release proof artifacts, consuming published release proof assets, comparing release proof, exporting release evidence, verifying downloaded evidence artifacts, and auditing the release evidence negative fixture corpus.

For the first PR-proof path, start with `examples/workflows/verify-pr.yml`. It is intentionally transparent shell instead of a hidden action: it installs ShipGuard, prepares a task contract, records a PR diff, writes a structured validation receipt, runs `shipguard verify`, and uploads `shipguard-verdict.json` plus `shipguard-verdict.md`. Set `SHIPGUARD_VALIDATION_COMMAND` once near the top of the workflow before using it in a real repository.

Copy it into a target repository with:

```bash
mkdir -p .github/workflows
cp examples/workflows/verify-pr.yml .github/workflows/shipguard-verify-pr.yml
```

Before trusting a copied workflow, run the read-only first-run audit:

```bash
shipguard action verify-pr \
  --workflow .github/workflows/shipguard-verify-pr.yml \
  --out /tmp/shipguard-action-verify-pr \
  --shareable
```

The audit blocks missing install, diff, receipt, verify, or artifact-upload wiring and returns `review` while the starter validation placeholder is still present. A static pass still needs runtime proof from a real PR run and the uploaded `shipguard-verdict` artifact.

After the first small PR run, download and consume the uploaded proof:

```bash
gh run download <run-id> --name shipguard-verdict --dir /tmp/shipguard-verdict-artifact
shipguard action verify-pr \
  --workflow .github/workflows/shipguard-verify-pr.yml \
  --artifact-dir /tmp/shipguard-verdict-artifact \
  --out /tmp/shipguard-action-verify-pr \
  --shareable
```

This second pass verifies the artifact shape, not the product change. A consumed artifact proves reviewers can inspect `shipguard-verdict.json` and Markdown from CI; the verdict status still decides whether the PR itself passes, needs review, or is blocked.

## Usage

```yaml
name: Validate Codex workflow bundle

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Validate Codex workflow bundle
        uses: jlekerli-source/ShipGuard/actions/validate@v3.131.0
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Path to validate. |

## Arena Compare Action

```yaml
- name: Compare Arena results
  uses: jlekerli-source/ShipGuard/actions/arena-compare@v3.131.0
  with:
    left-results: artifacts/arena-old/results.json
    right-results: artifacts/arena-current/results.json
    mode: fail
```

The action runs `shipguard arena compare`, uploads `arena-compare.json` and `arena-compare.md`, and exposes the comparison status. See `arena-compare-action.md`.

## Transcript Verify Action

```yaml
- name: Verify redacted transcript
  uses: jlekerli-source/ShipGuard/actions/transcript-verify@v3.131.0
  with:
    transcript: examples/redacted-transcript.md
    mode: fail
```

The action runs `shipguard transcript verify`, uploads `transcript-verify.json`, `transcript-verify.md`, and `badge.json`, and exposes the verification status. See `transcript-verify-action.md`.

## Transcript Corpus Action

```yaml
- name: Verify transcript corpus
  uses: jlekerli-source/ShipGuard/actions/transcript-corpus@v3.131.0
  with:
    source: fixtures/transcripts
    require-report: true
    mode: fail
```

The action runs `shipguard transcript corpus`, uploads `corpus.json`, `index.md`, `badge.json`, and per-case verification reports, and exposes the corpus status. See `transcript-corpus-action.md`.

## Release Proof Action

```yaml
- name: Build release proof
  uses: jlekerli-source/ShipGuard/actions/release-proof@v3.131.0
  with:
    release-url: https://github.com/owner/repo/releases/tag/v3.131.0
    issue-url: https://github.com/owner/repo/issues/123
```

The action builds the release tarball, manifest, release index, replay report, attestation, and attestation badge, then uploads them as an artifact. See `release-proof-action.md`, `release-proof-workflows.md`, and `release-proof-consumption.md`.

## Release Consume Action

```yaml
- name: Verify published proof assets
  uses: jlekerli-source/ShipGuard/actions/release-consume@v3.131.0
  with:
    repo: jlekerli-source/ShipGuard
    release-tag: v3.131.0
    mode: fail
```

The action downloads release assets with `gh release download`, runs `shipguard release-consume verify`, uploads the consumer proof bundle, and exposes paths for `consumer-report.json`, `asset-digests.json`, `sha256.txt`, and the regenerated attestation badge. See `release-consume-action.md`.

## Release Diff Action

```yaml
- name: Compare published proof assets
  uses: jlekerli-source/ShipGuard/actions/release-diff@v3.131.0
  with:
    repo: jlekerli-source/ShipGuard
    left-tag: v0.0.0
    right-tag: v3.131.0
    mode: fail
```

The action downloads both releases, runs `shipguard release-diff compare`, uploads the diff report, and exposes paths for `release-diff.json` and `release-diff.md`. See `release-diff-action.md`.

## Release Evidence Action

```yaml
- name: Export release evidence
  uses: jlekerli-source/ShipGuard/actions/release-evidence@v3.131.0
  with:
    title: ShipGuard Release Evidence
    include-diff: auto
    build-index: true
    mode: fail
```

The action runs `shipguard release-evidence site`, optionally runs `shipguard release-evidence index`, uploads the static evidence artifact, and exposes paths for `evidence.json` and `evidence-index.json`. See `release-evidence-action.md`.

## Release Evidence Bundle Action

```yaml
- name: Build release evidence bundle
  uses: jlekerli-source/ShipGuard/actions/release-evidence@v3.131.0
  with:
    run: bundle
    repo: jlekerli-source/ShipGuard
    release-tag: v3.131.0
    previous-tag: v3.19.0
    download-assets: true
    mode: fail
```

Bundle mode downloads release assets, runs `shipguard release-evidence bundle`, uploads consumer proof, optional release diff proof, static evidence site, evidence index, and `bundle.json`. See `release-evidence-action.md` and `release-evidence-bundle.md`.

## Release Evidence Verify Action

```yaml
- name: Verify release evidence artifact
  uses: jlekerli-source/ShipGuard/actions/release-evidence-verify@v3.131.0
  with:
    download-artifact: true
    source-artifact-name: shipguard-release-evidence
    dir: artifacts/shipguard-release-evidence
    require-diff: true
    require-index: true
    mode: fail
```

Use this in a downstream job to prove an evidence artifact produced by `actions/release-evidence` can be consumed independently. The action can download the artifact, runs `shipguard release-evidence verify`, uploads `evidence-verify.json`, `evidence-verify.md`, and `badge.json`, and exposes those paths as outputs. See `release-evidence-verify.md`.

## Release Evidence Negative Index Action

```yaml
- name: Audit release evidence negative fixtures
  uses: jlekerli-source/ShipGuard/actions/release-evidence-negative-index@v3.131.0
  with:
    mode: fail
```

The action runs `shipguard release-evidence negative-index` against the bundled intentional-failure fixtures, uploads `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, and per-case verifier reports, and exposes those paths as outputs. See `release-evidence-negative-index-action.md`.

## Local Action Development

This repository uses the validation action against itself in `.github/workflows/validate.yml`:

```yaml
- name: Validate through reusable action
  uses: ./actions/validate
```
