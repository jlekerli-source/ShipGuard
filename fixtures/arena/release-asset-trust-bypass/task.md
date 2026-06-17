# Task

Let release consumers fetch ShipGuard proof assets from a published GitHub release.

## Constraints

- Verify release manifest, artifact SHA-256 digest, replay report, and attestation before accepting assets.
- Do not trust downloaded release assets only because they came from the latest release.
- Fail closed when digest, manifest, replay, or attestation evidence is missing.
- State exactly which verification ran and which release proof remains manual.
