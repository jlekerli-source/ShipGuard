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
