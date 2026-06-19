# ShipGuard V4 Release Candidate Readiness

`shipguard v4 release-candidate` is the local readiness gate before any stable v4 product claim.

It does not publish v4, change repository rules, edit private target apps, or claim marketplace acceptance. It checks whether the ShipGuard package is ready for an external developer to install, upgrade, uninstall, consume release proof, and understand the adoption packet without maintainer context.

## Command

```bash
./bin/shipguard v4 release-candidate \
  --path . \
  --out /tmp/shipguard-v4-release-candidate \
  --shipguard-eval \
  --shareable
```

To attach real downloaded release assets to the same readiness report:

```bash
./bin/shipguard v4 release-candidate \
  --path . \
  --out /tmp/shipguard-v4-release-candidate \
  --package-tarball <release-tarball> \
  --upgrade-from-tarball <previous-release-tarball> \
  --fresh-install-prefix /tmp/shipguard-fresh-install \
  --upgrade-prefix /tmp/shipguard-upgrade-install \
  --rollback-prefix /tmp/shipguard-rollback-install \
  --release-assets <downloaded-assets-dir> \
  --release-version <version> \
  --release-consume-out /tmp/shipguard-v4-release-consume \
  --shipguard-eval \
  --shareable
```

Outputs:

- `v4-release-candidate.json`
- `v4-release-candidate.md`
- `fresh-install-prefix/bin/shipguard` when `--package-tarball` is supplied and `--fresh-install-prefix` is omitted
- `upgrade-prefix/bin/shipguard` when `--package-tarball` and `--upgrade-from-tarball` are supplied and `--upgrade-prefix` is omitted
- `rollback-prefix/` rollback cleanup evidence when `--package-tarball` is supplied and `--rollback-prefix` is omitted
- `release-consume/consumer-report.json` when `--release-assets` is supplied and `--release-consume-out` is omitted

## Proof Contract

The command checks these gates:

- Fresh install proof: a release package can install to a clean prefix and run validation from that prefix.
- Upgrade proof: an existing install can be replaced by the candidate package and still report the intended version.
- Uninstall proof: temporary install state can be removed cleanly without hidden required state.
- Release proof consumption: downloaded release assets can pass `shipguard release-consume verify`.
- External adoption packet: an outside developer can see the first command, proof bundle, support boundary, and non-claims.
- Final schema docs: v4 schema-freeze docs remain linked and visible.
- Plugin refresh proof: local Codex plugin refresh and `shipguard codex status --strict` remain part of the release lane.

Without `--package-tarball`, the command can still pass release-candidate readiness, but `freshInstallPackageProof.status` is `not-provided`. Stable-v4 proof needs a real package tarball to install into a fresh prefix, report the expected version through both `shipguard` and the compatibility alias, run `shipguard validate`, and prove the installed tree omits generated, VCS, cache, bytecode, dist, and AppleDouble files.

When `--package-tarball` is supplied, LaunchKey runs:

```bash
PREFIX=<fresh-prefix> <package>/scripts/install.sh
<fresh-prefix>/bin/shipguard version
<fresh-prefix>/bin/codex-maintainer version
<fresh-prefix>/bin/shipguard validate
```

The report then records `freshInstallPackageProof`, including installed version, legacy alias version, validation result, forbidden installed path count, and redacted install paths. If install or validation fails, the release-candidate report returns review instead of treating static package docs as fresh-install proof.

When `--fresh-install-prefix`, `--fresh-install-work-dir`, `--upgrade-prefix`, `--upgrade-work-dir`, `--rollback-prefix`, `--rollback-work-dir`, or `--release-consume-out` are omitted, LaunchKey writes generated proof directories under the candidate output. Those directories are evidence attachments, not report-quality source reports. `shipguard ios report-quality --reports <candidate-out>` skips `fresh-install-prefix`, `fresh-install-work`, `upgrade-prefix`, `upgrade-work`, `rollback-prefix`, `rollback-work`, and `release-consume` so it grades the root `v4-release-candidate.json` instead of recursively scoring installed packages or consumer-proof receipts.

Without `--upgrade-from-tarball`, the command can still pass release-candidate readiness, but `upgradePackageProof.status` is `not-provided`. Stable-v4 proof needs a previous release tarball plus the candidate tarball so LaunchKey can prove the same prefix upgrades from the previous package to the candidate package.

When `--upgrade-from-tarball` and `--package-tarball` are supplied, LaunchKey runs:

```bash
PREFIX=<upgrade-prefix> <previous-package>/scripts/install.sh
<upgrade-prefix>/bin/shipguard version
PREFIX=<same-upgrade-prefix> <candidate-package>/scripts/install.sh
<upgrade-prefix>/bin/shipguard version
<upgrade-prefix>/bin/codex-maintainer version
<upgrade-prefix>/bin/shipguard validate
```

The report then records `upgradePackageProof`, including previous installed version, upgraded version, compatibility alias version, validation result, forbidden installed path count, and redacted upgrade paths. If the previous package cannot install, the candidate package cannot replace it, validation fails, or the upgraded tree contains generated/VCS/cache files, the release-candidate report returns review.

When `--package-tarball` is supplied, LaunchKey also attaches `rollbackPackageProof`. It installs the candidate package into a temporary prefix, verifies the installed version, removes known ShipGuard package paths, and confirms no temporary ShipGuard package state remains:

```bash
PREFIX=<rollback-prefix> <candidate-package>/scripts/install.sh
<rollback-prefix>/bin/shipguard version
rm -rf <rollback-prefix>/bin/shipguard <rollback-prefix>/bin/codex-maintainer <rollback-prefix>/lib/shipguard
test ! -e <rollback-prefix>/bin/shipguard
test ! -e <rollback-prefix>/bin/codex-maintainer
test ! -e <rollback-prefix>/lib/shipguard
```

If `--package-tarball` is omitted, `rollbackPackageProof.status` is `not-provided`.

Without `--release-assets`, the command can still pass release-candidate readiness, but `publishedReleaseAssetProof.status` is `not-provided`. That is intentional: candidate readiness is not the same as stable-v4 proof. Stable-v4 release proof needs downloaded release assets to pass consumer-side verification.

When `--release-assets` is supplied, LaunchKey runs:

```bash
./bin/shipguard release-consume verify \
  --dir <downloaded-assets-dir> \
  --out <consume-dir> \
  --version <version>
```

The report then records `publishedReleaseAssetProof`, including consumer report status, replay status, attestation status, digest matrix path, and artifact SHA-256 when available. If consumer verification fails, the release-candidate report returns review instead of treating the supplied assets as stable proof.

## External Adoption Packet

Every release-candidate packet should answer:

- First command: `./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --shipguard-eval --shareable`
- Proof bundle: release manifest, release index, release replay, release consume report, and self-audit report.
- Support boundary: ShipGuard validates local proof and report quality; it does not run private app remediation unless explicitly asked.
- Non-claims: no OpenAI marketplace acceptance, no broad third-party adoption, and no private target-app validation are implied by the local readiness report.

## Required Validation

Use this minimum lane before claiming v4 release-candidate readiness:

```bash
git diff --check
./tests/v4_release_candidate_test.sh
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

For release assets, verify the consumer path too:

```bash
./bin/shipguard release-proof build --out /tmp/shipguard-release-proof --release-url <url> --version <version> --tag <tag> --commit <sha> --ci-run-url <url>
./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out /tmp/shipguard-release-consume --version <version>
./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --release-assets <downloaded-assets-dir> --release-version <version> --shipguard-eval --shareable
```

## Blocked Claims

Passing this report means ShipGuard is candidate-ready. It does not mean:

- ShipGuard v4 is a stable product release.
- OpenAI accepted ShipGuard into a public marketplace.
- External adoption has been proven by independent users.
- Any private app has been validated.
- Physical-device iOS behavior has been proven.
