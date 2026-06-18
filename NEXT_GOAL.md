# Next Goal

- Generated: 2026-06-18T09:08:13Z
- Current toolkit version: 3.98.0
- Target release: v3.98.0
- Title: ShipGuard Target Onboarding Receipts

## Slash Plan

```text
/plan v3.98.0 ShipGuard Target Onboarding Receipts for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Add targetOnboardingReceipts to value-gauntlet, add a public fresh-ios-target-first-plan receipt that proves a fresh iOS app repo can receive starter files, pass starter doctor, validate ShipGuard, run iOS doctor/inventory, get the first scoped permission-audit plan, and move the next priority to multi-profile onboarding receipts.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.98.0 ShipGuard Target Onboarding Receipts for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Add targetOnboardingReceipts to value-gauntlet, add a public fresh-ios-target-first-plan receipt that proves a fresh iOS app repo can receive starter files, pass starter doctor, validate ShipGuard, run iOS doctor/inventory, get the first scoped permission-audit plan, and move the next priority to multi-profile onboarding receipts, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Add targetOnboardingReceipts to value-gauntlet, add a public fresh-ios-target-first-plan receipt that proves a fresh iOS app repo can receive starter files, pass starter doctor, validate ShipGuard, run iOS doctor/inventory, get the first scoped permission-audit plan, and move the next priority to multi-profile onboarding receipts.

## Completion Receipt

- Completed scope: Add targetOnboardingReceipts to value-gauntlet, add a public fresh-ios-target-first-plan receipt that proves a fresh iOS app repo can receive starter files, pass starter doctor, validate ShipGuard, run iOS doctor/inventory, get the first scoped permission-audit plan, and move the next priority to multi-profile onboarding receipts.
- Evidence: Implemented targetOnboardingReceipts with fixtures/tool-value-gauntlet/target-onboarding-receipts/fresh-ios-target-first-plan/receipt.json; value-gauntlet probe shows targetOnboardingReceipts status pass, 1/1 receipts, six commands, and lowestValueSurfaceProbe now escalates to shipguard value-gauntlet multi-profile-onboarding-receipts.

## Following Slash Plan

```text
/plan v3.99.0 ShipGuard Multi-Profile Onboarding Receipts for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.99.0 ShipGuard Multi-Profile Onboarding Receipts for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.99.0 --title "ShipGuard Multi-Profile Onboarding Receipts" --out NEXT_GOAL.md
```

## Constraints

- Keep implementation dependency-light unless a dependency is clearly justified.
- Do not publish private Ringly, Ilmify, or other product source.
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

1. Open or update the tracking issue for v3.98.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.98.0` and upload `dist/shipguard-v3.98.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
