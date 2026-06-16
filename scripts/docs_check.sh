#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
codex-maintainer docs-check

Usage:
  codex-maintainer docs-check [path] [--out <dir>]

Checks Markdown files for broken local links. External URLs and in-page anchors are ignored.

Outputs with --out:
  docs-check.json
  docs-check.md
USAGE
}

fail() {
  echo "docs-check: $*" >&2
  exit 1
}

target="."
out_dir=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --out)
      [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
      out_dir="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    -*)
      fail "unknown argument: $1"
      ;;
    *)
      target="$1"
      shift
      ;;
  esac
done

[[ -e "$target" ]] || fail "path not found: $target"
[[ -z "$out_dir" ]] || mkdir -p "$out_dir"

TARGET="$target" OUT_DIR="$out_dir" perl <<'PERL'
use strict;
use warnings;
use Cwd qw(abs_path getcwd);
use File::Basename qw(dirname basename);
use File::Find;
use File::Spec;
use JSON::PP;

sub fail {
  die "docs-check: $_[0]\n";
}

sub read_text {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or fail("cannot read $path: $!");
  local $/;
  my $text = <$fh>;
  close $fh;
  return $text;
}

sub write_text {
  my ($path, $text) = @_;
  open my $fh, '>:encoding(UTF-8)', $path or fail("cannot write $path: $!");
  print {$fh} $text;
  close $fh;
}

sub rel_path {
  my ($path, $root) = @_;
  my $rel = File::Spec->abs2rel($path, $root);
  $rel =~ s{\\}{/}g;
  return $rel;
}

sub should_ignore_link {
  my ($link) = @_;
  return 1 if $link eq '';
  return 1 if $link =~ /\A#/;
  return 1 if $link =~ /\A(?:https?|mailto|tel):/i;
  return 1 if $link =~ /\A[A-Za-z][A-Za-z0-9+.-]*:/;
  return 0;
}

sub clean_link {
  my ($raw) = @_;
  $raw =~ s/\A\s+|\s+\z//g;
  $raw =~ s/\A<(.+)>\z/$1/;
  $raw =~ s/\s+["'][^"']*["']\z//;
  $raw =~ s/[?#].*\z//;
  return $raw;
}

my $target = $ENV{TARGET};
my $out_dir = $ENV{OUT_DIR} || '';
my $root = -d $target ? abs_path($target) : abs_path(dirname($target));
fail("cannot resolve path: $target") unless defined $root;

my @files;
if (-f $target) {
  push @files, abs_path($target) if $target =~ /\.md\z/i;
} else {
  find({
    wanted => sub {
      if (-d $File::Find::name && ($_ eq '.git' || $_ eq 'dist' || $_ eq '.cache' || $_ eq 'DerivedData' || $_ eq 'node_modules')) {
        $File::Find::prune = 1;
        return;
      }
      return unless -f $File::Find::name;
      return unless $File::Find::name =~ /\.md\z/i;
      push @files, abs_path($File::Find::name);
    },
    no_chdir => 1,
  }, $target);
}

@files = sort @files;
my @broken;
my $links_checked = 0;

for my $file (@files) {
  my $text = read_text($file);
  while ($text =~ /\[[^\]\n]+\]\(([^)\n]+)\)/g) {
    my $raw = $1;
    my $link = clean_link($raw);
    next if should_ignore_link($link);
    $links_checked++;

    my $candidate;
    if ($link =~ m{\A/}) {
      my $trimmed = $link;
      $trimmed =~ s{\A/+}{};
      $candidate = File::Spec->catfile($root, $trimmed);
    } else {
      $candidate = File::Spec->catfile(dirname($file), $link);
    }

    next if -e $candidate;
    push @broken, {
      file => rel_path($file, $root),
      link => $raw,
      target => rel_path(File::Spec->rel2abs($candidate), $root),
    };
  }
}

my $status = @broken ? 'blocked' : 'pass';
my $report = {
  schema_version => '1.0',
  status => $status,
  root => basename($root),
  files_checked => scalar(@files),
  links_checked => $links_checked,
  broken_count => scalar(@broken),
  broken_links => \@broken,
};

if (length $out_dir) {
  my $json = JSON::PP->new->ascii->canonical->pretty->encode($report);
  write_text(File::Spec->catfile($out_dir, 'docs-check.json'), $json);

  my $md = "# Docs Check\n\n"
    . "- Status: $status\n"
    . "- Files checked: " . scalar(@files) . "\n"
    . "- Local links checked: $links_checked\n"
    . "- Broken links: " . scalar(@broken) . "\n\n";
  if (@broken) {
    $md .= "| File | Link | Missing target |\n| --- | --- | --- |\n";
    for my $broken (@broken) {
      $md .= "| `$broken->{file}` | `$broken->{link}` | `$broken->{target}` |\n";
    }
  }
  write_text(File::Spec->catfile($out_dir, 'docs-check.md'), $md);
  print "wrote: " . File::Spec->catfile($out_dir, 'docs-check.json') . "\n";
  print "wrote: " . File::Spec->catfile($out_dir, 'docs-check.md') . "\n";
}

print "status: $status\n";
print "files_checked: " . scalar(@files) . "\n";
print "links_checked: $links_checked\n";
print "broken_count: " . scalar(@broken) . "\n";
exit(@broken ? 1 : 0);
PERL
