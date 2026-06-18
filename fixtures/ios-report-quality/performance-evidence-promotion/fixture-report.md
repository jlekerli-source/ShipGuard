# Performance Evidence Promotion Fixture

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

## Evidence Promotion Contract

- Source evidence: `source heuristic`
- Promotion status: `missing-runtime-proof`
- First candidate rule: `swiftui-repeat-forever-animation`
- Owner: `developer`
- Manual proof: Run the same local sample or trace before and after the single animation gate; attach device Instruments proof before claiming FPS, ProMotion, battery, thermal, or hardware-display improvement.
- Expected artifact: Same-route before/after trace, sample, or screen recording for the first swiftui-repeat-forever-animation experiment.
- Success condition: The same-route proof shows less constant motion work, Reduce Motion or visibility behavior remains correct, and no broader performance claim is made without device proof.
- Failure meaning: The source suspicion remains unpromoted; keep it as review guidance and do not broaden scanner heuristics or target-app remediation.

## Grouped Next Actions

| Rule | Count | Severity | First experiment | Validation route | Stop condition |
| --- | ---: | --- | --- | --- | --- |
| `swiftui-repeat-forever-animation` | 1 | review | Disable or gate one decorative repeatForever animation behind Reduce Motion and active-screen visibility, then compare an at-rest screen recording plus a same-route sample. | Run the same local sample or trace before and after the single gate; use device Instruments before claiming FPS, ProMotion, battery, or thermal improvement. | Stop after the first gated animation unless the same-route proof shows a measurable improvement and the UI still communicates the intended state. |

## Top Findings

| Severity | Rule | Location | Why severity | Why it matters |
| --- | --- | --- | --- | --- |
| review | `swiftui-repeat-forever-animation` | `Sources/SyntheticPerformanceFixture/LoopingMotionView.swift:12` | Review because repeatForever can keep the render loop active until it is gated by visibility, Reduce Motion, or user value. | Always-on decorative motion can keep rendering work alive and combine poorly with blur, material, or tab backgrounds. |

## Proof Boundaries

| Severity | Rule | Codex local proof | Manual/device proof |
| --- | --- | --- | --- |
| review | `swiftui-repeat-forever-animation` | Record the synthetic screen at rest and during one interaction, then compare samples after gating the animation. | Use physical-device Instruments before making FPS, ProMotion, thermal, battery, or hardware-display claims. |

## Fixture Intent

- Type: `ios-performance-report-quality-fixture`
- Source tool: `shipguard ios performance`
- Source question: Did the report make it obvious which evidence would promote a source suspicion into broader work?
