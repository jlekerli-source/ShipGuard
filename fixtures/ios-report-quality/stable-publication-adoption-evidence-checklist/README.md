# stable-publication-adoption-evidence-checklist

Public synthetic fixture for stable-publication adoption evidence quality.

## Boundary

- Synthetic ShipGuard report shape only.
- No private app code, local paths, screenshots, app identifiers, account data, or proprietary text.
- Proves weak adoption signals are rejected as non-proof.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`

## Expected Behavior

- `ios report-quality` treats this as an existing public fixture.
- No recursive `fixtureCandidates` are emitted for the same question.
- Stable-v4 release remains blocked until adoption evidence has an independent actor, commands, artifacts, redaction, outcome, and non-claims.
