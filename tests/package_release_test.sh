#!/usr/bin/env bash

set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
  rm -rf "$repo_root/scripts/__pycache__"
  rm -f "$repo_root/.cache/shipguard-package-test.tmp"
  rmdir "$repo_root/.cache" >/dev/null 2>&1 || true
  rm -f "$repo_root/DerivedData/shipguard-package-test.tmp"
  rmdir "$repo_root/DerivedData" >/dev/null 2>&1 || true
}
trap cleanup EXIT
trap 'echo "package release test failed at line $LINENO: $BASH_COMMAND" >&2' ERR

cd "$repo_root"

mkdir -p scripts/__pycache__ .cache DerivedData
printf 'bytecode sentinel\n' > scripts/__pycache__/shipguard_package_test.pyc
printf 'cache sentinel\n' > .cache/shipguard-package-test.tmp
printf 'derived data sentinel\n' > DerivedData/shipguard-package-test.tmp

tarball="$(./scripts/package_release.sh)"
version="$(sed -n '1p' VERSION)"
package_name="shipguard-v$version"
tar_list="$tmp_dir/tar-list.txt"

[[ -f "$tarball" ]] || {
  echo "missing package tarball: $tarball" >&2
  exit 1
}

tar -tzf "$tarball" > "$tar_list"
grep -q "^$package_name/bin/shipguard$" "$tar_list"
grep -q "^$package_name/bin/codex-maintainer$" "$tar_list"
grep -q "^$package_name/AGENTS.md$" "$tar_list"
grep -q "^$package_name/NEXT_GOAL.md$" "$tar_list"
grep -q "^$package_name/CODE_OF_CONDUCT.md$" "$tar_list"
grep -q "^$package_name/CONTRIBUTING.md$" "$tar_list"
grep -q "^$package_name/GOVERNANCE.md$" "$tar_list"
grep -q "^$package_name/LICENSE$" "$tar_list"
grep -q "^$package_name/SECURITY.md$" "$tar_list"
grep -q "^$package_name/SUPPORT.md$" "$tar_list"
grep -q "^$package_name/.agents/plugins/marketplace.json$" "$tar_list"
grep -q "^$package_name/.github/ISSUE_TEMPLATE/bug-report.yml$" "$tar_list"
grep -q "^$package_name/.github/ISSUE_TEMPLATE/proposal.yml$" "$tar_list"
grep -q "^$package_name/.github/ISSUE_TEMPLATE/workflow-gap.yml$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/.codex-plugin/plugin.json$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/.mcp.json$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/assets/app-icon.png$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/assets/composer-icon.png$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/SKILL.md$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/agents/openai.yaml$" "$tar_list"
grep -q "^$package_name/plugins/ios-shipguard/skills/ios-shipguard/references/modes.md$" "$tar_list"
grep -q 'SHIPGUARD_CLI' plugins/ios-shipguard/skills/ios-shipguard/SKILL.md
grep -q 'command -v shipguard' plugins/ios-shipguard/skills/ios-shipguard/SKILL.md
grep -q 'LaunchDeck' plugins/ios-shipguard/skills/ios-shipguard/SKILL.md
grep -q 'Brand Deck' plugins/ios-shipguard/skills/ios-shipguard/SKILL.md
grep -q 'Tool Value Gauntlet' plugins/ios-shipguard/skills/ios-shipguard/SKILL.md
grep -q 'hot reload' docs/ios-preview.md
python3 - <<'PY'
import json
from pathlib import Path

plugin = json.loads(Path("plugins/ios-shipguard/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
interface = plugin["interface"]
for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
    assert interface.get(key, "").startswith("https://github.com/jlekerli-source/ShipGuard"), key
assert len(interface["defaultPrompt"]) <= 3

mcp = json.loads(Path("plugins/ios-shipguard/.mcp.json").read_text(encoding="utf-8"))
server = mcp["mcpServers"]["shipguard-devspace"]
assert server["command"] == "bash"
args = " ".join(server["args"])
assert "SHIPGUARD_CLI" in args
assert "command -v shipguard" in args
assert "$HOME/.local/bin/shipguard" in args
assert "./scripts/shipguard_devspace_mcp.py" not in args
PY
grep -q "^$package_name/.github/workflows/autopsy-artifact.yml$" "$tar_list"
grep -q "^$package_name/actions/arena-compare/action.yml$" "$tar_list"
grep -q "^$package_name/actions/ci-gate/action.yml$" "$tar_list"
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
grep -q "^$package_name/fixtures/ios-report-quality/token-shareability/ios-devspace-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/token-shareability/ios-devspace-report.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/value-gauntlet-actionability/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/value-gauntlet-actionability/fixture-candidate.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/value-gauntlet-actionability/fixture-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/value-gauntlet-actionability/fixture-report.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/performance-evidence-promotion/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/performance-evidence-promotion/fixture-candidate.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/performance-evidence-promotion/fixture-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/performance-evidence-promotion/fixture-report.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-app-type-tailoring/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-app-type-tailoring/fixture-candidate.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-app-type-tailoring/fixture-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-app-type-tailoring/fixture-report.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-coherence-boundary/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-coherence-boundary/fixture-candidate.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-coherence-boundary/fixture-report.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-report-quality/design-coherence-boundary/fixture-report.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-devspace/complete-preview/session.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-devspace/complete-preview/handoff.json$" "$tar_list"
grep -q "^$package_name/fixtures/ios-devspace/complete-preview/handoff.md$" "$tar_list"
grep -q "^$package_name/fixtures/ios-devspace/complete-preview/preview-events.jsonl$" "$tar_list"
grep -q "^$package_name/docs/arena.md$" "$tar_list"
grep -q "^$package_name/docs/arena-compare-action.md$" "$tar_list"
grep -q "^$package_name/docs/autopsy-github-actions.md$" "$tar_list"
grep -q "^$package_name/docs/benchmark.md$" "$tar_list"
grep -q "^$package_name/docs/check-run.md$" "$tar_list"
grep -q "^$package_name/docs/ci-gate.md$" "$tar_list"
grep -q "^$package_name/docs/ci-summary.md$" "$tar_list"
grep -q "^$package_name/docs/codex-status.md$" "$tar_list"
grep -q "^$package_name/docs/codex-marketplace-readiness.md$" "$tar_list"
grep -q "^$package_name/docs/agent-trace.md$" "$tar_list"
grep -q "^$package_name/docs/full-audit.md$" "$tar_list"
grep -q "^$package_name/docs/inspect.md$" "$tar_list"
grep -q "^$package_name/docs/v4-preview.md$" "$tar_list"
grep -q "^$package_name/docs/compatibility.md$" "$tar_list"
grep -q "^$package_name/docs/command-matrix.md$" "$tar_list"
grep -q "^$package_name/docs/demo-reports.md$" "$tar_list"
grep -q "^$package_name/docs/docs-check.md$" "$tar_list"
grep -q "^$package_name/docs/shipguard-naming.md$" "$tar_list"
grep -q "^$package_name/docs/task-contract.md$" "$tar_list"
grep -q "^$package_name/docs/ios-preview.md$" "$tar_list"
grep -q "^$package_name/docs/ios-shipguard.md$" "$tar_list"
grep -q "^$package_name/docs/shipguard-devspace.md$" "$tar_list"
grep -q "^$package_name/docs/maintainer-reliability-os.md$" "$tar_list"
grep -q "^$package_name/docs/next-goal.md$" "$tar_list"
grep -q "^$package_name/docs/oss-evaluation.md$" "$tar_list"
grep -q "^$package_name/docs/open-source.md$" "$tar_list"
grep -q "^$package_name/docs/privacy.md$" "$tar_list"
grep -q "^$package_name/docs/product-strategy.md$" "$tar_list"
grep -q "^$package_name/docs/security-threat-model.md$" "$tar_list"
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
grep -q "^$package_name/scripts/install.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_import.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_compare.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_sign.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_verify.sh$" "$tar_list"
grep -q "^$package_name/scripts/autopsy_report.sh$" "$tar_list"
grep -q "^$package_name/scripts/build_demo_reports.sh$" "$tar_list"
grep -q "^$package_name/scripts/bug-triage/prompts.md$" "$tar_list"
grep -q "^$package_name/scripts/check_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/codex_status.sh$" "$tar_list"
grep -q "^$package_name/scripts/codex_marketplace_readiness.py$" "$tar_list"
grep -q "^$package_name/scripts/ci_gate.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_summary.sh$" "$tar_list"
grep -q "^$package_name/scripts/docs_check.sh$" "$tar_list"
grep -q "^$package_name/scripts/ios_ai_readiness.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_app_intelligence.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_branding.py$" "$tar_list"
grep -q "^$package_name/scripts/profile_audit.py$" "$tar_list"
grep -q "^$package_name/scripts/profile_fix_plan.py$" "$tar_list"
grep -q "^$package_name/scripts/task_domain_packs.py$" "$tar_list"
grep -q "^$package_name/scripts/task_contract.py$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_receipts.py$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_baseline.py$" "$tar_list"
grep -q "^$package_name/scripts/agent_trace.py$" "$tar_list"
grep -q "^$package_name/scripts/external_pilot_verdict_bench.py$" "$tar_list"
grep -q "^$package_name/scripts/tool_value_gauntlet.py$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_result.py$" "$tar_list"
grep -q "^$package_name/scripts/full_audit.py$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_inspect.py$" "$tar_list"
grep -q "^$package_name/scripts/v4_preview.py$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/skill-plugin-receipts/ios-shipguard-design-audit/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/skill-plugin-receipts/plugin-cache-status/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/skill-plugin-receipts/starter-ui-polish-plan/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/workflow-chain-receipts/report-quality-to-spec-and-next-goal/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/scenario-matrix-receipts/full-public-maintainer-loop/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/scenario-failure-receipts/bad-evidence-blocks/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/scenario-remediation-receipts/blocked-to-repaired-loop/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/adoption-receipts/fresh-package-first-audit/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/target-onboarding-receipts/fresh-ios-target-first-plan/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/multi-profile-onboarding-receipts/all-starter-profiles-init-doctor/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/profile-native-first-audit-receipts/web-backend-cli-first-audits/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/profile-native-fix-plan-receipts/web-backend-cli-fix-plans/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/profile-native-validation-receipts/web-backend-cli-validation-receipts/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/profile-native-validation-rerun-receipts/web-backend-cli-validation-rerun-receipts/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/profile-native-proof-handoff-receipts/web-backend-cli-proof-handoffs/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/command-family-runtime-output-receipts/major-family-report-outputs/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/trust-hardening-receipts/action-devspace-archive-release-provenance/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/task-contract-receipts/prepare-verify-proof-gate/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/external-pilot-verdict-bench-receipts/public-verdict-traces/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/domain-pack-sdk-receipts/synthetic-pack-extension/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/configuration-baseline-receipts/accepted-expired-regression/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/structured-evidence-receipts/v2-compatibility-freshness-downgrade/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/agent-adapter-receipts/codex-task-trace-adapter/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/xcodebuildmcp-evidence-receipts/simulator-build-ui-profiler-adapter/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/expo-eas-assurance-receipts/expo-prebuild-eas-runtime-adapter/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/universal-agent-packaging-receipts/claude-gemini-cursor-mcp-trace-packaging/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/full-audit-orchestrator-receipts/resumable-release-lane/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/unified-inspect-receipts/proof-state-control-deck/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/concise-verdict-result-ux-receipts/major-report-result-contract/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/codex-marketplace-readiness-receipts/public-marketplace-submission-packet/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/external-benchmark-v2-receipts/public-comparative-verdicts/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/tool-value-gauntlet/v4-preview-stabilization-receipts/preview-contract/receipt.json$" "$tar_list"
grep -q "^$package_name/fixtures/external-pilot-verdict-bench/notification-permission-review/trace.json$" "$tar_list"
grep -q "^$package_name/fixtures/external-pilot-verdict-bench/protected-scope-overclaim/trace.json$" "$tar_list"
grep -q "^$package_name/fixtures/external-benchmark-v2/comparative-permission-proof/trace.json$" "$tar_list"
grep -q "^$package_name/scripts/ios_launchdeck.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_codex_handoff.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_devspace_check.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_design.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_doctor.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_goal_loop.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_inventory.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_modernize.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_plan.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_performance.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_preview.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_prove.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_redaction.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_report_quality.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_scan_scope.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_shareable.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_spec_workflow.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_shipguard_demo.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_shipguard_eval.py$" "$tar_list"
grep -q "^$package_name/scripts/ios_target_match.py$" "$tar_list"
grep -q "^$package_name/scripts/lib/safe_paths.sh$" "$tar_list"
grep -q "^$package_name/scripts/shipguard_devspace_mcp.py$" "$tar_list"
grep -q "^$package_name/scripts/leaderboard_build.sh$" "$tar_list"
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
grep -q "^$package_name/tests/codex_status_test.sh$" "$tar_list"
grep -q "^$package_name/tests/codex_marketplace_readiness_test.sh$" "$tar_list"
grep -q "^$package_name/tests/docs_check_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_ai_readiness_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_app_intelligence_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_branding_test.sh$" "$tar_list"
grep -q "^$package_name/tests/tool_value_gauntlet_test.sh$" "$tar_list"
grep -q "^$package_name/tests/full_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/inspect_test.sh$" "$tar_list"
grep -q "^$package_name/tests/v4_preview_test.sh$" "$tar_list"
grep -q "^$package_name/tests/concise_verdict_result_ux_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_launchdeck_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_codex_handoff_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_devspace_check_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_design_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_doctor_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_external_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_goal_loop_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_inventory_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_modernize_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_plan_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_performance_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_preview_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_prove_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_redaction_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_report_quality_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_spec_workflow_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_shipguard_demo_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_shipguard_eval_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_target_match_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ios_target_risk_map_test.sh$" "$tar_list"
grep -q "^$package_name/tests/leaderboard_test.sh$" "$tar_list"
grep -q "^$package_name/tests/next_goal_test.sh$" "$tar_list"
grep -q "^$package_name/tests/policy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/profile_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/profile_fix_plan_test.sh$" "$tar_list"
grep -q "^$package_name/tests/profile_validation_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/profile_validation_rerun_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/profile_proof_handoff_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/command_family_runtime_output_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/trust_hardening_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/domain_pack_sdk_test.sh$" "$tar_list"
grep -q "^$package_name/tests/configuration_baseline_test.sh$" "$tar_list"
grep -q "^$package_name/tests/task_contract_test.sh$" "$tar_list"
grep -q "^$package_name/tests/task_contract_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/structured_evidence_receipts_test.sh$" "$tar_list"
grep -q "^$package_name/tests/agent_trace_test.sh$" "$tar_list"
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
grep -q "^$package_name/tests/sarif_test.sh$" "$tar_list"
grep -q "^$package_name/tests/self_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/safe_paths_test.sh$" "$tar_list"
grep -q "^$package_name/tests/shipguard_devspace_mcp_test.sh$" "$tar_list"
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
grep -q "^$package_name/fixtures/policy/strict.conf$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoShipGuardApp.xcodeproj/project.pbxproj$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoShipGuardApp.xcodeproj/xcshareddata/xcschemes/DemoShipGuardApp.xcscheme$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoShipGuardApp.xctestplan$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoShipGuardApp.xcworkspace/contents.xcworkspacedata$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/DemoProducts.storekit$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/PrivacyInfo.xcprivacy$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoShipGuardApp/DemoPermissions.swift$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoShipGuardApp/DemoShipGuardApp.entitlements$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Sources/DemoShipGuardApp/Info.plist$" "$tar_list"
grep -q "^$package_name/fixtures/demo-ios-repo/Tests/DemoShipGuardAppTests/DemoPermissionsTests.swift$" "$tar_list"
grep -q "^$package_name/fixtures/arena/good-maintainer/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/cli-dangerous-clean/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/docs-release-proof-drift/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/release-asset-trust-bypass/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/release-asset-trust-bypass/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/release-asset-trust-bypass/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/security-token-leakage/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/security-token-leakage/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/security-token-leakage/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/data-migration-loss-regression/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/data-migration-loss-regression/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/data-migration-loss-regression/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/storekit-entitlement-regression/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/storekit-entitlement-regression/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/storekit-entitlement-regression/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/frontend-async-state-regression/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/generated-artifact-cleanup-bypass/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/generated-artifact-cleanup-bypass/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/generated-artifact-cleanup-bypass/task.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/github-posting-without-dry-run/diff.patch$" "$tar_list"
grep -q "^$package_name/fixtures/arena/github-posting-without-dry-run/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/github-posting-without-dry-run/task.md$" "$tar_list"
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
grep -q "^$package_name/evals/README.md$" "$tar_list"
grep -q "^$package_name/evals/cases.jsonl$" "$tar_list"
grep -q "^$package_name/evals/ios_shipguard_cases.jsonl$" "$tar_list"
grep -q "^$package_name/evals/run_local.py$" "$tar_list"

if grep -Eq '(^|/)(\\.git|dist|DerivedData|\\.cache|__pycache__)(/|$)|\\.pyc$' "$tar_list"; then
  echo "package includes forbidden generated or VCS paths" >&2
  exit 1
fi

tar -xzf "$tarball" -C "$tmp_dir"
package_root="$tmp_dir/$package_name"

local_path_pattern="/""Users/[^/[:space:]]+/(Developer|Documents|Desktop|Downloads|Code|Library|Projects|Project|Repositories|repos|src|work|tmp)/"
linux_home_path="/""home/[^/[:space:]]+/(Developer|Documents|Desktop|Downloads|Code|Projects|repositories|repos|src|work|tmp)/"
if grep -RIEq "$local_path_pattern|$linux_home_path|ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}" "$package_root"; then
  echo "package includes a local path or secret-looking token" >&2
  exit 1
fi

test "$("$package_root/bin/shipguard" version)" = "$version"
test "$("$package_root/bin/codex-maintainer" version)" = "$version"
"$package_root/bin/shipguard" policy show >/dev/null
"$package_root/bin/shipguard" prepare --help >/dev/null
"$package_root/bin/shipguard" verify --help >/dev/null
"$package_root/bin/shipguard" validate "$package_root" >/dev/null
"$package_root/bin/shipguard" init ios "$tmp_dir/demo-target" --force >/dev/null
"$package_root/bin/shipguard" doctor "$tmp_dir/demo-target" >/dev/null
"$package_root/bin/shipguard" init web "$tmp_dir/web-target" --force >/dev/null
"$package_root/bin/shipguard" doctor web "$tmp_dir/web-target" >/dev/null
grep -q 'Web ShipGuard Instructions' "$tmp_dir/web-target/AGENTS.md"
"$package_root/bin/shipguard" init backend "$tmp_dir/backend-target" --force >/dev/null
"$package_root/bin/shipguard" doctor backend "$tmp_dir/backend-target" >/dev/null
grep -q 'Backend Service ShipGuard Instructions' "$tmp_dir/backend-target/AGENTS.md"
"$package_root/bin/shipguard" init cli "$tmp_dir/cli-target" --force >/dev/null
"$package_root/bin/shipguard" doctor cli "$tmp_dir/cli-target" >/dev/null
grep -q 'CLI Tool ShipGuard Instructions' "$tmp_dir/cli-target/AGENTS.md"
"$package_root/bin/shipguard" ios demo --out "$tmp_dir/package-ios-demo" >/dev/null
grep -q '"tool": "shipguard ios demo"' "$tmp_dir/package-ios-demo/shipguard-demo.json"
grep -q '"status": "pass"' "$tmp_dir/package-ios-demo/shipguard-demo.json"
grep -q 'codex plugin add ios-shipguard@shipguard' "$tmp_dir/package-ios-demo/README.md"
"$package_root/bin/shipguard" brand --path "$package_root" --out "$tmp_dir/package-brand" --strict >/dev/null
grep -q '"tool": "shipguard brand"' "$tmp_dir/package-brand/ios-branding.json"
grep -q '"status": "pass"' "$tmp_dir/package-brand/ios-branding.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/package-brand/ios-branding.json"
grep -q '"artifactCallsigns":' "$tmp_dir/package-brand/ios-branding.json"
grep -q '"name": "ShipGuard ShipYard"' "$tmp_dir/package-brand/ios-branding.json"
grep -q 'ShipGuard VibeCheck' "$tmp_dir/package-brand/ios-branding.md"
grep -q 'ShipGuard PluginRadar' "$tmp_dir/package-brand/ios-branding.md"
grep -q 'ShipGuard ShipYard' "$tmp_dir/package-brand/ios-branding.md"
grep -q 'Nitty-Gritty Call Signs' "$tmp_dir/package-brand/ios-branding.md"
grep -q 'Engine Tapes' "$tmp_dir/package-brand/ios-branding.md"
"$package_root/bin/shipguard" pilot-bench \
  --trace "$package_root/fixtures/external-pilot-verdict-bench" \
  --out "$tmp_dir/package-pilot-bench" \
  --shareable >/dev/null
grep -q '"tool": "shipguard pilot-bench"' "$tmp_dir/package-pilot-bench/pilot-bench.json"
grep -q '"surface": "ShipGuard PilotBench"' "$tmp_dir/package-pilot-bench/pilot-bench.json"
grep -q '"status": "pass"' "$tmp_dir/package-pilot-bench/pilot-bench.json"
grep -q 'firstUsefulVerdictTime' "$tmp_dir/package-pilot-bench/pilot-bench.md"
"$package_root/bin/shipguard" pilot-bench \
  --trace "$package_root/fixtures/external-benchmark-v2" \
  --out "$tmp_dir/package-external-benchmark-v2" \
  --shareable \
  --benchmark-v2 \
  --min-lift 15 >/dev/null
grep -q '"comparativeBenchmark":' "$tmp_dir/package-external-benchmark-v2/pilot-bench.json"
grep -q '"benchmarkVersion": 2' "$tmp_dir/package-external-benchmark-v2/pilot-bench.json"
grep -q 'External Benchmark v2' "$tmp_dir/package-external-benchmark-v2/pilot-bench.md"
"$package_root/bin/shipguard" agent trace --help >/dev/null
"$package_root/bin/shipguard" codex trace --help >/dev/null
"$package_root/bin/shipguard" full-audit --path "$package_root" --out "$tmp_dir/package-full-audit" --stage version --stage py-compile --shipguard-eval --shareable >/dev/null
grep -q '"tool": "shipguard full-audit"' "$tmp_dir/package-full-audit/shipguard-full-audit.json"
grep -q '"status": "pass"' "$tmp_dir/package-full-audit/shipguard-full-audit.json"
grep -q 'ShipGuard Full Audit' "$tmp_dir/package-full-audit/shipguard-full-audit.md"
"$package_root/bin/shipguard" value-gauntlet \
  --path "$package_root" \
  --out "$tmp_dir/package-value-gauntlet" >/dev/null
grep -q '"tool": "shipguard value-gauntlet"' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"surface": "ShipGuard Tool Value Gauntlet"' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"priorityActions":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"taskContractReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"agentAdapterReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"xcodeBuildMCPEvidenceReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"expoEASAssuranceReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"universalAgentPackagingReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q '"externalBenchmarkV2Receipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q 'Domain Pack SDK' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'Agent Adapter Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'XcodeBuildMCP Evidence Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'Expo/EAS Assurance Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'Universal Agent Packaging Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'External Benchmark v2 Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q '"v4PreviewStabilizationReceipts":' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.json"
grep -q 'V4 Preview Stabilization Receipts' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
grep -q 'ShipGuard Tool Value Gauntlet' "$tmp_dir/package-value-gauntlet/tool-value-gauntlet.md"
"$package_root/bin/shipguard" v4 preview \
  --path "$package_root" \
  --out "$tmp_dir/package-v4-preview" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"tool": "shipguard v4 preview"' "$tmp_dir/package-v4-preview/v4-preview.json"
grep -q '"status": "pass"' "$tmp_dir/package-v4-preview/v4-preview.json"
grep -q '"releaseClaim": "not-released"' "$tmp_dir/package-v4-preview/v4-preview.json"
grep -q 'ShipGuard V4 Preview' "$tmp_dir/package-v4-preview/v4-preview.md"
"$package_root/bin/shipguard" inspect \
  --path "$package_root" \
  --out "$tmp_dir/package-inspect" \
  --value-gauntlet "$tmp_dir/package-value-gauntlet" \
  --full-audit "$tmp_dir/package-full-audit" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"tool": "shipguard inspect"' "$tmp_dir/package-inspect/shipguard-inspect.json"
grep -q '"surface": "ShipGuard InspectDeck"' "$tmp_dir/package-inspect/shipguard-inspect.json"
grep -q '"nextAction":' "$tmp_dir/package-inspect/shipguard-inspect.json"
grep -q 'ShipGuard InspectDeck' "$tmp_dir/package-inspect/shipguard-inspect.md"
package_score_output="$("$package_root/bin/shipguard" score "$package_root/examples/scored-run.md")"
printf '%s\n' "$package_score_output" | grep -q 'Total score: 11/12'
printf '%s\n' "$package_score_output" | grep -q 'usable maintainer-quality run'
"$package_root/bin/shipguard" autopsy \
  --run "$package_root/fixtures/autopsy/good-run/run.md" \
  --task "$package_root/fixtures/autopsy/good-run/task.md" \
  --diff "$package_root/fixtures/autopsy/good-run/diff.patch" \
  --tests "$package_root/fixtures/autopsy/good-run/tests.log" \
  --out "$tmp_dir/package-autopsy" >/dev/null
grep -q '"total": 11' "$tmp_dir/package-autopsy/report.json"
grep -q '"verdict": "usable maintainer-quality run"' "$tmp_dir/package-autopsy/report.json"
"$package_root/bin/shipguard" arena run \
  --fixture "$package_root/fixtures/arena" \
  --out "$tmp_dir/package-arena" >/dev/null
grep -q '"case_count": 16' "$tmp_dir/package-arena/results.json"
grep -q '"average_total": 4.69' "$tmp_dir/package-arena/results.json"
grep -q '"high_risk_finding_count": 21' "$tmp_dir/package-arena/results.json"
mkdir -p "$tmp_dir/package-baseline-arena-fixture"
for case_id in \
  backend-webhook-idempotency \
  cli-dangerous-clean \
  dangerous-maintainer \
  data-migration-loss-regression \
  failing-validation \
  generated-artifact-cleanup-bypass \
  github-posting-without-dry-run \
  good-maintainer \
  no-diff-implementation \
  release-asset-trust-bypass \
  review-only \
  security-token-leakage \
  storekit-entitlement-regression \
  weak-maintainer; do
  cp -R "$package_root/fixtures/arena/$case_id" "$tmp_dir/package-baseline-arena-fixture/$case_id"
done
"$package_root/bin/shipguard" arena run \
  --fixture "$tmp_dir/package-baseline-arena-fixture" \
  --out "$tmp_dir/package-old-arena" >/dev/null
"$package_root/bin/shipguard" arena compare \
  --left "$tmp_dir/package-old-arena/results.json" \
  --right "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-arena-compare" >/dev/null
grep -q '"status" : "improved"' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"average_total_delta" : 0.76' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"id" : "docs-release-proof-drift"' "$tmp_dir/package-arena-compare/arena-compare.json"
grep -q '"id" : "frontend-async-state-regression"' "$tmp_dir/package-arena-compare/arena-compare.json"
"$package_root/bin/shipguard" arena import \
  --source "$package_root/fixtures/external-arena-pack" \
  --out "$tmp_dir/package-imported-arena" \
  --pack-name "package-imported" >/dev/null
grep -q 'Pack: package-imported' "$tmp_dir/package-imported-arena/PACK.md"
grep -q 'Source: external-arena-pack' "$tmp_dir/package-imported-arena/PACK.md"
if grep -q "$package_root" "$tmp_dir/package-imported-arena/PACK.md"; then
  echo "package imported PACK.md should not include local package path" >&2
  exit 1
fi
"$package_root/bin/shipguard" arena run \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-results" >/dev/null
grep -q '"case_count": 2' "$tmp_dir/package-imported-results/results.json"
"$package_root/bin/shipguard" arena sign \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-arena/PACK.json" \
  --pack-name "package-imported" \
  --signer "Package Fixture Maintainer" \
  --signer-url "https://github.com/jlekerli-source/ShipGuard" >/dev/null
grep -q '"signature_type" : "sha256-content-digest"' "$tmp_dir/package-imported-arena/PACK.json"
grep -q '"signer" : "Package Fixture Maintainer"' "$tmp_dir/package-imported-arena/PACK.json"
grep -q '"identity_digest" : "[a-f0-9]\{64\}"' "$tmp_dir/package-imported-arena/PACK.json"
"$package_root/bin/shipguard" arena verify \
  --fixture "$tmp_dir/package-imported-arena" \
  --manifest "$tmp_dir/package-imported-arena/PACK.json" >/dev/null
"$package_root/bin/shipguard" review-comment \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-review/comment.md" \
  --badge "$tmp_dir/package-review/badge.json" \
  --artifact-dir "$tmp_dir/package-review" >/dev/null
grep -q '| Status | pass |' "$tmp_dir/package-review/comment.md"
grep -q '"message": "pass 11/12"' "$tmp_dir/package-review/badge.json"
"$package_root/bin/shipguard" ci-gate \
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
"$package_root/bin/shipguard" docs-check "$package_root" --out "$tmp_dir/package-docs-check" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-docs-check/docs-check.json"
grep -q '"broken_count" : 0' "$tmp_dir/package-docs-check/docs-check.json"
package_empty_codex_status="$("$package_root/bin/shipguard" codex status --cache "$tmp_dir/empty-codex-cache")"
printf '%s\n' "$package_empty_codex_status" | grep -q 'Overall status: missing'
printf '%s\n' "$package_empty_codex_status" | grep -q '## Refresh Handoff'
printf '%s\n' "$package_empty_codex_status" | grep -q 'pushing or pulling the repository updates source only'
package_plugin_version="$(python3 - "$package_root/plugins/ios-shipguard/.codex-plugin/plugin.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as handle:
    print(json.load(handle)["version"])
PY
)"
package_plugin_cache="$tmp_dir/package-codex-cache/shipguard/ios-shipguard/$package_plugin_version"
mkdir -p "$(dirname "$package_plugin_cache")"
cp -R "$package_root/plugins/ios-shipguard" "$package_plugin_cache"
package_codex_status="$(env -u SHIPGUARD_CLI HOME="$tmp_dir/package-home" PATH="/usr/bin:/bin:/usr/sbin:/sbin" "$package_root/bin/shipguard" codex status --cache "$tmp_dir/package-codex-cache" --strict)"
printf '%s\n' "$package_codex_status" | grep -q 'Overall status: pass'
printf '%s\n' "$package_codex_status" | grep -Fq "Resolved ShipGuard CLI for MCP/status: $package_root/bin/shipguard"
printf '%s\n' "$package_codex_status" | grep -q 'codex plugin add ios-shipguard@shipguard'
env -u SHIPGUARD_CLI HOME="$tmp_dir/package-home" "$package_root/bin/shipguard" codex marketplace-readiness \
  --path "$package_root" \
  --out "$tmp_dir/package-marketplace-readiness" \
  --cache "$tmp_dir/package-codex-cache" \
  --strict \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-marketplace-readiness/codex-marketplace-readiness.json"
grep -q '"surface": "ShipGuard MarketplaceDeck"' "$tmp_dir/package-marketplace-readiness/codex-marketplace-readiness.json"
grep -q '# ShipGuard Codex Marketplace Readiness' "$tmp_dir/package-marketplace-readiness/codex-marketplace-readiness.md"
grep -q 'codex plugin add ios-shipguard@shipguard' "$tmp_dir/package-marketplace-readiness/codex-marketplace-readiness.md"
"$package_root/bin/shipguard" ci-summary \
  --gate "$tmp_dir/package-gate/gate.json" \
  --out "$tmp_dir/package-summary.md" >/dev/null
grep -q '| Score | 11/12 |' "$tmp_dir/package-summary.md"
"$package_root/bin/shipguard" check-run \
  --gate "$tmp_dir/package-gate/gate.json" \
  --head-sha 0123456789abcdef \
  --out "$tmp_dir/package-check-run/payload.json" >/dev/null
grep -q '"conclusion" : "success"' "$tmp_dir/package-check-run/payload.json"
grep -q '"head_sha" : "0123456789abcdef"' "$tmp_dir/package-check-run/payload.json"
"$package_root/bin/shipguard" check-run post \
  --payload "$tmp_dir/package-check-run/payload.json" \
  --repo owner/repo \
  --out "$tmp_dir/package-check-run/dry-run.json" \
  --dry-run >/dev/null
grep -q '"dry_run" : true' "$tmp_dir/package-check-run/dry-run.json"
grep -q '"url" : "https://api.github.com/repos/owner/repo/check-runs"' "$tmp_dir/package-check-run/dry-run.json"
"$package_root/bin/shipguard" leaderboard build \
  --arena-results "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-leaderboard.json" >/dev/null
grep -q '"schema_version": "1.0"' "$tmp_dir/package-leaderboard.json"
grep -q '"average_total": 4.69' "$tmp_dir/package-leaderboard.json"
"$package_root/bin/shipguard" release-manifest \
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
"$package_root/bin/shipguard" release-manifest verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --version "$version" \
  --tag "v$version" >/dev/null
"$package_root/bin/shipguard" release-index build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --out "$tmp_dir/package-release-index" >/dev/null
grep -q '"release_count" : 1' "$tmp_dir/package-release-index/release-index.json"
grep -q '| '"$version"' | v'"$version"' | 0123456789ab | shipguard-v'"$version"'.tar.gz |' "$tmp_dir/package-release-index/release-index.md"
"$package_root/bin/shipguard" release-replay verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --index "$tmp_dir/package-release-index/release-index.json" \
  --ledger "$tmp_dir/package-release-proof/proof-ledger.md" \
  --out "$tmp_dir/package-release-replay" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '"name": "artifact sha256"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '# Release Replay Report' "$tmp_dir/package-release-replay/replay-report.md"
"$package_root/bin/shipguard" release-attest build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --replay "$tmp_dir/package-release-replay/replay-report.json" \
  --out "$tmp_dir/package-release-attestation" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-attestation/attestation-badge.json"
grep -q '# ShipGuard Release Attestation' "$tmp_dir/package-release-attestation/attestation.md"
"$package_root/bin/shipguard" release-proof build \
  --out "$tmp_dir/package-release-proof-bundle" \
  --version "$version" \
  --tag "v$version" \
  --commit 0123456789abcdef \
  --ci-run-url "https://github.com/example/repo/actions/runs/123" \
  --release-url "https://github.com/example/repo/releases/tag/v$version" \
  --issue-url "https://github.com/example/repo/issues/99" >/dev/null
test -f "$tmp_dir/package-release-proof-bundle/shipguard-v$version.tar.gz"
grep -q '"status": "pass"' "$tmp_dir/package-release-proof-bundle/replay/replay-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-proof-bundle/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json"
mkdir -p "$tmp_dir/package-release-consume-assets"
cp "$tmp_dir/package-release-proof-bundle/shipguard-v$version.tar.gz" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/release-manifest.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/index/release-index.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/proof-ledger.md" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/replay/replay-report.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json" "$tmp_dir/package-release-consume-assets/"
"$package_root/bin/shipguard" release-consume verify \
  --dir "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-consume" \
  --version "$version" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_blocked": 0' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_report": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"attestation_badge": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"asset_digest_matrix": "asset-digests.json"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q "| shipguard-v$version.tar.gz | release tarball | true | present |" "$tmp_dir/package-release-consume/asset-digests.md"
grep -q '"name": "attestation-badge.json"' "$tmp_dir/package-release-consume/asset-digests.json"
"$package_root/bin/shipguard" release-diff compare \
  --left "$tmp_dir/package-release-proof-bundle" \
  --right "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-diff" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-diff/release-diff.json"
grep -q '# Release Diff Audit' "$tmp_dir/package-release-diff/release-diff.md"
"$package_root/bin/shipguard" release-evidence site \
  --consume "$tmp_dir/package-release-consume" \
  --diff "$tmp_dir/package-release-diff" \
  --out "$tmp_dir/package-release-site" >/dev/null
test -f "$tmp_dir/package-release-site/index.html"
test -f "$tmp_dir/package-release-site/evidence.json"
test -f "$tmp_dir/package-release-site/sources/consumer-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-site/evidence.json"
grep -q 'Asset Digest Matrix' "$tmp_dir/package-release-site/index.html"
"$package_root/bin/shipguard" release-evidence index \
  --site "$tmp_dir/package-release-site" \
  --out "$tmp_dir/package-release-evidence-index" >/dev/null
test -f "$tmp_dir/package-release-evidence-index/index.html"
test -f "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q 'Machine-readable index' "$tmp_dir/package-release-evidence-index/index.html"
"$package_root/bin/shipguard" release-evidence bundle \
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
"$package_root/bin/shipguard" release-evidence verify \
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
"$package_root/bin/shipguard" release-evidence negative-index \
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
"$package_root/tests/profile_audit_test.sh" >/dev/null
"$package_root/tests/profile_fix_plan_test.sh" >/dev/null
"$package_root/tests/profile_validation_receipts_test.sh" >/dev/null
"$package_root/tests/profile_validation_rerun_receipts_test.sh" >/dev/null
"$package_root/tests/profile_proof_handoff_receipts_test.sh" >/dev/null
"$package_root/tests/command_family_runtime_output_receipts_test.sh" >/dev/null
"$package_root/tests/trust_hardening_receipts_test.sh" >/dev/null
"$package_root/tests/domain_pack_sdk_test.sh" >/dev/null
"$package_root/tests/configuration_baseline_test.sh" >/dev/null
"$package_root/tests/task_contract_test.sh" >/dev/null
"$package_root/tests/task_contract_receipts_test.sh" >/dev/null
"$package_root/tests/structured_evidence_receipts_test.sh" >/dev/null
"$package_root/tests/agent_trace_test.sh" >/dev/null
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
"$package_root/bin/shipguard" transcript redact \
  --in "$package_raw_transcript" \
  --out "$tmp_dir/package-redacted-transcript.md" \
  --report "$tmp_dir/package-redaction-report.json" \
  --private-term "AcmePrivateApp" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-redaction-report.json"
grep -q '\[redacted-private-term\]' "$tmp_dir/package-redacted-transcript.md"
grep -q "$package_home_prefix/\\[redacted-user\\]" "$tmp_dir/package-redacted-transcript.md"
grep -q '\[redacted-email\]' "$tmp_dir/package-redacted-transcript.md"
grep -q 'API_TOKEN=\[redacted-secret\]' "$tmp_dir/package-redacted-transcript.md"
"$package_root/bin/shipguard" transcript verify \
  --in "$tmp_dir/package-redacted-transcript.md" \
  --report "$tmp_dir/package-redaction-report.json" \
  --out "$tmp_dir/package-transcript-verify" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-transcript-verify/transcript-verify.json"
grep -q '"message" : "pass"' "$tmp_dir/package-transcript-verify/badge.json"
"$package_root/bin/shipguard" transcript corpus \
  --source "$package_root/fixtures/transcripts" \
  --out "$tmp_dir/package-transcript-corpus" \
  --require-report true >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-transcript-corpus/corpus.json"
grep -q '"case_count": 4' "$tmp_dir/package-transcript-corpus/corpus.json"
grep -q '"message": "pass 4/4"' "$tmp_dir/package-transcript-corpus/badge.json"
"$package_root/bin/shipguard" self-audit \
  --out "$tmp_dir/package-self-audit" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-self-audit/self-audit.json"
grep -q '| shipguard web audit --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard web plan --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard backend audit --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard backend plan --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard cli audit --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard cli plan --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard transcript redact --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard transcript verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard transcript corpus --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard arena compare --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/arena-compare/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard leaderboard build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-attest build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-proof build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-index build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-manifest --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-manifest verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-replay verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-consume verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-diff compare --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-evidence site --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-evidence index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-evidence bundle --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-evidence verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard release-evidence negative-index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard docs-check --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard inspect --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard v4 preview --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios doctor --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios inventory --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios preview --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios devspace --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios devspace-check --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios target-match --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios codex-handoff --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios plan --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios prove --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios launchdeck --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios performance --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios design --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios modernize --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios app-intelligence --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios ai-readiness --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard pilot-bench --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard agent trace --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios external-audit --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios spec-workflow --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios report-quality --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios redact --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios eval --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios demo --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard ios goals --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard codex status --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard codex marketplace-readiness --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| shipguard codex trace --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| .agents/plugins/marketplace.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| NEXT_GOAL.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/.codex-plugin/plugin.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/.mcp.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/skills/ios-shipguard/SKILL.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/skills/ios-shipguard/agents/openai.yaml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| plugins/ios-shipguard/skills/ios-shipguard/references/modes.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-consume/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-diff/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-negative-index/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-verify/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-proof/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/transcript-corpus/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/transcript-verify/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/arena-compare-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/agent-trace.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/full-audit.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/inspect.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/v4-preview.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/codex-status.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/codex-marketplace-readiness.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/ios-preview.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/ios-shipguard.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/shipguard-devspace.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
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
grep -q '| docs/oss-evaluation.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/product-strategy.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/security-threat-model.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/task-contract.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-proof-on-tag.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/arena-compare.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
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
grep -q '| fixtures/tool-value-gauntlet/scenario-remediation-receipts/blocked-to-repaired-loop/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/adoption-receipts/fresh-package-first-audit/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/target-onboarding-receipts/fresh-ios-target-first-plan/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/multi-profile-onboarding-receipts/all-starter-profiles-init-doctor/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/profile-native-first-audit-receipts/web-backend-cli-first-audits/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/profile-native-fix-plan-receipts/web-backend-cli-fix-plans/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/ios-devspace/complete-preview/handoff.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/ios-devspace/complete-preview/handoff.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/demo-reports/transcripts/corpus.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/docs-check.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/release-proof-consumption-checklist.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/redacted-transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/transcripts/ios-notification-triage/transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/transcripts/release-evidence-consumption/transcript.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_redact.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_verify.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/transcript_corpus.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/docs_check.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/profile_audit.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/profile_fix_plan.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/task_domain_packs.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/task_contract.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_receipts.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_baseline.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/agent_trace.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/codex_marketplace_readiness.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_result.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/full_audit.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_inspect.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/v4_preview.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_doctor.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_inventory.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_launchdeck.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_performance.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_devspace_check.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_design.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_report_quality.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_scan_scope.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_shareable.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_spec_workflow.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/ios_shipguard_demo.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/shipguard_devspace_mcp.py | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| scripts/codex_status.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/profile_audit_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/profile_fix_plan_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/profile_validation_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/profile_validation_rerun_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/profile_proof_handoff_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/command_family_runtime_output_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/trust_hardening_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/domain_pack_sdk_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/configuration_baseline_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/task_contract_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/task_contract_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/structured_evidence_receipts_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/agent_trace_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/external_pilot_verdict_bench_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/full_audit_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/inspect_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/v4_preview_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| tests/concise_verdict_result_ux_test.sh | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/profile-native-validation-receipts/web-backend-cli-validation-receipts/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/profile-native-validation-rerun-receipts/web-backend-cli-validation-rerun-receipts/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/profile-native-proof-handoff-receipts/web-backend-cli-proof-handoffs/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/command-family-runtime-output-receipts/major-family-report-outputs/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/trust-hardening-receipts/action-devspace-archive-release-provenance/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/task-contract-receipts/prepare-verify-proof-gate/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/external-pilot-verdict-bench-receipts/public-verdict-traces/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/domain-pack-sdk-receipts/synthetic-pack-extension/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/configuration-baseline-receipts/accepted-expired-regression/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/structured-evidence-receipts/v2-compatibility-freshness-downgrade/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/agent-adapter-receipts/codex-task-trace-adapter/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/xcodebuildmcp-evidence-receipts/simulator-build-ui-profiler-adapter/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/expo-eas-assurance-receipts/expo-prebuild-eas-runtime-adapter/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/universal-agent-packaging-receipts/claude-gemini-cursor-mcp-trace-packaging/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/full-audit-orchestrator-receipts/resumable-release-lane/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/unified-inspect-receipts/proof-state-control-deck/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/concise-verdict-result-ux-receipts/major-report-result-contract/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/codex-marketplace-readiness-receipts/public-marketplace-submission-packet/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/external-benchmark-v2-receipts/public-comparative-verdicts/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/tool-value-gauntlet/v4-preview-stabilization-receipts/preview-contract/receipt.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/external-pilot-verdict-bench/notification-permission-review/trace.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/external-pilot-verdict-bench/protected-scope-overclaim/trace.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/external-benchmark-v2/comparative-permission-proof/trace.json | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q 'shipguard web audit' "$package_root/docs/cli.md"
grep -q 'shipguard web plan' "$package_root/docs/cli.md"
grep -q 'shipguard backend audit' "$package_root/docs/cli.md"
grep -q 'shipguard backend plan' "$package_root/docs/cli.md"
grep -q 'shipguard cli audit' "$package_root/docs/cli.md"
grep -q 'shipguard cli plan' "$package_root/docs/cli.md"
"$package_root/bin/shipguard" sarif \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-sarif/results.sarif" >/dev/null
grep -q '"version" : "2.1.0"' "$tmp_dir/package-sarif/results.sarif"
"$package_root/bin/shipguard" next-goal \
  --release 2.6.0 \
  --title "Package Proof Followup" \
  --out "$tmp_dir/package-next-goal.md" >/dev/null
grep -q '/plan v2.6.0 Package Proof Followup' "$tmp_dir/package-next-goal.md"
grep -q 'Pick exactly one high-signal maintainer reliability improvement from ROADMAP.md' "$tmp_dir/package-next-goal.md"
grep -q '/goal Implement v2.6.0 Package Proof Followup' "$tmp_dir/package-next-goal.md"
grep -q 'follow the /plan above' "$tmp_dir/package-next-goal.md"
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
grep -q './bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet' "$tmp_dir/package-next-goal.md"
grep -q './tests/profile_audit_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/profile_fix_plan_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/profile_validation_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/profile_validation_rerun_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/profile_proof_handoff_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/command_family_runtime_output_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/trust_hardening_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/task_contract_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/task_contract_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/structured_evidence_receipts_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/tool_value_gauntlet_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/concise_verdict_result_ux_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_launchdeck_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_performance_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_devspace_check_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_design_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_modernize_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_app_intelligence_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_ai_readiness_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_spec_workflow_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_report_quality_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ios_shipguard_eval_test.sh' "$tmp_dir/package-next-goal.md"
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
"$package_root/bin/shipguard" next-goal \
  --release 2.6.0 \
  --title "Scoped Package Proof Followup" \
  --scope "Make package next-goal proof emit scoped completion receipts." \
  --completion-evidence "package release test passed" \
  --following-title "Package Followup Two" \
  --out "$tmp_dir/package-scoped-next-goal.md" >/dev/null
grep -q '/plan v2.6.0 Scoped Package Proof Followup' "$tmp_dir/package-scoped-next-goal.md"
grep -q 'Implement this bounded improvement: Make package next-goal proof emit scoped completion receipts.' "$tmp_dir/package-scoped-next-goal.md"
grep -q '## Completion Receipt' "$tmp_dir/package-scoped-next-goal.md"
grep -q 'Evidence: package release test passed' "$tmp_dir/package-scoped-next-goal.md"
grep -q '## Following Slash Plan' "$tmp_dir/package-scoped-next-goal.md"
grep -q '/plan v2.7.0 Package Followup Two' "$tmp_dir/package-scoped-next-goal.md"
grep -q 'latest read-only ShipGuard product-QA evidence' "$tmp_dir/package-scoped-next-goal.md"
grep -q '/goal Implement v2.7.0 Package Followup Two' "$tmp_dir/package-scoped-next-goal.md"
grep -q 'following /plan above' "$tmp_dir/package-scoped-next-goal.md"
grep -q './bin/shipguard next-goal --release 2.7.0 --title "Package Followup Two" --out NEXT_GOAL.md' "$tmp_dir/package-scoped-next-goal.md"

install_prefix="$tmp_dir/install"
mkdir -p "$package_root/scripts/__pycache__" "$package_root/dist" "$package_root/.git"
printf 'bytecode sentinel\n' > "$package_root/scripts/__pycache__/install_sentinel.pyc"
printf 'dist sentinel\n' > "$package_root/dist/install-sentinel.tmp"
printf 'git sentinel\n' > "$package_root/.git/HEAD"
PREFIX="$install_prefix" "$package_root/scripts/install.sh" >/dev/null
test "$("$install_prefix/bin/shipguard" version)" = "$version"
test "$("$install_prefix/bin/codex-maintainer" version)" = "$version"
if find "$install_prefix/lib/shipguard" \
  \( -name '.git' -o -name 'dist' -o -name '.DS_Store' -o -name '.cache' -o -name 'DerivedData' -o -name '__pycache__' -o -name '*.pyc' \) \
  -print -quit | grep -q .; then
  echo "installed toolkit includes forbidden generated or VCS paths" >&2
  exit 1
fi

echo "package release tests passed"
