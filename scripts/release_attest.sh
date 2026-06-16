#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-attest

Usage:
  codex-maintainer release-attest build --manifest <release-manifest.json> --replay <replay-report.json> --out <dir> [--title <title>]

Outputs:
  attestation.json
  attestation.md
  attestation-badge.json
USAGE
}

fail() {
  echo "release-attest: $*" >&2
  exit 1
}

cmd_build() {
  local manifest_file=""
  local replay_file=""
  local out_dir=""
  local title="Codex Maintainer Release Attestation"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --manifest)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--manifest requires a value"
        manifest_file="$2"
        shift 2
        ;;
      --replay)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--replay requires a value"
        replay_file="$2"
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

  [[ -n "$manifest_file" ]] || fail "--manifest is required"
  [[ -n "$replay_file" ]] || fail "--replay is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -f "$manifest_file" ]] || fail "manifest not found: $manifest_file"
  [[ -f "$replay_file" ]] || fail "replay report not found: $replay_file"

  mkdir -p "$out_dir"

  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  TITLE="$title" GENERATED_AT="$generated_at" TOOL_VERSION="$(sed -n '1p' "$tool_root/VERSION")" \
    MANIFEST_FILE="$manifest_file" REPLAY_FILE="$replay_file" OUT_DIR="$out_dir" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub fail {
  die "release-attest: $_[0]\n";
}

sub read_json {
  my ($file) = @_;
  open my $fh, '<:encoding(UTF-8)', $file or fail("cannot read $file: $!");
  local $/;
  my $data = decode_json(<$fh>);
  close $fh;
  return $data;
}

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
my $manifest = read_json($ENV{MANIFEST_FILE});
my $replay = read_json($ENV{REPLAY_FILE});

fail("unsupported manifest schema") unless ($manifest->{schema_version} || '') eq '1.0';
fail("unsupported replay schema") unless ($replay->{schema_version} || '') eq '1.0';
fail("replay status is not pass") unless ($replay->{status} || '') eq 'pass';
fail("replay has blocked checks") unless (($replay->{summary} || {})->{blocked} || 0) == 0;

my $artifact = $manifest->{artifact} || fail("manifest missing artifact");
my $replay_artifact = $replay->{artifact} || fail("replay missing artifact");
my $proofs = $manifest->{proofs} || {};

for my $required (qw(version tag commit)) {
  fail("manifest missing $required") unless length($manifest->{$required} || '');
  fail("replay missing $required") unless length($replay->{$required} || '');
  fail("$required mismatch") unless $manifest->{$required} eq $replay->{$required};
}

fail("manifest missing artifact name") unless length($artifact->{name} || '');
fail("manifest missing artifact sha256") unless length($artifact->{sha256} || '');
fail("manifest missing artifact bytes") unless length($artifact->{bytes} || '');
fail("artifact sha mismatch with replay actual") unless ($artifact->{sha256} || '') eq ($replay_artifact->{actual_sha256} || '');
fail("artifact sha mismatch with replay expected") unless ($artifact->{sha256} || '') eq ($replay_artifact->{expected_sha256} || '');
fail("artifact byte mismatch with replay actual") unless (0 + ($artifact->{bytes} || 0)) == (0 + ($replay_artifact->{actual_bytes} || 0));
fail("manifest missing release_url") unless length($proofs->{release_url} || '');
fail("manifest missing ci_run_url") unless length($proofs->{ci_run_url} || '');

my $summary = $replay->{summary} || {};
my $attestation = {
  schema_version => '1.0',
  title => $ENV{TITLE},
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  status => 'pass',
  statement => 'Release artifact replay proof passed with zero blocked checks.',
  version => $manifest->{version},
  tag => $manifest->{tag},
  commit => $manifest->{commit},
  artifact => {
    name => $artifact->{name},
    bytes => 0 + $artifact->{bytes},
    sha256 => $artifact->{sha256},
  },
  proofs => {
    release_url => $proofs->{release_url} || '',
    ci_run_url => $proofs->{ci_run_url} || '',
    issue_url => $proofs->{issue_url} || '',
  },
  replay_summary => {
    pass => 0 + ($summary->{pass} || 0),
    blocked => 0 + ($summary->{blocked} || 0),
    skipped => 0 + ($summary->{skipped} || 0),
  },
  inputs => {
    manifest => do { my $f = $ENV{MANIFEST_FILE}; $f =~ s{.*/}{}; $f },
    replay => do { my $f = $ENV{REPLAY_FILE}; $f =~ s{.*/}{}; $f },
  },
};

my $badge = {
  schemaVersion => 1,
  label => 'release proof',
  message => "pass v$manifest->{version}",
  color => 'brightgreen',
};

my $attestation_file = "$ENV{OUT_DIR}/attestation.json";
my $badge_file = "$ENV{OUT_DIR}/attestation-badge.json";
my $md_file = "$ENV{OUT_DIR}/attestation.md";

open my $att, '>:encoding(UTF-8)', $attestation_file or fail("cannot write attestation: $!");
print {$att} $json->encode($attestation);
close $att;

open my $badge_out, '>:encoding(UTF-8)', $badge_file or fail("cannot write badge: $!");
print {$badge_out} $json->encode($badge);
close $badge_out;

open my $md, '>:encoding(UTF-8)', $md_file or fail("cannot write markdown: $!");
print {$md} "# $ENV{TITLE}\n\n";
print {$md} "- Generated: $ENV{GENERATED_AT}\n";
print {$md} "- Status: pass\n";
print {$md} "- Version: $manifest->{version}\n";
print {$md} "- Tag: $manifest->{tag}\n";
print {$md} "- Commit: $manifest->{commit}\n";
print {$md} "- Artifact: $artifact->{name}\n";
print {$md} "- Artifact bytes: $artifact->{bytes}\n";
print {$md} "- Artifact SHA-256: $artifact->{sha256}\n";
print {$md} "- Replay checks passed: " . (0 + ($summary->{pass} || 0)) . "\n";
print {$md} "- Replay checks blocked: " . (0 + ($summary->{blocked} || 0)) . "\n";
print {$md} "- Release: $proofs->{release_url}\n";
print {$md} "- CI run: $proofs->{ci_run_url}\n";
print {$md} "- Issue: $proofs->{issue_url}\n" if length($proofs->{issue_url} || '');
print {$md} "\n## Statement\n\n";
print {$md} "Release artifact replay proof passed with zero blocked checks.\n";
close $md;

print "wrote: $attestation_file\n";
print "wrote: $md_file\n";
print "wrote: $badge_file\n";
PERL
}

subcommand="${1:-}"
[[ "$subcommand" == "build" ]] || fail "release-attest requires subcommand: build"
shift || true
cmd_build "$@"
