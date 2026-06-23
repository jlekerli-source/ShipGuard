#!/usr/bin/env python3
"""ShipGuard full-audit orchestrator."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from shipguard_result import build_result_ux, render_result_markdown


SCHEMA_VERSION = 1
PROFILE_STAGES = {
    "quick": [
        "version",
        "git-diff-check",
        "py-compile",
        "validate",
        "docs-check",
        "value-gauntlet",
        "report-quality",
    ],
    "release": [
        "version",
        "git-diff-check",
        "py-compile",
        "validate",
        "docs-check",
        "cli-smoke",
        "self-audit",
        "value-gauntlet",
        "report-quality",
        "package-release",
        "plugin-status",
        "install-refresh",
        "ci-proof",
        "release-proof",
    ],
    "shipyard": [
        "version",
        "git-diff-check",
        "py-compile",
        "validate",
        "docs-check",
        "cli-smoke",
        "self-audit",
        "value-gauntlet",
        "report-quality",
        "package-release",
        "plugin-status",
        "install-refresh",
        "ci-proof",
        "release-proof",
        "next-goal",
    ],
}
SLOW_DEFAULTS = {"package-release", "value-gauntlet", "report-quality", "release-proof", "ci-proof"}
REQUIRED_RELEASE_PROOF_ARGS = ("release_url", "version", "tag", "commit", "ci_run_url")
RELEASE_PACKET_STAGES = ("package-release", "plugin-status", "install-refresh", "ci-proof", "release-proof")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"full-audit: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or plan one resumable ShipGuard full-audit lane.")
    parser.add_argument("--path", default=".", help="ShipGuard checkout to audit")
    parser.add_argument("--out", required=True, help="Output directory for shipguard-full-audit.json and .md")
    parser.add_argument("--profile", choices=sorted(PROFILE_STAGES), default="quick")
    parser.add_argument("--stage", action="append", help="Run only this stage id. May be passed multiple times.")
    parser.add_argument("--resume", action="store_true", help="Reuse passing stage receipts when command and cwd match")
    parser.add_argument("--plan-only", action="store_true", help="Write the audit plan without executing stages")
    parser.add_argument("--include-install", action="store_true", help="Allow the install/plugin refresh stage to mutate the local install cache")
    parser.add_argument("--release-url", help="Release URL for the optional release-proof stage")
    parser.add_argument("--version", help="Release version for the optional release-proof stage")
    parser.add_argument("--tag", help="Release tag for the optional release-proof stage")
    parser.add_argument("--commit", help="Commit SHA for the optional release-proof stage")
    parser.add_argument("--ci-run-url", help="GitHub Actions run URL for CI proof and release-proof stages")
    parser.add_argument("--slow-threshold-seconds", type=float, default=20.0)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--shipguard-eval", action="store_true")
    parser.add_argument("--shareable", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any executed stage fails")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def clean_stage_id(raw: str) -> str:
    return raw.strip().lower().replace("_", "-")


def shell_join(command: list[str]) -> str:
    return " ".join(subprocess.list2cmdline([part]) if " " in part else part for part in command)


def command_arg_value(args: argparse.Namespace, key: str, placeholder: str, force_placeholder: bool) -> str:
    value = getattr(args, key)
    if value:
        return str(value)
    return placeholder if force_placeholder else ""


def full_audit_command(
    repo: Path,
    out_dir: Path,
    args: argparse.Namespace,
    selected_ids: list[str],
    *,
    resume: bool = False,
    execute_plan: bool = False,
) -> str:
    parts = ["shipguard", "full-audit", "--path", str(repo), "--out", str(out_dir)]
    if args.stage:
        for stage_id in selected_ids:
            parts.extend(["--stage", stage_id])
    else:
        parts.extend(["--profile", args.profile])
    needs_install = "install-refresh" in selected_ids
    needs_ci = "ci-proof" in selected_ids or "release-proof" in selected_ids
    needs_release = "release-proof" in selected_ids
    if args.include_install or (execute_plan and needs_install):
        parts.append("--include-install")
    if resume:
        parts.append("--resume")
    release_args = [
        ("release_url", "--release-url", "<release-url>"),
        ("version", "--version", "<version>"),
        ("tag", "--tag", "<tag>"),
        ("commit", "--commit", "<commit-sha>"),
        ("ci_run_url", "--ci-run-url", "<ci-run-url>"),
    ]
    for key, flag, placeholder in release_args:
        should_force = execute_plan and (needs_release or (key == "ci_run_url" and needs_ci))
        value = command_arg_value(args, key, placeholder, should_force)
        if value:
            parts.extend([flag, value])
    if args.shipguard_eval:
        parts.append("--shipguard-eval")
    if args.shareable:
        parts.append("--shareable")
    if args.strict:
        parts.append("--strict")
    return shell_join(parts)


def redact_value(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        text = value
        for source, target in replacements:
            if source:
                text = text.replace(source, target)
        return text
    if isinstance(value, list):
        return [redact_value(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item, replacements) for key, item in value.items()}
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_fenced_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^##\s+{re.escape(heading)}\s*\n+```text\n(.*?)\n```")
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def markdown_bullet(text: str, label: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(label)}: (.*)$", text)
    return match.group(1).strip() if match else ""


def next_goal_metadata(text: str) -> dict[str, Any]:
    lineage_match = re.search(r"(?ms)^## Version Lineage Check\s*\n+(.*?)(?:\n## |\Z)", text)
    lineage_text = lineage_match.group(1) if lineage_match else ""
    return {
        "generatedAt": markdown_bullet(text, "Generated"),
        "currentToolkitVersion": markdown_bullet(text, "Current toolkit version"),
        "activeTargetRelease": markdown_bullet(text, "Target release"),
        "activeTitle": markdown_bullet(text, "Title"),
        "versionLineageStatus": markdown_bullet(lineage_text, "Status"),
        "versionLineageAction": markdown_bullet(lineage_text, "Action"),
        "completionReceiptPresent": "## Completion Receipt" in text
        and bool(markdown_bullet(text, "Completed scope"))
        and bool(markdown_bullet(text, "Evidence")),
    }


def slash_handoff_from_next_goal(repo: Path) -> tuple[str, str, dict[str, Any]]:
    next_goal_path = repo / "NEXT_GOAL.md"
    fallback_plan = (
        "/plan Refresh ShipGuard next-goal handoff for jlekerli-source/ShipGuard: "
        "run shipguard next-goal with the latest completed scope, evidence, and following title before using Full Audit as release-loop guidance."
    )
    fallback_goal = (
        "/goal Refresh ShipGuard next-goal handoff for jlekerli-source/ShipGuard: "
        "regenerate NEXT_GOAL.md from current ShipGuard proof before continuing the release loop."
    )
    if not next_goal_path.is_file():
        return (
            fallback_plan,
            fallback_goal,
            {
                "status": "fallback",
                "sourcePath": "NEXT_GOAL.md",
                "reason": "NEXT_GOAL.md missing",
                "section": "fallback",
            },
        )
    try:
        text = next_goal_path.read_text(encoding="utf-8")
    except OSError as exc:
        return (
            fallback_plan,
            fallback_goal,
            {
                "status": "fallback",
                "sourcePath": "NEXT_GOAL.md",
                "reason": f"could not read NEXT_GOAL.md: {exc}",
                "section": "fallback",
            },
        )
    section_pairs = [
        ("Following Slash Plan", "Following Slash Goal", "following"),
        ("Slash Plan", "Slash Goal", "active"),
    ]
    metadata = next_goal_metadata(text)
    for plan_heading, goal_heading, section in section_pairs:
        plan = markdown_fenced_section(text, plan_heading)
        goal = markdown_fenced_section(text, goal_heading)
        if plan and goal:
            return (
                plan,
                goal,
                {
                    "status": "loaded",
                    "sourcePath": "NEXT_GOAL.md",
                    "section": section,
                    "planHeading": plan_heading,
                    "goalHeading": goal_heading,
                    **metadata,
                },
            )
    return (
        fallback_plan,
        fallback_goal,
        {
            "status": "fallback",
            "sourcePath": "NEXT_GOAL.md",
            "reason": "missing fenced slash plan or slash goal sections",
            "section": "fallback",
        },
    )


def slash_handoff_proof(source: dict[str, Any], plan: str, goal: str) -> dict[str, Any]:
    copy_ready_plan = plan.strip().startswith("/plan ")
    copy_ready_goal = goal.strip().startswith("/goal ")
    stale_v3132_absent = "v3.132.0 v4 Product Release Stabilization" not in f"{plan}\n{goal}"
    loaded = source.get("status") == "loaded" and source.get("sourcePath") == "NEXT_GOAL.md"
    selected_section = str(source.get("section") or "")
    completion_present = bool(source.get("completionReceiptPresent"))
    freshness = "fresh-following-handoff" if selected_section == "following" and completion_present else "active-handoff"
    if selected_section == "fallback":
        freshness = "fallback-regenerate-required"
    elif selected_section == "following" and not completion_present:
        freshness = "following-without-completion-receipt"
    return {
        "status": "pass" if loaded and copy_ready_plan and copy_ready_goal and stale_v3132_absent else "review",
        "sourcePath": source.get("sourcePath", ""),
        "selectedSection": selected_section,
        "planHeading": source.get("planHeading", ""),
        "goalHeading": source.get("goalHeading", ""),
        "nextGoalGeneratedAt": source.get("generatedAt", ""),
        "activeTargetRelease": source.get("activeTargetRelease", ""),
        "activeTitle": source.get("activeTitle", ""),
        "versionLineageStatus": source.get("versionLineageStatus", ""),
        "versionLineageAction": source.get("versionLineageAction", ""),
        "completionReceiptPresent": completion_present,
        "handoffFreshness": freshness,
        "regenerateCommand": "./bin/shipguard next-goal --out NEXT_GOAL.md",
        "copyReadyPlan": copy_ready_plan,
        "copyReadyGoal": copy_ready_goal,
        "staleHardcodedV3132Absent": stale_v3132_absent,
        "proofBoundary": {
            "nextGoalFileRequired": True,
            "fallbackIsReviewOnly": True,
            "doesNotMarkGoalComplete": True,
            "doesNotPublishRelease": True,
        },
    }


def stage_catalog(repo: Path, out_dir: Path, args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    shipguard = str(repo / "bin" / "shipguard")
    python = os.environ.get("PYTHON", "python3")
    stages: dict[str, dict[str, Any]] = {
        "version": {
            "title": "Version beacon",
            "command": [shipguard, "version"],
            "purpose": "Confirm the CLI resolves and reports the current toolkit version.",
            "proofBoundary": "Local CLI proof only.",
        },
        "git-diff-check": {
            "title": "Diff whitespace gate",
            "command": ["git", "diff", "--check"],
            "purpose": "Catch whitespace and conflict-marker issues before deeper proof.",
            "proofBoundary": "Git working tree formatting proof only.",
        },
        "py-compile": {
            "title": "Python compile gate",
            "command": [
                python,
                "-m",
                "py_compile",
                "scripts/full_audit.py",
                "scripts/tool_value_gauntlet.py",
                "scripts/ios_report_quality.py",
            ],
            "purpose": "Catch syntax errors in the core report/eval scripts used by the audit lane.",
            "proofBoundary": "Syntax proof only; it does not execute report behavior.",
        },
        "validate": {
            "title": "Workflow bundle validation",
            "command": [shipguard, "validate"],
            "purpose": "Validate required ShipGuard files, scripts, docs, fixtures, actions, and package surfaces.",
            "proofBoundary": "Static toolkit bundle proof.",
        },
        "docs-check": {
            "title": "Docs link sweep",
            "command": [shipguard, "docs-check", ".", "--out", str(out_dir / "docs-check")],
            "purpose": "Check local Markdown links and docs integrity.",
            "proofBoundary": "Docs-link proof only.",
        },
        "cli-smoke": {
            "title": "CLI smoke tests",
            "command": ["./tests/cli_smoke_test.sh"],
            "purpose": "Exercise public command routing and starter profile smoke behavior.",
            "proofBoundary": "Local smoke proof.",
        },
        "self-audit": {
            "title": "Self-audit readiness",
            "command": ["./tests/self_audit_test.sh"],
            "purpose": "Verify command and artifact inventory proof.",
            "proofBoundary": "Toolkit self-audit proof.",
        },
        "value-gauntlet": {
            "title": "Tool Value Gauntlet",
            "command": [shipguard, "value-gauntlet", "--path", ".", "--out", str(out_dir / "value-gauntlet")],
            "purpose": "Grade ShipGuard developer-value surfaces and identify the next weak depth signal.",
            "proofBoundary": "ShipGuard product-QA proof, not target-app proof.",
            "slowDefault": True,
        },
        "report-quality": {
            "title": "Report-quality handoff",
            "command": [
                shipguard,
                "ios",
                "report-quality",
                "--reports",
                str(out_dir / "value-gauntlet"),
                "--out",
                str(out_dir / "value-quality"),
                "--shareable",
            ],
            "purpose": "Turn the gauntlet output into concise actionability and fixture-quality proof.",
            "proofBoundary": "Report-quality proof over ShipGuard reports.",
            "dependsOn": ["value-gauntlet"],
            "slowDefault": True,
        },
        "package-release": {
            "title": "Package release proof",
            "command": ["./tests/package_release_test.sh"],
            "purpose": "Build and inspect the distributable package, then run package-local proof checks.",
            "proofBoundary": "Local package proof, not GitHub release publication.",
            "slowDefault": True,
        },
        "plugin-status": {
            "title": "Codex plugin status",
            "command": [shipguard, "codex", "status", "--strict"],
            "purpose": "Confirm the installed local Codex plugin resolves to the current ShipGuard CLI.",
            "proofBoundary": "Local Codex plugin cache proof.",
        },
        "install-refresh": {
            "title": "Install and plugin refresh",
            "command": [
                "bash",
                "-lc",
                'PREFIX="$HOME/.local" ./scripts/install.sh && codex plugin marketplace add . && codex plugin add ios-shipguard@shipguard && ./bin/shipguard codex status --strict',
            ],
            "purpose": "Refresh the local CLI and Codex plugin cache after source changes.",
            "proofBoundary": "Mutates the local user install/cache only; it does not affect GitHub or target apps.",
            "manualUnless": "include-install",
        },
        "ci-proof": {
            "title": "GitHub Actions proof",
            "command": ci_command(args.ci_run_url),
            "purpose": "Verify the pushed validation run completed successfully.",
            "proofBoundary": "GitHub Actions proof for one run URL.",
            "manualUnless": "ci-run-url",
            "slowDefault": True,
        },
        "release-proof": {
            "title": "Release proof bundle",
            "command": release_proof_command(shipguard, out_dir, args),
            "purpose": "Build release proof, manifest, replay, attestation, and tarball assets.",
            "proofBoundary": "Builds local release assets; it does not create the GitHub release.",
            "manualUnless": "release-proof-args",
            "slowDefault": True,
        },
        "next-goal": {
            "title": "Next goal handoff",
            "command": [shipguard, "next-goal", "--out", str(out_dir / "NEXT_GOAL.md")],
            "purpose": "Generate the following slash plan and slash goal after proof.",
            "proofBoundary": "Planning handoff proof.",
        },
    }
    return stages


def ci_command(ci_run_url: str | None) -> list[str]:
    if not ci_run_url:
        return []
    match = re.search(r"/actions/runs/(\d+)", ci_run_url)
    if not match:
        return []
    return ["gh", "run", "view", match.group(1), "--json", "status,conclusion,headSha,url"]


def release_proof_command(shipguard: str, out_dir: Path, args: argparse.Namespace) -> list[str]:
    if not all(getattr(args, key) for key in REQUIRED_RELEASE_PROOF_ARGS):
        return []
    return [
        shipguard,
        "release-proof",
        "build",
        "--out",
        str(out_dir / "release-proof"),
        "--release-url",
        args.release_url,
        "--version",
        args.version,
        "--tag",
        args.tag,
        "--commit",
        args.commit,
        "--ci-run-url",
        args.ci_run_url,
        "--notes",
        "Generated by shipguard full-audit.",
    ]


def selected_stage_ids(args: argparse.Namespace) -> list[str]:
    if args.stage:
        return [clean_stage_id(item) for item in args.stage]
    return PROFILE_STAGES[args.profile]


def manual_reason(stage: dict[str, Any], args: argparse.Namespace) -> str | None:
    gate = stage.get("manualUnless")
    if gate == "include-install" and not args.include_install:
        return "install/plugin cache mutation requires --include-install"
    if gate == "ci-run-url" and not args.ci_run_url:
        return "CI proof requires --ci-run-url"
    if gate == "release-proof-args" and not all(getattr(args, key) for key in REQUIRED_RELEASE_PROOF_ARGS):
        return "release proof requires --release-url, --version, --tag, --commit, and --ci-run-url"
    if gate and not stage.get("command"):
        return f"{gate} not satisfied"
    return None


def receipt_path(out_dir: Path, stage_id: str) -> Path:
    return out_dir / "stage-receipts" / f"{stage_id}.json"


def can_reuse_receipt(path: Path, command: list[str], cwd: Path) -> tuple[bool, dict[str, Any]]:
    receipt = load_json(path)
    if not receipt:
        return False, {}
    if receipt.get("status") != "pass":
        return False, receipt
    if receipt.get("command") != command:
        return False, receipt
    if receipt.get("cwd") != str(cwd):
        return False, receipt
    return True, receipt


def run_stage(stage_id: str, stage: dict[str, Any], repo: Path, out_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    command = stage.get("command") or []
    receipt_file = receipt_path(out_dir, stage_id)
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard full-audit",
        "stageId": stage_id,
        "title": stage["title"],
        "purpose": stage["purpose"],
        "command": command,
        "cwd": str(repo),
        "proofBoundary": stage["proofBoundary"],
        "dependsOn": stage.get("dependsOn", []),
        "slowDefault": bool(stage.get("slowDefault") or stage_id in SLOW_DEFAULTS),
    }
    if args.plan_only:
        receipt = {**base, "status": "planned", "exitCode": None, "durationSeconds": 0.0, "skippedReason": "plan-only"}
        write_json(receipt_file, receipt)
        return receipt
    reason = manual_reason(stage, args)
    if reason:
        receipt = {**base, "status": "manual-required", "exitCode": None, "durationSeconds": 0.0, "skippedReason": reason}
        write_json(receipt_file, receipt)
        return receipt
    if args.resume:
        reusable, previous = can_reuse_receipt(receipt_file, command, repo)
        if reusable:
            receipt = {**previous, "status": "skipped", "skippedReason": "resume reused prior passing receipt"}
            write_json(receipt_file, receipt)
            return receipt
    started = utc_now()
    start_time = time.monotonic()
    stdout_path = out_dir / "logs" / f"{stage_id}.stdout.txt"
    stderr_path = out_dir / "logs" / f"{stage_id}.stderr.txt"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(command, cwd=repo, text=True, capture_output=True, timeout=args.timeout_seconds, check=False)
        exit_code = completed.returncode
        stdout_path.write_text(completed.stdout or "", encoding="utf-8")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8")
        status = "pass" if exit_code == 0 else "fail"
        error = "" if exit_code == 0 else (completed.stderr or completed.stdout or "").strip()[:1000]
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        status = "fail"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8")
        error = f"timed out after {args.timeout_seconds}s"
    duration = round(time.monotonic() - start_time, 3)
    receipt = {
        **base,
        "status": status,
        "exitCode": exit_code,
        "startedAt": started,
        "completedAt": utc_now(),
        "durationSeconds": duration,
        "stdoutPath": str(stdout_path),
        "stderrPath": str(stderr_path),
        "errorSummary": error,
    }
    write_json(receipt_file, receipt)
    return receipt


def summarize_status(stages: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for stage in stages:
        counts[stage["status"]] = counts.get(stage["status"], 0) + 1
    return counts


def release_packet_plan(args: argparse.Namespace, ids: list[str], stages: list[dict[str, Any]], execute_command: str) -> dict[str, Any]:
    selected = [stage_id for stage_id in RELEASE_PACKET_STAGES if stage_id in ids]
    if not selected:
        return {}
    metadata = [
        {"field": "release_url", "flag": "--release-url", "provided": bool(args.release_url), "placeholder": "<release-url>"},
        {"field": "version", "flag": "--version", "provided": bool(args.version), "placeholder": "<version>"},
        {"field": "tag", "flag": "--tag", "provided": bool(args.tag), "placeholder": "<tag>"},
        {"field": "commit", "flag": "--commit", "provided": bool(args.commit), "placeholder": "<commit-sha>"},
        {"field": "ci_run_url", "flag": "--ci-run-url", "provided": bool(args.ci_run_url), "placeholder": "<ci-run-url>"},
    ]
    missing = [item["field"] for item in metadata if not item["provided"]]
    stage_rows = [
        {
            "stageId": stage["stageId"],
            "status": stage["status"],
            "skippedReason": stage.get("skippedReason", ""),
            "proofBoundary": stage.get("proofBoundary", ""),
        }
        for stage in stages
        if stage.get("stageId") in selected
    ]
    return {
        "status": "review" if args.plan_only or missing or any(row["status"] != "pass" for row in stage_rows) else "pass",
        "selectedStages": selected,
        "proofOrder": selected,
        "requiredMetadata": metadata,
        "missingMetadataFields": missing,
        "stagePlan": stage_rows,
        "nextCommand": execute_command,
        "stableV4EvidenceRealityCheck": {
            "publicAssetConsumerProof": {
                "currentSource": "planned" if "release-proof" in selected else "not-selected",
                "countsAsStableV4Proof": False,
                "nextEvidence": "Publish real GitHub release assets, download them from the public release, then consume and verify those assets.",
            },
            "externalAdoptionEvidence": {
                "currentSource": "not-provided",
                "countsAsStableV4Proof": False,
                "nextEvidence": "Attach independent external adoption evidence; maintainer-only runs do not count as independent adoption.",
            },
            "finalSecurityReviewEvidence": {
                "currentSource": "not-provided",
                "countsAsStableV4Proof": False,
                "nextEvidence": "Attach redacted security-review evidence scoped to ShipGuard; label maintainer reviews as maintainer security review, not third-party certification.",
            },
        },
        "proofBoundary": {
            "planOnlyCountsAsReleaseProof": False,
            "sourceOnlyCountsAsStableV4Proof": False,
            "publishesGitHubRelease": False,
            "pushesMain": False,
            "installRefreshRequiresIncludeInstall": True,
            "releaseProofRequiresMetadata": "release-proof" in selected,
        },
        "nonClaims": [
            "Full Audit release-packet planning does not publish a GitHub release.",
            "Plan-only output proves route shape only, not completed release proof.",
            "Source-only proof does not count as stable-v4 publication proof.",
            "Maintainer-only runs do not count as independent external adoption evidence.",
        ],
    }


def execution_command_receipt(
    stages: list[dict[str, Any]], *, execute_command: str, resume_command: str
) -> dict[str, Any]:
    stage_rows = []
    empty_stage_ids = []
    manual_stage_ids = []
    for stage in stages:
        command = stage.get("command") if isinstance(stage.get("command"), list) else []
        command_text = shell_join([str(part) for part in command]) if command else ""
        copy_ready = bool(command_text)
        if not copy_ready:
            empty_stage_ids.append(str(stage.get("stageId") or "unknown"))
        if stage.get("status") == "manual-required":
            manual_stage_ids.append(str(stage.get("stageId") or "unknown"))
        stage_rows.append(
            {
                "stageId": stage.get("stageId", ""),
                "status": stage.get("status", ""),
                "command": command,
                "commandText": command_text,
                "copyReady": copy_ready,
                "fallbackCommand": "" if copy_ready else execute_command,
                "emptyReason": "" if copy_ready else stage.get("skippedReason") or "command requires external metadata or a manual gate",
                "proofBoundary": stage.get("proofBoundary", ""),
            }
        )
    return {
        "status": "review" if empty_stage_ids else "pass",
        "executeCommand": execute_command,
        "resumeCommand": resume_command,
        "stageCount": len(stages),
        "copyReadyStageCount": len(stages) - len(empty_stage_ids),
        "fallbackStageCount": len(empty_stage_ids),
        "manualStageCount": len(manual_stage_ids),
        "emptyStageCommandIds": empty_stage_ids,
        "manualStageCommandIds": manual_stage_ids,
        "stageCommands": stage_rows,
        "proofBoundary": {
            "doesNotExecuteByRendering": True,
            "commandsAreLocalRepoScoped": True,
            "doesNotPush": True,
            "doesNotPublishRelease": True,
            "installRefreshRequiresIncludeInstall": True,
        },
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.path).expanduser().resolve()
    if not repo.exists():
        fail(f"path not found: {repo}")
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    catalog = stage_catalog(repo, out_dir, args)
    ids = selected_stage_ids(args)
    unknown = [item for item in ids if item not in catalog]
    if unknown:
        fail(f"unknown stage id(s): {', '.join(unknown)}")
    stage_reports = [run_stage(stage_id, catalog[stage_id], repo, out_dir, args) for stage_id in ids]
    counts = summarize_status(stage_reports)
    failures = [item for item in stage_reports if item["status"] == "fail"]
    manual = [item for item in stage_reports if item["status"] == "manual-required"]
    planned = [item for item in stage_reports if item["status"] == "planned"]
    slow_lanes = [
        {
            "stageId": item["stageId"],
            "title": item["title"],
            "durationSeconds": item.get("durationSeconds", 0.0),
            "status": item["status"],
            "reason": "duration-threshold" if item.get("durationSeconds", 0) >= args.slow_threshold_seconds else "known-slow-stage",
        }
        for item in stage_reports
        if item.get("slowDefault") or item.get("durationSeconds", 0) >= args.slow_threshold_seconds
    ]
    execute_command = full_audit_command(repo, out_dir, args, ids, execute_plan=True)
    resume_command = full_audit_command(repo, out_dir, args, ids, resume=True)
    if failures:
        status = "fail"
        next_action = f"Fix `{failures[0]['stageId']}` then rerun with --resume."
        next_command = resume_command
    elif planned:
        status = "review"
        next_action = "Plan-only report created; run the planned stages before treating this as release proof."
        next_command = execute_command
    elif manual and not args.plan_only:
        status = "review"
        next_action = f"Run or satisfy manual stage `{manual[0]['stageId']}` when that external proof is required."
        next_command = execute_command
    else:
        status = "pass"
        next_action = "Use this single report as the release-loop receipt; rerun with --resume after making changes."
        next_command = resume_command
    verdict_one_line = f"{counts.get('pass', 0)} passed, {counts.get('planned', 0)} planned, {counts.get('manual-required', 0)} manual, {counts.get('fail', 0)} failed."
    result_ux = build_result_ux(
        status=status,
        summary=verdict_one_line,
        proof_source="stageStatusSummary + stage receipts",
        why_it_matters="Full Audit collapses validation, release proof, slow lanes, and resumability into one maintainer receipt.",
        next_command=next_command,
        next_action_summary=next_action,
    )
    slash_plan, slash_goal, slash_handoff_source = slash_handoff_from_next_goal(repo)
    slash_proof = slash_handoff_proof(slash_handoff_source, slash_plan, slash_goal)
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard full-audit",
        "status": status,
        "resultUX": result_ux,
        "generatedAt": utc_now(),
        "profile": args.profile,
        "planOnly": bool(args.plan_only),
        "resume": bool(args.resume),
        "stages": stage_reports,
        "stageStatusSummary": counts,
        "slowLaneSummary": slow_lanes,
        "efficiency": {
            "stagesPlanned": len(stage_reports),
            "executedStages": sum(1 for item in stage_reports if item["status"] in {"pass", "fail"}),
            "manualStages": len(manual),
            "plannedStages": len(planned),
            "collapsedCommandFamilies": sorted({item["stageId"] for item in stage_reports}),
            "resumeCommand": resume_command,
            "executeCommand": execute_command,
        },
        "scopeBoundary": {
            "shipguardOnly": bool(args.shipguard_eval),
            "targetAppsReadOnly": True,
            "doesNotPush": True,
            "doesNotPublishRelease": True,
            "installRefreshMutatesLocalCacheOnly": bool(args.include_install),
            "releaseProofBuildsLocalAssetsOnly": all(getattr(args, key) for key in REQUIRED_RELEASE_PROOF_ARGS),
        },
        "verdict": {
            "status": status,
            "oneLine": verdict_one_line,
            "nextAction": next_action,
        },
        "reportQualityQuestions": [
            "Does the full-audit report replace repeated manual validation ceremony with one resumable evidence lane?",
            "Are slow lanes summarized clearly enough for a solo developer to decide what to rerun?",
            "Does the command preserve proof boundaries instead of pushing, publishing, or editing target apps?",
            "Does the slash handoff come from the current NEXT_GOAL.md instead of stale hardcoded roadmap text?",
        ],
        "slashHandoffSource": slash_handoff_source,
        "slashHandoffProof": slash_proof,
        "executionCommandReceipt": execution_command_receipt(
            stage_reports,
            execute_command=execute_command,
            resume_command=resume_command,
        ),
        "slashPlan": slash_plan,
        "slashGoal": slash_goal,
    }
    packet_plan = release_packet_plan(args, ids, stage_reports, execute_command)
    if packet_plan:
        report["releasePacketPlan"] = packet_plan
    if args.shareable:
        replacements = [(str(repo), "<shipguard-repo>"), (str(out_dir), "<shipguard-full-audit-out>"), (str(Path.home()), "<home>")]
        report = redact_value(report, replacements)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Full Audit",
        "",
        f"- Status: {report['status']}",
        f"- Profile: {report['profile']}",
        f"- Plan only: {str(report['planOnly']).lower()}",
        f"- Verdict: {report['verdict']['oneLine']}",
        f"- Next action: {report['verdict']['nextAction']}",
        "",
    ]
    lines.extend(render_result_markdown(report["resultUX"]))
    lines.extend(
        [
            "## Efficiency",
            "",
        ]
    )
    lines.extend(
        [
        f"- Stages planned: {report['efficiency']['stagesPlanned']}",
        f"- Executed stages: {report['efficiency']['executedStages']}",
        f"- Manual stages: {report['efficiency']['manualStages']}",
        f"- Resume command: `{report['efficiency']['resumeCommand']}`",
        "",
        "## Stages",
        "",
        "| Status | Stage | Duration | Purpose |",
        "| --- | --- | ---: | --- |",
        ]
    )
    for stage in report["stages"]:
        lines.append(
            f"| {stage['status']} | `{stage['stageId']}` {stage['title']} | {stage.get('durationSeconds', 0.0)}s | {stage['purpose']} |"
        )
    lines.extend(["", "## Execution Commands", ""])
    if report["stages"]:
        lines.extend(["| Stage | Status | Command |", "| --- | --- | --- |"])
        for stage in report["stages"]:
            command = stage.get("command") or []
            command_text = shell_join([str(part) for part in command]) if isinstance(command, list) else str(command)
            lines.append(f"| `{stage['stageId']}` | {stage['status']} | `{command_text}` |")
    else:
        lines.append("No stages were selected.")
    receipt = report.get("executionCommandReceipt") if isinstance(report.get("executionCommandReceipt"), dict) else {}
    if receipt:
        lines.extend(["", "## Execution Command Receipt", ""])
        lines.append(f"- Status: `{receipt.get('status', 'unknown')}`")
        lines.append(f"- Execute command: `{receipt.get('executeCommand', '')}`")
        lines.append(f"- Resume command: `{receipt.get('resumeCommand', '')}`")
        lines.append(f"- Copy-ready stage commands: {receipt.get('copyReadyStageCount', 0)}/{receipt.get('stageCount', 0)}")
        lines.append(f"- Fallback stage commands: {receipt.get('fallbackStageCount', 0)}")
        lines.append(f"- Manual-required stage commands: {receipt.get('manualStageCount', 0)}")
        empty_ids = receipt.get("emptyStageCommandIds") or []
        lines.append(f"- Empty/manual stage commands: `{', '.join(empty_ids) or 'none'}`")
        lines.extend(["", "| Stage | Copy ready | Fallback | Reason | Boundary |", "| --- | --- | --- | --- | --- |"])
        for row in receipt.get("stageCommands", []):
            fallback = row.get("fallbackCommand") or "not-needed"
            reason = row.get("emptyReason") or "not-needed"
            lines.append(
                f"| `{row.get('stageId')}` | {str(bool(row.get('copyReady'))).lower()} | `{fallback}` | {reason} | {row.get('proofBoundary', '')} |"
            )
    lines.extend(["", "## Slow Lanes", ""])
    if report["slowLaneSummary"]:
        lines.extend(["| Stage | Status | Duration | Reason |", "| --- | --- | ---: | --- |"])
        for lane in report["slowLaneSummary"]:
            lines.append(f"| `{lane['stageId']}` | {lane['status']} | {lane['durationSeconds']}s | {lane['reason']} |")
    else:
        lines.append("No slow lanes were detected.")
    packet_plan = report.get("releasePacketPlan") if isinstance(report.get("releasePacketPlan"), dict) else {}
    if packet_plan:
        lines.extend(["", "## Release Packet Plan", ""])
        lines.append(f"- Status: `{packet_plan.get('status')}`")
        lines.append(f"- Next command: `{packet_plan.get('nextCommand')}`")
        lines.append(f"- Missing metadata: `{', '.join(packet_plan.get('missingMetadataFields') or []) or 'none'}`")
        lines.extend(["", "| Stage | Status | Boundary |", "| --- | --- | --- |"])
        for row in packet_plan.get("stagePlan", []):
            lines.append(f"| `{row.get('stageId')}` | {row.get('status')} | {row.get('proofBoundary')} |")
        reality = packet_plan.get("stableV4EvidenceRealityCheck") or {}
        if reality:
            lines.extend(["", "Stable v4 evidence reality check:", ""])
            lines.extend(["| Evidence | Current source | Counts as stable-v4 proof | Next evidence |", "| --- | --- | --- | --- |"])
            for key, row in reality.items():
                lines.append(
                    f"| `{key}` | {row.get('currentSource')} | {str(bool(row.get('countsAsStableV4Proof'))).lower()} | {row.get('nextEvidence')} |"
                )
        lines.extend(["", "Non-claims:"])
        for item in packet_plan.get("nonClaims", []):
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Proof Boundary",
            "",
            f"- ShipGuard only: {str(report['scopeBoundary']['shipguardOnly']).lower()}",
            f"- Target apps read-only: {str(report['scopeBoundary']['targetAppsReadOnly']).lower()}",
            f"- Does not push: {str(report['scopeBoundary']['doesNotPush']).lower()}",
            f"- Does not publish release: {str(report['scopeBoundary']['doesNotPublishRelease']).lower()}",
            "",
            "## Report Quality Questions",
            "",
        ]
    )
    for question in report.get("reportQualityQuestions", []):
        lines.append(f"- {question}")
    source = report.get("slashHandoffSource") or {}
    lines.extend(
        [
            "",
            "## Slash Handoff Source",
            "",
            f"- Status: `{source.get('status', 'unknown')}`",
            f"- Source path: `{source.get('sourcePath', 'unknown')}`",
            f"- Section: `{source.get('section', 'unknown')}`",
        ]
    )
    if source.get("reason"):
        lines.append(f"- Reason: {source['reason']}")
    proof = report.get("slashHandoffProof") if isinstance(report.get("slashHandoffProof"), dict) else {}
    if proof:
        lines.extend(
            [
                "",
                "## Slash Handoff Proof",
                "",
                f"- Status: `{proof.get('status', 'unknown')}`",
                f"- Selected section: `{proof.get('selectedSection', 'unknown')}`",
                f"- NEXT_GOAL generated: `{proof.get('nextGoalGeneratedAt') or 'unknown'}`",
                f"- Active target: `{proof.get('activeTargetRelease') or 'unknown'}`",
                f"- Active title: `{proof.get('activeTitle') or 'unknown'}`",
                f"- Version lineage: `{proof.get('versionLineageStatus') or 'unknown'}`",
                f"- Completion receipt present: {str(bool(proof.get('completionReceiptPresent'))).lower()}",
                f"- Handoff freshness: `{proof.get('handoffFreshness') or 'unknown'}`",
                f"- Regenerate command: `{proof.get('regenerateCommand') or './bin/shipguard next-goal --out NEXT_GOAL.md'}`",
                f"- Copy-ready plan/goal: {str(bool(proof.get('copyReadyPlan'))).lower()}/{str(bool(proof.get('copyReadyGoal'))).lower()}",
                f"- Stale v3.132 handoff absent: {str(bool(proof.get('staleHardcodedV3132Absent'))).lower()}",
            ]
        )
    lines.extend(["", "## Slash Plan", "", "```text", report["slashPlan"], "```", "", "## Slash Goal", "", "```text", report["slashGoal"], "```", ""])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args)
    out_dir = Path(args.out).expanduser().resolve()
    json_path = out_dir / "shipguard-full-audit.json"
    md_path = out_dir / "shipguard-full-audit.md"
    write_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(render_markdown(report))
    if not args.json and not args.markdown:
        print(f"wrote: {json_path}")
        print(f"wrote: {md_path}")
        print(f"status: {report['status']}")
    if args.strict and report["status"] == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
