#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard v4 preview --help >/dev/null
./bin/shipguard v4 preview \
  --path . \
  --out "$tmp_dir/v4-preview" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard v4 preview \
  --path . \
  --out "$tmp_dir/json-only" \
  --json >/dev/null
./bin/shipguard v4 preview \
  --path . \
  --out "$tmp_dir/markdown-only" \
  --markdown >/dev/null

test -f "$tmp_dir/v4-preview/v4-preview.json"
test -f "$tmp_dir/v4-preview/v4-preview.md"
test -f "$tmp_dir/json-only/v4-preview.json"
test ! -f "$tmp_dir/json-only/v4-preview.md"
test -f "$tmp_dir/markdown-only/v4-preview.md"
test ! -f "$tmp_dir/markdown-only/v4-preview.json"

python3 -m json.tool "$tmp_dir/v4-preview/v4-preview.json" >/dev/null

grep -q '# ShipGuard V4 Preview' "$tmp_dir/v4-preview/v4-preview.md"
grep -q '## Result' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Schema Freeze' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Security Review' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Migration Plan' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Deprecation Policy' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Release Readiness' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Blocked Claims' "$tmp_dir/v4-preview/v4-preview.md"
grep -q 'Scope Boundary' "$tmp_dir/v4-preview/v4-preview.md"

grep -q '"tool": "shipguard v4 preview"' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"surface": "ShipGuard V4 Preview"' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"status": "pass"' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"productStage": "v4-preview-stabilization"' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"stableContract":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"schemaFreeze":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"securityReview":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"migrationPlan":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"deprecationPolicy":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"releaseReadiness":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"blockedClaims":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"scopeBoundary":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"resultUX":' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"frozenForPreview": true' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"frozenForV4Release": false' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"releaseClaim": "not-released"' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"shipguardOnly": true' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"privateAppsUsed": false' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/v4-preview/v4-preview.json"
grep -q '"mode": "ShipGuard product QA"' "$tmp_dir/v4-preview/v4-preview.json"

if grep -R -F -q "$repo_root" "$tmp_dir/v4-preview"; then
  echo "shareable v4 preview output must not include the local repo path" >&2
  exit 1
fi

python3 - "$tmp_dir/v4-preview/v4-preview.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["status"] == "pass"
assert report["schemaFreeze"]["frozenForPreview"] is True
assert report["schemaFreeze"]["frozenForV4Release"] is False
assert report["releaseReadiness"]["releaseClaim"] == "not-released"
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["scopeBoundary"]["targetAppsReadOnly"] is True
assert report["scopeBoundary"]["privateAppsUsed"] is False
assert report["scopeBoundary"]["doesNotPublishRelease"] is True
assert len(report["stableContract"]["frontDoorCommands"]) >= 5
assert len(report["schemaFreeze"]["schemas"]) >= 3
assert len(report["securityReview"]["requiredGates"]) >= 3
assert len(report["migrationPlan"]["steps"]) >= 4
assert len(report["deprecationPolicy"]["rules"]) >= 3
assert len(report["blockedClaims"]) >= 3
assert len(report["reportQualityQuestions"]) >= 3
assert "v4 schema" in report["resultUX"]["priorityAction"].lower() or "freeze" in report["resultUX"]["priorityAction"].lower()
PY

echo "v4 preview test passed"
