# Synthetic Lean Deck Shortcut-Ledger Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?

## Behavior Gates

| Gate | Status | Policy |
| --- | --- | --- |
| Adapter boundary | policy | Thin plugin, hook, MCP, and agent-host adapters can be the product boundary; keep them unless host registration proof says they are redundant. |
| Hardware calibration | available | Hardware, sensors, clocks, timing, and physical devices need calibration or tuning proof before simplification. |
| Requested explanation | policy | Explicitly requested reports, walkthroughs, phase notes, and rationale are not clutter. |
| One runnable check | enforced-in-lean-review | Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony. |
| Shortcut debt | review | Every intentional shortcut needs a ceiling and upgrade trigger. |
| Gain honesty | available-in-lean-gain | Benchmark impact is not a current-repo savings claim without a matched baseline. |

## Lean Debt Ledger

- Markers: 2
- Missing upgrade trigger: 1
- Omitted by limit: 0

| Status | Marker | Location | Shortcut | Ceiling | Upgrade Trigger |
| --- | --- | --- | --- | --- | --- |
| tracked | `shipguard-lean` | Sources/CompactQueryParser.swift:12 | use the native parser here. ceiling: only one query string shape. upgrade: replace when repeated-key support is required. | only one query string shape | replace when repeated-key support is required |
| needs-trigger | `shipguard-lean` | Sources/FastPreviewLoader.swift:27 | cache the first fixture load while the preview dataset is tiny. ceiling: preview data only. | preview data only | - |

## Shortcut Decisions

| Lane | Location | Status | Why |
| --- | --- | --- | --- |
| Compact parser | Sources/CompactQueryParser.swift:12 | tracked | The shortcut has both a ceiling and an upgrade trigger, so the deferral is auditable. |
| Preview loader | Sources/FastPreviewLoader.swift:27 | needs-trigger | The shortcut has a ceiling but no upgrade trigger, so it must not look complete. |

## Report Quality Questions

- Does leanDebtLedger make intentional shortcuts auditable with ceilings and upgrade triggers?
