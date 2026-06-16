# Transcript Redaction

`codex-maintainer transcript redact` turns a raw maintainer transcript into shareable Markdown plus a machine-readable leak-audit report.

Use it before publishing anonymized agent runs, issue triage notes, or maintenance transcripts:

```bash
./bin/codex-maintainer transcript redact \
  --in raw-transcript.md \
  --out /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --private-term "InternalProjectName"
```

The command redacts:

- email addresses
- common GitHub and OpenAI token shapes
- bearer tokens
- secret-looking assignments such as `API_KEY=value`
- long hex token strings
- Unix and Windows user home paths
- custom terms passed with `--private-term`

The JSON report uses schema version `1.0` and includes:

- `status`: `pass` when no obvious risky pattern remains, otherwise `blocked`
- `total_replacements`: total redactions applied
- `private_terms_checked`: number of custom terms requested
- `rules`: per-rule replacement counts
- `remaining_risks`: any remaining risky pattern counts

This is a publication guardrail, not legal review. It is designed to catch obvious leaks before a maintainer adds a transcript to public docs, Arena fixtures, or benchmark writeups.

## Verify

Verify a redacted transcript before publishing it:

```bash
./bin/codex-maintainer transcript verify \
  --in /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --out /tmp/transcript-verify
```

The command writes:

- `transcript-verify.json`
- `transcript-verify.md`
- `badge.json`

It exits non-zero with `status: blocked` when the transcript still contains obvious risky patterns or when the optional redaction report is not passing.

For GitHub Actions, use `actions/transcript-verify` to run the same check and upload the verification bundle as an artifact.

## Corpus

Build a checked corpus of redacted transcripts:

```bash
./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out /tmp/transcript-corpus \
  --require-report true
```

See `transcript-corpus.md` for the fixture layout and aggregate outputs.

Checked demo corpus output is generated under `examples/demo-reports/transcripts/` from public fixtures only.
