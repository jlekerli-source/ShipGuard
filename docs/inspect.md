# ShipGuard InspectDeck

`shipguard inspect` is the daily control panel for ShipGuard itself. It reads existing proof outputs and summarizes the current repo state, value-gauntlet answer, full-audit state, local Codex plugin state, release proof state, and one exact next action.

```bash
./bin/shipguard inspect \
  --path . \
  --out /tmp/shipguard-inspect \
  --value-gauntlet /tmp/shipguard-value-gauntlet \
  --full-audit /tmp/shipguard-full-audit \
  --release-assets dist/release-proof-bundle-v3.131.0 \
  --shipguard-eval \
  --shareable
```

Outputs:

- `shipguard-inspect.json`
- `shipguard-inspect.md`

## What It Reads

- Git state and toolkit version from the inspected ShipGuard checkout.
- `tool-value-gauntlet.json`, including `lowestValueSurfaceProbe.answer`.
- `shipguard-full-audit.json`, including stage status, slow-lane, and efficiency summaries.
- `shipguard codex status` output for local plugin install health.
- `release-manifest.json` and optional attestation badge from a release proof bundle.

## What It Does Not Do

- It does not edit target apps.
- It does not run private app validation.
- It does not push commits.
- It does not publish a release.
- It does not replace the underlying reports; it links back to them so evidence stays inspectable.

## Product QA Boundary

Use `--shipguard-eval` when InspectDeck is part of ShipGuard product QA. That keeps the report language focused on ShipGuard usefulness instead of turning private-app findings into app work.

Use `--shareable` before moving the report into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence. Shareable output redacts local absolute paths.

## Result UX

InspectDeck leads with:

- one `status`
- one `resultUX` object
- one concise verdict
- one `nextAction`
- the proof source behind that action
- underlying evidence paths for deeper review

`resultUX.nextCommand` and `nextAction.command` must stay runnable command templates. If an upstream report such as Value Gauntlet provides prose-only proof guidance, InspectDeck keeps that prose in `nextAction.reason` / `resultUX.nextActionSummary` and falls back to a runnable ShipGuard command.

When Value Gauntlet exposes `stablePublicationPriority.nextCommand`, InspectDeck uses that stable-publication command directly. It should not send maintainers back to rerun Value Gauntlet after that receipt has already identified the real v4 publication blocker.

If an upstream Full Audit receipt has a missing or unsafe failed-stage id, InspectDeck falls back to a full-audit rerun command instead of rendering a malformed `--stage` command.

If a proof input is absent, InspectDeck marks it missing or not supplied instead of pretending the state is proven.

When multiple inputs are absent, InspectDeck prioritizes the nearest missing proof receipt first: generate `value-gauntlet`, then `full-audit`, then release proof. That keeps a bare `shipguard inspect` run useful instead of jumping straight to release publishing work before the weaker ShipGuard evidence exists.

The same order is exposed as `missingReceiptPriority` in JSON and as a Markdown table when anything is missing, so the top next action stays singular while the remaining proof queue is still visible.
