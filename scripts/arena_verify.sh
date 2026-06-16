#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer arena verify

Usage:
  codex-maintainer arena verify --fixture <fixture-dir> --manifest <manifest.json>

Verifies:
  case files, SHA-256 digests, file sizes, pack digest, and optional signer metadata digest.
USAGE
}

fail() {
  echo "arena-verify: $*" >&2
  exit 1
}

fixture_dir=""
manifest_file=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --fixture)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--fixture requires a value"
      fixture_dir="$2"
      shift 2
      ;;
    --manifest)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--manifest requires a value"
      manifest_file="$2"
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

[[ -n "$fixture_dir" ]] || fail "--fixture is required"
[[ -n "$manifest_file" ]] || fail "--manifest is required"
[[ -d "$fixture_dir" ]] || fail "fixture directory not found: $fixture_dir"
[[ -f "$manifest_file" ]] || fail "manifest file not found: $manifest_file"

FIXTURE_DIR="$fixture_dir" MANIFEST_FILE="$manifest_file" perl <<'PERL'
use strict;
use warnings;
use Digest::SHA qw(sha256_hex);
use JSON::PP;

my @supported = qw(run.md task.md diff.patch tests.log);
my %supported = map { $_ => 1 } @supported;

sub fail {
  die "arena-verify: $_[0]\n";
}

sub file_sha {
  my ($path) = @_;
  open my $fh, '<:raw', $path or fail("cannot read $path: $!");
  my $ctx = Digest::SHA->new(256);
  $ctx->addfile($fh);
  close $fh;
  return $ctx->hexdigest;
}

sub safe_case_id {
  my ($case_id) = @_;
  return $case_id =~ /\A[A-Za-z0-9._-]+\z/;
}

sub validate_identity_text {
  my ($field, $value) = @_;
  fail("$field cannot contain newlines or tabs") if $value =~ /[\r\n\t]/;
  fail("$field contains an email address") if $value =~ /[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/;
  fail("$field contains a secret-looking token") if $value =~ /\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+(?!\[redacted-secret\])[A-Za-z0-9._~+\/=-]{16,})\b/;
  fail("$field contains a secret-looking assignment") if $value =~ /\b[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*=(?!\[redacted-secret\])\S+/i;
  fail("$field contains a local home path") if $value =~ m{/(?:Users|home)/(?!\[redacted-user\])[A-Za-z0-9._-]+};
}

sub verify_identity {
  my ($manifest, $pack_name) = @_;
  my $identity = $manifest->{identity};
  return unless defined $identity;
  fail("identity must be an object") unless ref($identity) eq 'HASH';
  my $signer = $identity->{signer} || '';
  my $signer_url = $identity->{signer_url} || '';
  my $identity_digest = $identity->{identity_digest} || '';
  fail("identity signer is required") unless length $signer;
  validate_identity_text('identity signer', $signer);
  if (length $signer_url) {
    validate_identity_text('identity signer_url', $signer_url);
    fail("identity signer_url must be an https URL") unless $signer_url =~ m{\Ahttps://[A-Za-z0-9][A-Za-z0-9._~:/?#\[\]\@!\$&'()*+,;=%-]*\z};
  }
  my $canonical = join("\n",
    "schema_version=1.0",
    "pack_name=$pack_name",
    "signer=$signer",
    "signer_url=$signer_url",
  ) . "\n";
  fail("identity digest mismatch") unless $identity_digest eq sha256_hex($canonical);
}

sub validate_case_contents {
  my ($case_dir, $case_id) = @_;
  opendir my $dh, $case_dir or fail("cannot open case directory: $case_dir: $!");
  my @entries = sort grep { $_ !~ /\A\./ } readdir $dh;
  closedir $dh;

  for my $entry (@entries) {
    my $path = "$case_dir/$entry";
    fail("unsupported nested directory in fixture case: $case_id/$entry") if -d $path;
    fail("unsupported fixture case file: $case_id/$entry") unless $supported{$entry};
  }
}

sub build_actual {
  my ($fixture, $pack_name) = @_;
  opendir my $dh, $fixture or fail("cannot open fixture directory: $!");
  my @case_ids = sort grep { -d "$fixture/$_" && $_ !~ /\A\./ } readdir $dh;
  closedir $dh;
  fail("fixture directory has no case subdirectories: $fixture") unless @case_ids;

  my %files;
  my @canonical = ("schema_version=1.0", "pack_name=$pack_name");
  for my $case_id (@case_ids) {
    safe_case_id($case_id) or fail("unsafe case id: $case_id");
    my $case_dir = "$fixture/$case_id";
    fail("missing required case run file: $case_dir/run.md") unless -f "$case_dir/run.md";
    validate_case_contents($case_dir, $case_id);

    for my $file_name (@supported) {
      my $path = "$case_dir/$file_name";
      next unless -f $path;
      my $relative = "$case_id/$file_name";
      my $sha = file_sha($path);
      my $bytes = -s $path;
      $files{$relative} = {
        sha256 => $sha,
        bytes => $bytes + 0,
      };
      push @canonical, "$relative\t$sha\t$bytes";
    }
  }

  my $canonical_text = join("\n", @canonical) . "\n";
  return (\%files, scalar(@case_ids), sha256_hex($canonical_text));
}

open my $in, '<:encoding(UTF-8)', $ENV{MANIFEST_FILE} or fail("cannot read manifest: $!");
local $/;
my $manifest = decode_json(<$in>);
close $in;

fail("unsupported manifest schema") unless ($manifest->{schema_version} || '') eq '1.0';
fail("unsupported signature type") unless ($manifest->{signature_type} || '') eq 'sha256-content-digest';
my $pack_name = $manifest->{pack_name} || fail("manifest missing pack_name");
verify_identity($manifest, $pack_name);
my ($actual_files, $actual_case_count, $actual_digest) = build_actual($ENV{FIXTURE_DIR}, $pack_name);

fail("case_count mismatch") unless ($manifest->{case_count} || 0) == $actual_case_count;
fail("pack digest mismatch") unless ($manifest->{pack_digest} || '') eq $actual_digest;

my %expected;
for my $case (@{ $manifest->{cases} || [] }) {
  my $case_id = $case->{id} || fail("manifest case missing id");
  safe_case_id($case_id) or fail("unsafe manifest case id: $case_id");
  for my $file (@{ $case->{files} || [] }) {
    my $path = $file->{path} || fail("manifest file missing path");
    $expected{$path} = {
      sha256 => $file->{sha256} || '',
      bytes => $file->{bytes} || 0,
    };
  }
}

for my $path (sort keys %expected) {
  fail("manifest file missing from fixture: $path") unless exists $actual_files->{$path};
  fail("sha256 mismatch: $path") unless $expected{$path}{sha256} eq $actual_files->{$path}{sha256};
  fail("byte count mismatch: $path") unless $expected{$path}{bytes} == $actual_files->{$path}{bytes};
}

for my $path (sort keys %$actual_files) {
  fail("fixture has file not present in manifest: $path") unless exists $expected{$path};
}
PERL

echo "verified: $manifest_file"
