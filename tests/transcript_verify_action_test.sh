#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

version="$(sed -n '1p' VERSION)"
action="actions/transcript-verify/action.yml"
workflow="examples/workflows/transcript-verify.yml"

test -f "$action"
test -f "$workflow"

grep -q 'name: Verify ShipGuard transcript' "$action"
grep -q 'transcript:' "$action"
grep -q 'report:' "$action"
grep -q 'transcript verify' "$action"
grep -q 'transcript-verify.json' "$action"
grep -q 'transcript-verify.md' "$action"
grep -q 'badge.json' "$action"
grep -q 'mode must be fail or warn' "$action"
grep -q 'status="failed"' "$action"
grep -q 'exit_code="$verify_exit"' "$action"
grep -q 'actions/upload-artifact@v4' "$action"
grep -q 'shipguard-transcript-verify' "$action"

grep -q "jlekerli-source/ShipGuard/actions/transcript-verify@v$version" "$workflow"
grep -q 'contents: read' "$workflow"
grep -q 'mode: fail' "$workflow"
grep -q 'artifact-name: shipguard-transcript-verify' "$workflow"

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |file| YAML.load_file(file) }' "$action" "$workflow"
fi

raw="$tmp_dir/raw-transcript.md"
redacted="$tmp_dir/redacted-transcript.md"
redaction_report="$tmp_dir/redaction-report.json"
verify_dir="$tmp_dir/verify"
home_prefix="/""home"
home_path="$home_prefix/alex/TranscriptActionApp"

cat > "$raw" <<'RAW'
# Raw Transcript

Maintainer: TranscriptActionApp lives at __HOME_PATH__.
Agent: I will redact maintainer@example.com and API_KEY=secret-value before publication.
RAW
HOME_PATH="$home_path" perl -pi -e 's#__HOME_PATH__#$ENV{HOME_PATH}#g' "$raw"

./bin/shipguard transcript redact \
  --in "$raw" \
  --out "$redacted" \
  --report "$redaction_report" \
  --private-term "TranscriptActionApp" >/dev/null

./bin/shipguard transcript verify \
  --in "$redacted" \
  --report "$redaction_report" \
  --out "$verify_dir" >/dev/null

grep -q '"status" : "pass"' "$verify_dir/transcript-verify.json"
grep -q '| redaction report | pass | redaction report is passing |' "$verify_dir/transcript-verify.md"
grep -q '"message" : "pass"' "$verify_dir/badge.json"

echo "transcript verify action tests passed"
