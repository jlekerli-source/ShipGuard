# Release Evidence Verification

`codex-maintainer release-evidence verify` consumes a release evidence artifact and checks that the static evidence, copied source reports, optional index, and optional bundle metadata agree.

Use it after downloading the artifact produced by `actions/release-evidence`:

```bash
./bin/codex-maintainer release-evidence verify \
  --dir /tmp/codex-maintainer-release-evidence \
  --out /tmp/codex-maintainer-release-evidence-verify \
  --require-diff true \
  --require-index true
```

Outputs:

- `evidence-verify.json`
- `evidence-verify.md`
- `badge.json`

The verifier accepts either a full action artifact directory containing `site/`, `index/`, optional `consumer-proof/`, optional `release-diff/`, and optional `bundle.json`, or a standalone evidence site directory containing `evidence.json`.

Checks include:

- `evidence.json` schema and pass status.
- Source `consumer-report.json` and `asset-digests.json` presence.
- Consumer proof release identity matching the static evidence release identity.
- Asset digest summary consistency.
- Required asset availability.
- Release diff source and pass status when diff evidence is present.
- Evidence index schema, pass status, and release entry when an index is present.
- Bundle output paths and diff flag consistency when `bundle.json` is present.

Use `--require-diff true` when your workflow must include comparison against a previous release. Use `--require-index true` when your workflow must include a browsable evidence history. The default `auto` mode verifies those files when present without requiring them.

In GitHub Actions, let `actions/release-evidence-verify` download and verify the artifact in one step:

```yaml
- name: Verify release evidence artifact
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence-verify@v3.30.0
  with:
    download-artifact: true
    source-artifact-name: codex-maintainer-release-evidence
    dir: artifacts/codex-maintainer-release-evidence
    require-diff: true
    require-index: true
    mode: fail
```

If a previous step already downloaded the artifact, leave `download-artifact` as `false` and point `dir` at the downloaded directory.

## Negative Fixtures

The checked-in fixtures under `../fixtures/release-evidence/negative/` intentionally fail verification. They cover missing copied source reports, consumer/evidence release mismatches, digest summary mismatches, and bundle manifests that point at missing outputs.

Each negative fixture should exit nonzero while still writing:

- `evidence-verify.json` with `status` set to `blocked`
- `evidence-verify.md` with the failed check
- `badge.json` with `message` set to `blocked`

Use `negative-index` to run the full fixture manifest and publish a compact guardrail report:

```bash
./bin/codex-maintainer release-evidence negative-index \
  --fixture fixtures/release-evidence/negative \
  --out /tmp/codex-maintainer-negative-evidence
```

The command reads `cases.tsv`, runs every case through `release-evidence verify`, and writes `index.html`, `negative-fixture-index.json`, `negative-fixture-index.md`, `badge.json`, plus per-case verifier outputs under `runs/<case>/`. It passes only when every listed negative fixture blocks on its expected check.

Use `actions/release-evidence-negative-index` when the same guardrail report should be published from GitHub Actions. See `release-evidence-negative-index-action.md`.

See `release-evidence-action.md` for producing the artifact and `../examples/workflows/release-evidence-consume.yml` for the full two-job workflow.
