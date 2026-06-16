#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer --help >/dev/null
./bin/codex-maintainer validate
./bin/codex-maintainer doctor .

./bin/codex-maintainer init ios "$tmp_dir/app" >/dev/null
./bin/codex-maintainer doctor "$tmp_dir/app" >/dev/null

score_output="$(./bin/codex-maintainer score examples/scored-run.md)"
printf '%s\n' "$score_output" | grep -q 'Total score: 11/12'
printf '%s\n' "$score_output" | grep -q 'usable maintainer-quality run'

echo "cli smoke tests passed"
