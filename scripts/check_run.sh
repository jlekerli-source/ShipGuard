#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer check-run

Usage:
  codex-maintainer check-run --gate <gate.json> --head-sha <sha> --out <payload.json> [--name <name>]

Outputs:
  GitHub Checks API payload JSON.
USAGE
}

fail() {
  echo "check-run: $*" >&2
  exit 1
}

gate_file=""
head_sha=""
out_file=""
check_name="Codex Maintainer Gate"

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
