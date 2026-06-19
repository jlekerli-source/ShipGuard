# ShipGuard Agent Trace

`shipguard agent trace` is the Agent Adapter Kernel entry point. It turns an exported or synthetic agent trace into one reviewable ShipGuard timeline: prompt, tool calls, evidence receipts, optional `shipguard verify` output, verdict, next action, and worker-budget state.

Codex is the first native adapter:

```bash
./bin/shipguard agent trace \
  --trace /tmp/codex-trace.json \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --run-verify \
  --out /tmp/shipguard-agent-trace \
  --adapter codex \
  --shipguard-eval \
  --shareable
```

The Codex convenience alias is:

```bash
./bin/shipguard codex trace \
  --trace /tmp/codex-trace.json \
  --out /tmp/shipguard-codex-trace \
  --shipguard-eval \
  --shareable
```

Outputs:

- `agent-trace.json`: machine-readable timeline, receipt handoff, verify handoff, findings, slash plan, and slash goal.
- `agent-trace.md`: maintainer-readable summary.
- `agent-trace-receipt.json`: v2 runtime receipt pointing at `agent-trace.json`.

The command is local and deterministic. It does not require a separate API key and it does not modify target apps. When `--shipguard-eval --shareable` is used, the report states the ShipGuard-only product-QA boundary and redacts local absolute paths.

Worker-budget policy:

- Normal ShipGuard work should use 2-3 workers.
- The normal cap is 5 workers.
- Recursive worker spawning is blocked.
- Over-budget traces return a blocked report but still write JSON/Markdown so the maintainer can see the reason and rerun with a smaller plan.

`--run-verify` connects the trace back to the proof-gated task contract. It requires `--task` and `--diff`, passes all `--evidence` receipts to `shipguard verify`, and records the resulting verdict path, status, and next action. Without `--run-verify`, the report remains a trace review and prints the copy-ready verify command.

The v3.120 boundary is trace adaptation. Simulator/build/profiler evidence remains a typed input until the v3.121 XcodeBuildMCP evidence adapter lands.
