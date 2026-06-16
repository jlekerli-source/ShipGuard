#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-evidence

Usage:
  codex-maintainer release-evidence site --consume <consumer-proof-dir> --out <dir> [--diff <release-diff-dir>] [--title <title>]
  codex-maintainer release-evidence index --site <evidence-site-dir> [--site <evidence-site-dir> ...] --out <dir> [--title <title>]

Inputs:
  --consume must contain consumer-report.json and asset-digests.json.
  --diff may contain release-diff.json.

Outputs:
  index.html
  evidence.json
  README.md
  sources/consumer-report.json
  sources/asset-digests.json
  sources/release-diff.json

Index outputs:
  index.html
  evidence-index.json
  README.md
  sites/<release>/index.html
  sites/<release>/evidence.json
USAGE
}

fail() {
  echo "release-evidence: $*" >&2
  exit 1
}

cmd_site() {
  local consume_dir=""
  local diff_dir=""
  local out_dir=""
  local title="Codex Maintainer Release Evidence"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --consume)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--consume requires a value"
        consume_dir="$2"
        shift 2
        ;;
      --diff)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--diff requires a value"
        diff_dir="$2"
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
        fail "unknown site argument: $1"
        ;;
    esac
  done

  [[ -n "$consume_dir" ]] || fail "--consume is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$consume_dir" ]] || fail "consumer proof directory not found: $consume_dir"
  [[ -f "$consume_dir/consumer-report.json" ]] || fail "missing consumer-report.json in $consume_dir"
  [[ -f "$consume_dir/asset-digests.json" ]] || fail "missing asset-digests.json in $consume_dir"
  if [[ -n "$diff_dir" ]]; then
    [[ -d "$diff_dir" ]] || fail "release diff directory not found: $diff_dir"
    [[ -f "$diff_dir/release-diff.json" ]] || fail "missing release-diff.json in $diff_dir"
  fi

  mkdir -p "$out_dir/sources"

  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  CONSUME_DIR="$consume_dir" DIFF_DIR="$diff_dir" OUT_DIR="$out_dir" TITLE="$title" \
    TOOL_VERSION="$tool_version" GENERATED_AT="$generated_at" perl <<'PERL'
use strict;
use warnings;
use File::Spec;
use JSON::PP;

sub fail {
  die "release-evidence: $_[0]\n";
}

sub slurp_json {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or fail("cannot read $path: $!");
  local $/;
  my $raw = <$fh>;
  close $fh;
  return decode_json($raw);
}

sub write_text {
  my ($path, $text) = @_;
  open my $fh, '>:encoding(UTF-8)', $path or fail("cannot write $path: $!");
  print {$fh} $text;
  close $fh;
}

sub html_escape {
  my ($text) = @_;
  $text = '' unless defined $text;
  $text =~ s/&/&amp;/g;
  $text =~ s/</&lt;/g;
  $text =~ s/>/&gt;/g;
  $text =~ s/"/&quot;/g;
  $text =~ s/'/&#39;/g;
  return $text;
}

sub display {
  my ($value) = @_;
  return '-' if !defined($value) || ref($value);
  return "$value";
}

my $consume_dir = $ENV{CONSUME_DIR};
my $diff_dir = $ENV{DIFF_DIR} || '';
my $out_dir = $ENV{OUT_DIR};
my $source_dir = File::Spec->catdir($out_dir, 'sources');

my $consumer_path = File::Spec->catfile($consume_dir, 'consumer-report.json');
my $digests_path = File::Spec->catfile($consume_dir, 'asset-digests.json');
my $consumer = slurp_json($consumer_path);
my $digests = slurp_json($digests_path);

fail("unsupported consumer schema") unless ($consumer->{schema_version} || '') eq '1.0';
fail("unsupported asset digest schema") unless ($digests->{schema_version} || '') eq '1.0';

my $diff;
if (length $diff_dir) {
  my $diff_path = File::Spec->catfile($diff_dir, 'release-diff.json');
  $diff = slurp_json($diff_path);
  fail("unsupported release diff schema") unless ($diff->{schema_version} || '') eq '1.0';
}

my @assets = @{ $digests->{assets} || [] };
my %asset_summary = (
  asset_count => scalar(@assets),
  present => 0,
  missing => 0,
  required_missing => 0,
);
for my $asset (@assets) {
  my $status = $asset->{status} || 'missing';
  if ($status eq 'present') {
    $asset_summary{present}++;
  } else {
    $asset_summary{missing}++;
    $asset_summary{required_missing}++ if $asset->{required};
  }
}

my $status = (($consumer->{status} || '') eq 'pass' && (!$diff || (($diff->{status} || '') eq 'pass'))) ? 'pass' : 'blocked';

my $evidence = {
  schema_version => '1.0',
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  title => $ENV{TITLE},
  status => $status,
  release => {
    version => $consumer->{version},
    tag => $consumer->{tag},
    commit => $consumer->{commit},
    artifact => $consumer->{artifact},
    proofs => $consumer->{proofs},
    summary => $consumer->{summary},
    published => $consumer->{published},
  },
  asset_digest_summary => \%asset_summary,
  release_diff => $diff ? {
    present => JSON::PP::true,
    status => $diff->{status},
    left => $diff->{left},
    right => $diff->{right},
    summary => $diff->{summary},
  } : {
    present => JSON::PP::false,
  },
  sources => {
    consumer_report => 'sources/consumer-report.json',
    asset_digests => 'sources/asset-digests.json',
    release_diff => $diff ? 'sources/release-diff.json' : JSON::PP::null,
  },
};

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
write_text(File::Spec->catfile($out_dir, 'evidence.json'), $json->encode($evidence));
write_text(File::Spec->catfile($source_dir, 'consumer-report.json'), $json->encode($consumer));
write_text(File::Spec->catfile($source_dir, 'asset-digests.json'), $json->encode($digests));
write_text(File::Spec->catfile($source_dir, 'release-diff.json'), $json->encode($diff)) if $diff;

my $readme = "# $ENV{TITLE}\n\n"
  . "- Generated: $ENV{GENERATED_AT}\n"
  . "- Status: $status\n"
  . "- Version: " . display($consumer->{version}) . "\n"
  . "- Tag: " . display($consumer->{tag}) . "\n"
  . "- Artifact: " . display(($consumer->{artifact} || {})->{name}) . "\n"
  . "- Artifact SHA-256: " . display(($consumer->{artifact} || {})->{sha256}) . "\n"
  . "- Assets present: $asset_summary{present}/$asset_summary{asset_count}\n"
  . "- Required assets missing: $asset_summary{required_missing}\n"
  . "- Release diff: " . ($diff ? display($diff->{status}) : 'not included') . "\n\n"
  . "Open `index.html` for the human report or `evidence.json` for the machine-readable summary.\n";
write_text(File::Spec->catfile($out_dir, 'README.md'), $readme);

my $artifact = $consumer->{artifact} || {};
my $proofs = $consumer->{proofs} || {};
my $summary = $consumer->{summary} || {};
my $published = $consumer->{published} || {};
my $badge = $summary->{badge_message} || '';

my $html = <<"HTML";
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>@{[html_escape($ENV{TITLE})]}</title>
  <style>
    :root { color-scheme: light; --ink: #1f2937; --muted: #596273; --line: #d9dee7; --panel: #f6f8fb; --good: #0f766e; --bad: #b42318; }
    body { margin: 0; font: 15px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: #fff; }
    main { max-width: 1120px; margin: 0 auto; padding: 28px; }
    h1 { margin: 0 0 6px; font-size: 30px; letter-spacing: 0; }
    h2 { margin: 28px 0 10px; font-size: 18px; letter-spacing: 0; }
    p { margin: 0 0 12px; color: var(--muted); }
    .status { display: inline-block; margin: 12px 0 18px; padding: 5px 10px; border-radius: 6px; font-weight: 700; color: #fff; background: var(--good); }
    .status.blocked { background: var(--bad); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
    .metric { border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: var(--panel); }
    .label { display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; }
    .value { display: block; margin-top: 4px; overflow-wrap: anywhere; font-weight: 650; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
    th { background: var(--panel); }
    code { background: var(--panel); padding: 2px 4px; border-radius: 4px; }
    a { color: #1d4ed8; }
  </style>
</head>
<body>
<main>
  <h1>@{[html_escape($ENV{TITLE})]}</h1>
  <p>Static release evidence export generated from consumer proof and optional release diff reports.</p>
  <div class="status @{[$status eq 'pass' ? '' : 'blocked']}">@{[html_escape($status)]}</div>

  <section>
    <h2>Release</h2>
    <div class="grid">
      <div class="metric"><span class="label">Version</span><span class="value">@{[html_escape(display($consumer->{version}))]}</span></div>
      <div class="metric"><span class="label">Tag</span><span class="value">@{[html_escape(display($consumer->{tag}))]}</span></div>
      <div class="metric"><span class="label">Commit</span><span class="value">@{[html_escape(display($consumer->{commit}))]}</span></div>
      <div class="metric"><span class="label">Artifact</span><span class="value">@{[html_escape(display($artifact->{name}))]}</span></div>
      <div class="metric"><span class="label">Artifact bytes</span><span class="value">@{[html_escape(display($artifact->{bytes}))]}</span></div>
      <div class="metric"><span class="label">Artifact SHA-256</span><span class="value">@{[html_escape(display($artifact->{sha256}))]}</span></div>
      <div class="metric"><span class="label">Badge</span><span class="value">@{[html_escape($badge)]}</span></div>
      <div class="metric"><span class="label">Published crosschecks</span><span class="value">replay @{[html_escape(display($published->{replay_report}))]}, attestation @{[html_escape(display($published->{attestation}))]}, badge @{[html_escape(display($published->{attestation_badge}))]}</span></div>
    </div>
  </section>

  <section>
    <h2>Proof Links</h2>
    <ul>
HTML

for my $pair (
  ['Release', $proofs->{release_url}],
  ['CI run', $proofs->{ci_run_url}],
  ['Issue', $proofs->{issue_url}],
  ['Evidence JSON', 'evidence.json'],
  ['Consumer report source', 'sources/consumer-report.json'],
  ['Asset digest source', 'sources/asset-digests.json'],
  ($diff ? (['Release diff source', 'sources/release-diff.json']) : ()),
) {
  my ($label, $url) = @$pair;
  next unless defined $url && length "$url";
  $html .= '      <li><a href="' . html_escape($url) . '">' . html_escape($label) . "</a></li>\n";
}

$html .= <<"HTML";
    </ul>
  </section>

  <section>
    <h2>Asset Digest Matrix</h2>
    <p>Assets present: $asset_summary{present}/$asset_summary{asset_count}. Required assets missing: $asset_summary{required_missing}.</p>
    <table>
      <thead><tr><th>Asset</th><th>Role</th><th>Required</th><th>Status</th><th>Bytes</th><th>SHA-256</th></tr></thead>
      <tbody>
HTML

for my $asset (@assets) {
  $html .= '        <tr><td>' . html_escape(display($asset->{name})) . '</td><td>'
    . html_escape(display($asset->{role})) . '</td><td>'
    . html_escape($asset->{required} ? 'true' : 'false') . '</td><td>'
    . html_escape(display($asset->{status})) . '</td><td>'
    . html_escape(display($asset->{bytes})) . '</td><td>'
    . html_escape(display($asset->{sha256})) . "</td></tr>\n";
}

$html .= <<"HTML";
      </tbody>
    </table>
  </section>
HTML

if ($diff) {
  my $diff_summary = $diff->{summary} || {};
  $html .= <<"HTML";
  <section>
    <h2>Release Diff</h2>
    <div class="grid">
      <div class="metric"><span class="label">Left</span><span class="value">@{[html_escape(display(($diff->{left} || {})->{version}))]} (@{[html_escape(display(($diff->{left} || {})->{tag}))]})</span></div>
      <div class="metric"><span class="label">Right</span><span class="value">@{[html_escape(display(($diff->{right} || {})->{version}))]} (@{[html_escape(display(($diff->{right} || {})->{tag}))]})</span></div>
      <div class="metric"><span class="label">Changed assets</span><span class="value">@{[html_escape(display($diff_summary->{changed}))]}</span></div>
      <div class="metric"><span class="label">Added assets</span><span class="value">@{[html_escape(display($diff_summary->{added}))]}</span></div>
      <div class="metric"><span class="label">Removed assets</span><span class="value">@{[html_escape(display($diff_summary->{removed}))]}</span></div>
      <div class="metric"><span class="label">Required missing</span><span class="value">@{[html_escape(display($diff_summary->{required_missing}))]}</span></div>
    </div>
  </section>
HTML
}

$html .= <<"HTML";
</main>
</body>
</html>
HTML

write_text(File::Spec->catfile($out_dir, 'index.html'), $html);

print "wrote: " . File::Spec->catfile($out_dir, 'index.html') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'evidence.json') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'README.md') . "\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
}

cmd_index() {
  local out_dir=""
  local title="Codex Maintainer Release Evidence Index"
  local site_dirs=()

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --site)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--site requires a value"
        site_dirs+=("$2")
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
        fail "unknown index argument: $1"
        ;;
    esac
  done

  [[ "${#site_dirs[@]}" -gt 0 ]] || fail "--site is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  local site_dir
  for site_dir in "${site_dirs[@]}"; do
    [[ -d "$site_dir" ]] || fail "evidence site directory not found: $site_dir"
    [[ -f "$site_dir/evidence.json" ]] || fail "missing evidence.json in $site_dir"
    [[ -f "$site_dir/index.html" ]] || fail "missing index.html in $site_dir"
  done

  mkdir -p "$out_dir/sites"

  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"
  local site_list
  site_list="$(printf '%s\n' "${site_dirs[@]}")"

  SITE_DIRS="$site_list" OUT_DIR="$out_dir" TITLE="$title" \
    TOOL_VERSION="$tool_version" GENERATED_AT="$generated_at" perl <<'PERL'
use strict;
use warnings;
use File::Basename qw(dirname);
use File::Copy qw(copy);
use File::Find qw(find);
use File::Path qw(make_path);
use File::Spec;
use JSON::PP;

sub fail {
  die "release-evidence: $_[0]\n";
}

sub slurp_json {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or fail("cannot read $path: $!");
  local $/;
  my $raw = <$fh>;
  close $fh;
  return decode_json($raw);
}

sub write_text {
  my ($path, $text) = @_;
  make_path(dirname($path));
  open my $fh, '>:encoding(UTF-8)', $path or fail("cannot write $path: $!");
  print {$fh} $text;
  close $fh;
}

sub html_escape {
  my ($text) = @_;
  $text = '' unless defined $text;
  $text =~ s/&/&amp;/g;
  $text =~ s/</&lt;/g;
  $text =~ s/>/&gt;/g;
  $text =~ s/"/&quot;/g;
  $text =~ s/'/&#39;/g;
  return $text;
}

sub display {
  my ($value) = @_;
  return '-' if !defined($value) || ref($value);
  return "$value";
}

sub safe_id {
  my ($value) = @_;
  $value = 'release' unless defined $value && length $value;
  $value =~ s{[^A-Za-z0-9._-]+}{-}g;
  $value =~ s{^-+|-+$}{}g;
  return length($value) ? $value : 'release';
}

sub semver_key {
  my ($version) = @_;
  return (0, 0, 0) unless defined $version && $version =~ /^(\d+)\.(\d+)\.(\d+)$/;
  return (0 + $1, 0 + $2, 0 + $3);
}

sub copy_tree {
  my ($source, $target) = @_;
  find({
    wanted => sub {
      return if -d $File::Find::name;
      my $rel = File::Spec->abs2rel($File::Find::name, $source);
      my $dest = File::Spec->catfile($target, split m{/}, $rel);
      make_path(dirname($dest));
      copy($File::Find::name, $dest) or fail("cannot copy $File::Find::name to $dest: $!");
    },
    no_chdir => 1,
  }, $source);
}

my @site_dirs = grep { length $_ } split /\n/, ($ENV{SITE_DIRS} || '');
my $out_dir = $ENV{OUT_DIR};
my %used_ids;
my @entries;

for my $site_dir (@site_dirs) {
  my $evidence_path = File::Spec->catfile($site_dir, 'evidence.json');
  my $evidence = slurp_json($evidence_path);
  fail("unsupported evidence schema in $site_dir") unless ($evidence->{schema_version} || '') eq '1.0';

  my $release = $evidence->{release} || {};
  my $tag = $release->{tag} || $release->{version} || '';
  my $base_id = safe_id($tag);
  my $id = $base_id;
  my $suffix = 2;
  while ($used_ids{$id}) {
    $id = "$base_id-$suffix";
    $suffix++;
  }
  $used_ids{$id} = 1;

  my $target = File::Spec->catdir($out_dir, 'sites', $id);
  copy_tree($site_dir, $target);

  push @entries, {
    id => $id,
    title => $evidence->{title} || $tag || $id,
    status => $evidence->{status} || 'unknown',
    version => $release->{version},
    tag => $release->{tag},
    commit => $release->{commit},
    artifact => $release->{artifact} || {},
    asset_digest_summary => $evidence->{asset_digest_summary} || {},
    release_diff => $evidence->{release_diff} || { present => JSON::PP::false },
    paths => {
      site => "sites/$id/index.html",
      evidence => "sites/$id/evidence.json",
    },
  };
}

@entries = sort {
  my @av = semver_key($a->{version});
  my @bv = semver_key($b->{version});
  ($bv[0] <=> $av[0]) || ($bv[1] <=> $av[1]) || ($bv[2] <=> $av[2]) || (($b->{tag} || '') cmp ($a->{tag} || ''))
} @entries;

my $blocked = 0;
for my $entry (@entries) {
  $blocked++ unless ($entry->{status} || '') eq 'pass';
}
my $status = $blocked ? 'blocked' : 'pass';

my $index = {
  schema_version => '1.0',
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  title => $ENV{TITLE},
  status => $status,
  site_count => scalar(@entries),
  blocked_count => $blocked,
  releases => \@entries,
};

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
write_text(File::Spec->catfile($out_dir, 'evidence-index.json'), $json->encode($index));

my $readme = "# $ENV{TITLE}\n\n"
  . "- Generated: $ENV{GENERATED_AT}\n"
  . "- Status: $status\n"
  . "- Releases: " . scalar(@entries) . "\n"
  . "- Blocked releases: $blocked\n\n"
  . "Open `index.html` for the release history or `evidence-index.json` for the machine-readable index.\n";
write_text(File::Spec->catfile($out_dir, 'README.md'), $readme);

my $html = <<"HTML";
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>@{[html_escape($ENV{TITLE})]}</title>
  <style>
    :root { color-scheme: light; --ink: #1f2937; --muted: #596273; --line: #d9dee7; --panel: #f6f8fb; --good: #0f766e; --bad: #b42318; }
    body { margin: 0; font: 15px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: #fff; }
    main { max-width: 1120px; margin: 0 auto; padding: 28px; }
    h1 { margin: 0 0 6px; font-size: 30px; letter-spacing: 0; }
    p { margin: 0 0 12px; color: var(--muted); }
    .status { display: inline-block; margin: 12px 0 18px; padding: 5px 10px; border-radius: 6px; font-weight: 700; color: #fff; background: var(--good); }
    .status.blocked { background: var(--bad); }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; }
    th, td { border: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
    th { background: var(--panel); }
    a { color: #1d4ed8; }
    code { background: var(--panel); padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
<main>
  <h1>@{[html_escape($ENV{TITLE})]}</h1>
  <p>Static release evidence history generated from release evidence site exports.</p>
  <div class="status @{[$status eq 'pass' ? '' : 'blocked']}">@{[html_escape($status)]}</div>
  <p>Releases: @{[scalar(@entries)]}. Blocked releases: $blocked.</p>
  <p><a href="evidence-index.json">Machine-readable index</a></p>
  <table>
    <thead><tr><th>Version</th><th>Status</th><th>Artifact</th><th>Assets</th><th>Required Missing</th><th>Release Diff</th><th>Links</th></tr></thead>
    <tbody>
HTML

for my $entry (@entries) {
  my $assets = $entry->{asset_digest_summary} || {};
  my $diff = $entry->{release_diff} || {};
  my $diff_label = $diff->{present} ? display($diff->{status}) : 'not included';
  $html .= '      <tr><td>' . html_escape(display($entry->{version})) . ' (' . html_escape(display($entry->{tag})) . ')</td><td>'
    . html_escape(display($entry->{status})) . '</td><td>'
    . html_escape(display(($entry->{artifact} || {})->{name})) . '<br><code>' . html_escape(display(($entry->{artifact} || {})->{sha256})) . '</code></td><td>'
    . html_escape(display($assets->{present})) . '/' . html_escape(display($assets->{asset_count})) . '</td><td>'
    . html_escape(display($assets->{required_missing})) . '</td><td>'
    . html_escape($diff_label) . '</td><td><a href="'
    . html_escape($entry->{paths}{site}) . '">site</a> | <a href="'
    . html_escape($entry->{paths}{evidence}) . "\">json</a></td></tr>\n";
}

$html .= <<"HTML";
    </tbody>
  </table>
</main>
</body>
</html>
HTML

write_text(File::Spec->catfile($out_dir, 'index.html'), $html);

print "wrote: " . File::Spec->catfile($out_dir, 'index.html') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'evidence-index.json') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'README.md') . "\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
}

subcommand="${1:-}"
[[ "$subcommand" == "site" || "$subcommand" == "index" ]] || fail "release-evidence requires subcommand: site or index"
shift || true
case "$subcommand" in
  site)
    cmd_site "$@"
    ;;
  index)
    cmd_index "$@"
    ;;
esac
