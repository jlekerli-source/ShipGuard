# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-verify-first-task-contract-fixture`
- Source question: Did prepare produce one durable object connecting goal, risk, scope, proof, claims, and verdict?

## Quickstart Replay

- Phase: `prepare`
- First useful verdict: `shipguard verify --task <task-dir>/shipguard-task.json --diff <patch.diff> --evidence <validation-receipt.json> --claim <scoped-claim> --out <verdict-dir>`
- Proof inputs: `<patch.diff>`, `<validation-receipt.json>`, `<scoped-claim>`
- Success signal: shipguard-verdict.json returns pass, review, blocked, or incomplete with one nextAction.
- Connects: goal, riskClassification, authorizedFiles, protectedBoundaries, validationContract, agentClaims, verdict, nextAction
- Boundary: Synthetic replay contract only; it does not authorize target-app work.
