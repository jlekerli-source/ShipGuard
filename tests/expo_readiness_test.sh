#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

python3 -m py_compile scripts/expo_readiness.py

mkdir -p "$tmp_dir/runtime-evidence"
cat > "$tmp_dir/runtime-evidence/expo-doctor.log" <<'EOF'
npx expo-doctor
No issues found.
EOF
cat > "$tmp_dir/runtime-evidence/eas-build-timing.log" <<'EOF'
EAS build duration: 4m 12s
queue: 18s
EOF
touch "$tmp_dir/runtime-evidence/preview-screenshot.png"

./bin/shipguard expo readiness \
  --path fixtures/expo-sdk56-demo \
  --out "$tmp_dir/expo-readiness" \
  --runtime-evidence "$tmp_dir/runtime-evidence" \
  --shareable \
  --shipguard-eval >/dev/null

test -f "$tmp_dir/expo-readiness/expo-readiness.json"
test -f "$tmp_dir/expo-readiness/expo-readiness.md"
grep -q '"tool": "shipguard expo readiness"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"surface": "ShipGuard ExpoDeck"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"releaseDate": "2026-05-21"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "expo-sdk-behind-target"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "expo-router-react-navigation-pairing"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "expo-vector-icons-deprecation"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "expo-ui-migration-opportunity"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "expo-agent-scaffolding-incomplete"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"ruleId": "professional-design-evidence-thin"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"professionalDesignPrinciples"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"runtimeEvidence"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"expoDoctor"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"easTiming"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"screenshot"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"preview"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"contrast"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"unity"' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q 'how-to-apply-professional-design-principles-in-ai-app-development' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"doesNotRunExpoCommands": true' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q '"improveShipGuardNotTargetApp": true' "$tmp_dir/expo-readiness/expo-readiness.json"
grep -q 'ShipGuard ExpoDeck' "$tmp_dir/expo-readiness/expo-readiness.md"
grep -q 'Professional Design Principles' "$tmp_dir/expo-readiness/expo-readiness.md"
grep -q 'Runtime Evidence' "$tmp_dir/expo-readiness/expo-readiness.md"
grep -q 'npx expo-doctor' "$tmp_dir/expo-readiness/expo-readiness.md"
grep -q 'EAS build timing' "$tmp_dir/expo-readiness/expo-readiness.json"

python3 - <<'PY' "$tmp_dir/expo-readiness/expo-readiness.json"
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["status"] == "review", data["status"]
signals = data["projectSignals"]
assert signals["isExpoProject"] is True, signals
assert signals["expoMajor"] == 55, signals
assert signals["usesExpoRouter"] is True, signals
assert signals["usesReactNavigationPackages"] is True, signals
assert signals["usesEAS"] is True, signals
opportunities = {item["id"]: item["status"] for item in data["opportunities"]}
assert opportunities["expo-ui-stable"] == "candidate", opportunities
assert opportunities["precompiled-builds"] == "requires-sdk56", opportunities
assert opportunities["ai-agent-scaffolding"] == "incomplete", opportunities
assert data["shareability"]["localAbsolutePathsIncluded"] is False, data["shareability"]
assert data["scanScope"]["doesNotRunNpmOrExpo"] is True, data["scanScope"]
runtime = data["runtimeEvidence"]
assert runtime["provided"] is True, runtime
assert runtime["fileCount"] == 3, runtime
assert "expoDoctor" in runtime["categories"], runtime
assert "easTiming" in runtime["categories"], runtime
assert "screenshot" in runtime["categories"], runtime
assert "preview" in runtime["categories"], runtime
assert runtime["boundary"].startswith("ShipGuard reads provided artifacts only"), runtime
design = data["professionalDesignPrinciples"]
assert design["principles"] == [
    "contrast",
    "hierarchy",
    "alignment",
    "proximity",
    "repetition",
    "balance",
    "white-space",
    "unity",
], design
assert design["signals"]["styleDeclarationCount"] == 0, design
assert any(item["ruleId"] == "professional-design-evidence-thin" for item in data["findings"]), data["findings"]
PY

./bin/shipguard expo readiness --help >/dev/null

echo "expo readiness tests passed"
