# Performance Runtime Boundary Fixture

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

## Fixture Intent

- Type: `shipguard-eval-boundary-fixture`
- Source tool: `shipguard ios performance`
- Source question: Did report wording keep target-app remediation separate from ShipGuard product QA next steps?
