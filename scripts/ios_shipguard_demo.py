#!/usr/bin/env python3
"""Build a clean first-run iOS Shipguard demo bundle from the public fixture."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures" / "demo-ios-repo"
DEFAULT_CASES = ROOT / "evals" / "ios_shipguard_cases.jsonl"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-shipguard-demo: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a static first-run Shipguard demo bundle from the public iOS fixture."
    )
    parser.add_argument("--out", required=True, help="Output directory for the demo bundle")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE), help="Fixture iOS repo to inspect")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="Shipguard eval case file")
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown summary to stdout")
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def run_step(step_id: str, title: str, command: list[str], out_dir: Path) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    log_dir = out_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_file = log_dir / f"{step_id}.stdout.txt"
    stderr_file = log_dir / f"{step_id}.stderr.txt"
    stdout_file.write_text(result.stdout, encoding="utf-8")
    stderr_file.write_text(result.stderr, encoding="utf-8")
    status = "pass" if result.returncode == 0 else "fail"
    return {
        "id": step_id,
        "title": title,
        "status": status,
        "returnCode": result.returncode,
        "command": command,
        "stdout": rel(stdout_file),
        "stderr": rel(stderr_file),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# iOS Shipguard First-Run Demo",
        "",
        f"- Status: {report['status']}",
        f"- Fixture: `{report['fixture']}`",
        f"- Generated: {report['generatedAt']}",
        "",
        "## What This Proves",
        "",
        "- A clean checkout can run the static Shipguard loop without Xcode, a booted Simulator, credentials, or an API key.",
        "- The demo fixture produces topology, permission/runtime inventory, modernization, guided plan, proof route, App Intelligence, AI readiness, deterministic eval, and redaction artifacts.",
        "- Live preview, Devspace, TestFlight, App Store Connect, and physical-device proof remain separate manual or local-tool lanes.",
        "",
        "## Steps",
        "",
        "| Step | Status | Command |",
        "| --- | --- | --- |",
    ]
    for step in report["steps"]:
        command = " ".join(step["command"])
        lines.append(f"| {step['title']} | {step['status']} | `{command}` |")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
        ]
    )
    for label, path in report["artifacts"].items():
        lines.append(f"- {label}: `{path}`")

    lines.extend(
        [
            "",
            "## Try The Plugin",
            "",
            "Install the local marketplace-backed plugin from this checkout, then start a new Codex thread:",
            "",
            "```bash",
            "codex plugin marketplace add .agents/plugins",
            "codex plugin add ios-shipguard@ringly-codex-workflows",
            "```",
            "",
            "After installation, ask Codex to use `$ios-shipguard` before risky iOS edits.",
            "",
        ]
    )
    return "\n".join(lines)


def build_demo(out_dir: Path, fixture: Path, cases: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not fixture.is_dir():
        fail(f"fixture not found: {fixture}")
    if not cases.is_file():
        fail(f"eval cases not found: {cases}")

    python = sys.executable
    steps = [
        run_step(
            "doctor",
            "iOS Doctor",
            [python, str(ROOT / "scripts" / "ios_doctor.py"), "--path", str(fixture), "--out", str(out_dir / "doctor")],
            out_dir,
        ),
        run_step(
            "inventory",
            "iOS Inventory",
            [
                python,
                str(ROOT / "scripts" / "ios_inventory.py"),
                "--path",
                str(fixture),
                "--doctor",
                str(out_dir / "doctor" / "ios-doctor.json"),
                "--out",
                str(out_dir / "inventory"),
            ],
            out_dir,
        ),
        run_step(
            "modernize",
            "Swift Modernization",
            [
                python,
                str(ROOT / "scripts" / "ios_modernize.py"),
                "--focus",
                "swift",
                "--path",
                str(fixture),
                "--out",
                str(out_dir / "modernize"),
            ],
            out_dir,
        ),
        run_step(
            "plan",
            "Shipguard Plan",
            [
                python,
                str(ROOT / "scripts" / "ios_plan.py"),
                "--mode",
                "permission-audit",
                "--inventory",
                str(out_dir / "inventory" / "ios-inventory.json"),
                "--out",
                str(out_dir / "plan" / "ios-plan.md"),
            ],
            out_dir,
        ),
        run_step(
            "prove",
            "Shipguard Proof Route",
            [
                python,
                str(ROOT / "scripts" / "ios_prove.py"),
                "--plan",
                str(out_dir / "plan" / "ios-plan.json"),
                "--out",
                str(out_dir / "proof"),
            ],
            out_dir,
        ),
        run_step(
            "app-intelligence",
            "App Intelligence",
            [
                python,
                str(ROOT / "scripts" / "ios_app_intelligence.py"),
                "--path",
                str(fixture),
                "--out",
                str(out_dir / "app-intelligence"),
            ],
            out_dir,
        ),
        run_step(
            "ai-readiness",
            "AI Readiness",
            [
                python,
                str(ROOT / "scripts" / "ios_ai_readiness.py"),
                "--path",
                str(fixture),
                "--out",
                str(out_dir / "ai-readiness"),
            ],
            out_dir,
        ),
        run_step(
            "eval",
            "Shipguard Eval",
            [
                python,
                str(ROOT / "scripts" / "ios_shipguard_eval.py"),
                "--cases",
                str(cases),
                "--out",
                str(out_dir / "eval"),
            ],
            out_dir,
        ),
        run_step(
            "redaction",
            "Report Redaction",
            [
                python,
                str(ROOT / "scripts" / "ios_redaction.py"),
                "--in",
                str(out_dir / "ai-readiness" / "ios-ai-readiness.md"),
                "--out",
                str(out_dir / "redacted" / "ios-ai-readiness.md"),
                "--report",
                str(out_dir / "redacted" / "ios-redaction.json"),
            ],
            out_dir,
        ),
    ]

    artifacts = {
        "doctorMarkdown": rel(out_dir / "doctor" / "ios-doctor.md"),
        "inventoryMarkdown": rel(out_dir / "inventory" / "ios-inventory.md"),
        "modernizeMarkdown": rel(out_dir / "modernize" / "ios-modernize.md"),
        "planMarkdown": rel(out_dir / "plan" / "ios-plan.md"),
        "proofMarkdown": rel(out_dir / "proof" / "ios-proof.md"),
        "appIntelligenceMarkdown": rel(out_dir / "app-intelligence" / "ios-app-intelligence.md"),
        "aiReadinessMarkdown": rel(out_dir / "ai-readiness" / "ios-ai-readiness.md"),
        "evalMarkdown": rel(out_dir / "eval" / "ios-shipguard-eval.md"),
        "redactedAiReadiness": rel(out_dir / "redacted" / "ios-ai-readiness.md"),
        "redactionReport": rel(out_dir / "redacted" / "ios-redaction.json"),
    }
    failed = [step for step in steps if step["status"] != "pass"]
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "codex-maintainer ios demo",
        "generatedAt": utc_now(),
        "status": "pass" if not failed else "fail",
        "fixture": rel(fixture),
        "cases": rel(cases),
        "steps": steps,
        "artifacts": artifacts,
    }
    return report


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out)
    report = build_demo(out_dir, Path(args.fixture), Path(args.cases))
    markdown = write_markdown(report)
    (out_dir / "shipguard-demo.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(markdown, encoding="utf-8")

    print(f"wrote: {out_dir / 'shipguard-demo.json'}")
    print(f"wrote: {out_dir / 'README.md'}")
    print(f"status: {report['status']}")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)

    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
