#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer arena sign

Usage:
  codex-maintainer arena sign --fixture <fixture-dir> --out <manifest.json> [--pack-name <name>] [--signer <name>] [--signer-url <url>]

Outputs:
  Deterministic fixture-pack metadata with SHA-256 content digest and optional signer metadata.
USAGE
}

fail() {
  echo "arena-sign: $*" >&2
  exit 1
}

fixture_dir=""
out_file=""
pack_name=""
signer=""
signer_url=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --fixture)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--fixture requires a value"
      fixture_dir="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --pack-name)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--pack-name requires a value"
      pack_name="$2"
      shift 2
      ;;
    --signer)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--signer requires a value"
      signer="$2"
      shift 2
      ;;
    --signer-url)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--signer-url requires a value"
      signer_url="$2"
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
[[ -n "$out_file" ]] || fail "--out is required"
[[ -d "$fixture_dir" ]] || fail "fixture directory not found: $fixture_dir"
[[ -n "$pack_name" ]] || pack_name="$(basename "$fixture_dir")"

mkdir -p "$(dirname "$out_file")"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

FIXTURE_DIR="$fixture_dir" OUT_FILE="$out_file" PACK_NAME="$pack_name" GENERATED_AT="$generated_at" SIGNER="$signer" SIGNER_URL="$signer_url" perl <<'PERL'
use strict;
use warnings;
use Digest::SHA qw(sha256_hex);
use JSON::PP;

my @supported = qw(run.md task.md diff.patch tests.log);
my %supported = map { $_ => 1 } @supported;

sub fail {
  die "arena-sign: $_[0]\n";
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

sub build_identity {
  my ($pack_name, $signer, $signer_url) = @_;
  return undef unless length($signer) || length($signer_url);
  fail("--signer is required when --signer-url is set") unless length($signer);
  validate_identity_text('signer', $signer);
  if (length $signer_url) {
    validate_identity_text('signer_url', $signer_url);
    fail("signer_url must be an https URL") unless $signer_url =~ m{\Ahttps://[A-Za-z0-9][A-Za-z0-9._~:/?#\[\]\@!\$&'()*+,;=%-]*\z};
  }
  my $canonical = join("\n",
    "schema_version=1.0",
    "pack_name=$pack_name",
    "signer=$signer",
    "signer_url=$signer_url",
  ) . "\n";
  return {
    signer => $signer,
    signer_url => $signer_url,
    identity_digest => sha256_hex($canonical),
  };
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

sub build_metadata {
  my ($fixture, $pack_name) = @_;
  opendir my $dh, $fixture or fail("cannot open fixture directory: $!");
  my @case_ids = sort grep { -d "$fixture/$_" && $_ !~ /\A\./ } readdir $dh;
  closedir $dh;
  fail("fixture directory has no case subdirectories: $fixture") unless @case_ids;

  my @cases;
  my @canonical = ("schema_version=1.0", "pack_name=$pack_name");
  for my $case_id (@case_ids) {
    safe_case_id($case_id) or fail("unsafe case id: $case_id");
    my $case_dir = "$fixture/$case_id";
    fail("missing required case run file: $case_dir/run.md") unless -f "$case_dir/run.md";
    validate_case_contents($case_dir, $case_id);

    my @files;
    for my $file_name (@supported) {
      my $path = "$case_dir/$file_name";
      next unless -f $path;
      my $relative = "$case_id/$file_name";
      my $sha = file_sha($path);
      my $bytes = -s $path;
      push @files, {
        path => $relative,
        sha256 => $sha,
        bytes => $bytes + 0,
      };
      push @canonical, "$relative\t$sha\t$bytes";
    }
    push @cases, {
      id => $case_id,
      files => \@files,
    };
  }

  my $canonical_text = join("\n", @canonical) . "\n";
  return (\@cases, sha256_hex($canonical_text));
}

my ($cases, $pack_digest) = build_metadata($ENV{FIXTURE_DIR}, $ENV{PACK_NAME});
my $identity = build_identity($ENV{PACK_NAME}, $ENV{SIGNER} || '', $ENV{SIGNER_URL} || '');
my $manifest = {
  schema_version => "1.0",
  signature_type => "sha256-content-digest",
  pack_name => $ENV{PACK_NAME},
  generated_at => $ENV{GENERATED_AT},
  case_count => scalar(@$cases),
  pack_digest => $pack_digest,
  cases => $cases,
};
$manifest->{identity} = $identity if defined $identity;

open my $out, '>:encoding(UTF-8)', $ENV{OUT_FILE} or fail("cannot write manifest: $!");
print {$out} JSON::PP->new->utf8->canonical(1)->pretty->encode($manifest);
close $out;
PERL

echo "wrote: $out_file"
