# Policy Configuration

`codex-maintainer` policy files configure how Autopsy treats risky claims, protected areas, and scope size.

Create a default policy:

```bash
./bin/codex-maintainer policy init .codex-maintainer/policy.conf
```

Inspect a policy:

```bash
./bin/codex-maintainer policy show .codex-maintainer/policy.conf
```

Use it with Autopsy:

```bash
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/weak-run/run.md \
  --diff fixtures/autopsy/weak-run/diff.patch \
  --policy fixtures/policy/strict.conf \
  --out /tmp/autopsy-policy
```

## Keys

Policy files are plain `key=value`; they are parsed, not executed.

- `max_changed_files`: maximum diff files before `scope_creep_signal`.
- `protected_patterns`: grep-compatible protected area pattern.
- `validation_claim_patterns`: validation claim pattern.
- `risky_claim_patterns`: high-assurance claim pattern.
- `warn_below`: review-comment warning threshold for downstream gates.
- `fail_below`: review-comment failure threshold for downstream gates.

The default policy lives at `templates/policy/default.conf`.
