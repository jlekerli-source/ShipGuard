#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
prefix="${PREFIX:-/usr/local}"
bin_dir="$prefix/bin"
lib_dir="$prefix/lib/shipguard"
target="$bin_dir/shipguard"
legacy_target="$bin_dir/codex-maintainer"

if [[ ! -x "$package_root/bin/shipguard" ]]; then
  echo "shipguard binary not found in package root: $package_root" >&2
  exit 1
fi

rm -rf "$lib_dir"
mkdir -p "$lib_dir"
tar -C "$package_root" -cf - . | tar -C "$lib_dir" -xf -
find "$lib_dir" \
  \( -name '.git' -o -name 'dist' -o -name '.DS_Store' -o -name '.cache' -o -name 'DerivedData' -o -name '__pycache__' \) \
  -prune -exec rm -rf {} +
find "$lib_dir" -type f -name '*.pyc' -delete

mkdir -p "$bin_dir"
cat > "$target" <<WRAPPER
#!/usr/bin/env bash
exec "$lib_dir/bin/shipguard" "\$@"
WRAPPER
chmod +x "$target"

cat > "$legacy_target" <<WRAPPER
#!/usr/bin/env bash
exec "$lib_dir/bin/codex-maintainer" "\$@"
WRAPPER
chmod +x "$legacy_target"

echo "installed shipguard to $target"
echo "installed codex-maintainer compatibility alias to $legacy_target"
echo "installed toolkit files to $lib_dir"
