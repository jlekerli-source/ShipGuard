# Next Goal

- Generated: 2026-06-19T15:10:46Z
- Current toolkit version: 3.131.0
- Target release: v3.136.0
- Title: InspectDeck Executable Next Commands

## Slash Plan

```text
/plan v3.136.0 InspectDeck Executable Next Commands for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Improve InspectDeck after read-only ShipGuard self-QA showed Value Gauntlet prose proof guidance could be copied into resultUX.nextCommand, causing report-quality to flag result-ux-next-command-not-command.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.136.0 InspectDeck Executable Next Commands for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Improve InspectDeck after read-only ShipGuard self-QA showed Value Gauntlet prose proof guidance could be copied into resultUX.nextCommand, causing report-quality to flag result-ux-next-command-not-command, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Improve InspectDeck after read-only ShipGuard self-QA showed Value Gauntlet prose proof guidance could be copied into resultUX.nextCommand, causing report-quality to flag result-ux-next-command-not-command.

## Completion Receipt

- Completed scope: Fixed InspectDeck so Value Gauntlet prose proof guidance stays in nextAction.reason and resultUX.nextActionSummary while nextAction.command and resultUX.nextCommand fall back to a runnable value-gauntlet command template.
- Evidence: Read-only ShipGuard self-QA generated Value Gauntlet, Full Audit, MarketplaceDeck, Brand Deck, V4 Preview, V4 Schema Freeze, V4 Release Candidate, and InspectDeck reports under /tmp/shipguard-loop-*-5; ios report-quality returned review with result-ux-next-command-not-command for /tmp/shipguard-loop-inspect-5/shipguard-inspect.json; after the fix /tmp/shipguard-loop-inspect-5-fixed reports resultUX.nextCommand=./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet while preserving the prose proof guidance in nextAction.reason; python3 -m py_compile scripts/shipguard_inspect.py; ./tests/inspect_test.sh; ios report-quality on the fixed bundle passed.

## Following Slash Plan

```text
/plan v3.137.0 v4 Product Release Stabilization Receipts for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.137.0 v4 Product Release Stabilization Receipts for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.137.0 --title "v4 Product Release Stabilization Receipts" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.136.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.136.0` and upload `dist/shipguard-v3.136.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
