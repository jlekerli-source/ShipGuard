#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard brand --help >/dev/null
./bin/shipguard ios brand --help >/dev/null
./bin/shipguard brand \
  --path . \
  --out "$tmp_dir/brand" \
  --strict >/dev/null

test -f "$tmp_dir/brand/ios-branding.md"
test -f "$tmp_dir/brand/ios-branding.json"
python3 -m json.tool "$tmp_dir/brand/ios-branding.json" >/dev/null

grep -q '# ShipGuard Brand Deck' "$tmp_dir/brand/ios-branding.md"
grep -q 'Naming Rules' "$tmp_dir/brand/ios-branding.md"
grep -q 'Product Places' "$tmp_dir/brand/ios-branding.md"
grep -q 'Surface Scheme' "$tmp_dir/brand/ios-branding.md"
grep -q 'Nitty-Gritty Call Signs' "$tmp_dir/brand/ios-branding.md"
grep -q 'Future Naming Contract' "$tmp_dir/brand/ios-branding.md"
grep -q 'Report Quality Questions' "$tmp_dir/brand/ios-branding.md"
grep -q 'Plain Purpose' "$tmp_dir/brand/ios-branding.md"
grep -q 'proof boundary' "$tmp_dir/brand/ios-branding.md"

grep -q '"tool": "shipguard brand"' "$tmp_dir/brand/ios-branding.json"
grep -q '"surface": "ShipGuard Brand Deck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"compatibilityCommands":' "$tmp_dir/brand/ios-branding.json"
grep -q '"shipguard ios brand"' "$tmp_dir/brand/ios-branding.json"
grep -q '"status": "pass"' "$tmp_dir/brand/ios-branding.json"
grep -q '"intent": "shipguard-product-qa"' "$tmp_dir/brand/ios-branding.json"
grep -q '"shipguardOnly": true' "$tmp_dir/brand/ios-branding.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/brand/ios-branding.json"
grep -q '"productPlaces":' "$tmp_dir/brand/ios-branding.json"
grep -q '"name": "ShipGuard ShipYard"' "$tmp_dir/brand/ios-branding.json"
grep -q 'ShipYard names the workspace experience' "$tmp_dir/brand/ios-branding.json"
grep -q '"surfaceCount": 57' "$tmp_dir/brand/ios-branding.json"
grep -q '"artifactCallsigns":' "$tmp_dir/brand/ios-branding.json"
grep -q '"callSign": "Deckhand Scripts"' "$tmp_dir/brand/ios-branding.json"
grep -q '"callSign": "Gauntlet Runs"' "$tmp_dir/brand/ios-branding.json"
grep -q '"callSign": "Engine Tapes"' "$tmp_dir/brand/ios-branding.json"
grep -q '"callSign": "Cargo Crates"' "$tmp_dir/brand/ios-branding.json"
grep -q '"callSign": "Docking Gear"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard brand"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard init"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard ios launchdeck"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard release-evidence"' "$tmp_dir/brand/ios-branding.json"
grep -q '"command": "shipguard next-goal"' "$tmp_dir/brand/ios-branding.json"
grep -q '"toneGuardrail":' "$tmp_dir/brand/ios-branding.json"
grep -q '"publicInterfacePolicy":' "$tmp_dir/brand/ios-branding.json"
grep -q '"reportQualityQuestions":' "$tmp_dir/brand/ios-branding.json"
grep -q 'Does every public ShipGuard surface have a branded name' "$tmp_dir/brand/ios-branding.json"
grep -q 'Does ShipGuard ShipYard appear as the workshop-level product place' "$tmp_dir/brand/ios-branding.json"

surface_names=(
  "ShipGuard Brand Deck"
  "ShipGuard StarterBay"
  "ShipGuard RigCheck"
  "ShipGuard RepoVitals"
  "ShipGuard WebScan"
  "ShipGuard WebForge"
  "ShipGuard ServiceRadar"
  "ShipGuard ServiceForge"
  "ShipGuard CommandLens"
  "ShipGuard CommandForge"
  "ShipGuard RuleHarbor"
  "ShipGuard RunScore"
  "ShipGuard TraceVault"
  "ShipGuard ReviewBeacon"
  "ShipGuard GateTower"
  "ShipGuard BriefBeacon"
  "ShipGuard CheckPilot"
  "ShipGuard AlertBeacon"
  "ShipGuard LinkSweep"
  "ShipGuard Tool Value Gauntlet"
  "ShipGuard DockCheck"
  "ShipGuard CargoScan"
  "ShipGuard BriefForge"
  "ShipGuard ProofVault"
  "ShipGuard LaunchDeck"
  "ShipGuard PulseRadar"
  "ShipGuard VibeCheck"
  "ShipGuard UpgradeForge"
  "ShipGuard SignalLens"
  "ShipGuard ModelDock"
  "ShipGuard SourceScout"
  "ShipGuard SpecForge"
  "ShipGuard QualityRadar"
  "ShipGuard MirrorPort"
  "ShipGuard Devspace Bridge"
  "ShipGuard BridgeWatch"
  "ShipGuard TapCompass"
  "ShipGuard HandoffRail"
  "ShipGuard RedactionBay"
  "ShipGuard EvalArena"
  "ShipGuard DemoDock"
  "ShipGuard GoalEngine"
  "ShipGuard ReleaseDock"
  "ShipGuard ManifestForge"
  "ShipGuard ReleaseAtlas"
  "ShipGuard ReplayRig"
  "ShipGuard TrustStamp"
  "ShipGuard ConsumerDock"
  "ShipGuard DiffLens"
  "ShipGuard EvidenceHarbor"
  "ShipGuard AutopsyLab"
  "ShipGuard ArenaBench"
  "ShipGuard PluginRadar"
  "ShipGuard ScoreTower"
  "ShipGuard SelfScan"
  "ShipGuard NextRail"
  "ShipGuard VersionBeacon"
)

for surface_name in "${surface_names[@]}"; do
  grep -q "$surface_name" "$tmp_dir/brand/ios-branding.json"
  grep -q "$surface_name" "$tmp_dir/brand/ios-branding.md"
done

for call_sign in "Deckhand Scripts" "Sonar Modules" "Gauntlet Runs" "Blackbox Receipts" "Bridge Notes" "Engine Tapes" "Cargo Crates" "Docking Gear"; do
  grep -q "$call_sign" "$tmp_dir/brand/ios-branding.md"
done

json_stdout="$(./bin/shipguard brand --path . --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard brand"'
printf '%s\n' "$json_stdout" | grep -q '"surface": "ShipGuard Brand Deck"'

compat_stdout="$(./bin/shipguard ios brand --path . --json)"
printf '%s\n' "$compat_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$compat_stdout" | grep -q '"tool": "shipguard brand"'
printf '%s\n' "$compat_stdout" | grep -q '"surface": "ShipGuard Brand Deck"'

if rg -n 'Shipyard|Shipcard|Illumify|InweFi|Build iOS Apps bridge|Build iOS Apps front door' \
  README.md docs/cli.md docs/command-matrix.md docs/ios-shipguard.md docs/shipguard-naming.md \
  plugins/ios-shipguard/skills/ios-shipguard/SKILL.md \
  plugins/ios-shipguard/skills/ios-shipguard/references/modes.md >/dev/null; then
  echo "active docs or skill guidance contain stale ShipGuard naming" >&2
  exit 1
fi

echo "ios branding tests passed"
