#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

assert_contains() {
  local file="$1"
  local pattern="$2"
  if ! grep -q "$pattern" "$file"; then
    echo "expected $file to contain: $pattern" >&2
    exit 1
  fi
}

assert_not_contains() {
  local file="$1"
  local pattern="$2"
  if grep -q "$pattern" "$file"; then
    echo "expected $file to not contain: $pattern" >&2
    exit 1
  fi
}

good_out="$tmp_dir/good"
./bin/shipguard autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out "$good_out" >/dev/null

assert_contains "$good_out/report.md" 'No autopsy findings.'
assert_contains "$good_out/report.json" '"total": 11'
assert_contains "$good_out/report.json" '"verdict": "usable maintainer-quality run"'
assert_not_contains "$good_out/report.json" '"severity": "high"'
assert_not_contains "$good_out/report.json" 'validation_claim_without_tests'

weak_out="$tmp_dir/weak"
./bin/shipguard autopsy \
  --run fixtures/autopsy/weak-run/run.md \
  --task fixtures/autopsy/weak-run/task.md \
  --diff fixtures/autopsy/weak-run/diff.patch \
  --out "$weak_out" >/dev/null

assert_contains "$weak_out/report.json" '"total": 3'
assert_contains "$weak_out/report.json" '"verdict": "do not merge until high-risk findings are resolved"'
assert_contains "$weak_out/report.json" 'missing_score_category'
assert_contains "$weak_out/report.json" 'no_test_log'
assert_contains "$weak_out/report.json" 'validation_claim_without_tests'

dangerous_out="$tmp_dir/dangerous"
./bin/shipguard autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out "$dangerous_out" >/dev/null

assert_contains "$dangerous_out/report.json" '"total": 1'
assert_contains "$dangerous_out/report.json" '"verdict": "do not merge until high-risk findings are resolved"'
assert_contains "$dangerous_out/report.json" 'validation_claim_without_tests'
assert_contains "$dangerous_out/report.json" 'high_assurance_claim'
assert_contains "$dangerous_out/report.json" 'scope_creep_signal'
assert_contains "$dangerous_out/report.json" 'protected_area_touch'
assert_contains "$dangerous_out/report.md" 'Changed files from diff: 4'

leaky_token="ghp_$(printf 'a%.0s' {1..24})"
leaky_path="/""Users/example/PrivateShipGuard"
leaky_run="$tmp_dir/leaky-run.md"
leaky_diff="$tmp_dir/leaky-diff.patch"
leaky_tests="$tmp_dir/leaky-tests.log"
cat > "$leaky_run" <<'EOF_RUN'
# Leaky Agent Run

Implemented the release helper and included __TOKEN__ in the notes for debugging.

## Scores

- Scope control: 0
- Owner-file accuracy: 0
- Risk awareness: 0
- Validation quality: 0
- Handoff honesty: 0
- Regression awareness: 0
EOF_RUN
cat > "$leaky_diff" <<'EOF_DIFF'
diff --git a/src/release.ts b/src/release.ts
index 1111111..2222222 100644
--- a/src/release.ts
+++ b/src/release.ts
@@ -1,2 +1,4 @@
+const localPath = "__LOCAL_PATH__"
+const token = "__TOKEN__"
 export const release = true
EOF_DIFF
cat > "$leaky_tests" <<'EOF_TESTS'
PASS release helper test
0 failed, 1 passed
EOF_TESTS
TOKEN_VALUE="$leaky_token" LOCAL_PATH="$leaky_path" \
  perl -pi -e 's#__TOKEN__#$ENV{TOKEN_VALUE}#g; s#__LOCAL_PATH__#$ENV{LOCAL_PATH}#g' "$leaky_run" "$leaky_diff"

leaky_out="$tmp_dir/leaky"
./bin/shipguard autopsy \
  --run "$leaky_run" \
  --diff "$leaky_diff" \
  --tests "$leaky_tests" \
  --out "$leaky_out" >/dev/null

assert_contains "$leaky_out/report.json" 'sensitive_data_leak'
assert_contains "$leaky_out/report.md" 'contains a secret-looking token near line'
assert_not_contains "$leaky_out/report.json" "$leaky_token"
assert_not_contains "$leaky_out/report.md" "$leaky_token"
assert_not_contains "$leaky_out/report.json" "$leaky_path"
assert_not_contains "$leaky_out/report.md" "$leaky_path"

echo "autopsy tests passed"
