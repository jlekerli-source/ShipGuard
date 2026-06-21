# Synthetic Lean Deck Host-Adapter Protection Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does Lean Deck protect host adapters, hardware calibration, requested explanation, and one-check minimums from false less-code pressure?

## Precision Review

- Delete candidates: 0
- Simplify candidates: 0
- Keep boundaries: 4
- Proof-blocked candidates: 2
- Action groups: 2

## Behavior Gates

| Gate | Status | Policy |
| --- | --- | --- |
| Adapter boundary | policy | Thin plugin, hook, MCP, and agent-host adapters can be the product boundary; keep them unless host registration proof says they are redundant. |
| Hardware calibration | available | Hardware, sensors, clocks, timing, and physical devices need calibration or tuning proof before simplification. |
| Requested explanation | policy | Explicitly requested reports, walkthroughs, phase notes, and rationale are not clutter. |
| One runnable check | enforced-in-lean-review | Non-trivial new logic should leave one smallest runnable check; trivial one-liners do not need ceremony. |
| Gain honesty | available-in-lean-gain | Benchmark impact is not a current-repo savings claim without a matched baseline. |
| Shortcut debt | pass | Intentional lean shortcuts need a ceiling and upgrade trigger. |

### Grouped Action Plan

| Rank | Decision | Rule | Affected | First Location | First Experiment | Validation | Stop Condition |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | keep | `host-adapter-and-hardware-boundaries` | 2 | Sources/PluginHostAdapter.swift:18 | Leave the adapter and calibration files untouched, then collect proof that they are wired and behavior-bearing. | Run the focused host-registration check and attach timing or calibration proof before any deletion attempt. | Stop if registration, startup, timing, or physical-device proof is missing. |
| 2 | keep | `requested-explanation-and-one-check-minimum` | 2 | Docs/ReleaseWalkthrough.md:7 | Keep requested documentation and the one cheap behavior check until a replacement proof route exists. | Confirm requester intent and keep one smallest runnable check for non-trivial behavior. | Stop if the report was explicitly requested or the only focused runnable check would disappear. |

### Protected Lanes

| Lane | Location | Why It Stays | Proof Before Removal |
| --- | --- | --- | --- |
| Host adapter | Sources/PluginHostAdapter.swift:18 | Thin adapters can be the product integration boundary. | Host-registration or startup evidence. |
| Hardware calibration | Sources/SensorTimingCalibration.swift:41 | Calibration can preserve physical-world timing behavior. | Before/after timing or physical-device evidence. |
| Requested explanation | Docs/ReleaseWalkthrough.md:7 | Explicit reports and walkthroughs can be product support. | Requester or doc-ownership evidence. |
| One runnable check | Tests/HostAdapterRegistrationTests.swift:11 | One focused check protects non-trivial behavior from proofless cleanup. | Equivalent runnable proof. |

## Lean Debt Ledger

- Markers: 0
- Missing upgrade trigger: 0
- Omitted by limit: 0

No `ponytail:` or `shipguard-lean:` shortcut markers found.

## Report Quality Questions

- Does Lean Deck protect host adapters, hardware calibration, requested explanation, and one-check minimums from false less-code pressure?
