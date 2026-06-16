#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer transcript verify

Usage:
  codex-maintainer transcript verify --in <redacted.md> --out <dir> [--report <redaction-report.json>]

Outputs:
  transcript-verify.json
  transcript-verify.md
  badge.json
USAGE
}

fail() {
  echo "transcript-verify: $*" >&2
  exit 1
}

in_file=""
out_dir=""
report_file=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --in)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--in requires a value"
      in_file="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --report)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--report requires a value"
      report_file="$2"
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

[[ -n "$in_file" ]] || fail "--in is required"
[[ -n "$out_dir" ]] || fail "--out is required"
[[ -f "$in_file" ]] || fail "redacted transcript not found: $in_file"
[[ -z "$report_file" || -f "$report_file" ]] || fail "redaction report not found: $report_file"

mkdir -p "$out_dir"

perl -MJSON::PP -CS - "$in_file" "$out_dir" "$report_file" <<'PERL'
use strict;
use warnings;
use File::Basename qw(basename);
use File::Spec;
use JSON::PP;

my ($in_file, $out_dir, $report_file) = @ARGV;

sub read_text {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or die "transcript-verify: cannot read $path: $!\n";
  local $/;
  my $text = <$fh>;
  close $fh;
  return $text;
}

sub write_text {
  my ($path, $text) = @_;
  open my $fh, '>:encoding(UTF-8)', $path or die "transcript-verify: cannot write $path: $!\n";
  print {$fh} $text;
  close $fh;
}

sub json_string {
  my ($value) = @_;
  return JSON::PP->new->ascii->encode($value // '');
}

my $text = read_text($in_file);
my @checks;

sub add_check {
  my ($name, $status, $detail) = @_;
  push @checks, { name => $name, status => $status, detail => $detail };
}

my @risk_patterns = (
  ['email', qr/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/],
  ['secret token', qr/\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+(?!\[redacted-secret\])[A-Za-z0-9._~+\/=-]{16,})\b/],
  ['secret assignment', qr/\b[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*=(?!\[redacted-secret\])\S+/i],
  ['hex token', qr/\b[a-f0-9]{32,}\b/i],
  ['unix home path', qr{/(?:Users|home)/(?!\[redacted-user\])[A-Za-z0-9._-]+}],
  ['windows user path', qr{[A-Za-z]:\\Users\\(?!\[redacted-user\])[^\\\s]+}],
);

my $remaining_risk_count = 0;
for my $pattern (@risk_patterns) {
  my ($name, $regex) = @$pattern;
  my $count = scalar(() = $text =~ /$regex/g);
  $remaining_risk_count += $count;
  add_check($name, $count == 0 ? 'pass' : 'blocked', $count == 0 ? 'no match' : "$count risky match(es)");
}

my $report_status = 'skipped';
if (defined $report_file && length $report_file) {
  my $report_text = read_text($report_file);
  my $report = eval { JSON::PP->new->decode($report_text) };
  if (!$report) {
    add_check('redaction report', 'blocked', 'report is not valid JSON');
    $report_status = 'blocked';
  } elsif (($report->{schema_version} || '') ne '1.0') {
    add_check('redaction report', 'blocked', 'schema_version must be 1.0');
    $report_status = 'blocked';
  } elsif (($report->{status} || '') ne 'pass') {
    add_check('redaction report', 'blocked', 'redaction report status is not pass');
    $report_status = 'blocked';
  } elsif (($report->{remaining_risk_count} || 0) != 0) {
    add_check('redaction report', 'blocked', 'redaction report has remaining risks');
    $report_status = 'blocked';
  } else {
    add_check('redaction report', 'pass', 'redaction report is passing');
    $report_status = 'pass';
  }
} else {
  add_check('redaction report', 'skipped', 'no report provided');
}

my $blocked = scalar(grep { $_->{status} eq 'blocked' } @checks);
my $status = $blocked == 0 ? 'pass' : 'blocked';
my $json = JSON::PP->new->ascii->canonical->pretty;
my $report = {
  schema_version => '1.0',
  status => $status,
  input_name => basename($in_file),
  redaction_report_status => $report_status,
  remaining_risk_count => $remaining_risk_count,
  checks => \@checks,
};

write_text(File::Spec->catfile($out_dir, 'transcript-verify.json'), $json->encode($report));

my $md = "# Transcript Verification\n\n"
  . "- Status: $status\n"
  . "- Input: " . basename($in_file) . "\n"
  . "- Remaining risk count: $remaining_risk_count\n\n"
  . "## Checks\n\n"
  . "| Check | Status | Detail |\n"
  . "| --- | --- | --- |\n";
for my $check (@checks) {
  $md .= "| $check->{name} | $check->{status} | $check->{detail} |\n";
}
write_text(File::Spec->catfile($out_dir, 'transcript-verify.md'), $md);

my $color = $status eq 'pass' ? 'brightgreen' : 'red';
my $badge = {
  schemaVersion => 1,
  label => 'transcript',
  message => $status,
  color => $color,
};
write_text(File::Spec->catfile($out_dir, 'badge.json'), $json->encode($badge));

print "wrote: " . File::Spec->catfile($out_dir, 'transcript-verify.json') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'transcript-verify.md') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'badge.json') . "\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
