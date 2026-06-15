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
