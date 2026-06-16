# Transcript Corpus

`codex-maintainer transcript corpus` verifies a directory of redacted maintainer transcripts and writes a public corpus index.

Use it when adding anonymized maintenance notes to docs, benchmark commentary, or public examples:

```bash
./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out /tmp/transcript-corpus \
  --require-report true
```

The fixture layout is intentionally small:

```text
fixtures/transcripts/<case-id>/transcript.md
fixtures/transcripts/<case-id>/redaction-report.json
```

`redaction-report.json` is optional by default. Use `--require-report true` when every transcript must carry the original redaction audit.

The command writes:

- `corpus.json`
- `index.md`
- `badge.json`
- `runs/<case-id>/transcript-verify.json`
- `runs/<case-id>/transcript-verify.md`
- `runs/<case-id>/badge.json`

The aggregate status is `blocked` if any transcript still contains obvious risky content, if any verification report fails, or if `--require-report true` is set and a case is missing `redaction-report.json`.

This is not a claim that the transcripts are real adoption data. It is a reproducible publication gate for public-safe maintainer examples.
