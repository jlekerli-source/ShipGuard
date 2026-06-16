# Transcript Corpus Action

`actions/transcript-corpus` runs `codex-maintainer transcript corpus` in GitHub Actions and uploads the corpus verification bundle.

Use it when public transcript examples should be verified on every PR or before publishing docs:

```yaml
- name: Verify transcript corpus
  uses: jlekerli-source/ringly-codex-workflows/actions/transcript-corpus@v3.35.0
  with:
    source: fixtures/transcripts
    require-report: true
    mode: fail
```

Inputs:

- `source`: corpus fixture directory.
- `out`: output directory, default `artifacts/codex-maintainer-transcript-corpus`.
- `require-report`: `true` requires every case to include `redaction-report.json`.
- `upload-artifact`: set `false` to skip artifact upload.
- `artifact-name`: artifact name, default `codex-maintainer-transcript-corpus`.
- `mode`: `fail` blocks the job on unsafe corpus output, `warn` emits warnings only.

Outputs:

- `status`: `pass`, `blocked`, or `failed`.
- `corpus-json`: path to `corpus.json`.
- `index-md`: path to `index.md`.
- `badge`: path to `badge.json`.

The uploaded artifact contains the aggregate corpus report, Markdown index, badge JSON, and per-case transcript verification reports under `runs/`.
