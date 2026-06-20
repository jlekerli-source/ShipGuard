#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

make_pkg_root() {
  local root="$1"
  local version="$2"
  mkdir -p "$root/shipguard-v$version/bin" "$root/shipguard-v$version/scripts"
  printf '%s\n' "$version" > "$root/shipguard-v$version/VERSION"
  printf '#!/usr/bin/env bash\nprintf shipguard\n' > "$root/shipguard-v$version/bin/shipguard"
  printf '#!/usr/bin/env bash\nexit 0\n' > "$root/shipguard-v$version/scripts/install.sh"
  chmod +x "$root/shipguard-v$version/bin/shipguard" "$root/shipguard-v$version/scripts/install.sh"
}

safe_root="$tmp_dir/safe"
make_pkg_root "$safe_root" "9.9.9"
COPYFILE_DISABLE=1 tar -C "$safe_root" -czf "$tmp_dir/shipguard-v9.9.9.tar.gz" "shipguard-v9.9.9"

unsafe_root="$tmp_dir/unsafe"
make_pkg_root "$unsafe_root" "3.130.0"
printf 'generated metadata\n' > "$unsafe_root/shipguard-v3.130.0/._install.sh"
printf 'generated metadata\n' > "$unsafe_root/._shipguard-v3.130.0"
COPYFILE_DISABLE=1 tar -C "$unsafe_root" -czf "$tmp_dir/shipguard-v3.130.0.tar.gz" "._shipguard-v3.130.0" "shipguard-v3.130.0"

missing_root="$tmp_dir/missing-root"
mkdir -p "$missing_root/not-shipguard-v1.0.0"
printf 'incomplete\n' > "$missing_root/not-shipguard-v1.0.0/README.md"
COPYFILE_DISABLE=1 tar -C "$missing_root" -czf "$tmp_dir/shipguard-v1.0.0.tar.gz" "not-shipguard-v1.0.0"

./bin/shipguard release-package hygiene \
  --path . \
  --tarball "$tmp_dir/shipguard-v9.9.9.tar.gz" \
  --out "$tmp_dir/safe-report" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/safe-report/release-package-hygiene.json"
grep -q '"safeCurrentBaseline": null' "$tmp_dir/safe-report/release-package-hygiene.json"
grep -q 'safe to pass into install/upgrade proof' "$tmp_dir/safe-report/release-package-hygiene.md"

if ./bin/shipguard release-package hygiene \
  --path . \
  --tarball "$tmp_dir/shipguard-v3.130.0.tar.gz" \
  --tarball "$tmp_dir/shipguard-v1.0.0.tar.gz" \
  --out "$tmp_dir/blocked-report" \
  --shareable >/dev/null; then
  echo "expected unsafe package hygiene report to exit non-zero" >&2
  exit 1
fi

grep -q '"status": "blocked"' "$tmp_dir/blocked-report/release-package-hygiene.json"
grep -q '"ruleId": "appledouble-sidecar"' "$tmp_dir/blocked-report/release-package-hygiene.json"
grep -q '"ruleId": "installable-root-missing"' "$tmp_dir/blocked-report/release-package-hygiene.json"
grep -q '"ruleSummary":' "$tmp_dir/blocked-report/release-package-hygiene.json"
grep -q 'doesNotRewriteHistoricalAssets' "$tmp_dir/blocked-report/release-package-hygiene.json"
grep -q '._shipguard-v3.130.0' "$tmp_dir/blocked-report/release-package-hygiene.md"
grep -q 'Rule Summary' "$tmp_dir/blocked-report/release-package-hygiene.md"
grep -q './scripts/package_release.sh' "$tmp_dir/blocked-report/release-package-hygiene.md"

json_stdout="$(./bin/shipguard release-package hygiene --path . --tarball "$tmp_dir/shipguard-v9.9.9.tar.gz" --json)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard release-package hygiene"'

markdown_stdout="$(./bin/shipguard release-package hygiene --path . --tarball "$tmp_dir/shipguard-v9.9.9.tar.gz" --markdown)"
printf '%s\n' "$markdown_stdout" | grep -q '# ShipGuard Release Package Lineage Hygiene'

echo "release package hygiene tests passed"
