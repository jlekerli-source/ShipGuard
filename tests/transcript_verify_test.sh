#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer transcript verify --help >/dev/null

raw="$tmp_dir/raw-transcript.md"
redacted="$tmp_dir/redacted-transcript.md"
redaction_report="$tmp_dir/redaction-report.json"
verify_dir="$tmp_dir/verify"
home_prefix="/""home"
home_path="$home_prefix/alex/PrivateMaintainerApp"

cat > "$raw" <<'RAW'
# Raw Transcript

Maintainer: PrivateMaintainerApp is stored at __HOME_PATH__.
Agent: I will redact maintainer@example.com and API_KEY=secret-value before sharing.
RAW
HOME_PATH="$home_path" perl -pi -e 's#__HOME_PATH__#$ENV{HOME_PATH}#g' "$raw"

./bin/codex-maintainer transcript redact \
  --in "$raw" \
  --out "$redacted" \
  --report "$redaction_report" \
  --private-term "PrivateMaintainerApp" >/dev/null

./bin/codex-maintainer transcript verify \
  --in "$redacted" \
  --report "$redaction_report" \
  --out "$verify_dir" >/dev/null

test -f "$verify_dir/transcript-verify.json"
test -f "$verify_dir/transcript-verify.md"
test -f "$verify_dir/badge.json"
grep -q '"status" : "pass"' "$verify_dir/transcript-verify.json"
grep -q '"remaining_risk_count" : 0' "$verify_dir/transcript-verify.json"
grep -q '"redaction_report_status" : "pass"' "$verify_dir/transcript-verify.json"
grep -q '| redaction report | pass | redaction report is passing |' "$verify_dir/transcript-verify.md"
grep -q '"message" : "pass"' "$verify_dir/badge.json"

unsafe="$tmp_dir/unsafe-redacted.md"
unsafe_out="$tmp_dir/unsafe-verify"
cat > "$unsafe" <<'RAW'
# Unsafe Transcript

Maintainer: This still includes maintainer@example.com and API_TOKEN=secret-value.
RAW

if ./bin/codex-maintainer transcript verify --in "$unsafe" --out "$unsafe_out" >/dev/null 2>&1; then
  echo "expected unsafe transcript verification to fail" >&2
  exit 1
fi

test -f "$unsafe_out/transcript-verify.json"
test -f "$unsafe_out/transcript-verify.md"
test -f "$unsafe_out/badge.json"
grep -q '"status" : "blocked"' "$unsafe_out/transcript-verify.json"
grep -q '| email | blocked | 1 risky match(es) |' "$unsafe_out/transcript-verify.md"
grep -q '| secret assignment | blocked | 1 risky match(es) |' "$unsafe_out/transcript-verify.md"
grep -q '"message" : "blocked"' "$unsafe_out/badge.json"

echo "transcript verify tests passed"
