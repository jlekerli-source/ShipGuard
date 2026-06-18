#!/usr/bin/env python3
"""Configuration baseline and suppression helpers for ShipGuard reports."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "1.0"
DEFAULT_CONFIG_PATH = ".shipguard.yml"
DEFAULT_BASELINE_PATH = ".shipguard-baseline.json"
DEFAULT_POLICY = {
    "requireOwner": True,
    "requireReason": True,
    "requireExpiresAt": True,
    "requireProofBoundary": True,
}


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "item"


def finding_fingerprint(rule_id: str, subject: str) -> str:
    return hashlib.sha256(f"{rule_id}\n{subject}".encode("utf-8")).hexdigest()[:16]


def make_finding(
    *,
    rule_id: str,
    severity: str,
    subject: str,
    source_key: str,
    reason: str,
    path: str | None = None,
    requirement_id: str | None = None,
    proof_boundary: str | None = None,
) -> dict[str, Any]:
    fingerprint = finding_fingerprint(rule_id, subject)
    finding = {
        "id": f"{slug(rule_id)}-{fingerprint[:8]}",
        "ruleId": rule_id,
        "severity": severity,
        "subject": subject,
        "fingerprint": fingerprint,
        "sourceKey": source_key,
        "reason": reason,
        "proofBoundary": proof_boundary or "No accepted-risk boundary has been recorded for this finding.",
    }
    if path:
        finding["path"] = path
    if requirement_id:
        finding["requirementId"] = requirement_id
    return finding


def _parse_bool(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered in {"true", "yes", "on", "1"}:
        return True
    if lowered in {"false", "no", "off", "0"}:
        return False
    return None


def parse_shipguard_yml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    config: dict[str, Any] = {}
    section: str | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()
        if text.endswith(":") and indent == 0:
            section = text[:-1].strip()
            continue
        if ":" not in text:
            continue
        key, raw_value = text.split(":", 1)
        key = key.strip()
        value = raw_value.strip().strip("\"'")
        scoped_key = f"{section}.{key}" if section and indent > 0 else key
        if scoped_key in {"baseline.path", "baselinePath", "baseline.path"}:
            config["baselinePath"] = value
        elif scoped_key in {"suppressions.requireOwner", "baseline.requireOwner", "requireOwner"}:
            parsed = _parse_bool(value)
            if parsed is not None:
                config.setdefault("policy", {})["requireOwner"] = parsed
        elif scoped_key in {"suppressions.requireReason", "baseline.requireReason", "requireReason"}:
            parsed = _parse_bool(value)
            if parsed is not None:
                config.setdefault("policy", {})["requireReason"] = parsed
        elif scoped_key in {"suppressions.requireExpiresAt", "baseline.requireExpiresAt", "requireExpiresAt"}:
            parsed = _parse_bool(value)
            if parsed is not None:
                config.setdefault("policy", {})["requireExpiresAt"] = parsed
        elif scoped_key in {"suppressions.requireProofBoundary", "baseline.requireProofBoundary", "requireProofBoundary"}:
            parsed = _parse_bool(value)
            if parsed is not None:
                config.setdefault("policy", {})["requireProofBoundary"] = parsed
    return config


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_baseline(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.is_file():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"invalid JSON in baseline: {exc}"]
    if not isinstance(data, dict):
        return [], ["baseline root must be a JSON object"]
    suppressions = data.get("suppressions")
    if not isinstance(suppressions, list):
        return [], ["baseline suppressions must be a list"]
    return [item for item in suppressions if isinstance(item, dict)], []


def _redact_suppression(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("id"),
        "ruleId": entry.get("ruleId"),
        "fingerprint": entry.get("fingerprint"),
        "hasOwner": bool(entry.get("owner")),
        "hasReason": bool(entry.get("reason")),
        "hasExpiresAt": bool(entry.get("expiresAt")),
        "hasProofBoundary": bool(entry.get("proofBoundary")),
    }


def load_configuration(
    root: Path,
    *,
    shareable: bool = False,
    redact_value: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    config_path = root / DEFAULT_CONFIG_PATH
    parsed_config = parse_shipguard_yml(config_path)
    baseline_rel = str(parsed_config.get("baselinePath") or DEFAULT_BASELINE_PATH)
    baseline_path = (root / baseline_rel).resolve()
    suppressions, errors = _read_baseline(baseline_path)
    policy = {**DEFAULT_POLICY, **(parsed_config.get("policy") or {})}
    redactor = redact_value or (lambda value: value)

    if shareable:
        public_entries = [_redact_suppression(item) for item in suppressions]
    else:
        public_entries = []
        for item in suppressions:
            public_item = dict(item)
            for key in ("owner", "reason", "proofBoundary"):
                if isinstance(public_item.get(key), str):
                    public_item[key] = redactor(public_item[key])
            public_entries.append(public_item)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "configured" if config_path.is_file() or baseline_path.is_file() else "default",
        "configPath": DEFAULT_CONFIG_PATH if config_path.is_file() else None,
        "baselinePath": _safe_rel(baseline_path, root),
        "policy": policy,
        "baseline": {
            "present": baseline_path.is_file(),
            "suppressionCount": len(suppressions),
            "suppressions": public_entries,
            "errors": errors,
            "shareableRedacted": shareable,
        },
    }


def parse_expiry(value: Any) -> dt.datetime | None:
    if not value:
        return None
    text = str(value).strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return dt.datetime.fromisoformat(text + "T23:59:59+00:00")
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    except ValueError:
        return None


def suppression_validation(entry: dict[str, Any], policy: dict[str, Any], now: dt.datetime) -> dict[str, Any]:
    missing = []
    if not entry.get("id"):
        missing.append("id")
    if not entry.get("ruleId"):
        missing.append("ruleId")
    if not entry.get("fingerprint"):
        missing.append("fingerprint")
    if policy.get("requireOwner") and not entry.get("owner"):
        missing.append("owner")
    if policy.get("requireReason") and not entry.get("reason"):
        missing.append("reason")
    if policy.get("requireExpiresAt") and not entry.get("expiresAt"):
        missing.append("expiresAt")
    if policy.get("requireProofBoundary") and not entry.get("proofBoundary"):
        missing.append("proofBoundary")
    expiry = parse_expiry(entry.get("expiresAt"))
    expired = bool(expiry and expiry < now)
    if entry.get("expiresAt") and expiry is None:
        missing.append("validExpiresAt")
    status = "active"
    if missing:
        status = "invalid"
    elif expired:
        status = "expired"
    return {
        "id": entry.get("id"),
        "ruleId": entry.get("ruleId"),
        "fingerprint": entry.get("fingerprint"),
        "owner": entry.get("owner"),
        "expiresAt": entry.get("expiresAt"),
        "proofBoundary": entry.get("proofBoundary"),
        "status": status,
        "missing": missing,
        "expired": expired,
    }


def apply_configuration_baseline(
    configuration: dict[str, Any] | None,
    findings: list[dict[str, Any]],
    *,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    configuration = configuration or {
        "schemaVersion": SCHEMA_VERSION,
        "status": "default",
        "policy": DEFAULT_POLICY,
        "baseline": {"present": False, "suppressionCount": 0, "suppressions": [], "errors": []},
    }
    now = now or dt.datetime.now(dt.timezone.utc)
    policy = {**DEFAULT_POLICY, **(configuration.get("policy") or {})}
    suppressions = list((configuration.get("baseline") or {}).get("suppressions") or [])
    validated = [suppression_validation(item, policy, now) for item in suppressions if isinstance(item, dict)]

    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in validated:
        key = (str(item.get("ruleId") or ""), str(item.get("fingerprint") or ""))
        by_key.setdefault(key, []).append(item)

    accepted: list[dict[str, Any]] = []
    unsuppressed: list[dict[str, Any]] = []
    matched_suppression_ids: set[str] = set()
    for finding in findings:
        key = (str(finding.get("ruleId") or ""), str(finding.get("fingerprint") or ""))
        candidates = by_key.get(key) or []
        active = next((item for item in candidates if item.get("status") == "active"), None)
        if active:
            matched_suppression_ids.add(str(active.get("id") or ""))
            accepted.append(
                {
                    **finding,
                    "suppression": {
                        "id": active.get("id"),
                        "owner": active.get("owner"),
                        "expiresAt": active.get("expiresAt"),
                        "proofBoundary": active.get("proofBoundary"),
                    },
                    "baselineStatus": "accepted",
                }
            )
            continue
        invalid_or_expired = next((item for item in candidates if item.get("status") in {"invalid", "expired"}), None)
        if invalid_or_expired:
            matched_suppression_ids.add(str(invalid_or_expired.get("id") or ""))
            unsuppressed.append(
                {
                    **finding,
                    "baselineStatus": str(invalid_or_expired.get("status")),
                    "suppression": {
                        "id": invalid_or_expired.get("id"),
                        "missing": invalid_or_expired.get("missing") or [],
                        "expiresAt": invalid_or_expired.get("expiresAt"),
                    },
                }
            )
            continue
        unsuppressed.append({**finding, "baselineStatus": "new"})

    unmatched = [
        item
        for item in validated
        if str(item.get("id") or "") not in matched_suppression_ids and item.get("status") == "active"
    ]
    invalid = [item for item in validated if item.get("status") == "invalid"]
    expired = [item for item in validated if item.get("status") == "expired"]
    block_count = sum(1 for item in unsuppressed if item.get("severity") == "block")
    review_count = sum(1 for item in unsuppressed if item.get("severity") == "review")
    status = "blocked" if block_count else "review" if review_count else "pass"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "configured": configuration.get("status") == "configured",
        "policy": policy,
        "baselinePath": configuration.get("baselinePath"),
        "findingCount": len(findings),
        "acceptedFindingCount": len(accepted),
        "unsuppressedFindingCount": len(unsuppressed),
        "blockFindingCount": block_count,
        "reviewFindingCount": review_count,
        "acceptedFindings": accepted,
        "unsuppressedFindings": unsuppressed,
        "unmatchedSuppressions": unmatched,
        "invalidSuppressions": invalid,
        "expiredSuppressions": expired,
        "errors": list((configuration.get("baseline") or {}).get("errors") or []),
        "regressionBehavior": {
            "newFindingsBlock": block_count > 0,
            "newFindingsReview": review_count > 0 and block_count == 0,
            "acceptedFindingsVisible": bool(accepted),
            "exactFingerprintRequired": True,
        },
    }
