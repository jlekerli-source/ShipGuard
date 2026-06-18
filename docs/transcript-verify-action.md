# Transcript Verify Action

`actions/transcript-verify` runs `shipguard transcript verify` in GitHub Actions and uploads the verification bundle.

Use it when redacted maintainer transcripts, benchmark notes, or public examples should be checked before publication:

```yaml
- name: Verify redacted transcript
  uses: jlekerli-source/ShipGuard/actions/transcript-verify@v3.110.0
  with:
    transcript: docs/public-transcript.md
    report: artifacts/redaction-report.json
    mode: fail
```

Inputs:

- `transcript`: redacted Markdown transcript to verify.
- `report`: optional `redaction-report.json` from `transcript redact`.
- `out`: output directory, default `artifacts/shipguard-transcript-verify`.
- `upload-artifact`: set `false` to skip artifact upload.
- `artifact-name`: artifact name, default `shipguard-transcript-verify`.
- `mode`: `fail` blocks the job on unsafe content, `warn` emits warnings only.

Outputs:

- `status`: `pass`, `blocked`, or `failed`.
- `report-json`: path to `transcript-verify.json`.
- `report-md`: path to `transcript-verify.md`.
- `badge`: path to `badge.json`.

The uploaded artifact contains the JSON report, Markdown summary, and Shields-compatible badge JSON.
