# Next Goal

- Generated: 2026-06-22T03:17:04Z
- Current toolkit version: 3.131.0
- Target release: v3.181.0
- Title: Stable V4 Publication Real Release Packet QA

## Slash Plan

```text
/plan v3.181.0 Stable V4 Publication Real Release Packet QA for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Choose the next bounded ShipGuard stable-publication report-quality improvement from docs/oss-evaluation.md, preferably the next real public stable-v4 publication gap after report-quality local-delta alignment, and implement it with CLI output, docs, fixtures, report-quality enforcement, package proof, push, CI verification, and the next loop handoff.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.181.0 Stable V4 Publication Real Release Packet QA for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Choose the next bounded ShipGuard stable-publication report-quality improvement from docs/oss-evaluation.md, preferably the next real public stable-v4 publication gap after report-quality local-delta alignment, and implement it with CLI output, docs, fixtures, report-quality enforcement, package proof, push, CI verification, and the next loop handoff, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Choose the next bounded ShipGuard stable-publication report-quality improvement from docs/oss-evaluation.md, preferably the next real public stable-v4 publication gap after report-quality local-delta alignment, and implement it with CLI output, docs, fixtures, report-quality enforcement, package proof, push, CI verification, and the next loop handoff.

## Completion Receipt

- Completed scope: v3.180 aligned ios report-quality with v3.179 release visibility semantics: local HEAD/main deltas are advisory, selected/latest release or public tag/manifest mismatches still require publish-new-github-release, the real v3.131 stable-publication report now passes report-quality while remaining product-blocked on release notes, LaunchKey candidate proof, adoption evidence, and security evidence.
- Evidence: python3 -m py_compile scripts/ios_report_quality.py scripts/v4_stable_publication.py; ./bin/shipguard v4 stable-publication --path . --out /tmp/shipguard-v3180-real-stable-publication --github-release-repo jlekerli-source/ShipGuard --release-version 3.131.0 --release-candidate-report /tmp/shipguard-v3180-missing-candidate --download-release-assets --external-adoption-evidence /tmp/shipguard-v3180-missing-adoption --security-review-evidence /tmp/shipguard-v3180-missing-security --shipguard-eval --shareable; ./bin/shipguard ios report-quality --reports /tmp/shipguard-v3180-real-stable-publication --out /tmp/shipguard-v3180-real-stable-publication-quality-2 --shareable; ./tests/ios_report_quality_test.sh; git diff --check; ./bin/shipguard docs-check . --out /tmp/shipguard-v3180-docs-check; ./bin/shipguard validate; ./tests/self_audit_test.sh; ./tests/cli_smoke_test.sh; ./tests/v4_stable_publication_test.sh; ./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-v3180-value-gauntlet-final; ./tests/package_release_test.sh; ./bin/shipguard codex status --strict

## Following Slash Plan

```text
/plan v3.182.0 Stable V4 Publication Real Release Packet QA for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.182.0 Stable V4 Publication Real Release Packet QA for jlekerli-source/ShipGuard: follow the /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.182.0 --title "Stable V4 Publication Real Release Packet QA" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.181.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.181.0` and upload `dist/shipguard-v3.181.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
