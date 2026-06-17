#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
shipguard check-run

Usage:
  shipguard check-run --gate <gate.json> --head-sha <sha> --out <payload.json> [--name <name>]
  shipguard check-run post --payload <payload.json> --repo <owner/repo> --out <response.json> [--api-url <url>] [--token <token>] [--dry-run]

Outputs:
  GitHub Checks API payload JSON.
  Optional GitHub Checks API post response JSON.
USAGE
}

fail() {
  echo "check-run: $*" >&2
  exit 1
}

cmd_payload() {
gate_file=""
head_sha=""
out_file=""
check_name="ShipGuard Gate"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --gate)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--gate requires a value"
      gate_file="$2"
      shift 2
      ;;
    --head-sha)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--head-sha requires a value"
      head_sha="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --name)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--name requires a value"
      check_name="$2"
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

[[ -n "$gate_file" ]] || fail "--gate is required"
[[ -n "$head_sha" ]] || fail "--head-sha is required"
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$gate_file" ]] || fail "gate file not found: $gate_file"

mkdir -p "$(dirname "$out_file")"

GATE_FILE="$gate_file" HEAD_SHA="$head_sha" OUT_FILE="$out_file" CHECK_NAME="$check_name" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub conclusion_for {
  my ($status) = @_;
  return 'success' if defined $status && $status eq 'pass';
  return 'failure' if defined $status && $status eq 'blocked';
  return 'neutral';
}

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
open my $in, '<:encoding(UTF-8)', $ENV{GATE_FILE} or die "cannot read gate: $!";
local $/;
my $gate = decode_json(<$in>);
close $in;

my $status = $gate->{status} || 'unknown';
my $score = defined $gate->{score} ? $gate->{score} : 0;
my $max = defined $gate->{max} ? $gate->{max} : 12;
my $high = defined $gate->{high_risk_findings} ? $gate->{high_risk_findings} : 0;
my $summary = "Status: $status\nScore: $score/$max\nHigh-risk findings: $high\nMode: " . ($gate->{mode} || 'warn');
my $text = "Artifacts:\n";
for my $field (qw(autopsy_report sarif review_comment badge summary)) {
  next unless defined $gate->{$field} && length $gate->{$field};
  $text .= "- $field: `$gate->{$field}`\n";
}

my $payload = {
  name => $ENV{CHECK_NAME},
  head_sha => $ENV{HEAD_SHA},
  status => 'completed',
  conclusion => conclusion_for($status),
  output => {
    title => "$ENV{CHECK_NAME}: $status",
    summary => $summary,
    text => $text,
  },
};

open my $out, '>:encoding(UTF-8)', $ENV{OUT_FILE} or die "cannot write check-run payload: $!";
print {$out} $json->encode($payload);
close $out;
PERL

echo "wrote: $out_file"
}

cmd_post() {
  local payload_file=""
  local repo="${GITHUB_REPOSITORY:-}"
  local out_file=""
  local api_url="${GITHUB_API_URL:-https://api.github.com}"
  local token="${GITHUB_TOKEN:-}"
  local dry_run="false"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --payload)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--payload requires a value"
        payload_file="$2"
        shift 2
        ;;
      --repo)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--repo requires a value"
        repo="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_file="$2"
        shift 2
        ;;
      --api-url)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--api-url requires a value"
        api_url="$2"
        shift 2
        ;;
      --token)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--token requires a value"
        token="$2"
        shift 2
        ;;
      --dry-run)
        dry_run="true"
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown post argument: $1"
        ;;
    esac
  done

  [[ -n "$payload_file" ]] || fail "--payload is required"
  [[ -n "$repo" ]] || fail "--repo is required"
  [[ -n "$out_file" ]] || fail "--out is required"
  [[ -f "$payload_file" ]] || fail "payload file not found: $payload_file"
  [[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || fail "--repo must look like owner/repo"

  api_url="${api_url%/}"
  local endpoint="$api_url/repos/$repo/check-runs"
  mkdir -p "$(dirname "$out_file")"

  if [[ "$dry_run" == "true" ]]; then
    PAYLOAD_FILE="$payload_file" OUT_FILE="$out_file" ENDPOINT="$endpoint" TOKEN_PRESENT="$([[ -n "$token" ]] && echo true || echo false)" perl <<'PERL'
use strict;
use warnings;
use Digest::SHA qw(sha256_hex);
use JSON::PP;

sub file_sha {
  my ($path) = @_;
  open my $fh, '<:raw', $path or die "cannot read payload: $!";
  my $ctx = Digest::SHA->new(256);
  $ctx->addfile($fh);
  close $fh;
  return $ctx->hexdigest;
}

my $payload = {
  dry_run => JSON::PP::true,
  method => 'POST',
  url => $ENV{ENDPOINT},
  payload_file => $ENV{PAYLOAD_FILE},
  payload_sha256 => file_sha($ENV{PAYLOAD_FILE}),
  token_present => (($ENV{TOKEN_PRESENT} || '') eq 'true' ? JSON::PP::true : JSON::PP::false),
  headers => [
    'Accept: application/vnd.github+json',
    'X-GitHub-Api-Version: 2022-11-28',
    'Authorization: Bearer <redacted>',
  ],
};

open my $out, '>:encoding(UTF-8)', $ENV{OUT_FILE} or die "cannot write dry-run response: $!";
print {$out} JSON::PP->new->utf8->canonical(1)->pretty->encode($payload);
close $out;
PERL
    echo "dry-run: $endpoint"
    echo "wrote: $out_file"
    return 0
  fi

  [[ -n "$token" ]] || fail "--token or GITHUB_TOKEN is required unless --dry-run is set"
  command -v curl >/dev/null 2>&1 || fail "curl is required to post check runs"

  curl -fsS \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $token" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    --data-binary "@$payload_file" \
    "$endpoint" \
    -o "$out_file"

  echo "posted: $endpoint"
  echo "wrote: $out_file"
}

if [[ "${1:-}" == "post" ]]; then
  shift
  cmd_post "$@"
else
  cmd_payload "$@"
fi
