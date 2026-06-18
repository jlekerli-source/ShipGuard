# Grouped Performance Observation Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Runtime Evidence Boundary

- Evidence: `source heuristic`
- Confidence: `medium`
- Runtime proof: `missing`
- Blocking: `no`
- Interpretation: Synthetic source-only performance fixture; it does not prove actual CPU, GPU, memory, energy, hitch, FPS, or frame-rate problems.
- Promotion rule: Promote only after a public fixture or same-route runtime proof confirms the issue shape.

Required runtime proof:
- Same-route Simulator trace, sample, or log evidence for local-only claims.
- Physical-device Instruments or equivalent proof for FPS, ProMotion, thermal, battery, wake-path, or hardware-display claims.

## Grouped Next Actions

| Rule | Count | Severity | First experiment | Validation route | Stop condition |
| --- | ---: | --- | --- | --- | --- |
| `swiftui-repeat-forever-animation` | 4 | review | Disable or gate one decorative repeatForever animation behind Reduce Motion and active-screen visibility, then compare an at-rest screen recording plus a same-route sample. | Run the same local sample or trace before and after the single gate; use device Instruments before claiming FPS, ProMotion, battery, or thermal improvement. | Stop after the first gated animation unless the same-route proof shows a measurable improvement and the UI still communicates the intended state. |

## Top Findings

| Severity | Rule | Location | Why severity | Why it matters |
| --- | --- | --- | --- | --- |
| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:12` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |
| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:28` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |
| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:44` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |
| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:60` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |

## Proof Boundaries

| Severity | Rule | Codex local proof | Manual/device proof |
| --- | --- | --- | --- |
| review | `swiftui-repeat-forever-animation` | Record the synthetic screen at rest and during one interaction, then compare samples after gating the animation. | Use physical-device Instruments before making FPS, ProMotion, thermal, battery, or hardware-display claims. |

## Fixture Intent

- Type: `ios-performance-report-quality-fixture`
- Source tool: `shipguard ios performance`
- Source question: Which grouped performance observation should become a public fixture or eval case before changing scanner heuristics again?
