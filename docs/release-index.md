# Release Index

`codex-maintainer release-index build` creates a release proof catalog from one or more `release-manifest.json` files.

```bash
./bin/codex-maintainer release-index build \
  --manifest dist/release-proof-v3.2.0/release-manifest.json \
  --manifest dist/release-proof-v3.3.0/release-manifest.json \
  --out /tmp/codex-maintainer-release-index
```

Outputs:

- `release-index.json`
- `release-index.md`

The index records:

- schema version
- generated timestamp
- release count
- version, tag, commit, artifact name, bytes, and SHA-256
- CI run, release, and issue URLs when present in the source manifests

The command sorts releases by semantic version and rejects duplicate versions. It does not contact GitHub or verify the tarballs itself; run `codex-maintainer release-manifest verify` for each manifest before trusting the catalog.
