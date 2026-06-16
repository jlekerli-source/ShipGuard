# GitHub Action

This repo exposes a reusable composite action for validating a workflow-bundle checkout.

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
        uses: jlekerli-source/ringly-codex-workflows/actions/validate@v0.3.0
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Path to validate. |

## Local Action Development

This repository uses the action against itself in `.github/workflows/validate.yml`:

```yaml
- name: Validate through reusable action
  uses: ./actions/validate
```
