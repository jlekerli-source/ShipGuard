#!/usr/bin/env python3
"""ShipGuard Tool Value Gauntlet: grade toolkit surfaces for real developer value."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
LOWEST_VALUE_QUESTION = "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?"

COMMANDS: list[dict[str, str]] = [
    {"command": "shipguard brand", "surface": "ShipGuard Brand Deck", "family": "brand"},
    {"command": "shipguard init", "surface": "ShipGuard StarterBay", "family": "starter"},
    {"command": "shipguard validate", "surface": "ShipGuard RigCheck", "family": "validation"},
    {"command": "shipguard doctor", "surface": "ShipGuard RepoVitals", "family": "validation"},
    {"command": "shipguard policy", "surface": "ShipGuard RuleHarbor", "family": "policy"},
    {"command": "shipguard score", "surface": "ShipGuard RunScore", "family": "review"},
    {"command": "shipguard transcript", "surface": "ShipGuard TraceVault", "family": "privacy"},
    {"command": "shipguard review-comment", "surface": "ShipGuard ReviewBeacon", "family": "review"},
    {"command": "shipguard ci-gate", "surface": "ShipGuard GateTower", "family": "ci"},
    {"command": "shipguard ci-summary", "surface": "ShipGuard BriefBeacon", "family": "ci"},
    {"command": "shipguard check-run", "surface": "ShipGuard CheckPilot", "family": "ci"},
    {"command": "shipguard sarif", "surface": "ShipGuard AlertBeacon", "family": "ci"},
    {"command": "shipguard docs-check", "surface": "ShipGuard LinkSweep", "family": "docs"},
    {"command": "shipguard value-gauntlet", "surface": "ShipGuard Tool Value Gauntlet", "family": "shipyard"},
    {"command": "shipguard ios doctor", "surface": "ShipGuard DockCheck", "family": "ios"},
    {"command": "shipguard ios inventory", "surface": "ShipGuard CargoScan", "family": "ios"},
    {"command": "shipguard ios plan", "surface": "ShipGuard BriefForge", "family": "ios"},
    {"command": "shipguard ios prove", "surface": "ShipGuard ProofVault", "family": "ios"},
    {"command": "shipguard ios launchdeck", "surface": "ShipGuard LaunchDeck", "family": "ios"},
    {"command": "shipguard ios performance", "surface": "ShipGuard PulseRadar", "family": "ios"},
    {"command": "shipguard ios design", "surface": "ShipGuard VibeCheck", "family": "ios"},
    {"command": "shipguard ios modernize", "surface": "ShipGuard UpgradeForge", "family": "ios"},
    {"command": "shipguard ios app-intelligence", "surface": "ShipGuard SignalLens", "family": "ios"},
    {"command": "shipguard ios ai-readiness", "surface": "ShipGuard ModelDock", "family": "ios"},
    {"command": "shipguard ios external-audit", "surface": "ShipGuard SourceScout", "family": "ios"},
    {"command": "shipguard ios spec-workflow", "surface": "ShipGuard SpecForge", "family": "ios"},
    {"command": "shipguard ios report-quality", "surface": "ShipGuard QualityRadar", "family": "ios"},
    {"command": "shipguard ios preview", "surface": "ShipGuard MirrorPort", "family": "ios"},
    {"command": "shipguard ios devspace", "surface": "ShipGuard Devspace Bridge", "family": "ios"},
    {"command": "shipguard ios devspace-check", "surface": "ShipGuard BridgeWatch", "family": "ios"},
    {"command": "shipguard ios target-match", "surface": "ShipGuard TapCompass", "family": "ios"},
    {"command": "shipguard ios codex-handoff", "surface": "ShipGuard HandoffRail", "family": "ios"},
    {"command": "shipguard ios redact", "surface": "ShipGuard RedactionBay", "family": "ios"},
    {"command": "shipguard ios eval", "surface": "ShipGuard EvalArena", "family": "ios"},
    {"command": "shipguard ios demo", "surface": "ShipGuard DemoDock", "family": "ios"},
    {"command": "shipguard ios goals", "surface": "ShipGuard GoalEngine", "family": "ios"},
    {"command": "shipguard release-proof", "surface": "ShipGuard ReleaseDock", "family": "release"},
    {"command": "shipguard release-manifest", "surface": "ShipGuard ManifestForge", "family": "release"},
    {"command": "shipguard release-index", "surface": "ShipGuard ReleaseAtlas", "family": "release"},
    {"command": "shipguard release-replay", "surface": "ShipGuard ReplayRig", "family": "release"},
    {"command": "shipguard release-attest", "surface": "ShipGuard TrustStamp", "family": "release"},
    {"command": "shipguard release-consume", "surface": "ShipGuard ConsumerDock", "family": "release"},
    {"command": "shipguard release-diff", "surface": "ShipGuard DiffLens", "family": "release"},
    {"command": "shipguard release-evidence", "surface": "ShipGuard EvidenceHarbor", "family": "release"},
    {"command": "shipguard autopsy", "surface": "ShipGuard AutopsyLab", "family": "review"},
    {"command": "shipguard arena", "surface": "ShipGuard ArenaBench", "family": "bench"},
    {"command": "shipguard codex status", "surface": "ShipGuard PluginRadar", "family": "plugin"},
    {"command": "shipguard leaderboard", "surface": "ShipGuard ScoreTower", "family": "bench"},
    {"command": "shipguard self-audit", "surface": "ShipGuard SelfScan", "family": "shipyard"},
    {"command": "shipguard next-goal", "surface": "ShipGuard NextRail", "family": "shipyard"},
    {"command": "shipguard version", "surface": "ShipGuard VersionBeacon", "family": "shipyard"},
]

REPORT_QUALITY_QUESTIONS = [
    "Should the lowest-value surface probe execute representative commands and compare actual output against usefulness criteria instead of relying on static metadata only?",
    "Does every useful-looking surface have docs, tests, package proof, and a concrete proof boundary rather than only a branded name?",
    "Do plugin skills and starter skills give Codex actionable routing and validation commands, not just vague advice?",
    "Should repeated low-value patterns become public fixtures or eval cases so ShipGuard cannot regress into decorative output?",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"coming soon", re.IGNORECASE),
    re.compile(r"^\s*placeholder (text|content|copy|section|title)\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\breplace (this|me)\b", re.IGNORECASE),
    re.compile(r"lorem ipsum", re.IGNORECASE),
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"value-gauntlet: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ShipGuard Tool Value Gauntlet against a ShipGuard checkout.")
    parser.add_argument("--path", default=".", help="ShipGuard checkout to inspect")
    parser.add_argument("--out", help="Output directory for tool-value-gauntlet.json and .md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when high-severity value gaps are found")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def command_slug(command: str) -> str:
    return command.replace("shipguard ", "").replace(" ", "_").replace("-", "_")


def command_tokens(command: str) -> list[str]:
    return [part for part in command.replace("shipguard ", "").split() if part]


def has_placeholder(text: str) -> bool:
    return any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS)


def score_from_checks(checks: list[dict[str, Any]]) -> int:
    if not checks:
        return 0
    passed = sum(1 for check in checks if check["passed"])
    return round((passed / len(checks)) * 100)


def severity_for_score(score: int, *, missing_required: bool = False) -> str:
    if missing_required or score < 45:
        return "high"
    if score < 75:
        return "review"
    if score < 90:
        return "opportunity"
    return "info"


def add_finding(findings: list[dict[str, Any]], *, severity: str, category: str, rule_id: str, evidence: str, recommendation: str, proof: str) -> None:
    findings.append(
        {
            "severity": severity,
            "category": category,
            "ruleId": rule_id,
            "evidence": evidence,
            "recommendation": recommendation,
            "proofGuidance": proof,
        }
    )


def list_files(root: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(files))


def build_text_index(root: Path) -> dict[str, str]:
    targets = [
        "README.md",
        "CHANGELOG.md",
        "NEXT_GOAL.md",
        "docs/**/*.md",
        "tests/**/*.sh",
        "scripts/**/*.sh",
        "scripts/**/*.py",
        "plugins/**/*.md",
        "plugins/**/*.json",
        "plugins/**/*.yaml",
        ".agents/**/*.md",
        ".agents/**/*.json",
    ]
    return {rel(path, root): read_text(path) for path in list_files(root, targets)}


def text_contains_any(text_index: dict[str, str], needles: list[str]) -> bool:
    combined = "\n".join(text_index.values()).lower()
    return all(needle.lower() in combined for needle in needles)


def count_hits(text: str, needles: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(needle.lower()) for needle in needles if needle)


def count_hits_in_paths(text_index: dict[str, str], prefixes: tuple[str, ...], needles: list[str]) -> int:
    total = 0
    for path, text in text_index.items():
        if not path.startswith(prefixes):
            continue
        total += count_hits(text, needles)
    return total


def command_has_test(command: str, text_index: dict[str, str]) -> bool:
    slug = command_slug(command)
    tokens = command_tokens(command)
    direct_needles = [command]
    if tokens:
        direct_needles.append(" ".join(tokens))
    if any(needle.lower() in text.lower() for path, text in text_index.items() if path.startswith("tests/") for needle in direct_needles):
        return True
    token_hits = 0
    for path, text in text_index.items():
        if not path.startswith("tests/"):
            continue
        lowered = text.lower()
        if slug in lowered:
            return True
        if all(token.lower() in lowered for token in tokens[-2:]):
            token_hits += 1
    return token_hits > 0


def command_in_self_audit(command: str, self_audit_text: str) -> bool:
    stripped = command.replace("shipguard ", "", 1)
    return f'"{stripped}' in self_audit_text or f'"{command}' in self_audit_text


def command_in_package_proof(command: str, surface: str, family: str, package_text: str) -> bool:
    if command in package_text or surface in package_text:
        return True
    stripped = command.replace("shipguard ", "", 1)
    package_invocation_patterns = [
        f'bin/shipguard" {stripped}',
        f"bin/shipguard {stripped}",
        f"'$package_root/bin/shipguard' {stripped}",
    ]
    if any(pattern in package_text for pattern in package_invocation_patterns):
        return True
    return family in {"release", "bench", "ci"}


def evaluate_commands(root: Path, text_index: dict[str, str], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bin_text = read_text(root / "bin" / "shipguard")
    self_audit_text = read_text(root / "scripts" / "self_audit.sh")
    package_text = read_text(root / "tests" / "package_release_test.sh")
    rows: list[dict[str, Any]] = []
    for item in COMMANDS:
        command = item["command"]
        surface = item["surface"]
        tokens = command_tokens(command)
        help_token = tokens[-1] if tokens else command
        checks = [
            {"id": "wired", "passed": help_token in bin_text or command == "shipguard version"},
            {"id": "branded", "passed": surface in text_index.get("docs/shipguard-naming.md", "")},
            {"id": "documented", "passed": text_contains_any(text_index, [command]) or surface in text_index.get("docs/command-matrix.md", "")},
            {"id": "tested", "passed": command_has_test(command, text_index)},
            {"id": "selfAuditCovered", "passed": command_in_self_audit(command, self_audit_text) or command in {"shipguard init", "shipguard validate", "shipguard doctor", "shipguard version"}},
            {"id": "packageCovered", "passed": command_in_package_proof(command, surface, item["family"], package_text)},
        ]
        score = score_from_checks(checks)
        missing_required = not checks[0]["passed"] or not checks[2]["passed"]
        severity = severity_for_score(score, missing_required=missing_required)
        missing = [check["id"] for check in checks if not check["passed"]]
        rows.append(
            {
                **item,
                "score": score,
                "status": "pass" if score >= 90 else "review",
                "checks": checks,
                "missing": missing,
            }
        )
        if severity != "info":
            add_finding(
                findings,
                severity=severity,
                category="commands",
                rule_id="command-value-coverage-gap",
                evidence=f"{command} score {score}/100 missing {', '.join(missing)}",
                recommendation=f"Upgrade {surface} with concrete docs, tests, self-audit/package proof, or command wiring.",
                proof=f"Rerun shipguard value-gauntlet and the focused test covering {command}.",
            )
    return rows


def skill_title(path: Path) -> str:
    parent = path.parent.name
    if parent == "skills":
        return path.parent.parent.name
    return parent


def evaluate_skills(root: Path, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skill_paths = list_files(root, [".agents/skills/*/SKILL.md", "plugins/*/skills/*/SKILL.md"])
    rows: list[dict[str, Any]] = []
    for path in skill_paths:
        text = read_text(path)
        relative = rel(path, root)
        line_count = len(text.splitlines())
        has_frontmatter = text.startswith("---") and "description:" in text.split("---", 2)[1] if text.startswith("---") and text.count("---") >= 2 else False
        checks = [
            {"id": "exists", "passed": bool(text.strip())},
            {"id": "substantial", "passed": line_count >= 20},
            {"id": "purpose", "passed": "Use" in text or "use" in text or "description:" in text},
            {"id": "commands", "passed": "shipguard" in text or "scripts/" in text or "Run" in text or "run " in text.lower()},
            {"id": "proof", "passed": "proof" in text.lower() or "validation" in text.lower() or "test" in text.lower()},
            {"id": "boundaries", "passed": "do not" in text.lower() or "ask" in text.lower() or "blocked" in text.lower()},
            {"id": "frontmatter", "passed": has_frontmatter or relative.startswith(".agents/skills/")},
            {"id": "noPlaceholders", "passed": not has_placeholder(text)},
        ]
        score = score_from_checks(checks)
        missing = [check["id"] for check in checks if not check["passed"]]
        rows.append(
            {
                "path": relative,
                "name": skill_title(path),
                "score": score,
                "status": "pass" if score >= 85 else "review",
                "lineCount": line_count,
                "checks": checks,
                "missing": missing,
            }
        )
        severity = severity_for_score(score, missing_required=not checks[0]["passed"])
        if severity != "info":
            add_finding(
                findings,
                severity=severity,
                category="skills",
                rule_id="skill-actionability-gap",
                evidence=f"{relative} score {score}/100 missing {', '.join(missing)}",
                recommendation="Upgrade the skill with concrete trigger guidance, commands, proof boundaries, and validation steps.",
                proof="Rerun shipguard value-gauntlet and inspect the skill entry in tool-value-gauntlet.md.",
            )
    return rows


def evaluate_plugins(root: Path, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plugin_paths = list_files(root, ["plugins/*/.codex-plugin/plugin.json"])
    rows: list[dict[str, Any]] = []
    marketplace = load_json(root / ".agents" / "plugins" / "marketplace.json")
    marketplace_text = json.dumps(marketplace)
    for path in plugin_paths:
        data = load_json(path)
        relative = rel(path, root)
        plugin_root = path.parents[1]
        interface = data.get("interface") if isinstance(data.get("interface"), dict) else {}
        skill_path = plugin_root / "skills"
        mcp_path = plugin_root / ".mcp.json"
        checks = [
            {"id": "validJson", "passed": bool(data)},
            {"id": "name", "passed": bool(data.get("name"))},
            {"id": "version", "passed": bool(data.get("version"))},
            {"id": "description", "passed": len(str(data.get("description") or "")) >= 40},
            {"id": "repository", "passed": "ShipGuard" in str(data.get("repository") or data.get("homepage") or "")},
            {"id": "interface", "passed": bool(interface.get("displayName") and interface.get("shortDescription"))},
            {"id": "defaultPrompt", "passed": bool(interface.get("defaultPrompt"))},
            {"id": "skillsPresent", "passed": skill_path.is_dir() and any(skill_path.glob("*/SKILL.md"))},
            {"id": "mcpPresent", "passed": mcp_path.is_file()},
            {"id": "marketplace", "passed": str(data.get("name") or "") in marketplace_text},
        ]
        score = score_from_checks(checks)
        missing = [check["id"] for check in checks if not check["passed"]]
        rows.append(
            {
                "path": relative,
                "name": str(data.get("name") or plugin_root.name),
                "score": score,
                "status": "pass" if score >= 90 else "review",
                "checks": checks,
                "missing": missing,
            }
        )
        severity = severity_for_score(score, missing_required=not checks[0]["passed"])
        if severity != "info":
            add_finding(
                findings,
                severity=severity,
                category="plugins",
                rule_id="plugin-product-readiness-gap",
                evidence=f"{relative} score {score}/100 missing {', '.join(missing)}",
                recommendation="Upgrade plugin metadata, prompts, skill packaging, MCP config, or marketplace linkage.",
                proof="Run shipguard codex status --strict, package proof, and shipguard value-gauntlet.",
            )
    return rows


def action_has_test(action_name: str, text_index: dict[str, str]) -> bool:
    needles = [action_name, action_name.replace("-", "_")]
    return any(
        path.startswith("tests/") and any(needle in text for needle in needles)
        for path, text in text_index.items()
    )


def evaluate_actions(root: Path, text_index: dict[str, str], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    action_paths = list_files(root, ["actions/*/action.yml"])
    rows: list[dict[str, Any]] = []
    for path in action_paths:
        text = read_text(path)
        relative = rel(path, root)
        action_name = path.parent.name
        docs_path = root / "docs" / f"{action_name}.md"
        checks = [
            {"id": "exists", "passed": bool(text.strip())},
            {"id": "name", "passed": "name:" in text},
            {"id": "description", "passed": "description:" in text},
            {"id": "runs", "passed": "runs:" in text and "using:" in text},
            {"id": "shipguard", "passed": "shipguard" in text.lower() or "ShipGuard" in text},
            {"id": "tested", "passed": action_has_test(action_name, text_index)},
            {"id": "documented", "passed": docs_path.is_file() or action_name in text_index.get("docs/command-matrix.md", "")},
        ]
        score = score_from_checks(checks)
        missing = [check["id"] for check in checks if not check["passed"]]
        rows.append(
            {
                "path": relative,
                "name": action_name,
                "score": score,
                "status": "pass" if score >= 85 else "review",
                "checks": checks,
                "missing": missing,
            }
        )
        severity = severity_for_score(score, missing_required=not checks[0]["passed"])
        if severity != "info":
            add_finding(
                findings,
                severity=severity,
                category="actions",
                rule_id="action-value-coverage-gap",
                evidence=f"{relative} score {score}/100 missing {', '.join(missing)}",
                recommendation="Add action docs, tests, or clearer ShipGuard wiring so the action is useful to adopters.",
                proof="Rerun the action test and shipguard value-gauntlet.",
            )
    return rows


def evaluate_docs(root: Path, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    docs = [
        "README.md",
        "docs/cli.md",
        "docs/command-matrix.md",
        "docs/ios-shipguard.md",
        "docs/shipguard-naming.md",
        "docs/oss-evaluation.md",
        "NEXT_GOAL.md",
    ]
    rows: list[dict[str, Any]] = []
    for doc in docs:
        path = root / doc
        text = read_text(path)
        checks = [
            {"id": "exists", "passed": path.is_file()},
            {"id": "substantial", "passed": len(text.splitlines()) >= 10},
            {"id": "shipguard", "passed": "ShipGuard" in text},
            {"id": "commands", "passed": "shipguard" in text or "./bin/shipguard" in text},
            {"id": "proof", "passed": "proof" in text.lower() or "validation" in text.lower() or "test" in text.lower()},
            {"id": "noPlaceholders", "passed": not has_placeholder(text)},
        ]
        score = score_from_checks(checks)
        missing = [check["id"] for check in checks if not check["passed"]]
        rows.append({"path": doc, "score": score, "status": "pass" if score >= 85 else "review", "checks": checks, "missing": missing})
        severity = severity_for_score(score, missing_required=not checks[0]["passed"])
        if severity != "info":
            add_finding(
                findings,
                severity=severity,
                category="docs",
                rule_id="doc-usefulness-gap",
                evidence=f"{doc} score {score}/100 missing {', '.join(missing)}",
                recommendation="Make the doc more actionable with commands, proof boundaries, or validation references.",
                proof="Run docs-check, focused tests, and shipguard value-gauntlet.",
            )
    return rows


def depth_check(check_id: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"id": check_id, "passed": passed, "evidence": evidence}


def depth_score(checks: list[dict[str, Any]]) -> int:
    return score_from_checks([{"id": item["id"], "passed": bool(item["passed"])} for item in checks])


def surface_probe_row(
    *,
    surface_type: str,
    identifier: str,
    name: str,
    base_score: int,
    base_status: str,
    depth_checks: list[dict[str, Any]],
    recommendation: str,
    proof: str,
) -> dict[str, Any]:
    score = depth_score(depth_checks)
    missing = [check["id"] for check in depth_checks if not check["passed"]]
    return {
        "surfaceType": surface_type,
        "identifier": identifier,
        "name": name,
        "baseScore": base_score,
        "baseStatus": base_status,
        "depthScore": score,
        "depthStatus": "pass" if score >= 85 else "review",
        "depthChecks": depth_checks,
        "missingDepthSignals": missing,
        "recommendation": recommendation,
        "proofGuidance": proof,
    }


def command_depth_rows(
    commands: list[dict[str, Any]],
    text_index: dict[str, str],
    *,
    self_audit_text: str,
    package_text: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in commands:
        command = str(item["command"])
        surface = str(item["surface"])
        slug = command_slug(command)
        needles = [command, surface, slug.replace("_", "-"), slug]
        docs_hits = count_hits_in_paths(text_index, ("README.md", "docs/"), needles)
        test_hits = count_hits_in_paths(text_index, ("tests/",), [command, slug, slug.replace("_", "-")])
        script_hits = count_hits_in_paths(text_index, ("scripts/", "bin"), [command, slug, slug.replace("_", "-")])
        checks = [
            depth_check("baseChecksPass", int(item["score"]) >= 90 and item["status"] == "pass", f"base score {item['score']}/100"),
            depth_check("docsDepth", docs_hits >= 2, f"{docs_hits} README/docs references"),
            depth_check("testDepth", test_hits >= 2, f"{test_hits} test references"),
            depth_check("implementationDepth", script_hits >= 2, f"{script_hits} script/bin references"),
            depth_check(
                "selfAuditDepth",
                command_in_self_audit(command, self_audit_text) or command in {"shipguard init", "shipguard validate", "shipguard doctor", "shipguard version"},
                "covered by self-audit or accepted bootstrap/version route",
            ),
            depth_check("packageProofDepth", command_in_package_proof(command, surface, str(item["family"]), package_text), "covered by package proof heuristics"),
        ]
        rows.append(
            surface_probe_row(
                surface_type="command",
                identifier=command,
                name=surface,
                base_score=int(item["score"]),
                base_status=str(item["status"]),
                depth_checks=checks,
                recommendation=f"Upgrade `{command}` with richer examples, focused tests, or output-quality proof if it remains the lowest-depth surface.",
                proof=f"Rerun `./bin/shipguard value-gauntlet --path . --out <out>` and the focused test for `{command}`.",
            )
        )
    return rows


def skill_depth_rows(root: Path, skills: list[dict[str, Any]], text_index: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in skills:
        path = str(item["path"])
        text = read_text(root / path)
        name = str(item["name"])
        docs_hits = count_hits_in_paths(text_index, ("README.md", "docs/"), [name, path])
        test_hits = count_hits_in_paths(text_index, ("tests/",), [name, path])
        command_examples = len(re.findall(r"(?:^|\s)(?:\./bin/shipguard|shipguard|scripts/|python3\s+scripts/)", text))
        validation_hits = len(re.findall(r"(?i)\b(validate|validation|test|proof|rerun|blocked)\b", text))
        checks = [
            depth_check("baseChecksPass", int(item["score"]) >= 85 and item["status"] == "pass", f"base score {item['score']}/100"),
            depth_check("skillDepth", int(item.get("lineCount") or 0) >= 45, f"{item.get('lineCount') or 0} lines"),
            depth_check("commandExamples", command_examples >= 2, f"{command_examples} command/proof examples"),
            depth_check("validationDensity", validation_hits >= 5, f"{validation_hits} validation/proof terms"),
            depth_check("docsReferenced", docs_hits >= 1, f"{docs_hits} README/docs references"),
            depth_check("testReferenced", test_hits >= 1, f"{test_hits} test references"),
        ]
        rows.append(
            surface_probe_row(
                surface_type="skill",
                identifier=path,
                name=name,
                base_score=int(item["score"]),
                base_status=str(item["status"]),
                depth_checks=checks,
                recommendation=f"Upgrade `{path}` with more concrete command routing, examples, proof language, and test/docs linkage if it remains the lowest-depth skill.",
                proof="Rerun `./bin/shipguard value-gauntlet --path . --out <out>` and inspect the Skills plus Lowest-Value Surface Probe sections.",
            )
        )
    return rows


def plugin_depth_rows(root: Path, plugins: list[dict[str, Any]], text_index: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    combined_index = "\n".join(text_index.values())
    for item in plugins:
        path = str(item["path"])
        name = str(item["name"])
        data = load_json(root / path)
        interface = data.get("interface") if isinstance(data.get("interface"), dict) else {}
        default_prompt = str(interface.get("defaultPrompt") or "")
        docs_hits = count_hits_in_paths(text_index, ("README.md", "docs/"), [name, path, "ios-shipguard"])
        test_hits = count_hits_in_paths(text_index, ("tests/",), [name, path, "codex status"])
        checks = [
            depth_check("baseChecksPass", int(item["score"]) >= 90 and item["status"] == "pass", f"base score {item['score']}/100"),
            depth_check("promptDepth", len(default_prompt.split()) >= 12, f"{len(default_prompt.split())} default-prompt words"),
            depth_check("skillBridgeDepth", (root / "plugins" / "ios-shipguard" / "skills").is_dir(), "plugin has bundled skill bridge"),
            depth_check("docsReferenced", docs_hits >= 2, f"{docs_hits} README/docs references"),
            depth_check("testReferenced", test_hits >= 2, f"{test_hits} test references"),
            depth_check("strictStatusProof", "shipguard codex status --strict" in combined_index, "strict local cache status proof referenced"),
        ]
        rows.append(
            surface_probe_row(
                surface_type="plugin",
                identifier=path,
                name=name,
                base_score=int(item["score"]),
                base_status=str(item["status"]),
                depth_checks=checks,
                recommendation=f"Upgrade plugin `{name}` with clearer routing, install proof, and local-cache validation if it remains the lowest-depth surface.",
                proof="Run `codex plugin marketplace add .`, `codex plugin add ios-shipguard@shipguard`, and `./bin/shipguard codex status --strict`.",
            )
        )
    return rows


def action_depth_rows(root: Path, actions: list[dict[str, Any]], text_index: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in actions:
        path = str(item["path"])
        name = str(item["name"])
        text = read_text(root / path)
        docs_hits = count_hits_in_paths(text_index, ("README.md", "docs/"), [name, path])
        test_hits = count_hits_in_paths(text_index, ("tests/",), [name, path])
        input_hits = len(re.findall(r"(?m)^\s{2,}[A-Za-z0-9_-]+:\s*$", text))
        checks = [
            depth_check("baseChecksPass", int(item["score"]) >= 85 and item["status"] == "pass", f"base score {item['score']}/100"),
            depth_check("docsDepth", docs_hits >= 1, f"{docs_hits} README/docs references"),
            depth_check("testDepth", test_hits >= 1, f"{test_hits} test references"),
            depth_check("inputDepth", input_hits >= 1, f"{input_hits} action input-like blocks"),
            depth_check("shipguardInvocation", "./bin/shipguard" in text or "shipguard" in text.lower(), "action invokes or documents ShipGuard"),
        ]
        rows.append(
            surface_probe_row(
                surface_type="action",
                identifier=path,
                name=name,
                base_score=int(item["score"]),
                base_status=str(item["status"]),
                depth_checks=checks,
                recommendation=f"Upgrade GitHub Action `{name}` with stronger examples, inputs, and release proof if it remains the lowest-depth action.",
                proof=f"Rerun action/package tests and inspect `{path}` in the value-gauntlet report.",
            )
        )
    return rows


def doc_depth_rows(root: Path, docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in docs:
        path = str(item["path"])
        text = read_text(root / path)
        command_blocks = text.count("```")
        shipguard_hits = count_hits(text, ["shipguard", "./bin/shipguard"])
        proof_hits = count_hits(text, ["proof", "validate", "validation", "test"])
        checks = [
            depth_check("baseChecksPass", int(item["score"]) >= 85 and item["status"] == "pass", f"base score {item['score']}/100"),
            depth_check("commandExamples", command_blocks >= 2 or shipguard_hits >= 6, f"{command_blocks} code fences, {shipguard_hits} ShipGuard mentions"),
            depth_check("proofDensity", proof_hits >= 5, f"{proof_hits} proof/validation/test mentions"),
            depth_check("notTooThin", len(text.splitlines()) >= 25, f"{len(text.splitlines())} lines"),
        ]
        rows.append(
            surface_probe_row(
                surface_type="doc",
                identifier=path,
                name=path,
                base_score=int(item["score"]),
                base_status=str(item["status"]),
                depth_checks=checks,
                recommendation=f"Upgrade `{path}` with clearer commands, proof expectations, or examples if it remains the lowest-depth doc.",
                proof="Run `./bin/shipguard docs-check . --out <out>` plus value-gauntlet.",
            )
        )
    return rows


def lowest_value_surface_probe(
    root: Path,
    text_index: dict[str, str],
    *,
    commands: list[dict[str, Any]],
    skills: list[dict[str, Any]],
    plugins: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    docs: list[dict[str, Any]],
) -> dict[str, Any]:
    self_audit_text = read_text(root / "scripts" / "self_audit.sh")
    package_text = read_text(root / "tests" / "package_release_test.sh")
    rows: list[dict[str, Any]] = []
    rows.extend(command_depth_rows(commands, text_index, self_audit_text=self_audit_text, package_text=package_text))
    rows.extend(skill_depth_rows(root, skills, text_index))
    rows.extend(plugin_depth_rows(root, plugins, text_index))
    rows.extend(action_depth_rows(root, actions, text_index))
    rows.extend(doc_depth_rows(root, docs))
    type_order = {"command": 0, "skill": 1, "plugin": 2, "action": 3, "doc": 4}
    ranked = sorted(
        rows,
        key=lambda row: (
            int(row["baseScore"]),
            int(row["depthScore"]),
            type_order.get(str(row["surfaceType"]), 9),
            str(row["identifier"]),
        ),
    )
    all_static_green = bool(ranked) and all(int(row["baseScore"]) >= 90 and int(row["depthScore"]) >= 100 for row in ranked)
    if all_static_green:
        answer = surface_probe_row(
            surface_type="cross-cutting",
            identifier="shipguard value-gauntlet runtime-output-probe",
            name="Runtime output usefulness probe",
            base_score=100,
            base_status="pass",
            depth_checks=[
                depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                depth_check("runtimeOutputProbe", False, "representative commands are not executed and judged for output usefulness yet"),
            ],
            recommendation="Add a read-only runtime output probe that executes representative ShipGuard commands and grades whether their reports are specific, prioritized, proof-oriented, and non-decorative.",
            proof="Run the new output probe against public fixtures plus `./tests/tool_value_gauntlet_test.sh` and `./tests/ios_report_quality_test.sh`.",
        )
    else:
        answer = ranked[0] if ranked else {}
    if answer:
        missing = ", ".join(answer.get("missingDepthSignals") or []) or "no missing depth signals"
        answer = {
            **answer,
            "reason": (
                f"{answer['surfaceType']} `{answer['identifier']}` has base score {answer['baseScore']}/100 "
                f"and depth score {answer['depthScore']}/100; weakest depth signals: {missing}."
            ),
        }
    return {
        "question": LOWEST_VALUE_QUESTION,
        "method": "Rank by baseline coverage first, then deeper evidence density across docs, tests, implementation references, package/self-audit proof, and concrete command/proof examples. This is read-only ShipGuard product QA and does not inspect private target apps.",
        "answer": answer,
        "rankedSurfaces": ranked[:15],
        "nextProbeQuestion": REPORT_QUALITY_QUESTIONS[0],
    }


def priority_actions(findings: list[dict[str, Any]], probe: dict[str, Any]) -> list[dict[str, Any]]:
    severity_order = {"high": 0, "review": 1, "opportunity": 2, "info": 3}
    sorted_findings = sorted(findings, key=lambda item: (severity_order.get(item["severity"], 9), item["category"], item["ruleId"], item["evidence"]))
    actions = []
    for index, finding in enumerate(sorted_findings[:10], start=1):
        actions.append(
            {
                "priority": index,
                "kind": "upgrade-surface-value",
                "severity": finding["severity"],
                "category": finding["category"],
                "ruleId": finding["ruleId"],
                "summary": f"{finding['recommendation']} Evidence: {finding['evidence']}",
                "proofGuidance": finding["proofGuidance"],
            }
        )
    if not actions and probe.get("answer"):
        answer = probe["answer"]
        actions.append(
            {
                "priority": 1,
                "kind": "upgrade-lowest-depth-surface",
                "severity": "opportunity",
                "category": str(answer.get("surfaceType") or "surface"),
                "ruleId": "lowest-value-surface-depth-probe",
                "summary": f"{answer.get('reason')} {answer.get('recommendation')}",
                "proofGuidance": str(answer.get("proofGuidance") or "Rerun shipguard value-gauntlet after the upgrade."),
            }
        )
    return actions


def build_report(root: Path, strict: bool) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    text_index = build_text_index(root)
    commands = evaluate_commands(root, text_index, findings)
    skills = evaluate_skills(root, findings)
    plugins = evaluate_plugins(root, findings)
    actions = evaluate_actions(root, text_index, findings)
    docs = evaluate_docs(root, findings)
    probe = lowest_value_surface_probe(
        root,
        text_index,
        commands=commands,
        skills=skills,
        plugins=plugins,
        actions=actions,
        docs=docs,
    )
    all_scores = [item["score"] for group in (commands, skills, plugins, actions, docs) for item in group]
    high_count = sum(1 for finding in findings if finding["severity"] == "high")
    review_count = sum(1 for finding in findings if finding["severity"] == "review")
    status = "blocked" if high_count else "review" if review_count else "pass"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard value-gauntlet",
        "surface": "ShipGuard Tool Value Gauntlet",
        "intent": "shipguard-product-qa",
        "generatedAt": utc_now(),
        "status": status,
        "strict": strict,
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Grade ShipGuard's own commands, skills, plugins, actions, docs, and tests for real developer value.",
        },
        "summary": {
            "averageScore": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
            "commandCount": len(commands),
            "skillCount": len(skills),
            "pluginCount": len(plugins),
            "actionCount": len(actions),
            "docCount": len(docs),
            "findingCount": len(findings),
            "highFindingCount": high_count,
            "reviewFindingCount": review_count,
        },
        "commands": commands,
        "skills": skills,
        "plugins": plugins,
        "actions": actions,
        "docs": docs,
        "lowestValueSurfaceProbe": probe,
        "findings": findings,
        "priorityActions": priority_actions(findings, probe),
        "reportQualityQuestions": REPORT_QUALITY_QUESTIONS,
    }


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "..."
    return text


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# ShipGuard Tool Value Gauntlet",
        "",
        f"- Status: {report['status']}",
        f"- Average score: {summary['averageScore']}/100",
        f"- Commands: {summary['commandCount']}",
        f"- Skills: {summary['skillCount']}",
        f"- Plugins: {summary['pluginCount']}",
        f"- Actions: {summary['actionCount']}",
        f"- Findings: {summary['findingCount']} ({summary['highFindingCount']} high, {summary['reviewFindingCount']} review)",
        "",
        "## Priority Actions",
        "",
    ]
    if report["priorityActions"]:
        for action in report["priorityActions"]:
            lines.append(f"{action['priority']}. [{action['severity']}] {action['summary']}")
            lines.append(f"   Proof: {action['proofGuidance']}")
    else:
        lines.append("- No priority value gaps found.")
    probe = report.get("lowestValueSurfaceProbe") or {}
    answer = probe.get("answer") if isinstance(probe, dict) else {}
    lines.extend(["", "## Lowest-Value Surface Probe", ""])
    if answer:
        lines.append(f"- Question: {probe.get('question')}")
        lines.append(f"- Answer: `{answer.get('surfaceType')}` `{answer.get('identifier')}` ({answer.get('name')})")
        lines.append(f"- Base score: {answer.get('baseScore')}/100")
        lines.append(f"- Depth score: {answer.get('depthScore')}/100")
        lines.append(f"- Reason: {answer.get('reason')}")
        lines.append(f"- Recommendation: {answer.get('recommendation')}")
        lines.append(f"- Proof: {answer.get('proofGuidance')}")
        lines.append("")
        lines.append("| Rank | Type | Depth | Base | Surface | Missing Depth Signals |")
        lines.append("| ---: | --- | ---: | ---: | --- | --- |")
        for index, item in enumerate(probe.get("rankedSurfaces", [])[:10], start=1):
            missing = ", ".join(item.get("missingDepthSignals") or []) or "-"
            lines.append(
                f"| {index} | {item.get('surfaceType')} | {item.get('depthScore')} | {item.get('baseScore')} | `{table_cell(item.get('identifier'), 70)}` | {table_cell(missing, 90)} |"
            )
    else:
        lines.append("- No surfaces were available for depth probing.")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "| Score | Status | Command | Surface | Missing |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in sorted(report["commands"], key=lambda row: (row["score"], row["command"])):
        lines.append(f"| {item['score']} | {item['status']} | `{item['command']}` | {item['surface']} | {', '.join(item['missing']) or '-'} |")
    lines.extend(["", "## Skills", "", "| Score | Status | Skill | Path | Missing |", "| --- | --- | --- | --- | --- |"])
    for item in sorted(report["skills"], key=lambda row: (row["score"], row["path"])):
        lines.append(f"| {item['score']} | {item['status']} | {item['name']} | `{item['path']}` | {', '.join(item['missing']) or '-'} |")
    lines.extend(["", "## Plugins", "", "| Score | Status | Plugin | Path | Missing |", "| --- | --- | --- | --- | --- |"])
    for item in sorted(report["plugins"], key=lambda row: (row["score"], row["path"])):
        lines.append(f"| {item['score']} | {item['status']} | {item['name']} | `{item['path']}` | {', '.join(item['missing']) or '-'} |")
    lines.extend(["", "## Actions", "", "| Score | Status | Action | Path | Missing |", "| --- | --- | --- | --- | --- |"])
    for item in sorted(report["actions"], key=lambda row: (row["score"], row["path"])):
        lines.append(f"| {item['score']} | {item['status']} | {item['name']} | `{item['path']}` | {', '.join(item['missing']) or '-'} |")
    lines.extend(["", "## Docs", "", "| Score | Status | Path | Missing |", "| --- | --- | --- | --- |"])
    for item in sorted(report["docs"], key=lambda row: (row["score"], row["path"])):
        lines.append(f"| {item['score']} | {item['status']} | `{item['path']}` | {', '.join(item['missing']) or '-'} |")
    lines.extend(["", "## Findings", "", "| Severity | Category | Rule | Evidence | Recommendation |", "| --- | --- | --- | --- | --- |"])
    for finding in report["findings"][:40]:
        lines.append(
            f"| {finding['severity']} | {finding['category']} | {finding['ruleId']} | {table_cell(finding['evidence'])} | {table_cell(finding['recommendation'])} |"
        )
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    root = Path(args.path).resolve()
    if not root.is_dir():
        fail(f"path is not a directory: {root}")
    report = build_report(root, strict=args.strict)
    markdown = render_markdown(report)
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "tool-value-gauntlet.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out_dir / "tool-value-gauntlet.md").write_text(markdown, encoding="utf-8")
        print(f"wrote: {out_dir / 'tool-value-gauntlet.json'}")
        print(f"wrote: {out_dir / 'tool-value-gauntlet.md'}")
        print(f"status: {report['status']}")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)
    if args.strict and report["status"] == "blocked":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
