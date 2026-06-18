#!/usr/bin/env python3
"""Persistent ShipGuard task contracts for prepare/verify loops."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


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


def collect_project_snapshot(root: Path, profile: str, detected_signals: list[str], shareable: bool) -> dict[str, Any]:
    files = []
    for pattern in ("AGENTS.md", "README.md", "Package.swift", "package.json", "pyproject.toml", "go.mod", "VERSION"):
        if (root / pattern).is_file():
            files.append(pattern)
    xcode_projects = sorted(path.name for path in root.glob("*.xcodeproj"))
    swift_files = sum(1 for _ in root.glob("**/*.swift"))
    source_files = sum(1 for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)
    return {
        "root": path_display(root, shareable),
        "profile": profile,
        "signals": detected_signals,
        "files": files,
        "xcodeProjects": xcode_projects,
        "swiftFileCount": swift_files,
        "sourceFileCount": min(source_files, 10000),
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


def default_allowed(profile: str) -> list[str]:
    if profile == "ios":
        return ["Sources/**", "Tests/**", "Ringly/**", "RinglyWidgets/**", "*.swift", "docs/**", "README.md"]
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


def default_validation(profile: str, root: Path) -> list[dict[str, Any]]:
    if (root / "bin" / "shipguard").is_file():
        return [
            {
                "command": "./bin/shipguard validate",
                "expectedArtifact": "validation log",
                "successCondition": "ShipGuard bundle validation exits 0",
                "failureMeaning": "Workflow package integrity remains unproven",
            },
            {
                "command": "./tests/cli_smoke_test.sh",
                "expectedArtifact": "CLI smoke log",
                "successCondition": "Public CLI smoke tests exit 0",
                "failureMeaning": "The public command surface may be broken",
            },
        ]
    if profile == "ios":
        return [
            {
                "command": "xcodebuild test -scheme <scheme>",
                "expectedArtifact": "xcresult or test log",
                "successCondition": "Targeted owner tests pass",
                "failureMeaning": "iOS behavior remains unproven",
            }
        ]
    if profile == "web":
        return [
            {
                "command": "npm test",
                "expectedArtifact": "test log",
                "successCondition": "Targeted web tests pass",
                "failureMeaning": "Web behavior remains unproven",
            }
        ]
    return [
        {
            "command": "run the repository's targeted test command",
            "expectedArtifact": "test log",
            "successCondition": "Targeted owner tests pass",
            "failureMeaning": "Behavior remains unproven",
        }
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
    verify.add_argument("--json", action="store_true", help="Print JSON to stdout")
    verify.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def build_validation_contract(commands: list[str], defaults: list[dict[str, Any]]) -> dict[str, Any]:
    if commands:
        required = [
            {
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
    allowed = args.allowed or default_allowed(profile)
    forbidden = args.forbidden or default_forbidden(profile)
    risk = classify_risk(goal, profile)
    risk["approvalPolicy"]["forbiddenInThisTask"] = forbidden
    contract = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard prepare",
        "surface": "ShipGuard Task Contract",
        "taskId": make_task_id(goal, profile, root),
        "generatedAt": utc_now(),
        "goal": goal,
        "projectSnapshot": collect_project_snapshot(root, profile, signals, args.shareable),
        "riskClassification": risk,
        "protectedBoundaries": forbidden,
        "authorizedFiles": allowed,
        "validationContract": build_validation_contract(args.validation, default_validation(profile, root)),
        "agentClaims": args.claim,
        "evidence": [],
        "verdict": {
            "status": "prepared",
            "reason": "Task contract prepared; run Codex under this scope, then run shipguard verify with diff and evidence.",
        },
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
            "Can verify reject unsupported completion claims with an exact next action?",
        ]
    return contract


def match_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.rstrip("/") + "/**") for pattern in patterns)


def parse_diff_paths(diff: Path | None) -> list[str]:
    if diff is None:
        return []
    if not diff.is_file():
        fail(f"diff file not found: {diff}")
    paths: set[str] = set()
    for line in diff.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            for part in parts[2:4]:
                if part.startswith(("a/", "b/")):
                    value = part[2:]
                    if value != "/dev/null":
                        paths.add(value)
        elif line.startswith(("+++ ", "--- ")):
            value = line[4:].strip()
            if value.startswith(("a/", "b/")):
                value = value[2:]
            if value and value != "/dev/null":
                paths.add(value)
    return sorted(paths)


def resolve_task(path: str) -> Path:
    task = Path(path)
    if task.is_dir():
        task = task / "shipguard-task.json"
    return task


def evidence_entries(paths: list[str]) -> list[dict[str, Any]]:
    entries = []
    for value in paths:
        path = Path(value)
        entries.append(
            {
                "path": path.as_posix(),
                "present": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else 0,
            }
        )
    return entries


def unsupported_claims(claims: list[str], evidence_present: bool) -> list[str]:
    if evidence_present:
        return []
    lowered = "\n".join(claims).lower()
    return [phrase for phrase in CLAIM_REQUIRES_PROOF if phrase in lowered]


def verify_contract(args: argparse.Namespace) -> dict[str, Any]:
    task_path = resolve_task(args.task)
    task = read_json(task_path)
    allowed = [str(value) for value in task.get("authorizedFiles") or []]
    forbidden = [str(value) for value in task.get("protectedBoundaries") or []]
    diff_path = Path(args.diff) if args.diff else None
    changed = parse_diff_paths(diff_path)
    out_of_scope = [path for path in changed if allowed and not match_any(path, allowed)]
    forbidden_touched = [path for path in changed if match_any(path, forbidden)]
    evidence = evidence_entries(args.evidence)
    missing_evidence = [item["path"] for item in evidence if not item["present"]]
    evidence_present = bool(evidence) and not missing_evidence
    rejected_claims = unsupported_claims(args.claim, evidence_present)
    validation_required = bool((task.get("validationContract") or {}).get("required"))

    blocking_reasons: list[str] = []
    review_reasons: list[str] = []
    if forbidden_touched:
        blocking_reasons.append("forbidden protected boundary touched")
    if out_of_scope:
        blocking_reasons.append("changed files outside authorized scope")
    if rejected_claims:
        blocking_reasons.append("unsupported completion claim without evidence")
    if not changed:
        review_reasons.append("no diff was provided or no changed files were detected")
    if validation_required and not evidence_present:
        review_reasons.append("validation evidence missing")
    if missing_evidence:
        review_reasons.append("one or more evidence files were not found")

    if blocking_reasons:
        status = "blocked"
    elif review_reasons:
        status = "review"
    else:
        status = "pass"

    next_action = build_next_action(status, task, args, blocking_reasons, review_reasons)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard verify",
        "surface": "ShipGuard Task Contract Verdict",
        "generatedAt": utc_now(),
        "taskId": task.get("taskId"),
        "goal": task.get("goal"),
        "status": status,
        "changedFiles": changed,
        "scopeChecks": {
            "authorizedFiles": allowed,
            "protectedBoundaries": forbidden,
            "outOfScope": out_of_scope,
            "forbiddenTouched": forbidden_touched,
        },
        "evidence": evidence,
        "agentClaims": args.claim,
        "claimChecks": {
            "rejectedClaims": rejected_claims,
            "requiredProofPhrases": list(CLAIM_REQUIRES_PROOF),
        },
        "blockingReasons": blocking_reasons,
        "reviewReasons": review_reasons,
        "verdict": {
            "status": status,
            "reason": "; ".join(blocking_reasons or review_reasons or ["scope, evidence, and claims are consistent with the task contract"]),
        },
        "nextAction": next_action,
    }


def build_next_action(status: str, task: dict[str, Any], args: argparse.Namespace, blocking: list[str], review: list[str]) -> dict[str, str]:
    required = (task.get("validationContract") or {}).get("required") or []
    first_command = str((required[0] or {}).get("command") or "run the targeted validation command") if required else "attach validation evidence"
    if status == "blocked":
        return {
            "owner": "developer",
            "command": "Update the task contract scope or revert out-of-scope/protected changes, then rerun shipguard verify with the corrected diff and evidence.",
            "expectedArtifact": "shipguard-verdict.json",
            "successCondition": "No forbidden or out-of-scope files are reported, and unsupported claims have receipts",
            "failureMeaning": "; ".join(blocking),
        }
    if status == "review":
        return {
            "owner": "developer",
            "command": first_command,
            "expectedArtifact": str((required[0] or {}).get("expectedArtifact") or "validation receipt") if required else "validation receipt",
            "successCondition": str((required[0] or {}).get("successCondition") or "Evidence file is attached to shipguard verify") if required else "Evidence file is attached to shipguard verify",
            "failureMeaning": "; ".join(review),
        }
    return {
        "owner": "developer",
        "command": "Attach shipguard-verdict.json and the evidence receipts to the review.",
        "expectedArtifact": "review-ready proof packet",
        "successCondition": "Reviewer can inspect the task contract, diff scope, evidence, and claims from one packet",
        "failureMeaning": "The proof packet is incomplete",
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
    lines.extend(["", "## Next Action", ""])
    next_action = contract.get("nextAction") or {}
    lines.append(f"- Owner: {next_action.get('owner')}")
    lines.append(f"- Command: `{next_action.get('command')}`")
    lines.append(f"- Expected artifact: {next_action.get('expectedArtifact')}")
    if contract.get("scopeBoundary"):
        lines.extend(["", "## ShipGuard Product-QA Boundary", ""])
        lines.append("- This is ShipGuard-only evaluation output. Target app findings are evidence about ShipGuard report quality, not app work authorization.")
    return "\n".join(lines) + "\n"


def render_verify_markdown(verdict: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Task Verdict",
        "",
        f"- Task: {verdict.get('taskId')}",
        f"- Status: {verdict.get('status')}",
        f"- Goal: {verdict.get('goal')}",
        "",
        "## Changed Files",
        "",
    ]
    changed = verdict.get("changedFiles") or []
    lines.extend(f"- `{item}`" for item in changed) if changed else lines.append("- No changed files detected.")
    scope = verdict.get("scopeChecks") or {}
    if scope.get("forbiddenTouched") or scope.get("outOfScope"):
        lines.extend(["", "## Scope Problems", ""])
        for item in scope.get("forbiddenTouched") or []:
            lines.append(f"- Protected boundary touched: `{item}`")
        for item in scope.get("outOfScope") or []:
            lines.append(f"- Outside authorized scope: `{item}`")
    if verdict.get("claimChecks", {}).get("rejectedClaims"):
        lines.extend(["", "## Rejected Claims", ""])
        for item in verdict["claimChecks"]["rejectedClaims"]:
            lines.append(f"- `{item}` requires proof before it can be accepted.")
    lines.extend(["", "## Evidence", ""])
    evidence = verdict.get("evidence") or []
    if evidence:
        for item in evidence:
            status = "present" if item.get("present") else "missing"
            lines.append(f"- `{item.get('path')}`: {status}")
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
    print(f"status: {report['status']}")
    if report["status"] == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
