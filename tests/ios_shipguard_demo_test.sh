#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios demo --help >/dev/null
./bin/shipguard ios demo --out "$tmp_dir/demo" >/dev/null

test -f "$tmp_dir/demo/shipguard-demo.json"
test -f "$tmp_dir/demo/README.md"
grep -q '"tool": "shipguard ios demo"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"status": "pass"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "doctor"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "inventory"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "modernize"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "plan"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "prove"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "app-intelligence"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "ai-readiness"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "spec-workflow"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "eval"' "$tmp_dir/demo/shipguard-demo.json"
grep -q '"id": "redaction"' "$tmp_dir/demo/shipguard-demo.json"

test -f "$tmp_dir/demo/doctor/ios-doctor.md"
test -f "$tmp_dir/demo/inventory/ios-inventory.md"
test -f "$tmp_dir/demo/modernize/ios-modernize.md"
test -f "$tmp_dir/demo/plan/ios-plan.md"
test -f "$tmp_dir/demo/proof/ios-proof.md"
test -f "$tmp_dir/demo/app-intelligence/ios-app-intelligence.md"
test -f "$tmp_dir/demo/ai-readiness/ios-ai-readiness.md"
test -f "$tmp_dir/demo/spec-workflow/ios-spec-workflow.md"
test -f "$tmp_dir/demo/spec-workflow/tasks.md"
test -f "$tmp_dir/demo/eval/ios-shipguard-eval.md"
test -f "$tmp_dir/demo/redacted/ios-ai-readiness.md"
test -f "$tmp_dir/demo/redacted/ios-redaction.json"

grep -q '# iOS ShipGuard First-Run Demo' "$tmp_dir/demo/README.md"
grep -q 'clean checkout can run the static ShipGuard loop' "$tmp_dir/demo/README.md"
grep -q 'codex plugin add ios-shipguard@shipguard' "$tmp_dir/demo/README.md"
grep -q '"remainingRiskCount": 0' "$tmp_dir/demo/redacted/ios-redaction.json"
grep -q '"status": "pass"' "$tmp_dir/demo/eval/ios-shipguard-eval.json"

json_stdout="$(./bin/shipguard ios demo --out "$tmp_dir/demo-json" --json)"
printf '%s\n' "$json_stdout" | grep -q '"status": "pass"'

echo "ios shipguard demo tests passed"
