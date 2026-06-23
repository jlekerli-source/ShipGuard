# Next Goal

- Generated: 2026-06-23T07:03:44Z
- Current toolkit version: 3.165.0
- Target release: v3.165.0
- Title: Diff-first no-disposition repair hint

## Version Lineage Check

- Status: pass
- VERSION: 3.165.0
- Expected next release from VERSION: v3.166.0
- Planned target release: v3.165.0
- Current checkout package artifact: dist/shipguard-v3.165.0.tar.gz
- Release package artifact to build: dist/shipguard-v3.165.0.tar.gz
- Action: VERSION already names v3.165.0; build, verify, publish, and consume dist/shipguard-v3.165.0.tar.gz before generating the next goal.

## Slash Plan

```text
/plan v3.165.0 Diff-first no-disposition repair hint for jlekerli-source/ShipGuard:
1. Pick exactly one high-signal maintainer reliability improvement from ROADMAP.md and write the bounded scope before editing.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, build and verify the release tarball, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.165.0 Diff-first no-disposition repair hint for jlekerli-source/ShipGuard: follow the /plan above, finish one high-signal maintainer reliability improvement from ROADMAP.md with CLI/docs/tests/package proof, push main, verify GitHub Actions, build and verify the release tarball, publish and consume release proof, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Completion Receipt

- Completed scope: v3.165 added a no-disposition repair hint to shipguard verify: missing reviewer-disposition receipts now carry a copy-ready rerun command, accepted values, and the local-outcome-only boundary in JSON and Markdown.
- Evidence: Commit c234b8dbd44de9871189f0058bc236abce8d0345 implemented the v3.165 repair hint; commit 13351cb91870934eb85f6cf4db281775d665e864 fixed the release-consumption checklist and is pushed to main. Local proof passed: git diff --check; python3 -m py_compile scripts/task_contract.py; ./tests/task_contract_test.sh; ./tests/verify_first_quickstart_test.sh; ./bin/shipguard validate; ./bin/shipguard docs-check . --out /tmp/shipguard-docs-check-v3.165; ./tests/cli_smoke_test.sh; ./tests/self_audit_test.sh; ./tests/package_release_test.sh; env PREFIX="/Users/omarat-turkmani/.local" ./scripts/install.sh; ./bin/shipguard codex status --strict; ./tests/release_proof_consumption_test.sh after the stale checklist fix. GitHub Actions passed on the repair commit: https://github.com/jlekerli-source/ShipGuard/actions/runs/28008283538. Release proof built at /tmp/shipguard-v3.165.0-proof; public asset consumer proof passed at /tmp/shipguard-v3.165.0-consume; tarball SHA-256 54fa86f19c52404b70ccc8a8007bf91b4ea41fc59764691756fe3e2c57d0302d matched proof asset copy and dist/shipguard-v3.165.0.tar.gz. v4 release candidate passed at /tmp/shipguard-v3.165.0-candidate. Stable-publication remained honestly blocked with exit 1 at /tmp/shipguard-v3.165.0-stable-publication until public GitHub release metadata exists.

## Following Slash Plan

```text
/plan v3.166.0 Diff-first reviewer outcome copy polish for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.166.0 Diff-first reviewer outcome copy polish for jlekerli-source/ShipGuard: follow the /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.166.0 --title "Diff-first reviewer outcome copy polish" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.165.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Build `dist/shipguard-v3.165.0.tar.gz`, create release `v3.165.0`, upload the rebuilt tarball, and consume release proof.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
