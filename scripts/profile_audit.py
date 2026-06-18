#!/usr/bin/env python3
"""Profile-native first-audit reports for ShipGuard starter repos."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


PROFILE_CONFIG: dict[str, dict[str, Any]] = {
    "web": {
        "tool": "shipguard web audit",
        "surface": "ShipGuard WebScan",
        "json": "web-audit.json",
        "markdown": "web-audit.md",
        "signalGroups": {
            "framework": ["next.config", "vite.config", "nuxt.config", "svelte.config", "astro.config", "remix.config", "package.json"],
            "source": ["src", "app", "pages", "routes", "components", "public"],
            "validation": ["playwright", "cypress", "vitest", "jest", "eslint", "tsconfig", "package.json"],
            "risk": [".env", "auth", "payment", "stripe", "migration", "analytics", "server action"],
        },
        "firstCommands": [
            "shipguard web audit --path . --out /tmp/shipguard-web-audit",
            "shipguard web plan --report /tmp/shipguard-web-audit --out /tmp/shipguard-web-plan --shareable",
            "shipguard ios report-quality --reports /tmp/shipguard-web-audit --out /tmp/shipguard-web-quality --shareable",
        ],
        "recommendedValidation": ["npm run lint", "npm test", "npm run build", "npx playwright test"],
    },
    "backend": {
        "tool": "shipguard backend audit",
        "surface": "ShipGuard ServiceRadar",
        "json": "backend-audit.json",
        "markdown": "backend-audit.md",
        "signalGroups": {
            "framework": ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "requirements.txt", "Dockerfile"],
            "source": ["src", "app", "api", "routes", "services", "workers", "jobs"],
            "validation": ["pytest", "jest", "go test", "cargo test", "openapi", "contract", "migrations"],
            "risk": ["auth", "permission", "migration", "queue", "scheduler", "webhook", "secrets", "rate limit"],
        },
        "firstCommands": [
            "shipguard backend audit --path . --out /tmp/shipguard-backend-audit",
            "shipguard backend plan --report /tmp/shipguard-backend-audit --out /tmp/shipguard-backend-plan --shareable",
            "shipguard ios report-quality --reports /tmp/shipguard-backend-audit --out /tmp/shipguard-backend-quality --shareable",
        ],
        "recommendedValidation": ["lint/typecheck", "unit tests", "integration tests", "migration dry-run", "deployment preflight"],
    },
    "cli": {
        "tool": "shipguard cli audit",
        "surface": "ShipGuard CommandLens",
        "json": "cli-audit.json",
        "markdown": "cli-audit.md",
        "signalGroups": {
            "framework": ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "setup.py", "Makefile"],
            "source": ["bin", "cmd", "src", "scripts", "lib"],
            "validation": ["bats", "pytest", "go test", "cargo test", "shellcheck", "golden", "snapshot"],
            "risk": ["argparse", "commander", "click", "clap", "filesystem", "stdout", "stderr", "exit code", "token"],
        },
        "firstCommands": [
            "shipguard cli audit --path . --out /tmp/shipguard-cli-audit",
            "shipguard cli plan --report /tmp/shipguard-cli-audit --out /tmp/shipguard-cli-plan --shareable",
            "shipguard ios report-quality --reports /tmp/shipguard-cli-audit --out /tmp/shipguard-cli-quality --shareable",
        ],
        "recommendedValidation": ["--help smoke test", "version smoke test", "golden stdout/stderr test", "package install test"],
    },
}


TEXT_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".js", ".ts", ".tsx", ".jsx", ".py", ".go", ".rs", ".sh"}
SKIP_DIRS = {".git", ".cache", ".next", "node_modules", "dist", "build", "DerivedData", "__pycache__"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise SystemExit(f"profile-audit: {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a ShipGuard profile-native first audit.")
    parser.add_argument("profile", choices=sorted(PROFILE_CONFIG), help="Profile to audit")
    parser.add_argument("--path", default=".", help="Target repo to inspect")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report quality questions and scope boundary")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_repo_files(root: Path, limit: int = 350) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if len(files) >= limit:
            break
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile", "AGENTS.md", "SHIPGUARD_PROFILE.md"}):
            files.append(path)
    return files


def signal_hits(root: Path, files: list[Path], signals: list[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    lower_signals = [signal.lower() for signal in signals]
    for path in files:
        relative = rel(path, root)
        path_text = relative.lower()
        content = read_text(path).lower() if path.stat().st_size <= 200_000 else ""
        for raw, signal in zip(signals, lower_signals):
            if signal in path_text or signal in content:
                hits.append({"signal": raw, "path": relative})
                break
    return hits[:20]


def profile_files_status(root: Path) -> dict[str, Any]:
    required = ["AGENTS.md", "SHIPGUARD_PROFILE.md", "PLANS.md", "SUBAGENTS.md", "SCORECARD.md"]
    rows = [{"path": item, "present": (root / item).is_file()} for item in required]
    return {
        "required": rows,
        "presentCount": sum(1 for row in rows if row["present"]),
        "missing": [row["path"] for row in rows if not row["present"]],
    }


def validation_lane_findings(profile: str, grouped: dict[str, list[dict[str, str]]], profile_files: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if profile_files["missing"]:
        findings.append(
            {
                "severity": "review",
                "category": "starter-profile",
                "ruleId": "missing-starter-handoff",
                "evidence": f"Missing starter files: {', '.join(profile_files['missing'])}",
                "recommendation": f"Run `shipguard init {profile} .` or copy the missing starter files before relying on Codex handoffs.",
                "proofGuidance": f"Rerun `shipguard doctor {profile} .` and this profile audit.",
            }
        )
    if not grouped.get("validation"):
        findings.append(
            {
                "severity": "review",
                "category": "validation",
                "ruleId": "no-validation-signals",
                "evidence": "No obvious validation scripts, test frameworks, or contract checks were detected in the scanned files.",
                "recommendation": "Add real validation commands to AGENTS.md and keep the first audit from claiming proof until they run.",
                "proofGuidance": "Rerun the audit after adding the narrowest validation commands for this repo.",
            }
        )
    if not grouped.get("risk"):
        findings.append(
            {
                "severity": "info",
                "category": "risk-map",
                "ruleId": "risk-signals-not-yet-specific",
                "evidence": "The first audit did not detect profile-specific risk terms.",
                "recommendation": "Customize AGENTS.md with protected areas, rollout notes, and proof boundaries for the actual product.",
                "proofGuidance": "Rerun the audit and confirm the risk section names the real protected surfaces.",
            }
        )
    return findings


def build_report(profile: str, target: Path, *, shareable: bool, shipguard_eval: bool) -> dict[str, Any]:
    config = PROFILE_CONFIG[profile]
    root = target.resolve()
    if not root.is_dir():
        fail(f"--path is not a directory: {target}")
    files = iter_repo_files(root)
    grouped = {name: signal_hits(root, files, signals) for name, signals in config["signalGroups"].items()}
    profile_files = profile_files_status(root)
    findings = validation_lane_findings(profile, grouped, profile_files)
    status = "review" if any(item["severity"] == "review" for item in findings) else "pass"
    display_root = "<target-repo>" if shareable else root.as_posix()
    questions = [
        f"Should ShipGuard add a {profile} fix-plan command that turns this first audit into scoped tasks and validation commands?",
        f"Are the {profile} validation lanes specific enough for a solo developer to trust the next Codex edit?",
        f"Can this {profile} audit detect missing proof without leaking local paths or private app details?",
    ]
    if shipguard_eval:
        questions.insert(0, f"Does ShipGuard's {profile} first-audit report give useful next actions beyond starter init/doctor proof?")
    return {
        "schemaVersion": 1,
        "tool": config["tool"],
        "surface": config["surface"],
        "profile": profile,
        "generatedAt": utc_now(),
        "status": status,
        "target": {"root": display_root, "fileCountScanned": len(files)},
        "scopeBoundary": {
            "shipguardOnly": bool(shipguard_eval),
            "targetAppsReadOnly": True,
            "privateAppDetailsAllowed": False,
            "shareable": shareable,
        },
        "profileFiles": profile_files,
        "signals": grouped,
        "recommendedFirstCommands": config["firstCommands"],
        "recommendedValidation": config["recommendedValidation"],
        "findings": findings,
        "reportQualityQuestions": questions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['surface']}",
        "",
        f"- Tool: `{report['tool']}`",
        f"- Status: {report['status']}",
        f"- Profile: {report['profile']}",
        f"- Target: {report['target']['root']}",
        f"- Files scanned: {report['target']['fileCountScanned']}",
        "",
        "## Starter Profile",
        "",
        "| File | Present |",
        "| --- | --- |",
    ]
    for row in report["profileFiles"]["required"]:
        lines.append(f"| `{row['path']}` | {str(row['present']).lower()} |")
    lines.extend(["", "## Signals", ""])
    for group, hits in report["signals"].items():
        lines.append(f"### {group.title()}")
        if hits:
            for hit in hits[:8]:
                lines.append(f"- `{hit['signal']}` in `{hit['path']}`")
        else:
            lines.append("- No signals detected.")
        lines.append("")
    lines.extend(["## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] `{finding['ruleId']}`: {finding['recommendation']}")
            lines.append(f"  Proof: {finding['proofGuidance']}")
    else:
        lines.append("- No blocking first-audit findings.")
    lines.extend(["", "## Recommended First Commands", ""])
    for command in report["recommendedFirstCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Recommended Validation", ""])
    for command in report["recommendedValidation"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args.profile, Path(args.path), shareable=args.shareable, shipguard_eval=args.shipguard_eval)
    markdown = render_markdown(report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = PROFILE_CONFIG[args.profile]
    json_path = out_dir / config["json"]
    markdown_path = out_dir / config["markdown"]
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)
    else:
        print(f"wrote: {json_path}")
        print(f"wrote: {markdown_path}")
        print(f"status: {report['status']}")


if __name__ == "__main__":
    main()
