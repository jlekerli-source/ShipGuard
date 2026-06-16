#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer ios eval --help >/dev/null
./bin/codex-maintainer ios eval \
  --cases evals/ios_shipguard_cases.jsonl \
  --out "$tmp_dir/shipguard-eval" >/dev/null

test -f "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
test -f "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '"tool": "codex-maintainer ios eval"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"status": "pass"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"caseCount": 6' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"failed": 0' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "permission-audit"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "release-proof"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "storekit-commerce"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "preview-bridge"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "widgets-intents-shared-store"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "privacy-security"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '# iOS Shipguard Eval' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| preview-tap-needs-element-ref | pass | preview-bridge |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"

json_stdout="$(./bin/codex-maintainer ios eval --cases evals/ios_shipguard_cases.jsonl --json)"
printf '%s\n' "$json_stdout" | grep -q '"status": "pass"'

if env -u OPENAI_API_KEY python3 evals/run_local.py >"$tmp_dir/live-stdout.txt" 2>"$tmp_dir/live-stderr.txt"; then
  echo "expected live evals to skip without OPENAI_API_KEY" >&2
  exit 1
else
  status="$?"
  test "$status" -eq 2
fi
grep -q 'live evals require OPENAI_API_KEY' "$tmp_dir/live-stderr.txt"

echo "ios shipguard eval tests passed"
