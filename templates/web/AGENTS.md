# Web ShipGuard Instructions

Use this file as the root operating contract for Codex in a web app repository.

## Scope Discipline

- Read this file, `PLANS.md`, `SUBAGENTS.md`, and the task before editing.
- Keep changes narrowly tied to the requested behavior.
- Do not refactor routing, build configuration, auth, payments, migrations, or deployment code unless the task explicitly requires it.
- Preserve existing framework, package-manager, lint, formatting, and component conventions.
- Do not add runtime dependencies unless the task justifies them and tests cover the integration.

## High-Risk Areas

Treat these as protected until a maintainer explicitly includes them in scope:

- authentication, session, permission, and account code
- billing, checkout, subscriptions, invoices, or payment webhooks
- database migrations, schema changes, seeds, and production data access
- environment config, secrets, deployment, CDN, cache, or proxy behavior
- analytics, tracking consent, and privacy-sensitive user data
- server actions, API routes, background jobs, and queue workers

## Validation Lanes

Pick the narrowest lane that proves the change:

- Static: typecheck, lint, format check.
- Unit: component, utility, hook, API handler, or server function tests.
- Integration: route, form, data-fetching, auth, or payment-flow tests.
- Browser: Playwright or equivalent for user-visible behavior.
- Build: production build when routing, bundling, config, or deployment behavior changes.

If validation cannot run, say exactly why and what remains unproven.

## Handoff Rule

Every handoff must include:

- files changed
- user-visible behavior changed
- validation commands and results
- known risks or unproven areas
- follow-up work that should not be hidden inside the current change
