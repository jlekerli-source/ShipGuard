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

Outputs:

- `v4-release-candidate.json`
- `v4-release-candidate.md`

## Proof Contract

The command checks these gates:

- Fresh install proof: a release package can install to a clean prefix and run validation from that prefix.
- Upgrade proof: an existing install can be replaced by the candidate package and still report the intended version.
- Uninstall proof: temporary install state can be removed cleanly without hidden required state.
- Release proof consumption: downloaded release assets can pass `shipguard release-consume verify`.
- External adoption packet: an outside developer can see the first command, proof bundle, support boundary, and non-claims.
- Final schema docs: v4 schema-freeze docs remain linked and visible.
- Plugin refresh proof: local Codex plugin refresh and `shipguard codex status --strict` remain part of the release lane.

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
```

## Blocked Claims

Passing this report means ShipGuard is candidate-ready. It does not mean:

- ShipGuard v4 is a stable product release.
- OpenAI accepted ShipGuard into a public marketplace.
- External adoption has been proven by independent users.
- Any private app has been validated.
- Physical-device iOS behavior has been proven.
