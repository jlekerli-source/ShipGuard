# Security Threat Model

ShipGuard is a local-first workflow kit. Its security boundary is not a hosted service boundary; it is the boundary between a developer's machine, Codex threads, generated proof artifacts, GitHub automation, release assets, and any optional plugin or MCP surface connected to the checkout.

## Scope

This threat model covers:

- `bin/shipguard` and compatibility wrapper execution.
- local report, preview, demo, eval, release-proof, and package artifacts.
- `.agents/plugins/marketplace.json` and `plugins/ios-shipguard`.
- the ShipGuard Devspace MCP/App bridge and local preview screenshot proxy.
- GitHub Actions and local `gh` command workflows.
- Arena, transcript, and release-evidence fixture packs.

It does not claim to audit private Ringly source code, App Store Connect state, live purchase accounts, or physical-device alarm behavior.

## Assets

High-value assets:

- GitHub tokens, OpenAI API keys, App Store Connect credentials, and signing material.
- local workspace paths, user names, bundle IDs, team IDs, and private project names.
- screenshots, simulator state, preview events, handoff prompts, and Codex transcripts.
- release tarballs, release manifests, proof ledgers, replay reports, and evidence bundles.
- plugin metadata and marketplace source paths that tell Codex what code to execute.

## Trust Boundaries

| Boundary | Trusted side | Untrusted or lower-trust side | Required control |
| --- | --- | --- | --- |
| Local checkout to public docs | maintainer-reviewed source | generated reports, copied transcripts, public issues | run redaction and docs checks before publishing |
| Plugin marketplace to Codex cache | tracked `plugins/ios-shipguard` source | stale cache entries and old marketplace names | run `shipguard codex status --strict` after install or refresh |
| Devspace HTTP/MCP bridge to browser clients | loopback process and bearer token | browser widgets, event payloads, screenshot requests | require loopback binding, bounded payloads, screenshot view tokens when auth is enabled |
| CLI artifact writes to filesystem | explicit output directories | arbitrary paths, symlink surprises, cleanup commands | use safe output path checks before destructive cleanup |
| GitHub Actions to repository state | pinned action source and reviewed workflow inputs | user-supplied tags, release URLs, and artifact paths | verify release manifests, digests, and replay output before claims |
| Arena/imported fixtures to benchmark output | reviewed fixture packs | externally supplied fixture paths and run text | import only supported files, reject nested entries and symlinks, keep source metadata path-free, and reject obvious local paths or secret-looking strings |

## Threats And Controls

| Threat | Impact | Current controls | Next check |
| --- | --- | --- | --- |
| Secret or token printed into a public report | credential exposure and account takeover | transcript redaction, iOS redaction, Autopsy `sensitive_data_leak`, safe fixture import checks | keep adding Arena cases for token and path leakage |
| Stale plugin cache with old branding or guidance | Codex executes outdated workflow instructions | `shipguard codex status --strict`, marketplace-backed install docs | require fresh thread after plugin refresh |
| Devspace screenshot or event leak | private app UI or local path exposure | loopback default, optional bearer token, screenshot proxy token, bounded event payloads | test authenticated screenshot access before external tunnels |
| Release proof overclaim | false release readiness or security claim | release manifest, release replay, release consume, autopsy risky-claim and release-trust-gap findings | keep App Store/TestFlight claims blocked without external evidence |
| Unsafe artifact deletion | user data loss outside intended output dirs | `scripts/lib/safe_paths.sh`, Autopsy unsafe-cleanup findings, and package tests | use safe path helpers in new cleanup commands |
| Untrusted fixture pack hides local paths or secrets | benchmark artifact leaks private data | arena import allowlist, overlap checks, symlink/nested-entry rejection, and source-basename metadata | keep importer and pack-signing checks aligned |
| GitHub token overuse in local posting commands | unintended issue, check-run, or release mutation | dry-run options, explicit payload files, `gh auth status` visibility, Autopsy token-scope and network-mutation findings | keep mutation paths disabled by default |
| MCP prompt injection through preview events | Codex follows untrusted UI notes as instructions | handoff text treats events as evidence, not authority | keep target resolution semantic and require user approval for execution |

## Security Rules For Future Work

- Do not add network posting, release publishing, or GitHub mutation paths without a dry-run mode and persisted payload review.
- Do not claim security safety from source inspection alone; use Autopsy, Arena, redaction checks, and explicit residual-risk language.
- Do not copy preview screenshots, event logs, transcripts, or handoff prompts into public artifacts without redaction.
- Do not make the plugin cache the source of truth; tracked plugin source plus status verification is the source of truth.
- Do not run a broad Codex Security scan as a substitute for this threat model. Use this document to route the scan and record findings as follow-up work.

## Phase 4 Proof

Phase 4 is considered started when this document exists and at least one security-focused Arena fixture exercises token, path, or release-trust failure behavior.

The current proof command is:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/shipguard-security-arena
```

The fixtures `fixtures/arena/security-token-leakage`, `fixtures/arena/generated-artifact-cleanup-bypass`, `fixtures/arena/github-posting-without-dry-run`, and `fixtures/arena/release-asset-trust-bypass` are intentionally bad runs. They should remain low-scoring and produce high-risk findings. Autopsy now has dedicated findings for unredacted local paths, secret-looking tokens, bearer values, secret assignments, unsafe generated artifact cleanup, broad GitHub token scopes, network mutation without dry-run review, and release artifact verification bypasses in run, task, diff, or test evidence.
