#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer next-goal

Usage:
  codex-maintainer next-goal [--out <file>] [--release <version>] [--title <title>]

Outputs:
  Markdown file containing a slash-goal style release objective and checklist.
USAGE
}

fail() {
  echo "next-goal: $*" >&2
  exit 1
}

next_minor_version() {
  local version="$1"
  if [[ ! "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    fail "VERSION must be semantic: $version"
  fi
  echo "${BASH_REMATCH[1]}.$((BASH_REMATCH[2] + 1)).0"
}

out_file="NEXT_GOAL.md"
current_version="$(sed -n '1p' "$tool_root/VERSION")"
release_version="$(next_minor_version "$current_version")"
title="Next Maintainer Reliability Upgrade"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --release)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--release requires a value"
      release_version="$2"
      [[ "$release_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "--release must be semantic"
      shift 2
      ;;
    --title)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--title requires a value"
      title="$2"
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

mkdir -p "$(dirname "$out_file")"

cat > "$out_file" <<EOF
# Next Goal

- Generated: $generated_at
- Current toolkit version: $current_version
- Target release: v$release_version
- Title: $title

\`\`\`text
/goal Implement v$release_version $title for jlekerli-source/ringly-codex-workflows: choose one high-signal maintainer reliability improvement from ROADMAP.md, add CLI/docs/tests/package proof, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run codex-maintainer next-goal again for the following release.
\`\`\`

## Constraints

- Keep implementation dependency-light unless a dependency is clearly justified.
- Do not publish private Ringly, Ilmify, or other product source.
- Do not fake adoption, stars, downloads, benchmark results, or security findings.
- Prefer release-tarball proof over source-only proof.

## Required Proof

\`\`\`bash
./bin/codex-maintainer validate
./tests/cli_smoke_test.sh
./tests/template_profiles_test.sh
./tests/autopsy_test.sh
./tests/action_artifact_test.sh
./tests/arena_test.sh
./tests/arena_import_test.sh
./tests/arena_sign_test.sh
./tests/review_comment_test.sh
./tests/policy_test.sh
./tests/check_run_test.sh
./tests/check_run_post_test.sh
./tests/ci_gate_test.sh
./tests/ci_summary_test.sh
./tests/sarif_test.sh
./tests/leaderboard_test.sh
./tests/self_audit_test.sh
./tests/next_goal_test.sh
./tests/release_attest_test.sh
./tests/release_index_test.sh
./tests/release_manifest_test.sh
./tests/release_proof_action_test.sh
./tests/release_proof_workflow_test.sh
./tests/release_replay_test.sh
./tests/package_release_test.sh
./scripts/package_release.sh
\`\`\`

## Release Loop

1. Open or update the tracking issue for v$release_version.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push \`main\` and verify GitHub Actions success.
6. Create release \`v$release_version\` and upload \`dist/codex-maintainer-v$release_version.tar.gz\`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

\`\`\`bash
./bin/codex-maintainer next-goal --out NEXT_GOAL.md
\`\`\`
EOF

echo "wrote: $out_file"
