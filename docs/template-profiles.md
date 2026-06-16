# Template Profiles

`codex-maintainer init` supports workflow starter profiles for different app types.

## iOS

```bash
./bin/codex-maintainer init ios ../my-ios-app
./bin/codex-maintainer doctor ios ../my-ios-app
```

The iOS profile includes alarm, notification, release, bug-triage, and UI-polish skills.

## Web

```bash
./bin/codex-maintainer init web ../my-web-app
./bin/codex-maintainer doctor web ../my-web-app
```

The web profile copies the shared maintainer workflow files and a web-specific `AGENTS.md` that covers routing, auth, payments, migrations, browser validation, and build proof.

## Backend

```bash
./bin/codex-maintainer init backend ../my-service
./bin/codex-maintainer doctor backend ../my-service
```

The backend profile covers API endpoints, auth boundaries, migrations, queues, jobs, webhooks, observability, rollout risk, and operational proof.

## CLI

```bash
./bin/codex-maintainer init cli ../my-tool
./bin/codex-maintainer doctor cli ../my-tool
```

The CLI profile covers command dispatch, argument parsing, file safety, stdout and stderr contracts, exit codes, token redaction, cross-platform behavior, and package proof.

## Compatibility

These commands remain valid:

```bash
./bin/codex-maintainer init ios ../my-ios-app
./bin/codex-maintainer doctor ../my-ios-app
```

`doctor` without a profile defaults to `ios` for compatibility with older releases.
