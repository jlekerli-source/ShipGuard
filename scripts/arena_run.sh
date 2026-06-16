#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer arena run

Usage:
  codex-maintainer arena run --fixture <fixture-dir> [--out <dir>]

Fixture case format:
  <fixture-dir>/<case-id>/run.md
  <fixture-dir>/<case-id>/task.md       optional
  <fixture-dir>/<case-id>/diff.patch    optional
  <fixture-dir>/<case-id>/tests.log     optional

Outputs:
  results.json
  index.md
  runs/<case-id>/report.md
  runs/<case-id>/report.json
USAGE
}

fail() {
  echo "arena: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

json_total() {
  perl -0ne 'print $1 if /"total":\s*([0-9]+)/' "$1"
}

json_verdict() {
  perl -0ne 'print $1 if /"verdict":\s*"((?:\\.|[^"])*)"/' "$1"
}

json_category_score() {
  local key="$1"
  local file="$2"
  perl -0ne 'BEGIN { $key = shift @ARGV } if (/"\Q$key\E":\s*\{[^}]*"score":\s*([0-9]+)/s) { print $1 }' "$key" "$file"
}

json_has_tests() {
  perl -0ne 'print $1 if /"has_tests":\s*(true|false)/' "$1"
}

fixture_dir=""
out_dir="arena-report"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --fixture)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--fixture requires a value"
      fixture_dir="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[[ -n "$fixture_dir" ]] || fail "--fixture is required"
[[ -d "$fixture_dir" ]] || fail "fixture directory not found: $fixture_dir"

case_dirs=()
while IFS= read -r case_dir; do
  case_dirs+=("$case_dir")
done < <(find "$fixture_dir" -mindepth 1 -maxdepth 1 -type d | sort)

[[ "${#case_dirs[@]}" -gt 0 ]] || fail "fixture directory has no case subdirectories: $fixture_dir"

mkdir -p "$out_dir/runs"
generated_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
tool_version="$(sed -n '1p' "$tool_root/VERSION")"

case_ids=()
case_totals=()
case_verdicts=()
case_high_counts=()
case_scope_scores=()
case_validation_scores=()
case_has_tests=()

total_sum=0
scope_sum=0
validation_sum=0
high_sum=0
has_tests_count=0

for case_dir in "${case_dirs[@]}"; do
  case_id="$(basename "$case_dir")"
  run_file="$case_dir/run.md"
  task_file="$case_dir/task.md"
  diff_file="$case_dir/diff.patch"
  tests_file="$case_dir/tests.log"
  case_out="$out_dir/runs/$case_id"

  [[ -f "$run_file" ]] || fail "missing required case run file: $run_file"

  args=(--run "$run_file" --out "$case_out")
  [[ -f "$task_file" ]] && args+=(--task "$task_file")
  [[ -f "$diff_file" ]] && args+=(--diff "$diff_file")
  [[ -f "$tests_file" ]] && args+=(--tests "$tests_file")

  "$tool_root/scripts/autopsy_report.sh" "${args[@]}" >/dev/null

  report_json="$case_out/report.json"
  total="$(json_total "$report_json")"
  verdict="$(json_verdict "$report_json")"
  scope_score="$(json_category_score scope_control "$report_json")"
  validation_score="$(json_category_score validation_quality "$report_json")"
  has_tests="$(json_has_tests "$report_json")"
  high_count="$(grep -c '"severity": "high"' "$report_json" || true)"

  case_ids+=("$case_id")
  case_totals+=("$total")
  case_verdicts+=("$verdict")
  case_high_counts+=("$high_count")
  case_scope_scores+=("$scope_score")
  case_validation_scores+=("$validation_score")
  case_has_tests+=("$has_tests")

  total_sum=$((total_sum + total))
  scope_sum=$((scope_sum + scope_score))
  validation_sum=$((validation_sum + validation_score))
  high_sum=$((high_sum + high_count))
  [[ "$has_tests" == "true" ]] && has_tests_count=$((has_tests_count + 1))
done

case_count="${#case_ids[@]}"
average_total="$(awk -v total="$total_sum" -v count="$case_count" 'BEGIN { printf "%.2f", total / count }')"
scope_average="$(awk -v total="$scope_sum" -v count="$case_count" 'BEGIN { printf "%.2f", total / count }')"
validation_average="$(awk -v total="$validation_sum" -v count="$case_count" 'BEGIN { printf "%.2f", total / count }')"
validation_evidence_ratio="$(awk -v total="$has_tests_count" -v count="$case_count" 'BEGIN { printf "%.2f", total / count }')"

{
  echo "{"
  echo "  \"schema_version\": \"0.1\","
  echo "  \"tool_version\": $(json_string "$tool_version"),"
  echo "  \"generated_at\": $(json_string "$generated_at"),"
  echo "  \"fixture\": $(json_string "$fixture_dir"),"
  echo "  \"summary\": {"
  echo "    \"case_count\": $case_count,"
  echo "    \"average_total\": $average_total,"
  echo "    \"high_risk_finding_count\": $high_sum,"
  echo "    \"validation_evidence_cases\": $has_tests_count,"
  echo "    \"validation_evidence_ratio\": $validation_evidence_ratio,"
  echo "    \"validation_quality_average\": $validation_average,"
  echo "    \"scope_control_average\": $scope_average"
  echo "  },"
  echo "  \"cases\": ["
  for i in "${!case_ids[@]}"; do
    comma=","
    [[ "$i" -eq "$((case_count - 1))" ]] && comma=""
    echo "    {\"id\": $(json_string "${case_ids[$i]}"), \"total\": ${case_totals[$i]}, \"max\": 12, \"verdict\": $(json_string "${case_verdicts[$i]}"), \"high_risk_findings\": ${case_high_counts[$i]}, \"scope_control\": ${case_scope_scores[$i]}, \"validation_quality\": ${case_validation_scores[$i]}, \"has_tests\": ${case_has_tests[$i]}, \"report_json\": $(json_string "runs/${case_ids[$i]}/report.json"), \"report_md\": $(json_string "runs/${case_ids[$i]}/report.md")}$comma"
  done
  echo "  ]"
  echo "}"
} > "$out_dir/results.json"

{
  echo "# Maintainer Arena Results"
  echo
  echo "- Generated: $generated_at"
  echo "- Tool version: $tool_version"
  echo "- Fixture: $fixture_dir"
  echo "- Cases: $case_count"
  echo "- Average score: $average_total/12"
  echo "- High-risk findings: $high_sum"
  echo "- Validation evidence: $has_tests_count/$case_count"
  echo "- Scope-control average: $scope_average/2"
  echo
  echo "## Cases"
  echo
  echo "| Case | Score | High-risk findings | Tests | Verdict |"
  echo "| --- | ---: | ---: | --- | --- |"
  for i in "${!case_ids[@]}"; do
    echo "| ${case_ids[$i]} | ${case_totals[$i]}/12 | ${case_high_counts[$i]} | ${case_has_tests[$i]} | ${case_verdicts[$i]} |"
  done
} > "$out_dir/index.md"

echo "wrote: $out_dir/results.json"
echo "wrote: $out_dir/index.md"
echo "average: $average_total/12"
