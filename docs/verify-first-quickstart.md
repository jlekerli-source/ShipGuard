# Verify-First Quickstart

`shipguard verify` is the fastest way to understand ShipGuard.

It answers one practical maintainer question:

```text
Can this AI-generated diff be reviewed or merged from the task scope, proof receipts, and claims attached to it?
```

## Run The Demo

From a ShipGuard checkout:

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

The command prints the verdict immediately:

```text
ShipGuard Proof Report: pass. Validation 1/1 covered; claims 1/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable.
status: pass
```

For the full review packet, open:

```bash
/tmp/shipguard-verify-first/verdict/shipguard-verdict.md
```

The first section is intentionally copy-ready:

```text
ShipGuard Proof Report
Status: pass
Validation: 1/1 covered
Claims checked: 1/1 accepted
Risk files: 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s)
Release evidence: not-applicable
```

## Why It Matters

ShipGuard does not trust a phrase like "tests passed." It checks:

- whether the changed files are inside the prepared scope
- whether protected files were touched
- whether validation is backed by structured receipts
- whether broad claims overreach the proof
- what the next exact action should be

## Weak Proof Demo

Run the same diff with a plain log:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test.log \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verify-first/review
```

That returns `review`: the log is useful context, but it is not a structured validation receipt.
The terminal summary starts with `ShipGuard Proof Report: review`.

## Risky Diff Demo

Run the protected workflow diff:

```bash
./bin/shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/protected-workflow.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Notification permission copy is fully verified." \
  --out /tmp/shipguard-verify-first/blocked
```

That returns `blocked`: the diff touches a protected workflow path and the claim says "fully verified" without physical-device proof.
The terminal summary starts with `ShipGuard Proof Report: blocked`.

## PR Workflow

Use `examples/workflows/verify-pr.yml` as the transparent GitHub Actions starting point. It shows the shape:

1. install ShipGuard
2. prepare a task contract
3. write a PR diff
4. run validation
5. write a structured receipt
6. run `shipguard verify`
7. upload `shipguard-verdict.json` and `shipguard-verdict.md`

Set `SHIPGUARD_VALIDATION_COMMAND` once near the top of the workflow before using it in a real repository.
The workflow uses that single value for the task contract, the CI command, and the structured receipt; if the placeholder is left in place, it fails early with a clear setup message.
