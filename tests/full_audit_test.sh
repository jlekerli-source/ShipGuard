#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard full-audit --help >/dev/null

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/plan" \
  --profile release \
  --plan-only \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/plan/shipguard-full-audit.json"
test -f "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '"tool": "shipguard full-audit"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"status": "review"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"resultUX":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"proofSource":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"nextCommand":' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"planned": 14' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"stageId": "release-proof"' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"doesNotPush": true' "$tmp_dir/plan/shipguard-full-audit.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/plan/shipguard-full-audit.json"
python3 - <<'PY' "$tmp_dir/plan/shipguard-full-audit.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
result = data["resultUX"]
if result["status"] != "review":
    raise SystemExit(result)
if "Plan-only report created" not in result["nextActionSummary"]:
    raise SystemExit(result)
next_command = result["nextCommand"]
for expected in [
    "--profile release",
    "--include-install",
    "--release-url <release-url>",
    "--version <version>",
    "--tag <tag>",
    "--commit <commit-sha>",
    "--ci-run-url <ci-run-url>",
]:
    if expected not in next_command:
        raise SystemExit(next_command)
if data["efficiency"]["executeCommand"] != next_command:
    raise SystemExit(data["efficiency"])
packet = data.get("releasePacketPlan") or {}
if packet.get("status") != "review":
    raise SystemExit(packet)
if packet.get("selectedStages") != ["package-release", "plugin-status", "install-refresh", "ci-proof", "release-proof"]:
    raise SystemExit(packet)
if packet.get("missingMetadataFields") != ["release_url", "version", "tag", "commit", "ci_run_url"]:
    raise SystemExit(packet)
if packet.get("nextCommand") != next_command:
    raise SystemExit(packet)
boundary = packet.get("proofBoundary") or {}
for key in ["planOnlyCountsAsReleaseProof", "sourceOnlyCountsAsStableV4Proof", "publishesGitHubRelease", "pushesMain"]:
    if boundary.get(key) is not False:
        raise SystemExit(boundary)
if "Full Audit release-packet planning does not publish a GitHub release." not in packet.get("nonClaims", []):
    raise SystemExit(packet)
source = data.get("slashHandoffSource") or {}
if source.get("status") != "loaded" or source.get("sourcePath") != "NEXT_GOAL.md":
    raise SystemExit(source)
proof = data.get("slashHandoffProof") or {}
if proof.get("status") != "pass":
    raise SystemExit(proof)
if proof.get("sourcePath") != "NEXT_GOAL.md" or proof.get("selectedSection") != "following":
    raise SystemExit(proof)
if proof.get("copyReadyPlan") is not True or proof.get("copyReadyGoal") is not True:
    raise SystemExit(proof)
if proof.get("completionReceiptPresent") is not True:
    raise SystemExit(proof)
if proof.get("versionLineageStatus") != "review":
    raise SystemExit(proof)
for key in ["nextGoalFileRequired", "fallbackIsReviewOnly", "doesNotMarkGoalComplete", "doesNotPublishRelease"]:
    if (proof.get("proofBoundary") or {}).get(key) is not True:
        raise SystemExit(proof)
if not data.get("slashPlan", "").startswith("/plan "):
    raise SystemExit(data.get("slashPlan"))
if not data.get("slashGoal", "").startswith("/goal "):
    raise SystemExit(data.get("slashGoal"))
if "v3.132.0 v4 Product Release Stabilization" in data.get("slashPlan", "") + data.get("slashGoal", ""):
    raise SystemExit("stale full-audit slash handoff survived")
PY
grep -q 'ShipGuard Full Audit' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '## Result' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Proof source:' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Slow Lanes' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Execution Commands' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '| Stage | Status | Command |' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Release Packet Plan' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Missing metadata: `release_url, version, tag, commit, ci_run_url`' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Plan-only output proves route shape only, not completed release proof.' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q '<shipguard-repo>/bin/shipguard version' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'git diff --check' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Slash Handoff Source' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Source path: `NEXT_GOAL.md`' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Slash Handoff Proof' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Selected section: `following`' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Completion receipt present: true' "$tmp_dir/plan/shipguard-full-audit.md"
grep -q 'Copy-ready plan/goal: true/true' "$tmp_dir/plan/shipguard-full-audit.md"
if grep -q 'v3.132.0 v4 Product Release Stabilization' "$tmp_dir/plan/shipguard-full-audit.md"; then
  echo "full-audit output should not carry stale v3.132 slash handoff text" >&2
  exit 1
fi
if grep -q "$repo_root" "$tmp_dir/plan/shipguard-full-audit.json" "$tmp_dir/plan/shipguard-full-audit.md"; then
  echo "shareable full-audit output leaked local repo path" >&2
  exit 1
fi
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/plan" \
  --out "$tmp_dir/plan-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/plan-quality/ios-report-quality.json"
grep -q '"reportCount": 1' "$tmp_dir/plan-quality/ios-report-quality.json"
if grep -q 'report-tool-missing' "$tmp_dir/plan-quality/ios-report-quality.json"; then
  echo "report-quality should not treat full-audit stage receipts as standalone reports" >&2
  exit 1
fi

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/mini" \
  --stage version \
  --stage py-compile \
  --stage docs-check \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/mini/shipguard-full-audit.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
if data["status"] != "pass":
    raise SystemExit(data)
if data["stageStatusSummary"] != {"pass": 3}:
    raise SystemExit(data["stageStatusSummary"])
if data["efficiency"]["executedStages"] != 3:
    raise SystemExit(data["efficiency"])
if data["scopeBoundary"]["targetAppsReadOnly"] is not True:
    raise SystemExit(data["scopeBoundary"])
stage_ids = [stage["stageId"] for stage in data["stages"]]
if stage_ids != ["version", "py-compile", "docs-check"]:
    raise SystemExit(stage_ids)
if any(stage["durationSeconds"] < 0 for stage in data["stages"]):
    raise SystemExit(data["stages"])
if not data["reportQualityQuestions"]:
    raise SystemExit("missing report quality questions")
if not data.get("resultUX", {}).get("verdict", "").startswith("PASS:"):
    raise SystemExit(data.get("resultUX"))
PY

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/release-proof-manual" \
  --stage release-proof \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/release-proof-manual/shipguard-full-audit.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
if data["status"] != "review":
    raise SystemExit(data)
if data["stageStatusSummary"] != {"manual-required": 1}:
    raise SystemExit(data["stageStatusSummary"])
stage = data["stages"][0]
if stage["stageId"] != "release-proof" or stage["status"] != "manual-required":
    raise SystemExit(stage)
next_command = data["resultUX"]["nextCommand"]
for expected in [
    "--stage release-proof",
    "--release-url <release-url>",
    "--version <version>",
    "--tag <tag>",
    "--commit <commit-sha>",
    "--ci-run-url <ci-run-url>",
]:
    if expected not in next_command:
        raise SystemExit(next_command)
PY

./bin/shipguard full-audit \
  --path . \
  --out "$tmp_dir/mini" \
  --stage version \
  --stage py-compile \
  --stage docs-check \
  --resume \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir/mini/shipguard-full-audit.json"
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
statuses = {stage["status"] for stage in data["stages"]}
if statuses != {"skipped"}:
    raise SystemExit(data["stages"])
if data["stageStatusSummary"] != {"skipped": 3}:
    raise SystemExit(data["stageStatusSummary"])
if not all(stage.get("skippedReason") == "resume reused prior passing receipt" for stage in data["stages"]):
    raise SystemExit(data["stages"])
PY

json_stdout="$(./bin/shipguard full-audit --path . --out "$tmp_dir/json" --stage version --plan-only --json)"
grep -q '"tool": "shipguard full-audit"' <<<"$json_stdout"
grep -q '"status": "review"' <<<"$json_stdout"
grep -q -- '--stage version' <<<"$json_stdout"
markdown_stdout="$(./bin/shipguard full-audit --path . --out "$tmp_dir/md" --stage version --plan-only --markdown)"
grep -q '# ShipGuard Full Audit' <<<"$markdown_stdout"

echo "full audit tests passed"
