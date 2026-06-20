#!/usr/bin/env bash

set -euo pipefail

export COPYFILE_DISABLE=1
export COPY_EXTENDED_ATTRIBUTES_DISABLE=1

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
  \( -name '.git' -o -name 'dist' -o -name '.DS_Store' -o -name '._*' -o -name '.cache' -o -name 'DerivedData' -o -name '__pycache__' \) \
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
echo
echo "# ShipGuard Install Receipt"
echo "Status: pass"
echo "Installed CLI: $target"
echo "Toolkit files: $lib_dir"
echo "PATH hint: export PATH=\"$bin_dir:\$PATH\""
echo "Next action: run \"$target\" validate, then initialize and doctor your target repo."
echo
echo "Next commands:"
echo "- \"$target\" version"
echo "- \"$target\" validate"
echo "- \"$target\" init ios <repo>"
echo "- \"$target\" doctor ios <repo>"
echo "- \"$target\" prepare \"<task goal>\" --path <repo> --out /tmp/shipguard-task --profile ios --validation \"<test command>\""
echo "- \"$target\" verify --task /tmp/shipguard-task/shipguard-task.json --diff <patch.diff> --evidence <receipt.json> --out /tmp/shipguard-verdict"
