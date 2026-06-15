# Swiss Indie Development With Codex

I am a Swiss indie developer building Ringly, an iPhone alarm app focused on trustworthy wake-ups, polished daily routines, and calm product details. Ringly is also my working lab for solo development with AI coding agents: every meaningful change has to move through clear instructions, narrow validation, and reproducible proof.

This public repository shares the reusable workflows I use to collaborate with Codex while building a real mobile app as a solo developer. The goal is not to make AI feel magical. The goal is to make it operational: give the agent enough project context to act safely, make it plan before risky work, constrain it with the right tests, and keep release claims tied to evidence.

## What Is Inside

- An `AGENTS.md` template for mobile-app development with alarm, notification, StoreKit, and release-proof edge cases.
- A `PLANS.md` template that forces objective, affected files, risks, tests, and rollback thinking before large changes.
- Five reusable Codex skills under `.agents/skills`: alarm testing, notification permissions, UI polish, release checklist, and bug triage.
- Scripts and checklists for bug triage, release handoff, and notification/alarm validation.
- A subagent workflow for inspector, implementer, tester, and reviewer roles.
- A mini evaluation suite of realistic Ringly-style issues Codex can solve later.
- Short LinkedIn/X post drafts explaining the workflow.

## Why This Matters

Solo developers have to move fast, but they cannot outsource judgment. Codex is most useful when it is treated like a capable teammate inside a disciplined system: small scopes, explicit constraints, real validation, and honest handoffs when proof is missing.

Ringly is where I test that system. The workflows here are designed for developers who want AI assistance that is repeatable, auditable, and useful in production work, especially when building mobile apps with edge cases that cannot be hand-waved away.

## The Principle

Use AI to increase focus, not chaos. Write down the operating rules. Make the agent show its work. Validate the smallest thing that proves the change. Keep the human accountable for the product.
