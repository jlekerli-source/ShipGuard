# Next Goal Generator

`shipguard next-goal` emits deterministic slash-plan and slash-goal release guidance.

Use it after a release is verified:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```

The generated file includes:

- an exact `/plan` block for the next release
- an exact `/goal` block for the next release
- optional bounded scope and completion receipt sections
- an optional following `/goal` handoff after completion evidence is supplied
- release constraints
- required proof commands
- the iOS report-quality proof lane for `ios performance`, `ios design`, modernize, app-intelligence, AI-readiness, eval, demo, and goal-loop helpers
- the publish-and-verify loop
- the command to generate the following goal

Override the target release or title when needed:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "SARIF Evidence Export" \
  --out /tmp/next-goal.md
```

The command does not open issues, commit, push, or publish releases. It creates auditable `/plan` and `/goal` blocks that a maintainer can review before starting the next loop.

When the improvement scope is already known, include it directly in the slash-plan:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "Scoped Goal Handoff" \
  --scope "Make next-goal emit scoped plans and completion receipts." \
  --out /tmp/scoped-next-goal.md
```

After a slice is complete, pass the proof receipt to emit the completion record and the following `/goal` handoff:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "Scoped Goal Handoff" \
  --scope "Make next-goal emit scoped plans and completion receipts." \
  --completion-evidence "./tests/next_goal_test.sh and ./tests/package_release_test.sh passed" \
  --following-title "Next Reliability Slice" \
  --out NEXT_GOAL.md
```

The completion receipt is caller-supplied evidence. It does not mark work complete by itself; the maintainer still has to run and review the proof commands.
