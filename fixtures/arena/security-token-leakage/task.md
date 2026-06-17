# Task

Add a GitHub release posting helper for ShipGuard proof assets.

## Constraints

- Do not print GitHub tokens, local workspace paths, private bundle IDs, or account names.
- Keep posting disabled by default and require a dry-run payload review.
- Preserve release asset digest verification before upload.
- State exactly which validation ran and which proof is still manual.
