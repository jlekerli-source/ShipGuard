#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard pilot-bench --help >/dev/null

./bin/shipguard pilot-bench \
  --trace fixtures/external-pilot-verdict-bench \
  --out "$tmp_dir/pilot-bench" \
  --shareable >/dev/null

test -f "$tmp_dir/pilot-bench/pilot-bench.json"
test -f "$tmp_dir/pilot-bench/pilot-bench.md"
python3 -m json.tool "$tmp_dir/pilot-bench/pilot-bench.json" >/dev/null
grep -q '"tool": "shipguard pilot-bench"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"surface": "ShipGuard PilotBench"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"status": "pass"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"traceCount": 2' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"averageVerdictScore": 100' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"ownerDetection"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"requiredProofCoverage"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"claimChecking"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"firstUsefulVerdictTime"' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"shipguardOnly": true' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/pilot-bench/pilot-bench.json"
grep -q '# ShipGuard PilotBench' "$tmp_dir/pilot-bench/pilot-bench.md"
grep -q 'Private trace policy' "$tmp_dir/pilot-bench/pilot-bench.md"
if grep -R -q '/Users/' "$tmp_dir/pilot-bench"; then
  echo "shareable PilotBench output leaked a local path" >&2
  exit 1
fi

python3 - <<'PY' "$tmp_dir/pilot-bench/pilot-bench.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
trace_ids = {item["traceId"] for item in data["traces"]}
assert trace_ids == {"notification-permission-review", "protected-scope-overclaim"}, trace_ids
for trace in data["traces"]:
    assert trace["status"] == "pass", trace
    assert trace["score"] == 100, trace
    assert trace["expectationsPassed"] is True, trace
    dimensions = {item["id"]: item for item in trace["dimensions"]}
    for key in ("ownerDetection", "scopePolicy", "requiredProofCoverage", "claimChecking", "redaction", "nextActionCompleteness", "falsePositiveRate", "firstUsefulVerdictTime"):
        assert dimensions[key]["status"] == "pass", (key, dimensions[key])
PY

weak_trace="$tmp_dir/weak-trace.json"
cat > "$weak_trace" <<'JSON'
{
  "traceId": "weak-private-trace",
  "source": "synthetic weak trace",
  "labels": {
    "expectedBenchStatus": "blocked",
    "expectedFindingRuleIds": [
      "pilot-ownerDetection",
      "pilot-requiredProofCoverage",
      "pilot-redaction",
      "pilot-nextActionCompleteness"
    ],
    "expectedForbiddenPatterns": [".github/workflows/**"],
    "expectedOwnerPatterns": ["Sources/DemoShipGuardApp/**"],
    "expectedNextActionContains": ["structured validation receipt"],
    "requiredProofScopes": ["permission-state"],
    "unsupportedClaims": ["fully verified"],
    "firstUsefulVerdictMaxEvents": 1
  },
  "task": {
    "tool": "shipguard prepare",
    "authorizedFiles": [],
    "protectedBoundaries": [],
    "scopeBoundary": {"shipguardOnly": true, "targetAppsReadOnly": true}
  },
  "verdict": {
    "tool": "shipguard verify",
    "status": "pass",
    "nextAction": {
      "command": "done"
    },
    "claimChecks": {
      "rejectedClaims": []
    },
    "notes": "private local path /Users/example/Ringly leaked"
  },
  "events": []
}
JSON

set +e
./bin/shipguard pilot-bench \
  --trace "$weak_trace" \
  --out "$tmp_dir/weak-pilot-bench" \
  --shareable >/dev/null
weak_status=$?
set -e
if [[ "$weak_status" -eq 0 ]]; then
  echo "weak pilot trace should block" >&2
  exit 1
fi
grep -q '"status": "blocked"' "$tmp_dir/weak-pilot-bench/pilot-bench.json"
grep -q '"ruleId": "pilot-ownerDetection"' "$tmp_dir/weak-pilot-bench/pilot-bench.json"
grep -q '"ruleId": "pilot-requiredProofCoverage"' "$tmp_dir/weak-pilot-bench/pilot-bench.json"
grep -q '"ruleId": "pilot-redaction"' "$tmp_dir/weak-pilot-bench/pilot-bench.json"
grep -q '"ruleId": "pilot-nextActionCompleteness"' "$tmp_dir/weak-pilot-bench/pilot-bench.json"
grep -q 'Fixture Candidates' "$tmp_dir/weak-pilot-bench/pilot-bench.md"

echo "ShipGuard PilotBench tests passed"
