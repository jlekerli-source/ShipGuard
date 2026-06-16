#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer transcript redact --help >/dev/null

raw="$tmp_dir/raw-transcript.md"
redacted="$tmp_dir/redacted-transcript.md"
report="$tmp_dir/redaction-report.json"
github_token="ghp_""abcdefghijklmnopqrstuvwxyz123456"
openai_key="sk-""abcdefghijklmnopqrstuvwxyz123456"
home_prefix="/""home"
home_path="$home_prefix/alex/Developer/AcmePrivateApp"

cat > "$raw" <<'RAW'
# Raw Maintainer Transcript

Maintainer: Please inspect AcmePrivateApp under __HOME_PATH__.
Agent: I will not publish alex@example.com or any credentials.
Maintainer: The temporary GitHub token was __GITHUB_TOKEN__.
Maintainer: The OpenAI value looked like __OPENAI_KEY__.
Maintainer: Staging used API_KEY=secret-value-123 and Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456.
Agent: I also saw a cache token 0123456789abcdef0123456789abcdef.
RAW
HOME_PATH="$home_path" GITHUB_TOKEN="$github_token" OPENAI_KEY="$openai_key" \
  perl -pi -e 's#__HOME_PATH__#$ENV{HOME_PATH}#g; s#__GITHUB_TOKEN__#$ENV{GITHUB_TOKEN}#g; s#__OPENAI_KEY__#$ENV{OPENAI_KEY}#g' "$raw"

./bin/codex-maintainer transcript redact \
  --in "$raw" \
  --out "$redacted" \
  --report "$report" \
  --private-term "AcmePrivateApp" >/dev/null

test -f "$redacted"
test -f "$report"
grep -q '\[redacted-private-term\]' "$redacted"
grep -q "$home_prefix/\\[redacted-user\\]" "$redacted"
grep -q '\[redacted-email\]' "$redacted"
grep -q '\[redacted-secret\]' "$redacted"
grep -q '\[redacted-token\]' "$redacted"
grep -q '"status" : "pass"' "$report"
grep -q '"private_terms_checked" : 1' "$report"
grep -q '"remaining_risk_count" : 0' "$report"
grep -q '"total_replacements" : 9' "$report"
grep -q '"id" : "private_term"' "$report"
grep -q '"replacements" : 2' "$report"

if grep -Eq 'AcmePrivateApp|alex@example.com|ghp_|sk-|0123456789abcdef0123456789abcdef|Bearer abcdefghijklmnopqrstuvwxyz123456|API_KEY=secret-value-123' "$redacted" ||
  grep -Fq "$home_path" "$redacted"; then
  echo "redacted transcript still contains sensitive source content" >&2
  exit 1
fi

echo "transcript redaction tests passed"
