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

if ./bin/codex-maintainer init backend "$tmp_dir/backend-app" >/dev/null 2>&1; then
  echo "expected unknown init profile to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer doctor backend "$tmp_dir/backend-app" >/dev/null 2>&1; then
  echo "expected unknown doctor profile to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer doctor web "$tmp_dir/web-app" extra >/dev/null 2>&1; then
  echo "expected extra doctor argument to fail" >&2
  exit 1
fi

echo "template profile tests passed"
