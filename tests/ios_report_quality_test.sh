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
grep -q '# iOS ShipGuard Report Quality' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios performance' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'shipguard ios design' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'local-path-shareability-warning' "$tmp_dir/quality/ios-report-quality.json"

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

json_stdout="$(./bin/shipguard ios report-quality --reports "$reports" --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios report-quality"'

echo "ios report quality tests passed"
