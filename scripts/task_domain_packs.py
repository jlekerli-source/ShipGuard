#!/usr/bin/env python3
"""Domain-pack hooks for ShipGuard task contracts."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol


IOS_PERMISSION_SOURCE_TOKENS = (
    "UNUserNotificationCenter",
    "requestAuthorization",
    "authorizationStatus",
    "notDetermined",
    "denied",
    "authorized",
    "provisional",
    "UIApplication.openSettingsURLString",
)


@dataclass(frozen=True)
class DomainPackContext:
    root: Path
    shareable: bool
    snapshot_file_limit: int
    rel: Callable[[Path], str]
    redact_path: Callable[[str], str]
    should_skip_dir: Callable[[str], bool]


class DomainPack(Protocol):
    id: str
    version: str

    def build_prepare_risk_pack(self, contract: dict[str, Any], context: DomainPackContext) -> dict[str, Any] | None:
        ...

    def evaluate_verify(
        self,
        task: dict[str, Any],
        diff_files: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
        coverage: dict[str, Any],
    ) -> dict[str, Any] | None:
        ...


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def notification_permission_goal(goal: str) -> bool:
    lowered = goal.lower()
    return any(token in lowered for token in ("notification", "permission", "authorization", "denied", "provisional"))


def permission_candidate_signal(path: Path, context: DomainPackContext) -> list[str]:
    signals: list[str] = []
    relative = context.rel(path)
    lowered_path = relative.lower()
    if any(token in lowered_path for token in ("notification", "permission", "authorization", "onboarding")):
        signals.append("path references notification, permission, authorization, or onboarding")
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        text = ""
    lowered_text = text.lower()
    for token in IOS_PERMISSION_SOURCE_TOKENS:
        if token.lower() in lowered_text:
            signals.append(f"source references {token}")
    return signals[:6]


def discover_permission_candidates(context: DomainPackContext) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    scanned = 0
    for current_root, dirs, files in os.walk(context.root):
        kept_dirs = []
        for directory in dirs:
            if context.should_skip_dir(directory) or directory.endswith(".xcresult"):
                continue
            kept_dirs.append(directory)
        dirs[:] = kept_dirs
        current = Path(current_root)
        for filename in files:
            if not filename.endswith((".swift", "Info.plist", ".plist", ".entitlements")):
                continue
            scanned += 1
            if scanned > context.snapshot_file_limit:
                dirs[:] = []
                break
            path = current / filename
            signals = permission_candidate_signal(path, context)
            if not signals:
                continue
            candidates.append({"path": context.redact_path(context.rel(path)), "signals": signals})
            if len(candidates) >= 16:
                dirs[:] = []
                break
        if len(candidates) >= 16 or scanned > context.snapshot_file_limit:
            break
    return candidates


def evidence_text(item: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("receiptId", "validationId", "command", "environment", "proofType"):
        value = item.get(key)
        if value:
            values.append(str(value))
    values.extend(str(value) for value in item.get("scope") or [])
    values.extend(str(value) for value in item.get("proofScope") or [])
    artifact = item.get("artifact") if isinstance(item.get("artifact"), dict) else {}
    if artifact.get("path"):
        values.append(str(artifact.get("path")))
    return " ".join(values).lower()


def evidence_matches_any(evidence: list[dict[str, Any]], tokens: tuple[str, ...] | list[str]) -> bool:
    lowered_tokens = [token.lower() for token in tokens]
    return any(any(token in evidence_text(item) for token in lowered_tokens) for item in evidence)


def first_validation_command(task: dict[str, Any]) -> dict[str, Any]:
    required = (task.get("validationContract") or {}).get("required") or []
    return required[0] if required else {}


class IOSNotificationPermissionPack:
    id = "ios-notification-permission-workflow"
    version = "1"

    def build_prepare_risk_pack(self, contract: dict[str, Any], context: DomainPackContext) -> dict[str, Any] | None:
        profile = (contract.get("projectSnapshot") or {}).get("profile")
        goal = str(contract.get("goal") or "")
        if profile != "ios" or not notification_permission_goal(goal):
            return None
        required = (contract.get("validationContract") or {}).get("required") or []
        first_validation = required[0] if required else {}
        validation_command = str(first_validation.get("command") or "shipguard choose-ios-validation-scheme")
        validation_id = str(first_validation.get("requirementId") or slug(validation_command))
        authorized_scope = [item for item in contract.get("authorizedScope") or [] if isinstance(item, dict)]
        candidates = discover_permission_candidates(context)
        return {
            "id": self.id,
            "version": self.version,
            "status": "active",
            "triggerSignals": [
                signal
                for signal in [
                    "profile:ios",
                    "goal:notification" if "notification" in goal.lower() else "",
                    "goal:permission" if "permission" in goal.lower() or "authorization" in goal.lower() else "",
                    "goal:denied-state" if "denied" in goal.lower() else "",
                ]
                if signal
            ],
            "scopeRecommendations": {
                "authorized": [
                    {
                        "pattern": item.get("pattern"),
                        "reason": item.get("reason") or "Candidate owner for this notification or permission task.",
                    }
                    for item in authorized_scope
                ],
                "reviewOnly": [
                    {
                        "pattern": "**/Info.plist",
                        "reason": "Usage descriptions and notification prompt copy affect user trust; changes need explicit review.",
                    },
                    {
                        "pattern": "**/*AppDelegate*.swift",
                        "reason": "App lifecycle notification registration can affect delivery and prompt timing.",
                    },
                    {
                        "pattern": "**/*SceneDelegate*.swift",
                        "reason": "Scene lifecycle changes can affect permission recovery routes.",
                    },
                ],
                "forbiddenUnlessExplicit": [
                    {
                        "pattern": "**/*.entitlements",
                        "reason": "Entitlement changes are not implied by a notification permission UI task.",
                    },
                    {
                        "pattern": "**/project.pbxproj",
                        "reason": "Project-setting changes require a separate build-configuration task contract.",
                    },
                ],
            },
            "candidateEvidence": {
                "permissionSensitiveFiles": candidates,
                "scannedFileLimit": context.snapshot_file_limit,
                "shareable": context.shareable,
            },
            "validationReceiptRequirements": [
                {
                    "id": "permission-state-validation",
                    "validationId": validation_id,
                    "command": validation_command,
                    "requiredReceiptScope": ["permission-state", "denied-state", "not-determined-state"],
                    "expectedArtifact": "structured validation receipt with permission-state scope labels",
                    "successCondition": "Tests or UI automation cover not-determined, denied, and authorized/provisional states.",
                    "failureMeaning": "Permission-state behavior remains a generic test claim, not a permission workflow proof.",
                },
                {
                    "id": "simulator-denied-state-recovery",
                    "proofType": "ios-permission-simulator-reset",
                    "environment": "simulator",
                    "expectedArtifact": "simulator screenshot, UI log, or receipt after resetting notification permission state",
                    "successCondition": "Denied-state recovery is observed after a simulator permission reset.",
                    "failureMeaning": "The denied-state recovery path remains unproven in a runnable local environment.",
                },
                {
                    "id": "physical-device-prompt-boundary",
                    "proofType": "ios-permission-prompt-physical-device",
                    "environment": "physical-device",
                    "releaseOnly": True,
                    "expectedArtifact": "physical-device prompt receipt or manually reviewed screenshot reference",
                    "successCondition": "Real-device prompt timing and wording are observed before release claims.",
                    "failureMeaning": "ShipGuard must not treat simulator/source evidence as physical-device prompt proof.",
                },
            ],
            "proofBoundaries": {
                "localAutomation": "Structured validation receipts can prove state handling and regression coverage.",
                "simulator": "Simulator proof can show reset/denied-state recovery, but not final physical-device prompt truth.",
                "physicalDevice": "Physical-device prompt timing, OS-level permission UI, and release claims need manual/device proof.",
            },
            "nextAction": {
                "owner": "developer",
                "command": validation_command,
                "expectedArtifact": "structured receipt with scope labels: permission-state, denied-state, not-determined-state, simulator-permission-reset",
                "successCondition": "ShipGuard verify can distinguish local permission workflow proof from manual device proof.",
                "failureMeaning": "Notification permission work remains generic validation rather than a permission workflow contract.",
            },
            "reportQualityQuestions": [
                "Did prepare identify notification/permission owner scopes, review-only lifecycle/plist surfaces, and forbidden entitlement/project changes?",
                "Did verify require permission-state and denied-state proof instead of treating a generic test log as enough?",
                "Did the verdict separate simulator denied-state proof from physical-device prompt proof before release claims?",
            ],
        }

    def evaluate_verify(
        self,
        task: dict[str, Any],
        diff_files: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
        coverage: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not self._active(task, diff_files):
            return None
        pack = task.get("domainRiskPack") or {}
        validation = first_validation_command(task)
        validation_command = str(validation.get("command") or "shipguard choose-ios-validation-scheme")
        validation_requirement = str(validation.get("requirementId") or slug(validation_command))
        coverage_ok = coverage.get("status") in {"covered", "not-required"}
        permission_state_proven = coverage_ok and evidence_matches_any(
            evidence,
            ("permission-state", "authorization-state", "not-determined-state", "notdetermined", "provisional-state"),
        )
        denied_state_proven = evidence_matches_any(evidence, ("denied-state", "permission-denied", "denied recovery"))
        simulator_proven = evidence_matches_any(
            evidence,
            ("simulator", "simctl", "permission-reset", "simulator-permission-reset", "ios-permission-simulator-reset"),
        )
        physical_device_proven = evidence_matches_any(
            evidence,
            ("physical-device", "real-device", "device-permission-prompt", "ios-permission-prompt-physical-device"),
        )
        proof_lanes = [
            {
                "id": "permission-state-validation",
                "status": "proven" if permission_state_proven else "missing",
                "requiredReceiptScope": ["permission-state", "denied-state", "not-determined-state"],
                "proofBoundary": "local-automation",
                "validationId": validation_requirement,
                "command": validation_command,
                "failureMeaning": "Permission state coverage is not proven by a generic receipt.",
            },
            {
                "id": "denied-state-recovery",
                "status": "proven" if denied_state_proven else "missing",
                "requiredReceiptScope": ["denied-state"],
                "proofBoundary": "local-automation-or-simulator",
                "failureMeaning": "Denied-state recovery remains unproven.",
            },
            {
                "id": "simulator-permission-reset",
                "status": "proven" if simulator_proven else "missing",
                "requiredReceiptScope": ["simulator-permission-reset"],
                "proofBoundary": "simulator",
                "failureMeaning": "The workflow has not shown behavior after resetting simulator permissions.",
            },
            {
                "id": "physical-device-prompt",
                "status": "proven" if physical_device_proven else "manual-required",
                "requiredReceiptScope": ["physical-device-prompt"],
                "proofBoundary": "physical-device",
                "failureMeaning": "Real OS prompt timing and wording need physical-device proof before release claims.",
            },
        ]
        missing_review_lanes = [lane for lane in proof_lanes[:3] if lane["status"] != "proven"]
        if missing_review_lanes:
            first_missing = missing_review_lanes[0]
            status = "review"
            next_action = self._missing_next_action(first_missing, validation_command)
        else:
            status = "local-pass-manual-device-proof-required" if not physical_device_proven else "pass"
            next_action = {
                "owner": "developer",
                "command": "Attach physical-device permission prompt proof before making release or fully-verified claims."
                if not physical_device_proven
                else "Attach the permission workflow verdict and receipts to review.",
                "expectedArtifact": "physical-device prompt receipt" if not physical_device_proven else "review-ready permission proof packet",
                "successCondition": "Physical-device prompt timing and wording are recorded."
                if not physical_device_proven
                else "Reviewer can inspect local and device proof from one packet.",
                "failureMeaning": "Release claims still exceed local simulator/source proof."
                if not physical_device_proven
                else "The permission proof packet is incomplete.",
                "resolves": ["physical-device-prompt"] if not physical_device_proven else ["permission-workflow-proof"],
                "priority": 5 if not physical_device_proven else 7,
            }
        return {
            "id": self.id,
            "version": self.version,
            "status": status,
            "source": "task-domain-risk-pack" if pack else "diff-behavior-categories",
            "riskPack": pack,
            "changedPermissionFiles": [
                item.get("path")
                for item in diff_files
                if {"permission", "notification", "privacy"} & set(item.get("behaviorCategories") or [])
            ],
            "proofLanes": proof_lanes,
            "proofBoundary": {
                "localAutomation": "Permission-state tests and structured receipts can prove local state handling.",
                "simulator": "Simulator reset proof can prove denied/not-determined recovery locally.",
                "physicalDevice": "OS prompt timing, wording, and release claims need physical-device proof.",
            },
            "reviewRequired": bool(missing_review_lanes),
            "nextAction": next_action,
            "reportQualityQuestions": [
                "Did the verdict require permission-state scope labels instead of accepting generic test receipts?",
                "Did the verdict make simulator reset proof separate from physical-device prompt proof?",
            ],
        }

    def _active(self, task: dict[str, Any], diff_files: list[dict[str, Any]]) -> bool:
        if (task.get("domainRiskPack") or {}).get("id") == self.id:
            return True
        categories = {category for item in diff_files for category in item.get("behaviorCategories") or []}
        return bool({"notification", "permission", "privacy"} & categories)

    def _missing_next_action(self, first_missing: dict[str, Any], validation_command: str) -> dict[str, Any]:
        if first_missing["id"] == "permission-state-validation":
            command = validation_command
            expected = "structured validation receipt with permission-state, denied-state, and not-determined-state scope labels"
            success = "The receipt proves permission-state coverage rather than generic test execution."
        elif first_missing["id"] == "denied-state-recovery":
            command = "Capture denied-state recovery proof, then attach a receipt with scope: denied-state."
            expected = "denied-state recovery screenshot, UI log, or structured receipt"
            success = "A reviewer can see how the app recovers after notification permission is denied."
        else:
            command = "Reset simulator notification permissions, exercise the permission flow, then attach a receipt with environment=simulator and proofType=ios-permission-simulator-reset."
            expected = "simulator permission reset receipt"
            success = "Simulator proof shows the denied/not-determined path after a permission reset."
        return {
            "owner": "developer",
            "command": command,
            "expectedArtifact": expected,
            "successCondition": success,
            "failureMeaning": first_missing["failureMeaning"],
            "resolves": [first_missing["id"]],
            "priority": 4,
        }
