#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios external-audit --help >/dev/null

mkdir -p "$tmp_dir/spec-kit/workflows/speckit" "$tmp_dir/spec-kit/templates/commands"
cat > "$tmp_dir/spec-kit/README.md" <<'EOF_SPEC_README'
# Spec Kit

Spec-driven development with speckit commands for constitution, specify, clarify, checklist, plan, tasks, analyze, and implement.
EOF_SPEC_README
cat > "$tmp_dir/spec-kit/pyproject.toml" <<'EOF_SPEC_PYPROJECT'
[project]
name = "specify-cli"
version = "0.11.2.dev0"
license = "MIT"
EOF_SPEC_PYPROJECT
cat > "$tmp_dir/spec-kit/LICENSE" <<'EOF_SPEC_LICENSE'
MIT License
EOF_SPEC_LICENSE
cat > "$tmp_dir/spec-kit/workflows/speckit/workflow.yml" <<'EOF_SPEC_WORKFLOW'
workflow:
  id: speckit
steps:
  - id: specify
  - id: plan
  - id: tasks
  - id: implement
EOF_SPEC_WORKFLOW
cat > "$tmp_dir/spec-kit/templates/commands/checklist.md" <<'EOF_SPEC_CHECKLIST'
# Checklist Purpose: Unit Tests for English
Check requirements quality, not implementation behavior.
EOF_SPEC_CHECKLIST

mkdir -p "$tmp_dir/codexpro/src"
cat > "$tmp_dir/codexpro/README.md" <<'EOF_CODEXPRO_README'
# CodexPro

CodexPro lets ChatGPT Developer Mode inspect local repo context with .ai-bridge handoff mode, tool modes, and codexpro_token protected URLs.
EOF_CODEXPRO_README
cat > "$tmp_dir/codexpro/package.json" <<'EOF_CODEXPRO_PACKAGE'
{
  "name": "codexpro",
  "version": "0.28.5",
  "license": "MIT"
}
EOF_CODEXPRO_PACKAGE
cat > "$tmp_dir/codexpro/SECURITY.md" <<'EOF_CODEXPRO_SECURITY'
# Security
Use CODEXPRO_HTTP_TOKEN, allowed roots, blocked globs, and never expose public tunnels without auth.
EOF_CODEXPRO_SECURITY
cat > "$tmp_dir/codexpro/LICENSE" <<'EOF_CODEXPRO_LICENSE'
MIT License
EOF_CODEXPRO_LICENSE

mkdir -p "$tmp_dir/design-motion-principles/references"
cat > "$tmp_dir/design-motion-principles/SKILL.md" <<'EOF_MOTION_SKILL'
# Design Motion Principles

Motion and interaction design expert using The Frequency Gate, Emil Kowalski, Jakub Krehel, Jhey Tompkins, prefers-reduced-motion, Motion Gap Analysis, and AI-Slop Motion Patterns.
This file intentionally talks about easing several times, but it is not Expo and should not match EAS inside easing.
EOF_MOTION_SKILL

./bin/shipguard ios external-audit \
  --path . \
  --source-path "$tmp_dir/spec-kit" \
  --source-path "$tmp_dir/codexpro" \
  --source-path "$tmp_dir/design-motion-principles" \
  --source-url https://github.com/expo/expo \
  --source-url https://x.com/example/status/1234567890 \
  --out "$tmp_dir/audit" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/audit/ios-external-audit.json"
test -f "$tmp_dir/audit/ios-external-audit.md"
test -f "$tmp_dir/audit/replacement-ledger.md"
python3 -m json.tool "$tmp_dir/audit/ios-external-audit.json" >/dev/null
grep -q '"tool": "shipguard ios external-audit"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"mode": "shareable"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"shipguardOnly": true' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"displayName": "GitHub Spec Kit"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"displayName": "CodexPro"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"displayName": "Design Motion Principles"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"displayName": "Expo"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"sourceKey": "design-motion-principles"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"capabilityId": "motion-frequency-context-gate"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"capabilityId": "motion-anti-slop-audit"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"decision": "replace-weaker-guidance"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"decision": "extend-native"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"decision": "defer-with-native-plan"' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"replacementLedger":' "$tmp_dir/audit/ios-external-audit.json"
grep -q '"implementationBacklog":' "$tmp_dir/audit/ios-external-audit.json"
grep -q 'Do not vendor external source code into ShipGuard' "$tmp_dir/audit/ios-external-audit.json"
grep -q '# iOS ShipGuard External Source Audit' "$tmp_dir/audit/ios-external-audit.md"
grep -q '# Native External Workflow Replacement Ledger' "$tmp_dir/audit/replacement-ledger.md"
grep -q 'A source is not considered integrated until its capability has a decision' "$tmp_dir/audit/replacement-ledger.md"

if grep -R -F -q "$tmp_dir" "$tmp_dir/audit"; then
  echo "shareable external-audit output must not include local absolute temp paths" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/audit" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/quality/ios-report-quality.json"
grep -q 'shipguard ios external-audit' "$tmp_dir/quality/ios-report-quality.md"
grep -q 'Which deferred external capability should become a public fixture before ShipGuard adopts it?' "$tmp_dir/quality/ios-report-quality.json"

json_stdout="$(./bin/shipguard ios external-audit --path . --json)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios external-audit"'

echo "ios external-audit tests passed"
