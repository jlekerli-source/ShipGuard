# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does Lean Debt make every shortcut marker visible with a ceiling and upgrade trigger?

## Marker Visibility Review

- All markers visible: `true`
- Visible marker rows: 2 of 2
- Rows with ceiling: 2
- Rows missing ceiling: 0
- Rows with upgrade trigger: 1
- Rows needing upgrade trigger: 1
- Rows with upgrade status: 2
- Omitted state unknown: `false`
- Policy: Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written.

| Status | Marker | Location | Ceiling | Upgrade Trigger |
| --- | --- | --- | --- | --- |
| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | one query shape | replace when repeated-key support is required |
| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | one release migration window | - |

## Rot-Risk Review

- Top risk location: Sources/SyntheticLeanDebt/LegacyPanel.swift:27
- Top risk reason: Missing upgrade trigger means this shortcut can survive beyond its intended window.
- High-risk rows: 0
- Review-risk rows: 1
- Tracked rows: 1
- Missing ceiling rows: 0
- Missing upgrade-trigger rows: 1
- Omitted by limit: 0
- Omitted risk unknown: `false`
- Coverage boundary: Rot-risk ranking is based on visible shortcut rows. When omittedByLimit is greater than zero, omitted markers may contain higher risk and must be surfaced by rerunning with a narrower scope or extending the ledger limit.
- Policy: Start with the highest-risk shortcut marker before opening source again: missing ceiling first, missing upgrade trigger second, tracked trigger watch third.

| Rank | Risk | Status | Marker | Location | Rot Reason | Next Action | Proof Guidance |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | review | needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | Missing upgrade trigger means this shortcut can survive beyond its intended window. | Add an upgrade trigger that tells the maintainer exactly when to replace or delete it. | Name the release, dependency, migration state, or repeated call-site signal that should trigger cleanup. |
| 2 | tracked | tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | Tracked shortcut should be reviewed when its upgrade trigger becomes true. | Watch the upgrade trigger: replace when repeated-key support is required | When the trigger is true, run call-site search plus the smallest focused validation before deleting or replacing it. |

## Shortcut Ledger

- Markers: 2; missing upgrade trigger: 1

| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |
| --- | --- | --- | --- | --- | --- |
| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | use the native query parser while this bridge handles one query shape. ceiling: one query shape. upgrade: replace when repeated-key support is required. | one query shape | replace when repeated-key support is required |
| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | keep the temporary compatibility panel during migration. ceiling: one release migration window. | one release migration window | - |

## Current Repo Boundary

- Shortcut markers are current-repo evidence only.
- Do not claim benchmark, line, token, cost, or time savings from marker counts.

## Benchmark Savings Boundary

- Per-repo savings claim: `not-computed`
- Evidence type: `shortcut-ledger-only`
- Reason: Lean Debt counts intentional shortcut markers and missing triggers; it has no untreated baseline for current-repo line, token, cost, or time savings.
- Do not claim current-repo line, token, cost, or time savings from shortcut marker counts.
- Do not treat shortcut marker counts as benchmark savings.
- Benchmark route: `shipguard lean gain --path <repo> --out <lean-gain-out> --shipguard-eval --shareable`
- Benchmark artifact: lean-gain.json and lean-gain.md
- Boundary: Benchmark direction is separate from this shortcut-ledger evidence and still does not measure this repo without a matched baseline.
