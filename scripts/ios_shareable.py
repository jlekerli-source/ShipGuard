#!/usr/bin/env python3
"""Helpers for path-safe ShipGuard product-QA reports."""

from __future__ import annotations

import re
from typing import Any


LOCAL_PATH_VALUE_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:Users|private/tmp|var/folders)/[^\s`'\"),]+")
TOKEN_VALUE_RE = re.compile(
    r"(?i)\b(?:Bearer\s+[A-Za-z0-9._~+/=-]{12,}|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:SHIPGUARD_DEVSPACE_TOKEN|OPENAI_API_KEY|CODEXPRO_HTTP_TOKEN|CLOUDFLARE_TOKEN|NGROK_AUTHTOKEN)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{12,}"
)
PATHISH_RE = re.compile(r"\b([A-Z][A-Za-z0-9_-]{2,})(?=/[A-Za-z0-9_.-]+)")
PROJECT_RE = re.compile(r"\b([A-Z][A-Za-z0-9_-]{2,})(?:\.xcodeproj|\.xcworkspace)\b")
BUNDLE_ID_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+){2,}\b")

GENERIC_PATH_ROOTS = {
    "App",
    "Assets",
    "Config",
    "Core",
    "Docs",
    "Extensions",
    "Features",
    "Fixtures",
    "Package",
    "Packages",
    "Plugins",
    "Resources",
    "Scripts",
    "Shared",
    "Sources",
    "Support",
    "Tests",
    "Views",
    "Website",
}
GENERIC_TERMS = GENERIC_PATH_ROOTS | {
    "Debug",
    "Release",
    "Swift",
    "SwiftUI",
    "UIKit",
    "WidgetKit",
    "StoreKit",
    "CoreML",
    "Foundation",
    "ShipGuard",
    "Codex",
    "Demo",
}
DEFAULT_PRIVATE_TERMS = ("Ringly", "Ilmify", "InweFi")


def _walk(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, dict):
        for item in value.values():
            values.extend(_walk(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(_walk(item))
    return values


def _add_term(terms: set[str], value: object) -> None:
    text = str(value or "").strip()
    if not text or text.startswith("<") or text in GENERIC_TERMS:
        return
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "", text)
    if len(cleaned) < 3 or cleaned in GENERIC_TERMS:
        return
    if not re.search(r"[A-Za-z]", cleaned):
        return
    terms.add(cleaned)
    for suffix in ("UITests", "Tests", "WatchExtension", "Watch", "Extension"):
        if cleaned.endswith(suffix) and len(cleaned) > len(suffix) + 2:
            _add_term(terms, cleaned[: -len(suffix)])


def collect_private_terms(report: Any) -> list[str]:
    terms: set[str] = set(DEFAULT_PRIVATE_TERMS)

    def collect_from_known_fields(item: Any) -> None:
        if not isinstance(item, dict):
            return
        for key in ("targetNames", "targets", "bundleIds", "xcodeProjects"):
            value = item.get(key)
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        _add_term(terms, entry.get("name"))
                    else:
                        _add_term(terms, entry)
            elif isinstance(value, str):
                _add_term(terms, value)

    for item in _walk(report):
        collect_from_known_fields(item)
        if not isinstance(item, str):
            continue
        for match in PROJECT_RE.finditer(item):
            _add_term(terms, match.group(1))
        if any(suffix in item for suffix in (".swift", ".xcodeproj", ".xcworkspace", ".plist", ".storekit", ".entitlements")):
            for match in PATHISH_RE.finditer(item):
                _add_term(terms, match.group(1))
        for bundle in BUNDLE_ID_RE.findall(item):
            for component in bundle.split("."):
                if component and component[0].isupper():
                    _add_term(terms, component)

    return sorted(terms, key=lambda term: (-len(term), term.lower()))


def redact_text(value: object, *, private_terms: list[str] | None = None) -> str:
    text = str(value or "")
    if not text:
        return ""
    text = LOCAL_PATH_VALUE_RE.sub("<local-path>", text)
    text = TOKEN_VALUE_RE.sub("<token-like-value>", text)
    text = SECRET_ASSIGNMENT_RE.sub("<secret-assignment>", text)
    for term in private_terms or []:
        if not term or term in GENERIC_TERMS:
            continue
        text = re.sub(re.escape(term), "<private-app>", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip() if "\n" not in text else text


def redact_value(value: Any, *, private_terms: list[str]) -> Any:
    if isinstance(value, dict):
        return {key: redact_value(item, private_terms=private_terms) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item, private_terms=private_terms) for item in value]
    if isinstance(value, str):
        return redact_text(value, private_terms=private_terms)
    return value


def redact_shipguard_eval_report(report: dict[str, Any]) -> dict[str, Any]:
    private_terms = collect_private_terms(report)
    redacted = redact_value(report, private_terms=private_terms)
    if isinstance(redacted, dict):
        redacted["shareableRedactions"] = {
            "mode": "shipguard-eval-private-identity",
            "privateIdentifierCount": len(private_terms),
            "privateIdentifiersRedacted": bool(private_terms),
            "replacement": "<private-app>",
        }
    return redacted


def private_identifier_hits(text: str, report: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for term in collect_private_terms(report):
        if term and re.search(re.escape(term), text, re.IGNORECASE):
            hits.append(term)
    return sorted(set(hits), key=lambda term: (-len(term), term.lower()))
