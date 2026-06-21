# ShipGuard V4 Stable Publication Proof

`shipguard v4 stable-publication` is the final local proof gate before anyone says ShipGuard v4 is stable.

It does not publish a GitHub release, change repository rules, edit target apps, or claim marketplace acceptance. It reads public release metadata, release notes, a prior LaunchKey release-candidate report, release assets, adoption evidence, and security-review evidence, then blocks stable-v4 claims until the full packet passes.

## Command

```bash
./bin/shipguard v4 stable-publication \
  --path . \
  --out /tmp/shipguard-v4-stable-publication \
  --release-version <version> \
  --release-candidate-report <v4-release-candidate-json-or-dir> \
  --download-release-assets \
  --external-adoption-evidence <evidence-json-or-dir> \
  --security-review-evidence <evidence-json-or-dir> \
  --shipguard-eval \
  --shareable
```

When `--github-release-repo` is omitted, ShipGuard tries to infer `<owner/repo>` from the target repo's `origin` remote. Pass the flag explicitly when validating a fork, mirror, fixture API, or non-`origin` publication target.

If release assets were already downloaded:

```bash
./bin/shipguard v4 stable-publication \
  --path . \
  --out /tmp/shipguard-v4-stable-publication \
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
- `stable-publication-evidence-kit/README.md`
- `stable-publication-evidence-kit/stable-publication-checklist.json`
- `stable-publication-evidence-kit/external-adoption-evidence.json`
- `stable-publication-evidence-kit/security-review-evidence.json`
- `stable-publication-release-notes/README.md`
- `stable-publication-release-notes/release-notes-checklist.json`
- `stable-publication-release-notes/draft-release-notes.md`
- `stable-publication-launch-relay/README.md`
- `stable-publication-launch-relay/launch-relay-checklist.json`
- `stable-publication-launch-relay/product-hunt-draft.md`
- `stable-publication-launch-relay/reddit-r-shipguard-draft.md`
- `stable-publication-launch-relay/x-thread-draft.md`
- `stable-publication-launch-relay/hacker-news-draft.md`
- `stablePublicationEvidencePacket` in JSON, rendered as `Evidence Packet` in Markdown
- `stablePublicationClosureChecklist` in JSON, rendered as `Closure Checklist` in Markdown
- `stablePublicationEvidenceTemplates` in JSON, rendered as `Evidence Templates` in Markdown
- `stablePublicationEvidenceStarterKit` in JSON, rendered as `Evidence Starter Kit` in Markdown
- `stablePublicationReleaseNotesAuthoringKit` in JSON, rendered as `Release Notes Authoring Kit` in Markdown
- `stablePublicationLaunchRelayDrafts` in JSON, rendered as `Launch Relay Drafts` in Markdown

## Stable Gates

The report returns `pass` only when every gate passes:

- GitHub release metadata exists for the requested tag, is not draft/prerelease, and includes the required release assets.
- Release notes pass the stable-publication topic matrix: stable-v4 claim, publication-proof boundary, downloaded release assets, post-release consumer proof, independent adoption evidence, final security review evidence, and non-claim boundaries.
- The supplied `v4 release-candidate` report is from LaunchKey, passed, and still claims only `candidate-ready`.
- Downloaded or supplied release assets pass `shipguard release-consume verify`.
- Post-release consumer proof is attached from the release assets.
- External adoption evidence passes the stable-v4 gate with independent public or redacted external records.
- Final security-review evidence passes the stable-v4 gate with CLI, plugin, GitHub Actions, release-proof, package-install, and redaction/privacy scope coverage.

If any gate fails, the report returns `review`, sets `stableV4Release` to `false`, and puts the next command in `resultUX.nextCommand`.

## Release Notes Proof

`releaseNotesProof` is a structured gate, not a keyword vibe check. The report analyzes the full GitHub release body, records a SHA-256 digest, counts lines, and emits `topicMatrix` plus `missingTopicIds`.

The release notes must mention:

- the stable-v4 release claim
- the publication or release-proof boundary
- downloaded release assets
- post-release consumer proof
- independent adoption evidence
- final security-review evidence
- non-claims or blocked claims

Markdown renders the same matrix under `Release Notes Proof` so maintainers can fix the public release text without reading JSON.

## Release Notes Authoring Kit

Every run also writes `stable-publication-release-notes/` inside the report directory.

This directory is a draft-only authoring aid, not proof that the public GitHub release was edited. It contains:

- `README.md` with public-release-body rules and the rerun command
- `release-notes-checklist.json` with the same topic matrix and missing topic IDs from `releaseNotesProof`
- `draft-release-notes.md` with a copy-ready stable-publication section covering release assets, post-release consumer proof, independent adoption, final security review, and non-claims

The report exposes the same artifact as `stablePublicationReleaseNotesAuthoringKit`, and Markdown renders it under `Release Notes Authoring Kit`. `ios report-quality` flags stable-publication reports that expose release-note gaps but do not give maintainers a draft/checklist path to fix the public release body.

The generated release-notes directory is an authoring attachment, not a separate source report. `ios report-quality` grades the root `v4-stable-publication.json` report and skips the generated checklist during recursive report discovery.

## Launch Relay Drafts

Every run also writes `stable-publication-launch-relay/` inside the report directory.

This directory is a draft-only launch packet for Product Hunt, r/ShipGuard, X, and Hacker News style announcements. It does not publish, submit, post, schedule, or perform account-visible external actions.

The packet contains:

- `README.md` with launch guardrails and the approval boundary
- `launch-relay-checklist.json` with `approvalRequired: true`, `publicPostingAllowed: false`, and `computerUseMayPost: false`
- `product-hunt-draft.md`
- `reddit-r-shipguard-draft.md`
- `x-thread-draft.md`
- `hacker-news-draft.md`

Public posting, publishing, submission, scheduling, browser-field staging with account side effects, or any other account-visible external action requires explicit human approval for that exact launch run. Computer-use may help prepare drafts or stage fields only after that approval; it must not post by default.

`ios report-quality` flags stable-publication reports that declare launch-relay actionability but hide the draft-only packet, omit the approval gate, allow public posting by default, or fail to render the approval boundary in Markdown.

## Evidence Packet

The JSON report includes `stablePublicationEvidencePacket` so humans and tools can inspect the real publication packet without piecing it together from scattered sections. It lists:

- all seven required evidence inputs with stable IDs and statuses
- whether each input is required for stable v4 and must be real evidence
- `missingEvidenceIds`
- `firstBlockingGate` with the exact next command
- proof order from LaunchKey candidate proof to published release proof
- non-claims for marketplace acceptance, fixture-only proof, and GitHub download counts

When the supplied LaunchKey report is blocked by package proof, stable publication preserves the nested blocker in `releaseCandidatePacketProof.launchKeyBlockingProof` and mirrors it into the candidate evidence row. For package hygiene failures this includes the blocked receipt, failure evidence, first hygiene rule, tarball/member, blocked-finding count, and the `shipguard release-package hygiene` reproducer command. Markdown renders the same details under `LaunchKey Candidate Blocker` so a maintainer does not have to open the nested candidate JSON before acting.

`ios report-quality` checks this packet. A stable-publication report that has the gates but hides the packet receives a report-quality issue.

## Closure Checklist

`stablePublicationClosureChecklist` turns the evidence packet into the maintainer's ordered closing list.

It includes:

- every non-passing stable-publication evidence gate in dependency order
- the first blocking gate marker without hiding later blockers
- an exact `nextCommand` for each remaining blocker
- proof-boundary language for what real evidence must pass
- `noHiddenLowerOrderBlockers` so report-quality can detect summaries that stop at only the first failure

Markdown renders the same table under `Closure Checklist`. A passing stable-publication report has zero checklist items; a blocked report must mirror every non-passing `stablePublicationEvidencePacket.requiredEvidence` row.

When release notes are a closure blocker, the release-notes row also carries a closure kit:

- `missingTopicIds` copied from `releaseNotesProof`
- `authoringKitPaths` for the generated README, checklist JSON, and draft release notes
- `publicGitHubReleaseEditBoundary`, which states that ShipGuard does not edit the public GitHub release body and the generated files are draft-only
- `rerunCommand`, the stable-publication command to run after editing the public release notes

Markdown renders those fields as `Release Notes Closure Kit` so the first blocker can be closed without opening nested JSON.

When independent adoption or final security-review evidence is a closure blocker, the row also carries an evidence closure kit:

- the generated starter file path and source template path
- accepted `evidenceClass` values and required JSON fields
- required security scope for final security review evidence
- redaction and privacy boundaries, including private path, app identifier, screenshot, token, and account-data exclusions
- pass criteria and common fail criteria, including unchanged templates, missing redaction, fixture evidence, missing security scope, and open critical/high findings
- current diagnostics from the supplied evidence proof, such as record counts, first error, missing fields, and missing security scope
- `rerunCommand`, the stable-publication command to run after attaching real adoption/security evidence

Markdown renders these fields as `Evidence Closure Kit: <evidence-id>` so maintainers can close the adoption/security blockers without reverse-engineering template JSON or nested proof records.

## Evidence Starter Kit

Every run also writes `stable-publication-evidence-kit/` inside the report directory.

This directory is a convenience artifact, not proof. It contains:

- `README.md` with the collection rules and next command template
- `stable-publication-checklist.json` with the current seven-gate packet, closure checklist, first blocker, missing evidence IDs, and non-claims
- `external-adoption-evidence.json` copied from the draft-only adoption template
- `security-review-evidence.json` copied from the draft-only security-review template

The report exposes the same information in `stablePublicationEvidenceStarterKit`. `ios report-quality` flags stable-publication reports that do not write or render this starter kit, because the final publication gate should be actionable without making maintainers reverse-engineer JSON shapes from source code.

Starter-kit files are intentionally not pass-ready. Fill them with real reviewed evidence, redact private details, and pass the completed files back with `--external-adoption-evidence` and `--security-review-evidence`.

## Evidence Templates

Stable publication also exposes draft-only evidence templates:

- `templates/stable-publication/external-adoption-evidence.template.json`
- `templates/stable-publication/security-review-evidence.template.json`

The report includes those paths, accepted evidence classes, required fields, copy commands, and validation commands in `stablePublicationEvidenceTemplates`. The adoption and security entries inside `stablePublicationEvidencePacket.requiredEvidence` also link back to their template path and copy command.

These templates are intentionally not pass-ready. They default to `status: draft`, `privateDataRedacted: false`, and consent fields that must be reviewed before the record can pass. Copy them into a private evidence directory, replace placeholder text with real reviewed evidence, redact local paths/private app details/token-like strings/account data, then pass the completed file or directory to `--external-adoption-evidence` or `--security-review-evidence`.

Example:

```bash
mkdir -p /tmp/shipguard-stable-evidence
cp templates/stable-publication/external-adoption-evidence.template.json /tmp/shipguard-stable-evidence/external-adoption-evidence.json
cp templates/stable-publication/security-review-evidence.template.json /tmp/shipguard-stable-evidence/security-review-evidence.json
```

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
