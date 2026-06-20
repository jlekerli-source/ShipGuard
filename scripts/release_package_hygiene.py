#!/usr/bin/env python3
"""Read-only hygiene report for ShipGuard release packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown


SCHEMA_VERSION = 1
TOOL = "shipguard release-package hygiene"
SURFACE = "ShipGuard Release Package Lineage Hygiene"
VERSION_RE = re.compile(r"shipguard-v(?P<version>\d+\.\d+\.\d+)\.tar\.gz$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def release_version_from_path(path: Path) -> str | None:
    match = VERSION_RE.search(path.name)
    return match.group("version") if match else None


def rel_path(path: Path, root: Path, shareable: bool) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name if shareable else str(path)


def forbidden_member_reason(name: str) -> tuple[str, str] | None:
    parts = PurePosixPath(name).parts
    basename = PurePosixPath(name).name
    if "__MACOSX" in parts:
        return "appledouble-macosx-directory", "__MACOSX generated metadata directory"
    if any(part.startswith("._") for part in parts):
        return "appledouble-sidecar", "AppleDouble generated metadata sidecar"
    if basename == ".DS_Store":
        return "finder-metadata", "Finder .DS_Store metadata"
    if basename.endswith(".pyc") or "__pycache__" in parts:
        return "python-bytecode-cache", "Python bytecode/cache artifact"
    if ".git" in parts:
        return "git-directory", "Git metadata directory"
    if ".cache" in parts or "DerivedData" in parts:
        return "build-cache-artifact", "local cache/build artifact"
    return None


def unsafe_path_reason(name: str) -> tuple[str, str] | None:
    path = PurePosixPath(name)
    if path.is_absolute():
        return "absolute-path-member", "archive member uses an absolute path"
    if any(part == ".." for part in path.parts):
        return "path-traversal-member", "archive member can escape the extract destination"
    return None


def member_finding(tarball: Path, version: str | None, severity: str, rule_id: str, member: str, summary: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "category": "archive-member",
        "ruleId": rule_id,
        "tarball": tarball.name,
        "version": version,
        "member": member,
        "evidence": summary,
        "recommendation": "Rebuild the release package with metadata-disabled packaging, then rerun package release proof and this hygiene report.",
        "proofGuidance": "Run ./scripts/package_release.sh, ./tests/package_release_test.sh, and shipguard release-package hygiene against the rebuilt tarball.",
    }


def scan_tarball(tarball: Path, root: Path, shareable: bool) -> dict[str, Any]:
    version = release_version_from_path(tarball)
    findings: list[dict[str, Any]] = []
    package_roots: set[str] = set()
    member_count = 0
    install_script_roots: set[str] = set()
    bin_roots: set[str] = set()
    version_roots: set[str] = set()

    try:
        with tarfile.open(tarball, "r:gz") as archive:
            for member in archive.getmembers():
                member_count += 1
                name = member.name
                parts = PurePosixPath(name).parts
                if parts:
                    package_roots.add(parts[0])
                path_reason = unsafe_path_reason(name)
                if path_reason:
                    findings.append(member_finding(tarball, version, "blocked", path_reason[0], name, path_reason[1]))
                forbidden_reason = forbidden_member_reason(name)
                if forbidden_reason:
                    findings.append(member_finding(tarball, version, "blocked", forbidden_reason[0], name, forbidden_reason[1]))
                if member.issym() or member.islnk() or member.isdev():
                    findings.append(
                        member_finding(
                            tarball,
                            version,
                            "blocked",
                            "unsafe-link-or-device",
                            name,
                            "archive member is a symbolic link, hard link, or device",
                        )
                    )
                suffix = "/".join(parts[1:]) if len(parts) > 1 else ""
                if suffix == "scripts/install.sh":
                    install_script_roots.add(parts[0])
                if suffix == "bin/shipguard":
                    bin_roots.add(parts[0])
                if suffix == "VERSION":
                    version_roots.add(parts[0])
    except (tarfile.TarError, OSError) as exc:
        findings.append(
            {
                "severity": "blocked",
                "category": "archive-read",
                "ruleId": "tarball-unreadable",
                "tarball": tarball.name,
                "version": version,
                "member": None,
                "evidence": f"could not read tarball: {exc}",
                "recommendation": "Rebuild the package and verify that it is a valid .tar.gz archive.",
                "proofGuidance": "Run ./scripts/package_release.sh and ./tests/package_release_test.sh.",
            }
        )

    expected_root = f"shipguard-v{version}" if version else None
    if expected_root and expected_root not in package_roots:
        findings.append(
            {
                "severity": "review",
                "category": "package-root",
                "ruleId": "expected-root-missing",
                "tarball": tarball.name,
                "version": version,
                "member": None,
                "evidence": f"expected package root {expected_root!r} was not found",
                "recommendation": "Package release tarballs should extract into one shipguard-v<version> directory.",
                "proofGuidance": "Inspect the package list with tar -tzf and rebuild with ./scripts/package_release.sh.",
            }
        )
    viable_roots = install_script_roots & bin_roots & version_roots
    if not viable_roots:
        findings.append(
            {
                "severity": "blocked",
                "category": "package-root",
                "ruleId": "installable-root-missing",
                "tarball": tarball.name,
                "version": version,
                "member": None,
                "evidence": "no package root contains scripts/install.sh, bin/shipguard, and VERSION",
                "recommendation": "Rebuild the package from a complete ShipGuard checkout.",
                "proofGuidance": "Run ./scripts/package_release.sh and ./tests/package_release_test.sh.",
            }
        )

    severity_rank = {"blocked": 2, "review": 1}
    worst = "pass"
    for finding in findings:
        if severity_rank.get(finding["severity"], 0) > severity_rank.get(worst, 0):
            worst = finding["severity"]

    return {
        "path": rel_path(tarball, root, shareable),
        "name": tarball.name,
        "version": version,
        "status": worst,
        "memberCount": member_count,
        "packageRoots": sorted(package_roots),
        "installableRoots": sorted(viable_roots),
        "findings": findings,
        "installRiskSummary": "safe to pass into install/upgrade proof" if worst == "pass" else "do not use as install/upgrade proof until rebuilt or replaced",
    }


def collect_tarballs(root: Path, dirs: list[Path], assets: list[Path], tarballs: list[Path]) -> list[Path]:
    found: list[Path] = []
    for explicit in tarballs:
        found.append(explicit)
    scan_dirs = list(dirs) + list(assets)
    if not found and not scan_dirs:
        scan_dirs.append(root / "dist")
    for directory in scan_dirs:
        if directory.is_dir():
            found.extend(sorted(directory.glob("shipguard-v*.tar.gz")))
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in found:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(path)
    return deduped


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    tarballs = collect_tarballs(
        root,
        [Path(item) for item in args.dir],
        [Path(item) for item in args.assets],
        [Path(item) for item in args.tarball],
    )
    scans = [scan_tarball(path, root, args.shareable) for path in tarballs]
    findings = [finding for scan in scans for finding in scan["findings"]]
    blocked = [finding for finding in findings if finding["severity"] == "blocked"]
    review = [finding for finding in findings if finding["severity"] == "review"]
    status = "blocked" if blocked else "review" if review or not scans else "pass"
    version = read_text(root / "VERSION")
    current_candidates = [scan for scan in scans if scan.get("version") == version]
    safe_current = next((scan for scan in current_candidates if scan["status"] == "pass"), None)
    affected_versions = sorted({finding["version"] for finding in findings if finding.get("version")})
    grouped_rules: dict[str, dict[str, Any]] = {}
    for finding in findings:
        rule_id = finding["ruleId"]
        entry = grouped_rules.setdefault(
            rule_id,
            {
                "ruleId": rule_id,
                "severity": finding["severity"],
                "count": 0,
                "tarballs": set(),
                "versions": set(),
                "exampleMembers": [],
                "recommendation": finding["recommendation"],
            },
        )
        entry["count"] += 1
        entry["tarballs"].add(finding["tarball"])
        if finding.get("version"):
            entry["versions"].add(finding["version"])
        if finding.get("member") and len(entry["exampleMembers"]) < 5:
            entry["exampleMembers"].append(finding["member"])
    rule_summary = []
    for entry in grouped_rules.values():
        rule_summary.append(
            {
                "ruleId": entry["ruleId"],
                "severity": entry["severity"],
                "count": entry["count"],
                "tarballs": sorted(entry["tarballs"]),
                "versions": sorted(entry["versions"]),
                "exampleMembers": entry["exampleMembers"],
                "recommendation": entry["recommendation"],
            }
        )
    rule_summary.sort(key=lambda item: (-item["count"], item["ruleId"]))

    result_ux = build_result_ux(
        status=status,
        summary=(
            f"{len(scans)} release package(s) scanned; {len(blocked)} blocked finding(s), {len(review)} review finding(s)."
            if scans
            else "No ShipGuard release tarballs were found to scan."
        ),
        proof_source="read-only tarball member inspection; no extraction or package rewrite",
        why_it_matters="LaunchKey install and upgrade proof should fail early on unsafe release packages instead of discovering generated metadata during package validation.",
        next_command=(
            "./scripts/package_release.sh && ./tests/package_release_test.sh && ./bin/shipguard release-package hygiene --path . --out /tmp/shipguard-package-hygiene --shareable"
            if status != "pass"
            else "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --package-tarball dist/shipguard-v<VERSION>.tar.gz --shareable"
        ),
        next_action_summary=(
            blocked[0]["evidence"]
            if blocked
            else "Use the safe package baseline as input to LaunchKey install or upgrade proof."
        ),
    )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": status,
        "path": "." if args.shareable else str(root),
        "summary": {
            "tarballsScanned": len(scans),
            "blockedFindings": len(blocked),
            "reviewFindings": len(review),
            "affectedVersions": affected_versions,
            "currentVersion": version,
            "safeCurrentBaseline": safe_current["name"] if safe_current else None,
        },
        "scannedTarballs": scans,
        "findings": findings,
        "ruleSummary": rule_summary,
        "repairPlan": [
            {
                "step": "Rebuild package artifacts from a clean checkout with metadata-disabled packaging.",
                "command": "./scripts/package_release.sh",
            },
            {
                "step": "Run package proof before using tarballs in LaunchKey install or upgrade proof.",
                "command": "./tests/package_release_test.sh",
            },
            {
                "step": "Rerun read-only package hygiene against the rebuilt tarballs.",
                "command": "./bin/shipguard release-package hygiene --path . --out /tmp/shipguard-package-hygiene --shareable",
            },
        ],
        "scopeBoundary": {
            "readOnly": True,
            "doesNotExtractTarballs": True,
            "doesNotRewriteHistoricalAssets": True,
            "doesNotClaimHistoricalReleaseRepair": True,
            "privateAppBoundary": "This report is ShipGuard package QA only; it does not validate or modify target apps.",
        },
        "nonClaims": [
            "This report does not rewrite or delete historical release assets.",
            "This report does not prove GitHub release replacement or stable-v4 publication.",
            "This report does not validate private app source or app behavior.",
        ],
        "reportQualityQuestions": [
            "Does the report name the exact unsafe archive member before install or upgrade proof runs?",
            "Does it separate historical affected versions from the safe current package baseline?",
            "Does it give a concrete rebuild and proof command without claiming old assets were repaired?",
        ],
        "resultUX": result_ux,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Release Package Lineage Hygiene",
        "",
        *render_result_markdown(report["resultUX"]),
        "",
        "## Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Tarballs scanned: {report['summary']['tarballsScanned']}",
        f"- Blocked findings: {report['summary']['blockedFindings']}",
        f"- Review findings: {report['summary']['reviewFindings']}",
        f"- Affected versions: {', '.join(report['summary']['affectedVersions']) or 'none'}",
        f"- Safe current baseline: {report['summary']['safeCurrentBaseline'] or 'not proven'}",
        "",
        "## Tarballs",
        "",
        "| Tarball | Version | Status | Members | Install risk |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for scan in report["scannedTarballs"]:
        lines.append(
            f"| `{scan['name']}` | `{scan.get('version') or 'unknown'}` | `{scan['status']}` | {scan['memberCount']} | {scan['installRiskSummary']} |"
        )
    if not report["scannedTarballs"]:
        lines.append("| none | n/a | `review` | 0 | no package input found |")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["### Rule Summary", ""])
        lines.extend(["| Rule | Severity | Count | Versions | Examples |", "| --- | --- | ---: | --- | --- |"])
        for item in report.get("ruleSummary", []):
            lines.append(
                f"| `{item['ruleId']}` | `{item['severity']}` | {item['count']} | {', '.join(item['versions']) or 'n/a'} | {', '.join(f'`{member}`' for member in item['exampleMembers']) or 'n/a'} |"
            )
        lines.extend(["", "### Finding Details", ""])
        lines.extend(["| Severity | Rule | Tarball | Member | Evidence |", "| --- | --- | --- | --- | --- |"])
        for finding in report["findings"]:
            lines.append(
                f"| `{finding['severity']}` | `{finding['ruleId']}` | `{finding['tarball']}` | `{finding.get('member') or 'n/a'}` | {finding['evidence']} |"
            )
    else:
        lines.append("No archive hygiene findings.")
    lines.extend(["", "## Repair Plan", ""])
    for item in report["repairPlan"]:
        lines.append(f"- {item['step']} `{item['command']}`")
    lines.extend(["", "## Scope Boundary", ""])
    for key, value in report["scopeBoundary"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Non-Claims", ""])
    for item in report["nonClaims"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Report-Quality Questions", ""])
    for item in report["reportQualityQuestions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan ShipGuard release tarballs for package-lineage hygiene problems.")
    parser.add_argument("--path", default=".", help="ShipGuard repository root.")
    parser.add_argument("--out", required=False, help="Output directory.")
    parser.add_argument("--dir", action="append", default=[], help="Directory containing shipguard-v*.tar.gz files. Defaults to <path>/dist.")
    parser.add_argument("--assets", action="append", default=[], help="Downloaded release asset directory to scan for shipguard-v*.tar.gz.")
    parser.add_argument("--tarball", action="append", default=[], help="Explicit tarball to scan; can be repeated.")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths from report fields.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of writing files.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout instead of writing files.")
    args = parser.parse_args()

    report = build_report(args)
    markdown = render_markdown(report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)
    else:
        if not args.out:
            parser.error("--out is required unless --json or --markdown is used")
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "release-package-hygiene.json"
        markdown_path = out_dir / "release-package-hygiene.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        markdown_path.write_text(markdown, encoding="utf-8")
        print(f"wrote: {json_path}")
        print(f"wrote: {markdown_path}")
        print(f"status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
