#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"
doc="docs/release-proof-consumption.md"
checklist="examples/release-proof-consumption-checklist.md"

test -f "$doc"
test -f "$checklist"

grep -q "gh release download v$version" "$doc"
grep -q -- "--repo jlekerli-source/ShipGuard" "$doc"
grep -q "shipguard-v$version.tar.gz" "$doc"
grep -q "release-manifest.json" "$doc"
grep -q "release-index.json" "$doc"
grep -q "proof-ledger.md" "$doc"
grep -q "replay-report.json" "$doc"
grep -q "attestation.json" "$doc"
grep -q "attestation-badge.json" "$doc"
grep -q "shasum -a 256" "$doc"
grep -q "release-replay verify" "$doc"
grep -q "release-attest build" "$doc"
grep -q "not a cryptographic signature" "$doc"

grep -q "gh release download v$version" "$checklist"
grep -q "release-replay verify" "$checklist"
grep -q "release-attest build" "$checklist"
grep -q "blocked checks are \`0\`" "$checklist"

SHIPGUARD_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/downloaded" \
    --version "$version" \
    --tag "v$version" \
    --commit 0123456789abcdef \
    --ci-run-url "https://github.com/jlekerli-source/ShipGuard/actions/runs/123" \
    --release-url "https://github.com/jlekerli-source/ShipGuard/releases/tag/v$version" \
    --issue-url "https://github.com/jlekerli-source/ShipGuard/issues/99" >/dev/null

shasum -a 256 "$tmp_dir/downloaded/shipguard-v$version.tar.gz" > "$tmp_dir/sha256.txt"
grep -q "$(perl -MJSON::PP -e 'open my $fh, "<", $ARGV[0] or die $!; local $/; print decode_json(<$fh>)->{artifact}->{sha256}' "$tmp_dir/downloaded/proof/release-manifest.json")" "$tmp_dir/sha256.txt"

./bin/shipguard release-replay verify \
  --manifest "$tmp_dir/downloaded/proof/release-manifest.json" \
  --tarball "$tmp_dir/downloaded/shipguard-v$version.tar.gz" \
  --index "$tmp_dir/downloaded/index/release-index.json" \
  --ledger "$tmp_dir/downloaded/proof/proof-ledger.md" \
  --out "$tmp_dir/consumer-replay" >/dev/null

./bin/shipguard release-attest build \
  --manifest "$tmp_dir/downloaded/proof/release-manifest.json" \
  --replay "$tmp_dir/consumer-replay/replay-report.json" \
  --out "$tmp_dir/consumer-attestation" >/dev/null

grep -q '"status": "pass"' "$tmp_dir/consumer-replay/replay-report.json"
grep -q '"blocked": 0' "$tmp_dir/consumer-replay/replay-report.json"
grep -q '"status" : "pass"' "$tmp_dir/consumer-attestation/attestation.json"
grep -q '"blocked" : 0' "$tmp_dir/consumer-attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/consumer-attestation/attestation-badge.json"

echo "release proof consumption tests passed"
