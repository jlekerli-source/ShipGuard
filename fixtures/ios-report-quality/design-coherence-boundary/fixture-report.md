# Design Coherence Boundary Fixture

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

## Finding Proof Actions

### `design-coherence-target-work-boundary`

- Owner: `developer`
- Kind: `report-quality-proof`
- Manual proof: Review the Design Tailoring Contract and Design Coherence Boundary, then run report-quality on the synthetic fixture.
- Expected artifact: ios-report-quality.json plus fixture coverage for design coherence boundaries.
- Success condition: Report-quality accepts the public fixture while preserving the target-app work boundary.
- Failure meaning: ShipGuard design QA can still drift into app-specific remediation instead of product QA.

## Design Coherence Boundary

- Purpose: Keep design-system coherence findings as ShipGuard product-QA evidence until target-app work is separately authorized.
- Source inventory app type: `education`
- Coherence risks: 1
- Inventory is not remediation: `true`
- Coherence risk is not target task: `true`
- ShipGuard action is public fixture or rule: `true`
- App work requires separate authorization: `true`
- Target remediation status: `not-authorized-from-this-run`

ShipGuard next action:
- Owner: `ShipGuard maintainer`
- Kind: `public-fixture-or-report-rule`
- Source question: Did it separate design-system coherence findings from target-app implementation work?
- Expected artifact: A public synthetic report-quality fixture that checks the coherence boundary without private app data.
- Success condition: Report-quality fails if a design report turns coherence inventory into target-app implementation work or hides the authorization boundary.
- Failure meaning: Private app design evidence can still become unreviewed app remediation advice instead of ShipGuard product QA.

App work authorization:
- Status: `not-authorized-from-this-run`
- Requires explicit request: `true`

Proof boundary:
- Local proof: Run shipguard ios report-quality on this synthetic design fixture.
- Manual proof: A human may later authorize target-app design work, but this fixture does not authorize it.
- Expected artifact: ios-report-quality.json plus fixture coverage for design coherence boundaries.

## Professional Design Principle Vocabulary

- Source: ShipGuard native design QA vocabulary inspired by professional visual-design principles.

| Principle | Review question |
| --- | --- |
| contrast | Can lesson status and primary actions be distinguished without decorative color dependence? |
| hierarchy | Does the learning flow show lesson goal, current task, and next step in that order? |
| alignment | Do lesson cards, progress labels, and controls share a deliberate grid? |
| proximity | Are related learning controls grouped and recovery actions separated? |
| repetition | Are cards, buttons, and success states reused across the learning flow? |
| balance | Is progress feedback visually weighted without overwhelming the lesson content? |
| white space | Does spacing give comprehension room without wasting mobile screen density? |
| unity | Do color, type, symbols, copy, motion, and haptics feel like one education product? |
| motion | Does motion clarify progress or recovery while respecting Reduce Motion? |
| haptics | Are haptics milestone-aware, sparse, and left unclaimed until device proof exists? |
| preview proof | Are visual claims backed by iPhone preview or Devspace evidence? |
| app-type fit | Is the guidance tuned for education comprehension instead of generic utility polish? |

## Findings

| Severity | Category | Rule | Principles | Finding | Recommendation | Proof action |
| --- | --- | --- | --- | --- | --- | --- |
| review | Design DNA | `design-coherence-target-work-boundary` | unity, app-type fit | Design coherence finding must not become target-app work | Improve ShipGuard report-quality rules or public fixtures before using this as target-app implementation guidance. | report-quality-proof: ios-report-quality.json plus fixture coverage for design coherence boundaries. |

## Fixture Intent

- Type: `ios-design-coherence-boundary-fixture`
- Source tool: `shipguard ios design`
- Source question: Did it separate design-system coherence findings from target-app implementation work?
