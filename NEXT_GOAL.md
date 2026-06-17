# Next Goal

- Generated: 2026-06-17T19:34:07Z
- Current toolkit version: 3.59.0
- Target release: v3.62.0
- Title: Report Quality Prioritized Next-Action Gate

## Slash Plan

```text
/plan v3.62.0 Report Quality Prioritized Next-Action Gate for jlekerli-source/ShipGuard:
1. Implement this bounded improvement: Make ios report-quality emit a priorityAction and prioritizedActionabilityQuestions so clean read-only product-QA reports identify the first concrete ShipGuard improvement instead of leaving developers with an unranked checklist.
2. Implement the CLI, docs, tests, and package proof needed for that improvement.
3. Run the required proof commands, treat blocked or timed-out commands as failures, and record exact blockers.
4. Push main, verify GitHub Actions, publish and consume release proof, verify asset SHA-256 and clean git status, then generate the following goal.
```

## Slash Goal

```text
/goal Implement v3.62.0 Report Quality Prioritized Next-Action Gate for jlekerli-source/ShipGuard: follow the /plan above, deliver this bounded improvement: Make ios report-quality emit a priorityAction and prioritizedActionabilityQuestions so clean read-only product-QA reports identify the first concrete ShipGuard improvement instead of leaving developers with an unranked checklist, push main, verify GitHub Actions, publish the release tarball, verify asset SHA-256 and clean git status, then run shipguard next-goal again for the following release.
```


## Bounded Scope

Make ios report-quality emit a priorityAction and prioritizedActionabilityQuestions so clean read-only product-QA reports identify the first concrete ShipGuard improvement instead of leaving developers with an unranked checklist.

## Completion Receipt

- Completed scope: Make ios report-quality emit a priorityAction and prioritizedActionabilityQuestions so clean read-only product-QA reports identify the first concrete ShipGuard improvement instead of leaving developers with an unranked checklist.
- Evidence: A public demo-ios-repo read-only ShipGuard product-QA run generated shareable design, performance, modernize, app-intelligence, and ai-readiness reports. Report-quality passed with 5 reports, 100.0 average score, zero findings, and 21 actionability questions, but its nextActions were generic and started with fixing high report-quality issues even though no findings existed. After the change, ios report-quality emits priorityAction and prioritizedActionabilityQuestions, ranks report-quality findings before questions, and otherwise ranks questions from blocked/review source reports before lower-risk output. The same read-only quality pass now prioritizes the blocked performance report question 'Did the report explain why each finding matters without requiring private app context?' Added a focused fixture proving blocked performance outranks lower-priority AI readiness. Validated with python3 -m py_compile scripts/ios_report_quality.py; git diff --check; ./tests/ios_report_quality_test.sh; ./tests/ios_spec_workflow_test.sh; ./tests/ios_shipguard_eval_test.sh; ./bin/shipguard validate; ./bin/shipguard docs-check . --out /tmp/shipguard-docs-check-v362; ./tests/cli_smoke_test.sh; ./tests/self_audit_test.sh; ./tests/next_goal_test.sh; ./tests/package_release_test.sh; ./bin/shipguard ios eval --cases evals/ios_shipguard_cases.jsonl --out /tmp/ios-shipguard-eval-v362; codex plugin marketplace add .; codex plugin add ios-shipguard@shipguard; and ./bin/shipguard codex status --strict.

## Following Slash Plan

```text
/plan v3.63.0 Performance Finding Explanation Gate for jlekerli-source/ShipGuard:
1. Review ROADMAP.md, docs/oss-evaluation.md, and the latest read-only ShipGuard product-QA evidence.
2. Pick one bounded improvement that makes ShipGuard reports more useful without turning private-app findings into app work.
3. Implement the CLI, docs, tests, package proof, and plugin-refresh proof needed for that improvement.
4. Generate the next completion receipt and following /plan plus /goal after validation passes.
```

## Following Slash Goal

```text
/goal Implement v3.63.0 Performance Finding Explanation Gate for jlekerli-source/ShipGuard: follow the following /plan above, choose one bounded ShipGuard report-quality improvement from ROADMAP.md and docs/oss-evaluation.md, implement it with proof, and generate the next completion receipt plus following /plan and /goal after validation passes.
```

Generate that follow-up file with:

```bash
./bin/shipguard next-goal --release 3.63.0 --title "Performance Finding Explanation Gate" --out NEXT_GOAL.md
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

1. Open or update the tracking issue for v3.62.0.
2. Implement the smallest complete improvement that makes the toolkit more useful.
3. Update README, CLI docs, changelog, roadmap, and package verification.
4. Commit with an issue-closing reference.
5. Push `main` and verify GitHub Actions success.
6. Create release `v3.62.0` and upload `dist/shipguard-v3.62.0.tar.gz`.
7. Verify release asset digest, closed issue, tag target, and clean git status.
8. Generate the next goal:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```
