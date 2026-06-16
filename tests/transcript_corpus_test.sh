#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer transcript corpus --help >/dev/null

./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out "$tmp_dir/corpus" \
  --require-report true >/dev/null

test -f "$tmp_dir/corpus/corpus.json"
test -f "$tmp_dir/corpus/index.md"
test -f "$tmp_dir/corpus/badge.json"
test -f "$tmp_dir/corpus/runs/ios-notification-triage/transcript-verify.json"
grep -q '"status": "pass"' "$tmp_dir/corpus/corpus.json"
grep -q '"case_count": 4' "$tmp_dir/corpus/corpus.json"
grep -q '"passed_count": 4' "$tmp_dir/corpus/corpus.json"
grep -q '"blocked_count": 0' "$tmp_dir/corpus/corpus.json"
grep -q '"message": "pass 4/4"' "$tmp_dir/corpus/badge.json"
grep -q '| ios-notification-triage | pass | 0 | pass | runs/ios-notification-triage/transcript-verify.json |' "$tmp_dir/corpus/index.md"
grep -q '| release-evidence-consumption | pass | 0 | pass | runs/release-evidence-consumption/transcript-verify.json |' "$tmp_dir/corpus/index.md"

unsafe_source="$tmp_dir/unsafe-source"
mkdir -p "$unsafe_source/leaky-case"
cat > "$unsafe_source/leaky-case/transcript.md" <<'RAW'
# Leaky Transcript

Maintainer: This still includes maintainer@example.com and API_TOKEN=secret-value.
RAW

if ./bin/codex-maintainer transcript corpus --source "$unsafe_source" --out "$tmp_dir/unsafe-corpus" >/dev/null 2>&1; then
  echo "expected unsafe transcript corpus to fail" >&2
  exit 1
fi
test -f "$tmp_dir/unsafe-corpus/corpus.json"
grep -q '"status": "blocked"' "$tmp_dir/unsafe-corpus/corpus.json"
grep -q '"blocked_count": 1' "$tmp_dir/unsafe-corpus/corpus.json"
grep -q '"message": "blocked 0/1"' "$tmp_dir/unsafe-corpus/badge.json"

missing_report_source="$tmp_dir/missing-report-source"
mkdir -p "$missing_report_source/clean-case"
cat > "$missing_report_source/clean-case/transcript.md" <<'RAW'
# Clean Transcript

Maintainer: All sensitive values are represented with redacted placeholders.
RAW

if ./bin/codex-maintainer transcript corpus --source "$missing_report_source" --out "$tmp_dir/missing-report-corpus" --require-report true >/dev/null 2>&1; then
  echo "expected require-report corpus to fail without a report" >&2
  exit 1
fi
grep -q '"status": "blocked"' "$tmp_dir/missing-report-corpus/corpus.json"
grep -q '"redaction_report_status": "missing"' "$tmp_dir/missing-report-corpus/corpus.json"
grep -q '| clean-case | blocked | 0 | missing | runs/clean-case/transcript-verify.json |' "$tmp_dir/missing-report-corpus/index.md"

echo "transcript corpus tests passed"
