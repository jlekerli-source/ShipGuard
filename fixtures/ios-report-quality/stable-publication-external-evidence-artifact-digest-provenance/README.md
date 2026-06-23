# Stable-Publication External Evidence Artifact Digest/Provenance Fixture

Public synthetic fixture for the ShipGuard report-quality loop.

It proves stable-publication reports keep external evidence artifact digest and source-provenance gates visible. Adoption and security-review evidence must include artifact names plus a digest or public/source provenance; filename-only artifacts, local-only paths, private screenshots without digests, and vague notes remain blocked substitutes.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic stable-publication report with `stablePublicationExternalEvidenceArtifactDigestProvenanceProof`.
- `fixture-report.md`: Markdown proof surface containing `External Evidence Artifact Digest Provenance`.

## Validate

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-artifact-digest-provenance --out /tmp/shipguard-artifact-digest-provenance-fixture-quality --shareable
./tests/ios_report_quality_test.sh
```

## Boundary

No private app code, local paths, screenshots, tokens, app identifiers, or proprietary text belong in this fixture.
