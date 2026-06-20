# Verify-First Quickstart

This is the smallest public ShipGuard proof loop:

1. Prepare one task contract.
2. Verify one diff against one structured validation receipt.
3. Read one concise proof report before merging.

Run it from the repository root:

```bash
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-verify-first/task \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable

./bin/shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verify-first/verdict
```

Open `/tmp/shipguard-verify-first/verdict/shipguard-verdict.md`.

The top `Proof Report` is the launch-facing summary:

```text
Status: pass
Validation: 1/1 covered
Claims checked: 1/1 accepted
Risk files: 0 risk file(s)
Release evidence: not-applicable
```

To see ShipGuard reject weak proof, use the plain log instead of the JSON receipt:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test.log \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verify-first/review
```

That returns `review` because a plain log is context, not a structured proof receipt.

To see ShipGuard block a risky change, use the protected workflow diff:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/protected-workflow.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Notification permission copy is fully verified." \
  --out /tmp/shipguard-verify-first/blocked
```

That returns `blocked` because the diff touches a protected workflow file and the claim overreaches the attached proof.

