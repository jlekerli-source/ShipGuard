#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard --help >/dev/null
test "$(./bin/shipguard version)" = "$(sed -n '1p' VERSION)"
test "$(./bin/codex-maintainer version)" = "$(sed -n '1p' VERSION)"
./bin/shipguard policy show >/dev/null
./bin/shipguard autopsy --help >/dev/null
./bin/shipguard arena run --help >/dev/null
./bin/shipguard arena compare --help >/dev/null
./bin/shipguard transcript redact --help >/dev/null
./bin/shipguard transcript verify --help >/dev/null
./bin/shipguard transcript corpus --help >/dev/null
./bin/shipguard review-comment --help >/dev/null
./bin/shipguard ci-gate --help >/dev/null
./bin/shipguard ci-summary --help >/dev/null
./bin/shipguard check-run --help >/dev/null
./bin/shipguard check-run post --help >/dev/null
./bin/shipguard sarif --help >/dev/null
./bin/shipguard docs-check --help >/dev/null
./bin/shipguard brand --help >/dev/null
./bin/shipguard value-gauntlet --help >/dev/null
./bin/shipguard prepare --help >/dev/null
./bin/shipguard verify --help >/dev/null
./bin/shipguard web audit --help >/dev/null
./bin/shipguard web plan --help >/dev/null
./bin/shipguard backend audit --help >/dev/null
./bin/shipguard backend plan --help >/dev/null
./bin/shipguard cli audit --help >/dev/null
./bin/shipguard cli plan --help >/dev/null
./bin/shipguard ios doctor --help >/dev/null
./bin/shipguard ios inventory --help >/dev/null
./bin/shipguard ios preview --help >/dev/null
./bin/shipguard ios devspace --help >/dev/null
./bin/shipguard ios devspace-check --help >/dev/null
./bin/shipguard ios brand --help >/dev/null
./bin/shipguard ios target-match --help >/dev/null
./bin/shipguard ios codex-handoff --help >/dev/null
./bin/shipguard ios plan --help >/dev/null
./bin/shipguard ios prove --help >/dev/null
./bin/shipguard ios launchdeck --help >/dev/null
./bin/shipguard ios performance --help >/dev/null
./bin/shipguard ios design --help >/dev/null
./bin/shipguard ios modernize --help >/dev/null
./bin/shipguard ios app-intelligence --help >/dev/null
./bin/shipguard ios ai-readiness --help >/dev/null
./bin/shipguard pilot-bench --help >/dev/null
./bin/shipguard ios external-audit --help >/dev/null
./bin/shipguard ios spec-workflow --help >/dev/null
./bin/shipguard ios report-quality --help >/dev/null
./bin/shipguard ios redact --help >/dev/null
./bin/shipguard ios eval --help >/dev/null
./bin/shipguard ios demo --help >/dev/null
./bin/shipguard ios goals --help >/dev/null
./bin/shipguard codex status --help >/dev/null
./bin/shipguard leaderboard build --help >/dev/null
./bin/shipguard release-attest build --help >/dev/null
./bin/shipguard release-proof build --help >/dev/null
./bin/shipguard release-manifest --help >/dev/null
./bin/shipguard release-manifest verify --help >/dev/null
./bin/shipguard release-index build --help >/dev/null
./bin/shipguard release-replay verify --help >/dev/null
./bin/shipguard release-consume verify --help >/dev/null
./bin/shipguard self-audit --help >/dev/null
./bin/shipguard next-goal --help >/dev/null
if ./bin/shipguard autopsy --run >/dev/null 2>&1; then
  echo "expected autopsy --run without a value to fail" >&2
  exit 1
fi
./bin/shipguard validate
./bin/shipguard doctor .

./bin/shipguard init ios "$tmp_dir/app" >/dev/null
./bin/shipguard doctor "$tmp_dir/app" >/dev/null
./bin/shipguard init web "$tmp_dir/web-app" >/dev/null
./bin/shipguard doctor web "$tmp_dir/web-app" >/dev/null
./bin/shipguard init backend "$tmp_dir/backend-app" >/dev/null
./bin/shipguard doctor backend "$tmp_dir/backend-app" >/dev/null
./bin/shipguard init cli "$tmp_dir/cli-tool" >/dev/null
./bin/shipguard doctor cli "$tmp_dir/cli-tool" >/dev/null

score_output="$(./bin/shipguard score examples/scored-run.md)"
printf '%s\n' "$score_output" | grep -q 'Total score: 11/12'
printf '%s\n' "$score_output" | grep -q 'usable maintainer-quality run'

echo "cli smoke tests passed"
