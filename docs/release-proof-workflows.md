# Release Proof Workflow Examples

The workflow examples under `examples/workflows/` show two safe ways to adopt `actions/release-proof`.

## Tag Trigger

Use `examples/workflows/release-proof-on-tag.yml` when release proof should be built automatically for tags that look like `vX.Y.Z`.

The workflow:

- runs on pushed semantic-version tags
- checks out the repository
- calls `jlekerli-source/ShipGuard/actions/release-proof@v3.112.0`
- uses the predictable release URL for the pushed tag
- uploads the release proof bundle as a GitHub Actions artifact
- prints action output paths for the tarball, manifest, replay report, attestation, and attestation badge

## Manual Dispatch

Use `examples/workflows/release-proof-manual.yml` when a maintainer wants to build proof for a specific tag from the Actions UI.

The workflow asks for:

- release tag
- release URL
- optional tracking issue URL

This is useful when publishing and proof generation are separated or when a maintainer wants to rebuild proof for a release candidate without changing code.

## Safety Notes

These examples do not create a GitHub release and do not upload release assets to a release page. They only build and upload a workflow artifact. Publish the release separately, then verify the final release assets with `shipguard release-replay verify`.

For local proof generation without GitHub Actions, use `shipguard release-proof build`. For release review from downloaded assets, use `release-proof-consumption.md`.
