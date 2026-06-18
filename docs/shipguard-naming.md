# ShipGuard Naming

ShipGuard should feel like a real product, not a pile of generic helper scripts. The public commands stay literal because they need to be searchable, scriptable, and boring in CI. The product personality lives in branded surface names, report headings, section names, and docs.

The rule is simple: a fun name is allowed only when its plain job and proof boundary are visible beside it.

## Naming Rules

- Keep CLI verbs literal and searchable; add personality through surface names, section labels, and report copy.
- Pair every branded surface with a plain-purpose sentence.
- Use short techy nouns from the ShipGuard universe: Deck, Dock, Radar, Forge, Lens, Port, Vault, Bay, Arena, Engine, and Lab.
- Avoid app-specific branding in reusable surfaces. Private app names belong only in read-only product-QA evidence.
- Never let a vibe label weaken proof language. Release, payment, privacy, haptic, performance, and simulator claims stay literal.
- New user-facing surfaces must update `shipguard ios brand`, docs, skill routing, self-audit, package proof, and focused tests.

## Surface Scheme

| Command | Branded Surface | Plain Purpose |
| --- | --- | --- |
| `shipguard ios brand` | ShipGuard Brand Deck | Keep ShipGuard naming, tone, and future feature labels consistent. |
| `shipguard ios doctor` | ShipGuard DockCheck | Inspect Xcode, SwiftPM, schemes, targets, and proof readiness. |
| `shipguard ios inventory` | ShipGuard CargoScan | Map permissions, entitlements, StoreKit, widgets, intents, and runtime risk. |
| `shipguard ios plan` | ShipGuard BriefForge | Turn inventory into a scoped Codex brief with blockers and proof route. |
| `shipguard ios prove` | ShipGuard ProofVault | Separate local proof, simulator proof, manual proof, and blocked claims. |
| `shipguard ios launchdeck` | ShipGuard LaunchDeck | Route build/run, debugger, live preview, hot reload, and profiler work. |
| `shipguard ios performance` | ShipGuard PulseRadar | Find SwiftUI, rendering, main-thread, and profiler-proof performance risks. |
| `shipguard ios design` | ShipGuard VibeCheck | Audit UI/UX coherence, motion, haptics, preview routing, and icon direction. |
| `shipguard ios modernize` | ShipGuard UpgradeForge | Plan Swift, SwiftUI, Observation, availability, and platform modernization. |
| `shipguard ios app-intelligence` | ShipGuard SignalLens | Audit App Intents, shortcuts, widgets, Spotlight, Siri, and system exposure. |
| `shipguard ios ai-readiness` | ShipGuard ModelDock | Compare on-device, cloud, Core ML, no-AI, privacy, latency, and cost choices. |
| `shipguard ios external-audit` | ShipGuard SourceScout | Audit external repos, posts, and skills before native ShipGuard adoption. |
| `shipguard ios spec-workflow` | ShipGuard SpecForge | Generate ShipGuard-owned constitution, spec, plan, tasks, and analysis gates. |
| `shipguard ios report-quality` | ShipGuard QualityRadar | Grade ShipGuard reports for usefulness, boundaries, shareability, and fixtures. |
| `shipguard ios preview` | ShipGuard MirrorPort | Serve the phone-shaped preview and typed visual-event receipts. |
| `shipguard ios devspace` | ShipGuard Devspace Bridge | Expose preview evidence to ChatGPT/MCP planning and guarded Codex handoff. |
| `shipguard ios redact` | ShipGuard RedactionBay | Redact paths, tokens, IDs, accounts, and private terms before sharing. |
| `shipguard ios eval` | ShipGuard EvalArena | Run deterministic behavior evals for routing, proof honesty, and plugin guidance. |
| `shipguard ios goals` | ShipGuard GoalEngine | Keep slash-goal loops evidence-gated and restartable. |
| `shipguard release-proof` | ShipGuard ReleaseDock | Package, replay, consume, diff, attest, and publish release evidence. |
| `shipguard autopsy` | ShipGuard AutopsyLab | Score AI coding runs, diffs, tasks, validation logs, and PR-ready gates. |
| `shipguard arena` | ShipGuard ArenaBench | Run, compare, import, sign, and verify public benchmark fixture packs. |

## Future Naming Contract

Before shipping a new command or major report surface:

1. Add the literal CLI command to `bin/shipguard`.
2. Add a branded surface row to `scripts/ios_branding.py`.
3. Mention the surface here and in `docs/command-matrix.md`.
4. Add skill or eval routing when a user would ask for the surface by name.
5. Add self-audit, package, and focused tests.
6. Run `./bin/shipguard ios brand --path . --out /tmp/ios-shipguard-brand --strict`.

Do not rename stable public commands only for flavor. ShipGuard can be vibey in reports and docs while keeping automation-safe CLI names.
