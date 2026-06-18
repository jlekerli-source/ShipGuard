#!/usr/bin/env python3
"""Discover iOS project topology before Codex edits an app."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ios_scan_scope

SCHEMA_VERSION = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover iOS projects, packages, targets, schemes, and proof-relevant app metadata."
    )
    parser.add_argument("--path", default=".", help="iOS repo root to inspect")
    parser.add_argument("--out", help="Output directory for ios-doctor.md and ios-doctor.json")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of Markdown")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"ios-doctor: {message}", file=sys.stderr)
    raise SystemExit(1)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def should_skip_dir(path: Path) -> bool:
    return ios_scan_scope.should_skip_dir(path)


def iter_files(root: Path) -> list[Path]:
    return ios_scan_scope.iter_files(root).files


def iter_dirs(root: Path, suffix: str) -> list[Path]:
    return ios_scan_scope.iter_dirs(root, suffix).files


def load_plist(path: Path) -> Any | None:
    try:
        with path.open("rb") as handle:
            return plistlib.load(handle)
    except Exception:
        return None


def plist_summary(path: Path, root: Path) -> dict[str, Any]:
    loaded = load_plist(path)
    keys: list[str] = []
    if isinstance(loaded, dict):
        keys = sorted(str(key) for key in loaded.keys())
    return {"path": rel(path, root), "keys": keys}


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def parse_package(path: Path, root: Path) -> dict[str, Any]:
    text = read_text(path)
    name_match = re.search(r'Package\s*\(\s*name:\s*"([^"]+)"', text, re.S)
    tools_match = re.search(r"swift-tools-version:\s*([0-9.]+)", text)
    ios_platforms = re.findall(r"\.iOS\(\.v([0-9_]+)\)", text)
    target_details = parse_package_target_details(text)
    targets = [target["name"] for target in target_details]
    products = re.findall(r"\.(?:library|executable|plugin)\(\s*name:\s*\"([^\"]+)\"", text)
    return {
        "path": rel(path, root),
        "name": name_match.group(1) if name_match else None,
        "swift_tools_version": tools_match.group(1) if tools_match else None,
        "ios_platforms": unique_sorted(ios_platforms),
        "targets": unique_sorted(targets),
        "target_details": target_details,
        "products": unique_sorted(products),
    }


def parse_package_target_details(text: str) -> list[dict[str, str | None]]:
    details: list[dict[str, str | None]] = []
    pattern = re.compile(r"\.(target|executableTarget|testTarget)\(\s*name:\s*\"([^\"]+)\"(.*?)(?=\n\s*\.(?:target|executableTarget|testTarget)\(|\n\s*\]\s*\)|\n\s*\]\s*,)", re.S)
    for match in pattern.finditer(text):
        raw_kind = match.group(1)
        name = match.group(2)
        body = match.group(3)
        path_match = re.search(r"\bpath:\s*\"([^\"]+)\"", body)
        details.append(
            {
                "name": name,
                "kind": "test" if raw_kind == "testTarget" else "package-target",
                "path": path_match.group(1) if path_match else None,
            }
        )
    if details:
        return details
    return [
        {"name": name, "kind": "package-target", "path": None}
        for name in unique_sorted(re.findall(r"\.(?:target|executableTarget|testTarget)\(\s*name:\s*\"([^\"]+)\"", text))
    ]


def parse_pbx_assignments(text: str, key: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(key)}\s*=\s*([^;]+);")
    values = []
    for match in pattern.finditer(text):
        value = match.group(1).strip().strip('"')
        values.append(value)
    return unique_sorted(values)


def parse_pbx_section_blocks(text: str, section: str) -> dict[str, dict[str, str]]:
    section_match = re.search(
        rf"/\* Begin {re.escape(section)} section \*/(.*?)/\* End {re.escape(section)} section \*/",
        text,
        re.S,
    )
    if not section_match:
        return {}

    blocks: dict[str, dict[str, str]] = {}
    lines = section_match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        start = re.match(r"\s*([A-Za-z0-9]+)\s*/\*\s*(.*?)\s*\*/\s*=\s*\{", line)
        if not start:
            index += 1
            continue

        object_id = start.group(1)
        comment = start.group(2)
        body_lines: list[str] = []
        depth = line.count("{") - line.count("}")
        index += 1
        while index < len(lines) and depth > 0:
            body_line = lines[index]
            depth += body_line.count("{") - body_line.count("}")
            if depth > 0:
                body_lines.append(body_line)
            index += 1
        blocks[object_id] = {"comment": comment, "body": "\n".join(body_lines)}
    return blocks


def parse_pbx_value(body: str, key: str) -> str | None:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*([^;]+);", body)
    if not match:
        return None
    return clean_pbx_scalar(match.group(1))


def clean_pbx_scalar(value: str) -> str:
    return re.sub(r"/\*.*?\*/", "", value).strip().strip('"')


def parse_build_settings(body: str) -> dict[str, str]:
    match = re.search(r"\bbuildSettings\s*=\s*\{(.*?)\n\s*\};", body, re.S)
    if not match:
        return {}
    settings: dict[str, str] = {}
    for key, value in re.findall(r"\b([A-Za-z0-9_]+)\s*=\s*([^;]+);", match.group(1)):
        settings[key] = clean_pbx_scalar(value)
    return settings


def parse_configuration_lists(text: str) -> dict[str, list[str]]:
    lists: dict[str, list[str]] = {}
    for object_id, block in parse_pbx_section_blocks(text, "XCConfigurationList").items():
        match = re.search(r"\bbuildConfigurations\s*=\s*\((.*?)\);", block["body"], re.S)
        if not match:
            lists[object_id] = []
            continue
        lists[object_id] = re.findall(r"\b([A-Za-z0-9]+)\s*/\*", match.group(1))
    return lists


def target_kind(product_type: str | None, name: str) -> str:
    lowered_type = (product_type or "").lower()
    lowered_name = name.lower()
    if "ui-testing" in lowered_type or "unit-test" in lowered_type or lowered_name.endswith("tests"):
        return "test"
    if "extension" in lowered_type:
        return "extension"
    if "application" in lowered_type:
        return "app"
    return "xcode-target"


def values_from_settings(config_settings: list[dict[str, str]], key: str) -> list[str]:
    return unique_sorted([settings.get(key, "") for settings in config_settings])


def parse_native_target_details(text: str) -> list[dict[str, Any]]:
    target_blocks = parse_pbx_section_blocks(text, "PBXNativeTarget")
    config_blocks = parse_pbx_section_blocks(text, "XCBuildConfiguration")
    config_lists = parse_configuration_lists(text)
    all_config_settings = [parse_build_settings(block["body"]) for block in config_blocks.values()]
    details: list[dict[str, Any]] = []

    for object_id, block in target_blocks.items():
        body = block["body"]
        name = parse_pbx_value(body, "name") or block["comment"]
        product_name = parse_pbx_value(body, "productName")
        product_type = parse_pbx_value(body, "productType")
        config_list_id = parse_pbx_value(body, "buildConfigurationList")
        config_ids = config_lists.get(config_list_id or "", [])
        config_settings = [
            parse_build_settings(config_blocks[config_id]["body"])
            for config_id in config_ids
            if config_id in config_blocks
        ]
        if not config_settings and len(target_blocks) == 1:
            config_settings = all_config_settings
        kind = target_kind(product_type, name)
        if kind == "xcode-target" and len(target_blocks) == 1:
            kind = "app"
        details.append(
            {
                "id": object_id,
                "name": name,
                "kind": kind,
                "product_name": product_name,
                "product_type": product_type,
                "bundle_identifiers": values_from_settings(config_settings, "PRODUCT_BUNDLE_IDENTIFIER"),
                "deployment_targets": values_from_settings(config_settings, "IPHONEOS_DEPLOYMENT_TARGET"),
                "swift_versions": values_from_settings(config_settings, "SWIFT_VERSION"),
                "info_plists": values_from_settings(config_settings, "INFOPLIST_FILE"),
                "entitlements": values_from_settings(config_settings, "CODE_SIGN_ENTITLEMENTS"),
            }
        )
    return sorted(details, key=lambda item: item["name"])


def parse_native_target_names(text: str) -> list[str]:
    names: list[str] = []
    section_match = re.search(r"/\* Begin PBXNativeTarget section \*/(.*?)/\* End PBXNativeTarget section \*/", text, re.S)
    if section_match:
        section = section_match.group(1)
        names.extend(match.group(1).strip().strip('"') for match in re.finditer(r"\bname\s*=\s*([^;]+);", section))
        product_names = re.findall(r"productName\s*=\s*([^;]+);", section)
        names.extend(value.strip().strip('"') for value in product_names)
    return unique_sorted(names)


def parse_project(project: Path, root: Path) -> dict[str, Any]:
    pbxproj = project / "project.pbxproj"
    text = read_text(pbxproj) if pbxproj.exists() else ""
    target_details = parse_native_target_details(text)
    shared_scheme_dir = project / "xcshareddata" / "xcschemes"
    user_scheme_dirs = list((project / "xcuserdata").glob("*/xcschemes")) if (project / "xcuserdata").exists() else []
    scheme_files: list[Path] = []
    if shared_scheme_dir.exists():
        scheme_files.extend(sorted(shared_scheme_dir.glob("*.xcscheme")))
    for scheme_dir in user_scheme_dirs:
        scheme_files.extend(sorted(scheme_dir.glob("*.xcscheme")))
    return {
        "path": rel(project, root),
        "name": project.name.removesuffix(".xcodeproj"),
        "project_file": rel(pbxproj, root) if pbxproj.exists() else None,
        "targets": parse_native_target_names(text),
        "target_details": target_details,
        "schemes": unique_sorted([path.stem for path in scheme_files]),
        "bundle_identifiers": parse_pbx_assignments(text, "PRODUCT_BUNDLE_IDENTIFIER"),
        "deployment_targets": parse_pbx_assignments(text, "IPHONEOS_DEPLOYMENT_TARGET"),
        "swift_versions": parse_pbx_assignments(text, "SWIFT_VERSION"),
        "info_plists": parse_pbx_assignments(text, "INFOPLIST_FILE"),
        "entitlements": parse_pbx_assignments(text, "CODE_SIGN_ENTITLEMENTS"),
    }


def parse_workspace(workspace: Path, root: Path) -> dict[str, Any]:
    contents = workspace / "contents.xcworkspacedata"
    references: list[str] = []
    if contents.exists():
        text = read_text(contents)
        references = unique_sorted(re.findall(r'location\s*=\s*"[^:]+:([^"]+)"', text))
    return {
        "path": rel(workspace, root),
        "name": workspace.name.removesuffix(".xcworkspace"),
        "references": references,
    }


def source_imports(swift_files: list[Path]) -> list[str]:
    imports: list[str] = []
    for path in swift_files:
        for match in re.finditer(r"^\s*import\s+([A-Za-z0-9_]+)", read_text(path), re.M):
            imports.append(match.group(1))
    return unique_sorted(imports)


def finding(
    *,
    severity: str,
    rule_id: str,
    message: str,
    evidence: str,
    recommendation: str,
    proof_guidance: str,
) -> dict[str, str]:
    return {
        "severity": severity,
        "code": rule_id,
        "ruleId": rule_id,
        "category": "ios-topology",
        "message": message,
        "evidence": evidence,
        "recommendation": recommendation,
        "proofGuidance": proof_guidance,
    }


def build_findings(report: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    counts = report["counts"]
    if counts["xcode_projects"] == 0 and counts["swift_packages"] == 0:
        findings.append(
            finding(
                severity="high",
                rule_id="no-build-topology",
                message="No Xcode project, workspace, or Swift package was detected. Codex cannot choose an honest build or simulator route yet.",
                evidence="Detected 0 .xcodeproj directories and 0 Package.swift files.",
                recommendation="Point ShipGuard at the iOS repository root or add the missing project/package before running build, simulator, or release proof workflows.",
                proof_guidance="Rerun shipguard ios doctor and confirm at least one Xcode project, workspace, or Swift package is reported.",
            )
        )
    if counts["xcode_projects"] == 0 and counts["swift_packages"] > 0:
        findings.append(
            finding(
                severity="review",
                rule_id="package-only",
                message="Only a Swift package was detected. Simulator proof may require a host app or generated preview host.",
                evidence=f"Detected {counts['swift_packages']} Swift package(s) and 0 Xcode projects.",
                recommendation="Name the SwiftPM validation lane explicitly and add a preview host before claiming simulator UI proof.",
                proof_guidance="Run swift test for package proof, or add a host app and rerun ios doctor before simulator workflows.",
            )
        )
    for project in report["xcode_projects"]:
        if not project["schemes"]:
            findings.append(
                finding(
                    severity="review",
                    rule_id="no-shared-schemes",
                    message=f"{project['path']} has no shared schemes. Codex may need an explicit scheme from the user.",
                    evidence=f"{project['path']} contains no xcshareddata/xcschemes entries.",
                    recommendation="Commit a shared scheme or record the exact scheme name in the task contract before build/test work.",
                    proof_guidance="Rerun ios doctor and confirm the scheme appears under the project evidence table.",
                )
            )
        if not project["deployment_targets"]:
            findings.append(
                finding(
                    severity="review",
                    rule_id="missing-deployment-target",
                    message=f"{project['path']} does not expose an iOS deployment target in parsed build settings.",
                    evidence=f"{project['path']} parsed deployment_targets is empty.",
                    recommendation="Confirm the intended minimum iOS version before modernization, API adoption, or simulator matrix claims.",
                    proof_guidance="Inspect build settings or rerun ios doctor after the deployment target is visible in the project file.",
                )
            )
        if not project["swift_versions"]:
            findings.append(
                finding(
                    severity="review",
                    rule_id="missing-swift-version",
                    message=f"{project['path']} does not expose SWIFT_VERSION in parsed build settings.",
                    evidence=f"{project['path']} parsed swift_versions is empty.",
                    recommendation="Confirm the Swift language mode before concurrency, Swift 6, or modernization planning.",
                    proof_guidance="Inspect build settings or rerun ios doctor after SWIFT_VERSION is visible in the project file.",
                )
            )
    if counts["privacy_manifests"] == 0:
        findings.append(
            finding(
                severity="review",
                rule_id="missing-privacy-manifest",
                message="No PrivacyInfo.xcprivacy file was detected. Verify whether the app or SDKs require privacy manifest coverage.",
                evidence="Detected 0 PrivacyInfo.xcprivacy files.",
                recommendation="Check privacy manifest requirements before App Store, SDK, analytics, or permission-copy work.",
                proof_guidance="Rerun ios doctor and confirm the privacy manifest path is listed, or document why this target does not require one.",
            )
        )
    if counts["test_plans"] == 0:
        findings.append(
            finding(
                severity="info",
                rule_id="no-test-plan",
                message="No .xctestplan file was detected. Codex can still build/test, but release proof should name the chosen scheme and test command.",
                evidence="Detected 0 .xctestplan files.",
                recommendation="Make the validation lane explicit in the task contract or release proof when no test plan exists.",
                proof_guidance="Record the exact xcodebuild or swift test command that proves the scoped change.",
            )
        )
    return findings


def build_next_actions(report: dict[str, Any]) -> list[str]:
    actions = [
        "Run `ios inventory` next to map permission, entitlement, StoreKit, widget, App Intent, and Live Activity surfaces.",
        "Before simulator work, choose one scheme, one simulator, one reproduction path, and one expected proof artifact.",
    ]
    if report["counts"]["xcode_projects"] > 0:
        actions.append("Use XcodeBuildMCP session defaults for the selected project/workspace, scheme, and simulator before building.")
    if report["counts"]["swift_packages"] > 0 and report["counts"]["xcode_projects"] == 0:
        actions.append("For Swift Package UI proof, use a preview host or add an app fixture before claiming simulator coverage.")
    if report["counts"]["storekit_configs"] > 0:
        actions.append("For commerce changes, require StoreKit config or sandbox-account proof before paid-access claims.")
    if report["counts"]["privacy_manifests"] > 0:
        actions.append("For privacy changes, compare permission copy, privacy manifest content, and App Store privacy claims.")
    return actions


def report_status(findings: list[dict[str, str]]) -> str:
    if any(finding["severity"] == "high" for finding in findings):
        return "blocked"
    if any(finding["severity"] == "review" for finding in findings):
        return "review"
    return "pass"


def build_report(root: Path) -> dict[str, Any]:
    files = iter_files(root)
    projects = [parse_project(path, root) for path in iter_dirs(root, ".xcodeproj")]
    workspaces = [parse_workspace(path, root) for path in iter_dirs(root, ".xcworkspace")]
    packages = [parse_package(path, root) for path in files if path.name == "Package.swift"]
    swift_files = [path for path in files if path.suffix == ".swift"]
    plists = [path for path in files if path.name.endswith(".plist")]
    entitlements = [path for path in files if path.name.endswith(".entitlements")]
    privacy_manifests = [path for path in files if path.name == "PrivacyInfo.xcprivacy"]
    test_plans = [path for path in files if path.name.endswith(".xctestplan")]
    storekit_configs = [path for path in files if path.name.endswith(".storekit")]

    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "tool": "shipguard ios doctor",
        "surface": "ShipGuard DockCheck",
        "generatedAt": utc_now(),
        "project": "<target-repo>",
        "target": {
            "root": "<target-repo>",
            "name": root.name,
            "pathRedacted": True,
        },
        "xcodebuild_available": shutil.which("xcodebuild") is not None,
        "counts": {
            "files": len(files),
            "swift_files": len(swift_files),
            "xcode_projects": len(projects),
            "xcode_workspaces": len(workspaces),
            "swift_packages": len(packages),
            "plists": len(plists),
            "entitlements": len(entitlements),
            "privacy_manifests": len(privacy_manifests),
            "test_plans": len(test_plans),
            "storekit_configs": len(storekit_configs),
        },
        "xcode_projects": projects,
        "xcode_workspaces": workspaces,
        "swift_packages": packages,
        "projects": projects,
        "packages": packages,
        "schemes": unique_sorted([scheme for project in projects for scheme in project["schemes"]]),
        "test_plans": [rel(path, root) for path in test_plans],
        "storekit_configs": [rel(path, root) for path in storekit_configs],
        "privacy_manifests": [plist_summary(path, root) for path in privacy_manifests],
        "plists": [plist_summary(path, root) for path in plists],
        "entitlements": [plist_summary(path, root) for path in entitlements],
        "swift_imports": source_imports(swift_files),
    }
    report["findings"] = build_findings(report)
    report["status"] = report_status(report["findings"])
    report["next_actions"] = build_next_actions(report)
    return report


def render_list(values: list[str]) -> str:
    if not values:
        return "-"
    return ", ".join(f"`{value}`" for value in values)


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# iOS Doctor",
        "",
        f"- Status: {report['status']}",
        f"- Project: `{report['project']}`",
        f"- Project name: `{report['target']['name']}`",
        f"- Xcode projects: {counts['xcode_projects']}",
        f"- Xcode workspaces: {counts['xcode_workspaces']}",
        f"- Swift packages: {counts['swift_packages']}",
        f"- Swift files: {counts['swift_files']}",
        f"- Test plans: {counts['test_plans']}",
        f"- StoreKit configs: {counts['storekit_configs']}",
        f"- Privacy manifests: {counts['privacy_manifests']}",
        f"- `xcodebuild` available: {str(report['xcodebuild_available']).lower()}",
        "",
        "## Xcode Projects",
        "",
        "| Project | Targets | Schemes | Deployment | Swift | Bundle IDs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for project in report["xcode_projects"]:
        lines.append(
            "| {path} | {targets} | {schemes} | {deploy} | {swift} | {bundles} |".format(
                path=f"`{project['path']}`",
                targets=render_list(project["targets"]),
                schemes=render_list(project["schemes"]),
                deploy=render_list(project["deployment_targets"]),
                swift=render_list(project["swift_versions"]),
                bundles=render_list(project["bundle_identifiers"]),
            )
        )
    if not report["xcode_projects"]:
        lines.append("| - | - | - | - | - | - |")

    lines.extend(["", "## Swift Packages", "", "| Package | Tools | iOS Platforms | Products | Targets |", "| --- | --- | --- | --- | --- |"])
    for package in report["swift_packages"]:
        lines.append(
            "| {path} | {tools} | {platforms} | {products} | {targets} |".format(
                path=f"`{package['path']}`",
                tools=f"`{package['swift_tools_version']}`" if package["swift_tools_version"] else "-",
                platforms=render_list(package["ios_platforms"]),
                products=render_list(package["products"]),
                targets=render_list(package["targets"]),
            )
        )
    if not report["swift_packages"]:
        lines.append("| - | - | - | - | - |")

    lines.extend(["", "## Project Evidence", ""])
    lines.append(f"- Workspaces: {render_list([item['path'] for item in report['xcode_workspaces']])}")
    lines.append(f"- Test plans: {render_list(report['test_plans'])}")
    lines.append(f"- StoreKit configs: {render_list(report['storekit_configs'])}")
    lines.append(f"- Privacy manifests: {render_list([item['path'] for item in report['privacy_manifests']])}")
    lines.append(f"- Swift imports: {render_list(report['swift_imports'])}")

    lines.extend(["", "## Findings", ""])
    for finding in report["findings"]:
        lines.append(f"- **{finding['severity']}** `{finding['code']}`: {finding['message']}")
    if not report["findings"]:
        lines.append("- No topology findings.")

    lines.extend(["", "## Next Codex Actions", ""])
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(out_dir: Path, report: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-doctor.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-doctor.md").write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path is not a directory: {root}")
    report = build_report(root)
    if args.out:
        write_outputs(Path(args.out).expanduser(), report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
