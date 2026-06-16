#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer --help >/dev/null
test "$(./bin/codex-maintainer version)" = "$(sed -n '1p' VERSION)"
./bin/codex-maintainer policy show >/dev/null
./bin/codex-maintainer autopsy --help >/dev/null
./bin/codex-maintainer arena run --help >/dev/null
./bin/codex-maintainer review-comment --help >/dev/null
./bin/codex-maintainer ci-gate --help >/dev/null
./bin/codex-maintainer ci-summary --help >/dev/null
./bin/codex-maintainer check-run --help >/dev/null
./bin/codex-maintainer check-run post --help >/dev/null
./bin/codex-maintainer sarif --help >/dev/null
./bin/codex-maintainer leaderboard build --help >/dev/null
./bin/codex-maintainer release-attest build --help >/dev/null
./bin/codex-maintainer release-manifest --help >/dev/null
./bin/codex-maintainer release-manifest verify --help >/dev/null
./bin/codex-maintainer release-index build --help >/dev/null
./bin/codex-maintainer release-replay verify --help >/dev/null
./bin/codex-maintainer self-audit --help >/dev/null
./bin/codex-maintainer next-goal --help >/dev/null
if ./bin/codex-maintainer autopsy --run >/dev/null 2>&1; then
  echo "expected autopsy --run without a value to fail" >&2
  exit 1
fi
./bin/codex-maintainer validate
./bin/codex-maintainer doctor .

./bin/codex-maintainer init ios "$tmp_dir/app" >/dev/null
./bin/codex-maintainer doctor "$tmp_dir/app" >/dev/null
./bin/codex-maintainer init web "$tmp_dir/web-app" >/dev/null
./bin/codex-maintainer doctor web "$tmp_dir/web-app" >/dev/null
./bin/codex-maintainer init backend "$tmp_dir/backend-app" >/dev/null
./bin/codex-maintainer doctor backend "$tmp_dir/backend-app" >/dev/null
./bin/codex-maintainer init cli "$tmp_dir/cli-tool" >/dev/null
./bin/codex-maintainer doctor cli "$tmp_dir/cli-tool" >/dev/null

score_output="$(./bin/codex-maintainer score examples/scored-run.md)"
printf '%s\n' "$score_output" | grep -q 'Total score: 11/12'
printf '%s\n' "$score_output" | grep -q 'usable maintainer-quality run'

echo "cli smoke tests passed"
