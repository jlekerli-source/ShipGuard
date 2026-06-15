#!/usr/bin/env bash

set -euo pipefail

cat <<'CHECKLIST'
Ringly release checklist

Read first:
  - docs/release-gate.md
  - docs/release-checklist.md
  - docs/validation-commands.md

Local proof:
  - git diff --check
  - ./scripts/ci_validate.sh fast
  - ./scripts/run_onboarding_validation.sh
  - ./scripts/run_alarm_ui_batches.sh alarm-home-smoke
  - ./scripts/run_alarm_ui_batches.sh all
  - ./scripts/check_storekit_mapping.sh
  - ./scripts/check_shared_store_integrity.sh

Release handoff:
  - ./scripts/print_release_operator_handoff.sh
  - ./scripts/print_release_status.sh
  - ./scripts/print_testflight_handoff.sh
  - ./scripts/run_release_preflight.sh --with-fast-gate
  - ./scripts/run_release_preflight.sh --with-fast-gate --with-ui-gates

Device proof:
  - ./scripts/push_to_device.sh --list
  - ./scripts/push_to_device.sh --status --device <udid-or-name>
  - ./scripts/begin_device_release_pass.sh --device <udid-or-name>

Stop instead of guessing when blocked by:
  - TestFlight install or tester action
  - App Store Connect credentials or review state
  - live StoreKit account proof
  - privacy/legal review
  - physical-device access
CHECKLIST
