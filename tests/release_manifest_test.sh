#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-manifest --help >/dev/null

tarball="$(./scripts/package_release.sh)"
version="$(sed -n '1p' VERSION)"
sha="$(shasum -a 256 "$tarball" | awk '{print $1}')"
commit="$(git rev-parse HEAD)"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-manifest \
    --tarball "$tarball" \
    --out "$tmp_dir/proof" \
    --version "$version" \
    --tag "v$version" \
    --commit "$commit" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" \
    --notes "local proof fixture" >/dev/null

test -f "$tmp_dir/proof/release-manifest.json"
test -f "$tmp_dir/proof/proof-ledger.md"

EXPECTED_VERSION="$version" EXPECTED_COMMIT="$commit" EXPECTED_SHA="$sha" \
  perl -MJSON::PP -0e '
  my $manifest = decode_json(<>);
  die "bad schema" unless $manifest->{schema_version} eq "1.0";
  die "bad generated_at" unless $manifest->{generated_at} eq "2026-06-16T00:00:00Z";
  die "bad version" unless $manifest->{version} eq $ENV{EXPECTED_VERSION};
  die "bad tag" unless $manifest->{tag} eq "v$ENV{EXPECTED_VERSION}";
  die "bad commit" unless $manifest->{commit} eq $ENV{EXPECTED_COMMIT};
  die "bad artifact name" unless $manifest->{artifact}{name} eq "codex-maintainer-v$ENV{EXPECTED_VERSION}.tar.gz";
  die "bad sha" unless $manifest->{artifact}{sha256} eq $ENV{EXPECTED_SHA};
  die "bad bytes" unless $manifest->{artifact}{bytes} > 1000;
  die "missing ci url" unless $manifest->{proofs}{ci_run_url} =~ /actions\/runs\/123/;
  die "missing release url" unless $manifest->{proofs}{release_url} =~ /releases\/tag/;
  die "missing issue url" unless $manifest->{proofs}{issue_url} =~ /issues\/99/;
  die "clean status required" unless $manifest->{proofs}{clean_status_required};
  die "missing notes" unless $manifest->{notes} eq "local proof fixture";
' "$tmp_dir/proof/release-manifest.json"

grep -q '# Release Proof Ledger' "$tmp_dir/proof/proof-ledger.md"
grep -q "Artifact SHA-256: $sha" "$tmp_dir/proof/proof-ledger.md"
grep -q 'GitHub Actions passed on the release commit' "$tmp_dir/proof/proof-ledger.md"
grep -q 'Tracking issue is closed' "$tmp_dir/proof/proof-ledger.md"

if ./bin/codex-maintainer release-manifest \
  --tarball "$tarball" \
  --out "$tmp_dir/bad-version" \
  --version 9.9.9 >/dev/null 2>&1; then
  echo "expected mismatched tarball version to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer release-manifest \
  --tarball "$tmp_dir/missing.tar.gz" \
  --out "$tmp_dir/missing" >/dev/null 2>&1; then
  echo "expected missing tarball to fail" >&2
  exit 1
fi

echo "release manifest tests passed"
