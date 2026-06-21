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
grep -q '"runtimeEvidenceBoundary":' "$reports/performance/ios-performance.json"
grep -q '"evidence": "source heuristic"' "$reports/performance/ios-performance.json"
grep -q '"runtimeProof": "missing"' "$reports/performance/ios-performance.json"
grep -q '"blocking": "no"' "$reports/performance/ios-performance.json"
grep -q 'Runtime Evidence Boundary' "$reports/performance/ios-performance.md"
grep -q 'Evidence: `source heuristic`' "$reports/performance/ios-performance.md"
grep -q 'Runtime proof: `missing`' "$reports/performance/ios-performance.md"
grep -q 'Blocking: `no`' "$reports/performance/ios-performance.md"

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
grep -q '"fixtureCandidates":' "$tmp_dir/quality/ios-report-quality.json"
grep -q '# iOS ShipGuard Report Quality' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios performance' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios design' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'Actionability Questions' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'Fixture Candidates' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'local-path-shareability-warning' "$tmp_dir/quality/ios-report-quality.json"
grep -q '"redactionPlan":' "$tmp_dir/quality/ios-report-quality.json"
grep -q 'Redaction Plan' "$tmp_dir/quality/ios-report-quality.md"

./bin/shipguard ios report-quality \
  --reports "$reports" \
  --out "$tmp_dir/quality-eval" \
  --shipguard-eval >/dev/null
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/quality-eval/ios-report-quality.json"
grep -q '"explicitShipGuardEval": true' "$tmp_dir/quality-eval/ios-report-quality.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/quality-eval/ios-report-quality.json"
grep -q 'ShipGuard-eval mode: `yes`' "$tmp_dir/quality-eval/ios-report-quality.md"

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
grep -q '"shareableRedactions":' "$shareable_reports/design/ios-design.json"
if grep -R -E -q 'DemoShipGuardApp' "$shareable_reports/design"; then
  echo "shareable ShipGuard-eval design output must redact target identifiers" >&2
  exit 1
fi
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
./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/full-audit-plan" \
  --profile quick \
  --plan-only \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/full-audit-plan" \
  --out "$tmp_dir/full-audit-plan-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/full-audit-plan-fixtures" >/dev/null
python3 - <<'PY' "$tmp_dir/full-audit-plan-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
covered = {
    "Does the command preserve proof boundaries instead of pushing, publishing, or editing target apps?":
        "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries",
    "Does the full-audit report replace repeated manual validation ceremony with one resumable evidence lane?":
        "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated",
    "Are slow lanes summarized clearly enough for a solo developer to decide what to rerun?":
        "fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo",
    "Does the slash handoff come from the current NEXT_GOAL.md instead of stale hardcoded roadmap text?":
        "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren",
}
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected all full-audit actionability questions covered, got {priority!r}")
if priority.get("coveredQuestionCount") != len(covered):
    raise SystemExit(f"expected all covered question count, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
for question, path in covered.items():
    if not any(item.get("question") == question and item.get("publicFixturePath") == path for item in coverage):
        raise SystemExit(f"expected full-audit fixture coverage for {question!r}: {coverage!r}")
candidates = data.get("fixtureCandidates") or []
if candidates:
    raise SystemExit(f"expected no duplicate full-audit fixture candidates after coverage, got {candidates!r}")
PY
grep -q 'shipguard-full-audit-proof-boundary-fixture' "$tmp_dir/full-audit-plan-quality/ios-report-quality.json"

full_audit_proof_boundary_fixture="fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries"
./bin/shipguard ios report-quality \
  --reports "$full_audit_proof_boundary_fixture" \
  --out "$tmp_dir/full-audit-proof-boundary-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/full-audit-proof-boundary-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/full-audit-proof-boundary-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries"' "$tmp_dir/full-audit-proof-boundary-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/full-audit-proof-boundary-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/full-audit-proof-boundary-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard full-audit", item
assert item.get("fixtureType") == "shipguard-full-audit-proof-boundary-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries", item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-command-preserve-proof-boundaries", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

full_audit_evidence_lane_fixture="fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated"
./bin/shipguard ios report-quality \
  --reports "$full_audit_evidence_lane_fixture" \
  --out "$tmp_dir/full-audit-evidence-lane-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/full-audit-evidence-lane-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/full-audit-evidence-lane-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated"' "$tmp_dir/full-audit-evidence-lane-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/full-audit-evidence-lane-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/full-audit-evidence-lane-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard full-audit", item
assert item.get("fixtureType") == "shipguard-full-audit-proof-boundary-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated", item
assert "resumable evidence lane" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-full-audit-report-replace-repeated", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

full_audit_slow_lane_fixture="fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo"
./bin/shipguard ios report-quality \
  --reports "$full_audit_slow_lane_fixture" \
  --out "$tmp_dir/full-audit-slow-lane-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/full-audit-slow-lane-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/full-audit-slow-lane-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo"' "$tmp_dir/full-audit-slow-lane-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/full-audit-slow-lane-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/full-audit-slow-lane-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard full-audit", item
assert item.get("fixtureType") == "shipguard-full-audit-proof-boundary-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo", item
assert "slow lanes" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-are-slow-lanes-summarized-clearly-enough-fo", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

full_audit_slash_handoff_fixture="fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren"
./bin/shipguard ios report-quality \
  --reports "$full_audit_slash_handoff_fixture" \
  --out "$tmp_dir/full-audit-slash-handoff-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/full-audit-slash-handoff-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/full-audit-slash-handoff-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren"' "$tmp_dir/full-audit-slash-handoff-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/full-audit-slash-handoff-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/full-audit-slash-handoff-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard full-audit", item
assert item.get("fixtureType") == "shipguard-full-audit-proof-boundary-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren", item
assert "slash handoff" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-full-audit-does-the-slash-handoff-come-from-the-curren", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/inspect" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/inspect" \
  --out "$tmp_dir/inspect-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/inspect-fixtures" >/dev/null
python3 - <<'PY' "$tmp_dir/inspect-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
expected_covered = "Does InspectDeck make the next action obvious without hiding the source proof?"
expected_covered_missing = "Are missing inputs marked as missing instead of silently downgraded into confidence?"
expected_covered_evidence = "Can a maintainer jump from the summary to the underlying full-audit, value-gauntlet, release, and plugin evidence?"
expected_path = "fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious"
expected_missing_path = "fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o"
expected_evidence_path = "fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the"
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected all InspectDeck actionability questions covered, got {priority!r}")
if priority.get("coveredQuestionCount") != 3:
    raise SystemExit(f"expected three covered InspectDeck questions, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("question") == expected_covered and item.get("publicFixturePath") == expected_path for item in coverage):
    raise SystemExit(f"expected InspectDeck fixture coverage for next-action question: {coverage!r}")
if not any(item.get("question") == expected_covered_missing and item.get("publicFixturePath") == expected_missing_path for item in coverage):
    raise SystemExit(f"expected InspectDeck fixture coverage for missing-inputs question: {coverage!r}")
if not any(item.get("question") == expected_covered_evidence and item.get("publicFixturePath") == expected_evidence_path for item in coverage):
    raise SystemExit(f"expected InspectDeck fixture coverage for underlying-evidence question: {coverage!r}")
candidates = data.get("fixtureCandidates") or []
if candidates:
    raise SystemExit(f"expected no duplicate InspectDeck fixture candidates after coverage, got {candidates!r}")
PY
grep -q 'shipguard-inspect-proof-state-fixture' "$tmp_dir/inspect-quality/ios-report-quality.json"

inspect_next_action_fixture="fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious"
./bin/shipguard ios report-quality \
  --reports "$inspect_next_action_fixture" \
  --out "$tmp_dir/inspect-next-action-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/inspect-next-action-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/inspect-next-action-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious"' "$tmp_dir/inspect-next-action-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/inspect-next-action-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/inspect-next-action-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard inspect", item
assert item.get("fixtureType") == "shipguard-inspect-proof-state-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious", item
assert "InspectDeck" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-does-inspectdeck-make-the-next-action-obvious", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

inspect_missing_inputs_fixture="fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o"
./bin/shipguard ios report-quality \
  --reports "$inspect_missing_inputs_fixture" \
  --out "$tmp_dir/inspect-missing-inputs-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/inspect-missing-inputs-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/inspect-missing-inputs-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o"' "$tmp_dir/inspect-missing-inputs-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/inspect-missing-inputs-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/inspect-missing-inputs-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard inspect", item
assert item.get("fixtureType") == "shipguard-inspect-proof-state-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o", item
assert "missing inputs" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-are-missing-inputs-marked-as-missing-instead-o", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

inspect_underlying_evidence_fixture="fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the"
./bin/shipguard ios report-quality \
  --reports "$inspect_underlying_evidence_fixture" \
  --out "$tmp_dir/inspect-underlying-evidence-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/inspect-underlying-evidence-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/inspect-underlying-evidence-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the"' "$tmp_dir/inspect-underlying-evidence-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/inspect-underlying-evidence-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/inspect-underlying-evidence-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard inspect", item
assert item.get("fixtureType") == "shipguard-inspect-proof-state-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the", item
assert "underlying full-audit" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-inspect-can-a-maintainer-jump-from-the-summary-to-the", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

./bin/shipguard codex marketplace-readiness \
  --path . \
  --out "$tmp_dir/marketplace-readiness" \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/marketplace-readiness" \
  --out "$tmp_dir/marketplace-readiness-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/marketplace-readiness-fixtures" >/dev/null
python3 - <<'PY' "$tmp_dir/marketplace-readiness-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
covered_question = "Can a fresh Codex user understand what ShipGuard does from the README and plugin listing without prior private-app context?"
covered_path = "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und"
covered_plugin_question = "Can a maintainer prove plugin install freshness from tracked source, local marketplace, and strict status output?"
covered_plugin_path = "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu"
covered_submission_question = "Are icon, composer icon, screenshot policy, privacy notes, model-choice boundary, and proof commands ready for a public marketplace submission packet?"
covered_submission_path = "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr"
covered_docs_question = "Can docs/index.md guide first-time users without a long command dump or stale release wall?"
covered_docs_path = "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi"
covered_github_question = "Does the GitHub About/sidebar copy and social preview still match the latest published release without claiming unreleased v4 stability?"
covered_github_path = "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side"
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected MarketplaceDeck to be fully covered, got {priority!r}")
if priority.get("coveredQuestionCount") != 5:
    raise SystemExit(f"expected five covered MarketplaceDeck questions, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("question") == covered_question and item.get("publicFixturePath") == covered_path for item in coverage):
    raise SystemExit(f"expected MarketplaceDeck fresh-user fixture coverage: {coverage!r}")
if not any(item.get("question") == covered_plugin_question and item.get("publicFixturePath") == covered_plugin_path for item in coverage):
    raise SystemExit(f"expected MarketplaceDeck plugin-freshness fixture coverage: {coverage!r}")
if not any(item.get("question") == covered_submission_question and item.get("publicFixturePath") == covered_submission_path for item in coverage):
    raise SystemExit(f"expected MarketplaceDeck submission-packet fixture coverage: {coverage!r}")
if not any(item.get("question") == covered_docs_question and item.get("publicFixturePath") == covered_docs_path for item in coverage):
    raise SystemExit(f"expected MarketplaceDeck docs-index clarity fixture coverage: {coverage!r}")
if not any(item.get("question") == covered_github_question and item.get("publicFixturePath") == covered_github_path for item in coverage):
    raise SystemExit(f"expected MarketplaceDeck GitHub presentation fixture coverage: {coverage!r}")
if data.get("fixtureCandidates") != []:
    raise SystemExit(f"fully covered MarketplaceDeck should not create candidates: {data.get('fixtureCandidates')!r}")
PY
grep -q 'shipguard-marketplace-readiness-fixture' "$tmp_dir/marketplace-readiness-quality/ios-report-quality.json"

marketplace_fresh_user_fixture="fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und"
./bin/shipguard ios report-quality \
  --reports "$marketplace_fresh_user_fixture" \
  --out "$tmp_dir/marketplace-fresh-user-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/marketplace-fresh-user-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/marketplace-fresh-user-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und"' "$tmp_dir/marketplace-fresh-user-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/marketplace-fresh-user-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/marketplace-fresh-user-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard codex marketplace-readiness", item
assert item.get("fixtureType") == "shipguard-marketplace-readiness-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und", item
assert "fresh Codex user" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-fresh-codex-user-und", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

marketplace_plugin_freshness_fixture="fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu"
./bin/shipguard ios report-quality \
  --reports "$marketplace_plugin_freshness_fixture" \
  --out "$tmp_dir/marketplace-plugin-freshness-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/marketplace-plugin-freshness-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/marketplace-plugin-freshness-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu"' "$tmp_dir/marketplace-plugin-freshness-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/marketplace-plugin-freshness-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/marketplace-plugin-freshness-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard codex marketplace-readiness", item
assert item.get("fixtureType") == "shipguard-marketplace-readiness-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu", item
assert "plugin install freshness" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-a-maintainer-prove-plu", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

marketplace_submission_packet_fixture="fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr"
./bin/shipguard ios report-quality \
  --reports "$marketplace_submission_packet_fixture" \
  --out "$tmp_dir/marketplace-submission-packet-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/marketplace-submission-packet-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/marketplace-submission-packet-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr"' "$tmp_dir/marketplace-submission-packet-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/marketplace-submission-packet-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/marketplace-submission-packet-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard codex marketplace-readiness", item
assert item.get("fixtureType") == "shipguard-marketplace-readiness-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr", item
assert "submission packet" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-are-icon-composer-icon-scr", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

marketplace_docs_index_fixture="fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi"
./bin/shipguard ios report-quality \
  --reports "$marketplace_docs_index_fixture" \
  --out "$tmp_dir/marketplace-docs-index-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/marketplace-docs-index-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/marketplace-docs-index-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi"' "$tmp_dir/marketplace-docs-index-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/marketplace-docs-index-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/marketplace-docs-index-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard codex marketplace-readiness", item
assert item.get("fixtureType") == "shipguard-marketplace-readiness-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi", item
assert "docs/index.md" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-can-docs-index-md-guide-fi", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

marketplace_github_presentation_fixture="fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side"
./bin/shipguard ios report-quality \
  --reports "$marketplace_github_presentation_fixture" \
  --out "$tmp_dir/marketplace-github-presentation-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/marketplace-github-presentation-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/marketplace-github-presentation-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side"' "$tmp_dir/marketplace-github-presentation-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/marketplace-github-presentation-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/marketplace-github-presentation-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard codex marketplace-readiness", item
assert item.get("fixtureType") == "shipguard-marketplace-readiness-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side", item
assert "GitHub About/sidebar" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-codex-marketplace-readiness-does-the-github-about-side", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

./bin/shipguard docs-check . --out "$tmp_dir/docs-check-report" >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/docs-check-report" \
  --out "$tmp_dir/docs-check-report-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/docs-check-report-fixtures" >/dev/null
python3 - <<'PY' "$tmp_dir/docs-check-report-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected docs-check questions to be fully covered, got {priority!r}")
if priority.get("coveredQuestionCount") != 3:
    raise SystemExit(f"expected three covered docs-check questions, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
expected = {
    "Does docs-check expose a stable tool name and result summary when nested inside full-audit?": "fixtures/ios-report-quality/01-shipguard-docs-check-does-docs-check-expose-a-stable-tool-name-a",
    "Are broken local documentation links listed with file, link, and missing target?": "fixtures/ios-report-quality/02-shipguard-docs-check-are-broken-local-documentation-links-listed",
    "Does docs-check avoid implying external URLs or in-page anchors were verified?": "fixtures/ios-report-quality/03-shipguard-docs-check-does-docs-check-avoid-implying-external-url",
}
for question, path in expected.items():
    if not any(item.get("question") == question and item.get("publicFixturePath") == path for item in coverage):
        raise SystemExit(f"missing docs-check fixture coverage for {question!r}: {coverage!r}")
if data.get("fixtureCandidates") != []:
    raise SystemExit(f"fully covered docs-check should not create candidates: {data.get('fixtureCandidates')!r}")
PY

leaky_private="$tmp_dir/leaky-private"
cp -R "$shareable_reports/design" "$leaky_private"
python3 - <<'PY' "$leaky_private/ios-design.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.setdefault("sourceSummary", {})["targets"] = ["SecretApp", "SecretAppTests"]
data.setdefault("scanScope", data.get("sourceSummary", {}).get("scanScope", {}))
findings = data.setdefault("findings", [])
findings.insert(
    0,
    {
        "severity": "review",
        "category": "privacy",
        "ruleId": "synthetic-private-leak",
        "evidence": "SecretApp/Features/SecretCheckoutView.swift keeps a source snippet in shareable output",
        "recommendation": "Regenerate through the shareable redaction path.",
        "proof": "No private target identifiers remain.",
    },
)
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$leaky_private" \
  --out "$tmp_dir/leaky-private-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "private-identifier-shareability-risk"' "$tmp_dir/leaky-private-quality/ios-report-quality.json"
grep -q '"status": "blocked"' "$tmp_dir/leaky-private-quality/ios-report-quality.json"
if grep -R -q 'SecretApp' "$tmp_dir/leaky-private-quality"; then
  echo "report-quality must not echo private identifiers while reporting shareability risk" >&2
  exit 1
fi
broken_design="$tmp_dir/broken-design"
cp -R "$shareable_reports/design" "$broken_design"
python3 - <<'PY' "$broken_design/ios-design.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.pop("designTailoring", None)
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$broken_design" \
  --out "$tmp_dir/broken-design-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "design-tailoring-contract-missing"' "$tmp_dir/broken-design-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/broken-design-quality/ios-report-quality.json" "$tmp_dir/broken-design-quality/ios-report-quality.md"
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
markdown = Path(sys.argv[2]).read_text(encoding="utf-8")
next_command = data["resultUX"]["nextCommand"]
if not next_command.startswith("./bin/shipguard ios report-quality "):
    raise SystemExit(f"finding-fix nextCommand should be rerunnable report-quality CLI, got {next_command!r}")
if "`" in next_command:
    raise SystemExit(f"nextCommand must not contain Markdown backticks: {next_command!r}")
if "Next command: `Fix `" in markdown:
    raise SystemExit("Markdown next command must not wrap prose finding summaries as a command")
PY

broken_coherence="$tmp_dir/broken-coherence"
cp -R "$shareable_reports/design" "$broken_coherence"
python3 - <<'PY' "$broken_coherence/ios-design.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.pop("designCoherenceBoundary", None)
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$broken_coherence" \
  --out "$tmp_dir/broken-coherence-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "design-coherence-boundary-missing"' "$tmp_dir/broken-coherence-quality/ios-report-quality.json"

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
python3 - <<'PY' "$tmp_dir/actionability-quality/ios-report-quality.json" "$tmp_dir/actionability-quality/ios-report-quality.md"
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
markdown = Path(sys.argv[2]).read_text(encoding="utf-8")
next_command = data["resultUX"]["nextCommand"]
priority_command = data["priorityAction"]["nextCommand"]
if next_command != priority_command:
    raise SystemExit(f"priorityAction nextCommand drifted from resultUX: {priority_command!r} != {next_command!r}")
if not next_command.startswith("./bin/shipguard ios report-quality "):
    raise SystemExit(f"fixture-worthy actionability nextCommand should rerun report-quality, got {next_command!r}")
if "--write-fixture-candidates <fixture-output-dir>" not in next_command:
    raise SystemExit(f"fixture-worthy actionability nextCommand should materialize fixture candidates, got {next_command!r}")
if "`" in next_command:
    raise SystemExit(f"nextCommand must not contain Markdown backticks: {next_command!r}")
if "Next command: `Start with `" in markdown:
    raise SystemExit("Markdown next command must not wrap prose actionability questions as a command")
PY

broken_result_ux="$tmp_dir/broken-result-ux"
mkdir -p "$broken_result_ux"
cat > "$broken_result_ux/tool-value-gauntlet.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard value-gauntlet",
  "surface": "ShipGuard Tool Value Gauntlet",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "resultUX": {
    "status": "pass",
    "verdict": "PASS: Synthetic report completed.",
    "proofSource": "synthetic fixture",
    "whyItMatters": "The command field must stay executable.",
    "nextCommand": "Run value-gauntlet plus focused fixtures after reading this report.",
    "nextActionSummary": "Use the next exact proof slice."
  },
  "reportQualityQuestions": [
    "Does result UX keep prose action separate from the command template?"
  ]
}
JSON
cat > "$broken_result_ux/tool-value-gauntlet.md" <<'MD'
# Synthetic Value Gauntlet

## Result

- Verdict: PASS: Synthetic report completed.
- Proof source: synthetic fixture
- Why it matters: The command field must stay executable.
- Next command: `Run value-gauntlet plus focused fixtures after reading this report.`
- Next action: Use the next exact proof slice.

## Report Quality Questions

- Does result UX keep prose action separate from the command template?
MD
./bin/shipguard ios report-quality \
  --reports "$broken_result_ux" \
  --out "$tmp_dir/broken-result-ux-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/broken-result-ux-quality/ios-report-quality.json"
grep -q '"ruleId": "result-ux-next-command-not-command"' "$tmp_dir/broken-result-ux-quality/ios-report-quality.json"
grep -q 'resultUX.nextCommand is prose or Markdown instead of a command template' "$tmp_dir/broken-result-ux-quality/ios-report-quality.md"

stale_full_audit="$tmp_dir/stale-full-audit"
mkdir -p "$stale_full_audit"
cat > "$stale_full_audit/shipguard-full-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard full-audit",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "review",
  "resultUX": {
    "status": "review",
    "verdict": "REVIEW: Synthetic Full Audit report needs execution.",
    "proofSource": "stageStatusSummary + stage receipts",
    "whyItMatters": "Full Audit drives the release-loop handoff.",
    "nextCommand": "shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release",
    "nextActionSummary": "Execute the planned release lane."
  },
  "stageStatusSummary": {
    "planned": 14
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true,
    "doesNotPush": true,
    "doesNotPublishRelease": true
  },
  "reportQualityQuestions": [
    "Does Full Audit keep release-loop slash handoff text current?"
  ],
  "slashPlan": "/plan v3.132.0 v4 Product Release Stabilization for jlekerli-source/ShipGuard: prove external adoption evidence, final security review, rollback proof, package proof, and release proof consumption on published assets before any stable v4 claim.",
  "slashGoal": "/goal Implement v3.132.0 v4 Product Release Stabilization for jlekerli-source/ShipGuard: make the v4 product release externally adoptable, reversible, consumable, security-reviewed, and release-proof verified without claiming marketplace acceptance."
}
JSON
cat > "$stale_full_audit/shipguard-full-audit.md" <<'MD'
# ShipGuard Full Audit

## Result

- Verdict: REVIEW: Synthetic Full Audit report needs execution.
- Proof source: stageStatusSummary + stage receipts
- Why it matters: Full Audit drives the release-loop handoff.
- Next command: `shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release`
- Next action: Execute the planned release lane.

## Slash Plan

```text
/plan v3.132.0 v4 Product Release Stabilization for jlekerli-source/ShipGuard: prove external adoption evidence, final security review, rollback proof, package proof, and release proof consumption on published assets before any stable v4 claim.
```

## Slash Goal

```text
/goal Implement v3.132.0 v4 Product Release Stabilization for jlekerli-source/ShipGuard: make the v4 product release externally adoptable, reversible, consumable, security-reviewed, and release-proof verified without claiming marketplace acceptance.
```
MD
./bin/shipguard ios report-quality \
  --reports "$stale_full_audit" \
  --out "$tmp_dir/stale-full-audit-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/stale-full-audit-quality/ios-report-quality.json"
grep -q '"ruleId": "full-audit-slash-handoff-source-missing"' "$tmp_dir/stale-full-audit-quality/ios-report-quality.json"
grep -q '"ruleId": "full-audit-slash-handoff-stale"' "$tmp_dir/stale-full-audit-quality/ios-report-quality.json"
grep -q 'old v3.132 Full Audit slash handoff' "$tmp_dir/stale-full-audit-quality/ios-report-quality.md"

commandless_full_audit="$tmp_dir/commandless-full-audit"
mkdir -p "$commandless_full_audit"
cat > "$commandless_full_audit/shipguard-full-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard full-audit",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "review",
  "resultUX": {
    "status": "review",
    "verdict": "REVIEW: Synthetic Full Audit report needs execution.",
    "proofSource": "stageStatusSummary + stage receipts",
    "whyItMatters": "Full Audit drives the release-loop handoff.",
    "nextCommand": "shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release",
    "nextActionSummary": "Execute the planned release lane."
  },
  "stages": [
    {
      "stageId": "version",
      "title": "Version beacon",
      "status": "planned",
      "durationSeconds": 0.0,
      "purpose": "Confirm the CLI resolves.",
      "command": ["<shipguard-repo>/bin/shipguard", "version"]
    },
    {
      "stageId": "git-diff-check",
      "title": "Diff whitespace gate",
      "status": "planned",
      "durationSeconds": 0.0,
      "purpose": "Catch whitespace issues.",
      "command": ["git", "diff", "--check"]
    }
  ],
  "stageStatusSummary": {
    "planned": 2
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true,
    "doesNotPush": true,
    "doesNotPublishRelease": true
  },
  "reportQualityQuestions": [
    "Can a maintainer run the planned release lane from the Markdown?"
  ],
  "slashHandoffSource": {
    "status": "loaded",
    "sourcePath": "NEXT_GOAL.md",
    "section": "following"
  },
  "slashPlan": "/plan v3.147.0 Stable V4 Release Packet Execution Receipts for jlekerli-source/ShipGuard: make execution receipts copy-ready.",
  "slashGoal": "/goal Implement v3.147.0 Stable V4 Release Packet Execution Receipts for jlekerli-source/ShipGuard: make execution receipts copy-ready."
}
JSON
cat > "$commandless_full_audit/shipguard-full-audit.md" <<'MD'
# ShipGuard Full Audit

## Result

- Verdict: REVIEW: Synthetic Full Audit report needs execution.
- Proof source: stageStatusSummary + stage receipts
- Why it matters: Full Audit drives the release-loop handoff.
- Next command: `shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release`
- Next action: Execute the planned release lane.

## Stages

| Status | Stage | Duration | Purpose |
| --- | --- | ---: | --- |
| planned | `version` Version beacon | 0.0s | Confirm the CLI resolves. |
| planned | `git-diff-check` Diff whitespace gate | 0.0s | Catch whitespace issues. |

## Slash Handoff Source

- Status: `loaded`
- Source path: `NEXT_GOAL.md`
- Section: `following`
MD
./bin/shipguard ios report-quality \
  --reports "$commandless_full_audit" \
  --out "$tmp_dir/commandless-full-audit-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/commandless-full-audit-quality/ios-report-quality.json"
grep -q '"ruleId": "full-audit-execution-commands-markdown-missing"' "$tmp_dir/commandless-full-audit-quality/ios-report-quality.json"
grep -q 'Render an Execution Commands table from stages' "$tmp_dir/commandless-full-audit-quality/ios-report-quality.md"

design_tailoring_fixture="fixtures/ios-report-quality/design-app-type-tailoring"
./bin/shipguard ios report-quality \
  --reports "$design_tailoring_fixture" \
  --out "$tmp_dir/design-tailoring-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/design-tailoring-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/design-tailoring-quality/ios-report-quality.json"
grep -q '"designTailoring":' "$design_tailoring_fixture/fixture-report.json"
grep -q 'Design Tailoring Contract' "$design_tailoring_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/design-tailoring-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"design tailoring fixture should not recurse: {data['fixtureCandidates']!r}")
PY

design_coherence_fixture="fixtures/ios-report-quality/design-coherence-boundary"
./bin/shipguard ios report-quality \
  --reports "$design_coherence_fixture" \
  --out "$tmp_dir/design-coherence-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/design-coherence-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/design-coherence-quality/ios-report-quality.json"
grep -q '"designCoherenceBoundary":' "$design_coherence_fixture/fixture-report.json"
grep -q '"targetRemediationStatus": "not-authorized-from-this-run"' "$design_coherence_fixture/fixture-report.json"
grep -q 'Design Coherence Boundary' "$design_coherence_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/design-coherence-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"design coherence fixture should not recurse: {data['fixtureCandidates']!r}")
PY

preview_devspace_fixture="fixtures/ios-report-quality/preview-devspace-routing"
./bin/shipguard ios report-quality \
  --reports "$preview_devspace_fixture" \
  --out "$tmp_dir/preview-devspace-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/preview-devspace-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/preview-devspace-quality/ios-report-quality.json"
grep -q '"previewEvidence":' "$preview_devspace_fixture/fixture-report.json"
grep -q 'shipguard ios preview' "$preview_devspace_fixture/fixture-report.json"
grep -q 'shipguard ios devspace' "$preview_devspace_fixture/fixture-report.json"
grep -q 'Preview And Devspace' "$preview_devspace_fixture/fixture-report.md"
grep -q 'model selection happens in ChatGPT' "$preview_devspace_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/preview-devspace-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"preview/devspace fixture should not recurse: {data['fixtureCandidates']!r}")
PY

broken_preview_routing="$tmp_dir/broken-preview-routing"
cp -R "$preview_devspace_fixture" "$broken_preview_routing"
python3 - <<'PY' "$broken_preview_routing/fixture-report.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.pop("previewEvidence", None)
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$broken_preview_routing" \
  --out "$tmp_dir/broken-preview-routing-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/broken-preview-routing-quality/ios-report-quality.json"
grep -q '"ruleId": "design-preview-evidence-missing"' "$tmp_dir/broken-preview-routing-quality/ios-report-quality.json"

./bin/shipguard brand \
  --path . \
  --out "$tmp_dir/brand-report" \
  --strict >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/brand-report" \
  --out "$tmp_dir/brand-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/brand-quality/ios-report-quality.json"
grep -q '"tool": "shipguard brand"' "$tmp_dir/brand-quality/ios-report-quality.json"
grep -q '"kind": "answer-actionability-question"' "$tmp_dir/brand-quality/ios-report-quality.json"
grep -q 'Does every public ShipGuard surface have a branded name' "$tmp_dir/brand-quality/ios-report-quality.json"
grep -q 'ShipGuard Brand Deck' "$tmp_dir/brand-report/ios-branding.md"
grep -q 'Report Quality Questions' "$tmp_dir/brand-report/ios-branding.md"
grep -q 'Actionability Questions' "$tmp_dir/brand-quality/ios-report-quality.md"
grep -q 'Does every public ShipGuard surface have a branded name' "$tmp_dir/brand-quality/ios-report-quality.md"
if grep -q 'add-actionability-questions' "$tmp_dir/brand-quality/ios-report-quality.json"; then
  echo "Brand Deck reports must carry concrete actionability questions into report-quality" >&2
  exit 1
fi

launchdeck_receipt_fixture="fixtures/ios-report-quality/launchdeck-receipts"
./bin/shipguard ios report-quality \
  --reports "$launchdeck_receipt_fixture" \
  --out "$tmp_dir/launchdeck-receipt-quality" \
  --write-fixture-candidates "$tmp_dir/launchdeck-receipt-fixtures" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.json"
grep -q '"fixtureType": "ios-launchdeck-receipt-quality-fixture"' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.json"
grep -q '"kind": "answer-actionability-question"' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("status") != "pass":
    raise SystemExit(f"expected report-quality status to stay pass, got {data.get('status')!r}")
visibility = data.get("sourceIssueVisibility") or {}
if visibility.get("sourceFindingCount") != 2:
    raise SystemExit(f"expected two visible source findings, got {visibility!r}")
if visibility.get("reportsWithSourceFindings") != 1:
    raise SystemExit(f"expected one source report with findings, got {visibility!r}")
source_rules = {item.get("ruleId") for item in data.get("sourceFindings") or []}
expected_rules = {
    "launchdeck-build-run-receipt-missing",
    "launchdeck-performance-receipt-missing",
}
if not expected_rules.issubset(source_rules):
    raise SystemExit(f"source findings did not preserve receipt rules: {source_rules!r}")
if data.get("findings"):
    raise SystemExit(f"source findings must not be mixed into report-quality findings: {data['findings']!r}")
priority = data["priorityAction"]
expected = "When receipts are supplied, does it name missing build/run, UI, preview, log, or profiler proof for the selected lane?"
if priority.get("question") != expected:
    raise SystemExit(f"expected receipt-focused priority action, got {priority!r}")
candidate = (data.get("fixtureCandidates") or [None])[0]
if not candidate:
    raise SystemExit("expected launchdeck receipt fixture candidate")
if candidate.get("fixtureType") != "ios-launchdeck-receipt-quality-fixture":
    raise SystemExit(f"unexpected fixture type: {candidate!r}")
if candidate.get("sourceQuestion") != expected:
    raise SystemExit(f"unexpected source question: {candidate!r}")
if not str(candidate.get("publicFixturePath", "")).startswith("fixtures/ios-report-quality/"):
    raise SystemExit(f"unexpected fixture path: {candidate!r}")
PY
grep -q 'ios-launchdeck-receipt-quality-fixture' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.md"
grep -q 'missing build/run' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.md"
grep -q 'Source Report Findings' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.md"
grep -q 'launchdeck-build-run-receipt-missing' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.md"
grep -q 'launchdeck-performance-receipt-missing' "$tmp_dir/launchdeck-receipt-quality/ios-report-quality.md"
test -f "$tmp_dir/launchdeck-receipt-fixtures/fixture-promotion-manifest.json"
launchdeck_materialized_candidate_dir="$(find "$tmp_dir/launchdeck-receipt-fixtures" -mindepth 1 -maxdepth 1 -type d -name '*shipguard-ios-launchdeck*' | sort | head -n 1)"
test -n "$launchdeck_materialized_candidate_dir"
test -f "$launchdeck_materialized_candidate_dir/fixture-report.json"
grep -q '"sourceReportsRedacted": true' "$launchdeck_materialized_candidate_dir/fixture-candidate.json"

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
  "runtimeEvidenceBoundary": {
    "evidence": "source heuristic",
    "confidence": "medium",
    "runtimeProof": "missing",
    "blocking": "no",
    "interpretation": "Source-only findings nominate review and proof candidates; they do not prove actual CPU, GPU, memory, energy, hitch, FPS, or frame-rate problems.",
    "promotionRule": "Promote only after same-route runtime proof confirms the issue shape.",
    "requiredRuntimeProof": [
      "Same-route Simulator trace, sample, or log evidence for local-only claims.",
      "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims."
    ]
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

## Runtime Evidence Boundary

- Evidence: `source heuristic`
- Confidence: `medium`
- Runtime proof: `missing`
- Blocking: `no`
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
  "appType": {
    "value": "education",
    "inferred": "education",
    "override": null,
    "confidence": 0.78,
    "scores": {
      "education": 25,
      "utility": 4
    },
    "signals": [
      {
        "appType": "education",
        "token": "lesson",
        "file": "Sources/SyntheticDesignFixture/LearningFlow.swift",
        "count": 12
      }
    ]
  },
  "designTailoring": {
    "tailoredFor": "education",
    "guidanceProfile": "learning-progress",
    "universalDefaultsRejected": true,
    "sourceSignalSummary": "lesson->education",
    "sourceSignals": [
      {
        "appType": "education",
        "token": "lesson",
        "file": "Sources/SyntheticDesignFixture/LearningFlow.swift",
        "count": 12
      }
    ],
    "dimensions": {
      "motion": {
        "stance": "production-polish",
        "reason": "Motion should clarify learning state.",
        "observedSignals": {
          "withAnimation": 2
        }
      },
      "haptics": {
        "tone": "encouraging, milestone-aware, and interruption-sparse",
        "deviceProofRequired": true,
        "observedSignals": {
          "uikitFeedbackSignals": 1
        }
      },
      "visualDensity": {
        "stance": "allow expressive hierarchy with proof",
        "observedSignals": {
          "rounded": 4
        }
      },
      "copyTone": {
        "stance": "specific to the app task and audience",
        "visibleStringCount": 4,
        "localizationSignals": 1
      }
    },
    "nextAction": {
      "owner": "developer",
      "kind": "manual-proof",
      "manualProof": "Review one synthetic learning flow for app-type fit.",
      "expectedArtifact": "One preview receipt plus a note mapping the learning-progress profile to source signals.",
      "successCondition": "The report uses education guidance and avoids utility-only advice.",
      "failureMeaning": "The design report remains an inventory, not app-type-specific design QA."
    },
    "risk": "Generic utility restraint can make learning feedback feel flat."
  },
  "designCoherenceBoundary": {
    "purpose": "Keep design-system coherence findings as ShipGuard product-QA evidence until target-app work is separately authorized.",
    "sourceInventory": {
      "appType": "education",
      "colorSignals": 4,
      "typographySignals": 2,
      "componentSignals": {
        "Button": 1
      },
      "visualEffectSignals": {
        "rounded": 4
      },
      "motionSignals": {
        "withAnimation": 2
      },
      "hapticSignals": {
        "uikitFeedbackSignals": 1
      },
      "copySignals": {
        "visibleStringCount": 4,
        "localizationSignals": 1
      },
      "iconographySignals": {
        "sfSymbolSignals": 2
      }
    },
    "coherenceRisks": [],
    "separationChecks": {
      "inventoryIsNotRemediation": true,
      "coherenceRiskIsNotTargetTask": true,
      "shipguardActionIsPublicFixtureOrRule": true,
      "appWorkRequiresSeparateAuthorization": true
    },
    "shipguardNextAction": {
      "owner": "ShipGuard maintainer",
      "kind": "public-fixture-or-report-rule",
      "sourceQuestion": "Did it separate design-system coherence findings from target-app implementation work?",
      "expectedArtifact": "A public synthetic report-quality fixture or rule update.",
      "successCondition": "Report-quality keeps design coherence evidence separate from target-app tasks.",
      "failureMeaning": "Design QA evidence can still become target-app remediation advice."
    },
    "appWorkAuthorization": {
      "status": "not-authorized-from-this-run",
      "requiresExplicitRequest": true,
      "forbiddenActions": [
        "Do not edit the scanned app from this report."
      ],
      "allowedShipGuardActions": [
        "Improve ShipGuard report fields, Markdown, rules, docs, plugin guidance, or public fixtures."
      ]
    },
    "proofBoundary": {
      "localProof": "Run report-quality on this fixture.",
      "manualProof": "Separate app-work authorization is required for target-app edits.",
      "expectedArtifact": "ios-report-quality.json"
    },
    "targetRemediationStatus": "not-authorized-from-this-run"
  },
  "findings": [],
  "reportQualityQuestions": [
    "Did report wording keep target-app remediation separate from ShipGuard product QA next steps?",
    "Should design DNA evidence include enough app-type context for a public fixture?",
    "Should Ringly private app evidence become a public fixture?"
  ]
}
JSON
cat > "$dedupe_fixture/ios-design.md" <<'MD'
# Design Dedupe Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.

## Design Tailoring Contract

- Tailored for: `education`
- Guidance profile: `learning-progress`
- Universal defaults rejected: `true`
- Source signals: lesson->education
- Owner: `developer`
- Manual proof: Review one synthetic learning flow for app-type fit.
- Expected artifact: One preview receipt plus a note mapping the learning-progress profile to source signals.
- Success condition: The report uses education guidance and avoids utility-only advice.
- Failure meaning: The design report remains an inventory, not app-type-specific design QA.

## Design Coherence Boundary

- Purpose: Keep design-system coherence findings as ShipGuard product-QA evidence until target-app work is separately authorized.
- Source inventory app type: `education`
- Coherence risks: 0
- Inventory is not remediation: `true`
- Coherence risk is not target task: `true`
- ShipGuard action is public fixture or rule: `true`
- App work requires separate authorization: `true`
- Target remediation status: `not-authorized-from-this-run`

ShipGuard next action:
- Owner: `ShipGuard maintainer`
- Kind: `public-fixture-or-report-rule`
- Source question: Did it separate design-system coherence findings from target-app implementation work?
- Expected artifact: A public synthetic report-quality fixture or rule update.
- Success condition: Report-quality keeps design coherence evidence separate from target-app tasks.
- Failure meaning: Design QA evidence can still become target-app remediation advice.

App work authorization:
- Status: `not-authorized-from-this-run`
- Requires explicit request: `true`

Proof boundary:
- Local proof: Run report-quality on this fixture.
- Manual proof: Separate app-work authorization is required for target-app edits.
- Expected artifact: ios-report-quality.json
MD
./bin/shipguard ios report-quality \
  --reports "$dedupe_fixture" \
  --out "$tmp_dir/dedupe-quality" \
  --write-fixture-candidates "$tmp_dir/materialized-fixtures" \
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
fixture_candidates = data.get("fixtureCandidates") or []
if not fixture_candidates:
    raise SystemExit("expected fixture candidates for fixture-focused questions")
candidate_questions = [item["sourceQuestion"] for item in fixture_candidates]
if "Which grouped performance observation should become a public fixture?" not in candidate_questions:
    raise SystemExit(f"missing performance fixture candidate: {candidate_questions!r}")
if "Should design DNA evidence include enough app-type context for a public fixture?" not in candidate_questions:
    raise SystemExit(f"missing design fixture candidate: {candidate_questions!r}")
for candidate in fixture_candidates:
    if not str(candidate.get("publicFixturePath", "")).startswith("fixtures/ios-report-quality/"):
        raise SystemExit(f"unexpected public fixture path: {candidate!r}")
    materialization = candidate.get("materialization") or {}
    if materialization.get("safeSyntheticOnly") is not True:
        raise SystemExit(f"missing safe materialization flag: {candidate!r}")
    if "fixture-report.json" not in materialization.get("files", []):
        raise SystemExit(f"missing materialized fixture file list: {candidate!r}")
    if "private app report only to choose the shape" not in candidate.get("privateDataPolicy", ""):
        raise SystemExit(f"missing private data policy: {candidate!r}")
PY
grep -q 'Fixture Candidates' "$tmp_dir/dedupe-quality/ios-report-quality.md"
grep -q 'Fixture Materialization' "$tmp_dir/dedupe-quality/ios-report-quality.md"
grep -q 'fixtures/ios-report-quality/' "$tmp_dir/dedupe-quality/ios-report-quality.md"
test -f "$tmp_dir/materialized-fixtures/fixture-candidates-index.json"
test -f "$tmp_dir/materialized-fixtures/fixture-promotion-manifest.json"
test -f "$tmp_dir/materialized-fixtures/PROMOTION.md"
test -f "$tmp_dir/materialized-fixtures/README.md"
grep -q 'Fixture Promotion Guide' "$tmp_dir/materialized-fixtures/PROMOTION.md"
grep -q 'fixtures/ios-report-quality/' "$tmp_dir/materialized-fixtures/PROMOTION.md"
python3 - <<'PY' "$tmp_dir/materialized-fixtures/fixture-promotion-manifest.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("candidateCount", 0) < 1:
    raise SystemExit(f"expected promotion candidates: {data!r}")
candidate = data["candidates"][0]
path = candidate.get("suggestedFixturePath") or ""
if not path.startswith("fixtures/ios-report-quality/"):
    raise SystemExit(f"unexpected suggested fixture path: {candidate!r}")
copy_commands = "\n".join(candidate.get("copyCommands") or [])
if "<materialized-candidate-dir>" not in copy_commands:
    raise SystemExit(f"copy commands must use path-safe placeholder: {candidate!r}")
local_home_pattern = "/" + "Users/"
if "/tmp/" in copy_commands or local_home_pattern in copy_commands:
    raise SystemExit(f"copy commands leaked local path: {candidate!r}")
validation_commands = "\n".join(candidate.get("validationCommands") or [])
if "ios report-quality" not in validation_commands or "./tests/ios_report_quality_test.sh" not in validation_commands:
    raise SystemExit(f"missing validation commands: {candidate!r}")
checklist = " ".join(candidate.get("reviewChecklist") or []).lower()
if "no private app code" not in checklist:
    raise SystemExit(f"missing private-data review checklist: {candidate!r}")
PY
materialized_candidate_dir="$(find "$tmp_dir/materialized-fixtures" -mindepth 1 -maxdepth 1 -type d | sort | head -n 1)"
test -n "$materialized_candidate_dir"
materialized_candidate_name="$(basename "$materialized_candidate_dir")"
case "$materialized_candidate_name" in
  *shipguard-ios-*|*shipguard-value-gauntlet*) ;;
  *)
    echo "materialized fixture candidate should use a descriptive tool/question slug, got $materialized_candidate_name" >&2
    exit 1
    ;;
esac
case "$materialized_candidate_name" in
  *shipguard-eval-boundary-fixture|*report-quality-actionability-fixture)
    echo "materialized fixture candidate should not collapse to a generic fixture type slug: $materialized_candidate_name" >&2
    exit 1
    ;;
esac
test -f "$materialized_candidate_dir/README.md"
test -f "$materialized_candidate_dir/fixture-candidate.json"
test -f "$materialized_candidate_dir/fixture-report.json"
test -f "$materialized_candidate_dir/fixture-report.md"
grep -q '"sourceReportsRedacted": true' "$materialized_candidate_dir/fixture-candidate.json"
grep -q '"promotion":' "$materialized_candidate_dir/fixture-candidate.json"
grep -q '"suggestedFixturePath": "fixtures/ios-report-quality/' "$materialized_candidate_dir/fixture-candidate.json"
grep -q '## Promotion' "$materialized_candidate_dir/README.md"
grep -q '"tool": "shipguard ios ' "$materialized_candidate_dir/fixture-report.json"
grep -q '"shipguardOnly": true' "$materialized_candidate_dir/fixture-report.json"
grep -q '"targetAppsReadOnly": true' "$materialized_candidate_dir/fixture-report.json"
grep -q 'Synthetic Report-Quality Fixture' "$materialized_candidate_dir/fixture-report.md"
materialized_performance_candidate_dir="$(find "$tmp_dir/materialized-fixtures" -mindepth 1 -maxdepth 1 -type d -name '*ios-performance*' | sort | head -n 1)"
test -n "$materialized_performance_candidate_dir"
grep -q '"groupedActionPlan":' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"evidencePromotion":' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"promotionStatus": "missing-runtime-proof"' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"expectedArtifact":' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"successCondition":' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"failureMeaning":' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q '"ruleId": "swiftui-repeat-forever-animation"' "$materialized_performance_candidate_dir/fixture-report.json"
grep -q 'Evidence Promotion Contract' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Expected artifact' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Success condition' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Failure meaning' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Grouped Next Actions' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'First experiment' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Validation route' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Stop condition' "$materialized_performance_candidate_dir/fixture-report.md"
grep -q 'Proof Boundaries' "$materialized_performance_candidate_dir/fixture-report.md"
collision_fixture="$tmp_dir/candidate-collision"
mkdir -p "$collision_fixture"
cat > "$collision_fixture/report.json" <<'JSON'
{
  "tool": "shipguard v4 stable-publication",
  "status": "review",
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  },
  "reportQualityQuestions": [
    "Does the stable-publication collision probe keep a long same-prefix fixture candidate unique for release template evidence alpha?",
    "Does the stable-publication collision probe keep a long same-prefix fixture candidate unique for release template evidence beta?"
  ]
}
JSON
cat > "$collision_fixture/report.md" <<'MD'
# Synthetic stable-publication candidate collision report
MD
./bin/shipguard ios report-quality \
  --reports "$collision_fixture" \
  --out "$tmp_dir/candidate-collision-quality" \
  --write-fixture-candidates "$tmp_dir/candidate-collision-fixtures" \
  --shareable >/dev/null
python3 - <<'PY' "$tmp_dir/candidate-collision-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
candidates = data.get("fixtureCandidates") or []
ids = [item.get("candidateId") for item in candidates]
paths = [item.get("publicFixturePath") for item in candidates]
if len(ids) != 2:
    raise SystemExit(f"expected two stable-publication candidates, got {ids!r}")
if len(set(ids)) != len(ids):
    raise SystemExit(f"candidate ids must stay unique for long same-prefix questions: {ids!r}")
if len(set(paths)) != len(paths):
    raise SystemExit(f"candidate paths must stay unique for long same-prefix questions: {paths!r}")
if not all(str(item).startswith(("01-shipguard-v4-stable-publication-", "02-shipguard-v4-stable-publication-")) for item in ids):
    raise SystemExit(f"candidate ids should keep a readable stable-publication prefix: {ids!r}")
suffixes = [str(item).rsplit("-", 1)[-1] for item in ids]
if not all(len(suffix) == 8 and all(char in "0123456789abcdef" for char in suffix) for suffix in suffixes):
    raise SystemExit(f"expected hash-suffixed long candidate ids: {ids!r}")
PY
materialized_design_candidate_dir="$(find "$tmp_dir/materialized-fixtures" -mindepth 1 -maxdepth 1 -type d -name '*ios-design*' | sort | head -n 1)"
test -n "$materialized_design_candidate_dir"
grep -q '"designTailoring":' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"designCoherenceBoundary":' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"tailoredFor": "education"' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"guidanceProfile": "learning-progress"' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"universalDefaultsRejected": true' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"targetRemediationStatus": "not-authorized-from-this-run"' "$materialized_design_candidate_dir/fixture-report.json"
grep -q '"expectedArtifact":' "$materialized_design_candidate_dir/fixture-report.json"
grep -q 'Design Tailoring Contract' "$materialized_design_candidate_dir/fixture-report.md"
grep -q 'Design Coherence Boundary' "$materialized_design_candidate_dir/fixture-report.md"
grep -q 'App work authorization' "$materialized_design_candidate_dir/fixture-report.md"
grep -q 'Universal defaults rejected' "$materialized_design_candidate_dir/fixture-report.md"
./bin/shipguard ios report-quality \
  --reports "$materialized_candidate_dir" \
  --out "$tmp_dir/materialized-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/materialized-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/materialized-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"materialized synthetic fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions:
    raise SystemExit("materialized synthetic fixture should still preserve actionability questions")
if questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"materialized source flag missing: {questions[0]!r}")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/materialized-fixtures" \
  --out "$tmp_dir/materialized-root-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/materialized-root-quality/ios-report-quality.json"
grep -q '"fixturePromotionManifests":' "$tmp_dir/materialized-root-quality/ios-report-quality.json"
grep -q '"path": "<report-input-1>/fixture-promotion-manifest.json"' "$tmp_dir/materialized-root-quality/ios-report-quality.json"
grep -q 'Fixture Promotion Manifests' "$tmp_dir/materialized-root-quality/ios-report-quality.md"
if grep -q 'self-report-skipped' "$tmp_dir/materialized-root-quality/ios-report-quality.json"; then
  echo "promotion manifests must be consumed as metadata, not graded as report-quality reports" >&2
  exit 1
fi
python3 - <<'PY' "$tmp_dir/materialized-root-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
manifest_rows = data.get("fixturePromotionManifests") or []
if not manifest_rows:
    raise SystemExit("expected fixturePromotionManifests metadata")
if manifest_rows[0].get("status") != "pass":
    raise SystemExit(f"expected clean promotion manifest to pass: {manifest_rows!r}")
if manifest_rows[0].get("issueCount") != 0:
    raise SystemExit(f"unexpected promotion manifest issues: {manifest_rows!r}")
if any(report.get("tool") == "shipguard ios report-quality" for report in data.get("reports", [])):
    raise SystemExit(f"promotion manifest was graded as a source report: {data.get('reports')!r}")
PY
preview_design_report="$tmp_dir/preview-design-report"
mkdir -p "$preview_design_report"
cat > "$preview_design_report/ios-design.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard ios design",
  "intent": "shipguard-evaluation",
  "status": "review",
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  },
  "appType": {
    "value": "education"
  },
  "designTailoring": {
    "tailoredFor": "education",
    "guidanceProfile": "learning-progress",
    "sourceSignals": [],
    "dimensions": {},
    "nextAction": {
      "expectedArtifact": "preview receipt"
    }
  },
  "designCoherenceBoundary": {
    "targetRemediationStatus": "not-authorized-from-this-run"
  },
  "findings": [],
  "reportQualityQuestions": [
    "Did preview and Devspace guidance make the iPhone visual proof path obvious?"
  ]
}
JSON
cat > "$preview_design_report/ios-design.md" <<'MD'
# iOS Design Audit

## ShipGuard Evaluation Boundary

Do not edit the scanned app.

## Design Tailoring Contract

Tailored for education.

## Design Coherence Boundary

Target remediation status is not authorized from this run.

## Report Quality Questions

- Did preview and Devspace guidance make the iPhone visual proof path obvious?
MD
./bin/shipguard ios report-quality \
  --reports "$preview_design_report" \
  --out "$tmp_dir/preview-design-quality" \
  --write-fixture-candidates "$tmp_dir/preview-design-fixtures" \
  --shareable >/dev/null
grep -q '"ruleId": "design-preview-evidence-missing"' "$tmp_dir/preview-design-quality/ios-report-quality.json"
grep -q '"fixtureCoverage":' "$tmp_dir/preview-design-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/preview-devspace-routing"' "$tmp_dir/preview-design-quality/ios-report-quality.json"
grep -q 'Fixture Coverage' "$tmp_dir/preview-design-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/preview-design-quality/ios-report-quality.json" "$tmp_dir/preview-design-fixtures"
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
fixture_root = Path(sys.argv[2])
if data.get("fixtureCandidates"):
    raise SystemExit(f"covered preview/devspace question should not emit duplicate fixture candidates: {data['fixtureCandidates']!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("publicFixturePath") == "fixtures/ios-report-quality/preview-devspace-routing" for item in coverage):
    raise SystemExit(f"preview/devspace fixture coverage missing: {coverage!r}")
candidate_dirs = [p for p in fixture_root.iterdir() if p.is_dir()]
if candidate_dirs:
    raise SystemExit(f"covered preview/devspace question should not materialize duplicate candidate dirs: {candidate_dirs!r}")
PY
./bin/shipguard ios report-quality \
  --reports fixtures/ios-report-quality/design-observation-promotion \
  --out "$tmp_dir/design-observation-quality" \
  --write-fixture-candidates "$tmp_dir/design-observation-fixtures" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/design-observation-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/design-observation-promotion"' "$tmp_dir/design-observation-quality/ios-report-quality.json"
grep -q 'Fixture Coverage' "$tmp_dir/design-observation-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/design-observation-quality/ios-report-quality.json" "$tmp_dir/design-observation-fixtures"
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
fixture_root = Path(sys.argv[2])
if data.get("fixtureCandidates"):
    raise SystemExit(f"covered design observation question should not emit duplicate fixture candidates: {data['fixtureCandidates']!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("publicFixturePath") == "fixtures/ios-report-quality/design-observation-promotion" for item in coverage):
    raise SystemExit(f"design observation fixture coverage missing: {coverage!r}")
candidate_dirs = [p for p in fixture_root.iterdir() if p.is_dir()]
if candidate_dirs:
    raise SystemExit(f"covered design observation question should not materialize duplicate candidate dirs: {candidate_dirs!r}")
PY
broken_materialized="$tmp_dir/broken-materialized-fixtures"
cp -R "$tmp_dir/materialized-fixtures" "$broken_materialized"
python3 - <<'PY' "$broken_materialized/fixture-promotion-manifest.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["candidates"][0]["suggestedFixturePath"] = "../unsafe-fixture"
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$broken_materialized" \
  --out "$tmp_dir/broken-materialized-quality" \
  --shareable >/dev/null
grep -q '"status": "blocked"' "$tmp_dir/broken-materialized-quality/ios-report-quality.json"
grep -q '"ruleId": "fixture-promotion-path-unsafe"' "$tmp_dir/broken-materialized-quality/ios-report-quality.json"
grep -q 'Fixture Promotion Manifests' "$tmp_dir/broken-materialized-quality/ios-report-quality.md"
if grep -R -F -q "$tmp_dir" "$tmp_dir/dedupe-quality"; then
  echo "shareable fixture-candidate output must not include local absolute temp paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir" "$tmp_dir/materialized-fixtures"; then
  echo "materialized fixture candidates must not include local absolute temp paths" >&2
  exit 1
fi
if grep -R -E -q 'Ringly|Ilmify|InweFi' "$tmp_dir/materialized-fixtures"; then
  echo "materialized fixture candidates must not include private app identifiers" >&2
  exit 1
fi
if grep -q 'local-path-shareability-warning' "$tmp_dir/shareable-quality/ios-report-quality.json"; then
  echo "shareable report-quality output should not add local-path warnings for shareable inputs" >&2
  exit 1
fi

materialized_public_fixture="fixtures/ios-report-quality/materialized-external-audit"
./bin/shipguard ios report-quality \
  --reports "$materialized_public_fixture" \
  --out "$tmp_dir/materialized-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/materialized-public-quality/ios-report-quality.json"
grep -q 'Which deferred external capability should become a public fixture before ShipGuard adopts it?' "$tmp_dir/materialized-public-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/materialized-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"public materialized fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions or questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"public materialized fixture should retain sourceMaterializedFixture question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$materialized_public_fixture"; then
  echo "public materialized fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_public_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-should-this-recurring-lean-code-ob-f228f086"
./bin/shipguard ios report-quality \
  --reports "$lean_public_fixture" \
  --out "$tmp_dir/lean-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-public-quality/ios-report-quality.json"
grep -q 'Should this recurring lean-code observation become a public fixture instead of depending on one current repo scan?' "$tmp_dir/lean-public-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/lean-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck public fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_public_fixture"; then
  echo "Lean Deck public fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_priority_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-precisionreview-identify-dele-286dc4bb"
./bin/shipguard ios report-quality \
  --reports "$lean_priority_fixture" \
  --out "$tmp_dir/lean-priority-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-priority-public-quality/ios-report-quality.json"
grep -q 'Does precisionReview identify delete, simplify, keep, and proof-blocked decisions instead of dumping findings?' "$tmp_dir/lean-priority-public-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/lean-priority-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck priority public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck priority fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_priority_fixture"; then
  echo "Lean Deck priority fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_safety_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-deck-separate-real-simpl-fa325230"
./bin/shipguard ios report-quality \
  --reports "$lean_safety_fixture" \
  --out "$tmp_dir/lean-safety-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-safety-public-quality/ios-report-quality.json"
grep -q 'Does Lean Deck separate real simplification candidates from safety-boundary files?' "$tmp_dir/lean-safety-public-quality/ios-report-quality.md"
grep -q 'do-not-cut-safety-logic-without-proof' "$lean_safety_fixture/fixture-report.json"
grep -q 'native-url-components' "$lean_safety_fixture/fixture-report.json"
python3 - <<'PY' "$tmp_dir/lean-safety-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck safety-boundary public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck safety-boundary fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_safety_fixture"; then
  echo "Lean Deck safety-boundary fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_host_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-deck-protect-host-adapte-6c18ff70"
./bin/shipguard ios report-quality \
  --reports "$lean_host_fixture" \
  --out "$tmp_dir/lean-host-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-host-public-quality/ios-report-quality.json"
grep -q 'Does Lean Deck protect host adapters, hardware calibration, requested explanation, and one-check minimums from false less-code pressure?' "$tmp_dir/lean-host-public-quality/ios-report-quality.md"
grep -q 'keep-host-adapter-boundary' "$lean_host_fixture/fixture-report.json"
grep -q 'keep-hardware-calibration-boundary' "$lean_host_fixture/fixture-report.json"
grep -q 'keep-requested-explanation' "$lean_host_fixture/fixture-report.json"
grep -q 'keep-one-runnable-check' "$lean_host_fixture/fixture-report.json"
grep -q 'Behavior Gates' "$lean_host_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-host-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck host-adapter public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck host-adapter fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_host_fixture"; then
  echo "Lean Deck host-adapter fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_deletion_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-the-report-help-a-solo-develo-e645ec7e"
./bin/shipguard ios report-quality \
  --reports "$lean_deletion_fixture" \
  --out "$tmp_dir/lean-deletion-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-deletion-public-quality/ios-report-quality.json"
grep -q 'Does the report help a solo developer delete clutter without deleting product behavior?' "$tmp_dir/lean-deletion-public-quality/ios-report-quality.md"
grep -q 'delete-unused-debug-banner' "$lean_deletion_fixture/fixture-report.json"
grep -q 'native-url-components' "$lean_deletion_fixture/fixture-report.json"
grep -q 'keep-product-behavior-boundary' "$lean_deletion_fixture/fixture-report.json"
grep -q 'proof-blocked-migration-bridge' "$lean_deletion_fixture/fixture-report.json"
grep -q 'Behavior Gates' "$lean_deletion_fixture/fixture-report.md"
grep -q 'Grouped Action Plan' "$lean_deletion_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-deletion-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck deletion-usefulness public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck deletion-usefulness fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_deletion_fixture"; then
  echo "Lean Deck deletion-usefulness fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_shortcut_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-leandebtledger-make-intention-e856e9a3"
./bin/shipguard ios report-quality \
  --reports "$lean_shortcut_fixture" \
  --out "$tmp_dir/lean-shortcut-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-shortcut-public-quality/ios-report-quality.json"
grep -q 'Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?' "$tmp_dir/lean-shortcut-public-quality/ios-report-quality.md"
grep -q '"leanDebtLedger":' "$lean_shortcut_fixture/fixture-report.json"
grep -q '"status": "tracked"' "$lean_shortcut_fixture/fixture-report.json"
grep -q '"status": "needs-trigger"' "$lean_shortcut_fixture/fixture-report.json"
grep -q '"missingUpgradeTrigger": 1' "$lean_shortcut_fixture/fixture-report.json"
grep -q 'Lean Debt Ledger' "$lean_shortcut_fixture/fixture-report.md"
grep -q 'Upgrade Trigger' "$lean_shortcut_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-shortcut-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Deck shortcut-ledger public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Deck shortcut-ledger fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_shortcut_fixture"; then
  echo "Lean Deck shortcut-ledger fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_debt_marker_fixture="fixtures/ios-report-quality/01-shipguard-lean-debt-does-lean-debt-make-every-shortcut-034a83d4"
./bin/shipguard ios report-quality \
  --reports "$lean_debt_marker_fixture" \
  --out "$tmp_dir/lean-debt-marker-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-debt-marker-public-quality/ios-report-quality.json"
grep -q 'Does Lean Debt make every shortcut marker visible with a ceiling and upgrade trigger?' "$tmp_dir/lean-debt-marker-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean debt"' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"markerVisibilityReview":' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"rotRiskReview":' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"currentRepoBoundary":' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"perRepoSavingsClaim": "not-computed"' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"rowsWithCeiling": 2' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"rowsNeedingUpgradeTrigger": 1' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"rowsWithUpgradeStatus": 2' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"status": "tracked"' "$lean_debt_marker_fixture/fixture-report.json"
grep -q '"status": "needs-trigger"' "$lean_debt_marker_fixture/fixture-report.json"
grep -q 'Marker Visibility Review' "$lean_debt_marker_fixture/fixture-report.md"
grep -q 'Rot-Risk Review' "$lean_debt_marker_fixture/fixture-report.md"
grep -q 'Benchmark Savings Boundary' "$lean_debt_marker_fixture/fixture-report.md"
grep -q 'shipguard lean gain' "$lean_debt_marker_fixture/fixture-report.md"
grep -q 'Rows needing upgrade trigger' "$lean_debt_marker_fixture/fixture-report.md"
grep -q 'Sources/SyntheticLeanDebt/LegacyPanel.swift:27' "$lean_debt_marker_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-debt-marker-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Debt marker-visibility public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Debt marker-visibility fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_debt_marker_fixture"; then
  echo "Lean Debt marker-visibility fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_debt_benchmark_fixture="fixtures/ios-report-quality/01-shipguard-lean-debt-does-it-avoid-pretending-benchmark-e86ef9dc"
./bin/shipguard ios report-quality \
  --reports "$lean_debt_benchmark_fixture" \
  --out "$tmp_dir/lean-debt-benchmark-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-debt-benchmark-public-quality/ios-report-quality.json"
grep -q 'Does it avoid pretending benchmark savings are measurable in this repo?' "$tmp_dir/lean-debt-benchmark-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean debt"' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q '"currentRepoBoundary":' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q '"rotRiskReview":' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q '"perRepoSavingsClaim": "not-computed"' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q '"evidenceType": "shortcut-ledger-only"' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q '"benchmarkRoute":' "$lean_debt_benchmark_fixture/fixture-report.json"
grep -q 'Benchmark Savings Boundary' "$lean_debt_benchmark_fixture/fixture-report.md"
grep -q 'Rot-Risk Review' "$lean_debt_benchmark_fixture/fixture-report.md"
grep -q 'Do not claim current-repo line, token, cost, or time savings' "$lean_debt_benchmark_fixture/fixture-report.md"
grep -q 'Do not treat shortcut marker counts as benchmark savings' "$lean_debt_benchmark_fixture/fixture-report.md"
grep -q 'shipguard lean gain' "$lean_debt_benchmark_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-debt-benchmark-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Debt benchmark-savings public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Debt benchmark-savings fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_debt_benchmark_fixture"; then
  echo "Lean Debt benchmark-savings fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_debt_rot_fixture="fixtures/ios-report-quality/01-shipguard-lean-debt-can-a-maintainer-tell-which-marker-f778022c"
./bin/shipguard ios report-quality \
  --reports "$lean_debt_rot_fixture" \
  --out "$tmp_dir/lean-debt-rot-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-debt-rot-public-quality/ios-report-quality.json"
grep -q 'Can a maintainer tell which marker will rot without another source inspection pass?' "$tmp_dir/lean-debt-rot-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean debt"' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"rotRiskReview":' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"topRiskLocation": "Sources/SyntheticLeanDebt/LegacyPanel.swift:27"' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"riskLevel": "review"' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"riskLevel": "tracked"' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"nextAction": "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it."' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"triggerWatchContract":' "$lean_debt_rot_fixture/fixture-report.json"
grep -q '"triggerWatchContractRows": 2' "$lean_debt_rot_fixture/fixture-report.json"
grep -q 'Rot-Risk Review' "$lean_debt_rot_fixture/fixture-report.md"
grep -q 'Trigger-Watch Contracts' "$lean_debt_rot_fixture/fixture-report.md"
grep -q 'Top risk location: Sources/SyntheticLeanDebt/LegacyPanel.swift:27' "$lean_debt_rot_fixture/fixture-report.md"
grep -q 'Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.' "$lean_debt_rot_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-debt-rot-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Debt rot-risk public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Debt rot-risk fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_debt_rot_fixture"; then
  echo "Lean Debt rot-risk fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_debt_trigger_fixture="fixtures/ios-report-quality/01-shipguard-lean-debt-does-each-rot-risk-row-give-the-exa-691cec38"
./bin/shipguard ios report-quality \
  --reports "$lean_debt_trigger_fixture" \
  --out "$tmp_dir/lean-debt-trigger-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-debt-trigger-public-quality/ios-report-quality.json"
grep -q 'Does each rot-risk row give the exact next action and proof to prevent trigger rot?' "$tmp_dir/lean-debt-trigger-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean debt"' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q '"triggerWatchContract":' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q '"triggerWatchContractRows": 2' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q '"topTriggerWatchAction": "Add an upgrade trigger that tells the maintainer exactly when to replace or delete it."' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q '"triggerState": "watch-trigger"' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q '"exactNextAction": "Check whether this trigger is true: replace when repeated-key support is required"' "$lean_debt_trigger_fixture/fixture-report.json"
grep -q 'Trigger-Watch Contracts' "$lean_debt_trigger_fixture/fixture-report.md"
grep -q 'Check whether this trigger is true: replace when repeated-key support is required' "$lean_debt_trigger_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-debt-trigger-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Debt trigger-watch public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Debt trigger-watch fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_debt_trigger_fixture"; then
  echo "Lean Debt trigger-watch fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

mkdir -p "$tmp_dir/lean-debt-missing-marker-visibility"
python3 - <<'PY' "$lean_debt_marker_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-marker-visibility/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data.pop("markerVisibilityReview", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_marker_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-marker-visibility/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-marker-visibility" \
  --out "$tmp_dir/lean-debt-missing-marker-visibility-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-marker-visibility-review-missing"' "$tmp_dir/lean-debt-missing-marker-visibility-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-marker-visibility-missing-row"
cp "$lean_debt_marker_fixture/fixture-report.json" "$tmp_dir/lean-debt-marker-visibility-missing-row/lean-debt.json"
python3 - <<'PY' "$lean_debt_marker_fixture/fixture-report.md" "$tmp_dir/lean-debt-marker-visibility-missing-row/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
lines = open(source, encoding="utf-8").read().splitlines()
out = []
in_visibility = False
removed = False
for line in lines:
    if line == "## Marker Visibility Review":
        in_visibility = True
    elif in_visibility and line.startswith("## "):
        in_visibility = False
    if in_visibility and "Sources/SyntheticLeanDebt/LegacyPanel.swift:27" in line and not removed:
        removed = True
        continue
    out.append(line)
if not removed:
    raise SystemExit("did not remove marker visibility row")
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-marker-visibility-missing-row" \
  --out "$tmp_dir/lean-debt-marker-visibility-missing-row-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-marker-visibility-markdown-rows-missing"' "$tmp_dir/lean-debt-marker-visibility-missing-row-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch"
python3 - <<'PY' "$lean_debt_marker_fixture/fixture-report.json" "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
row = data["markerVisibilityReview"]["visibilityRows"][0]
row["ceiling"] = ""
row["hasCeiling"] = False
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_marker_fixture/fixture-report.md" "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch" \
  --out "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-marker-visibility-counts-mismatch"' "$tmp_dir/lean-debt-marker-visibility-ceiling-mismatch-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-fake-benchmark-savings"
python3 - <<'PY' "$lean_debt_benchmark_fixture/fixture-report.json" "$tmp_dir/lean-debt-fake-benchmark-savings/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data["currentRepoBoundary"]["perRepoSavingsClaim"] = "saved-54-percent"
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_benchmark_fixture/fixture-report.md" "$tmp_dir/lean-debt-fake-benchmark-savings/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-fake-benchmark-savings" \
  --out "$tmp_dir/lean-debt-fake-benchmark-savings-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-benchmark-savings-boundary-missing"' "$tmp_dir/lean-debt-fake-benchmark-savings-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-incomplete-benchmark-boundary"
python3 - <<'PY' "$lean_debt_benchmark_fixture/fixture-report.json" "$tmp_dir/lean-debt-incomplete-benchmark-boundary/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
boundary = data["currentRepoBoundary"]
boundary["reason"] = "Shortcut counts are useful."
boundary["nonClaims"] = []
boundary.pop("benchmarkRoute", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_benchmark_fixture/fixture-report.md" "$tmp_dir/lean-debt-incomplete-benchmark-boundary/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-incomplete-benchmark-boundary" \
  --out "$tmp_dir/lean-debt-incomplete-benchmark-boundary-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-benchmark-savings-boundary-incomplete"' "$tmp_dir/lean-debt-incomplete-benchmark-boundary-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-missing-benchmark-markdown"
cp "$lean_debt_benchmark_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-benchmark-markdown/lean-debt.json"
python3 - <<'PY' "$lean_debt_benchmark_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-benchmark-markdown/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
lines = open(source, encoding="utf-8").read().splitlines()
out = []
skip = False
removed = False
for line in lines:
    if line == "## Benchmark Savings Boundary":
        skip = True
        removed = True
        continue
    if skip and line.startswith("## "):
        skip = False
    if not skip:
        out.append(line)
if not removed:
    raise SystemExit("did not remove benchmark savings boundary")
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-benchmark-markdown" \
  --out "$tmp_dir/lean-debt-missing-benchmark-markdown-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-benchmark-savings-markdown-missing"' "$tmp_dir/lean-debt-missing-benchmark-markdown-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-missing-rot-risk"
python3 - <<'PY' "$lean_debt_rot_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-rot-risk/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data.pop("rotRiskReview", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_rot_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-rot-risk/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-rot-risk" \
  --out "$tmp_dir/lean-debt-missing-rot-risk-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-review-missing"' "$tmp_dir/lean-debt-missing-rot-risk-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-incomplete-rot-risk-row"
python3 - <<'PY' "$lean_debt_rot_fixture/fixture-report.json" "$tmp_dir/lean-debt-incomplete-rot-risk-row/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
row = data["rotRiskReview"]["prioritizedRows"][0]
row["nextAction"] = "Later."
row["proofGuidance"] = "Maybe."
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_rot_fixture/fixture-report.md" "$tmp_dir/lean-debt-incomplete-rot-risk-row/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-incomplete-rot-risk-row" \
  --out "$tmp_dir/lean-debt-incomplete-rot-risk-row-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-row-fields-incomplete"' "$tmp_dir/lean-debt-incomplete-rot-risk-row-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-missing-trigger-watch-contract"
python3 - <<'PY' "$lean_debt_trigger_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-trigger-watch-contract/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data["rotRiskReview"]["summary"]["triggerWatchContractRows"] = 1
data["rotRiskReview"]["summary"]["missingTriggerWatchContractRows"] = 1
data["rotRiskReview"]["prioritizedRows"][1].pop("triggerWatchContract", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_debt_trigger_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-trigger-watch-contract/lean-debt.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-trigger-watch-contract" \
  --out "$tmp_dir/lean-debt-missing-trigger-watch-contract-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-row-fields-incomplete"' "$tmp_dir/lean-debt-missing-trigger-watch-contract-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-old-schema-trigger-watch"
python3 - <<'PY' "$lean_debt_trigger_fixture/fixture-report.json" "$tmp_dir/lean-debt-old-schema-trigger-watch/lean-debt.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data["schemaVersion"] = 1
summary = data["rotRiskReview"]["summary"]
for key in (
    "triggerWatchContractRows",
    "missingTriggerWatchContractRows",
    "trackedTriggerWatchRows",
    "missingTriggerDefinitionRows",
    "topTriggerWatchAction",
):
    summary.pop(key, None)
for row in data["rotRiskReview"]["prioritizedRows"]:
    row.pop("triggerWatchContract", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
python3 - <<'PY' "$lean_debt_trigger_fixture/fixture-report.md" "$tmp_dir/lean-debt-old-schema-trigger-watch/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
lines = open(source, encoding="utf-8").read().splitlines()
out = []
skip = False
for line in lines:
    if line in {
        "- Trigger-watch contract rows: 2",
        "- Missing trigger-watch contracts: 0",
        "- Tracked trigger-watch rows: 1",
        "- Missing trigger definitions: 1",
        "- Top trigger-watch action: Add an upgrade trigger that tells the maintainer exactly when to replace or delete it.",
    }:
        continue
    if line == "## Trigger-Watch Contracts":
        skip = True
        continue
    if skip and line.startswith("## "):
        skip = False
    if not skip:
        out.append(line)
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-old-schema-trigger-watch" \
  --out "$tmp_dir/lean-debt-old-schema-trigger-watch-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-trigger-watch-schema-outdated"' "$tmp_dir/lean-debt-old-schema-trigger-watch-quality/ios-report-quality.json"
if grep -q '"ruleId": "lean-debt-rot-risk-summary-missing"' "$tmp_dir/lean-debt-old-schema-trigger-watch-quality/ios-report-quality.json"; then
  echo "old schema Lean Debt reports should get one outdated trigger-watch schema finding, not noisy v2 missing-summary failures" >&2
  exit 1
fi

mkdir -p "$tmp_dir/lean-debt-missing-trigger-watch-markdown"
cp "$lean_debt_trigger_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-trigger-watch-markdown/lean-debt.json"
python3 - <<'PY' "$lean_debt_trigger_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-trigger-watch-markdown/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
lines = open(source, encoding="utf-8").read().splitlines()
out = []
skip = False
removed = False
for line in lines:
    if line == "## Trigger-Watch Contracts":
        skip = True
        removed = True
        continue
    if skip and line.startswith("## "):
        skip = False
    if not skip:
        out.append(line)
if not removed:
    raise SystemExit("did not remove trigger-watch contracts")
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-trigger-watch-markdown" \
  --out "$tmp_dir/lean-debt-missing-trigger-watch-markdown-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-markdown-missing"' "$tmp_dir/lean-debt-missing-trigger-watch-markdown-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-missing-rot-risk-markdown"
cp "$lean_debt_rot_fixture/fixture-report.json" "$tmp_dir/lean-debt-missing-rot-risk-markdown/lean-debt.json"
python3 - <<'PY' "$lean_debt_rot_fixture/fixture-report.md" "$tmp_dir/lean-debt-missing-rot-risk-markdown/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
lines = open(source, encoding="utf-8").read().splitlines()
out = []
skip = False
removed = False
for line in lines:
    if line == "## Rot-Risk Review":
        skip = True
        removed = True
        continue
    if skip and line.startswith("## "):
        skip = False
    if not skip:
        out.append(line)
if not removed:
    raise SystemExit("did not remove rot-risk review")
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-missing-rot-risk-markdown" \
  --out "$tmp_dir/lean-debt-missing-rot-risk-markdown-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-markdown-missing"' "$tmp_dir/lean-debt-missing-rot-risk-markdown-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-weak-rot-risk-markdown"
cp "$lean_debt_rot_fixture/fixture-report.json" "$tmp_dir/lean-debt-weak-rot-risk-markdown/lean-debt.json"
python3 - <<'PY' "$lean_debt_rot_fixture/fixture-report.md" "$tmp_dir/lean-debt-weak-rot-risk-markdown/lean-debt.md"
import sys

source, target = sys.argv[1], sys.argv[2]
text = open(source, encoding="utf-8").read()
text = text.replace(" | Proof Guidance |", " | |")
text = text.replace(" | Name the release, dependency, migration state, or repeated call-site signal that should trigger cleanup. |", " | |")
text = text.replace(" | When the trigger is true, run call-site search plus the smallest focused validation before deleting or replacing it. |", " | |")
open(target, "w", encoding="utf-8").write(text)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-weak-rot-risk-markdown" \
  --out "$tmp_dir/lean-debt-weak-rot-risk-markdown-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-rot-risk-markdown-missing"' "$tmp_dir/lean-debt-weak-rot-risk-markdown-quality/ios-report-quality.json"

lean_gain_fixture="fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-gain-avoid-fake-per-repo-08315752"
./bin/shipguard ios report-quality \
  --reports "$lean_gain_fixture" \
  --out "$tmp_dir/lean-gain-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-gain-public-quality/ios-report-quality.json"
grep -q 'Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?' "$tmp_dir/lean-gain-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean gain"' "$lean_gain_fixture/fixture-report.json"
grep -q '"benchmarkScoreboard":' "$lean_gain_fixture/fixture-report.json"
grep -q '"perRepoSavingsClaim": "not-computed"' "$lean_gain_fixture/fixture-report.json"
grep -q '"evidenceRoutes":' "$lean_gain_fixture/fixture-report.json"
grep -q '"id": "lean-audit"' "$lean_gain_fixture/fixture-report.json"
grep -q '"id": "lean-review"' "$lean_gain_fixture/fixture-report.json"
grep -q '"id": "lean-debt"' "$lean_gain_fixture/fixture-report.json"
grep -q 'public benchmark, not this repository' "$lean_gain_fixture/fixture-report.json"
grep -q 'Honesty Boundary' "$lean_gain_fixture/fixture-report.md"
grep -q 'Current Repo Signals' "$lean_gain_fixture/fixture-report.md"
grep -q 'Current Repo Evidence Routes' "$lean_gain_fixture/fixture-report.md"
grep -q 'shipguard lean audit' "$lean_gain_fixture/fixture-report.md"
grep -q 'shipguard lean review' "$lean_gain_fixture/fixture-report.md"
grep -q 'shipguard lean debt' "$lean_gain_fixture/fixture-report.md"
grep -q 'Do not claim current-repo line, token, cost, or time savings' "$lean_gain_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-gain-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Gain honesty public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Gain honesty fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_gain_fixture"; then
  echo "Lean Gain honesty fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_gain_route_fixture="fixtures/ios-report-quality/01-shipguard-lean-gain-does-it-route-current-repo-evidence-9bae8f6f"
./bin/shipguard ios report-quality \
  --reports "$lean_gain_route_fixture" \
  --out "$tmp_dir/lean-gain-route-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-gain-route-public-quality/ios-report-quality.json"
grep -q 'Does it route current-repo evidence back to lean audit, lean review, and lean debt?' "$tmp_dir/lean-gain-route-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean gain"' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"evidenceRoutes":' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"command": "shipguard lean audit' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"command": "shipguard lean review' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"command": "shipguard lean debt' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"expectedArtifact": "lean-audit.json and lean-audit.md"' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"expectedArtifact": "lean-review.json and lean-review.md"' "$lean_gain_route_fixture/fixture-report.json"
grep -q '"expectedArtifact": "lean-debt.json and lean-debt.md"' "$lean_gain_route_fixture/fixture-report.json"
grep -q 'Current Repo Evidence Routes' "$lean_gain_route_fixture/fixture-report.md"
grep -q 'does not prove line, token, cost, or time savings' "$lean_gain_route_fixture/fixture-report.md"
grep -q 'does not prove whole-repo or benchmark savings' "$lean_gain_route_fixture/fixture-report.md"
grep -q 'does not prove benchmark or per-repo savings' "$lean_gain_route_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-gain-route-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Gain route public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Gain route fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_gain_route_fixture"; then
  echo "Lean Gain route fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_current_diff_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-give-a-current-d-9a6d6c8a"
./bin/shipguard ios report-quality \
  --reports "$lean_review_current_diff_fixture" \
  --out "$tmp_dir/lean-review-current-diff-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-current-diff-public-quality/ios-report-quality.json"
grep -q 'Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?' "$tmp_dir/lean-review-current-diff-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"currentDiffDecisionMap":' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"scope": "current-diff-only"' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"decision": "delete"' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"decision": "simplify"' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"decision": "keep"' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q '"deleteOrSimplifyList":' "$lean_review_current_diff_fixture/fixture-report.json"
grep -q 'Current Diff Decision Map' "$lean_review_current_diff_fixture/fixture-report.md"
grep -q 'current-diff-only' "$lean_review_current_diff_fixture/fixture-report.md"
grep -q 'does not scan the whole repo' "$lean_review_current_diff_fixture/fixture-report.md"
grep -q 'shipguard lean audit' "$lean_review_current_diff_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-current-diff-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review current-diff public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review current-diff fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_current_diff_fixture"; then
  echo "Lean Review current-diff fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_runnable_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-require-one-smal-247885c9"
./bin/shipguard ios report-quality \
  --reports "$lean_review_runnable_fixture" \
  --out "$tmp_dir/lean-review-runnable-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-runnable-public-quality/ios-report-quality.json"
grep -q 'Does Lean Review require one smallest runnable check for non-trivial new logic?' "$tmp_dir/lean-review-runnable-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"runnableCheckReview":' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"missingProofFindings":' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"sameDiffProofFindings":' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"duplicateCeremonyAvoided": 1' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"sameDiffProofStatus": "present"' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"missingRunnableCheckFindings": 1' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"codeFindingsCoveredBySameDiffProof": 1' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"ruleId": "one-runnable-check-missing-diff"' "$lean_review_runnable_fixture/fixture-report.json"
grep -q '"ruleId": "one-runnable-check-signal-present-diff"' "$lean_review_runnable_fixture/fixture-report.json"
grep -q 'Runnable Check Review' "$lean_review_runnable_fixture/fixture-report.md"
grep -q 'Missing Runnable Checks' "$lean_review_runnable_fixture/fixture-report.md"
grep -q 'Same-Diff Proof Signals' "$lean_review_runnable_fixture/fixture-report.md"
grep -q 'duplicate test ceremony' "$lean_review_runnable_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-runnable-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review runnable-check public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review runnable-check fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_runnable_fixture"; then
  echo "Lean Review runnable-check fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_proof_signal_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-proofsignalcalibration-disti-013d0422"
./bin/shipguard ios report-quality \
  --reports "$lean_review_proof_signal_fixture" \
  --out "$tmp_dir/lean-review-proof-signal-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-proof-signal-public-quality/ios-report-quality.json"
grep -q 'Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?' "$tmp_dir/lean-review-proof-signal-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"proofSignalCalibration":' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"proofSignalMatching":' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"matchedSameDiffProofFiles": 1' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"missingProofFiles": 1' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"unmatchedProofSignalCount": 1' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"unmatchedProofSignals":' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"codeFindingsCoveredBySameDiffProof": 1' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q '"missingRunnableCheckFindings": 1' "$lean_review_proof_signal_fixture/fixture-report.json"
grep -q 'Proof Signal Matching' "$lean_review_proof_signal_fixture/fixture-report.md"
grep -q 'Unmatched Proof Signals' "$lean_review_proof_signal_fixture/fixture-report.md"
grep -q 'not treated as global proof' "$lean_review_proof_signal_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-proof-signal-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review proof-signal public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review proof-signal fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_proof_signal_fixture"; then
  echo "Lean Review proof-signal fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_hardware_host_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-protect-hardware-c8a9af68"
./bin/shipguard ios report-quality \
  --reports "$lean_review_hardware_host_fixture" \
  --out "$tmp_dir/lean-review-hardware-host-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-hardware-host-public-quality/ios-report-quality.json"
grep -q 'Does Lean Review protect hardware calibration and host boundaries from false less-code pressure?' "$tmp_dir/lean-review-hardware-host-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"hardwareHostBoundaryReview":' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"hardwareCalibrationFindings": 1' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"hostAdapterBoundaryFindings": 1' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"falseLessCodePressureBlocked": 2' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"ruleId": "hardware-calibration-missing-diff"' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"ruleId": "host-adapter-boundary-diff"' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"decision": "proof-blocked"' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q '"decision": "keep"' "$lean_review_hardware_host_fixture/fixture-report.json"
grep -q 'Hardware And Host Boundary Review' "$lean_review_hardware_host_fixture/fixture-report.md"
grep -q 'Hardware Calibration Proof' "$lean_review_hardware_host_fixture/fixture-report.md"
grep -q 'Host Adapter Boundaries' "$lean_review_hardware_host_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-hardware-host-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review hardware/host public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review hardware/host fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_hardware_host_fixture"; then
  echo "Lean Review hardware/host fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_safety_boundary_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-it-keep-safety-boundary-code-df36ee0b"
./bin/shipguard ios report-quality \
  --reports "$lean_review_safety_boundary_fixture" \
  --out "$tmp_dir/lean-review-safety-boundary-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-safety-boundary-public-quality/ios-report-quality.json"
grep -q 'Does it keep safety-boundary code out of automatic deletion?' "$tmp_dir/lean-review-safety-boundary-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"safetyBoundaryReview":' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"safetyBoundaryFindings": 1' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"falseDeletionPressureBlocked": 1' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"keepSafetyBoundaryFiles": 1' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"ruleId": "do-not-cut-safety-diff-without-proof"' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q '"decision": "keep"' "$lean_review_safety_boundary_fixture/fixture-report.json"
grep -q 'Safety Boundary Review' "$lean_review_safety_boundary_fixture/fixture-report.md"
grep -q 'Keep With Proof Boundaries' "$lean_review_safety_boundary_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-safety-boundary-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review safety-boundary public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review safety-boundary fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_safety_boundary_fixture"; then
  echo "Lean Review safety-boundary fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

lean_review_mode_bias_fixture="fixtures/ios-report-quality/01-shipguard-lean-review-does-lean-review-expose-the-selec-bb4e13be"
./bin/shipguard ios report-quality \
  --reports "$lean_review_mode_bias_fixture" \
  --out "$tmp_dir/lean-review-mode-bias-public-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/lean-review-mode-bias-public-quality/ios-report-quality.json"
grep -q 'Does Lean Review expose the selected lite/full/ultra mode and bias first actions accordingly?' "$tmp_dir/lean-review-mode-bias-public-quality/ios-report-quality.md"
grep -q '"tool": "shipguard lean review"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"leanMode":' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"modeBiasReview":' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"selectedMode": "full"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"selectedFirstActionBias": "proof-ladder"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"selectedTopActionMatchesBias": true' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"mode": "lite"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"firstActionBias": "suggestion-first"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"mode": "ultra"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q '"firstActionBias": "delete-first"' "$lean_review_mode_bias_fixture/fixture-report.json"
grep -q 'Lean Mode' "$lean_review_mode_bias_fixture/fixture-report.md"
grep -q 'Mode Bias Review' "$lean_review_mode_bias_fixture/fixture-report.md"
grep -q 'suggestion-first' "$lean_review_mode_bias_fixture/fixture-report.md"
grep -q 'delete-first' "$lean_review_mode_bias_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/lean-review-mode-bias-public-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"Lean Review mode-bias public fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
top = questions[0] if questions else {}
if not top or not (top.get("sourceMaterializedFixture") is True or top.get("existingFixture")):
    raise SystemExit(f"Lean Review mode-bias fixture should retain materialized or fixture-coverage question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$lean_review_mode_bias_fixture"; then
  echo "Lean Review mode-bias fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

mkdir -p "$tmp_dir/lean-review-mode-bias-broken"
python3 - <<'PY' "$lean_review_mode_bias_fixture/fixture-report.json" "$tmp_dir/lean-review-mode-bias-broken/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data["leanMode"]["firstActionBias"] = "delete-first"
data["modeBiasReview"]["summary"]["selectedTopActionMatchesBias"] = False
data["precisionReview"]["topActions"] = list(reversed(data["precisionReview"]["topActions"]))
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_review_mode_bias_fixture/fixture-report.md" "$tmp_dir/lean-review-mode-bias-broken/lean-review.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-mode-bias-broken" \
  --out "$tmp_dir/lean-review-mode-bias-broken-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-mode-bias-incomplete"' "$tmp_dir/lean-review-mode-bias-broken-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-mode-top-action-mismatch"' "$tmp_dir/lean-review-mode-bias-broken-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-mode-bias-summary-incomplete"' "$tmp_dir/lean-review-mode-bias-broken-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-hardware-host-wrong-decisions"
python3 - <<'PY' "$lean_review_hardware_host_fixture/fixture-report.json" "$tmp_dir/lean-review-hardware-host-wrong-decisions/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for row in data["currentDiffDecisionMap"]["decisions"]:
    if row.get("file") == "Sources/SyntheticLeanReview/SensorSampler.swift":
        row["decision"] = "clean"
        row["ruleIds"] = []
    if row.get("file") == "Sources/SyntheticLeanReview/PluginHostAdapter.swift":
        row["decision"] = "delete"
        row["ruleIds"] = ["thin-wrapper-diff-review"]
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_review_hardware_host_fixture/fixture-report.md" "$tmp_dir/lean-review-hardware-host-wrong-decisions/lean-review.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-hardware-host-wrong-decisions" \
  --out "$tmp_dir/lean-review-hardware-host-wrong-decisions-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-hardware-calibration-decision-map-incomplete"' "$tmp_dir/lean-review-hardware-host-wrong-decisions-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-host-adapter-decision-map-incomplete"' "$tmp_dir/lean-review-hardware-host-wrong-decisions-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-safety-boundary-wrong-decision"
python3 - <<'PY' "$lean_review_safety_boundary_fixture/fixture-report.json" "$tmp_dir/lean-review-safety-boundary-wrong-decision/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for row in data["currentDiffDecisionMap"]["decisions"]:
    if row.get("file") == "Sources/SyntheticLeanReview/PermissionGate.swift":
        row["decision"] = "delete"
        row["ruleIds"] = ["thin-wrapper-diff-review"]
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_review_safety_boundary_fixture/fixture-report.md" "$tmp_dir/lean-review-safety-boundary-wrong-decision/lean-review.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-safety-boundary-wrong-decision" \
  --out "$tmp_dir/lean-review-safety-boundary-wrong-decision-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-safety-boundary-decision-map-incomplete"' "$tmp_dir/lean-review-safety-boundary-wrong-decision-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-safety-boundary-malformed-row"
python3 - <<'PY' "$lean_review_safety_boundary_fixture/fixture-report.json" "$tmp_dir/lean-review-safety-boundary-malformed-row/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data["safetyBoundaryReview"]["safetyBoundaryFindings"] = [{}]
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cp "$lean_review_safety_boundary_fixture/fixture-report.md" "$tmp_dir/lean-review-safety-boundary-malformed-row/lean-review.md"

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-safety-boundary-malformed-row" \
  --out "$tmp_dir/lean-review-safety-boundary-malformed-row-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-safety-boundary-row-fields-incomplete"' "$tmp_dir/lean-review-safety-boundary-malformed-row-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-safety-boundary-markdown-row-missing"
cp "$lean_review_safety_boundary_fixture/fixture-report.json" "$tmp_dir/lean-review-safety-boundary-markdown-row-missing/lean-review.json"
python3 - <<'PY' "$lean_review_safety_boundary_fixture/fixture-report.md" "$tmp_dir/lean-review-safety-boundary-markdown-row-missing/lean-review.md"
import sys

markdown = open(sys.argv[1], encoding="utf-8").read()
markdown = markdown.replace(
    "| Sources/SyntheticLeanReview/PermissionGate.swift:31 | Less code is not the goal in this file until behavior proof exists. | Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior. |\n",
    "",
)
open(sys.argv[2], "w", encoding="utf-8").write(markdown)
PY

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-safety-boundary-markdown-row-missing" \
  --out "$tmp_dir/lean-review-safety-boundary-markdown-row-missing-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-safety-boundary-markdown-rows-missing"' "$tmp_dir/lean-review-safety-boundary-markdown-row-missing-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-missing-safety-boundary"
python3 - <<'PY' "$lean_review_safety_boundary_fixture/fixture-report.json" "$tmp_dir/lean-review-missing-safety-boundary/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data.pop("safetyBoundaryReview", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cat > "$tmp_dir/lean-review-missing-safety-boundary/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Current Diff Decision Map

- Scope: `current-diff-only`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo.

## Precision Ledger

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | keep | `do-not-cut-safety-diff-without-proof` | 1 | Sources/SyntheticLeanReview/PermissionGate.swift:31 | Attach proof. | Run focused permission proof. | Stop without proof. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-missing-safety-boundary" \
  --out "$tmp_dir/lean-review-missing-safety-boundary-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-safety-boundary-review-missing"' "$tmp_dir/lean-review-missing-safety-boundary-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-safety-boundary-markdown-missing"' "$tmp_dir/lean-review-missing-safety-boundary-quality/ios-report-quality.json"

./bin/shipguard lean audit \
  --path . \
  --out "$tmp_dir/lean-fresh-priority" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-fresh-priority" \
  --out "$tmp_dir/lean-fresh-priority-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/lean-fresh-priority-candidates" >/dev/null
grep -q '"fixtureCoverage":' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-precisionreview-identify-dele-286dc4bb' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-lean-deck-separate-real-simpl-fa325230' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-lean-deck-protect-host-adapte-6c18ff70' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-the-report-help-a-solo-develo-e645ec7e' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-leandebtledger-make-intention-e856e9a3' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-audit-does-lean-gain-avoid-fake-per-repo-08315752' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '"fixtureType": "shipguard-lean-report-quality-fixture"' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q '"fixtureCandidates":' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
grep -q 'Does each finding explain the proof needed before removing code?' "$tmp_dir/lean-fresh-priority-quality/ios-report-quality.json"
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$tmp_dir/lean-fresh-priority-candidates"; then
  echo "materialized Lean Deck priority candidate must not include local paths or private app identifiers" >&2
  exit 1
fi

empty_lean_diff="$tmp_dir/empty-lean.diff"
: > "$empty_lean_diff"
./bin/shipguard lean review \
  --path . \
  --diff "$empty_lean_diff" \
  --out "$tmp_dir/lean-fresh-review-priority" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard lean debt \
  --path . \
  --out "$tmp_dir/lean-fresh-debt-priority" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard lean gain \
  --path . \
  --out "$tmp_dir/lean-fresh-gain-priority" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-fresh-priority" \
  --reports "$tmp_dir/lean-fresh-review-priority" \
  --reports "$tmp_dir/lean-fresh-debt-priority" \
  --reports "$tmp_dir/lean-fresh-gain-priority" \
  --out "$tmp_dir/lean-fresh-combined-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/lean-fresh-combined-candidates" >/dev/null
grep -q '01-shipguard-lean-gain-does-it-route-current-repo-evidence-9bae8f6f' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-lean-review-give-a-current-d-9a6d6c8a' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-lean-review-require-one-smal-247885c9' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-proofsignalcalibration-disti-013d0422' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-lean-review-protect-hardware-c8a9af68' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-it-keep-safety-boundary-code-df36ee0b' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-review-does-lean-review-expose-the-selec-bb4e13be' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-debt-does-lean-debt-make-every-shortcut-034a83d4' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-debt-does-it-avoid-pretending-benchmark-e86ef9dc' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-debt-can-a-maintainer-tell-which-marker-f778022c' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q '01-shipguard-lean-debt-does-each-rot-risk-row-give-the-exa-691cec38' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does Lean Review require one smallest runnable check for non-trivial new logic?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does Lean Review protect hardware calibration and host boundaries from false less-code pressure?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does it keep safety-boundary code out of automatic deletion?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does Lean Review expose the selected lite/full/ultra mode and bias first actions accordingly?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does Lean Debt make every shortcut marker visible with a ceiling and upgrade trigger?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does it avoid pretending benchmark savings are measurable in this repo?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Can a maintainer tell which marker will rot without another source inspection pass?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
grep -q 'Does each rot-risk row give the exact next action and proof to prevent trigger rot?' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/lean-fresh-combined-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
expected_question = "Does each rot-risk row give the exact next action and proof to prevent trigger rot?"
expected_path = "fixtures/ios-report-quality/01-shipguard-lean-debt-does-each-rot-risk-row-give-the-exa-691cec38"
if not any(item.get("question") == expected_question and item.get("publicFixturePath") == expected_path for item in coverage):
    raise SystemExit(f"expected combined Lean QA fixture coverage for trigger-rot next action: {coverage!r}")
if any((candidate.get("sourceQuestion") == expected_question) for candidate in (data.get("fixtureCandidates") or [])):
    raise SystemExit(f"combined Lean QA should not emit duplicate trigger-rot fixture candidate: {data.get('fixtureCandidates')!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$tmp_dir/lean-fresh-combined-candidates"; then
  echo "materialized combined Lean candidate must not include local paths or private app identifiers" >&2
  exit 1
fi
if grep -R -q 'Does each rot-risk row give the exact next action and proof to prevent trigger rot?' "$tmp_dir/lean-fresh-combined-candidates"; then
  echo "combined Lean QA should not materialize duplicate trigger-rot next-action candidate" >&2
  exit 1
fi

mkdir -p "$tmp_dir/lean-review-missing-hardware-host-boundary"
python3 - <<'PY' "$lean_review_hardware_host_fixture/fixture-report.json" "$tmp_dir/lean-review-missing-hardware-host-boundary/lean-review.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
data.pop("hardwareHostBoundaryReview", None)
json.dump(data, open(sys.argv[2], "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
cat > "$tmp_dir/lean-review-missing-hardware-host-boundary/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Current Diff Decision Map

- Scope: `current-diff-only`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo.
- Whole-repo fallback: `shipguard lean audit --path <repo> --out <lean-audit-out>`

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review
- `hardwareCalibration`: available
- `requestedExplanation`: policy
- `adapterBoundary`: available
- `gainHonesty`: available-in-lean-gain

## Precision Ledger

- Delete candidates: 1; simplify candidates: 1; keep boundaries: 2; proof-blocked candidates: 2; action groups: 4

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 4 | proof-blocked | `hardware-calibration-missing-diff` | 1 | Sources/SyntheticLeanReview/SensorSampler.swift:33 | Attach calibration proof. | Run physical-device proof. | Stop without proof. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-missing-hardware-host-boundary" \
  --out "$tmp_dir/lean-review-missing-hardware-host-boundary-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-hardware-host-boundary-review-missing"' "$tmp_dir/lean-review-missing-hardware-host-boundary-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-hardware-host-boundary-markdown-missing"' "$tmp_dir/lean-review-missing-hardware-host-boundary-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-current-diff-missing"
cat > "$tmp_dir/lean-review-current-diff-missing/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "review",
  "metrics": {
    "filesChanged": 1,
    "addedLines": 6,
    "findings": 1
  },
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 1,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 0,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "delete",
        "ruleId": "thin-wrapper-diff-review",
        "evidenceCount": 1,
        "firstLocation": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
        "firstExperiment": "Search call sites.",
        "validationRoute": "Run focused check.",
        "stopCondition": "Stop at compatibility behavior."
      }
    ],
    "topActions": [
      {
        "rank": 1,
        "ruleId": "thin-wrapper-diff-review",
        "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
        "severity": "opportunity",
        "action": "Inline wrapper.",
        "proofRequired": "Search call sites."
      }
    ]
  },
  "findings": [],
  "reportQualityQuestions": [
    "Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-current-diff-missing/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Ledger

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search call sites. | Run focused check. | Stop at compatibility behavior. |
MD
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-current-diff-missing" \
  --out "$tmp_dir/lean-review-current-diff-missing-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-current-diff-map-missing"' "$tmp_dir/lean-review-current-diff-missing-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-current-diff-incomplete"
cat > "$tmp_dir/lean-review-current-diff-incomplete/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "review",
  "metrics": {
    "filesChanged": 1,
    "addedLines": 6,
    "findings": 1
  },
  "currentDiffDecisionMap": {
    "scope": "repo-inventory",
    "inventoryBoundary": "Scans useful files.",
    "summary": {
      "filesChanged": 1,
      "addedLinesInspected": 6
    },
    "decisions": [
      {
        "file": "Sources/SyntheticLeanReview/FormatterShim.swift",
        "source": "repo-scan",
        "decision": "maybe",
        "addedLines": 6
      }
    ]
  },
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 1,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 0,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "delete",
        "ruleId": "thin-wrapper-diff-review",
        "evidenceCount": 1,
        "firstLocation": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
        "firstExperiment": "Search call sites.",
        "validationRoute": "Run focused check.",
        "stopCondition": "Stop at compatibility behavior."
      }
    ],
    "topActions": [
      {
        "rank": 1,
        "ruleId": "thin-wrapper-diff-review",
        "location": "Sources/SyntheticLeanReview/FormatterShim.swift:14",
        "severity": "opportunity",
        "action": "Inline wrapper.",
        "proofRequired": "Search call sites."
      }
    ]
  },
  "findings": [],
  "reportQualityQuestions": [
    "Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-current-diff-incomplete/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Current Diff Decision Map

Generic map.

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Ledger

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `thin-wrapper-diff-review` | 1 | Sources/SyntheticLeanReview/FormatterShim.swift:14 | Search call sites. | Run focused check. | Stop at compatibility behavior. |
MD
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-current-diff-incomplete" \
  --out "$tmp_dir/lean-review-current-diff-incomplete-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-current-diff-scope-invalid"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-boundary-incomplete"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-summary-incomplete"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-decision-incomplete"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-decision-source-invalid"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-decision-kind-invalid"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-delete-simplify-list-missing"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-current-diff-markdown-incomplete"' "$tmp_dir/lean-review-current-diff-incomplete-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-missing-groups"
cat > "$tmp_dir/lean-missing-groups/lean-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean audit",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "review",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 2
    },
    "topActions": [
      {
        "rank": 1,
        "ruleId": "large-legacy-file-review",
        "location": "scripts/example.py:1",
        "severity": "review",
        "action": "Do not split the whole file first; start at the first marker line and prove one removable branch.",
        "proofRequired": "Attach call-site evidence."
      }
    ]
  },
  "findings": [],
  "reportQualityQuestions": [
    "Does precisionReview group repeated proof-blocked decisions into a bounded action plan?"
  ]
}
JSON
cat > "$tmp_dir/lean-missing-groups/lean-audit.md" <<'MD'
# ShipGuard Lean Deck

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Review

| Rank | Decision | Location | Action | Proof |
| ---: | --- | --- | --- | --- |
| 1 | proof-blocked | scripts/example.py:1 | Start small. | Attach call-site evidence. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-missing-groups" \
  --out "$tmp_dir/lean-missing-groups-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-action-groups-missing"' "$tmp_dir/lean-missing-groups-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-action-groups-markdown-missing"' "$tmp_dir/lean-missing-groups-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-clean-state-missing"
cat > "$tmp_dir/lean-clean-state-missing/lean-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean audit",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "pass",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 2,
      "proofBlockedCandidates": 0,
      "actionGroups": 0
    },
    "actionGroups": [],
    "topActions": [],
    "keepList": [
      {
        "ruleId": "thin-adapter-boundary",
        "location": "scripts/example.py",
        "reason": "Keep adapter boundary.",
        "proofRequired": "Host proof required."
      }
    ]
  },
  "findings": [],
  "reportQualityQuestions": [
    "Does a pass-state Lean report still tell the developer what to do next?"
  ]
}
JSON
cat > "$tmp_dir/lean-clean-state-missing/lean-audit.md" <<'MD'
# ShipGuard Lean Deck

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Review

- Delete candidates: 0; simplify candidates: 0; keep boundaries: 2; proof-blocked candidates: 0; action groups: 0
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-clean-state-missing" \
  --out "$tmp_dir/lean-clean-state-missing-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-clean-state-action-missing"' "$tmp_dir/lean-clean-state-missing-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-clean-state-action-markdown-missing"' "$tmp_dir/lean-clean-state-missing-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-debt-ledger-missing-proof"
cat > "$tmp_dir/lean-debt-ledger-missing-proof/lean-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean audit",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "review",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "leanDebtLedger": {
    "summary": {
      "markers": 1
    },
    "markers": [
      {
        "file": "Sources/FastPreviewLoader.swift",
        "line": 27,
        "marker": "shipguard-lean",
        "summary": "cache the first fixture load while the preview dataset is tiny",
        "hasUpgradeTrigger": false,
        "status": "tracked"
      }
    ]
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "proofBlockedCandidates": 0,
      "actionGroups": 0
    },
    "topActions": []
  },
  "reportQualityQuestions": [
    "Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?"
  ]
}
JSON
cat > "$tmp_dir/lean-debt-ledger-missing-proof/lean-audit.md" <<'MD'
# ShipGuard Lean Deck

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review
- `hardwareCalibration`: available
- `requestedExplanation`: policy
- `adapterBoundary`: available
- `gainHonesty`: available-in-lean-gain

## Findings

Shortcut debt exists, but the ledger table is missing.
MD
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-debt-ledger-missing-proof" \
  --out "$tmp_dir/lean-debt-ledger-missing-proof-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-debt-ledger-summary-missing"' "$tmp_dir/lean-debt-ledger-missing-proof-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-debt-ledger-marker-incomplete"' "$tmp_dir/lean-debt-ledger-missing-proof-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-debt-ledger-trigger-status-missing"' "$tmp_dir/lean-debt-ledger-missing-proof-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-debt-ledger-markdown-missing"' "$tmp_dir/lean-debt-ledger-missing-proof-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-gain-fake-savings"
cat > "$tmp_dir/lean-gain-fake-savings/lean-gain.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean gain",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "pass",
  "surface": "ShipGuard Lean Gain",
  "target": {"path": ".", "shareable": true},
  "benchmarkScoreboard": {
    "primary": {
      "label": "Synthetic benchmark",
      "scope": "this repository",
      "remainingPercentOfBaseline": {
        "linesOfCode": 46
      },
      "reportedChange": {
        "linesOfCode": "-54%"
      }
    }
  },
  "currentRepoBoundary": {
    "perRepoSavingsClaim": "saved-54-percent",
    "reason": "",
    "realRepoSignals": [
      "diff size after an actual change"
    ]
  },
  "reportQualityQuestions": [
    "Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?"
  ]
}
JSON
cat > "$tmp_dir/lean-gain-fake-savings/lean-gain.md" <<'MD'
# ShipGuard Lean Gain

The current repo saved 54 percent lines of code.

## Benchmark

This benchmark is presented as if it measured the current repository.
MD
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-gain-fake-savings" \
  --out "$tmp_dir/lean-gain-fake-savings-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-gain-fake-repo-savings-risk"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-current-routing-missing"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-current-route-contract-missing"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-scoreboard-incomplete"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-scoreboard-metrics-missing"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-honesty-markdown-missing"' "$tmp_dir/lean-gain-fake-savings-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-gain-incomplete-routes"
cat > "$tmp_dir/lean-gain-incomplete-routes/lean-gain.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean gain",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "pass",
  "surface": "ShipGuard Lean Gain",
  "target": {"path": ".", "shareable": true},
  "benchmarkScoreboard": {
    "primary": {
      "label": "Synthetic benchmark",
      "baseline": "same agent without the lean-code ruleset",
      "scope": "public benchmark, not this repository",
      "method": "paired public fixture tasks",
      "remainingPercentOfBaseline": {
        "linesOfCode": 46,
        "tokens": 78,
        "cost": 80,
        "time": 73,
        "safety": 100
      },
      "reportedChange": {
        "linesOfCode": "-54%",
        "tokens": "-22%",
        "cost": "-20%",
        "time": "-27%",
        "safety": "100%"
      }
    }
  },
  "currentRepoBoundary": {
    "perRepoSavingsClaim": "not-computed",
    "reason": "No untreated current-repo baseline exists.",
    "realRepoSignals": [
      "lean audit findings",
      "lean review findings",
      "lean debt marker counts"
    ],
    "evidenceRoutes": [
      {
        "id": "lean-audit",
        "command": "shipguard lean audit --path <repo> --out <lean-audit-out>",
        "expectedArtifact": "lean-audit.json and lean-audit.md",
        "answers": "cuttable repo surfaces",
        "proofBoundary": "Source scan only.",
        "nonClaim": "Audit summary."
      },
      {
        "id": "lean-review",
        "command": "shipguard lean review --path <repo> --diff <diff-file> --out <lean-review-out>",
        "expectedArtifact": "lean-review.json and lean-review.md",
        "answers": "current-diff opportunities",
        "proofBoundary": "Diff scan only.",
        "nonClaim": "Review summary."
      }
    ]
  },
  "reportQualityQuestions": [
    "Does it route current-repo evidence back to lean audit, lean review, and lean debt?"
  ]
}
JSON
cat > "$tmp_dir/lean-gain-incomplete-routes/lean-gain.md" <<'MD'
# ShipGuard Lean Gain

## Benchmark Scoreboard

- Scope: public benchmark, not this repository

## Honesty Boundary

- Per-repo savings claim: `not-computed`
- Do not claim current-repo line, token, cost, or time savings without a matched baseline.

## Current Repo Signals

- Lean audit findings
- Lean review findings
- Lean debt marker counts

## Current Repo Evidence Routes

| Route | Command |
| --- | --- |
| `lean-audit` | `shipguard lean audit --path <repo> --out <lean-audit-out>` |
| `lean-review` | `shipguard lean review --path <repo> --diff <diff-file> --out <lean-review-out>` |
MD
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-gain-incomplete-routes" \
  --out "$tmp_dir/lean-gain-incomplete-routes-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-gain-current-route-contract-incomplete"' "$tmp_dir/lean-gain-incomplete-routes-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-current-route-boundary-incomplete"' "$tmp_dir/lean-gain-incomplete-routes-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-current-route-nonclaim-incomplete"' "$tmp_dir/lean-gain-incomplete-routes-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-gain-honesty-markdown-incomplete"' "$tmp_dir/lean-gain-incomplete-routes-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-large-missing-evidence"
cat > "$tmp_dir/lean-large-missing-evidence/lean-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean audit",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "review",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 1,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "proof-blocked",
        "ruleId": "large-legacy-file-review",
        "evidenceCount": 1,
        "firstLocation": "scripts/example.py:12",
        "firstExperiment": "Open the first marker line.",
        "validationRoute": "Run call-site search.",
        "stopCondition": "Stop if behavior is still active."
      }
    ],
    "topActions": [
      {
        "rank": 1,
        "ruleId": "large-legacy-file-review",
        "location": "scripts/example.py:12",
        "severity": "review",
        "action": "Do not split the whole file first.",
        "proofRequired": "Attach call-site evidence."
      }
    ]
  },
  "findings": [
    {
      "severity": "review",
      "category": "does-this-need-to-exist",
      "ruleId": "large-legacy-file-review",
      "evidence": {
        "file": "scripts/example.py",
        "line": 12,
        "snippet": "900 lines, 1 comment marker; inspect marker lines before splitting"
      },
      "recommendation": "Triage the marker cluster first.",
      "proofGuidance": "Attach grep/call-site evidence."
    }
  ],
  "reportQualityQuestions": [
    "Does each large-file finding expose a proof packet?"
  ]
}
JSON
cat > "$tmp_dir/lean-large-missing-evidence/lean-audit.md" <<'MD'
# ShipGuard Lean Deck

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Review

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | proof-blocked | `large-legacy-file-review` | 1 | scripts/example.py:12 | Open the first marker line. | Run call-site search. | Stop if behavior is still active. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-large-missing-evidence" \
  --out "$tmp_dir/lean-large-missing-evidence-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-large-file-evidence-missing"' "$tmp_dir/lean-large-missing-evidence-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-large-file-evidence-markdown-missing"' "$tmp_dir/lean-large-missing-evidence-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-missing-group-md"
cat > "$tmp_dir/lean-review-missing-group-md/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "review",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 2,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 0,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "simplify",
        "ruleId": "one-runnable-check-missing-diff",
        "evidenceCount": 2,
        "firstLocation": "scripts/example.py:12",
        "firstExperiment": "Add one smallest runnable check at the first changed branch.",
        "validationRoute": "Run the focused test that covers the changed branch.",
        "stopCondition": "Stop if the check would only restate implementation details."
      }
    ],
    "topActions": [
      {
        "rank": 1,
        "ruleId": "one-runnable-check-missing-diff",
        "location": "scripts/example.py:12",
        "severity": "review",
        "action": "Leave one smallest runnable check.",
        "proofRequired": "Add a focused test."
      }
    ]
  },
  "findings": [],
  "reportQualityQuestions": [
    "Does Lean Review make the first grouped diff action visible in Markdown?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-missing-group-md/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Ledger

- Delete candidates: 0; simplify candidates: 2; keep boundaries: 0; proof-blocked candidates: 0; action groups: 1

| Rank | Location | Action | Proof |
| ---: | --- | --- | --- |
| 1 | scripts/example.py:12 | Leave one smallest runnable check. | Add a focused test. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-missing-group-md" \
  --out "$tmp_dir/lean-review-missing-group-md-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-action-groups-markdown-missing"' "$tmp_dir/lean-review-missing-group-md-quality/ios-report-quality.json"
if grep -q '"ruleId": "lean-action-groups-missing"' "$tmp_dir/lean-review-missing-group-md-quality/ios-report-quality.json"; then
  echo "Lean Review JSON action groups should pass while missing Markdown is flagged separately" >&2
  exit 1
fi

mkdir -p "$tmp_dir/lean-review-missing-proof-calibration"
cat > "$tmp_dir/lean-review-missing-proof-calibration/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "review",
  "behaviorGates": {
    "oneRunnableCheck": {"status": "enforced-in-lean-review"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 1,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 0,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "simplify",
        "ruleId": "one-runnable-check-missing-diff",
        "evidenceCount": 1,
        "firstLocation": "scripts/example.py:12",
        "firstExperiment": "Add one smallest runnable check at the first changed branch.",
        "validationRoute": "Run the focused test that covers the changed branch.",
        "stopCondition": "Stop if the check would only restate implementation details."
      }
    ],
    "topActions": [
      {
        "rank": 1,
        "ruleId": "one-runnable-check-missing-diff",
        "location": "scripts/example.py:12",
        "severity": "review",
        "action": "Leave one smallest runnable check.",
        "proofRequired": "Add a focused test."
      }
    ]
  },
  "findings": [
    {
      "severity": "review",
      "category": "proof-diff-review",
      "ruleId": "one-runnable-check-missing-diff",
      "evidence": {
        "file": "scripts/example.py",
        "line": 12,
        "snippet": "non-trivial logic added without a runnable check signal"
      },
      "recommendation": "Leave one smallest runnable check.",
      "proofGuidance": "Add a focused test."
    }
  ],
  "reportQualityQuestions": [
    "Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-missing-proof-calibration/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Behavior Gates

- `oneRunnableCheck`: enforced-in-lean-review

## Precision Ledger

- Delete candidates: 0; simplify candidates: 1; keep boundaries: 0; proof-blocked candidates: 0; action groups: 1

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | simplify | `one-runnable-check-missing-diff` | 1 | scripts/example.py:12 | Add one smallest runnable check. | Run the focused test. | Stop if redundant. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-missing-proof-calibration" \
  --out "$tmp_dir/lean-review-missing-proof-calibration-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-proof-signal-calibration-missing"' "$tmp_dir/lean-review-missing-proof-calibration-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-proof-signal-markdown-missing"' "$tmp_dir/lean-review-missing-proof-calibration-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-review-missing"' "$tmp_dir/lean-review-missing-proof-calibration-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-markdown-missing"' "$tmp_dir/lean-review-missing-proof-calibration-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-runnable-check-incomplete"
cat > "$tmp_dir/lean-review-runnable-check-incomplete/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "review",
  "metrics": {
    "filesChanged": 2,
    "addedLines": 12,
    "findings": 2
  },
  "currentDiffDecisionMap": {
    "scope": "current-diff-only",
    "diffPath": "synthetic.diff",
    "inventoryBoundary": "This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.",
    "wholeRepoFallbackCommand": "shipguard lean audit --path <repo> --out <lean-audit-out> --mode full --shipguard-eval --shareable",
    "changedFiles": [
      {"file": "Sources/SyntheticLeanReview/RuleRouter.swift", "addedLines": 7, "removedLines": 0},
      {"file": "Sources/SyntheticLeanReview/SelectionPolicy.swift", "addedLines": 5, "removedLines": 0}
    ],
    "decisions": [
      {
        "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
        "source": "unified-diff",
        "decision": "proof-blocked",
        "addedLines": 7,
        "removedLines": 0,
        "ruleIds": ["one-runnable-check-missing-diff"],
        "firstExperiment": "Add one smallest runnable check.",
        "validationRoute": "Run the focused test.",
        "stopCondition": "Stop if proof is absent."
      },
      {
        "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
        "source": "unified-diff",
        "decision": "clean",
        "addedLines": 5,
        "removedLines": 0,
        "ruleIds": ["one-runnable-check-signal-present-diff"],
        "firstExperiment": "Review matching same-diff test.",
        "validationRoute": "Run the focused test.",
        "stopCondition": "Stop if proof is unrelated."
      }
    ],
    "deleteOrSimplifyList": [],
    "summary": {
      "filesChanged": 2,
      "addedLinesInspected": 12,
      "removedLinesSeen": 0,
      "decisionRows": 2,
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 1,
      "cleanFiles": 1
    }
  },
  "behaviorGates": {
    "oneRunnableCheck": {"status": "same-diff-proof-signal-present"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "proofSignalCalibration": {
    "sameDiffProofStatus": "present",
    "proofSignals": [
      {
        "file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift",
        "line": 9,
        "kind": "test-file",
        "addedLines": 5,
        "snippet": "func testPrimaryOptionWins()",
        "checkSignal": true
      }
    ],
    "sameDiffProofSignalCount": 1,
    "codeFindingsCoveredBySameDiffProof": 1,
    "missingRunnableCheckFindings": 1
  },
  "runnableCheckReview": {
    "summary": {
      "missingRunnableCheckFindings": 0,
      "sameDiffProofFindings": 0,
      "sameDiffProofSignalCount": 1,
      "duplicateCeremonyAvoided": 0
    },
    "missingProofFindings": [],
    "sameDiffProofFindings": [],
    "nonCeremonyBoundary": "Same diff proof exists."
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 1,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "proof-blocked",
        "ruleId": "one-runnable-check-missing-diff",
        "evidenceCount": 1,
        "firstLocation": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
        "firstExperiment": "Add one smallest runnable check.",
        "validationRoute": "Run the focused test.",
        "stopCondition": "Stop if proof is absent."
      }
    ]
  },
  "findings": [
    {
      "severity": "review",
      "category": "proof-diff-review",
      "ruleId": "one-runnable-check-missing-diff",
      "evidence": {"file": "Sources/SyntheticLeanReview/RuleRouter.swift", "line": 18, "snippet": "if route.kind == .generated"},
      "recommendation": "Leave one smallest runnable check.",
      "proofGuidance": "Add a focused test."
    },
    {
      "severity": "info",
      "category": "proof-signal-diff-review",
      "ruleId": "one-runnable-check-signal-present-diff",
      "evidence": {"file": "Sources/SyntheticLeanReview/SelectionPolicy.swift", "line": 27, "snippet": "if option.isPrimary"},
      "recommendation": "Do not add duplicate test ceremony.",
      "proofGuidance": "Run the changed same-diff test."
    }
  ],
  "reportQualityQuestions": [
    "Does Lean Review require one smallest runnable check for non-trivial new logic?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-runnable-check-incomplete/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Current Diff Decision Map

- Scope: `current-diff-only`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.
- Whole-repo fallback: `shipguard lean audit --path <repo> --out <lean-audit-out>`

## Behavior Gates

- `oneRunnableCheck`: same-diff-proof-signal-present

## Proof Signal Calibration

- Same-diff proof status: `present`
- Proof signals: 1
- Code findings covered by same-diff proof: 1
- Missing runnable-check findings: 1

## Precision Ledger

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | proof-blocked | `one-runnable-check-missing-diff` | 1 | Sources/SyntheticLeanReview/RuleRouter.swift:18 | Add one smallest runnable check. | Run the focused test. | Stop if proof is absent. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-runnable-check-incomplete" \
  --out "$tmp_dir/lean-review-runnable-check-incomplete-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-runnable-check-missing-proof-rows-incomplete"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-same-diff-proof-rows-incomplete"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-duplicate-ceremony-count-missing"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-non-ceremony-boundary-incomplete"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-runnable-check-markdown-missing"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-proof-signal-matching-missing"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-proof-signal-matching-markdown-missing"' "$tmp_dir/lean-review-runnable-check-incomplete-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/lean-review-proof-signal-matching-incoherent"
cat > "$tmp_dir/lean-review-proof-signal-matching-incoherent/lean-review.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard lean review",
  "generatedAt": "2026-06-21T00:00:00Z",
  "status": "review",
  "metrics": {
    "filesChanged": 3,
    "addedLines": 15,
    "findings": 2
  },
  "currentDiffDecisionMap": {
    "scope": "current-diff-only",
    "inventoryBoundary": "This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.",
    "summary": {
      "filesChanged": 3,
      "addedLinesInspected": 15,
      "removedLinesSeen": 0,
      "decisionRows": 3,
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 1,
      "cleanFiles": 2
    },
    "decisions": [
      {
        "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
        "source": "unified-diff",
        "decision": "proof-blocked",
        "addedLines": 7,
        "removedLines": 0,
        "ruleIds": ["one-runnable-check-missing-diff"],
        "firstExperiment": "Add one smallest runnable check.",
        "validationRoute": "Run the focused test.",
        "stopCondition": "Stop if proof is absent."
      }
    ]
  },
  "behaviorGates": {
    "oneRunnableCheck": {"status": "same-diff-proof-signal-present"},
    "hardwareCalibration": {"status": "available"},
    "requestedExplanation": {"status": "policy"},
    "adapterBoundary": {"status": "available"},
    "gainHonesty": {"status": "available-in-lean-gain"}
  },
  "proofSignalCalibration": {
    "sameDiffProofStatus": "present",
    "proofSignals": [
      {
        "file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift",
        "line": 9,
        "kind": "test-file",
        "addedLines": 5,
        "snippet": "func testPrimaryOptionWins()",
        "checkSignal": true
      },
      {
        "file": "Tests/SyntheticLeanReviewTests/UnrelatedSmokeTests.swift",
        "line": 7,
        "kind": "test-file",
        "addedLines": 4,
        "snippet": "func testUnrelatedSmokePath()",
        "checkSignal": true
      }
    ],
    "sameDiffProofSignalCount": 2,
    "codeFindingsCoveredBySameDiffProof": 1,
    "missingRunnableCheckFindings": 1
  },
  "proofSignalMatching": {
    "nonGlobalProofBoundary": "Same diff proof exists.",
    "rows": [
      {
        "file": "Sources/SyntheticLeanReview/RuleRouter.swift",
        "matchingDecision": "missing-proof",
        "matchedProofSignalCount": 0,
        "matchedProofSignals": []
      },
      {
        "file": "Sources/SyntheticLeanReview/SelectionPolicy.swift",
        "matchingDecision": "matched-same-diff-proof",
        "matchedProofSignalCount": 1,
        "matchedProofSignals": [
          {
            "file": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift",
            "line": 9,
            "location": "Tests/SyntheticLeanReviewTests/SelectionPolicyTests.swift:9"
          }
        ]
      }
    ],
    "unmatchedProofSignals": [],
    "summary": {
      "changedCodeFiles": 2,
      "nonTrivialLogicFiles": 2,
      "matchedSameDiffProofFiles": 1,
      "missingProofFiles": 1,
      "inlineCheckFiles": 0,
      "matchedProofSignalCount": 1,
      "unmatchedProofSignalCount": 0
    }
  },
  "runnableCheckReview": {
    "summary": {
      "missingRunnableCheckFindings": 1,
      "sameDiffProofFindings": 1,
      "sameDiffProofSignalCount": 2,
      "duplicateCeremonyAvoided": 1
    },
    "missingProofFindings": [
      {"location": "Sources/SyntheticLeanReview/RuleRouter.swift:18"}
    ],
    "sameDiffProofFindings": [
      {"location": "Sources/SyntheticLeanReview/SelectionPolicy.swift:27"}
    ],
    "nonCeremonyBoundary": "same-diff proof avoids duplicate ceremony"
  },
  "precisionReview": {
    "summary": {
      "deleteCandidates": 0,
      "simplifyCandidates": 0,
      "keepBoundaries": 0,
      "proofBlockedCandidates": 1,
      "actionGroups": 1
    },
    "actionGroups": [
      {
        "rank": 1,
        "decision": "proof-blocked",
        "ruleId": "one-runnable-check-missing-diff",
        "evidenceCount": 1,
        "firstLocation": "Sources/SyntheticLeanReview/RuleRouter.swift:18",
        "firstExperiment": "Add one smallest runnable check.",
        "validationRoute": "Run the focused test.",
        "stopCondition": "Stop if proof is absent."
      }
    ]
  },
  "findings": [
    {
      "severity": "review",
      "category": "proof-diff-review",
      "ruleId": "one-runnable-check-missing-diff",
      "evidence": {"file": "Sources/SyntheticLeanReview/RuleRouter.swift", "line": 18, "snippet": "if route.kind == .generated"},
      "recommendation": "Leave one smallest runnable check.",
      "proofGuidance": "Add a focused test."
    },
    {
      "severity": "info",
      "category": "proof-signal-diff-review",
      "ruleId": "one-runnable-check-signal-present-diff",
      "evidence": {"file": "Sources/SyntheticLeanReview/SelectionPolicy.swift", "line": 27, "snippet": "if option.isPrimary"},
      "recommendation": "Do not add duplicate test ceremony.",
      "proofGuidance": "Run the changed same-diff test."
    }
  ],
  "reportQualityQuestions": [
    "Does proofSignalCalibration distinguish missing runnable checks from same-diff proof signals?"
  ]
}
JSON
cat > "$tmp_dir/lean-review-proof-signal-matching-incoherent/lean-review.md" <<'MD'
# ShipGuard Lean Review

## Current Diff Decision Map

- Scope: `current-diff-only`
- Boundary: This report is built only from the supplied unified diff; it does not scan the whole repo or claim a whole-repo inventory.

## Behavior Gates

- `oneRunnableCheck`: same-diff-proof-signal-present

## Proof Signal Calibration

- Same-diff proof status: `present`
- Proof signals: 2
- Code findings covered by same-diff proof: 1
- Missing runnable-check findings: 1

## Runnable Check Review

## Proof Signal Matching

- Matched same-diff proof files: 1
- Missing proof files: 1

## Precision Ledger

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | proof-blocked | `one-runnable-check-missing-diff` | 1 | Sources/SyntheticLeanReview/RuleRouter.swift:18 | Add one smallest runnable check. | Run the focused test. | Stop if proof is absent. |
MD

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean-review-proof-signal-matching-incoherent" \
  --out "$tmp_dir/lean-review-proof-signal-matching-incoherent-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "lean-review-proof-signal-matching-counts-incoherent"' "$tmp_dir/lean-review-proof-signal-matching-incoherent-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-proof-signal-matching-unmatched-signals-incomplete"' "$tmp_dir/lean-review-proof-signal-matching-incoherent-quality/ios-report-quality.json"
grep -q '"ruleId": "lean-review-proof-signal-matching-boundary-incomplete"' "$tmp_dir/lean-review-proof-signal-matching-incoherent-quality/ios-report-quality.json"

performance_boundary_fixture="fixtures/ios-report-quality/performance-runtime-boundary"
./bin/shipguard ios report-quality \
  --reports "$performance_boundary_fixture" \
  --out "$tmp_dir/performance-boundary-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/performance-boundary-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/performance-boundary-quality/ios-report-quality.json"
grep -q 'Runtime Evidence Boundary' "$performance_boundary_fixture/fixture-report.md"
grep -q '"runtimeEvidenceBoundary":' "$performance_boundary_fixture/fixture-report.json"
grep -q 'Did report wording keep target-app remediation separate from ShipGuard product QA next steps?' "$tmp_dir/performance-boundary-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/performance-boundary-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"performance runtime boundary fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions or questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"promoted performance fixture should retain sourceMaterializedFixture question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$performance_boundary_fixture"; then
  echo "performance runtime boundary fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

grouped_performance_fixture="fixtures/ios-report-quality/grouped-performance-observation"
./bin/shipguard ios report-quality \
  --reports "$grouped_performance_fixture" \
  --out "$tmp_dir/grouped-performance-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/grouped-performance-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/grouped-performance-quality/ios-report-quality.json"
grep -q 'Grouped Next Actions' "$grouped_performance_fixture/fixture-report.md"
grep -q 'First experiment' "$grouped_performance_fixture/fixture-report.md"
grep -q 'Validation route' "$grouped_performance_fixture/fixture-report.md"
grep -q 'Stop condition' "$grouped_performance_fixture/fixture-report.md"
grep -q 'Proof Boundaries' "$grouped_performance_fixture/fixture-report.md"
grep -q '"groupedActionPlan":' "$grouped_performance_fixture/fixture-report.json"
grep -q '"evidencePromotion":' "$grouped_performance_fixture/fixture-report.json"
grep -q '"ruleId": "swiftui-repeat-forever-animation"' "$grouped_performance_fixture/fixture-report.json"
grep -q 'Evidence Promotion Contract' "$grouped_performance_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/grouped-performance-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"grouped performance fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions or questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"grouped performance fixture should retain sourceMaterializedFixture question evidence: {questions!r}")
source_rules = {item.get("ruleId") for item in data.get("sourceFindings") or []}
if "swiftui-repeat-forever-animation" not in source_rules:
    raise SystemExit(f"grouped performance source finding was not preserved: {source_rules!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$grouped_performance_fixture"; then
  echo "grouped performance fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

performance_promotion_fixture="fixtures/ios-report-quality/performance-evidence-promotion"
./bin/shipguard ios report-quality \
  --reports "$performance_promotion_fixture" \
  --out "$tmp_dir/performance-promotion-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/performance-promotion-quality/ios-report-quality.json"
grep -q '"sourceMaterializedFixture": true' "$tmp_dir/performance-promotion-quality/ios-report-quality.json"
grep -q 'Evidence Promotion Contract' "$performance_promotion_fixture/fixture-report.md"
grep -q '"evidencePromotion":' "$performance_promotion_fixture/fixture-report.json"
grep -q '"firstCandidateRule": "swiftui-repeat-forever-animation"' "$performance_promotion_fixture/fixture-report.json"
grep -q '"expectedArtifact":' "$performance_promotion_fixture/fixture-report.json"
grep -q '"successCondition":' "$performance_promotion_fixture/fixture-report.json"
grep -q '"failureMeaning":' "$performance_promotion_fixture/fixture-report.json"
grep -q 'Did the report make it obvious which evidence would promote a source suspicion into broader work?' "$tmp_dir/performance-promotion-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/performance-promotion-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"performance promotion fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions or questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"performance promotion fixture should retain sourceMaterializedFixture question evidence: {questions!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$performance_promotion_fixture"; then
  echo "performance promotion fixture must not include local paths or private app identifiers" >&2
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
  "runtimeEvidenceBoundary": {
    "evidence": "source heuristic",
    "confidence": "medium",
    "runtimeProof": "missing",
    "blocking": "no",
    "interpretation": "Source-only findings nominate review and proof candidates; they do not prove actual CPU, GPU, memory, energy, hitch, FPS, or frame-rate problems.",
    "promotionRule": "Promote only after same-route runtime proof confirms the issue shape.",
    "requiredRuntimeProof": [
      "Same-route Simulator trace, sample, or log evidence for local-only claims.",
      "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims."
    ]
  },
  "evidencePromotion": {
    "sourceEvidence": "source heuristic",
    "promotionStatus": "missing-runtime-proof",
    "firstCandidateRule": "performance-higher-priority",
    "proofRequired": [
      "Same-route Simulator trace, sample, or log evidence for local-only claims.",
      "Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims."
    ],
    "nextAction": {
      "owner": "developer",
      "kind": "manual-proof",
      "manualProof": "Run report-quality on the fixture locally.",
      "expectedArtifact": "priority-quality/ios-report-quality.json",
      "successCondition": "The blocked performance question remains the first priority action.",
      "failureMeaning": "The priority fixture no longer proves blocked performance questions outrank lower-status reports."
    }
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

## Runtime Evidence Boundary

- Evidence: `source heuristic`
- Confidence: `medium`
- Runtime proof: `missing`
- Blocking: `no`
- Interpretation: Source-only findings nominate review and proof candidates; they do not prove actual CPU, GPU, memory, energy, hitch, FPS, or frame-rate problems.
- Promotion rule: Promote only after same-route runtime proof confirms the issue shape.

Required runtime proof:
- Same-route Simulator trace, sample, or log evidence for local-only claims.
- Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.

## Evidence Promotion Contract

- Source evidence: `source heuristic`
- Promotion status: `missing-runtime-proof`
- First candidate rule: `performance-higher-priority`
- Owner: `developer`
- Manual proof: Run report-quality on the fixture locally.
- Expected artifact: priority-quality/ios-report-quality.json
- Success condition: The blocked performance question remains the first priority action.
- Failure meaning: The priority fixture no longer proves blocked performance questions outrank lower-status reports.

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

missing_runtime_boundary_dir="$tmp_dir/missing-runtime-boundary"
mkdir -p "$missing_runtime_boundary_dir"
cat > "$missing_runtime_boundary_dir/ios-performance.json" <<'JSON'
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
  "findings": [],
  "reportQualityQuestions": [
    "Does the performance report clearly state that source heuristics are not runtime proof?"
  ]
}
JSON
cat > "$missing_runtime_boundary_dir/ios-performance.md" <<'MD'
# Missing Runtime Boundary Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Scan Scope

No skipped directories.
MD
./bin/shipguard ios report-quality \
  --reports "$missing_runtime_boundary_dir" \
  --out "$tmp_dir/missing-runtime-boundary-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-runtime-boundary-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-runtime-evidence-boundary-missing"' "$tmp_dir/missing-runtime-boundary-quality/ios-report-quality.json"

missing_promotion_dir="$tmp_dir/missing-promotion"
mkdir -p "$missing_promotion_dir"
cat > "$missing_promotion_dir/ios-performance.json" <<'JSON'
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
  "runtimeEvidenceBoundary": {
    "evidence": "source heuristic",
    "confidence": "medium",
    "runtimeProof": "missing",
    "blocking": "no",
    "interpretation": "Source-only findings nominate proof candidates; they do not prove CPU, GPU, or FPS runtime problems.",
    "promotionRule": "Promote only after same-route runtime proof confirms the issue shape.",
    "requiredRuntimeProof": [
      "Same-route Simulator trace, sample, or log evidence for local-only claims.",
      "Physical-device Instruments proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims."
    ]
  },
  "scanScope": {
    "skippedDirectoryCount": 0,
    "skippedDirectories": []
  },
  "findings": [
    {
      "severity": "review",
      "ruleId": "performance-missing-promotion",
      "category": "SwiftUI Rendering",
      "title": "Missing exact next action",
      "evidence": ".repeatForever()",
      "recommendation": "Add evidencePromotion.",
      "proof": "Runtime proof required.",
      "impact": "A source suspicion needs promotion evidence.",
      "severityReason": "Review because this is a source-only signal.",
      "localProof": "Run a same-route sample.",
      "manualProof": "Use device Instruments for hardware claims."
    }
  ],
  "reportQualityQuestions": [
    "Did report-quality enforce performance evidence promotion?"
  ]
}
JSON
cat > "$missing_promotion_dir/ios-performance.md" <<'MD'
# Missing Evidence Promotion Fixture

## Runtime Evidence Boundary

- Evidence: `source heuristic`
- Runtime proof: `missing`
- Blocking: `no`

## Top Findings

| Severity | Rule | Why severity | Why it matters |
| --- | --- | --- | --- |
| review | `performance-missing-promotion` | Review because this is a source-only signal. | A source suspicion needs promotion evidence. |

## Proof Boundaries

| Severity | Rule | Codex local proof | Manual/device proof |
| --- | --- | --- | --- |
| review | `performance-missing-promotion` | Run a same-route sample. | Use device Instruments for hardware claims. |
MD
./bin/shipguard ios report-quality \
  --reports "$missing_promotion_dir" \
  --out "$tmp_dir/missing-promotion-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-promotion-quality/ios-report-quality.json"
grep -q '"ruleId": "performance-evidence-promotion-contract-missing"' "$tmp_dir/missing-promotion-quality/ios-report-quality.json"

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

value_gauntlet_fixture="fixtures/ios-report-quality/value-gauntlet-actionability"
./bin/shipguard ios report-quality \
  --reports "$value_gauntlet_fixture" \
  --out "$tmp_dir/value-gauntlet-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/value-gauntlet-fixture-quality/ios-report-quality.json"
grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/value-gauntlet-fixture-quality/ios-report-quality.json"
grep -q 'ShipGuard Tool Value Gauntlet' "$tmp_dir/value-gauntlet-fixture-quality/ios-report-quality.md"
grep -q 'Should repeated low-value patterns become public fixtures or eval cases' "$tmp_dir/value-gauntlet-fixture-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/value-gauntlet-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data.get("fixtureCandidates"):
    raise SystemExit(f"value-gauntlet materialized fixture should not create recursive fixture candidates: {data['fixtureCandidates']!r}")
questions = data.get("prioritizedActionabilityQuestions") or []
if not questions:
    raise SystemExit("value-gauntlet materialized fixture should preserve actionability questions")
if questions[0].get("sourceMaterializedFixture") is not True:
    raise SystemExit(f"value-gauntlet fixture should be marked materialized: {questions[0]!r}")
if questions[0].get("tool") != "shipguard value-gauntlet":
    raise SystemExit(f"unexpected source tool: {questions[0]!r}")
PY
if grep -R -E -q '/Users|/private/tmp|/var/folders|Ringly|Ilmify|InweFi' "$value_gauntlet_fixture"; then
  echo "value-gauntlet fixture must not include local paths or private app identifiers" >&2
  exit 1
fi

./bin/shipguard value-gauntlet \
  --path . \
  --out "$tmp_dir/value-gauntlet-fresh" >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/value-gauntlet-fresh" \
  --out "$tmp_dir/value-gauntlet-fresh-quality" \
  --shareable >/dev/null
grep -q '"fixtureCoverage":' "$tmp_dir/value-gauntlet-fresh-quality/ios-report-quality.json"
grep -q 'fixtures/ios-report-quality/value-gauntlet-actionability' "$tmp_dir/value-gauntlet-fresh-quality/ios-report-quality.json"
grep -q 'Fixture Coverage' "$tmp_dir/value-gauntlet-fresh-quality/ios-report-quality.md"
grep -q 'value-gauntlet-actionability' "$tmp_dir/value-gauntlet-fresh-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/value-gauntlet-fresh-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
covered_question = "Should repeated low-value patterns become public fixtures or eval cases so ShipGuard cannot regress into decorative output?"
stable_publication_question = "Can ShipGuard prove stable-v4 publication with downloaded GitHub release assets, independent adoption evidence, final security review evidence, release notes, and post-release consumer proof?"
product_release_question = "Should ShipGuard stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption?"
proof_boundary_question = "Does every useful-looking surface have docs, tests, package proof, and a concrete proof boundary rather than only a branded name?"
plugin_skill_question = "Do plugin skills and starter skills give Codex actionable routing and validation commands, not just vague advice?"
coverage = data.get("fixtureCoverage") or []
if not any(item.get("question") == covered_question for item in coverage):
    raise SystemExit(f"expected value-gauntlet question to be covered by a promoted fixture: {coverage!r}")
if not any(item.get("question") == stable_publication_question for item in coverage):
    raise SystemExit(f"expected stable-publication value-gauntlet question to be covered by a promoted fixture: {coverage!r}")
for item in coverage:
    if item.get("question") == covered_question and item.get("publicFixturePath") != "fixtures/ios-report-quality/value-gauntlet-actionability":
        raise SystemExit(f"unexpected coverage path: {item!r}")
    if item.get("question") == stable_publication_question and item.get("publicFixturePath") != "fixtures/ios-report-quality/stable-publication-value-gauntlet-question":
        raise SystemExit(f"unexpected stable-publication coverage path: {item!r}")
    if item.get("question") == product_release_question and item.get("publicFixturePath") != "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question":
        raise SystemExit(f"unexpected product-release coverage path: {item!r}")
    if item.get("question") == proof_boundary_question and item.get("publicFixturePath") != "fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question":
        raise SystemExit(f"unexpected proof-boundary coverage path: {item!r}")
    if item.get("question") == plugin_skill_question and item.get("publicFixturePath") != "fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question":
        raise SystemExit(f"unexpected plugin-skill routing coverage path: {item!r}")
if not any(item.get("question") == product_release_question for item in coverage):
    raise SystemExit(f"expected product-release stabilization question to be covered by a promoted fixture: {coverage!r}")
if not any(item.get("question") == proof_boundary_question for item in coverage):
    raise SystemExit(f"expected proof-boundary question to be covered by a promoted fixture: {coverage!r}")
if not any(item.get("question") == plugin_skill_question for item in coverage):
    raise SystemExit(f"expected plugin-skill routing question to be covered by a promoted fixture: {coverage!r}")
for candidate in data.get("fixtureCandidates") or []:
    if candidate.get("sourceQuestion") in {covered_question, stable_publication_question, product_release_question, proof_boundary_question, plugin_skill_question}:
        raise SystemExit(f"covered value-gauntlet question should not create a duplicate fixture candidate: {candidate!r}")
priority = data.get("priorityAction") or {}
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected all-actionability-covered once fresh value-gauntlet questions are covered: {priority!r}")
if priority.get("topCoveredQuestion") != stable_publication_question:
    raise SystemExit(f"expected the top covered stable-publication question to remain visible: {priority!r}")
if priority.get("topExistingFixturePath") != "fixtures/ios-report-quality/stable-publication-value-gauntlet-question":
    raise SystemExit(f"unexpected existing fixture path: {priority!r}")
if priority.get("coveredQuestionCount", 0) < 5:
    raise SystemExit(f"expected all promoted value-gauntlet questions to count as covered: {priority!r}")
PY

mixed_release_priority_dir="$tmp_dir/mixed-release-priority"
mkdir -p "$mixed_release_priority_dir"
cat > "$mixed_release_priority_dir/shipguard-full-audit.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard full-audit",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "review",
  "resultUX": {
    "status": "review",
    "verdict": "REVIEW: Synthetic Full Audit report is plan-only.",
    "proofSource": "stageStatusSummary + NEXT_GOAL handoff",
    "whyItMatters": "Full Audit plans the release lane without claiming execution.",
    "nextCommand": "shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release",
    "nextActionSummary": "Execute the planned release lane."
  },
  "stageStatusSummary": {
    "planned": 14
  },
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true,
    "doesNotPush": true,
    "doesNotPublishRelease": true
  },
  "slashHandoffSource": {
    "status": "loaded",
    "sourcePath": "NEXT_GOAL.md",
    "section": "following"
  },
  "slashPlan": "/plan v3.148.0 Stable V4 Release Packet Artifact Receipts for jlekerli-source/ShipGuard: prioritize release-proof artifact gaps from self-QA.",
  "slashGoal": "/goal Implement v3.148.0 Stable V4 Release Packet Artifact Receipts for jlekerli-source/ShipGuard: make report-quality follow concrete release-proof gaps.",
  "reportQualityQuestions": [
    "Does the command preserve proof boundaries instead of pushing, publishing, or editing target apps?"
  ]
}
JSON
cat > "$mixed_release_priority_dir/shipguard-full-audit.md" <<'MD'
# ShipGuard Full Audit

## Result

- Verdict: REVIEW: Synthetic Full Audit report is plan-only.
- Proof source: stageStatusSummary + NEXT_GOAL handoff
- Why it matters: Full Audit plans the release lane without claiming execution.
- Next command: `shipguard full-audit --path <shipguard-repo> --out <shipguard-full-audit-out> --profile release`
- Next action: Execute the planned release lane.

## Slash Handoff Source

- Status: `loaded`
- Source path: `NEXT_GOAL.md`
- Section: `following`

## Slash Plan

```text
/plan v3.148.0 Stable V4 Release Packet Artifact Receipts for jlekerli-source/ShipGuard: prioritize release-proof artifact gaps from self-QA.
```

## Slash Goal

```text
/goal Implement v3.148.0 Stable V4 Release Packet Artifact Receipts for jlekerli-source/ShipGuard: make report-quality follow concrete release-proof gaps.
```
MD
cat > "$mixed_release_priority_dir/tool-value-gauntlet.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard value-gauntlet",
  "surface": "ShipGuard Tool Value Gauntlet",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "resultUX": {
    "status": "pass",
    "verdict": "PASS: Synthetic value gauntlet completed.",
    "proofSource": "synthetic report-quality fixture",
    "whyItMatters": "The lowest-value surface should drive the next ShipGuard improvement.",
    "nextCommand": "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
    "nextActionSummary": "Stabilize the v4 product release with external adoption evidence, final security review, package proof, rollback proof, and release proof consumption."
  },
  "lowestValueSurfaceProbe": {
    "answer": {
      "identifier": "shipguard v4-product-release-stabilization",
      "title": "V4 product release stabilization",
      "missingDepthSignals": [
        "runtimeV4ProductReleaseStabilization"
      ]
    }
  },
  "reportQualityQuestions": [
    "Should ShipGuard stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption?"
  ]
}
JSON
cat > "$mixed_release_priority_dir/tool-value-gauntlet.md" <<'MD'
# ShipGuard Tool Value Gauntlet

## Result

- Verdict: PASS: Synthetic value gauntlet completed.
- Proof source: synthetic report-quality fixture
- Why it matters: The lowest-value surface should drive the next ShipGuard improvement.
- Next command: `./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet`
- Next action: Stabilize the v4 product release with external adoption evidence, final security review, package proof, rollback proof, and release proof consumption.
MD
cat > "$mixed_release_priority_dir/v4-release-candidate.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard v4 release-candidate",
  "surface": "ShipGuard V4 Release Candidate Readiness",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "resultUX": {
    "status": "pass",
    "verdict": "PASS: Synthetic LaunchKey report completed.",
    "proofSource": "synthetic release-readiness fixture",
    "whyItMatters": "LaunchKey tracks stable-v4 proof gates.",
    "nextCommand": "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --package-tarball <release-tarball> --shipguard-eval --shareable",
    "nextActionSummary": "Attach fresh-install, release-asset, external-adoption, security-review, rollback, and release-proof evidence before a stable v4 claim."
  },
  "releaseReadiness": {
    "stableV4Release": false,
    "freshInstallPackageProof": {
      "status": "not-provided"
    },
    "publishedReleaseAssetProof": {
      "status": "not-provided"
    }
  },
  "reportQualityQuestions": [
    "Can a fresh user install, upgrade, uninstall, and validate ShipGuard from the release package without maintainer context?"
  ]
}
JSON
cat > "$mixed_release_priority_dir/v4-release-candidate.md" <<'MD'
# ShipGuard V4 Release Candidate Readiness

## Result

- Verdict: PASS: Synthetic LaunchKey report completed.
- Proof source: synthetic release-readiness fixture
- Why it matters: LaunchKey tracks stable-v4 proof gates.
- Next command: `./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --package-tarball <release-tarball> --shipguard-eval --shareable`
- Next action: Attach fresh-install, release-asset, external-adoption, security-review, rollback, and release-proof evidence before a stable v4 claim.
MD
./bin/shipguard ios report-quality \
  --reports "$mixed_release_priority_dir" \
  --out "$tmp_dir/mixed-release-priority-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/mixed-release-priority-quality/ios-report-quality.json"
grep -q 'value-gauntlet lowest-value surface is v4 product release stabilization' "$tmp_dir/mixed-release-priority-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/mixed-release-priority-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
covered = "Should ShipGuard stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption?"
expected = "Can a fresh user install, upgrade, uninstall, and validate ShipGuard from the release package without maintainer context?"
if priority.get("tool") != "shipguard v4 release-candidate":
    raise SystemExit(f"expected LaunchKey package-proof question after covered value-gauntlet question: {priority!r}")
if priority.get("question") != expected:
    raise SystemExit(f"expected LaunchKey package-proof question, got {priority!r}")
if priority.get("priorityReason") != "LaunchKey release-readiness evidence still has stable-v4 proof gaps":
    raise SystemExit(f"expected source-priority reason, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("question") == covered and item.get("publicFixturePath") == "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question" for item in coverage):
    raise SystemExit(f"product-release value-gauntlet question should be covered by the promoted fixture: {coverage!r}")
ranked = data.get("prioritizedActionabilityQuestions") or []
if not ranked or ranked[0].get("question") != covered or not ranked[0].get("existingFixture"):
    raise SystemExit(f"covered value-gauntlet release signal should remain visible with fixture metadata: {ranked!r}")
if len(ranked) < 2 or ranked[1].get("tool") != "shipguard v4 release-candidate":
    raise SystemExit(f"LaunchKey package-proof question should follow covered value-gauntlet signal: {ranked!r}")
if any(
    item.get("priority") == 1 and item.get("tool") == "shipguard full-audit"
    for item in ranked
):
    raise SystemExit(f"generic Full Audit review question outranked release-stabilization signal: {ranked!r}")
PY

stable_publication_priority_dir="$tmp_dir/stable-publication-priority"
mkdir -p "$stable_publication_priority_dir"
cat > "$stable_publication_priority_dir/tool-value-gauntlet.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard value-gauntlet",
  "surface": "ShipGuard Tool Value Gauntlet",
  "generatedAt": "2026-06-20T00:00:00Z",
  "status": "pass",
  "resultUX": {
    "status": "pass",
    "verdict": "PASS: Synthetic value gauntlet completed.",
    "proofSource": "synthetic report-quality fixture",
    "whyItMatters": "The lowest-value surface should drive the next ShipGuard improvement.",
    "nextCommand": "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
    "nextActionSummary": "Prepare and verify the real stable-v4 public release packet with downloaded GitHub release assets, independent adoption evidence, final security review evidence, release notes, and post-release consumer proof."
  },
  "lowestValueSurfaceProbe": {
    "answer": {
      "identifier": "shipguard v4-stable-release-publication",
      "name": "v4 Stable Release Publication",
      "recommendation": "Prepare and verify the real stable-v4 public release packet with downloaded GitHub release assets, independent adoption evidence, final security review evidence, release notes, and post-release consumer proof.",
      "missingDepthSignals": [
        "runtimeV4StableReleasePublication"
      ]
    }
  },
  "reportQualityQuestions": [
    "Should ShipGuard stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption?"
  ]
}
JSON
cat > "$stable_publication_priority_dir/tool-value-gauntlet.md" <<'MD'
# ShipGuard Tool Value Gauntlet

## Result

- Verdict: PASS: Synthetic value gauntlet completed.
- Proof source: synthetic report-quality fixture
- Why it matters: The lowest-value surface should drive the next ShipGuard improvement.
- Next command: `./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet`
- Next action: Prepare and verify the real stable-v4 public release packet with downloaded GitHub release assets, independent adoption evidence, final security review evidence, release notes, and post-release consumer proof.
MD
./bin/shipguard ios report-quality \
  --reports "$stable_publication_priority_dir" \
  --out "$tmp_dir/stable-publication-priority-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-priority-quality/ios-report-quality.json"
grep -q 'value-gauntlet lowest-value surface is stable-v4 publication' "$tmp_dir/stable-publication-priority-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/stable-publication-priority-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
covered = "Can ShipGuard prove stable-v4 publication with downloaded GitHub release assets, independent adoption evidence, final security review evidence, release notes, and post-release consumer proof?"
product_release = "Should ShipGuard stabilize the v4 product release with external adoption evidence, final security review, rollback proof, package proof, and release proof consumption?"
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected covered fresh-report priority to advance beyond fixture review: {priority!r}")
if priority.get("tool") != "shipguard value-gauntlet":
    raise SystemExit(f"expected stable publication value-gauntlet priority: {priority!r}")
if priority.get("topCoveredQuestion") != covered:
    raise SystemExit(f"expected covered stable-v4 fixture priority to remain visible, got {priority!r}")
if priority.get("topExistingFixturePath") != "fixtures/ios-report-quality/stable-publication-value-gauntlet-question":
    raise SystemExit(f"expected stable-v4 fixture path, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
if not any(item.get("question") == covered and item.get("publicFixturePath") == "fixtures/ios-report-quality/stable-publication-value-gauntlet-question" for item in coverage):
    raise SystemExit(f"stable-v4 publication question should be covered by the promoted fixture: {coverage!r}")
if not any(item.get("question") == product_release and item.get("publicFixturePath") == "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question" for item in coverage):
    raise SystemExit(f"product-release stabilization question should be covered by the promoted fixture: {coverage!r}")
ranked = data.get("prioritizedActionabilityQuestions") or []
if not ranked or ranked[0].get("question") != covered or not ranked[0].get("existingFixture"):
    raise SystemExit(f"covered stable-v4 question should stay visible with existing fixture metadata: {ranked!r}")
if len(ranked) < 2 or ranked[1].get("question") != product_release or not ranked[1].get("existingFixture"):
    raise SystemExit(f"covered product-release question should follow stable-v4 item with existing fixture metadata: {ranked!r}")
PY

stable_publication_packet_dir="$tmp_dir/stable-publication-packet"
mkdir -p "$stable_publication_packet_dir"
cat > "$stable_publication_packet_dir/v4-stable-publication.json" <<'JSON'
{
  "schemaVersion": 1,
  "generatedAt": "2026-06-20T00:00:00Z",
  "tool": "shipguard v4 stable-publication",
  "surface": "ShipGuard V4 Stable Publication Proof",
  "status": "review",
  "stableV4Release": false,
  "stablePublicationGates": [
    {
      "receipt": "githubReleaseMetadataProof",
      "status": "review",
      "nextCommand": "./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable"
    }
  ],
  "resultUX": {
    "status": "review",
    "verdict": "REVIEW: Stable publication blocked.",
    "proofSource": "githubReleaseMetadataProof",
    "whyItMatters": "Stable-v4 publication must be proven from public release artifacts and external evidence.",
    "nextCommand": "./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable",
    "nextActionSummary": "Complete githubReleaseMetadataProof before claiming stable-v4 publication."
  },
  "reportQualityQuestions": [
    "Can ShipGuard prove stable-v4 publication from real release metadata, release notes, downloaded assets, external adoption evidence, security evidence, and post-release consumer proof?"
  ],
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  }
}
JSON
cat > "$stable_publication_packet_dir/v4-stable-publication.md" <<'MD'
# ShipGuard V4 Stable Publication Proof

## Result

- Verdict: REVIEW: Stable publication blocked.
- Proof source: githubReleaseMetadataProof
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence.
- Next command: `./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable`
MD
./bin/shipguard ios report-quality \
  --reports "$stable_publication_packet_dir" \
  --out "$tmp_dir/stable-publication-packet-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "stable-publication-evidence-packet-missing"' "$tmp_dir/stable-publication-packet-quality/ios-report-quality.json"

stable_publication_templates_dir="$tmp_dir/stable-publication-templates"
mkdir -p "$stable_publication_templates_dir"
cat > "$stable_publication_templates_dir/v4-stable-publication.json" <<'JSON'
{
  "schemaVersion": 1,
  "generatedAt": "2026-06-20T00:00:00Z",
  "tool": "shipguard v4 stable-publication",
  "surface": "ShipGuard V4 Stable Publication Proof",
  "status": "review",
  "stableV4Release": false,
  "stablePublicationEvidencePacket": {
    "schemaVersion": 1,
    "status": "review",
    "stableV4Release": false,
    "requiredEvidenceCount": 7,
    "passedEvidenceCount": 5,
    "missingEvidenceIds": [
      "independent-adoption-evidence",
      "final-security-review-evidence"
    ],
    "firstBlockingGate": {
      "id": "independent-adoption-evidence",
      "receipt": "externalAdoptionEvidenceStableGate",
      "status": "not-provided",
      "summary": "Adoption evidence missing.",
      "nextCommand": "./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v4-stable-publication --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable"
    },
    "requiredEvidence": [
      {"id": "github-release-metadata", "receipt": "githubReleaseMetadataProof", "status": "pass", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "release-notes", "receipt": "releaseNotesProof", "status": "pass", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "launchkey-candidate-packet", "receipt": "releaseCandidatePacketProof", "status": "pass", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "downloaded-release-assets", "receipt": "publishedReleaseAssetProof", "status": "pass", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "post-release-consumer-proof", "receipt": "postReleaseConsumerProof", "status": "pass", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "independent-adoption-evidence", "receipt": "externalAdoptionEvidenceStableGate", "status": "not-provided", "requiredForStableV4": true, "realEvidenceRequired": true},
      {"id": "final-security-review-evidence", "receipt": "securityReviewEvidenceStableGate", "status": "not-provided", "requiredForStableV4": true, "realEvidenceRequired": true}
    ],
    "nonClaims": [
      "Fixture adoption records do not prove real stable-v4 publication."
    ]
  },
  "reportQualityQuestions": [
    "Does the stable-publication evidence packet list every required real-evidence input, first blocker, next command, and non-claim before a stable-v4 announcement?"
  ],
  "scopeBoundary": {
    "shipguardOnly": true,
    "targetAppsReadOnly": true
  }
}
JSON
cat > "$stable_publication_templates_dir/v4-stable-publication.md" <<'MD'
# ShipGuard V4 Stable Publication Proof

## Evidence Packet

| Evidence | Status |
| --- | --- |
| `independent-adoption-evidence` | `not-provided` |
MD
./bin/shipguard ios report-quality \
  --reports "$stable_publication_templates_dir" \
  --out "$tmp_dir/stable-publication-templates-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "stable-publication-evidence-templates-missing"' "$tmp_dir/stable-publication-templates-quality/ios-report-quality.json"
grep -q '"ruleId": "stable-publication-evidence-templates-markdown-missing"' "$tmp_dir/stable-publication-templates-quality/ios-report-quality.json"
grep -q '"ruleId": "stable-publication-evidence-starter-kit-missing"' "$tmp_dir/stable-publication-templates-quality/ios-report-quality.json"
grep -q '"ruleId": "stable-publication-evidence-starter-kit-markdown-missing"' "$tmp_dir/stable-publication-templates-quality/ios-report-quality.json"

launchkey_skip_dir="$tmp_dir/launchkey-proof-dir-skip"
mkdir -p \
  "$launchkey_skip_dir/fresh-install-prefix/lib/shipguard/examples/demo-reports/arena" \
  "$launchkey_skip_dir/fresh-install-work/extracted/shipguard-v0.0.0" \
  "$launchkey_skip_dir/upgrade-prefix/lib/shipguard/examples/demo-reports/arena" \
  "$launchkey_skip_dir/upgrade-work/candidate/shipguard-v0.0.0" \
  "$launchkey_skip_dir/rollback-prefix/lib/shipguard/examples/demo-reports/arena" \
  "$launchkey_skip_dir/rollback-work/extracted/shipguard-v0.0.0" \
  "$launchkey_skip_dir/downloaded-release-assets" \
  "$launchkey_skip_dir/release-consume" \
  "$launchkey_skip_dir/stable-publication-launch-relay" \
  "$launchkey_skip_dir/stable-publication-release-notes" \
  "$launchkey_skip_dir/fresh-install-prefix/lib/shipguard/fixtures/promotions" \
  "$launchkey_skip_dir/upgrade-prefix/lib/shipguard/fixtures/promotions" \
  "$launchkey_skip_dir/rollback-prefix/lib/shipguard/fixtures/promotions"
cat > "$launchkey_skip_dir/v4-release-candidate.json" <<'JSON'
{
  "schemaVersion": 1,
  "tool": "shipguard v4 release-candidate",
  "surface": "ShipGuard V4 Release Candidate Readiness",
  "generatedAt": "2026-06-19T00:00:00Z",
  "status": "pass",
  "resultUX": {
    "nextCommand": "./tests/v4_release_candidate_test.sh"
  },
  "reportQualityQuestions": [
    "Can a fresh user install, upgrade, uninstall, and validate ShipGuard from the release package without maintainer context?"
  ]
}
JSON
cat > "$launchkey_skip_dir/v4-release-candidate.md" <<'MD'
# ShipGuard V4 Release Candidate Readiness

## Result

The root LaunchKey report is the only report-quality input here.
MD
cat > "$launchkey_skip_dir/fresh-install-prefix/lib/shipguard/examples/demo-reports/arena/results.json" <<'JSON'
{
  "not": "a ShipGuard report"
}
JSON
cat > "$launchkey_skip_dir/fresh-install-work/extracted/shipguard-v0.0.0/embedded.json" <<'JSON'
{
  "tool": "",
  "findings": [
    {
      "severity": "high"
    }
  ]
}
JSON
cat > "$launchkey_skip_dir/upgrade-prefix/lib/shipguard/examples/demo-reports/arena/results.json" <<'JSON'
{
  "not": "an upgrade source report"
}
JSON
cat > "$launchkey_skip_dir/upgrade-work/candidate/shipguard-v0.0.0/embedded.json" <<'JSON'
{
  "tool": "",
  "findings": [
    {
      "severity": "high"
    }
  ]
}
JSON
cat > "$launchkey_skip_dir/rollback-prefix/lib/shipguard/examples/demo-reports/arena/results.json" <<'JSON'
{
  "not": "a rollback source report"
}
JSON
cat > "$launchkey_skip_dir/rollback-work/extracted/shipguard-v0.0.0/embedded.json" <<'JSON'
{
  "tool": "",
  "findings": [
    {
      "severity": "high"
    }
  ]
}
JSON
cat > "$launchkey_skip_dir/release-consume/consumer-report.json" <<'JSON'
{
  "consumer": "proof receipt, not a report-quality source report"
}
JSON
cat > "$launchkey_skip_dir/downloaded-release-assets/attestation-badge.json" <<'JSON'
{
  "downloaded": "release asset, not a report-quality source report"
}
JSON
cat > "$launchkey_skip_dir/stable-publication-release-notes/release-notes-checklist.json" <<'JSON'
{
  "draftOnly": true,
  "status": "review",
  "topicMatrix": []
}
JSON
cat > "$launchkey_skip_dir/stable-publication-launch-relay/launch-relay-checklist.json" <<'JSON'
{
  "draftOnly": true,
  "publicPostingAllowed": false,
  "status": "blocked-until-stable-publication-pass"
}
JSON
cat > "$launchkey_skip_dir/fresh-install-prefix/lib/shipguard/fixtures/promotions/fixture-promotion-manifest.json" <<'JSON'
{
  "candidateCount": "bad"
}
JSON
cat > "$launchkey_skip_dir/upgrade-prefix/lib/shipguard/fixtures/promotions/fixture-promotion-manifest.json" <<'JSON'
{
  "candidateCount": "bad"
}
JSON
cat > "$launchkey_skip_dir/rollback-prefix/lib/shipguard/fixtures/promotions/fixture-promotion-manifest.json" <<'JSON'
{
  "candidateCount": "bad"
}
JSON
./bin/shipguard ios report-quality \
  --reports "$launchkey_skip_dir" \
  --out "$tmp_dir/launchkey-proof-dir-skip-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/launchkey-proof-dir-skip-quality/ios-report-quality.json"
grep -q '"reportCount": 1' "$tmp_dir/launchkey-proof-dir-skip-quality/ios-report-quality.json"
grep -q '"path": "<report-input-1>/v4-release-candidate.json"' "$tmp_dir/launchkey-proof-dir-skip-quality/ios-report-quality.json"
if grep -q 'fresh-install-prefix\|fresh-install-work\|upgrade-prefix\|upgrade-work\|rollback-prefix\|rollback-work\|downloaded-release-assets\|release-consume\|stable-publication-launch-relay\|stable-publication-release-notes\|fixture-promotion-manifest' "$tmp_dir/launchkey-proof-dir-skip-quality/ios-report-quality.json"; then
  echo "report-quality must skip generated LaunchKey proof directories under report outputs" >&2
  exit 1
fi

stable_publication_fixture="fixtures/ios-report-quality/stable-publication-complete"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_fixture" \
  --out "$tmp_dir/stable-publication-complete-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-complete-fixture-quality/ios-report-quality.json"
grep -q '"reportCount": 1' "$tmp_dir/stable-publication-complete-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-complete-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/stable-publication-complete"' "$tmp_dir/stable-publication-complete-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/stable-publication-complete-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage_paths = {item.get("publicFixturePath") for item in data.get("fixtureCoverage", [])}
assert "fixtures/ios-report-quality/stable-publication-complete" in coverage_paths
assert "fixtures/ios-report-quality/stable-publication-release-notes-authoring" in coverage_paths
assert data.get("fixtureCandidates") == []
assert data.get("priorityAction", {}).get("kind") == "review-existing-fixture"
PY

stable_publication_block_fixture="fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-repo"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_block_fixture" \
  --out "$tmp_dir/stable-publication-block-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-block-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-block-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-repo"' "$tmp_dir/stable-publication-block-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-block-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/stable-publication-block-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard v4 stable-publication", item
assert item.get("fixtureType") == "shipguard-release-proof-quality-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-repo", item
assert "block every stable-v4 claim" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-repo", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

stable_publication_packet_fixture="fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-evid"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_packet_fixture" \
  --out "$tmp_dir/stable-publication-packet-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-packet-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-packet-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-evid"' "$tmp_dir/stable-publication-packet-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-packet-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/stable-publication-packet-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard v4 stable-publication", item
assert item.get("fixtureType") == "shipguard-release-proof-quality-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-evid", item
assert "evidence packet list every required real-evidence input" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publication-evid", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

stable_publication_templates_fixture="fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f54b9564"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_templates_fixture" \
  --out "$tmp_dir/stable-publication-templates-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-templates-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-templates-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f54b9564"' "$tmp_dir/stable-publication-templates-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-templates-fixture-quality/ios-report-quality.json"
python3 - <<'PY' "$tmp_dir/stable-publication-templates-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard v4 stable-publication", item
assert item.get("fixtureType") == "shipguard-release-proof-quality-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f54b9564", item
assert "draft-only evidence templates" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f54b9564", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

stable_publication_starter_fixture="fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-481951ae"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_starter_fixture" \
  --out "$tmp_dir/stable-publication-starter-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-starter-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-starter-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-481951ae"' "$tmp_dir/stable-publication-starter-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-starter-fixture-quality/ios-report-quality.json"
grep -q '"stablePublicationEvidenceStarterKit":' "$stable_publication_starter_fixture/fixture-report.json"
grep -q 'Evidence Starter Kit' "$stable_publication_starter_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/stable-publication-starter-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard v4 stable-publication", item
assert item.get("fixtureType") == "report-evidence-promotion-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-481951ae", item
assert "draft-only evidence starter kit" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-481951ae", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

stable_publication_launch_relay_fixture="fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f059d5b6"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_launch_relay_fixture" \
  --out "$tmp_dir/stable-publication-launch-relay-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-launch-relay-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-launch-relay-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f059d5b6"' "$tmp_dir/stable-publication-launch-relay-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-launch-relay-fixture-quality/ios-report-quality.json"
grep -q '"stablePublicationLaunchRelayDrafts":' "$stable_publication_launch_relay_fixture/fixture-report.json"
grep -q 'Launch Relay Drafts' "$stable_publication_launch_relay_fixture/fixture-report.md"
python3 - <<'PY' "$tmp_dir/stable-publication-launch-relay-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard v4 stable-publication", item
assert item.get("fixtureType") == "shipguard-release-proof-quality-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f059d5b6", item
assert "launch relay drafts" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/01-shipguard-v4-stable-publication-does-the-stable-publica-f059d5b6", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

stable_publication_product_hunt_missing_relay="$tmp_dir/stable-publication-product-hunt-missing-relay"
mkdir -p "$stable_publication_product_hunt_missing_relay"
python3 - <<'PY' "$stable_publication_launch_relay_fixture/fixture-report.json" "$stable_publication_launch_relay_fixture/fixture-report.md" "$stable_publication_product_hunt_missing_relay"
import json
import pathlib
import sys

source_json = pathlib.Path(sys.argv[1])
source_md = pathlib.Path(sys.argv[2])
target = pathlib.Path(sys.argv[3])
report = json.loads(source_json.read_text(encoding="utf-8"))
report.pop("stablePublicationLaunchRelayDrafts", None)
report["reportQualityQuestions"] = [
    "Does the stable-publication report prepare Product Hunt and public posting drafts without bypassing explicit human approval?",
]
(target / "v4-stable-publication.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
(target / "v4-stable-publication.md").write_text(source_md.read_text(encoding="utf-8"), encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$stable_publication_product_hunt_missing_relay" \
  --out "$tmp_dir/stable-publication-product-hunt-missing-relay-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "stable-publication-launch-relay-drafts-missing"' "$tmp_dir/stable-publication-product-hunt-missing-relay-quality/ios-report-quality.json"
grep -q 'Product Hunt and public posting drafts' "$tmp_dir/stable-publication-product-hunt-missing-relay-quality/ios-report-quality.json"

stable_publication_value_fixture="fixtures/ios-report-quality/stable-publication-value-gauntlet-question"
./bin/shipguard ios report-quality \
  --reports "$stable_publication_value_fixture" \
  --out "$tmp_dir/stable-publication-value-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/stable-publication-value-gauntlet-question"' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.json"
grep -q 'stable-v4 publication' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/stable-publication-value-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard value-gauntlet", item
assert item.get("candidateId") == "stable-publication-value-gauntlet-question", item
assert item.get("fixtureType") == "shipguard-release-proof-quality-fixture", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/stable-publication-value-gauntlet-question", item
assert "stable-v4 publication" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/stable-publication-value-gauntlet-question", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

product_release_value_fixture="fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question"
./bin/shipguard ios report-quality \
  --reports "$product_release_value_fixture" \
  --out "$tmp_dir/product-release-value-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question"' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.json"
grep -q 'v4 product release' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/product-release-value-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard value-gauntlet", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question", item
assert "v4 product release" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/product-release-stabilization-value-gauntlet-question", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

surface_proof_value_fixture="fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question"
./bin/shipguard ios report-quality \
  --reports "$surface_proof_value_fixture" \
  --out "$tmp_dir/surface-proof-value-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question"' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.json"
grep -q 'proof boundary' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/surface-proof-value-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard value-gauntlet", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question", item
assert "proof boundary" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/surface-proof-boundary-value-gauntlet-question", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

plugin_skill_value_fixture="fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question"
./bin/shipguard ios report-quality \
  --reports "$plugin_skill_value_fixture" \
  --out "$tmp_dir/plugin-skill-value-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.json"
grep -q '"kind": "review-existing-fixture"' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.json"
grep -q '"publicFixturePath": "fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question"' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.json"
grep -q 'plugin skills' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.md"
python3 - <<'PY' "$tmp_dir/plugin-skill-value-fixture-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
coverage = data.get("fixtureCoverage") or []
assert len(coverage) == 1, coverage
item = coverage[0]
assert item.get("sourceTool") == "shipguard value-gauntlet", item
assert item.get("publicFixturePath") == "fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question", item
assert "plugin skills" in item.get("question", ""), item
priority = data.get("priorityAction") or {}
assert priority.get("kind") == "review-existing-fixture", priority
assert priority.get("existingFixturePath") == "fixtures/ios-report-quality/plugin-skill-routing-value-gauntlet-question", priority
assert data.get("fixtureCandidates") == [], data.get("fixtureCandidates")
PY

./bin/shipguard v4 preview \
  --path . \
  --out "$tmp_dir/v4-preview" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/v4-preview" \
  --out "$tmp_dir/v4-preview-quality" \
  --shareable \
  --write-fixture-candidates "$tmp_dir/v4-preview-fixtures" >/dev/null
python3 - <<'PY' "$tmp_dir/v4-preview-quality/ios-report-quality.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
priority = data.get("priorityAction") or {}
covered = {
    "Are all v4 preview claims backed by runnable ShipGuard commands instead of roadmap prose?":
        (
            "fixtures/ios-report-quality/01-shipguard-v4-preview-are-all-v4-preview-claims-backed-by-runnabl",
            "shipguard-v4-preview-quality-fixture",
        ),
    "Can a solo developer understand what is stable, what is preview-only, and what remains blocked?":
        (
            "fixtures/ios-report-quality/02-shipguard-v4-preview-can-a-solo-developer-understand-what-is-sta",
            "shipguard-v4-preview-quality-fixture",
        ),
    "Does the report give a concrete next proof step rather than a broad product wish?":
        (
            "fixtures/ios-report-quality/01-shipguard-v4-preview-does-the-report-give-a-concrete-next-proof",
            "shipguard-v4-preview-quality-fixture",
        ),
    "Are private-app observations excluded from public artifacts unless converted into redacted fixtures?":
        (
            "fixtures/ios-report-quality/03-shipguard-v4-preview-are-private-app-observations-excluded-from",
            "shipguard-eval-boundary-fixture",
        ),
}
if priority.get("kind") != "all-actionability-covered":
    raise SystemExit(f"expected all v4 preview actionability questions covered, got {priority!r}")
if priority.get("coveredQuestionCount") != len(covered):
    raise SystemExit(f"expected all covered v4 preview questions, got {priority!r}")
coverage = data.get("fixtureCoverage") or []
for question, (path, fixture_type) in covered.items():
    if not any(
        item.get("question") == question
        and item.get("publicFixturePath") == path
        and item.get("fixtureType") == fixture_type
        for item in coverage
    ):
        raise SystemExit(f"expected v4 preview fixture coverage for {question!r}: {coverage!r}")
candidates = data.get("fixtureCandidates") or []
if candidates:
    raise SystemExit(f"expected no duplicate v4 preview fixture candidates after coverage, got {candidates!r}")
PY

for fixture in \
  fixtures/ios-report-quality/01-shipguard-v4-preview-are-all-v4-preview-claims-backed-by-runnabl \
  fixtures/ios-report-quality/01-shipguard-v4-preview-does-the-report-give-a-concrete-next-proof \
  fixtures/ios-report-quality/02-shipguard-v4-preview-can-a-solo-developer-understand-what-is-sta \
  fixtures/ios-report-quality/03-shipguard-v4-preview-are-private-app-observations-excluded-from
do
  ./bin/shipguard ios report-quality \
    --reports "$fixture" \
    --out "$tmp_dir/$(basename "$fixture")-quality" \
    --shareable >/dev/null
  grep -q '"status": "pass"' "$tmp_dir/$(basename "$fixture")-quality/ios-report-quality.json"
  grep -q '"kind": "review-existing-fixture"' "$tmp_dir/$(basename "$fixture")-quality/ios-report-quality.json"
  grep -q '"fixtureCandidates": \[\]' "$tmp_dir/$(basename "$fixture")-quality/ios-report-quality.json"
done

verify_first_reports="$tmp_dir/verify-first-reports"
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out "$verify_first_reports/task" \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard verify \
  --task "$verify_first_reports/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out "$verify_first_reports/pass" >/dev/null
./bin/shipguard verify \
  --task "$verify_first_reports/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test.log \
  --claim "Implemented scoped notification permission copy." \
  --out "$verify_first_reports/review" >/dev/null
set +e
./bin/shipguard verify \
  --task "$verify_first_reports/task/shipguard-task.json" \
  --diff examples/verify-first/diffs/protected-workflow.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Notification permission copy is fully verified." \
  --out "$verify_first_reports/blocked" >/dev/null
verify_first_blocked_status=$?
set -e
if [[ "$verify_first_blocked_status" -ne 2 ]]; then
  echo "expected verify-first blocked report to exit 2, got $verify_first_blocked_status" >&2
  exit 1
fi
./bin/shipguard ios report-quality \
  --reports "$verify_first_reports" \
  --out "$tmp_dir/verify-first-quality" \
  --write-fixture-candidates "$tmp_dir/verify-first-fixture-candidates" \
  --shareable >/dev/null
python3 - <<'PY' "$tmp_dir/verify-first-quality/ios-report-quality.json" "$tmp_dir/verify-first-fixture-candidates"
import json
import sys
from pathlib import Path

data = json.load(open(sys.argv[1], encoding="utf-8"))
candidate_root = Path(sys.argv[2])
questions = [
    "Did prepare produce one durable object connecting goal, risk, scope, proof, claims, and verdict?",
    "Can verify reject unsupported completion claims with an exact next action?",
    "Did prepare identify notification/permission owner scopes, review-only lifecycle/plist surfaces, and forbidden entitlement/project changes?",
    "Did verify require permission-state and denied-state proof instead of treating a generic test log as enough?",
    "Did the verdict separate simulator denied-state proof from physical-device prompt proof before release claims?",
]
coverage = data.get("fixtureCoverage") or []
if not any(
    item.get("question") == questions[0]
    and item.get("publicFixturePath") == "fixtures/ios-report-quality/01-shipguard-prepare-did-prepare-produce-one-durable-objec-5d1f722f"
    and item.get("fixtureType") == "shipguard-verify-first-task-contract-fixture"
    for item in coverage
):
    raise SystemExit(f"expected promoted verify-first fixture coverage for first question: {coverage!r}")
candidates = data.get("fixtureCandidates") or []
if [item.get("sourceQuestion") for item in candidates] != questions[1:]:
    raise SystemExit(f"verify-first candidates did not match questions: {candidates!r}")
if {item.get("fixtureType") for item in candidates} != {"shipguard-verify-first-task-contract-fixture"}:
    raise SystemExit(f"unexpected verify-first fixture types: {candidates!r}")
priority = data.get("priorityAction") or {}
if priority.get("kind") != "answer-actionability-question":
    raise SystemExit(f"expected actionability priority, got {priority!r}")
if priority.get("question") != questions[1]:
    raise SystemExit(f"expected verify-first QA to advance to second question, got {priority!r}")
if "write-fixture-candidates" not in str(priority.get("nextCommand") or ""):
    raise SystemExit(f"expected materialization next command, got {priority!r}")
for item in candidates:
    candidate_id = item.get("candidateId")
    if not candidate_id:
        raise SystemExit(f"missing candidate id: {item!r}")
    directory = candidate_root / candidate_id
    expected = {"README.md", "fixture-candidate.json", "fixture-report.json", "fixture-report.md"}
    actual = {path.name for path in directory.iterdir()} if directory.is_dir() else set()
    if not expected <= actual:
        raise SystemExit(f"materialized files missing for {candidate_id}: {actual!r}")
    report = json.load(open(directory / "fixture-report.json", encoding="utf-8"))
    if report.get("tool") != "shipguard prepare":
        raise SystemExit(f"expected synthetic verify-first fixture to keep source tool, got {report.get('tool')!r}")
    if report.get("scopeBoundary", {}).get("shipguardOnly") is not True:
        raise SystemExit(f"missing ShipGuard-only boundary in {directory}")
    replay = report.get("quickstartReplay") or {}
    if not replay:
        raise SystemExit(f"synthetic verify-first fixture missing quickstartReplay in {directory}")
    markdown = (directory / "fixture-report.md").read_text(encoding="utf-8")
    if "Quickstart Replay" not in markdown:
        raise SystemExit(f"synthetic verify-first fixture missing Quickstart Replay Markdown in {directory}")
PY

cp "$verify_first_reports/task/shipguard-task.json" "$tmp_dir/missing-quickstart-replay.json"
python3 - <<'PY' "$tmp_dir/missing-quickstart-replay.json"
import json
import sys

path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data.pop("quickstartReplay", None)
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-quickstart-replay.json" \
  --out "$tmp_dir/missing-quickstart-replay-quality" \
  --shareable >/dev/null
grep -q '"ruleId": "task-contract-quickstart-replay-missing"' "$tmp_dir/missing-quickstart-replay-quality/ios-report-quality.json"

./bin/shipguard ios report-quality \
  --reports fixtures/ios-report-quality/01-shipguard-prepare-did-prepare-produce-one-durable-objec-5d1f722f \
  --out "$tmp_dir/verify-first-promoted-fixture-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/verify-first-promoted-fixture-quality/ios-report-quality.json"
grep -q '"fixtureCandidates": \[\]' "$tmp_dir/verify-first-promoted-fixture-quality/ios-report-quality.json"

python3 - <<'PY'
import json
from pathlib import Path

root = Path("fixtures/ios-report-quality")
problems = []
for candidate_path in sorted(root.rglob("fixture-candidate.json")):
    folder = candidate_path.parent.name
    expected_path = f"fixtures/ios-report-quality/{folder}"
    candidate = json.load(open(candidate_path, encoding="utf-8"))
    if candidate.get("candidateId") != folder:
        problems.append(f"{candidate_path}: candidateId={candidate.get('candidateId')!r}, expected {folder!r}")
    if candidate.get("publicFixturePath") != expected_path:
        problems.append(f"{candidate_path}: publicFixturePath={candidate.get('publicFixturePath')!r}, expected {expected_path!r}")
    report_path = candidate_path.parent / "fixture-report.json"
    if not report_path.exists():
        continue
    report = json.load(open(report_path, encoding="utf-8"))
    nested = report.get("fixtureCandidate")
    if not isinstance(nested, dict):
        continue
    if nested.get("candidateId") != folder:
        problems.append(f"{report_path}: fixtureCandidate.candidateId={nested.get('candidateId')!r}, expected {folder!r}")
    if nested.get("publicFixturePath") != expected_path:
        problems.append(f"{report_path}: fixtureCandidate.publicFixturePath={nested.get('publicFixturePath')!r}, expected {expected_path!r}")
    if candidate.get("fixtureType") and nested.get("fixtureType") != candidate.get("fixtureType"):
        problems.append(f"{report_path}: fixtureCandidate.fixtureType={nested.get('fixtureType')!r}, expected {candidate.get('fixtureType')!r}")

if problems:
    raise SystemExit("\n".join(problems))
PY

json_stdout="$(./bin/shipguard ios report-quality --reports "$reports" --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
grep -q '"tool": "shipguard ios report-quality"' <<<"$json_stdout"

echo "ios report quality tests passed"
