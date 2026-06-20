# Release Package Hygiene

`shipguard release-package hygiene` is a read-only package-lineage report for ShipGuard release tarballs.

It exists because real public-release QA showed a previous package could block LaunchKey same-prefix upgrade proof before install: the tarball contained generated macOS AppleDouble metadata such as `._*`.

## Run It

Scan the default local release package directory:

```bash
./bin/shipguard release-package hygiene \
  --path . \
  --out /tmp/shipguard-package-hygiene \
  --shareable
```

Scan explicit tarballs or downloaded GitHub release assets:

```bash
./bin/shipguard release-package hygiene \
  --path . \
  --tarball dist/shipguard-v3.131.0.tar.gz \
  --assets /tmp/downloaded-release-assets \
  --out /tmp/shipguard-package-hygiene \
  --shareable
```

## What It Checks

- generated metadata members such as `._*`, `.DS_Store`, and `__MACOSX`
- bytecode and cache artifacts such as `.pyc`, `__pycache__`, `.cache`, and `DerivedData`
- unsafe absolute paths, path traversal, links, hard links, and devices
- missing installable package roots with `scripts/install.sh`, `bin/shipguard`, and `VERSION`
- whether the current `VERSION` has a safe package baseline among scanned tarballs

## Output

The command writes:

- `release-package-hygiene.json`
- `release-package-hygiene.md`

The report includes affected versions, blocked/review findings, a safe current baseline when proven, exact unsafe archive members, a repair plan, result UX, scope boundaries, and report-quality questions.

## Boundary

The command does not extract packages, rewrite historical release assets, delete old files, or claim old releases are repaired.

Use it before LaunchKey install or upgrade proof when a package lineage question exists:

```bash
./scripts/package_release.sh
./tests/package_release_test.sh
./bin/shipguard release-package hygiene --path . --out /tmp/shipguard-package-hygiene --shareable
```
