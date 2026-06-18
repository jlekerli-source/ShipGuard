#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios brand --help >/dev/null
./bin/shipguard ios brand \
  --path . \
  --out "$tmp_dir/brand" \
  --strict >/dev/null

test -f "$tmp_dir/brand/ios-branding.md"
test -f "$tmp_dir/brand/ios-branding.json"
python3 -m json.tool "$tmp_dir/brand/ios-branding.json" >/dev/null

grep -q '# ShipGuard Brand Deck' "$tmp_dir/brand/ios-branding.md"
grep -q 'Naming Rules' "$tmp_dir/brand/ios-branding.md"
grep -q 'Surface Scheme' "$tmp_dir/brand/ios-branding.md"
grep -q 'Future Naming Contract' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard LaunchDeck' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard PulseRadar' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard VibeCheck' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard UpgradeForge' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard SourceScout' "$tmp_dir/brand/ios-branding.md"
grep -q 'ShipGuard ReleaseDock' "$tmp_dir/brand/ios-branding.md"
grep -q 'Plain Purpose' "$tmp_dir/brand/ios-branding.md"
grep -q 'proof boundary' "$tmp_dir/brand/ios-branding.md"

grep -q '"tool": "shipguard ios brand"' "$tmp_dir/brand/ios-branding.json"
grep -q '"status": "pass"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceCount": 22' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard Brand Deck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard DockCheck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard CargoScan"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard BriefForge"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard ProofVault"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard LaunchDeck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard PulseRadar"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard VibeCheck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard UpgradeForge"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard SignalLens"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard ModelDock"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard SourceScout"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard SpecForge"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard QualityRadar"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard MirrorPort"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard Devspace Bridge"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard RedactionBay"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard EvalArena"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard GoalEngine"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard ReleaseDock"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard AutopsyLab"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceName": "ShipGuard ArenaBench"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard ios launchdeck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard ios performance"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard ios design"' "$tmp_dir/brand/ios-branding.json"
grep -q '"toneGuardrail":' "$tmp_dir/brand/ios-branding.json"
grep -q '"publicInterfacePolicy":' "$tmp_dir/brand/ios-branding.json"

json_stdout="$(./bin/shipguard ios brand --path . --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios brand"'

if rg -n 'Shipyard|Shipcard|Illumify|InweFi|Build iOS Apps bridge|Build iOS Apps front door' \
  README.md docs/cli.md docs/command-matrix.md docs/ios-shipguard.md docs/shipguard-naming.md \
  plugins/ios-shipguard/skills/ios-shipguard/SKILL.md \
  plugins/ios-shipguard/skills/ios-shipguard/references/modes.md >/dev/null; then
  echo "active docs or skill guidance contain stale ShipGuard naming" >&2
  exit 1
fi

echo "ios branding tests passed"
