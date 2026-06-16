#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer self-audit

Usage:
  codex-maintainer self-audit [--out <dir>]

Outputs:
  self-audit.md
  self-audit.json
USAGE
}

fail() {
  echo "self-audit: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

out_dir="self-audit"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
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

mkdir -p "$out_dir"
version="$(sed -n '1p' "$tool_root/VERSION")"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

commands=(
  "policy show"
  "autopsy --help"
  "arena run --help"
  "arena import --help"
  "arena compare --help"
  "arena sign --help"
  "arena verify --help"
  "transcript redact --help"
  "transcript verify --help"
  "transcript corpus --help"
  "review-comment --help"
  "ci-gate --help"
  "ci-summary --help"
  "check-run --help"
  "check-run post --help"
  "sarif --help"
  "leaderboard build --help"
  "release-attest build --help"
  "release-proof build --help"
  "release-index build --help"
  "release-manifest --help"
  "release-manifest verify --help"
  "release-replay verify --help"
  "release-consume verify --help"
  "release-diff compare --help"
  "release-evidence site --help"
  "release-evidence index --help"
  "release-evidence bundle --help"
  "release-evidence verify --help"
  "release-evidence negative-index --help"
  "self-audit --help"
  "next-goal --help"
)

missing=0
command_count=0
for command in "${commands[@]}"; do
  if "$tool_root/bin/codex-maintainer" $command >/dev/null; then
    command_count=$((command_count + 1))
  else
    missing=1
  fi
done

required_artifacts=(
  "templates/policy/default.conf"
  "actions/arena-compare/action.yml"
  "actions/ci-gate/action.yml"
  "actions/release-consume/action.yml"
  "actions/release-diff/action.yml"
  "actions/release-evidence/action.yml"
  "actions/release-evidence-negative-index/action.yml"
  "actions/release-evidence-verify/action.yml"
  "actions/release-proof/action.yml"
  "actions/review-comment/action.yml"
  "actions/transcript-corpus/action.yml"
  "actions/transcript-verify/action.yml"
  "examples/demo-reports/leaderboard.json"
  "examples/demo-reports/arena/results.json"
  "docs/next-goal.md"
  "docs/arena-compare-action.md"
  "docs/sarif.md"
  "docs/ci-summary.md"
  "docs/check-run.md"
  "docs/template-profiles.md"
  "docs/transcript-corpus-action.md"
  "docs/transcript-corpus.md"
  "docs/transcript-redaction.md"
  "docs/transcript-verify-action.md"
  "docs/release-attest.md"
  "docs/release-consume-action.md"
  "docs/release-consume.md"
  "docs/release-diff-action.md"
  "docs/release-diff.md"
  "docs/release-evidence-action.md"
  "docs/release-evidence-bundle.md"
  "docs/release-evidence-index.md"
  "docs/release-evidence-negative-index-action.md"
  "docs/release-evidence-site.md"
  "docs/release-evidence-verify.md"
  "docs/release-proof.md"
  "docs/release-proof-consumption.md"
  "docs/release-manifest.md"
  "docs/release-index.md"
  "docs/release-proof-action.md"
  "docs/release-proof-workflows.md"
  "docs/release-replay.md"
  "examples/workflows/release-proof-on-tag.yml"
  "examples/workflows/arena-compare.yml"
  "examples/workflows/transcript-corpus.yml"
  "examples/workflows/transcript-verify.yml"
  "examples/workflows/release-proof-manual.yml"
  "examples/workflows/release-consume-verify.yml"
  "examples/workflows/release-diff-compare.yml"
  "examples/workflows/release-evidence-bundle.yml"
  "examples/workflows/release-evidence-consume.yml"
  "examples/workflows/release-evidence-export.yml"
  "examples/workflows/release-evidence-negative-index.yml"
  "examples/release-proof-consumption-checklist.md"
  "examples/redacted-transcript.md"
  "fixtures/transcripts/ios-notification-triage/transcript.md"
  "templates/web/AGENTS.md"
  "templates/backend/AGENTS.md"
  "templates/cli/AGENTS.md"
  "fixtures/external-arena-pack/imported-clean/run.md"
  "fixtures/release-evidence/negative/README.md"
  "fixtures/release-evidence/negative/cases.tsv"
  "scripts/arena_sign.sh"
  "scripts/arena_compare.sh"
  "scripts/arena_verify.sh"
  "scripts/release_attest.sh"
  "scripts/release_consume.sh"
  "scripts/release_diff.sh"
  "scripts/release_evidence.sh"
  "scripts/release_proof.sh"
  "scripts/release_index.sh"
  "scripts/release_manifest.sh"
  "scripts/release_replay.sh"
  "scripts/transcript_redact.sh"
  "scripts/transcript_verify.sh"
  "scripts/transcript_corpus.sh"
)

artifact_count=0
for artifact in "${required_artifacts[@]}"; do
  if [[ -f "$tool_root/$artifact" ]]; then
    artifact_count=$((artifact_count + 1))
  else
    missing=1
  fi
done

status="pass"
[[ "$missing" -ne 0 ]] && status="blocked"

{
  echo "# Codex Maintainer Self-Audit"
  echo
  echo "- Generated: $generated_at"
  echo "- Version: $version"
  echo "- Status: $status"
  echo "- Commands checked: $command_count/${#commands[@]}"
  echo "- Required artifacts checked: $artifact_count/${#required_artifacts[@]}"
  echo
  echo "## Commands"
  echo
  echo "| Command | Status |"
  echo "| --- | --- |"
  for command in "${commands[@]}"; do
    if "$tool_root/bin/codex-maintainer" $command >/dev/null; then
      echo "| codex-maintainer $command | pass |"
    else
      echo "| codex-maintainer $command | missing |"
    fi
  done
  echo
  echo "## Required Artifacts"
  echo
  echo "| Artifact | Status |"
  echo "| --- | --- |"
  for artifact in "${required_artifacts[@]}"; do
    if [[ -f "$tool_root/$artifact" ]]; then
      echo "| $artifact | pass |"
    else
      echo "| $artifact | missing |"
    fi
  done
} > "$out_dir/self-audit.md"

{
  echo "{"
  echo "  \"schema_version\": \"0.1\","
  echo "  \"tool_version\": $(json_string "$version"),"
  echo "  \"generated_at\": $(json_string "$generated_at"),"
  echo "  \"status\": $(json_string "$status"),"
  echo "  \"commands_checked\": $command_count,"
  echo "  \"commands_expected\": ${#commands[@]},"
  echo "  \"artifacts_checked\": $artifact_count,"
  echo "  \"artifacts_expected\": ${#required_artifacts[@]}"
  echo "}"
} > "$out_dir/self-audit.json"

echo "wrote: $out_dir/self-audit.md"
echo "wrote: $out_dir/self-audit.json"
echo "status: $status"

[[ "$status" == "pass" ]] || exit 1
