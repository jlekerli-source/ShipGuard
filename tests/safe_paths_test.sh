#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"
source "$repo_root/scripts/lib/safe_paths.sh"

export GITHUB_WORKSPACE="$repo_root"

expect_accept() {
  local path="$1"
  require_safe_artifact_dir "test path" "$path" "$repo_root" >/dev/null
}

expect_reject() {
  local path="$1"
  if require_safe_artifact_dir "test path" "$path" "$repo_root" >/dev/null 2>&1; then
    echo "expected path to be rejected: $path" >&2
    exit 1
  fi
}

expect_accept "artifacts/safe-output"
expect_accept "$tmp_dir/absolute-output"

expect_reject ""
expect_reject "/"
expect_reject "."
expect_reject ".."
expect_reject "./"
expect_reject "../"
expect_reject "../outside"
expect_reject "artifacts/../outside"
expect_reject "$repo_root"
expect_reject "$(dirname "$repo_root")"
expect_reject $'artifacts/bad\npath'

ln -s "$repo_root" "$tmp_dir/workspace-link"
expect_reject "$tmp_dir/workspace-link"

mkdir -p "$tmp_dir/left" "$tmp_dir/right"
require_no_artifact_overlap "left" "$tmp_dir/left" "right" "$tmp_dir/right"

if require_no_artifact_overlap "left" "$tmp_dir/left" "nested" "$tmp_dir/left/nested" >/dev/null 2>&1; then
  echo "expected overlapping artifact paths to be rejected" >&2
  exit 1
fi

if safe_rm_artifact_dir "workspace root" "$repo_root" "$repo_root" >/dev/null 2>&1; then
  echo "expected safe rm to reject workspace root" >&2
  exit 1
fi

mkdir -p "$tmp_dir/remove-me"
safe_rm_artifact_dir "temp artifact" "$tmp_dir/remove-me" "$repo_root"
if [[ -e "$tmp_dir/remove-me" ]]; then
  echo "expected safe rm to remove temp artifact directory" >&2
  exit 1
fi

echo "safe path tests passed"

