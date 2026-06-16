#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer arena import

Usage:
  codex-maintainer arena import --source <fixture-dir> --out <fixture-dir> [--pack-name <name>] [--force]

Fixture case format:
  <fixture-dir>/<case-id>/run.md
  <fixture-dir>/<case-id>/task.md       optional
  <fixture-dir>/<case-id>/diff.patch    optional
  <fixture-dir>/<case-id>/tests.log     optional

Outputs:
  <out>/<case-id>/<fixture-files>
  <out>/PACK.md
USAGE
}

fail() {
  echo "arena-import: $*" >&2
  exit 1
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/lib/safe_paths.sh"

safe_case_id() {
  [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]]
}

scan_safe_content() {
  local file="$1"
  local users_path="/""Users/"
  local home_path="/""home/[^ ]+"
  local ghp_pattern="ghp_""[A-Za-z0-9_]{20,}"
  local sk_pattern="sk-""[A-Za-z0-9_-]{20,}"
  local private_key_pattern="BEGIN ""[A-Z ]*PRIVATE KEY"
  if grep -IEq "$users_path|$home_path|$ghp_pattern|$sk_pattern|$private_key_pattern" "$file"; then
    fail "unsafe local path or secret-looking value in $file"
  fi
}

source_dir=""
out_dir=""
pack_name=""
force="false"

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
    --pack-name)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--pack-name requires a value"
      pack_name="$2"
      shift 2
      ;;
    --force)
      force="true"
      shift
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
[[ -d "$source_dir" ]] || fail "source fixture directory not found: $source_dir"
[[ "$source_dir" != "$out_dir" ]] || fail "--source and --out must be different directories"
require_safe_artifact_dir "out" "$out_dir" "$(pwd -P)" >/dev/null || exit 1
require_no_artifact_overlap "source" "$source_dir" "out" "$out_dir" || exit 1

case_dirs=()
while IFS= read -r case_dir; do
  case_dirs+=("$case_dir")
done < <(find "$source_dir" -mindepth 1 -maxdepth 1 -type d | sort)

[[ "${#case_dirs[@]}" -gt 0 ]] || fail "source fixture directory has no case subdirectories: $source_dir"

mkdir -p "$out_dir"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"
[[ -n "$pack_name" ]] || pack_name="$(basename "$source_dir")"

supported_files=(run.md task.md diff.patch tests.log)
imported_cases=()

for case_dir in "${case_dirs[@]}"; do
  case_id="$(basename "$case_dir")"
  safe_case_id "$case_id" || fail "unsafe case id: $case_id"
  [[ -f "$case_dir/run.md" ]] || fail "missing required case run file: $case_dir/run.md"

  dest_case="$out_dir/$case_id"
  if [[ -e "$dest_case" && "$force" != "true" ]]; then
    fail "destination case exists, use --force to overwrite: $dest_case"
  fi

  rm -rf "$dest_case"
  mkdir -p "$dest_case"

  for file_name in "${supported_files[@]}"; do
    source_file="$case_dir/$file_name"
    [[ -f "$source_file" ]] || continue
    scan_safe_content "$source_file"
    cp "$source_file" "$dest_case/$file_name"
  done

  imported_cases+=("$case_id")
done

{
  echo "# Arena Fixture Pack"
  echo
  echo "- Pack: $pack_name"
  echo "- Imported: $generated_at"
  echo "- Source: $source_dir"
  echo "- Cases: ${#imported_cases[@]}"
  echo
  echo "## Case IDs"
  echo
  for case_id in "${imported_cases[@]}"; do
    echo "- $case_id"
  done
} > "$out_dir/PACK.md"

echo "imported ${#imported_cases[@]} cases into $out_dir"
