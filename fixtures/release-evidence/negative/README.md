# Release Evidence Negative Fixtures

These fixtures are intentionally invalid `release-evidence verify` inputs. They prove the verifier reports blocked evidence with machine-readable failed checks instead of accepting inconsistent artifacts.

Cases:

- `missing-source`: `evidence.json` points at a missing `asset-digests.json`.
- `consumer-mismatch`: copied consumer proof reports a different release than `evidence.json`.
- `digest-summary-mismatch`: copied asset digest rows do not match the summary in `evidence.json`.
- `bundle-missing-output`: `bundle.json` points at a missing evidence index output.

Use:

```bash
./bin/codex-maintainer release-evidence verify \
  --dir fixtures/release-evidence/negative/consumer-mismatch \
  --out /tmp/release-evidence-negative
```

The command should exit nonzero and write `evidence-verify.json` with `status` set to `blocked`.
