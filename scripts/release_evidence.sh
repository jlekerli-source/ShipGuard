#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-evidence

Usage:
  codex-maintainer release-evidence site --consume <consumer-proof-dir> --out <dir> [--diff <release-diff-dir>] [--title <title>]
  codex-maintainer release-evidence index --site <evidence-site-dir> [--site <evidence-site-dir> ...] --out <dir> [--title <title>]
  codex-maintainer release-evidence bundle --assets <release-assets-dir> --out <dir> [--version <version>] [--left <previous-release-assets-dir>] [--title <title>] [--index-title <title>]
  codex-maintainer release-evidence verify --dir <evidence-artifact-dir> --out <dir> [--require-diff auto|true|false] [--require-index auto|true|false]
  codex-maintainer release-evidence negative-index --fixture <negative-fixture-dir> --out <dir> [--title <title>]

Inputs:
  --consume must contain consumer-report.json and asset-digests.json.
  --diff may contain release-diff.json.
  --assets must contain downloaded release proof assets.
  --left may contain previous release proof assets for a diff.

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

Bundle outputs:
  consumer-proof/consumer-report.json
  release-diff/release-diff.json when --left is provided
  site/index.html
  index/evidence-index.json
  bundle.json
  README.md

Verify outputs:
  evidence-verify.json
  evidence-verify.md
  badge.json

Negative fixture index outputs:
  negative-fixture-index.json
  negative-fixture-index.md
  badge.json
  runs/<case>/evidence-verify.json
  runs/<case>/evidence-verify.md
  runs/<case>/badge.json
USAGE
}

fail() {
  echo "release-evidence: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
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

cmd_bundle() {
  local assets_dir=""
  local left_dir=""
  local out_dir=""
  local version=""
  local title="Codex Maintainer Release Evidence"
  local index_title="Codex Maintainer Release Evidence Index"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --assets)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--assets requires a value"
        assets_dir="$2"
        shift 2
        ;;
      --left)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--left requires a value"
        left_dir="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
        shift 2
        ;;
      --version)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--version requires a value"
        version="$2"
        shift 2
        ;;
      --title)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--title requires a value"
        title="$2"
        shift 2
        ;;
      --index-title)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--index-title requires a value"
        index_title="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown bundle argument: $1"
        ;;
    esac
  done

  [[ -n "$assets_dir" ]] || fail "--assets is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$assets_dir" ]] || fail "release assets directory not found: $assets_dir"
  if [[ -n "$left_dir" ]]; then
    [[ -d "$left_dir" ]] || fail "previous release assets directory not found: $left_dir"
  fi

  local assets_abs
  local out_abs
  assets_abs="$(cd "$assets_dir" && pwd -P)"
  mkdir -p "$(dirname "$out_dir")"
  out_abs="$(cd "$(dirname "$out_dir")" && pwd -P)/$(basename "$out_dir")"
  case "$out_abs/" in
    "$assets_abs"/*)
      fail "--out must not be inside --assets"
      ;;
  esac
  if [[ -n "$left_dir" ]]; then
    local left_abs
    left_abs="$(cd "$left_dir" && pwd -P)"
    case "$out_abs/" in
      "$left_abs"/*)
        fail "--out must not be inside --left"
        ;;
    esac
  fi

  local consumer_dir="$out_dir/consumer-proof"
  local diff_dir="$out_dir/release-diff"
  local site_dir="$out_dir/site"
  local index_dir="$out_dir/index"
  rm -rf "$consumer_dir" "$diff_dir" "$site_dir" "$index_dir"
  mkdir -p "$out_dir"

  local consume_args=(release-consume verify --dir "$assets_dir" --out "$consumer_dir")
  if [[ -n "$version" ]]; then
    consume_args+=(--version "$version")
  fi
  "$tool_root/bin/codex-maintainer" "${consume_args[@]}"

  local site_args=(release-evidence site --consume "$consumer_dir" --out "$site_dir" --title "$title")
  local diff_included="false"
  if [[ -n "$left_dir" ]]; then
    "$tool_root/bin/codex-maintainer" release-diff compare \
      --left "$left_dir" \
      --right "$assets_dir" \
      --out "$diff_dir"
    site_args+=(--diff "$diff_dir")
    diff_included="true"
  fi

  "$tool_root/bin/codex-maintainer" "${site_args[@]}"
  "$tool_root/bin/codex-maintainer" release-evidence index \
    --site "$site_dir" \
    --out "$index_dir" \
    --title "$index_title"

  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  {
    echo "{"
    echo "  \"schema_version\": \"1.0\","
    echo "  \"tool_version\": $(json_string "$tool_version"),"
    echo "  \"generated_at\": $(json_string "$generated_at"),"
    echo "  \"status\": \"pass\","
    echo "  \"assets_dir\": $(json_string "$assets_dir"),"
    echo "  \"left_dir\": $(json_string "$left_dir"),"
    echo "  \"version\": $(json_string "$version"),"
    echo "  \"diff_included\": $diff_included,"
    echo "  \"outputs\": {"
    echo "    \"consumer_report\": \"consumer-proof/consumer-report.json\","
    if [[ "$diff_included" == "true" ]]; then
      echo "    \"release_diff\": \"release-diff/release-diff.json\","
    else
      echo "    \"release_diff\": null,"
    fi
    echo "    \"evidence_site\": \"site/index.html\","
    echo "    \"evidence_json\": \"site/evidence.json\","
    echo "    \"evidence_index\": \"index/evidence-index.json\""
    echo "  }"
    echo "}"
  } > "$out_dir/bundle.json"

  {
    echo "# Codex Maintainer Release Evidence Bundle"
    echo
    echo "- Generated: $generated_at"
    echo "- Status: pass"
    echo "- Assets: $assets_dir"
    echo "- Previous assets: ${left_dir:-not included}"
    echo "- Version: ${version:-auto}"
    echo "- Consumer proof: consumer-proof/consumer-report.json"
    if [[ "$diff_included" == "true" ]]; then
      echo "- Release diff: release-diff/release-diff.json"
    else
      echo "- Release diff: not included"
    fi
    echo "- Evidence site: site/index.html"
    echo "- Evidence index: index/evidence-index.json"
    echo
    echo "Open \`site/index.html\` for the release evidence page or \`index/index.html\` for the local evidence history."
  } > "$out_dir/README.md"

  echo "wrote: $out_dir/bundle.json"
  echo "wrote: $out_dir/README.md"
  echo "status: pass"
}

cmd_verify() {
  local evidence_dir=""
  local out_dir=""
  local require_diff="auto"
  local require_index="auto"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --dir)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--dir requires a value"
        evidence_dir="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
        shift 2
        ;;
      --require-diff)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--require-diff requires a value"
        require_diff="$2"
        shift 2
        ;;
      --require-index)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--require-index requires a value"
        require_index="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        fail "unknown verify argument: $1"
        ;;
    esac
  done

  [[ -n "$evidence_dir" ]] || fail "--dir is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$evidence_dir" ]] || fail "evidence artifact directory not found: $evidence_dir"
  [[ "$require_diff" == "auto" || "$require_diff" == "true" || "$require_diff" == "false" ]] || fail "--require-diff must be auto, true, or false"
  [[ "$require_index" == "auto" || "$require_index" == "true" || "$require_index" == "false" ]] || fail "--require-index must be auto, true, or false"

  mkdir -p "$out_dir"
  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  EVIDENCE_DIR="$evidence_dir" OUT_DIR="$out_dir" REQUIRE_DIFF="$require_diff" \
    REQUIRE_INDEX="$require_index" TOOL_VERSION="$tool_version" GENERATED_AT="$generated_at" perl <<'PERL'
use strict;
use warnings;
use File::Spec;
use JSON::PP;

sub read_json {
  my ($path) = @_;
  open my $fh, '<:encoding(UTF-8)', $path or die "release-evidence: cannot read $path: $!\n";
  local $/;
  my $raw = <$fh>;
  close $fh;
  return decode_json($raw);
}

sub write_text {
  my ($path, $text) = @_;
  open my $fh, '>:encoding(UTF-8)', $path or die "release-evidence: cannot write $path: $!\n";
  print {$fh} $text;
  close $fh;
}

sub bool_value {
  my ($value) = @_;
  return $value ? JSON::PP::true : JSON::PP::false;
}

sub display {
  my ($value) = @_;
  return '-' if !defined($value) || ref($value);
  return "$value";
}

sub rel_file {
  my ($base, $rel) = @_;
  return undef unless defined($rel) && !ref($rel) && length($rel);
  return File::Spec->catfile($base, split m{/}, $rel);
}

sub rel_exists {
  my ($base, $rel) = @_;
  my $path = rel_file($base, $rel);
  return defined($path) && -f $path;
}

my $root = $ENV{EVIDENCE_DIR};
my $out_dir = $ENV{OUT_DIR};
my $require_diff = $ENV{REQUIRE_DIFF};
my $require_index = $ENV{REQUIRE_INDEX};
my @checks;

sub check {
  my ($name, $passed, $detail) = @_;
  push @checks, {
    name => $name,
    status => $passed ? 'pass' : 'fail',
    detail => defined($detail) ? $detail : '',
  };
}

my $site_dir = -f File::Spec->catfile($root, 'site', 'evidence.json')
  ? File::Spec->catdir($root, 'site')
  : (-f File::Spec->catfile($root, 'evidence.json') ? $root : '');
check('evidence json present', length($site_dir) > 0, length($site_dir) ? $site_dir : 'missing site/evidence.json');

my ($evidence, $consumer, $digests, $diff, $index, $bundle);
if (length($site_dir)) {
  $evidence = read_json(File::Spec->catfile($site_dir, 'evidence.json'));
  check('evidence schema', (($evidence->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
  check('evidence status', (($evidence->{status} || '') eq 'pass'), 'status must be pass');
  check('evidence html present', -f File::Spec->catfile($site_dir, 'index.html'), 'index.html');

  my $sources = $evidence->{sources} || {};
  my $consumer_path = rel_file($site_dir, $sources->{consumer_report});
  my $digests_path = rel_file($site_dir, $sources->{asset_digests});
  check('consumer report source present', defined($consumer_path) && -f $consumer_path, display($sources->{consumer_report}));
  check('asset digests source present', defined($digests_path) && -f $digests_path, display($sources->{asset_digests}));

  if (defined($consumer_path) && -f $consumer_path) {
    $consumer = read_json($consumer_path);
    check('consumer schema', (($consumer->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
    check('consumer status', (($consumer->{status} || '') eq 'pass'), 'status must be pass');
  }
  if (defined($digests_path) && -f $digests_path) {
    $digests = read_json($digests_path);
    check('asset digest schema', (($digests->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
  }

  my $release = $evidence->{release} || {};
  my $artifact = $release->{artifact} || {};
  check('release identity present', length($release->{version} || '') && length($release->{tag} || ''), 'version and tag');
  check('artifact digest present', length($artifact->{name} || '') && length($artifact->{sha256} || ''), 'artifact name and sha256');

  if ($consumer) {
    my $consumer_artifact = $consumer->{artifact} || {};
    check('consumer release matches evidence',
      display($consumer->{version}) eq display($release->{version}) &&
      display($consumer->{tag}) eq display($release->{tag}),
      display($consumer->{version}) . ' / ' . display($release->{version}));
    check('consumer artifact matches evidence',
      display($consumer_artifact->{name}) eq display($artifact->{name}) &&
      display($consumer_artifact->{sha256}) eq display($artifact->{sha256}),
      display($consumer_artifact->{name}) . ' / ' . display($artifact->{name}));
  }

  if ($digests) {
    my @assets = @{ $digests->{assets} || [] };
    my $present = 0;
    my $missing = 0;
    my $required_missing = 0;
    for my $asset (@assets) {
      if (($asset->{status} || '') eq 'present') {
        $present++;
      } else {
        $missing++;
        $required_missing++ if $asset->{required};
      }
    }
    my $summary = $evidence->{asset_digest_summary} || {};
    check('asset digest summary matches',
      display($summary->{asset_count}) eq display(scalar(@assets)) &&
      display($summary->{present}) eq display($present) &&
      display($summary->{missing}) eq display($missing) &&
      display($summary->{required_missing}) eq display($required_missing),
      "$present/" . scalar(@assets) . " present");
    check('required assets present', $required_missing == 0, "$required_missing required missing");
  }

  my $diff_state = $evidence->{release_diff} || {};
  my $diff_present = $diff_state->{present} ? 1 : 0;
  my $diff_source = $sources->{release_diff};
  if ($require_diff eq 'true') {
    check('release diff required', $diff_present, 'release_diff.present must be true');
  }
  if ($diff_present) {
    my $diff_path = rel_file($site_dir, $diff_source);
    check('release diff source present', defined($diff_path) && -f $diff_path, display($diff_source));
    if (defined($diff_path) && -f $diff_path) {
      $diff = read_json($diff_path);
      check('release diff schema', (($diff->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
      check('release diff status', (($diff->{status} || '') eq 'pass'), 'status must be pass');
      check('release diff matches evidence',
        display($diff->{status}) eq display($diff_state->{status}),
        display($diff->{status}) . ' / ' . display($diff_state->{status}));
    }
  }
}

my $index_file = -f File::Spec->catfile($root, 'index', 'evidence-index.json')
  ? File::Spec->catfile($root, 'index', 'evidence-index.json')
  : (-f File::Spec->catfile($root, 'evidence-index.json') ? File::Spec->catfile($root, 'evidence-index.json') : '');
if ($require_index eq 'true') {
  check('evidence index required', length($index_file) > 0, 'evidence-index.json');
}
if (length($index_file)) {
  $index = read_json($index_file);
  check('evidence index schema', (($index->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
  check('evidence index status', (($index->{status} || '') eq 'pass'), 'status must be pass');
  check('evidence index has releases', scalar(@{ $index->{releases} || [] }) > 0, 'at least one release');
  if ($evidence) {
    my $release = $evidence->{release} || {};
    my $matched = 0;
    for my $entry (@{ $index->{releases} || [] }) {
      if (display($entry->{version}) eq display($release->{version}) && display($entry->{tag}) eq display($release->{tag})) {
        $matched = 1;
        last;
      }
    }
    check('evidence index contains release', $matched, display($release->{tag}));
  }
}

my $bundle_file = File::Spec->catfile($root, 'bundle.json');
if (-f $bundle_file) {
  $bundle = read_json($bundle_file);
  check('bundle schema', (($bundle->{schema_version} || '') eq '1.0'), 'schema_version must be 1.0');
  check('bundle status', (($bundle->{status} || '') eq 'pass'), 'status must be pass');
  my $outputs = $bundle->{outputs} || {};
  for my $pair (
    ['bundle consumer report output', $outputs->{consumer_report}],
    ['bundle evidence json output', $outputs->{evidence_json}],
    ['bundle evidence index output', $outputs->{evidence_index}],
  ) {
    check($pair->[0], rel_exists($root, $pair->[1]), display($pair->[1]));
  }
  if ($bundle->{diff_included}) {
    check('bundle release diff output', rel_exists($root, $outputs->{release_diff}), display($outputs->{release_diff}));
  }
  if ($evidence) {
    my $diff_present = ($evidence->{release_diff} || {})->{present} ? 1 : 0;
    check('bundle diff flag matches evidence', ($bundle->{diff_included} ? 1 : 0) == $diff_present, 'diff_included');
  }
}

my $failed = 0;
for my $check (@checks) {
  $failed++ if ($check->{status} || '') ne 'pass';
}
my $status = $failed ? 'blocked' : 'pass';
my $release = $evidence ? ($evidence->{release} || {}) : {};
my $artifact = $release->{artifact} || {};

my $report = {
  schema_version => '1.0',
  tool_version => $ENV{TOOL_VERSION},
  generated_at => $ENV{GENERATED_AT},
  status => $status,
  input_dir => $root,
  require_diff => $require_diff,
  require_index => $require_index,
  release => {
    version => $release->{version},
    tag => $release->{tag},
    commit => $release->{commit},
    artifact => {
      name => $artifact->{name},
      sha256 => $artifact->{sha256},
      bytes => $artifact->{bytes},
    },
  },
  summary => {
    checks => scalar(@checks),
    failed => $failed,
    site_present => bool_value(length($site_dir) > 0),
    index_present => bool_value(length($index_file) > 0),
    bundle_present => bool_value(-f $bundle_file),
    diff_present => bool_value($diff ? 1 : 0),
  },
  checks => \@checks,
};

my $json = JSON::PP->new->utf8->canonical(1)->pretty;
write_text(File::Spec->catfile($out_dir, 'evidence-verify.json'), $json->encode($report));

my $md = "# Release Evidence Verification\n\n"
  . "- Generated: $ENV{GENERATED_AT}\n"
  . "- Status: $status\n"
  . "- Version: " . display($release->{version}) . "\n"
  . "- Tag: " . display($release->{tag}) . "\n"
  . "- Artifact: " . display($artifact->{name}) . "\n"
  . "- Artifact SHA-256: " . display($artifact->{sha256}) . "\n"
  . "- Checks: " . scalar(@checks) . "\n"
  . "- Failed checks: $failed\n\n"
  . "## Checks\n\n"
  . "| Check | Status | Detail |\n"
  . "| --- | --- | --- |\n";
for my $check (@checks) {
  my $detail = display($check->{detail});
  $detail =~ s/\|/\\|/g;
  $md .= "| $check->{name} | $check->{status} | $detail |\n";
}
write_text(File::Spec->catfile($out_dir, 'evidence-verify.md'), $md);

my $badge = {
  schemaVersion => 1,
  label => 'release evidence',
  message => ($status eq 'pass' ? 'pass ' . display($release->{tag}) : 'blocked'),
  color => ($status eq 'pass' ? 'brightgreen' : 'red'),
};
write_text(File::Spec->catfile($out_dir, 'badge.json'), $json->encode($badge));

print "wrote: " . File::Spec->catfile($out_dir, 'evidence-verify.json') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'evidence-verify.md') . "\n";
print "wrote: " . File::Spec->catfile($out_dir, 'badge.json') . "\n";
print "status: $status\n";
exit($status eq 'pass' ? 0 : 1);
PERL
}

cmd_negative_index() {
  local fixture_dir=""
  local out_dir=""
  local title="Release Evidence Negative Fixture Index"

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --fixture)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--fixture requires a value"
        fixture_dir="$2"
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
        fail "unknown negative-index argument: $1"
        ;;
    esac
  done

  [[ -n "$fixture_dir" ]] || fail "--fixture is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -d "$fixture_dir" ]] || fail "negative fixture directory not found: $fixture_dir"
  [[ -f "$fixture_dir/cases.tsv" ]] || fail "missing cases.tsv in $fixture_dir"

  mkdir -p "$out_dir/runs"

  local tool_version
  tool_version="$(sed -n '1p' "$tool_root/VERSION")"
  local generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"
  local results_file="$out_dir/results.tsv"
  : > "$results_file"

  local case_name expected_check description case_dir run_dir exit_code
  local blocked expected_failed badge_blocked files_present case_status
  local case_count=0
  local expected_blocked_count=0
  local passed_count=0
  local failed_count=0

  while IFS=$'\t' read -r case_name expected_check description || [[ -n "$case_name" ]]; do
    [[ -n "$case_name" ]] || continue
    [[ "${case_name:0:1}" != "#" ]] || continue
    [[ "$case_name" != "case" ]] || continue
    [[ "$case_name" =~ ^[A-Za-z0-9._-]+$ ]] || fail "invalid case name in cases.tsv: $case_name"
    [[ -n "$expected_check" ]] || fail "missing expected_check for case: $case_name"

    case_count=$((case_count + 1))
    case_dir="$fixture_dir/$case_name"
    run_dir="$out_dir/runs/$case_name"
    [[ -d "$case_dir" ]] || fail "negative fixture case directory not found: $case_dir"
    mkdir -p "$run_dir"

    if CODEX_MAINTAINER_GENERATED_AT="$generated_at" "$tool_root/bin/codex-maintainer" \
      release-evidence verify \
      --dir "$case_dir" \
      --out "$run_dir" >/dev/null 2>&1; then
      exit_code=0
    else
      exit_code=$?
    fi

    files_present=false
    if [[ -f "$run_dir/evidence-verify.json" && -f "$run_dir/evidence-verify.md" && -f "$run_dir/badge.json" ]]; then
      files_present=true
    fi

    blocked=false
    if [[ -f "$run_dir/evidence-verify.json" ]] && grep -q '"status" : "blocked"' "$run_dir/evidence-verify.json"; then
      blocked=true
    fi

    expected_failed=false
    if [[ -f "$run_dir/evidence-verify.md" ]] && grep -Fq "| $expected_check | fail |" "$run_dir/evidence-verify.md"; then
      expected_failed=true
    fi

    badge_blocked=false
    if [[ -f "$run_dir/badge.json" ]] && grep -q '"message" : "blocked"' "$run_dir/badge.json"; then
      badge_blocked=true
    fi

    case_status=fail
    if [[ "$exit_code" -ne 0 && "$files_present" == "true" && "$blocked" == "true" && "$expected_failed" == "true" && "$badge_blocked" == "true" ]]; then
      case_status=pass
      expected_blocked_count=$((expected_blocked_count + 1))
      passed_count=$((passed_count + 1))
    else
      failed_count=$((failed_count + 1))
    fi

    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$case_name" "$expected_check" "${description:-}" "$case_status" "$exit_code" \
      "$blocked" "$expected_failed" "$badge_blocked" >> "$results_file"
  done < "$fixture_dir/cases.tsv"

  [[ "$case_count" -gt 0 ]] || fail "cases.tsv must contain at least one case"

  local status="pass"
  [[ "$failed_count" -ne 0 ]] && status="blocked"

  {
    echo "{"
    echo "  \"schema_version\" : \"1.0\","
    echo "  \"tool_version\" : $(json_string "$tool_version"),"
    echo "  \"generated_at\" : $(json_string "$generated_at"),"
    echo "  \"title\" : $(json_string "$title"),"
    echo "  \"status\" : $(json_string "$status"),"
    echo "  \"fixture_dir\" : $(json_string "$fixture_dir"),"
    echo "  \"case_count\" : $case_count,"
    echo "  \"expected_blocked_count\" : $expected_blocked_count,"
    echo "  \"passed_count\" : $passed_count,"
    echo "  \"failed_count\" : $failed_count,"
    echo "  \"cases\" : ["
    local first=true
    while IFS=$'\t' read -r case_name expected_check description case_status exit_code blocked expected_failed badge_blocked; do
      if [[ "$first" == "true" ]]; then
        first=false
      else
        echo ","
      fi
      echo "    {"
      echo "      \"name\" : $(json_string "$case_name"),"
      echo "      \"expected_check\" : $(json_string "$expected_check"),"
      echo "      \"description\" : $(json_string "$description"),"
      echo "      \"status\" : $(json_string "$case_status"),"
      echo "      \"verify_exit_code\" : $exit_code,"
      echo "      \"blocked\" : $blocked,"
      echo "      \"expected_check_failed\" : $expected_failed,"
      echo "      \"badge_blocked\" : $badge_blocked,"
      echo "      \"report\" : $(json_string "runs/$case_name/evidence-verify.json"),"
      echo "      \"markdown\" : $(json_string "runs/$case_name/evidence-verify.md"),"
      echo "      \"badge\" : $(json_string "runs/$case_name/badge.json")"
      echo -n "    }"
    done < "$results_file"
    echo
    echo "  ]"
    echo "}"
  } > "$out_dir/negative-fixture-index.json"

  {
    echo "# $title"
    echo
    echo "- Generated: $generated_at"
    echo "- Status: $status"
    echo "- Fixture directory: $fixture_dir"
    echo "- Cases: $case_count"
    echo "- Expected blocked cases: $expected_blocked_count"
    echo "- Failed index checks: $failed_count"
    echo
    echo "| Case | Status | Expected blocked check | Verify exit | Blocked report | Badge blocked | Description |"
    echo "| --- | --- | --- | --- | --- | --- | --- |"
    while IFS=$'\t' read -r case_name expected_check description case_status exit_code blocked expected_failed badge_blocked; do
      local safe_description="$description"
      safe_description="${safe_description//|/\\|}"
      echo "| $case_name | $case_status | $expected_check | $exit_code | $blocked | $badge_blocked | $safe_description |"
    done < "$results_file"
    echo
    echo "Per-case verifier outputs are under \`runs/<case>/\`."
  } > "$out_dir/negative-fixture-index.md"

  {
    echo "{"
    echo "  \"schemaVersion\" : 1,"
    echo "  \"label\" : \"negative evidence fixtures\","
    if [[ "$status" == "pass" ]]; then
      echo "  \"message\" : \"pass $passed_count/$case_count\","
      echo "  \"color\" : \"brightgreen\""
    else
      echo "  \"message\" : \"blocked $failed_count/$case_count\","
      echo "  \"color\" : \"red\""
    fi
    echo "}"
  } > "$out_dir/badge.json"

  rm -f "$results_file"

  echo "wrote: $out_dir/negative-fixture-index.json"
  echo "wrote: $out_dir/negative-fixture-index.md"
  echo "wrote: $out_dir/badge.json"
  echo "status: $status"
  [[ "$status" == "pass" ]]
}

subcommand="${1:-}"
[[ "$subcommand" == "site" || "$subcommand" == "index" || "$subcommand" == "bundle" || "$subcommand" == "verify" || "$subcommand" == "negative-index" ]] || fail "release-evidence requires subcommand: site, index, bundle, verify, or negative-index"
shift || true
case "$subcommand" in
  site)
    cmd_site "$@"
    ;;
  index)
    cmd_index "$@"
    ;;
  bundle)
    cmd_bundle "$@"
    ;;
  verify)
    cmd_verify "$@"
    ;;
  negative-index)
    cmd_negative_index "$@"
    ;;
esac
