# CLI

`bin/codex-maintainer` is a dependency-light helper for validating and reusing this workflow kit.

## Validate

Run this from a checkout of this repository:

```bash
./bin/codex-maintainer validate
```

You can also pass a path to another checkout of this workflow bundle:

```bash
./bin/codex-maintainer validate ../ringly-codex-workflows
```

Validation checks required files, skill metadata, shell syntax, executable scripts, local markdown links, YAML files, and whitespace.

## Policy

Create or inspect a policy file:

```bash
./bin/codex-maintainer policy init .codex-maintainer/policy.conf
./bin/codex-maintainer policy show .codex-maintainer/policy.conf
```

Pass a policy into Autopsy with `--policy`. See `policy.md`.

## Version

Print the toolkit version:

```bash
./bin/codex-maintainer version
```

The command reads `VERSION`, which is also used by the release packaging script.

## Init

Copy a starter workflow profile into another project:

```bash
./bin/codex-maintainer init ios ../my-ios-app
./bin/codex-maintainer init web ../my-web-app
./bin/codex-maintainer init backend ../my-service
./bin/codex-maintainer init cli ../my-tool
```

The command writes:

- `AGENTS.md`
- `PLANS.md`
- `SUBAGENTS.md`
- `SCORECARD.md`
- `.agents/skills/`

Existing files are skipped. Use `--force` to overwrite generated workflow files:

```bash
./bin/codex-maintainer init ios ../my-ios-app --force
./bin/codex-maintainer init web ../my-web-app --force
./bin/codex-maintainer init backend ../my-service --force
./bin/codex-maintainer init cli ../my-tool --force
```

See `template-profiles.md` for profile details.

## Doctor

Check whether a target repo has the starter workflow files:

```bash
./bin/codex-maintainer doctor ../my-ios-app
./bin/codex-maintainer doctor ios ../my-ios-app
./bin/codex-maintainer doctor web ../my-web-app
./bin/codex-maintainer doctor backend ../my-service
./bin/codex-maintainer doctor cli ../my-tool
```

`doctor` without a profile defaults to `ios` for compatibility with older releases.

## Score

Score a Codex run markdown file:

```bash
./bin/codex-maintainer score examples/scored-run.md
```

The score file must include these categories:

- Scope control
- Owner-file accuracy
- Risk awareness
- Validation quality
- Handoff honesty
- Regression awareness

Each category should include a value from `0` to `2`.

## Autopsy

Generate Markdown and JSON evidence reports for an AI coding run:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

The command writes:

- `report.md`
- `report.json`

It checks the run score, validation claims, test evidence, diff size, high-assurance claims, and protected-area touches. High-severity findings produce a `do not merge until high-risk findings are resolved` verdict.

See `autopsy.md` for the full guide.

## Arena

Run a fixture pack through Autopsy and aggregate the results:

```bash
./bin/codex-maintainer arena run \
  --fixture fixtures/arena \
  --out /tmp/arena
```

The command writes aggregate `results.json`, a readable `index.md`, and per-case autopsy reports under `runs/<case-id>/`.

See `arena.md` for the fixture format and metrics.

Import an external fixture pack before running it:

```bash
./bin/codex-maintainer arena import \
  --source external-pack \
  --out /tmp/imported-arena-pack \
  --pack-name "external-pack"
```

The import command copies supported fixture files, writes `PACK.md`, and rejects obvious local paths or secret-looking values.

Sign and verify fixture-pack metadata:

```bash
./bin/codex-maintainer arena sign \
  --fixture /tmp/imported-arena-pack \
  --out /tmp/imported-arena-pack/PACK.json \
  --pack-name "external-pack"

./bin/codex-maintainer arena verify \
  --fixture /tmp/imported-arena-pack \
  --manifest /tmp/imported-arena-pack/PACK.json
```

The signature is a deterministic SHA-256 content digest for integrity checks, not identity signing with a private key.

Compare two Arena result files:

```bash
./bin/codex-maintainer arena compare \
  --left /tmp/arena-old/results.json \
  --right /tmp/arena-new/results.json \
  --out /tmp/arena-compare
```

The command writes `arena-compare.json` and `arena-compare.md`. It reports score, case-count, high-risk, added-case, removed-case, and per-case deltas so benchmark changes are reviewable instead of implied by a new average.

## Transcript Redaction

Redact a maintainer transcript before publishing it as an example, benchmark note, or public proof:

```bash
./bin/codex-maintainer transcript redact \
  --in raw-transcript.md \
  --out /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --private-term "InternalProjectName"
```

The command writes redacted Markdown and a JSON report. It redacts emails, token-like values, secret assignments, local user paths, long hex strings, bearer tokens, and custom private terms. See `transcript-redaction.md`.

Verify a redacted transcript and optional redaction report:

```bash
./bin/codex-maintainer transcript verify \
  --in /tmp/redacted-transcript.md \
  --report /tmp/redaction-report.json \
  --out /tmp/transcript-verify
```

The command writes `transcript-verify.json`, `transcript-verify.md`, and `badge.json`. It exits non-zero when risky content remains.

Build a public-safe transcript corpus index:

```bash
./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out /tmp/transcript-corpus \
  --require-report true
```

The command writes `corpus.json`, `index.md`, `badge.json`, and per-case verification reports under `runs/`. It exits non-zero when any transcript verification is blocked or when `--require-report true` is set and a case is missing `redaction-report.json`. See `transcript-corpus.md`.

## Review Comment

Generate a PR-ready comment and Shields-compatible badge from an autopsy report:

```bash
./bin/codex-maintainer review-comment \
  --report /tmp/autopsy/report.json \
  --out /tmp/review/comment.md \
  --badge /tmp/review/badge.json \
  --artifact-dir /tmp/review \
  --mode warn
```

Use `--mode fail` to exit non-zero when the report is blocked. See `pr-review-bot.md` for the GitHub Actions workflow shape.

## CI Gate

Run Autopsy, review-comment, badge generation, and gate JSON in one command:

```bash
./bin/codex-maintainer ci-gate \
  --run run.md \
  --diff change.patch \
  --tests test.log \
  --policy .codex-maintainer/policy.conf \
  --out artifacts/codex-maintainer-gate \
  --mode warn
```

Use `--mode fail` when blocked gates should fail CI. See `ci-gate.md`.

## CI Summary

Generate GitHub Actions step-summary Markdown from `gate.json`:

```bash
./bin/codex-maintainer ci-summary \
  --gate /tmp/codex-gate/gate.json \
  --out /tmp/codex-gate/summary.md
```

`ci-gate` writes `summary.md` automatically. See `ci-summary.md`.

## Check Run

Generate a GitHub Checks API payload from `gate.json`:

```bash
./bin/codex-maintainer check-run \
  --gate /tmp/codex-gate/gate.json \
  --head-sha "$GITHUB_SHA" \
  --out /tmp/codex-gate/check-run/payload.json
```

Post the payload only when the workflow has an explicit token and `checks: write` permission:

```bash
./bin/codex-maintainer check-run post \
  --payload /tmp/codex-gate/check-run/payload.json \
  --repo "$GITHUB_REPOSITORY" \
  --out /tmp/codex-gate/check-run/response.json
```

Use `--dry-run` to write the request metadata without contacting GitHub. The reusable CI gate action writes this payload into the artifact bundle and can post it when `post-check-run` is enabled. See `check-run.md`.

## SARIF

Convert an Autopsy report into SARIF 2.1.0:

```bash
./bin/codex-maintainer sarif \
  --report /tmp/autopsy/report.json \
  --out /tmp/autopsy/results.sarif
```

`ci-gate` writes `sarif/results.sarif` automatically. See `sarif.md`.

## Leaderboard

Build a stable public leaderboard JSON file from arena results:

```bash
./bin/codex-maintainer leaderboard build \
  --arena-results /tmp/arena/results.json \
  --out /tmp/leaderboard.json
```

See `benchmark.md` for the schema and `demo-reports.md` for checked-in generated examples.

## Release Manifest

Generate release proof files for a tarball:

```bash
./bin/codex-maintainer release-manifest \
  --tarball dist/codex-maintainer-v3.34.0.tar.gz \
  --out /tmp/codex-maintainer-release-proof
```

Verify the manifest against the tarball:

```bash
./bin/codex-maintainer release-manifest verify \
  --manifest /tmp/codex-maintainer-release-proof/release-manifest.json \
  --tarball dist/codex-maintainer-v3.34.0.tar.gz
```

The command writes `release-manifest.json` and `proof-ledger.md`. Add `--ci-run-url`, `--release-url`, and `--issue-url` after publishing to bind the local artifact digest to public release proof. See `release-manifest.md`.

Build a release proof catalog from manifests:

```bash
./bin/codex-maintainer release-index build \
  --manifest dist/release-proof-v3.5.0/release-manifest.json \
  --manifest dist/release-proof-v3.34.0/release-manifest.json \
  --out /tmp/codex-maintainer-release-index
```

The command writes `release-index.json` and `release-index.md`. See `release-index.md`.

Replay-verify downloaded release assets:

```bash
./bin/codex-maintainer release-replay verify \
  --manifest /tmp/codex-maintainer-release-proof/release-manifest.json \
  --tarball /tmp/codex-maintainer-release-assets/codex-maintainer-v3.34.0.tar.gz \
  --index /tmp/codex-maintainer-release-index/release-index.json \
  --ledger /tmp/codex-maintainer-release-proof/proof-ledger.md \
  --out /tmp/codex-maintainer-release-replay
```

The command writes `replay-report.json` and `replay-report.md`. See `release-replay.md`.

Build a compact release attestation:

```bash
./bin/codex-maintainer release-attest build \
  --manifest /tmp/codex-maintainer-release-proof/release-manifest.json \
  --replay /tmp/codex-maintainer-release-replay/replay-report.json \
  --out /tmp/codex-maintainer-release-attestation
```

The command writes `attestation.json`, `attestation.md`, and `attestation-badge.json`. See `release-attest.md`.

Build the full release proof bundle in one command:

```bash
./bin/codex-maintainer release-proof build \
  --out /tmp/codex-maintainer-release-proof-bundle \
  --release-url https://github.com/owner/repo/releases/tag/v3.34.0
```

The command writes the release tarball, manifest, release index, replay report, attestation, and attestation badge. See `release-proof.md`.

## Release Consume

Verify a flat directory of downloaded release assets and write a consumer report:

```bash
./bin/codex-maintainer release-consume verify \
  --dir /tmp/codex-maintainer-v3.34.0 \
  --out /tmp/codex-maintainer-v3.34.0/consumer-proof \
  --version 3.34.0
```

The command writes `consumer-report.json`, `consumer-report.md`, `asset-digests.json`, `asset-digests.md`, `sha256.txt`, replay outputs, and attestation outputs. It also cross-checks downloaded replay, attestation, and badge assets when they are present. Use `actions/release-consume` when this verification should run in GitHub Actions. See `release-consume.md` and `release-consume-action.md`.

## Release Diff

Compare two release proof asset directories and write JSON/Markdown diff reports:

```bash
./bin/codex-maintainer release-diff compare \
  --left /tmp/codex-maintainer-old \
  --right /tmp/codex-maintainer-v3.34.0 \
  --out /tmp/codex-maintainer-release-diff
```

The command accepts flat GitHub release downloads or nested `release-proof build` output. It compares release tarballs, manifests, indexes, ledgers, replay reports, attestations, and badges. Use `actions/release-diff` when this comparison should run in GitHub Actions. See `release-diff.md` and `release-diff-action.md`.

## Release Evidence

Export release proof reports as a static evidence page:

```bash
./bin/codex-maintainer release-evidence site \
  --consume /tmp/codex-maintainer-v3.34.0/consumer-proof \
  --diff /tmp/codex-maintainer-release-diff \
  --out /tmp/codex-maintainer-release-site
```

The command writes `index.html`, `evidence.json`, `README.md`, and source JSON copies under `sources/`. Use `actions/release-evidence` when this export should run in GitHub Actions. See `release-evidence-site.md` and `release-evidence-action.md`.

Build a static index from one or more evidence site exports:

```bash
./bin/codex-maintainer release-evidence index \
  --site /tmp/codex-maintainer-previous-site \
  --site /tmp/codex-maintainer-v3.34.0-site \
  --out /tmp/codex-maintainer-release-history
```

The command writes `index.html`, `evidence-index.json`, `README.md`, and copied site exports under `sites/`. Use `actions/release-evidence` with `build-index: true` when this index should run in GitHub Actions. See `release-evidence-index.md` and `release-evidence-action.md`.

Build the full local evidence path from downloaded release assets:

```bash
./bin/codex-maintainer release-evidence bundle \
  --assets /tmp/codex-maintainer-v3.34.0 \
  --left /tmp/codex-maintainer-old \
  --out /tmp/codex-maintainer-release-evidence-bundle \
  --version 3.34.0 \
  --title "Codex Maintainer v3.34.0 Evidence"
```

The command writes consumer proof, optional release-diff proof, `site/index.html`, `index/evidence-index.json`, `bundle.json`, and `README.md`. See `release-evidence-bundle.md`.

Verify a downloaded release evidence artifact:

```bash
./bin/codex-maintainer release-evidence verify \
  --dir /tmp/codex-maintainer-release-evidence \
  --out /tmp/codex-maintainer-release-evidence-verify \
  --require-diff true \
  --require-index true
```

The command writes `evidence-verify.json`, `evidence-verify.md`, and `badge.json`. It checks the static evidence site, copied source reports, optional evidence index, and optional `bundle.json` for consistency. Use `actions/release-evidence-verify` when this consumption proof should run in GitHub Actions. See `release-evidence-verify.md`.

Run the checked-in negative fixture pack as a single guardrail index:

```bash
./bin/codex-maintainer release-evidence negative-index \
  --fixture fixtures/release-evidence/negative \
  --out /tmp/codex-maintainer-negative-evidence
```

The command reads `cases.tsv`, runs each intentionally broken fixture through `release-evidence verify`, and writes `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, and per-case verifier outputs under `runs/<case>/`. It exits successfully only when every case blocks on the expected failed check.

Use `actions/release-evidence-negative-index` when this guardrail index should run in GitHub Actions. See `release-evidence-negative-index-action.md`.

## Release Proof Consumption

Download a published release bundle, verify the tarball digest, replay the proof, and rebuild the compact attestation:

```bash
gh release download v3.34.0 \
  --repo jlekerli-source/ringly-codex-workflows \
  --pattern 'codex-maintainer-v3.34.0.tar.gz' \
  --pattern 'release-manifest.json' \
  --pattern 'release-index.json' \
  --pattern 'proof-ledger.md' \
  --pattern 'attestation-badge.json' \
  --dir /tmp/codex-maintainer-v3.34.0

shasum -a 256 /tmp/codex-maintainer-v3.34.0/codex-maintainer-v3.34.0.tar.gz

./bin/codex-maintainer release-replay verify \
  --manifest /tmp/codex-maintainer-v3.34.0/release-manifest.json \
  --tarball /tmp/codex-maintainer-v3.34.0/codex-maintainer-v3.34.0.tar.gz \
  --index /tmp/codex-maintainer-v3.34.0/release-index.json \
  --ledger /tmp/codex-maintainer-v3.34.0/proof-ledger.md \
  --out /tmp/codex-maintainer-v3.34.0/consumer-replay

./bin/codex-maintainer release-attest build \
  --manifest /tmp/codex-maintainer-v3.34.0/release-manifest.json \
  --replay /tmp/codex-maintainer-v3.34.0/consumer-replay/replay-report.json \
  --out /tmp/codex-maintainer-v3.34.0/consumer-attestation
```

See `release-proof-consumption.md` for the rejection rules and trust model.

## Self-Audit

Generate release-readiness proof for the toolkit itself:

```bash
./bin/codex-maintainer self-audit --out /tmp/codex-maintainer-self-audit
```

The command writes:

- `self-audit.md`
- `self-audit.json`

It checks stable command availability and the core artifacts that make the Maintainer Reliability OS useful: policy config, CI gate action, review-comment action, demo leaderboard, and demo arena results.

See `maintainer-reliability-os.md`, `command-matrix.md`, and `release-checklist.md`.

## Next Goal

Generate a slash-goal style plan for the next release:

```bash
./bin/codex-maintainer next-goal --out NEXT_GOAL.md
```

Override the target release and title when the next improvement is already known:

```bash
./bin/codex-maintainer next-goal \
  --release 2.2.0 \
  --title "SARIF Evidence Export" \
  --out /tmp/next-goal.md
```

The command writes a Markdown plan with a `/goal` block, release constraints, proof commands, publishing checks, and the command to generate the following goal. See `next-goal.md`.

## Install From Release Tarball

Download and extract a release package:

```bash
tar -xzf codex-maintainer-v3.34.0.tar.gz
cd codex-maintainer-v3.34.0
PREFIX="$HOME/.local" ./scripts/install.sh
```

The installer copies toolkit files into `${PREFIX:-/usr/local}/lib/codex-maintainer` and writes a `codex-maintainer` wrapper into `${PREFIX:-/usr/local}/bin`.

## Package Contents

Release packages include the CLI, scripts, skills, templates, examples, demo fixtures, docs, scorecard, planning templates, and license. They exclude `.git`, `dist`, generated caches, and local machine paths.
