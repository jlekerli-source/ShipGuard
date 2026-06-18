# Design App-Type Tailoring Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## App Type Signals

| App Type | Score |
| --- | ---: |
| education | 25 |
| utility | 4 |
| game | 3 |

Top signals:
- `lesson` -> education (12) in Sources/SyntheticDesignFixture/LearningFlow.swift
- `learn` -> education (8) in Sources/SyntheticDesignFixture/LearningFlow.swift
- `progress` -> education (5) in Sources/SyntheticDesignFixture/LearningFlow.swift

## Design Tailoring Contract

- Tailored for: `education`
- Guidance profile: `learning-progress`
- Universal defaults rejected: `true`
- Source signals: lesson->education, learn->education, progress->education
- Motion stance: production-polish
- Haptics tone: encouraging, milestone-aware, and interruption-sparse
- Visual density stance: allow expressive hierarchy with proof
- Copy tone stance: specific to the app task and audience
- Risk: Generic utility restraint can make learning feedback feel flat, while generic game delight can distract from comprehension.
- Owner: `developer`
- Manual proof: Review one synthetic learning flow and confirm motion, haptics, visual density, and copy guidance match the education profile rather than a universal design checklist.
- Expected artifact: A same-flow screenshot or preview receipt plus one note mapping the learning-progress profile to source signals.
- Success condition: The report explains why learning-progress is the right profile for education and avoids utility-only advice.
- Failure meaning: The design report remains an inventory, not an app-type-specific design QA recommendation.

## Findings

| Severity | Category | Rule | Finding | Recommendation | Proof |
| --- | --- | --- | --- | --- | --- |
| review | Design Tailoring | `design-tailoring-app-type-proof` | Education guidance must be app-type tailored | Use the learning-progress profile for motion, haptics, visual density, and copy guidance. | Review the Design Tailoring Contract and attach one preview or screenshot receipt for the synthetic learning flow. |

## Fixture Intent

- Type: `ios-design-report-quality-fixture`
- Source tool: `shipguard ios design`
- Source question: Did the report tailor advice to the app type instead of applying one universal design rule?
