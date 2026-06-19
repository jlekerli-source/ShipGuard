# GitHub Presentation

ShipGuard's GitHub surface should explain the product quickly, without making it look like a private-app helper or an unfinished pile of internal tools.

## Current Public State

- Latest published release: `v3.131.0`.
- Current CLI version in this checkout: read from `VERSION`.
- Product name: ShipGuard.
- Contributor and maintainer workspace name: ShipGuard ShipYard.
- Public promise: local-first CLI plus Codex plugin for proof-gated app maintenance.
- Template status: enabled on GitHub, so the repo shows `Use this template`.
- Active `main` state: later ShipYard stabilization slices harden LaunchKey native GitHub release-asset download, published-release asset proof, package fresh-install receipts, same-prefix upgrade receipts, rollback cleanup receipts, generated archive-member screening, blocking-proof result UX, and report-quality exclusion for generated proof directories; present them as active hardening, not as a new published release.
- Stable claim boundary: v4 is not stable until release-candidate, schema, package, security, install, rollback, and release-proof consumption evidence all pass on published assets.

Use this command pair before changing the GitHub presentation:

```bash
./bin/shipguard version
gh release list --limit 5
```

## Repository About Box

Recommended description:

```text
Local-first CLI and Codex plugin for proof-gated app maintenance.
```

Longer alternative:

```text
ShipGuard turns AI-assisted app work into scoped tasks, evidence receipts, review verdicts, and release proof.
```

Recommended topics:

```text
swift
ios
xcode
openai
codex
developer-tools
ai-agents
workflow-automation
mobile-development
ios-development
release-engineering
open-source
```

Recommended sidebar links:

- Website: leave blank until GitHub Pages is enabled, or use `https://github.com/jlekerli-source/ShipGuard`.
- Documentation: `docs/index.md`.
- Latest release: `https://github.com/jlekerli-source/ShipGuard/releases/latest`.

Owner/admin action: GitHub repository description, topics, template status, and social preview are GitHub settings. The description, topics, and template flag are currently set; social preview upload still requires the GitHub web UI.

## README Lead

The README should open with the tracked icon, centered product name, and one plain sentence:

```html
<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="96" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Local-first CLI + Codex plugin for proof-gated app maintenance.
</p>
```

Keep the first visible paragraphs app-neutral. Do not mention Ringly, Ilmify, private app paths, private screenshots, or private report snippets in the GitHub lead.

## Social Preview And Icon

Tracked asset:

```text
.github/assets/shipguard-icon.png
```

Use the tracked icon for the README logo and, if a simple presentation is preferred, for the GitHub social preview. GitHub social preview upload is a repository settings action:

```text
Settings -> General -> Social preview -> Upload .github/assets/shipguard-icon.png
```

Do not generate CSS/SVG mock art for the social preview. Use the icon until a stronger product screenshot or real generated brand asset exists; do not keep unused preview mockups in the repo.

## Release Page Copy

Use the latest shipped capability as the release headline. For `v3.131.0`, the release story is:

```text
ShipGuard v3.131.0 adds V4 Release Candidate Readiness / LaunchKey: fresh install, package-tarball fresh-install proof, upgrade, uninstall, release-proof consumption, external adoption packet, final schema docs, plugin refresh proof, release-readiness commands, and blocked stable-v4 claims.
```

Mention supporting context only after the headline:

- `v3.130.0`: V4 Schema Freeze and compatibility policy.
- `v3.129.0`: V4 Preview stabilization.
- `v3.128.0`: External Benchmark v2.
- `v3.127.0`: Codex marketplace readiness.
- `v3.126.0`: concise result UX.
- `v3.125.0`: unified InspectDeck.

Do not call v4 stable on the release page until the stable-v4 gate is actually published and consumed from release assets.

For active `main` updates after `v3.131.0`, use a short maintenance note rather than rewriting the release headline:

```text
Main now carries LaunchKey hardening for native GitHub release-asset download, published-release asset proof, fresh-install package receipts, same-prefix upgrade receipts, rollback cleanup receipts, generated archive-member screening, blocking-proof result UX, and report-quality exclusion of generated proof directories. These are v4 stabilization slices, not a stable-v4 release claim.
```

## Refresh Checklist

Run this local presentation proof before publishing or announcing a GitHub refresh:

```bash
./bin/shipguard codex marketplace-readiness --path . --out /tmp/shipguard-marketplace --strict --shareable
./bin/shipguard docs-check . --out /tmp/shipguard-docs-check
./bin/shipguard brand --path . --out /tmp/shipguard-brand --strict
```

If these pass, update the live GitHub sidebar and social preview manually if needed, then verify the public repo page visually.
