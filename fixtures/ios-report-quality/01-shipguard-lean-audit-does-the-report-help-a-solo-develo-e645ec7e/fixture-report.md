# Synthetic Lean Deck Deletion-Usefulness Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does the report help a solo developer delete clutter without deleting product behavior?

## Precision Review

- Delete candidates: 1
- Simplify candidates: 1
- Keep boundaries: 1
- Proof-blocked candidates: 1
- Action groups: 4

## Behavior Gates

| Gate | Status | Policy |
| --- | --- | --- |
| Adapter boundary | policy | Thin plugin, hook, MCP, and agent-host adapters can be the product boundary; keep them unless host registration proof says they are redundant. |
| Hardware calibration | available | Hardware, sensors, clocks, timing, and physical devices need calibration or tuning proof before simplification. |
| Requested explanation | policy | Explicitly requested reports, walkthroughs, phase notes, and rationale are not clutter. |
| One runnable check | enforced-in-lean-review | Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony. |
| Gain honesty | available-in-lean-gain | Benchmark impact is not a current-repo savings claim without a matched baseline. |
| Shortcut debt | pass | Intentional lean shortcuts need a ceiling and upgrade trigger. |

## Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | delete | `delete-unused-debug-banner` | 1 | Sources/UnusedDebugBanner.swift:14 | Prove the debug banner has no call sites, then delete only that file in the first cleanup pass. | Run symbol search and one UI smoke check before accepting the deletion. | Stop if search finds a runtime route, preview, test, or support workflow that still references the banner. |
| 2 | simplify | `native-url-components` | 1 | Sources/QueryFlagParser.swift:22 | Replace only the query flag helper with the platform URL parser behind focused parser tests. | Run parser checks for repeated keys, empty values, ordering, and encoding. | Stop if repeated keys, empty values, or percent encoding behave differently. |
| 3 | keep | `keep-product-behavior-boundary` | 1 | Sources/SubscriptionEntitlementGate.swift:38 | Leave the entitlement gate untouched and document the proof required before any cleanup. | Require focused entitlement behavior checks before simplification. | Stop if purchase, restore, denied, or expired entitlement proof is missing. |
| 4 | proof-blocked | `proof-blocked-migration-bridge` | 1 | Sources/LegacyMigrationBridge.swift:51 | Search migration call sites and add a synthetic migrated-user fixture before touching the bridge. | Run call-site search plus a migration fixture before any deletion. | Stop if migrated-user state, call-site search, or rollback proof is missing. |

## Solo Developer Decision Map

| Lane | Location | Decision | Proof Before Edit |
| --- | --- | --- | --- |
| Debug banner | Sources/UnusedDebugBanner.swift:14 | Delete | Symbol search plus one UI smoke check. |
| Query parser | Sources/QueryFlagParser.swift:22 | Simplify | Parser checks for repeated keys, empty values, ordering, and encoding. |
| Entitlement gate | Sources/SubscriptionEntitlementGate.swift:38 | Keep | Purchase, restore, denied, and expired entitlement behavior checks. |
| Migration bridge | Sources/LegacyMigrationBridge.swift:51 | Proof-blocked | Call-site search plus migrated-user fixture. |

## Lean Debt Ledger

- Markers: 0
- Missing upgrade trigger: 0
- Omitted by limit: 0

No `ponytail:` or `shipguard-lean:` shortcut markers found.

## Report Quality Questions

- Does the report help a solo developer delete clutter without deleting product behavior?
