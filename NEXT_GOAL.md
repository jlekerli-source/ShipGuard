# Next Goal

- Generated: 2026-06-19T18:50:05Z
- Current toolkit version: 3.131.0
- Target release: v3.143.0
- Title: Stable V4 External Adoption Evidence Gate

## Slash Plan

```text
/plan v3.143.0 Stable V4 External Adoption Evidence Gate for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Improve ShipGuard after read-only LaunchKey self-QA showed install, upgrade, rollback, and release-asset proof can pass while stable-v4 adoption evidence remains only prose. Add a structured external adoption evidence gate that validates independent redacted evidence, blocks private paths, fake adoption, and token-like strings, and gives a concrete next command when adoption proof is missing.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.143.0 Stable V4 External Adoption Evidence Gate for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Improve ShipGuard after read-only LaunchKey self-QA showed install, upgrade, rollback, and release-asset proof can pass while stable-v4 adoption evidence remains only prose. Add a structured external adoption evidence gate that validates independent redacted evidence, blocks private paths, fake adoption, and token-like strings, and gives a concrete next command when adoption proof is missing, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Improve ShipGuard after read-only LaunchKey self-QA showed install, upgrade, rollback, and release-asset proof can pass while stable-v4 adoption evidence remains only prose. Add a structured external adoption evidence gate that validates independent redacted evidence, blocks private paths, fake adoption, and token-like strings, and gives a concrete next command when adoption proof is missing.

## Completion Receipt

- Completed scope: shipguard v4 release-candidate now accepts --external-adoption-evidence JSON files or directories, records externalAdoptionEvidenceProof and externalAdoptionEvidenceStableGate, separates structurally valid synthetic fixture evidence from stable-v4 eligible independent evidence, blocks private paths, private app identifiers, token-like text, missing fields, non-independent actors, and unredacted records through blockingProof, redacts evidence paths in shareable reports, and updates README, GitHub presentation guidance, CLI docs, roadmap, changelog, and Codex skill guidance.
- Evidence: Read-only current-state QA at /tmp/shipguard-v3143-qa-after reported freshInstallPackageProof=pass, upgradePackageProof=pass, rollbackPackageProof=pass, githubReleaseAssetDownloadProof=pass, publishedReleaseAssetProof=pass, externalAdoptionEvidenceProof=not-provided, externalAdoptionEvidenceStableGate=not-provided, and a next command requiring --external-adoption-evidence. Synthetic adoption QA at /tmp/shipguard-v3143-adoption-pass reported externalAdoptionEvidenceProof=pass and externalAdoptionEvidenceStableGate=pass with shareable redaction. Focused regression ./tests/v4_release_candidate_test.sh passed with not-provided, synthetic review, stable-eligible pass, missing-path blocked, and invalid-record blocked coverage.

## Following Slash Plan

```text
/plan v3.144.0 Stable V4 Security Review Evidence Gate for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.144.0 Stable V4 Security Review Evidence Gate for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.144.0 --title "Stable V4 Security Review Evidence Gate" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.143.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.143.0` and upload `dist/shipguard-v3.143.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
