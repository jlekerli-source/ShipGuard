#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard lean audit --help >/dev/null
./bin/shipguard lean review --help >/dev/null
./bin/shipguard lean debt --help >/dev/null
python3 -m py_compile scripts/lean_audit.py scripts/lean_review.py scripts/lean_debt.py

./bin/shipguard lean audit \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/lean" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/lean/lean-audit.json"
test -f "$tmp_dir/lean/lean-audit.md"
grep -q '"tool": "shipguard lean audit"' "$tmp_dir/lean/lean-audit.json"
grep -q '"surface": "ShipGuard Lean Deck"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "native-date-input"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "native-color-input"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "dependency-date-helper-review"' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "do-not-cut-safety-logic-without-proof"' "$tmp_dir/lean/lean-audit.json"
grep -q '"precisionReview":' "$tmp_dir/lean/lean-audit.json"
grep -q '"leanDebtLedger":' "$tmp_dir/lean/lean-audit.json"
grep -q '"marker": "shipguard-lean"' "$tmp_dir/lean/lean-audit.json"
grep -q '"hasUpgradeTrigger": true' "$tmp_dir/lean/lean-audit.json"
grep -q '"deleteList":' "$tmp_dir/lean/lean-audit.json"
grep -q '"simplifyFirst":' "$tmp_dir/lean/lean-audit.json"
grep -q '"keepList":' "$tmp_dir/lean/lean-audit.json"
grep -q '"blockedByProof":' "$tmp_dir/lean/lean-audit.json"
grep -q '"ruleId": "thin-wrapper-review"' "$tmp_dir/lean/lean-audit.json"
grep -q '"scopeBoundary"' "$tmp_dir/lean/lean-audit.json"
grep -q '"reportQualityQuestions"' "$tmp_dir/lean/lean-audit.json"
grep -q '"scanScope":' "$tmp_dir/lean/lean-audit.json"
grep -q 'Ponytail' "$tmp_dir/lean/lean-audit.md"
grep -q '## Precision Review' "$tmp_dir/lean/lean-audit.md"
grep -q '## Lean Debt Ledger' "$tmp_dir/lean/lean-audit.md"
grep -q 'replace when fixture needs multi-call-site proof' "$tmp_dir/lean/lean-audit.md"
grep -q 'Keep Without More Proof' "$tmp_dir/lean/lean-audit.md"
grep -q 'Do not cut trust-boundary validation without proof' "$tmp_dir/lean/lean-audit.md"
if grep -q '/Users/' "$tmp_dir/lean/lean-audit.json"; then
  echo "shareable lean audit leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null

grep -q 'shipguard lean audit' "$tmp_dir/quality/ios-report-quality.json"

./bin/shipguard lean audit \
  --path . \
  --out "$tmp_dir/repo-lean" \
  --shipguard-eval \
  --shareable >/dev/null

grep -q '"fixtures"' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '"leanEvidence":' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '"leanDebtLedger":' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '"firstMarkerLines":' "$tmp_dir/repo-lean/lean-audit.json"
grep -q '## Lean Evidence Packets' "$tmp_dir/repo-lean/lean-audit.md"
if grep -q 'fixtures/lean-audit-demo' "$tmp_dir/repo-lean/lean-audit.json"; then
  echo "repo-level lean audit should not let public fixtures dominate findings" >&2
  exit 1
fi
if grep -q '"ruleId": "native-date-input"' "$tmp_dir/repo-lean/lean-audit.json"; then
  echo "repo-level lean audit should not treat prose such as 'moments' as a date picker dependency" >&2
  exit 1
fi

./bin/shipguard lean review \
  --path fixtures/lean-audit-demo \
  --diff fixtures/lean-audit-demo/diffs/overbuilt-widget.diff \
  --out "$tmp_dir/review" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/review/lean-review.json"
test -f "$tmp_dir/review/lean-review.md"
grep -q '"tool": "shipguard lean review"' "$tmp_dir/review/lean-review.json"
grep -q '"surface": "ShipGuard Lean Review"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "native-date-input-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "dependency-small-helper-diff"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "thin-wrapper-diff-review"' "$tmp_dir/review/lean-review.json"
grep -q '"ruleId": "deferred-shortcut-without-trigger"' "$tmp_dir/review/lean-review.json"
grep -q '"reviewLines":' "$tmp_dir/review/lean-review.json"
grep -q '"precisionReview":' "$tmp_dir/review/lean-review.json"
grep -q 'ShipGuard Lean Review' "$tmp_dir/review/lean-review.md"
grep -q 'Diff Review' "$tmp_dir/review/lean-review.md"
if grep -q '/Users/' "$tmp_dir/review/lean-review.json"; then
  echo "shareable lean review leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard lean debt \
  --path fixtures/lean-audit-demo \
  --out "$tmp_dir/debt" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/debt/lean-debt.json"
test -f "$tmp_dir/debt/lean-debt.md"
grep -q '"tool": "shipguard lean debt"' "$tmp_dir/debt/lean-debt.json"
grep -q '"surface": "ShipGuard Lean Debt"' "$tmp_dir/debt/lean-debt.json"
grep -q '"marker": "shipguard-lean"' "$tmp_dir/debt/lean-debt.json"
grep -q '"status": "tracked"' "$tmp_dir/debt/lean-debt.json"
grep -q 'ShipGuard Lean Debt' "$tmp_dir/debt/lean-debt.md"
if grep -q '/Users/' "$tmp_dir/debt/lean-debt.json"; then
  echo "shareable lean debt leaked an absolute user path" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/lean" \
  --reports "$tmp_dir/review" \
  --reports "$tmp_dir/debt" \
  --out "$tmp_dir/lean-family-quality" \
  --shareable >/dev/null

grep -q 'shipguard lean audit' "$tmp_dir/lean-family-quality/ios-report-quality.json"
grep -q 'shipguard lean review' "$tmp_dir/lean-family-quality/ios-report-quality.json"
grep -q 'shipguard lean debt' "$tmp_dir/lean-family-quality/ios-report-quality.json"

echo "lean audit tests passed"
