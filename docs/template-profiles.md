# Template Profiles

`shipguard init` supports workflow starter profiles for different app types.

## iOS

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard doctor ios ../my-ios-app
```

The iOS profile includes alarm, notification, release, bug-triage, and UI-polish skills. Each starter skill also carries ShipGuard QA hooks so `shipguard value-gauntlet` can verify it has command examples, validation language, docs linkage, and test coverage.

| Skill | Path | Primary use |
| --- | --- | --- |
| alarm-testing | `.agents/skills/alarm-testing/SKILL.md` | Alarm runtime and wake-path proof routing. |
| notification-permissions | `.agents/skills/notification-permissions/SKILL.md` | Notification, AlarmKit, fallback, and permission-truth checks. |
| release-checklist | `.agents/skills/release-checklist/SKILL.md` | Release readiness, TestFlight handoff, and proof claims. |
| bug-triage | `.agents/skills/bug-triage/SKILL.md` | Bug report classification before implementation. |
| ui-polish | `.agents/skills/ui-polish/SKILL.md` | UI/UX polish with accessibility, localization, and visual-proof boundaries. |

## Web

```bash
./bin/shipguard init web ../my-web-app
./bin/shipguard doctor web ../my-web-app
```

The web profile copies the shared maintainer workflow files and a web-specific `AGENTS.md` that covers routing, auth, payments, migrations, browser validation, and build proof.

## Backend

```bash
./bin/shipguard init backend ../my-service
./bin/shipguard doctor backend ../my-service
```

The backend profile covers API endpoints, auth boundaries, migrations, queues, jobs, webhooks, observability, rollout risk, and operational proof.

## CLI

```bash
./bin/shipguard init cli ../my-tool
./bin/shipguard doctor cli ../my-tool
```

The CLI profile covers command dispatch, argument parsing, file safety, stdout and stderr contracts, exit codes, token redaction, cross-platform behavior, and package proof.

## Compatibility

These commands remain valid:

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard doctor ../my-ios-app
```

`doctor` without a profile defaults to `ios` for compatibility with older releases.
