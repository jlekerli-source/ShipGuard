#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

action="actions/transcript-corpus/action.yml"
workflow="examples/workflows/transcript-corpus.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Verify Codex maintainer transcript corpus' "$action"
grep -q 'source:' "$action"
grep -q 'require-report:' "$action"
grep -q 'transcript corpus' "$action"
grep -q 'corpus.json' "$action"
grep -q 'index.md' "$action"
grep -q 'badge.json' "$action"
grep -q 'require-report must be true or false' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'status="failed"' "$action"
grep -q 'exit_code="$corpus_exit"' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'codex-maintainer-transcript-corpus' "$action"

grep -q 'jlekerli-source/ringly-codex-workflows/actions/transcript-corpus@v3.36.0' "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'require-report: true' "$workflow"
grep -q 'mode: fail' "$workflow"
grep -q 'artifact-name: codex-maintainer-transcript-corpus' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out "$tmp_dir/corpus" \
  --require-report true >/dev/null

grep -q '"status": "pass"' "$tmp_dir/corpus/corpus.json"
grep -q '"case_count": 4' "$tmp_dir/corpus/corpus.json"
grep -q '"message": "pass 4/4"' "$tmp_dir/corpus/badge.json"
grep -q '| release-proof-review | pass | 0 | pass | runs/release-proof-review/transcript-verify.json |' "$tmp_dir/corpus/index.md"
grep -q '| release-evidence-consumption | pass | 0 | pass | runs/release-evidence-consumption/transcript-verify.json |' "$tmp_dir/corpus/index.md"

echo "transcript corpus action tests passed"
