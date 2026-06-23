#!/usr/bin/env python3
"""Read-only Expo SDK 56 readiness audit."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {".json", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".md", ".yml", ".yaml"}
EVIDENCE_SUFFIXES = TEXT_SUFFIXES | {".txt", ".log", ".out", ".png", ".jpg", ".jpeg", ".webp"}
SKIP_DIRS = {".git", "node_modules", ".expo", ".next", "dist", "build", "ios/Pods", "android/.gradle"}
SDK56_TOPICS = [
    "expo-ui-stable-native-primitives",
    "precompiled-ios-expo-modules",
    "android-precompiled-headers",
    "inline-expo-modules",
    "expo-type-information",
    "hermes-v1-default",
    "hermes-bytecode-diffing",
    "expo-router-react-navigation-split",
    "eas-build-timing-statistics",
    "ai-agent-scaffolding",
]
PROFESSIONAL_DESIGN_PRINCIPLES = [
    "contrast",
    "hierarchy",
    "alignment",
    "proximity",
    "repetition",
    "balance",
    "white-space",
    "unity",
]
DESIGN_SOURCE_URL = "https://expo.dev/blog/how-to-apply-professional-design-principles-in-ai-app-development"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit an Expo/React Native repo for SDK 56-era readiness.")
    parser.add_argument("--path", default=".", help="Repo to inspect")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--target-sdk", default="56", help="Target Expo SDK major version")
    parser.add_argument("--runtime-evidence", action="append", default=[], help="Read-only Expo Doctor, EAS timing, preview, screenshot, or runtime evidence file/dir")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Do not include local absolute paths")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_text(path: Path, limit: int = 160_000) -> str:
    try:
        if path.stat().st_size > limit:
            return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def read_evidence_text(path: Path, limit: int = 24_000) -> str:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        return ""
    return read_text(path, limit)


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def version_major(value: object) -> int | None:
    text = str(value or "")
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def iter_files(root: Path, limit: int = 500) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if len(files) >= limit:
            break
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts if part):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name in {"package.json", "app.json", "eas.json", "AGENTS.md", "CLAUDE.md"}):
            files.append(path)
    return files


def iter_evidence_paths(inputs: list[str], limit: int = 40) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        base = Path(raw).expanduser()
        if base.is_file():
            paths.append(base)
        elif base.is_dir():
            for path in sorted(base.rglob("*")):
                if path.is_file() and (path.suffix.lower() in EVIDENCE_SUFFIXES or path.name.lower() in {"expo-doctor", "eas-build"}):
                    paths.append(path)
                    if len(paths) >= limit:
                        return paths
    return paths[:limit]


def runtime_evidence(inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    files = iter_evidence_paths(inputs)
    categories = {
        "expoDoctor": ["expo doctor", "expo-doctor", "npx expo-doctor", "expo diagnostics"],
        "easTiming": ["eas build", "build details", "duration", "queue", "build time", "timing"],
        "preview": ["preview", "devspace", "localhost", "simulator", "expo go"],
        "screenshot": ["screenshot", "screen capture", ".png", ".jpg", ".jpeg", ".webp"],
        "nativeRuntime": ["ios simulator", "android emulator", "device", "xcodebuild", "gradle", "runtime"],
    }
    matches: dict[str, list[str]] = {key: [] for key in categories}
    for path in files:
        haystack = f"{path.name}\n{read_evidence_text(path)}".lower()
        rendered = path.name if shareable else str(path)
        for category, needles in categories.items():
            if any(needle in haystack for needle in needles):
                matches[category].append(rendered)
    found = {key: sorted(set(value))[:6] for key, value in matches.items() if value}
    return {
        "provided": bool(inputs),
        "fileCount": len(files),
        "categories": found,
        "summary": "runtime evidence attached" if found else ("no matching runtime evidence found" if inputs else "not provided"),
        "boundary": "ShipGuard reads provided artifacts only; it does not run Expo Doctor, EAS, simulators, or builds.",
    }


def dependency_map(package_json: dict[str, Any]) -> dict[str, str]:
    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = package_json.get(key)
        if isinstance(value, dict):
            deps.update({str(name): str(version) for name, version in value.items()})
    return deps


def app_config(root: Path) -> tuple[str | None, dict[str, Any]]:
    for name in ("app.json", "app.config.json"):
        path = root / name
        if path.is_file():
            data = read_json(path)
            expo = data.get("expo") if isinstance(data.get("expo"), dict) else data
            return name, expo if isinstance(expo, dict) else {}
    for name in ("app.config.ts", "app.config.js", "app.config.mjs", "app.config.cjs"):
        if (root / name).is_file():
            return name, {}
    return None, {}


def contains_any(files: list[Path], root: Path, needles: list[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    lowered = [needle.lower() for needle in needles]
    for path in files:
        relative = rel(path, root)
        text = f"{relative}\n{read_text(path)}".lower()
        for needle, raw in zip(lowered, needles):
            if needle in text:
                hits.append({"signal": raw, "path": relative})
                break
    return hits[:12]


def count_matches(files: list[Path], root: Path, pattern: str) -> int:
    matcher = re.compile(pattern, re.IGNORECASE)
    count = 0
    for path in files:
        text = f"{rel(path, root)}\n{read_text(path)}"
        count += len(matcher.findall(text))
    return count


def design_signals(files: list[Path], root: Path) -> dict[str, Any]:
    return {
        "styleSystemFiles": [
            rel(path, root)
            for path in files
            if path.name.lower() in {"theme.ts", "theme.js", "tokens.ts", "tokens.js", "design-system.ts", "design-system.tsx"}
            or "design-system" in rel(path, root).lower()
            or "theme" in rel(path, root).lower()
        ][:12],
        "styleDeclarationCount": count_matches(files, root, r"\bStyleSheet\.create\b|\bclassName=|styled\(|tailwind|nativewind"),
        "colorLiteralCount": count_matches(files, root, r"#[0-9a-f]{3,8}\b|rgba?\("),
        "spacingLiteralCount": count_matches(files, root, r"\b(?:padding|margin|gap|space|inset)[A-Za-z]*\s*[:=]"),
        "typographyLiteralCount": count_matches(files, root, r"\b(?:fontSize|fontWeight|lineHeight|fontFamily)\s*[:=]"),
        "layoutPrimitiveCount": count_matches(files, root, r"\b(?:View|SafeAreaView|ScrollView|FlatList|SectionList)\b"),
        "motionSignalCount": count_matches(files, root, r"\b(?:Animated|withTiming|withSpring|LayoutAnimation|MotiView|Reanimated)\b"),
        "accessibilitySignalCount": count_matches(files, root, r"\b(?:accessibilityLabel|accessibilityRole|accessibilityHint|aria-|accessible=)\b"),
    }


def finding(severity: str, category: str, rule_id: str, evidence: str, recommendation: str, proof: str) -> dict[str, str]:
    return {
        "severity": severity,
        "category": category,
        "ruleId": rule_id,
        "evidence": evidence,
        "recommendation": recommendation,
        "proofGuidance": proof,
    }


def build_report(root: Path, target_sdk: str, *, runtime_evidence_inputs: list[str], shareable: bool, shipguard_eval: bool) -> dict[str, Any]:
    package_path = root / "package.json"
    package = read_json(package_path)
    deps = dependency_map(package)
    config_name, config = app_config(root)
    eas = read_json(root / "eas.json")
    files = iter_files(root)

    expo_version = deps.get("expo")
    expo_major = version_major(expo_version)
    target_major = version_major(target_sdk) or 56
    is_expo_project = "expo" in deps or config_name is not None or (root / "eas.json").is_file()
    has_ios = (root / "ios").is_dir()
    has_android = (root / "android").is_dir()
    uses_router = "expo-router" in deps
    uses_react_navigation = any(name.startswith("@react-navigation/") for name in deps)
    uses_expo_ui = "@expo/ui" in deps or "expo-ui" in deps or bool(contains_any(files, root, ["@expo/ui", "expo/ui"]))
    uses_gorhom = "@gorhom/bottom-sheet" in deps
    uses_vector_icons = "@expo/vector-icons" in deps
    uses_eas = bool(eas)
    has_agents = (root / "AGENTS.md").is_file()
    has_claude = (root / "CLAUDE.md").is_file()
    has_claude_settings = (root / ".claude" / "settings.json").is_file()

    native_ui_hits = contains_any(
        files,
        root,
        ["@gorhom/bottom-sheet", "react-native-pager-view", "@react-native-picker/picker", "@react-native-community/slider", "@react-native-menu/menu"],
    )
    inline_module_hits = contains_any(files, root, ["expo-module.config.json", "ExpoModulesCore", "expo.modules.kotlin", "create-expo-module"])
    eas_workflow_hits = contains_any(files, root, ["eas/workflows", "eas workflow", "build:", "submit:", "updates:"])
    agent_hits = contains_any(files, root, ["AGENTS.md", "CLAUDE.md", ".claude/settings.json", "npx skills add expo/skills"])
    design = design_signals(files, root)
    runtime = runtime_evidence(runtime_evidence_inputs, shareable=shareable)

    findings: list[dict[str, str]] = []
    if not is_expo_project:
        findings.append(
            finding(
                "blocked",
                "project-detection",
                "expo-project-not-detected",
                "No package.json Expo dependency, app config, or eas.json was detected.",
                "Run this command at an Expo or React Native project root.",
                "Confirm package.json/app.json/eas.json from the target repo before using Expo SDK guidance.",
            )
        )
    if expo_major is None:
        findings.append(
            finding(
                "review",
                "sdk",
                "expo-version-missing",
                "package.json does not expose an expo dependency version.",
                "Run npx expo install --fix after confirming this is an Expo app.",
                "Rerun shipguard expo readiness and npx expo-doctor after package metadata is present.",
            )
        )
    elif expo_major < target_major:
        findings.append(
            finding(
                "review",
                "sdk",
                "expo-sdk-behind-target",
                f"Detected expo dependency {expo_version}; target SDK is {target_major}.",
                "Plan an SDK 56 upgrade before relying on Expo UI stable APIs, Hermes v1 defaults, and SDK 56 build-performance behavior.",
                "Run npx expo install expo@latest --fix, npx expo-doctor, and the app's build/test lane.",
            )
        )
    if uses_router and uses_react_navigation:
        findings.append(
            finding(
                "review",
                "navigation",
                "expo-router-react-navigation-pairing",
                "expo-router and @react-navigation packages are both installed.",
                "Review whether direct @react-navigation imports are intentional after the Expo Router / React Navigation split.",
                "Run npx expo-doctor and inspect routing imports before changing navigation code.",
            )
        )
    if uses_vector_icons:
        findings.append(
            finding(
                "review",
                "deprecation",
                "expo-vector-icons-deprecation",
                "@expo/vector-icons is present.",
                "Plan migration to scoped @react-native-vector-icons packages or an app-specific icon system.",
                "Run the official vector-icons codemod in a branch and verify affected screens.",
            )
        )
    if native_ui_hits and not uses_expo_ui:
        findings.append(
            finding(
                "info",
                "ui",
                "expo-ui-migration-opportunity",
                f"Found native component library signals: {', '.join(hit['signal'] for hit in native_ui_hits[:4])}.",
                "Evaluate Expo UI stable native primitives as drop-in or partial replacements where they simplify dependencies.",
                "Prototype one low-risk component migration and verify iOS, Android, accessibility, and visual behavior.",
            )
        )
    if not (has_agents and has_claude and has_claude_settings):
        missing = [name for name, present in (("AGENTS.md", has_agents), ("CLAUDE.md", has_claude), (".claude/settings.json", has_claude_settings)) if not present]
        findings.append(
            finding(
                "info",
                "agent-scaffolding",
                "expo-agent-scaffolding-incomplete",
                f"Missing AI-agent scaffolding: {', '.join(missing)}.",
                "Add Expo-specific agent guidance and install the official Expo skills where appropriate.",
                "Run npx skills add expo/skills, then keep project-specific safety rules in AGENTS.md.",
            )
        )
    if uses_eas and not eas_workflow_hits:
        findings.append(
            finding(
                "info",
                "eas",
                "eas-workflow-proof-thin",
                "eas.json exists, but no EAS workflow or timing evidence was detected in scanned files.",
                "Use EAS build/workflow timing output as proof for native build optimization decisions.",
                "Attach EAS build timing or workflow evidence with --runtime-evidence or shipguard agent trace --expo-eas-evidence.",
            )
        )
    if is_expo_project and not design["styleSystemFiles"] and design["styleDeclarationCount"] == 0:
        findings.append(
            finding(
                "review",
                "design",
                "professional-design-evidence-thin",
                "No theme, token, design-system, StyleSheet, className, styled-component, Tailwind, or NativeWind signal was found in the bounded scan.",
                "Add or point ShipGuard at reusable design evidence so AI output can be critiqued for contrast, hierarchy, alignment, proximity, repetition, balance, white space, and unity instead of generic visual taste.",
                "Run the app through shipguard ios preview/devspace or attach screenshots, then rerun ExpoDeck with --runtime-evidence plus the source that defines design tokens/components.",
            )
        )
    if design["colorLiteralCount"] >= 8 and not design["styleSystemFiles"]:
        findings.append(
            finding(
                "review",
                "design",
                "design-repetition-risk",
                f"Found {design['colorLiteralCount']} color literals without a detected token/theme file.",
                "Consolidate repeated colors into named tokens before asking an agent for more UI changes.",
                "Attach a before/after diff showing token reuse plus screenshots for the affected screens.",
            )
        )
    if design["motionSignalCount"] > 0:
        findings.append(
            finding(
                "info",
                "design",
                "motion-proof-required",
                f"Found {design['motionSignalCount']} animation or motion signals.",
                "Review motion against app genre, reduced-motion behavior, frequency, and whether it supports hierarchy rather than decoration.",
                "Use simulator/device preview evidence, --runtime-evidence, and reduced-motion proof before accepting AI-generated motion changes.",
            )
        )

    opportunities = [
        {
            "id": "expo-ui-stable",
            "status": "present" if uses_expo_ui else "candidate",
            "why": "SDK 56 makes Expo UI stable on iOS and Android with native SwiftUI and Jetpack Compose primitives.",
            "proofCommand": "npx expo-doctor && npm run test",
        },
        {
            "id": "precompiled-builds",
            "status": "eligible" if expo_major and expo_major >= 56 else "requires-sdk56",
            "why": "SDK 56 enables precompiled Expo packages on iOS by default and EAS adds prebuilt community libraries.",
            "proofCommand": "Compare clean local/EAS build timing before and after the SDK upgrade.",
        },
        {
            "id": "inline-native-modules",
            "status": "present" if inline_module_hits else "candidate",
            "why": "SDK 56 supports inline Expo modules plus type generation for Swift module interfaces.",
            "proofCommand": "Use create-expo-module or expo-type-information in a branch, then verify generated TypeScript and native build.",
        },
        {
            "id": "ai-agent-scaffolding",
            "status": "present" if has_agents and has_claude and has_claude_settings else "incomplete",
            "why": "Expo SDK 56 project scaffolding includes agent guidance and official Expo skills.",
            "proofCommand": "npx skills add expo/skills && shipguard expo readiness --path . --out <dir>",
        },
    ]

    status = "blocked" if any(item["severity"] == "blocked" for item in findings) else ("review" if findings else "pass")
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "tool": "shipguard expo readiness",
        "surface": "ShipGuard ExpoDeck",
        "generatedAt": utc_now(),
        "status": status,
        "targetSdk": str(target_major),
        "shareability": {"mode": "shareable" if shareable else "local", "localAbsolutePathsIncluded": not shareable},
        "scanScope": {
            "root": "<redacted>" if shareable else str(root.resolve()),
            "fileCount": len(files),
            "bounded": True,
            "doesNotRunNpmOrExpo": True,
        },
        "projectSignals": {
            "isExpoProject": is_expo_project,
            "packageJsonPresent": package_path.is_file(),
            "appConfig": config_name or "missing",
            "easJsonPresent": bool(eas),
            "hasIosDirectory": has_ios,
            "hasAndroidDirectory": has_android,
            "expoVersion": expo_version or "missing",
            "expoMajor": expo_major,
            "usesExpoRouter": uses_router,
            "usesReactNavigationPackages": uses_react_navigation,
            "usesExpoUI": uses_expo_ui,
            "usesEAS": uses_eas,
        },
        "sdk56Readiness": {
            "topics": SDK56_TOPICS,
            "source": "Expo SDK 56 public changelog",
            "sourceUrl": "https://expo.dev/changelog/sdk-56",
            "releaseDate": "2026-05-21",
        },
        "professionalDesignPrinciples": {
            "source": "Expo professional design principles for AI app development",
            "sourceUrl": DESIGN_SOURCE_URL,
            "principles": PROFESSIONAL_DESIGN_PRINCIPLES,
            "useInShipGuard": "Critique AI-generated UI with concrete design vocabulary; require preview or screenshot proof before treating source heuristics as visual truth.",
            "signals": design,
        },
        "nativeUISignals": native_ui_hits,
        "inlineModuleSignals": inline_module_hits,
        "agentScaffoldingSignals": agent_hits,
        "runtimeEvidence": runtime,
        "opportunities": opportunities,
        "findings": findings,
        "nextCommands": [
            "shipguard expo readiness --path . --out /tmp/shipguard-expo-readiness --shareable",
            "shipguard expo readiness --path . --out /tmp/shipguard-expo-readiness --runtime-evidence <proof-file-or-dir> --shareable",
            "npx expo-doctor",
            "npx expo install --fix",
            "shipguard agent trace --trace <agent-trace> --out <trace-dir> --expo-eas-evidence <eas-evidence-dir>",
        ],
        "scopeBoundary": {
            "readOnly": True,
            "doesNotRunExpoCommands": True,
            "doesNotModifyTarget": True,
            "doesNotClaimBuildSpeedWithoutTimingEvidence": True,
        },
        "reportQualityQuestions": [
            "Does ExpoDeck identify SDK 56 upgrade blockers, Expo UI opportunities, EAS build-timing proof, and AI-agent scaffolding gaps without mutating the target app?",
            "Does ExpoDeck distinguish source heuristics from real npx expo-doctor, EAS build, native runtime, and timing evidence?",
            "Does ExpoDeck critique AI-generated UI with concrete design principles while requiring visual proof for rendered quality claims?",
        ],
    }
    if shipguard_eval:
        report["shipguardEval"] = {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "improveShipGuardNotTargetApp": True,
        }
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard ExpoDeck",
        "",
        f"- Status: `{report['status']}`",
        f"- Target SDK: `{report['targetSdk']}`",
        f"- Expo version: `{report['projectSignals']['expoVersion']}`",
        f"- Expo project detected: `{report['projectSignals']['isExpoProject']}`",
        f"- Read-only: `{report['scopeBoundary']['readOnly']}`",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    if findings:
        for item in findings:
            lines.extend(
                [
                    f"### {item['ruleId']}",
                    "",
                    f"- Severity: `{item['severity']}`",
                    f"- Category: `{item['category']}`",
                    f"- Evidence: {item['evidence']}",
                    f"- Recommendation: {item['recommendation']}",
                    f"- Proof: {item['proofGuidance']}",
                    "",
                ]
            )
    else:
        lines.extend(["No findings.", ""])
    lines.extend(["## SDK 56 Opportunities", ""])
    for item in report.get("opportunities") or []:
        lines.extend(
            [
                f"- `{item['id']}`: `{item['status']}`",
                f"  - Why: {item['why']}",
                f"  - Proof: `{item['proofCommand']}`",
            ]
        )
    principles = report.get("professionalDesignPrinciples") or {}
    if principles:
        lines.extend(["", "## Professional Design Principles", ""])
        lines.append(f"- Source: {principles.get('sourceUrl')}")
        lines.append(f"- Principles: {', '.join(principles.get('principles') or [])}")
        lines.append(f"- Boundary: {principles.get('useInShipGuard')}")
        signals = principles.get("signals") or {}
        lines.append(
            "- Signals: "
            f"style systems `{len(signals.get('styleSystemFiles') or [])}`, "
            f"style declarations `{signals.get('styleDeclarationCount')}`, "
            f"color literals `{signals.get('colorLiteralCount')}`, "
            f"motion signals `{signals.get('motionSignalCount')}`, "
            f"accessibility signals `{signals.get('accessibilitySignalCount')}`"
        )
    runtime = report.get("runtimeEvidence") or {}
    lines.extend(["", "## Runtime Evidence", ""])
    lines.append(f"- Summary: {runtime.get('summary', 'not provided')}")
    lines.append(f"- Boundary: {runtime.get('boundary', '')}")
    for category, paths in (runtime.get("categories") or {}).items():
        lines.append(f"- `{category}`: {', '.join(paths)}")
    lines.extend(["", "## Next Commands", ""])
    for command in report.get("nextCommands") or []:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Report-Quality Questions", ""])
    for question in report.get("reportQualityQuestions") or []:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser()
    if not root.exists():
        raise SystemExit(f"expo-readiness: path does not exist: {root}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = build_report(root, args.target_sdk, runtime_evidence_inputs=args.runtime_evidence, shareable=args.shareable, shipguard_eval=args.shipguard_eval)
    md = markdown(report)
    (out / "expo-readiness.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "expo-readiness.md").write_text(md, encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
