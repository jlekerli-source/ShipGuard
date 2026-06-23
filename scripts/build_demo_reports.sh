#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root="${1:-examples/demo-reports}"
generated_at="${SHIPGUARD_GENERATED_AT:-${CODEX_MAINTAINER_GENERATED_AT:-2026-06-16T00:00:00Z}}"

cd "$repo_root"

rm -rf "$out_root"
mkdir -p "$out_root"

SHIPGUARD_GENERATED_AT="$generated_at" \
  ./bin/shipguard arena run \
  --fixture fixtures/arena \
  --out "$out_root/arena" >/dev/null

SHIPGUARD_GENERATED_AT="$generated_at" \
  ./bin/shipguard leaderboard build \
  --arena-results "$out_root/arena/results.json" \
  --out "$out_root/leaderboard.json" >/dev/null

SHIPGUARD_GENERATED_AT="$generated_at" \
  ./bin/shipguard transcript corpus \
  --source fixtures/transcripts \
  --out "$out_root/transcripts" \
  --require-report true >/dev/null

cat > "$out_root/README.md" <<'README'
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
README

echo "wrote demo reports: $out_root"
