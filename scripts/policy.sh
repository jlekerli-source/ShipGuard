#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer policy

Usage:
  codex-maintainer policy init [target] [--force]
  codex-maintainer policy show [policy.conf]

Commands:
  init    Write a default policy file to <target> or .codex-maintainer/policy.conf.
  show    Print a policy file, defaulting to templates/policy/default.conf.
USAGE
}

fail() {
  echo "policy: $*" >&2
  exit 1
}

cmd_init() {
  local target=".codex-maintainer/policy.conf"
  local force="false"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --force)
        force="true"
        shift
        ;;
      -*)
        fail "unknown init option: $1"
        ;;
      *)
        target="$1"
        shift
        ;;
    esac
  done

  mkdir -p "$(dirname "$target")"
  if [[ -e "$target" && "$force" != "true" ]]; then
    fail "policy already exists: $target"
  fi
  cp "$tool_root/templates/policy/default.conf" "$target"
  echo "wrote: $target"
}

cmd_show() {
  local policy_file="${1:-$tool_root/templates/policy/default.conf}"
  [[ -f "$policy_file" ]] || fail "policy file not found: $policy_file"
  sed -n '1,200p' "$policy_file"
}

command="${1:-help}"
shift || true

case "$command" in
  init)
    cmd_init "$@"
    ;;
  show)
    cmd_show "$@"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    usage
    fail "unknown command: $command"
    ;;
esac
