#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
shipguard review-comment

Usage:
  shipguard review-comment --report <report.json> --out <comment.md> [--badge <badge.json>] [--artifact-dir <dir>] [--mode warn|fail] [--warn-below <score>] [--fail-below <score>]

Defaults:
  --mode warn
  --warn-below 10
  --fail-below 7
USAGE
}

fail() {
  echo "review-comment: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

copy_if_different() {
  local source="$1"
  local target="$2"
  local source_abs
  local target_abs
  source_abs="$(cd "$(dirname "$source")" && pwd)/$(basename "$source")"
  target_abs="$(cd "$(dirname "$target")" && pwd)/$(basename "$target")"
  [[ "$source_abs" == "$target_abs" ]] && return
  cp "$source" "$target"
}

json_total() {
  perl -0ne 'print $1 if /"total":\s*([0-9]+)/' "$1"
}

json_max() {
  perl -0ne 'print $1 if /"max":\s*([0-9]+)/' "$1"
}

json_verdict() {
  perl -0ne 'print $1 if /"verdict":\s*"((?:\\.|[^"])*)"/' "$1"
}

report_file=""
out_file=""
badge_file=""
artifact_dir=""
mode="warn"
warn_below="10"
fail_below="7"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --report)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--report requires a value"
      report_file="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --badge)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--badge requires a value"
      badge_file="$2"
      shift 2
      ;;
    --artifact-dir)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--artifact-dir requires a value"
      artifact_dir="$2"
      shift 2
      ;;
    --mode)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--mode requires a value"
      mode="$2"
      shift 2
      ;;
    --warn-below)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--warn-below requires a value"
      warn_below="$2"
      shift 2
      ;;
    --fail-below)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--fail-below requires a value"
      fail_below="$2"
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

[[ -n "$report_file" ]] || fail "--report is required"
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$report_file" ]] || fail "report not found: $report_file"
[[ "$mode" == "warn" || "$mode" == "fail" ]] || fail "--mode must be warn or fail"
[[ "$warn_below" =~ ^[0-9]+$ ]] || fail "--warn-below must be an integer"
[[ "$fail_below" =~ ^[0-9]+$ ]] || fail "--fail-below must be an integer"

[[ -n "$badge_file" ]] || badge_file="$(dirname "$out_file")/badge.json"

mkdir -p "$(dirname "$out_file")" "$(dirname "$badge_file")"

total="$(json_total "$report_file")"
max_score="$(json_max "$report_file")"
verdict="$(json_verdict "$report_file")"
high_count="$(grep -c '"severity": "high"' "$report_file" || true)"
tool_version="$(sed -n '1p' "$tool_root/VERSION")"

[[ -n "$total" ]] || fail "report is missing score.total"
[[ -n "$max_score" ]] || max_score="12"
[[ -n "$verdict" ]] || verdict="unknown"

status="pass"
color="brightgreen"
summary="maintainer evidence looks usable"
if [[ "$high_count" -gt 0 || "$total" -lt "$fail_below" ]]; then
  status="blocked"
  color="red"
  summary="do not merge until high-risk findings or low score are resolved"
elif [[ "$total" -lt "$warn_below" ]]; then
  status="review"
  color="yellow"
  summary="review weak evidence before merging"
fi

{
  echo "## ShipGuard Review"
  echo
  echo "| Field | Value |"
  echo "| --- | --- |"
  echo "| Status | $status |"
  echo "| Score | $total/$max_score |"
  echo "| Verdict | $verdict |"
  echo "| High-risk findings | $high_count |"
  echo "| Mode | $mode |"
  echo "| Warn below | $warn_below |"
  echo "| Fail below | $fail_below |"
  echo "| Tool version | $tool_version |"
  echo
  echo "**Next action:** $summary."
  echo
  echo "Review the full autopsy report artifact before merging."
} > "$out_file"

{
  echo "{"
  echo "  \"schemaVersion\": 1,"
  echo "  \"label\": \"codex maintainer\","
  echo "  \"message\": $(json_string "$status $total/$max_score"),"
  echo "  \"color\": $(json_string "$color")"
  echo "}"
} > "$badge_file"

if [[ -n "$artifact_dir" ]]; then
  mkdir -p "$artifact_dir"
  copy_if_different "$report_file" "$artifact_dir/report.json"
  report_md="$(dirname "$report_file")/report.md"
  [[ -f "$report_md" ]] && copy_if_different "$report_md" "$artifact_dir/report.md"
  copy_if_different "$out_file" "$artifact_dir/comment.md"
  copy_if_different "$badge_file" "$artifact_dir/badge.json"
fi

echo "wrote: $out_file"
echo "wrote: $badge_file"
[[ -n "$artifact_dir" ]] && echo "wrote artifact bundle: $artifact_dir"
echo "status: $status"

if [[ "$mode" == "fail" && "$status" == "blocked" ]]; then
  exit 1
fi
