#!/usr/bin/env python3
"""Audit whether the tracked Codex plugin source is marketplace-ready."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shipguard_result import build_result_ux, render_result_markdown


SCHEMA_VERSION = 1
EXPECTED_REPOSITORY = "https://github.com/jlekerli-source/ShipGuard"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def scrub(text: str, *, root: Path, cache: Path | None, shareable: bool) -> str:
    if not shareable:
        return text
    replacements = {
        root.resolve().as_posix(): "<shipguard-repo>",
        Path.home().resolve().as_posix(): "<home>",
    }
    if cache is not None:
        replacements[cache.resolve().as_posix()] = "<codex-cache>"
    result = text
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result


def value_at_path(data: Any, dotted: str) -> Any:
    value = data
    for part in dotted.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def asset_exists(root: Path, base: Path, raw_path: str) -> tuple[bool, str]:
    if not raw_path:
        return False, "missing path"
    candidate = (base / raw_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return False, f"{raw_path} escapes repository"
    return candidate.is_file() and candidate.stat().st_size > 0, rel(candidate, root)


def add_check(
    checks: list[dict[str, Any]],
    *,
    category: str,
    rule_id: str,
    passed: bool,
    evidence: str,
    recommendation: str,
    required: bool = True,
) -> None:
    checks.append(
        {
            "category": category,
            "id": rule_id,
            "passed": bool(passed),
            "required": bool(required),
            "evidence": evidence,
            "recommendation": recommendation,
        }
    )


def check_text_contains(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return all(phrase.lower() in lowered for phrase in phrases)


def run_codex_status(root: Path, cache: Path | None, shareable: bool) -> dict[str, Any]:
    command = [str(root / "scripts" / "codex_status.sh"), "--strict"]
    if cache is not None:
        command.extend(["--cache", str(cache)])
    env = dict(os.environ, SHIPGUARD_CLI=str(root / "bin" / "shipguard"))
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=45,
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        exit_code: int | str = completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        exit_code = "timeout"
        timed_out = True
    combined = scrub(f"{stdout}\n{stderr}", root=root, cache=cache, shareable=shareable)
    overall = "unknown"
    for line in combined.splitlines():
        if line.startswith("- Overall status:"):
            overall = line.split(":", 1)[1].strip()
            break
    return {
        "command": scrub(" ".join(command), root=root, cache=cache, shareable=shareable),
        "exitCode": exit_code,
        "timedOut": timed_out,
        "overallStatus": overall,
        "passed": exit_code == 0 and overall == "pass",
        "outputSummary": [line for line in combined.splitlines() if line.startswith("- ")][:12],
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    out_dir = Path(args.out).resolve()
    cache = Path(args.cache).resolve() if args.cache else None
    plugin_root = root / "plugins" / "ios-shipguard"
    plugin_json_path = plugin_root / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    readme_path = root / "README.md"
    readiness_doc_path = root / "docs" / "codex-marketplace-readiness.md"
    presentation_doc_path = root / "docs" / "github-presentation.md"
    codex_status_doc_path = root / "docs" / "codex-status.md"
    adoption_doc_path = root / "docs" / "adoption-guide.md"
    install_doc_path = root / "docs" / "install-doctor.md"
    cli_doc_path = root / "docs" / "cli.md"
    ios_doc_path = root / "docs" / "ios-shipguard.md"
    version = read_text(root / "VERSION").strip()
    plugin = load_json(plugin_json_path)
    marketplace = load_json(marketplace_path)
    interface = plugin.get("interface") if isinstance(plugin.get("interface"), dict) else {}
    marketplace_plugins = marketplace.get("plugins") if isinstance(marketplace.get("plugins"), list) else []
    marketplace_plugin = next((item for item in marketplace_plugins if isinstance(item, dict) and item.get("name") == "ios-shipguard"), {})
    marketplace_source = marketplace_plugin.get("source") if isinstance(marketplace_plugin.get("source"), dict) else {}
    readme = read_text(readme_path)
    readiness_doc = read_text(readiness_doc_path)
    presentation_doc = read_text(presentation_doc_path)
    codex_status_doc = read_text(codex_status_doc_path)
    adoption_doc = read_text(adoption_doc_path)
    install_doc = read_text(install_doc_path)
    cli_doc = read_text(cli_doc_path)
    ios_doc = read_text(ios_doc_path)

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="plugin-json-present",
        passed=bool(plugin),
        evidence=rel(plugin_json_path, root) if plugin_json_path.is_file() else "missing",
        recommendation="Keep the tracked plugin manifest in plugins/ios-shipguard/.codex-plugin/plugin.json.",
    )
    for path, expected in {
        "name": "ios-shipguard",
        "repository": EXPECTED_REPOSITORY,
        "homepage": EXPECTED_REPOSITORY,
        "license": "MIT",
        "interface.displayName": "iOS ShipGuard",
        "interface.developerName": "ShipGuard",
        "interface.category": "Developer",
        "interface.websiteURL": EXPECTED_REPOSITORY,
    }.items():
        value = value_at_path(plugin, path)
        add_check(
            checks,
            category="pluginMetadata",
            rule_id=f"plugin-{path.replace('.', '-')}",
            passed=value == expected,
            evidence=f"{path}={value!r}",
            recommendation=f"Set {path} to {expected!r}.",
        )
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="plugin-version-present",
        passed=bool(plugin.get("version")),
        evidence=f"version={plugin.get('version')!r}",
        recommendation="Keep the plugin version bumped with release metadata.",
    )
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="plugin-description-actionable",
        passed=len(str(plugin.get("description") or "")) >= 60 and "Ringly" not in str(plugin.get("description") or ""),
        evidence=str(plugin.get("description") or "")[:140],
        recommendation="Describe ShipGuard as a reusable iOS/Codex workflow, not a single-app helper.",
    )
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="interface-long-description-actionable",
        passed=len(str(interface.get("longDescription") or "")) >= 160 and "Ringly" not in str(interface.get("longDescription") or ""),
        evidence=f"{len(str(interface.get('longDescription') or ''))} character(s)",
        recommendation="Keep the marketplace long description concrete, reusable, and non-app-specific.",
    )
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="interface-default-prompts",
        passed=len(interface.get("defaultPrompt") or []) >= 3,
        evidence=f"{len(interface.get('defaultPrompt') or [])} prompt(s)",
        recommendation="Provide three starter prompts that help a new user start quickly.",
    )
    capabilities = interface.get("capabilities") if isinstance(interface.get("capabilities"), list) else []
    add_check(
        checks,
        category="pluginMetadata",
        rule_id="interface-capabilities-present",
        passed=all(item in capabilities for item in ["Read", "Write", "Interactive"]),
        evidence=", ".join(str(item) for item in capabilities) or "missing",
        recommendation="Declare Read, Write, and Interactive so marketplace reviewers understand the surface.",
    )

    logo_ok, logo_evidence = asset_exists(root, plugin_root, str(interface.get("logo") or ""))
    composer_ok, composer_evidence = asset_exists(root, plugin_root, str(interface.get("composerIcon") or ""))
    readme_icon_ok, readme_icon_evidence = asset_exists(root, root, ".github/assets/shipguard-icon.png")
    add_check(
        checks,
        category="publicAssets",
        rule_id="plugin-logo-present",
        passed=logo_ok,
        evidence=logo_evidence,
        recommendation="Keep a real plugin logo asset in plugins/ios-shipguard/assets/.",
    )
    add_check(
        checks,
        category="publicAssets",
        rule_id="plugin-composer-icon-present",
        passed=composer_ok,
        evidence=composer_evidence,
        recommendation="Keep a composer icon asset in plugins/ios-shipguard/assets/.",
    )
    add_check(
        checks,
        category="publicAssets",
        rule_id="readme-logo-present",
        passed=readme_icon_ok and ".github/assets/shipguard-icon.png" in readme,
        evidence=readme_icon_evidence,
        recommendation="Keep the ShipGuard icon visible at the top of README.md.",
    )
    screenshot_policy_ok = check_text_contains(
        readiness_doc,
        ["Do not fabricate screenshots", "real demo", "Devspace", "public directory"],
    )
    add_check(
        checks,
        category="publicAssets",
        rule_id="screenshot-policy-honest",
        passed=screenshot_policy_ok,
        evidence="real screenshot policy present" if screenshot_policy_ok else "missing screenshot policy",
        recommendation="Document that screenshots must come from real demo/devspace evidence, not fabricated art.",
    )
    social_preview_guidance_ok = check_text_contains(
        presentation_doc,
        [".github/assets/shipguard-icon.png", "Social preview", "owner/admin action"],
    )
    add_check(
        checks,
        category="publicAssets",
        rule_id="github-social-preview-guidance",
        passed=social_preview_guidance_ok,
        evidence=rel(presentation_doc_path, root) if social_preview_guidance_ok else "missing social-preview guidance",
        recommendation="Document the tracked social-preview/icon asset and the GitHub owner/admin upload boundary.",
    )

    add_check(
        checks,
        category="marketplaceSource",
        rule_id="local-marketplace-present",
        passed=bool(marketplace),
        evidence=rel(marketplace_path, root) if marketplace_path.is_file() else "missing",
        recommendation="Keep .agents/plugins/marketplace.json tracked.",
    )
    add_check(
        checks,
        category="marketplaceSource",
        rule_id="local-marketplace-id",
        passed=marketplace.get("name") == "shipguard",
        evidence=f"name={marketplace.get('name')!r}",
        recommendation="Expose the local marketplace as shipguard.",
    )
    add_check(
        checks,
        category="marketplaceSource",
        rule_id="local-marketplace-plugin-path",
        passed=marketplace_plugin.get("name") == "ios-shipguard" and marketplace_source.get("path") == "./plugins/ios-shipguard",
        evidence=f"plugin={marketplace_plugin.get('name')!r}, path={marketplace_source.get('path')!r}",
        recommendation="Expose ios-shipguard@shipguard from ./plugins/ios-shipguard.",
    )

    release_install_docs = "\n".join([install_doc, cli_doc, readiness_doc])
    release_install_ok = (
        f"shipguard-v{version}.tar.gz" in release_install_docs
        or "release package" in install_doc.lower()
    )
    add_check(
        checks,
        category="publicPresentation",
        rule_id="release-install-guidance-present",
        passed=release_install_ok,
        evidence=(
            f"install docs reference shipguard-v{version}.tar.gz"
            if f"shipguard-v{version}.tar.gz" in release_install_docs
            else "install docs describe release package install"
            if release_install_ok
            else "install docs do not describe release package install"
        ),
        recommendation="Keep release-package install guidance in docs so README can stay concise.",
    )
    add_check(
        checks,
        category="publicPresentation",
        rule_id="readme-reusable-positioning",
        passed="Ringly" not in readme[:2500] and check_text_contains(readme[:2500], ["local-first", "open source", "app-neutral"]),
        evidence=(
            "README intro is app-neutral"
            if "Ringly" not in readme[:2500]
            else "README intro mentions Ringly"
        ),
        recommendation="Keep GitHub profile text app-neutral and reusable.",
    )
    add_check(
        checks,
        category="publicPresentation",
        rule_id="marketplace-readiness-doc",
        passed=check_text_contains(readiness_doc, ["Submission Packet", "Install Commands", "Proof Commands", "Asset Checklist"]),
        evidence=rel(readiness_doc_path, root) if readiness_doc_path.is_file() else "missing",
        recommendation="Maintain docs/codex-marketplace-readiness.md as the public submission packet source.",
    )
    add_check(
        checks,
        category="publicPresentation",
        rule_id="github-presentation-doc",
        passed=check_text_contains(presentation_doc, ["Repository About Box", "Release Page Copy", "Refresh Checklist"]),
        evidence=rel(presentation_doc_path, root) if presentation_doc_path.is_file() else "missing",
        recommendation="Maintain docs/github-presentation.md as the public GitHub profile and release-page source of truth.",
    )
    for doc_path, doc_text, rule_id, phrase in [
        (codex_status_doc_path, codex_status_doc, "codex-status-doc-install-flow", "codex plugin marketplace add ."),
        (adoption_doc_path, adoption_doc, "adoption-doc-install-flow", "codex plugin marketplace add ."),
        (ios_doc_path, ios_doc, "ios-doc-plugin-flow", "codex plugin add ios-shipguard@shipguard"),
    ]:
        add_check(
            checks,
            category="publicPresentation",
            rule_id=rule_id,
            passed=phrase in doc_text,
            evidence=rel(doc_path, root) if phrase in doc_text else f"{phrase!r} missing",
            recommendation="Keep plugin install and refresh docs copy-pasteable.",
        )

    status_proof = run_codex_status(root, cache, args.shareable)
    add_check(
        checks,
        category="statusProof",
        rule_id="codex-status-strict-pass",
        passed=bool(status_proof["passed"]),
        evidence=f"overall={status_proof['overallStatus']}, exit={status_proof['exitCode']}",
        recommendation="Refresh the local/synthetic plugin cache and rerun shipguard codex status --strict.",
    )

    install_commands = [
        "codex plugin marketplace add .",
        "codex plugin add ios-shipguard@shipguard",
        "./bin/shipguard codex status --strict",
        "Start a new Codex thread after the plugin refresh.",
    ]
    proof_commands = [
        "./bin/shipguard codex marketplace-readiness --path . --out /tmp/shipguard-marketplace --strict --shareable",
        "./bin/shipguard value-gauntlet --path . --out /tmp/shipguard-value-gauntlet",
        "./tests/codex_marketplace_readiness_test.sh",
        "./tests/package_release_test.sh",
    ]
    submission_packet = {
        "listingTitle": "iOS ShipGuard",
        "developerName": "ShipGuard",
        "category": "Developer",
        "shortDescription": str(interface.get("shortDescription") or ""),
        "longDescription": str(interface.get("longDescription") or ""),
        "repository": EXPECTED_REPOSITORY,
        "homepage": EXPECTED_REPOSITORY,
        "license": "MIT",
        "installCommands": install_commands,
        "proofCommands": proof_commands,
        "assetChecklist": [
            {"asset": "README logo", "path": ".github/assets/shipguard-icon.png", "status": "pass" if readme_icon_ok else "blocked"},
            {
                "asset": "GitHub social preview",
                "path": ".github/assets/shipguard-icon.png via Settings -> General -> Social preview",
                "status": "manual-upload-required",
            },
            {"asset": "Plugin logo", "path": str(interface.get("logo") or ""), "status": "pass" if logo_ok else "blocked"},
            {"asset": "Composer icon", "path": str(interface.get("composerIcon") or ""), "status": "pass" if composer_ok else "blocked"},
            {
                "asset": "Screenshots",
                "path": "generate from real ShipGuard demo/devspace proof when required",
                "status": "policy-ready" if screenshot_policy_ok else "blocked",
            },
        ],
        "privacySecurityNotes": [
            "ShipGuard is local-first and does not require a separate API key for ordinary interactive CLI/plugin use.",
            "Do not publish private app code, screenshots, local paths, tokens, app identifiers, or proprietary reports.",
            "Devspace uses loopback defaults and bearer-token guidance before tunneled visual planning.",
        ],
        "modelChoiceBoundary": "ShipGuard exposes CLI/plugin/MCP surfaces; ChatGPT or Codex model selection happens outside ShipGuard.",
        "screenshotPolicy": "Do not fabricate screenshots. Use real demo, Devspace, or marketplace-requested captures when the public directory asks for screenshots.",
    }

    required_failures = [check for check in checks if check["required"] and not check["passed"]]
    advisory_failures = [check for check in checks if not check["required"] and not check["passed"]]
    status = "blocked" if required_failures else "review" if advisory_failures else "pass"
    next_action = (
        "Fix blocked marketplace readiness checks, refresh the plugin cache, then rerun this command with --strict."
        if status == "blocked"
        else "Run value-gauntlet marketplace-readiness receipts and publish the release proof once the next slice is complete."
    )
    result_ux = build_result_ux(
        status=status,
        summary=f"{len(checks) - len(required_failures) - len(advisory_failures)}/{len(checks)} marketplace readiness checks passed.",
        proof_source="tracked plugin metadata + local marketplace + README/docs/assets + codex status strict proof",
        why_it_matters="A public Codex plugin source must be understandable, installable, visually presentable, and status-verifiable before external users trust it.",
        next_command="./bin/shipguard codex marketplace-readiness --path . --out /tmp/shipguard-marketplace --strict --shareable",
        next_action_summary=next_action,
    )
    findings = [
        {
            "severity": "high" if check["required"] else "review",
            "category": check["category"],
            "ruleId": check["id"],
            "evidence": check["evidence"],
            "recommendation": check["recommendation"],
        }
        for check in checks
        if not check["passed"]
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard codex marketplace-readiness",
        "surface": "ShipGuard MarketplaceDeck",
        "status": status,
        "generatedAt": utc_now(),
        "path": "<shipguard-repo>" if args.shareable else str(root),
        "shareable": bool(args.shareable),
        "resultUX": result_ux,
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "mutatesPluginCache": False,
            "publishesRelease": False,
            "purpose": "Grade the tracked ShipGuard Codex marketplace source and submission packet readiness.",
        },
        "summary": {
            "checkCount": len(checks),
            "passedCheckCount": sum(1 for check in checks if check["passed"]),
            "requiredFailureCount": len(required_failures),
            "advisoryFailureCount": len(advisory_failures),
        },
        "checks": checks,
        "pluginMetadata": {
            "path": rel(plugin_json_path, root),
            "name": plugin.get("name"),
            "version": plugin.get("version"),
            "repository": plugin.get("repository"),
            "displayName": interface.get("displayName"),
            "shortDescription": interface.get("shortDescription"),
            "category": interface.get("category"),
            "defaultPromptCount": len(interface.get("defaultPrompt") or []),
        },
        "marketplaceSource": {
            "path": rel(marketplace_path, root),
            "id": marketplace.get("name"),
            "plugin": marketplace_plugin.get("name"),
            "pluginPath": marketplace_source.get("path"),
        },
        "publicAssets": {
            "readmeLogo": ".github/assets/shipguard-icon.png",
            "githubSocialPreview": ".github/assets/shipguard-icon.png (manual GitHub settings upload)",
            "pluginLogo": str(interface.get("logo") or ""),
            "composerIcon": str(interface.get("composerIcon") or ""),
            "screenshots": interface.get("screenshots") if isinstance(interface.get("screenshots"), list) else [],
            "screenshotPolicy": submission_packet["screenshotPolicy"],
        },
        "installProof": {
            "commands": install_commands,
            "statusCommand": status_proof["command"],
        },
        "statusProof": status_proof,
        "submissionPacket": submission_packet,
        "findings": findings,
        "reportQualityQuestions": [
            "Can a fresh Codex user understand what ShipGuard does from the README and plugin listing without prior private-app context?",
            "Can a maintainer prove plugin install freshness from tracked source, local marketplace, and strict status output?",
            "Are icon, composer icon, screenshot policy, privacy notes, model-choice boundary, and proof commands ready for a public marketplace submission packet?",
            "Does the GitHub About/sidebar copy and social preview still match the latest published release without claiming unreleased v4 stability?",
        ],
    }


def table_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# ShipGuard Codex Marketplace Readiness",
        "",
        f"- Status: {report['status']}",
        f"- Checks: {summary['passedCheckCount']}/{summary['checkCount']} passed",
        f"- Required failures: {summary['requiredFailureCount']}",
        "",
    ]
    lines.extend(render_result_markdown(report["resultUX"]))
    lines.extend(
        [
            "## Submission Packet",
            "",
            f"- Listing title: {report['submissionPacket']['listingTitle']}",
            f"- Developer: {report['submissionPacket']['developerName']}",
            f"- Category: {report['submissionPacket']['category']}",
            f"- Short description: {report['submissionPacket']['shortDescription']}",
            f"- Repository: {report['submissionPacket']['repository']}",
            f"- Model boundary: {report['submissionPacket']['modelChoiceBoundary']}",
            f"- Screenshot policy: {report['submissionPacket']['screenshotPolicy']}",
            "",
            "### Install Commands",
            "",
        ]
    )
    for command in report["submissionPacket"]["installCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "### Proof Commands", ""])
    for command in report["submissionPacket"]["proofCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Public Assets", "", "| Asset | Path | Status |", "| --- | --- | --- |"])
    for item in report["submissionPacket"]["assetChecklist"]:
        lines.append(f"| {table_cell(item['asset'])} | `{table_cell(item['path'])}` | {table_cell(item['status'])} |")
    lines.extend(["", "## Status Proof", ""])
    proof = report["statusProof"]
    lines.append(f"- Command: `{proof['command']}`")
    lines.append(f"- Overall status: {proof['overallStatus']}")
    lines.append(f"- Exit code: {proof['exitCode']}")
    if proof.get("outputSummary"):
        lines.append("- Summary:")
        for line in proof["outputSummary"]:
            lines.append(f"  - {line[2:] if line.startswith('- ') else line}")
    lines.extend(["", "## Checks", "", "| Status | Required | Category | Check | Evidence |", "| --- | --- | --- | --- | --- |"])
    for check in report["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(
            f"| {status} | {str(check['required']).lower()} | {table_cell(check['category'])} | `{table_cell(check['id'])}` | {table_cell(check['evidence'])} |"
        )
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] {finding['ruleId']}: {finding['recommendation']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit ShipGuard Codex marketplace readiness.")
    parser.add_argument("--path", default=".", help="ShipGuard checkout to inspect.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--cache", help="Codex plugin cache to use for strict status proof.")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute paths from report output.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when marketplace readiness is not pass.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout.")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    markdown = render_markdown(report)
    json_path = out_dir / "codex-marketplace-readiness.json"
    markdown_path = out_dir / "codex-marketplace-readiness.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown, end="")
    else:
        print(f"wrote: {json_path}")
        print(f"wrote: {markdown_path}")
        print(f"status: {report['status']}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
