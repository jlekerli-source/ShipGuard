# Open Source Operating Model

ShipGuard is open source, MIT licensed, and local-first. The public repository should be useful without private app code, private screenshots, hosted credentials, or a paid service.

## What Is Public

- CLI source, scripts, tests, fixtures, and release packaging.
- Codex plugin metadata, skills, MCP launcher configuration, and Devspace source.
- Public demo iOS fixtures and report-quality cases.
- GitHub Actions for validation, report comparison, transcript checks, and release evidence.
- Docs for adoption, privacy, security, release proof, and contribution workflow.

## What Stays Private

- Real app source unless the app owner explicitly publishes it.
- App Store Connect credentials, Apple team IDs, user data, device IDs, tokens, and local absolute paths.
- Private screenshots unless the owner explicitly approves sharing.
- Raw real-app report artifacts that have not been generated with `--shareable` and redacted when needed.

## Native ShipGuard Model

ShipGuard should learn from mature open-source developer tools without copying their code, text, or product shape. The native model is:

- Local CLI first.
- Codex plugin and skill layer second.
- Public fixtures and evals for repeatable quality.
- Release artifacts that can be consumed and verified downstream.
- Private-app learning converted into public-safe rules, docs, and fixtures.

## Contributor Path

1. Read `CONTRIBUTING.md`, `GOVERNANCE.md`, `SECURITY.md`, and `SUPPORT.md`.
2. Choose the smallest public fixture, doc, test, or command change that proves the problem.
3. Run the narrowest validation command that proves the change.
4. Include the exact command output or blocked-proof note in the pull request.
5. Keep private app evidence out of the PR unless it is redacted and explicitly approved for publication.

## Project Health Goals

- Every public command has docs and tests.
- Every report that can leave the machine has a shareability and redaction story.
- Every plugin install path has a status command that proves what Codex will load.
- Every release can be checked from the downloaded tarball.
- Every private-app product-QA lesson can become a public fixture before it becomes a permanent rule.
