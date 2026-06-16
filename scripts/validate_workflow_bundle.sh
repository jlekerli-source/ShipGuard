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
  "actions/review-comment/action.yml"
  "actions/validate/action.yml"
  "_config.yml"
  "docs/adoption-guide.md"
  "docs/arena.md"
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
  "docs/sarif.md"
  "docs/template-profiles.md"
  "docs/use-in-your-repo.md"
  "docs/workflow-diagram.md"
  "examples/adoption-checklist.md"
  "examples/arena-results.md"
  "examples/autopsy-report.md"
  "examples/ci-gate.md"
  "examples/demo-walkthrough.md"
  "examples/demo-reports/README.md"
  "examples/demo-reports/arena/index.md"
  "examples/demo-reports/arena/results.json"
  "examples/demo-reports/leaderboard.json"
  "examples/issue-to-plan-to-validation.md"
  "examples/prompt-pack.md"
  "examples/review-comment.md"
  "examples/scored-run.md"
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
  "scripts/arena_run.sh"
  "scripts/arena_import.sh"
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
  "scripts/review_comment.sh"
  "scripts/sarif.sh"
  "scripts/self_audit.sh"
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
  "tests/arena_import_test.sh"
  "tests/arena_sign_test.sh"
  "tests/arena_test.sh"
  "tests/autopsy_test.sh"
  "tests/leaderboard_test.sh"
  "tests/next_goal_test.sh"
  "tests/package_release_test.sh"
  "tests/policy_test.sh"
  "tests/review_comment_test.sh"
  "tests/sarif_test.sh"
  "tests/self_audit_test.sh"
  "tests/template_profiles_test.sh"
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
