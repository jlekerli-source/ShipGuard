# Posts And Outreach Drafts

## 1. How I use Codex as a solo Swiss indie dev building Ringly

I am building Ringly as a solo Swiss indie developer, and Codex has become part of my daily workflow.

The biggest lesson: AI coding works best when it has constraints.

For Ringly, I give Codex repo-specific instructions, make it plan risky changes, route each task to the smallest useful validation command, and keep release claims tied to evidence.

It is not "ask AI to build an app."

It is more like: define the operating system for an AI teammate, then keep human judgment in the loop.

I am starting to share the reproducible workflows behind that setup for other solo developers building real products.

## 2. My AGENTS.md setup for mobile-app development

My `AGENTS.md` setup for Ringly is built around one rule: alarm trust comes before everything else.

The file tells Codex:

- where the app, widgets, website, tests, and release evidence live
- which scripts are the source of truth for build and validation
- which files are protected alarm-runtime areas
- when to run focused UI lanes vs fast CI
- when to stop and ask for manual TestFlight, StoreKit, or device proof

The result is not perfect automation. It is safer collaboration.

Good agent instructions reduce ambiguity, prevent broad refactors, and make AI-generated changes easier to review.

## 3. Codex vs manual coding: one real Ringly bug from issue to tested fix

A real Ringly bug workflow looks like this:

1. Capture the failure clearly.
2. Ask Codex to inspect the smallest affected area.
3. Force a plan: objective, files, risks, tests, rollback.
4. Implement the fix in one narrow slice.
5. Run the routed validation command, not every test in the repo.
6. Review the diff like a human engineer.

Example: a quick-alarm UI test can intermittently fail to find the Power Nap action from an empty alarm state.

That is a good Codex task because the expected behavior is clear, the failure is reproducible enough to benchmark, and the fix should improve both product accessibility identifiers and test determinism.

AI helps most when the workflow turns vague bugs into bounded engineering tasks.

## 4. Reddit draft: ShipGuard, a Codex plugin for risky iOS maintenance

Title:

I built a Codex plugin/workflow kit for safer solo iOS maintenance

Body:

I have been using Codex heavily while building Ringly, an iPhone alarm app where reliability matters more than speed.

The hardest part was not getting AI to write code. It was getting it to behave like a careful maintainer:

- route risky tasks before editing
- avoid touching protected runtime files without explicit scope
- ask permission and StoreKit questions before making assumptions
- choose the smallest validation command that proves the change
- keep release claims tied to real evidence
- hand off blocked work clearly when TestFlight, devices, App Store Connect, or human review are required

I turned that operating layer into ShipGuard, an open-source Codex workflow kit and local `ios-shipguard` plugin.

It includes:

- an `AGENTS.md` template for iOS apps
- Codex skill guidance for permissions, notifications, AlarmKit, widgets, App Intents, StoreKit, background modes, Live Activities, simulator proof, and release readiness
- a `shipguard` CLI for validation, project inventory, iOS planning, proof routing, release evidence, transcript redaction, and AI-run autopsy reports
- GitHub Actions and fixture-based evals for checking whether agent claims match actual proof

The goal is not "AI ships my app for me."

The goal is to make AI-assisted coding more repeatable, reviewable, and honest for real product maintenance.

Local install from the repo:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
./bin/shipguard codex status --strict
```

Repo:

https://github.com/jlekerli-source/ShipGuard

I would be interested in feedback from other solo iOS devs or maintainers using coding agents on production apps. What proof gates or "never edit without asking" rules have you added to your own workflow?

## 5. LinkedIn draft: ShipGuard plugin launch

I have been turning the Codex workflow behind Ringly into something reusable.

Ringly is an iPhone alarm app, so the development process has to treat reliability, permissions, notifications, StoreKit, widgets, and release evidence as first-class product concerns. For that kind of app, the useful question is not just "can AI write the code?"

It is:

Can the agent understand risk before editing?
Can it ask the right product questions?
Can it choose the right validation lane?
Can it avoid making release claims without proof?
Can another maintainer review what happened later?

That is the reason I built ShipGuard.

ShipGuard is an open-source Codex workflow kit and local `ios-shipguard` plugin for solo iOS developers working on apps where user trust matters. It packages the operating layer I use around Ringly: agent instructions, planning templates, validation routing, release checklists, GitHub Actions, CLI tools, evidence bundles, and eval fixtures.

The plugin focuses Codex before the code changes happen. It routes risky iOS work across permissions, notifications, AlarmKit, widgets, App Intents, StoreKit, background modes, Live Activities, simulator proof, and release readiness. The CLI then helps generate inventory, proof routes, release artifacts, redaction reports, and autopsy checks for AI-assisted runs.

The point is not to replace engineering judgment. It is to make AI-assisted maintenance more explicit, auditable, and useful.

The repo is here:

https://github.com/jlekerli-source/ShipGuard

I am especially interested in how other developers are designing proof gates around AI coding agents for production software.
