# Release Checklist

Use this checklist for every release after `v2.0.0`.

```bash
./bin/codex-maintainer validate
./tests/cli_smoke_test.sh
./tests/template_profiles_test.sh
./tests/autopsy_test.sh
./tests/action_artifact_test.sh
./tests/arena_test.sh
./tests/arena_import_test.sh
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
./tests/release_replay_test.sh
./tests/release_proof_action_test.sh
./tests/release_proof_consumption_test.sh
./tests/release_proof_workflow_test.sh
./tests/package_release_test.sh
```

Then:

```bash
./scripts/package_release.sh
shasum -a 256 dist/codex-maintainer-vX.Y.Z.tar.gz
./bin/codex-maintainer release-manifest --tarball dist/codex-maintainer-vX.Y.Z.tar.gz --out /tmp/codex-maintainer-release-proof
./bin/codex-maintainer release-manifest verify --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --tarball dist/codex-maintainer-vX.Y.Z.tar.gz
./bin/codex-maintainer release-index build --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --out /tmp/codex-maintainer-release-index
./bin/codex-maintainer release-replay verify --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --tarball dist/codex-maintainer-vX.Y.Z.tar.gz --index /tmp/codex-maintainer-release-index/release-index.json --ledger /tmp/codex-maintainer-release-proof/proof-ledger.md --out /tmp/codex-maintainer-release-replay
./bin/codex-maintainer release-attest build --manifest /tmp/codex-maintainer-release-proof/release-manifest.json --replay /tmp/codex-maintainer-release-replay/replay-report.json --out /tmp/codex-maintainer-release-attestation
./bin/codex-maintainer release-proof build --out /tmp/codex-maintainer-release-proof-bundle --release-url https://github.com/owner/repo/releases/tag/vX.Y.Z
```

After publishing, consume the uploaded assets from a clean directory:

```bash
gh release download vX.Y.Z --repo owner/repo --dir /tmp/codex-maintainer-vX.Y.Z
./bin/codex-maintainer release-replay verify --manifest /tmp/codex-maintainer-vX.Y.Z/release-manifest.json --tarball /tmp/codex-maintainer-vX.Y.Z/codex-maintainer-vX.Y.Z.tar.gz --index /tmp/codex-maintainer-vX.Y.Z/release-index.json --ledger /tmp/codex-maintainer-vX.Y.Z/proof-ledger.md --out /tmp/codex-maintainer-vX.Y.Z/consumer-replay
./bin/codex-maintainer release-attest build --manifest /tmp/codex-maintainer-vX.Y.Z/release-manifest.json --replay /tmp/codex-maintainer-vX.Y.Z/consumer-replay/replay-report.json --out /tmp/codex-maintainer-vX.Y.Z/consumer-attestation
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
