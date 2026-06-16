#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer docs-check --help >/dev/null

./bin/codex-maintainer docs-check . --out "$tmp_dir/docs-check" >/dev/null
test -f "$tmp_dir/docs-check/docs-check.json"
test -f "$tmp_dir/docs-check/docs-check.md"
grep -q '"status" : "pass"' "$tmp_dir/docs-check/docs-check.json"
grep -q '"broken_count" : 0' "$tmp_dir/docs-check/docs-check.json"
grep -q '# Docs Check' "$tmp_dir/docs-check/docs-check.md"

mkdir -p "$tmp_dir/broken"
cat > "$tmp_dir/broken/README.md" <<'MD'
# Broken Docs

This link points at [missing local docs](missing.md).
This one is external and ignored: [OpenAI](https://openai.com/).
This in-page anchor is ignored: [top](#broken-docs).
MD

if ./bin/codex-maintainer docs-check "$tmp_dir/broken" --out "$tmp_dir/broken-out" >/dev/null 2>&1; then
  echo "expected docs-check to fail on a broken local link" >&2
  exit 1
fi
grep -q '"status" : "blocked"' "$tmp_dir/broken-out/docs-check.json"
grep -q '"broken_count" : 1' "$tmp_dir/broken-out/docs-check.json"
grep -q '"link" : "missing.md"' "$tmp_dir/broken-out/docs-check.json"

echo "docs check tests passed"
