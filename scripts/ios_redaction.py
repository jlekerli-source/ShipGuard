#!/usr/bin/env python3
"""Redact sensitive iOS report artifacts before sharing with Codex or humans."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Pattern


SCHEMA_VERSION = 1
TEXT_SUFFIXES = {
    ".entitlements",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".pbxproj",
    ".plist",
    ".swift",
    ".txt",
    ".xcconfig",
    ".xml",
    ".yaml",
    ".yml",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-redaction: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Redact local paths, Apple team IDs, bundle IDs, tokens, emails, accounts, and device IDs from iOS report files."
    )
    parser.add_argument("--in", dest="input_path", required=True, help="Input report file or directory")
    parser.add_argument("--out", dest="output_path", required=True, help="Output redacted file or directory")
    parser.add_argument("--report", help="Redaction report JSON path; defaults to <out>/ios-redaction.json for directories")
    parser.add_argument(
        "--private-term",
        action="append",
        default=[],
        help="Additional literal term to redact; may be provided more than once",
    )
    return parser.parse_args()


class Redactor:
    def __init__(self, private_terms: list[str]) -> None:
        self.private_terms = [term for term in private_terms if term]
        self.counts: dict[str, int] = {
            "private_term": 0,
            "email": 0,
            "bearer_token": 0,
            "secret_assignment": 0,
            "api_token": 0,
            "jwt_token": 0,
            "hex_token": 0,
            "local_path": 0,
            "apple_team_id": 0,
            "bundle_id": 0,
            "apple_account": 0,
            "device_id": 0,
        }

    def _replace(self, text: str, rule_id: str, pattern: Pattern[str], replacement: str | Callable[[re.Match[str]], str]) -> str:
        def repl(match: re.Match[str]) -> str:
            self.counts[rule_id] += 1
            if callable(replacement):
                return replacement(match)
            return replacement

        return pattern.sub(repl, text)

    def redact(self, text: str) -> str:
        for term in self.private_terms:
            text = self._replace(
                text,
                "private_term",
                re.compile(re.escape(term), re.IGNORECASE),
                "[REDACTED_PRIVATE_TERM]",
            )

        text = self._replace(
            text,
            "apple_account",
            re.compile(
                r"((?:APPLE_ID|APPLE_ACCOUNT|ASC_ISSUER_ID|App Store Connect ID|Apple ID|Account)\s*[:=]\s*)([\"']?)[A-Za-z0-9._%+\-@]{3,}([\"']?)",
                re.IGNORECASE,
            ),
            lambda match: f"{match.group(1)}{match.group(2)}[REDACTED_ACCOUNT]{match.group(3)}",
        )
        text = self._replace(
            text,
            "email",
            re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
            "[REDACTED_EMAIL]",
        )
        text = self._replace(
            text,
            "bearer_token",
            re.compile(r"\b(Authorization\s*:\s*Bearer\s+)[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE),
            lambda match: f"{match.group(1)}[REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "bearer_token",
            re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
            "Bearer [REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "api_token",
            re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
            "[REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "api_token",
            re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
            "[REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "secret_assignment",
            re.compile(
                r"((?:\"|')?[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*(?:\"|')?\s*[:=]\s*)([\"']?)([^\s\"',}]+)([\"']?)",
                re.IGNORECASE,
            ),
            lambda match: f"{match.group(1)}{match.group(2)}[REDACTED_TOKEN]{match.group(4)}",
        )
        text = self._replace(
            text,
            "jwt_token",
            re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
            "[REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "hex_token",
            re.compile(r"\b[a-f0-9]{32,}\b", re.IGNORECASE),
            "[REDACTED_TOKEN]",
        )
        text = self._replace(
            text,
            "local_path",
            re.compile(r"(?<![\w])/(?:Users|home)/[^\s\"'`,)]+"),
            "[REDACTED_LOCAL_PATH]",
        )
        text = self._replace(
            text,
            "local_path",
            re.compile(r"(?<![\w])/(?:private/var/folders|var/folders)/[^\s\"'`,)]+"),
            "[REDACTED_LOCAL_PATH]",
        )
        text = self._replace(
            text,
            "local_path",
            re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s\"'`,)]+(?:\\[^\\\s\"'`,)]+)*"),
            "[REDACTED_LOCAL_PATH]",
        )
        text = self._replace(
            text,
            "apple_team_id",
            re.compile(
                r"((?:DEVELOPMENT_TEAM|TEAM_ID|Team ID|teamIdentifier|com\.apple\.developer\.team-identifier)\s*[:=]\s*)([A-Z0-9]{10})\b",
                re.IGNORECASE,
            ),
            lambda match: f"{match.group(1)}[REDACTED_TEAM_ID]",
        )
        text = self._replace(
            text,
            "apple_team_id",
            re.compile(
                r"(<key>com\.apple\.developer\.team-identifier</key>\s*<string>)([^<]+)(</string>)",
                re.IGNORECASE,
            ),
            lambda match: f"{match.group(1)}[REDACTED_TEAM_ID]{match.group(3)}",
        )
        text = self._replace(
            text,
            "bundle_id",
            re.compile(
                r"((?:\"|')?(?:PRODUCT_BUNDLE_IDENTIFIER|CFBundleIdentifier|bundleIdentifier|bundle_id|Bundle ID|Bundle Identifier)(?:\"|')?\s*[:=]\s*)([\"']?)([A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)+)([\"']?)",
                re.IGNORECASE,
            ),
            lambda match: f"{match.group(1)}{match.group(2)}[REDACTED_BUNDLE_ID]{match.group(4)}",
        )
        text = self._replace(
            text,
            "bundle_id",
            re.compile(r"(<key>CFBundleIdentifier</key>\s*<string>)([^<]+)(</string>)", re.IGNORECASE),
            lambda match: f"{match.group(1)}[REDACTED_BUNDLE_ID]{match.group(3)}",
        )
        text = self._replace(
            text,
            "device_id",
            re.compile(r"((?:UDID|Device ID|deviceIdentifier)\s*[:=]\s*)([A-Fa-f0-9-]{20,})", re.IGNORECASE),
            lambda match: f"{match.group(1)}[REDACTED_DEVICE_ID]",
        )
        return text


def risk_patterns(private_terms: list[str]) -> list[tuple[str, Pattern[str]]]:
    patterns: list[tuple[str, Pattern[str]]] = [
        ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
        ("secret_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+(?!\[REDACTED_TOKEN\])[A-Za-z0-9._~+/=-]{16,})\b")),
        (
            "secret_assignment",
            re.compile(
                r"(?:\"|')?[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z0-9_]*(?:\"|')?\s*[:=]\s*(?![\"']?\[REDACTED_TOKEN\])\S+",
                re.IGNORECASE,
            ),
        ),
        ("hex_token", re.compile(r"\b[a-f0-9]{32,}\b", re.IGNORECASE)),
        ("local_path", re.compile(r"(?<![\w])/(?:Users|home|private/var/folders|var/folders)/(?!\[REDACTED_LOCAL_PATH\])[^\s\"'`,)]+")),
        (
            "windows_user_path",
            re.compile(r"\b[A-Za-z]:\\Users\\(?!\[REDACTED_LOCAL_PATH\])[^\\\s\"'`,)]+(?:\\[^\\\s\"'`,)]+)*"),
        ),
        (
            "apple_team_id",
            re.compile(
                r"(?:DEVELOPMENT_TEAM|TEAM_ID|Team ID|teamIdentifier|com\.apple\.developer\.team-identifier)\s*[:=]\s*(?!\[REDACTED_TEAM_ID\])[A-Z0-9]{10}\b",
                re.IGNORECASE,
            ),
        ),
        (
            "bundle_id",
            re.compile(
                r"(?:PRODUCT_BUNDLE_IDENTIFIER|CFBundleIdentifier|bundleIdentifier|bundle_id|Bundle ID|Bundle Identifier)(?:\"|')?\s*[:=]\s*(?:\"|')?(?!\[REDACTED_BUNDLE_ID\])[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)+",
                re.IGNORECASE,
            ),
        ),
        (
            "apple_account",
            re.compile(
                r"(?:APPLE_ID|APPLE_ACCOUNT|ASC_ISSUER_ID|App Store Connect ID|Apple ID|Account)\s*[:=]\s*(?:\"|')?(?!\[REDACTED_ACCOUNT\])[A-Za-z0-9._%+\-@]{3,}",
                re.IGNORECASE,
            ),
        ),
        ("device_id", re.compile(r"(?:UDID|Device ID|deviceIdentifier)\s*[:=]\s*(?!\[REDACTED_DEVICE_ID\])[A-Fa-f0-9-]{20,}", re.IGNORECASE)),
    ]
    for term in private_terms:
        if term:
            patterns.append(("private_term", re.compile(re.escape(term), re.IGNORECASE)))
    return patterns


def remaining_risks(text: str, private_terms: list[str]) -> list[dict[str, int]]:
    risks: list[dict[str, int]] = []
    for risk_id, pattern in risk_patterns(private_terms):
        count = len(pattern.findall(text))
        if count:
            risks.append({"id": risk_id, "count": count})
    return risks


def sanitize_report_value(value: str, private_terms: list[str]) -> str:
    text = value
    for term in private_terms:
        if term:
            text = re.sub(re.escape(term), "[REDACTED_PRIVATE_TERM]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", text)
    text = re.sub(r"(?<![\w])/(?:Users|home|private/var/folders|var/folders)/[^\s\"'`,)]+", "[REDACTED_LOCAL_PATH]", text)
    text = re.sub(r"\b[A-Za-z]:\\Users\\[^\\\s\"'`,)]+(?:\\[^\\\s\"'`,)]+)*", "[REDACTED_LOCAL_PATH]", text)
    text = re.sub(r"\b[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+){2,}\b", "[REDACTED_BUNDLE_ID]", text)
    text = re.sub(r"\b[A-Z0-9]{10}\b", "[REDACTED_TEAM_ID]", text)
    return text


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_supported_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {"project.pbxproj", "Package.swift"}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def process_file(input_file: Path, output_file: Path, private_terms: list[str], display_name: str) -> dict[str, Any]:
    redactor = Redactor(private_terms)
    source = read_text(input_file)
    redacted = redactor.redact(source)
    risks = remaining_risks(redacted, private_terms)
    write_text(output_file, redacted)
    return {
        "input": sanitize_report_value(display_name, private_terms),
        "output": sanitize_report_value(output_file.name, private_terms),
        "status": "pass" if not risks else "blocked",
        "totalReplacements": sum(redactor.counts.values()),
        "replacements": redactor.counts,
        "remainingRisks": risks,
    }


def safe_output_for(input_path: Path, output_path: Path) -> None:
    in_resolved = input_path.resolve(strict=False)
    out_resolved = output_path.resolve(strict=False)
    if in_resolved == out_resolved:
        fail("--out must be different from --in")
    if input_path.is_dir():
        try:
            out_resolved.relative_to(in_resolved)
        except ValueError:
            return
        fail("--out must not be inside the input directory")


def process_directory(input_dir: Path, output_dir: Path, private_terms: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    files: list[dict[str, Any]] = []
    skipped: list[str] = []
    for path in sorted(input_dir.rglob("*"), key=lambda item: rel(item, input_dir)):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(input_dir)
        if not is_supported_text_file(path):
            skipped.append(sanitize_report_value(relative.as_posix(), private_terms))
            continue
        output_file = output_dir / relative
        files.append(process_file(path, output_file, private_terms, relative.as_posix()))
    return files, skipped


def build_report(
    input_path: Path,
    output_path: Path,
    files: list[dict[str, Any]],
    skipped: list[str],
    private_terms: list[str],
) -> dict[str, Any]:
    totals = {rule: 0 for rule in Redactor(private_terms).counts}
    remaining: dict[str, int] = {}
    for file_report in files:
        for rule, count in file_report["replacements"].items():
            totals[rule] = totals.get(rule, 0) + int(count)
        for risk in file_report["remainingRisks"]:
            remaining[risk["id"]] = remaining.get(risk["id"], 0) + int(risk["count"])
    remaining_risks = [{"id": risk_id, "count": count} for risk_id, count in sorted(remaining.items()) if count]
    total_replacements = sum(totals.values())
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios redact",
        "generatedAt": utc_now(),
        "status": "pass" if not remaining_risks else "blocked",
        "inputKind": "directory" if input_path.is_dir() else "file",
        "inputName": sanitize_report_value(input_path.name, private_terms),
        "outputName": sanitize_report_value(output_path.name, private_terms),
        "privateTermsChecked": len(private_terms),
        "filesProcessed": len(files),
        "filesSkipped": len(skipped),
        "totalReplacements": total_replacements,
        "totals": totals,
        "remainingRiskCount": sum(risk["count"] for risk in remaining_risks),
        "remainingRisks": remaining_risks,
        "files": files,
        "skippedFiles": skipped,
    }


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    private_terms = list(args.private_term)

    if not input_path.exists():
        fail(f"input not found: {input_path}")
    safe_output_for(input_path, output_path)

    if input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        files, skipped = process_directory(input_path, output_path, private_terms)
        report_path = Path(args.report) if args.report else output_path / "ios-redaction.json"
    else:
        if input_path.is_symlink() or not input_path.is_file():
            fail(f"input is not a regular file: {input_path}")
        files = [process_file(input_path, output_path, private_terms, input_path.name)]
        skipped: list[str] = []
        report_path = Path(args.report) if args.report else output_path.parent / "ios-redaction.json"

    report = build_report(input_path, output_path, files, skipped, private_terms)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote: {output_path}")
    print(f"wrote: {report_path}")
    print(f"status: {report['status']}")
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        fail(str(exc))
