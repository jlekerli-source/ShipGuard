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

dedupe_fixture="$tmp_dir/dedupe-fixture"
mkdir -p "$dedupe_fixture"
cat > "$dedupe_fixture/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-18T00:00:00Z",
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
  "findings": [],
  "reportQualityQuestions": [
    "Did report wording keep target-app remediation separate from ShipGuard product QA next steps?",
    "Which grouped performance observation should become a public fixture?"
  ]
}
JSON
cat > "$dedupe_fixture/ios-performance.md" <<'MD'
# Performance Dedupe Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
cat > "$dedupe_fixture/ios-design.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios design",
  "intent": "shipguard-evaluation",
  "generatedAt": "2026-06-18T00:00:00Z",
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
  "findings": [],
  "reportQualityQuestions": [
    "Did report wording keep target-app remediation separate from ShipGuard product QA next steps?",
    "Should design DNA evidence include enough app-type context for a public fixture?"
  ]
}
JSON
cat > "$dedupe_fixture/ios-design.md" <<'MD'
# Design Dedupe Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
./bin/shipguard ios report-quality \
  --reports "$dedupe_fixture" \
  --out "$tmp_dir/dedupe-quality" \
  --shareable >/dev/null
python3 - <<'PY' "$tmp_dir/dedupe-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
shared = "Did report wording keep target-app remediation separate from ShipGuard product QA next steps?"
ranked = data["prioritizedActionabilityQuestions"]
texts = [item["question"] for item in ranked]
if texts.count(shared) != 1:
    raise SystemExit(f"expected one shared question, got {texts!r}")
if "Which grouped performance observation should become a public fixture?" not in texts:
    raise SystemExit(f"later unique performance question was dropped: {texts!r}")
if "Should design DNA evidence include enough app-type context for a public fixture?" not in texts:
    raise SystemExit(f"later unique design question was dropped: {texts!r}")
shared_row = next(item for item in ranked if item["question"] == shared)
if shared_row.get("duplicateCount") != 2:
    raise SystemExit(f"expected duplicateCount=2, got {shared_row!r}")
questions = [item["question"] for item in data["actionabilityQuestions"]]
if questions.count(shared) != 1:
    raise SystemExit(f"raw actionabilityQuestions were not deduped: {questions!r}")
PY
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
      "severityReason": "High because this fixture intentionally represents a blocked performance source report.",
      "impact": "This fixture should stay first because blocked performance reports should outrank lower-status source reports.",
      "recommendation": "Prioritize blocked performance report questions.",
      "localProof": "Run report-quality on the fixture locally.",
      "manualProof": "No manual proof is required for this synthetic priority fixture.",
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

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| high | `performance-higher-priority` | High because this fixture intentionally represents a blocked performance source report. | This fixture should stay first because blocked performance reports should outrank lower-status source reports. |

## Proof Boundaries

| Severity | Rule | Codex local proof | Manual/device proof |
| --- | --- | --- | --- |
| high | `performance-higher-priority` | Run report-quality on the fixture locally. | No manual proof is required for this synthetic priority fixture. |
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

missing_impact_dir="$tmp_dir/missing-impact"
mkdir -p "$missing_impact_dir"
cat > "$missing_impact_dir/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
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
      "ruleId": "performance-missing-impact",
      "severity": "review",
      "evidence": "Performance fixture has evidence and proof but no why-it-matters explanation.",
      "recommendation": "Keep the report actionable.",
      "proofGuidance": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce performance finding explanations?"
  ]
}
JSON
cat > "$missing_impact_dir/ios-performance.md" <<'MD'
# Missing Impact Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
./bin/shipguard ios report-quality \
  --reports "$missing_impact_dir" \
  --out "$tmp_dir/missing-impact-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-impact-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-finding-impact-missing"' "$tmp_dir/missing-impact-quality/ios-report-quality.json"

missing_markdown_impact_dir="$tmp_dir/missing-markdown-impact"
mkdir -p "$missing_markdown_impact_dir"
cat > "$missing_markdown_impact_dir/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
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
      "ruleId": "performance-hidden-impact",
      "severity": "review",
      "evidence": "Performance fixture has impact in JSON only.",
      "impact": "Readers need the impact explanation in Markdown too.",
      "recommendation": "Keep human-readable reports useful.",
      "proofGuidance": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce Markdown explanation visibility?"
  ]
}
JSON
cat > "$missing_markdown_impact_dir/ios-performance.md" <<'MD'
# Hidden Impact Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
./bin/shipguard ios report-quality \
  --reports "$missing_markdown_impact_dir" \
  --out "$tmp_dir/missing-markdown-impact-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-markdown-impact-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-impact-missing"' "$tmp_dir/missing-markdown-impact-quality/ios-report-quality.json"

missing_severity_dir="$tmp_dir/missing-severity"
mkdir -p "$missing_severity_dir"
cat > "$missing_severity_dir/ios-performance.json" <<'JSON'
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
      "ruleId": "performance-high-without-reason",
      "severity": "high",
      "evidence": "High performance fixture has no explicit severity reason.",
      "impact": "High findings should explain why the severity is high.",
      "recommendation": "Add a severity reason.",
      "proof": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce high severity reasons?"
  ]
}
JSON
cat > "$missing_severity_dir/ios-performance.md" <<'MD'
# Missing Severity Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| high | `performance-high-without-reason` | Missing in JSON. | High findings should explain why the severity is high. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_severity_dir" \
  --out "$tmp_dir/missing-severity-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-severity-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-high-severity-reason-missing"' "$tmp_dir/missing-severity-quality/ios-report-quality.json"

missing_markdown_severity_dir="$tmp_dir/missing-markdown-severity"
mkdir -p "$missing_markdown_severity_dir"
cat > "$missing_markdown_severity_dir/ios-performance.json" <<'JSON'
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
      "ruleId": "performance-hidden-severity",
      "severity": "high",
      "evidence": "High performance fixture hides severity reason from Markdown.",
      "severityReason": "High because this fixture has an explicit high source signal.",
      "impact": "Reviewers need the severity reason in Markdown too.",
      "recommendation": "Show severity reason in Markdown.",
      "proof": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce Markdown severity visibility?"
  ]
}
JSON
cat > "$missing_markdown_severity_dir/ios-performance.md" <<'MD'
# Hidden Severity Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Top Findings

| Severity | Rule | Why it matters |
| --- | --- | --- |
| high | `performance-hidden-severity` | Reviewers need the severity reason in Markdown too. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_markdown_severity_dir" \
  --out "$tmp_dir/missing-markdown-severity-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-markdown-severity-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-severity-reason-missing"' "$tmp_dir/missing-markdown-severity-quality/ios-report-quality.json"

missing_proof_boundary_dir="$tmp_dir/missing-proof-boundary"
mkdir -p "$missing_proof_boundary_dir"
cat > "$missing_proof_boundary_dir/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
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
      "ruleId": "performance-unsplit-proof",
      "severity": "review",
      "evidence": "Performance fixture has only a generic proof sentence.",
      "severityReason": "Review because this fixture represents a performance source signal.",
      "impact": "Proof guidance needs a local/manual boundary.",
      "recommendation": "Split proof guidance into local and manual proof fields.",
      "proof": "Run a profiler and device proof if needed."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce split performance proof boundaries?"
  ]
}
JSON
cat > "$missing_proof_boundary_dir/ios-performance.md" <<'MD'
# Missing Proof Boundary Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| review | `performance-unsplit-proof` | Review because this fixture represents a performance source signal. | Proof guidance needs a local/manual boundary. |

## Proof Boundaries

| Severity | Rule | Codex local proof | Manual/device proof |
| --- | --- | --- | --- |
| review | `performance-unsplit-proof` | Missing in JSON. | Missing in JSON. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_proof_boundary_dir" \
  --out "$tmp_dir/missing-proof-boundary-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-proof-boundary-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-proof-boundary-missing"' "$tmp_dir/missing-proof-boundary-quality/ios-report-quality.json"

missing_markdown_proof_boundary_dir="$tmp_dir/missing-markdown-proof-boundary"
mkdir -p "$missing_markdown_proof_boundary_dir"
cat > "$missing_markdown_proof_boundary_dir/ios-performance.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios performance",
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
      "ruleId": "performance-hidden-proof-boundary",
      "severity": "review",
      "evidence": "Performance fixture hides split proof guidance from Markdown.",
      "severityReason": "Review because this fixture represents a performance source signal.",
      "impact": "Reviewers need local and manual proof boundaries in Markdown too.",
      "recommendation": "Show split proof guidance in Markdown.",
      "localProof": "Run local report-quality and simulator proof.",
      "manualProof": "Use device proof for hardware claims.",
      "proof": "Local proof: Run local report-quality and simulator proof. Manual/device proof: Use device proof for hardware claims."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce Markdown proof boundary visibility?"
  ]
}
JSON
cat > "$missing_markdown_proof_boundary_dir/ios-performance.md" <<'MD'
# Hidden Proof Boundary Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| review | `performance-hidden-proof-boundary` | Review because this fixture represents a performance source signal. | Reviewers need local and manual proof boundaries in Markdown too. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_markdown_proof_boundary_dir" \
  --out "$tmp_dir/missing-markdown-proof-boundary-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-markdown-proof-boundary-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-proof-boundary-missing"' "$tmp_dir/missing-markdown-proof-boundary-quality/ios-report-quality.json"

missing_grouping_dir="$tmp_dir/missing-grouping"
mkdir -p "$missing_grouping_dir"
cat > "$missing_grouping_dir/ios-performance.json" <<'JSON'
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
      "ruleId": "performance-repeated-rule",
      "severity": "high",
      "evidence": "Repeated performance evidence 1.",
      "severityReason": "High because this repeated fixture represents a concrete high source signal.",
      "impact": "Repeated rows are noisy without grouped action guidance.",
      "recommendation": "Group repeated rules.",
      "proof": "Run report-quality on the fixture."
    },
    {
      "ruleId": "performance-repeated-rule",
      "severity": "high",
      "evidence": "Repeated performance evidence 2.",
      "severityReason": "High because this repeated fixture represents a concrete high source signal.",
      "impact": "Repeated rows are noisy without grouped action guidance.",
      "recommendation": "Group repeated rules.",
      "proof": "Run report-quality on the fixture."
    },
    {
      "ruleId": "performance-repeated-rule",
      "severity": "high",
      "evidence": "Repeated performance evidence 3.",
      "severityReason": "High because this repeated fixture represents a concrete high source signal.",
      "impact": "Repeated rows are noisy without grouped action guidance.",
      "recommendation": "Group repeated rules.",
      "proof": "Run report-quality on the fixture."
    },
    {
      "ruleId": "performance-repeated-rule",
      "severity": "high",
      "evidence": "Repeated performance evidence 4.",
      "severityReason": "High because this repeated fixture represents a concrete high source signal.",
      "impact": "Repeated rows are noisy without grouped action guidance.",
      "recommendation": "Group repeated rules.",
      "proof": "Run report-quality on the fixture."
    }
  ],
  "reportQualityQuestions": [
    "Does report-quality enforce grouping for repeated performance rules?"
  ]
}
JSON
cat > "$missing_grouping_dir/ios-performance.md" <<'MD'
# Missing Grouping Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| high | `performance-repeated-rule` | High because this repeated fixture represents a concrete high source signal. | Repeated rows are noisy without grouped action guidance. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_grouping_dir" \
  --out "$tmp_dir/missing-grouping-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-grouping-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-grouped-action-plan-missing"' "$tmp_dir/missing-grouping-quality/ios-report-quality.json"

missing_markdown_grouping_dir="$tmp_dir/missing-markdown-grouping"
mkdir -p "$missing_markdown_grouping_dir"
cp "$missing_grouping_dir/ios-performance.json" "$missing_markdown_grouping_dir/ios-performance.json"
python3 - <<'PY' "$missing_markdown_grouping_dir/ios-performance.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["groupedActionPlan"] = [
    {
        "ruleId": "performance-repeated-rule",
        "category": "SwiftUI Rendering",
        "title": "Repeated performance rule",
        "count": 4,
        "severity": "high",
        "firstLocations": ["Demo.swift:1"],
        "severityReason": "High because this repeated fixture represents a concrete high source signal.",
        "whyThisGroupMatters": "Repeated rows are noisy without grouped action guidance.",
        "firstExperiment": "Change one repeated fixture location, rerun report-quality, and stop if the grouped action is not clearer.",
        "validationRoute": "Run report-quality on this grouped fixture and inspect the grouped action table.",
        "stopCondition": "Stop once report-quality passes and the Markdown exposes grouped action proof fields.",
        "recommendedFirstMove": "Group repeated rules.",
        "proofGuidance": "Run report-quality on the fixture."
    }
]
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
cp "$missing_grouping_dir/ios-performance.md" "$missing_markdown_grouping_dir/ios-performance.md"
./bin/shipguard ios report-quality \
  --reports "$missing_markdown_grouping_dir" \
  --out "$tmp_dir/missing-markdown-grouping-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-markdown-grouping-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-grouping-missing"' "$tmp_dir/missing-markdown-grouping-quality/ios-report-quality.json"

missing_first_experiment_dir="$tmp_dir/missing-first-experiment"
mkdir -p "$missing_first_experiment_dir"
cp "$missing_markdown_grouping_dir/ios-performance.json" "$missing_first_experiment_dir/ios-performance.json"
python3 - <<'PY' "$missing_first_experiment_dir/ios-performance.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
for group in data["groupedActionPlan"]:
    group.pop("firstExperiment", None)
    group.pop("validationRoute", None)
    group.pop("stopCondition", None)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
cat > "$missing_first_experiment_dir/ios-performance.md" <<'MD'
# Missing First Experiment Performance Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Grouped Next Actions

| Rule | Count | First Locations | Why severity | Why this group matters | First move |
| --- | ---: | --- | --- | --- | --- |
| `performance-repeated-rule` | 4 | `Demo.swift:1` | High because this repeated fixture represents a concrete high source signal. | Repeated rows are noisy without grouped action guidance. | Group repeated rules. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_first_experiment_dir" \
  --out "$tmp_dir/missing-first-experiment-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-grouped-first-experiment-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-grouped-validation-route-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-grouped-stop-condition-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-first-experiment-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-validation-route-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-markdown-stop-condition-missing"' "$tmp_dir/missing-first-experiment-quality/ios-report-quality.json"

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
