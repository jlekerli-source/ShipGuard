#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer check-run --help >/dev/null

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/good-gate" \
  --mode warn >/dev/null

./bin/codex-maintainer check-run \
  --gate "$tmp_dir/good-gate/gate.json" \
  --head-sha 0123456789abcdef \
  --name "Codex Gate Test" \
  --out "$tmp_dir/good-payload.json" >/dev/null

perl -MJSON::PP -0e '
  my $payload = decode_json(<>);
  die "bad name" unless $payload->{name} eq "Codex Gate Test";
  die "bad sha" unless $payload->{head_sha} eq "0123456789abcdef";
  die "bad status" unless $payload->{status} eq "completed";
  die "expected success" unless $payload->{conclusion} eq "success";
  die "missing summary" unless $payload->{output}{summary} =~ /Score: 11\/12/;
' "$tmp_dir/good-payload.json"

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/dangerous-gate" \
  --mode warn >/dev/null

./bin/codex-maintainer check-run \
  --gate "$tmp_dir/dangerous-gate/gate.json" \
  --head-sha abcdef0123456789 \
  --out "$tmp_dir/dangerous-payload.json" >/dev/null

perl -MJSON::PP -0e '
  my $payload = decode_json(<>);
  die "expected failure" unless $payload->{conclusion} eq "failure";
  die "missing artifact text" unless $payload->{output}{text} =~ /check-run/ || $payload->{output}{text} =~ /summary.md/;
' "$tmp_dir/dangerous-payload.json"

if ./bin/codex-maintainer check-run --gate "$tmp_dir/missing.json" --head-sha abc --out "$tmp_dir/missing.json" >/dev/null 2>&1; then
  echo "expected missing gate to fail" >&2
  exit 1
fi

grep -q 'Generate check-run payload' actions/ci-gate/action.yml
grep -q 'check-run/payload.json' actions/ci-gate/action.yml

echo "check run tests passed"
