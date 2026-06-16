# Backend Service Codex Maintainer Instructions

Use this file as the root operating contract for Codex in a backend service repository.

## Scope Discipline

- Read this file, `PLANS.md`, `SUBAGENTS.md`, and the task before editing.
- Keep changes narrowly tied to the requested endpoint, job, schema, or service behavior.
- Do not refactor routing, authentication, authorization, persistence, queues, deployment, or observability unless the task explicitly requires it.
- Preserve existing framework, dependency, migration, formatting, and test conventions.
- Do not add runtime dependencies unless the task justifies them and tests cover the integration.

## High-Risk Areas

Treat these as protected until a maintainer explicitly includes them in scope:

- authentication, authorization, sessions, API keys, and tenant boundaries
- database migrations, schema changes, seeds, backfills, and production data access
- payment, billing, webhook, and entitlement handlers
- background jobs, queues, schedulers, retries, and idempotency behavior
- caching, rate limits, feature flags, rollouts, and traffic routing
- logging, telemetry, privacy-sensitive data, and incident-response paths
- deployment config, secrets, infrastructure, and environment variables

## Validation Lanes

Pick the narrowest lane that proves the change:

- Static: typecheck, lint, format check.
- Unit: service, repository, validator, policy, or utility tests.
- Integration: endpoint, database, migration, auth, webhook, or queue tests.
- Contract: OpenAPI, GraphQL schema, generated client, or API compatibility checks.
- Operations: migration dry-run, rollback check, idempotency proof, or deployment preflight.

If validation cannot run, say exactly why and what remains unproven.

## Handoff Rule

Every handoff must include:

- files changed
- behavior changed
- data, auth, or operational risk touched
- validation commands and results
- rollout, rollback, or migration notes when relevant
- known risks or unproven areas
