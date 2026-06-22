# ShipGuard Full Audit

`shipguard full-audit` is the release-loop orchestrator. It collapses validation, value-gauntlet, report-quality, package proof, plugin status, CI proof, and release-proof preparation into one resumable report.

Typical planning run:

```bash
./bin/shipguard full-audit \
  --path . \
  --out /tmp/shipguard-full-audit \
  --profile release \
  --plan-only \
  --shipguard-eval \
  --shareable
```

Planning output is a `review` report, not a `pass` report. It writes the same stage ledger, slow-lane summary, and `Execution Commands` table, but `resultUX.nextCommand` points to the executable release lane with missing CI/release metadata placeholders. Release-profile plans also include `releasePacketPlan`, a compact summary of selected release stages, required release metadata, missing metadata, non-claims, and proof boundaries. Treat that as the next command to run before calling the report release proof.

Full Audit reads `NEXT_GOAL.md` for its `slashPlan` and `slashGoal` handoff. When `NEXT_GOAL.md` has a completion receipt, Full Audit uses the `Following Slash Plan` and `Following Slash Goal`; otherwise it uses the active `Slash Plan` and `Slash Goal`. JSON and Markdown include `slashHandoffSource` plus `slashHandoffProof` so report-quality can reject stale hardcoded handoff text and prove the selected section, copy-ready slash commands, completion receipt presence, version-lineage status, and no-publication boundaries.

Typical local rerun after a failure:

```bash
./bin/shipguard full-audit \
  --path . \
  --out /tmp/shipguard-full-audit \
  --profile release \
  --resume
```

For fast proof while developing the orchestrator itself:

```bash
./bin/shipguard full-audit \
  --path . \
  --out /tmp/shipguard-full-audit-mini \
  --stage version \
  --stage py-compile \
  --stage docs-check \
  --shipguard-eval \
  --shareable
```

Outputs:

- `shipguard-full-audit.json`
- `shipguard-full-audit.md`
- `stage-receipts/<stage-id>.json`
- `logs/<stage-id>.stdout.txt`
- `logs/<stage-id>.stderr.txt`

The JSON includes `resultUX`, `slashHandoffSource`, `slashHandoffProof`, and release-profile `releasePacketPlan`, and the Markdown starts with `## Result`. That block gives the normalized status, concise verdict, proof source, why the report matters, and the next run or resume command before the stage ledger. The Markdown `## Execution Commands` section renders each `stages[].command` value so a maintainer can audit or copy the planned release lane without opening JSON.

Profiles:

- `quick`: version, diff check, Python compile, validate, docs-check, value-gauntlet, and report-quality.
- `release`: quick proof plus CLI smoke, self-audit, package-release, plugin-status, install-refresh, CI proof, and release-proof stages.
- `shipyard`: release proof plus next-goal handoff.

Boundary:

- The command does not push.
- The command does not publish a GitHub release.
- `install-refresh` mutates the local install/plugin cache only and requires `--include-install`.
- `release-proof` builds local assets only and requires release metadata.
- Target apps remain read-only; this command is ShipGuard product QA.

Use the `slowLaneSummary` section to decide what to rerun and `Execution Commands` to inspect the exact commands behind the lane. Use `--resume` to skip passing stages when the stage command and working directory match the previous receipt. A plan-only report proves route shape only; an executed report proves stage behavior.
