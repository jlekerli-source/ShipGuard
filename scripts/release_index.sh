#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
shipguard release-index

Usage:
  shipguard release-index build --manifest <release-manifest.json> [--manifest <release-manifest.json> ...] --out <dir> [--title <title>]

Outputs:
  release-index.json
  release-index.md
USAGE
}

fail() {
  echo "release-index: $*" >&2
  exit 1
}

cmd_build() {
  local out_dir=""
  local title="ShipGuard Release Proof Catalog"
  local manifests=()

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --manifest)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--manifest requires a value"
        manifests+=("$2")
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
        shift 2
        ;;
      --title)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--title requires a value"
        title="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown build argument: $1"
        ;;
    esac
  done

  [[ "${#manifests[@]}" -gt 0 ]] || fail "at least one --manifest is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  for manifest in "${manifests[@]}"; do
    [[ -f "$manifest" ]] || fail "manifest not found: $manifest"
  done

  mkdir -p "$out_dir"
  local index_json="$out_dir/release-index.json"
  local index_md="$out_dir/release-index.md"
  local generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}}"

  TITLE="$title" GENERATED_AT="$generated_at" INDEX_JSON="$index_json" INDEX_MD="$index_md" perl -MJSON::PP -MList::Util=none -e '
use strict;
use warnings;

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
my @rows;
for my $file (@ARGV) {
  open my $fh, "<:encoding(UTF-8)", $file or die "release-index: cannot read $file: $!\n";
  local $/;
  my $manifest = decode_json(<$fh>);
  close $fh;

  die "release-index: unsupported schema in $file\n" unless ($manifest->{schema_version} || "") eq "1.0";
  my $artifact = $manifest->{artifact} || die "release-index: missing artifact in $file\n";
  my $proofs = $manifest->{proofs} || {};
  for my $required (qw(version tag commit)) {
    die "release-index: missing $required in $file\n" unless length($manifest->{$required} || "");
  }
  for my $required (qw(name sha256 bytes)) {
    die "release-index: missing artifact $required in $file\n" unless length($artifact->{$required} || "");
  }
  push @rows, {
    version => $manifest->{version},
    tag => $manifest->{tag},
    commit => $manifest->{commit},
    generated_at => $manifest->{generated_at} || "",
    artifact => {
      name => $artifact->{name},
      bytes => 0 + $artifact->{bytes},
      sha256 => $artifact->{sha256},
    },
    proofs => {
      ci_run_url => $proofs->{ci_run_url} || "",
      release_url => $proofs->{release_url} || "",
      issue_url => $proofs->{issue_url} || "",
    },
  };
}

@rows = sort {
  my @aa = split /\./, $a->{version};
  my @bb = split /\./, $b->{version};
  ($aa[0] <=> $bb[0]) || ($aa[1] <=> $bb[1]) || ($aa[2] <=> $bb[2])
} @rows;

my %seen;
for my $row (@rows) {
  die "release-index: duplicate version $row->{version}\n" if $seen{$row->{version}}++;
}

my $index = {
  schema_version => "1.0",
  title => $ENV{TITLE},
  generated_at => $ENV{GENERATED_AT},
  release_count => scalar(@rows),
  releases => \@rows,
};

open my $json_out, ">:encoding(UTF-8)", $ENV{INDEX_JSON} or die "release-index: cannot write index json: $!\n";
print {$json_out} $json->encode($index);
close $json_out;

open my $md, ">:encoding(UTF-8)", $ENV{INDEX_MD} or die "release-index: cannot write index md: $!\n";
print {$md} "# $ENV{TITLE}\n\n";
print {$md} "- Generated: $ENV{GENERATED_AT}\n";
print {$md} "- Releases: " . scalar(@rows) . "\n\n";
print {$md} "| Version | Tag | Commit | Artifact | SHA-256 | Release |\n";
print {$md} "| --- | --- | --- | --- | --- | --- |\n";
for my $row (@rows) {
  my $short = substr($row->{commit}, 0, 12);
  my $release = $row->{proofs}{release_url} || "";
  print {$md} "| $row->{version} | $row->{tag} | $short | $row->{artifact}{name} | `$row->{artifact}{sha256}` | $release |\n";
}
close $md;
' "${manifests[@]}"

  echo "wrote: $index_json"
  echo "wrote: $index_md"
}

subcommand="${1:-}"
[[ "$subcommand" == "build" ]] || fail "release-index requires subcommand: build"
shift || true
cmd_build "$@"
