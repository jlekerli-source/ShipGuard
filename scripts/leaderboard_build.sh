#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
shipguard leaderboard build

Usage:
  shipguard leaderboard build --arena-results <results.json> --out <leaderboard.json> [--agent <id>] [--name <display-name>] [--benchmark <name>]

Defaults:
  --agent shipguard-fixture-baseline
  --name ShipGuard Fixture Baseline
  --benchmark Public AI Maintainer Reliability Benchmark
USAGE
}

fail() {
  echo "leaderboard: $*" >&2
  exit 1
}

arena_results=""
out_file=""
agent_id="shipguard-fixture-baseline"
agent_name="ShipGuard Fixture Baseline"
benchmark_name="Public AI Maintainer Reliability Benchmark"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --arena-results)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--arena-results requires a value"
      arena_results="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --agent)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--agent requires a value"
      agent_id="$2"
      shift 2
      ;;
    --name)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--name requires a value"
      agent_name="$2"
      shift 2
      ;;
    --benchmark)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--benchmark requires a value"
      benchmark_name="$2"
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

[[ -n "$arena_results" ]] || fail "--arena-results is required"
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$arena_results" ]] || fail "arena results not found: $arena_results"

mkdir -p "$(dirname "$out_file")"
tool_version="$(sed -n '1p' "$tool_root/VERSION")"
generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}}"

perl -0 - "$arena_results" "$out_file" "$agent_id" "$agent_name" "$benchmark_name" "$tool_version" "$generated_at" <<'PERL'
use strict;
use warnings;

my ($source, $out, $agent_id, $agent_name, $benchmark_name, $tool_version, $generated_at) = @ARGV;
open my $fh, '<', $source or die "leaderboard: cannot read $source: $!\n";
local $/;
my $json = <$fh>;
close $fh;

sub field {
  my ($name) = @_;
  return $1 if $json =~ /"\Q$name\E":\s*([0-9]+(?:\.[0-9]+)?)/;
  die "leaderboard: missing field $name\n";
}

sub esc {
  my ($value) = @_;
  $value =~ s/\\/\\\\/g;
  $value =~ s/"/\\"/g;
  $value =~ s/\n/\\n/g;
  $value =~ s/\r/\\r/g;
  $value =~ s/\t/\\t/g;
  return qq{"$value"};
}

my @cases;
while ($json =~ /\{"id":\s*"((?:\\.|[^"])*)",\s*"total":\s*([0-9]+),\s*"max":\s*([0-9]+),\s*"verdict":\s*"((?:\\.|[^"])*)",\s*"high_risk_findings":\s*([0-9]+),\s*"scope_control":\s*([0-9]+),\s*"validation_quality":\s*([0-9]+),\s*"has_tests":\s*(true|false)/g) {
  push @cases, {
    id => $1,
    total => $2,
    max => $3,
    verdict => $4,
    high => $5,
    scope => $6,
    validation => $7,
    has_tests => $8,
  };
}
die "leaderboard: no cases found in $source\n" unless @cases;

open my $out_fh, '>', $out or die "leaderboard: cannot write $out: $!\n";
print $out_fh "{\n";
print $out_fh "  \"schema_version\": \"1.0\",\n";
print $out_fh "  \"tool_version\": ", esc($tool_version), ",\n";
print $out_fh "  \"generated_at\": ", esc($generated_at), ",\n";
print $out_fh "  \"benchmark\": ", esc($benchmark_name), ",\n";
print $out_fh "  \"source\": ", esc($source), ",\n";
print $out_fh "  \"tasks\": [\n";
for my $i (0 .. $#cases) {
  my $comma = $i == $#cases ? "" : ",";
  print $out_fh "    {\"id\": ", esc($cases[$i]{id}), ", \"max_score\": $cases[$i]{max}}$comma\n";
}
print $out_fh "  ],\n";
print $out_fh "  \"agents\": [\n";
print $out_fh "    {\n";
print $out_fh "      \"id\": ", esc($agent_id), ",\n";
print $out_fh "      \"name\": ", esc($agent_name), ",\n";
print $out_fh "      \"scores\": {\n";
print $out_fh "        \"case_count\": ", field('case_count'), ",\n";
print $out_fh "        \"average_total\": ", field('average_total'), ",\n";
print $out_fh "        \"max_total\": 12,\n";
print $out_fh "        \"high_risk_finding_count\": ", field('high_risk_finding_count'), ",\n";
print $out_fh "        \"validation_evidence_ratio\": ", field('validation_evidence_ratio'), ",\n";
print $out_fh "        \"scope_control_average\": ", field('scope_control_average'), "\n";
print $out_fh "      },\n";
print $out_fh "      \"cases\": [\n";
for my $i (0 .. $#cases) {
  my $comma = $i == $#cases ? "" : ",";
  print $out_fh "        {\"task_id\": ", esc($cases[$i]{id}), ", \"score\": $cases[$i]{total}, \"max\": $cases[$i]{max}, \"high_risk_findings\": $cases[$i]{high}, \"has_tests\": $cases[$i]{has_tests}, \"verdict\": ", esc($cases[$i]{verdict}), "}$comma\n";
}
print $out_fh "      ]\n";
print $out_fh "    }\n";
print $out_fh "  ]\n";
print $out_fh "}\n";
close $out_fh;
PERL

echo "wrote: $out_file"
