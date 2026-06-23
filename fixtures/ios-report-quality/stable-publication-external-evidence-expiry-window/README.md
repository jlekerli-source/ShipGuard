# Stable-Publication External Evidence Expiry Window Fixture

This public synthetic fixture keeps ShipGuard report-quality honest about evidence age. It proves external adoption and final security-review records need an explicit expiry window, not only a `generatedAt` timestamp.

It is not adoption evidence, final security-review evidence, or stable-v4 publication proof.

Validate with:

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/stable-publication-external-evidence-expiry-window --out <quality-dir> --shareable
```
