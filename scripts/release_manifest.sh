#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-manifest

Usage:
  codex-maintainer release-manifest --tarball <release.tar.gz> --out <dir> [--version <version>] [--tag <tag>] [--commit <sha>] [--ci-run-url <url>] [--release-url <url>] [--issue-url <url>] [--notes <text>]

Outputs:
  release-manifest.json
  proof-ledger.md
USAGE
}

fail() {
  echo "release-manifest: $*" >&2
  exit 1
}

tarball=""
out_dir=""
version="$(sed -n '1p' "$tool_root/VERSION")"
tag=""
commit=""
ci_run_url=""
release_url=""
issue_url=""
notes=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --tarball)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--tarball requires a value"
      tarball="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --version)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--version requires a value"
      version="$2"
      shift 2
      ;;
    --tag)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--tag requires a value"
      tag="$2"
      shift 2
      ;;
    --commit)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--commit requires a value"
      commit="$2"
      shift 2
      ;;
    --ci-run-url)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--ci-run-url requires a value"
      ci_run_url="$2"
      shift 2
      ;;
    --release-url)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--release-url requires a value"
      release_url="$2"
      shift 2
      ;;
    --issue-url)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--issue-url requires a value"
      issue_url="$2"
      shift 2
      ;;
    --notes)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--notes requires a value"
      notes="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[[ -n "$tarball" ]] || fail "--tarball is required"
[[ -n "$out_dir" ]] || fail "--out is required"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "--version must be semantic"
[[ -f "$tarball" ]] || fail "tarball not found: $tarball"
[[ "$tarball" == *"v$version"* ]] || fail "tarball name must contain v$version"
[[ -n "$tag" ]] || tag="v$version"
if [[ -z "$commit" ]] && git -C "$tool_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  commit="$(git -C "$tool_root" rev-parse HEAD)"
fi
[[ -n "$commit" ]] || commit="unknown"

mkdir -p "$out_dir"
manifest_file="$out_dir/release-manifest.json"
ledger_file="$out_dir/proof-ledger.md"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"
tarball_name="$(basename "$tarball")"
tarball_bytes="$(wc -c < "$tarball" | tr -d '[:space:]')"
tarball_sha="$(shasum -a 256 "$tarball" | awk '{print $1}')"

VERSION_VALUE="$version" TAG_VALUE="$tag" COMMIT_VALUE="$commit" GENERATED_AT="$generated_at" \
  TARBALL_NAME="$tarball_name" TARBALL_BYTES="$tarball_bytes" TARBALL_SHA="$tarball_sha" \
  CI_RUN_URL="$ci_run_url" RELEASE_URL="$release_url" ISSUE_URL="$issue_url" NOTES="$notes" \
  MANIFEST_FILE="$manifest_file" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
my $manifest = {
  schema_version => '1.0',
  generated_at => $ENV{GENERATED_AT},
  version => $ENV{VERSION_VALUE},
  tag => $ENV{TAG_VALUE},
  commit => $ENV{COMMIT_VALUE},
  artifact => {
    name => $ENV{TARBALL_NAME},
    path => $ENV{TARBALL_NAME},
    bytes => 0 + $ENV{TARBALL_BYTES},
    sha256 => $ENV{TARBALL_SHA},
  },
  proofs => {
    ci_run_url => $ENV{CI_RUN_URL},
    release_url => $ENV{RELEASE_URL},
    issue_url => $ENV{ISSUE_URL},
    clean_status_required => JSON::PP::true,
  },
  notes => $ENV{NOTES},
};

open my $out, '>:encoding(UTF-8)', $ENV{MANIFEST_FILE} or die "release-manifest: cannot write manifest: $!\n";
print {$out} $json->encode($manifest);
close $out;
PERL

{
  echo "# Release Proof Ledger"
  echo
  echo "- Generated: $generated_at"
  echo "- Version: $version"
  echo "- Tag: $tag"
  echo "- Commit: $commit"
  echo "- Artifact: $tarball_name"
  echo "- Artifact bytes: $tarball_bytes"
  echo "- Artifact SHA-256: $tarball_sha"
  [[ -n "$ci_run_url" ]] && echo "- CI run: $ci_run_url"
  [[ -n "$release_url" ]] && echo "- Release: $release_url"
  [[ -n "$issue_url" ]] && echo "- Issue: $issue_url"
  [[ -n "$notes" ]] && echo "- Notes: $notes"
  echo
  echo "## Required Release Proof"
  echo
  echo "- [ ] Local release suite passed."
  echo "- [ ] GitHub Actions passed on the release commit."
  echo "- [ ] Release asset was uploaded."
  echo "- [ ] Asset SHA-256 matches this ledger."
  echo "- [ ] Tag points at the release commit."
  echo "- [ ] Tracking issue is closed."
  echo "- [ ] Git status is clean after publish."
} > "$ledger_file"

echo "wrote: $manifest_file"
echo "wrote: $ledger_file"
