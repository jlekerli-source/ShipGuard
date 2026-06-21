# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication report prepare guarded launch relay drafts without posting, submitting, or bypassing explicit human approval?

## Evidence Packet

- Packet status: `pass`
- Required evidence passed: `7/7`
- First blocking gate: `none`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `pass` |
| `launchkey-candidate-packet` | `pass` |
| `downloaded-release-assets` | `pass` |
| `post-release-consumer-proof` | `pass` |
| `independent-adoption-evidence` | `pass` |
| `final-security-review-evidence` | `pass` |

## Closure Checklist

- Checklist status: `pass`
- Remaining blockers: `0`
- No hidden lower-order blockers: `True`

| Rank | Evidence | Status | First | Next command | Proof boundary |
| --- | --- | --- | --- | --- | --- |
| `none` | `none` | `pass` | `False` | `not-needed` | Every stable-publication gate passed. |

## Evidence Templates

- Draft-only templates: `True`

| Template | Exists | Copy command |
| --- | --- | --- |
| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |
| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `none`

## Launch Relay Drafts

- Directory: `stable-publication-launch-relay`
- Draft-only: `True`
- Approval required: `True`
- Public posting allowed: `False`
- Computer-use may post: `False`
- Status: `ready-to-stage`

| File | Purpose |
| --- | --- |
| `stable-publication-launch-relay/README.md` | Synthetic approval boundary. |
| `stable-publication-launch-relay/launch-relay-checklist.json` | Synthetic checklist. |
| `stable-publication-launch-relay/product-hunt-draft.md` | Synthetic Product Hunt draft. |
| `stable-publication-launch-relay/reddit-r-shipguard-draft.md` | Synthetic Reddit draft. |
| `stable-publication-launch-relay/x-thread-draft.md` | Synthetic X draft. |
| `stable-publication-launch-relay/hacker-news-draft.md` | Synthetic HN draft. |

Approval boundary:

Public posting, publishing, submission, or account-visible external actions require explicit human approval for that exact launch run.
