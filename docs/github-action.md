# GitHub Action

This repo exposes reusable composite actions for validating a workflow-bundle checkout, comparing Arena benchmark results, verifying redacted maintainer transcripts, building release proof artifacts, consuming published release proof assets, comparing release proof, exporting release evidence, verifying downloaded evidence artifacts, and auditing the release evidence negative fixture corpus.

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
        uses: jlekerli-source/ringly-codex-workflows/actions/validate@v3.33.0
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Path to validate. |

## Arena Compare Action

```yaml
- name: Compare Arena results
  uses: jlekerli-source/ringly-codex-workflows/actions/arena-compare@v3.33.0
  with:
    left-results: artifacts/arena-old/results.json
    right-results: artifacts/arena-current/results.json
    mode: fail
```

The action runs `codex-maintainer arena compare`, uploads `arena-compare.json` and `arena-compare.md`, and exposes the comparison status. See `arena-compare-action.md`.

## Transcript Verify Action

```yaml
- name: Verify redacted transcript
  uses: jlekerli-source/ringly-codex-workflows/actions/transcript-verify@v3.33.0
  with:
    transcript: examples/redacted-transcript.md
    mode: fail
```

The action runs `codex-maintainer transcript verify`, uploads `transcript-verify.json`, `transcript-verify.md`, and `badge.json`, and exposes the verification status. See `transcript-verify-action.md`.

## Release Proof Action

```yaml
- name: Build release proof
  uses: jlekerli-source/ringly-codex-workflows/actions/release-proof@v3.33.0
  with:
    release-url: https://github.com/owner/repo/releases/tag/v3.33.0
    issue-url: https://github.com/owner/repo/issues/123
```

The action builds the release tarball, manifest, release index, replay report, attestation, and attestation badge, then uploads them as an artifact. See `release-proof-action.md`, `release-proof-workflows.md`, and `release-proof-consumption.md`.

## Release Consume Action

```yaml
- name: Verify published proof assets
  uses: jlekerli-source/ringly-codex-workflows/actions/release-consume@v3.33.0
  with:
    repo: jlekerli-source/ringly-codex-workflows
    release-tag: v3.33.0
    mode: fail
```

The action downloads release assets with `gh release download`, runs `codex-maintainer release-consume verify`, uploads the consumer proof bundle, and exposes paths for `consumer-report.json`, `asset-digests.json`, `sha256.txt`, and the regenerated attestation badge. See `release-consume-action.md`.

## Release Diff Action

```yaml
- name: Compare published proof assets
  uses: jlekerli-source/ringly-codex-workflows/actions/release-diff@v3.33.0
  with:
    repo: jlekerli-source/ringly-codex-workflows
    left-tag: v0.0.0
    right-tag: v3.33.0
    mode: fail
```

The action downloads both releases, runs `codex-maintainer release-diff compare`, uploads the diff report, and exposes paths for `release-diff.json` and `release-diff.md`. See `release-diff-action.md`.

## Release Evidence Action

```yaml
- name: Export release evidence
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.33.0
  with:
    title: Codex Maintainer Release Evidence
    include-diff: auto
    build-index: true
    mode: fail
```

The action runs `codex-maintainer release-evidence site`, optionally runs `codex-maintainer release-evidence index`, uploads the static evidence artifact, and exposes paths for `evidence.json` and `evidence-index.json`. See `release-evidence-action.md`.

## Release Evidence Bundle Action

```yaml
- name: Build release evidence bundle
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.33.0
  with:
    run: bundle
    repo: jlekerli-source/ringly-codex-workflows
    release-tag: v3.33.0
    previous-tag: v3.19.0
    download-assets: true
    mode: fail
```

Bundle mode downloads release assets, runs `codex-maintainer release-evidence bundle`, uploads consumer proof, optional release diff proof, static evidence site, evidence index, and `bundle.json`. See `release-evidence-action.md` and `release-evidence-bundle.md`.

## Release Evidence Verify Action

```yaml
- name: Verify release evidence artifact
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence-verify@v3.33.0
  with:
    download-artifact: true
    source-artifact-name: codex-maintainer-release-evidence
    dir: artifacts/codex-maintainer-release-evidence
    require-diff: true
    require-index: true
    mode: fail
```

Use this in a downstream job to prove an evidence artifact produced by `actions/release-evidence` can be consumed independently. The action can download the artifact, runs `codex-maintainer release-evidence verify`, uploads `evidence-verify.json`, `evidence-verify.md`, and `badge.json`, and exposes those paths as outputs. See `release-evidence-verify.md`.

## Release Evidence Negative Index Action

```yaml
- name: Audit release evidence negative fixtures
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence-negative-index@v3.33.0
  with:
    mode: fail
```

The action runs `codex-maintainer release-evidence negative-index` against the bundled intentional-failure fixtures, uploads `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, and per-case verifier reports, and exposes those paths as outputs. See `release-evidence-negative-index-action.md`.

## Local Action Development

This repository uses the validation action against itself in `.github/workflows/validate.yml`:

```yaml
- name: Validate through reusable action
  uses: ./actions/validate
```
