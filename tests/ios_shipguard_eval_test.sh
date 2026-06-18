#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios eval --help >/dev/null
./bin/shipguard ios eval \
  --cases evals/ios_shipguard_cases.jsonl \
  --out "$tmp_dir/shipguard-eval" >/dev/null

test -f "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
test -f "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '"tool": "shipguard ios eval"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"status": "pass"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"caseCount": 11' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"failed": 0' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "permission-audit"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "release-proof"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "storekit-commerce"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "build-apps-bridge"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "preview-bridge"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "widgets-intents-shared-store"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "performance-audit"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "design-audit"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "external-source-audit"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '"mode": "privacy-security"' "$tmp_dir/shipguard-eval/ios-shipguard-eval.json"
grep -q '# iOS ShipGuard Eval' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| preview-tap-needs-element-ref | pass | preview-bridge |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| performance-stutter-profiler-fallback | pass | performance-audit |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| build-ios-apps-front-door | pass | build-apps-bridge |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| design-genre-icon-haptics-preview | pass | design-audit |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"
grep -q '| external-source-native-adoption | pass | external-source-audit |' "$tmp_dir/shipguard-eval/ios-shipguard-eval.md"

json_stdout="$(./bin/shipguard ios eval --cases evals/ios_shipguard_cases.jsonl --json)"
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
