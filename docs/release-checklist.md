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
./tests/review_comment_test.sh
./tests/policy_test.sh
./tests/check_run_test.sh
./tests/ci_gate_test.sh
./tests/ci_summary_test.sh
./tests/sarif_test.sh
./tests/leaderboard_test.sh
./tests/self_audit_test.sh
./tests/next_goal_test.sh
./tests/package_release_test.sh
```

Then:

```bash
./scripts/package_release.sh
shasum -a 256 dist/codex-maintainer-vX.Y.Z.tar.gz
```

Before publishing, confirm:

- CI is green on `main`.
- Release asset name matches `VERSION`.
- Demo reports contain no local paths or secret-looking strings.
- Tracking issue is closed by the release commit.
- `git status -sb` is clean.
