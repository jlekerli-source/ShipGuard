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

The JSON includes `resultUX`, and the Markdown starts with `## Result`. That block gives the normalized status, concise verdict, proof source, why the report matters, and the next resume command before the stage ledger.

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

Use the `slowLaneSummary` section to decide what to rerun. Use `--resume` to skip passing stages when the stage command and working directory match the previous receipt.
