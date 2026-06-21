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
- Policy: Every intentional shortcut marker should be rendered as a row with location, summary, ceiling, upgrade-trigger status, and explicit missing-trigger state when the upgrade is not yet written.

| Status | Marker | Location | Ceiling | Upgrade Trigger |
| --- | --- | --- | --- | --- |
| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | one query shape | replace when repeated-key support is required |
| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | one release migration window | - |

## Shortcut Ledger

- Markers: 2; missing upgrade trigger: 1

| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |
| --- | --- | --- | --- | --- | --- |
| tracked | `shipguard-lean` | Sources/SyntheticLeanDebt/QueryBridge.swift:12 | use the native query parser while this bridge handles one query shape. ceiling: one query shape. upgrade: replace when repeated-key support is required. | one query shape | replace when repeated-key support is required |
| needs-trigger | `ponytail` | Sources/SyntheticLeanDebt/LegacyPanel.swift:27 | keep the temporary compatibility panel during migration. ceiling: one release migration window. | one release migration window | - |

## Current Repo Boundary

- Shortcut markers are current-repo evidence only.
- Do not claim benchmark, line, token, cost, or time savings from marker counts.
