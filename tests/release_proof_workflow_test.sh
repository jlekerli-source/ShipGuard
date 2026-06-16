#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$repo_root"

tag_workflow="examples/workflows/release-proof-on-tag.yml"
manual_workflow="examples/workflows/release-proof-manual.yml"

test -f "$tag_workflow"
test -f "$manual_workflow"

for workflow in "$tag_workflow" "$manual_workflow"; do
  grep -q 'actions/checkout@v5' "$workflow"
  grep -q 'jlekerli-source/ringly-codex-workflows/actions/release-proof@v3.38.0' "$workflow"
  grep -q 'release-url:' "$workflow"
  grep -q 'artifacts/codex-maintainer-release-proof' "$workflow"
  grep -q 'attestation-badge' "$workflow"
  grep -q 'permissions:' "$workflow"
  grep -q 'contents: read' "$workflow"
done

grep -q 'tags:' "$tag_workflow"
grep -q '"v\*\.\*\.\*"' "$tag_workflow"
grep -q 'github.ref_name' "$tag_workflow"
grep -q 'workflow_dispatch:' "$manual_workflow"
grep -q 'release-tag:' "$manual_workflow"
grep -q 'issue-url:' "$manual_workflow"
grep -q 'tag: ${{ inputs.release-tag }}' "$manual_workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$tag_workflow" "$manual_workflow"
fi

echo "release proof workflow tests passed"
