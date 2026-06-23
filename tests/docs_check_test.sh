#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard docs-check --help >/dev/null

./bin/shipguard docs-check . --out "$tmp_dir/docs-check" >/dev/null
test -f "$tmp_dir/docs-check/docs-check.json"
test -f "$tmp_dir/docs-check/docs-check.md"
grep -q '"status" : "pass"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"tool" : "shipguard docs-check"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"surface" : "ShipGuard DocsLink"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"schemaVersion" : 1' "$tmp_dir/docs-check/docs-check.json"
grep -q '"generatedAt"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"resultUX"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"scopeBoundary"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"reportQualityQuestions"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"broken_count" : 0' "$tmp_dir/docs-check/docs-check.json"
grep -q '# Docs Check' "$tmp_dir/docs-check/docs-check.md"
grep -q '## Result' "$tmp_dir/docs-check/docs-check.md"
grep -q '## Scope Boundary' "$tmp_dir/docs-check/docs-check.md"
grep -q '## Report Quality Questions' "$tmp_dir/docs-check/docs-check.md"
grep -q 'Record reviewer outcome without note' docs/cli.md
grep -q 'Record reviewer outcome with note' docs/cli.md
grep -q 'reviewer outcome is still local feedback' docs/task-contract.md
grep -q -- '--reviewer-note "Accepted after reviewing the proof packet."' README.md
grep -q -- '--reviewer-note "Accepted after reviewing the proof packet."' docs/cli.md
grep -q 'Private app runs and maintainer reviews prove ShipGuard QA only' README.md
grep -q 'Independent adoption needs an external user, repo, install, issue, PR, or marketplace signal' docs/cli.md
grep -q 'Final security-review proof needs review evidence that covers the CLI, plugin, GitHub Action, release proof, package install, and redaction/privacy surfaces' docs/cli.md
grep -q '## Proof Boundary Quickstart' docs/v4-stable-publication.md
grep -q 'Do not claim stable v4 until `v4 stable-publication` returns `pass`.' docs/v4-stable-publication.md
grep -q 'Stable Publication Proof Boundary Quickstart' docs/index.md
grep -q 'ban on substituting private app runs, fixture reports, generated starter files, stars, downloads, or vague testimonials for external evidence' docs/v4-stable-publication.md

mkdir -p "$tmp_dir/broken"
cat > "$tmp_dir/broken/README.md" <<'MD'
# Broken Docs

This link points at [missing local docs](missing.md).
This one is external and ignored: [OpenAI](https://openai.com/).
This in-page anchor is ignored: [top](#broken-docs).
MD

if ./bin/shipguard docs-check "$tmp_dir/broken" --out "$tmp_dir/broken-out" >/dev/null 2>&1; then
  echo "expected docs-check to fail on a broken local link" >&2
  exit 1
fi
grep -q '"status" : "blocked"' "$tmp_dir/broken-out/docs-check.json"
grep -q '"tool" : "shipguard docs-check"' "$tmp_dir/broken-out/docs-check.json"
grep -q '"broken_count" : 1' "$tmp_dir/broken-out/docs-check.json"
grep -q '"link" : "missing.md"' "$tmp_dir/broken-out/docs-check.json"
grep -q 'Fix the broken local Markdown links' "$tmp_dir/broken-out/docs-check.md"

echo "docs check tests passed"
