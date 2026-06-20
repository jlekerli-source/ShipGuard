# ShipGuard V4 Stable Publication Proof

`shipguard v4 stable-publication` is the final local proof gate before anyone says ShipGuard v4 is stable.

It does not publish a GitHub release, change repository rules, edit target apps, or claim marketplace acceptance. It reads public release metadata, release notes, a prior LaunchKey release-candidate report, release assets, adoption evidence, and security-review evidence, then blocks stable-v4 claims until the full packet passes.

## Command

```bash
./bin/shipguard v4 stable-publication \
  --path . \
  --out /tmp/shipguard-v4-stable-publication \
  --github-release-repo <owner/repo> \
  --release-version <version> \
  --release-candidate-report <v4-release-candidate-json-or-dir> \
  --download-release-assets \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable
```

If release assets were already downloaded:

```bash
./bin/shipguard v4 stable-publication \
  --path . \
  --out /tmp/shipguard-v4-stable-publication \
  --github-release-repo <owner/repo> \
  --release-version <version> \
  --release-candidate-report <v4-release-candidate-json-or-dir> \
  --release-assets <downloaded-assets-dir> \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable
```

Outputs:

- `v4-stable-publication.json`
- `v4-stable-publication.md`
- `downloaded-release-assets/` when `--download-release-assets` is supplied and no custom destination is given
- `release-consume/consumer-report.json` when downloaded or supplied release assets are verified
- `stablePublicationEvidencePacket` in JSON, rendered as `Evidence Packet` in Markdown

## Stable Gates

The report returns `pass` only when every gate passes:

- GitHub release metadata exists for the requested tag, is not draft/prerelease, and includes the required release assets.
- Release notes explicitly describe stable-v4 publication proof.
- The supplied `v4 release-candidate` report is from LaunchKey, passed, and still claims only `candidate-ready`.
- Downloaded or supplied release assets pass `shipguard release-consume verify`.
- Post-release consumer proof is attached from the release assets.
- External adoption evidence passes the stable-v4 gate with independent public or redacted external records.
- Final security-review evidence passes the stable-v4 gate with CLI, plugin, GitHub Actions, release-proof, package-install, and redaction/privacy scope coverage.

If any gate fails, the report returns `review`, sets `stableV4Release` to `false`, and puts the next command in `resultUX.nextCommand`.

## Evidence Packet

The JSON report includes `stablePublicationEvidencePacket` so humans and tools can inspect the real publication packet without piecing it together from scattered sections. It lists:

- all seven required evidence inputs with stable IDs and statuses
- whether each input is required for stable v4 and must be real evidence
- `missingEvidenceIds`
- `firstBlockingGate` with the exact next command
- proof order from LaunchKey candidate proof to published release proof
- non-claims for marketplace acceptance, fixture-only proof, and GitHub download counts

`ios report-quality` checks this packet. A stable-publication report that has the gates but hides the packet receives a report-quality issue.

## Evidence Boundary

`stable-publication` intentionally sits after `v4 release-candidate`.

`v4 release-candidate` proves the package and release packet are candidate-ready. It can use public fixtures to prove the workflow works. `v4 stable-publication` proves the actual published release by reading public release metadata, real release notes, downloaded release assets, independent adoption evidence, and final security-review evidence. Synthetic fixture adoption or security records can prove the tool path, but they do not prove stable-v4 publication.

Use `--shareable` before moving this report into GitHub, ChatGPT planning, public docs, or release evidence. Shareable output redacts local paths while preserving proof status, gate names, and next commands.

## Required Validation

Use this lane when changing the stable-publication surface:

```bash
git diff --check
python3 -m py_compile scripts/v4_stable_publication.py scripts/v4_release_candidate.py
./tests/v4_stable_publication_test.sh
./tests/ios_report_quality_test.sh
./tests/tool_value_gauntlet_test.sh
./bin/shipguard validate
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
./tests/self_audit_test.sh
./tests/cli_smoke_test.sh
./tests/package_release_test.sh
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

## Blocked Claims

Passing earlier v4 reports does not mean:

- ShipGuard v4 is stable.
- The GitHub release assets were downloaded and consumed by a fresh user.
- Independent adoption happened.
- Final security review happened.
- OpenAI accepted ShipGuard into a public marketplace.

Only a passing `v4 stable-publication` report allows the local stable-v4 release claim.
