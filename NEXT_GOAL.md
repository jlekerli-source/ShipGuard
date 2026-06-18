# Next Goal

- Generated: 2026-06-18T20:16:10Z
- Current toolkit version: 3.115.0
- Target release: v3.116.0
- Title: ShipGuard External Pilot Verdict Bench

## Slash Plan

```text
/plan v3.116.0 ShipGuard External Pilot Verdict Bench for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Build a measurement release, not another report family: add an external pilot verdict bench that scores public-safe read-only task traces for owner detection, acceptable and forbidden scope, required proof coverage, claim checking, redaction, exact next-action completeness, false-positive rate, and first useful verdict time. Keep private Ringly and Ilmify evidence read-only and convert any repeated weakness into public fixtures or synthetic labels before it affects ShipGuard behavior.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.116.0 ShipGuard External Pilot Verdict Bench for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Build a measurement release, not another report family: add an external pilot verdict bench that scores public-safe read-only task traces for owner detection, acceptable and forbidden scope, required proof coverage, claim checking, redaction, exact next-action completeness, false-positive rate, and first useful verdict time. Keep private Ringly and Ilmify evidence read-only and convert any repeated weakness into public fixtures or synthetic labels before it affects ShipGuard behavior, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Build a measurement release, not another report family: add an external pilot verdict bench that scores public-safe read-only task traces for owner detection, acceptable and forbidden scope, required proof coverage, claim checking, redaction, exact next-action completeness, false-positive rate, and first useful verdict time. Keep private Ringly and Ilmify evidence read-only and convert any repeated weakness into public fixtures or synthetic labels before it affects ShipGuard behavior.

## Completion Receipt

- Completed scope: v3.115.0 iOS Notification Permission Workflow shipped as the first domain-specific vertical workflow on top of prepare/verify.
- Evidence: v3.115.0 adds scripts/task_domain_packs.py with DomainPackContext and IOSNotificationPermissionPack, prepare domainRiskPack output for notification/permission/authorization/denied/provisional goals, verify proof lanes for permission-state, denied-state, simulator reset, and physical-device prompt boundaries, a negative generic-receipt review fixture, shareable redaction for target names inside candidate filenames, focused task-contract tests, value-gauntlet escalation to the external pilot verdict bench, refreshed current-version release docs, package-release proof, and strict Codex status proof with installed CLI 3.115.0.

## Following Slash Plan

```text
/plan v3.117.0 ShipGuard Domain Pack SDK Core Extraction for jlekerli-source/ShipGuard:
1. Extract the task-contract core behind stable modules for project snapshots, scope policy, evidence requirements, diff classification, claim verification, verdict calculation, and next-action selection while preserving the public `shipguard prepare` and `shipguard verify` JSON/Markdown shapes.
2. Turn `scripts/task_domain_packs.py` into a reusable Domain Pack SDK contract with a synthetic test pack proving new packs can be added without editing the verdict engine.
3. Add schema-version and compatibility tests so existing notification-permission task contracts and verdicts remain readable.
4. Update docs, package proof, plugin guidance, and value-gauntlet/report-quality expectations so future StoreKit, persistence, lifecycle, performance, design, and modernization packs plug into the core instead of becoming standalone report families.
5. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.117.0 ShipGuard Domain Pack SDK Core Extraction for jlekerli-source/ShipGuard: follow the following /plan above, extract the task-contract core behind stable modules, turn `scripts/task_domain_packs.py` into a reusable Domain Pack SDK with a synthetic test pack, preserve existing prepare/verify compatibility, update docs/tests/package/plugin proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.117.0 --title "ShipGuard Domain Pack SDK Core Extraction" --scope "Extract the task-contract core behind stable modules and turn task_domain_packs.py into a reusable Domain Pack SDK with a synthetic test pack, compatibility tests, docs, package proof, and plugin guidance." --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.116.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.116.0` and upload `dist/shipguard-v3.116.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
