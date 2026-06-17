#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios redact --help >/dev/null

raw="$tmp_dir/raw-ios-report.md"
redacted="$tmp_dir/redacted-ios-report.md"
report="$tmp_dir/ios-redaction.json"
github_token="ghp_""abcdefghijklmnopqrstuvwxyz123456"
openai_key="sk-""abcdefghijklmnopqrstuvwxyz123456"
local_path="/""Users/omar/Developer/SecretClientApp/Demo.xcodeproj"

cat > "$raw" <<'RAW'
# iOS Report

Workspace: __LOCAL_PATH__
Developer Team: DEVELOPMENT_TEAM = ABCDE12345;
Bundle: PRODUCT_BUNDLE_IDENTIFIER = com.secret.client.app;
Auth: Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456
OpenAI: OPENAI_API_KEY=__OPENAI_KEY__
GitHub: __GITHUB_TOKEN__
Account: ios.owner@example.com
Apple ID: private.owner@example.com
Reviewer: build.reviewer@example.com
Device: UDID: 00008110-001C2D3E4F58001E
Project nickname: SecretClientApp
RAW

LOCAL_PATH="$local_path" GITHUB_TOKEN="$github_token" OPENAI_KEY="$openai_key" \
  perl -pi -e 's#__LOCAL_PATH__#$ENV{LOCAL_PATH}#g; s#__GITHUB_TOKEN__#$ENV{GITHUB_TOKEN}#g; s#__OPENAI_KEY__#$ENV{OPENAI_KEY}#g' "$raw"

./bin/shipguard ios redact \
  --in "$raw" \
  --out "$redacted" \
  --report "$report" \
  --private-term "SecretClientApp" >/dev/null

test -f "$redacted"
test -f "$report"
grep -q '\[REDACTED_LOCAL_PATH\]' "$redacted"
grep -q '\[REDACTED_TEAM_ID\]' "$redacted"
grep -q '\[REDACTED_BUNDLE_ID\]' "$redacted"
grep -q '\[REDACTED_TOKEN\]' "$redacted"
grep -q '\[REDACTED_EMAIL\]' "$redacted"
grep -q '\[REDACTED_ACCOUNT\]' "$redacted"
grep -q '\[REDACTED_DEVICE_ID\]' "$redacted"
grep -q '\[REDACTED_PRIVATE_TERM\]' "$redacted"
grep -q '"status": "pass"' "$report"
grep -q '"tool": "shipguard ios redact"' "$report"
grep -q '"filesProcessed": 1' "$report"
grep -q '"privateTermsChecked": 1' "$report"
grep -q '"remainingRiskCount": 0' "$report"

if grep -Eq 'SecretClientApp|ios.owner@example.com|private.owner@example.com|build.reviewer@example.com|ghp_|sk-|abcdefghijklmnopqrstuvwxyz123456|ABCDE12345|com\.secret\.client\.app|00008110-001C2D3E4F58001E' "$redacted" ||
  grep -Fq "$local_path" "$redacted" ||
  grep -Fq "$local_path" "$report"; then
  echo "redacted iOS report still contains sensitive source content" >&2
  exit 1
fi

input_dir="$tmp_dir/input-dir"
output_dir="$tmp_dir/output-dir"
derived_prefix="/""Users"
derived_path="$derived_prefix/omar/Library/Developer/Xcode/DerivedData/SecretClientApp"
mkdir -p "$input_dir/nested"
cat > "$input_dir/nested/session.json" <<'JSON'
{
  "bundleIdentifier": "com.secret.client.extension",
  "SHIPGUARD_DEVSPACE_TOKEN": "devspace-super-secret-value",
  "path": "__DERIVED_PATH__"
}
JSON
DERIVED_PATH="$derived_path" perl -pi -e 's#__DERIVED_PATH__#$ENV{DERIVED_PATH}#g' "$input_dir/nested/session.json"
printf 'binary-ish' > "$input_dir/nested/screenshot.png"

./bin/shipguard ios redact \
  --in "$input_dir" \
  --out "$output_dir" \
  --private-term "SecretClientApp" >/dev/null

test -f "$output_dir/nested/session.json"
test ! -f "$output_dir/nested/screenshot.png"
grep -q '\[REDACTED_BUNDLE_ID\]' "$output_dir/nested/session.json"
grep -q '\[REDACTED_TOKEN\]' "$output_dir/nested/session.json"
grep -q '\[REDACTED_LOCAL_PATH\]' "$output_dir/nested/session.json"
grep -q '"filesProcessed": 1' "$output_dir/ios-redaction.json"
grep -q '"filesSkipped": 1' "$output_dir/ios-redaction.json"
grep -q '"status": "pass"' "$output_dir/ios-redaction.json"

if grep -R -Eq 'com\.secret\.client|devspace-super-secret-value|SecretClientApp' "$output_dir" ||
  grep -R -Fq "$derived_prefix/omar" "$output_dir"; then
  echo "redacted iOS directory still contains sensitive source content" >&2
  exit 1
fi

echo "ios redaction tests passed"
