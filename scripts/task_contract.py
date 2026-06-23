#!/usr/bin/env python3
"""Persistent ShipGuard task contracts for prepare/verify loops."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from shipguard_baseline import apply_configuration_baseline, load_configuration, make_finding
from shipguard_receipts import evidence_entries as load_receipt_evidence_entries
from shipguard_receipts import receipt_schema_summary
from task_domain_packs import DEFAULT_DOMAIN_PACK_REGISTRY, DomainPackContext


SCHEMA_VERSION = 1
PROFILES = ("auto", "ios", "web", "backend", "cli")

RISK_KEYWORDS = {
    "critical": (
        "permission",
        "notification",
        "entitlement",
        "storekit",
        "purchase",
        "subscription",
        "migration",
        "privacy",
        "security",
        "release",
        "background",
        "widget",
        "app intent",
    ),
    "high": ("performance", "concurrency", "data", "persistence", "authentication", "payment", "onboarding"),
}

CLAIM_REQUIRES_PROOF = (
    "fully verified",
    "production-ready",
    "production ready",
    "complete",
    "done",
    "safe to ship",
    "no regressions",
)

SNAPSHOT_FILE_LIMIT = 10000
SNAPSHOT_DIR_LIMIT = 4000
SNAPSHOT_SKIP_DIRS = {
    ".build",
    ".cache",
    ".codex",
    ".deriveddata",
    ".git",
    ".next",
    ".pytest_cache",
    ".swiftpm",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "DerivedData",
    "dist",
    "node_modules",
    "Pods",
    "release-artifacts",
    "scratch",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"task-contract: {message}", file=sys.stderr)
    raise SystemExit(1)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"expected JSON object in {path}")
    return data


def path_display(root: Path, shareable: bool) -> str:
    return "<target-repo>" if shareable else str(root.resolve())


def path_is_within(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def detect_profile(root: Path) -> tuple[str, list[str]]:
    signals: list[str] = []
    if list(root.glob("*.xcodeproj")) or list(root.glob("*.xcworkspace")) or any(root.glob("**/*.swift")):
        signals.append("xcode-or-swift")
        return "ios", signals
    if (root / "package.json").is_file():
        signals.append("package-json")
        return "web", signals
    if any((root / name).is_file() for name in ("pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml")):
        signals.append("backend-manifest")
        return "backend", signals
    if (root / "bin").is_dir() or (root / "scripts").is_dir():
        signals.append("bin-or-scripts")
        return "cli", signals
    signals.append("no-strong-profile-signal")
    return "cli", signals


def should_skip_snapshot_dir(name: str) -> bool:
    return name in SNAPSHOT_SKIP_DIRS or name.lower() in SNAPSHOT_SKIP_DIRS


def bounded_snapshot_counts(root: Path) -> dict[str, Any]:
    swift_files = 0
    source_files = 0
    scanned_dirs = 0
    skipped_dirs: list[str] = []
    capped = False
    for current_root, dirs, files in os.walk(root):
        current = Path(current_root)
        scanned_dirs += 1
        kept_dirs = []
        for directory in dirs:
            directory_path = current / directory
            relative = rel(directory_path, root)
            if should_skip_snapshot_dir(directory) or directory.endswith(".xcresult"):
                if len(skipped_dirs) < 80:
                    skipped_dirs.append(relative)
                continue
            kept_dirs.append(directory)
        dirs[:] = kept_dirs
        for filename in files:
            source_files += 1
            if filename.endswith(".swift"):
                swift_files += 1
            if source_files >= SNAPSHOT_FILE_LIMIT:
                capped = True
                dirs[:] = []
                break
        if scanned_dirs >= SNAPSHOT_DIR_LIMIT:
            capped = True
            dirs[:] = []
        if capped and not dirs:
            break
    return {
        "swiftFileCount": swift_files,
        "sourceFileCount": min(source_files, SNAPSHOT_FILE_LIMIT),
        "scanScope": {
            "mode": "bounded",
            "fileLimit": SNAPSHOT_FILE_LIMIT,
            "dirLimit": SNAPSHOT_DIR_LIMIT,
            "scannedDirCount": scanned_dirs,
            "skippedDirs": skipped_dirs,
            "skippedDirCount": len(skipped_dirs),
            "capped": capped,
            "reason": "Project snapshots skip generated, cache, package, and proof directories so prepare returns quickly on real app checkouts.",
        },
    }


def collect_project_snapshot(root: Path, profile: str, detected_signals: list[str], shareable: bool) -> dict[str, Any]:
    files = []
    for pattern in ("AGENTS.md", "README.md", "Package.swift", "package.json", "pyproject.toml", "go.mod", "VERSION"):
        if (root / pattern).is_file():
            files.append(pattern)
    xcode_projects = sorted(path.name for path in root.glob("*.xcodeproj"))
    counts = bounded_snapshot_counts(root)
    return {
        "root": path_display(root, shareable),
        "profile": profile,
        "signals": detected_signals,
        "files": files,
        "xcodeProjects": xcode_projects,
        "swiftFileCount": counts["swiftFileCount"],
        "sourceFileCount": counts["sourceFileCount"],
        "scanScope": counts["scanScope"],
    }


def classify_risk(goal: str, profile: str) -> dict[str, Any]:
    lowered = goal.lower()
    critical_hits = [word for word in RISK_KEYWORDS["critical"] if word in lowered]
    high_hits = [word for word in RISK_KEYWORDS["high"] if word in lowered]
    if critical_hits:
        level = "critical"
    elif high_hits or profile == "ios":
        level = "high"
    else:
        level = "review"
    return {
        "level": level,
        "signals": critical_hits + high_hits + ([f"profile:{profile}"] if profile == "ios" else []),
        "approvalPolicy": {
            "allowedAutomatically": ["docs", "tests", "small source edits inside authorizedFiles"],
            "allowedAfterAgentReview": ["generated reports", "new validation receipts"],
            "requiresHumanApproval": ["entitlements", "release workflows", "billing", "permission prompts", "destructive migrations"],
            "forbiddenInThisTask": [],
            "manualOnlyProof": ["physical-device behavior", "live account or App Store Connect proof", "legal/privacy approval"],
        },
    }


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "item"


def discover_swift_dirs(root: Path, base: str) -> list[str]:
    directory = root / base
    if not directory.is_dir():
        return []
    discovered = []
    for child in sorted(directory.iterdir()):
        if child.is_dir() and any(child.rglob("*.swift")):
            discovered.append(f"{base}/{child.name}/**")
    if not discovered and any(directory.rglob("*.swift")):
        discovered.append(f"{base}/**")
    return discovered


def discover_root_swift_dirs(root: Path) -> list[str]:
    discovered = []
    for child in sorted(root.iterdir() if root.exists() else []):
        if not child.is_dir():
            continue
        if should_skip_snapshot_dir(child.name) or child.suffix in {".xcodeproj", ".xcworkspace"}:
            continue
        if child.name in {"Sources", "Tests"}:
            continue
        if any(child.rglob("*.swift")):
            discovered.append(f"{child.name}/**")
    return discovered


def default_authorized_scope(profile: str, root: Path, goal: str) -> tuple[list[str], list[dict[str, str]]]:
    patterns = default_allowed(profile, root)
    lowered_goal = goal.lower()
    details = []
    for pattern in patterns:
        reason = "Detected source or test owner for this profile."
        if "test" in pattern.lower():
            reason = "Detected test owner for validation or regression coverage."
        elif "notification" in lowered_goal or "permission" in lowered_goal:
            reason = "Allowed as a candidate source owner for the requested notification or permission task."
        details.append({"pattern": pattern, "reason": reason})
    return patterns, details


def scope_placeholder(pattern: str) -> str:
    first = pattern.split("/", 1)[0].lower()
    if "test" in first:
        return "<ios-test-target>"
    if any(token in first for token in ("widget", "watch", "extension", "intent")):
        return "<ios-extension-target>"
    return "<ios-source-target>"


def redact_scope_pattern(pattern: str, sensitive_names: set[str]) -> str:
    if "/" not in pattern:
        return pattern
    first, rest = pattern.split("/", 1)
    if first not in sensitive_names:
        return pattern
    return f"{scope_placeholder(pattern)}/{rest}"


def collect_shareable_sensitive_names(root: Path) -> set[str]:
    sensitive_names: set[str] = set()
    if not root.exists():
        return sensitive_names
    for child in sorted(root.iterdir()):
        if child.is_dir() and any(child.rglob("*.swift")):
            sensitive_names.add(child.name)
    for project in root.glob("*.xcodeproj"):
        sensitive_names.add(project.stem)
    return sensitive_names


def redact_sensitive_name_occurrences(value: str, sensitive_names: set[str]) -> str:
    redacted = value
    structural_names = {"app", "ios", "source", "sources", "test", "tests", "src"}
    for name in sorted(sensitive_names, key=len, reverse=True):
        if not name or name.lower() in structural_names:
            continue
        redacted = re.sub(re.escape(name), "<ios-target>", redacted, flags=re.IGNORECASE)
    return redacted


def redact_top_level_name(path_value: str, sensitive_names: set[str]) -> str:
    if "/" not in path_value:
        stem = Path(path_value).stem
        suffix = "".join(Path(path_value).suffixes)
        if stem in sensitive_names:
            return f"<ios-project>{suffix}"
        return redact_sensitive_name_occurrences(path_value, sensitive_names)
    first, rest = path_value.split("/", 1)
    if first not in sensitive_names:
        return redact_sensitive_name_occurrences(path_value, sensitive_names)
    return f"{scope_placeholder(path_value)}/{redact_sensitive_name_occurrences(rest, sensitive_names)}"


def redact_validation_item(item: dict[str, Any], sensitive_names: set[str]) -> dict[str, Any]:
    redacted = dict(item)
    command = str(redacted.get("command") or "")
    for name in sensitive_names:
        command = re.sub(rf"(-scheme\s+){re.escape(name)}(\b|$)", r"\1<ios-scheme>\2", command)
        command = command.replace(f"{name}.xcresult", "<ios-scheme>.xcresult")
    redacted["command"] = command
    expected = str(redacted.get("expectedArtifact") or "")
    for name in sensitive_names:
        expected = expected.replace(f"{name}.xcresult", "<ios-scheme>.xcresult")
    redacted["expectedArtifact"] = expected
    if str(redacted.get("requirementId") or "").endswith("-scheme-tests"):
        redacted["requirementId"] = "ios-scheme-tests"
    return redacted


def domain_pack_context(root: Path, shareable: bool) -> DomainPackContext:
    sensitive_names = collect_shareable_sensitive_names(root) if shareable else set()
    return DomainPackContext(
        root=root,
        shareable=shareable,
        snapshot_file_limit=SNAPSHOT_FILE_LIMIT,
        rel=lambda path: rel(path, root),
        redact_path=lambda value: redact_top_level_name(value, sensitive_names) if shareable else value,
        should_skip_dir=should_skip_snapshot_dir,
    )


def build_prepare_domain_risk_pack(contract: dict[str, Any], root: Path, shareable: bool) -> dict[str, Any] | None:
    context = domain_pack_context(root, shareable)
    return DEFAULT_DOMAIN_PACK_REGISTRY.build_prepare_risk_pack(contract, context)


def evaluate_domain_workflows(
    task: dict[str, Any],
    diff_files: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return DEFAULT_DOMAIN_PACK_REGISTRY.evaluate_verify(task, diff_files, evidence, coverage)


def redact_external_shareable_contract(contract: dict[str, Any], root: Path) -> dict[str, Any]:
    sensitive_names = collect_shareable_sensitive_names(root)
    for pattern in contract.get("authorizedFiles") or []:
        if isinstance(pattern, str) and "/" in pattern:
            first = pattern.split("/", 1)[0]
            if first and not first.startswith("<"):
                sensitive_names.add(first)
    for project in (contract.get("projectSnapshot") or {}).get("xcodeProjects") or []:
        stem = Path(str(project)).stem
        if stem:
            sensitive_names.add(stem)
    if not sensitive_names:
        return contract

    redacted = dict(contract)
    redacted["authorizedFiles"] = list(
        dict.fromkeys(redact_scope_pattern(str(pattern), sensitive_names) for pattern in contract.get("authorizedFiles") or [])
    )
    scope_details: list[dict[str, str]] = []
    seen_scope_patterns: set[str] = set()
    for item in contract.get("authorizedScope") or []:
        if not isinstance(item, dict):
            continue
        pattern = redact_scope_pattern(str(item.get("pattern") or ""), sensitive_names)
        if pattern in seen_scope_patterns:
            continue
        seen_scope_patterns.add(pattern)
        scope_details.append(
            {
                **item,
                "pattern": pattern,
                "reason": str(item.get("reason") or "").replace("private target name", "target name"),
            }
        )
    redacted["authorizedScope"] = scope_details
    snapshot = dict(contract.get("projectSnapshot") or {})
    snapshot["xcodeProjects"] = [
        redact_top_level_name(str(project), sensitive_names) for project in snapshot.get("xcodeProjects") or []
    ]
    scan_scope = dict(snapshot.get("scanScope") or {})
    scan_scope["skippedDirs"] = [
        redact_top_level_name(str(item), sensitive_names) for item in scan_scope.get("skippedDirs") or []
    ]
    snapshot["scanScope"] = scan_scope
    redacted["projectSnapshot"] = snapshot

    validation = dict(contract.get("validationContract") or {})
    validation["required"] = [
        redact_validation_item(item, sensitive_names)
        for item in validation.get("required") or []
        if isinstance(item, dict)
    ]
    redacted["validationContract"] = validation
    redacted["shareableRedactions"] = {
        "targetNames": True,
        "reason": "External target repo names are redacted in shareable task contracts. Run without --shareable for machine-verification contracts against the private checkout.",
    }
    return redacted


def default_allowed(profile: str, root: Path | None = None) -> list[str]:
    if profile == "ios":
        if root is not None:
            discovered = discover_swift_dirs(root, "Sources") + discover_swift_dirs(root, "Tests") + discover_root_swift_dirs(root)
            if discovered:
                return sorted(dict.fromkeys(discovered))
        return ["Sources/**", "Tests/**", "*.swift"]
    if profile == "web":
        return ["src/**", "app/**", "pages/**", "components/**", "tests/**", "package.json", "README.md", "docs/**"]
    if profile == "backend":
        return ["src/**", "app/**", "tests/**", "pyproject.toml", "requirements.txt", "go.mod", "README.md", "docs/**"]
    return ["bin/**", "scripts/**", "tests/**", "fixtures/**", "docs/**", "README.md", "CHANGELOG.md", "VERSION", "plugins/**"]


def default_forbidden(profile: str) -> list[str]:
    patterns = [
        ".git/**",
        ".env",
        ".env.*",
        "**/*secret*",
        "**/*Secret*",
        "**/*key*",
        ".github/workflows/release*.yml",
        ".github/workflows/release*.yaml",
    ]
    if profile == "ios":
        patterns.extend(["**/*.entitlements", "**/Info.plist", "**/project.pbxproj"])
    return patterns


def discover_xcode_schemes(root: Path) -> list[str]:
    schemes = []
    for path in root.glob("*.xcodeproj/xcshareddata/xcschemes/*.xcscheme"):
        schemes.append(path.stem)
    for path in root.glob("*.xcworkspace/xcshareddata/xcschemes/*.xcscheme"):
        schemes.append(path.stem)
    return sorted(dict.fromkeys(schemes))


def validation_item(command: str, expected: str, success: str, failure: str, requirement_id: str | None = None) -> dict[str, Any]:
    return {
        "requirementId": requirement_id or slug(command),
        "command": command,
        "expectedArtifact": expected,
        "successCondition": success,
        "failureMeaning": failure,
    }


def default_validation(profile: str, root: Path) -> list[dict[str, Any]]:
    if (root / "bin" / "shipguard").is_file():
        return [
            validation_item(
                "./bin/shipguard validate",
                "validation log",
                "ShipGuard bundle validation exits 0",
                "Workflow package integrity remains unproven",
                "shipguard-bundle-validation",
            ),
            validation_item(
                "./tests/cli_smoke_test.sh",
                "CLI smoke log",
                "Public CLI smoke tests exit 0",
                "The public command surface may be broken",
                "shipguard-cli-smoke",
            ),
        ]
    if profile == "ios":
        schemes = discover_xcode_schemes(root)
        if schemes:
            scheme = schemes[0]
            return [
                validation_item(
                    f"xcodebuild test -scheme {scheme}",
                    f"{scheme}.xcresult or test log",
                    "Selected iOS scheme tests pass",
                    "iOS behavior remains unproven",
                    f"{slug(scheme)}-scheme-tests",
                )
            ]
        if (root / "Package.swift").is_file():
            return [
                validation_item(
                    "swift test",
                    "swift test log",
                    "SwiftPM tests pass",
                    "SwiftPM behavior remains unproven",
                    "swiftpm-tests",
                )
            ]
        return [
            validation_item(
                "shipguard choose-ios-validation-scheme",
                "selected scheme name",
                "Developer selects an executable shared scheme for this task",
                "ShipGuard cannot emit an executable iOS validation command until a scheme is chosen",
                "ios-validation-scheme-selection",
            )
        ]
    if profile == "web":
        return [
            validation_item("npm test", "test log", "Targeted web tests pass", "Web behavior remains unproven", "web-tests")
        ]
    return [
        validation_item(
            "shipguard choose-validation-command",
            "selected validation command",
            "Developer selects the repository's targeted validation command",
            "Behavior remains unproven until an executable validation command is chosen",
            "validation-command-selection",
        )
    ]


def make_task_id(goal: str, profile: str, root: Path) -> str:
    digest = hashlib.sha256(f"{goal}\n{profile}\n{root.resolve()}".encode("utf-8")).hexdigest()[:8].upper()
    return f"SG-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d')}-{digest}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare or verify a proof-gated ShipGuard task contract.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", description="Create a durable task contract before Codex edits.")
    prepare.add_argument("goal_positional", nargs="?", help="Task goal, equivalent to --goal")
    prepare.add_argument("--goal", help="Task goal")
    prepare.add_argument("--path", default=".", help="Target repository path")
    prepare.add_argument("--out", required=True, help="Output directory")
    prepare.add_argument("--profile", choices=PROFILES, default="auto")
    prepare.add_argument("--allowed", action="append", default=[], help="Authorized file glob")
    prepare.add_argument("--forbidden", action="append", default=[], help="Forbidden file glob")
    prepare.add_argument("--validation", action="append", default=[], help="Validation command required as evidence")
    prepare.add_argument("--claim", action="append", default=[], help="Agent claim to track")
    prepare.add_argument("--shipguard-eval", action="store_true", help="Include ShipGuard product-QA boundary language")
    prepare.add_argument("--shareable", action="store_true", help="Redact local absolute paths")
    prepare.add_argument("--json", action="store_true", help="Print JSON to stdout")
    prepare.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")

    verify = subparsers.add_parser("verify", description="Verify a diff and evidence against a task contract.")
    verify.add_argument("--task", required=True, help="shipguard-task.json or a directory containing it")
    verify.add_argument("--out", required=True, help="Output directory")
    verify.add_argument("--diff", help="Unified diff/patch file")
    verify.add_argument("--evidence", action="append", default=[], help="Evidence receipt/log file")
    verify.add_argument("--claim", action="append", default=[], help="Agent claim to verify")
    verify.add_argument(
        "--reviewer-disposition",
        choices=("accepted", "dismissed", "follow-up", "unknown"),
        default="",
        help="Optional maintainer outcome for local recurring-signal tuning.",
    )
    verify.add_argument("--reviewer-note", default="", help="Optional short note for --reviewer-disposition.")
    verify.add_argument("--json", action="store_true", help="Print JSON to stdout")
    verify.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def safe_command_arg(value: str | None, placeholder: str) -> str:
    text = str(value or "").strip()
    if not text:
        return placeholder
    if Path(text).is_absolute():
        return placeholder
    return shlex.quote(text)


def build_prepare_quickstart_replay() -> dict[str, Any]:
    verify_template = (
        "shipguard verify --task <task-dir>/shipguard-task.json "
        "--diff <patch.diff> --evidence <validation-receipt.json> "
        "--claim <scoped-claim> --out <verdict-dir>"
    )
    return {
        "phase": "prepare",
        "taskArtifact": "shipguard-task.json",
        "markdownArtifact": "shipguard-task.md",
        "firstUsefulVerdictCommand": verify_template,
        "proofInputs": ["<patch.diff>", "<validation-receipt.json>", "<scoped-claim>"],
        "successSignal": "shipguard-verdict.json returns pass, review, blocked, or incomplete with one nextAction.",
        "connects": [
            "goal",
            "riskClassification",
            "authorizedFiles",
            "protectedBoundaries",
            "validationContract",
            "agentClaims",
            "verdict",
            "nextAction",
        ],
        "boundary": "Use this replay contract to reach the first verdict; it is not proof that the target app was changed or fixed.",
    }


def build_verify_quickstart_replay(args: argparse.Namespace, report: dict[str, Any]) -> dict[str, Any]:
    evidence_parts = [
        f"--evidence {safe_command_arg(path, '<validation-receipt.json>')}"
        for path in (args.evidence or ["<validation-receipt.json>"])
    ]
    claim_parts = [f"--claim {shlex.quote(str(claim))}" for claim in args.claim or []]
    replay_command = " ".join(
        part
        for part in [
            "shipguard verify",
            f"--task {safe_command_arg(args.task, '<shipguard-task.json>')}",
            f"--diff {safe_command_arg(args.diff, '<patch.diff>')}" if args.diff else "--diff <patch.diff>",
            *evidence_parts,
            *claim_parts,
            "--out <verdict-dir>",
        ]
        if part
    )
    proof_report = report.get("proofReport") if isinstance(report.get("proofReport"), dict) else {}
    next_action = report.get("nextAction") if isinstance(report.get("nextAction"), dict) else {}
    return {
        "phase": "verify",
        "status": report.get("status"),
        "replayCommand": replay_command,
        "fastVerdict": proof_report.get("copyReadyText"),
        "reviewPacket": [
            "shipguard-verdict.json",
            "shipguard-verdict.md",
            "<shipguard-task.json>",
            "<patch.diff>",
            "<validation-receipt.json>",
        ],
        "nextAction": next_action.get("command"),
        "successSignal": "Reviewer can replay the same verdict shape and inspect the JSON plus Markdown packet before merging.",
        "boundary": "Replay confirms ShipGuard's verdict logic for the supplied task, diff, receipts, and claims; it does not replace target validation.",
    }


def build_unsupported_claim_replay(
    report: dict[str, Any],
    *,
    rejected_phrases: list[str],
    manual_claims: list[str] | None = None,
) -> dict[str, Any]:
    claim_checks = report.get("claimChecks") if isinstance(report.get("claimChecks"), dict) else {}
    decisions = claim_checks.get("claimDecisions") if isinstance(claim_checks.get("claimDecisions"), list) else []
    manual_claim_set = {str(claim) for claim in manual_claims or []}
    rejected_phrase_set = {str(phrase) for phrase in rejected_phrases}
    unsupported_decisions = []
    rejected_decisions = []
    manual_proof_decisions = []
    for item in decisions:
        if not isinstance(item, dict) or item.get("status") not in {"rejected", "needs-manual-proof"}:
            continue
        claim = str(item.get("claim") or "")
        phrases = {str(phrase) for phrase in item.get("requiredProofPhrases") or []}
        matches_rejected_phrase = bool(rejected_phrase_set and phrases & rejected_phrase_set)
        matches_manual_claim = bool(manual_claim_set and claim in manual_claim_set)
        if not matches_rejected_phrase and not matches_manual_claim:
            continue
        rejected_phrase_set.update(phrases)
        row = {
            "claim": item.get("claim"),
            "status": item.get("status"),
            "reason": item.get("reason"),
            "requiredProofPhrases": sorted(phrases),
            "resolution": "Revise the claim or attach structured evidence receipts that prove it.",
        }
        unsupported_decisions.append(row)
        if item.get("status") == "rejected":
            rejected_decisions.append(row)
        else:
            manual_proof_decisions.append(row)
    replay = report.get("quickstartReplay") if isinstance(report.get("quickstartReplay"), dict) else {}
    replay_status = "blocked" if rejected_decisions else "review"
    if manual_proof_decisions and not rejected_decisions:
        command = "Revise the completion claim, or capture the required manual/physical-device proof receipt, then rerun shipguard verify."
        expected_artifact = "updated claim or manual/physical-device proof receipt"
        failure_meaning = "broad completion claim still needs manual or physical-device proof"
        resolves = ["unsupported-completion-claim", "manual-device-proof"]
    else:
        command = "Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify."
        expected_artifact = "updated claim or structured evidence receipt"
        failure_meaning = "unsupported completion claim without evidence"
        resolves = ["unsupported-completion-claim"]
    claim_next_action = {
        "owner": "developer",
        "command": command,
        "expectedArtifact": expected_artifact,
        "successCondition": "No unsupported completion claim remains",
        "failureMeaning": failure_meaning,
        "resolves": resolves,
        "priority": 6,
    }
    return {
        "schemaVersion": 1,
        "status": replay_status,
        "unsupportedPhrases": sorted(rejected_phrase_set),
        "unsupportedClaimCount": len(unsupported_decisions),
        "unsupportedClaims": unsupported_decisions,
        "rejectedClaimCount": len(rejected_decisions),
        "rejectedClaims": rejected_decisions,
        "manualProofClaimCount": len(manual_proof_decisions),
        "manualProofClaims": manual_proof_decisions,
        "replayCommand": replay.get("replayCommand"),
        "fastVerdict": replay.get("fastVerdict"),
        "reviewPacket": replay.get("reviewPacket") or [],
        "nextAction": claim_next_action,
        "proofBoundary": (
            "This replay proves ShipGuard did not accept the supplied completion claim against the attached task, diff, "
            "and evidence receipts. It does not prove the claimed behavior; the claim must be narrowed or backed by "
            "new structured proof or manual/device proof."
        ),
        "nonClaims": [
            "An unsupported-claim replay is not product proof.",
            "A review or blocked verdict is not a merge or release approval.",
            "Changing the wording is not enough unless the new claim matches the attached evidence.",
        ],
    }


def build_validation_contract(commands: list[str], defaults: list[dict[str, Any]]) -> dict[str, Any]:
    if commands:
        required = [
            {
                "requirementId": slug(command),
                "command": command,
                "expectedArtifact": "validation log",
                "successCondition": "Command exits 0 and the receipt is attached to shipguard verify",
                "failureMeaning": "Claimed behavior remains unproven",
            }
            for command in commands
        ]
    else:
        required = defaults
    return {
        "required": required,
        "manualProof": [
            {
                "check": "Device-only or account-only behavior",
                "expectedArtifact": "manual receipt or screenshot reference",
                "successCondition": "Human operator records the observed state",
                "failureMeaning": "ShipGuard must not treat simulator or source evidence as release proof",
            }
        ],
    }


def prepare_contract(args: argparse.Namespace) -> dict[str, Any]:
    goal = (args.goal or args.goal_positional or "").strip()
    if not goal:
        fail("prepare requires --goal or a positional goal")
    root = Path(args.path)
    if not root.exists():
        fail(f"path does not exist: {root}")
    detected_profile, signals = detect_profile(root)
    profile = detected_profile if args.profile == "auto" else args.profile
    if args.profile != "auto":
        signals.append(f"override:{args.profile}")
    default_scope, default_scope_details = default_authorized_scope(profile, root, goal)
    allowed = args.allowed or default_scope
    authorized_scope_details = (
        [{"pattern": pattern, "reason": "Explicitly supplied with --allowed."} for pattern in args.allowed]
        if args.allowed
        else default_scope_details
    )
    forbidden = args.forbidden or default_forbidden(profile)
    risk = classify_risk(goal, profile)
    risk["approvalPolicy"]["forbiddenInThisTask"] = forbidden
    contract = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard prepare",
        "surface": "ShipGuard Task Contract",
        "status": "prepared",
        "taskId": make_task_id(goal, profile, root),
        "generatedAt": utc_now(),
        "goal": goal,
        "projectSnapshot": collect_project_snapshot(root, profile, signals, args.shareable),
        "riskClassification": risk,
        "protectedBoundaries": forbidden,
        "authorizedFiles": allowed,
        "authorizedScope": authorized_scope_details,
        "validationContract": build_validation_contract(args.validation, default_validation(profile, root)),
        "configurationPolicy": load_configuration(
            root,
            shareable=args.shareable,
            redact_value=lambda value: redact_sensitive_name_occurrences(
                value,
                collect_shareable_sensitive_names(root),
            ),
        ),
        "domainPackSDK": DEFAULT_DOMAIN_PACK_REGISTRY.manifest(),
        "agentClaims": args.claim,
        "evidence": [],
        "verdict": {
            "status": "prepared",
            "reason": "Task contract prepared; run Codex under this scope, then run shipguard verify with diff and evidence.",
        },
        "quickstartReplay": build_prepare_quickstart_replay(),
        "nextAction": {
            "owner": "developer",
            "command": "Run Codex under this task contract, then run shipguard verify --task <out>/shipguard-task.json --diff <patch> --evidence <receipt>",
            "expectedArtifact": "shipguard-verdict.json",
            "successCondition": "Verify returns pass or an exact blocked next action",
            "failureMeaning": "The change remains a disconnected report without proof-gated verdict",
        },
    }
    if args.shipguard_eval:
        contract["scopeBoundary"] = {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Evaluate ShipGuard's task-contract usefulness; do not convert target-app findings into app work.",
        }
        contract["reportQualityQuestions"] = [
            "Did prepare produce one durable object connecting goal, risk, scope, proof, claims, and verdict?",
        ]
    if args.shareable and not path_is_within(root, Path.cwd()):
        contract = redact_external_shareable_contract(contract, root)
    risk_pack = build_prepare_domain_risk_pack(contract, root, args.shareable)
    if risk_pack:
        contract["domainRiskPack"] = risk_pack
        contract["domainPackSDK"] = DEFAULT_DOMAIN_PACK_REGISTRY.manifest(active_pack=str(risk_pack.get("id") or ""))
        if isinstance(risk_pack.get("nextAction"), dict):
            contract["nextAction"] = dict(risk_pack["nextAction"])
        existing_questions = contract.get("reportQualityQuestions") or []
        contract["reportQualityQuestions"] = existing_questions + risk_pack.get("reportQualityQuestions", [])
    return contract


def match_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.rstrip("/") + "/**") for pattern in patterns)


def clean_diff_path(value: str) -> str:
    value = value.strip()
    if value.startswith(("a/", "b/")):
        value = value[2:]
    return value


def parse_diff_files(diff: Path | None) -> list[dict[str, Any]]:
    if diff is None:
        return []
    if not diff.is_file():
        fail(f"diff file not found: {diff}")
    files: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def finish_current() -> None:
        if current is None:
            return
        path = current.get("path") or current.get("oldPath")
        if not path or path == "/dev/null":
            return
        current["path"] = path
        current["isTest"] = is_test_path(path)
        current["behaviorCategoryEvidence"] = behavior_category_details(current)
        current["behaviorCategories"] = [item["category"] for item in current["behaviorCategoryEvidence"]]
        files.append(current.copy())

    for line in diff.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("diff --git "):
            finish_current()
            parts = line.split()
            old_path = clean_diff_path(parts[2]) if len(parts) > 2 else ""
            new_path = clean_diff_path(parts[3]) if len(parts) > 3 else old_path
            current = {
                "path": new_path,
                "oldPath": old_path,
                "changeType": "modified",
                "addedLines": 0,
                "removedLines": 0,
                "addedSamples": [],
                "removedSamples": [],
            }
            continue
        if current is None:
            continue
        if line.startswith("new file mode"):
            current["changeType"] = "added"
        elif line.startswith("deleted file mode"):
            current["changeType"] = "deleted"
        elif line.startswith("Binary files "):
            current["changeType"] = "binary-modified"
            current["isBinary"] = True
        elif line.startswith("rename from "):
            current["oldPath"] = clean_diff_path(line.removeprefix("rename from "))
            current["changeType"] = "renamed"
        elif line.startswith("rename to "):
            current["path"] = clean_diff_path(line.removeprefix("rename to "))
            current["changeType"] = "renamed"
        elif line.startswith("--- "):
            old_path = clean_diff_path(line[4:])
            if old_path == "/dev/null":
                current["changeType"] = "added"
            else:
                current["oldPath"] = old_path
        elif line.startswith("+++ "):
            new_path = clean_diff_path(line[4:])
            if new_path == "/dev/null":
                current["changeType"] = "deleted"
                current["path"] = current.get("oldPath")
            else:
                current["path"] = new_path
        elif line.startswith("+") and not line.startswith("+++"):
            current["addedLines"] += 1
            if len(current["addedSamples"]) < 8:
                current["addedSamples"].append(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            current["removedLines"] += 1
            if len(current["removedSamples"]) < 8:
                current["removedSamples"].append(line[1:].strip())
    finish_current()
    deduped: dict[str, dict[str, Any]] = {}
    for item in files:
        path = str(item["path"])
        if path not in deduped:
            deduped[path] = item
            continue
        existing = deduped[path]
        existing["addedLines"] = int(existing.get("addedLines") or 0) + int(item.get("addedLines") or 0)
        existing["removedLines"] = int(existing.get("removedLines") or 0) + int(item.get("removedLines") or 0)
        existing["behaviorCategories"] = sorted(set(existing.get("behaviorCategories") or []) | set(item.get("behaviorCategories") or []))
    return [deduped[path] for path in sorted(deduped)]


def parse_diff_paths(diff: Path | None) -> list[str]:
    return [str(item["path"]) for item in parse_diff_files(diff)]


def is_test_path(path: str) -> bool:
    lowered = path.lower()
    name = Path(path).name.lower()
    return "test" in name or "/tests/" in f"/{lowered}/" or "xctest" in lowered


def add_category(categories: dict[str, list[str]], category: str, evidence: str) -> None:
    categories.setdefault(category, [])
    if evidence not in categories[category]:
        categories[category].append(evidence)


def behavior_category_details(file_change: dict[str, Any]) -> list[dict[str, Any]]:
    path = str(file_change.get("path") or "")
    text = "\n".join(
        [
            path,
            str(file_change.get("oldPath") or ""),
            "\n".join(file_change.get("addedSamples") or []),
            "\n".join(file_change.get("removedSamples") or []),
        ]
    ).lower()
    categories: dict[str, list[str]] = {}
    if is_test_path(path):
        add_category(categories, "test", "Path or filename indicates a test file.")
    if path.endswith((".md", ".rst", ".txt")) or path.startswith("docs/"):
        add_category(categories, "documentation", "Path is documentation-oriented.")
    if path.startswith(".github/workflows/"):
        add_category(categories, "release-workflow", "Path is a GitHub Actions workflow.")
    if path.endswith((".entitlements",)):
        add_category(categories, "entitlement", "Path is an entitlement file.")
        add_category(categories, "build-configuration", "Entitlement changes affect build/runtime configuration.")
    if path.endswith(("Info.plist", ".plist")) or "project.pbxproj" in path:
        add_category(categories, "build-configuration", "Path is a plist or Xcode project configuration file.")
    if any(token in text for token in ("permission", "requestauthorization", "authorization", "provisional")):
        add_category(categories, "permission", "Diff or path references permission or authorization state.")
    if "notification" in text or "unusernotification" in text:
        add_category(categories, "notification", "Diff or path references notification behavior.")
    if any(token in text for token in ("storekit", "purchase", "subscription", "entitlement")):
        add_category(categories, "storekit", "Diff or path references StoreKit, purchases, subscriptions, or entitlements.")
    if any(token in text for token in ("widget", "appintent", "app intent", "activitykit", "live activity")):
        if "widget" in text:
            add_category(categories, "widget", "Diff or path references widget behavior.")
        if "appintent" in text or "app intent" in text:
            add_category(categories, "app-intent", "Diff or path references App Intents.")
    if any(token in text for token in ("database", "coredata", "swiftdata", "userdefaults", "persistence")):
        add_category(categories, "persistence", "Diff or path references persistence state.")
    if any(token in text for token in ("migration", "schema")):
        add_category(categories, "migration", "Diff or path references migration or schema behavior.")
    if any(token in text for token in ("appdelegate", "scenephase", "lifecycle", "applicationdid")):
        add_category(categories, "app-lifecycle", "Diff or path references app lifecycle hooks.")
    if any(token in text for token in ("background", "bgprocessing", "bgapprefresh")):
        add_category(categories, "background-execution", "Diff or path references background execution.")
    if any(token in text for token in ("privacy", "xcprivacy", "tracking", "permission")):
        add_category(categories, "privacy", "Diff or path references privacy, tracking, or permissions.")
    if any(token in text for token in ("security", "secret", "keychain", "token")):
        add_category(categories, "security", "Diff or path references security-sensitive concepts.")
    if any(token in text for token in ("fastlane", "testflight", "release")):
        add_category(categories, "release-workflow", "Diff or path references release automation.")
    if not categories:
        add_category(categories, "source", "Changed file is source-like but no higher-risk category matched.")
    return [
        {"category": category, "evidence": evidence, "confidence": "high" if len(evidence) > 1 else "medium"}
        for category, evidence in sorted(categories.items())
    ]


def behavior_categories(file_change: dict[str, Any]) -> list[str]:
    return [item["category"] for item in behavior_category_details(file_change)]


def resolve_task(path: str) -> Path:
    task = Path(path)
    if task.is_dir():
        task = task / "shipguard-task.json"
    return task


def evidence_entries(paths: list[str]) -> list[dict[str, Any]]:
    entries, _summary = load_receipt_evidence_entries(paths)
    return entries


def significant_command_tokens(command: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_./:-]+", command.lower())
    ignored = {"the", "and", "or", "run", "with", "a", "an", "to", "for"}
    return [token for token in tokens if len(token) > 2 and token not in ignored][:8]


def parse_timestamp(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    except ValueError:
        return None


def command_matches(required: str, observed: str) -> bool:
    return " ".join(required.split()).lower() == " ".join(observed.split()).lower()


def validation_coverage(
    required: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    task_generated_at: str | None = None,
) -> dict[str, Any]:
    present_evidence = [item for item in evidence if item.get("present")]
    covered: list[dict[str, Any]] = []
    uncovered: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    downgraded: list[dict[str, Any]] = []
    task_time = parse_timestamp(task_generated_at)
    for item in required:
        command = str(item.get("command") or "")
        requirement_id = str(item.get("requirementId") or slug(command))
        matched_receipts = []
        for receipt in present_evidence:
            receipt_id = str(receipt.get("validationId") or "")
            receipt_command = str(receipt.get("command") or "")
            command_ok = command_matches(command, receipt_command)
            id_ok = bool(receipt_id and receipt_id == requirement_id)
            if not (command_ok or id_ok):
                continue
            if receipt.get("kind") != "structured-validation":
                downgraded.append(
                    {
                        "requirementId": requirement_id,
                        "receiptId": receipt.get("receiptId"),
                        "path": receipt.get("path"),
                        "receiptType": receipt.get("receiptType"),
                        "command": receipt_command,
                        "reason": receipt.get("reason")
                        or "Receipt matched this requirement but is not a validation-compatible receipt type.",
                    }
                )
                continue
            completed = parse_timestamp(receipt.get("completedAt"))
            stale = bool(task_time and completed and completed < task_time)
            if receipt.get("receiptStatus") == "pass" and not stale:
                matched_receipts.append(
                    {
                        "receiptId": receipt.get("receiptId"),
                        "path": receipt.get("path"),
                        "command": receipt_command,
                        "matchedBy": "validationId" if id_ok else "command",
                    }
                )
            else:
                invalid.append(
                    {
                        "requirementId": requirement_id,
                        "receiptId": receipt.get("receiptId"),
                        "path": receipt.get("path"),
                        "command": receipt_command,
                        "exitCode": receipt.get("exitCode"),
                        "status": receipt.get("status"),
                        "reason": "receipt predates task contract" if stale else receipt.get("reason"),
                    }
                )
        if matched_receipts:
            covered.append({"requirementId": requirement_id, "command": command, "matchedEvidence": matched_receipts})
        else:
            uncovered.append(
                {
                    "requirementId": requirement_id,
                    "command": command,
                    "expectedArtifact": item.get("expectedArtifact"),
                    "successCondition": item.get("successCondition"),
                    "failureMeaning": item.get("failureMeaning"),
                }
            )
    if invalid:
        status = "invalid"
    elif not required:
        status = "not-required"
    elif uncovered:
        status = "missing"
    else:
        status = "covered"
    return {
        "status": status,
        "requiredCommands": required,
        "coveredCommands": covered,
        "uncoveredCommands": uncovered,
        "invalidReceipts": invalid,
        "downgradedReceipts": downgraded,
        "evidenceReceiptCount": len(present_evidence),
        "missingEvidenceFiles": [item["path"] for item in evidence if not item.get("present")],
    }


def public_evidence_entries(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in item.items() if not key.startswith("_")} for item in evidence]


def unsupported_claims(claims: list[str], evidence_covered: bool) -> list[str]:
    if evidence_covered:
        return []
    lowered = "\n".join(claims).lower()
    return [phrase for phrase in CLAIM_REQUIRES_PROOF if phrase in lowered]


def claim_decisions(claims: list[str], coverage: dict[str, Any], manual_proof_required: bool) -> list[dict[str, Any]]:
    decisions = []
    coverage_ok = coverage.get("status") in {"covered", "not-required"}
    for claim in claims:
        lowered = claim.lower()
        required_phrases = [phrase for phrase in CLAIM_REQUIRES_PROOF if phrase in lowered]
        if required_phrases and not coverage_ok:
            status = "rejected"
            reason = "Broad completion claim lacks covered validation evidence."
        elif required_phrases and manual_proof_required:
            status = "needs-manual-proof"
            reason = "Broad completion claim has local evidence but manual/device proof remains separate."
        else:
            status = "accepted"
            reason = "Claim does not exceed attached evidence."
        decisions.append(
            {
                "claim": claim,
                "status": status,
                "requiredProofPhrases": required_phrases,
                "reason": reason,
            }
        )
    return decisions


def behavior_category_summary(diff_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for item in diff_files:
        for category in item.get("behaviorCategories") or []:
            grouped.setdefault(category, []).append(str(item.get("path")))
    return [
        {
            "category": category,
            "fileCount": len(sorted(set(paths))),
            "files": sorted(set(paths))[:12],
        }
        for category, paths in sorted(grouped.items())
    ]


def deleted_test_changes(diff_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deleted = []
    for item in diff_files:
        if item.get("isTest") and (item.get("changeType") == "deleted" or int(item.get("removedLines") or 0) > 0):
            deleted.append(
                {
                    "path": item.get("path"),
                    "changeType": item.get("changeType"),
                    "removedLines": item.get("removedLines"),
                    "reason": "Test file or test content was removed; reviewers need proof that validation coverage did not shrink.",
                }
            )
    return deleted


def contract_findings(
    *,
    changed: list[str],
    forbidden_touched: list[str],
    out_of_scope: list[str],
    coverage: dict[str, Any],
    deleted_tests: list[dict[str, Any]],
    rejected_claims: list[str],
    manual_claims: list[str],
    domain_workflows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in forbidden_touched:
        findings.append(
            make_finding(
                rule_id="task-contract.protected-boundary",
                severity="block",
                subject=path,
                source_key=f"protected:{path}",
                path=path,
                reason="Changed file touches a protected boundary from the task contract.",
                proof_boundary="Suppression applies only to this exact protected path fingerprint and does not authorize other protected files.",
            )
        )
    for path in out_of_scope:
        findings.append(
            make_finding(
                rule_id="task-contract.out-of-scope-diff",
                severity="block",
                subject=path,
                source_key=f"scope:{path}",
                path=path,
                reason="Changed file is outside the authorized task scope.",
                proof_boundary="Suppression applies only to this exact out-of-scope path fingerprint and does not expand the task scope.",
            )
        )
    for item in coverage.get("invalidReceipts") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "invalid-validation-receipt")
        findings.append(
            make_finding(
                rule_id="task-contract.invalid-validation-receipt",
                severity="block",
                subject=requirement_id,
                source_key=f"validation-invalid:{requirement_id}",
                requirement_id=requirement_id,
                reason=str(item.get("reason") or "Structured validation receipt is invalid."),
                proof_boundary="Suppression applies only to this validation requirement; other invalid receipts remain blocking.",
            )
        )
    for item in coverage.get("downgradedReceipts") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "downgraded-evidence-receipt")
        findings.append(
            make_finding(
                rule_id="task-contract.downgraded-evidence-receipt",
                severity="review",
                subject=requirement_id,
                source_key=f"validation-downgraded:{requirement_id}",
                requirement_id=requirement_id,
                reason=str(item.get("reason") or "Evidence receipt was downgraded and cannot prove the validation command."),
                proof_boundary="Suppression applies only to this downgraded receipt requirement; validation coverage still needs compatible proof.",
            )
        )
    for item in coverage.get("uncoveredCommands") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "missing-validation")
        findings.append(
            make_finding(
                rule_id="task-contract.missing-validation",
                severity="review",
                subject=requirement_id,
                source_key=f"validation-missing:{requirement_id}",
                requirement_id=requirement_id,
                reason=str(item.get("failureMeaning") or "Required validation remains uncovered."),
                proof_boundary="Suppression applies only to this missing validation requirement; new validation gaps remain visible.",
            )
        )
    for path in coverage.get("missingEvidenceFiles") or []:
        findings.append(
            make_finding(
                rule_id="task-contract.missing-evidence-file",
                severity="review",
                subject=str(path),
                source_key=f"missing-evidence:{path}",
                path=str(path),
                reason="Evidence file referenced by verify was not found.",
                proof_boundary="Suppression applies only to this missing evidence path fingerprint.",
            )
        )
    for item in deleted_tests:
        path = str(item.get("path") or "deleted-test")
        findings.append(
            make_finding(
                rule_id="task-contract.deleted-test",
                severity="review",
                subject=path,
                source_key=f"deleted-test:{path}",
                path=path,
                reason=str(item.get("reason") or "Test coverage was deleted or reduced."),
                proof_boundary="Suppression applies only to this exact deleted-test fingerprint; other removed tests remain visible.",
            )
        )
    for phrase in rejected_claims:
        findings.append(
            make_finding(
                rule_id="task-contract.unsupported-claim",
                severity="block",
                subject=phrase,
                source_key=f"unsupported-claim:{phrase}",
                reason="Completion claim exceeds attached evidence.",
                proof_boundary="Suppression applies only to this exact claim phrase and does not prove the claimed behavior.",
            )
        )
    for claim in manual_claims:
        findings.append(
            make_finding(
                rule_id="task-contract.manual-proof-claim",
                severity="review",
                subject=claim,
                source_key=f"manual-claim:{claim}",
                reason="Broad completion claim still needs manual or device-only proof.",
                proof_boundary="Suppression applies only to this exact manual-proof claim and does not replace device proof.",
            )
        )
    if not changed:
        findings.append(
            make_finding(
                rule_id="task-contract.incomplete-diff",
                severity="review",
                subject="no-changed-files",
                source_key="incomplete-diff:no-changed-files",
                reason="No usable diff was provided or no changed files were detected.",
                proof_boundary="Suppression applies only to an intentionally empty-diff review packet.",
            )
        )
    for field, workflow in domain_workflows.items():
        if workflow.get("reviewRequired"):
            workflow_id = str(workflow.get("id") or field)
            findings.append(
                make_finding(
                    rule_id="task-contract.domain-workflow-proof",
                    severity="review",
                    subject=workflow_id,
                    source_key=f"domain-workflow:{field}",
                    reason=f"{workflow_id} proof lanes are not fully satisfied.",
                    proof_boundary="Suppression applies only to this domain workflow result; new domain gaps remain visible.",
                )
            )
    return findings


def accepted_source_keys(baseline_result: dict[str, Any]) -> set[str]:
    return {str(item.get("sourceKey") or "") for item in baseline_result.get("acceptedFindings") or []}


def adjusted_validation_coverage(coverage: dict[str, Any], accepted: set[str]) -> dict[str, Any]:
    adjusted = dict(coverage)
    invalid = []
    for item in coverage.get("invalidReceipts") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "invalid-validation-receipt")
        if f"validation-invalid:{requirement_id}" not in accepted:
            invalid.append(item)
    downgraded = []
    for item in coverage.get("downgradedReceipts") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "downgraded-evidence-receipt")
        if f"validation-downgraded:{requirement_id}" not in accepted:
            downgraded.append(item)
    uncovered = []
    for item in coverage.get("uncoveredCommands") or []:
        requirement_id = str(item.get("requirementId") or item.get("command") or "missing-validation")
        if f"validation-missing:{requirement_id}" not in accepted:
            uncovered.append(item)
    missing_files = [
        item
        for item in coverage.get("missingEvidenceFiles") or []
        if f"missing-evidence:{item}" not in accepted
    ]
    adjusted["invalidReceipts"] = invalid
    adjusted["downgradedReceipts"] = downgraded
    adjusted["uncoveredCommands"] = uncovered
    adjusted["missingEvidenceFiles"] = missing_files
    original_status = str(coverage.get("status") or "")
    if invalid:
        adjusted["status"] = "invalid"
    elif uncovered:
        adjusted["status"] = "missing"
    elif original_status in {"invalid", "missing"}:
        adjusted["status"] = "suppressed"
    else:
        adjusted["status"] = original_status
    adjusted["baselineAdjusted"] = adjusted["status"] != original_status
    adjusted["originalStatus"] = original_status
    return adjusted


def adjusted_domain_workflows(domain_workflows: dict[str, dict[str, Any]], accepted: set[str]) -> dict[str, dict[str, Any]]:
    adjusted: dict[str, dict[str, Any]] = {}
    for field, workflow in domain_workflows.items():
        item = dict(workflow)
        if item.get("reviewRequired") and f"domain-workflow:{field}" in accepted:
            item["reviewRequired"] = False
            item["baselineAccepted"] = True
        adjusted[field] = item
    return adjusted


def diff_file_summaries(diff_files: list[dict[str, Any]], allowed: list[str], forbidden: list[str]) -> list[dict[str, Any]]:
    summaries = []
    for item in diff_files:
        path = str(item.get("path") or "")
        summaries.append(
            {
                "path": path,
                "oldPath": item.get("oldPath"),
                "changeType": item.get("changeType"),
                "addedLines": item.get("addedLines"),
                "removedLines": item.get("removedLines"),
                "isTest": item.get("isTest"),
                "isBinary": bool(item.get("isBinary")),
                "behaviorCategories": item.get("behaviorCategories") or [],
                "behaviorCategoryEvidence": item.get("behaviorCategoryEvidence") or [],
                "scope": {
                    "authorized": not allowed or match_any(path, allowed),
                    "forbidden": match_any(path, forbidden),
                },
            }
        )
    return summaries


def build_diff_first_analysis(
    status: str,
    task: dict[str, Any],
    diff_files: list[dict[str, Any]],
    allowed: list[str],
    forbidden: list[str],
    out_of_scope: list[str],
    forbidden_touched: list[str],
    evidence: list[dict[str, Any]],
    coverage: dict[str, Any],
    decisions: list[dict[str, Any]],
    next_action: dict[str, str],
    blocking_reasons: list[str],
    review_reasons: list[str],
    evidence_receipt_schema: dict[str, Any] | None = None,
    notification_permission_workflow: dict[str, Any] | None = None,
    domain_workflows: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    deleted_tests = deleted_test_changes(diff_files)
    file_summaries = diff_file_summaries(diff_files, allowed, forbidden)
    source_files_changed = [
        item
        for item in file_summaries
        if not item.get("isTest") and "documentation" not in (item.get("behaviorCategories") or [])
    ]
    evidence_coverage = [
        {
            "requirementId": item.get("requirementId"),
            "status": "proven",
            "receipts": [receipt.get("receiptId") for receipt in item.get("matchedEvidence") or []],
        }
        for item in coverage.get("coveredCommands") or []
    ]
    evidence_coverage.extend(
        {
            "requirementId": item.get("requirementId"),
            "status": "missing",
            "receipts": [],
        }
        for item in coverage.get("uncoveredCommands") or []
    )
    analysis = {
        "status": status,
        "summary": "; ".join(blocking_reasons or review_reasons or ["diff, validation coverage, evidence, and claims match the task contract"]),
        "changedFileCount": len(diff_files),
        "changedFiles": file_summaries,
        "summaryCounts": {
            "changedFileCount": len(diff_files),
            "sourceFilesChanged": len(source_files_changed),
            "testFilesChanged": sum(1 for item in file_summaries if item.get("isTest")),
            "testsDeleted": len(deleted_tests),
            "protectedFilesTouched": len(forbidden_touched),
            "binaryFilesChanged": sum(1 for item in file_summaries if item.get("isBinary")),
        },
        "changedBehaviorCategories": behavior_category_summary(diff_files),
        "deletedTests": deleted_tests,
        "validationCoverage": coverage,
        "evidenceReceiptSchema": evidence_receipt_schema or receipt_schema_summary(evidence),
        "evidenceCoverage": evidence_coverage,
        "protectedBoundaryCrossings": {
            "outOfScope": out_of_scope,
            "forbiddenTouched": forbidden_touched,
        },
        "evidenceReceipts": public_evidence_entries(evidence),
        "claimDecisions": decisions,
        "mergeVerdict": {
            "status": status,
            "allowedToMerge": status == "pass",
            "reason": "; ".join(blocking_reasons or review_reasons or ["No blocking or review gaps found."]),
            "riskLevel": (task.get("riskClassification") or {}).get("level"),
        },
        "nextAction": next_action,
        "reportQualityQuestions": [
            "Did verify explain the exact changed files, behavior categories, deleted tests, validation coverage, evidence receipts, claims, and merge verdict?",
            "Can a reviewer decide the next action from shipguard-verdict.md without reading the raw patch first?",
        ],
    }
    domain_workflows = domain_workflows or {}
    if domain_workflows:
        analysis["domainWorkflows"] = domain_workflows
        for field, workflow in domain_workflows.items():
            analysis[field] = workflow
        for workflow in domain_workflows.values():
            analysis["reportQualityQuestions"].extend(workflow.get("reportQualityQuestions") or [])
    if notification_permission_workflow:
        analysis["notificationPermissionWorkflow"] = notification_permission_workflow
    return analysis


def build_diff_learning_handoff(
    *,
    status: str,
    diff_first: dict[str, Any],
    next_action: dict[str, Any],
    reviewer_disposition: str = "",
    reviewer_note: str = "",
) -> dict[str, Any]:
    scope = diff_first.get("protectedBoundaryCrossings") or {}
    coverage = diff_first.get("validationCoverage") or {}
    claims = diff_first.get("claimDecisions") or []
    deleted_tests = diff_first.get("deletedTests") or []
    changed_files = diff_first.get("changedFiles") or []
    changed_categories = diff_first.get("changedBehaviorCategories") or []
    signals: list[str] = []
    if scope.get("forbiddenTouched"):
        signals.append("protected-boundary-crossing")
    if scope.get("outOfScope"):
        signals.append("out-of-scope-diff")
    if deleted_tests:
        signals.append("deleted-test-coverage-risk")
    if coverage.get("uncoveredCommands"):
        signals.append("missing-validation-coverage")
    if any(item.get("status") == "rejected" for item in claims):
        signals.append("unsupported-completion-claim")
    if any(item.get("status") == "needs-manual-proof" for item in claims):
        signals.append("manual-proof-claim")
    if not signals and status == "pass":
        signals.append("scope-evidence-claim-match")

    recurrence_candidates = [signal for signal in signals if signal != "scope-evidence-claim-match"]
    disposition = reviewer_disposition or "not-recorded"
    disposition_followups = {
        "accepted": "Keep this verdict as positive local outcome evidence; do not weaken rules from one accepted packet.",
        "dismissed": "Keep the dismissed signal for recurrence review; tune only after repeated dismissed outcomes with matching context.",
        "follow-up": "Capture the follow-up fix or missing receipt, then rerun shipguard verify with the updated evidence.",
        "unknown": "Leave this verdict out of tuning decisions until a maintainer records a clearer outcome.",
        "not-recorded": "Ask the reviewer to rerun verify with --reviewer-disposition after deciding the packet.",
    }
    reviewer_disposition_receipt = {
        "schemaVersion": 1,
        "status": "present" if reviewer_disposition else "missing",
        "disposition": disposition,
        "note": reviewer_note,
        "trackedSignals": recurrence_candidates,
        "recommendedFollowUp": disposition_followups[disposition],
        "repairHint": (
            {
                "command": (
                    "shipguard verify --task <task.json> --diff <change.diff> --evidence "
                    "<validation-receipt.json> --reviewer-disposition accepted --out <verdict-dir>"
                ),
                "acceptedValues": ["accepted", "dismissed", "follow-up", "unknown"],
                "when": "Run after the maintainer decides whether this proof packet was accepted, dismissed, or needs follow-up.",
                "boundary": "This records local reviewer outcome only; it is not adoption, benchmark, or security-review evidence.",
            }
            if not reviewer_disposition
            else None
        ),
        "localOutcomeUse": (
            "Use this with later reviewed verdicts to count accepted blockers, dismissed warnings, "
            "and follow-up fixes before tuning ShipGuard rules."
        ),
        "proofBoundary": (
            "Reviewer disposition is local maintainer feedback. It is not adoption evidence, "
            "external benchmark proof, or a reason to weaken a rule from one verdict."
        ),
    }
    reviewer_disposition_summary = {
        "status": reviewer_disposition_receipt["status"],
        "disposition": disposition,
        "trackedSignalCount": len(recurrence_candidates),
        "nextStep": reviewer_disposition_receipt["recommendedFollowUp"],
        "guard": "Do not tune recurring-signal rules from one local reviewer disposition.",
    }
    recurring_signal_tuning = {
        "schemaVersion": 1,
        "shouldTrackLocally": bool(recurrence_candidates),
        "signalKeys": recurrence_candidates,
        "recurrenceRule": "Treat a signal as recurring only after it appears in two or more reviewed verify verdicts for the same repo or task family.",
        "localMetricCandidates": [
            "signalKey",
            "verdictStatus",
            "changedFileCategory",
            "nextActionCommand",
            "reviewerDisposition",
        ],
        "doNotTuneFromSingleVerdict": True,
        "proofBoundary": (
            "Recurring-signal tuning needs local reviewed outcomes. This packet suggests what to count; "
            "it does not prove a false positive, recurring mistake, or accepted ownership mapping by itself."
        ),
        "reviewerDispositionReceipt": reviewer_disposition_receipt,
    }

    if status == "pass":
        lesson = "This exact diff matched the task scope, attached proof, and completion claim."
    elif status == "blocked":
        lesson = "This exact diff exposed a merge-blocking scope, receipt, or claim boundary."
    elif status == "review":
        lesson = "This exact diff is reviewable only after the missing proof or manual evidence is attached."
    else:
        lesson = "This verdict did not include enough diff evidence to learn from safely."

    return {
        "schemaVersion": 1,
        "status": status,
        "primaryLesson": lesson,
        "changedFileCount": len(changed_files),
        "changedFileSignals": [
            {
                "path": item.get("path"),
                "changeType": item.get("changeType"),
                "categories": item.get("behaviorCategories") or [],
                "authorized": (item.get("scope") or {}).get("authorized"),
                "forbidden": (item.get("scope") or {}).get("forbidden"),
            }
            for item in changed_files[:12]
        ],
        "behaviorCategories": [item.get("category") for item in changed_categories],
        "learningSignals": signals,
        "reviewerDispositionSummary": reviewer_disposition_summary,
        "reviewerDispositionReceipt": reviewer_disposition_receipt,
        "recurringSignalTuning": recurring_signal_tuning,
        "nextTuningAction": {
            "command": next_action.get("command"),
            "expectedArtifact": next_action.get("expectedArtifact"),
            "successCondition": next_action.get("successCondition"),
        },
        "proofBoundary": (
            "This handoff summarizes the current verify verdict only. It is not persistent project memory, "
            "external adoption evidence, or proof that future similar diffs are safe."
        ),
    }


def build_proof_report(
    *,
    status: str,
    goal: str,
    changed: list[str],
    coverage: dict[str, Any],
    claim_results: list[dict[str, Any]],
    evidence_receipt_schema: dict[str, Any],
    forbidden_touched: list[str],
    out_of_scope: list[str],
    deleted_tests: list[dict[str, Any]],
    next_action: dict[str, Any],
) -> dict[str, Any]:
    covered = coverage.get("coveredCommands") or []
    uncovered = coverage.get("uncoveredCommands") or []
    invalid = coverage.get("invalidReceipts") or []
    downgraded = coverage.get("downgradedReceipts") or []
    accepted_claims = [item for item in claim_results if item.get("status") == "accepted"]
    rejected_claims = [item for item in claim_results if item.get("status") == "rejected"]
    manual_claims = [item for item in claim_results if item.get("status") == "needs-manual-proof"]
    risk_file_count = len(set(forbidden_touched + out_of_scope + [str(item.get("path")) for item in deleted_tests]))
    validation_total = len(covered) + len(uncovered)
    validation_label = (
        f"{len(covered)}/{validation_total} covered"
        if validation_total
        else "not required"
    )
    claims_label = (
        f"{len(accepted_claims)}/{len(claim_results)} accepted"
        if claim_results
        else "none supplied"
    )
    risk_label = (
        f"{risk_file_count} risk file(s): {len(forbidden_touched)} protected, {len(out_of_scope)} out of scope, {len(deleted_tests)} deleted test(s)"
    )
    release_evidence = "not-applicable"
    summary = (
        f"ShipGuard Proof Report: {status}. Validation {validation_label}; "
        f"claims {claims_label}; {risk_label}; release evidence {release_evidence}."
    )
    return {
        "title": "ShipGuard Proof Report",
        "status": status,
        "goal": goal,
        "summary": summary,
        "changedFiles": len(changed),
        "validation": {
            "status": coverage.get("status"),
            "requiredCount": validation_total,
            "coveredCount": len(covered),
            "missingCount": len(uncovered),
            "invalidReceiptCount": len(invalid),
            "downgradedReceiptCount": len(downgraded),
            "label": validation_label,
        },
        "claims": {
            "checkedCount": len(claim_results),
            "acceptedCount": len(accepted_claims),
            "rejectedCount": len(rejected_claims),
            "manualProofCount": len(manual_claims),
            "label": claims_label,
        },
        "riskFiles": {
            "count": risk_file_count,
            "protectedCount": len(forbidden_touched),
            "outOfScopeCount": len(out_of_scope),
            "deletedTestCount": len(deleted_tests),
            "label": risk_label,
        },
        "evidenceReceipts": {
            "v2Count": evidence_receipt_schema.get("v2Count", 0),
            "legacyCount": evidence_receipt_schema.get("legacyCount", 0),
            "downgradedCount": evidence_receipt_schema.get("downgradedCount", 0),
            "staleCount": evidence_receipt_schema.get("staleCount", 0),
        },
        "releaseEvidence": release_evidence,
        "mergeAllowed": status == "pass",
        "nextAction": {
            "command": next_action.get("command"),
            "expectedArtifact": next_action.get("expectedArtifact"),
            "successCondition": next_action.get("successCondition"),
        },
        "copyReadyText": summary,
    }


def verify_contract(args: argparse.Namespace) -> dict[str, Any]:
    task_path = resolve_task(args.task)
    task = read_json(task_path)
    allowed = [str(value) for value in task.get("authorizedFiles") or []]
    forbidden = [str(value) for value in task.get("protectedBoundaries") or []]
    diff_path = Path(args.diff) if args.diff else None
    diff_files = parse_diff_files(diff_path)
    changed = [str(item["path"]) for item in diff_files]
    out_of_scope = [path for path in changed if allowed and not match_any(path, allowed)]
    forbidden_touched = [path for path in changed if match_any(path, forbidden)]
    evidence, initial_evidence_receipt_schema = load_receipt_evidence_entries(args.evidence)
    required_validation = (task.get("validationContract") or {}).get("required") or []
    manual_proof = (task.get("validationContract") or {}).get("manualProof") or []
    coverage = validation_coverage(required_validation, evidence, task.get("generatedAt"))
    claim_results = claim_decisions(args.claim, coverage, bool(manual_proof))
    rejected_claims = sorted(
        {
            phrase
            for item in claim_results
            if item["status"] == "rejected"
            for phrase in item.get("requiredProofPhrases", [])
        }
    )
    manual_claims = [item["claim"] for item in claim_results if item["status"] == "needs-manual-proof"]
    deleted_tests = deleted_test_changes(diff_files)
    domain_workflows = evaluate_domain_workflows(task, diff_files, evidence, coverage)
    baseline_findings = contract_findings(
        changed=changed,
        forbidden_touched=forbidden_touched,
        out_of_scope=out_of_scope,
        coverage=coverage,
        deleted_tests=deleted_tests,
        rejected_claims=rejected_claims,
        manual_claims=manual_claims,
        domain_workflows=domain_workflows,
    )
    baseline_result = apply_configuration_baseline(task.get("configurationPolicy"), baseline_findings)
    accepted = accepted_source_keys(baseline_result)
    effective_forbidden_touched = [path for path in forbidden_touched if f"protected:{path}" not in accepted]
    effective_out_of_scope = [path for path in out_of_scope if f"scope:{path}" not in accepted]
    effective_deleted_tests = [
        item for item in deleted_tests if f"deleted-test:{item.get('path')}" not in accepted
    ]
    effective_rejected_claims = [
        phrase for phrase in rejected_claims if f"unsupported-claim:{phrase}" not in accepted
    ]
    effective_manual_claims = [
        claim for claim in manual_claims if f"manual-claim:{claim}" not in accepted
    ]
    effective_coverage = adjusted_validation_coverage(coverage, accepted)
    evidence_receipt_schema = receipt_schema_summary(
        evidence,
        compatibility_warnings=initial_evidence_receipt_schema.get("compatibilityWarnings") or [],
        invalid_receipts=(effective_coverage.get("invalidReceipts") or []) + (effective_coverage.get("downgradedReceipts") or []),
        task_generated_at=task.get("generatedAt"),
    )
    missing_evidence = effective_coverage["missingEvidenceFiles"]
    coverage_ok = effective_coverage["status"] in {"covered", "not-required", "suppressed"}
    effective_domain_workflows = adjusted_domain_workflows(domain_workflows, accepted)
    notification_permission_workflow = effective_domain_workflows.get("notificationPermissionWorkflow")

    blocking_reasons: list[str] = []
    review_reasons: list[str] = []
    if effective_forbidden_touched:
        blocking_reasons.append("forbidden protected boundary touched")
    if effective_out_of_scope:
        blocking_reasons.append("changed files outside authorized scope")
    if effective_coverage["status"] == "invalid":
        blocking_reasons.append("invalid validation receipt")
    if effective_rejected_claims:
        blocking_reasons.append("unsupported completion claim without evidence")
    if not changed:
        if "incomplete-diff:no-changed-files" not in accepted:
            review_reasons.append("no usable diff was provided or no changed files were detected")
    if required_validation and not coverage_ok:
        review_reasons.append("validation coverage missing")
    if missing_evidence:
        review_reasons.append("one or more evidence files were not found")
    if effective_deleted_tests and not coverage_ok:
        review_reasons.append("deleted tests require validation coverage proof")
    if notification_permission_workflow and notification_permission_workflow.get("reviewRequired"):
        review_reasons.append("iOS notification permission workflow proof missing")
    for field, workflow in effective_domain_workflows.items():
        if field == "notificationPermissionWorkflow":
            continue
        if workflow.get("reviewRequired"):
            review_reasons.append(f"{workflow.get('id') or field} proof missing")
    if effective_manual_claims:
        review_reasons.append("broad completion claim still needs manual/device proof")

    if not changed:
        status = "incomplete"
    elif blocking_reasons:
        status = "blocked"
    elif review_reasons:
        status = "review"
    else:
        status = "pass"

    next_action = build_next_action(
        status,
        task,
        args,
        blocking_reasons,
        review_reasons,
        forbidden_touched=effective_forbidden_touched,
        out_of_scope=effective_out_of_scope,
        deleted_tests=effective_deleted_tests,
        coverage=effective_coverage,
        rejected_claims=effective_rejected_claims,
        manual_claims=effective_manual_claims,
        notification_permission_workflow=notification_permission_workflow,
        domain_workflows=effective_domain_workflows,
    )
    diff_first = build_diff_first_analysis(
        status,
        task,
        diff_files,
        allowed,
        forbidden,
        effective_out_of_scope,
        effective_forbidden_touched,
        evidence,
        effective_coverage,
        claim_results,
        next_action,
        blocking_reasons,
        review_reasons,
        evidence_receipt_schema,
        notification_permission_workflow,
        effective_domain_workflows,
    )
    diff_first["configurationBaseline"] = baseline_result
    diff_learning_handoff = build_diff_learning_handoff(
        status=status,
        diff_first=diff_first,
        next_action=next_action,
        reviewer_disposition=args.reviewer_disposition,
        reviewer_note=args.reviewer_note,
    )
    diff_first["learningHandoff"] = diff_learning_handoff
    proof_report = build_proof_report(
        status=status,
        goal=str(task.get("goal") or ""),
        changed=changed,
        coverage=effective_coverage,
        claim_results=claim_results,
        evidence_receipt_schema=evidence_receipt_schema,
        forbidden_touched=effective_forbidden_touched,
        out_of_scope=effective_out_of_scope,
        deleted_tests=effective_deleted_tests,
        next_action=next_action,
    )
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard verify",
        "surface": "ShipGuard Task Contract Verdict",
        "generatedAt": utc_now(),
        "taskId": task.get("taskId"),
        "goal": task.get("goal"),
        "domainPackSDK": DEFAULT_DOMAIN_PACK_REGISTRY.manifest(
            active_pack=(task.get("domainRiskPack") or {}).get("id"),
            evaluated_packs=[str(workflow.get("id") or field) for field, workflow in domain_workflows.items()],
        ),
        "status": status,
        "proofReport": proof_report,
        "changedFiles": changed,
        "scopeChecks": {
            "authorizedFiles": allowed,
            "protectedBoundaries": forbidden,
            "outOfScope": effective_out_of_scope,
            "forbiddenTouched": effective_forbidden_touched,
            "rawOutOfScope": out_of_scope,
            "rawForbiddenTouched": forbidden_touched,
        },
        "evidence": public_evidence_entries(evidence),
        "evidenceReceiptSchema": evidence_receipt_schema,
        "validationCoverage": effective_coverage,
        "agentClaims": args.claim,
        "claimChecks": {
            "rejectedClaims": effective_rejected_claims,
            "rawRejectedClaims": rejected_claims,
            "claimDecisions": claim_results,
            "requiredProofPhrases": list(CLAIM_REQUIRES_PROOF),
        },
        "diffFirstAnalysis": diff_first,
        "diffLearningHandoff": diff_learning_handoff,
        "configurationBaseline": baseline_result,
        "contractFindings": baseline_findings,
        "domainWorkflows": effective_domain_workflows,
        "notificationPermissionWorkflow": notification_permission_workflow,
        "blockingReasons": blocking_reasons,
        "reviewReasons": review_reasons,
        "verdict": {
            "status": status,
            "reason": "; ".join(blocking_reasons or review_reasons or ["scope, evidence, and claims are consistent with the task contract"]),
        },
        "nextAction": next_action,
    }
    report.update(domain_workflows)
    report["quickstartReplay"] = build_verify_quickstart_replay(args, report)
    if effective_rejected_claims or effective_manual_claims:
        report["unsupportedClaimReplay"] = build_unsupported_claim_replay(
            report,
            rejected_phrases=effective_rejected_claims,
            manual_claims=effective_manual_claims,
        )
        report["reportQualityQuestions"] = [
            "Can verify reject unsupported completion claims with an exact next action and replay packet?",
        ]
    return report


def build_next_action(
    status: str,
    task: dict[str, Any],
    args: argparse.Namespace,
    blocking: list[str],
    review: list[str],
    *,
    forbidden_touched: list[str] | None = None,
    out_of_scope: list[str] | None = None,
    deleted_tests: list[dict[str, Any]] | None = None,
    coverage: dict[str, Any] | None = None,
    rejected_claims: list[str] | None = None,
    manual_claims: list[str] | None = None,
    notification_permission_workflow: dict[str, Any] | None = None,
    domain_workflows: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    required = (task.get("validationContract") or {}).get("required") or []
    first_command = str((required[0] or {}).get("command") or "run the targeted validation command") if required else "attach validation evidence"
    forbidden_touched = forbidden_touched or []
    out_of_scope = out_of_scope or []
    deleted_tests = deleted_tests or []
    coverage = coverage or {}
    rejected_claims = rejected_claims or []
    manual_claims = manual_claims or []
    notification_permission_workflow = notification_permission_workflow or {}
    domain_workflows = domain_workflows or {}
    if forbidden_touched or out_of_scope:
        return {
            "owner": "developer",
            "command": "Update the task contract scope or revert out-of-scope/protected changes, then rerun shipguard verify with the corrected diff and evidence.",
            "expectedArtifact": "shipguard-verdict.json",
            "successCondition": "No forbidden or out-of-scope files are reported, and unsupported claims have receipts",
            "failureMeaning": "; ".join(blocking),
            "resolves": ["protected-boundary-crossing", "out-of-scope-diff"],
            "priority": 1,
        }
    if deleted_tests:
        first_deleted = deleted_tests[0]
        return {
            "owner": "developer",
            "command": f"Restore or replace `{first_deleted.get('path')}`, then rerun the targeted validation receipt.",
            "expectedArtifact": "replacement test diff plus structured validation receipt",
            "successCondition": "Deleted test coverage is restored or replaced and validation coverage is proven",
            "failureMeaning": "The change may have reduced regression coverage",
            "resolves": ["deleted-test-coverage"],
            "priority": 2,
        }
    if coverage.get("invalidReceipts"):
        first_invalid = coverage["invalidReceipts"][0]
        return {
            "owner": "developer",
            "command": str(first_invalid.get("command") or first_command),
            "expectedArtifact": "structured validation receipt with status=pass, exitCode=0, matching artifact digest, and completedAt after task creation",
            "successCondition": "The receipt matches the required validation command and is usable for validation coverage",
            "failureMeaning": str(first_invalid.get("reason") or "Validation receipt is invalid"),
            "resolves": [str(first_invalid.get("requirementId") or "invalid-validation-receipt")],
            "priority": 3,
        }
    if coverage.get("uncoveredCommands"):
        first_missing = coverage["uncoveredCommands"][0]
        return {
            "owner": "developer",
            "command": str(first_missing.get("command") or first_command),
            "expectedArtifact": str(first_missing.get("expectedArtifact") or "structured validation receipt"),
            "successCondition": str(first_missing.get("successCondition") or "Required validation command passes and its structured receipt is attached"),
            "failureMeaning": str(first_missing.get("failureMeaning") or "Required automated validation remains unproven"),
            "resolves": [str(first_missing.get("requirementId") or "missing-validation")],
            "priority": 3,
        }
    if notification_permission_workflow.get("reviewRequired"):
        return dict(notification_permission_workflow.get("nextAction") or {})
    for field, workflow in domain_workflows.items():
        if field == "notificationPermissionWorkflow":
            continue
        if workflow.get("reviewRequired"):
            return dict(workflow.get("nextAction") or {})
    if manual_claims:
        return {
            "owner": "developer",
            "command": "Capture the required manual or physical-device proof, then rerun shipguard verify with the receipt reference.",
            "expectedArtifact": "manual or device proof receipt",
            "successCondition": "Manual/device-only risk is explicitly recorded",
            "failureMeaning": "The broad completion claim still exceeds local automated proof",
            "resolves": ["manual-device-proof"],
            "priority": 5,
        }
    if rejected_claims:
        return {
            "owner": "developer",
            "command": "Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify.",
            "expectedArtifact": "updated claim or structured evidence receipt",
            "successCondition": "No unsupported completion claim remains",
            "failureMeaning": "; ".join(blocking),
            "resolves": ["unsupported-completion-claim"],
            "priority": 6,
        }
    if status in {"review", "incomplete"}:
        return {
            "owner": "developer",
            "command": first_command,
            "expectedArtifact": str((required[0] or {}).get("expectedArtifact") or "validation receipt") if required else "validation receipt",
            "successCondition": str((required[0] or {}).get("successCondition") or "Evidence file is attached to shipguard verify") if required else "Evidence file is attached to shipguard verify",
            "failureMeaning": "; ".join(review),
            "resolves": ["incomplete-proof"],
            "priority": 4,
        }
    return {
        "owner": "developer",
        "command": "Attach shipguard-verdict.json and the evidence receipts to the review.",
        "expectedArtifact": "review-ready proof packet",
        "successCondition": "Reviewer can inspect the task contract, diff scope, evidence, and claims from one packet",
        "failureMeaning": "The proof packet is incomplete",
        "resolves": ["review-ready-packet"],
        "priority": 7,
    }


def render_prepare_markdown(contract: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Task Contract",
        "",
        f"- Task: {contract['taskId']}",
        f"- Status: {contract['verdict']['status']}",
        f"- Goal: {contract['goal']}",
        f"- Profile: {contract['projectSnapshot']['profile']}",
        f"- Risk: {contract['riskClassification']['level']}",
        "",
        "## Authorized Scope",
        "",
    ]
    lines.extend(f"- `{item}`" for item in contract.get("authorizedFiles") or [])
    lines.extend(["", "## Protected Boundaries", ""])
    lines.extend(f"- `{item}`" for item in contract.get("protectedBoundaries") or [])
    lines.extend(["", "## Required Proof", ""])
    for item in (contract.get("validationContract") or {}).get("required") or []:
        lines.append(f"- `{item.get('command')}`")
        lines.append(f"  Expected: {item.get('expectedArtifact')}")
        lines.append(f"  Success: {item.get('successCondition')}")
    configuration = contract.get("configurationPolicy") or {}
    if configuration:
        baseline = configuration.get("baseline") or {}
        lines.extend(["", "## Configuration Baseline", ""])
        lines.append(f"- Status: {configuration.get('status')}")
        lines.append(f"- Config path: `{configuration.get('configPath') or 'default'}`")
        lines.append(f"- Baseline path: `{configuration.get('baselinePath')}`")
        lines.append(f"- Suppressions: {baseline.get('suppressionCount', 0)}")
        policy = configuration.get("policy") or {}
        lines.append(
            "- Policy: owner={owner}, reason={reason}, expiresAt={expires}, proofBoundary={boundary}".format(
                owner=policy.get("requireOwner"),
                reason=policy.get("requireReason"),
                expires=policy.get("requireExpiresAt"),
                boundary=policy.get("requireProofBoundary"),
            )
        )
    sdk = contract.get("domainPackSDK") or {}
    if sdk:
        lines.extend(["", "## Domain Pack SDK", ""])
        lines.append(f"- SDK version: {sdk.get('sdkVersion')}")
        lines.append(f"- Active pack: {sdk.get('activePack') or 'none'}")
        registered = sdk.get("registeredPacks") or []
        if registered:
            lines.append("- Registered packs:")
            for item in registered:
                lines.append(f"  - `{item.get('id')}` -> `{item.get('resultField')}`")
    risk_pack = contract.get("domainRiskPack") or {}
    if risk_pack:
        if risk_pack.get("id") == "ios-notification-permission-workflow":
            lines.extend(["", "## iOS Notification Permission Workflow", ""])
        else:
            lines.extend(["", "## Domain Pack Workflow", ""])
            lines.append(f"- Pack: `{risk_pack.get('id')}`")
        lines.append(f"- Status: {risk_pack.get('status')}")
        triggers = ", ".join(risk_pack.get("triggerSignals") or [])
        lines.append(f"- Trigger signals: {triggers}")
        candidates = ((risk_pack.get("candidateEvidence") or {}).get("permissionSensitiveFiles") or [])
        if candidates:
            lines.append("- Permission-sensitive source signals:")
            for item in candidates[:8]:
                signals = "; ".join(item.get("signals") or [])
                lines.append(f"  - `{item.get('path')}`: {signals}")
        scope = risk_pack.get("scopeRecommendations") or {}
        lines.append("- Scope recommendations:")
        for item in scope.get("authorized") or []:
            lines.append(f"  - Authorized candidate `{item.get('pattern')}`: {item.get('reason')}")
        for item in scope.get("reviewOnly") or []:
            lines.append(f"  - Review only `{item.get('pattern')}`: {item.get('reason')}")
        for item in scope.get("forbiddenUnlessExplicit") or []:
            lines.append(f"  - Forbidden unless explicit `{item.get('pattern')}`: {item.get('reason')}")
        lines.append("- Receipt requirements:")
        for item in risk_pack.get("validationReceiptRequirements") or []:
            required_scope = ", ".join(item.get("requiredReceiptScope") or [item.get("proofType") or item.get("environment") or ""])
            lines.append(f"  - {item.get('id')}: {required_scope}")
            lines.append(f"    Expected: {item.get('expectedArtifact')}")
            if item.get("successCondition"):
                lines.append(f"    Success: {item.get('successCondition')}")
            if item.get("failureMeaning"):
                lines.append(f"    Failure meaning: {item.get('failureMeaning')}")
        boundaries = risk_pack.get("proofBoundaries") or {}
        if boundaries:
            lines.append("- Proof boundaries:")
            for key, value in boundaries.items():
                lines.append(f"  - {key}: {value}")
    scan_scope = (contract.get("projectSnapshot") or {}).get("scanScope") or {}
    if scan_scope:
        lines.extend(["", "## Snapshot Scope", ""])
        lines.append(f"- Mode: {scan_scope.get('mode')}")
        lines.append(f"- Source files counted: {contract.get('projectSnapshot', {}).get('sourceFileCount')}")
        lines.append(f"- Swift files counted: {contract.get('projectSnapshot', {}).get('swiftFileCount')}")
        lines.append(f"- Capped: {scan_scope.get('capped')}")
        skipped = scan_scope.get("skippedDirs") or []
        if skipped:
            lines.append("- Skipped generated/cache/proof directories:")
            lines.extend(f"  - `{item}`" for item in skipped[:12])
    lines.extend(["", "## Next Action", ""])
    next_action = contract.get("nextAction") or {}
    lines.append(f"- Owner: {next_action.get('owner')}")
    lines.append(f"- Command: `{next_action.get('command')}`")
    lines.append(f"- Expected artifact: {next_action.get('expectedArtifact')}")
    if contract.get("scopeBoundary"):
        lines.extend(["", "## ShipGuard Product-QA Boundary", ""])
        lines.append("- This is ShipGuard-only evaluation output. Target app findings are evidence about ShipGuard report quality, not app work authorization.")
    replay = contract.get("quickstartReplay") or {}
    if replay:
        lines.extend(["", "## Quickstart Replay", ""])
        lines.append(f"- Phase: `{replay.get('phase')}`")
        lines.append(f"- First useful verdict: `{replay.get('firstUsefulVerdictCommand')}`")
        inputs = ", ".join(f"`{item}`" for item in replay.get("proofInputs") or [])
        lines.append(f"- Proof inputs: {inputs}")
        lines.append(f"- Success signal: {replay.get('successSignal')}")
        lines.append(f"- Boundary: {replay.get('boundary')}")
    return "\n".join(lines) + "\n"


def render_verify_markdown(verdict: dict[str, Any]) -> str:
    def markdown_cell(value: Any) -> str:
        return str(value or "").replace("|", "\\|").replace("\n", " ")

    diff_first = verdict.get("diffFirstAnalysis") or {}
    merge = diff_first.get("mergeVerdict") or {}
    proof_report = verdict.get("proofReport") or {}
    lines = [
        "# ShipGuard Task Verdict",
        "",
        f"- Task: {verdict.get('taskId')}",
        f"- Status: {verdict.get('status')}",
        f"- Goal: {verdict.get('goal')}",
        f"- Merge allowed: {merge.get('allowedToMerge')}",
        f"- Merge reason: {merge.get('reason')}",
        "",
        "## Proof Report",
        "",
        f"- Status: `{proof_report.get('status')}`",
        f"- Validation: `{(proof_report.get('validation') or {}).get('label')}`",
        f"- Claims checked: `{(proof_report.get('claims') or {}).get('label')}`",
        f"- Risk files: `{(proof_report.get('riskFiles') or {}).get('label')}`",
        f"- Release evidence: `{proof_report.get('releaseEvidence')}`",
        f"- Merge allowed: `{proof_report.get('mergeAllowed')}`",
        f"- Next action: `{(proof_report.get('nextAction') or {}).get('command')}`",
        "",
        "## Quickstart Replay",
        "",
        f"- Phase: `{(verdict.get('quickstartReplay') or {}).get('phase')}`",
        f"- Replay command: `{(verdict.get('quickstartReplay') or {}).get('replayCommand')}`",
        f"- Fast verdict: `{(verdict.get('quickstartReplay') or {}).get('fastVerdict')}`",
        f"- Review packet: {', '.join(f'`{item}`' for item in ((verdict.get('quickstartReplay') or {}).get('reviewPacket') or []))}",
        f"- Boundary: {(verdict.get('quickstartReplay') or {}).get('boundary')}",
        "",
        "## Changed Files",
        "",
    ]
    changed_files = (diff_first.get("changedFiles") or [])
    if changed_files:
        for item in changed_files:
            categories = ", ".join(item.get("behaviorCategories") or [])
            lines.append(
                f"- `{item.get('path')}`: {item.get('changeType')}, +{item.get('addedLines')}/-{item.get('removedLines')}, categories: {categories}"
            )
    else:
        lines.append("- No changed files detected.")
    categories = diff_first.get("changedBehaviorCategories") or []
    lines.extend(["", "## Behavior Categories", ""])
    if categories:
        for item in categories:
            files = ", ".join(f"`{path}`" for path in item.get("files") or [])
            lines.append(f"- {item.get('category')}: {item.get('fileCount')} file(s) - {files}")
    else:
        lines.append("- No behavior categories detected.")
    learning = verdict.get("diffLearningHandoff") or {}
    if learning:
        lines.extend(["", "## Diff Learning Handoff", ""])
        lines.append(f"- Status: `{learning.get('status')}`")
        lines.append(f"- Primary lesson: {learning.get('primaryLesson')}")
        signals = ", ".join(f"`{item}`" for item in learning.get("learningSignals") or [])
        lines.append(f"- Learning signals: {signals}")
        summary = learning.get("reviewerDispositionSummary") if isinstance(learning.get("reviewerDispositionSummary"), dict) else {}
        if summary:
            lines.append(
                f"- Reviewer disposition summary: `{summary.get('disposition')}` / `{summary.get('status')}` / "
                f"{summary.get('trackedSignalCount')} tracked signal(s)"
            )
        disposition = learning.get("reviewerDispositionReceipt") if isinstance(learning.get("reviewerDispositionReceipt"), dict) else {}
        if disposition:
            lines.append(f"- Reviewer disposition: `{disposition.get('disposition')}`")
            lines.append(f"- Reviewer follow-up: {disposition.get('recommendedFollowUp')}")
            repair_hint = disposition.get("repairHint") if isinstance(disposition.get("repairHint"), dict) else {}
            if repair_hint:
                lines.append(f"- Reviewer repair hint: `{repair_hint.get('command')}`")
            if disposition.get("note"):
                lines.append(f"- Reviewer note: {disposition.get('note')}")
        recurrence = learning.get("recurringSignalTuning") if isinstance(learning.get("recurringSignalTuning"), dict) else {}
        if recurrence:
            recurring_keys = ", ".join(f"`{item}`" for item in recurrence.get("signalKeys") or [])
            lines.append(f"- Track recurring signals: `{recurrence.get('shouldTrackLocally')}`")
            lines.append(f"- Recurring signal keys: {recurring_keys or '`none`'}")
            lines.append(f"- Recurrence rule: {recurrence.get('recurrenceRule')}")
        next_tuning = learning.get("nextTuningAction") if isinstance(learning.get("nextTuningAction"), dict) else {}
        lines.append(f"- Next tuning action: `{next_tuning.get('command')}`")
        lines.append(f"- Boundary: {learning.get('proofBoundary')}")
    deleted_tests = diff_first.get("deletedTests") or []
    if deleted_tests:
        lines.extend(["", "## Deleted Tests", ""])
        for item in deleted_tests:
            lines.append(f"- `{item.get('path')}` removed {item.get('removedLines')} line(s). {item.get('reason')}")
    scope = verdict.get("scopeChecks") or {}
    if scope.get("forbiddenTouched") or scope.get("outOfScope"):
        lines.extend(["", "## Scope Problems", ""])
        for item in scope.get("forbiddenTouched") or []:
            lines.append(f"- Protected boundary touched: `{item}`")
        for item in scope.get("outOfScope") or []:
            lines.append(f"- Outside authorized scope: `{item}`")
    lines.extend(["", "## Validation Coverage", ""])
    coverage = verdict.get("validationCoverage") or {}
    lines.append(f"- Status: {coverage.get('status')}")
    if coverage.get("baselineAdjusted"):
        lines.append(f"- Original status before baseline: {coverage.get('originalStatus')}")
    for item in coverage.get("coveredCommands") or []:
        receipts = ", ".join(f"`{match.get('path')}`" for match in item.get("matchedEvidence") or [])
        lines.append(f"- Covered: `{item.get('command')}` via {receipts}")
    for item in coverage.get("uncoveredCommands") or []:
        lines.append(f"- Missing: `{item.get('command')}`")
        lines.append(f"  Expected: {item.get('expectedArtifact')}")
        lines.append(f"  Failure meaning: {item.get('failureMeaning')}")
    claim_decisions = (verdict.get("claimChecks") or {}).get("claimDecisions") or []
    if claim_decisions:
        lines.extend(["", "## Claim Decisions", ""])
        for item in claim_decisions:
            lines.append(f"- {item.get('status')}: {item.get('claim')}")
            lines.append(f"  Reason: {item.get('reason')}")
    unsupported_replay = verdict.get("unsupportedClaimReplay") if isinstance(verdict.get("unsupportedClaimReplay"), dict) else {}
    if unsupported_replay:
        lines.extend(["", "## Unsupported Claim Replay", ""])
        lines.append(f"- Status: `{unsupported_replay.get('status')}`")
        phrases = ", ".join(f"`{item}`" for item in unsupported_replay.get("unsupportedPhrases") or [])
        lines.append(f"- Unsupported phrases: {phrases}")
        lines.append(f"- Replay command: `{unsupported_replay.get('replayCommand')}`")
        next_action = unsupported_replay.get("nextAction") if isinstance(unsupported_replay.get("nextAction"), dict) else {}
        lines.append(f"- Next action: `{next_action.get('command')}`")
        lines.append(f"- Expected artifact: {next_action.get('expectedArtifact')}")
        lines.append(f"- Success condition: {next_action.get('successCondition')}")
        lines.append(f"- Boundary: {unsupported_replay.get('proofBoundary')}")
        lines.append(f"- Unsupported claims: {unsupported_replay.get('unsupportedClaimCount', 0)}")
        lines.append(f"- Rejected claims: {unsupported_replay.get('rejectedClaimCount', 0)}")
        lines.append(f"- Manual-proof claims: {unsupported_replay.get('manualProofClaimCount', 0)}")
        unsupported_rows = unsupported_replay.get("unsupportedClaims") if isinstance(unsupported_replay.get("unsupportedClaims"), list) else []
        if not unsupported_rows and isinstance(unsupported_replay.get("rejectedClaims"), list):
            unsupported_rows = unsupported_replay.get("rejectedClaims") or []
        if unsupported_rows:
            lines.append("")
            lines.append("| Status | Claim | Reason | Resolution |")
            lines.append("| --- | --- | --- | --- |")
            for item in unsupported_rows:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"| {markdown_cell(item.get('status'))} | {markdown_cell(item.get('claim'))} | {markdown_cell(item.get('reason'))} | {markdown_cell(item.get('resolution'))} |"
                )
        non_claims = unsupported_replay.get("nonClaims") if isinstance(unsupported_replay.get("nonClaims"), list) else []
        if non_claims:
            lines.extend(["", "### Non-Claims", ""])
            for item in non_claims:
                lines.append(f"- {item}")
    baseline = verdict.get("configurationBaseline") or {}
    if baseline:
        lines.extend(["", "## Configuration Baseline", ""])
        lines.append(f"- Status: {baseline.get('status')}")
        lines.append(f"- Baseline path: `{baseline.get('baselinePath')}`")
        lines.append(f"- Findings: {baseline.get('findingCount', 0)} total")
        lines.append(f"- Accepted findings: {baseline.get('acceptedFindingCount', 0)}")
        lines.append(f"- Unsuppressed findings: {baseline.get('unsuppressedFindingCount', 0)}")
        accepted = baseline.get("acceptedFindings") or []
        if accepted:
            lines.append("- Accepted:")
            for item in accepted[:12]:
                suppression = item.get("suppression") or {}
                lines.append(
                    f"  - `{item.get('ruleId')}` `{item.get('fingerprint')}`: {item.get('subject')} "
                    f"(owner: {suppression.get('owner')}, expires: {suppression.get('expiresAt')})"
                )
                lines.append(f"    Boundary: {suppression.get('proofBoundary')}")
        unsuppressed = baseline.get("unsuppressedFindings") or []
        if unsuppressed:
            lines.append("- Unsuppressed:")
            for item in unsuppressed[:12]:
                lines.append(
                    f"  - `{item.get('ruleId')}` `{item.get('fingerprint')}`: {item.get('subject')} "
                    f"({item.get('baselineStatus')})"
                )
                lines.append(f"    Reason: {item.get('reason')}")
        if baseline.get("expiredSuppressions"):
            lines.append(f"- Expired suppressions: {len(baseline.get('expiredSuppressions') or [])}")
        if baseline.get("invalidSuppressions"):
            lines.append(f"- Invalid suppressions: {len(baseline.get('invalidSuppressions') or [])}")
        if baseline.get("unmatchedSuppressions"):
            lines.append(f"- Unmatched active suppressions: {len(baseline.get('unmatchedSuppressions') or [])}")
    sdk = verdict.get("domainPackSDK") or {}
    if sdk:
        lines.extend(["", "## Domain Pack SDK", ""])
        lines.append(f"- SDK version: {sdk.get('sdkVersion')}")
        lines.append(f"- Active pack: {sdk.get('activePack') or 'none'}")
        evaluated = ", ".join(sdk.get("evaluatedPacks") or [])
        lines.append(f"- Evaluated packs: {evaluated or 'none'}")
    workflow = verdict.get("notificationPermissionWorkflow") or {}
    if workflow:
        lines.extend(["", "## iOS Notification Permission Workflow", ""])
        lines.append(f"- Status: {workflow.get('status')}")
        lines.append(f"- Source: {workflow.get('source')}")
        changed_permission_files = workflow.get("changedPermissionFiles") or []
        if changed_permission_files:
            lines.append("- Permission-sensitive changed files:")
            lines.extend(f"  - `{path}`" for path in changed_permission_files[:12])
        lines.append("- Proof lanes:")
        for item in workflow.get("proofLanes") or []:
            required_scope = ", ".join(item.get("requiredReceiptScope") or [])
            lines.append(f"  - {item.get('id')}: {item.get('status')} ({item.get('proofBoundary')})")
            if required_scope:
                lines.append(f"    Required receipt scope: {required_scope}")
            lines.append(f"    Failure meaning: {item.get('failureMeaning')}")
        boundary = workflow.get("proofBoundary") or {}
        if boundary:
            lines.append("- Proof boundary:")
            for key, value in boundary.items():
                lines.append(f"  - {key}: {value}")
    for field, pack_workflow in (verdict.get("domainWorkflows") or {}).items():
        if field == "notificationPermissionWorkflow" or not isinstance(pack_workflow, dict):
            continue
        lines.extend(["", f"## Domain Pack Workflow: {pack_workflow.get('id') or field}", ""])
        lines.append(f"- Status: {pack_workflow.get('status')}")
        lines.append(f"- Source: {pack_workflow.get('source')}")
        lines.append("- Proof lanes:")
        for item in pack_workflow.get("proofLanes") or []:
            required_scope = ", ".join(item.get("requiredReceiptScope") or [])
            lines.append(f"  - {item.get('id')}: {item.get('status')} ({item.get('proofBoundary')})")
            if required_scope:
                lines.append(f"    Required receipt scope: {required_scope}")
            lines.append(f"    Failure meaning: {item.get('failureMeaning')}")
        boundary = pack_workflow.get("proofBoundary") or {}
        if boundary:
            lines.append("- Proof boundary:")
            for key, value in boundary.items():
                lines.append(f"  - {key}: {value}")
    lines.extend(["", "## Evidence Receipts", ""])
    receipt_schema = verdict.get("evidenceReceiptSchema") or {}
    if receipt_schema:
        lines.append("### Evidence Receipt Schema")
        lines.append(f"- Schema version: {receipt_schema.get('schemaVersion')}")
        lines.append(f"- Mode: {receipt_schema.get('mode')}")
        lines.append(f"- v2 receipts: {receipt_schema.get('v2Count', 0)}")
        lines.append(f"- Legacy-compatible receipts: {receipt_schema.get('legacyCount', 0)}")
        lines.append(f"- Downgraded receipts: {receipt_schema.get('downgradedCount', 0)}")
        lines.append(f"- Stale receipts: {receipt_schema.get('staleCount', 0)}")
        warnings = receipt_schema.get("compatibilityWarnings") or []
        if warnings:
            lines.append("- Compatibility warnings:")
            for warning in warnings[:8]:
                lines.append(f"  - {warning}")
    evidence = verdict.get("evidence") or []
    if evidence:
        for item in evidence:
            status = "present" if item.get("present") else "missing"
            digest = item.get("sha256") or "no-digest"
            lines.append(f"- `{item.get('path')}`: {status}, {item.get('bytes')} bytes, sha256 `{digest}`")
    else:
        lines.append("- No evidence receipts attached.")
    lines.extend(["", "## Next Action", ""])
    next_action = verdict.get("nextAction") or {}
    lines.append(f"- Owner: {next_action.get('owner')}")
    lines.append(f"- Command: `{next_action.get('command')}`")
    lines.append(f"- Expected artifact: {next_action.get('expectedArtifact')}")
    lines.append(f"- Success condition: {next_action.get('successCondition')}")
    lines.append(f"- Failure meaning: {next_action.get('failureMeaning')}")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.command == "prepare":
        report = prepare_contract(args)
        markdown = render_prepare_markdown(report)
        write_json(out_dir / "shipguard-task.json", report)
        (out_dir / "shipguard-task.md").write_text(markdown, encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        if args.markdown:
            print(markdown, end="")
        print(f"wrote: {out_dir / 'shipguard-task.json'}")
        print(f"wrote: {out_dir / 'shipguard-task.md'}")
        print("status: prepared")
        return
    report = verify_contract(args)
    markdown = render_verify_markdown(report)
    write_json(out_dir / "shipguard-verdict.json", report)
    (out_dir / "shipguard-verdict.md").write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(markdown, end="")
    print(f"wrote: {out_dir / 'shipguard-verdict.json'}")
    print(f"wrote: {out_dir / 'shipguard-verdict.md'}")
    proof_report = report.get("proofReport") if isinstance(report.get("proofReport"), dict) else {}
    copy_ready_text = str(proof_report.get("copyReadyText") or "").strip()
    if copy_ready_text:
        print(copy_ready_text)
    print(f"status: {report['status']}")
    if report["status"] == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
