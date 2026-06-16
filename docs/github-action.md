# GitHub Action

This repo exposes reusable composite actions for validating a workflow-bundle checkout and building release proof artifacts.

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
        uses: jlekerli-source/ringly-codex-workflows/actions/validate@v3.9.0
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Path to validate. |

## Release Proof Action

```yaml
- name: Build release proof
  uses: jlekerli-source/ringly-codex-workflows/actions/release-proof@v3.9.0
  with:
    release-url: https://github.com/owner/repo/releases/tag/v3.9.0
    issue-url: https://github.com/owner/repo/issues/123
```

The action builds the release tarball, manifest, release index, replay report, attestation, and attestation badge, then uploads them as an artifact. See `release-proof-action.md`, `release-proof-workflows.md`, and `release-proof-consumption.md`.

## Local Action Development

This repository uses the validation action against itself in `.github/workflows/validate.yml`:

```yaml
- name: Validate through reusable action
  uses: ./actions/validate
```
