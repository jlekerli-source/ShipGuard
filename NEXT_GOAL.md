# Next Goal

- Generated: 2026-06-20T03:21:54Z
- Current toolkit version: 3.131.0
- Target release: v3.155.0
- Title: Stable V4 Publication Evidence Starter Kit

## Slash Plan

```text
/plan v3.155.0 Stable V4 Publication Evidence Starter Kit for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Make the stable-v4 publication evidence packet concrete and easier to collect without claiming stable v4: every stable-publication report should write a draft-only starter kit with checklist, adoption evidence starter, security-review starter, and clear report-quality coverage.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.155.0 Stable V4 Publication Evidence Starter Kit for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Make the stable-v4 publication evidence packet concrete and easier to collect without claiming stable v4: every stable-publication report should write a draft-only starter kit with checklist, adoption evidence starter, security-review starter, and clear report-quality coverage, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Make the stable-v4 publication evidence packet concrete and easier to collect without claiming stable v4: every stable-publication report should write a draft-only starter kit with checklist, adoption evidence starter, security-review starter, and clear report-quality coverage.

## Completion Receipt

- Completed scope: Added stablePublicationEvidenceStarterKit to shipguard v4 stable-publication, generated stable-publication-evidence-kit/ with README, checklist JSON, adoption starter JSON, and security-review starter JSON on every run, rendered the kit in Markdown, skipped the generated kit during report-quality recursion, and protected the behavior through focused, report-quality, package, docs, self-audit, and value-gauntlet proof.
- Evidence: Passed: python3 -m py_compile scripts/v4_stable_publication.py scripts/ios_report_quality.py; ./tests/v4_stable_publication_test.sh; ./tests/ios_report_quality_test.sh; ./bin/shipguard ios report-quality --reports /tmp/shipguard-v3155-stable-publication-after --out /tmp/shipguard-v3155-stable-publication-after-quality2 --shareable; ./bin/shipguard docs-check . --out /tmp/shipguard-docs-check-v3155-starter-kit; ./bin/shipguard validate; ./tests/self_audit_test.sh; ./tests/cli_smoke_test.sh; ./tests/package_release_test.sh; ./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-v3155-value-gauntlet-after; ./bin/shipguard codex status --strict.

## Following Slash Plan

```text
/plan v3.156.0 Real Stable V4 Evidence Packet Collection for jlekerli-source/ShipGuard:
1. Use the new stable-publication evidence starter kit against the real public ShipGuard release state: run LaunchKey/release-candidate where possible, download or supply release assets, fill or explicitly mark adoption/security evidence as missing, and run `shipguard v4 stable-publication`.
2. If real evidence is unavailable, improve ShipGuard's blocked-state UX rather than faking proof: add a publication packet status page or command output that says exactly which external artifacts are missing, where to obtain them, and which claims stay forbidden.
3. Convert any confusing or repetitive blocked-state output into public fixtures, report-quality checks, docs, package proof, and value-gauntlet coverage.
4. Generate the next completion receipt and following /plan plus /goal after validation passes, keeping the active goal loop alive.
```

## Following Slash Goal

```text
/goal Implement v3.156.0 Real Stable V4 Evidence Packet Collection for jlekerli-source/ShipGuard: follow the following /plan above, use the stable-publication starter kit against the real public ShipGuard release state, either collect the missing real evidence or improve the blocked-state UX so the missing external artifacts and forbidden claims are unmistakable, prove the behavior with fixtures/tests/docs/package/value-gauntlet, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.156.0 --title "Real Stable V4 Evidence Packet Collection" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.155.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.155.0` and upload `dist/shipguard-v3.155.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
