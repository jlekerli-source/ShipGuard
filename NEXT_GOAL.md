# Next Goal

- Generated: 2026-06-18T17:55:20Z
- Current toolkit version: 3.113.0
- Target release: v3.114.0
- Title: ShipGuard Diff-First Verification Verdict

## Slash Plan

```text
/plan v3.114.0 ShipGuard Diff-First Verification Verdict for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Close the next product-strategy gap from the external evaluation: make shipguard verify explain the exact AI-generated diff before merge. Extend the task contract/report-quality loop with public fixtures and checks for changed files, changed behavior categories, deleted tests, validation coverage, protected-boundary crossings, evidence receipts, unsupported completion claims, and one exact next action. Keep this ShipGuard-only: do not edit Ringly or Ilmify, do not add broad new public command families, and keep private app observations as redacted eval evidence only. The release should make prepare/verify feel like the center of ShipGuard's proof-gated Codex change loop.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.114.0 ShipGuard Diff-First Verification Verdict for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Close the next product-strategy gap from the external evaluation: make shipguard verify explain the exact AI-generated diff before merge. Extend the task contract/report-quality loop with public fixtures and checks for changed files, changed behavior categories, deleted tests, validation coverage, protected-boundary crossings, evidence receipts, unsupported completion claims, and one exact next action. Keep this ShipGuard-only: do not edit Ringly or Ilmify, do not add broad new public command families, and keep private app observations as redacted eval evidence only. The release should make prepare/verify feel like the center of ShipGuard's proof-gated Codex change loop, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Close the next product-strategy gap from the external evaluation: make shipguard verify explain the exact AI-generated diff before merge. Extend the task contract/report-quality loop with public fixtures and checks for changed files, changed behavior categories, deleted tests, validation coverage, protected-boundary crossings, evidence receipts, unsupported completion claims, and one exact next action. Keep this ShipGuard-only: do not edit Ringly or Ilmify, do not add broad new public command families, and keep private app observations as redacted eval evidence only. The release should make prepare/verify feel like the center of ShipGuard's proof-gated Codex change loop.

## Completion Receipt

- Completed scope: v3.113.0 ShipGuard Design Coherence Boundary Fixtures. ShipGuard now separates design inventory, coherence risks, ShipGuard-owned follow-up work, target-app authorization, and proof boundaries in iOS design/report-quality outputs.
- Evidence: v3.113.0 shipped designCoherenceBoundary in ios design and ios report-quality, promoted fixtures/ios-report-quality/design-coherence-boundary, refreshed the Codex plugin to 0.2.28+codex.20260618172721, passed local/package/CI validation, and published https://github.com/jlekerli-source/ShipGuard/releases/tag/v3.113.0 with consumer release proof SHA-256 6a3dd931ea9c5f5f2db2d155c20648305a3e0546a6078fffa247ee5908acd4a2.

## Following Slash Plan

```text
/plan v3.115.0 ShipGuard iOS Notification Permission Killer Workflow for jlekerli-source/ShipGuard:
1. Use the improved diff-first task contract as the entry point for one risky iOS notification or permission change.
2. Add public fixtures and proof receipts for permission-state risk, protected scheduler/lifecycle boundaries, simulator/device proof separation, validation commands, unsupported completion claims, and one exact next action.
3. Keep this as a ShipGuard workflow/eval improvement; private Ringly or Ilmify observations remain read-only evidence and must not become app work.
4. Implement the CLI, docs, tests, package proof, plugin-refresh proof, release proof, and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.115.0 ShipGuard iOS Notification Permission Killer Workflow for jlekerli-source/ShipGuard: follow the following /plan above, make prepare/verify exceptional for one risky iOS notification or permission change, prove permission-state risk, protected-boundary, simulator/device-proof, validation, claim-checking, and exact-next-action behavior with public fixtures, then publish the release proof and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.115.0 --title "ShipGuard iOS Notification Permission Killer Workflow" --out NEXT_GOAL.md
```

## Constraints

- Keep implementation dependency-light unless a dependency is clearly justified.
- Do not publish private app source, paths, screenshots, app identifiers, or secrets.
- Do not fake adoption, stars, downloads, benchmark results, or security findings.
- Prefer release-tarball proof over source-only proof.

## Required Proof

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
./tests/docs_check_test.sh
./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict
./tests/ios_branding_test.sh
./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet
./tests/profile_audit_test.sh
./tests/profile_fix_plan_test.sh
./tests/profile_validation_receipts_test.sh
./tests/profile_validation_rerun_receipts_test.sh
./tests/profile_proof_handoff_receipts_test.sh
./tests/command_family_runtime_output_receipts_test.sh
./tests/trust_hardening_receipts_test.sh
./tests/task_contract_test.sh
./tests/task_contract_receipts_test.sh
./tests/tool_value_gauntlet_test.sh
./tests/ios_doctor_test.sh
./tests/ios_inventory_test.sh
./tests/ios_preview_test.sh
./tests/ios_target_match_test.sh
./tests/ios_codex_handoff_test.sh
./tests/ios_plan_test.sh
./tests/ios_prove_test.sh
./tests/ios_launchdeck_test.sh
./tests/ios_performance_test.sh
./tests/ios_devspace_check_test.sh
./tests/ios_design_test.sh
./tests/ios_modernize_test.sh
./tests/ios_app_intelligence_test.sh
./tests/ios_ai_readiness_test.sh
./tests/ios_spec_workflow_test.sh
./tests/ios_report_quality_test.sh
./tests/ios_redaction_test.sh
./tests/ios_shipguard_eval_test.sh
./tests/ios_shipguard_demo_test.sh
./tests/ios_goal_loop_test.sh
./tests/transcript_redaction_test.sh
./tests/transcript_verify_test.sh
./tests/transcript_verify_action_test.sh
./tests/transcript_corpus_test.sh
./tests/transcript_corpus_action_test.sh
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
./tests/release_proof_action_test.sh
./tests/release_proof_consumption_test.sh
./tests/release_proof_workflow_test.sh
./tests/release_replay_test.sh
./tests/package_release_test.sh
./scripts/package_release.sh
```

## Release Loop

1. Open or update the tracking issue for v3.114.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.114.0` and upload `dist/shipguard-v3.114.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
