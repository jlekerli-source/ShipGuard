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
  "actions/validate/action.yml"
  "_config.yml"
  "docs/adoption-guide.md"
  "docs/autopsy.md"
  "docs/_config.yml"
  "docs/cli.md"
  "docs/github-action.md"
  "docs/index.md"
  "docs/use-in-your-repo.md"
  "docs/workflow-diagram.md"
  "examples/adoption-checklist.md"
  "examples/autopsy-report.md"
  "examples/demo-walkthrough.md"
  "examples/issue-to-plan-to-validation.md"
  "examples/prompt-pack.md"
  "examples/scored-run.md"
  "fixtures/demo-ios-repo/Package.swift"
  "fixtures/demo-ios-repo/README.md"
  "fixtures/demo-ios-repo/SampleRun.md"
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
  "scripts/autopsy_report.sh"
  "scripts/install.sh"
  "scripts/package_release.sh"
  "templates/ios/README.md"
  "templates/ios/AGENTS.md"
  "tests/cli_smoke_test.sh"
  "tests/autopsy_test.sh"
  "tests/package_release_test.sh"
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
