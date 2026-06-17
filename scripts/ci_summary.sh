#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
shipguard ci-summary

Usage:
  shipguard ci-summary --gate <gate.json> --out <summary.md>

Outputs:
  GitHub Actions step-summary compatible Markdown.
USAGE
}

fail() {
  echo "ci-summary: $*" >&2
  exit 1
}

gate_file=""
out_file=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --gate)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--gate requires a value"
      gate_file="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
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
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$gate_file" ]] || fail "gate file not found: $gate_file"

mkdir -p "$(dirname "$out_file")"

GATE_FILE="$gate_file" OUT_FILE="$out_file" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

open my $in, '<:encoding(UTF-8)', $ENV{GATE_FILE} or die "cannot read gate: $!";
local $/;
my $gate = decode_json(<$in>);
close $in;

my $status = $gate->{status} || 'unknown';
my $score = defined $gate->{score} ? $gate->{score} : 0;
my $max = defined $gate->{max} ? $gate->{max} : 12;
my $high = defined $gate->{high_risk_findings} ? $gate->{high_risk_findings} : 0;
my $mode = $gate->{mode} || 'warn';

open my $out, '>:encoding(UTF-8)', $ENV{OUT_FILE} or die "cannot write summary: $!";
print {$out} "# ShipGuard Gate\n\n";
print {$out} "| Field | Value |\n";
print {$out} "| --- | --- |\n";
print {$out} "| Status | $status |\n";
print {$out} "| Mode | $mode |\n";
print {$out} "| Score | $score/$max |\n";
print {$out} "| High-risk findings | $high |\n";
print {$out} "| Warn below | " . ($gate->{warn_below} // '') . " |\n";
print {$out} "| Fail below | " . ($gate->{fail_below} // '') . " |\n";
print {$out} "\n## Artifacts\n\n";
for my $field (qw(autopsy_report sarif review_comment badge)) {
  next unless defined $gate->{$field} && length $gate->{$field};
  my $label = $field;
  $label =~ s/_/ /g;
  print {$out} "- $label: `$gate->{$field}`\n";
}
close $out;
PERL

echo "wrote: $out_file"
