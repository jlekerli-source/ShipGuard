#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-consume

Usage:
  codex-maintainer release-consume verify --dir <downloaded-assets-dir> --out <dir> [--version <version>]

Inputs in --dir:
  codex-maintainer-vX.Y.Z.tar.gz
  release-manifest.json
  release-index.json
  proof-ledger.md

Outputs:
  consumer-report.json
  consumer-report.md
  sha256.txt
  replay/replay-report.json
  replay/replay-report.md
  attestation/attestation.json
  attestation/attestation.md
  attestation/attestation-badge.json
USAGE
}

fail() {
  echo "release-consume: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

cmd_verify() {
  local asset_dir=""
  local out_dir=""
  local expected_version=""

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --dir)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--dir requires a value"
        asset_dir="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
        shift 2
        ;;
      --version)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--version requires a value"
        expected_version="$2"
        [[ "$expected_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "--version must be semantic"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown verify argument: $1"
        ;;
    esac
  done

  [[ -n "$asset_dir" ]] || fail "--dir is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$asset_dir" ]] || fail "asset directory not found: $asset_dir"

  local manifest_file="$asset_dir/release-manifest.json"
  local index_file="$asset_dir/release-index.json"
  local ledger_file="$asset_dir/proof-ledger.md"
  [[ -f "$manifest_file" ]] || fail "missing release-manifest.json in $asset_dir"
  [[ -f "$index_file" ]] || fail "missing release-index.json in $asset_dir"
  [[ -f "$ledger_file" ]] || fail "missing proof-ledger.md in $asset_dir"

  local manifest_fields
  manifest_fields="$(MANIFEST_FILE="$manifest_file" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub fail {
  die "release-consume: $_[0]\n";
}

open my $fh, '<:encoding(UTF-8)', $ENV{MANIFEST_FILE} or fail("cannot read manifest: $!");
local $/;
my $manifest = decode_json(<$fh>);
close $fh;

fail("unsupported manifest schema") unless ($manifest->{schema_version} || '') eq '1.0';
my $artifact = $manifest->{artifact} || fail("manifest missing artifact");
for my $required (qw(version tag commit)) {
  fail("manifest missing $required") unless length($manifest->{$required} || '');
}
for my $required (qw(name sha256 bytes)) {
  fail("manifest missing artifact $required") unless length($artifact->{$required} || '');
}

my $proofs = $manifest->{proofs} || {};
print join("\t",
  $manifest->{version},
  $manifest->{tag},
  $manifest->{commit},
  $artifact->{name},
  $artifact->{sha256},
  $artifact->{bytes},
  $proofs->{release_url} || '',
  $proofs->{ci_run_url} || '',
  $proofs->{issue_url} || '',
), "\n";
PERL
)"

  local version tag commit artifact_name artifact_sha artifact_bytes release_url ci_run_url issue_url
  IFS=$'\t' read -r version tag commit artifact_name artifact_sha artifact_bytes release_url ci_run_url issue_url <<< "$manifest_fields"

  if [[ -n "$expected_version" && "$expected_version" != "$version" ]]; then
    fail "expected version $expected_version but manifest has $version"
  fi

  local tarball="$asset_dir/$artifact_name"
  [[ -f "$tarball" ]] || fail "missing release tarball: $tarball"

  mkdir -p "$out_dir"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"
  local sha_file="$out_dir/sha256.txt"
  local replay_dir="$out_dir/replay"
  local attestation_dir="$out_dir/attestation"
  local report_json="$out_dir/consumer-report.json"
  local report_md="$out_dir/consumer-report.md"

  local actual_sha
  actual_sha="$(shasum -a 256 "$tarball" | awk '{print $1}')"
  printf '%s  %s\n' "$actual_sha" "$artifact_name" > "$sha_file"

  if [[ "$actual_sha" != "$artifact_sha" ]]; then
    fail "tarball sha256 mismatch: expected $artifact_sha, got $actual_sha"
  fi

  "$tool_root/bin/codex-maintainer" release-replay verify \
    --manifest "$manifest_file" \
    --tarball "$tarball" \
    --index "$index_file" \
    --ledger "$ledger_file" \
    --out "$replay_dir" >/dev/null

  "$tool_root/bin/codex-maintainer" release-attest build \
    --manifest "$manifest_file" \
    --replay "$replay_dir/replay-report.json" \
    --out "$attestation_dir" >/dev/null

  local replay_fields
  replay_fields="$(REPLAY_FILE="$replay_dir/replay-report.json" ATTESTATION_FILE="$attestation_dir/attestation.json" BADGE_FILE="$attestation_dir/attestation-badge.json" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub read_json {
  my ($file) = @_;
  open my $fh, '<:encoding(UTF-8)', $file or die "release-consume: cannot read $file: $!\n";
  local $/;
  my $data = decode_json(<$fh>);
  close $fh;
  return $data;
}

my $replay = read_json($ENV{REPLAY_FILE});
my $attestation = read_json($ENV{ATTESTATION_FILE});
my $badge = read_json($ENV{BADGE_FILE});

print join("\t",
  $replay->{status} || '',
  ($replay->{summary} || {})->{blocked} || 0,
  ($replay->{summary} || {})->{pass} || 0,
  $attestation->{status} || '',
  (($attestation->{replay_summary} || {})->{blocked} || 0),
  $badge->{message} || '',
), "\n";
PERL
)"

  local replay_status replay_blocked replay_pass attestation_status attestation_blocked badge_message
  IFS=$'\t' read -r replay_status replay_blocked replay_pass attestation_status attestation_blocked badge_message <<< "$replay_fields"

  local status="pass"
  if [[ "$replay_status" != "pass" || "$replay_blocked" != "0" || "$attestation_status" != "pass" || "$attestation_blocked" != "0" ]]; then
    status="blocked"
  fi

  {
    echo "{"
    echo "  \"schema_version\": \"1.0\","
    echo "  \"tool_version\": $(json_string "$(sed -n '1p' "$tool_root/VERSION")"),"
    echo "  \"generated_at\": $(json_string "$generated_at"),"
    echo "  \"status\": $(json_string "$status"),"
    echo "  \"version\": $(json_string "$version"),"
    echo "  \"tag\": $(json_string "$tag"),"
    echo "  \"commit\": $(json_string "$commit"),"
    echo "  \"artifact\": {"
    echo "    \"name\": $(json_string "$artifact_name"),"
    echo "    \"bytes\": $artifact_bytes,"
    echo "    \"sha256\": $(json_string "$artifact_sha")"
    echo "  },"
    echo "  \"proofs\": {"
    echo "    \"release_url\": $(json_string "$release_url"),"
    echo "    \"ci_run_url\": $(json_string "$ci_run_url"),"
    echo "    \"issue_url\": $(json_string "$issue_url")"
    echo "  },"
    echo "  \"outputs\": {"
    echo "    \"sha256\": \"sha256.txt\","
    echo "    \"replay\": \"replay/replay-report.json\","
    echo "    \"attestation\": \"attestation/attestation.json\","
    echo "    \"attestation_badge\": \"attestation/attestation-badge.json\""
    echo "  },"
    echo "  \"summary\": {"
    echo "    \"replay_status\": $(json_string "$replay_status"),"
    echo "    \"replay_pass\": $replay_pass,"
    echo "    \"replay_blocked\": $replay_blocked,"
    echo "    \"attestation_status\": $(json_string "$attestation_status"),"
    echo "    \"attestation_blocked\": $attestation_blocked,"
    echo "    \"badge_message\": $(json_string "$badge_message")"
    echo "  }"
    echo "}"
  } > "$report_json"

  {
    echo "# Release Proof Consumer Report"
    echo
    echo "- Generated: $generated_at"
    echo "- Status: $status"
    echo "- Version: $version"
    echo "- Tag: $tag"
    echo "- Commit: $commit"
    echo "- Artifact: $artifact_name"
    echo "- Artifact SHA-256: $artifact_sha"
    echo "- Replay status: $replay_status"
    echo "- Replay blocked checks: $replay_blocked"
    echo "- Attestation status: $attestation_status"
    echo "- Attestation blocked checks: $attestation_blocked"
    echo "- Badge: $badge_message"
    [[ -n "$release_url" ]] && echo "- Release: $release_url"
    [[ -n "$ci_run_url" ]] && echo "- CI run: $ci_run_url"
    [[ -n "$issue_url" ]] && echo "- Issue: $issue_url"
    echo
    echo "## Outputs"
    echo
    echo "- SHA-256: \`sha256.txt\`"
    echo "- Replay: \`replay/replay-report.json\`"
    echo "- Attestation: \`attestation/attestation.json\`"
    echo "- Badge: \`attestation/attestation-badge.json\`"
  } > "$report_md"

  echo "wrote: $report_json"
  echo "wrote: $report_md"
  echo "status: $status"

  [[ "$status" == "pass" ]] || exit 1
}

subcommand="${1:-}"
[[ "$subcommand" == "verify" ]] || fail "release-consume requires subcommand: verify"
shift || true
cmd_verify "$@"
