#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer autopsy

Usage:
  codex-maintainer autopsy --run <run.md> [--diff <patch.diff>] [--tests <test.log>] [--task <task.md>] [--policy <policy.conf>] [--out <dir>]

Outputs:
  report.md
  report.json
USAGE
}

fail() {
  echo "autopsy: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

extract_score() {
  local label="$1"
  local file="$2"
  local line
  line="$(grep -iF "$label" "$file" | head -n 1 || true)"
  if [[ "$line" =~ (^|[^0-9])([0-2])([^0-9]|$) ]]; then
    printf '%s\n' "${BASH_REMATCH[2]}"
  fi
}

verdict_for_total() {
  local total="$1"
  local high_count="$2"
  if [[ "$high_count" -gt 0 ]]; then
    echo "do not merge until high-risk findings are resolved"
  elif [[ "$total" -ge 10 ]]; then
    echo "usable maintainer-quality run"
  elif [[ "$total" -ge 7 ]]; then
    echo "probably useful; review weak categories"
  elif [[ "$total" -ge 4 ]]; then
    echo "analysis only; request a narrower repair pass"
  else
    echo "discard as implementation evidence"
  fi
}

run_file=""
diff_file=""
tests_file=""
task_file=""
policy_file=""
out_dir="autopsy-report"
max_changed_files=3
protected_pattern='Secrets|Credentials|Protected|AlarmRuntime|StoreKit'
validation_claim_pattern='(^|[^A-Za-z])((tests?|validation|ci).*(passed|green|success|succeeded)|all tests passed)([^A-Za-z]|$)'
risky_claim_pattern='(^|[^A-Za-z])(release[- ]ready|production[- ]ready|security[- ]safe|no vulnerabilities|secure|approved|live|guaranteed|proven)([^A-Za-z]|$)'

read_policy() {
  local file="$1"
  local line key value
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    [[ -z "$line" || "$line" != *"="* ]] && continue
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in
      max_changed_files)
        [[ "$value" =~ ^[0-9]+$ ]] || fail "policy max_changed_files must be an integer"
        max_changed_files="$value"
        ;;
      protected_patterns)
        protected_pattern="$value"
        ;;
      validation_claim_patterns)
        validation_claim_pattern="$value"
        ;;
      risky_claim_patterns)
        risky_claim_pattern="$value"
        ;;
      warn_below|fail_below)
        ;;
      *)
        fail "unknown policy key: $key"
        ;;
    esac
  done < "$file"
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --run)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--run requires a value"
      run_file="${2:-}"
      shift 2
      ;;
    --diff)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--diff requires a value"
      diff_file="${2:-}"
      shift 2
      ;;
    --tests)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--tests requires a value"
      tests_file="${2:-}"
      shift 2
      ;;
    --task)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--task requires a value"
      task_file="${2:-}"
      shift 2
      ;;
    --policy)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--policy requires a value"
      policy_file="${2:-}"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="${2:-}"
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

[[ -n "$run_file" ]] || fail "--run is required"
[[ -f "$run_file" ]] || fail "run file not found: $run_file"
[[ -z "$diff_file" || -f "$diff_file" ]] || fail "diff file not found: $diff_file"
[[ -z "$tests_file" || -f "$tests_file" ]] || fail "test log not found: $tests_file"
[[ -z "$task_file" || -f "$task_file" ]] || fail "task file not found: $task_file"
[[ -z "$policy_file" || -f "$policy_file" ]] || fail "policy file not found: $policy_file"
[[ -n "$policy_file" ]] && read_policy "$policy_file"

mkdir -p "$out_dir"
markdown_report="$out_dir/report.md"
json_report="$out_dir/report.json"
tool_version="$(sed -n '1p' "$tool_root/VERSION")"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

category_labels=(
  "Scope control"
  "Owner-file accuracy"
  "Risk awareness"
  "Validation quality"
  "Handoff honesty"
  "Regression awareness"
)
category_keys=(
  "scope_control"
  "owner_file_accuracy"
  "risk_awareness"
  "validation_quality"
  "handoff_honesty"
  "regression_awareness"
)
category_scores=()

finding_ids=()
finding_severities=()
finding_messages=()
finding_evidence=()

add_finding() {
  finding_ids+=("$1")
  finding_severities+=("$2")
  finding_messages+=("$3")
  finding_evidence+=("$4")
}

total=0
for label in "${category_labels[@]}"; do
  score="$(extract_score "$label" "$run_file" || true)"
  if [[ -z "$score" ]]; then
    score=0
    add_finding "missing_score_category" "medium" "Run summary is missing score category: $label." "$label"
  fi
  category_scores+=("$score")
  total=$((total + score))
done

if [[ -z "$tests_file" ]]; then
  add_finding "no_test_log" "medium" "No test log was provided, so validation evidence cannot be verified." "--tests missing"
  if grep -Eiq "$validation_claim_pattern" "$run_file"; then
    add_finding "validation_claim_without_tests" "high" "Run claims validation success, but no test log was provided." "$(grep -Ei "$validation_claim_pattern" "$run_file" | head -n 1)"
  fi
else
  failure_line="$(grep -Ei '(^|[^A-Za-z])(FAIL|FAILED|FAILURE|ERROR|Traceback|Exception)([^A-Za-z]|$)' "$tests_file" | grep -Eiv '0 failed|0 failures|no failures' | head -n 1 || true)"
  if [[ -n "$failure_line" ]]; then
    add_finding "test_log_failure" "high" "Provided test log contains failure or error language." "$failure_line"
  fi
  if grep -Eiq "$validation_claim_pattern" "$run_file" && ! grep -Eiq 'PASS|passed|success|succeeded|green|0 failed' "$tests_file"; then
    add_finding "weak_test_log_evidence" "medium" "Run claims validation success, but the test log does not contain an obvious pass signal." "$tests_file"
  fi
fi

if grep -Eiq "$risky_claim_pattern" "$run_file"; then
  add_finding "high_assurance_claim" "high" "Run makes a release, security, or reliability claim that requires explicit maintainer proof." "$(grep -Ei "$risky_claim_pattern" "$run_file" | head -n 1)"
fi

changed_files=0
if [[ -n "$diff_file" ]]; then
  changed_files="$(grep -c '^diff --git ' "$diff_file" || true)"
  if [[ "$changed_files" -gt "$max_changed_files" ]]; then
    add_finding "scope_creep_signal" "medium" "Diff touches more files than the configured policy limit." "$changed_files changed files; limit $max_changed_files"
  fi
  if [[ -n "$protected_pattern" ]] && grep -Eiq "$protected_pattern" "$diff_file"; then
    add_finding "protected_area_touch" "high" "Diff appears to touch protected or high-risk file areas." "$(grep -Ei "$protected_pattern" "$diff_file" | head -n 1)"
  fi
else
  if grep -Eiq 'changed|modified|updated|fixed|implemented' "$run_file"; then
    add_finding "changed_without_diff" "medium" "Run describes implementation changes, but no diff was provided." "$(grep -Ei 'changed|modified|updated|fixed|implemented' "$run_file" | head -n 1)"
  fi
fi

high_count=0
if [[ "${#finding_severities[@]}" -gt 0 ]]; then
  for severity in "${finding_severities[@]}"; do
    if [[ "$severity" == "high" ]]; then
      high_count=$((high_count + 1))
    fi
  done
fi
verdict="$(verdict_for_total "$total" "$high_count")"

{
  echo "# Agent Autopsy Report"
  echo
  echo "- Generated: $generated_at"
  echo "- Tool version: $tool_version"
  echo "- Verdict: $verdict"
  echo "- Total score: $total/12"
  echo
  echo "## Inputs"
  echo
  echo "- Run summary: $run_file"
  echo "- Task file: ${task_file:-not provided}"
  echo "- Diff file: ${diff_file:-not provided}"
  echo "- Test log: ${tests_file:-not provided}"
  echo "- Policy file: ${policy_file:-built-in defaults}"
  echo "- Changed files from diff: $changed_files"
  echo
  echo "## Category Scores"
  echo
  echo "| Category | Score |"
  echo "| --- | ---: |"
  for i in "${!category_labels[@]}"; do
    echo "| ${category_labels[$i]} | ${category_scores[$i]} |"
  done
  echo
  echo "## Findings"
  echo
  if [[ "${#finding_ids[@]}" -eq 0 ]]; then
    echo "No autopsy findings."
  else
    echo "| Severity | Finding | Evidence |"
    echo "| --- | --- | --- |"
    for i in "${!finding_ids[@]}"; do
      echo "| ${finding_severities[$i]} | ${finding_ids[$i]}: ${finding_messages[$i]} | ${finding_evidence[$i]} |"
    done
  fi
  echo
  echo "## Maintainer Rule"
  echo
  echo "Do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result."
} > "$markdown_report"

{
  echo "{"
  echo "  \"schema_version\": \"0.1\","
  echo "  \"tool_version\": $(json_string "$tool_version"),"
  echo "  \"generated_at\": $(json_string "$generated_at"),"
  echo "  \"inputs\": {"
  echo "    \"run\": $(json_string "$run_file"),"
  echo "    \"task\": $(json_string "${task_file:-}"),"
  echo "    \"diff\": $(json_string "${diff_file:-}"),"
  echo "    \"tests\": $(json_string "${tests_file:-}"),"
  echo "    \"policy\": $(json_string "${policy_file:-}")"
  echo "  },"
  echo "  \"score\": {"
  echo "    \"total\": $total,"
  echo "    \"max\": 12,"
  echo "    \"verdict\": $(json_string "$verdict"),"
  echo "    \"categories\": {"
  for i in "${!category_keys[@]}"; do
    comma=","
    [[ "$i" -eq "$((${#category_keys[@]} - 1))" ]] && comma=""
    echo "      \"${category_keys[$i]}\": {\"label\": $(json_string "${category_labels[$i]}"), \"score\": ${category_scores[$i]}}$comma"
  done
  echo "    }"
  echo "  },"
  echo "  \"evidence\": {"
  echo "    \"changed_files\": $changed_files,"
  echo "    \"has_diff\": $([[ -n "$diff_file" ]] && echo true || echo false),"
  echo "    \"has_tests\": $([[ -n "$tests_file" ]] && echo true || echo false),"
  echo "    \"has_task\": $([[ -n "$task_file" ]] && echo true || echo false),"
  echo "    \"max_changed_files\": $max_changed_files"
  echo "  },"
  echo "  \"findings\": ["
  if [[ "${#finding_ids[@]}" -gt 0 ]]; then
    for i in "${!finding_ids[@]}"; do
      comma=","
      [[ "$i" -eq "$((${#finding_ids[@]} - 1))" ]] && comma=""
      echo "    {\"id\": $(json_string "${finding_ids[$i]}"), \"severity\": $(json_string "${finding_severities[$i]}"), \"message\": $(json_string "${finding_messages[$i]}"), \"evidence\": $(json_string "${finding_evidence[$i]}")}$comma"
    done
  fi
  echo "  ]"
  echo "}"
} > "$json_report"

echo "wrote: $markdown_report"
echo "wrote: $json_report"
echo "verdict: $verdict"
