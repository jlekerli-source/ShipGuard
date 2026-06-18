#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
shipguard self-audit

Usage:
  shipguard self-audit [--out <dir>]

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
generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}}"

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
  "docs-check --help"
  "brand --help"
  "value-gauntlet --help"
  "prepare --help"
  "verify --help"
  "web audit --help"
  "web plan --help"
  "backend audit --help"
  "backend plan --help"
  "cli audit --help"
  "cli plan --help"
  "pilot-bench --help"
  "score examples/scored-run.md"
  "ios doctor --help"
  "ios inventory --help"
  "ios preview --help"
  "ios devspace --help"
  "ios devspace-check --help"
  "ios brand --help"
  "ios target-match --help"
  "ios codex-handoff --help"
  "ios plan --help"
  "ios prove --help"
  "ios launchdeck --help"
  "ios performance --help"
  "ios design --help"
  "ios modernize --help"
  "ios app-intelligence --help"
  "ios ai-readiness --help"
  "ios external-audit --help"
  "ios spec-workflow --help"
  "ios report-quality --help"
  "ios redact --help"
  "ios eval --help"
  "ios demo --help"
  "ios goals --help"
  "codex status --help"
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
  if "$tool_root/bin/shipguard" $command >/dev/null; then
    command_count=$((command_count + 1))
  else
    missing=1
  fi
done

required_artifacts=(
  "README.md"
  "NEXT_GOAL.md"
  "LICENSE"
  "CODE_OF_CONDUCT.md"
  "CONTRIBUTING.md"
  "GOVERNANCE.md"
  "SECURITY.md"
  "SUPPORT.md"
  ".github/ISSUE_TEMPLATE/config.yml"
  ".github/ISSUE_TEMPLATE/workflow-gap.yml"
  ".github/ISSUE_TEMPLATE/bug-report.yml"
  ".github/ISSUE_TEMPLATE/proposal.yml"
  "templates/policy/default.conf"
  ".agents/plugins/marketplace.json"
  "actions/arena-compare/action.yml"
  "plugins/ios-shipguard/.codex-plugin/plugin.json"
  "plugins/ios-shipguard/.mcp.json"
  "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md"
  "plugins/ios-shipguard/skills/ios-shipguard/agents/openai.yaml"
  "plugins/ios-shipguard/skills/ios-shipguard/references/modes.md"
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
  "examples/demo-reports/transcripts/corpus.json"
  "examples/demo-reports/transcripts/index.md"
  "docs/next-goal.md"
  "docs/arena-compare-action.md"
  "docs/sarif.md"
  "docs/docs-check.md"
  "docs/ci-summary.md"
  "docs/check-run.md"
  "docs/codex-status.md"
  "docs/compatibility.md"
  "docs/shipguard-naming.md"
  "docs/ios-preview.md"
  "docs/ios-shipguard.md"
  "docs/shipguard-devspace.md"
  "docs/task-contract.md"
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
  "docs/oss-evaluation.md"
  "docs/open-source.md"
  "docs/privacy.md"
  "docs/product-strategy.md"
  "docs/security-threat-model.md"
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
  "fixtures/transcripts/release-evidence-consumption/transcript.md"
  "templates/web/AGENTS.md"
  "templates/backend/AGENTS.md"
  "templates/cli/AGENTS.md"
  "fixtures/external-arena-pack/imported-clean/run.md"
  "fixtures/arena/generated-artifact-cleanup-bypass/run.md"
  "fixtures/arena/github-posting-without-dry-run/run.md"
  "fixtures/arena/release-asset-trust-bypass/run.md"
  "fixtures/arena/security-token-leakage/run.md"
  "fixtures/arena/data-migration-loss-regression/run.md"
  "fixtures/arena/storekit-entitlement-regression/run.md"
  "fixtures/ios-devspace/complete-preview/session.json"
  "fixtures/ios-devspace/complete-preview/handoff.json"
  "fixtures/ios-devspace/complete-preview/handoff.md"
  "fixtures/ios-devspace/complete-preview/preview-events.jsonl"
  "fixtures/release-evidence/negative/README.md"
  "fixtures/release-evidence/negative/cases.tsv"
  "fixtures/tool-value-gauntlet/runtime-output/decorative-empty-report/fixture.json"
  "fixtures/tool-value-gauntlet/runtime-output/decorative-empty-report/report.json"
  "fixtures/tool-value-gauntlet/runtime-output/decorative-empty-report/report.md"
  "fixtures/tool-value-gauntlet/runtime-output/boundaryless-design-report/fixture.json"
  "fixtures/tool-value-gauntlet/runtime-output/boundaryless-design-report/report.json"
  "fixtures/tool-value-gauntlet/runtime-output/boundaryless-design-report/report.md"
  "fixtures/tool-value-gauntlet/skill-plugin-receipts/ios-shipguard-design-audit/receipt.json"
  "fixtures/tool-value-gauntlet/skill-plugin-receipts/plugin-cache-status/receipt.json"
  "fixtures/tool-value-gauntlet/skill-plugin-receipts/starter-ui-polish-plan/receipt.json"
  "fixtures/tool-value-gauntlet/workflow-chain-receipts/report-quality-to-spec-and-next-goal/receipt.json"
  "fixtures/tool-value-gauntlet/scenario-matrix-receipts/full-public-maintainer-loop/receipt.json"
  "fixtures/tool-value-gauntlet/scenario-failure-receipts/bad-evidence-blocks/receipt.json"
  "fixtures/tool-value-gauntlet/scenario-remediation-receipts/blocked-to-repaired-loop/receipt.json"
  "fixtures/tool-value-gauntlet/adoption-receipts/fresh-package-first-audit/receipt.json"
  "fixtures/tool-value-gauntlet/target-onboarding-receipts/fresh-ios-target-first-plan/receipt.json"
  "fixtures/tool-value-gauntlet/multi-profile-onboarding-receipts/all-starter-profiles-init-doctor/receipt.json"
  "fixtures/tool-value-gauntlet/profile-native-first-audit-receipts/web-backend-cli-first-audits/receipt.json"
  "fixtures/tool-value-gauntlet/profile-native-fix-plan-receipts/web-backend-cli-fix-plans/receipt.json"
  "fixtures/tool-value-gauntlet/profile-native-validation-receipts/web-backend-cli-validation-receipts/receipt.json"
  "fixtures/tool-value-gauntlet/profile-native-validation-rerun-receipts/web-backend-cli-validation-rerun-receipts/receipt.json"
  "fixtures/tool-value-gauntlet/profile-native-proof-handoff-receipts/web-backend-cli-proof-handoffs/receipt.json"
  "fixtures/tool-value-gauntlet/command-family-runtime-output-receipts/major-family-report-outputs/receipt.json"
  "fixtures/tool-value-gauntlet/trust-hardening-receipts/action-devspace-archive-release-provenance/receipt.json"
  "fixtures/tool-value-gauntlet/task-contract-receipts/prepare-verify-proof-gate/receipt.json"
  "fixtures/tool-value-gauntlet/external-pilot-verdict-bench-receipts/public-verdict-traces/receipt.json"
  "fixtures/external-pilot-verdict-bench/notification-permission-review/trace.json"
  "fixtures/external-pilot-verdict-bench/protected-scope-overclaim/trace.json"
  "fixtures/demo-ios-repo/DemoShipGuardApp.xcodeproj/project.pbxproj"
  "fixtures/demo-ios-repo/DemoShipGuardApp.xcodeproj/xcshareddata/xcschemes/DemoShipGuardApp.xcscheme"
  "fixtures/demo-ios-repo/DemoShipGuardApp.xctestplan"
  "fixtures/demo-ios-repo/DemoShipGuardApp.xcworkspace/contents.xcworkspacedata"
  "fixtures/demo-ios-repo/DemoProducts.storekit"
  "fixtures/demo-ios-repo/PrivacyInfo.xcprivacy"
  "fixtures/demo-ios-repo/Sources/DemoShipGuardApp/DemoPermissions.swift"
  "fixtures/demo-ios-repo/Sources/DemoShipGuardApp/DemoShipGuardApp.entitlements"
  "fixtures/demo-ios-repo/Sources/DemoShipGuardApp/Info.plist"
  "fixtures/demo-ios-repo/Tests/DemoShipGuardAppTests/DemoPermissionsTests.swift"
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
  "scripts/docs_check.sh"
  "scripts/ios_ai_readiness.py"
  "scripts/ios_app_intelligence.py"
  "scripts/ios_branding.py"
  "scripts/profile_audit.py"
  "scripts/profile_fix_plan.py"
  "scripts/task_contract.py"
  "scripts/external_pilot_verdict_bench.py"
  "scripts/tool_value_gauntlet.py"
  "scripts/ios_launchdeck.py"
  "scripts/ios_codex_handoff.py"
  "scripts/ios_devspace_check.py"
  "scripts/ios_design.py"
  "scripts/ios_doctor.py"
  "scripts/ios_goal_loop.py"
  "scripts/ios_inventory.py"
  "scripts/ios_modernize.py"
  "scripts/ios_plan.py"
  "scripts/ios_performance.py"
  "scripts/ios_preview.py"
  "scripts/ios_prove.py"
  "scripts/ios_redaction.py"
  "scripts/ios_report_quality.py"
  "scripts/ios_scan_scope.py"
  "scripts/ios_spec_workflow.py"
  "scripts/ios_shipguard_demo.py"
  "scripts/ios_shipguard_eval.py"
  "scripts/ios_target_match.py"
  "scripts/lib/safe_paths.sh"
  "scripts/shipguard_devspace_mcp.py"
  "tests/ios_branding_test.sh"
  "tests/profile_audit_test.sh"
  "tests/profile_fix_plan_test.sh"
  "tests/profile_validation_receipts_test.sh"
  "tests/profile_validation_rerun_receipts_test.sh"
  "tests/profile_proof_handoff_receipts_test.sh"
  "tests/command_family_runtime_output_receipts_test.sh"
  "tests/trust_hardening_receipts_test.sh"
  "tests/task_contract_test.sh"
  "tests/task_contract_receipts_test.sh"
  "tests/external_pilot_verdict_bench_test.sh"
  "tests/tool_value_gauntlet_test.sh"
  "tests/ios_devspace_check_test.sh"
  "tests/ios_spec_workflow_test.sh"
  "scripts/codex_status.sh"
  "scripts/transcript_redact.sh"
  "scripts/transcript_verify.sh"
  "scripts/transcript_corpus.sh"
  "evals/README.md"
  "evals/cases.jsonl"
  "evals/ios_shipguard_cases.jsonl"
  "evals/run_local.py"
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
  echo "# ShipGuard Self-Audit"
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
    if "$tool_root/bin/shipguard" $command >/dev/null; then
      echo "| shipguard $command | pass |"
    else
      echo "| shipguard $command | missing |"
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
