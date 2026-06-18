# Next Goal

- Generated: 2026-06-18T01:41:24Z
- Current toolkit version: 3.70.1
- Target release: v3.78.0
- Title: Report Quality Promotion Manifest Consumption

## Slash Plan

```text
/plan v3.78.0 Report Quality Promotion Manifest Consumption for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Consume report-quality fixture promotion manifests as materialized-fixture metadata instead of grading them as source reports, validate promotion paths, copy placeholders, validation commands, review checklist coverage, guide synchronization, and materialized files, and keep generated outputs path-safe and ShipGuard-only.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.78.0 Report Quality Promotion Manifest Consumption for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Consume report-quality fixture promotion manifests as materialized-fixture metadata instead of grading them as source reports, validate promotion paths, copy placeholders, validation commands, review checklist coverage, guide synchronization, and materialized files, and keep generated outputs path-safe and ShipGuard-only, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Consume report-quality fixture promotion manifests as materialized-fixture metadata instead of grading them as source reports, validate promotion paths, copy placeholders, validation commands, review checklist coverage, guide synchronization, and materialized files, and keep generated outputs path-safe and ShipGuard-only.

## Completion Receipt

- Completed scope: Consume report-quality fixture promotion manifests as materialized-fixture metadata instead of grading them as source reports, validate promotion paths, copy placeholders, validation commands, review checklist coverage, guide synchronization, and materialized files, and keep generated outputs path-safe and ShipGuard-only.
- Evidence: A fresh read-only external-audit over ShipGuard plus the Expo URL and Design Motion Principles source generated materialized report-quality fixtures. Scoring the full materialized fixture root exposed that fixture-promotion-manifest.json was being graded as an ordinary report-quality source report, producing false self-report-skipped and markdown-companion-missing findings. Report-quality now excludes promotion manifests from source report discovery, consumes them under fixturePromotionManifests, renders a Fixture Promotion Manifests Markdown section, passes clean materialized roots, and flags broken manifest metadata such as unsafe suggestedFixturePath or missing copy placeholders with fixture-promotion-* findings. Focused tests, clean-root proof, broken-manifest proof, docs check, bundle validation, CLI smoke, self-audit, Codex status, and package release proof passed.

## Following Slash Plan

```text
/plan v3.79.0 Build iOS Apps Native Integration for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.79.0 Build iOS Apps Native Integration for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.79.0 --title "Build iOS Apps Native Integration" --out NEXT_GOAL.md
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
./tests/ios_doctor_test.sh
./tests/ios_inventory_test.sh
./tests/ios_preview_test.sh
./tests/ios_target_match_test.sh
./tests/ios_codex_handoff_test.sh
./tests/ios_plan_test.sh
./tests/ios_prove_test.sh
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

1. Open or update the tracking issue for v3.78.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.78.0` and upload `dist/shipguard-v3.78.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
