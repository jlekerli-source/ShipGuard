#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer transcript redact

Usage:
  codex-maintainer transcript redact --in <transcript.md> --out <redacted.md> [--report <report.json>] [--private-term <text> ...]

Outputs:
  redacted transcript Markdown
  redaction report JSON
USAGE
}

fail() {
  echo "transcript-redact: $*" >&2
  exit 1
}

in_file=""
out_file=""
report_file=""
private_terms=()

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --in)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--in requires a value"
      in_file="$2"
      shift 2
      ;;
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_file="$2"
      shift 2
      ;;
    --report)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--report requires a value"
      report_file="$2"
      shift 2
      ;;
    --private-term)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--private-term requires a value"
      private_terms+=("$2")
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
[[ -n "$out_file" ]] || fail "--out is required"
[[ -f "$in_file" ]] || fail "input transcript not found: $in_file"

if [[ -z "$report_file" ]]; then
  report_file="$(dirname "$out_file")/redaction-report.json"
fi

mkdir -p "$(dirname "$out_file")" "$(dirname "$report_file")"

perl -MJSON::PP -CS - "$in_file" "$out_file" "$report_file" "${private_terms[@]}" <<'PERL'
use strict;
use warnings;
use File::Basename qw(basename);
use JSON::PP;

my ($in_file, $out_file, $report_file, @private_terms) = @ARGV;

open my $in, '<:encoding(UTF-8)', $in_file or die "transcript-redact: cannot read $in_file: $!\n";
local $/;
my $text = <$in>;
close $in;

my @rules = (
  { id => 'private_term', replacements => 0 },
  { id => 'email', replacements => 0 },
  { id => 'bearer_token', replacements => 0 },
  { id => 'secret_assignment', replacements => 0 },
  { id => 'github_token', replacements => 0 },
  { id => 'openai_key', replacements => 0 },
  { id => 'hex_token', replacements => 0 },
  { id => 'unix_home_path', replacements => 0 },
  { id => 'windows_user_path', replacements => 0 },
);

my %rule_by_id = map { $_->{id} => $_ } @rules;

sub mark {
  my ($id, $replacement) = @_;
  $rule_by_id{$id}->{replacements}++;
  return $replacement;
}

for my $term (@private_terms) {
  next unless defined $term && length $term;
  my $quoted = quotemeta($term);
  $text =~ s/$quoted/mark('private_term', '[redacted-private-term]')/gei;
}

$text =~ s/[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/mark('email', '[redacted-email]')/ge;
$text =~ s{\bBearer\s+[A-Za-z0-9._~+/=-]{16,}}{mark('bearer_token', 'Bearer [redacted-secret]')}ge;
$text =~ s{\b([A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*)=([^\s`"']+)}{mark('secret_assignment', "$1=[redacted-secret]")}gei;
$text =~ s/\bgh[pousr]_[A-Za-z0-9_]{20,}\b/mark('github_token', '[redacted-secret]')/ge;
$text =~ s/\bsk-[A-Za-z0-9_-]{20,}\b/mark('openai_key', '[redacted-secret]')/ge;
$text =~ s/\b[a-f0-9]{32,}\b/mark('hex_token', '[redacted-token]')/gei;
$text =~ s{/(Users|home)/[A-Za-z0-9._-]+}{mark('unix_home_path', "/$1/[redacted-user]")}ge;
$text =~ s{([A-Za-z]:\\Users\\)[^\\\s]+}{mark('windows_user_path', $1 . '[redacted-user]')}ge;

open my $out, '>:encoding(UTF-8)', $out_file or die "transcript-redact: cannot write $out_file: $!\n";
print {$out} $text;
close $out;

my @remaining;
push @remaining, { id => 'email', count => scalar(() = $text =~ /[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/g) };
push @remaining, { id => 'secret_token', count => scalar(() = $text =~ /\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+(?!\[redacted-secret\])[A-Za-z0-9._~+\/=-]{16,})\b/g) };
push @remaining, { id => 'secret_assignment', count => scalar(() = $text =~ /\b[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*=(?!\[redacted-secret\])\S+/ig) };
push @remaining, { id => 'hex_token', count => scalar(() = $text =~ /\b[a-f0-9]{32,}\b/ig) };
push @remaining, { id => 'unix_home_path', count => scalar(() = $text =~ m{/(?:Users|home)/(?!\[redacted-user\])[A-Za-z0-9._-]+}g) };
push @remaining, { id => 'windows_user_path', count => scalar(() = $text =~ m{[A-Za-z]:\\Users\\(?!\[redacted-user\])[^\\\s]+}g) };

for my $term (@private_terms) {
  next unless defined $term && length $term;
  my $quoted = quotemeta($term);
  push @remaining, { id => 'private_term', count => scalar(() = $text =~ /$quoted/ig) };
}

@remaining = grep { $_->{count} > 0 } @remaining;
my $remaining_risk_count = 0;
$remaining_risk_count += $_->{count} for @remaining;
my $total_replacements = 0;
$total_replacements += $_->{replacements} for @rules;

my $status = $remaining_risk_count == 0 ? 'pass' : 'blocked';
my $report = {
  schema_version => '1.0',
  status => $status,
  input_name => basename($in_file),
  output_name => basename($out_file),
  private_terms_checked => scalar(@private_terms),
  total_replacements => $total_replacements,
  remaining_risk_count => $remaining_risk_count,
  rules => \@rules,
  remaining_risks => \@remaining,
};

open my $report_out, '>:encoding(UTF-8)', $report_file or die "transcript-redact: cannot write $report_file: $!\n";
print {$report_out} JSON::PP->new->ascii->canonical->pretty->encode($report);
close $report_out;

print "wrote: $out_file\n";
print "wrote: $report_file\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
