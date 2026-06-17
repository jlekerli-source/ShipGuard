#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios spec-workflow --help >/dev/null

./bin/shipguard ios design \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/design" \
  --shipguard-eval \
  --shareable >/dev/null

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/design" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null

./bin/shipguard ios spec-workflow \
  --path fixtures/demo-ios-repo \
  --feature "Spec-driven Devspace workflow integration" \
  --from-report "$tmp_dir/quality" \
  --app-type game \
  --shipguard-eval \
  --shareable \
  --out "$tmp_dir/spec" >/dev/null

test -f "$tmp_dir/spec/ios-spec-workflow.json"
test -f "$tmp_dir/spec/ios-spec-workflow.md"
test -f "$tmp_dir/spec/shipguard-constitution.md"
test -f "$tmp_dir/spec/feature-spec.md"
test -f "$tmp_dir/spec/implementation-plan.md"
test -f "$tmp_dir/spec/tasks.md"
test -f "$tmp_dir/spec/devspace-guardrails.md"
python3 -m json.tool "$tmp_dir/spec/ios-spec-workflow.json" >/dev/null
grep -q '"tool": "shipguard ios spec-workflow"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"value": "game"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"mode": "shareable"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"shipguardOnly": true' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"source": "GitHub Spec Kit"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"source": "CodexPro"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q 'Did the report tailor advice to the app type' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '# ShipGuard Constitution' "$tmp_dir/spec/shipguard-constitution.md"
grep -q 'Devspace is a planning bridge' "$tmp_dir/spec/shipguard-constitution.md"
grep -q '# Feature Spec' "$tmp_dir/spec/feature-spec.md"
grep -q '# Implementation Plan' "$tmp_dir/spec/implementation-plan.md"
grep -q '# Tasks' "$tmp_dir/spec/tasks.md"
grep -q '# Devspace Guardrails' "$tmp_dir/spec/devspace-guardrails.md"
grep -q 'Model selection happens in ChatGPT, not ShipGuard' "$tmp_dir/spec/devspace-guardrails.md" || \
  grep -q 'model selection happens in ChatGPT, not ShipGuard' "$tmp_dir/spec/devspace-guardrails.md"
grep -q '/plan Spec-driven Devspace workflow integration' "$tmp_dir/spec/ios-spec-workflow.md"
grep -q '/goal Implement Spec-driven Devspace workflow integration' "$tmp_dir/spec/ios-spec-workflow.md"
grep -q 'Scan Scope' "$tmp_dir/spec/ios-spec-workflow.md"

if grep -R -F -q "$tmp_dir" "$tmp_dir/spec"; then
  echo "shareable spec-workflow output must not include temp absolute paths" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/spec" \
  --out "$tmp_dir/spec-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/spec-quality/ios-report-quality.json"

cp -R "$tmp_dir/spec" "$tmp_dir/missing-artifact-spec"
rm "$tmp_dir/missing-artifact-spec/tasks.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-artifact-spec" \
  --out "$tmp_dir/missing-artifact-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-artifact-file-missing"' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
grep -q 'tasks.md' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-artifact-quality"; then
  echo "shareable artifact-missing quality output must not include temp absolute paths" >&2
  exit 1
fi

./bin/shipguard ios spec-workflow \
  --path fixtures/demo-ios-repo \
  --feature "No report context spec" \
  --shareable \
  --out "$tmp_dir/no-context-spec" >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/no-context-spec" \
  --out "$tmp_dir/no-context-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/no-context-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-report-context-missing"' "$tmp_dir/no-context-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-actionability-missing"' "$tmp_dir/no-context-quality/ios-report-quality.json"

json_stdout="$(
  ./bin/shipguard ios spec-workflow \
    --path fixtures/demo-ios-repo \
    --feature "Inline spec workflow" \
    --json
)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios spec-workflow"'
printf '%s\n' "$json_stdout" | grep -q '"ruleId": "spec-report-context-not-provided"'

echo "ios spec-workflow tests passed"
