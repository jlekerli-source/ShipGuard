#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_root="${1:-examples/demo-reports}"
generated_at="${CODEX_MAINTAINER_GENERATED_AT:-2026-06-16T00:00:00Z}"

cd "$repo_root"
# shellcheck source=/dev/null
source "$repo_root/scripts/lib/safe_paths.sh"

safe_rm_artifact_dir "out root" "$out_root" "$repo_root"
mkdir -p "$out_root"

CODEX_MAINTAINER_GENERATED_AT="$generated_at" \
  ./bin/codex-maintainer arena run \
  --fixture fixtures/arena \
  --out "$out_root/arena" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="$generated_at" \
  ./bin/codex-maintainer leaderboard build \
  --arena-results "$out_root/arena/results.json" \
  --out "$out_root/leaderboard.json" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="$generated_at" \
  ./bin/codex-maintainer transcript corpus \
  --source fixtures/transcripts \
  --out "$out_root/transcripts" \
  --require-report true >/dev/null

cat > "$out_root/README.md" <<'README'
# Demo Reports

These reports are generated from the public fixture pack with:

```bash
./scripts/build_demo_reports.sh
```

The generated output includes Arena results, leaderboard JSON, and transcript corpus verification reports. It is proof of format and workflow behavior, not a claim about real-world adoption.
README

echo "wrote demo reports: $out_root"
