# ShipGuard Agent Trace

`shipguard agent trace` is the Agent Adapter Kernel entry point. It turns an exported or synthetic Codex, Claude, Gemini, Cursor, MCP, or generic agent trace into one reviewable ShipGuard timeline: prompt, tool calls, evidence receipts, optional `shipguard verify` output, verdict, next action, worker-budget state, optional XcodeBuildMCP proof, and optional Expo/EAS assurance proof.

Codex is the first native adapter:

```bash
./bin/shipguard agent trace \
  --trace /tmp/codex-trace.json \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff /tmp/change.diff \
  --evidence /tmp/validation-receipt.json \
  --xcodebuildmcp-evidence /tmp/xcodebuildmcp-proof \
  --expo-eas-evidence /tmp/expo-eas-proof \
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

Non-Codex packaging uses the same command and schema:

```bash
./bin/shipguard agent trace \
  --trace /tmp/claude-trace.json \
  --adapter claude \
  --evidence /tmp/validation-receipt.json \
  --out /tmp/shipguard-claude-trace \
  --shipguard-eval \
  --shareable
```

Supported adapter values are `auto`, `codex`, `claude`, `gemini`, `cursor`, `mcp`, and `generic`. `auto` uses trace metadata and source tokens when they are present; an explicit `--adapter` value wins. Claude, Gemini, Cursor, MCP, and generic traces receive an `adapterPackaging` section that explains the source signals, shared receipt schema, handoff command, and packaging guidance. This keeps ShipGuard agent-neutral without forking its proof model.

Outputs:

- `agent-trace.json`: machine-readable timeline, receipt handoff, verify handoff, adapter packaging, XcodeBuildMCP evidence summary, Expo/EAS assurance summary, findings, slash plan, and slash goal.
- `agent-trace.md`: maintainer-readable summary, including the Agent Packaging section when applicable.
- `agent-trace-receipt.json`: v2 runtime receipt pointing at `agent-trace.json`.

The command is local and deterministic. It does not require a separate API key and it does not modify target apps. When `--shipguard-eval --shareable` is used, the report states the ShipGuard-only product-QA boundary and redacts local absolute paths.

Worker-budget policy:

- Normal ShipGuard work should use 2-3 workers.
- The normal cap is 5 workers.
- Recursive worker spawning is blocked.
- Over-budget traces return a blocked report but still write JSON/Markdown so the maintainer can see the reason and rerun with a smaller plan.

`--run-verify` connects the trace back to the proof-gated task contract. It requires `--task` and `--diff`, passes all `--evidence` receipts to `shipguard verify`, and records the resulting verdict path, status, and next action. Without `--run-verify`, the report remains a trace review and prints the copy-ready verify command.

`--xcodebuildmcp-evidence` attaches proof emitted after Codex uses XcodeBuildMCP or adjacent simulator/profiler tooling. Pass a file or directory containing build/run logs, session-default output, `describe_ui`/`snapshot_ui` JSON, screenshots, runtime logs, `.trace`/Instruments output, or focused profiler notes. The adapter adds `xcodeBuildMCPEvidence`, `taskTrace.xcodeBuildMCPEvidenceTimeline`, and `traceSummary.xcodeBuildMCPEvidenceCount`.

`--expo-eas-evidence` attaches proof emitted after Codex uses Expo MCP, Expo CLI, or EAS tooling. Pass a file or directory containing Expo project metadata, `expo prebuild` output, `eas build` logs, `eas update` receipts, native runtime logs, artifact URLs/checksums, or credential-boundary notes with secrets redacted. The adapter adds `expoEASAssuranceEvidence`, `taskTrace.expoEASAssuranceEvidenceTimeline`, and `traceSummary.expoEASAssuranceEvidenceCount`.

Expo/EAS proof is classified as assurance evidence, not store-distribution proof. Build IDs, update groups, artifact URLs, and runtime logs can support a trace, but App Store, Play Store, TestFlight, physical-device, and production rollout claims still need their own receipts.

ShipGuard treats simulator proof and physical-device proof separately. Simulator names such as `iPhone 15` do not count as physical-device evidence; haptics, thermal behavior, touch latency, and ProMotion claims still need device-route proof or a manual proof boundary.

For Claude, Gemini, Cursor, MCP, and generic traces, the emitted runtime receipt uses `requirementId: universal-agent-packaging-adapter` and includes the `agent-neutral-packaging` scope. That receipt proves packaging compatibility only. It does not prove the target app changed, shipped, passed store review, or ran on a physical device.
