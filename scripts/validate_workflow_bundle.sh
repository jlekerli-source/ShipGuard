#!/usr/bin/env bash

set -euo pipefail

required_files=(
  "README.md"
  "AGENTS.md"
  "PLANS.md"
  "SUBAGENTS.md"
  "EVALUATION_SUITE.md"
  "CONTRIBUTING.md"
  "ROADMAP.md"
  "SECURITY.md"
  "LICENSE"
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

for skill in .agents/skills/*/SKILL.md; do
  grep -q '^---$' "$skill" || {
    echo "missing frontmatter delimiter: $skill" >&2
    exit 1
  }
  grep -q '^name: ' "$skill" || {
    echo "missing skill name: $skill" >&2
    exit 1
  }
  grep -q '^description: ' "$skill" || {
    echo "missing skill description: $skill" >&2
    exit 1
  }
done

while IFS= read -r script; do
  bash -n "$script"
done < <(find scripts -type f -name '*.sh' | sort)

git diff --check

echo "workflow bundle validation passed"
