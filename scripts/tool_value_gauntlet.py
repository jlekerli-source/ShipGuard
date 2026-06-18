#!/usr/bin/env python3
"""ShipGuard Tool Value Gauntlet: grade toolkit surfaces for real developer value."""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
LOWEST_VALUE_QUESTION = "Which ShipGuard command, skill, plugin, or action has the lowest developer-value score and should be upgraded next?"

COMMANDS: list[dict[str, str]] = [
    {"command": "shipguard brand", "surface": "ShipGuard Brand Deck", "family": "brand"},
    {"command": "shipguard init", "surface": "ShipGuard StarterBay", "family": "starter"},
    {"command": "shipguard validate", "surface": "ShipGuard RigCheck", "family": "validation"},
    {"command": "shipguard doctor", "surface": "ShipGuard RepoVitals", "family": "validation"},
    {"command": "shipguard web audit", "surface": "ShipGuard WebScan", "family": "profile"},
    {"command": "shipguard web plan", "surface": "ShipGuard WebForge", "family": "profile"},
    {"command": "shipguard backend audit", "surface": "ShipGuard ServiceRadar", "family": "profile"},
    {"command": "shipguard backend plan", "surface": "ShipGuard ServiceForge", "family": "profile"},
    {"command": "shipguard cli audit", "surface": "ShipGuard CommandLens", "family": "profile"},
    {"command": "shipguard cli plan", "surface": "ShipGuard CommandForge", "family": "profile"},
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
    "Should ShipGuard add profile-native proof handoff receipts so repaired web, backend, and CLI plans become copy-ready evidence packets?",
    "Does every useful-looking surface have docs, tests, package proof, and a concrete proof boundary rather than only a branded name?",
    "Do plugin skills and starter skills give Codex actionable routing and validation commands, not just vague advice?",
    "Should repeated low-value patterns become public fixtures or eval cases so ShipGuard cannot regress into decorative output?",
]

RUNTIME_OUTPUT_SPECS: list[dict[str, Any]] = [
    {
        "id": "brand-deck",
        "surface": "ShipGuard Brand Deck",
        "displayCommand": "./bin/shipguard brand --path . --out <probe-out>/brand --strict",
        "args": ["brand", "--path", ".", "--out", "{out}/brand", "--strict"],
        "jsonPath": "brand/ios-branding.json",
        "markdownPath": "brand/ios-branding.md",
        "requiredJsonKeys": ["tool", "status", "surface", "reportQualityQuestions"],
        "requiredNonEmptyJsonPaths": ["reportQualityQuestions", "surfaces"],
        "markdownPhrases": ["# ShipGuard", "Report Quality Questions"],
        "usefulnessSignals": ["ShipGuard", "proof", "question", "command"],
    },
    {
        "id": "ios-doctor-demo",
        "surface": "ShipGuard DockCheck",
        "displayCommand": "./bin/shipguard ios doctor --path fixtures/demo-ios-repo --out <probe-out>/doctor",
        "args": ["ios", "doctor", "--path", "fixtures/demo-ios-repo", "--out", "{out}/doctor"],
        "jsonPath": "doctor/ios-doctor.json",
        "markdownPath": "doctor/ios-doctor.md",
        "requiredJsonKeys": ["status", "projects", "packages", "schemes"],
        "requiredNonEmptyJsonPaths": ["projects", "packages", "schemes"],
        "markdownPhrases": ["# iOS Doctor", "Status:"],
        "usefulnessSignals": ["project", "scheme", "package", "validation"],
    },
    {
        "id": "ios-design-demo",
        "surface": "ShipGuard VibeCheck",
        "displayCommand": "./bin/shipguard ios design --path fixtures/demo-ios-repo --out <probe-out>/design --shipguard-eval --shareable",
        "args": ["ios", "design", "--path", "fixtures/demo-ios-repo", "--out", "{out}/design", "--shipguard-eval", "--shareable"],
        "jsonPath": "design/ios-design.json",
        "markdownPath": "design/ios-design.md",
        "requiredJsonKeys": ["tool", "status", "appType", "designDNA", "findings", "reportQualityQuestions"],
        "requiredNonEmptyJsonPaths": ["appType", "designDNA", "findings", "reportQualityQuestions"],
        "markdownPhrases": ["# iOS Design QA", "Report Quality Questions"],
        "usefulnessSignals": ["motion", "haptics", "proof", "recommendation"],
        "expectShipGuardBoundary": True,
    },
    {
        "id": "report-quality-fixture",
        "surface": "ShipGuard QualityRadar",
        "displayCommand": "./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/value-gauntlet-actionability --out <probe-out>/quality --shareable",
        "args": [
            "ios",
            "report-quality",
            "--reports",
            "fixtures/ios-report-quality/value-gauntlet-actionability",
            "--out",
            "{out}/quality",
            "--shareable",
        ],
        "jsonPath": "quality/ios-report-quality.json",
        "markdownPath": "quality/ios-report-quality.md",
        "requiredJsonKeys": ["tool", "status", "priorityAction", "actionabilityQuestions", "fixtureCoverage"],
        "requiredNonEmptyJsonPaths": ["priorityAction", "actionabilityQuestions", "fixtureCoverage"],
        "markdownPhrases": ["# iOS ShipGuard Report Quality", "Priority Action", "Fixture Coverage"],
        "usefulnessSignals": ["priority", "actionability", "fixture", "proof"],
        "expectShipGuardBoundary": True,
    },
]

RUNTIME_NEGATIVE_FIXTURE_ROOT = Path("fixtures") / "tool-value-gauntlet" / "runtime-output"
SKILL_PLUGIN_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "skill-plugin-receipts"
WORKFLOW_CHAIN_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "workflow-chain-receipts"
SCENARIO_MATRIX_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "scenario-matrix-receipts"
SCENARIO_FAILURE_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "scenario-failure-receipts"
SCENARIO_REMEDIATION_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "scenario-remediation-receipts"
ADOPTION_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "adoption-receipts"
TARGET_ONBOARDING_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "target-onboarding-receipts"
MULTI_PROFILE_ONBOARDING_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "multi-profile-onboarding-receipts"
PROFILE_NATIVE_FIRST_AUDIT_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "profile-native-first-audit-receipts"
PROFILE_NATIVE_FIX_PLAN_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "profile-native-fix-plan-receipts"
PROFILE_NATIVE_VALIDATION_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "profile-native-validation-receipts"
PROFILE_NATIVE_VALIDATION_RERUN_RECEIPT_ROOT = Path("fixtures") / "tool-value-gauntlet" / "profile-native-validation-rerun-receipts"

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


def compact_error(text: str, limit: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "..."


def runtime_probe_check(check_id: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"id": check_id, "passed": passed, "evidence": evidence}


def value_at_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def is_meaningful_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, set, tuple)):
        return bool(value)
    return True


def runtime_status_for_checks(checks: list[dict[str, Any]], score: int, *, exit_code: int | str, timed_out: bool) -> str:
    critical_missing = any(
        (not check["passed"])
        and (
            check["id"] in {"exitZero", "jsonArtifact", "markdownArtifact", "machineStatus", "shipguardBoundary"}
            or str(check["id"]).startswith("json:")
            or str(check["id"]).startswith("jsonNonEmpty:")
        )
        for check in checks
    )
    if timed_out or exit_code != 0:
        return "blocked"
    if score >= 85 and not critical_missing:
        return "pass"
    return "review"


def score_runtime_output_artifacts(
    spec: dict[str, Any],
    *,
    loaded: dict[str, Any],
    markdown: str,
    exit_code: int | str,
    timed_out: bool,
    duration_ms: int,
    stdout: str = "",
    stderr: str = "",
) -> dict[str, Any]:
    combined = (json.dumps(loaded, sort_keys=True) + "\n" + markdown).lower()

    checks = [
        runtime_probe_check("exitZero", exit_code == 0, f"exit code {exit_code}"),
        runtime_probe_check("jsonArtifact", bool(loaded), f"{spec['jsonPath']} parsed" if loaded else f"{spec['jsonPath']} missing or invalid"),
        runtime_probe_check(
            "markdownArtifact",
            bool(markdown.strip()),
            f"{spec['markdownPath']} written" if markdown.strip() else f"{spec['markdownPath']} missing or empty",
        ),
        runtime_probe_check("machineStatus", bool(loaded.get("status")), f"status={loaded.get('status') or 'missing'}"),
    ]
    for key in spec.get("requiredJsonKeys", []):
        checks.append(
            runtime_probe_check(
                f"json:{key}",
                value_at_path(loaded, str(key)) is not None,
                f"{key} present" if value_at_path(loaded, str(key)) is not None else f"{key} missing",
            )
        )
    for key in spec.get("requiredNonEmptyJsonPaths", []):
        value = value_at_path(loaded, str(key))
        checks.append(
            runtime_probe_check(
                f"jsonNonEmpty:{key}",
                is_meaningful_value(value),
                f"{key} has meaningful content" if is_meaningful_value(value) else f"{key} empty or missing",
            )
        )
    for phrase in spec.get("markdownPhrases", []):
        checks.append(
            runtime_probe_check(
                f"markdown:{phrase}",
                phrase.lower() in markdown.lower(),
                f"Markdown contains {phrase!r}" if phrase.lower() in markdown.lower() else f"Markdown missing {phrase!r}",
            )
        )
    signal_hits = sum(1 for signal in spec.get("usefulnessSignals", []) if str(signal).lower() in combined)
    checks.append(
        runtime_probe_check(
            "usefulnessSignals",
            signal_hits >= min(3, len(spec.get("usefulnessSignals", []))),
            f"{signal_hits}/{len(spec.get('usefulnessSignals', []))} usefulness signals found",
        )
    )
    if spec.get("expectShipGuardBoundary"):
        boundary = loaded.get("scopeBoundary") if isinstance(loaded.get("scopeBoundary"), dict) else {}
        checks.append(
            runtime_probe_check(
                "shipguardBoundary",
                boundary.get("shipguardOnly") is True,
                "scopeBoundary.shipguardOnly=true" if boundary.get("shipguardOnly") is True else "scopeBoundary.shipguardOnly missing",
            )
        )

    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    status = runtime_status_for_checks(checks, score, exit_code=exit_code, timed_out=timed_out)
    return {
        "id": spec["id"],
        "surface": spec["surface"],
        "command": spec["displayCommand"],
        "durationMs": duration_ms,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "artifacts": {
            "json": f"<probe-out>/{spec['jsonPath']}",
            "markdown": f"<probe-out>/{spec['markdownPath']}",
        },
        "stdoutLineCount": len(stdout.splitlines()),
        "stderrLineCount": len(stderr.splitlines()),
        "errorSummary": compact_error(stderr or stdout) if exit_code != 0 or timed_out else "",
    }


def run_runtime_output_spec(root: Path, probe_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    command_args = [str(part).format(out=probe_root.as_posix()) for part in spec["args"]]
    command = [str(root / "bin" / "shipguard"), *command_args]
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=False,
        )
        exit_code: int | str = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = "timeout"
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        timed_out = True
    except OSError as exc:
        exit_code = "oserror"
        stdout = ""
        stderr = str(exc)
        timed_out = False
    duration_ms = round((time.monotonic() - started) * 1000)

    json_path = probe_root / str(spec["jsonPath"])
    markdown_path = probe_root / str(spec["markdownPath"])
    loaded = load_json(json_path)
    markdown = read_text(markdown_path)
    return score_runtime_output_artifacts(
        spec,
        loaded=loaded,
        markdown=markdown,
        exit_code=exit_code,
        timed_out=timed_out,
        duration_ms=duration_ms,
        stdout=stdout,
        stderr=stderr,
    )


def runtime_output_probe(root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="shipguard-value-runtime-") as tmp:
        probe_root = Path(tmp)
        rows = [run_runtime_output_spec(root, probe_root, spec) for spec in RUNTIME_OUTPUT_SPECS]
    average = round(sum(row["score"] for row in rows) / len(rows), 1) if rows else 0
    blocked_count = sum(1 for row in rows if row["status"] == "blocked")
    review_count = sum(1 for row in rows if row["status"] == "review")
    status = "blocked" if blocked_count else "review" if review_count else "pass"
    lowest = min(rows, key=lambda row: (row["score"], row["id"])) if rows else {}
    return {
        "status": status,
        "averageScore": average,
        "commandCount": len(rows),
        "purpose": "Execute representative ShipGuard commands on public/demo inputs and grade whether their generated outputs are specific, prioritized, proof-oriented, and machine-readable.",
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["ShipGuard checkout", "fixtures/demo-ios-repo", "fixtures/ios-report-quality/value-gauntlet-actionability"],
        },
        "commands": rows,
        "lowestScoringCommand": lowest,
        "nextAction": (
            "Add negative runtime-output fixtures that prove decorative but low-value reports fail the probe."
            if status == "pass"
            else f"Improve runtime output for `{lowest.get('id') or 'unknown'}` before expanding the probe."
        ),
    }


def load_runtime_negative_fixtures(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / RUNTIME_NEGATIVE_FIXTURE_ROOT
    fixtures: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return fixtures
    for meta_path in sorted(fixture_root.glob("*/fixture.json")):
        meta = load_json(meta_path)
        if meta:
            fixtures.append((meta_path.parent, meta))
    return fixtures


def run_runtime_negative_fixture(root: Path, fixture_dir: Path, meta: dict[str, Any]) -> dict[str, Any]:
    spec = {
        "id": str(meta.get("id") or fixture_dir.name),
        "surface": str(meta.get("surface") or "Synthetic runtime-output fixture"),
        "displayCommand": str(meta.get("displayCommand") or f"<fixture>/{rel(fixture_dir, root)}"),
        "jsonPath": str(Path(rel(fixture_dir, root)) / str(meta.get("jsonFile") or "report.json")),
        "markdownPath": str(Path(rel(fixture_dir, root)) / str(meta.get("markdownFile") or "report.md")),
        "requiredJsonKeys": list(meta.get("requiredJsonKeys") or []),
        "requiredNonEmptyJsonPaths": list(meta.get("requiredNonEmptyJsonPaths") or []),
        "markdownPhrases": list(meta.get("markdownPhrases") or []),
        "usefulnessSignals": list(meta.get("usefulnessSignals") or []),
        "expectShipGuardBoundary": bool(meta.get("expectShipGuardBoundary")),
    }
    started = time.monotonic()
    result = score_runtime_output_artifacts(
        spec,
        loaded=load_json(fixture_dir / str(meta.get("jsonFile") or "report.json")),
        markdown=read_text(fixture_dir / str(meta.get("markdownFile") or "report.md")),
        exit_code=0,
        timed_out=False,
        duration_ms=round((time.monotonic() - started) * 1000),
    )
    expected_missing = [str(item) for item in meta.get("expectedMissing") or []]
    expected_max_score = int(meta.get("expectedMaxScore") or 84)
    fixture_passed = (
        result["status"] != "pass"
        and int(result["score"]) <= expected_max_score
        and all(item in result["missing"] for item in expected_missing)
    )
    return {
        **result,
        "fixturePath": rel(fixture_dir, root),
        "fixturePassed": fixture_passed,
        "expectedStatus": "not-pass",
        "expectedMaxScore": expected_max_score,
        "expectedMissing": expected_missing,
        "description": str(meta.get("description") or ""),
    }


def runtime_negative_fixture_probe(root: Path) -> dict[str, Any]:
    cases = [run_runtime_negative_fixture(root, fixture_dir, meta) for fixture_dir, meta in load_runtime_negative_fixtures(root)]
    passed = sum(1 for case in cases if case["fixturePassed"])
    status = "pass" if cases and passed == len(cases) else "review"
    return {
        "status": status,
        "fixtureCount": len(cases),
        "passedFixtureCount": passed,
        "purpose": "Run synthetic public negative fixtures that should fail runtime-output scoring when reports are decorative, boundaryless, empty, or not action-oriented.",
        "fixtureRoot": RUNTIME_NEGATIVE_FIXTURE_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public synthetic runtime-output fixtures"],
        },
        "cases": cases,
        "nextAction": (
            "Expand runtimeOutputProbe from representative command samples into broader command-family execution coverage."
            if cases and passed == len(cases)
            else "Fix runtime-output scoring or fixture expectations so decorative reports cannot pass."
        ),
    }


def runtime_help_command(command: str) -> list[str]:
    return command.replace("shipguard ", "", 1).split() + ["--help"]


def run_runtime_command_help(root: Path, item: dict[str, str]) -> dict[str, Any]:
    command = item["command"]
    args = runtime_help_command(command)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [str(root / "bin" / "shipguard"), *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        exit_code: int | str = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = "timeout"
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        timed_out = True
    except OSError as exc:
        exit_code = "oserror"
        stdout = ""
        stderr = str(exc)
        timed_out = False
    duration_ms = round((time.monotonic() - started) * 1000)
    output = f"{stdout}\n{stderr}".strip()
    tokens = [token for token in command_tokens(command) if token not in {"ios"}]
    token_hits = sum(1 for token in tokens if token.lower() in output.lower())
    checks = [
        runtime_probe_check("exitZero", exit_code == 0, f"exit code {exit_code}"),
        runtime_probe_check("helpOutput", bool(output), "help output present" if output else "help output missing"),
        runtime_probe_check(
            "commandMention",
            "shipguard" in output.lower() or token_hits >= 1,
            f"{token_hits}/{len(tokens)} command token(s) mentioned",
        ),
    ]
    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    status = "pass" if score == 100 and exit_code == 0 and not timed_out else "blocked" if exit_code != 0 or timed_out else "review"
    return {
        "command": f"./bin/shipguard {' '.join(args)}",
        "surface": item["surface"],
        "family": item["family"],
        "durationMs": duration_ms,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "stdoutLineCount": len(stdout.splitlines()),
        "stderrLineCount": len(stderr.splitlines()),
        "errorSummary": compact_error(stderr or stdout) if exit_code != 0 or timed_out else "",
    }


def runtime_command_family_probe(root: Path) -> dict[str, Any]:
    rows = [run_runtime_command_help(root, item) for item in COMMANDS]
    passed = sum(1 for row in rows if row["status"] == "pass")
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    review = sum(1 for row in rows if row["status"] == "review")
    families: dict[str, dict[str, int]] = {}
    for row in rows:
        family = str(row["family"])
        families.setdefault(family, {"commandCount": 0, "passCount": 0, "reviewCount": 0, "blockedCount": 0})
        families[family]["commandCount"] += 1
        if row["status"] == "pass":
            families[family]["passCount"] += 1
        elif row["status"] == "blocked":
            families[family]["blockedCount"] += 1
        else:
            families[family]["reviewCount"] += 1
    status = "blocked" if blocked else "review" if review else "pass"
    return {
        "status": status,
        "commandCount": len(rows),
        "passedCommandCount": passed,
        "purpose": "Execute `--help` for every public ShipGuard command family so the toolkit catches unwired or confusing command entry points at runtime.",
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["ShipGuard public command registry"],
        },
        "families": families,
        "commands": rows,
        "nextAction": (
            "Command-family help coverage is passing; use skill/plugin receipt and workflow-chain probes for higher-level Codex guidance proof."
            if status == "pass"
            else "Fix public commands whose top-level help path does not execute cleanly."
        ),
    }


def load_skill_plugin_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / SKILL_PLUGIN_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_workflow_chain_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / WORKFLOW_CHAIN_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_scenario_matrix_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / SCENARIO_MATRIX_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_scenario_failure_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / SCENARIO_FAILURE_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_scenario_remediation_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / SCENARIO_REMEDIATION_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_adoption_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / ADOPTION_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_target_onboarding_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / TARGET_ONBOARDING_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_multi_profile_onboarding_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / MULTI_PROFILE_ONBOARDING_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_profile_native_first_audit_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / PROFILE_NATIVE_FIRST_AUDIT_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_profile_native_fix_plan_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / PROFILE_NATIVE_FIX_PLAN_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_profile_native_validation_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / PROFILE_NATIVE_VALIDATION_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def load_profile_native_validation_rerun_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    fixture_root = root / PROFILE_NATIVE_VALIDATION_RERUN_RECEIPT_ROOT
    receipts: list[tuple[Path, dict[str, Any]]] = []
    if not fixture_root.is_dir():
        return receipts
    for meta_path in sorted(fixture_root.glob("*/receipt.json")):
        meta = load_json(meta_path)
        if meta:
            receipts.append((meta_path.parent, meta))
    return receipts


def format_receipt_value(value: object, *, out_dir: Path, cache_dir: Path) -> str:
    return str(value).format(out=out_dir.as_posix(), cache=cache_dir.as_posix())


def safe_receipt_relative_path(raw_path: object) -> Path | None:
    path_text = str(raw_path or "").strip()
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path


def prepare_receipt_files(out_dir: Path, meta: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for item in meta.get("prepareFiles") or []:
        relative = safe_receipt_relative_path(item.get("path"))
        check_id = f"preparedFile:{item.get('path') or 'missing'}"
        if relative is None:
            checks.append(runtime_probe_check(check_id, False, "prepared file path must be relative and stay inside receipt output"))
            continue
        target = out_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(item.get("text") or ""), encoding="utf-8")
        checks.append(runtime_probe_check(f"preparedFile:{relative.as_posix()}", target.is_file(), f"{relative.as_posix()} prepared"))
    return checks


def prepare_receipt_tarballs(out_dir: Path, meta: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for item in meta.get("prepareTarballs") or []:
        relative = safe_receipt_relative_path(item.get("path"))
        check_id = f"preparedTarball:{item.get('path') or 'missing'}"
        if relative is None:
            checks.append(runtime_probe_check(check_id, False, "tarball path must be relative and stay inside receipt output"))
            continue
        target = out_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        entries = item.get("entries") if isinstance(item.get("entries"), list) else []
        unsafe_entry = ""
        with tarfile.open(target, "w:gz") as archive:
            for entry in entries:
                entry_path = safe_receipt_relative_path(entry.get("path") if isinstance(entry, dict) else "")
                if entry_path is None:
                    unsafe_entry = str(entry.get("path") if isinstance(entry, dict) else "missing")
                    continue
                payload = str(entry.get("text") or "").encode("utf-8") if isinstance(entry, dict) else b""
                info = tarfile.TarInfo(entry_path.as_posix())
                info.size = len(payload)
                info.mode = int(entry.get("mode") or 0o644) if isinstance(entry, dict) else 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(payload))
        checks.append(runtime_probe_check(f"preparedTarball:{relative.as_posix()}", target.is_file(), f"{relative.as_posix()} prepared with {len(entries)} entrie(s)"))
        if unsafe_entry:
            checks.append(runtime_probe_check(f"preparedTarballEntry:{unsafe_entry}", False, "tarball entry path must be relative and portable"))
    return checks


def prepare_receipt_fixture_copies(root: Path, out_dir: Path, meta: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for item in meta.get("prepareFixtureCopies") or []:
        source_relative = safe_receipt_relative_path(item.get("sourcePath"))
        target_relative = safe_receipt_relative_path(item.get("path"))
        check_id = f"preparedFixtureCopy:{item.get('sourcePath') or 'missing'}->{item.get('path') or 'missing'}"
        if source_relative is None or target_relative is None:
            checks.append(runtime_probe_check(check_id, False, "fixture copy source and target must be relative and stay inside allowed roots"))
            continue
        source = root / source_relative
        target = out_dir / target_relative
        if not source.exists():
            checks.append(runtime_probe_check(check_id, False, f"{source_relative.as_posix()} missing"))
            continue
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(".git", "dist", ".DS_Store", ".cache", "DerivedData", "__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(source, target)
        checks.append(
            runtime_probe_check(
                f"preparedFixtureCopy:{source_relative.as_posix()}->{target_relative.as_posix()}",
                target.exists(),
                f"{source_relative.as_posix()} copied to {target_relative.as_posix()}" if target.exists() else f"{target_relative.as_posix()} missing after copy",
            )
        )
    return checks


def prepare_receipt_codex_cache(root: Path, out_dir: Path, meta: dict[str, Any]) -> Path:
    cache_dir = out_dir / "codex-cache"
    if not meta.get("prepareCodexPluginCache"):
        return cache_dir
    plugin_source = root / "plugins" / "ios-shipguard"
    plugin_json = load_json(plugin_source / ".codex-plugin" / "plugin.json")
    version = str(plugin_json.get("version") or "fixture")
    plugin_dest = cache_dir / "shipguard" / "ios-shipguard" / version
    if plugin_dest.exists():
        shutil.rmtree(plugin_dest)
    plugin_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_source, plugin_dest)
    return cache_dir


def receipt_artifact_checks(artifact_path: Path, artifact: dict[str, Any], *, root: Path, out_dir: Path) -> list[dict[str, Any]]:
    relative = rel(artifact_path, out_dir) if out_dir in artifact_path.parents or artifact_path == out_dir else artifact_path.as_posix()
    kind = str(artifact.get("type") or "")
    checks = [runtime_probe_check(f"artifact:{relative}", artifact_path.is_file(), f"{relative} exists" if artifact_path.is_file() else f"{relative} missing")]
    if not artifact_path.is_file():
        return checks

    if kind == "json":
        loaded = load_json(artifact_path)
        checks.append(runtime_probe_check(f"jsonArtifact:{relative}", bool(loaded), f"{relative} parsed" if loaded else f"{relative} missing or invalid"))
        for key in artifact.get("requiredJsonKeys") or []:
            present = value_at_path(loaded, str(key)) is not None
            checks.append(runtime_probe_check(f"json:{relative}:{key}", present, f"{key} present" if present else f"{key} missing"))
        for key in artifact.get("requiredNonEmptyJsonPaths") or []:
            value = value_at_path(loaded, str(key))
            checks.append(
                runtime_probe_check(
                    f"jsonNonEmpty:{relative}:{key}",
                    is_meaningful_value(value),
                    f"{key} has meaningful content" if is_meaningful_value(value) else f"{key} empty or missing",
                )
            )
        for expected in artifact.get("requiredValues") or []:
            path = str(expected.get("path") or "")
            value = value_at_path(loaded, path)
            equals = expected.get("equals")
            checks.append(
                runtime_probe_check(
                    f"jsonValue:{relative}:{path}",
                    value == equals,
                    f"{path}={value!r}" if value == equals else f"{path} expected {equals!r}, got {value!r}",
                )
            )
    else:
        text = read_text(artifact_path)
        phrases = list(artifact.get("requiredPhrases") or artifact.get("markdownPhrases") or [])
        for phrase in phrases:
            present = str(phrase).lower() in text.lower()
            checks.append(runtime_probe_check(f"text:{relative}:{phrase}", present, f"{phrase!r} present" if present else f"{phrase!r} missing"))
        if artifact.get("forbidLocalPaths"):
            local_path_hit = root.as_posix() in text or ("/" + "Users/") in text or "/private/tmp/" in text
            checks.append(
                runtime_probe_check(
                    f"textShareable:{relative}",
                    not local_path_hit,
                    "no local absolute paths" if not local_path_hit else "local absolute path found",
                )
            )
    return checks


def receipt_artifact_path(raw_path: object, *, out_dir: Path, cache_dir: Path) -> Path:
    artifact_relative = format_receipt_value(raw_path or "", out_dir=out_dir, cache_dir=cache_dir)
    artifact_path = Path(artifact_relative)
    if not artifact_path.is_absolute():
        artifact_path = out_dir / artifact_path
    return artifact_path


def receipt_value_proof_check(proof: dict[str, Any], *, out_dir: Path, cache_dir: Path, check_prefix: str) -> tuple[bool, dict[str, Any] | None]:
    if not proof:
        return False, None
    artifact_path = receipt_artifact_path(proof.get("artifact") or "", out_dir=out_dir, cache_dir=cache_dir)
    loaded = load_json(artifact_path)
    path = str(proof.get("path") or "")
    value = value_at_path(loaded, path)
    passed = False
    if "equals" in proof:
        passed = value == proof.get("equals")
        evidence = f"{path}={value!r}, expected {proof.get('equals')!r}"
    elif "min" in proof:
        try:
            passed = float(value) >= float(proof.get("min"))
        except (TypeError, ValueError):
            passed = False
        evidence = f"{path}={value!r}, expected >= {proof.get('min')!r}"
    else:
        passed = is_meaningful_value(value)
        evidence = f"{path} has meaningful content" if passed else f"{path} missing or empty"
    return passed, runtime_probe_check(f"{check_prefix}:{path}", passed, evidence)


def run_skill_plugin_receipt_command(
    root: Path,
    out_dir: Path,
    cache_dir: Path,
    command_spec: dict[str, Any],
) -> dict[str, Any]:
    prepared_checks = prepare_receipt_files(out_dir, command_spec) + prepare_receipt_tarballs(out_dir, command_spec)
    args = [format_receipt_value(part, out_dir=out_dir, cache_dir=cache_dir) for part in command_spec.get("args") or []]
    started = time.monotonic()
    try:
        env = dict(os.environ, SHIPGUARD_CLI=str(root / "bin" / "shipguard"))
        completed = subprocess.run(
            [str(root / "bin" / "shipguard"), *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=int(command_spec.get("timeoutSeconds") or 60),
            check=False,
            env=env,
        )
        exit_code: int | str = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = "timeout"
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        timed_out = True
    duration_ms = round((time.monotonic() - started) * 1000)
    expected_exit = command_spec.get("expectedExitCode", 0)
    if str(expected_exit) == "nonzero":
        exit_expected = isinstance(exit_code, int) and exit_code != 0
        exit_evidence = f"exit code {exit_code}, expected nonzero"
        exit_check_id = "exitExpected"
    else:
        expected_exit_int = int(expected_exit or 0)
        exit_expected = exit_code == expected_exit_int
        exit_evidence = f"exit code {exit_code}, expected {expected_exit_int}"
        exit_check_id = "exitZero" if expected_exit_int == 0 else "exitExpected"
    checks = prepared_checks + [runtime_probe_check(exit_check_id, exit_expected, exit_evidence)]
    combined_output = f"{stdout}\n{stderr}"
    for phrase in command_spec.get("expectedOutputPhrases") or []:
        present = str(phrase).lower() in combined_output.lower()
        checks.append(runtime_probe_check(f"stdout:{phrase}", present, f"{phrase!r} present" if present else f"{phrase!r} missing"))
    for artifact in command_spec.get("artifacts") or []:
        artifact_path = receipt_artifact_path(artifact.get("path") or "", out_dir=out_dir, cache_dir=cache_dir)
        checks.extend(receipt_artifact_checks(artifact_path, artifact, root=root, out_dir=out_dir))
    proved_blocker, blocker_check = receipt_value_proof_check(
        command_spec.get("blockingProof") if isinstance(command_spec.get("blockingProof"), dict) else {},
        out_dir=out_dir,
        cache_dir=cache_dir,
        check_prefix="blockingProof",
    )
    if blocker_check:
        checks.append(blocker_check)
    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    status = "pass" if score == 100 and exit_expected and not timed_out else "blocked" if not exit_expected or timed_out else "review"
    return {
        "id": str(command_spec.get("id") or "receipt-command"),
        "command": str(command_spec.get("display") or f"./bin/shipguard {' '.join(args)}"),
        "durationMs": duration_ms,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "stdoutLineCount": len(stdout.splitlines()),
        "stderrLineCount": len(stderr.splitlines()),
        "errorSummary": compact_error(stderr or stdout) if not exit_expected or timed_out else "",
        "provedBlocker": proved_blocker,
    }


def receipt_command_blocked(command: dict[str, Any] | None) -> bool:
    if not command:
        return False
    if command.get("provedBlocker") is True and command.get("status") == "pass":
        return True
    exit_code = command.get("exitCode")
    return isinstance(exit_code, int) and exit_code != 0 and command.get("status") == "pass"


def evaluate_remediation_pairs(meta: dict[str, Any], commands: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    command_by_id = {str(command.get("id") or ""): command for command in commands}
    pairs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for item in meta.get("remediationPairs") or []:
        pair_id = str(item.get("id") or "remediation-pair")
        blocked_id = str(item.get("blockedCommandId") or "")
        rerun_id = str(item.get("rerunCommandId") or "")
        repair_ids = [str(value) for value in item.get("repairCommandIds") or []]
        blocked_command = command_by_id.get(blocked_id)
        rerun_command = command_by_id.get(rerun_id)
        repair_commands = [command_by_id.get(command_id) for command_id in repair_ids]
        blocked_passed = receipt_command_blocked(blocked_command)
        repairs_passed = bool(repair_ids) and all(command and command.get("status") == "pass" for command in repair_commands)
        rerun_passed = bool(rerun_command) and rerun_command.get("status") == "pass" and rerun_command.get("exitCode") == 0
        pair_checks = [
            runtime_probe_check(f"remediation:{pair_id}:blocked", blocked_passed, f"{blocked_id} blocked before repair" if blocked_passed else f"{blocked_id} did not prove a blocking failure"),
            runtime_probe_check(f"remediation:{pair_id}:repair", repairs_passed, f"{len(repair_ids)} repair command(s) passed" if repairs_passed else f"{pair_id} repair command(s) missing or failed"),
            runtime_probe_check(f"remediation:{pair_id}:rerun", rerun_passed, f"{rerun_id} passed after repair" if rerun_passed else f"{rerun_id} did not pass after repair"),
        ]
        checks.extend(pair_checks)
        pairs.append(
            {
                "id": pair_id,
                "blockedCommandId": blocked_id,
                "repairCommandIds": repair_ids,
                "rerunCommandId": rerun_id,
                "smallestRepair": str(item.get("smallestRepair") or ""),
                "status": "pass" if all(check["passed"] for check in pair_checks) else "blocked",
                "checks": pair_checks,
                "missing": [check["id"] for check in pair_checks if not check["passed"]],
            }
        )
    return pairs, checks


def run_skill_plugin_receipt(root: Path, fixture_dir: Path, meta: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"shipguard-receipt-{fixture_dir.name}-") as tmp:
        out_dir = Path(tmp)
        prepared_checks = prepare_receipt_files(out_dir, meta) + prepare_receipt_tarballs(out_dir, meta) + prepare_receipt_fixture_copies(root, out_dir, meta)
        cache_dir = prepare_receipt_codex_cache(root, out_dir, meta)
        source_paths = [str(path) for path in meta.get("sourcePaths") or []]
        source_text = "\n".join(read_text(root / path) for path in source_paths)
        source_checks = [
            runtime_probe_check(
                "sourcePaths",
                bool(source_paths) and all((root / path).is_file() for path in source_paths),
                f"{len(source_paths)} source path(s) present",
            ),
            runtime_probe_check("trigger", bool(str(meta.get("trigger") or "").strip()), "trigger present" if meta.get("trigger") else "trigger missing"),
            runtime_probe_check(
                "scopeBoundary",
                (meta.get("scopeBoundary") or {}).get("shipguardOnly") is True and (meta.get("scopeBoundary") or {}).get("targetAppsReadOnly") is True,
                "ShipGuard-only read-only boundary present",
            ),
        ]
        for phrase in meta.get("expectedSourcePhrases") or []:
            present = str(phrase).lower() in source_text.lower()
            source_checks.append(runtime_probe_check(f"source:{phrase}", present, f"{phrase!r} present" if present else f"{phrase!r} missing"))
        commands = [run_skill_plugin_receipt_command(root, out_dir, cache_dir, command) for command in meta.get("commands") or []]
        remediation_pairs, remediation_checks = evaluate_remediation_pairs(meta, commands)
    command_checks = [check for command in commands for check in command.get("checks", [])]
    checks = source_checks + prepared_checks + command_checks + remediation_checks
    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    blocked = any(command.get("status") == "blocked" for command in commands)
    review = any(command.get("status") == "review" for command in commands)
    status = "blocked" if blocked else "review" if review or score < 100 else "pass"
    return {
        "id": str(meta.get("id") or fixture_dir.name),
        "kind": str(meta.get("kind") or "skill-plugin-receipt"),
        "surface": str(meta.get("surface") or meta.get("selectedSkill") or fixture_dir.name),
        "selectedSkill": str(meta.get("selectedSkill") or ""),
        "selectedMode": str(meta.get("selectedMode") or ""),
        "fixturePath": rel(fixture_dir, root),
        "sourcePaths": source_paths,
        "trigger": str(meta.get("trigger") or ""),
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "commands": commands,
        "remediationPairs": remediation_pairs,
        "scopeBoundary": meta.get("scopeBoundary") or {},
    }


def skill_plugin_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_skill_plugin_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public skill/plugin receipt fixtures that prove ShipGuard guidance routes Codex into useful CLI workflows and evidence artifacts.",
        "fixtureRoot": SKILL_PLUGIN_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public skill/plugin receipt fixtures", "fixtures/demo-ios-repo", "synthetic Codex plugin cache"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add end-to-end workflow chain receipts so report-quality questions become spec-workflow tasks and the next slash plan without manual interpretation."
            if status == "pass"
            else "Fix skill/plugin receipt fixtures or guidance so Codex-facing surfaces prove useful runtime workflows."
        ),
    }


def workflow_chain_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_workflow_chain_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public end-to-end workflow receipts that prove report-quality questions become SpecForge tasks, validation commands, slash plans, and the next-goal handoff.",
        "fixtureRoot": WORKFLOW_CHAIN_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public workflow-chain receipt fixtures", "fixtures/demo-ios-repo", "synthetic report-quality output"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add scenario-matrix receipts that execute complete public developer journeys across command families."
            if status == "pass"
            else "Fix workflow-chain receipts so report-quality questions become tasks, proof commands, and slash handoffs without manual interpretation."
        ),
    }


def scenario_matrix_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_scenario_matrix_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public scenario-matrix receipts that prove complete developer journeys across iOS, docs, privacy, CI, plugin, and release surfaces.",
        "fixtureRoot": SCENARIO_MATRIX_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public scenario-matrix receipt fixtures", "fixtures/demo-ios-repo", "synthetic release package", "synthetic Codex plugin cache"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add scenario-failure receipts so complete journeys prove missing proof, unsafe sharing, stale plugin cache, and incomplete release evidence are rejected."
            if status == "pass"
            else "Fix scenario-matrix receipts so complete developer journeys pass before expanding into failure-path proof."
        ),
    }


def scenario_failure_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_scenario_failure_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public scenario-failure receipts that prove ShipGuard blocks unsafe transcripts, broken docs, stale plugin cache, and incomplete release proof with concrete evidence.",
        "fixtureRoot": SCENARIO_FAILURE_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public scenario-failure receipt fixtures", "synthetic unsafe transcript", "synthetic stale plugin cache", "synthetic incomplete release proof"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add scenario-remediation receipts so blocked journeys also prove the smallest repair command and successful rerun."
            if status == "pass"
            else "Fix scenario-failure receipts so bad evidence is blocked with specific machine-readable proof."
        ),
    }


def scenario_remediation_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_scenario_remediation_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    pair_count = sum(len(receipt.get("remediationPairs") or []) for receipt in receipts)
    passed_pair_count = sum(
        1
        for receipt in receipts
        for pair in receipt.get("remediationPairs") or []
        if pair.get("status") == "pass"
    )
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "remediationPairCount": pair_count,
        "passedRemediationPairCount": passed_pair_count,
        "purpose": "Run public scenario-remediation receipts that prove blocked journeys also provide the smallest repair step and a successful rerun.",
        "fixtureRoot": SCENARIO_REMEDIATION_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public scenario-remediation receipt fixtures", "synthetic unsafe transcript", "synthetic broken docs", "synthetic stale plugin cache", "synthetic incomplete release proof"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add adoption receipts so a fresh user journey proves install, plugin refresh, first audit, and next-command handoff from package artifacts."
            if status == "pass"
            else "Fix scenario-remediation receipts so every blocking path also proves the smallest repair step and successful rerun."
        ),
    }


def adoption_expected_exit_check(exit_code: int | str, expected_exit: int | str) -> tuple[str, bool, str]:
    if str(expected_exit) == "nonzero":
        passed = isinstance(exit_code, int) and exit_code != 0
        return ("exitExpected", passed, f"exit code {exit_code}, expected nonzero")
    expected_exit_int = int(expected_exit or 0)
    passed = exit_code == expected_exit_int
    check_id = "exitZero" if expected_exit_int == 0 else "exitExpected"
    return (check_id, passed, f"exit code {exit_code}, expected {expected_exit_int}")


def run_adoption_process(
    *,
    command_id: str,
    display: str,
    command: list[str],
    cwd: Path,
    expected_exit: int | str = 0,
    expected_output_phrases: list[str] | None = None,
    env: dict[str, str] | None = None,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
        exit_code: int | str = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = "timeout"
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        timed_out = True
    duration_ms = round((time.monotonic() - started) * 1000)
    exit_check_id, exit_expected, exit_evidence = adoption_expected_exit_check(exit_code, expected_exit)
    checks = [runtime_probe_check(exit_check_id, exit_expected, exit_evidence)]
    combined_output = f"{stdout}\n{stderr}"
    for phrase in expected_output_phrases or []:
        present = str(phrase).lower() in combined_output.lower()
        checks.append(runtime_probe_check(f"stdout:{phrase}", present, f"{phrase!r} present" if present else f"{phrase!r} missing"))
    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    status = "pass" if score == 100 and exit_expected and not timed_out else "blocked" if not exit_expected or timed_out else "review"
    return {
        "id": command_id,
        "command": display,
        "durationMs": duration_ms,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "stdoutLineCount": len(stdout.splitlines()),
        "stderrLineCount": len(stderr.splitlines()),
        "errorSummary": compact_error(stderr or stdout) if not exit_expected or timed_out else "",
        "stdout": stdout,
        "stderr": stderr,
    }


def public_adoption_command(command: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in command.items() if key not in {"stdout", "stderr"}}


def copy_checkout_for_adoption(root: Path, target: Path) -> None:
    shutil.copytree(
        root,
        target,
        ignore=shutil.ignore_patterns(".git", "dist", ".DS_Store", ".cache", "DerivedData", "__pycache__", "*.pyc"),
    )


def safe_extract_tarball(tarball: Path, extract_dir: Path) -> tuple[bool, str]:
    try:
        extract_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(tarball, "r:gz") as archive:
            for member in archive.getmembers():
                member_path = extract_dir / member.name
                try:
                    member_path.resolve().relative_to(extract_dir.resolve())
                except ValueError:
                    return False, f"unsafe tar member path: {member.name}"
            archive.extractall(extract_dir)
    except (tarfile.TarError, OSError) as exc:
        return False, str(exc)
    return True, "tarball extracted"


def adoption_artifact_checks(root: Path, out_dir: Path, artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for artifact in artifacts:
        artifact_path = Path(format_receipt_value(artifact.get("path") or "", out_dir=out_dir, cache_dir=out_dir))
        if not artifact_path.is_absolute():
            artifact_path = out_dir / artifact_path
        checks.extend(receipt_artifact_checks(artifact_path, artifact, root=root, out_dir=out_dir))
    return checks


def adoption_shareability_checks(out_dir: Path, artifact_paths: list[Path]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    forbidden = [out_dir.as_posix(), "/" + "Users/", "/" + "private/tmp/", "/" + "var/folders/"]
    for artifact_path in artifact_paths:
        relative = rel(artifact_path, out_dir) if artifact_path.exists() else artifact_path.as_posix()
        text = read_text(artifact_path)
        leaked = next((needle for needle in forbidden if needle and needle in text), "")
        checks.append(
            runtime_probe_check(
                f"shareable:{relative}",
                artifact_path.is_file() and not leaked,
                f"{relative} omits local absolute paths" if artifact_path.is_file() and not leaked else f"{relative} leaked {leaked or 'missing file'}",
            )
        )
    return checks


def run_adoption_receipt(root: Path, fixture_dir: Path, meta: dict[str, Any]) -> dict[str, Any]:
    source_paths = [str(path) for path in meta.get("sourcePaths") or []]
    source_text = "\n".join(read_text(root / path) for path in source_paths)
    source_checks = [
        runtime_probe_check(
            "sourcePaths",
            bool(source_paths) and all((root / path).is_file() for path in source_paths),
            f"{len(source_paths)} source path(s) present",
        ),
        runtime_probe_check("trigger", bool(str(meta.get("trigger") or "").strip()), "trigger present" if meta.get("trigger") else "trigger missing"),
        runtime_probe_check(
            "scopeBoundary",
            (meta.get("scopeBoundary") or {}).get("shipguardOnly") is True and (meta.get("scopeBoundary") or {}).get("targetAppsReadOnly") is True,
            "ShipGuard-only read-only boundary present",
        ),
    ]
    for phrase in meta.get("expectedSourcePhrases") or []:
        present = str(phrase).lower() in source_text.lower()
        source_checks.append(runtime_probe_check(f"source:{phrase}", present, f"{phrase!r} present" if present else f"{phrase!r} missing"))

    commands: list[dict[str, Any]] = []
    generated_checks: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix=f"shipguard-adoption-{fixture_dir.name}-") as tmp:
        out_dir = Path(tmp)
        source_copy = out_dir / "source-copy"
        extract_dir = out_dir / "extract"
        prefix = out_dir / "prefix"
        first_audit_dir = out_dir / "first-audit"
        first_quality_dir = out_dir / "first-quality"
        cache_dir = out_dir / "codex-cache"
        copy_checkout_for_adoption(root, source_copy)

        package_command = run_adoption_process(
            command_id="package-from-fresh-copy",
            display="./scripts/package_release.sh from temporary checkout copy",
            command=[str(source_copy / "scripts" / "package_release.sh")],
            cwd=source_copy,
            expected_output_phrases=[f"shipguard-v{read_text(root / 'VERSION').strip()}.tar.gz"],
            timeout_seconds=120,
        )
        commands.append(package_command)
        tarball_lines = [line.strip() for line in str(package_command.get("stdout") or "").splitlines() if line.strip()]
        tarball = Path(tarball_lines[-1]) if tarball_lines else out_dir / "missing.tar.gz"
        version = read_text(source_copy / "VERSION").strip().splitlines()[0]
        package_name = f"shipguard-v{version}"
        generated_checks.append(runtime_probe_check("tarballArtifact", tarball.is_file(), f"{tarball.name} exists" if tarball.is_file() else f"{tarball} missing"))

        extract_ok, extract_evidence = safe_extract_tarball(tarball, extract_dir)
        package_root = extract_dir / package_name
        generated_checks.append(runtime_probe_check("tarballExtracted", extract_ok and package_root.is_dir(), extract_evidence if extract_ok else extract_evidence))
        generated_checks.append(runtime_probe_check("packagedCliPresent", (package_root / "bin" / "shipguard").is_file(), "packaged bin/shipguard present"))

        install_command = run_adoption_process(
            command_id="install-to-temp-prefix",
            display='PREFIX=<temp-prefix> ./scripts/install.sh from extracted package',
            command=["bash", str(package_root / "scripts" / "install.sh")],
            cwd=package_root,
            expected_output_phrases=["installed shipguard to", "installed toolkit files"],
            env=dict(os.environ, PREFIX=prefix.as_posix()),
            timeout_seconds=120,
        )
        commands.append(install_command)
        installed_bin = prefix / "bin" / "shipguard"
        generated_checks.append(runtime_probe_check("installedCliPresent", installed_bin.is_file(), "temp-prefix shipguard wrapper present"))

        version_command = run_adoption_process(
            command_id="installed-version",
            display="shipguard version from temp-prefix install",
            command=[str(installed_bin), "version"],
            cwd=package_root,
            expected_output_phrases=[version],
            timeout_seconds=30,
        )
        commands.append(version_command)

        plugin_source = package_root / "plugins" / "ios-shipguard"
        plugin_json = load_json(plugin_source / ".codex-plugin" / "plugin.json")
        plugin_version = str(plugin_json.get("version") or "fixture")
        plugin_dest = cache_dir / "shipguard" / "ios-shipguard" / plugin_version
        plugin_dest.parent.mkdir(parents=True, exist_ok=True)
        if plugin_dest.exists():
            shutil.rmtree(plugin_dest)
        shutil.copytree(plugin_source, plugin_dest)
        generated_checks.append(runtime_probe_check("freshPluginCachePrepared", (plugin_dest / ".codex-plugin" / "plugin.json").is_file(), "synthetic fresh Codex plugin cache prepared"))

        plugin_status_command = run_adoption_process(
            command_id="fresh-plugin-cache-status",
            display="shipguard codex status --cache <fresh-codex-cache> --strict",
            command=[str(installed_bin), "codex", "status", "--cache", cache_dir.as_posix(), "--strict"],
            cwd=package_root,
            expected_output_phrases=["Overall status: pass", "Installed ios-shipguard plugins: 1", "Refresh Handoff"],
            env=dict(os.environ, SHIPGUARD_CLI=installed_bin.as_posix()),
            timeout_seconds=60,
        )
        commands.append(plugin_status_command)

        first_audit_command = run_adoption_process(
            command_id="first-useful-audit",
            display="shipguard brand --path <extracted-package> --out <first-audit> --strict",
            command=[str(installed_bin), "brand", "--path", package_root.as_posix(), "--out", first_audit_dir.as_posix(), "--strict"],
            cwd=package_root,
            expected_output_phrases=["wrote:", "status: pass"],
            timeout_seconds=60,
        )
        commands.append(first_audit_command)

        report_quality_command = run_adoption_process(
            command_id="next-command-handoff",
            display="shipguard ios report-quality --reports <first-audit> --out <first-quality> --shareable",
            command=[str(installed_bin), "ios", "report-quality", "--reports", first_audit_dir.as_posix(), "--out", first_quality_dir.as_posix(), "--shareable"],
            cwd=package_root,
            expected_output_phrases=["wrote:", "status: pass"],
            timeout_seconds=60,
        )
        commands.append(report_quality_command)

        generated_checks.extend(
            adoption_artifact_checks(
                package_root,
                out_dir,
                [
                    {
                        "path": "first-audit/ios-branding.json",
                        "type": "json",
                        "requiredJsonKeys": ["tool", "status", "surface", "reportQualityQuestions", "surfaces"],
                        "requiredValues": [
                            {"path": "tool", "equals": "shipguard brand"},
                            {"path": "status", "equals": "pass"},
                        ],
                    },
                    {
                        "path": "first-audit/ios-branding.md",
                        "type": "markdown",
                        "requiredPhrases": ["# ShipGuard", "Report Quality Questions", "ShipGuard Brand Deck"],
                    },
                    {
                        "path": "first-quality/ios-report-quality.json",
                        "type": "json",
                        "requiredJsonKeys": ["tool", "status", "priorityAction", "actionabilityQuestions"],
                        "requiredNonEmptyJsonPaths": ["priorityAction", "actionabilityQuestions"],
                        "requiredValues": [
                            {"path": "tool", "equals": "shipguard ios report-quality"},
                            {"path": "status", "equals": "pass"},
                        ],
                    },
                    {
                        "path": "first-quality/ios-report-quality.md",
                        "type": "markdown",
                        "requiredPhrases": ["# iOS ShipGuard Report Quality", "Priority Action", "Actionability Questions", "Shareability mode: `shareable`"],
                    },
                ],
            )
        )
        quality_json = load_json(first_quality_dir / "ios-report-quality.json")
        priority_action = quality_json.get("priorityAction") if isinstance(quality_json.get("priorityAction"), dict) else {}
        generated_checks.append(
            runtime_probe_check(
                "nextCommandActionable",
                bool(priority_action.get("kind")) and bool(priority_action.get("question") or priority_action.get("summary")),
                "priorityAction gives a next command/question" if priority_action else "priorityAction missing",
            )
        )
        generated_checks.extend(
            adoption_shareability_checks(
                out_dir,
                [
                    first_quality_dir / "ios-report-quality.json",
                    first_quality_dir / "ios-report-quality.md",
                ],
            )
        )

    command_checks = [check for command in commands for check in command.get("checks", [])]
    checks = source_checks + command_checks + generated_checks
    score = score_from_checks(checks)
    missing = [check["id"] for check in checks if not check["passed"]]
    blocked = any(command.get("status") == "blocked" for command in commands)
    review = any(command.get("status") == "review" for command in commands)
    status = "blocked" if blocked else "review" if review or score < 100 else "pass"
    return {
        "id": str(meta.get("id") or fixture_dir.name),
        "kind": str(meta.get("kind") or "adoption-receipt"),
        "surface": str(meta.get("surface") or fixture_dir.name),
        "selectedSkill": str(meta.get("selectedSkill") or ""),
        "selectedMode": str(meta.get("selectedMode") or ""),
        "fixturePath": rel(fixture_dir, root),
        "sourcePaths": source_paths,
        "trigger": str(meta.get("trigger") or ""),
        "score": score,
        "status": status,
        "checks": checks,
        "missing": missing,
        "commands": [public_adoption_command(command) for command in commands],
        "scopeBoundary": meta.get("scopeBoundary") or {},
    }


def adoption_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_adoption_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_adoption_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public fresh-user adoption receipts that prove packaged ShipGuard can be installed, paired with a fresh Codex plugin cache, used for a first audit, and routed to a next actionable command.",
        "fixtureRoot": ADOPTION_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["temporary package copy", "extracted release package", "synthetic fresh Codex plugin cache", "public ShipGuard package artifacts"],
        },
        "receipts": receipts,
        "nextAction": (
            "Fresh-user package adoption is passing; inspect targetOnboardingReceipts for fresh target-app onboarding proof before expanding the matrix."
            if status == "pass"
            else "Fix adoption receipts so install, plugin refresh, first audit, and next-command handoff are proven from packaged artifacts."
        ),
    }


def target_onboarding_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_target_onboarding_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public target-onboarding receipts that prove a fresh app repo can receive ShipGuard starter files, pass starter validation, run iOS discovery, and receive a first scoped plan without maintainer context.",
        "fixtureRoot": TARGET_ONBOARDING_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public target-onboarding receipt fixtures", "fixtures/demo-ios-repo copied into a temporary fresh target repo", "starter profile files", "iOS doctor, inventory, and plan artifacts"],
        },
        "receipts": receipts,
        "nextAction": (
            "Target onboarding is passing; inspect multiProfileOnboardingReceipts for starter-profile breadth before expanding into profile-native first audits."
            if status == "pass"
            else "Fix target-onboarding receipts so fresh app onboarding proves starter install, doctor/validate, and first scoped plan."
        ),
    }


def multi_profile_onboarding_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_multi_profile_onboarding_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public multi-profile onboarding receipts that prove iOS, web, backend, and CLI starter profiles each install, pass doctor, and expose first useful commands without maintainer context.",
        "fixtureRoot": MULTI_PROFILE_ONBOARDING_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public multi-profile onboarding receipt fixtures", "starter profile templates", "temporary fresh target repos"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add profile-native first-audit receipts so web, backend, and CLI targets get useful ShipGuard reports beyond init/doctor starter files."
            if status == "pass"
            else "Fix multi-profile onboarding receipts so every starter profile proves init, doctor, and first useful commands from a fresh target repo."
        ),
    }


def profile_native_first_audit_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_profile_native_first_audit_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public profile-native first-audit receipts that prove web, backend, and CLI starter targets get real report commands and report-quality handoff beyond init/doctor.",
        "fixtureRoot": PROFILE_NATIVE_FIRST_AUDIT_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public profile-native first-audit receipt fixtures", "starter profile templates", "temporary fresh target repos", "synthetic web/backend/CLI source signals"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add profile-native fix-plan receipts so web, backend, and CLI first audits become scoped tasks with validation commands."
            if status == "pass"
            else "Fix profile-native first-audit receipts so web, backend, and CLI targets prove useful first reports beyond init/doctor."
        ),
    }


def profile_native_fix_plan_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_profile_native_fix_plan_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public profile-native fix-plan receipts that prove web, backend, and CLI first audits become scoped tasks, validation commands, stop conditions, and report-quality handoff.",
        "fixtureRoot": PROFILE_NATIVE_FIX_PLAN_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public profile-native fix-plan receipt fixtures", "starter profile templates", "temporary fresh target repos", "synthetic web/backend/CLI audit reports"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add profile-native validation receipts so web, backend, and CLI fix plans prove commands can run or block honestly."
            if status == "pass"
            else "Fix profile-native fix-plan receipts so every profile audit produces scoped tasks, validation commands, and report-quality proof."
        ),
    }


def profile_native_validation_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_profile_native_validation_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "purpose": "Run public profile-native validation receipt fixtures that prove WebForge, ServiceForge, and CommandForge classify runnable, blocked, manual, and unchecked validation lanes without executing arbitrary target commands.",
        "fixtureRoot": PROFILE_NATIVE_VALIDATION_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public profile-native validation receipt fixtures", "temporary synthetic target repos", "prepared web/backend/CLI audit reports"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add profile-native validation rerun receipts so blocked validation lanes prove the smallest repair and successful rerun."
            if status == "pass"
            else "Fix profile-native validation receipts so every profile plan proves command availability or blockers honestly."
        ),
    }


def profile_native_validation_rerun_receipt_probe(root: Path) -> dict[str, Any]:
    receipts = [run_skill_plugin_receipt(root, fixture_dir, meta) for fixture_dir, meta in load_profile_native_validation_rerun_receipts(root)]
    passed = sum(1 for receipt in receipts if receipt.get("status") == "pass")
    blocked = sum(1 for receipt in receipts if receipt.get("status") == "blocked")
    review = sum(1 for receipt in receipts if receipt.get("status") == "review")
    command_count = sum(len(receipt.get("commands") or []) for receipt in receipts)
    pair_count = sum(len(receipt.get("remediationPairs") or []) for receipt in receipts)
    passed_pair_count = sum(
        1
        for receipt in receipts
        for pair in receipt.get("remediationPairs") or []
        if pair.get("status") == "pass"
    )
    status = "blocked" if blocked else "review" if review or not receipts else "pass"
    return {
        "status": status,
        "receiptCount": len(receipts),
        "passedReceiptCount": passed,
        "commandCount": command_count,
        "remediationPairCount": pair_count,
        "passedRemediationPairCount": passed_pair_count,
        "purpose": "Run public profile-native validation rerun receipts that prove blocked WebForge, ServiceForge, and CommandForge validation lanes expose the smallest repair and pass after a rerun.",
        "fixtureRoot": PROFILE_NATIVE_VALIDATION_RERUN_RECEIPT_ROOT.as_posix(),
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "inputs": ["public profile-native validation rerun receipt fixtures", "temporary synthetic target repos", "prepared web/backend/CLI audit reports", "fixture-local smallest repairs"],
        },
        "receipts": receipts,
        "nextAction": (
            "Add profile-native proof handoff receipts so repaired plans become copy-ready evidence packets for Codex and maintainers."
            if status == "pass"
            else "Fix profile-native validation rerun receipts so every blocked lane proves the smallest repair and successful rerun."
        ),
    }


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
    runtime_probe: dict[str, Any],
    negative_fixture_probe: dict[str, Any],
    command_family_probe: dict[str, Any],
    skill_plugin_receipts: dict[str, Any],
    workflow_chain_receipts: dict[str, Any],
    scenario_matrix_receipts: dict[str, Any],
    scenario_failure_receipts: dict[str, Any],
    scenario_remediation_receipts: dict[str, Any],
    adoption_receipts: dict[str, Any],
    target_onboarding_receipts: dict[str, Any],
    multi_profile_onboarding_receipts: dict[str, Any],
    profile_native_first_audit_receipts: dict[str, Any],
    profile_native_fix_plan_receipts: dict[str, Any],
    profile_native_validation_receipts: dict[str, Any],
    profile_native_validation_rerun_receipts: dict[str, Any],
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
        runtime_passed = runtime_probe.get("status") == "pass"
        if runtime_passed:
            negative_fixtures_passed = negative_fixture_probe.get("status") == "pass"
            if negative_fixtures_passed:
                command_family_passed = command_family_probe.get("status") == "pass"
                if command_family_passed:
                    skill_plugin_receipts_passed = skill_plugin_receipts.get("status") == "pass"
                    if skill_plugin_receipts_passed:
                        workflow_chain_receipts_passed = workflow_chain_receipts.get("status") == "pass"
                        if workflow_chain_receipts_passed:
                            scenario_matrix_receipts_passed = scenario_matrix_receipts.get("status") == "pass"
                            if scenario_matrix_receipts_passed:
                                scenario_failure_receipts_passed = scenario_failure_receipts.get("status") == "pass"
                                if scenario_failure_receipts_passed:
                                    scenario_remediation_receipts_passed = scenario_remediation_receipts.get("status") == "pass"
                                    if scenario_remediation_receipts_passed:
                                        adoption_receipts_passed = adoption_receipts.get("status") == "pass"
                                        if adoption_receipts_passed:
                                            target_onboarding_receipts_passed = target_onboarding_receipts.get("status") == "pass"
                                            if target_onboarding_receipts_passed:
                                                multi_profile_onboarding_receipts_passed = multi_profile_onboarding_receipts.get("status") == "pass"
                                                if multi_profile_onboarding_receipts_passed:
                                                    profile_native_first_audit_receipts_passed = profile_native_first_audit_receipts.get("status") == "pass"
                                                    if profile_native_first_audit_receipts_passed:
                                                        profile_native_fix_plan_receipts_passed = profile_native_fix_plan_receipts.get("status") == "pass"
                                                        if profile_native_fix_plan_receipts_passed:
                                                            profile_native_validation_receipts_passed = profile_native_validation_receipts.get("status") == "pass"
                                                            if profile_native_validation_receipts_passed:
                                                                profile_native_validation_rerun_receipts_passed = profile_native_validation_rerun_receipts.get("status") == "pass"
                                                                if profile_native_validation_rerun_receipts_passed:
                                                                    answer = surface_probe_row(
                                                                        surface_type="cross-cutting",
                                                                        identifier="shipguard value-gauntlet profile-native-proof-handoff-receipts",
                                                                        name="Profile-native proof handoff receipts",
                                                                        base_score=100,
                                                                        base_status="pass",
                                                                        depth_checks=[
                                                                            depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                                            depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                                            depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                                            depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                                            depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                                            depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                                            depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                                            depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                                            depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                                            depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                                            depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                                            depth_check("runtimeMultiProfileOnboardingReceipts", True, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts executed"),
                                                                            depth_check("runtimeProfileNativeFirstAuditReceipts", True, f"{profile_native_first_audit_receipts.get('passedReceiptCount') or 0}/{profile_native_first_audit_receipts.get('receiptCount') or 0} profile-native first-audit receipts executed"),
                                                                            depth_check("runtimeProfileNativeFixPlanReceipts", True, f"{profile_native_fix_plan_receipts.get('passedReceiptCount') or 0}/{profile_native_fix_plan_receipts.get('receiptCount') or 0} profile-native fix-plan receipts executed"),
                                                                            depth_check("runtimeProfileNativeValidationReceipts", True, f"{profile_native_validation_receipts.get('passedReceiptCount') or 0}/{profile_native_validation_receipts.get('receiptCount') or 0} profile-native validation receipts executed"),
                                                                            depth_check("runtimeProfileNativeValidationRerunReceipts", True, f"{profile_native_validation_rerun_receipts.get('passedRemediationPairCount') or 0}/{profile_native_validation_rerun_receipts.get('remediationPairCount') or 0} validation rerun pairs executed"),
                                                                            depth_check("runtimeProfileNativeProofHandoffReceipts", False, "repaired plans do not yet become copy-ready evidence packets"),
                                                                        ],
                                                                        recommendation="Add profile-native proof handoff receipts so repaired web, backend, and CLI plans become copy-ready evidence packets for Codex and maintainers.",
                                                                        proof="Run value-gauntlet plus focused profile-native proof handoff receipts that turn rerun-clean plans into shareable proof packets.",
                                                                    )
                                                                else:
                                                                    answer = surface_probe_row(
                                                                        surface_type="cross-cutting",
                                                                        identifier="shipguard value-gauntlet profile-native-validation-rerun-receipts",
                                                                        name="Profile-native validation rerun receipts",
                                                                        base_score=100,
                                                                        base_status="pass",
                                                                        depth_checks=[
                                                                            depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                                            depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                                            depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                                            depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                                            depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                                            depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                                            depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                                            depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                                            depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                                            depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                                            depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                                            depth_check("runtimeMultiProfileOnboardingReceipts", True, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts executed"),
                                                                            depth_check("runtimeProfileNativeFirstAuditReceipts", True, f"{profile_native_first_audit_receipts.get('passedReceiptCount') or 0}/{profile_native_first_audit_receipts.get('receiptCount') or 0} profile-native first-audit receipts executed"),
                                                                            depth_check("runtimeProfileNativeFixPlanReceipts", True, f"{profile_native_fix_plan_receipts.get('passedReceiptCount') or 0}/{profile_native_fix_plan_receipts.get('receiptCount') or 0} profile-native fix-plan receipts executed"),
                                                                            depth_check("runtimeProfileNativeValidationReceipts", True, f"{profile_native_validation_receipts.get('passedReceiptCount') or 0}/{profile_native_validation_receipts.get('receiptCount') or 0} profile-native validation receipts executed"),
                                                                            depth_check("runtimeProfileNativeValidationRerunReceipts", False, f"{profile_native_validation_rerun_receipts.get('passedRemediationPairCount') or 0}/{profile_native_validation_rerun_receipts.get('remediationPairCount') or 0} validation rerun pairs passed"),
                                                                        ],
                                                                        recommendation="Add profile-native validation rerun receipts so blocked validation lanes prove the smallest repair and successful rerun.",
                                                                        proof="Run value-gauntlet plus focused profile-native validation rerun receipts that start blocked, repair one target lane, and rerun the plan.",
                                                                    )
                                                            else:
                                                                answer = surface_probe_row(
                                                                    surface_type="cross-cutting",
                                                                    identifier="shipguard value-gauntlet profile-native-validation-receipts",
                                                                    name="Profile-native validation receipts",
                                                                    base_score=100,
                                                                    base_status="pass",
                                                                    depth_checks=[
                                                                        depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                                        depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                                        depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                                        depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                                        depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                                        depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                                        depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                                        depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                                        depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                                        depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                                        depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                                        depth_check("runtimeMultiProfileOnboardingReceipts", True, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts executed"),
                                                                        depth_check("runtimeProfileNativeFirstAuditReceipts", True, f"{profile_native_first_audit_receipts.get('passedReceiptCount') or 0}/{profile_native_first_audit_receipts.get('receiptCount') or 0} profile-native first-audit receipts executed"),
                                                                        depth_check("runtimeProfileNativeFixPlanReceipts", True, f"{profile_native_fix_plan_receipts.get('passedReceiptCount') or 0}/{profile_native_fix_plan_receipts.get('receiptCount') or 0} profile-native fix-plan receipts executed"),
                                                                        depth_check("runtimeProfileNativeValidationReceipts", False, f"{profile_native_validation_receipts.get('passedReceiptCount') or 0}/{profile_native_validation_receipts.get('receiptCount') or 0} profile-native validation receipts passed"),
                                                                    ],
                                                                    recommendation="Add profile-native validation receipts so web, backend, and CLI fix plans prove commands can run or block honestly.",
                                                                    proof="Run value-gauntlet plus focused profile-native validation receipts for web, backend, and CLI synthetic target repos.",
                                                                )
                                                        else:
                                                            answer = surface_probe_row(
                                                                surface_type="cross-cutting",
                                                                identifier="shipguard value-gauntlet profile-native-fix-plan-receipts",
                                                                name="Profile-native fix-plan receipts",
                                                                base_score=100,
                                                                base_status="pass",
                                                                depth_checks=[
                                                                    depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                                    depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                                    depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                                    depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                                    depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                                    depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                                    depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                                    depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                                    depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                                    depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                                    depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                                    depth_check("runtimeMultiProfileOnboardingReceipts", True, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts executed"),
                                                                    depth_check("runtimeProfileNativeFirstAuditReceipts", True, f"{profile_native_first_audit_receipts.get('passedReceiptCount') or 0}/{profile_native_first_audit_receipts.get('receiptCount') or 0} profile-native first-audit receipts executed"),
                                                                    depth_check("runtimeProfileNativeFixPlanReceipts", False, f"{profile_native_fix_plan_receipts.get('passedReceiptCount') or 0}/{profile_native_fix_plan_receipts.get('receiptCount') or 0} profile-native fix-plan receipts passed"),
                                                                ],
                                                                recommendation="Add profile-native fix-plan receipts so web, backend, and CLI first audits become scoped tasks with validation commands.",
                                                                proof="Run value-gauntlet plus focused profile-native fix-plan receipts for web, backend, and CLI synthetic target repos.",
                                                            )
                                                    else:
                                                        answer = surface_probe_row(
                                                            surface_type="cross-cutting",
                                                            identifier="shipguard value-gauntlet profile-native-first-audit-receipts",
                                                            name="Profile-native first-audit receipts",
                                                            base_score=100,
                                                            base_status="pass",
                                                            depth_checks=[
                                                                depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                                depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                                depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                                depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                                depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                                depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                                depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                                depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                                depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                                depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                                depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                                depth_check("runtimeMultiProfileOnboardingReceipts", True, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts executed"),
                                                                depth_check("runtimeProfileNativeFirstAuditReceipts", False, f"{profile_native_first_audit_receipts.get('passedReceiptCount') or 0}/{profile_native_first_audit_receipts.get('receiptCount') or 0} profile-native first-audit receipts passed"),
                                                            ],
                                                            recommendation="Add profile-native first-audit receipts so web, backend, and CLI targets get useful ShipGuard reports beyond init/doctor starter files.",
                                                            proof="Run value-gauntlet plus focused profile-native first-audit receipts for web, backend, and CLI synthetic target repos.",
                                                        )
                                                else:
                                                    answer = surface_probe_row(
                                                        surface_type="cross-cutting",
                                                        identifier="shipguard value-gauntlet multi-profile-onboarding-receipts",
                                                        name="Multi-profile onboarding receipts",
                                                        base_score=100,
                                                        base_status="pass",
                                                        depth_checks=[
                                                            depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                            depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                            depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                            depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                            depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                            depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                            depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                            depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                            depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                            depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                            depth_check("runtimeTargetOnboardingReceipts", True, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts executed"),
                                                            depth_check("runtimeMultiProfileOnboardingReceipts", False, f"{multi_profile_onboarding_receipts.get('passedReceiptCount') or 0}/{multi_profile_onboarding_receipts.get('receiptCount') or 0} multi-profile onboarding receipts passed"),
                                                        ],
                                                        recommendation="Add multi-profile onboarding receipts that prove iOS, web, backend, and CLI starter profiles each install, pass doctor, and name first useful commands without maintainer context.",
                                                        proof="Run value-gauntlet plus focused multi-profile onboarding receipts across public synthetic target repos and starter profiles.",
                                                    )
                                            else:
                                                answer = surface_probe_row(
                                                    surface_type="cross-cutting",
                                                    identifier="shipguard value-gauntlet target-onboarding-receipts",
                                                    name="Fresh target-repo onboarding receipts",
                                                    base_score=100,
                                                    base_status="pass",
                                                    depth_checks=[
                                                        depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                        depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                        depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                        depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                        depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                        depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                        depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                        depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                        depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                        depth_check("runtimeAdoptionReceipts", True, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                        depth_check("runtimeTargetOnboardingReceipts", False, f"{target_onboarding_receipts.get('passedReceiptCount') or 0}/{target_onboarding_receipts.get('receiptCount') or 0} target-onboarding receipts passed"),
                                                    ],
                                                    recommendation="Add target-onboarding receipts that prove a fresh app repo can install starter files, run doctor/validate, and get the first scoped plan without maintainer context.",
                                                    proof="Run value-gauntlet plus focused target-onboarding receipts from a synthetic fresh app repo and packaged ShipGuard install.",
                                                )
                                        else:
                                            answer = surface_probe_row(
                                                surface_type="cross-cutting",
                                                identifier="shipguard value-gauntlet adoption-receipts",
                                                name="Fresh-user adoption receipts",
                                                base_score=100,
                                                base_status="pass",
                                                depth_checks=[
                                                    depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                    depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                    depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                    depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                    depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                    depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                    depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                    depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                    depth_check("runtimeScenarioRemediationReceipts", True, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                                    depth_check("runtimeAdoptionReceipts", False, f"{adoption_receipts.get('passedReceiptCount') or 0}/{adoption_receipts.get('receiptCount') or 0} fresh-user adoption receipts executed"),
                                                ],
                                                recommendation="Add adoption receipts that prove a fresh user can install ShipGuard, refresh the Codex plugin, run the first useful audit, and understand the next command without maintainer context.",
                                                proof="Run value-gauntlet plus focused adoption receipts from packaged artifacts and a synthetic fresh Codex plugin cache.",
                                            )
                                    else:
                                        answer = surface_probe_row(
                                            surface_type="cross-cutting",
                                            identifier="shipguard value-gauntlet scenario-remediation-receipts",
                                            name="Scenario remediation receipts",
                                            base_score=100,
                                            base_status="pass",
                                            depth_checks=[
                                                depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                                depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                                depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                                depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                                depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                                depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                                depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                                depth_check("runtimeScenarioFailureReceipts", True, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts executed"),
                                                depth_check("runtimeScenarioRemediationReceipts", False, f"{scenario_remediation_receipts.get('passedRemediationPairCount') or 0}/{scenario_remediation_receipts.get('remediationPairCount') or 0} remediation pairs executed"),
                                            ],
                                            recommendation="Add scenario-remediation receipts that pair each blocked journey with the smallest repair command and successful rerun proof.",
                                            proof="Run value-gauntlet plus focused remediation receipts for privacy, docs, plugin cache, release proof, and report-quality repair loops.",
                                        )
                                else:
                                    answer = surface_probe_row(
                                        surface_type="cross-cutting",
                                        identifier="shipguard value-gauntlet scenario-failure-receipts",
                                        name="Scenario failure receipts",
                                        base_score=100,
                                        base_status="pass",
                                        depth_checks=[
                                            depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                            depth_check("runtimeOutputProbe", True, f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100"),
                                            depth_check("runtimeRegressionFixtures", True, f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output"),
                                            depth_check("runtimeCommandCoverage", True, f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed"),
                                            depth_check("runtimeSkillPluginReceipts", True, f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed"),
                                            depth_check("runtimeWorkflowChainReceipts", True, f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed"),
                                            depth_check("runtimeScenarioMatrixReceipts", True, f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts executed"),
                                            depth_check("runtimeScenarioFailureReceipts", False, f"{scenario_failure_receipts.get('passedReceiptCount') or 0}/{scenario_failure_receipts.get('receiptCount') or 0} scenario-failure receipts passed"),
                                        ],
                                        recommendation="Add scenario-failure receipts that intentionally feed incomplete or unsafe workflow evidence and require ShipGuard to block with specific guidance.",
                                        proof="Run value-gauntlet plus focused scenario-failure receipt fixtures for privacy, release proof, stale plugin cache, report-quality, and CI evidence failures.",
                                    )
                            else:
                                answer = surface_probe_row(
                                    surface_type="cross-cutting",
                                    identifier="shipguard value-gauntlet scenario-matrix-receipts",
                                    name="Scenario matrix receipts",
                                    base_score=100,
                                    base_status="pass",
                                    depth_checks=[
                                        depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                        depth_check(
                                            "runtimeOutputProbe",
                                            True,
                                            f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100",
                                        ),
                                        depth_check(
                                            "runtimeRegressionFixtures",
                                            True,
                                            f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output",
                                        ),
                                        depth_check(
                                            "runtimeCommandCoverage",
                                            True,
                                            f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed",
                                        ),
                                        depth_check(
                                            "runtimeSkillPluginReceipts",
                                            True,
                                            f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed",
                                        ),
                                        depth_check(
                                            "runtimeWorkflowChainReceipts",
                                            True,
                                            f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts executed",
                                        ),
                                        depth_check(
                                            "runtimeScenarioMatrixReceipts",
                                            False,
                                            f"{scenario_matrix_receipts.get('passedReceiptCount') or 0}/{scenario_matrix_receipts.get('receiptCount') or 0} scenario-matrix receipts passed",
                                        ),
                                    ],
                                    recommendation="Add scenario-matrix receipts that execute full public developer journeys, not only individual commands or one report-quality chain.",
                                    proof="Run value-gauntlet plus focused scenario-matrix receipt fixtures across iOS, release, privacy, CI, plugin, and docs journeys.",
                                )
                        else:
                            answer = surface_probe_row(
                                surface_type="cross-cutting",
                                identifier="shipguard value-gauntlet workflow-chain-receipts",
                                name="Workflow chain receipts",
                                base_score=100,
                                base_status="pass",
                                depth_checks=[
                                    depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                    depth_check(
                                        "runtimeOutputProbe",
                                        True,
                                        f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100",
                                    ),
                                    depth_check(
                                        "runtimeRegressionFixtures",
                                        True,
                                        f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output",
                                    ),
                                    depth_check(
                                        "runtimeCommandCoverage",
                                        True,
                                        f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed",
                                    ),
                                    depth_check(
                                        "runtimeSkillPluginReceipts",
                                        True,
                                        f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts executed",
                                    ),
                                    depth_check(
                                        "runtimeWorkflowChainReceipts",
                                        False,
                                        f"{workflow_chain_receipts.get('passedReceiptCount') or 0}/{workflow_chain_receipts.get('receiptCount') or 0} workflow-chain receipts passed",
                                    ),
                                ],
                                recommendation="Add workflow chain receipts that prove report-quality questions become SpecForge tasks, validation commands, and the next slash plan/goal without manual interpretation.",
                                proof="Run value-gauntlet, report-quality, spec-workflow, next-goal, and focused workflow-chain receipt fixture tests after adding the chain receipts.",
                            )
                    else:
                        answer = surface_probe_row(
                            surface_type="cross-cutting",
                            identifier="shipguard value-gauntlet skill-plugin-runtime-receipts",
                            name="Skill and plugin runtime receipts",
                            base_score=100,
                            base_status="pass",
                            depth_checks=[
                                depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                                depth_check(
                                    "runtimeOutputProbe",
                                    True,
                                    f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100",
                                ),
                                depth_check(
                                    "runtimeRegressionFixtures",
                                    True,
                                    f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output",
                                ),
                                depth_check(
                                    "runtimeCommandCoverage",
                                    True,
                                    f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths executed",
                                ),
                                depth_check(
                                    "runtimeSkillPluginReceipts",
                                    False,
                                    f"{skill_plugin_receipts.get('passedReceiptCount') or 0}/{skill_plugin_receipts.get('receiptCount') or 0} skill/plugin receipts passed",
                                ),
                            ],
                            recommendation="Add skill/plugin runtime receipt fixtures that prove Codex guidance invokes useful ShipGuard workflows, not only static skill prose.",
                            proof="Run value-gauntlet, report-quality, codex status, and focused skill/plugin receipt fixture tests after adding the receipts.",
                        )
                else:
                    answer = surface_probe_row(
                        surface_type="cross-cutting",
                        identifier="shipguard value-gauntlet runtime-command-coverage",
                        name="Runtime command-family coverage",
                        base_score=100,
                        base_status="pass",
                        depth_checks=[
                            depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                            depth_check(
                                "runtimeOutputProbe",
                                True,
                                f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100",
                            ),
                            depth_check(
                                "runtimeRegressionFixtures",
                                True,
                                f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures rejected decorative output",
                            ),
                            depth_check(
                                "runtimeCommandCoverage",
                                False,
                                f"{command_family_probe.get('passedCommandCount') or 0}/{command_family_probe.get('commandCount') or 0} public command help paths passed",
                            ),
                        ],
                        recommendation="Expand runtimeOutputProbe into a broader command-family matrix so every major ShipGuard surface is executed over time, not only statically scored.",
                        proof="Run value-gauntlet, report-quality, and focused command-family probe tests after adding the next command family.",
                    )
            else:
                answer = surface_probe_row(
                    surface_type="cross-cutting",
                    identifier="shipguard value-gauntlet runtime-regression-fixtures",
                    name="Runtime output regression fixtures",
                    base_score=100,
                    base_status="pass",
                    depth_checks=[
                        depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                        depth_check(
                            "runtimeOutputProbe",
                            True,
                            f"{runtime_probe.get('commandCount') or 0} representative runtime outputs scored {runtime_probe.get('averageScore')}/100",
                        ),
                        depth_check(
                            "runtimeRegressionFixtures",
                            False,
                            f"{negative_fixture_probe.get('passedFixtureCount') or 0}/{negative_fixture_probe.get('fixtureCount') or 0} negative runtime-output fixtures passed",
                        ),
                    ],
                    recommendation="Add negative runtime-output fixtures that prove decorative but low-value reports fail the probe before the probe is treated as mature.",
                    proof="Run value-gauntlet, ios report-quality, and a focused runtime-output fixture test after adding the negative cases.",
                )
        else:
            lowest_runtime = runtime_probe.get("lowestScoringCommand") if isinstance(runtime_probe.get("lowestScoringCommand"), dict) else {}
            answer = surface_probe_row(
                surface_type="cross-cutting",
                identifier="shipguard value-gauntlet runtime-output-probe",
                name="Runtime output usefulness probe",
                base_score=100,
                base_status="pass",
                depth_checks=[
                    depth_check("staticSurfaceCoverage", True, f"{len(ranked)} command/skill/plugin/action/doc surfaces passed static depth checks"),
                    depth_check(
                        "runtimeOutputProbe",
                        False,
                        f"runtime output probe status={runtime_probe.get('status') or 'missing'} lowest={lowest_runtime.get('id') or 'unknown'}",
                    ),
                ],
                recommendation="Fix the representative runtime output probe so generated reports are specific, prioritized, proof-oriented, and non-decorative.",
                proof="Run the runtime output probe through `./tests/tool_value_gauntlet_test.sh` and inspect runtimeOutputProbe.lowestScoringCommand.",
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
    runtime_probe = runtime_output_probe(root)
    negative_fixture_probe = runtime_negative_fixture_probe(root)
    command_family_probe = runtime_command_family_probe(root)
    skill_plugin_receipts = skill_plugin_receipt_probe(root)
    workflow_chain_receipts = workflow_chain_receipt_probe(root)
    scenario_matrix_receipts = scenario_matrix_receipt_probe(root)
    scenario_failure_receipts = scenario_failure_receipt_probe(root)
    scenario_remediation_receipts = scenario_remediation_receipt_probe(root)
    adoption_receipts = adoption_receipt_probe(root)
    target_onboarding_receipts = target_onboarding_receipt_probe(root)
    multi_profile_onboarding_receipts = multi_profile_onboarding_receipt_probe(root)
    profile_native_first_audit_receipts = profile_native_first_audit_receipt_probe(root)
    profile_native_fix_plan_receipts = profile_native_fix_plan_receipt_probe(root)
    profile_native_validation_receipts = profile_native_validation_receipt_probe(root)
    profile_native_validation_rerun_receipts = profile_native_validation_rerun_receipt_probe(root)
    probe = lowest_value_surface_probe(
        root,
        text_index,
        commands=commands,
        skills=skills,
        plugins=plugins,
        actions=actions,
        docs=docs,
        runtime_probe=runtime_probe,
        negative_fixture_probe=negative_fixture_probe,
        command_family_probe=command_family_probe,
        skill_plugin_receipts=skill_plugin_receipts,
        workflow_chain_receipts=workflow_chain_receipts,
        scenario_matrix_receipts=scenario_matrix_receipts,
        scenario_failure_receipts=scenario_failure_receipts,
        scenario_remediation_receipts=scenario_remediation_receipts,
        adoption_receipts=adoption_receipts,
        target_onboarding_receipts=target_onboarding_receipts,
        multi_profile_onboarding_receipts=multi_profile_onboarding_receipts,
        profile_native_first_audit_receipts=profile_native_first_audit_receipts,
        profile_native_fix_plan_receipts=profile_native_fix_plan_receipts,
        profile_native_validation_receipts=profile_native_validation_receipts,
        profile_native_validation_rerun_receipts=profile_native_validation_rerun_receipts,
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
        "runtimeOutputProbe": runtime_probe,
        "runtimeOutputNegativeFixtures": negative_fixture_probe,
        "runtimeCommandFamilyCoverage": command_family_probe,
        "skillPluginRuntimeReceipts": skill_plugin_receipts,
        "workflowChainReceipts": workflow_chain_receipts,
        "scenarioMatrixReceipts": scenario_matrix_receipts,
        "scenarioFailureReceipts": scenario_failure_receipts,
        "scenarioRemediationReceipts": scenario_remediation_receipts,
        "adoptionReceipts": adoption_receipts,
        "targetOnboardingReceipts": target_onboarding_receipts,
        "multiProfileOnboardingReceipts": multi_profile_onboarding_receipts,
        "profileNativeFirstAuditReceipts": profile_native_first_audit_receipts,
        "profileNativeFixPlanReceipts": profile_native_fix_plan_receipts,
        "profileNativeValidationReceipts": profile_native_validation_receipts,
        "profileNativeValidationRerunReceipts": profile_native_validation_rerun_receipts,
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
    runtime_probe = report.get("runtimeOutputProbe") or {}
    lines.extend(["", "## Runtime Output Probe", ""])
    lines.append(f"- Status: {runtime_probe.get('status') or 'unknown'}")
    lines.append(f"- Average score: {runtime_probe.get('averageScore', 0)}/100")
    lines.append(f"- Commands executed: {runtime_probe.get('commandCount', 0)}")
    if runtime_probe.get("nextAction"):
        lines.append(f"- Next action: {runtime_probe['nextAction']}")
    lines.extend(["", "| Score | Status | Runtime Command | Output Artifacts | Missing |", "| ---: | --- | --- | --- | --- |"])
    for item in runtime_probe.get("commands", []):
        artifacts = item.get("artifacts") if isinstance(item.get("artifacts"), dict) else {}
        artifact_text = ", ".join(value for value in (artifacts.get("json"), artifacts.get("markdown")) if value)
        lines.append(
            f"| {item.get('score')} | {item.get('status')} | `{table_cell(item.get('command'), 82)}` | {table_cell(artifact_text or '-', 90)} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    negative_probe = report.get("runtimeOutputNegativeFixtures") or {}
    lines.extend(["", "## Runtime Output Negative Fixtures", ""])
    lines.append(f"- Status: {negative_probe.get('status') or 'unknown'}")
    lines.append(f"- Fixtures: {negative_probe.get('passedFixtureCount', 0)}/{negative_probe.get('fixtureCount', 0)} rejected as expected")
    if negative_probe.get("nextAction"):
        lines.append(f"- Next action: {negative_probe['nextAction']}")
    lines.extend(["", "| Fixture | Score | Status | Passed | Expected Missing | Actual Missing |", "| --- | ---: | --- | --- | --- | --- |"])
    for item in negative_probe.get("cases", []):
        lines.append(
            f"| `{table_cell(item.get('fixturePath'), 64)}` | {item.get('score')} | {item.get('status')} | {str(item.get('fixturePassed')).lower()} | {table_cell(', '.join(item.get('expectedMissing') or []) or '-', 90)} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    command_family_probe = report.get("runtimeCommandFamilyCoverage") or {}
    lines.extend(["", "## Runtime Command-Family Coverage", ""])
    lines.append(f"- Status: {command_family_probe.get('status') or 'unknown'}")
    lines.append(f"- Commands: {command_family_probe.get('passedCommandCount', 0)}/{command_family_probe.get('commandCount', 0)} help paths passed")
    if command_family_probe.get("nextAction"):
        lines.append(f"- Next action: {command_family_probe['nextAction']}")
    lines.extend(["", "| Family | Commands | Pass | Review | Blocked |", "| --- | ---: | ---: | ---: | ---: |"])
    families = command_family_probe.get("families") if isinstance(command_family_probe.get("families"), dict) else {}
    for family in sorted(families):
        item = families[family]
        lines.append(
            f"| {family} | {item.get('commandCount', 0)} | {item.get('passCount', 0)} | {item.get('reviewCount', 0)} | {item.get('blockedCount', 0)} |"
        )
    failing_commands = [item for item in command_family_probe.get("commands", []) if item.get("status") != "pass"]
    if failing_commands:
        lines.extend(["", "| Status | Command | Missing | Error |", "| --- | --- | --- | --- |"])
        for item in failing_commands[:20]:
            lines.append(
                f"| {item.get('status')} | `{table_cell(item.get('command'), 80)}` | {table_cell(', '.join(item.get('missing') or []) or '-', 80)} | {table_cell(item.get('errorSummary') or '-', 90)} |"
            )
    skill_plugin_receipts = report.get("skillPluginRuntimeReceipts") or {}
    lines.extend(["", "## Skill/Plugin Runtime Receipts", ""])
    lines.append(f"- Status: {skill_plugin_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {skill_plugin_receipts.get('passedReceiptCount', 0)}/{skill_plugin_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {skill_plugin_receipts.get('commandCount', 0)}")
    if skill_plugin_receipts.get("nextAction"):
        lines.append(f"- Next action: {skill_plugin_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in skill_plugin_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_receipt_commands = [
        (receipt, command)
        for receipt in skill_plugin_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_receipt_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_receipt_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    workflow_chain_receipts = report.get("workflowChainReceipts") or {}
    lines.extend(["", "## Workflow Chain Receipts", ""])
    lines.append(f"- Status: {workflow_chain_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {workflow_chain_receipts.get('passedReceiptCount', 0)}/{workflow_chain_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {workflow_chain_receipts.get('commandCount', 0)}")
    if workflow_chain_receipts.get("nextAction"):
        lines.append(f"- Next action: {workflow_chain_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in workflow_chain_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_workflow_commands = [
        (receipt, command)
        for receipt in workflow_chain_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_workflow_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_workflow_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    scenario_matrix_receipts = report.get("scenarioMatrixReceipts") or {}
    lines.extend(["", "## Scenario Matrix Receipts", ""])
    lines.append(f"- Status: {scenario_matrix_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {scenario_matrix_receipts.get('passedReceiptCount', 0)}/{scenario_matrix_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {scenario_matrix_receipts.get('commandCount', 0)}")
    if scenario_matrix_receipts.get("nextAction"):
        lines.append(f"- Next action: {scenario_matrix_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in scenario_matrix_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_scenario_commands = [
        (receipt, command)
        for receipt in scenario_matrix_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_scenario_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_scenario_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    scenario_failure_receipts = report.get("scenarioFailureReceipts") or {}
    lines.extend(["", "## Scenario Failure Receipts", ""])
    lines.append(f"- Status: {scenario_failure_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {scenario_failure_receipts.get('passedReceiptCount', 0)}/{scenario_failure_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {scenario_failure_receipts.get('commandCount', 0)}")
    if scenario_failure_receipts.get("nextAction"):
        lines.append(f"- Next action: {scenario_failure_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in scenario_failure_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_failure_commands = [
        (receipt, command)
        for receipt in scenario_failure_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_failure_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_failure_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    scenario_remediation_receipts = report.get("scenarioRemediationReceipts") or {}
    lines.extend(["", "## Scenario Remediation Receipts", ""])
    lines.append(f"- Status: {scenario_remediation_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {scenario_remediation_receipts.get('passedReceiptCount', 0)}/{scenario_remediation_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {scenario_remediation_receipts.get('commandCount', 0)}")
    lines.append(f"- Remediation pairs: {scenario_remediation_receipts.get('passedRemediationPairCount', 0)}/{scenario_remediation_receipts.get('remediationPairCount', 0)} passed")
    if scenario_remediation_receipts.get("nextAction"):
        lines.append(f"- Next action: {scenario_remediation_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Pairs | Missing |", "| --- | ---: | --- | --- | ---: | ---: | --- |"])
    for item in scenario_remediation_receipts.get("receipts", []):
        passed_pairs = sum(1 for pair in item.get("remediationPairs") or [] if pair.get("status") == "pass")
        pair_count = len(item.get("remediationPairs") or [])
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {passed_pairs}/{pair_count} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    remediation_pairs = [
        (receipt, pair)
        for receipt in scenario_remediation_receipts.get("receipts", [])
        for pair in receipt.get("remediationPairs", [])
    ]
    if remediation_pairs:
        lines.extend(["", "| Receipt | Pair | Status | Blocked | Repair | Rerun |", "| --- | --- | --- | --- | --- | --- |"])
        for receipt, pair in remediation_pairs[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | `{table_cell(pair.get('id'), 40)}` | {pair.get('status')} | `{table_cell(pair.get('blockedCommandId'), 40)}` | {table_cell(', '.join(pair.get('repairCommandIds') or []) or '-', 70)} | `{table_cell(pair.get('rerunCommandId'), 40)}` |"
            )
    failing_remediation_commands = [
        (receipt, command)
        for receipt in scenario_remediation_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_remediation_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_remediation_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    adoption_receipts = report.get("adoptionReceipts") or {}
    lines.extend(["", "## Fresh-User Adoption Receipts", ""])
    lines.append(f"- Status: {adoption_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {adoption_receipts.get('passedReceiptCount', 0)}/{adoption_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {adoption_receipts.get('commandCount', 0)}")
    if adoption_receipts.get("nextAction"):
        lines.append(f"- Next action: {adoption_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in adoption_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_adoption_commands = [
        (receipt, command)
        for receipt in adoption_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_adoption_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_adoption_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    target_onboarding_receipts = report.get("targetOnboardingReceipts") or {}
    lines.extend(["", "## Target Onboarding Receipts", ""])
    lines.append(f"- Status: {target_onboarding_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {target_onboarding_receipts.get('passedReceiptCount', 0)}/{target_onboarding_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {target_onboarding_receipts.get('commandCount', 0)}")
    if target_onboarding_receipts.get("nextAction"):
        lines.append(f"- Next action: {target_onboarding_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in target_onboarding_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_target_onboarding_commands = [
        (receipt, command)
        for receipt in target_onboarding_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_target_onboarding_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_target_onboarding_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    multi_profile_onboarding_receipts = report.get("multiProfileOnboardingReceipts") or {}
    lines.extend(["", "## Multi-Profile Onboarding Receipts", ""])
    lines.append(f"- Status: {multi_profile_onboarding_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {multi_profile_onboarding_receipts.get('passedReceiptCount', 0)}/{multi_profile_onboarding_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {multi_profile_onboarding_receipts.get('commandCount', 0)}")
    if multi_profile_onboarding_receipts.get("nextAction"):
        lines.append(f"- Next action: {multi_profile_onboarding_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in multi_profile_onboarding_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_multi_profile_onboarding_commands = [
        (receipt, command)
        for receipt in multi_profile_onboarding_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_multi_profile_onboarding_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_multi_profile_onboarding_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    profile_native_first_audit_receipts = report.get("profileNativeFirstAuditReceipts") or {}
    lines.extend(["", "## Profile-Native First-Audit Receipts", ""])
    lines.append(f"- Status: {profile_native_first_audit_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {profile_native_first_audit_receipts.get('passedReceiptCount', 0)}/{profile_native_first_audit_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {profile_native_first_audit_receipts.get('commandCount', 0)}")
    if profile_native_first_audit_receipts.get("nextAction"):
        lines.append(f"- Next action: {profile_native_first_audit_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in profile_native_first_audit_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_profile_native_first_audit_commands = [
        (receipt, command)
        for receipt in profile_native_first_audit_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_profile_native_first_audit_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_profile_native_first_audit_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    profile_native_fix_plan_receipts = report.get("profileNativeFixPlanReceipts") or {}
    lines.extend(["", "## Profile-Native Fix-Plan Receipts", ""])
    lines.append(f"- Status: {profile_native_fix_plan_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {profile_native_fix_plan_receipts.get('passedReceiptCount', 0)}/{profile_native_fix_plan_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {profile_native_fix_plan_receipts.get('commandCount', 0)}")
    if profile_native_fix_plan_receipts.get("nextAction"):
        lines.append(f"- Next action: {profile_native_fix_plan_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in profile_native_fix_plan_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 32)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_profile_native_fix_plan_commands = [
        (receipt, command)
        for receipt in profile_native_fix_plan_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_profile_native_fix_plan_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_profile_native_fix_plan_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    profile_native_validation_receipts = report.get("profileNativeValidationReceipts") or {}
    lines.extend(["", "## Profile-Native Validation Receipts", ""])
    lines.append(f"- Status: {profile_native_validation_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {profile_native_validation_receipts.get('passedReceiptCount', 0)}/{profile_native_validation_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {profile_native_validation_receipts.get('commandCount', 0)}")
    if profile_native_validation_receipts.get("nextAction"):
        lines.append(f"- Next action: {profile_native_validation_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Missing |", "| --- | ---: | --- | --- | ---: | --- |"])
    for item in profile_native_validation_receipts.get("receipts", []):
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 40)} | {len(item.get('commands') or [])} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    failing_profile_native_validation_commands = [
        (receipt, command)
        for receipt in profile_native_validation_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_profile_native_validation_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_profile_native_validation_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
    profile_native_validation_rerun_receipts = report.get("profileNativeValidationRerunReceipts") or {}
    lines.extend(["", "## Profile-Native Validation Rerun Receipts", ""])
    lines.append(f"- Status: {profile_native_validation_rerun_receipts.get('status') or 'unknown'}")
    lines.append(f"- Receipts: {profile_native_validation_rerun_receipts.get('passedReceiptCount', 0)}/{profile_native_validation_rerun_receipts.get('receiptCount', 0)} passed")
    lines.append(f"- Commands executed: {profile_native_validation_rerun_receipts.get('commandCount', 0)}")
    lines.append(f"- Repair/rerun pairs: {profile_native_validation_rerun_receipts.get('passedRemediationPairCount', 0)}/{profile_native_validation_rerun_receipts.get('remediationPairCount', 0)} passed")
    if profile_native_validation_rerun_receipts.get("nextAction"):
        lines.append(f"- Next action: {profile_native_validation_rerun_receipts['nextAction']}")
    lines.extend(["", "| Status | Score | Receipt | Kind | Commands | Pairs | Missing |", "| --- | ---: | --- | --- | ---: | ---: | --- |"])
    for item in profile_native_validation_rerun_receipts.get("receipts", []):
        passed_pairs = sum(1 for pair in item.get("remediationPairs") or [] if pair.get("status") == "pass")
        pair_count = len(item.get("remediationPairs") or [])
        lines.append(
            f"| {item.get('status')} | {item.get('score')} | `{table_cell(item.get('id'), 64)}` | {table_cell(item.get('kind'), 44)} | {len(item.get('commands') or [])} | {passed_pairs}/{pair_count} | {table_cell(', '.join(item.get('missing') or []) or '-', 90)} |"
        )
    rerun_pairs = [
        (receipt, pair)
        for receipt in profile_native_validation_rerun_receipts.get("receipts", [])
        for pair in receipt.get("remediationPairs", [])
    ]
    if rerun_pairs:
        lines.extend(["", "| Receipt | Pair | Status | Blocked | Repair | Rerun |", "| --- | --- | --- | --- | --- | --- |"])
        for receipt, pair in rerun_pairs[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | `{table_cell(pair.get('id'), 40)}` | {pair.get('status')} | `{table_cell(pair.get('blockedCommandId'), 40)}` | {table_cell(', '.join(pair.get('repairCommandIds') or []) or '-', 70)} | `{table_cell(pair.get('rerunCommandId'), 40)}` |"
            )
    failing_profile_native_validation_rerun_commands = [
        (receipt, command)
        for receipt in profile_native_validation_rerun_receipts.get("receipts", [])
        for command in receipt.get("commands", [])
        if command.get("status") != "pass"
    ]
    if failing_profile_native_validation_rerun_commands:
        lines.extend(["", "| Receipt | Status | Command | Missing | Error |", "| --- | --- | --- | --- | --- |"])
        for receipt, command in failing_profile_native_validation_rerun_commands[:20]:
            lines.append(
                f"| `{table_cell(receipt.get('id'), 52)}` | {command.get('status')} | `{table_cell(command.get('command'), 80)}` | {table_cell(', '.join(command.get('missing') or []) or '-', 80)} | {table_cell(command.get('errorSummary') or '-', 90)} |"
            )
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
