#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

tarball="$(./scripts/package_release.sh)"
version="$(sed -n '1p' VERSION)"
package_name="codex-maintainer-v$version"
tar_list="$tmp_dir/tar-list.txt"

[[ -f "$tarball" ]] || {
  echo "missing package tarball: $tarball" >&2
  exit 1
}

tar -tzf "$tarball" > "$tar_list"
grep -q "^$package_name/bin/codex-maintainer$" "$tar_list"
grep -q "^$package_name/AGENTS.md$" "$tar_list"
grep -q "^$package_name/.github/workflows/autopsy-artifact.yml$" "$tar_list"
grep -q "^$package_name/actions/arena-compare/action.yml$" "$tar_list"
grep -q "^$package_name/actions/ci-gate/action.yml$" "$tar_list"
grep -q "^$package_name/actions/docs-check/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-consume/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-diff/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence-negative-index/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence-verify/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-proof/action.yml$" "$tar_list"
grep -q "^$package_name/actions/review-comment/action.yml$" "$tar_list"
grep -q "^$package_name/actions/transcript-corpus/action.yml$" "$tar_list"
grep -q "^$package_name/actions/transcript-verify/action.yml$" "$tar_list"
grep -q "^$package_name/actions/validate/action.yml$" "$tar_list"
grep -q "^$package_name/docs/arena.md$" "$tar_list"
grep -q "^$package_name/docs/arena-compare-action.md$" "$tar_list"
grep -q "^$package_name/docs/autopsy-github-actions.md$" "$tar_list"
grep -q "^$package_name/docs/benchmark.md$" "$tar_list"
grep -q "^$package_name/docs/check-run.md$" "$tar_list"
grep -q "^$package_name/docs/ci-gate.md$" "$tar_list"
grep -q "^$package_name/docs/ci-summary.md$" "$tar_list"
grep -q "^$package_name/docs/command-matrix.md$" "$tar_list"
grep -q "^$package_name/docs/core-loop.md$" "$tar_list"
grep -q "^$package_name/docs/demo-reports.md$" "$tar_list"
grep -q "^$package_name/docs/docs-check-action.md$" "$tar_list"
grep -q "^$package_name/docs/docs-check.md$" "$tar_list"
grep -q "^$package_name/docs/ios-shipguard.md$" "$tar_list"
grep -q "^$package_name/docs/ios-preview.md$" "$tar_list"
grep -q "^$package_name/docs/shipguard-devspace.md$" "$tar_list"
grep -q "^$package_name/docs/maintainer-reliability-os.md$" "$tar_list"
grep -q "^$package_name/docs/next-goal.md$" "$tar_list"
grep -q "^$package_name/docs/policy.md$" "$tar_list"
grep -q "^$package_name/docs/pr-review-bot.md$" "$tar_list"
grep -q "^$package_name/docs/release-checklist.md$" "$tar_list"
grep -q "^$package_name/docs/release-attest.md$" "$tar_list"
grep -q "^$package_name/docs/release-consume-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-consume.md$" "$tar_list"
grep -q "^$package_name/docs/release-diff-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-diff.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-bundle.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-index.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-negative-index-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-site.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-verify.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-consumption.md$" "$tar_list"
grep -q "^$package_name/docs/release-index.md$" "$tar_list"
grep -q "^$package_name/docs/release-manifest.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-workflows.md$" "$tar_list"
grep -q "^$package_name/docs/release-replay.md$" "$tar_list"
grep -q "^$package_name/docs/sarif.md$" "$tar_list"
grep -q "^$package_name/docs/template-profiles.md$" "$tar_list"
grep -q "^$package_name/docs/transcript-corpus-action.md$" "$tar_list"
grep -q "^$package_name/docs/transcript-corpus.md$" "$tar_list"
grep -q "^$package_name/docs/transcript-redaction.md$" "$tar_list"
grep -q "^$package_name/docs/transcript-verify-action.md$" "$tar_list"
grep -q "^$package_name/docs/oss-evaluation.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/specs/2026-06-16-ios-preview-bridge-design.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/specs/2026-06-16-shipguard-devspace-mcp-design.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/plans/2026-06-16-oss-eval-improvements.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/plans/2026-06-16-ios-shipguard-autonomous-loop.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/plans/2026-06-16-ios-preview-bridge.md$" "$tar_list"
grep -q "^$package_name/docs/superpowers/plans/2026-06-16-shipguard-devspace-mcp.md$" "$tar_list"
grep -q "^$package_name/scripts/install.sh$" "$tar_list"
grep -q "^$package_name/scripts/ios_doctor.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_goal_loop.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_inventory.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_preview.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_codex_handoff.py$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_devspace_mcp.py$" "$tar_list"
grep -q "^$package_name/scripts/arena_import.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_compare.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_sign.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_verify.sh$" "$tar_list"
grep -q "^$package_name/scripts/autopsy_report.sh$" "$tar_list"
grep -q "^$package_name/scripts/build_demo_reports.sh$" "$tar_list"
grep -q "^$package_name/scripts/check_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_gate.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_summary.sh$" "$tar_list"
grep -q "^$package_name/scripts/docs_check.sh$" "$tar_list"
grep -q "^$package_name/scripts/leaderboard_build.sh$" "$tar_list"
grep -q "^$package_name/scripts/lib/safe_paths.sh$" "$tar_list"
grep -q "^$package_name/scripts/next_goal.sh$" "$tar_list"
grep -q "^$package_name/scripts/policy.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_attest.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_consume.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_proof.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_index.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_manifest.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_replay.sh$" "$tar_list"
grep -q "^$package_name/scripts/review_comment.sh$" "$tar_list"
grep -q "^$package_name/scripts/sarif.sh$" "$tar_list"
grep -q "^$package_name/scripts/self_audit.sh$" "$tar_list"
grep -q "^$package_name/scripts/transcript_redact.sh$" "$tar_list"
grep -q "^$package_name/scripts/transcript_verify.sh$" "$tar_list"
grep -q "^$package_name/scripts/transcript_corpus.sh$" "$tar_list"
grep -q "^$package_name/tests/package_release_test.sh$" "$tar_list"
grep -q "^$package_name/tests/action_artifact_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_compare_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_compare_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_import_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_sign_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_test.sh$" "$tar_list"
grep -q "^$package_name/tests/autopsy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/check_run_post_test.sh$" "$tar_list"
grep -q "^$package_name/tests/check_run_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ci_gate_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ci_summary_test.sh$" "$tar_list"
grep -q "^$package_name/tests/docs_check_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/docs_check_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_doctor_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_goal_loop_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_inventory_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_preview_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_codex_handoff_test.sh$" "$tar_list"
grep -q "^$package_name/tests/shipguard_devspace_mcp_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_target_risk_map_test.sh$" "$tar_list"
grep -q "^$package_name/tests/leaderboard_test.sh$" "$tar_list"
grep -q "^$package_name/tests/next_goal_test.sh$" "$tar_list"
grep -q "^$package_name/tests/policy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_attest_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_consume_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_consume_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_diff_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_diff_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_negative_index_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_verify_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_verify_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_index_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_manifest_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_consumption_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_workflow_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_replay_test.sh$" "$tar_list"
grep -q "^$package_name/tests/review_comment_test.sh$" "$tar_list"
grep -q "^$package_name/tests/safe_paths_test.sh$" "$tar_list"
grep -q "^$package_name/tests/sarif_test.sh$" "$tar_list"
grep -q "^$package_name/tests/self_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/template_profiles_test.sh$" "$tar_list"
grep -q "^$package_name/tests/transcript_redaction_test.sh$" "$tar_list"
grep -q "^$package_name/tests/transcript_verify_test.sh$" "$tar_list"
grep -q "^$package_name/tests/transcript_verify_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/transcript_corpus_test.sh$" "$tar_list"
grep -q "^$package_name/tests/transcript_corpus_action_test.sh$" "$tar_list"
grep -q "^$package_name/templates/backend/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/backend/README.md$" "$tar_list"
grep -q "^$package_name/templates/cli/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/cli/README.md$" "$tar_list"
grep -q "^$package_name/templates/ios/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/web/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/web/README.md$" "$tar_list"
grep -q "^$package_name/templates/policy/default.conf$" "$tar_list"
grep -q "^$package_name/evals/README.md$" "$tar_list"
grep -q "^$package_name/evals/cases.jsonl$" "$tar_list"
grep -q "^$package_name/evals/run_local.py$" "$tar_list"
grep -q "^$package_name/fixtures/policy/strict.conf$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoCodexMaintainerApp.xcodeproj/project.pbxproj$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoCodexMaintainerApp.xcodeproj/xcshareddata/xcschemes/DemoCodexMaintainerApp.xcscheme$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoCodexMaintainerApp.xcworkspace/contents.xcworkspacedata$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoCodexMaintainerApp.xctestplan$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoProducts.storekit$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/PrivacyInfo.xcprivacy$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoCodexMaintainerApp/DemoCodexMaintainerApp.entitlements$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoCodexMaintainerApp/DemoPermissions.swift$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoCodexMaintainerApp/Info.plist$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Tests/DemoCodexMaintainerAppTests/DemoPermissionsTests.swift$" "$tar_list"
grep -q "^$package_name/fixtures/arena/good-maintainer/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/cli-dangerous-clean/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/failing-validation/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/no-diff-implementation/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/review-only/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/external-arena-pack/imported-clean/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/external-arena-pack/imported-risky/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/autopsy/good-run/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/ios-notification-triage/transcript.md$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/ios-notification-triage/redaction-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/release-proof-review/transcript.md$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/release-proof-review/redaction-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/release-evidence-consumption/transcript.md$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/release-evidence-consumption/redaction-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/web-regression-review/transcript.md$" "$tar_list"
grep -q "^$package_name/fixtures/transcripts/web-regression-review/redaction-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/cases.tsv$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/missing-source/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/consumer-mismatch/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/digest-summary-mismatch/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/bundle-missing-output/bundle.json$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/leaderboard.json$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/transcripts/corpus.json$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/transcripts/index.md$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/transcripts/badge.json$" "$tar_list"
grep -q "^$package_name/examples/release-proof-consumption-checklist.md$" "$tar_list"
grep -q "^$package_name/examples/redacted-transcript.md$" "$tar_list"
grep -q "^$package_name/examples/workflows/arena-compare.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/docs-check.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/transcript-corpus.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/transcript-verify.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-consume-verify.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-diff-compare.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-bundle.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-consume.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-export.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-negative-index.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-proof-on-tag.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-proof-manual.yml$" "$tar_list"
grep -q "^$package_name/.agents/skills/alarm-testing/SKILL.md$" "$tar_list"
grep -q "^$package_name/.agents/plugins/marketplace.json$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/.mcp.json$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/.codex-plugin/plugin.json$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/SKILL.md$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/agents/openai.yaml$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/references/modes.md$" "$tar_list"

if grep -Eq '(^|/)(\\.git|dist|DerivedData|\\.cache)(/|$)' "$tar_list"; then
  echo "package includes forbidden generated or VCS paths" >&2
  exit 1
fi

tar -xzf "$tarball" -C "$tmp_dir"
package_root="$tmp_dir/$package_name"

local_path_pattern="/""Users/"
if grep -RIEq "$local_path_pattern|ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}" "$package_root"; then
  echo "package includes a local path or secret-looking token" >&2
  exit 1
fi

test "$("$package_root/bin/codex-maintainer" version)" = "$version"
"$package_root/bin/codex-maintainer" policy show >/dev/null
"$package_root/bin/codex-maintainer" validate "$package_root" >/dev/null
"$package_root/bin/codex-maintainer" ios doctor \
  --path "$package_root/fixtures/demo-ios-repo" \
  --out "$tmp_dir/package-ios-doctor" >/dev/null
grep -q 'DemoCodexMaintainerApp.xcodeproj' "$tmp_dir/package-ios-doctor/ios-doctor.md"
grep -q 'DemoProducts.storekit' "$tmp_dir/package-ios-doctor/ios-doctor.md"
"$package_root/bin/codex-maintainer" ios inventory \
  --path "$package_root/fixtures/demo-ios-repo" \
  --doctor "$tmp_dir/package-ios-doctor/ios-doctor.json" \
  --out "$tmp_dir/package-ios-inventory" >/dev/null
grep -q 'Target Risk Map' "$tmp_dir/package-ios-inventory/ios-inventory.md"
grep -q 'Location | needs-user-answer' "$tmp_dir/package-ios-inventory/ios-inventory.md"
"$package_root/bin/codex-maintainer" ios preview --help >/dev/null
"$package_root/bin/codex-maintainer" ios devspace --help >/dev/null
"$package_root/bin/codex-maintainer" ios codex-handoff --help >/dev/null
"$package_root/bin/codex-maintainer" ios goals init \
  --state "$tmp_dir/package-shipguard-goals.json" \
  --out "$tmp_dir/package-next-shipguard-goal.md" >/dev/null
grep -q '/goal Implement shipguard-ios-doctor' "$tmp_dir/package-next-shipguard-goal.md"
"$package_root/bin/codex-maintainer" init ios "$tmp_dir/demo-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor "$tmp_dir/demo-target" >/dev/null
"$package_root/bin/codex-maintainer" init web "$tmp_dir/web-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor web "$tmp_dir/web-target" >/dev/null
grep -q 'Web Codex Maintainer Instructions' "$tmp_dir/web-target/AGENTS.md"
"$package_root/bin/codex-maintainer" init backend "$tmp_dir/backend-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor backend "$tmp_dir/backend-target" >/dev/null
grep -q 'Backend Service Codex Maintainer Instructions' "$tmp_dir/backend-target/AGENTS.md"
"$package_root/bin/codex-maintainer" init cli "$tmp_dir/cli-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor cli "$tmp_dir/cli-target" >/dev/null
grep -q 'CLI Tool Codex Maintainer Instructions' "$tmp_dir/cli-target/AGENTS.md"
"$package_root/bin/codex-maintainer" autopsy \
  --run "$package_root/fixtures/autopsy/good-run/run.md" \
  --task "$package_root/fixtures/autopsy/good-run/task.md" \
  --diff "$package_root/fixtures/autopsy/good-run/diff.patch" \
  --tests "$package_root/fixtures/autopsy/good-run/tests.log" \
  --out "$tmp_dir/package-autopsy" >/dev/null
grep -q '"total": 11' "$tmp_dir/package-autopsy/report.json"
grep -q '"verdict": "usable maintainer-quality run"' "$tmp_dir/package-autopsy/report.json"
"$package_root/bin/codex-maintainer" arena run \
  --fixture "$package_root/fixtures/arena" \
  --out "$tmp_dir/package-arena" >/dev/null
grep -q '"case_count": 10' "$tmp_dir/package-arena/results.json"
grep -q '"average_total": 7.00' "$tmp_dir/package-arena/results.json"
grep -q '"high_risk_finding_count": 8' "$tmp_dir/package-arena/results.json"
mkdir -p "$tmp_dir/package-eight-case-fixture"
for case_id in \
  backend-webhook-idempotency \
  cli-dangerous-clean \
  dangerous-maintainer \
  failing-validation \
  good-maintainer \
  no-diff-implementation \
  review-only \
  weak-maintainer; do
  cp -R "$package_root/fixtures/arena/$case_id" "$tmp_dir/package-eight-case-fixture/$case_id"
done
"$package_root/bin/codex-maintainer" arena run \
  --fixture "$tmp_dir/package-eight-case-fixture" \
  --out "$tmp_dir/package-old-arena" >/dev/null
"$package_root/bin/codex-maintainer" arena compare \
  --left "$tmp_dir/package-old-arena/results.json" \
  --right "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-arena-compare" >/dev/null
grep -q '"status" : "improved"' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"average_total_delta" : 0.75' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"id" : "docs-release-proof-drift"' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"id" : "frontend-async-state-regression"' "$tmp_dir/package-arena-compare/arena-compare.json"
"$package_root/bin/codex-maintainer" arena import \
  --source "$package_root/fixtures/external-arena-pack" \
  --out "$tmp_dir/package-imported-arena" \
  --pack-name "package-imported" >/dev/null
grep -q 'Pack: package-imported' "$tmp_dir/package-imported-arena/PACK.md"
"$package_root/bin/codex-maintainer" arena run \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-results" >/dev/null
grep -q '"case_count": 2' "$tmp_dir/package-imported-results/results.json"
"$package_root/bin/codex-maintainer" arena sign \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-arena/PACK.json" \
  --pack-name "package-imported" \
  --signer "Package Fixture Maintainer" \
  --signer-url "https://github.com/jlekerli-source/ringly-codex-workflows" >/dev/null
grep -q '"signature_type" : "sha256-content-digest"' "$tmp_dir/package-imported-arena/PACK.json"
grep -q '"signer" : "Package Fixture Maintainer"' "$tmp_dir/package-imported-arena/PACK.json"
grep -q '"identity_digest" : "[a-f0-9]\{64\}"' "$tmp_dir/package-imported-arena/PACK.json"
"$package_root/bin/codex-maintainer" arena verify \
  --fixture "$tmp_dir/package-imported-arena" \
  --manifest "$tmp_dir/package-imported-arena/PACK.json" >/dev/null
"$package_root/bin/codex-maintainer" review-comment \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-review/comment.md" \
  --badge "$tmp_dir/package-review/badge.json" \
  --artifact-dir "$tmp_dir/package-review" >/dev/null
grep -q '| Status | pass |' "$tmp_dir/package-review/comment.md"
grep -q '"message": "pass 11/12"' "$tmp_dir/package-review/badge.json"
"$package_root/bin/codex-maintainer" ci-gate \
  --run "$package_root/fixtures/autopsy/good-run/run.md" \
  --task "$package_root/fixtures/autopsy/good-run/task.md" \
  --diff "$package_root/fixtures/autopsy/good-run/diff.patch" \
  --tests "$package_root/fixtures/autopsy/good-run/tests.log" \
  --policy "$package_root/templates/policy/default.conf" \
  --out "$tmp_dir/package-gate" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-gate/gate.json"
grep -q '"sarif": "sarif/results.sarif"' "$tmp_dir/package-gate/gate.json"
grep -q '"summary": "summary.md"' "$tmp_dir/package-gate/gate.json"
grep -q '"version" : "2.1.0"' "$tmp_dir/package-gate/sarif/results.sarif"
grep -q '| Status | pass |' "$tmp_dir/package-gate/summary.md"
"$package_root/bin/codex-maintainer" docs-check "$package_root" --out "$tmp_dir/package-docs-check" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-docs-check/docs-check.json"
grep -q '"broken_count" : 0' "$tmp_dir/package-docs-check/docs-check.json"
"$package_root/bin/codex-maintainer" ci-summary \
  --gate "$tmp_dir/package-gate/gate.json" \
  --out "$tmp_dir/package-summary.md" >/dev/null
grep -q '| Score | 11/12 |' "$tmp_dir/package-summary.md"
"$package_root/bin/codex-maintainer" check-run \
  --gate "$tmp_dir/package-gate/gate.json" \
  --head-sha 0123456789abcdef \
  --out "$tmp_dir/package-check-run/payload.json" >/dev/null
grep -q '"conclusion" : "success"' "$tmp_dir/package-check-run/payload.json"
grep -q '"head_sha" : "0123456789abcdef"' "$tmp_dir/package-check-run/payload.json"
"$package_root/bin/codex-maintainer" check-run post \
  --payload "$tmp_dir/package-check-run/payload.json" \
  --repo owner/repo \
  --out "$tmp_dir/package-check-run/dry-run.json" \
  --dry-run >/dev/null
grep -q '"dry_run" : true' "$tmp_dir/package-check-run/dry-run.json"
grep -q '"url" : "https://api.github.com/repos/owner/repo/check-runs"' "$tmp_dir/package-check-run/dry-run.json"
"$package_root/bin/codex-maintainer" leaderboard build \
  --arena-results "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-leaderboard.json" >/dev/null
grep -q '"schema_version": "1.0"' "$tmp_dir/package-leaderboard.json"
grep -q '"average_total": 7.00' "$tmp_dir/package-leaderboard.json"
"$package_root/bin/codex-maintainer" release-manifest \
  --tarball "$tarball" \
  --out "$tmp_dir/package-release-proof" \
  --version "$version" \
  --tag "v$version" \
  --commit 0123456789abcdef \
  --ci-run-url "https://github.com/example/repo/actions/runs/123" \
  --release-url "https://github.com/example/repo/releases/tag/v$version" \
  --issue-url "https://github.com/example/repo/issues/99" >/dev/null
grep -q '"schema_version" : "1.0"' "$tmp_dir/package-release-proof/release-manifest.json"
grep -q "\"tag\" : \"v$version\"" "$tmp_dir/package-release-proof/release-manifest.json"
grep -q 'Artifact SHA-256:' "$tmp_dir/package-release-proof/proof-ledger.md"
"$package_root/bin/codex-maintainer" release-manifest verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --version "$version" \
  --tag "v$version" >/dev/null
"$package_root/bin/codex-maintainer" release-index build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --out "$tmp_dir/package-release-index" >/dev/null
grep -q '"release_count" : 1' "$tmp_dir/package-release-index/release-index.json"
grep -q '| '"$version"' | v'"$version"' | 0123456789ab | codex-maintainer-v'"$version"'.tar.gz |' "$tmp_dir/package-release-index/release-index.md"
"$package_root/bin/codex-maintainer" release-replay verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --index "$tmp_dir/package-release-index/release-index.json" \
  --ledger "$tmp_dir/package-release-proof/proof-ledger.md" \
  --out "$tmp_dir/package-release-replay" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '"name": "artifact sha256"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '# Release Replay Report' "$tmp_dir/package-release-replay/replay-report.md"
"$package_root/bin/codex-maintainer" release-attest build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --replay "$tmp_dir/package-release-replay/replay-report.json" \
  --out "$tmp_dir/package-release-attestation" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-attestation/attestation-badge.json"
grep -q '# Codex Maintainer Release Attestation' "$tmp_dir/package-release-attestation/attestation.md"
"$package_root/bin/codex-maintainer" release-proof build \
  --out "$tmp_dir/package-release-proof-bundle" \
  --version "$version" \
  --tag "v$version" \
  --commit 0123456789abcdef \
  --ci-run-url "https://github.com/example/repo/actions/runs/123" \
  --release-url "https://github.com/example/repo/releases/tag/v$version" \
  --issue-url "https://github.com/example/repo/issues/99" >/dev/null
test -f "$tmp_dir/package-release-proof-bundle/codex-maintainer-v$version.tar.gz"
grep -q '"status": "pass"' "$tmp_dir/package-release-proof-bundle/replay/replay-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-proof-bundle/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json"
mkdir -p "$tmp_dir/package-release-consume-assets"
cp "$tmp_dir/package-release-proof-bundle/codex-maintainer-v$version.tar.gz" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/release-manifest.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/index/release-index.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/proof-ledger.md" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/replay/replay-report.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json" "$tmp_dir/package-release-consume-assets/"
"$package_root/bin/codex-maintainer" release-consume verify \
  --dir "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-consume" \
  --version "$version" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_blocked": 0' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_report": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"attestation_badge": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"asset_digest_matrix": "asset-digests.json"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q "| codex-maintainer-v$version.tar.gz | release tarball | true | present |" "$tmp_dir/package-release-consume/asset-digests.md"
grep -q '"name": "attestation-badge.json"' "$tmp_dir/package-release-consume/asset-digests.json"
"$package_root/bin/codex-maintainer" release-diff compare \
  --left "$tmp_dir/package-release-proof-bundle" \
  --right "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-diff" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-diff/release-diff.json"
grep -q '# Release Diff Audit' "$tmp_dir/package-release-diff/release-diff.md"
"$package_root/bin/codex-maintainer" release-evidence site \
  --consume "$tmp_dir/package-release-consume" \
  --diff "$tmp_dir/package-release-diff" \
  --out "$tmp_dir/package-release-site" >/dev/null
test -f "$tmp_dir/package-release-site/index.html"
test -f "$tmp_dir/package-release-site/evidence.json"
test -f "$tmp_dir/package-release-site/sources/consumer-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-site/evidence.json"
grep -q 'Asset Digest Matrix' "$tmp_dir/package-release-site/index.html"
"$package_root/bin/codex-maintainer" release-evidence index \
  --site "$tmp_dir/package-release-site" \
  --out "$tmp_dir/package-release-evidence-index" >/dev/null
test -f "$tmp_dir/package-release-evidence-index/index.html"
test -f "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q 'Machine-readable index' "$tmp_dir/package-release-evidence-index/index.html"
"$package_root/bin/codex-maintainer" release-evidence bundle \
  --assets "$tmp_dir/package-release-consume-assets" \
  --left "$tmp_dir/package-release-proof-bundle" \
  --out "$tmp_dir/package-release-evidence-bundle" \
  --version "$version" >/dev/null
test -f "$tmp_dir/package-release-evidence-bundle/bundle.json"
test -f "$tmp_dir/package-release-evidence-bundle/consumer-proof/consumer-report.json"
test -f "$tmp_dir/package-release-evidence-bundle/release-diff/release-diff.json"
test -f "$tmp_dir/package-release-evidence-bundle/site/index.html"
test -f "$tmp_dir/package-release-evidence-bundle/index/evidence-index.json"
grep -q '"status": "pass"' "$tmp_dir/package-release-evidence-bundle/bundle.json"
grep -q '"diff_included": true' "$tmp_dir/package-release-evidence-bundle/bundle.json"
"$package_root/bin/codex-maintainer" release-evidence verify \
  --dir "$tmp_dir/package-release-evidence-bundle" \
  --out "$tmp_dir/package-release-evidence-verify" \
  --require-diff true \
  --require-index true >/dev/null
test -f "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
test -f "$tmp_dir/package-release-evidence-verify/evidence-verify.md"
test -f "$tmp_dir/package-release-evidence-verify/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
grep -q '"bundle_present" : true' "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-evidence-verify/badge.json"
"$package_root/bin/codex-maintainer" release-evidence negative-index \
  --fixture "$package_root/fixtures/release-evidence/negative" \
  --out "$tmp_dir/package-release-evidence-negative-index" >/dev/null
test -f "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
test -f "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.md"
test -f "$tmp_dir/package-release-evidence-negative-index/index.html"
test -f "$tmp_dir/package-release-evidence-negative-index/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"case_count" : 4' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"expected_blocked_count" : 4' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"message" : "pass 4/4"' "$tmp_dir/package-release-evidence-negative-index/badge.json"
grep -q 'Machine-readable index' "$tmp_dir/package-release-evidence-negative-index/index.html"
test -f "$package_root/actions/release-diff/action.yml"
grep -q 'release-diff compare' "$package_root/actions/release-diff/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-diff/action.yml"
test -f "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence site' "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence index' "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence bundle' "$package_root/actions/release-evidence/action.yml"
grep -q 'download-assets:' "$package_root/actions/release-evidence/action.yml"
grep -q 'gh release download "$release_tag"' "$package_root/actions/release-evidence/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence/action.yml"
test -f "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'release-evidence negative-index' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'fixture:' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'index-html=' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence-negative-index/action.yml"
test -f "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'release-evidence verify' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'require-diff:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'download-artifact:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'source-artifact-name:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'actions/download-artifact@v4' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence-verify/action.yml"
test -f "$package_root/actions/release-consume/action.yml"
grep -q 'release-consume verify' "$package_root/actions/release-consume/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-consume/action.yml"
test -f "$package_root/actions/docs-check/action.yml"
grep -q 'docs-check' "$package_root/actions/docs-check/action.yml"
grep -q 'docs-check.json' "$package_root/actions/docs-check/action.yml"
grep -q 'docs-check.md' "$package_root/actions/docs-check/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/docs-check/action.yml"
"$package_root/tests/release_consume_action_test.sh" >/dev/null
"$package_root/tests/release_diff_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_test.sh" >/dev/null
"$package_root/tests/release_evidence_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_negative_index_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_verify_test.sh" >/dev/null
"$package_root/tests/release_evidence_verify_action_test.sh" >/dev/null
"$package_root/tests/release_proof_consumption_test.sh" >/dev/null
"$package_root/tests/arena_compare_action_test.sh" >/dev/null
"$package_root/tests/transcript_redaction_test.sh" >/dev/null
"$package_root/tests/transcript_verify_test.sh" >/dev/null
"$package_root/tests/transcript_verify_action_test.sh" >/dev/null
"$package_root/tests/transcript_corpus_test.sh" >/dev/null
"$package_root/tests/transcript_corpus_action_test.sh" >/dev/null
"$package_root/tests/docs_check_action_test.sh" >/dev/null
package_raw_transcript="$tmp_dir/package-raw-transcript.md"
package_home_prefix="/""home"
package_home_path="$package_home_prefix/runner/AcmePrivateApp"
cat > "$package_raw_transcript" <<'RAW'
# Raw Transcript

Maintainer: AcmePrivateApp lives under __PACKAGE_HOME_PATH__.
Agent: I will redact maintainer@example.com before sharing.
Maintainer: Use API_TOKEN=example-secret-value only as a placeholder.
RAW
PACKAGE_HOME_PATH="$package_home_path" \
  perl -pi -e 's#__PACKAGE_HOME_PATH__#$ENV{PACKAGE_HOME_PATH}#g' "$package_raw_transcript"
"$package_root/bin/codex-maintainer" transcript redact \
  --in "$package_raw_transcript" \
  --out "$tmp_dir/package-redacted-transcript.md" \
  --report "$tmp_dir/package-redaction-report.json" \
  --private-term "AcmePrivateApp" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-redaction-report.json"
grep -q '\[redacted-private-term\]' "$tmp_dir/package-redacted-transcript.md"
grep -q "$package_home_prefix/\\[redacted-user\\]" "$tmp_dir/package-redacted-transcript.md"
grep -q '\[redacted-email\]' "$tmp_dir/package-redacted-transcript.md"
grep -q 'API_TOKEN=\[redacted-secret\]' "$tmp_dir/package-redacted-transcript.md"
"$package_root/bin/codex-maintainer" transcript verify \
  --in "$tmp_dir/package-redacted-transcript.md" \
  --report "$tmp_dir/package-redaction-report.json" \
  --out "$tmp_dir/package-transcript-verify" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-transcript-verify/transcript-verify.json"
grep -q '"message" : "pass"' "$tmp_dir/package-transcript-verify/badge.json"
"$package_root/bin/codex-maintainer" transcript corpus \
  --source "$package_root/fixtures/transcripts" \
  --out "$tmp_dir/package-transcript-corpus" \
  --require-report true >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-transcript-corpus/corpus.json"
grep -q '"case_count": 4' "$tmp_dir/package-transcript-corpus/corpus.json"
grep -q '"message": "pass 4/4"' "$tmp_dir/package-transcript-corpus/badge.json"
"$package_root/bin/codex-maintainer" self-audit \
  --out "$tmp_dir/package-self-audit" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-self-audit/self-audit.json"
grep -q '| codex-maintainer transcript redact --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer transcript verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer transcript corpus --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer arena compare --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/arena-compare/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer leaderboard build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-attest build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-proof build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-index build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-manifest --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-manifest verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-replay verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-consume verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-diff compare --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence site --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence bundle --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence negative-index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer docs-check --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/docs-check/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-consume/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-diff/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-negative-index/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-verify/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-proof/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/transcript-corpus/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/transcript-verify/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/arena-compare-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/docs-check-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/transcript-corpus-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/transcript-corpus.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/transcript-redaction.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/transcript-verify-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-consume-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-consume.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-diff-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-diff.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-bundle.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-index.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-negative-index-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-site.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-verify.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-consumption.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-workflows.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-proof-on-tag.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/arena-compare.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/docs-check.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/transcript-corpus.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/transcript-verify.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-proof-manual.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-consume-verify.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-diff-compare.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-bundle.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-consume.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-export.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-negative-index.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/release-evidence/negative/README.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/release-evidence/negative/cases.tsv | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/demo-reports/transcripts/corpus.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/docs-check.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/ios-preview.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/shipguard-devspace.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/superpowers/specs/2026-06-16-ios-preview-bridge-design.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/superpowers/specs/2026-06-16-shipguard-devspace-mcp-design.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/superpowers/plans/2026-06-16-ios-preview-bridge.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/superpowers/plans/2026-06-16-shipguard-devspace-mcp.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/release-proof-consumption-checklist.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/redacted-transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/transcripts/ios-notification-triage/transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/transcripts/release-evidence-consumption/transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_redact.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_verify.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_corpus.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/docs_check.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_preview.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_codex_handoff.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_devspace_mcp.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/ios_codex_handoff_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/shipguard_devspace_mcp_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/.mcp.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
"$package_root/bin/codex-maintainer" sarif \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-sarif/results.sarif" >/dev/null
grep -q '"version" : "2.1.0"' "$tmp_dir/package-sarif/results.sarif"
"$package_root/bin/codex-maintainer" next-goal \
  --release 2.6.0 \
  --title "Package Proof Followup" \
  --out "$tmp_dir/package-next-goal.md" >/dev/null
grep -q '/goal Implement v2.6.0 Package Proof Followup' "$tmp_dir/package-next-goal.md"
grep -q './tests/template_profiles_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_import_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_compare_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_compare_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_sign_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/check_run_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/check_run_post_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ci_summary_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/sarif_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/docs_check_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/docs_check_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/transcript_redaction_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/transcript_verify_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/transcript_verify_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/transcript_corpus_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/transcript_corpus_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_attest_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_index_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_manifest_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_consume_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_consume_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_diff_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_diff_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_verify_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_verify_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_negative_index_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_consumption_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_workflow_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_replay_test.sh' "$tmp_dir/package-next-goal.md"

install_prefix="$tmp_dir/install"
PREFIX="$install_prefix" "$package_root/scripts/install.sh" >/dev/null
test "$("$install_prefix/bin/codex-maintainer" version)" = "$version"

echo "package release tests passed"
