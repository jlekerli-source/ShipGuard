# Next Goal

- Generated: 2026-06-23T22:20:02Z
- Current toolkit version: 3.205.0
- Target release: v3.206.0
- Title: Stable-publication external evidence next-gap index polish

## Version Lineage Check

- Status: pass
- VERSION: 3.205.0
- Expected next release from VERSION: v3.206.0
- Planned target release: v3.206.0
- Current checkout package artifact before version bump: dist/shipguard-v3.205.0.tar.gz
- Expected package artifact after release bump: dist/shipguard-v3.206.0.tar.gz
- Action: Before publishing v3.206.0, bump VERSION to 3.206.0, rebuild, and verify dist/shipguard-v3.206.0.tar.gz.

## Slash Plan

```text
/plan v3.206.0 Stable-publication external evidence next-gap index polish for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Polish the stable-publication external evidence next-gap index so the next real QA target is concrete, useful, and does not recycle an already-promoted fixture or blur fixture coverage with adoption/security/stable-v4 proof.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, bump VERSION before release packaging, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.206.0 Stable-publication external evidence next-gap index polish for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Polish the stable-publication external evidence next-gap index so the next real QA target is concrete, useful, and does not recycle an already-promoted fixture or blur fixture coverage with adoption/security/stable-v4 proof, push main, verify GitHub Actions, bump VERSION before publishing the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Polish the stable-publication external evidence next-gap index so the next real QA target is concrete, useful, and does not recycle an already-promoted fixture or blur fixture coverage with adoption/security/stable-v4 proof.

## Completion Receipt

- Completed scope: v3.205.0 promoted a public artifact-redaction fixture proving stable-publication reports keep artifact/provenance gates, required fields, rejected unredacted artifacts, blocked substitutes, non-claims, and Markdown visibility regression-covered.
- Evidence: Commit 3d9c0e4e pushed to main; GitHub Actions run 28060867745 completed success; local package tarball dist/shipguard-v3.205.0.tar.gz SHA-256 41f5dd869c32944d6b277871c8d86608e1c01925463f9254645bb5644b228b44; ./bin/shipguard codex status --strict passed after local CLI refresh; ./tests/package_release_test.sh passed.

## Following Slash Plan

```text
/plan v3.207.0 Stable-publication external evidence real-QA candidate capture for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.207.0 Stable-publication external evidence real-QA candidate capture for jlekerli-source/ShipGuard: follow the /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.207.0 --title "Stable-publication external evidence real-QA candidate capture" --out NEXT_GOAL.md
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
./tests/structured_evidence_receipts_test.sh
./tests/tool_value_gauntlet_test.sh
./tests/full_audit_test.sh
./tests/inspect_test.sh
./tests/concise_verdict_result_ux_test.sh
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
./tests/ios_scan_scope_budget_test.sh
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

1. Open or update the tracking issue for v3.206.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Bump VERSION to 3.206.0, build `dist/shipguard-v3.206.0.tar.gz`, create release `v3.206.0`, and upload the rebuilt tarball.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
