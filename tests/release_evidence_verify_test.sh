#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-evidence verify --help >/dev/null
./bin/codex-maintainer release-evidence negative-index --help >/dev/null

version="$(sed -n '1p' VERSION)"
bundle="$tmp_dir/release-proof-bundle"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-proof build \
    --out "$bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "5555555555555555555555555555555555555555" \
    --ci-run-url "https://github.com/example/repo/actions/runs/555" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/5" \
    --notes "release evidence verify test" >/dev/null

assets="$tmp_dir/assets"
mkdir -p "$assets"
cp "$bundle/codex-maintainer-v$version.tar.gz" "$assets/"
cp "$bundle/proof/release-manifest.json" "$assets/"
cp "$bundle/proof/proof-ledger.md" "$assets/"
cp "$bundle/index/release-index.json" "$assets/"
cp "$bundle/index/release-index.md" "$assets/"
cp "$bundle/replay/replay-report.json" "$assets/"
cp "$bundle/replay/replay-report.md" "$assets/"
cp "$bundle/attestation/attestation.json" "$assets/"
cp "$bundle/attestation/attestation.md" "$assets/"
cp "$bundle/attestation/attestation-badge.json" "$assets/"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence bundle \
    --assets "$assets" \
    --left "$bundle" \
    --out "$tmp_dir/evidence-bundle" \
    --version "$version" \
    --title "Release Evidence Verify Test" \
    --index-title "Release Evidence Verify History" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence verify \
    --dir "$tmp_dir/evidence-bundle" \
    --out "$tmp_dir/evidence-verify" \
    --require-diff true \
    --require-index true >/dev/null

test -f "$tmp_dir/evidence-verify/evidence-verify.json"
test -f "$tmp_dir/evidence-verify/evidence-verify.md"
test -f "$tmp_dir/evidence-verify/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"bundle_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"diff_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"index_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"site_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q "\"version\" : \"$version\"" "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/evidence-verify/badge.json"
grep -q '| release diff status | pass | status must be pass |' "$tmp_dir/evidence-verify/evidence-verify.md"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence verify \
    --dir "$tmp_dir/evidence-bundle/site" \
    --out "$tmp_dir/site-verify" \
    --require-index false >/dev/null

grep -q '"bundle_present" : false' "$tmp_dir/site-verify/evidence-verify.json"
grep -q '"site_present" : true' "$tmp_dir/site-verify/evidence-verify.json"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence bundle \
    --assets "$assets" \
    --out "$tmp_dir/evidence-bundle-no-diff" \
    --version "$version" >/dev/null

if ./bin/codex-maintainer release-evidence verify \
  --dir "$tmp_dir/evidence-bundle-no-diff" \
  --out "$tmp_dir/should-fail-diff" \
  --require-diff true >/dev/null 2>&1; then
  echo "expected require-diff true to fail when release diff is absent" >&2
  exit 1
fi

cp -R "$tmp_dir/evidence-bundle" "$tmp_dir/tampered-evidence"
perl -0pi -e 's/"status" : "pass"/"status" : "blocked"/' "$tmp_dir/tampered-evidence/site/evidence.json"
if ./bin/codex-maintainer release-evidence verify \
  --dir "$tmp_dir/tampered-evidence" \
  --out "$tmp_dir/should-fail-tampered" >/dev/null 2>&1; then
  echo "expected tampered evidence status to fail" >&2
  exit 1
fi

expect_negative_fixture() {
  local name="$1"
  local expected_check="$2"
  local fixture="fixtures/release-evidence/negative/$name"
  local out="$tmp_dir/negative-$name"

  if CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
    ./bin/codex-maintainer release-evidence verify \
      --dir "$fixture" \
      --out "$out" >/dev/null 2>&1; then
    echo "expected negative fixture to fail: $name" >&2
    exit 1
  fi

  test -f "$out/evidence-verify.json"
  test -f "$out/evidence-verify.md"
  test -f "$out/badge.json"
  grep -q '"status" : "blocked"' "$out/evidence-verify.json"
  grep -q '"failed" : ' "$out/evidence-verify.json"
  grep -q "| $expected_check | fail |" "$out/evidence-verify.md"
  grep -q '"message" : "blocked"' "$out/badge.json"
}

expect_negative_fixture "missing-source" "asset digests source present"
expect_negative_fixture "consumer-mismatch" "consumer release matches evidence"
expect_negative_fixture "digest-summary-mismatch" "asset digest summary matches"
expect_negative_fixture "bundle-missing-output" "bundle evidence index output"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence negative-index \
    --fixture fixtures/release-evidence/negative \
    --out "$tmp_dir/negative-index" \
    --title "Release Evidence Negative Fixture Index" >/dev/null

test -f "$tmp_dir/negative-index/negative-fixture-index.json"
test -f "$tmp_dir/negative-index/negative-fixture-index.md"
test -f "$tmp_dir/negative-index/index.html"
test -f "$tmp_dir/negative-index/badge.json"
test -f "$tmp_dir/negative-index/runs/missing-source/evidence-verify.json"
grep -q '"status" : "pass"' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"case_count" : 4' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"expected_blocked_count" : 4' "$tmp_dir/negative-index/negative-fixture-index.json"
grep -q '"message" : "pass 4/4"' "$tmp_dir/negative-index/badge.json"
grep -q 'Release Evidence Negative Fixture Index' "$tmp_dir/negative-index/index.html"
grep -q 'Machine-readable index' "$tmp_dir/negative-index/index.html"
grep -q '| missing-source | pass | asset digests source present |' "$tmp_dir/negative-index/negative-fixture-index.md"
grep -q '| consumer-mismatch | pass | consumer release matches evidence |' "$tmp_dir/negative-index/negative-fixture-index.md"
grep -q '| digest-summary-mismatch | pass | asset digest summary matches |' "$tmp_dir/negative-index/negative-fixture-index.md"
grep -q '| bundle-missing-output | pass | bundle evidence index output |' "$tmp_dir/negative-index/negative-fixture-index.md"

echo "release evidence verify tests passed"
