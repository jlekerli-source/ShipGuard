#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
shipguard next-goal

Usage:
  shipguard next-goal [--out <file>] [--release <version>] [--title <title>] [--scope <text>] [--completion-evidence <text>] [--following-title <title>]

Outputs:
  Markdown file containing slash-plan and slash-goal release guidance.
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
scope=""
completion_evidence=""
following_title="Following Maintainer Reliability Upgrade"
generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}}"

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
    --scope)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--scope requires a value"
      scope="$2"
      shift 2
      ;;
    --completion-evidence)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--completion-evidence requires a value"
      completion_evidence="$2"
      shift 2
      ;;
    --following-title)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--following-title requires a value"
      following_title="$2"
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

if [[ -n "$scope" ]]; then
  scope_sentence="${scope%[.!?]}"
  plan_step_one="1. Implement this bounded improvement: $scope"
  goal_detail="deliver this bounded improvement: $scope_sentence"
else
  plan_step_one="1. Pick exactly one high-signal maintainer reliability improvement from ROADMAP.md and write the bounded scope before editing."
  goal_detail="finish one high-signal maintainer reliability improvement from ROADMAP.md with CLI/docs/tests/package proof"
fi

following_version="$(next_minor_version "$release_version")"

cat > "$out_file" <<EOF
# Next Goal

- Generated: $generated_at
- Current toolkit version: $current_version
- Target release: v$release_version
- Title: $title

## Slash Plan

\`\`\`text
/plan v$release_version $title for jlekerli-source/ShipGuard:
$plan_step_one
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
\`\`\`

## Slash Goal

\`\`\`text
/goal Implement v$release_version $title for jlekerli-source/ShipGuard: follow the /plan above, $goal_detail, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
\`\`\`

EOF

if [[ -n "$scope" ]]; then
  cat >> "$out_file" <<EOF

## Bounded Scope

$scope
EOF
fi

if [[ -n "$completion_evidence" ]]; then
  completed_scope="$title"
  if [[ -n "$scope" ]]; then
    completed_scope="$scope"
  fi
  cat >> "$out_file" <<EOF

## Completion Receipt

- Completed scope: $completed_scope
- Evidence: $completion_evidence

## Following Slash Plan

\`\`\`text
/plan v$following_version $following_title for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
\`\`\`

## Following Slash Goal

\`\`\`text
/goal Implement v$following_version $following_title for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
\`\`\`

Generate that follow-up file with:

\`\`\`bash
./bin/shipguard next-goal --release $following_version --title "$following_title" --out NEXT_GOAL.md
\`\`\`
EOF
fi

cat >> "$out_file" <<EOF

## Constraints

- Keep implementation dependency-light unless a dependency is clearly justified.
- Do not publish private Ringly, Ilmify, or other product source.
- Do not fake adoption, stars, downloads, benchmark results, or security findings.
- Prefer release-tarball proof over source-only proof.

## Required Proof

\`\`\`bash
./bin/shipguard validate
./tests/cli_smoke_test.sh
./tests/template_profiles_test.sh
./tests/autopsy_test.sh
./tests/action_artifact_test.sh
./tests/arena_test.sh
./tests/arena_import_test.sh
./tests/arena_compare_test.sh
./tests/arena_compare_action_test.sh
./tests/arena_sign_test.sh
./tests/review_comment_test.sh
./tests/policy_test.sh
./tests/check_run_test.sh
./tests/check_run_post_test.sh
./tests/ci_gate_test.sh
./tests/ci_summary_test.sh
./tests/sarif_test.sh
./tests/docs_check_test.sh
./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict
./tests/ios_branding_test.sh
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./tests/tool_value_gauntlet_test.sh
./tests/ios_doctor_test.sh
./tests/ios_inventory_test.sh
./tests/ios_preview_test.sh
./tests/ios_target_match_test.sh
./tests/ios_codex_handoff_test.sh
./tests/ios_plan_test.sh
./tests/ios_prove_test.sh
./tests/ios_launchdeck_test.sh
./tests/ios_performance_test.sh
./tests/ios_devspace_check_test.sh
./tests/ios_design_test.sh
./tests/ios_modernize_test.sh
./tests/ios_app_intelligence_test.sh
./tests/ios_ai_readiness_test.sh
./tests/ios_spec_workflow_test.sh
./tests/ios_report_quality_test.sh
./tests/ios_redaction_test.sh
./tests/ios_shipguard_eval_test.sh
./tests/ios_shipguard_demo_test.sh
./tests/ios_goal_loop_test.sh
./tests/transcript_redaction_test.sh
./tests/transcript_verify_test.sh
./tests/transcript_verify_action_test.sh
./tests/transcript_corpus_test.sh
./tests/transcript_corpus_action_test.sh
./tests/leaderboard_test.sh
./tests/self_audit_test.sh
./tests/next_goal_test.sh
./tests/release_attest_test.sh
./tests/release_proof_test.sh
./tests/release_index_test.sh
./tests/release_manifest_test.sh
./tests/release_consume_test.sh
./tests/release_consume_action_test.sh
./tests/release_diff_test.sh
./tests/release_diff_action_test.sh
./tests/release_evidence_test.sh
./tests/release_evidence_action_test.sh
./tests/release_evidence_verify_test.sh
./tests/release_evidence_verify_action_test.sh
./tests/release_evidence_negative_index_action_test.sh
./tests/release_proof_action_test.sh
./tests/release_proof_consumption_test.sh
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
6. Create release \`v$release_version\` and upload \`dist/shipguard-v$release_version.tar.gz\`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

\`\`\`bash
./bin/shipguard next-goal --out NEXT_GOAL.md
\`\`\`
EOF

echo "wrote: $out_file"
