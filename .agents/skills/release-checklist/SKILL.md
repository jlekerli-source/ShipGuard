---
name: release-checklist
description: App release-readiness and App Store/TestFlight checklist workflow. Use when preparing release evidence, TestFlight handoff, App Store review, StoreKit proof, release preflight, device release pass, or public-release readiness claims.
---

# Release Checklist

Use this skill to keep release claims tied to proof.

## Steps

1. Read `docs/release-gate.md`, `docs/release-checklist.md`, and `docs/validation-commands.md`.
2. Print the current operator path:

```bash
./scripts/print_release_operator_handoff.sh
./scripts/print_release_status.sh
./scripts/print_testflight_handoff.sh
```

3. Confirm the candidate version/build and source commit. Do not mix local dev, TestFlight, and App Store binaries.
4. Run release preflight only when source scope is final:

```bash
./scripts/run_release_preflight.sh --with-fast-gate
```

5. Add UI gates only when release-wide simulator evidence is required:

```bash
./scripts/run_release_preflight.sh --with-fast-gate --with-ui-gates
```

6. For StoreKit or Premium proof, run:

```bash
./scripts/check_storekit_mapping.sh
./scripts/print_premium_upload_handoff.sh
./scripts/create_premium_live_proof_notes.sh
```

7. For physical-device release proof, use:

```bash
./scripts/begin_device_release_pass.sh --device <udid-or-name>
```

8. Stop on manual blockers. Record the exact operator action instead of rerunning stale local proof.

## Release Claim Rule

Do not say release-ready, submitted, approved, live, or proven unless the matching command, App Store/TestFlight state, proof packet, or operator-provided evidence exists.
