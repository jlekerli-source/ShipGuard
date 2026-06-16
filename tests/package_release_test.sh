#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

tarball="$(./scripts/package_release.sh)"
version="$(sed -n '1p' VERSION)"
package_name="codex-maintainer-v$version"
tar_list="$tmp_dir/tar-list.txt"

[[ -f "$tarball" ]] || {
  echo "missing package tarball: $tarball" >&2
  exit 1
}

tar -tzf "$tarball" > "$tar_list"
grep -q "^$package_name/bin/codex-maintainer$" "$tar_list"
grep -q "^$package_name/AGENTS.md$" "$tar_list"
grep -q "^$package_name/.github/workflows/autopsy-artifact.yml$" "$tar_list"
grep -q "^$package_name/actions/ci-gate/action.yml$" "$tar_list"
grep -q "^$package_name/actions/review-comment/action.yml$" "$tar_list"
grep -q "^$package_name/actions/validate/action.yml$" "$tar_list"
grep -q "^$package_name/docs/arena.md$" "$tar_list"
grep -q "^$package_name/docs/autopsy-github-actions.md$" "$tar_list"
grep -q "^$package_name/docs/benchmark.md$" "$tar_list"
grep -q "^$package_name/docs/ci-gate.md$" "$tar_list"
grep -q "^$package_name/docs/demo-reports.md$" "$tar_list"
grep -q "^$package_name/docs/policy.md$" "$tar_list"
grep -q "^$package_name/docs/pr-review-bot.md$" "$tar_list"
grep -q "^$package_name/scripts/install.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/autopsy_report.sh$" "$tar_list"
grep -q "^$package_name/scripts/build_demo_reports.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_gate.sh$" "$tar_list"
grep -q "^$package_name/scripts/leaderboard_build.sh$" "$tar_list"
grep -q "^$package_name/scripts/policy.sh$" "$tar_list"
grep -q "^$package_name/scripts/review_comment.sh$" "$tar_list"
grep -q "^$package_name/tests/package_release_test.sh$" "$tar_list"
grep -q "^$package_name/tests/action_artifact_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_test.sh$" "$tar_list"
grep -q "^$package_name/tests/autopsy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ci_gate_test.sh$" "$tar_list"
grep -q "^$package_name/tests/leaderboard_test.sh$" "$tar_list"
grep -q "^$package_name/tests/policy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/review_comment_test.sh$" "$tar_list"
grep -q "^$package_name/templates/ios/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/policy/default.conf$" "$tar_list"
grep -q "^$package_name/fixtures/policy/strict.conf$" "$tar_list"
grep -q "^$package_name/fixtures/arena/good-maintainer/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/autopsy/good-run/run.md$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/leaderboard.json$" "$tar_list"
grep -q "^$package_name/.agents/skills/alarm-testing/SKILL.md$" "$tar_list"

if grep -Eq '(^|/)(\\.git|dist|DerivedData|\\.cache)(/|$)' "$tar_list"; then
  echo "package includes forbidden generated or VCS paths" >&2
  exit 1
fi

tar -xzf "$tarball" -C "$tmp_dir"
package_root="$tmp_dir/$package_name"

local_path_pattern="/""Users/"
if grep -RIEq "$local_path_pattern|ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}" "$package_root"; then
  echo "package includes a local path or secret-looking token" >&2
  exit 1
fi

test "$("$package_root/bin/codex-maintainer" version)" = "$version"
"$package_root/bin/codex-maintainer" policy show >/dev/null
"$package_root/bin/codex-maintainer" validate "$package_root" >/dev/null
"$package_root/bin/codex-maintainer" init ios "$tmp_dir/demo-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor "$tmp_dir/demo-target" >/dev/null
"$package_root/bin/codex-maintainer" autopsy \
  --run "$package_root/fixtures/autopsy/good-run/run.md" \
  --task "$package_root/fixtures/autopsy/good-run/task.md" \
  --diff "$package_root/fixtures/autopsy/good-run/diff.patch" \
  --tests "$package_root/fixtures/autopsy/good-run/tests.log" \
  --out "$tmp_dir/package-autopsy" >/dev/null
grep -q '"total": 11' "$tmp_dir/package-autopsy/report.json"
grep -q '"verdict": "usable maintainer-quality run"' "$tmp_dir/package-autopsy/report.json"
"$package_root/bin/codex-maintainer" arena run \
  --fixture "$package_root/fixtures/arena" \
  --out "$tmp_dir/package-arena" >/dev/null
grep -q '"average_total": 5.00' "$tmp_dir/package-arena/results.json"
grep -q '"high_risk_finding_count": 4' "$tmp_dir/package-arena/results.json"
"$package_root/bin/codex-maintainer" review-comment \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-review/comment.md" \
  --badge "$tmp_dir/package-review/badge.json" \
  --artifact-dir "$tmp_dir/package-review" >/dev/null
grep -q '| Status | pass |' "$tmp_dir/package-review/comment.md"
grep -q '"message": "pass 11/12"' "$tmp_dir/package-review/badge.json"
"$package_root/bin/codex-maintainer" ci-gate \
  --run "$package_root/fixtures/autopsy/good-run/run.md" \
  --task "$package_root/fixtures/autopsy/good-run/task.md" \
  --diff "$package_root/fixtures/autopsy/good-run/diff.patch" \
  --tests "$package_root/fixtures/autopsy/good-run/tests.log" \
  --policy "$package_root/templates/policy/default.conf" \
  --out "$tmp_dir/package-gate" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-gate/gate.json"
"$package_root/bin/codex-maintainer" leaderboard build \
  --arena-results "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-leaderboard.json" >/dev/null
grep -q '"schema_version": "1.0"' "$tmp_dir/package-leaderboard.json"
grep -q '"average_total": 5.00' "$tmp_dir/package-leaderboard.json"

install_prefix="$tmp_dir/install"
PREFIX="$install_prefix" "$package_root/scripts/install.sh" >/dev/null
test "$("$install_prefix/bin/codex-maintainer" version)" = "$version"

echo "package release tests passed"
