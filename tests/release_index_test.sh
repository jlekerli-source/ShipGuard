#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-index build --help >/dev/null

make_manifest() {
  local version="$1"
  local commit="$2"
  local sha="$3"
  local out="$4"
  cat > "$out" <<JSON
{
  "schema_version": "1.0",
  "generated_at": "2026-06-16T00:00:00Z",
  "version": "$version",
  "tag": "v$version",
  "commit": "$commit",
  "artifact": {
    "name": "codex-maintainer-v$version.tar.gz",
    "path": "codex-maintainer-v$version.tar.gz",
    "bytes": 12345,
    "sha256": "$sha"
  },
  "proofs": {
    "ci_run_url": "https://github.com/example/repo/actions/runs/$version",
    "release_url": "https://github.com/example/repo/releases/tag/v$version",
    "issue_url": "https://github.com/example/repo/issues/$version",
    "clean_status_required": true
  },
  "notes": "fixture"
}
JSON
}

make_manifest "3.2.0" "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" "2222222222222222222222222222222222222222222222222222222222222222" "$tmp_dir/v3.2.0.json"
make_manifest "3.1.0" "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" "1111111111111111111111111111111111111111111111111111111111111111" "$tmp_dir/v3.1.0.json"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-index build \
    --manifest "$tmp_dir/v3.2.0.json" \
    --manifest "$tmp_dir/v3.1.0.json" \
    --title "Fixture Release Catalog" \
    --out "$tmp_dir/index" >/dev/null

test -f "$tmp_dir/index/release-index.json"
test -f "$tmp_dir/index/release-index.md"

perl -MJSON::PP -0e '
  my $index = decode_json(<>);
  die "bad schema" unless $index->{schema_version} eq "1.0";
  die "bad title" unless $index->{title} eq "Fixture Release Catalog";
  die "bad generated_at" unless $index->{generated_at} eq "2026-06-16T00:00:00Z";
  die "bad count" unless $index->{release_count} == 2;
  die "bad first version" unless $index->{releases}[0]{version} eq "3.1.0";
  die "bad second version" unless $index->{releases}[1]{version} eq "3.2.0";
  die "missing sha" unless $index->{releases}[0]{artifact}{sha256} =~ /^1{64}$/;
  die "missing release url" unless $index->{releases}[1]{proofs}{release_url} =~ /v3\.2\.0/;
' "$tmp_dir/index/release-index.json"

grep -q '# Fixture Release Catalog' "$tmp_dir/index/release-index.md"
grep -q '| 3.1.0 | v3.1.0 | aaaaaaaaaaaa | codex-maintainer-v3.1.0.tar.gz | `1111111111111111111111111111111111111111111111111111111111111111` | https://github.com/example/repo/releases/tag/v3.1.0 |' "$tmp_dir/index/release-index.md"
grep -q '| 3.2.0 | v3.2.0 | bbbbbbbbbbbb | codex-maintainer-v3.2.0.tar.gz | `2222222222222222222222222222222222222222222222222222222222222222` | https://github.com/example/repo/releases/tag/v3.2.0 |' "$tmp_dir/index/release-index.md"

if ./bin/codex-maintainer release-index build \
  --manifest "$tmp_dir/v3.1.0.json" \
  --manifest "$tmp_dir/v3.1.0.json" \
  --out "$tmp_dir/duplicate" >/dev/null 2>&1; then
  echo "expected duplicate manifest versions to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer release-index build \
  --manifest "$tmp_dir/missing.json" \
  --out "$tmp_dir/missing" >/dev/null 2>&1; then
  echo "expected missing manifest to fail" >&2
  exit 1
fi

echo "release index tests passed"
