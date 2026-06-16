# Redacted Transcript: Release Proof Review

Maintainer: Before tagging, compare the release tarball SHA-256, the replay report, and the attestation badge.

Agent: I will download the release assets, run `release-consume verify`, and block if the regenerated badge disagrees with the published badge.

Maintainer: The private token appeared as `GH_TOKEN=[redacted-secret]` in the raw log and must remain redacted.

Agent: The public proof will include only asset names, digest values, and GitHub release URLs.

Result: The release was accepted only after the downloaded tarball and proof assets replayed successfully.
