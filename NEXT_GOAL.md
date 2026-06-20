# Next Goal

- Generated: 2026-06-20T03:39:05Z
- Current toolkit version: 3.131.0
- Target release: v3.156.0
- Title: Real Stable V4 Blocked-State UX

## Slash Plan

```text
/plan v3.156.0 Real Stable V4 Blocked-State UX for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Use the stable-publication starter kit against the real public ShipGuard release state and improve the blocked-state UX where real evidence is unavailable or contradictory.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.156.0 Real Stable V4 Blocked-State UX for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Use the stable-publication starter kit against the real public ShipGuard release state and improve the blocked-state UX where real evidence is unavailable or contradictory, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Use the stable-publication starter kit against the real public ShipGuard release state and improve the blocked-state UX where real evidence is unavailable or contradictory.

## Completion Receipt

- Completed scope: Ran LaunchKey and stable-publication against the real public v3.131.0 release assets. Public release assets and current package fresh-install/rollback proof passed, but same-prefix upgrade proof blocked on the previous v3.130.0 tarball's AppleDouble metadata, and stable-publication remained blocked on releaseNotesProof plus missing independent adoption and final security-review evidence. Fixed v4 release-candidate so supplied package/release-asset readiness summary rows reflect actual receipt status, and made the blocked upgrade nextCommand point to package rebuild, package-release proof, and the focused LaunchKey test.
- Evidence: Passed: gh release view v3.131.0 --repo jlekerli-source/ShipGuard; ./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v3156-real-release-candidate-final --package-tarball dist/shipguard-v3.131.0.tar.gz --upgrade-from-tarball dist/shipguard-v3.130.0.tar.gz --download-release-assets --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --shipguard-eval --shareable (review expected); ./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v3156-real-stable-publication-final --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report /tmp/shipguard-v3156-real-release-candidate-final --release-assets /tmp/shipguard-v3156-real-release-candidate-final/downloaded-release-assets --release-consume-out /tmp/shipguard-v3156-real-stable-consume-final --shipguard-eval --shareable (review expected); ./bin/shipguard ios report-quality --reports /tmp/shipguard-v3156-real-release-candidate-final --reports /tmp/shipguard-v3156-real-stable-publication-final --out /tmp/shipguard-v3156-real-report-quality-final --shareable; git diff --check; python3 -m py_compile scripts/v4_release_candidate.py; ./tests/v4_release_candidate_test.sh; ./tests/ios_report_quality_test.sh; ./bin/shipguard docs-check . --out /tmp/shipguard-docs-check-v3156-blocked-ux; ./bin/shipguard validate; ./tests/self_audit_test.sh; ./tests/cli_smoke_test.sh; ./tests/package_release_test.sh; ./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-v3156-value-gauntlet-final; ./bin/shipguard codex status --strict.

## Following Slash Plan

```text
/plan v3.157.0 Release Package Lineage Hygiene for jlekerli-source/ShipGuard:
1. Turn the real v3.130.0 AppleDouble blocker into a ShipGuard-owned package-lineage hygiene surface: scan local `dist/shipguard-v*.tar.gz` and optionally downloaded GitHub release assets for forbidden archive members, unsafe links/devices, missing package roots, and install-risk summaries.
2. Keep the output read-only and honest: do not rewrite historical release assets or claim they are fixed; produce a repair plan, affected versions, safe current baseline, and exact next commands for rebuilding/replacing future packages.
3. Wire the surface into docs, tests, package proof, and report-quality/value-gauntlet coverage so old package hygiene regressions are caught before LaunchKey upgrade proof.
4. Generate the next completion receipt and following /plan plus /goal after validation passes, keeping the active goal loop alive.
```

## Following Slash Goal

```text
/goal Implement v3.157.0 Release Package Lineage Hygiene for jlekerli-source/ShipGuard: follow the following /plan above, add a read-only ShipGuard package-lineage hygiene report for release tarballs and downloaded assets, prove it catches the historical AppleDouble blocker without rewriting releases or faking repair, wire docs/tests/package/report-quality/value-gauntlet coverage, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.157.0 --title "Release Package Lineage Hygiene" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.156.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.156.0` and upload `dist/shipguard-v3.156.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
