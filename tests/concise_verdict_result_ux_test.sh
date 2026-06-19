#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard value-gauntlet --path . --out "$tmp_dir/gauntlet" >/dev/null
./bin/shipguard full-audit --path . --out "$tmp_dir/full" --profile quick --plan-only --shipguard-eval --shareable >/dev/null
./bin/shipguard ios design --path fixtures/demo-ios-repo --out "$tmp_dir/design" --shipguard-eval --shareable >/dev/null
./bin/shipguard ios performance --path fixtures/demo-ios-repo --out "$tmp_dir/performance" --shipguard-eval --shareable >/dev/null

mkdir -p "$tmp_dir/release/proof" "$tmp_dir/release/attestation"
cat > "$tmp_dir/release/proof/release-manifest.json" <<'JSON'
{
  "schema_version": "1.0",
  "version": "3.126.0",
  "tag": "v3.126.0",
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "artifact": {
    "name": "shipguard-v3.126.0.tar.gz",
    "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "proofs": {
    "release_url": "https://github.com/jlekerli-source/ShipGuard/releases/tag/v3.126.0",
    "ci_run_url": "https://github.com/jlekerli-source/ShipGuard/actions/runs/1"
  }
}
JSON
cat > "$tmp_dir/release/attestation/attestation-badge.json" <<'JSON'
{"status": "pass"}
JSON

./bin/shipguard inspect \
  --path . \
  --out "$tmp_dir/inspect" \
  --value-gauntlet "$tmp_dir/gauntlet" \
  --full-audit "$tmp_dir/full" \
  --release-assets "$tmp_dir/release" \
  --shipguard-eval \
  --shareable >/dev/null

python3 - <<'PY' "$tmp_dir" "$repo_root"
import json
import pathlib
import sys

tmp = pathlib.Path(sys.argv[1])
repo_root = sys.argv[2]
home = str(pathlib.Path.home())
pairs = [
    ("value-gauntlet", tmp / "gauntlet" / "tool-value-gauntlet.json", tmp / "gauntlet" / "tool-value-gauntlet.md"),
    ("full-audit", tmp / "full" / "shipguard-full-audit.json", tmp / "full" / "shipguard-full-audit.md"),
    ("ios-design", tmp / "design" / "ios-design.json", tmp / "design" / "ios-design.md"),
    ("ios-performance", tmp / "performance" / "ios-performance.json", tmp / "performance" / "ios-performance.md"),
    ("inspect", tmp / "inspect" / "shipguard-inspect.json", tmp / "inspect" / "shipguard-inspect.md"),
]
required = {"status", "verdict", "proofSource", "whyItMatters", "nextCommand", "nextActionSummary"}
for name, json_path, md_path in pairs:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    result = data.get("resultUX") or {}
    missing = sorted(key for key in required if not str(result.get(key) or "").strip())
    if missing:
        raise SystemExit(f"{name} resultUX missing {missing}: {result!r}")
    if result["status"] not in {"pass", "review", "blocked"}:
        raise SystemExit(f"{name} has non-standard result status: {result!r}")
    if not result["verdict"].startswith(result["status"].upper() + ": "):
        raise SystemExit(f"{name} verdict should start with normalized status: {result!r}")
    markdown = md_path.read_text(encoding="utf-8")
    for phrase in ("## Result", "Verdict:", "Proof source:", "Why it matters:", "Next command:"):
        if phrase not in markdown:
            raise SystemExit(f"{name} markdown missing {phrase!r}")
    if name != "value-gauntlet" and (repo_root in markdown or repo_root in json_path.read_text(encoding="utf-8")):
        raise SystemExit(f"{name} shareable output leaked repo path")
    if name != "value-gauntlet" and (home in markdown or home in json_path.read_text(encoding="utf-8")):
        raise SystemExit(f"{name} shareable output leaked home path")

gauntlet = json.loads((tmp / "gauntlet" / "tool-value-gauntlet.json").read_text(encoding="utf-8"))
receipts = gauntlet.get("conciseVerdictResultUXReceipts") or {}
if receipts.get("status") != "pass":
    raise SystemExit(f"concise result UX receipts should pass: {receipts!r}")
if receipts.get("receiptCount") != 1 or receipts.get("passedReceiptCount") != 1 or receipts.get("commandCount") != 4:
    raise SystemExit(f"unexpected concise result UX receipt counts: {receipts!r}")
answer = ((gauntlet.get("lowestValueSurfaceProbe") or {}).get("answer") or {})
if answer.get("identifier") != "shipguard v4-preview-stabilization":
    raise SystemExit(f"passing external benchmark v2 receipts should escalate to v4 preview stabilization: {answer!r}")
missing = answer.get("missingDepthSignals") or []
if "runtimeConciseVerdictResultUX" in missing:
    raise SystemExit(f"concise result UX should no longer be missing: {answer!r}")
if "runtimeExternalBenchmarkV2" in missing:
    raise SystemExit(f"external benchmark v2 should no longer be missing: {answer!r}")
if "runtimeV4PreviewStabilization" not in missing:
    raise SystemExit(f"v4 preview stabilization should be the next explicit gap: {answer!r}")
PY

grep -q 'Concise Verdict Result UX Receipts' "$tmp_dir/gauntlet/tool-value-gauntlet.md"

echo "concise verdict result UX tests passed"
