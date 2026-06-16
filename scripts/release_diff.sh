#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-diff

Usage:
  codex-maintainer release-diff compare --left <release-assets-dir> --right <release-assets-dir> --out <dir>

Inputs:
  Directories may contain flat GitHub release assets or a nested release-proof bundle.

Outputs:
  release-diff.json
  release-diff.md
USAGE
}

fail() {
  echo "release-diff: $*" >&2
  exit 1
}

cmd_compare() {
  local left_dir=""
  local right_dir=""
  local out_dir=""

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --left)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--left requires a value"
        left_dir="$2"
        shift 2
        ;;
      --right)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--right requires a value"
        right_dir="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown compare argument: $1"
        ;;
    esac
  done

  [[ -n "$left_dir" ]] || fail "--left is required"
  [[ -n "$right_dir" ]] || fail "--right is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$left_dir" ]] || fail "left directory not found: $left_dir"
  [[ -d "$right_dir" ]] || fail "right directory not found: $right_dir"

  mkdir -p "$out_dir"

  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  LEFT_DIR="$left_dir" RIGHT_DIR="$right_dir" OUT_DIR="$out_dir" \
    TOOL_VERSION="$tool_version" GENERATED_AT="$generated_at" perl <<'PERL'
use strict;
use warnings;
use Digest::SHA qw(sha256_hex);
use File::Basename qw(basename);
use File::Spec;
use JSON::PP;

sub fail {
  die "release-diff: $_[0]\n";
}

sub slurp_json {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or fail("cannot read $path: $!");
  local $/;
  my $raw = <$fh>;
  close $fh;
  return decode_json($raw);
}

sub first_existing {
  my ($dir, @rel_paths) = @_;
  for my $rel (@rel_paths) {
    my $path = File::Spec->catfile($dir, split m{/}, $rel);
    return ($path, $rel) if -f $path;
  }
  return ('', '');
}

sub file_meta {
  my ($path, $rel) = @_;
  return undef unless length $path && -f $path;
  open my $fh, '<:raw', $path or fail("cannot read $path: $!");
  local $/;
  my $bytes = <$fh>;
  close $fh;
  return {
    status => 'present',
    path => $rel,
    name => basename($path),
    bytes => length($bytes),
    sha256 => sha256_hex($bytes),
  };
}

sub missing_meta {
  return {
    status => 'missing',
    path => JSON::PP::null,
    name => JSON::PP::null,
    bytes => JSON::PP::null,
    sha256 => JSON::PP::null,
  };
}

sub manifest_path {
  my ($dir) = @_;
  my ($path, $rel) = first_existing($dir, 'release-manifest.json', 'proof/release-manifest.json');
  fail("missing release-manifest.json in $dir") unless length $path;
  return ($path, $rel);
}

sub read_manifest {
  my ($dir, $side) = @_;
  my ($path, $rel) = manifest_path($dir);
  my $manifest = slurp_json($path);
  fail("$side manifest has unsupported schema") unless ($manifest->{schema_version} || '') eq '1.0';
  my $artifact = $manifest->{artifact} || fail("$side manifest missing artifact");
  for my $field (qw(version tag commit)) {
    fail("$side manifest missing $field") unless length($manifest->{$field} || '');
  }
  for my $field (qw(name sha256 bytes)) {
    fail("$side manifest missing artifact $field") unless length($artifact->{$field} || '');
  }
  return ($manifest, $path, $rel);
}

sub asset_candidates {
  my ($key, $artifact_name) = @_;
  return ($artifact_name) if $key eq 'tarball';
  return ('release-manifest.json', 'proof/release-manifest.json') if $key eq 'release-manifest';
  return ('release-index.json', 'index/release-index.json') if $key eq 'release-index-json';
  return ('release-index.md', 'index/release-index.md') if $key eq 'release-index-md';
  return ('proof-ledger.md', 'proof/proof-ledger.md') if $key eq 'proof-ledger';
  return ('replay-report.json', 'replay/replay-report.json') if $key eq 'replay-json';
  return ('replay-report.md', 'replay/replay-report.md') if $key eq 'replay-md';
  return ('attestation.json', 'attestation/attestation.json') if $key eq 'attestation-json';
  return ('attestation.md', 'attestation/attestation.md') if $key eq 'attestation-md';
  return ('attestation-badge.json', 'attestation/attestation-badge.json') if $key eq 'attestation-badge';
  fail("unknown asset key: $key");
}

sub side_asset {
  my ($dir, $key, $artifact_name) = @_;
  my ($path, $rel) = first_existing($dir, asset_candidates($key, $artifact_name));
  return file_meta($path, $rel) || missing_meta();
}

my $left_dir = $ENV{LEFT_DIR};
my $right_dir = $ENV{RIGHT_DIR};
my $out_dir = $ENV{OUT_DIR};
my ($left_manifest) = read_manifest($left_dir, 'left');
my ($right_manifest) = read_manifest($right_dir, 'right');

my @assets = (
  { key => 'tarball', role => 'release tarball', required => 1 },
  { key => 'release-manifest', role => 'release manifest', required => 1 },
  { key => 'release-index-json', role => 'release index json', required => 1 },
  { key => 'release-index-md', role => 'release index markdown', required => 0 },
  { key => 'proof-ledger', role => 'proof ledger', required => 1 },
  { key => 'replay-json', role => 'replay report json', required => 0 },
  { key => 'replay-md', role => 'replay report markdown', required => 0 },
  { key => 'attestation-json', role => 'attestation json', required => 0 },
  { key => 'attestation-md', role => 'attestation markdown', required => 0 },
  { key => 'attestation-badge', role => 'attestation badge', required => 0 },
);

my @rows;
my %summary = (
  changed => 0,
  unchanged => 0,
  added => 0,
  removed => 0,
  missing_both => 0,
  required_missing => 0,
);

for my $asset (@assets) {
  my $left = side_asset($left_dir, $asset->{key}, $left_manifest->{artifact}{name});
  my $right = side_asset($right_dir, $asset->{key}, $right_manifest->{artifact}{name});
  my $change;
  if ($left->{status} eq 'present' && $right->{status} eq 'present') {
    $change = ($left->{sha256} eq $right->{sha256} && $left->{bytes} == $right->{bytes}) ? 'unchanged' : 'changed';
  } elsif ($left->{status} eq 'missing' && $right->{status} eq 'present') {
    $change = 'added';
  } elsif ($left->{status} eq 'present' && $right->{status} eq 'missing') {
    $change = 'removed';
  } else {
    $change = 'missing-both';
  }

  $summary{$change =~ s/-/_/r}++;
  if ($asset->{required} && ($left->{status} ne 'present' || $right->{status} ne 'present')) {
    $summary{required_missing}++;
  }

  push @rows, {
    role => $asset->{role},
    key => $asset->{key},
    required => $asset->{required} ? JSON::PP::true : JSON::PP::false,
    change => $change,
    left => $left,
    right => $right,
  };
}

my $status = $summary{required_missing} ? 'blocked' : 'pass';
my $report = {
  schema_version => '1.0',
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  status => $status,
  left => {
    version => $left_manifest->{version},
    tag => $left_manifest->{tag},
    commit => $left_manifest->{commit},
    artifact => $left_manifest->{artifact},
  },
  right => {
    version => $right_manifest->{version},
    tag => $right_manifest->{tag},
    commit => $right_manifest->{commit},
    artifact => $right_manifest->{artifact},
  },
  summary => {
    asset_count => scalar(@rows),
    changed => $summary{changed},
    unchanged => $summary{unchanged},
    added => $summary{added},
    removed => $summary{removed},
    missing_both => $summary{missing_both},
    required_missing => $summary{required_missing},
    artifact_changed => ($left_manifest->{artifact}{sha256} ne $right_manifest->{artifact}{sha256} ? JSON::PP::true : JSON::PP::false),
  },
  assets => \@rows,
};

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
my $json_path = File::Spec->catfile($out_dir, 'release-diff.json');
open my $json_fh, '>:encoding(UTF-8)', $json_path or fail("cannot write $json_path: $!");
print {$json_fh} $json->encode($report);
close $json_fh;

sub display {
  my ($value) = @_;
  return '-' if !defined($value) || ref($value);
  return "$value";
}

my $md_path = File::Spec->catfile($out_dir, 'release-diff.md');
open my $md, '>:encoding(UTF-8)', $md_path or fail("cannot write $md_path: $!");
print {$md} "# Release Diff Audit\n\n";
print {$md} "- Generated: $ENV{GENERATED_AT}\n";
print {$md} "- Status: $status\n";
print {$md} "- Left: $left_manifest->{version} ($left_manifest->{tag})\n";
print {$md} "- Right: $right_manifest->{version} ($right_manifest->{tag})\n";
print {$md} "- Changed assets: $summary{changed}\n";
print {$md} "- Added assets: $summary{added}\n";
print {$md} "- Removed assets: $summary{removed}\n";
print {$md} "- Required missing: $summary{required_missing}\n\n";
print {$md} "## Assets\n\n";
print {$md} "| Role | Required | Change | Left asset | Right asset | Left bytes | Right bytes | Left SHA-256 | Right SHA-256 |\n";
print {$md} "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |\n";
for my $row (@rows) {
  print {$md} "| $row->{role} | " . ($row->{required} ? 'true' : 'false') . " | $row->{change} | "
    . display($row->{left}{path}) . " | "
    . display($row->{right}{path}) . " | "
    . display($row->{left}{bytes}) . " | "
    . display($row->{right}{bytes}) . " | "
    . display($row->{left}{sha256}) . " | "
    . display($row->{right}{sha256}) . " |\n";
}
close $md;

print "wrote: $json_path\n";
print "wrote: $md_path\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
}

subcommand="${1:-}"
[[ "$subcommand" == "compare" ]] || fail "release-diff requires subcommand: compare"
shift || true
cmd_compare "$@"
