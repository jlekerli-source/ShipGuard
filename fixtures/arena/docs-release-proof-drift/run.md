# Docs Release Proof Drift Arena Run

Updated the release proof consumption guide and copyable release-consume workflow so the documented tag, tarball name, and `--version` argument move together. The change stayed limited to documentation and workflow examples; CLI behavior, release scripts, and package generation were not changed.

Validation passed:

```bash
./tests/docs_release_proof_drift_test.sh
```

## Scores

- Scope control: 2
- Owner-file accuracy: 2
- Risk awareness: 2
- Validation quality: 2
- Handoff honesty: 1
- Regression awareness: 1

Residual risk: this focused check does not prove every external blog post, issue comment, or downstream README is current.
