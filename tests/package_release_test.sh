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
grep -q "^$package_name/actions/release-consume/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-diff/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence-negative-index/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-evidence-verify/action.yml$" "$tar_list"
grep -q "^$package_name/actions/release-proof/action.yml$" "$tar_list"
grep -q "^$package_name/actions/review-comment/action.yml$" "$tar_list"
grep -q "^$package_name/actions/validate/action.yml$" "$tar_list"
grep -q "^$package_name/docs/arena.md$" "$tar_list"
grep -q "^$package_name/docs/autopsy-github-actions.md$" "$tar_list"
grep -q "^$package_name/docs/benchmark.md$" "$tar_list"
grep -q "^$package_name/docs/check-run.md$" "$tar_list"
grep -q "^$package_name/docs/ci-gate.md$" "$tar_list"
grep -q "^$package_name/docs/ci-summary.md$" "$tar_list"
grep -q "^$package_name/docs/command-matrix.md$" "$tar_list"
grep -q "^$package_name/docs/demo-reports.md$" "$tar_list"
grep -q "^$package_name/docs/maintainer-reliability-os.md$" "$tar_list"
grep -q "^$package_name/docs/next-goal.md$" "$tar_list"
grep -q "^$package_name/docs/policy.md$" "$tar_list"
grep -q "^$package_name/docs/pr-review-bot.md$" "$tar_list"
grep -q "^$package_name/docs/release-checklist.md$" "$tar_list"
grep -q "^$package_name/docs/release-attest.md$" "$tar_list"
grep -q "^$package_name/docs/release-consume-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-consume.md$" "$tar_list"
grep -q "^$package_name/docs/release-diff-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-diff.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-bundle.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-index.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-negative-index-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-site.md$" "$tar_list"
grep -q "^$package_name/docs/release-evidence-verify.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-consumption.md$" "$tar_list"
grep -q "^$package_name/docs/release-index.md$" "$tar_list"
grep -q "^$package_name/docs/release-manifest.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-action.md$" "$tar_list"
grep -q "^$package_name/docs/release-proof-workflows.md$" "$tar_list"
grep -q "^$package_name/docs/release-replay.md$" "$tar_list"
grep -q "^$package_name/docs/sarif.md$" "$tar_list"
grep -q "^$package_name/docs/template-profiles.md$" "$tar_list"
grep -q "^$package_name/scripts/install.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_import.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_sign.sh$" "$tar_list"
grep -q "^$package_name/scripts/arena_verify.sh$" "$tar_list"
grep -q "^$package_name/scripts/autopsy_report.sh$" "$tar_list"
grep -q "^$package_name/scripts/build_demo_reports.sh$" "$tar_list"
grep -q "^$package_name/scripts/check_run.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_gate.sh$" "$tar_list"
grep -q "^$package_name/scripts/ci_summary.sh$" "$tar_list"
grep -q "^$package_name/scripts/leaderboard_build.sh$" "$tar_list"
grep -q "^$package_name/scripts/next_goal.sh$" "$tar_list"
grep -q "^$package_name/scripts/policy.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_attest.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_consume.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_proof.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_index.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_manifest.sh$" "$tar_list"
grep -q "^$package_name/scripts/release_replay.sh$" "$tar_list"
grep -q "^$package_name/scripts/review_comment.sh$" "$tar_list"
grep -q "^$package_name/scripts/sarif.sh$" "$tar_list"
grep -q "^$package_name/scripts/self_audit.sh$" "$tar_list"
grep -q "^$package_name/tests/package_release_test.sh$" "$tar_list"
grep -q "^$package_name/tests/action_artifact_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_import_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_sign_test.sh$" "$tar_list"
grep -q "^$package_name/tests/arena_test.sh$" "$tar_list"
grep -q "^$package_name/tests/autopsy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/check_run_post_test.sh$" "$tar_list"
grep -q "^$package_name/tests/check_run_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ci_gate_test.sh$" "$tar_list"
grep -q "^$package_name/tests/ci_summary_test.sh$" "$tar_list"
grep -q "^$package_name/tests/leaderboard_test.sh$" "$tar_list"
grep -q "^$package_name/tests/next_goal_test.sh$" "$tar_list"
grep -q "^$package_name/tests/policy_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_attest_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_consume_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_consume_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_diff_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_diff_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_negative_index_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_verify_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_evidence_verify_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_index_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_manifest_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_action_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_consumption_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_proof_workflow_test.sh$" "$tar_list"
grep -q "^$package_name/tests/release_replay_test.sh$" "$tar_list"
grep -q "^$package_name/tests/review_comment_test.sh$" "$tar_list"
grep -q "^$package_name/tests/sarif_test.sh$" "$tar_list"
grep -q "^$package_name/tests/self_audit_test.sh$" "$tar_list"
grep -q "^$package_name/tests/template_profiles_test.sh$" "$tar_list"
grep -q "^$package_name/templates/backend/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/backend/README.md$" "$tar_list"
grep -q "^$package_name/templates/cli/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/cli/README.md$" "$tar_list"
grep -q "^$package_name/templates/ios/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/web/AGENTS.md$" "$tar_list"
grep -q "^$package_name/templates/web/README.md$" "$tar_list"
grep -q "^$package_name/templates/policy/default.conf$" "$tar_list"
grep -q "^$package_name/fixtures/policy/strict.conf$" "$tar_list"
grep -q "^$package_name/fixtures/arena/good-maintainer/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/backend-webhook-idempotency/tests.log$" "$tar_list"
grep -q "^$package_name/fixtures/arena/cli-dangerous-clean/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/failing-validation/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/no-diff-implementation/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/arena/review-only/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/external-arena-pack/imported-clean/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/external-arena-pack/imported-risky/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/autopsy/good-run/run.md$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/README.md$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/cases.tsv$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/missing-source/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/consumer-mismatch/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/digest-summary-mismatch/site/evidence.json$" "$tar_list"
grep -q "^$package_name/fixtures/release-evidence/negative/bundle-missing-output/bundle.json$" "$tar_list"
grep -q "^$package_name/examples/demo-reports/leaderboard.json$" "$tar_list"
grep -q "^$package_name/examples/release-proof-consumption-checklist.md$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-consume-verify.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-diff-compare.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-bundle.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-consume.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-export.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-evidence-negative-index.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-proof-on-tag.yml$" "$tar_list"
grep -q "^$package_name/examples/workflows/release-proof-manual.yml$" "$tar_list"
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
"$package_root/bin/codex-maintainer" init web "$tmp_dir/web-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor web "$tmp_dir/web-target" >/dev/null
grep -q 'Web Codex Maintainer Instructions' "$tmp_dir/web-target/AGENTS.md"
"$package_root/bin/codex-maintainer" init backend "$tmp_dir/backend-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor backend "$tmp_dir/backend-target" >/dev/null
grep -q 'Backend Service Codex Maintainer Instructions' "$tmp_dir/backend-target/AGENTS.md"
"$package_root/bin/codex-maintainer" init cli "$tmp_dir/cli-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor cli "$tmp_dir/cli-target" >/dev/null
grep -q 'CLI Tool Codex Maintainer Instructions' "$tmp_dir/cli-target/AGENTS.md"
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
grep -q '"average_total": 6.25' "$tmp_dir/package-arena/results.json"
grep -q '"high_risk_finding_count": 8' "$tmp_dir/package-arena/results.json"
"$package_root/bin/codex-maintainer" arena import \
  --source "$package_root/fixtures/external-arena-pack" \
  --out "$tmp_dir/package-imported-arena" \
  --pack-name "package-imported" >/dev/null
grep -q 'Pack: package-imported' "$tmp_dir/package-imported-arena/PACK.md"
"$package_root/bin/codex-maintainer" arena run \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-results" >/dev/null
grep -q '"case_count": 2' "$tmp_dir/package-imported-results/results.json"
"$package_root/bin/codex-maintainer" arena sign \
  --fixture "$tmp_dir/package-imported-arena" \
  --out "$tmp_dir/package-imported-arena/PACK.json" \
  --pack-name "package-imported" >/dev/null
grep -q '"signature_type" : "sha256-content-digest"' "$tmp_dir/package-imported-arena/PACK.json"
"$package_root/bin/codex-maintainer" arena verify \
  --fixture "$tmp_dir/package-imported-arena" \
  --manifest "$tmp_dir/package-imported-arena/PACK.json" >/dev/null
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
grep -q '"sarif": "sarif/results.sarif"' "$tmp_dir/package-gate/gate.json"
grep -q '"summary": "summary.md"' "$tmp_dir/package-gate/gate.json"
grep -q '"version" : "2.1.0"' "$tmp_dir/package-gate/sarif/results.sarif"
grep -q '| Status | pass |' "$tmp_dir/package-gate/summary.md"
"$package_root/bin/codex-maintainer" ci-summary \
  --gate "$tmp_dir/package-gate/gate.json" \
  --out "$tmp_dir/package-summary.md" >/dev/null
grep -q '| Score | 11/12 |' "$tmp_dir/package-summary.md"
"$package_root/bin/codex-maintainer" check-run \
  --gate "$tmp_dir/package-gate/gate.json" \
  --head-sha 0123456789abcdef \
  --out "$tmp_dir/package-check-run/payload.json" >/dev/null
grep -q '"conclusion" : "success"' "$tmp_dir/package-check-run/payload.json"
grep -q '"head_sha" : "0123456789abcdef"' "$tmp_dir/package-check-run/payload.json"
"$package_root/bin/codex-maintainer" check-run post \
  --payload "$tmp_dir/package-check-run/payload.json" \
  --repo owner/repo \
  --out "$tmp_dir/package-check-run/dry-run.json" \
  --dry-run >/dev/null
grep -q '"dry_run" : true' "$tmp_dir/package-check-run/dry-run.json"
grep -q '"url" : "https://api.github.com/repos/owner/repo/check-runs"' "$tmp_dir/package-check-run/dry-run.json"
"$package_root/bin/codex-maintainer" leaderboard build \
  --arena-results "$tmp_dir/package-arena/results.json" \
  --out "$tmp_dir/package-leaderboard.json" >/dev/null
grep -q '"schema_version": "1.0"' "$tmp_dir/package-leaderboard.json"
grep -q '"average_total": 6.25' "$tmp_dir/package-leaderboard.json"
"$package_root/bin/codex-maintainer" release-manifest \
  --tarball "$tarball" \
  --out "$tmp_dir/package-release-proof" \
  --version "$version" \
  --tag "v$version" \
  --commit 0123456789abcdef \
  --ci-run-url "https://github.com/example/repo/actions/runs/123" \
  --release-url "https://github.com/example/repo/releases/tag/v$version" \
  --issue-url "https://github.com/example/repo/issues/99" >/dev/null
grep -q '"schema_version" : "1.0"' "$tmp_dir/package-release-proof/release-manifest.json"
grep -q "\"tag\" : \"v$version\"" "$tmp_dir/package-release-proof/release-manifest.json"
grep -q 'Artifact SHA-256:' "$tmp_dir/package-release-proof/proof-ledger.md"
"$package_root/bin/codex-maintainer" release-manifest verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --version "$version" \
  --tag "v$version" >/dev/null
"$package_root/bin/codex-maintainer" release-index build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --out "$tmp_dir/package-release-index" >/dev/null
grep -q '"release_count" : 1' "$tmp_dir/package-release-index/release-index.json"
grep -q '| '"$version"' | v'"$version"' | 0123456789ab | codex-maintainer-v'"$version"'.tar.gz |' "$tmp_dir/package-release-index/release-index.md"
"$package_root/bin/codex-maintainer" release-replay verify \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --tarball "$tarball" \
  --index "$tmp_dir/package-release-index/release-index.json" \
  --ledger "$tmp_dir/package-release-proof/proof-ledger.md" \
  --out "$tmp_dir/package-release-replay" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '"name": "artifact sha256"' "$tmp_dir/package-release-replay/replay-report.json"
grep -q '# Release Replay Report' "$tmp_dir/package-release-replay/replay-report.md"
"$package_root/bin/codex-maintainer" release-attest build \
  --manifest "$tmp_dir/package-release-proof/release-manifest.json" \
  --replay "$tmp_dir/package-release-replay/replay-report.json" \
  --out "$tmp_dir/package-release-attestation" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-attestation/attestation-badge.json"
grep -q '# Codex Maintainer Release Attestation' "$tmp_dir/package-release-attestation/attestation.md"
"$package_root/bin/codex-maintainer" release-proof build \
  --out "$tmp_dir/package-release-proof-bundle" \
  --version "$version" \
  --tag "v$version" \
  --commit 0123456789abcdef \
  --ci-run-url "https://github.com/example/repo/actions/runs/123" \
  --release-url "https://github.com/example/repo/releases/tag/v$version" \
  --issue-url "https://github.com/example/repo/issues/99" >/dev/null
test -f "$tmp_dir/package-release-proof-bundle/codex-maintainer-v$version.tar.gz"
grep -q '"status": "pass"' "$tmp_dir/package-release-proof-bundle/replay/replay-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-proof-bundle/attestation/attestation.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json"
mkdir -p "$tmp_dir/package-release-consume-assets"
cp "$tmp_dir/package-release-proof-bundle/codex-maintainer-v$version.tar.gz" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/release-manifest.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/index/release-index.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/proof/proof-ledger.md" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/replay/replay-report.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation.json" "$tmp_dir/package-release-consume-assets/"
cp "$tmp_dir/package-release-proof-bundle/attestation/attestation-badge.json" "$tmp_dir/package-release-consume-assets/"
"$package_root/bin/codex-maintainer" release-consume verify \
  --dir "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-consume" \
  --version "$version" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_blocked": 0' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"replay_report": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"attestation_badge": "pass"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q '"asset_digest_matrix": "asset-digests.json"' "$tmp_dir/package-release-consume/consumer-report.json"
grep -q "| codex-maintainer-v$version.tar.gz | release tarball | true | present |" "$tmp_dir/package-release-consume/asset-digests.md"
grep -q '"name": "attestation-badge.json"' "$tmp_dir/package-release-consume/asset-digests.json"
"$package_root/bin/codex-maintainer" release-diff compare \
  --left "$tmp_dir/package-release-proof-bundle" \
  --right "$tmp_dir/package-release-consume-assets" \
  --out "$tmp_dir/package-release-diff" >/dev/null
grep -q '"status" : "pass"' "$tmp_dir/package-release-diff/release-diff.json"
grep -q '# Release Diff Audit' "$tmp_dir/package-release-diff/release-diff.md"
"$package_root/bin/codex-maintainer" release-evidence site \
  --consume "$tmp_dir/package-release-consume" \
  --diff "$tmp_dir/package-release-diff" \
  --out "$tmp_dir/package-release-site" >/dev/null
test -f "$tmp_dir/package-release-site/index.html"
test -f "$tmp_dir/package-release-site/evidence.json"
test -f "$tmp_dir/package-release-site/sources/consumer-report.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-site/evidence.json"
grep -q 'Asset Digest Matrix' "$tmp_dir/package-release-site/index.html"
"$package_root/bin/codex-maintainer" release-evidence index \
  --site "$tmp_dir/package-release-site" \
  --out "$tmp_dir/package-release-evidence-index" >/dev/null
test -f "$tmp_dir/package-release-evidence-index/index.html"
test -f "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-index/evidence-index.json"
grep -q 'Machine-readable index' "$tmp_dir/package-release-evidence-index/index.html"
"$package_root/bin/codex-maintainer" release-evidence bundle \
  --assets "$tmp_dir/package-release-consume-assets" \
  --left "$tmp_dir/package-release-proof-bundle" \
  --out "$tmp_dir/package-release-evidence-bundle" \
  --version "$version" >/dev/null
test -f "$tmp_dir/package-release-evidence-bundle/bundle.json"
test -f "$tmp_dir/package-release-evidence-bundle/consumer-proof/consumer-report.json"
test -f "$tmp_dir/package-release-evidence-bundle/release-diff/release-diff.json"
test -f "$tmp_dir/package-release-evidence-bundle/site/index.html"
test -f "$tmp_dir/package-release-evidence-bundle/index/evidence-index.json"
grep -q '"status": "pass"' "$tmp_dir/package-release-evidence-bundle/bundle.json"
grep -q '"diff_included": true' "$tmp_dir/package-release-evidence-bundle/bundle.json"
"$package_root/bin/codex-maintainer" release-evidence verify \
  --dir "$tmp_dir/package-release-evidence-bundle" \
  --out "$tmp_dir/package-release-evidence-verify" \
  --require-diff true \
  --require-index true >/dev/null
test -f "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
test -f "$tmp_dir/package-release-evidence-verify/evidence-verify.md"
test -f "$tmp_dir/package-release-evidence-verify/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
grep -q '"bundle_present" : true' "$tmp_dir/package-release-evidence-verify/evidence-verify.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/package-release-evidence-verify/badge.json"
"$package_root/bin/codex-maintainer" release-evidence negative-index \
  --fixture "$package_root/fixtures/release-evidence/negative" \
  --out "$tmp_dir/package-release-evidence-negative-index" >/dev/null
test -f "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
test -f "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.md"
test -f "$tmp_dir/package-release-evidence-negative-index/index.html"
test -f "$tmp_dir/package-release-evidence-negative-index/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"case_count" : 4' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"expected_blocked_count" : 4' "$tmp_dir/package-release-evidence-negative-index/negative-fixture-index.json"
grep -q '"message" : "pass 4/4"' "$tmp_dir/package-release-evidence-negative-index/badge.json"
grep -q 'Machine-readable index' "$tmp_dir/package-release-evidence-negative-index/index.html"
test -f "$package_root/actions/release-diff/action.yml"
grep -q 'release-diff compare' "$package_root/actions/release-diff/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-diff/action.yml"
test -f "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence site' "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence index' "$package_root/actions/release-evidence/action.yml"
grep -q 'release-evidence bundle' "$package_root/actions/release-evidence/action.yml"
grep -q 'download-assets:' "$package_root/actions/release-evidence/action.yml"
grep -q 'gh release download "$release_tag"' "$package_root/actions/release-evidence/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence/action.yml"
test -f "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'release-evidence negative-index' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'fixture:' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'index-html=' "$package_root/actions/release-evidence-negative-index/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence-negative-index/action.yml"
test -f "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'release-evidence verify' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'require-diff:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'download-artifact:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'source-artifact-name:' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'actions/download-artifact@v4' "$package_root/actions/release-evidence-verify/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-evidence-verify/action.yml"
test -f "$package_root/actions/release-consume/action.yml"
grep -q 'release-consume verify' "$package_root/actions/release-consume/action.yml"
grep -q 'actions/upload-artifact@v4' "$package_root/actions/release-consume/action.yml"
"$package_root/tests/release_consume_action_test.sh" >/dev/null
"$package_root/tests/release_diff_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_test.sh" >/dev/null
"$package_root/tests/release_evidence_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_negative_index_action_test.sh" >/dev/null
"$package_root/tests/release_evidence_verify_test.sh" >/dev/null
"$package_root/tests/release_evidence_verify_action_test.sh" >/dev/null
"$package_root/tests/release_proof_consumption_test.sh" >/dev/null
"$package_root/bin/codex-maintainer" self-audit \
  --out "$tmp_dir/package-self-audit" >/dev/null
grep -q '"status": "pass"' "$tmp_dir/package-self-audit/self-audit.json"
grep -q '| codex-maintainer leaderboard build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-attest build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-proof build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-index build --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-manifest --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-manifest verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-replay verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-consume verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-diff compare --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence site --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence bundle --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence verify --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| codex-maintainer release-evidence negative-index --help | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-consume/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-diff/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-negative-index/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-evidence-verify/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| actions/release-proof/action.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-consume-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-consume.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-diff-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-diff.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-bundle.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-index.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-negative-index-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-site.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-evidence-verify.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-consumption.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-action.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| docs/release-proof-workflows.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-proof-on-tag.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-proof-manual.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-consume-verify.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-diff-compare.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-bundle.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-consume.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-export.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/workflows/release-evidence-negative-index.yml | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/release-evidence/negative/README.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| fixtures/release-evidence/negative/cases.tsv | pass |' "$tmp_dir/package-self-audit/self-audit.md"
grep -q '| examples/release-proof-consumption-checklist.md | pass |' "$tmp_dir/package-self-audit/self-audit.md"
"$package_root/bin/codex-maintainer" sarif \
  --report "$tmp_dir/package-autopsy/report.json" \
  --out "$tmp_dir/package-sarif/results.sarif" >/dev/null
grep -q '"version" : "2.1.0"' "$tmp_dir/package-sarif/results.sarif"
"$package_root/bin/codex-maintainer" next-goal \
  --release 2.6.0 \
  --title "Package Proof Followup" \
  --out "$tmp_dir/package-next-goal.md" >/dev/null
grep -q '/goal Implement v2.6.0 Package Proof Followup' "$tmp_dir/package-next-goal.md"
grep -q './tests/template_profiles_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_import_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/arena_sign_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/check_run_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/check_run_post_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/ci_summary_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/sarif_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_attest_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_index_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_manifest_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_consume_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_consume_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_diff_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_diff_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_verify_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_verify_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_evidence_negative_index_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_action_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_consumption_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_proof_workflow_test.sh' "$tmp_dir/package-next-goal.md"
grep -q './tests/release_replay_test.sh' "$tmp_dir/package-next-goal.md"

install_prefix="$tmp_dir/install"
PREFIX="$install_prefix" "$package_root/scripts/install.sh" >/dev/null
test "$("$install_prefix/bin/codex-maintainer" version)" = "$version"

echo "package release tests passed"
