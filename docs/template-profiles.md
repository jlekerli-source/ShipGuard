# Template Profiles

`shipguard init` supports workflow starter profiles for different app types.

Every profile writes a target-repo `SHIPGUARD_PROFILE.md` next to `AGENTS.md`. That file is the developer-facing handoff for the selected starter profile: first commands, profile intent, and the next local customization work before using Codex on production code.

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
./bin/shipguard web audit --path ../my-web-app --out /tmp/shipguard-web-audit --shareable
./bin/shipguard web plan --report /tmp/shipguard-web-audit --target ../my-web-app --out /tmp/shipguard-web-plan --shareable
```

The web profile copies the shared maintainer workflow files, `SHIPGUARD_PROFILE.md`, and a web-specific `AGENTS.md` that covers routing, auth, payments, migrations, browser validation, and build proof. ShipGuard WebScan turns that starter state into a read-only first audit with framework, auth/payment, validation, starter-health, and next-command evidence. ShipGuard WebForge then turns the audit into scoped tasks, validation commands, stop conditions, and report-quality questions without editing the target repo.

## Backend

```bash
./bin/shipguard init backend ../my-service
./bin/shipguard doctor backend ../my-service
./bin/shipguard backend audit --path ../my-service --out /tmp/shipguard-backend-audit --shareable
./bin/shipguard backend plan --report /tmp/shipguard-backend-audit --target ../my-service --out /tmp/shipguard-backend-plan --shareable
```

The backend profile writes `SHIPGUARD_PROFILE.md` and covers API endpoints, auth boundaries, migrations, queues, jobs, webhooks, observability, rollout risk, and operational proof. ShipGuard ServiceRadar turns those signals into a read-only first audit with validation guidance and backend-specific next commands. ShipGuard ServiceForge then turns the audit into scoped backend tasks, validation commands, stop conditions, and report-quality questions without contacting services or editing code.

## CLI

```bash
./bin/shipguard init cli ../my-tool
./bin/shipguard doctor cli ../my-tool
./bin/shipguard cli audit --path ../my-tool --out /tmp/shipguard-cli-audit --shareable
./bin/shipguard cli plan --report /tmp/shipguard-cli-audit --target ../my-tool --out /tmp/shipguard-cli-plan --shareable
```

The CLI profile writes `SHIPGUARD_PROFILE.md` and covers command dispatch, argument parsing, file safety, stdout and stderr contracts, exit codes, token redaction, cross-platform behavior, and package proof. ShipGuard CommandLens turns those signals into a read-only first audit with contract, redaction, packaging, validation, and next-command guidance. ShipGuard CommandForge then turns the audit into scoped CLI contract tasks, smoke checks, validation commands, stop conditions, and report-quality questions without executing the target CLI.

## Compatibility

These commands remain valid:

```bash
./bin/shipguard init ios ../my-ios-app
./bin/shipguard doctor ../my-ios-app
```

`doctor` without a profile defaults to `ios` for compatibility with older releases.
