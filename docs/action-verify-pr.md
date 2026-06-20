# Verify-PR Action Audit

`shipguard action verify-pr` is a read-only setup audit for the transparent GitHub Actions workflow in `examples/workflows/verify-pr.yml`.

Use it after copying the starter workflow into another repository:

```bash
shipguard action verify-pr \
  --workflow .github/workflows/shipguard-verify-pr.yml \
  --out /tmp/shipguard-action-verify-pr \
  --shareable
```

The report checks whether the workflow has the first-run proof chain ShipGuard expects:

- pull request trigger without `pull_request_target`
- full checkout for base/head diff generation
- ShipGuard install step
- PR diff written to `/tmp/shipguard-pr.diff`
- one configured `SHIPGUARD_VALIDATION_COMMAND`
- `shipguard prepare` wired to that validation command
- validation execution plus a v2 structured receipt
- `shipguard verify` using the task, diff, and receipt
- uploaded `shipguard-verdict` artifact

The bundled starter intentionally returns `review` until `SHIPGUARD_VALIDATION_COMMAND` is changed from `replace-with-your-test-command` to a real test command. A configured workflow can pass the static audit, but runtime proof still requires opening a small PR and inspecting the uploaded `shipguard-verdict` artifact.

After the workflow has run on a small PR, download and consume the artifact with the same command:

```bash
gh run download <run-id> \
  --name shipguard-verdict \
  --dir /tmp/shipguard-verdict-artifact

shipguard action verify-pr \
  --workflow .github/workflows/shipguard-verify-pr.yml \
  --artifact-dir /tmp/shipguard-verdict-artifact \
  --out /tmp/shipguard-action-verify-pr \
  --shareable
```

With `--artifact-dir`, the report checks for `shipguard-verdict.json`, `shipguard-verdict.md`, `tool: shipguard verify`, a known verdict status, proof-report summary, validation coverage, v2 evidence receipt schema, diff-first merge verdict, and a reviewer next action. This proves the PR action produced a consumable ShipGuard verdict artifact; it does not mean the PR itself passed.

This command does not run target tests, push code, or claim the GitHub workflow has executed.
