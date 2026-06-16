#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer sarif

Usage:
  codex-maintainer sarif --report <report.json> --out <results.sarif>

Outputs:
  SARIF 2.1.0 file containing autopsy findings.
USAGE
}

fail() {
  echo "sarif: $*" >&2
  exit 1
}

report_file=""
out_file=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --report)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--report requires a value"
      report_file="$2"
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

[[ -n "$report_file" ]] || fail "--report is required"
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$report_file" ]] || fail "report file not found: $report_file"

mkdir -p "$(dirname "$out_file")"
tool_version="$(sed -n '1p' "$tool_root/VERSION")"

REPORT_FILE="$report_file" OUT_FILE="$out_file" TOOL_VERSION="$tool_version" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub level_for {
  my ($severity) = @_;
  return 'error' if defined $severity && $severity eq 'high';
  return 'warning' if defined $severity && $severity eq 'medium';
  return 'note';
}

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
open my $in, '<:encoding(UTF-8)', $ENV{REPORT_FILE} or die "cannot read report: $!";
local $/;
my $report = decode_json(<$in>);
close $in;

my $inputs = $report->{inputs} || {};
my $score = $report->{score} || {};
my $run_uri = $inputs->{run} || $ENV{REPORT_FILE};
my @findings = @{ $report->{findings} || [] };

my %rule_seen;
my @rules;
for my $finding (@findings) {
  my $id = $finding->{id} || 'autopsy_finding';
  next if $rule_seen{$id}++;
  push @rules, {
    id => $id,
    name => $id,
    shortDescription => { text => $finding->{message} || $id },
    fullDescription => { text => $finding->{message} || $id },
    defaultConfiguration => { level => level_for($finding->{severity}) },
    properties => {
      severity => $finding->{severity} || 'unknown',
    },
  };
}

my @results = map {
  my $finding = $_;
  {
    ruleId => $finding->{id} || 'autopsy_finding',
    level => level_for($finding->{severity}),
    message => { text => $finding->{message} || 'Autopsy finding.' },
    locations => [
      {
        physicalLocation => {
          artifactLocation => { uri => $run_uri },
          region => { startLine => 1 },
        },
      },
    ],
    properties => {
      severity => $finding->{severity} || 'unknown',
      evidence => $finding->{evidence} || '',
      verdict => $score->{verdict} || '',
    },
  }
} @findings;

my $sarif = {
  '$schema' => 'https://json.schemastore.org/sarif-2.1.0.json',
  version => '2.1.0',
  runs => [
    {
      tool => {
        driver => {
          name => 'codex-maintainer',
          informationUri => 'https://github.com/jlekerli-source/ringly-codex-workflows',
          semanticVersion => $ENV{TOOL_VERSION},
          rules => \@rules,
        },
      },
      automationDetails => { id => 'codex-maintainer/autopsy' },
      invocations => [
        {
          executionSuccessful => JSON::PP::true,
          endTimeUtc => $report->{generated_at} || undef,
        },
      ],
      results => \@results,
      properties => {
        autopsySchemaVersion => $report->{schema_version} || '',
        autopsyVerdict => $score->{verdict} || '',
        score => $score->{total} || 0,
        maxScore => $score->{max} || 12,
        findingCount => scalar @findings,
      },
    },
  ],
};

open my $out, '>:encoding(UTF-8)', $ENV{OUT_FILE} or die "cannot write SARIF: $!";
print {$out} $json->encode($sarif);
close $out;
PERL

echo "wrote: $out_file"
