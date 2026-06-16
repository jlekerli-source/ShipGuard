safe_paths_fail() {
  echo "safe-paths: $*" >&2
  return 1
}

safe_paths_normalize() {
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

safe_paths_is_parent_or_same() {
  local parent="${1%/}"
  local child="${2%/}"
  [[ "$child" == "$parent" || "$child" == "$parent"/* ]]
}

require_safe_artifact_dir() {
  local label="$1"
  local path="${2:-}"
  local root="${3:-${GITHUB_WORKSPACE:-}}"

  [[ -n "$path" ]] || safe_paths_fail "$label is empty" || return 1
  [[ "$path" != *$'\n'* && "$path" != *$'\r'* ]] || safe_paths_fail "$label contains a newline" || return 1
  [[ "$path" != "/" ]] || safe_paths_fail "$label must not be /" || return 1
  [[ "$path" != "." && "$path" != ".." && "$path" != "./" && "$path" != "../" ]] || safe_paths_fail "$label must not be $path" || return 1
  [[ "$path" != */../* && "$path" != ../* && "$path" != */.. ]] || safe_paths_fail "$label must not contain .. segments" || return 1

  local path_abs
  path_abs="$(safe_paths_normalize "$path")" || safe_paths_fail "$label cannot be resolved: $path" || return 1
  [[ "$path_abs" != "/" ]] || safe_paths_fail "$label resolves to /" || return 1

  if [[ -n "$root" && -e "$root" ]]; then
    local root_abs
    root_abs="$(safe_paths_normalize "$root")" || safe_paths_fail "root cannot be resolved: $root" || return 1
    [[ "$path_abs" != "$root_abs" ]] || safe_paths_fail "$label must not be the workspace root: $path" || return 1
    if safe_paths_is_parent_or_same "$path_abs" "$root_abs"; then
      safe_paths_fail "$label must not be a workspace parent: $path"
      return 1
    fi
  fi

  printf '%s\n' "$path_abs"
}

require_no_artifact_overlap() {
  local left_label="$1"
  local left_path="$2"
  local right_label="$3"
  local right_path="$4"

  local left_abs
  local right_abs
  left_abs="$(safe_paths_normalize "$left_path")" || safe_paths_fail "$left_label cannot be resolved: $left_path" || return 1
  right_abs="$(safe_paths_normalize "$right_path")" || safe_paths_fail "$right_label cannot be resolved: $right_path" || return 1

  if safe_paths_is_parent_or_same "$left_abs" "$right_abs" || safe_paths_is_parent_or_same "$right_abs" "$left_abs"; then
    safe_paths_fail "$left_label and $right_label must not overlap: $left_path, $right_path"
    return 1
  fi
}

safe_rm_artifact_dir() {
  local label="$1"
  local path="$2"
  local root="${3:-${GITHUB_WORKSPACE:-}}"
  local path_abs

  path_abs="$(require_safe_artifact_dir "$label" "$path" "$root")" || return 1
  rm -rf -- "$path_abs"
}

