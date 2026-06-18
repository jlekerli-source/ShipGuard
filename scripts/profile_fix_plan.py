#!/usr/bin/env python3
"""Profile-native fix-plan reports for ShipGuard starter audits."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

from profile_audit import PROFILE_CONFIG


PLAN_CONFIG: dict[str, dict[str, Any]] = {
    "web": {
        "tool": "shipguard web plan",
        "surface": "ShipGuard WebForge",
        "json": "web-plan.json",
        "markdown": "web-plan.md",
        "auditJson": "web-audit.json",
        "auditTool": "shipguard web audit",
        "auditSurface": "ShipGuard WebScan",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-web-plan --out /tmp/shipguard-web-plan-quality --shareable",
    },
    "backend": {
        "tool": "shipguard backend plan",
        "surface": "ShipGuard ServiceForge",
        "json": "backend-plan.json",
        "markdown": "backend-plan.md",
        "auditJson": "backend-audit.json",
        "auditTool": "shipguard backend audit",
        "auditSurface": "ShipGuard ServiceRadar",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-backend-plan --out /tmp/shipguard-backend-plan-quality --shareable",
    },
    "cli": {
        "tool": "shipguard cli plan",
        "surface": "ShipGuard CommandForge",
        "json": "cli-plan.json",
        "markdown": "cli-plan.md",
        "auditJson": "cli-audit.json",
        "auditTool": "shipguard cli audit",
        "auditSurface": "ShipGuard CommandLens",
        "qualityCommand": "shipguard ios report-quality --reports /tmp/shipguard-cli-plan --out /tmp/shipguard-cli-plan-quality --shareable",
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise SystemExit(f"profile-fix-plan: {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn a ShipGuard profile first-audit report into a scoped fix plan.")
    parser.add_argument("profile", choices=sorted(PLAN_CONFIG), help="Profile to plan")
    parser.add_argument("--report", required=True, help="Profile audit JSON file or directory")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--target", help="Optional read-only target repo used to classify validation commands as runnable, blocked, or manual")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report quality questions and scope boundary")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"could not read audit report {path}: {exc}")
    if not isinstance(loaded, dict):
        fail(f"audit report is not a JSON object: {path}")
    return loaded


def resolve_report(report_path: Path, profile: str) -> Path:
    config = PLAN_CONFIG[profile]
    if report_path.is_file():
        return report_path
    if not report_path.is_dir():
        fail(f"--report is not a file or directory: {report_path}")
    direct = report_path / str(config["auditJson"])
    if direct.is_file():
        return direct
    candidates = sorted(report_path.glob("*-audit.json"))
    if not candidates:
        candidates = sorted(report_path.glob("*.json"))
    if not candidates:
        fail(f"no audit JSON found in {report_path}")
    return candidates[0]


def display_report_path(path: Path, *, shareable: bool, profile: str) -> str:
    return f"<{profile}-audit-report>" if shareable else path.resolve().as_posix()


def display_target_path(path: Path | None, *, shareable: bool) -> str:
    if path is None:
        return "<not-provided>"
    return "<target-repo>" if shareable else path.resolve().as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def target_from_args(raw_target: str | None, audit: dict[str, Any]) -> Path | None:
    if raw_target:
        target = Path(raw_target)
        if not target.is_dir():
            fail(f"--target is not a directory: {raw_target}")
        return target
    audit_target = audit.get("target") if isinstance(audit.get("target"), dict) else {}
    root = str(audit_target.get("root") or "")
    if root and not root.startswith("<"):
        target = Path(root)
        if target.is_dir():
            return target
    return None


def normalize_commands(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    commands: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in commands:
            commands.append(text)
    return commands


def finding_title(finding: dict[str, Any]) -> str:
    rule_id = str(finding.get("ruleId") or "finding")
    category = str(finding.get("category") or "audit")
    return f"{category}: {rule_id}"


def task(
    task_id: str,
    title: str,
    *,
    source: str,
    recommendation: str,
    proof: str,
    validation: list[str],
    severity: str = "review",
) -> dict[str, Any]:
    return {
        "id": task_id,
        "title": title,
        "severity": severity,
        "source": source,
        "recommendation": recommendation,
        "proofGuidance": proof,
        "validationCommands": validation,
        "status": "ready",
    }


def task_from_finding(profile: str, finding: dict[str, Any], index: int) -> dict[str, Any]:
    rule_id = str(finding.get("ruleId") or f"finding-{index}")
    proof = str(finding.get("proofGuidance") or f"Rerun `shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable`.")
    return task(
        f"finding-{index}-{rule_id}",
        finding_title(finding),
        source=f"audit finding `{rule_id}`",
        recommendation=str(finding.get("recommendation") or "Address the audit finding with the smallest reversible change."),
        proof=proof,
        validation=[
            f"shipguard doctor {profile} .",
            f"shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable",
        ],
        severity=str(finding.get("severity") or "review"),
    )


def build_tasks(profile: str, audit: dict[str, Any]) -> list[dict[str, Any]]:
    profile_config = PROFILE_CONFIG[profile]
    validation = normalize_commands(audit.get("recommendedValidation")) or normalize_commands(profile_config.get("recommendedValidation"))
    first_commands = normalize_commands(audit.get("recommendedFirstCommands")) or normalize_commands(profile_config.get("firstCommands"))
    findings = audit.get("findings") if isinstance(audit.get("findings"), list) else []
    tasks = [task_from_finding(profile, item, index) for index, item in enumerate(findings, start=1) if isinstance(item, dict)]
    tasks.extend(
        [
            task(
                "starter-handoff-readiness",
                "Verify starter handoff and repo-local guardrails",
                source="starter profile",
                recommendation="Confirm the target has AGENTS.md, planning templates, scorecard, and profile-specific handoff files before authorizing edits.",
                proof=f"Run `shipguard doctor {profile} .` and keep missing starter files out of release claims.",
                validation=[f"shipguard doctor {profile} .", *first_commands[:1]],
                severity="review",
            ),
            task(
                "validation-lane-hardening",
                "Name the narrowest validation lane before the next Codex edit",
                source="recommendedValidation",
                recommendation="Replace generic validation placeholders with commands the repo can actually run, then keep blocked commands as blockers.",
                proof="Run the smallest listed validation command and capture the exact pass, fail, timeout, or infrastructure blocker.",
                validation=validation,
                severity="review",
            ),
            task(
                "risk-boundary-map",
                "Map product risk into proof boundaries",
                source="audit signals",
                recommendation="Turn detected framework, validation, and risk signals into protected areas, stop conditions, and proof requirements in the target handoff.",
                proof=f"Rerun `shipguard {profile} audit` and confirm the report names concrete risk signals instead of generic advice.",
                validation=[f"shipguard {profile} audit --path . --out /tmp/shipguard-{profile}-audit --shareable"],
                severity="opportunity",
            ),
            task(
                "report-quality-handoff",
                "Grade this plan as ShipGuard output before treating it as useful",
                source="ShipGuard product QA",
                recommendation="Run report-quality on the generated plan so ShipGuard learns when plans are too generic, too noisy, or missing proof guidance.",
                proof="Use QualityRadar results as ShipGuard product QA, not as target-app remediation authorization.",
                validation=[str(PLAN_CONFIG[profile]["qualityCommand"])],
                severity="opportunity",
            ),
        ]
    )
    return tasks


def collect_validation_commands(tasks: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for item in tasks:
        for command in item.get("validationCommands") or []:
            text = str(command).strip()
            if text and text not in commands:
                commands.append(text)
    return commands


def package_json(target: Path | None) -> dict[str, Any]:
    return read_json_file(target / "package.json") if target else {}


def package_scripts(target: Path | None) -> dict[str, str]:
    package = package_json(target)
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def package_dependencies(target: Path | None) -> set[str]:
    package = package_json(target)
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        values = package.get(key)
        if isinstance(values, dict):
            names.update(str(name).lower() for name in values)
    return names


def package_bins(target: Path | None) -> dict[str, str]:
    package = package_json(target)
    raw = package.get("bin")
    if isinstance(raw, dict):
        return {str(key): str(value) for key, value in raw.items()}
    if isinstance(raw, str):
        name = str(package.get("name") or "cli")
        return {name: raw}
    return {}


def has_any_file(target: Path | None, candidates: list[str]) -> bool:
    if not target:
        return False
    return any((target / candidate).exists() for candidate in candidates)


def has_path_match(target: Path | None, patterns: list[str]) -> bool:
    if not target:
        return False
    lowered = [pattern.lower() for pattern in patterns]
    for path in target.rglob("*"):
        if any(part in {".git", "node_modules", ".next", "dist", "build", "__pycache__"} for part in path.parts):
            continue
        relative = path.relative_to(target).as_posix().lower()
        if any(pattern in relative for pattern in lowered):
            return True
    return False


def receipt(
    command: str,
    *,
    status: str,
    evidence: list[str],
    recommended_action: str,
    proof: str,
    suggested_command: str | None = None,
) -> dict[str, Any]:
    return {
        "command": command,
        "status": status,
        "executed": False,
        "runAuthorized": False,
        "suggestedCommand": suggested_command or command,
        "evidence": evidence,
        "recommendedAction": recommended_action,
        "proofGuidance": proof,
    }


def classify_web_command(command: str, target: Path | None) -> dict[str, Any] | None:
    scripts = package_scripts(target)
    deps = package_dependencies(target)
    lowered = command.lower()
    npm_run = re.match(r"^npm run ([A-Za-z0-9:_-]+)$", command)
    if npm_run:
        script = npm_run.group(1)
        if script in scripts:
            return receipt(
                command,
                status="runnable",
                evidence=[f"package.json scripts.{script} is present"],
                recommended_action=f"Run `{command}` when app work is authorized; capture pass/fail output.",
                proof=f"Recheck package.json scripts.{script} before claiming validation proof.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=[f"package.json scripts.{script} is missing"],
            recommended_action=f"Add or document a `{script}` script before using `{command}` as proof.",
            proof="Rerun the profile plan with --target after adding the script.",
        )
    if command == "npm test":
        if "test" in scripts:
            return receipt(
                command,
                status="runnable",
                evidence=["package.json scripts.test is present"],
                recommended_action="Run `npm test` when implementation work is authorized; keep failures as blockers.",
                proof="Recheck package.json scripts.test and capture the test result.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["package.json scripts.test is missing"],
            recommended_action="Add a real test script before relying on `npm test` as proof.",
            proof="Rerun the profile plan with --target after adding a test script.",
        )
    if "playwright" in lowered:
        scripts_text = " ".join(scripts.values()).lower()
        if "playwright" in deps or "playwright" in scripts_text or has_any_file(target, ["playwright.config.ts", "playwright.config.js"]):
            return receipt(
                command,
                status="runnable",
                evidence=["Playwright dependency, script, or config signal is present"],
                recommended_action=f"Run `{command}` only when browser/e2e validation is in scope.",
                proof="Capture the e2e result or exact infrastructure blocker.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No Playwright dependency, script, or config signal was detected"],
            recommended_action="Add a Playwright config/script or replace this with the actual e2e command.",
            proof="Rerun the profile plan with --target after the e2e lane exists.",
        )
    return None


def classify_backend_command(command: str, target: Path | None) -> dict[str, Any] | None:
    lowered = command.lower()
    scripts = package_scripts(target)
    script_names = set(scripts)
    pyproject = read_text(target / "pyproject.toml").lower() if target else ""
    if lowered in {"lint/typecheck", "lint", "typecheck"}:
        if {"lint", "typecheck", "check"} & script_names or any(token in pyproject for token in ("ruff", "mypy", "pyright")):
            return receipt(
                command,
                status="runnable",
                evidence=["lint/typecheck script or Python type/lint tool signal is present"],
                recommended_action="Run the repo-local lint/typecheck command and capture the exact result.",
                proof="Record the concrete command chosen from package.json or pyproject.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No lint/typecheck script or Python lint/type tool signal was detected"],
            recommended_action="Replace the generic lint/typecheck lane with a concrete command.",
            proof="Rerun the profile plan after documenting the command.",
        )
    if lowered in {"unit tests", "test", "tests"}:
        if "test" in script_names or has_any_file(target, ["pytest.ini"]) or "pytest" in pyproject or has_path_match(target, ["tests/", "_test.go", ".test."]):
            return receipt(
                command,
                status="runnable",
                evidence=["unit-test script, pytest config, or tests path signal is present"],
                recommended_action="Run the concrete unit-test command and capture pass/fail output.",
                proof="Record the chosen command and result; generic `unit tests` is not proof by itself.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No test script, pytest config, or obvious tests path was detected"],
            recommended_action="Add a concrete unit-test command before claiming unit-test proof.",
            proof="Rerun the profile plan with --target after the test lane exists.",
        )
    if lowered == "integration tests":
        if "integration" in script_names or has_path_match(target, ["integration", "contract"]):
            return receipt(
                command,
                status="runnable",
                evidence=["integration/contract script or path signal is present"],
                recommended_action="Run the concrete integration or contract command when that risk is in scope.",
                proof="Capture the integration result or exact infrastructure blocker.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No integration or contract validation signal was detected"],
            recommended_action="Do not claim integration proof until a concrete lane exists.",
            proof="Rerun the profile plan after documenting the lane.",
        )
    if lowered == "migration dry-run":
        if has_path_match(target, ["migration", "alembic", "prisma", "schema"]):
            return receipt(
                command,
                status="manual",
                evidence=["migration/schema signal is present but no universal dry-run command can be inferred"],
                recommended_action="Name the repo-specific migration dry-run command before database work.",
                proof="Capture dry-run output or the exact environment blocker.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No migration or schema signal was detected"],
            recommended_action="Remove this lane from the plan or add the real migration dry-run command.",
            proof="Rerun the profile plan after the lane is concrete.",
        )
    if lowered == "deployment preflight":
        return receipt(
            command,
            status="manual",
            evidence=["deployment preflight is environment-specific"],
            recommended_action="Replace with the repo's deploy preview, smoke, or release preflight command.",
            proof="Capture the named preflight command, result, and any credential blocker.",
        )
    return None


def classify_cli_command(command: str, target: Path | None) -> dict[str, Any] | None:
    lowered = command.lower()
    scripts = package_scripts(target)
    bins = package_bins(target)
    if lowered == "--help smoke test":
        if bins or has_any_file(target, ["bin", "cmd"]):
            suggested = f"{next(iter(bins), '<cli-binary>')} --help"
            return receipt(
                command,
                status="runnable",
                suggested_command=suggested,
                evidence=["CLI bin entry or bin/cmd path is present"],
                recommended_action=f"Run `{suggested}` and keep nonzero or broken help output as a blocker.",
                proof="Capture stdout/stderr and exit code.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No CLI bin entry, bin directory, or cmd directory was detected"],
            recommended_action="Add a real CLI entrypoint before claiming help-smoke proof.",
            proof="Rerun the profile plan after the entrypoint exists.",
        )
    if lowered == "version smoke test":
        if bins:
            suggested = f"{next(iter(bins))} --version"
            return receipt(
                command,
                status="manual",
                suggested_command=suggested,
                evidence=["package.json bin entry is present"],
                recommended_action=f"Confirm whether `{suggested}` is supported; if not, document the real version command.",
                proof="Capture stdout/stderr and exit code.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No package.json bin entry was detected"],
            recommended_action="Add or document the CLI binary before version-smoke proof.",
            proof="Rerun the profile plan after the entrypoint exists.",
        )
    if lowered == "golden stdout/stderr test":
        if "test" in scripts or has_path_match(target, ["golden", "snapshot", "tests/"]):
            return receipt(
                command,
                status="runnable",
                evidence=["test script, golden fixture, snapshot, or tests path signal is present"],
                recommended_action="Run the concrete golden/snapshot test and capture stdout/stderr/exit-code proof.",
                proof="Record the chosen command and result.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No test script, golden fixture, snapshot, or tests path was detected"],
            recommended_action="Add a golden CLI behavior test before claiming output proof.",
            proof="Rerun the profile plan after the test exists.",
        )
    if lowered == "package install test":
        if has_any_file(target, ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "setup.py"]):
            return receipt(
                command,
                status="manual",
                evidence=["package manifest is present"],
                recommended_action="Name the repo-specific install smoke command for this language/toolchain.",
                proof="Capture install output and the resulting binary smoke command.",
            )
        return receipt(
            command,
            status="blocked",
            evidence=["No package manifest was detected"],
            recommended_action="Add package metadata before claiming install proof.",
            proof="Rerun the profile plan after package metadata exists.",
        )
    return None


def classify_validation_command(profile: str, command: str, target: Path | None) -> dict[str, Any]:
    if target is None:
        return receipt(
            command,
            status="not_checked",
            evidence=["No --target repo was provided and the audit report did not contain a usable local target root"],
            recommended_action=f"Rerun `shipguard {profile} plan --report <audit> --target <repo> --out <dir>` for read-only command availability receipts.",
            proof="Keep validation proof unclaimed until a target-backed receipt exists.",
        )
    if command.startswith("shipguard "):
        return receipt(
            command,
            status="runnable",
            evidence=["ShipGuard CLI command; availability is covered by the current ShipGuard checkout or installed CLI"],
            recommended_action=f"Run `{command}` from a checkout or installed ShipGuard CLI when this proof lane is needed.",
            proof="Capture the ShipGuard command status and generated artifact paths.",
        )
    classifier = {
        "web": classify_web_command,
        "backend": classify_backend_command,
        "cli": classify_cli_command,
    }[profile]
    classified = classifier(command, target)
    if classified:
        return classified
    return receipt(
        command,
        status="manual",
        evidence=["No profile-specific detector recognized this command"],
        recommended_action="Name the exact repo-local command and owner before claiming proof.",
        proof="Capture the exact command, result, and blocker if it cannot run.",
    )


def build_validation_receipts(profile: str, commands: list[str], target: Path | None, *, shareable: bool) -> dict[str, Any]:
    rows = [classify_validation_command(profile, command, target) for command in commands]
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ("runnable", "blocked", "manual", "not_checked")}
    return {
        "checked": target is not None,
        "target": display_target_path(target, shareable=shareable),
        "mode": "read-only command availability classification; commands were not executed",
        "runnableCount": counts["runnable"],
        "blockedCount": counts["blocked"],
        "manualCount": counts["manual"],
        "notCheckedCount": counts["not_checked"],
        "receipts": rows,
    }


def receipt_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "validation-lane"


def rerun_plan_command(profile: str, audit_path: Path, target: Path | None, *, shareable: bool, shipguard_eval: bool) -> str:
    report_arg = f"<{profile}-audit-report>" if shareable else audit_path.resolve().as_posix()
    target_arg = "<target-repo>" if target is None else display_target_path(target, shareable=shareable)
    parts = [
        f"shipguard {profile} plan",
        f"--report {report_arg}",
        f"--target {target_arg}",
        "--out <rerun-plan-out>",
    ]
    if shipguard_eval:
        parts.append("--shipguard-eval")
    if shareable:
        parts.append("--shareable")
    return " ".join(parts)


def build_validation_rerun_receipts(
    profile: str,
    validation_receipts: dict[str, Any],
    audit_path: Path,
    target: Path | None,
    *,
    shareable: bool,
    shipguard_eval: bool,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    rerun_command = rerun_plan_command(profile, audit_path, target, shareable=shareable, shipguard_eval=shipguard_eval)
    for item in validation_receipts.get("receipts") or []:
        status = str(item.get("status") or "")
        command = str(item.get("command") or "")
        if status == "blocked":
            rows.append(
                {
                    "id": f"repair-{receipt_slug(command)}",
                    "blockedCommand": command,
                    "blockedStatus": status,
                    "blockerEvidence": item.get("evidence") or [],
                    "smallestRepair": item.get("recommendedAction") or "Make this validation lane concrete before claiming proof.",
                    "rerunCommand": rerun_command,
                    "proofGuidance": item.get("proofGuidance") or "Rerun the plan after the smallest repair and verify this lane is no longer blocked.",
                    "repairAuthorized": False,
                    "rerunAuthorized": False,
                    "status": "blocked_until_repaired",
                }
            )
        elif status == "not_checked":
            rows.append(
                {
                    "id": f"target-required-{receipt_slug(command)}",
                    "blockedCommand": command,
                    "blockedStatus": status,
                    "blockerEvidence": item.get("evidence") or [],
                    "smallestRepair": f"Provide `--target <repo>` to classify `{command}` against the real target checkout.",
                    "rerunCommand": rerun_plan_command(profile, audit_path, target, shareable=shareable, shipguard_eval=shipguard_eval),
                    "proofGuidance": "Rerun the profile plan with a target-backed receipt before claiming validation proof.",
                    "repairAuthorized": False,
                    "rerunAuthorized": False,
                    "status": "target_required",
                }
            )
    blocked_pairs = sum(1 for row in rows if row["status"] == "blocked_until_repaired")
    not_checked_pairs = sum(1 for row in rows if row["status"] == "target_required")
    return {
        "checked": validation_receipts.get("checked") is True,
        "mode": "read-only repair/rerun guidance; repair and rerun commands were not executed",
        "pairCount": len(rows),
        "blockedPairCount": blocked_pairs,
        "notCheckedPairCount": not_checked_pairs,
        "rerunCommandTemplate": rerun_command,
        "pairs": rows,
    }


def build_report(profile: str, report_path: Path, *, target_path: str | None, shareable: bool, shipguard_eval: bool) -> dict[str, Any]:
    config = PLAN_CONFIG[profile]
    audit_path = resolve_report(report_path, profile)
    audit = read_json(audit_path)
    if audit.get("profile") != profile:
        fail(f"audit profile mismatch: expected {profile}, got {audit.get('profile') or 'missing'}")
    if audit.get("tool") not in {config["auditTool"], PROFILE_CONFIG[profile]["tool"]}:
        fail(f"audit tool mismatch: expected {config['auditTool']}, got {audit.get('tool') or 'missing'}")
    tasks = build_tasks(profile, audit)
    validation = collect_validation_commands(tasks)
    target = target_from_args(target_path, audit)
    validation_receipts = build_validation_receipts(profile, validation, target, shareable=shareable)
    validation_rerun_receipts = build_validation_rerun_receipts(
        profile,
        validation_receipts,
        audit_path,
        target,
        shareable=shareable,
        shipguard_eval=shipguard_eval,
    )
    status = "review" if audit.get("status") != "pass" or any(task["severity"] == "review" for task in tasks) else "pass"
    questions = [
        f"Does {config['surface']} turn {config['auditSurface']} findings into scoped tasks with validation commands?",
        f"Do validation receipts distinguish runnable {profile} commands from blockers without executing arbitrary target commands?",
        f"Do validation rerun receipts show the smallest repair and rerun path for blocked {profile} validation lanes?",
        f"Are the {profile} plan tasks concrete enough for a solo developer to execute without guessing?",
        f"Does the {profile} plan keep target-app work read-only until a separate implementation task is authorized?",
    ]
    if shipguard_eval:
        questions.insert(0, f"Did ShipGuard produce a useful {profile} fix plan, or is this still decorative guidance?")
    return {
        "schemaVersion": 1,
        "tool": config["tool"],
        "surface": config["surface"],
        "profile": profile,
        "generatedAt": utc_now(),
        "status": status,
        "sourceAudit": {
            "tool": audit.get("tool"),
            "surface": audit.get("surface"),
            "status": audit.get("status"),
            "profile": audit.get("profile"),
            "path": display_report_path(audit_path, shareable=shareable, profile=profile),
            "findingCount": len(audit.get("findings") or []),
            "recommendedValidationCount": len(normalize_commands(audit.get("recommendedValidation"))),
        },
        "scopeBoundary": {
            "shipguardOnly": bool(shipguard_eval),
            "targetAppsReadOnly": True,
            "privateAppDetailsAllowed": False,
            "shareable": shareable,
            "implementationAuthorized": False,
        },
        "fixPlan": {
            "intent": "turn-profile-first-audit-into-scoped-work",
            "taskCount": len(tasks),
            "tasks": tasks,
        },
        "validationCommands": validation,
        "validationReceipts": validation_receipts,
        "validationRerunReceipts": validation_rerun_receipts,
        "stopConditions": [
            "Stop before editing the target repo unless the user explicitly changes the task from ShipGuard product QA to app implementation.",
            "Stop if validation receipts mark a command blocked or not_checked; record the exact blocker instead of claiming proof.",
            "Stop if validation rerun receipts do not show the smallest repair and a rerun command for a blocked lane.",
            "Stop if report-quality flags missing scope boundary, local path leakage, or generic recommendations.",
        ],
        "reportQualityQuestions": questions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['surface']}",
        "",
        f"- Tool: `{report['tool']}`",
        f"- Status: {report['status']}",
        f"- Profile: {report['profile']}",
        f"- ShipGuard-only: {str(report['scopeBoundary']['shipguardOnly']).lower()}",
        f"- Implementation authorized: {str(report['scopeBoundary']['implementationAuthorized']).lower()}",
        "",
        "## Source Audit",
        "",
        f"- Audit tool: `{report['sourceAudit']['tool']}`",
        f"- Audit surface: {report['sourceAudit']['surface']}",
        f"- Audit status: {report['sourceAudit']['status']}",
        f"- Audit path: `{report['sourceAudit']['path']}`",
        f"- Findings: {report['sourceAudit']['findingCount']}",
        "",
        "## Scoped Fix Plan",
        "",
    ]
    for item in report["fixPlan"]["tasks"]:
        lines.append(f"### {item['id']}: {item['title']}")
        lines.append(f"- Severity: {item['severity']}")
        lines.append(f"- Source: {item['source']}")
        lines.append(f"- Recommendation: {item['recommendation']}")
        lines.append(f"- Proof: {item['proofGuidance']}")
        if item.get("validationCommands"):
            lines.append("- Validation:")
            for command in item["validationCommands"]:
                lines.append(f"  - `{command}`")
        lines.append("")
    lines.extend(["## Validation Commands", ""])
    for command in report["validationCommands"]:
        lines.append(f"- `{command}`")
    receipts = report["validationReceipts"]
    lines.extend(
        [
            "",
            "## Validation Receipts",
            "",
            f"- Checked target: {str(receipts['checked']).lower()}",
            f"- Target: `{receipts['target']}`",
            f"- Mode: {receipts['mode']}",
            f"- Runnable: {receipts['runnableCount']}",
            f"- Blocked: {receipts['blockedCount']}",
            f"- Manual: {receipts['manualCount']}",
            f"- Not checked: {receipts['notCheckedCount']}",
            "",
            "| Status | Command | Evidence | Next Action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in receipts["receipts"]:
        evidence = "; ".join(item.get("evidence") or [])
        lines.append(f"| {item['status']} | `{item['command']}` | {evidence} | {item['recommendedAction']} |")
    rerun = report["validationRerunReceipts"]
    lines.extend(
        [
            "",
            "## Validation Rerun Receipts",
            "",
            f"- Checked target: {str(rerun['checked']).lower()}",
            f"- Mode: {rerun['mode']}",
            f"- Repair/rerun pairs: {rerun['pairCount']}",
            f"- Blocked pairs: {rerun['blockedPairCount']}",
            f"- Not-checked pairs: {rerun['notCheckedPairCount']}",
            f"- Rerun template: `{rerun['rerunCommandTemplate']}`",
            "",
            "| Status | Blocked Command | Smallest Repair | Rerun |",
            "| --- | --- | --- | --- |",
        ]
    )
    if rerun["pairs"]:
        for item in rerun["pairs"]:
            lines.append(f"| {item['status']} | `{item['blockedCommand']}` | {item['smallestRepair']} | `{item['rerunCommand']}` |")
    else:
        lines.append("| pass | - | No blocked or unchecked validation lanes were detected. | - |")
    lines.extend(["", "## Stop Conditions", ""])
    for condition in report["stopConditions"]:
        lines.append(f"- {condition}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args.profile, Path(args.report), target_path=args.target, shareable=args.shareable, shipguard_eval=args.shipguard_eval)
    markdown = render_markdown(report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = PLAN_CONFIG[args.profile]
    json_path = out_dir / config["json"]
    markdown_path = out_dir / config["markdown"]
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(markdown)
    print(f"wrote: {json_path}")
    print(f"wrote: {markdown_path}")
    print(f"status: {report['status']}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
