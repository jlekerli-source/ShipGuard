# Release Checklist

Use this checklist for every release after `v2.0.0`.

```bash
./bin/shipguard validate
./tests/cli_smoke_test.sh
./tests/template_profiles_test.sh
./tests/autopsy_test.sh
./tests/action_artifact_test.sh
./tests/arena_test.sh
./tests/arena_import_test.sh
./tests/arena_compare_test.sh
./tests/arena_compare_action_test.sh
./tests/arena_sign_test.sh
./tests/review_comment_test.sh
./tests/policy_test.sh
./tests/check_run_test.sh
./tests/check_run_post_test.sh
./tests/ci_gate_test.sh
./tests/ci_summary_test.sh
./tests/sarif_test.sh
./tests/leaderboard_test.sh
./tests/self_audit_test.sh
./tests/next_goal_test.sh
./tests/release_attest_test.sh
./tests/release_proof_test.sh
./tests/release_index_test.sh
./tests/release_manifest_test.sh
./tests/release_consume_test.sh
./tests/release_consume_action_test.sh
./tests/release_diff_test.sh
./tests/release_diff_action_test.sh
./tests/release_evidence_test.sh
./tests/release_evidence_action_test.sh
./tests/release_evidence_verify_test.sh
./tests/release_evidence_verify_action_test.sh
./tests/release_evidence_negative_index_action_test.sh
./tests/release_replay_test.sh
./tests/release_proof_action_test.sh
./tests/release_proof_consumption_test.sh
./tests/release_proof_workflow_test.sh
./tests/package_release_test.sh
```

`./tests/package_release_test.sh` prints coarse phase timings to stderr. If it is slow, use the latest phase line to distinguish package build, manifest/privacy checks, packaged CLI smoke proof, full-audit/value-gauntlet proof, v4 proof gates, or install proof instead of treating silence as a hang.

Then:

```bash
./scripts/package_release.sh
shasum -a 256 dist/shipguard-vX.Y.Z.tar.gz
./bin/shipguard release-manifest --tarball dist/shipguard-vX.Y.Z.tar.gz --out /tmp/shipguard-release-proof
./bin/shipguard release-manifest verify --manifest /tmp/shipguard-release-proof/release-manifest.json --tarball dist/shipguard-vX.Y.Z.tar.gz
./bin/shipguard release-index build --manifest /tmp/shipguard-release-proof/release-manifest.json --out /tmp/shipguard-release-index
./bin/shipguard release-replay verify --manifest /tmp/shipguard-release-proof/release-manifest.json --tarball dist/shipguard-vX.Y.Z.tar.gz --index /tmp/shipguard-release-index/release-index.json --ledger /tmp/shipguard-release-proof/proof-ledger.md --out /tmp/shipguard-release-replay
./bin/shipguard release-attest build --manifest /tmp/shipguard-release-proof/release-manifest.json --replay /tmp/shipguard-release-replay/replay-report.json --out /tmp/shipguard-release-attestation
./bin/shipguard release-proof build --out /tmp/shipguard-release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/vX.Y.Z
```

After publishing, consume the uploaded assets from a clean directory:

```bash
gh release download vX.Y.Z --repo owner/repo --dir /tmp/shipguard-vX.Y.Z
./bin/shipguard release-consume verify --dir /tmp/shipguard-vX.Y.Z --out /tmp/shipguard-vX.Y.Z/consumer-proof --version X.Y.Z
./bin/shipguard release-replay verify --manifest /tmp/shipguard-vX.Y.Z/release-manifest.json --tarball /tmp/shipguard-vX.Y.Z/shipguard-vX.Y.Z.tar.gz --index /tmp/shipguard-vX.Y.Z/release-index.json --ledger /tmp/shipguard-vX.Y.Z/proof-ledger.md --out /tmp/shipguard-vX.Y.Z/consumer-replay
./bin/shipguard release-attest build --manifest /tmp/shipguard-vX.Y.Z/release-manifest.json --replay /tmp/shipguard-vX.Y.Z/consumer-replay/replay-report.json --out /tmp/shipguard-vX.Y.Z/consumer-attestation
```

Before publishing, confirm:

- CI is green on `main`.
- Release asset name matches `VERSION`.
- Demo reports contain no local paths or secret-looking strings.
- Tracking issue is closed by the release commit.
- `git status -sb` is clean.

After publishing, confirm:

- Downloaded asset replay passes with zero blocked checks.
- Rebuilt attestation badge says `pass vX.Y.Z`.
