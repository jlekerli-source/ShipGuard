# Web Workflow Starter

This profile adapts the ShipGuard workflow for web apps.

It is intentionally framework-neutral. Replace placeholder paths with the actual app structure before using it for production work.

After initializing:

```bash
shipguard init web ../my-web-app
shipguard doctor web .
```

Then update `AGENTS.md` with:

- app framework and package manager
- source, route, component, and test paths
- build, lint, unit, integration, and browser validation commands
- protected areas such as auth, payments, migrations, and production config
