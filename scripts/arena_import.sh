#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
shipguard arena import

Usage:
  shipguard arena import --source <fixture-dir> --out <fixture-dir> [--pack-name <name>] [--force]

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

safe_case_id() {
  [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]]
}

normalize_path() {
  local path="$1"
  local target="$path"
  local suffix=""

  while [[ ! -e "$target" ]]; do
    local base
    base="$(basename "$target")"
    [[ "$base" != "." && "$base" != "/" ]] || return 1
    if [[ -n "$suffix" ]]; then
      suffix="$base/$suffix"
    else
      suffix="$base"
    fi
    target="$(dirname "$target")"
  done

  local base_abs
  base_abs="$(cd "$target" 2>/dev/null && pwd -P)" || return 1
  if [[ -n "$suffix" ]]; then
    printf '%s/%s\n' "$base_abs" "$suffix"
  else
    printf '%s\n' "$base_abs"
  fi
}

is_parent_or_same() {
  local parent="${1%/}"
  local child="${2%/}"
  [[ "$child" == "$parent" || "$child" == "$parent"/* ]]
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

supported_case_file() {
  case "$1" in
    run.md|task.md|diff.patch|tests.log)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
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

source_abs="$(normalize_path "$source_dir")" || fail "source fixture directory cannot be resolved: $source_dir"
out_abs="$(normalize_path "$out_dir")" || fail "output fixture directory cannot be resolved: $out_dir"
if is_parent_or_same "$source_abs" "$out_abs" || is_parent_or_same "$out_abs" "$source_abs"; then
  fail "--source and --out must not overlap"
fi

case_dirs=()
while IFS= read -r entry; do
  entry_name="$(basename "$entry")"
  [[ ! -L "$entry" ]] || fail "unsupported symlink in fixture pack: $entry_name"
  [[ -d "$entry" ]] || fail "unsupported fixture pack entry: $entry_name"
  safe_case_id "$entry_name" || fail "unsafe case id: $entry_name"
  case_dirs+=("$entry")
done < <(find "$source_dir" -mindepth 1 -maxdepth 1 | sort)

[[ "${#case_dirs[@]}" -gt 0 ]] || fail "source fixture directory has no case subdirectories: $source_dir"

generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}}"
[[ -n "$pack_name" ]] || pack_name="$(basename "$source_dir")"

supported_files=(run.md task.md diff.patch tests.log)
imported_cases=()

for case_dir in "${case_dirs[@]}"; do
  case_id="$(basename "$case_dir")"
  safe_case_id "$case_id" || fail "unsafe case id: $case_id"

  while IFS= read -r entry; do
    entry_name="$(basename "$entry")"
    [[ ! -L "$entry" ]] || fail "unsupported symlink in fixture case: $case_id/$entry_name"
    [[ ! -d "$entry" ]] || fail "unsupported nested directory in fixture case: $case_id/$entry_name"
    [[ -f "$entry" ]] || fail "unsupported fixture case entry: $case_id/$entry_name"
    supported_case_file "$entry_name" || fail "unsupported fixture case file: $case_id/$entry_name"
  done < <(find "$case_dir" -mindepth 1 -maxdepth 1 | sort)

  [[ -f "$case_dir/run.md" ]] || fail "missing required case run file: $case_dir/run.md"

  dest_case="$out_dir/$case_id"
  if [[ -e "$dest_case" && "$force" != "true" ]]; then
    fail "destination case exists, use --force to overwrite: $dest_case"
  fi

  for file_name in "${supported_files[@]}"; do
    source_file="$case_dir/$file_name"
    [[ -f "$source_file" ]] || continue
    scan_safe_content "$source_file"
  done

  imported_cases+=("$case_id")
done

mkdir -p "$out_dir"

for case_dir in "${case_dirs[@]}"; do
  case_id="$(basename "$case_dir")"
  dest_case="$out_dir/$case_id"
  rm -rf "$dest_case"
  mkdir -p "$dest_case"

  for file_name in "${supported_files[@]}"; do
    source_file="$case_dir/$file_name"
    [[ -f "$source_file" ]] || continue
    cp "$source_file" "$dest_case/$file_name"
  done
done

{
  echo "# Arena Fixture Pack"
  echo
  echo "- Pack: $pack_name"
  echo "- Imported: $generated_at"
  echo "- Source: $(basename "$source_dir")"
  echo "- Cases: ${#imported_cases[@]}"
  echo
  echo "## Case IDs"
  echo
  for case_id in "${imported_cases[@]}"; do
    echo "- $case_id"
  done
} > "$out_dir/PACK.md"

echo "imported ${#imported_cases[@]} cases into $out_dir"
