#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

reports="$tmp_dir/reports"
./bin/shipguard ios report-quality --help >/dev/null
./bin/shipguard ios performance \
  --path fixtures/demo-ios-repo \
  --out "$reports/performance" \
  --shipguard-eval >/dev/null
./bin/shipguard ios design \
  --path fixtures/demo-ios-repo \
  --out "$reports/design" \
  --shipguard-eval >/dev/null

./bin/shipguard ios report-quality \
  --reports "$reports" \
  --out "$tmp_dir/quality" >/dev/null

test -f "$tmp_dir/quality/ios-report-quality.json"
test -f "$tmp_dir/quality/ios-report-quality.md"
python3 -m json.tool "$tmp_dir/quality/ios-report-quality.json" >/dev/null
grep -q '"tool": "shipguard ios report-quality"' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"reportCount": 2' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"purpose": "Grade ShipGuard report usefulness; do not convert target-app findings into app work."' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"actionabilityQuestions":' "$tmp_dir/quality/ios-report-quality.json"
grep -q '# iOS ShipGuard Report Quality' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios performance' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios design' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'Actionability Questions' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'local-path-shareability-warning' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"redactionPlan":' "$tmp_dir/quality/ios-report-quality.json"
grep -q 'Redaction Plan' "$tmp_dir/quality/ios-report-quality.md"

shareable_reports="$tmp_dir/shareable-reports"
./bin/shipguard ios design \
  --path fixtures/demo-ios-repo \
  --out "$shareable_reports/design" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$shareable_reports/design" \
  --out "$tmp_dir/shareable-quality" \
  --shareable >/dev/null
grep -q '"mode": "shareable"' "$tmp_dir/shareable-quality/ios-report-quality.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/shareable-quality/ios-report-quality.json"
grep -q '"path": "<report-input-1>/ios-design.json"' "$tmp_dir/shareable-quality/ios-report-quality.json"
grep -q '"markdownPath": "<report-input-1>/ios-design.md"' "$tmp_dir/shareable-quality/ios-report-quality.json"
grep -q 'Shareability mode: `shareable`' "$tmp_dir/shareable-quality/ios-report-quality.md"
grep -q 'Actionability Questions' "$tmp_dir/shareable-quality/ios-report-quality.md"
if grep -R -F -q "$tmp_dir" "$tmp_dir/shareable-quality"; then
  echo "shareable report-quality output must not include local absolute temp paths" >&2
  exit 1
fi

actionability_fixture="fixtures/ios-report-quality/actionability"
./bin/shipguard ios report-quality \
  --reports "$actionability_fixture" \
  --out "$tmp_dir/actionability-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q '"priorityAction":' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q '"prioritizedActionabilityQuestions":' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q '"kind": "answer-actionability-question"' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q '"report": "fixtures/ios-report-quality/actionability/ios-ai-readiness-report.json"' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q '"question": "Does the report explain which AI path is the safest default for this app type?"' "$tmp_dir/actionability-quality/ios-report-quality.json"
grep -q 'Priority Action' "$tmp_dir/actionability-quality/ios-report-quality.md"
grep -q 'Actionability Questions' "$tmp_dir/actionability-quality/ios-report-quality.md"
grep -q 'safest default for this app type' "$tmp_dir/actionability-quality/ios-report-quality.md"
grep -q 'Answer the actionability questions above' "$tmp_dir/actionability-quality/ios-report-quality.md"
if grep -q 'local-path-shareability-warning' "$tmp_dir/shareable-quality/ios-report-quality.json"; then
  echo "shareable report-quality output should not add local-path warnings for shareable inputs" >&2
  exit 1
fi

priority_fixture="$tmp_dir/priority-fixture"
mkdir -p "$priority_fixture"
cat > "$priority_fixture/ios-ai-readiness.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios ai-readiness",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-17T00:00:00Z",
  "status": "review",
  "shareability": {
    "mode": "shareable",
    "localAbsolutePathsIncluded": false
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  },
  "scanScope": {
    "skippedDirectoryCount": 0,
    "skippedDirectories": []
  },
  "findings": [
    {
      "ruleId": "ai-lower-priority",
      "severity": "review",
      "evidence": "AI readiness fixture has a review-level source finding.",
      "recommendation": "Keep AI guidance path-safe.",
      "proofGuidance": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "AI lower-priority question should not outrank blocked performance."
  ]
}
JSON
cat > "$priority_fixture/ios-ai-readiness.md" <<'MD'
# AI Readiness Priority Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
cat > "$priority_fixture/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-17T00:00:00Z",
  "status": "blocked",
  "shareability": {
    "mode": "shareable",
    "localAbsolutePathsIncluded": false
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  },
  "scanScope": {
    "skippedDirectoryCount": 0,
    "skippedDirectories": []
  },
  "findings": [
    {
      "ruleId": "performance-higher-priority",
      "severity": "high",
      "evidence": "Performance fixture has a blocked source finding.",
      "recommendation": "Prioritize blocked performance report questions.",
      "proofGuidance": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Performance priority question should be first."
  ]
}
JSON
cat > "$priority_fixture/ios-performance.md" <<'MD'
# Performance Priority Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
./bin/shipguard ios report-quality \
  --reports "$priority_fixture" \
  --out "$tmp_dir/priority-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/priority-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/priority-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data["priorityAction"]
if priority["kind"] != "answer-actionability-question":
    raise SystemExit(f"unexpected priority kind: {priority!r}")
if priority["tool"] != "shipguard ios performance":
    raise SystemExit(f"expected performance priority, got {priority!r}")
if priority["sourceStatus"] != "blocked":
    raise SystemExit(f"expected blocked source status, got {priority!r}")
if priority["question"] != "Performance priority question should be first.":
    raise SystemExit(f"unexpected priority question: {priority!r}")
ranked = data["prioritizedActionabilityQuestions"]
if ranked[0]["tool"] != "shipguard ios performance":
    raise SystemExit(f"ranked questions did not start with performance: {ranked!r}")
PY
grep -q 'Priority Action' "$tmp_dir/priority-quality/ios-report-quality.md"
grep -q 'Performance priority question should be first.' "$tmp_dir/priority-quality/ios-report-quality.md"

local_contract_reports="$tmp_dir/local-contract-reports"
./bin/shipguard ios modernize \
  --focus swift \
  --path fixtures/demo-ios-repo \
  --out "$local_contract_reports/modernize" \
  --shipguard-eval >/dev/null
./bin/shipguard ios report-quality \
  --reports "$local_contract_reports/modernize" \
  --out "$tmp_dir/local-contract-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/local-contract-quality/ios-report-quality.json"
grep -q '"ruleId": "declared-shareability-local-mode"' "$tmp_dir/local-contract-quality/ios-report-quality.json"

missing_contract_dir="$tmp_dir/missing-contract"
mkdir -p "$missing_contract_dir"
cat > "$missing_contract_dir/ios-ai-readiness.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios ai-readiness",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-17T00:00:00Z",
  "status": "review",
  "scanScope": {
    "skippedDirectoryCount": 0,
    "skippedDirectories": []
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  },
  "findings": [
    {
      "ruleId": "ai-demo",
      "severity": "review",
      "evidence": "Demo AI signal",
      "recommendation": "Keep the fixture path-safe.",
      "proofGuidance": "Run report-quality in shareable mode."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality catch missing declared shareability metadata?"
  ]
}
JSON
cat > "$missing_contract_dir/ios-ai-readiness.md" <<'MD'
# Missing Contract Report

## ShipGuard Evaluation Boundary

This fixture is intentionally missing shareability metadata.
MD

./bin/shipguard ios report-quality \
  --reports "$missing_contract_dir" \
  --out "$tmp_dir/missing-contract-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-contract-quality/ios-report-quality.json"
grep -q '"ruleId": "declared-shareability-missing"' "$tmp_dir/missing-contract-quality/ios-report-quality.json"

bad_dir="$tmp_dir/bad"
mkdir -p "$bad_dir"
cat > "$bad_dir/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-17T00:00:00Z",
  "status": "review",
  "findings": [
    {
      "ruleId": "demo-rule",
      "severity": "review",
      "title": "Weak finding"
    }
  ]
}
JSON
cat > "$bad_dir/ios-performance.md" <<'MD'
# Weak Report

No boundary, no scan scope, and no report-quality questions.
MD

./bin/shipguard ios report-quality \
  --reports "$bad_dir" \
  --out "$tmp_dir/bad-quality" >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/bad-quality/ios-report-quality.json"
grep -q '"ruleId": "shipguard-eval-boundary-missing"' "$tmp_dir/bad-quality/ios-report-quality.json"
grep -q '"ruleId": "scan-scope-missing"' "$tmp_dir/bad-quality/ios-report-quality.json"
grep -q '"ruleId": "finding-proof-guidance-missing"' "$tmp_dir/bad-quality/ios-report-quality.json"
if ./bin/shipguard ios report-quality --reports "$bad_dir" --strict >/dev/null 2>&1; then
  echo "strict report-quality should fail for blocked report quality" >&2
  exit 1
fi

token_fixture="fixtures/ios-report-quality/token-shareability"
./bin/shipguard ios report-quality \
  --reports "$token_fixture" \
  --out "$tmp_dir/token-quality" >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/token-quality/ios-report-quality.json"
grep -q '"ruleId": "token-shareability-risk"' "$tmp_dir/token-quality/ios-report-quality.json"
grep -q '"blockedUntilRedacted": true' "$tmp_dir/token-quality/ios-report-quality.json"
grep -q 'shipguard ios redact' "$tmp_dir/token-quality/ios-report-quality.md"
if grep -R -q 'fixtureconnector1234567890' "$tmp_dir/token-quality"; then
  echo "report-quality output must not echo token-like fixture values" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$token_fixture" \
  --out "$tmp_dir/token-quality-shareable" \
  --shareable >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/token-quality-shareable/ios-report-quality.json"
grep -q '"mode": "shareable"' "$tmp_dir/token-quality-shareable/ios-report-quality.json"
grep -q '"report": "fixtures/ios-report-quality/token-shareability/ios-devspace-report.json"' "$tmp_dir/token-quality-shareable/ios-report-quality.json"
grep -q '"input": "fixtures/ios-report-quality/token-shareability"' "$tmp_dir/token-quality-shareable/ios-report-quality.json"
grep -q '"output": "<redacted-report-dir>"' "$tmp_dir/token-quality-shareable/ios-report-quality.json"
if grep -R -F -q "$repo_root" "$tmp_dir/token-quality-shareable"; then
  echo "shareable token report-quality output must not include repo absolute paths" >&2
  exit 1
fi
if grep -R -q 'fixtureconnector1234567890' "$tmp_dir/token-quality-shareable"; then
  echo "shareable report-quality output must not echo token-like fixture values" >&2
  exit 1
fi

json_stdout="$(./bin/shipguard ios report-quality --reports "$reports" --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios report-quality"'

echo "ios report quality tests passed"
