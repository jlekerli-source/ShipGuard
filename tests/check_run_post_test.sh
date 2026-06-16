#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer check-run post --help >/dev/null

./bin/codex-maintainer ci-gate \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --policy templates/policy/default.conf \
  --out "$tmp_dir/gate" \
  --mode warn >/dev/null

./bin/codex-maintainer check-run \
  --gate "$tmp_dir/gate/gate.json" \
  --head-sha 0123456789abcdef \
  --out "$tmp_dir/payload.json" >/dev/null

GITHUB_TOKEN="secret-value-that-must-not-be-written" \
  ./bin/codex-maintainer check-run post \
    --payload "$tmp_dir/payload.json" \
    --repo owner/repo \
    --out "$tmp_dir/dry-run.json" \
    --dry-run >/dev/null

perl -MJSON::PP -0e '
  my $response = decode_json(<>);
  die "expected dry run" unless $response->{dry_run};
  die "bad method" unless $response->{method} eq "POST";
  die "bad url" unless $response->{url} eq "https://api.github.com/repos/owner/repo/check-runs";
  die "bad payload path" unless $response->{payload_file} =~ /payload\.json$/;
  die "missing payload digest" unless $response->{payload_sha256} =~ /^[a-f0-9]{64}$/;
  die "expected token marker" unless $response->{token_present};
  die "must not write token" if index(join("\n", @{ $response->{headers} || [] }), "secret-value") >= 0;
' "$tmp_dir/dry-run.json"

env -u GITHUB_TOKEN ./bin/codex-maintainer check-run post \
  --payload "$tmp_dir/payload.json" \
  --repo owner/repo \
  --api-url "https://example.test/api/" \
  --out "$tmp_dir/custom-api.json" \
  --dry-run >/dev/null

grep -q '"url" : "https://example.test/api/repos/owner/repo/check-runs"' "$tmp_dir/custom-api.json"
grep -q '"token_present" : false' "$tmp_dir/custom-api.json"

if ./bin/codex-maintainer check-run post \
  --payload "$tmp_dir/payload.json" \
  --repo bad \
  --out "$tmp_dir/bad-repo.json" \
  --dry-run >/dev/null 2>&1; then
  echo "expected invalid repo to fail" >&2
  exit 1
fi

if ./bin/codex-maintainer check-run post \
  --payload "$tmp_dir/missing.json" \
  --repo owner/repo \
  --out "$tmp_dir/missing.json" \
  --dry-run >/dev/null 2>&1; then
  echo "expected missing payload to fail" >&2
  exit 1
fi

if env -u GITHUB_TOKEN ./bin/codex-maintainer check-run post \
  --payload "$tmp_dir/payload.json" \
  --repo owner/repo \
  --out "$tmp_dir/no-token.json" >/dev/null 2>&1; then
  echo "expected real post without token to fail" >&2
  exit 1
fi

grep -q 'post-check-run' actions/ci-gate/action.yml
grep -q 'check-run post' actions/ci-gate/action.yml
grep -q 'checks: write' actions/ci-gate/action.yml
grep -q 'check-run/response.json' actions/ci-gate/action.yml

echo "check run post tests passed"
