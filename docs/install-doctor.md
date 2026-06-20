# Install And Doctor

This is the fastest first-run path for a fresh maintainer.

## Install From A Checkout Or Release Package

From a ShipGuard checkout or extracted release package:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" version
"$HOME/.local/bin/shipguard" validate
```

Add `$HOME/.local/bin` to `PATH` if you want to run `shipguard` without the absolute path.

## Prove A Target Repo Is Ready

Initialize a starter profile in a test repo:

```bash
shipguard init ios ../my-ios-app
shipguard doctor ios ../my-ios-app
```

`shipguard doctor` is ShipGuard RepoVitals. It checks that the target has the starter workflow files needed before agent work starts:

```text
# ShipGuard RepoVitals
Profile: ios
Status: pass
Required files: 10/10
Next action: run shipguard prepare or the profile-specific audit command for the first scoped task.
```

If required starter files are missing, `doctor` exits non-zero and prints the smallest repair:

```text
Status: missing
Required files: 0/10
Next action: run shipguard init ios "<target>" --force only if overwriting generated workflow files is intended.
```

## Then Run Verify-First

After install and RepoVitals pass, run the public proof demo:

```bash
shipguard prepare "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-verify-first/task \
  --profile ios \
  --validation "swift test" \
  --shipguard-eval \
  --shareable

shipguard verify \
  --task /tmp/shipguard-verify-first/task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verify-first/verdict
```

See `verify-first-quickstart.md` for the pass, review, and blocked examples.
