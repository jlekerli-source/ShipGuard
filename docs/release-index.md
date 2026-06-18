# Release Index

`shipguard release-index build` creates a release proof catalog from one or more `release-manifest.json` files.

```bash
./bin/shipguard release-index build \
  --manifest dist/release-proof-v3.6.0/release-manifest.json \
  --manifest dist/release-proof-v3.102.0/release-manifest.json \
  --out /tmp/shipguard-release-index
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

The command sorts releases by semantic version and rejects duplicate versions. It does not contact GitHub or verify the tarballs itself; run `shipguard release-manifest verify` for each manifest before trusting the catalog. Run `shipguard release-replay verify` after downloading published release assets when you also want to verify the catalog row against the tarball and proof ledger.
