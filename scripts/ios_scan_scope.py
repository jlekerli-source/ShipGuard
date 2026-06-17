#!/usr/bin/env python3
"""Shared read-only scan scope helpers for iOS ShipGuard commands."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


SKIP_DIR_NAMES = {
    ".build",
    ".codex",
    ".cursor",
    ".git",
    ".github",
    ".playwright-cli",
    ".swiftpm",
    ".vscode",
    "Carthage",
    "DerivedData",
    "Pods",
    "Reports",
    "Website",
    "build",
    "coverage",
    "dist",
    "fastlane",
    "node_modules",
    "release-artifacts",
    "scratch",
    "xcuserdata",
}


@dataclass(frozen=True)
class ScanResult:
    files: list[Path]
    skipped_directories: list[str]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def should_skip_dir(path: Path) -> bool:
    return path.name in SKIP_DIR_NAMES or path.name.endswith(".xcresult")


def iter_files(root: Path, suffixes: set[str] | None = None) -> ScanResult:
    normalized_suffixes = {suffix.lower() for suffix in suffixes} if suffixes is not None else None
    files: list[Path] = []
    skipped: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        kept_dirs: list[str] = []
        for dirname in dirnames:
            candidate = current / dirname
            if should_skip_dir(candidate):
                skipped.append(rel(candidate, root))
            else:
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            path = current / filename
            if normalized_suffixes is not None and path.suffix.lower() not in normalized_suffixes:
                continue
            files.append(path)
    return ScanResult(
        files=sorted(files, key=lambda item: rel(item, root)),
        skipped_directories=sorted(set(skipped)),
    )


def iter_dirs(root: Path, suffix: str) -> ScanResult:
    matches: list[Path] = []
    skipped: list[str] = []
    for dirpath, dirnames, _filenames in os.walk(root):
        current = Path(dirpath)
        kept_dirs: list[str] = []
        for dirname in dirnames:
            candidate = current / dirname
            if should_skip_dir(candidate):
                skipped.append(rel(candidate, root))
            else:
                kept_dirs.append(dirname)
                if candidate.name.endswith(suffix):
                    matches.append(candidate)
        dirnames[:] = kept_dirs
    return ScanResult(
        files=sorted(matches, key=lambda item: rel(item, root)),
        skipped_directories=sorted(set(skipped)),
    )


def summary(result: ScanResult, *, max_directories: int = 20) -> dict[str, object]:
    return {
        "filesScanned": len(result.files),
        "skippedDirectoryCount": len(result.skipped_directories),
        "skippedDirectories": result.skipped_directories[:max_directories],
        "skippedDirectoryListTruncated": len(result.skipped_directories) > max_directories,
    }
