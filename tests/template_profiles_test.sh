#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard init ios "$tmp_dir/ios-app" >/dev/null
./bin/shipguard doctor ios "$tmp_dir/ios-app" >/dev/null
./bin/shipguard doctor "$tmp_dir/ios-app" >/dev/null
grep -q 'AGENTS.md Template For iOS App Work' "$tmp_dir/ios-app/AGENTS.md"

./bin/shipguard init web "$tmp_dir/web-app" >/dev/null
./bin/shipguard doctor web "$tmp_dir/web-app" >/dev/null
grep -q 'Web ShipGuard Instructions' "$tmp_dir/web-app/AGENTS.md"
grep -q 'auth, payments, migrations' "$tmp_dir/web-app/AGENTS.md"

printf 'custom\n' > "$tmp_dir/web-app/AGENTS.md"
./bin/shipguard init web "$tmp_dir/web-app" >/dev/null
grep -qx 'custom' "$tmp_dir/web-app/AGENTS.md"
./bin/shipguard init web "$tmp_dir/web-app" --force >/dev/null
grep -q 'Web ShipGuard Instructions' "$tmp_dir/web-app/AGENTS.md"

./bin/shipguard init backend "$tmp_dir/backend-app" >/dev/null
./bin/shipguard doctor backend "$tmp_dir/backend-app" >/dev/null
grep -q 'Backend Service ShipGuard Instructions' "$tmp_dir/backend-app/AGENTS.md"
grep -q 'queues, schedulers, retries' "$tmp_dir/backend-app/AGENTS.md"

./bin/shipguard init cli "$tmp_dir/cli-tool" >/dev/null
./bin/shipguard doctor cli "$tmp_dir/cli-tool" >/dev/null
grep -q 'CLI Tool ShipGuard Instructions' "$tmp_dir/cli-tool/AGENTS.md"
grep -q 'stdout, stderr, exit codes' "$tmp_dir/cli-tool/AGENTS.md"

if ./bin/shipguard init desktop "$tmp_dir/desktop-app" >/dev/null 2>&1; then
  echo "expected unknown init profile to fail" >&2
  exit 1
fi

if ./bin/shipguard doctor desktop "$tmp_dir/desktop-app" >/dev/null 2>&1; then
  echo "expected unknown doctor profile to fail" >&2
  exit 1
fi

if ./bin/shipguard doctor web "$tmp_dir/web-app" extra >/dev/null 2>&1; then
  echo "expected extra doctor argument to fail" >&2
  exit 1
fi

echo "template profile tests passed"
