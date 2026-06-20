#!/usr/bin/env python3
"""Audit external workflow projects as ShipGuard-native integration decisions."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import ios_scan_scope


SCHEMA_VERSION = 1
TOOL = "shipguard ios external-audit"
SOURCE_SUFFIXES = {".md", ".json", ".toml", ".yml", ".yaml", ".ts", ".js", ".mjs", ".py"}

SOURCE_PROFILES: dict[str, dict[str, Any]] = {
    "spec-kit": {
        "displayName": "GitHub Spec Kit",
        "canonicalUrl": "https://github.com/github/spec-kit",
        "license": "MIT",
        "signals": ["spec-kit", "specify-cli", "speckit", "spec-driven", "constitution-template.md"],
        "capabilities": [
            {
                "id": "speckit-sdd-cycle",
                "name": "Spec-driven development cycle",
                "externalSignal": "constitution -> specify -> clarify -> checklist -> plan -> tasks -> analyze -> implement",
                "currentShipGuardSurface": "ios spec-workflow, requirements-checklist.md, consistency-analysis.md, tasks.md, report-quality gates",
                "decision": "replace-weaker-guidance",
                "replacement": "Replace static planning advice with generated ShipGuard artifacts that are scored by report-quality.",
                "nativeAction": "Keep spec-workflow as the native implementation, and require exact validation commands plus proof gates before implementation.",
                "validation": "./tests/ios_spec_workflow_test.sh && ./tests/ios_report_quality_test.sh",
            },
            {
                "id": "speckit-checklists-unit-tests",
                "name": "Checklist as unit tests for requirements",
                "externalSignal": "checklists validate requirements quality rather than implementation behavior",
                "currentShipGuardSurface": "requirements-checklist.md and spec-workflow checklist coverage checks",
                "decision": "extend-native",
                "replacement": "Extend checklist output so each item maps to completeness, clarity, coverage, proof, safety, or traceability.",
                "nativeAction": "Emit checklist entries with expected evidence and make report-quality fail weak or placeholder checklist artifacts.",
                "validation": "./tests/ios_spec_workflow_test.sh",
            },
            {
                "id": "speckit-extension-preset-stack",
                "name": "Extension and preset stack",
                "externalSignal": "project-local overrides, presets, extensions, and core templates resolved by priority",
                "currentShipGuardSurface": "policy profiles, plugin skill guidance, command matrix, and future app-type packs",
                "decision": "defer-with-native-plan",
                "replacement": "Do not copy Spec Kit's installer or template stack; create ShipGuard app-type packs only after command/report contracts are stable.",
                "nativeAction": "Track as a future ShipGuard source-pack layer for iOS genres, proof styles, and release policies.",
                "validation": "Future: public fixture plus ./bin/shipguard ios external-audit --shareable",
            },
            {
                "id": "speckit-converge-analysis",
                "name": "Converge and cross-artifact analysis",
                "externalSignal": "non-destructive consistency analysis across spec, plan, and tasks",
                "currentShipGuardSurface": "consistency-analysis.md and report-quality artifact coverage checks",
                "decision": "extend-native",
                "replacement": "Make consistency analysis a generated artifact and report-quality target rather than a free-form prompt.",
                "nativeAction": "Keep checking question coverage across clarifying questions, acceptance criteria, tasks, validation, and analysis gates.",
                "validation": "./tests/ios_spec_workflow_test.sh",
            },
        ],
    },
    "codexpro": {
        "displayName": "CodexPro",
        "canonicalUrl": "https://github.com/rebel0789/codexpro",
        "license": "MIT",
        "signals": ["codexpro", "CODEXPRO_", "codexpro_token", ".ai-bridge", "ChatGPT Developer Mode"],
        "capabilities": [
            {
                "id": "codexpro-local-bridge",
                "name": "ChatGPT local repo bridge",
                "externalSignal": "MCP/App bridge exposes repo tools to ChatGPT with tool modes",
                "currentShipGuardSurface": "ios devspace, ios devspace-check, preview widget resource, codex_prepare_handoff",
                "decision": "keep-current-with-extensions",
                "replacement": "Keep ShipGuard narrower than a general remote editing bridge because iOS release proof needs stronger boundaries.",
                "nativeAction": "Use Devspace for visual planning and handoff only; route trusted edits through local Codex handoff commands.",
                "validation": "./tests/ios_devspace_check_test.sh",
            },
            {
                "id": "codexpro-path-guard",
                "name": "Workspace path and secret guards",
                "externalSignal": "allowed roots, blocked globs, symlink escape checks, token-protected tunnels",
                "currentShipGuardSurface": "devspace-check public URL/token checks, ios redact, report-quality token/path shareability checks",
                "decision": "replace-weaker-guidance",
                "replacement": "Replace scattered bridge safety docs with scored connector-readiness findings and redaction commands.",
                "nativeAction": "Keep adding report-quality checks for token-bearing URLs, local paths, screenshot tokens, and unsafe handoff execution.",
                "validation": "./tests/ios_devspace_check_test.sh && ./tests/ios_report_quality_test.sh",
            },
            {
                "id": "codexpro-visual-cards",
                "name": "Compact visual cards",
                "externalSignal": "high-signal tools attach widget resources; plumbing tools stay data-only",
                "currentShipGuardSurface": "ios preview, ios target-match, devspace widget, handoff.md, report-quality summaries",
                "decision": "extend-native",
                "replacement": "Keep ShipGuard visual output receipt-based instead of turning every tool call into UI.",
                "nativeAction": "Use preview receipts, semantic target matching, and concise report sections as the native visual planning surface.",
                "validation": "./tests/ios_devspace_check_test.sh",
            },
            {
                "id": "codexpro-handoff-watcher",
                "name": "Local-only handoff execution watcher",
                "externalSignal": "watcher executes .ai-bridge/current-plan.md only from a user-started terminal",
                "currentShipGuardSurface": "ios codex-handoff --execute and Devspace codex_prepare_handoff",
                "decision": "defer-with-native-plan",
                "replacement": "Do not add a background watcher until ShipGuard has explicit approval, sandbox, duplicate-run, and audit-log controls.",
                "nativeAction": "Keep execution explicit and local for now; use this audit as the guardrail for any future watcher.",
                "validation": "Future: handoff watcher fixture plus security threat-model update",
            },
        ],
    },
    "expo": {
        "displayName": "Expo",
        "canonicalUrl": "https://github.com/expo/expo",
        "license": "MIT",
        "signals": ["expo", "Expo Application Services", "EAS", "packages", "templates", "docs.expo.dev", "universal native apps"],
        "capabilities": [
            {
                "id": "expo-oss-product-surface",
                "name": "Open-source product surface",
                "externalSignal": "docs, CLI, templates, package layout, examples, support, contribution lanes, release proof",
                "currentShipGuardSurface": "README, docs, command matrix, fixtures, package release proof, GitHub Actions examples",
                "decision": "extend-native",
                "replacement": "Replace private-app-helper positioning with a public ShipGuard product surface and package proof.",
                "nativeAction": "Keep ShipGuard fully open-source while documenting its Codex/iOS workflow contract and contribution lanes.",
                "validation": "./tests/package_release_test.sh && ./bin/shipguard docs-check . --out /tmp/shipguard-docs-check",
            },
            {
                "id": "expo-docs-community-surface",
                "name": "Documentation and community surface",
                "externalSignal": "central docs, getting-started links, support/community routing, contribution guide, license, and security surfaces",
                "currentShipGuardSurface": "docs/index.md, docs/open-source.md, CONTRIBUTING.md, SUPPORT.md, SECURITY.md, issue templates, command matrix",
                "decision": "extend-native",
                "replacement": "Make ShipGuard approachable as a public tool instead of a private workflow dump.",
                "nativeAction": "Keep docs, support, contribution, security, and command discovery surfaces complete and package-validated.",
                "validation": "./bin/shipguard docs-check . --out /tmp/shipguard-docs-check && ./tests/self_audit_test.sh",
            },
            {
                "id": "expo-build-ship-iterate-loop",
                "name": "Build, ship, and iterate loop",
                "externalSignal": "open-source tools plus integrated hosted services for building, shipping, and iterating",
                "currentShipGuardSurface": "release proof, release evidence, package release tests, codex status, next-goal loop",
                "decision": "integrate-by-routing",
                "replacement": "Do not create hosted services; route ShipGuard-native release proof and plugin refresh through local CLI evidence.",
                "nativeAction": "Keep release/package/plugin proof as the ShipGuard equivalent of a build/ship/iterate loop for Codex workflows.",
                "validation": "./tests/package_release_test.sh && ./bin/shipguard codex status --strict",
            },
            {
                "id": "expo-template-and-module-ecosystem",
                "name": "Template and module ecosystem",
                "externalSignal": "templates, packages, app examples, and native module contribution paths",
                "currentShipGuardSurface": "starter profiles, fixtures, skills, plugin source, and future command packs",
                "decision": "defer-with-native-plan",
                "replacement": "Do not adopt React Native monorepo/package architecture; build ShipGuard-native iOS proof packs instead.",
                "nativeAction": "Use Expo as an OSS maturity benchmark, not as ShipGuard's architecture.",
                "validation": "Future: package fixture that installs a ShipGuard iOS proof pack from source.",
            },
        ],
    },
    "design-motion-principles": {
        "displayName": "Design Motion Principles",
        "canonicalUrl": "local Codex skill: design-motion-principles",
        "license": "local skill instructions; attribution required for named influences",
        "signals": [
            "design-motion-principles",
            "The Frequency Gate",
            "Emil Kowalski",
            "Jakub Krehel",
            "Jhey Tompkins",
            "prefers-reduced-motion",
            "AI-Slop Motion Patterns",
            "Motion Gap Analysis",
        ],
        "capabilities": [
            {
                "id": "motion-frequency-context-gate",
                "name": "Context-weighted frequency gate",
                "externalSignal": "rare interactions may delight; frequent and keyboard-triggered interactions should be instant or restrained",
                "currentShipGuardSurface": "ios design motionBlueprint and motionQualityGates",
                "decision": "replace-weaker-guidance",
                "replacement": "Replace generic animation tips with app-type-weighted motion doctrine inside ios design.",
                "nativeAction": "Emit ShipGuard-native frequency, purpose, keyboard, reduced-motion, performance, and anti-slop gates by app type.",
                "validation": "./tests/ios_design_test.sh && ./tests/ios_external_audit_test.sh",
            },
            {
                "id": "motion-anti-slop-audit",
                "name": "AI-slop motion audit",
                "externalSignal": "flag pulsing indicators, blur-everywhere entrances, hover/scale spam, stagger spam, bounce on utility controls, and static-content entrance motion",
                "currentShipGuardSurface": "ios design findings, performance scanner repeated-animation rules, report-quality fixture candidates",
                "decision": "extend-native",
                "replacement": "Keep the taxonomy but express findings as ShipGuard report data instead of a separate branded HTML audit.",
                "nativeAction": "Surface anti-slop checks as motion quality gates and future public iOS fixture cases.",
                "validation": "./tests/ios_design_test.sh && ./tests/ios_report_quality_test.sh",
            },
            {
                "id": "motion-accessibility-performance-gates",
                "name": "Motion accessibility and performance gates",
                "externalSignal": "prefers-reduced-motion is mandatory; transform/opacity preferred; will-change must be sparse; looping motion needs pause/proof",
                "currentShipGuardSurface": "ios design reduced-motion findings, ios performance continuous-animation rules, local/manual proof fields",
                "decision": "extend-native",
                "replacement": "Make accessibility and performance proof part of ShipGuard reports rather than optional design advice.",
                "nativeAction": "Require reduced-motion evidence, physical-device haptic proof, and profiler/device proof before motion quality claims.",
                "validation": "./tests/ios_design_test.sh && ./tests/ios_performance_test.sh",
            },
        ],
    },
    "ponytail": {
        "displayName": "Ponytail",
        "canonicalUrl": "https://github.com/DietrichGebert/ponytail",
        "license": "MIT",
        "signals": [
            "ponytail",
            "lazy senior developer",
            "best code is the code never written",
            "Does this need to be built at all",
            "Does the standard library already do this",
            "Native platform feature",
            "ponytail-review",
            "ponytail-audit",
            "ponytail-debt",
            "ponytail-gain",
        ],
        "capabilities": [
            {
                "id": "ponytail-lean-ladder",
                "name": "Precise-code decision ladder",
                "externalSignal": "YAGNI -> stdlib -> native platform -> installed dependency -> one line -> minimum code",
                "currentShipGuardSurface": "lean audit, lean review, --mode lite/full/ultra, precisionReview, nativeOpportunityCatalog, behaviorGates",
                "decision": "replace-weaker-guidance",
                "replacement": "Replace generic 'write less code' advice with ShipGuard-native delete/simplify/keep/proof-blocked report data.",
                "nativeAction": "Keep Lean Deck as the native precise-code engine, expose lite/full/ultra intensity, and require safety, adapter, hardware, requested-explanation, and one-check gates before deletion.",
                "validation": "./tests/lean_audit_test.sh && ./tests/ios_external_audit_test.sh",
            },
            {
                "id": "ponytail-diff-review",
                "name": "Diff-only over-engineering review",
                "externalSignal": "ponytail-review returns one-line delete, stdlib, native, yagni, and shrink findings for the current diff",
                "currentShipGuardSurface": "lean review, reviewLines, precisionReview.topActions",
                "decision": "extend-native",
                "replacement": "Keep the one-line review style, but add ShipGuard proof guidance and safety-boundary warnings.",
                "nativeAction": "Use `shipguard lean review --diff <patch>` before merge and feed the result to report-quality when improving ShipGuard.",
                "validation": "./tests/lean_audit_test.sh && ./tests/ios_report_quality_test.sh",
            },
            {
                "id": "ponytail-shortcut-ledger",
                "name": "Intentional shortcut debt ledger",
                "externalSignal": "ponytail: comments record deliberate shortcuts and upgrade paths",
                "currentShipGuardSurface": "lean debt, leanDebtLedger, shipguard-lean markers",
                "decision": "extend-native",
                "replacement": "Support both `ponytail:` and ShipGuard-owned `shipguard-lean:` markers, and require ceilings plus upgrade triggers.",
                "nativeAction": "Use `shipguard lean debt` to keep precise-code shortcuts visible instead of letting deferrals rot.",
                "validation": "./tests/lean_audit_test.sh",
            },
            {
                "id": "ponytail-benchmark-honesty",
                "name": "Benchmark-honest gain card",
                "externalSignal": "benchmark impact is useful direction but not a per-repo savings claim",
                "currentShipGuardSurface": "lean gain, benchmarkScoreboard, currentRepoBoundary",
                "decision": "extend-native",
                "replacement": "Report public benchmark direction while explicitly marking current-repo savings as not computed.",
                "nativeAction": "Keep `shipguard lean gain` as an honesty gate for launch claims about code, token, cost, or time savings.",
                "validation": "./tests/lean_audit_test.sh && ./tests/tool_value_gauntlet_test.sh",
            },
            {
                "id": "ponytail-always-on-host-mode",
                "name": "Always-on host activation",
                "externalSignal": "Codex/Claude lifecycle hooks inject Ponytail mode and track lite/full/ultra/off state",
                "currentShipGuardSurface": "Codex plugin skill routing, Lean Deck commands, codex status",
                "decision": "integrate-by-routing",
                "replacement": "Do not make ShipGuard a global terse-mode hook; route precise-code requests to explicit Lean Deck proof reports.",
                "nativeAction": "Keep Ponytail available as a separate Codex plugin if desired, and keep ShipGuard's native integration reportable, testable, and opt-in per command.",
                "validation": "codex plugin list && ./bin/shipguard codex status --strict",
            },
        ],
    },
    "openai-ios-workflow": {
        "displayName": "LaunchDeck / OpenAI Native iOS Workflow",
        "canonicalUrl": "local Codex skill/plugin surface",
        "license": "not vendored",
        "signals": ["ios-simulator-browser", "SwiftUI preview", "hot reload", "XcodeBuildMCP"],
        "capabilities": [
            {
                "id": "native-ios-preview-loop",
                "name": "Native iOS preview and simulator loop",
                "externalSignal": "simulator browser, SwiftUI preview, XcodeBuildMCP, hot-reload style feedback",
                "currentShipGuardSurface": "ios preview, target-match, devspace, devspace-check, report-quality proof routing",
                "decision": "integrate-by-routing",
                "replacement": "Do not pretend ShipGuard owns the renderer; route to native iOS tools and capture ShipGuard receipts around them.",
                "nativeAction": "Use native preview/simulator tools for live visuals, then ShipGuard for typed receipts, redaction, target matching, and handoff.",
                "validation": "./tests/ios_devspace_check_test.sh && ./tests/ios_spec_workflow_test.sh",
            }
        ],
    },
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-external-audit: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit external workflow projects as native ShipGuard replacement and integration decisions."
    )
    parser.add_argument("--path", default=".", help="ShipGuard checkout to compare against")
    parser.add_argument(
        "--source-path",
        action="append",
        default=[],
        help="Read-only external source checkout to inspect. May be passed multiple times.",
    )
    parser.add_argument(
        "--source-url",
        action="append",
        default=[],
        help="External source URL or post URL to record as evidence. May be passed multiple times.",
    )
    parser.add_argument("--out", help="Output directory for ios-external-audit artifacts")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this as ShipGuard product QA only; external findings must not become target-app work.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from report fields before ChatGPT, GitHub, docs, or report-quality use.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path, *, limit: int = 600_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return data[:limit]


def run_git(path: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", path.as_posix(), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def label_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return path.as_posix()
    try:
        rel = path.relative_to(root)
        return rel.as_posix() or "."
    except ValueError:
        return f"<{placeholder}>"


def source_path_label(path: Path, *, shareable: bool, index: int) -> str:
    return f"<external-source-{index}>" if shareable else path.as_posix()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "external-source"


def signal_present(haystack: str, signal: str) -> bool:
    needle = signal.lower()
    if not needle:
        return False
    if not re.search(r"[a-z0-9]", needle):
        return needle in haystack
    if re.fullmatch(r"[a-z0-9][a-z0-9 _.-]*[a-z0-9]", needle):
        pattern = re.escape(needle).replace(r"\ ", r"\s+")
        return re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", haystack) is not None
    return needle in haystack


def detect_profile(text: str, path: Path | None = None, url: str = "") -> str:
    haystack = f"{url}\n{path.name if path else ''}\n{text}".lower()
    scores: dict[str, int] = {}
    for key, profile in SOURCE_PROFILES.items():
        score = 0
        for signal in profile["signals"]:
            if signal_present(haystack, str(signal)):
                score += 2
        if signal_present(haystack, key):
            score += 3
        if signal_present(haystack, str(profile["displayName"])):
            score += 3
        scores[key] = score
    best, best_score = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0]
    return best if best_score > 0 else "unknown"


def license_from_text(text: str, profile_key: str) -> str:
    lowered = text.lower()
    if "mit license" in lowered or '"license": "mit"' in lowered:
        return "MIT"
    if profile_key in SOURCE_PROFILES:
        return str(SOURCE_PROFILES[profile_key].get("license") or "unknown")
    return "unknown"


def source_text_summary(path: Path) -> str:
    parts: list[str] = []
    for rel in (
        "README.md",
        "SECURITY.md",
        "package.json",
        "pyproject.toml",
        "workflows/speckit/workflow.yml",
        "templates/commands/analyze.md",
        "templates/commands/checklist.md",
    ):
        candidate = path / rel
        if candidate.is_file():
            parts.append(read_text(candidate, limit=120_000))
    if not parts:
        for candidate in sorted(path.glob("*"))[:20]:
            if candidate.is_file() and candidate.suffix.lower() in {".md", ".json", ".toml", ".yml", ".yaml"}:
                parts.append(read_text(candidate, limit=80_000))
    return "\n".join(parts)


def source_record_from_path(path: Path, *, shareable: bool, index: int) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        fail(f"source path not found: {resolved}")
    text = source_text_summary(resolved)
    profile_key = detect_profile(text, resolved)
    commit = run_git(resolved, ["rev-parse", "--short", "HEAD"])
    tags = run_git(resolved, ["tag", "--points-at", "HEAD"])
    profile = SOURCE_PROFILES.get(profile_key, {})
    return {
        "kind": "local-checkout",
        "sourceKey": profile_key,
        "displayName": profile.get("displayName") or resolved.name,
        "canonicalUrl": profile.get("canonicalUrl") or "",
        "path": source_path_label(resolved, shareable=shareable, index=index),
        "commit": commit or "unknown",
        "tags": [item for item in tags.splitlines() if item][:5],
        "license": license_from_text(text, profile_key),
        "evidenceSignals": matched_signals(text, profile_key),
        "scanScope": ios_scan_scope.summary(ios_scan_scope.iter_files(resolved, SOURCE_SUFFIXES)),
    }


def source_record_from_url(url: str) -> dict[str, Any]:
    profile_key = detect_profile("", None, url)
    profile = SOURCE_PROFILES.get(profile_key, {})
    return {
        "kind": "url",
        "sourceKey": profile_key,
        "displayName": profile.get("displayName") or ("External X/Post Source" if "x.com/" in url else "External Source"),
        "canonicalUrl": url,
        "path": "",
        "commit": "not-applicable",
        "tags": [],
        "license": profile.get("license") or "unknown",
        "evidenceSignals": matched_signals(url, profile_key),
        "scanScope": {"filesScanned": 0, "skippedDirectoryCount": 0, "skippedDirectories": [], "skippedDirectoryListTruncated": False},
    }


def matched_signals(text: str, profile_key: str) -> list[str]:
    profile = SOURCE_PROFILES.get(profile_key)
    if not profile:
        return []
    lowered = text.lower()
    matches = [signal for signal in profile["signals"] if signal_present(lowered, str(signal))]
    return matches[:10]


def default_source_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key, profile in SOURCE_PROFILES.items():
        records.append(
            {
                "kind": "built-in-profile",
                "sourceKey": key,
                "displayName": profile["displayName"],
                "canonicalUrl": profile["canonicalUrl"],
                "path": "",
                "commit": "profile",
                "tags": [],
                "license": profile["license"],
                "evidenceSignals": profile["signals"][:6],
                "scanScope": {"filesScanned": 0, "skippedDirectoryCount": 0, "skippedDirectories": [], "skippedDirectoryListTruncated": False},
            }
        )
    return records


def current_surface(root: Path) -> dict[str, Any]:
    files = {
        "iosSpecWorkflow": "scripts/ios_spec_workflow.py",
        "iosReportQuality": "scripts/ios_report_quality.py",
        "iosDevspaceCheck": "scripts/ios_devspace_check.py",
        "iosDevspaceServer": "scripts/shipguard_devspace_mcp.py",
        "iosPreview": "scripts/ios_preview.py",
        "iosDesign": "scripts/ios_design.py",
        "leanAudit": "scripts/lean_audit.py",
        "leanReview": "scripts/lean_review.py",
        "leanDebt": "scripts/lean_debt.py",
        "leanGain": "scripts/lean_gain.py",
        "pluginSource": "plugins/ios-shipguard/.codex-plugin/plugin.json",
        "packageProof": "tests/package_release_test.sh",
        "ossEvaluation": "docs/oss-evaluation.md",
    }
    return {
        key: {
            "path": rel,
            "present": (root / rel).is_file(),
        }
        for key, rel in files.items()
    }


def capability_matrix(source_records: list[dict[str, Any]], surface: dict[str, Any]) -> list[dict[str, Any]]:
    included_keys = []
    for record in source_records:
        key = record.get("sourceKey")
        if key in SOURCE_PROFILES and key not in included_keys:
            included_keys.append(key)
    if not included_keys:
        included_keys = list(SOURCE_PROFILES)

    matrix: list[dict[str, Any]] = []
    for key in included_keys:
        profile = SOURCE_PROFILES[key]
        for capability in profile["capabilities"]:
            row = dict(capability)
            row["source"] = profile["displayName"]
            row["sourceKey"] = key
            row["surfacePresent"] = any(item["present"] for item in surface.values() if item["path"] in row["currentShipGuardSurface"])
            matrix.append(row)
    return matrix


def replacement_ledger(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {
        "replace-weaker-guidance": 0,
        "extend-native": 1,
        "integrate-by-routing": 2,
        "keep-current-with-extensions": 3,
        "defer-with-native-plan": 4,
    }
    ledger = []
    for row in sorted(matrix, key=lambda item: (order.get(str(item.get("decision")), 9), item["source"], item["id"])):
        ledger.append(
            {
                "source": row["source"],
                "capabilityId": row["id"],
                "decision": row["decision"],
                "replaceOrKeep": row["replacement"],
                "nativeAction": row["nativeAction"],
                "validation": row["validation"],
            }
        )
    return ledger


def implementation_backlog(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    backlog = []
    for row in matrix:
        if row["decision"] in {"replace-weaker-guidance", "extend-native", "defer-with-native-plan"}:
            backlog.append(
                {
                    "id": f"EXT-{len(backlog) + 1:03d}",
                    "source": row["source"],
                    "capabilityId": row["id"],
                    "task": row["nativeAction"],
                    "proof": row["validation"],
                    "adoptionRule": "Implement only as ShipGuard-owned CLI/docs/tests/fixtures. Do not vendor external source code.",
                }
            )
    return backlog


def findings(source_records: list[dict[str, Any]], matrix: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    unknowns = [record for record in source_records if record.get("sourceKey") == "unknown"]
    for record in unknowns:
        out.append(
            {
                "severity": "opportunity",
                "ruleId": "external-source-unclassified",
                "category": "source-evidence",
                "evidence": f"{record.get('displayName')} did not match a built-in ShipGuard source profile.",
                "recommendation": "Capture a local source snapshot or add a ShipGuard-owned profile before treating this as adopted.",
                "proofGuidance": "Run ios external-audit with --source-path for the source or add a public fixture that reproduces the idea.",
            }
        )
    deferred = [row for row in matrix if row["decision"] == "defer-with-native-plan"]
    if deferred:
        out.append(
            {
                "severity": "opportunity",
                "ruleId": "external-capability-deferred",
                "category": "native-integration",
                "evidence": f"{len(deferred)} external capabilities are useful but not safe to adopt without a ShipGuard-native contract.",
                "recommendation": "Convert one deferred capability into a public fixture and report-quality gate before implementation.",
                "proofGuidance": "Use ios spec-workflow --from-report on this audit, then validate with ios report-quality.",
            }
        )
    return out


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path not found: {root}")
    source_records = [
        source_record_from_path(Path(item), shareable=bool(args.shareable), index=index)
        for index, item in enumerate(args.source_path, start=1)
    ]
    source_records.extend(source_record_from_url(url) for url in args.source_url)
    if not source_records:
        source_records = default_source_records()

    surface = current_surface(root)
    matrix = capability_matrix(source_records, surface)
    ledger = replacement_ledger(matrix)
    backlog = implementation_backlog(matrix)
    report_findings = findings(source_records, matrix)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "generatedAt": utc_now(),
        "status": "pass",
        "path": label_path(root, root=root, shareable=bool(args.shareable), placeholder="shipguard-repo"),
        "scanScope": ios_scan_scope.summary(ios_scan_scope.iter_files(root, SOURCE_SUFFIXES)),
        "shareability": {
            "mode": "shareable" if args.shareable else "local",
            "localAbsolutePathsIncluded": not bool(args.shareable),
            "note": "Use --shareable before moving this audit into ChatGPT, GitHub, docs, release evidence, or report-quality scoring."
            if not args.shareable
            else "Report fields are intended to avoid local absolute paths for external planning and report-quality scoring.",
        },
        "scopeBoundary": {
            "shipguardOnly": bool(args.shipguard_eval),
            "targetAppsReadOnly": bool(args.shipguard_eval),
            "purpose": "Evaluate external workflow sources as ShipGuard product QA; integrate only native ShipGuard CLI/docs/tests/fixtures.",
            "forbiddenUses": [
                "Do not vendor external source code into ShipGuard from this report.",
                "Do not claim an external repo has been fully integrated unless its capability appears in replacementLedger with passing validation.",
                "Do not turn private app or social-post observations into app remediation work.",
            ],
        },
        "sourceInputs": source_records,
        "currentShipGuardSurface": surface,
        "capabilityMatrix": matrix,
        "replacementLedger": ledger,
        "implementationBacklog": backlog,
        "licenseBoundary": {
            "policy": "MIT sources can inspire native ShipGuard implementation, but copied code/templates require explicit attribution and package review. Default path is no vendoring.",
            "defaultDecision": "native-adaptation-only",
        },
        "findings": report_findings,
        "reportQualityQuestions": [
            "Did external-audit name concrete replace, extend, keep, route, or defer decisions for every adopted external capability?",
            "Did every adopted external idea map to a current ShipGuard surface and validation command?",
            "Which deferred external capability should become a public fixture before ShipGuard adopts it?",
            "Did the audit avoid vendoring external code while preserving license and attribution boundaries?",
        ],
    }


def cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# iOS ShipGuard External Source Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Purpose: {report['scopeBoundary']['purpose']}",
        "",
        "## Source Inputs",
        "",
        "| Source | Kind | License | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["sourceInputs"]:
        evidence = ", ".join(item.get("evidenceSignals") or []) or item.get("canonicalUrl") or item.get("path") or "-"
        lines.append(f"| {cell(item.get('displayName'))} | `{item.get('kind')}` | {cell(item.get('license'))} | {cell(evidence, 180)} |")
    scan = report["scanScope"]
    lines.extend(["", "## Scan Scope", ""])
    lines.append(f"- Files scanned: {scan['filesScanned']}")
    lines.append(f"- Skipped directories: {scan['skippedDirectoryCount']}")
    for directory in scan.get("skippedDirectories", [])[:10]:
        lines.append(f"- `{directory}`")
    lines.extend(["", "## Source Scan Scope", ""])
    for item in report["sourceInputs"]:
        source_scan = item.get("scanScope") or {}
        lines.append(
            f"- {item.get('displayName')}: files scanned `{source_scan.get('filesScanned', 0)}`, skipped directories `{source_scan.get('skippedDirectoryCount', 0)}`"
        )
    lines.extend(
        [
            "",
            "## Replacement Ledger",
            "",
            "| Source | Capability | Decision | Native Action | Validation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["replacementLedger"]:
        lines.append(
            f"| {cell(row['source'])} | `{cell(row['capabilityId'], 80)}` | `{row['decision']}` | {cell(row['nativeAction'], 220)} | `{cell(row['validation'], 160)}` |"
        )
    lines.extend(["", "## Capability Matrix", ""])
    for row in report["capabilityMatrix"]:
        lines.extend(
            [
                f"### {row['source']} - {row['name']}",
                "",
                f"- Decision: `{row['decision']}`",
                f"- External signal: {row['externalSignal']}",
                f"- Current ShipGuard surface: {row['currentShipGuardSurface']}",
                f"- Replace or keep: {row['replacement']}",
                f"- Native action: {row['nativeAction']}",
                f"- Validation: `{row['validation']}`",
                "",
            ]
        )
    lines.extend(["## Implementation Backlog", ""])
    for item in report["implementationBacklog"]:
        lines.append(f"- [ ] `{item['id']}` {item['task']} Proof: `{item['proof']}`")
    lines.extend(
        [
            "",
            "## License And Vendoring Boundary",
            "",
            f"- {report['licenseBoundary']['policy']}",
            f"- Default decision: `{report['licenseBoundary']['defaultDecision']}`",
            "",
            "## Findings",
            "",
        ]
    )
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation |", "| --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(f"| {item['severity']} | `{item['ruleId']}` | {cell(item['evidence'], 180)} | {cell(item['recommendation'], 180)} |")
    else:
        lines.append("No external-audit issues were detected.")
    lines.extend(["", "## Report Quality Questions", ""])
    lines.extend(f"- {question}" for question in report["reportQualityQuestions"])
    lines.append("")
    return "\n".join(lines)


def render_ledger_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Native External Workflow Replacement Ledger",
        "",
        "This ledger is the ShipGuard-native adoption contract. A source is not considered integrated until its capability has a decision, native action, and passing validation.",
        "",
        "| Source | Capability | Decision | Replace Or Keep | Validation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["replacementLedger"]:
        lines.append(
            f"| {cell(row['source'])} | `{cell(row['capabilityId'], 80)}` | `{row['decision']}` | {cell(row['replaceOrKeep'], 220)} | `{cell(row['validation'], 160)}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-external-audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-external-audit.md").write_text(render_markdown(report), encoding="utf-8")
    (out_dir / "replacement-ledger.md").write_text(render_ledger_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-external-audit.json'}")
    print(f"wrote: {out_dir / 'ios-external-audit.md'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    report = build_report(args)
    markdown = render_markdown(report)
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
