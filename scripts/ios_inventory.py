#!/usr/bin/env python3
"""Inventory iOS permission and runtime surfaces for Codex planning."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor


SCHEMA_VERSION = 2


SURFACES = [
    {
        "name": "Notifications",
        "kind": "permission",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": [
            "UNUserNotificationCenter",
            "UNNotification",
            "UserNotifications",
            "requestAuthorization",
        ],
        "codex_mode": "notification-permission-gate",
        "question": "Which authorization states must remain truthful: not determined, denied, provisional, fallback-only, or granted?",
    },
    {
        "name": "AlarmKit",
        "kind": "runtime",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["AlarmKit", "AlarmManager", "AlarmPresentation", "AlarmMetadata"],
        "codex_mode": "alarm-runtime-gate",
        "question": "Is this a simulator-only change, or does it require physical-device wake-path proof before release claims?",
    },
    {
        "name": "Location",
        "kind": "permission",
        "plist_keys": [
            "NSLocationWhenInUseUsageDescription",
            "NSLocationAlwaysAndWhenInUseUsageDescription",
            "NSLocationAlwaysUsageDescription",
        ],
        "entitlement_keys": [],
        "source_tokens": ["CLLocationManager", "CoreLocation", "requestWhenInUseAuthorization", "requestAlwaysAuthorization"],
        "codex_mode": "permission-copy-gate",
        "question": "What user-visible feature justifies location access, and which iOS authorization level is required?",
    },
    {
        "name": "Camera",
        "kind": "permission",
        "plist_keys": ["NSCameraUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["AVCaptureDevice", "UIImagePickerController", "cameraCaptureMode"],
        "codex_mode": "permission-copy-gate",
        "question": "What screen needs camera access, and what should happen when access is denied?",
    },
    {
        "name": "Microphone",
        "kind": "permission",
        "plist_keys": ["NSMicrophoneUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["AVAudioRecorder", "AVAudioSession", "requestRecordPermission"],
        "codex_mode": "permission-copy-gate",
        "question": "What recording path needs microphone access, and what degraded state is acceptable?",
    },
    {
        "name": "Photos",
        "kind": "permission",
        "plist_keys": ["NSPhotoLibraryUsageDescription", "NSPhotoLibraryAddUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["PHPhotoLibrary", "PhotosUI", "PHPickerViewController", "UIImagePickerController"],
        "codex_mode": "permission-copy-gate",
        "question": "Does the app need read access, write-only access, or a picker-only flow that avoids broad library permission?",
    },
    {
        "name": "Contacts",
        "kind": "permission",
        "plist_keys": ["NSContactsUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["CNContactStore", "ContactsUI"],
        "codex_mode": "permission-copy-gate",
        "question": "Which contact fields are needed, and can the feature work without full contact access?",
    },
    {
        "name": "Calendars",
        "kind": "permission",
        "plist_keys": [
            "NSCalendarsUsageDescription",
            "NSCalendarsFullAccessUsageDescription",
            "NSCalendarsWriteOnlyAccessUsageDescription",
        ],
        "entitlement_keys": [],
        "source_tokens": ["EKEventStore", "EventKit"],
        "codex_mode": "permission-copy-gate",
        "question": "Does the app need calendar read/write access, write-only access, or no calendar permission at all?",
    },
    {
        "name": "Reminders",
        "kind": "permission",
        "plist_keys": ["NSRemindersUsageDescription", "NSRemindersFullAccessUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["EKReminder", "reminderStore"],
        "codex_mode": "permission-copy-gate",
        "question": "Which reminder operation requires access, and what is the denied-state behavior?",
    },
    {
        "name": "Bluetooth",
        "kind": "permission",
        "plist_keys": ["NSBluetoothAlwaysUsageDescription", "NSBluetoothPeripheralUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["CBCentralManager", "CBPeripheralManager", "CoreBluetooth"],
        "codex_mode": "permission-copy-gate",
        "question": "What hardware path needs Bluetooth, and how should unavailable hardware be handled?",
    },
    {
        "name": "Speech",
        "kind": "permission",
        "plist_keys": ["NSSpeechRecognitionUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["SFSpeechRecognizer", "Speech"],
        "codex_mode": "permission-copy-gate",
        "question": "What spoken input is processed, and what privacy copy should be shown before recognition?",
    },
    {
        "name": "HealthKit",
        "kind": "permission",
        "plist_keys": ["NSHealthShareUsageDescription", "NSHealthUpdateUsageDescription"],
        "entitlement_keys": ["com.apple.developer.healthkit"],
        "source_tokens": ["HKHealthStore", "HealthKit"],
        "codex_mode": "permission-and-entitlement-gate",
        "question": "Which HealthKit sample types are read or written, and what device/account proof is required?",
    },
    {
        "name": "Face ID",
        "kind": "permission",
        "plist_keys": ["NSFaceIDUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["LAContext", "biometryType", "LocalAuthentication"],
        "codex_mode": "permission-copy-gate",
        "question": "What action is protected by biometrics, and what fallback path is allowed?",
    },
    {
        "name": "Motion",
        "kind": "permission",
        "plist_keys": ["NSMotionUsageDescription"],
        "entitlement_keys": [],
        "source_tokens": ["CMMotionManager", "CMPedometer", "CoreMotion"],
        "codex_mode": "permission-copy-gate",
        "question": "Which motion signal is needed, and how should unavailable sensors be handled?",
    },
    {
        "name": "NFC",
        "kind": "permission",
        "plist_keys": ["NFCReaderUsageDescription"],
        "entitlement_keys": ["com.apple.developer.nfc.readersession.formats"],
        "source_tokens": ["NFCNDEFReaderSession", "CoreNFC"],
        "codex_mode": "permission-and-entitlement-gate",
        "question": "Which tags or formats are supported, and what physical-device proof is required?",
    },
    {
        "name": "HomeKit",
        "kind": "permission",
        "plist_keys": ["NSHomeKitUsageDescription"],
        "entitlement_keys": ["com.apple.developer.homekit"],
        "source_tokens": ["HMHomeManager", "HomeKit"],
        "codex_mode": "permission-and-entitlement-gate",
        "question": "What home data is accessed, and what denied-state UI should stay available?",
    },
    {
        "name": "Push Notifications",
        "kind": "entitlement",
        "plist_keys": [],
        "entitlement_keys": ["aps-environment"],
        "source_tokens": ["registerForRemoteNotifications", "didRegisterForRemoteNotifications"],
        "codex_mode": "entitlement-and-device-gate",
        "question": "Is this local notification work, remote push work, or both, and which environment must be proven?",
    },
    {
        "name": "App Groups",
        "kind": "entitlement",
        "plist_keys": [],
        "entitlement_keys": ["com.apple.security.application-groups"],
        "source_tokens": ["suiteName:", "UserDefaults(suiteName", "FileManager.default.containerURL"],
        "codex_mode": "shared-container-gate",
        "question": "Which app, widget, intent, or extension reads this shared container, and what migration proof is required?",
    },
    {
        "name": "Background Modes",
        "kind": "runtime",
        "plist_keys": ["UIBackgroundModes"],
        "entitlement_keys": [],
        "source_tokens": ["beginBackgroundTask", "BGTaskScheduler", "BGAppRefreshTask", "BGProcessingTask"],
        "codex_mode": "background-runtime-gate",
        "question": "Which background mode is required, and what foreground/background/terminated proof will validate it?",
    },
    {
        "name": "Live Activities",
        "kind": "runtime",
        "plist_keys": ["NSSupportsLiveActivities", "NSSupportsLiveActivitiesFrequentUpdates"],
        "entitlement_keys": [],
        "source_tokens": ["ActivityKit", "Activity<", "DynamicIsland", "LiveActivity"],
        "codex_mode": "activitykit-gate",
        "question": "Which start, update, stale, and cleanup states must be verified in Simulator or on device?",
    },
    {
        "name": "Widgets",
        "kind": "extension",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["WidgetKit", "WidgetBundle", "WidgetConfiguration", "TimelineProvider"],
        "codex_mode": "widget-shared-state-gate",
        "question": "Which app state is shared with widgets, and what stale-data behavior must stay correct?",
    },
    {
        "name": "App Intents",
        "kind": "system-integration",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["AppIntent", "AppEntity", "AppShortcutsProvider", "AppIntents"],
        "codex_mode": "app-intents-gate",
        "question": "Which actions and entities should be visible to Shortcuts, Siri, Spotlight, widgets, or controls?",
    },
    {
        "name": "StoreKit",
        "kind": "commerce",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["StoreKit", "Product.products", "Transaction.currentEntitlements", "SKPaymentQueue"],
        "codex_mode": "storekit-proof-gate",
        "question": "Which sandbox account, product IDs, restore path, and entitlement states must be proven?",
    },
    {
        "name": "Swift Concurrency",
        "kind": "modernization",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["async", "await", "Task", "Task.detached", "@MainActor", "actor"],
        "codex_mode": "swift-6-modernization-gate",
        "question": "Which async paths require MainActor isolation, cancellation, or Sendable proof before Codex changes them?",
    },
    {
        "name": "Foundation Models",
        "kind": "modernization",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["FoundationModels", "LanguageModelSession", "SystemLanguageModel", "Generable"],
        "codex_mode": "apple-foundation-models-gate",
        "question": "Which on-device model capability, fallback, and privacy boundary should Codex preserve?",
    },
    {
        "name": "Core ML",
        "kind": "modernization",
        "plist_keys": [],
        "entitlement_keys": [],
        "source_tokens": ["CoreML", "MLModel", "MLFeatureProvider", "MLMultiArray"],
        "codex_mode": "on-device-ml-gate",
        "question": "Which model inputs, outputs, performance budget, and device fallback must remain true?",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory iOS permission and runtime surfaces before Codex edits risky app behavior."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-inventory.md and ios-inventory.json")
    parser.add_argument(
        "--doctor",
        help="Optional ios-doctor.json to reuse for deterministic target ownership instead of rebuilding topology",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of Markdown")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"ios-inventory: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def should_skip_dir(path: Path) -> bool:
    return path.name in {
        ".git",
        ".build",
        ".swiftpm",
        "DerivedData",
        "build",
        "Carthage",
        "Pods",
        "node_modules",
    }


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if not should_skip_dir(current / name)]
        for filename in filenames:
            files.append(current / filename)
    return sorted(files, key=lambda item: rel(item, root))


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def load_plist(path: Path) -> Any | None:
    try:
        with path.open("rb") as handle:
            return plistlib.load(handle)
    except Exception:
        return None


def flatten_plist_keys(value: Any, prefix: str = "") -> dict[str, Any]:
    found: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, nested in value.items():
            text_key = str(key)
            found[text_key] = nested
            nested_prefix = f"{prefix}.{text_key}" if prefix else text_key
            found.update(flatten_plist_keys(nested, nested_prefix))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.update(flatten_plist_keys(nested, f"{prefix}[{index}]"))
    return found


def collect_project(root: Path) -> dict[str, Any]:
    files = iter_files(root)
    swift_files = [path for path in files if path.suffix == ".swift"]
    plist_files = [path for path in files if path.name.endswith(".plist")]
    entitlement_files = [path for path in files if path.name.endswith(".entitlements")]

    plist_values: dict[str, list[dict[str, Any]]] = {}
    entitlements: dict[str, list[dict[str, Any]]] = {}

    for path in plist_files:
        loaded = load_plist(path)
        if loaded is None:
            continue
        for key, value in flatten_plist_keys(loaded).items():
            plist_values.setdefault(key, []).append({"file": rel(path, root), "value": value})

    for path in entitlement_files:
        loaded = load_plist(path)
        if loaded is None:
            continue
        for key, value in flatten_plist_keys(loaded).items():
            entitlements.setdefault(key, []).append({"file": rel(path, root), "value": value})

    source_texts = []
    for path in swift_files:
        source_texts.append((path, read_text(path)))

    return {
        "files": files,
        "swift_files": swift_files,
        "plist_files": plist_files,
        "entitlement_files": entitlement_files,
        "plist_values": plist_values,
        "entitlements": entitlements,
        "source_texts": source_texts,
    }


def load_doctor_report(root: Path, doctor_path: Path | None) -> dict[str, Any]:
    if doctor_path is None:
        return ios_doctor.build_report(root)
    if not doctor_path.exists():
        fail(f"doctor report not found: {doctor_path}")
    try:
        with doctor_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except json.JSONDecodeError as exc:
        fail(f"doctor report is not valid JSON: {doctor_path}: {exc}")
    if not isinstance(loaded, dict):
        fail(f"doctor report must be a JSON object: {doctor_path}")
    return loaded


def normalize_project_path(value: str) -> str:
    text = str(value).strip().strip('"')
    for prefix in ("$(SRCROOT)/", "$(PROJECT_DIR)/", "${SRCROOT}/", "${PROJECT_DIR}/"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
    return text.removeprefix("./")


def path_is_under(path: str, root: str) -> bool:
    normalized_path = normalize_project_path(path)
    normalized_root = normalize_project_path(root).rstrip("/")
    return normalized_path == normalized_root or normalized_path.startswith(f"{normalized_root}/")


def setting_paths(values: list[str]) -> list[str]:
    return unique_sorted([normalize_project_path(value) for value in values])


def package_target_kind(root: Path, package_dir: str, name: str) -> str:
    if (root / package_dir / "Tests" / name).exists() or name.lower().endswith("tests"):
        return "test"
    return "package-target"


def looks_like_test_source_path(file_path: str) -> bool:
    parts = normalize_project_path(file_path).split("/")
    if any(part in {"Tests", "UITests"} or part.endswith("Tests") or part.endswith("UITests") for part in parts[:-1]):
        return True
    filename = parts[-1] if parts else ""
    return filename.endswith("Tests.swift") or filename.endswith("UITests.swift")


def target_ref(target: dict[str, Any], status: str) -> dict[str, str]:
    return {
        "id": target["id"],
        "name": target["name"],
        "kind": target["kind"],
        "status": status,
    }


def add_unique_path(target: dict[str, Any], key: str, value: str) -> None:
    normalized = normalize_project_path(value)
    if normalized and normalized not in target[key]:
        target[key].append(normalized)
        target[key].sort()


def new_target(
    target_id: str,
    name: str,
    kind: str,
    source: str,
    project_path: str | None = None,
    package_path: str | None = None,
) -> dict[str, Any]:
    return {
        "id": target_id,
        "name": name,
        "kind": kind,
        "source": source,
        "project": project_path,
        "package": package_path,
        "schemes": [],
        "bundle_identifiers": [],
        "deployment_targets": [],
        "swift_versions": [],
        "info_plists": [],
        "entitlements": [],
        "storekit_configs": [],
        "privacy_manifests": [],
        "source_roots": [],
        "risk_counts": {"high": 0, "review": 0, "unmapped": 0},
        "surfaces": [],
    }


def build_xcode_targets(project: dict[str, Any]) -> list[dict[str, Any]]:
    details = project.get("target_details") or []
    if not details:
        fallback_kind = "app" if len(project.get("targets", [])) == 1 else "xcode-target"
        details = [
            {
                "name": name,
                "kind": fallback_kind,
                "bundle_identifiers": project.get("bundle_identifiers", []) if len(project.get("targets", [])) == 1 else [],
                "deployment_targets": project.get("deployment_targets", []) if len(project.get("targets", [])) == 1 else [],
                "swift_versions": project.get("swift_versions", []) if len(project.get("targets", [])) == 1 else [],
                "info_plists": project.get("info_plists", []) if len(project.get("targets", [])) == 1 else [],
                "entitlements": project.get("entitlements", []) if len(project.get("targets", [])) == 1 else [],
            }
            for name in project.get("targets", [])
        ]
    targets: list[dict[str, Any]] = []
    for detail in details:
        name = detail.get("name")
        if not name:
            continue
        target = new_target(
            f"xcode:{project.get('path', '<unknown>')}:{name}",
            name,
            detail.get("kind") or "xcode-target",
            "xcode_project",
            project_path=project.get("path"),
        )
        target["schemes"] = unique_sorted(project.get("schemes", []))
        target["bundle_identifiers"] = setting_paths(detail.get("bundle_identifiers", []))
        target["deployment_targets"] = setting_paths(detail.get("deployment_targets", []))
        target["swift_versions"] = setting_paths(detail.get("swift_versions", []))
        target["info_plists"] = setting_paths(detail.get("info_plists", []))
        target["entitlements"] = setting_paths(detail.get("entitlements", []))
        targets.append(target)
    return targets


def build_package_targets(root: Path, package: dict[str, Any]) -> list[dict[str, Any]]:
    package_dir = Path(package.get("path", "Package.swift")).parent.as_posix()
    if package_dir == ".":
        package_dir = ""
    targets: list[dict[str, Any]] = []
    details = package.get("target_details") or [
        {
            "name": name,
            "kind": package_target_kind(root, package_dir, name),
            "path": None,
        }
        for name in package.get("targets", [])
    ]
    for detail in details:
        name = detail.get("name")
        if not name:
            continue
        explicit_path = detail.get("path")
        target = new_target(
            f"swiftpm:{package.get('path', '<unknown>')}:{name}",
            name,
            detail.get("kind") or package_target_kind(root, package_dir, name),
            "swift_package",
            package_path=package.get("path"),
        )
        if explicit_path:
            candidate = f"{package_dir}/{explicit_path}".lstrip("/")
            if (root / candidate).exists():
                add_unique_path(target, "source_roots", candidate)
        else:
            for base in ("Sources", "Tests"):
                candidate = f"{package_dir}/{base}/{name}".lstrip("/")
                if (root / candidate).exists():
                    add_unique_path(target, "source_roots", candidate)
        targets.append(target)
    return targets


def assign_repo_files_to_targets(targets: list[dict[str, Any]], doctor_report: dict[str, Any]) -> None:
    app_targets = [target for target in targets if target["kind"] == "app"]
    repo_storekit = doctor_report.get("storekit_configs", [])
    repo_privacy = [item["path"] for item in doctor_report.get("privacy_manifests", []) if isinstance(item, dict)]

    for target in targets:
        for path in repo_storekit:
            if any(path_is_under(path, root) for root in target["source_roots"]):
                add_unique_path(target, "storekit_configs", path)
        for path in repo_privacy:
            if any(path_is_under(path, root) for root in target["source_roots"]):
                add_unique_path(target, "privacy_manifests", path)

    if len(app_targets) == 1:
        app_target = app_targets[0]
        for path in repo_storekit:
            add_unique_path(app_target, "storekit_configs", path)
        for path in repo_privacy:
            add_unique_path(app_target, "privacy_manifests", path)


def build_targets(root: Path, doctor_report: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for project in doctor_report.get("xcode_projects", []):
        targets.extend(build_xcode_targets(project))
    for package in doctor_report.get("swift_packages", []):
        targets.extend(build_package_targets(root, package))
    assign_repo_files_to_targets(targets, doctor_report)
    return sorted(targets, key=lambda item: (item["source"], item["name"], item["id"]))


def direct_owner_refs(file_path: str, targets: list[dict[str, Any]], key: str) -> list[dict[str, str]]:
    owners: list[dict[str, str]] = []
    for target in targets:
        if any(normalize_project_path(file_path) == normalize_project_path(path) for path in target[key]):
            owners.append(target_ref(target, "owned"))
    return owners


def source_owner_refs(file_path: str, targets: list[dict[str, Any]]) -> list[dict[str, str]]:
    owners: list[dict[str, str]] = []
    for target in targets:
        if any(path_is_under(file_path, root) for root in target["source_roots"]):
            owners.append(target_ref(target, "owned"))

    app_targets = [target for target in targets if target["kind"] == "app"]
    if (
        len(app_targets) == 1
        and not looks_like_test_source_path(file_path)
        and not any(owner["kind"] == "test" for owner in owners)
        and not any(owner["id"].startswith("xcode:") for owner in owners)
    ):
        owners.append(target_ref(app_targets[0], "single-app-target"))
    return dedupe_owners(owners)


def dedupe_owners(owners: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {"owned": 3, "single-app-target": 2, "repo-wide": 1, "unmapped": 0}
    deduped: dict[str, dict[str, str]] = {}
    for owner in owners:
        existing = deduped.get(owner["id"])
        if existing is None or priority.get(owner["status"], 0) > priority.get(existing["status"], 0):
            deduped[owner["id"]] = owner
    return sorted(deduped.values(), key=lambda item: (item["kind"], item["name"], item["status"]))


def owners_for_file(file_path: str, targets: list[dict[str, Any]], evidence_kind: str) -> list[dict[str, str]]:
    if evidence_kind == "plist":
        return direct_owner_refs(file_path, targets, "info_plists")
    if evidence_kind == "entitlement":
        return direct_owner_refs(file_path, targets, "entitlements")
    if evidence_kind == "storekit_config":
        return direct_owner_refs(file_path, targets, "storekit_configs")
    if evidence_kind == "privacy_manifest":
        return direct_owner_refs(file_path, targets, "privacy_manifests")
    if evidence_kind == "source":
        return source_owner_refs(file_path, targets)
    return []


def evidence_owner_status(owners: list[dict[str, str]], evidence_kind: str) -> str:
    if owners:
        if all(owner["status"] == "single-app-target" for owner in owners):
            return "single-app-target"
        return "owned"
    if evidence_kind in {"storekit_config", "privacy_manifest"}:
        return "repo-wide"
    return "unmapped"


def annotate_file_evidence(
    item: dict[str, Any],
    targets: list[dict[str, Any]],
    evidence_kind: str,
) -> dict[str, Any]:
    owners = owners_for_file(item["file"], targets, evidence_kind)
    annotated = dict(item)
    annotated["owners"] = owners
    annotated["owner_status"] = evidence_owner_status(owners, evidence_kind)
    return annotated


def surface_owner_status(evidence_groups: list[list[dict[str, Any]]]) -> str:
    evidence = [item for group in evidence_groups for item in group]
    if not evidence:
        return "not-detected"
    statuses = {item.get("owner_status", "unmapped") for item in evidence}
    owner_count = sum(len(item.get("owners", [])) for item in evidence)
    if "unmapped" in statuses and owner_count > 0:
        return "partially-owned"
    if "unmapped" in statuses:
        return "unmapped"
    if owner_count == 0 and "repo-wide" in statuses:
        return "repo-wide"
    if statuses == {"single-app-target"}:
        return "single-app-target"
    return "owned"


def surface_owners(evidence_groups: list[list[dict[str, Any]]]) -> list[dict[str, str]]:
    owners: list[dict[str, str]] = []
    for group in evidence_groups:
        for item in group:
            owners.extend(item.get("owners", []))
    return dedupe_owners(owners)


def value_summary(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [value_summary(item) for item in value]
    if isinstance(value, dict):
        return {str(key): value_summary(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    return str(value)


def token_regex(token: str) -> re.Pattern[str]:
    escaped = re.escape(token)
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):
        return re.compile(rf"\b{escaped}\b")
    return re.compile(escaped)


def find_token_matches(source_texts: list[tuple[Path, str]], root: Path, tokens: list[str]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for token in tokens:
        pattern = token_regex(token)
        for path, text in source_texts:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                matches.append({"token": token, "file": rel(path, root), "line": line_number})
                break
    return sorted(matches, key=lambda item: (item["file"], item["line"], item["token"]))


def target_project_files(surface_name: str, doctor_report: dict[str, Any]) -> list[dict[str, Any]]:
    if surface_name != "StoreKit":
        return []
    return [{"kind": "storekit_config", "file": path} for path in doctor_report.get("storekit_configs", [])]


def risk_for_surface(status: str, base_risk: str, owner_status: str) -> str:
    if status == "not-detected":
        return "none"
    if owner_status in {"unmapped", "repo-wide"}:
        return "unmapped"
    return base_risk


def attach_target_risks(targets: list[dict[str, Any]], surfaces: list[dict[str, Any]]) -> None:
    by_id = {target["id"]: target for target in targets}
    seen: set[tuple[str, str]] = set()
    for surface in surfaces:
        if surface["status"] == "not-detected":
            continue
        for owner in surface["owners"]:
            target = by_id.get(owner["id"])
            if target is None:
                continue
            key = (target["id"], surface["surface"])
            if key in seen:
                continue
            seen.add(key)
            if surface["risk"] in target["risk_counts"]:
                target["risk_counts"][surface["risk"]] += 1
            target["surfaces"].append(
                {
                    "surface": surface["surface"],
                    "kind": surface["kind"],
                    "status": surface["status"],
                    "risk": surface["risk"],
                    "owner_status": surface["owner_status"],
                }
            )
    for target in targets:
        target["surfaces"] = sorted(target["surfaces"], key=lambda item: (item["risk"], item["surface"]))


def build_inventory(root: Path, doctor_path: Path | None = None) -> dict[str, Any]:
    project = collect_project(root)
    doctor_report = load_doctor_report(root, doctor_path)
    targets = build_targets(root, doctor_report)
    surfaces = []

    for surface in SURFACES:
        plist_hits = []
        for key in surface["plist_keys"]:
            for hit in project["plist_values"].get(key, []):
                plist_hits.append(
                    annotate_file_evidence(
                        {"key": key, "file": hit["file"], "value": value_summary(hit["value"])},
                        targets,
                        "plist",
                    )
                )

        entitlement_hits = []
        for key in surface["entitlement_keys"]:
            for hit in project["entitlements"].get(key, []):
                entitlement_hits.append(
                    annotate_file_evidence(
                        {"key": key, "file": hit["file"], "value": value_summary(hit["value"])},
                        targets,
                        "entitlement",
                    )
                )

        source_hits = [
            annotate_file_evidence(hit, targets, "source")
            for hit in find_token_matches(project["source_texts"], root, surface["source_tokens"])
        ]
        project_file_hits = [
            annotate_file_evidence(hit, targets, hit["kind"])
            for hit in target_project_files(surface["name"], doctor_report)
        ]
        declared = bool(plist_hits or entitlement_hits)
        used = bool(source_hits or project_file_hits)
        expected_declaration = bool(surface["plist_keys"] or surface["entitlement_keys"])

        if used and expected_declaration and not declared:
            status = "needs-user-answer"
            base_risk = "high"
            finding = "Source uses this surface but the expected usage description or entitlement was not found."
        elif used or declared:
            status = "present"
            base_risk = "review"
            finding = "Surface is present; keep permission copy, entitlements, and validation proof aligned."
        else:
            status = "not-detected"
            base_risk = "none"
            finding = "No matching source, usage description, or entitlement was detected."
        owner_status = surface_owner_status([plist_hits, entitlement_hits, source_hits, project_file_hits])
        risk = risk_for_surface(status, base_risk, owner_status)

        surfaces.append(
            {
                "surface": surface["name"],
                "kind": surface["kind"],
                "status": status,
                "risk": risk,
                "owners": surface_owners([plist_hits, entitlement_hits, source_hits, project_file_hits]),
                "owner_status": owner_status,
                "codex_mode": surface["codex_mode"],
                "question": surface["question"],
                "finding": finding,
                "plist_keys": plist_hits,
                "entitlements": entitlement_hits,
                "source_matches": source_hits,
                "project_files": project_file_hits,
            }
        )

    present = [item for item in surfaces if item["status"] != "not-detected"]
    needs_answer = [item for item in surfaces if item["status"] == "needs-user-answer"]
    unmapped = [item for item in present if item["owner_status"] in {"unmapped", "repo-wide", "partially-owned"}]
    attach_target_risks(targets, surfaces)

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "codex-maintainer ios inventory",
        "project": str(root),
        "counts": {
            "files": len(project["files"]),
            "swift_files": len(project["swift_files"]),
            "plist_files": len(project["plist_files"]),
            "entitlement_files": len(project["entitlement_files"]),
            "targets": len(targets),
            "surfaces_present": len(present),
            "needs_user_answer": len(needs_answer),
            "unmapped_surfaces": len(unmapped),
        },
        "doctor": {
            "source": str(doctor_path) if doctor_path else "auto",
            "schema_version": doctor_report.get("schema_version"),
            "tool": doctor_report.get("tool"),
        },
        "targets": targets,
        "surfaces": surfaces,
        "recommended_codex_prompts": build_prompts(present, needs_answer),
    }


def build_prompts(present: list[dict[str, Any]], needs_answer: list[dict[str, Any]]) -> list[str]:
    prompts = [
        "Before editing, classify the Codex thread mode: permission audit, simulator bug, release proof, StoreKit, widget/intents, or UI polish.",
        "Use Codex built-in diff comments and Git tools for review; use this inventory only to decide what evidence and answers are still missing.",
    ]
    if needs_answer:
        labels = ", ".join(item["surface"] for item in needs_answer)
        prompts.append(f"Pause for explicit user answers before editing these surfaces: {labels}.")
    if any(item["surface"] in {"Notifications", "AlarmKit", "Background Modes", "Live Activities"} for item in present):
        prompts.append("For notification or wake-path work, verify foreground, background, denied, fallback, and cleanup states before release claims.")
    if any(item["surface"] in {"StoreKit", "Push Notifications", "NFC", "HealthKit"} for item in present):
        prompts.append("For account, entitlement, or hardware-backed work, record the manual account/device proof that Codex cannot infer from source alone.")
    if any(item["surface"] in {"Widgets", "App Intents", "App Groups"} for item in present):
        prompts.append("For widgets, intents, or app groups, verify shared-store consistency and stale-data behavior across app and extension targets.")
    return prompts


def render_hits(items: list[dict[str, Any]], key_name: str) -> str:
    if not items:
        return "-"
    rendered = []
    for item in items[:5]:
        if key_name == "source":
            rendered.append(f"{item['token']} in `{item['file']}:{item['line']}`")
        elif key_name == "project_file":
            rendered.append(f"{item['kind']} in `{item['file']}`")
        else:
            rendered.append(f"{item['key']} in `{item['file']}`")
    if len(items) > 5:
        rendered.append(f"+{len(items) - 5} more")
    return "<br>".join(rendered)


def render_values(values: list[str]) -> str:
    if not values:
        return "-"
    rendered = [f"`{value}`" for value in values[:3]]
    if len(values) > 3:
        rendered.append(f"+{len(values) - 3} more")
    return "<br>".join(rendered)


def render_owner_refs(owners: list[dict[str, str]]) -> str:
    if not owners:
        return "-"
    rendered = []
    for owner in owners[:5]:
        rendered.append(f"{owner['name']} ({owner['kind']}, {owner['status']})")
    if len(owners) > 5:
        rendered.append(f"+{len(owners) - 5} more")
    return "<br>".join(rendered)


def render_target_evidence(target: dict[str, Any]) -> str:
    evidence = []
    if target["info_plists"]:
        evidence.append(f"plist {render_values(target['info_plists'])}")
    if target["entitlements"]:
        evidence.append(f"entitlements {render_values(target['entitlements'])}")
    if target["storekit_configs"]:
        evidence.append(f"StoreKit {render_values(target['storekit_configs'])}")
    if target["privacy_manifests"]:
        evidence.append(f"privacy {render_values(target['privacy_manifests'])}")
    return "<br>".join(evidence) if evidence else "-"


def render_target_surfaces(target: dict[str, Any]) -> str:
    if not target["surfaces"]:
        return "-"
    names = [f"{item['surface']} ({item['risk']})" for item in target["surfaces"][:6]]
    if len(target["surfaces"]) > 6:
        names.append(f"+{len(target['surfaces']) - 6} more")
    return "<br>".join(names)


def surface_evidence(surface: dict[str, Any]) -> str:
    evidence_parts = [
        render_hits(surface["plist_keys"], "plist"),
        render_hits(surface["entitlements"], "entitlement"),
        render_hits(surface["source_matches"], "source"),
        render_hits(surface.get("project_files", []), "project_file"),
    ]
    return "<br>".join(part for part in evidence_parts if part != "-") or "-"


def render_markdown(inventory: dict[str, Any]) -> str:
    counts = inventory["counts"]
    lines = [
        "# iOS Permission And Runtime Inventory",
        "",
        f"- Project: `{inventory['project']}`",
        f"- Targets: {counts.get('targets', 0)}",
        f"- Swift files: {counts['swift_files']}",
        f"- Plist files: {counts['plist_files']}",
        f"- Entitlement files: {counts['entitlement_files']}",
        f"- Surfaces present: {counts['surfaces_present']}",
        f"- Needs user answer: {counts['needs_user_answer']}",
        f"- Unmapped surfaces: {counts.get('unmapped_surfaces', 0)}",
        "",
        "## Target Risk Map",
        "",
        "| Target | Kind | Bundle IDs | Deploy / Swift | Evidence | Risk counts | Surfaces |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for target in inventory.get("targets", []):
        risk_counts = target["risk_counts"]
        lines.append(
            "| {target} | {kind} | {bundles} | {deploy}<br>{swift} | {evidence} | high {high}<br>review {review}<br>unmapped {unmapped} | {surfaces} |".format(
                target=f"`{target['name']}`",
                kind=target["kind"],
                bundles=render_values(target["bundle_identifiers"]),
                deploy=render_values(target["deployment_targets"]),
                swift=render_values(target["swift_versions"]),
                evidence=render_target_evidence(target),
                high=risk_counts["high"],
                review=risk_counts["review"],
                unmapped=risk_counts["unmapped"],
                surfaces=render_target_surfaces(target),
            )
        )
    if not inventory.get("targets"):
        lines.append("| - | - | - | - | - | - | No targets were detected. |")

    lines.extend(
        [
            "",
            "## Detected Surfaces",
            "",
            "| Surface | Status | Owners | Codex mode | Evidence | Required question |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for surface in inventory["surfaces"]:
        if surface["status"] == "not-detected":
            continue
        lines.append(
            "| {surface} | {status} | {owners} | `{mode}` | {evidence} | {question} |".format(
                surface=surface["surface"],
                status=surface["status"],
                owners=render_owner_refs(surface.get("owners", [])),
                mode=surface["codex_mode"],
                evidence=surface_evidence(surface),
                question=surface["question"],
            )
        )

    if counts["surfaces_present"] == 0:
        lines.append("| - | not-detected | - | - | - | No iOS permission or runtime surfaces were detected. |")

    review_surfaces = [
        item
        for item in inventory["surfaces"]
        if item["status"] != "not-detected" and item["kind"] in {"permission", "entitlement"}
    ]
    lines.extend(
        [
            "",
            "## Permission And Entitlement Review",
            "",
            "| Surface | Status | Risk | Owners | Required question |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for surface in review_surfaces:
        lines.append(
            "| {surface} | {status} | {risk} | {owners} | {question} |".format(
                surface=surface["surface"],
                status=surface["status"],
                risk=surface["risk"],
                owners=render_owner_refs(surface.get("owners", [])),
                question=surface["question"],
            )
        )
    if not review_surfaces:
        lines.append("| - | not-detected | none | - | No permission or entitlement surfaces were detected. |")

    unmapped_surfaces = [
        item
        for item in inventory["surfaces"]
        if item["status"] != "not-detected" and item["owner_status"] in {"unmapped", "repo-wide", "partially-owned"}
    ]
    lines.extend(
        [
            "",
            "## Unmapped Surfaces",
            "",
            "| Surface | Owner status | Risk | Evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for surface in unmapped_surfaces:
        lines.append(f"| {surface['surface']} | {surface['owner_status']} | {surface['risk']} | {surface_evidence(surface)} |")
    if not unmapped_surfaces:
        lines.append("| - | owned | none | No unmapped detected surfaces. |")

    modernization_surfaces = [
        item
        for item in inventory["surfaces"]
        if item["status"] != "not-detected"
        and item["kind"] in {"modernization", "system-integration", "extension", "commerce", "runtime"}
    ]
    lines.extend(
        [
            "",
            "## Modernization Opportunities",
            "",
            "| Surface | Kind | Owners | Codex mode | Review prompt |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for surface in modernization_surfaces:
        lines.append(
            "| {surface} | {kind} | {owners} | `{mode}` | {question} |".format(
                surface=surface["surface"],
                kind=surface["kind"],
                owners=render_owner_refs(surface.get("owners", [])),
                mode=surface["codex_mode"],
                question=surface["question"],
            )
        )
    if not modernization_surfaces:
        lines.append("| - | - | - | - | No modernization surfaces were detected. |")

    lines.extend(["", "## Codex Workflow Prompts", ""])
    for prompt in inventory["recommended_codex_prompts"]:
        lines.append(f"- {prompt}")

    needs_answer = [item for item in inventory["surfaces"] if item["status"] == "needs-user-answer"]
    if needs_answer:
        lines.extend(["", "## Ask Before Editing", ""])
        for item in needs_answer:
            lines.append(f"- {item['surface']}: {item['question']}")

    lines.append("")
    return "\n".join(lines)


def write_outputs(out_dir: Path, inventory: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-inventory.md").write_text(render_markdown(inventory), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path is not a directory: {root}")

    doctor_path = Path(args.doctor).expanduser().resolve() if args.doctor else None
    inventory = build_inventory(root, doctor_path)
    if args.out:
        write_outputs(Path(args.out).expanduser(), inventory)

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
