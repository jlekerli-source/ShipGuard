# Next Goal Generator

`shipguard next-goal` emits deterministic slash-plan and slash-goal release guidance.

Use it after a release is verified:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```

The generated file includes:

- an exact `/plan` block for the next release
- an exact `/goal` block for the next release
- a version lineage check that compares `VERSION`, the expected next release, the planned target, the current pre-bump package artifact, and the expected post-bump artifact
- optional bounded scope and completion receipt sections
- an optional following `/plan` and `/goal` handoff after completion evidence is supplied
- release constraints
- required proof commands
- Brand Deck strict proof so public surface naming changes stay covered by `shipguard brand`
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

If `--release` skips ahead of the next semantic release from `VERSION`, the generated `Version Lineage Check` is `review`. That is allowed for planning handoffs, but a real package publish still needs either a `VERSION` bump to the planned release or a regenerated goal for the next `VERSION`-based release. In that state the slash plan, slash goal, and release loop stop at version-lineage resolution instead of telling the maintainer to publish a tarball that the current checkout cannot build.

Even when the planned release is the expected next release, the current checkout still builds the current `VERSION` until the release bump is made. The lineage check therefore shows both the current pre-bump artifact and the expected post-bump artifact.

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

When you are generating the next release goal after finishing a previous release, keep the next bounded scope separate from the completed scope:

```bash
./bin/shipguard next-goal \
  --release 2.3.0 \
  --title "Notification Permission Workflow" \
  --scope "Add the next notification permission workflow." \
  --completed-scope "v2.2.0 diff-first verification verdict shipped." \
  --completion-evidence "release proof and consumer verification passed" \
  --following-title "External Pilot Verdict Bench" \
  --out NEXT_GOAL.md
```
