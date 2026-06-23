# Demo Reports

Start with the verify-first quickstart when you want the smallest public proof loop:

```bash
./bin/shipguard prepare "Add notification permission copy" --path fixtures/demo-ios-repo --out /tmp/shipguard-verify-first/task --profile ios --validation "swift test" --shipguard-eval --shareable
./bin/shipguard verify --task /tmp/shipguard-verify-first/task/shipguard-task.json --diff examples/verify-first/diffs/scoped-permission.diff --evidence examples/verify-first/receipts/swift-test-receipt.json --claim "Implemented scoped notification permission copy." --out /tmp/shipguard-verify-first/verdict
```

Expected result: `ShipGuard Proof Report: pass`.

The same quickstart also has review and blocked variants in `docs/verify-first-quickstart.md`.

These reports are generated from the public fixture pack with:

```bash
./scripts/build_demo_reports.sh
```

The generated output includes Arena results, leaderboard JSON, and transcript corpus verification reports. It is proof of format and workflow behavior, not a claim about real-world adoption.
