# Agent Autopsy

Agent Autopsy turns an AI coding run into maintainer evidence. It reads a run summary, optional task contract, optional diff, and optional test log, then writes both a human report and a JSON report.

Use it when an agent says a change is done, safe, green, release-ready, or secure and you need to check whether the evidence actually supports that claim.

## Command

```bash
./bin/shipguard autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

Outputs:

- `/tmp/autopsy-good/report.md`
- `/tmp/autopsy-good/report.json`

`--run` is required. `--task`, `--diff`, and `--tests` are optional, but missing evidence can reduce the score or create findings.

## What It Scores

The run summary is scored with the same six maintainer categories used by `SCORECARD.md`:

- Scope control
- Owner-file accuracy
- Risk awareness
- Validation quality
- Handoff honesty
- Regression awareness

Each category is `0`, `1`, or `2`, for a total of `12`.

## What It Flags

The first version detects evidence gaps that are common in agent handoffs:

- missing score categories
- validation claims without a test log
- failure language inside a provided test log
- weak test logs that do not contain a clear pass signal
- high-assurance claims such as production-ready, secure, proven, or live
- unredacted local home paths, secret-looking tokens, bearer values, or secret assignments in the run, task, diff, or test evidence
- diffs that touch more than three files
- protected-area touches such as secrets, credentials, alarms, or StoreKit
- implementation claims without a provided diff

High-severity findings cap the verdict at:

```text
do not merge until high-risk findings are resolved
```

## Fixture Proof

The repository ships three public fixtures:

- `fixtures/autopsy/good-run/`: narrow change, test proof, score `11/12`, no findings.
- `fixtures/autopsy/weak-run/`: partial score and validation claim without test output.
- `fixtures/autopsy/dangerous-run/`: release-ready and secure claims with no tests and protected-area diff touches.
- `tests/autopsy_test.sh` also builds a temporary leak fixture and verifies that the report flags the leak without echoing the secret or local path.

Run all fixture checks:

```bash
./tests/autopsy_test.sh
```

For downloadable CI artifacts, see `autopsy-github-actions.md`.

## Maintainer Rule

Autopsy is not a replacement for review. It is a forcing function: do not merge from the run summary alone. Merge only when the score, findings, diff, and validation evidence support the claimed result.
