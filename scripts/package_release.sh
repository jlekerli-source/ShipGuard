#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="$(sed -n '1p' "$repo_root/VERSION")"
package_name="shipguard-v$version"
dist_dir="$repo_root/dist"
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

mkdir -p "$dist_dir"
package_root="$work_dir/$package_name"
mkdir -p "$package_root"

copy_path() {
  local path="$1"
  mkdir -p "$package_root/$(dirname "$path")"
  cp -R "$repo_root/$path" "$package_root/$path"
}

paths=(
  ".gitignore"
  ".github"
  "VERSION"
  "AGENTS.md"
  "README.md"
  "CHANGELOG.md"
  "CODEX_TASK_TEMPLATE.md"
  "CODE_OF_CONDUCT.md"
  "CONTRIBUTING.md"
  "EVALUATION_SUITE.md"
  "GOVERNANCE.md"
  "PLANS.md"
  "ROADMAP.md"
  "SECURITY.md"
  "SUPPORT.md"
  "SUBAGENTS.md"
  "SCORECARD.md"
  "LICENSE"
  "_config.yml"
  "actions"
  "bin"
  "plugins"
  "scripts"
  ".agents"
  "templates"
  "docs"
  "evals"
  "examples"
  "fixtures"
  "tests"
)

for path in "${paths[@]}"; do
  copy_path "$path"
done

find "$package_root" \
  \( -name '.git' -o -name 'dist' -o -name '.DS_Store' -o -name '.cache' -o -name 'DerivedData' -o -name '__pycache__' \) \
  -prune -exec rm -rf {} +
find "$package_root" -type f -name '*.pyc' -delete

tarball="$dist_dir/$package_name.tar.gz"
tmp_tarball="$work_dir/$package_name.tar.gz"
tar -C "$work_dir" -czf "$tmp_tarball" "$package_name"
mv -f "$tmp_tarball" "$tarball"

echo "$tarball"
