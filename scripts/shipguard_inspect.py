#!/usr/bin/env python3
"""Unified ShipGuard inspect report."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from shipguard_result import build_result_ux, render_result_markdown

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.path and os.path.abspath(sys.path[0] or os.getcwd()) == SCRIPT_DIR:
    sys.path.pop(0)

import argparse


SCHEMA_VERSION = 1
SURFACE = "ShipGuard InspectDeck"
RELEASE_PROOF_COMMAND = "./bin/shipguard release-proof build --out <dir> --release-url <url> --version <version> --tag <tag> --commit <sha> --ci-run-url <url>"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"inspect: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize ShipGuard repo, proof, plugin, release, and next-action state.")
    parser.add_argument("--path", default=".", help="ShipGuard checkout to inspect")
    parser.add_argument("--out", required=True, help="Output directory for shipguard-inspect.json and .md")
    parser.add_argument("--value-gauntlet", help="tool-value-gauntlet JSON file or output directory")
    parser.add_argument("--full-audit", help="shipguard-full-audit JSON file or output directory")
    parser.add_argument("--release-assets", help="Release proof asset directory containing release-manifest.json")
    parser.add_argument("--shipguard-eval", action="store_true", help="Mark this as ShipGuard product QA only")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths from report output")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def run_command(command: list[str], *, cwd: Path, timeout: int = 12) -> tuple[int | None, str, str]:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def load_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def find_json(source: str | None, filename: str) -> tuple[Path | None, dict[str, Any]]:
    if not source:
        return None, {}
    path = Path(source).expanduser()
    if path.is_file():
        return path, load_json(path)
    if not path.is_dir():
        return path, {}
    direct = path / filename
    if direct.is_file():
        return direct, load_json(direct)
    matches = sorted(path.rglob(filename))
    if matches:
        return matches[0], load_json(matches[0])
    return path, {}


def rel_or_redacted(path: Path | None, root: Path, *, shareable: bool) -> str:
    if path is None:
        return ""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return "<external-path>" if shareable and path.is_absolute() else path.as_posix()


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


def repo_state(root: Path, *, shareable: bool) -> dict[str, Any]:
    version = ""
    version_file = root / "VERSION"
    if version_file.is_file():
        version = version_file.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
    branch_code, branch_out, branch_err = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
    head_code, head_out, _ = run_command(["git", "rev-parse", "HEAD"], cwd=root)
    status_code, status_out, _ = run_command(["git", "status", "--short"], cwd=root)
    remote_code, remote_out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=root)
    return {
        "path": "<shipguard-repo>" if shareable else root.as_posix(),
        "toolkitVersion": version or "unknown",
        "isGitRepo": branch_code == 0,
        "branch": branch_out.strip() if branch_code == 0 else "",
        "upstream": remote_out.strip() if remote_code == 0 else "",
        "head": head_out.strip() if head_code == 0 else "",
        "dirty": bool(status_out.strip()) if status_code == 0 else None,
        "statusLineCount": len(status_out.splitlines()) if status_code == 0 else 0,
        "statusSample": status_out.splitlines()[:20],
        "gitError": branch_err.strip() if branch_code not in (0, None) else "",
    }


def value_gauntlet_summary(path: Path | None, data: dict[str, Any], root: Path, *, shareable: bool) -> dict[str, Any]:
    probe = data.get("lowestValueSurfaceProbe") if isinstance(data.get("lowestValueSurfaceProbe"), dict) else {}
    answer = probe.get("answer") if isinstance(probe.get("answer"), dict) else {}
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    stable_publication = data.get("stablePublicationPriority") if isinstance(data.get("stablePublicationPriority"), dict) else {}
    return {
        "found": bool(data),
        "path": rel_or_redacted(path, root, shareable=shareable),
        "status": data.get("status") or ("missing" if not data else "unknown"),
        "surface": data.get("surface") or "",
        "averageScore": summary.get("averageScore"),
        "commandCount": summary.get("commandCount"),
        "lowestValueSurface": {
            "identifier": answer.get("identifier") or "",
            "name": answer.get("name") or "",
            "surfaceType": answer.get("surfaceType") or "",
            "depthScore": answer.get("depthScore"),
            "missingDepthSignals": answer.get("missingDepthSignals") or [],
            "recommendation": answer.get("recommendation") or "",
            "proofGuidance": answer.get("proofGuidance") or "",
            "reason": answer.get("reason") or "",
        },
        "stablePublicationPriority": {
            "status": stable_publication.get("status") or "",
            "surface": stable_publication.get("surface") or "",
            "nextCommand": stable_publication.get("nextCommand") or "",
            "blockedBy": stable_publication.get("blockedBy") or [],
            "whyItMatters": stable_publication.get("whyItMatters") or "",
        },
        "reportQualityQuestions": data.get("reportQualityQuestions") or [],
    }


def full_audit_summary(path: Path | None, data: dict[str, Any], root: Path, *, shareable: bool) -> dict[str, Any]:
    stages = data.get("stages") if isinstance(data.get("stages"), list) else []
    failing = [stage for stage in stages if isinstance(stage, dict) and stage.get("status") in {"blocked", "failed", "review"}]
    return {
        "found": bool(data),
        "path": rel_or_redacted(path, root, shareable=shareable),
        "status": data.get("status") or ("missing" if not data else "unknown"),
        "profile": data.get("profile") or "",
        "planOnly": data.get("planOnly"),
        "stageStatusSummary": data.get("stageStatusSummary") or {},
        "slowLaneSummary": data.get("slowLaneSummary") or {},
        "efficiency": data.get("efficiency") or {},
        "failedStages": [
            {
                "stageId": stage.get("stageId") or "",
                "title": stage.get("title") or "",
                "status": stage.get("status") or "",
                "errorSummary": stage.get("errorSummary") or "",
            }
            for stage in failing[:8]
        ],
        "scopeBoundary": data.get("scopeBoundary") or {},
        "reportQualityQuestions": data.get("reportQualityQuestions") or [],
    }


def plugin_state(root: Path, *, shareable: bool) -> dict[str, Any]:
    code, stdout, stderr = run_command([str(root / "bin" / "shipguard"), "codex", "status"], cwd=root, timeout=20)
    lines = stdout.splitlines()
    parsed: dict[str, str] = {}
    for line in lines:
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            parsed[key.strip()] = value.strip()
    status = parsed.get("Overall status") or ("blocked" if code not in (0, None) else "unknown")
    output = stdout.strip()
    if shareable:
        output = output.replace(root.as_posix(), "<shipguard-repo>").replace(str(Path.home()), "<home>")
    return {
        "checked": True,
        "status": status,
        "exitCode": code,
        "toolkitVersion": parsed.get("Toolkit version") or "",
        "trackedPluginVersion": parsed.get("Tracked plugin version") or "",
        "installedPluginCount": parsed.get("Installed ios-shipguard plugins") or "",
        "resolvedCLI": parsed.get("Resolved ShipGuard CLI for MCP/status") or "",
        "resolvedCLIVersion": parsed.get("Resolved ShipGuard CLI version") or "",
        "findings": [line[2:] for line in lines if line.startswith("- ") and "_" in line],
        "rawSummary": output.splitlines()[:60],
        "stderr": stderr.strip()[:500],
    }


def release_state(source: str | None, root: Path, *, shareable: bool) -> dict[str, Any]:
    manifest_path, manifest = find_json(source, "release-manifest.json")
    badge_path, badge = find_json(source, "attestation-badge.json")
    artifact = manifest.get("artifact") if isinstance(manifest.get("artifact"), dict) else {}
    proofs = manifest.get("proofs") if isinstance(manifest.get("proofs"), dict) else {}
    required = {
        "version": manifest.get("version") or "",
        "tag": manifest.get("tag") or "",
        "commit": manifest.get("commit") or "",
        "artifact.name": artifact.get("name") or "",
        "artifact.sha256": artifact.get("sha256") or "",
        "proofs.release_url": proofs.get("release_url") or "",
        "proofs.ci_run_url": proofs.get("ci_run_url") or "",
    }
    missing_fields = [key for key, value in required.items() if not str(value).strip()]
    status = "not-provided" if not source else ("missing" if not manifest else ("review" if missing_fields else "pass"))
    return {
        "found": bool(manifest),
        "manifestPath": rel_or_redacted(manifest_path, root, shareable=shareable),
        "badgePath": rel_or_redacted(badge_path, root, shareable=shareable),
        "status": status,
        "version": manifest.get("version") or "",
        "tag": manifest.get("tag") or "",
        "commit": manifest.get("commit") or "",
        "artifactName": artifact.get("name") or "",
        "artifactSHA256": artifact.get("sha256") or "",
        "releaseURL": proofs.get("release_url") or "",
        "ciRunURL": proofs.get("ci_run_url") or "",
        "badgeStatus": badge.get("status") if isinstance(badge, dict) else "",
        "requiredFields": sorted(required),
        "missingRequiredFields": missing_fields,
        "nextCommand": RELEASE_PROOF_COMMAND if missing_fields or not manifest else "",
    }


def proof_inputs(value_path: Path | None, value_data: dict[str, Any], full_path: Path | None, full_data: dict[str, Any], release: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"id": "value-gauntlet", "provided": value_path is not None, "found": bool(value_data), "status": value_data.get("status") or "missing"},
        {"id": "full-audit", "provided": full_path is not None, "found": bool(full_data), "status": full_data.get("status") or "missing"},
        {"id": "release-assets", "provided": bool(release.get("manifestPath")), "found": bool(release.get("found")), "status": release.get("status") or "missing"},
    ]


def missing_receipt_priority(inputs: list[dict[str, Any]]) -> list[dict[str, str]]:
    commands = {
        "value-gauntlet": "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
        "full-audit": "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --plan-only --shipguard-eval --shareable",
        "release-assets": RELEASE_PROOF_COMMAND,
    }
    reasons = {
        "value-gauntlet": "Generate this first so InspectDeck can rank the weakest ShipGuard surface before release proof.",
        "full-audit": "Generate this after value-gauntlet so InspectDeck can summarize the ShipYard lane.",
        "release-assets": "Attach release proof last so publication state is checked against runtime receipts.",
    }
    rows: list[dict[str, str]] = []
    for item in inputs:
        receipt = str(item.get("id") or "")
        if item.get("found"):
            continue
        rows.append(
            {
                "id": receipt,
                "status": str(item.get("status") or "missing"),
                "source": f"{receipt}.missing",
                "nextCommand": commands.get(receipt, ""),
                "reason": reasons.get(receipt, "Generate the missing receipt and rerun inspect."),
            }
        )
    return rows


def command_template_or_default(candidate: str, default: str) -> str:
    text = candidate.strip()
    if not text:
        return default
    command_prefixes = (
        "./",
        "/",
        "shipguard ",
        "codex ",
        "gh ",
        "git ",
        "python ",
        "python3 ",
        "bash ",
        "sh ",
        "make ",
        "pytest ",
        "xcodebuild ",
        "swift ",
    )
    if text.startswith(command_prefixes):
        return text
    return default


def append_proof_guidance(reason: str, proof_guidance: str, command: str) -> str:
    proof = proof_guidance.strip()
    if not proof or proof == command:
        return reason
    return f"{reason} Proof guidance: {proof}"


def command_safe_token(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    return text if all(char in allowed for char in text) else ""


def choose_next_action(value_summary: dict[str, Any], full_summary: dict[str, Any], plugin: dict[str, Any], release: dict[str, Any]) -> dict[str, str]:
    if not value_summary.get("found"):
        return {
            "source": "value-gauntlet.missing",
            "command": "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
            "reason": "No value-gauntlet receipt was supplied to inspect; generate it first so InspectDeck can rank the weakest ShipGuard surface before release proof.",
        }
    if not full_summary.get("found"):
        return {
            "source": "full-audit.missing",
            "command": "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --plan-only --shipguard-eval --shareable",
            "reason": "No full-audit receipt was supplied to inspect; generate it so InspectDeck can summarize the ShipYard lane before release proof.",
        }
    failed = full_summary.get("failedStages") or []
    if failed:
        stage = failed[0]
        stage_id = command_safe_token(stage.get("stageId"))
        command = "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --shipguard-eval --shareable"
        if stage_id:
            command = f"./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --stage {stage_id} --resume --shipguard-eval --shareable"
        return {
            "source": "full-audit.failedStages",
            "command": command,
            "reason": f"Full Audit has a non-passing stage: {stage.get('stageId') or 'unknown'}.",
        }
    stable_publication = value_summary.get("stablePublicationPriority") or {}
    stable_command = command_template_or_default(str(stable_publication.get("nextCommand") or ""), "")
    if stable_publication.get("status") in {"review", "blocked"} and stable_command:
        blockers = stable_publication.get("blockedBy") if isinstance(stable_publication.get("blockedBy"), list) else []
        blocker_text = ", ".join(str(item) for item in blockers[:5] if item)
        reason = stable_publication.get("whyItMatters") or "Stable v4 publication needs real public release proof."
        if blocker_text:
            reason = f"{reason} Blocked by: {blocker_text}."
        return {
            "source": "value-gauntlet.stablePublicationPriority",
            "command": stable_command,
            "reason": reason,
        }
    if not release.get("found"):
        return {
            "source": "release-assets.missing",
            "command": RELEASE_PROOF_COMMAND,
            "reason": "No release proof manifest was supplied to inspect; attach release proof before following lower-priority product recommendations.",
        }
    if release.get("status") != "pass":
        missing = release.get("missingRequiredFields") if isinstance(release.get("missingRequiredFields"), list) else []
        missing_text = ", ".join(str(item) for item in missing[:8] if item) or "unknown required fields"
        return {
            "source": "release-assets.incomplete",
            "command": str(release.get("nextCommand") or RELEASE_PROOF_COMMAND),
            "reason": f"Release proof is readable but incomplete. Missing: {missing_text}.",
        }
    lowest = value_summary.get("lowestValueSurface") or {}
    if lowest.get("recommendation"):
        proof = str(lowest.get("proofGuidance") or "")
        command = command_template_or_default(
            proof,
            "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
        )
        reason = append_proof_guidance(str(lowest.get("recommendation") or ""), proof, command)
        return {
            "source": "value-gauntlet.lowestValueSurfaceProbe.answer",
            "command": command,
            "reason": reason,
        }
    if plugin.get("status") not in {"pass", "unknown"}:
        return {
            "source": "codex.status",
            "command": "codex plugin marketplace add . && codex plugin add ios-shipguard@shipguard && ./bin/shipguard codex status --strict",
            "reason": "The installed Codex plugin state is stale or missing.",
        }
    return {
        "source": "inspect",
        "command": "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile shipyard --shipguard-eval --shareable",
        "reason": "All supplied inspect inputs are readable; run the ShipYard lane when preparing a release.",
    }


def combined_status(inputs: list[dict[str, Any]], repo: dict[str, Any], plugin: dict[str, Any], value: dict[str, Any], full: dict[str, Any]) -> str:
    if repo.get("dirty"):
        return "review"
    hard = {value.get("status"), full.get("status"), plugin.get("status")}
    if "blocked" in hard or "failed" in hard:
        return "blocked"
    if plugin.get("status") in {"missing", "stale"}:
        return "review"
    if any(item.get("provided") and not item.get("found") for item in inputs):
        return "review"
    if not any(item.get("found") for item in inputs):
        return "review"
    if any(item.get("id") == "release-assets" and not item.get("found") for item in inputs):
        return "review"
    if any(item.get("id") == "release-assets" and item.get("status") != "pass" for item in inputs):
        return "review"
    if any(status in {"review", "missing"} for status in hard):
        return "review"
    return "pass"


def render_markdown(report: dict[str, Any]) -> str:
    repo = report["repoState"]
    value = report["proofReceipts"]["valueGauntlet"]
    full = report["proofReceipts"]["fullAudit"]
    plugin = report["pluginState"]
    release = report["releaseState"]
    next_action = report["nextAction"]
    lines = [
        "# ShipGuard InspectDeck",
        "",
        f"- Status: {report['status']}",
        f"- Toolkit version: {repo.get('toolkitVersion')}",
        f"- Branch: {repo.get('branch') or 'unknown'}",
        f"- Dirty worktree: {repo.get('dirty')}",
        f"- Verdict: {report['unifiedVerdict']['summary']}",
        "",
    ]
    lines.extend(render_result_markdown(report["resultUX"]))
    lines.extend(
        [
            "## Next Action",
            "",
        f"- Source: {next_action.get('source')}",
        f"- Reason: {next_action.get('reason')}",
        f"- Command or proof: `{next_action.get('command')}`",
        "",
        "## Proof Inputs",
        "",
        "| Input | Provided | Found | Status |",
        "| --- | --- | --- | --- |",
        ]
    )
    for item in report["proofInputs"]:
        lines.append(f"| {item['id']} | {item['provided']} | {item['found']} | {item['status']} |")
    if report.get("missingReceiptPriority"):
        lines.extend(
            [
                "",
                "## Missing Receipt Priority",
                "",
                "| Receipt | Status | Next command |",
                "| --- | --- | --- |",
            ]
        )
        for item in report["missingReceiptPriority"]:
            lines.append(f"| {item['id']} | {item['status']} | `{item['nextCommand']}` |")
    lowest = value.get("lowestValueSurface") or {}
    lines.extend(
        [
            "",
            "## Value Gauntlet",
            "",
            f"- Status: {value.get('status')}",
            f"- Lowest surface: {lowest.get('identifier') or 'unknown'}",
            f"- Recommendation: {lowest.get('recommendation') or 'none'}",
            f"- Proof guidance: {lowest.get('proofGuidance') or 'none'}",
            "",
            "## Full Audit",
            "",
            f"- Status: {full.get('status')}",
            f"- Profile: {full.get('profile') or 'unknown'}",
            f"- Plan only: {full.get('planOnly')}",
            f"- Stage summary: `{json.dumps(full.get('stageStatusSummary') or {}, sort_keys=True)}`",
            "",
            "## Plugin State",
            "",
            f"- Status: {plugin.get('status')}",
            f"- Tracked plugin version: {plugin.get('trackedPluginVersion') or 'unknown'}",
            f"- Installed plugin count: {plugin.get('installedPluginCount') or 'unknown'}",
            "",
            "## Release State",
            "",
            f"- Status: {release.get('status')}",
            f"- Version: {release.get('version') or 'unknown'}",
            f"- Tag: {release.get('tag') or 'unknown'}",
            f"- Artifact SHA-256: `{release.get('artifactSHA256') or 'unknown'}`",
            f"- Missing required fields: {', '.join(release.get('missingRequiredFields') or []) or 'none'}",
            f"- Next command: `{release.get('nextCommand') or 'none'}`",
            "",
            "## Underlying Evidence",
            "",
        ]
    )
    for item in report["underlyingEvidence"]:
        lines.append(f"- {item['id']}: {item['path'] or 'not supplied'}")
    lines.extend(["", "## Scope Boundary", ""])
    for key, value in report["scopeBoundary"].items():
        lines.append(f"- {key}: {value}")
    if report.get("reportQualityQuestions"):
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    if not root.is_dir():
        fail(f"path is not a directory: {root}")
    value_path, value_data = find_json(args.value_gauntlet, "tool-value-gauntlet.json")
    full_path, full_data = find_json(args.full_audit, "shipguard-full-audit.json")
    repo = repo_state(root, shareable=args.shareable)
    value = value_gauntlet_summary(value_path, value_data, root, shareable=args.shareable)
    full = full_audit_summary(full_path, full_data, root, shareable=args.shareable)
    plugin = plugin_state(root, shareable=args.shareable)
    release = release_state(args.release_assets, root, shareable=args.shareable)
    inputs = proof_inputs(value_path, value_data, full_path, full_data, release)
    missing_receipts = missing_receipt_priority(inputs)
    next_action = choose_next_action(value, full, plugin, release)
    status = combined_status(inputs, repo, plugin, value, full)
    verdict_summary = (
        "Inspect found readable ShipGuard proof inputs and one exact next action."
        if status == "pass"
        else "Inspect completed, but at least one proof input, plugin state, release state, or repo state needs review."
    )
    result_ux = build_result_ux(
        status=status,
        summary=verdict_summary,
        proof_source=str(next_action.get("source") or "proof receipts"),
        why_it_matters="InspectDeck makes ShipGuard's proof state and next move readable from one surface.",
        next_command=str(next_action.get("command") or "shipguard inspect --path . --out /tmp/shipguard-inspect"),
        next_action_summary=str(next_action.get("reason") or verdict_summary),
    )
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard inspect",
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": status,
        "shipguardEval": bool(args.shipguard_eval),
        "shareable": bool(args.shareable),
        "repoState": repo,
        "proofInputs": inputs,
        "missingReceiptPriority": missing_receipts,
        "proofReceipts": {
            "valueGauntlet": value,
            "fullAudit": full,
        },
        "pluginState": plugin,
        "releaseState": release,
        "unifiedVerdict": {
            "status": status,
            "summary": verdict_summary,
        },
        "resultUX": result_ux,
        "nextAction": next_action,
        "underlyingEvidence": [
            {"id": "value-gauntlet", "path": value.get("path") or ""},
            {"id": "full-audit", "path": full.get("path") or ""},
            {"id": "release-manifest", "path": release.get("manifestPath") or ""},
            {"id": "codex-status", "path": "generated inline from shipguard codex status"},
        ],
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "privateAppsUsed": False,
            "doesNotEditTargetApps": True,
            "doesNotPush": True,
            "doesNotPublishRelease": True,
            "purpose": "Summarize ShipGuard proof state and next action from existing receipts.",
        },
        "reportQualityQuestions": [
            "Does InspectDeck make the next action obvious without hiding the source proof?",
            "Are missing inputs marked as missing instead of silently downgraded into confidence?",
            "Can a maintainer jump from the summary to the underlying full-audit, value-gauntlet, release, and plugin evidence?",
        ]
        if args.shipguard_eval
        else [],
    }
    if args.shareable:
        replacements = [(root.as_posix(), "<shipguard-repo>"), (str(Path.home()), "<home>")]
        report = redact_value(report, replacements)
    return report


def main() -> None:
    args = parse_args()
    report = build_report(args)
    markdown = render_markdown(report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "shipguard-inspect.json"
    markdown_path = out_dir / "shipguard-inspect.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    print(f"wrote: {json_path}")
    print(f"wrote: {markdown_path}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(markdown)


if __name__ == "__main__":
    main()
