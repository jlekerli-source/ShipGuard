#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer init ios "$tmp_dir/ios-app" >/dev/null
./bin/codex-maintainer doctor ios "$tmp_dir/ios-app" >/dev/null
./bin/codex-maintainer doctor "$tmp_dir/ios-app" >/dev/null
grep -q 'AGENTS.md Template For iOS App Work' "$tmp_dir/ios-app/AGENTS.md"

./bin/codex-maintainer init web "$tmp_dir/web-app" >/dev/null
./bin/codex-maintainer doctor web "$tmp_dir/web-app" >/dev/null
grep -q 'Web Codex Maintainer Instructions' "$tmp_dir/web-app/AGENTS.md"
grep -q 'auth, payments, migrations' "$tmp_dir/web-app/AGENTS.md"

printf 'custom\n' > "$tmp_dir/web-app/AGENTS.md"
./bin/codex-maintainer init web "$tmp_dir/web-app" >/dev/null
grep -qx 'custom' "$tmp_dir/web-app/AGENTS.md"
./bin/codex-maintainer init web "$tmp_dir/web-app" --force >/dev/null
grep -q 'Web Codex Maintainer Instructions' "$tmp_dir/web-app/AGENTS.md"

./bin/codex-maintainer init backend "$tmp_dir/backend-app" >/dev/null
./bin/codex-maintainer doctor backend "$tmp_dir/backend-app" >/dev/null
grep -q 'Backend Service Codex Maintainer Instructions' "$tmp_dir/backend-app/AGENTS.md"
grep -q 'queues, schedulers, retries' "$tmp_dir/backend-app/AGENTS.md"

./bin/codex-maintainer init cli "$tmp_dir/cli-tool" >/dev/null
./bin/codex-maintainer doctor cli "$tmp_dir/cli-tool" >/dev/null
grep -q 'CLI Tool Codex Maintainer Instructions' "$tmp_dir/cli-tool/AGENTS.md"
grep -q 'stdout, stderr, exit codes' "$tmp_dir/cli-tool/AGENTS.md"

if ./bin/codex-maintainer init desktop "$tmp_dir/desktop-app" >/dev/null 2>&1; then
  echo "expected unknown init profile to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer doctor desktop "$tmp_dir/desktop-app" >/dev/null 2>&1; then
  echo "expected unknown doctor profile to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer doctor web "$tmp_dir/web-app" extra >/dev/null 2>&1; then
  echo "expected extra doctor argument to fail" >&2
  exit 1
fi

echo "template profile tests passed"
