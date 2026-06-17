# Task

Fix a migration regression where existing alarms disappear after adding a new `soundProfileID` column.

## Constraints

- Preserve existing alarm rows and enabled/disabled state.
- Include rollback, backup, or migration rehearsal proof before release claims.
- Verify fresh install, upgrade from the previous schema, and corrupted-store recovery behavior.
- Do not claim production readiness from a clean database launch alone.
