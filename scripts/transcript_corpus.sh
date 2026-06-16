#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer transcript corpus

Usage:
  codex-maintainer transcript corpus --source <dir> --out <dir> [--require-report true|false]

Fixture format:
  <dir>/<case-id>/transcript.md
  <dir>/<case-id>/redaction-report.json optional

Outputs:
  corpus.json
  index.md
  badge.json
  runs/<case-id>/transcript-verify.json
USAGE
}

fail() {
  echo "transcript-corpus: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

json_field() {
  local field="$1"
  local file="$2"
  perl -MJSON::PP -0777 -e '
    my ($field) = @ARGV;
    my $text = <STDIN>;
    my $data = JSON::PP->new->decode($text);
    print defined $data->{$field} ? $data->{$field} : "";
  ' "$field" < "$file"
}

source_dir=""
out_dir=""
require_report="false"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --source)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--source requires a value"
      source_dir="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --require-report)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--require-report requires a value"
      require_report="$2"
      [[ "$require_report" == "true" || "$require_report" == "false" ]] || fail "--require-report must be true or false"
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

[[ -n "$source_dir" ]] || fail "--source is required"
[[ -n "$out_dir" ]] || fail "--out is required"
[[ -d "$source_dir" ]] || fail "source directory not found: $source_dir"

mkdir -p "$out_dir/runs"
cases_tsv="$out_dir/.cases.tsv"
: > "$cases_tsv"

case_count=0
passed_count=0
blocked_count=0

while IFS= read -r transcript_file; do
  case_dir="$(dirname "$transcript_file")"
  case_id="$(basename "$case_dir")"
  report_file="$case_dir/redaction-report.json"
  verify_dir="$out_dir/runs/$case_id"
  mkdir -p "$verify_dir"

  verify_args=(transcript verify --in "$transcript_file" --out "$verify_dir")
  report_present="false"
  report_path="missing"
  if [[ -f "$report_file" ]]; then
    verify_args+=(--report "$report_file")
    report_present="true"
    report_path="redaction-report.json"
  fi

  verify_exit=0
  if ! "$tool_root/bin/codex-maintainer" "${verify_args[@]}" >/dev/null; then
    verify_exit=1
  fi

  verify_json="$verify_dir/transcript-verify.json"
  [[ -f "$verify_json" ]] || fail "verification did not write report for case: $case_id"

  verify_status="$(json_field status "$verify_json")"
  remaining_risk_count="$(json_field remaining_risk_count "$verify_json")"
  redaction_report_status="$(json_field redaction_report_status "$verify_json")"
  case_status="$verify_status"

  if [[ "$require_report" == "true" && "$report_present" != "true" ]]; then
    case_status="blocked"
    redaction_report_status="missing"
  fi
  if [[ "$verify_exit" -ne 0 ]]; then
    case_status="blocked"
  fi

  case_count=$((case_count + 1))
  if [[ "$case_status" == "pass" ]]; then
    passed_count=$((passed_count + 1))
  else
    blocked_count=$((blocked_count + 1))
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$case_id" \
    "$case_status" \
    "$remaining_risk_count" \
    "$redaction_report_status" \
    "$report_present" \
    "$report_path" \
    "runs/$case_id/transcript-verify.json" >> "$cases_tsv"
done < <(find "$source_dir" -mindepth 2 -maxdepth 2 -type f -name transcript.md | sort)

[[ "$case_count" -gt 0 ]] || fail "no transcript cases found under: $source_dir"

status="pass"
[[ "$blocked_count" -ne 0 ]] && status="blocked"

{
  echo "{"
  echo "  \"schema_version\": \"1.0\","
  echo "  \"status\": $(json_string "$status"),"
  echo "  \"source_name\": $(json_string "$(basename "$source_dir")"),"
  echo "  \"require_report\": $require_report,"
  echo "  \"case_count\": $case_count,"
  echo "  \"passed_count\": $passed_count,"
  echo "  \"blocked_count\": $blocked_count,"
  echo "  \"cases\": ["
  row_index=0
  while IFS=$'\t' read -r case_id case_status remaining redaction_status report_present report_path verification_path; do
    row_index=$((row_index + 1))
    comma=","
    [[ "$row_index" -eq "$case_count" ]] && comma=""
    echo "    {"
    echo "      \"id\": $(json_string "$case_id"),"
    echo "      \"status\": $(json_string "$case_status"),"
    echo "      \"remaining_risk_count\": $remaining,"
    echo "      \"redaction_report_status\": $(json_string "$redaction_status"),"
    echo "      \"redaction_report_present\": $report_present,"
    echo "      \"redaction_report\": $(json_string "$report_path"),"
    echo "      \"verification\": $(json_string "$verification_path")"
    echo "    }$comma"
  done < "$cases_tsv"
  echo "  ]"
  echo "}"
} > "$out_dir/corpus.json"

{
  echo "# Transcript Corpus"
  echo
  echo "- Status: $status"
  echo "- Source: $(basename "$source_dir")"
  echo "- Cases: $case_count"
  echo "- Passed: $passed_count"
  echo "- Blocked: $blocked_count"
  echo "- Require redaction reports: $require_report"
  echo
  echo "| Case | Status | Remaining Risks | Redaction Report | Verification |"
  echo "| --- | --- | ---: | --- | --- |"
  while IFS=$'\t' read -r case_id case_status remaining redaction_status report_present report_path verification_path; do
    echo "| $case_id | $case_status | $remaining | $redaction_status | $verification_path |"
  done < "$cases_tsv"
} > "$out_dir/index.md"

badge_color="brightgreen"
[[ "$status" != "pass" ]] && badge_color="red"
{
  echo "{"
  echo "  \"schemaVersion\": 1,"
  echo "  \"label\": \"transcripts\","
  echo "  \"message\": $(json_string "$status $passed_count/$case_count"),"
  echo "  \"color\": $(json_string "$badge_color")"
  echo "}"
} > "$out_dir/badge.json"

rm -f "$cases_tsv"

echo "wrote: $out_dir/corpus.json"
echo "wrote: $out_dir/index.md"
echo "wrote: $out_dir/badge.json"
echo "status: $status"

[[ "$status" == "pass" ]] || exit 1
