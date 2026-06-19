#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard v4 schema-freeze --help >/dev/null
./bin/shipguard v4 schema-freeze \
  --path . \
  --out "$tmp_dir/v4-schema-freeze" \
  --shipguard-eval \
  --shareable >/dev/null
./bin/shipguard v4 schema-freeze \
  --path . \
  --out "$tmp_dir/json-only" \
  --json >/dev/null
./bin/shipguard v4 schema-freeze \
  --path . \
  --out "$tmp_dir/markdown-only" \
  --markdown >/dev/null

test -f "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
test -f "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
test -f "$tmp_dir/json-only/v4-schema-freeze.json"
test ! -f "$tmp_dir/json-only/v4-schema-freeze.md"
test -f "$tmp_dir/markdown-only/v4-schema-freeze.md"
test ! -f "$tmp_dir/markdown-only/v4-schema-freeze.json"

python3 -m json.tool "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json" >/dev/null

grep -q '# ShipGuard V4 Schema Freeze' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q '## Result' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Schema Registry' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Compatibility Policy' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Compatibility Fixtures' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Migration Checks' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Changelog Policy' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Deprecation Policy' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Release Readiness' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Blocked Claims' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"
grep -q 'Scope Boundary' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.md"

grep -q '"tool": "shipguard v4 schema-freeze"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"surface": "ShipGuard V4 Schema Freeze"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"status": "pass"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"productStage": "v4-schema-freeze"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"schemaRegistry":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"compatibilityPolicy":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"compatibilityFixtures":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"migrationChecks":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"changelogPolicy":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"deprecationPolicy":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"releaseReadiness":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"blockedClaims":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"scopeBoundary":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"resultUX":' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"frozenForV4Release": true' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"releaseClaim": "not-released"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"shipguardOnly": true' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"privateAppsUsed": false' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"
grep -q '"mode": "ShipGuard product QA"' "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json"

if grep -R -F -q "$repo_root" "$tmp_dir/v4-schema-freeze"; then
  echo "shareable v4 schema-freeze output must not include the local repo path" >&2
  exit 1
fi

python3 - "$tmp_dir/v4-schema-freeze/v4-schema-freeze.json" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["status"] == "pass"
assert report["productStage"] == "v4-schema-freeze"
assert report["compatibilityPolicy"]["frozenForV4Release"] is True
assert report["releaseReadiness"]["frozenForV4Release"] is True
assert report["releaseReadiness"]["releaseClaim"] == "not-released"
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["scopeBoundary"]["targetAppsReadOnly"] is True
assert report["scopeBoundary"]["privateAppsUsed"] is False
assert report["scopeBoundary"]["doesNotPublishRelease"] is True
assert len(report["schemaRegistry"]) >= 4
assert len(report["compatibilityPolicy"]["rules"]) >= 4
assert len(report["compatibilityFixtures"]) >= 3
assert len(report["migrationChecks"]) >= 4
assert len(report["changelogPolicy"]["requiredFor"]) >= 4
assert len(report["deprecationPolicy"]["rules"]) >= 3
assert len(report["blockedClaims"]) >= 4
assert len(report["reportQualityQuestions"]) >= 4
assert "release-candidate" in report["resultUX"]["priorityAction"].lower()
PY

echo "v4 schema-freeze test passed"
