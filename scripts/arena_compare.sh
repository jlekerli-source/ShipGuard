#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer arena compare

Usage:
  codex-maintainer arena compare --left <results.json> --right <results.json> --out <dir> [--title <title>]

Outputs:
  arena-compare.json
  arena-compare.md
USAGE
}

fail() {
  echo "arena-compare: $*" >&2
  exit 1
}

left_results=""
right_results=""
out_dir=""
title="Maintainer Arena Compare"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --left)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--left requires a value"
      left_results="$2"
      shift 2
      ;;
    --right)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--right requires a value"
      right_results="$2"
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
      fail "unknown argument: $1"
      ;;
  esac
done

[[ -n "$left_results" ]] || fail "--left is required"
[[ -n "$right_results" ]] || fail "--right is required"
[[ -n "$out_dir" ]] || fail "--out is required"
[[ -f "$left_results" ]] || fail "left results not found: $left_results"
[[ -f "$right_results" ]] || fail "right results not found: $right_results"

mkdir -p "$out_dir"

tool_version="$(sed -n '1p' "$tool_root/VERSION")"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

LEFT_RESULTS="$left_results" RIGHT_RESULTS="$right_results" OUT_DIR="$out_dir" \
  TITLE="$title" TOOL_VERSION="$tool_version" GENERATED_AT="$generated_at" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;
use File::Spec;

sub fail {
  die "arena-compare: $_[0]\n";
}

sub slurp_json {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or fail("cannot read $path: $!");
  local $/;
  my $raw = <$fh>;
  close $fh;
  return decode_json($raw);
}

sub require_number {
  my ($data, $field) = @_;
  my $value = $data->{summary}{$field};
  fail("missing summary.$field") unless defined $value && $value =~ /\A-?[0-9]+(?:\.[0-9]+)?\z/;
  return 0 + $value;
}

sub case_map {
  my ($data, $side) = @_;
  my $cases = $data->{cases};
  fail("$side results missing cases") unless ref($cases) eq 'ARRAY' && @$cases;

  my %map;
  for my $case (@$cases) {
    my $id = $case->{id} // fail("$side case missing id");
    fail("$side duplicate case id: $id") if exists $map{$id};
    for my $field (qw(total max high_risk_findings scope_control validation_quality)) {
      fail("$side case $id missing $field") unless defined $case->{$field};
    }
    $map{$id} = $case;
  }
  return %map;
}

sub delta2 {
  my ($right, $left) = @_;
  return 0 + sprintf('%.2f', $right - $left);
}

sub null_or_number {
  my ($value) = @_;
  return defined $value ? 0 + $value : JSON::PP::null;
}

sub null_or_string {
  my ($value) = @_;
  return defined $value ? $value : JSON::PP::null;
}

sub cell {
  my ($value) = @_;
  return '-' unless defined $value;
  return $value;
}

sub signed_cell {
  my ($value) = @_;
  return '-' unless defined $value;
  return $value > 0 ? "+$value" : "$value";
}

sub signed_float_cell {
  my ($value) = @_;
  return '-' unless defined $value;
  my $formatted = sprintf('%.2f', $value);
  return $value > 0 ? "+$formatted" : $formatted;
}

my $left_path = $ENV{LEFT_RESULTS};
my $right_path = $ENV{RIGHT_RESULTS};
my $out_dir = $ENV{OUT_DIR};
my $left = slurp_json($left_path);
my $right = slurp_json($right_path);

for my $side (['left', $left], ['right', $right]) {
  fail("$side->[0] results missing summary") unless ref($side->[1]{summary}) eq 'HASH';
  fail("$side->[0] results missing cases") unless ref($side->[1]{cases}) eq 'ARRAY';
}

my %left_cases = case_map($left, 'left');
my %right_cases = case_map($right, 'right');
my %all_ids = map { $_ => 1 } (keys %left_cases, keys %right_cases);

my @rows;
my ($added, $removed, $changed, $unchanged) = (0, 0, 0, 0);
my $case_regressions = 0;

for my $id (sort keys %all_ids) {
  my $l = $left_cases{$id};
  my $r = $right_cases{$id};
  my ($status, $score_delta, $high_delta);

  if ($l && $r) {
    $score_delta = (0 + $r->{total}) - (0 + $l->{total});
    $high_delta = (0 + $r->{high_risk_findings}) - (0 + $l->{high_risk_findings});
    if ($score_delta != 0 || $high_delta != 0 || ($l->{verdict} // '') ne ($r->{verdict} // '') || ($l->{has_tests} // '') ne ($r->{has_tests} // '')) {
      $status = 'changed';
      $changed++;
    } else {
      $status = 'unchanged';
      $unchanged++;
    }
    $case_regressions++ if $score_delta < 0 || $high_delta > 0;
  } elsif ($r) {
    $status = 'added';
    $added++;
  } else {
    $status = 'removed';
    $removed++;
    $case_regressions++;
  }

  push @rows, {
    id => $id,
    status => $status,
    left_total => null_or_number($l ? $l->{total} : undef),
    right_total => null_or_number($r ? $r->{total} : undef),
    score_delta => defined $score_delta ? 0 + $score_delta : JSON::PP::null,
    left_high_risk_findings => null_or_number($l ? $l->{high_risk_findings} : undef),
    right_high_risk_findings => null_or_number($r ? $r->{high_risk_findings} : undef),
    high_risk_delta => defined $high_delta ? 0 + $high_delta : JSON::PP::null,
    left_verdict => null_or_string($l ? $l->{verdict} : undef),
    right_verdict => null_or_string($r ? $r->{verdict} : undef),
  };
}

my $left_count = require_number($left, 'case_count');
my $right_count = require_number($right, 'case_count');
my $left_avg = require_number($left, 'average_total');
my $right_avg = require_number($right, 'average_total');
my $left_high = require_number($left, 'high_risk_finding_count');
my $right_high = require_number($right, 'high_risk_finding_count');
my $case_delta = $right_count - $left_count;
my $avg_delta = delta2($right_avg, $left_avg);
my $high_delta = $right_high - $left_high;

my $status;
if ($avg_delta < 0 || $high_delta > 0 || $removed > 0 || $case_regressions > 0) {
  $status = 'regressed';
} elsif ($avg_delta > 0 || $high_delta < 0 || $added > 0 || $changed > 0) {
  $status = 'improved';
} else {
  $status = 'unchanged';
}

my $result = {
  schema_version => '0.1',
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  title => $ENV{TITLE},
  left => {
    path => $left_path,
    case_count => $left_count,
    average_total => $left_avg,
    high_risk_finding_count => $left_high,
  },
  right => {
    path => $right_path,
    case_count => $right_count,
    average_total => $right_avg,
    high_risk_finding_count => $right_high,
  },
  summary => {
    status => $status,
    case_count_delta => $case_delta,
    average_total_delta => $avg_delta,
    high_risk_finding_delta => $high_delta,
    added_cases => $added,
    removed_cases => $removed,
    changed_cases => $changed,
    unchanged_cases => $unchanged,
  },
  cases => \@rows,
};

my $json_path = File::Spec->catfile($out_dir, 'arena-compare.json');
open my $json_fh, '>:encoding(UTF-8)', $json_path or fail("cannot write $json_path: $!");
print {$json_fh} JSON::PP->new->utf8->canonical(1)->pretty->encode($result);
close $json_fh;

my $md_path = File::Spec->catfile($out_dir, 'arena-compare.md');
open my $md_fh, '>:encoding(UTF-8)', $md_path or fail("cannot write $md_path: $!");
print {$md_fh} "# $ENV{TITLE}\n\n";
print {$md_fh} "- Generated: $ENV{GENERATED_AT}\n";
print {$md_fh} "- Tool version: $ENV{TOOL_VERSION}\n";
print {$md_fh} "- Left: $left_path\n";
print {$md_fh} "- Right: $right_path\n\n";
print {$md_fh} "## Summary\n\n";
print {$md_fh} "| Metric | Value |\n";
print {$md_fh} "| --- | ---: |\n";
print {$md_fh} "| Status | $status |\n";
print {$md_fh} "| Case count delta | ", signed_cell($case_delta), " |\n";
print {$md_fh} "| Average score delta | ", signed_float_cell($avg_delta), " |\n";
print {$md_fh} "| High-risk finding delta | ", signed_cell($high_delta), " |\n";
print {$md_fh} "| Added cases | $added |\n";
print {$md_fh} "| Removed cases | $removed |\n";
print {$md_fh} "| Changed cases | $changed |\n";
print {$md_fh} "| Unchanged cases | $unchanged |\n\n";
print {$md_fh} "## Cases\n\n";
print {$md_fh} "| Case | Status | Left score | Right score | Score delta | Left high-risk | Right high-risk | High-risk delta |\n";
print {$md_fh} "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |\n";
for my $row (@rows) {
  my $score_delta = ref($row->{score_delta}) ? undef : $row->{score_delta};
  my $high_delta = ref($row->{high_risk_delta}) ? undef : $row->{high_risk_delta};
  print {$md_fh} "| $row->{id} | $row->{status} | ",
    cell(ref($row->{left_total}) ? undef : $row->{left_total}), " | ",
    cell(ref($row->{right_total}) ? undef : $row->{right_total}), " | ",
    signed_cell($score_delta), " | ",
    cell(ref($row->{left_high_risk_findings}) ? undef : $row->{left_high_risk_findings}), " | ",
    cell(ref($row->{right_high_risk_findings}) ? undef : $row->{right_high_risk_findings}), " | ",
    signed_cell($high_delta), " |\n";
}
close $md_fh;
PERL

echo "wrote: $out_dir/arena-compare.json"
echo "wrote: $out_dir/arena-compare.md"
