#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer ci-gate

Usage:
  codex-maintainer ci-gate --run <run.md> [--diff <patch.diff>] [--tests <test.log>] [--task <task.md>] [--policy <policy.conf>] [--out <dir>] [--mode warn|fail]

Outputs:
  autopsy/report.md
  autopsy/report.json
  sarif/results.sarif
  review/comment.md
  review/badge.json
  summary.md
  gate.json
USAGE
}

fail() {
  echo "ci-gate: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

read_policy_thresholds() {
  local file="$1"
  local line key value
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    [[ -z "$line" || "$line" != *"="* ]] && continue
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in
      warn_below)
        [[ "$value" =~ ^[0-9]+$ ]] || fail "policy warn_below must be an integer"
        warn_below="$value"
        ;;
      fail_below)
        [[ "$value" =~ ^[0-9]+$ ]] || fail "policy fail_below must be an integer"
        fail_below="$value"
        ;;
    esac
  done < "$file"
}

json_total() {
  perl -0ne 'print $1 if /"total":\s*([0-9]+)/' "$1"
}

json_max() {
  perl -0ne 'print $1 if /"max":\s*([0-9]+)/' "$1"
}

run_file=""
diff_file=""
tests_file=""
task_file=""
policy_file=""
out_dir="ci-gate-artifacts"
mode="warn"
warn_below=10
fail_below=7

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --run)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--run requires a value"
      run_file="$2"
      shift 2
      ;;
    --diff)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--diff requires a value"
      diff_file="$2"
      shift 2
      ;;
    --tests)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--tests requires a value"
      tests_file="$2"
      shift 2
      ;;
    --task)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--task requires a value"
      task_file="$2"
      shift 2
      ;;
    --policy)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--policy requires a value"
      policy_file="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --mode)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--mode requires a value"
      mode="$2"
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
[[ "$mode" == "warn" || "$mode" == "fail" ]] || fail "--mode must be warn or fail"
[[ -z "$policy_file" || -f "$policy_file" ]] || fail "policy file not found: $policy_file"
[[ -n "$policy_file" ]] && read_policy_thresholds "$policy_file"

mkdir -p "$out_dir"
autopsy_dir="$out_dir/autopsy"
sarif_dir="$out_dir/sarif"
review_dir="$out_dir/review"

autopsy_args=(--run "$run_file" --out "$autopsy_dir")
[[ -n "$diff_file" ]] && autopsy_args+=(--diff "$diff_file")
[[ -n "$tests_file" ]] && autopsy_args+=(--tests "$tests_file")
[[ -n "$task_file" ]] && autopsy_args+=(--task "$task_file")
[[ -n "$policy_file" ]] && autopsy_args+=(--policy "$policy_file")

"$tool_root/scripts/autopsy_report.sh" "${autopsy_args[@]}" >/dev/null
"$tool_root/scripts/sarif.sh" \
  --report "$autopsy_dir/report.json" \
  --out "$sarif_dir/results.sarif" >/dev/null
"$tool_root/scripts/review_comment.sh" \
  --report "$autopsy_dir/report.json" \
  --out "$review_dir/comment.md" \
  --badge "$review_dir/badge.json" \
  --artifact-dir "$review_dir" \
  --mode warn \
  --warn-below "$warn_below" \
  --fail-below "$fail_below" >/dev/null

total="$(json_total "$autopsy_dir/report.json")"
max_score="$(json_max "$autopsy_dir/report.json")"
high_count="$(grep -c '"severity": "high"' "$autopsy_dir/report.json" || true)"
status="pass"
if [[ "$high_count" -gt 0 || "$total" -lt "$fail_below" ]]; then
  status="blocked"
elif [[ "$total" -lt "$warn_below" ]]; then
  status="review"
fi

{
  echo "{"
  echo "  \"schema_version\": \"0.1\","
  echo "  \"status\": $(json_string "$status"),"
  echo "  \"mode\": $(json_string "$mode"),"
  echo "  \"score\": $total,"
  echo "  \"max\": ${max_score:-12},"
  echo "  \"high_risk_findings\": $high_count,"
  echo "  \"warn_below\": $warn_below,"
  echo "  \"fail_below\": $fail_below,"
  echo "  \"autopsy_report\": \"autopsy/report.json\","
  echo "  \"sarif\": \"sarif/results.sarif\","
  echo "  \"review_comment\": \"review/comment.md\","
  echo "  \"badge\": \"review/badge.json\","
  echo "  \"summary\": \"summary.md\""
  echo "}"
} > "$out_dir/gate.json"

"$tool_root/scripts/ci_summary.sh" \
  --gate "$out_dir/gate.json" \
  --out "$out_dir/summary.md" >/dev/null

echo "wrote: $out_dir/gate.json"
echo "status: $status"

if [[ "$mode" == "fail" && "$status" == "blocked" ]]; then
  exit 1
fi
