# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-eval-boundary-fixture`
- Source question: Which private-app observation should become a public design fixture or eval case?

## App Type Signals

| App Type | Score |
| --- | ---: |
| education | 25 |
| utility | 4 |

Top signals:
- `lesson` -> education (12) in Sources/SyntheticDesignFixture/LearningFlow.swift
- `learn` -> education (8) in Sources/SyntheticDesignFixture/LearningFlow.swift

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
| review | Design DNA | `design-coherence-target-work-boundary` | Design coherence finding must not become target-app work | Improve ShipGuard report-quality rules or public fixtures before using this as target-app implementation guidance. | Review the Design Tailoring Contract and Design Coherence Boundary, then run report-quality on the synthetic fixture. |

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

## Preview And Devspace

- No preview directory was supplied.
- Run `shipguard ios preview --out /tmp/ios-shipguard-preview` for a phone-shaped visual proof loop.
- Run `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN` when ChatGPT should plan from the preview widget.
- ChatGPT model selection happens in ChatGPT; ShipGuard exposes the MCP/App bridge but cannot force a model.
