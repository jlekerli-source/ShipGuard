#!/usr/bin/env python3
"""Shared read-only scan scope helpers for iOS ShipGuard commands."""

from __future__ import annotations

import os
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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

DEFAULT_MAX_TEXT_BYTES = 96 * 1024
DEFAULT_READ_TIMEOUT_SECONDS = 0.05


def max_text_bytes() -> int:
    raw = os.environ.get("SHIPGUARD_IOS_SCAN_MAX_TEXT_BYTES", "").strip()
    if not raw:
        return DEFAULT_MAX_TEXT_BYTES
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_TEXT_BYTES
    return max(16 * 1024, value)


def read_timeout_seconds() -> float:
    raw = os.environ.get("SHIPGUARD_IOS_SCAN_READ_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return DEFAULT_READ_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_READ_TIMEOUT_SECONDS
    return max(0.01, value)


@dataclass(frozen=True)
class ScanResult:
    files: list[Path]
    skipped_directories: list[str]


@dataclass(frozen=True)
class TextRead:
    text: str
    truncated: bool
    size_bytes: int
    bytes_read: int
    omitted: bool = False
    timed_out: bool = False


class TextReadTimeout(Exception):
    pass


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


def read_text_limited(path: Path, *, max_bytes: int | None = None) -> TextRead:
    limit = max_text_bytes() if max_bytes is None else max(16 * 1024, max_bytes)
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    read_large = os.environ.get("SHIPGUARD_IOS_SCAN_READ_LARGE_TEXT", "").strip().lower() in {"1", "true", "yes"}
    if size > limit and not read_large:
        return TextRead(text="", truncated=True, size_bytes=size, bytes_read=0, omitted=True)
    timeout = read_timeout_seconds()
    old_handler = signal.getsignal(signal.SIGALRM)

    def on_timeout(_signum: int, _frame: object) -> None:
        raise TextReadTimeout()

    try:
        signal.signal(signal.SIGALRM, on_timeout)
        signal.setitimer(signal.ITIMER_REAL, timeout)
        with path.open("rb") as handle:
            payload = handle.read(limit + 1)
    except (TextReadTimeout, TimeoutError):
        return TextRead(text="", truncated=True, size_bytes=size, bytes_read=0, omitted=True, timed_out=True)
    except OSError:
        return TextRead(text="", truncated=True, size_bytes=size, bytes_read=0, omitted=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
    truncated = len(payload) > limit
    if truncated:
        payload = payload[:limit]
    return TextRead(
        text=payload.decode("utf-8", errors="ignore"),
        truncated=truncated or (size > limit and len(payload) >= limit),
        size_bytes=size,
        bytes_read=len(payload),
        omitted=False,
        timed_out=False,
    )


def large_text_read_mode() -> str:
    read_large = os.environ.get("SHIPGUARD_IOS_SCAN_READ_LARGE_TEXT", "").strip().lower() in {"1", "true", "yes"}
    return "sample-large-files" if read_large else "omit-large-files"


def truncated_summary(
    paths: list[Path],
    root: Path,
    *,
    omitted_paths: list[Path] | None = None,
    timed_out_paths: list[Path] | None = None,
    max_files: int = 20,
) -> dict[str, Any]:
    omitted_paths = omitted_paths or []
    timed_out_paths = timed_out_paths or []
    return {
        "truncatedTextFileCount": len(paths),
        "truncatedTextFiles": [rel(path, root) for path in paths[:max_files]],
        "truncatedTextFileListTruncated": len(paths) > max_files,
        "omittedLargeTextFileCount": len(omitted_paths),
        "omittedLargeTextFiles": [rel(path, root) for path in omitted_paths[:max_files]],
        "omittedLargeTextFileListTruncated": len(omitted_paths) > max_files,
        "timedOutTextFileCount": len(timed_out_paths),
        "timedOutTextFiles": [rel(path, root) for path in timed_out_paths[:max_files]],
        "timedOutTextFileListTruncated": len(timed_out_paths) > max_files,
        "textBytesPerFileLimit": max_text_bytes(),
        "textReadTimeoutSeconds": read_timeout_seconds(),
        "largeTextReadMode": large_text_read_mode(),
    }


def summary(result: ScanResult, *, max_directories: int = 20) -> dict[str, object]:
    return {
        "filesScanned": len(result.files),
        "skippedDirectoryCount": len(result.skipped_directories),
        "skippedDirectories": result.skipped_directories[:max_directories],
        "skippedDirectoryListTruncated": len(result.skipped_directories) > max_directories,
    }


def summary_with_text_limits(
    result: ScanResult,
    root: Path,
    *,
    max_directories: int = 20,
    truncated_text_files: list[Path] | None = None,
    omitted_large_text_files: list[Path] | None = None,
    timed_out_text_files: list[Path] | None = None,
) -> dict[str, object]:
    base = summary(result, max_directories=max_directories)
    base.update(
        truncated_summary(
            truncated_text_files or [],
            root,
            omitted_paths=omitted_large_text_files or [],
            timed_out_paths=timed_out_text_files or [],
        )
    )
    return base
