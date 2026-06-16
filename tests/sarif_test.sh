#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer sarif --help >/dev/null

./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out "$tmp_dir/dangerous-autopsy" >/dev/null

./bin/codex-maintainer sarif \
  --report "$tmp_dir/dangerous-autopsy/report.json" \
  --out "$tmp_dir/dangerous.sarif" >/dev/null

perl -MJSON::PP -0e '
  my $sarif = decode_json(<>);
  die "bad sarif version" unless $sarif->{version} eq "2.1.0";
  my $run = $sarif->{runs}[0];
  die "bad tool" unless $run->{tool}{driver}{name} eq "codex-maintainer";
  die "expected five findings" unless @{$run->{results}} == 5;
  my %rules = map { $_->{id} => 1 } @{$run->{tool}{driver}{rules}};
  die "missing validation rule" unless $rules{validation_claim_without_tests};
  my %levels = map { $_->{ruleId} => $_->{level} } @{$run->{results}};
  die "high finding should be error" unless $levels{validation_claim_without_tests} eq "error";
  die "medium finding should be warning" unless $levels{no_test_log} eq "warning";
  die "wrong score" unless $run->{properties}{score} == 1;
' "$tmp_dir/dangerous.sarif"

./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out "$tmp_dir/good-autopsy" >/dev/null

./bin/codex-maintainer sarif \
  --report "$tmp_dir/good-autopsy/report.json" \
  --out "$tmp_dir/good.sarif" >/dev/null

perl -MJSON::PP -0e '
  my $sarif = decode_json(<>);
  die "expected zero findings" unless @{$sarif->{runs}[0]{results}} == 0;
' "$tmp_dir/good.sarif"

if ./bin/codex-maintainer sarif --report "$tmp_dir/missing.json" --out "$tmp_dir/missing.sarif" >/dev/null 2>&1; then
  echo "expected missing report to fail" >&2
  exit 1
fi

echo "sarif tests passed"
