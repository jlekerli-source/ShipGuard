#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"
tarball="$(./scripts/package_release.sh)"

./bin/codex-maintainer release-attest build --help >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-manifest \
    --tarball "$tarball" \
    --out "$tmp_dir/proof" \
    --version "$version" \
    --tag "v$version" \
    --commit "0123456789abcdef0123456789abcdef01234567" \
    --ci-run-url "https://github.com/example/repo/actions/runs/123" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/99" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-index build \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --out "$tmp_dir/index" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-replay verify \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --tarball "$tarball" \
    --index "$tmp_dir/index/release-index.json" \
    --ledger "$tmp_dir/proof/proof-ledger.md" \
    --out "$tmp_dir/replay" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-attest build \
    --manifest "$tmp_dir/proof/release-manifest.json" \
    --replay "$tmp_dir/replay/replay-report.json" \
    --out "$tmp_dir/attestation" >/dev/null

test -f "$tmp_dir/attestation/attestation.json"
test -f "$tmp_dir/attestation/attestation.md"
test -f "$tmp_dir/attestation/attestation-badge.json"
grep -q '"status" : "pass"' "$tmp_dir/attestation/attestation.json"
grep -q "\"version\" : \"$version\"" "$tmp_dir/attestation/attestation.json"
grep -q '"blocked" : 0' "$tmp_dir/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/attestation/attestation-badge.json"
grep -q '# Codex Maintainer Release Attestation' "$tmp_dir/attestation/attestation.md"
grep -q 'Release artifact replay proof passed with zero blocked checks.' "$tmp_dir/attestation/attestation.md"

blocked_replay="$tmp_dir/blocked-replay.json"
perl -MJSON::PP -0e '
  my $json = JSON::PP->new->utf8->canonical(1)->pretty;
  my $r = decode_json(<>);
  $r->{status} = "blocked";
  $r->{summary}{blocked} = 1;
  print $json->encode($r);
' "$tmp_dir/replay/replay-report.json" > "$blocked_replay"

if ./bin/codex-maintainer release-attest build \
  --manifest "$tmp_dir/proof/release-manifest.json" \
  --replay "$blocked_replay" \
  --out "$tmp_dir/blocked-attestation" >/dev/null 2>&1; then
  echo "expected blocked replay attestation to fail" >&2
  exit 1
fi

echo "release attest tests passed"
