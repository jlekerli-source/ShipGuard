#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"
current_version="$(sed -n '1p' VERSION)"

./bin/codex-maintainer next-goal --help >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer next-goal \
    --out "$tmp_dir/NEXT_GOAL.md" \
    --release 2.6.0 \
    --title "External Fixture Pack Import" >/dev/null

test -f "$tmp_dir/NEXT_GOAL.md"
grep -q "Current toolkit version: $current_version" "$tmp_dir/NEXT_GOAL.md"
grep -q 'Target release: v2.6.0' "$tmp_dir/NEXT_GOAL.md"
grep -q '/goal Implement v2.6.0 External Fixture Pack Import' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/template_profiles_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/arena_import_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/arena_compare_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/arena_compare_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/arena_sign_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/check_run_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/check_run_post_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/ci_summary_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/sarif_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/docs_check_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/transcript_redaction_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/transcript_verify_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/transcript_verify_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/transcript_corpus_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/transcript_corpus_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/next_goal_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_attest_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_proof_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_index_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_manifest_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_consume_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_consume_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_diff_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_diff_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_evidence_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_evidence_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_evidence_verify_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_evidence_verify_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_evidence_negative_index_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_proof_action_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_proof_consumption_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_proof_workflow_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/release_replay_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './bin/codex-maintainer next-goal --out NEXT_GOAL.md' "$tmp_dir/NEXT_GOAL.md"

if ./bin/codex-maintainer next-goal --release nope >/dev/null 2>&1; then
  echo "expected invalid release to fail" >&2
  exit 1
fi

echo "next goal tests passed"
