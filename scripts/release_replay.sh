#!/usr/bin/env bash

set -euo pipefail

tool_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
codex-maintainer release-replay

Usage:
  codex-maintainer release-replay verify --manifest <release-manifest.json> --tarball <release.tar.gz> --out <dir> [--index <release-index.json>] [--ledger <proof-ledger.md>]

Outputs:
  replay-report.json
  replay-report.md
USAGE
}

fail() {
  echo "release-replay: $*" >&2
  exit 1
}

json_escape() {
  perl -0pe 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}

json_string() {
  printf '"%s"' "$(printf '%s' "$1" | json_escape)"
}

md_cell() {
  printf '%s' "$1" | sed 's/|/\\|/g'
}

cmd_verify() {
  local manifest_file=""
  local tarball=""
  local index_file=""
  local ledger_file=""
  local out_dir=""

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --manifest)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--manifest requires a value"
        manifest_file="$2"
        shift 2
        ;;
      --tarball)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--tarball requires a value"
        tarball="$2"
        shift 2
        ;;
      --index)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--index requires a value"
        index_file="$2"
        shift 2
        ;;
      --ledger)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--ledger requires a value"
        ledger_file="$2"
        shift 2
        ;;
      --out)
        [[ "$#" -ge 2 && -n "${2:-}" ]] || fail "--out requires a value"
        out_dir="$2"
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

  [[ -n "$manifest_file" ]] || fail "--manifest is required"
  [[ -n "$tarball" ]] || fail "--tarball is required"
  [[ -n "$out_dir" ]] || fail "--out is required"
  [[ -f "$manifest_file" ]] || fail "manifest not found: $manifest_file"
  [[ -f "$tarball" ]] || fail "tarball not found: $tarball"
  [[ -z "$index_file" || -f "$index_file" ]] || fail "index not found: $index_file"
  [[ -z "$ledger_file" || -f "$ledger_file" ]] || fail "ledger not found: $ledger_file"

  local manifest_fields
  manifest_fields="$(MANIFEST_FILE="$manifest_file" perl <<'PERL'
use strict;
use warnings;
use JSON::PP;

sub fail {
  die "release-replay: $_[0]\n";
}

open my $fh, '<:encoding(UTF-8)', $ENV{MANIFEST_FILE} or fail("cannot read manifest: $!");
local $/;
my $manifest = decode_json(<$fh>);
close $fh;

fail("unsupported manifest schema") unless ($manifest->{schema_version} || '') eq '1.0';
my $artifact = $manifest->{artifact} || fail("manifest missing artifact");
for my $required (qw(version tag commit generated_at)) {
  fail("manifest missing $required") unless length($manifest->{$required} || '');
}
for my $required (qw(name path bytes sha256)) {
  fail("manifest missing artifact $required") unless length($artifact->{$required} || '');
}

my $proofs = $manifest->{proofs} || {};
print join("\t",
  $manifest->{version},
  $manifest->{tag},
  $manifest->{commit},
  $artifact->{name},
  $artifact->{path},
  $artifact->{bytes},
  $artifact->{sha256},
  $proofs->{release_url} || '',
  $proofs->{ci_run_url} || '',
  $proofs->{issue_url} || '',
), "\n";
PERL
)"

  local version tag commit artifact_name artifact_path artifact_bytes artifact_sha release_url ci_run_url issue_url
  IFS=$'\t' read -r version tag commit artifact_name artifact_path artifact_bytes artifact_sha release_url ci_run_url issue_url <<< "$manifest_fields"

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN

  mkdir -p "$out_dir"

  local actual_name actual_bytes actual_sha generated_at
  actual_name="$(basename "$tarball")"
  actual_bytes="$(wc -c < "$tarball" | tr -d '[:space:]')"
  actual_sha="$(shasum -a 256 "$tarball" | awk '{print $1}')"
  generated_at="${CODEX_MAINTAINER_GENERATED_AT:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

  local check_names=()
  local check_statuses=()
  local check_details=()

  add_check() {
    check_statuses+=("$1")
    check_names+=("$2")
    check_details+=("$3")
  }

  add_check "pass" "manifest schema" "manifest schema 1.0 parsed"

  if [[ "$artifact_name" == "$actual_name" ]]; then
    add_check "pass" "artifact name" "$artifact_name matches tarball filename"
  else
    add_check "blocked" "artifact name" "manifest has $artifact_name but tarball is $actual_name"
  fi

  if [[ "$artifact_path" == "$artifact_name" && "$artifact_path" != /* && "$artifact_path" != *"/"* && "$artifact_path" != *".."* ]]; then
    add_check "pass" "artifact path portability" "$artifact_path is portable"
  else
    add_check "blocked" "artifact path portability" "$artifact_path is not a portable artifact path"
  fi

  if [[ "$artifact_bytes" == "$actual_bytes" ]]; then
    add_check "pass" "artifact byte count" "$actual_bytes bytes match"
  else
    add_check "blocked" "artifact byte count" "expected $artifact_bytes bytes, got $actual_bytes"
  fi

  if [[ "$artifact_sha" == "$actual_sha" ]]; then
    add_check "pass" "artifact sha256" "$actual_sha matches manifest"
  else
    add_check "blocked" "artifact sha256" "expected $artifact_sha, got $actual_sha"
  fi

  if [[ "$release_url" == https://github.com/*/releases/tag/"$tag" && "$ci_run_url" == https://github.com/*/actions/runs/* ]]; then
    add_check "pass" "public proof urls" "release and CI URLs are present"
  else
    add_check "blocked" "public proof urls" "manifest must include GitHub release and CI run URLs"
  fi

  local tar_list="$tmp_dir/tar-list.txt"
  local tar_ok="false"
  if tar -tzf "$tarball" > "$tar_list"; then
    tar_ok="true"
    add_check "pass" "tarball readable" "tar list is readable"
  else
    add_check "blocked" "tarball readable" "tar list failed"
  fi

  if [[ "$tar_ok" == "true" ]]; then
    local package_root_name="codex-maintainer-v$version"
    if grep -q "^$package_root_name/bin/codex-maintainer$" "$tar_list" &&
      grep -q "^$package_root_name/VERSION$" "$tar_list" &&
      grep -q "^$package_root_name/scripts/install.sh$" "$tar_list"; then
      add_check "pass" "release runtime files" "bin, VERSION, and installer are present"
    else
      add_check "blocked" "release runtime files" "expected runtime files are missing from $package_root_name"
    fi

    if grep -Eq '(^|/)(\.git|dist|DerivedData|\.cache|\.DS_Store)(/|$)' "$tar_list"; then
      add_check "blocked" "forbidden tar entries" "tarball contains VCS, cache, build, or dist entries"
    else
      add_check "pass" "forbidden tar entries" "no VCS, cache, build, or dist entries found"
    fi

    local extract_dir="$tmp_dir/extract"
    mkdir -p "$extract_dir"
    if tar -xzf "$tarball" -C "$extract_dir"; then
      local mac_user_path="/""Users/"
      local linux_home_path="/""home/"
      local secret_like_pattern='ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}'
      if grep -RIEq "$mac_user_path|$linux_home_path|$secret_like_pattern" "$extract_dir"; then
        add_check "blocked" "private path and secret scan" "extracted release contains a local path or secret-looking token"
      else
        add_check "pass" "private path and secret scan" "no local path or secret-looking token found"
      fi
    else
      add_check "blocked" "tarball extraction" "tar extraction failed"
    fi
  fi

  if [[ -n "$index_file" ]]; then
    local index_detail
    if index_detail="$(INDEX_FILE="$index_file" VERSION_VALUE="$version" TAG_VALUE="$tag" COMMIT_VALUE="$commit" SHA_VALUE="$artifact_sha" perl <<'PERL' 2>&1
use strict;
use warnings;
use JSON::PP;

sub fail {
  die "release-replay: $_[0]\n";
}

open my $fh, '<:encoding(UTF-8)', $ENV{INDEX_FILE} or fail("cannot read release index: $!");
local $/;
my $index = decode_json(<$fh>);
close $fh;

fail("unsupported release index schema") unless ($index->{schema_version} || '') eq '1.0';
my @matches = grep { ($_->{version} || '') eq $ENV{VERSION_VALUE} } @{ $index->{releases} || [] };
fail("release index missing version $ENV{VERSION_VALUE}") unless @matches == 1;
my $row = $matches[0];
fail("release index tag mismatch") unless ($row->{tag} || '') eq $ENV{TAG_VALUE};
fail("release index commit mismatch") unless ($row->{commit} || '') eq $ENV{COMMIT_VALUE};
fail("release index sha mismatch") unless (($row->{artifact} || {})->{sha256} || '') eq $ENV{SHA_VALUE};
print "release index matches version $ENV{VERSION_VALUE}";
PERL
)"; then
      add_check "pass" "release index replay" "$index_detail"
    else
      add_check "blocked" "release index replay" "$index_detail"
    fi
  else
    add_check "skipped" "release index replay" "no release index supplied"
  fi

  if [[ -n "$ledger_file" ]]; then
    local ledger_missing=()
    grep -Fq -- "- Version: $version" "$ledger_file" || ledger_missing+=("version")
    grep -Fq -- "- Tag: $tag" "$ledger_file" || ledger_missing+=("tag")
    grep -Fq -- "- Artifact SHA-256: $artifact_sha" "$ledger_file" || ledger_missing+=("sha256")
    [[ -z "$release_url" ]] || grep -Fq -- "$release_url" "$ledger_file" || ledger_missing+=("release_url")
    if [[ "${#ledger_missing[@]}" -eq 0 ]]; then
      add_check "pass" "proof ledger replay" "proof ledger matches manifest identity"
    else
      add_check "blocked" "proof ledger replay" "proof ledger missing ${ledger_missing[*]}"
    fi
  else
    add_check "skipped" "proof ledger replay" "no proof ledger supplied"
  fi

  local status="pass"
  local pass_count=0
  local blocked_count=0
  local skipped_count=0
  local i
  for i in "${!check_statuses[@]}"; do
    case "${check_statuses[$i]}" in
      pass)
        pass_count=$((pass_count + 1))
        ;;
      blocked)
        blocked_count=$((blocked_count + 1))
        status="blocked"
        ;;
      skipped)
        skipped_count=$((skipped_count + 1))
        ;;
    esac
  done

  local report_json="$out_dir/replay-report.json"
  local report_md="$out_dir/replay-report.md"
  {
    echo "{"
    echo "  \"schema_version\": \"1.0\","
    echo "  \"tool_version\": $(json_string "$(sed -n '1p' "$tool_root/VERSION")"),"
    echo "  \"generated_at\": $(json_string "$generated_at"),"
    echo "  \"status\": $(json_string "$status"),"
    echo "  \"version\": $(json_string "$version"),"
    echo "  \"tag\": $(json_string "$tag"),"
    echo "  \"commit\": $(json_string "$commit"),"
    echo "  \"artifact\": {"
    echo "    \"name\": $(json_string "$artifact_name"),"
    echo "    \"expected_bytes\": $artifact_bytes,"
    echo "    \"actual_bytes\": $actual_bytes,"
    echo "    \"expected_sha256\": $(json_string "$artifact_sha"),"
    echo "    \"actual_sha256\": $(json_string "$actual_sha")"
    echo "  },"
    echo "  \"proofs\": {"
    echo "    \"release_url\": $(json_string "$release_url"),"
    echo "    \"ci_run_url\": $(json_string "$ci_run_url"),"
    echo "    \"issue_url\": $(json_string "$issue_url")"
    echo "  },"
    echo "  \"inputs\": {"
    echo "    \"manifest\": $(json_string "$(basename "$manifest_file")"),"
    echo "    \"tarball\": $(json_string "$(basename "$tarball")"),"
    echo "    \"index\": $(json_string "${index_file:+$(basename "$index_file")}"),"
    echo "    \"ledger\": $(json_string "${ledger_file:+$(basename "$ledger_file")}")"
    echo "  },"
    echo "  \"summary\": {"
    echo "    \"pass\": $pass_count,"
    echo "    \"blocked\": $blocked_count,"
    echo "    \"skipped\": $skipped_count"
    echo "  },"
    echo "  \"checks\": ["
    for i in "${!check_names[@]}"; do
      [[ "$i" -eq 0 ]] || echo "    },"
      echo "    {"
      echo "      \"name\": $(json_string "${check_names[$i]}"),"
      echo "      \"status\": $(json_string "${check_statuses[$i]}"),"
      echo "      \"detail\": $(json_string "${check_details[$i]}")"
    done
    echo "    }"
    echo "  ]"
    echo "}"
  } > "$report_json"

  {
    echo "# Release Replay Report"
    echo
    echo "- Generated: $generated_at"
    echo "- Status: $status"
    echo "- Version: $version"
    echo "- Tag: $tag"
    echo "- Commit: $commit"
    echo "- Artifact: $artifact_name"
    echo "- Expected SHA-256: $artifact_sha"
    echo "- Actual SHA-256: $actual_sha"
    [[ -n "$release_url" ]] && echo "- Release: $release_url"
    [[ -n "$ci_run_url" ]] && echo "- CI run: $ci_run_url"
    echo
    echo "## Checks"
    echo
    echo "| Check | Status | Detail |"
    echo "| --- | --- | --- |"
    for i in "${!check_names[@]}"; do
      echo "| $(md_cell "${check_names[$i]}") | ${check_statuses[$i]} | $(md_cell "${check_details[$i]}") |"
    done
  } > "$report_md"

  echo "wrote: $report_json"
  echo "wrote: $report_md"
  echo "status: $status"

  [[ "$status" == "pass" ]] || exit 1
}

subcommand="${1:-}"
[[ "$subcommand" == "verify" ]] || fail "release-replay requires subcommand: verify"
shift || true
cmd_verify "$@"
