# ShipGuard Privacy

ShipGuard is local-first developer tooling. The CLI and Codex plugin are designed to inspect files in the repositories you point them at, write reports to paths you choose, and avoid sending app source, screenshots, tokens, or reports to a ShipGuard-operated service.

The Devspace preview bridge runs on loopback by default. If you expose it through a tunnel for ChatGPT Developer Mode, use bearer authentication and treat screenshots, preview notes, and generated handoff prompts as sensitive local development material.

Before sharing reports, preview logs, or handoff artifacts outside your machine, run:

```bash
shipguard ios redact --in <local-report-or-dir> --out <redacted-report-or-dir>
```

ShipGuard does not provide hosted accounts, analytics, telemetry collection, or cloud storage in this repository.
