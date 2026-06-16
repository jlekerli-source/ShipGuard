#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer arena import --help >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer arena import \
    --source fixtures/external-arena-pack \
    --out "$tmp_dir/imported-pack" \
    --pack-name "external-pack" >/dev/null

test -f "$tmp_dir/imported-pack/PACK.md"
test -f "$tmp_dir/imported-pack/imported-clean/run.md"
test -f "$tmp_dir/imported-pack/imported-clean/task.md"
test -f "$tmp_dir/imported-pack/imported-clean/diff.patch"
test -f "$tmp_dir/imported-pack/imported-clean/tests.log"
test -f "$tmp_dir/imported-pack/imported-risky/run.md"
grep -q 'Pack: external-pack' "$tmp_dir/imported-pack/PACK.md"
grep -q 'Cases: 2' "$tmp_dir/imported-pack/PACK.md"

./bin/codex-maintainer arena run \
  --fixture "$tmp_dir/imported-pack" \
  --out "$tmp_dir/imported-results" >/dev/null

grep -q '"case_count": 2' "$tmp_dir/imported-results/results.json"
grep -q '"id": "imported-clean"' "$tmp_dir/imported-results/results.json"
grep -q '"id": "imported-risky"' "$tmp_dir/imported-results/results.json"

if ./bin/codex-maintainer arena import \
  --source fixtures/external-arena-pack \
  --out "$tmp_dir/imported-pack" >/dev/null 2>&1; then
  echo "expected import without --force to fail on existing destination" >&2
  exit 1
fi

./bin/codex-maintainer arena import \
  --source fixtures/external-arena-pack \
  --out "$tmp_dir/imported-pack" \
  --force >/dev/null

mkdir -p "$tmp_dir/unsafe/case"
printf '# Unsafe\n\n- Scope control: 1\n' > "$tmp_dir/unsafe/case/run.md"
printf 'token %s%s\n' 'sk-' '123456789012345678901234' >> "$tmp_dir/unsafe/case/run.md"
if ./bin/codex-maintainer arena import \
  --source "$tmp_dir/unsafe" \
  --out "$tmp_dir/unsafe-out" >/dev/null 2>&1; then
  echo "expected unsafe fixture import to fail" >&2
  exit 1
fi

mkdir -p "$tmp_dir/missing-run/case"
if ./bin/codex-maintainer arena import \
  --source "$tmp_dir/missing-run" \
  --out "$tmp_dir/missing-run-out" >/dev/null 2>&1; then
  echo "expected missing run.md import to fail" >&2
  exit 1
fi

echo "arena import tests passed"
