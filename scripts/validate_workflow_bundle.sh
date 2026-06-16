#!/usr/bin/env bash

set -euo pipefail

root="${1:-.}"
cd "$root"

required_files=(
  ".gitignore"
  "README.md"
  "AGENTS.md"
  "CHANGELOG.md"
  "CODEX_TASK_TEMPLATE.md"
  "VERSION"
  "PLANS.md"
  "SUBAGENTS.md"
  "EVALUATION_SUITE.md"
  "SCORECARD.md"
  "CONTRIBUTING.md"
  "ROADMAP.md"
  "SECURITY.md"
  "LICENSE"
  "bin/codex-maintainer"
  ".github/workflows/autopsy-artifact.yml"
  "actions/ci-gate/action.yml"
  "actions/arena-compare/action.yml"
  "actions/release-evidence/action.yml"
  "actions/release-evidence-negative-index/action.yml"
  "actions/release-evidence-verify/action.yml"
  "actions/release-proof/action.yml"
  "actions/review-comment/action.yml"
  "actions/transcript-corpus/action.yml"
  "actions/transcript-verify/action.yml"
  "actions/validate/action.yml"
  "_config.yml"
  "docs/adoption-guide.md"
  "docs/arena.md"
  "docs/arena-compare-action.md"
  "docs/autopsy.md"
  "docs/autopsy-github-actions.md"
  "docs/benchmark.md"
  "docs/check-run.md"
  "docs/ci-gate.md"
  "docs/ci-summary.md"
  "docs/command-matrix.md"
  "docs/demo-reports.md"
  "docs/_config.yml"
  "docs/cli.md"
  "docs/github-action.md"
  "docs/index.md"
  "docs/maintainer-reliability-os.md"
  "docs/next-goal.md"
  "docs/policy.md"
  "docs/pr-review-bot.md"
  "docs/release-checklist.md"
  "docs/release-attest.md"
  "docs/release-consume.md"
  "docs/release-proof.md"
  "docs/release-proof-consumption.md"
  "docs/release-evidence-negative-index-action.md"
  "docs/release-evidence-verify.md"
  "docs/sarif.md"
  "docs/release-proof-action.md"
  "docs/release-proof-workflows.md"
  "docs/release-replay.md"
  "docs/template-profiles.md"
  "docs/transcript-corpus-action.md"
  "docs/transcript-corpus.md"
  "docs/transcript-redaction.md"
  "docs/transcript-verify-action.md"
  "docs/use-in-your-repo.md"
  "docs/workflow-diagram.md"
  "examples/adoption-checklist.md"
  "examples/arena-results.md"
  "examples/redacted-transcript.md"
  "examples/autopsy-report.md"
  "examples/ci-gate.md"
  "examples/demo-walkthrough.md"
  "examples/workflows/release-proof-manual.yml"
  "examples/workflows/release-proof-on-tag.yml"
  "examples/workflows/arena-compare.yml"
  "examples/workflows/transcript-corpus.yml"
  "examples/workflows/transcript-verify.yml"
  "examples/workflows/release-evidence-negative-index.yml"
  "examples/workflows/release-evidence-consume.yml"
  "examples/demo-reports/README.md"
  "examples/demo-reports/arena/index.md"
  "examples/demo-reports/arena/results.json"
  "examples/demo-reports/leaderboard.json"
  "examples/issue-to-plan-to-validation.md"
  "examples/prompt-pack.md"
  "examples/review-comment.md"
  "examples/release-proof-consumption-checklist.md"
  "examples/scored-run.md"
  "fixtures/transcripts/ios-notification-triage/transcript.md"
  "fixtures/transcripts/ios-notification-triage/redaction-report.json"
  "fixtures/transcripts/release-proof-review/transcript.md"
  "fixtures/transcripts/release-proof-review/redaction-report.json"
  "fixtures/transcripts/web-regression-review/transcript.md"
  "fixtures/transcripts/web-regression-review/redaction-report.json"
  "fixtures/demo-ios-repo/Package.swift"
  "fixtures/demo-ios-repo/README.md"
  "fixtures/demo-ios-repo/SampleRun.md"
  "fixtures/policy/strict.conf"
  "fixtures/autopsy/good-run/diff.patch"
  "fixtures/autopsy/good-run/run.md"
  "fixtures/autopsy/good-run/task.md"
  "fixtures/autopsy/good-run/tests.log"
  "fixtures/autopsy/weak-run/diff.patch"
  "fixtures/autopsy/weak-run/run.md"
  "fixtures/autopsy/weak-run/task.md"
  "fixtures/autopsy/dangerous-run/diff.patch"
  "fixtures/autopsy/dangerous-run/run.md"
  "fixtures/autopsy/dangerous-run/task.md"
  "fixtures/arena/good-maintainer/diff.patch"
  "fixtures/arena/good-maintainer/run.md"
  "fixtures/arena/good-maintainer/task.md"
  "fixtures/arena/good-maintainer/tests.log"
  "fixtures/arena/backend-webhook-idempotency/diff.patch"
  "fixtures/arena/backend-webhook-idempotency/run.md"
  "fixtures/arena/backend-webhook-idempotency/task.md"
  "fixtures/arena/backend-webhook-idempotency/tests.log"
  "fixtures/arena/frontend-async-state-regression/diff.patch"
  "fixtures/arena/frontend-async-state-regression/run.md"
  "fixtures/arena/frontend-async-state-regression/task.md"
  "fixtures/arena/frontend-async-state-regression/tests.log"
  "fixtures/arena/cli-dangerous-clean/diff.patch"
  "fixtures/arena/cli-dangerous-clean/run.md"
  "fixtures/arena/cli-dangerous-clean/task.md"
  "fixtures/arena/weak-maintainer/diff.patch"
  "fixtures/arena/weak-maintainer/run.md"
  "fixtures/arena/weak-maintainer/task.md"
  "fixtures/arena/dangerous-maintainer/diff.patch"
  "fixtures/arena/dangerous-maintainer/run.md"
  "fixtures/arena/dangerous-maintainer/task.md"
  "fixtures/arena/failing-validation/diff.patch"
  "fixtures/arena/failing-validation/run.md"
  "fixtures/arena/failing-validation/task.md"
  "fixtures/arena/failing-validation/tests.log"
  "fixtures/arena/no-diff-implementation/run.md"
  "fixtures/arena/no-diff-implementation/task.md"
  "fixtures/arena/review-only/run.md"
  "fixtures/arena/review-only/task.md"
  "fixtures/external-arena-pack/imported-clean/diff.patch"
  "fixtures/external-arena-pack/imported-clean/run.md"
  "fixtures/external-arena-pack/imported-clean/task.md"
  "fixtures/external-arena-pack/imported-clean/tests.log"
  "fixtures/external-arena-pack/imported-risky/diff.patch"
  "fixtures/external-arena-pack/imported-risky/run.md"
  "fixtures/external-arena-pack/imported-risky/task.md"
  "fixtures/release-evidence/negative/README.md"
  "fixtures/release-evidence/negative/cases.tsv"
  "fixtures/release-evidence/negative/missing-source/site/evidence.json"
  "fixtures/release-evidence/negative/consumer-mismatch/site/evidence.json"
  "fixtures/release-evidence/negative/digest-summary-mismatch/site/evidence.json"
  "fixtures/release-evidence/negative/bundle-missing-output/bundle.json"
  "scripts/arena_run.sh"
  "scripts/arena_import.sh"
  "scripts/arena_compare.sh"
  "scripts/arena_sign.sh"
  "scripts/arena_verify.sh"
  "scripts/autopsy_report.sh"
  "scripts/build_demo_reports.sh"
  "scripts/check_run.sh"
  "scripts/ci_gate.sh"
  "scripts/ci_summary.sh"
  "scripts/install.sh"
  "scripts/leaderboard_build.sh"
  "scripts/next_goal.sh"
  "scripts/package_release.sh"
  "scripts/policy.sh"
  "scripts/release_proof.sh"
  "scripts/release_index.sh"
  "scripts/release_attest.sh"
  "scripts/release_consume.sh"
  "scripts/release_manifest.sh"
  "scripts/release_replay.sh"
  "scripts/review_comment.sh"
  "scripts/sarif.sh"
  "scripts/self_audit.sh"
  "scripts/transcript_redact.sh"
  "scripts/transcript_verify.sh"
  "scripts/transcript_corpus.sh"
  "templates/backend/README.md"
  "templates/backend/AGENTS.md"
  "templates/cli/README.md"
  "templates/cli/AGENTS.md"
  "templates/ios/README.md"
  "templates/ios/AGENTS.md"
  "templates/web/README.md"
  "templates/web/AGENTS.md"
  "templates/policy/default.conf"
  "tests/check_run_post_test.sh"
  "tests/check_run_test.sh"
  "tests/ci_gate_test.sh"
  "tests/ci_summary_test.sh"
  "tests/cli_smoke_test.sh"
  "tests/action_artifact_test.sh"
  "tests/arena_compare_action_test.sh"
  "tests/arena_import_test.sh"
  "tests/arena_compare_test.sh"
  "tests/arena_sign_test.sh"
  "tests/arena_test.sh"
  "tests/autopsy_test.sh"
  "tests/leaderboard_test.sh"
  "tests/next_goal_test.sh"
  "tests/package_release_test.sh"
  "tests/policy_test.sh"
  "tests/release_index_test.sh"
  "tests/release_attest_test.sh"
  "tests/release_consume_test.sh"
  "tests/release_proof_test.sh"
  "tests/release_manifest_test.sh"
  "tests/release_proof_action_test.sh"
  "tests/release_proof_consumption_test.sh"
  "tests/release_proof_workflow_test.sh"
  "tests/release_replay_test.sh"
  "tests/release_evidence_negative_index_action_test.sh"
  "tests/release_evidence_verify_action_test.sh"
  "tests/release_evidence_verify_test.sh"
  "tests/review_comment_test.sh"
  "tests/sarif_test.sh"
  "tests/self_audit_test.sh"
  "tests/template_profiles_test.sh"
  "tests/transcript_redaction_test.sh"
  "tests/transcript_verify_test.sh"
  "tests/transcript_verify_action_test.sh"
  "tests/transcript_corpus_test.sh"
  "tests/transcript_corpus_action_test.sh"
  ".agents/skills/alarm-testing/SKILL.md"
  ".agents/skills/bug-triage/SKILL.md"
  ".agents/skills/notification-permissions/SKILL.md"
  ".agents/skills/release-checklist/SKILL.md"
  ".agents/skills/ui-polish/SKILL.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "missing required file: $file" >&2
    exit 1
  fi
done

if ! grep -qxE '[0-9]+\.[0-9]+\.[0-9]+' VERSION; then
  echo "VERSION must be a semantic version like 0.5.0" >&2
  exit 1
fi

for skill in .agents/skills/*/SKILL.md; do
  delimiter_count=$(grep -c '^---$' "$skill")
  if [[ "$delimiter_count" -ne 2 ]]; then
    echo "expected exactly two frontmatter delimiters: $skill" >&2
    exit 1
  fi
  if [[ "$(grep -c '^name: ' "$skill")" -ne 1 ]]; then
    echo "missing skill name: $skill" >&2
    exit 1
  fi
  if [[ "$(grep -c '^description: ' "$skill")" -ne 1 ]]; then
    echo "missing skill description: $skill" >&2
    exit 1
  fi
done

while IFS= read -r script; do
  bash -n "$script"
  if head -n 1 "$script" | grep -q '^#!' && [[ ! -x "$script" ]]; then
    echo "script has shebang but is not executable: $script" >&2
    exit 1
  fi
done < <(find scripts -type f -name '*.sh' | sort)

while IFS=: read -r file target; do
  [[ -z "$target" ]] && continue
  [[ "$target" == http://* || "$target" == https://* || "$target" == mailto:* || "$target" == "#"* ]] && continue
  target="${target%%#*}"
  [[ -z "$target" ]] && continue
  candidate="$(dirname "$file")/$target"
  if [[ ! -e "$candidate" ]]; then
    echo "broken local markdown link in $file: $target" >&2
    exit 1
  fi
done < <(
  find . -type f -name '*.md' -not -path './.git/*' -print0 |
    xargs -0 perl -ne 'while (/\[[^\]]+\]\(([^)]+)\)/g) { print "$ARGV:$1\n" }'
)

if command -v ruby >/dev/null 2>&1; then
  yaml_files=()
  while IFS= read -r file; do
    yaml_files+=("$file")
  done < <(find .github -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)
  if [[ "${#yaml_files[@]}" -gt 0 ]]; then
    ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "${yaml_files[@]}"
  fi
else
  echo "ruby unavailable; skipping yaml parse"
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --check
else
  echo "not inside a git worktree; skipping git diff --check"
fi

echo "workflow bundle validation passed"
