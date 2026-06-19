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
    if failures:
        status = "fail"
        next_action = f"Fix `{failures[0]['stageId']}` then rerun with --resume."
    elif manual and not args.plan_only:
        status = "review"
        next_action = f"Run or satisfy manual stage `{manual[0]['stageId']}` when that external proof is required."
    else:
        status = "pass"
        next_action = "Use this single report as the release-loop receipt; rerun with --resume after making changes."
    verdict_one_line = f"{counts.get('pass', 0)} passed, {counts.get('planned', 0)} planned, {counts.get('manual-required', 0)} manual, {counts.get('fail', 0)} failed."
    resume_command = f"shipguard full-audit --path {repo} --out {out_dir} --profile {args.profile} --resume"
    result_ux = build_result_ux(
        status=status,
        summary=verdict_one_line,
        proof_source="stageStatusSummary + stage receipts",
        why_it_matters="Full Audit collapses validation, release proof, slow lanes, and resumability into one maintainer receipt.",
        next_command=resume_command,
        next_action_summary=next_action,
    )
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
            "Should the next ShipGuard slice prove Codex marketplace readiness with public install, metadata, status, screenshot/asset, and submission-packet receipts?",
        ],
        "slashPlan": "/plan v3.127.0 Codex Marketplace Readiness for jlekerli-source/ShipGuard: prove public plugin metadata, install proof, README/profile presentation, screenshots/assets, status checks, and submission packet quality with executable receipts.",
        "slashGoal": "/goal Implement v3.127.0 Codex Marketplace Readiness for jlekerli-source/ShipGuard: make the Codex marketplace source adopter-ready with proof, without hiding install or status evidence.",
    }
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
    lines.extend(["", "## Slow Lanes", ""])
    if report["slowLaneSummary"]:
        lines.extend(["| Stage | Status | Duration | Reason |", "| --- | --- | ---: | --- |"])
        for lane in report["slowLaneSummary"]:
            lines.append(f"| `{lane['stageId']}` | {lane['status']} | {lane['durationSeconds']}s | {lane['reason']} |")
    else:
        lines.append("No slow lanes were detected.")
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
